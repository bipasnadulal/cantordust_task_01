from schemas import (
    Evidence,
    ExtractedField,
    NormalizedField,
    ReconciledField,
    ReconciliationStatus,
    FieldCategory,
)

from ground_truth import (
    build_ground_truth_matrix,
    determine_overall_status,
    build_review_items,
)


def make_field(
    name,
    value,
    status=ReconciliationStatus.AGREES,
    category=FieldCategory.ELECTRICAL,
):
    evidence = Evidence(
        document_name="test.pdf",
        page_number=2,
        source_text=f"{name}: {value}",
    )

    normalized = NormalizedField(
        field_name=name,
        category=category,
        raw_value=str(value),
        normalized_value=value,
        unit=None,
        evidence=evidence,
    )

    return ReconciledField(
        field_name=name,
        category=category,
        source_1=normalized,
        source_2=normalized,
        status=status,
        explanation=f"Test comparison for {name}",
    )


def test_build_ground_truth_matrix():
    fields = [
        make_field("Max DC Input Voltage", 1100),
        make_field("Max Efficiency", 98.5),
    ]

    result = build_ground_truth_matrix(fields)

    assert len(result) == 2
    assert all(isinstance(field, ReconciledField) for field in result)


def test_matrix_preserves_reconciliation_status():
    fields = [
        make_field(
            "Max DC Input Current",
            20,
            ReconciliationStatus.CONFLICT,
        )
    ]

    result = build_ground_truth_matrix(fields)

    assert result[0].status == ReconciliationStatus.CONFLICT


def test_overall_status_agrees():
    fields = [
        make_field("Voltage", 1100),
        make_field("Efficiency", 98.5),
    ]

    assert determine_overall_status(fields) == "agrees"


def test_overall_status_conflict():
    fields = [
        make_field(
            "Voltage",
            1100,
            ReconciliationStatus.CONFLICT,
        )
    ]

    assert determine_overall_status(fields) == "conflict"


def test_overall_status_uncertain():
    fields = [
        make_field(
            "Voltage",
            1100,
            ReconciliationStatus.UNCERTAIN,
        )
    ]

    assert determine_overall_status(fields) == "uncertain"


def test_conflict_creates_review_item():
    fields = [
        make_field(
            "Max DC Input Current",
            20,
            ReconciliationStatus.CONFLICT,
        )
    ]

    review_items = build_review_items(fields)

    assert len(review_items) == 1
    assert review_items[0].field_name == "Max DC Input Current"
    assert review_items[0].priority.value == "high"
    assert review_items[0].status == ReconciliationStatus.CONFLICT


def test_agreement_does_not_create_review_item():
    fields = [
        make_field(
            "Max DC Input Voltage",
            1100,
            ReconciliationStatus.AGREES,
        )
    ]

    review_items = build_review_items(fields)

    assert len(review_items) == 0


def test_source_only_creates_low_priority_review():
    fields = [
        make_field(
            "Warranty",
            "5 years",
            ReconciliationStatus.SOURCE_1_ONLY,
        )
    ]

    review_items = build_review_items(fields)

    assert len(review_items) == 1
    assert review_items[0].priority.value == "low"


def test_review_item_contains_evidence():
    fields = [
        make_field(
            "Max DC Input Current",
            20,
            ReconciliationStatus.CONFLICT,
        )
    ]

    review_items = build_review_items(fields)

    assert len(review_items[0].evidence) == 2