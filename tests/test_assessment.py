from schemas import (
    Evidence,
    FieldCategory,
    NormalizedField,
    ReconciledField,
    ReconciliationStatus,
)

from assessment import (
    build_assessment,
    build_summary,
)


def make_field(
    name,
    source_1_value,
    source_2_value,
    status,
):
    evidence_1 = Evidence(
        document_name="datasheet_1.pdf",
        page_number=2,
        source_text=f"{name}: {source_1_value}",
    )

    evidence_2 = Evidence(
        document_name="datasheet_2.pdf",
        page_number=2,
        source_text=f"{name}: {source_2_value}",
    )

    source_1 = NormalizedField(
        field_name=name,
        category=FieldCategory.ELECTRICAL,
        raw_value=str(source_1_value),
        normalized_value=source_1_value,
        unit="V",
        evidence=evidence_1,
    )

    source_2 = NormalizedField(
        field_name=name,
        category=FieldCategory.ELECTRICAL,
        raw_value=str(source_2_value),
        normalized_value=source_2_value,
        unit="V",
        evidence=evidence_2,
    )

    return ReconciledField(
        field_name=name,
        category=FieldCategory.ELECTRICAL,
        source_1=source_1,
        source_2=source_2,
        status=status,
        explanation="Test reconciliation.",
    )


def test_build_assessment():
    fields = [
        make_field(
            "Max DC Input Voltage",
            1100,
            1100,
            ReconciliationStatus.AGREES,
        )
    ]

    result = build_assessment(
        product_model="SUN-5K-G06P3-EU-AM2",
        source_documents=[
            "datasheet_1.pdf",
            "datasheet_2.pdf",
        ],
        reconciled_fields=fields,
    )

    assert result.product_model == "SUN-5K-G06P3-EU-AM2"
    assert len(result.source_documents) == 2
    assert len(result.specifications) == 1
    assert result.overall_status == "agrees"


def test_conflict_assessment():
    fields = [
        make_field(
            "Max DC Input Voltage",
            1100,
            1000,
            ReconciliationStatus.CONFLICT,
        )
    ]

    result = build_assessment(
        product_model="SUN-5K-G06P3-EU-AM2",
        source_documents=[
            "datasheet_1.pdf",
            "datasheet_2.pdf",
        ],
        reconciled_fields=fields,
    )

    assert result.overall_status == "conflict"
    assert len(result.review_items) == 1
    assert result.review_items[0].field_name == (
        "Max DC Input Voltage"
    )


def test_agreement_creates_no_review_item():
    fields = [
        make_field(
            "Max DC Input Voltage",
            1100,
            1100,
            ReconciliationStatus.AGREES,
        ),
        make_field(
            "Efficiency",
            98.5,
            98.5,
            ReconciliationStatus.AGREES,
        ),
    ]

    result = build_assessment(
        product_model="SUN-5K-G06P3-EU-AM2",
        source_documents=[
            "datasheet_1.pdf",
            "datasheet_2.pdf",
        ],
        reconciled_fields=fields,
    )

    assert result.overall_status == "agrees"
    assert result.review_items == []


def test_summary_contains_key_information():
    fields = [
        make_field(
            "Max DC Input Voltage",
            1100,
            1100,
            ReconciliationStatus.AGREES,
        ),
        make_field(
            "Max DC Input Current",
            20,
            19.5,
            ReconciliationStatus.CONFLICT,
        ),
    ]

    summary = build_summary(
        product_model="SUN-5K-G06P3-EU-AM2",
        source_documents=[
            "datasheet_1.pdf",
            "datasheet_2.pdf",
        ],
        reconciled_fields=fields,
        review_items=[],
    )

    assert "SUN-5K-G06P3-EU-AM2" in summary
    assert "2 specification fields" in summary
    assert "1 fields agree" in summary
    assert "1 fields conflict" in summary


def test_source_only_status():
    fields = [
        make_field(
            "Warranty",
            "5 years",
            "5 years",
            ReconciliationStatus.SOURCE_1_ONLY,
        )
    ]

    result = build_assessment(
        product_model="SUN-5K-G06P3-EU-AM2",
        source_documents=[
            "datasheet_1.pdf",
            "datasheet_2.pdf",
        ],
        reconciled_fields=fields,
    )

    assert len(result.review_items) == 1
    assert result.overall_status == "incomplete"