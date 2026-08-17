from schemas import (
    Evidence,
    ExtractedField,
    FieldCategory,
)
from normalizer import normalize_field
from field_mapper import canonicalize_field
from reconciler import reconcile_fields


def make_field(
    name: str,
    value: str,
    unit: str | None = None,
):
    extracted = ExtractedField(
        field_name=name,
        category=FieldCategory.ELECTRICAL,
        raw_value=value,
        unit=unit,
        evidence=Evidence(
            document_name="test.pdf",
            page_number=2,
            source_text=f"{name} {value}",
        ),
    )

    normalized = normalize_field(extracted)

    return canonicalize_field(normalized)


def test_matching_values_agree():
    source_1 = [
        make_field(
            "Max. DC Input Voltage",
            "1100",
            "V",
        )
    ]

    source_2 = [
        make_field(
            "Max. PV Input Voltage",
            "1100",
            "V",
        )
    ]

    results = reconcile_fields(source_1, source_2)

    assert len(results) == 1
    assert results[0].status.value == "agrees"


def test_different_values_conflict():
    source_1 = [
        make_field(
            "Max. DC Input Current",
            "20",
            "A",
        )
    ]

    source_2 = [
        make_field(
            "Max. Operating PV Input Current",
            "19.5",
            "A",
        )
    ]

    results = reconcile_fields(source_1, source_2)

    assert len(results) == 1
    assert results[0].status.value == "conflict"


def test_source_1_only():
    source_1 = [
        make_field(
            "Warranty",
            "5 Years",
            "Years",
        )
    ]

    source_2 = []

    results = reconcile_fields(source_1, source_2)

    assert len(results) == 1
    assert results[0].status.value == "source_1_only"


def test_source_2_only():
    source_1 = []

    source_2 = [
        make_field(
            "Warranty",
            "5 Years",
            "Years",
        )
    ]

    results = reconcile_fields(source_1, source_2)

    assert len(results) == 1
    assert results[0].status.value == "source_2_only"


def test_multiple_fields():
    source_1 = [
        make_field(
            "Max. DC Input Voltage",
            "1100",
            "V",
        ),
        make_field(
            "Max. DC Input Current",
            "20",
            "A",
        ),
    ]

    source_2 = [
        make_field(
            "Max. PV Input Voltage",
            "1100",
            "V",
        ),
        make_field(
            "Max. Operating PV Input Current",
            "19.5",
            "A",
        ),
    ]

    results = reconcile_fields(source_1, source_2)

    assert len(results) == 2

    statuses = [result.status.value for result in results]

    assert "agrees" in statuses
    assert "conflict" in statuses