from schemas import Evidence, ExtractedField, FieldCategory
from normalizer import (
    normalize_field,
    normalize_fields,
)


def make_field(
    field_name: str,
    raw_value: str,
    unit: str | None,
    category: FieldCategory = FieldCategory.ELECTRICAL,
) -> ExtractedField:

    return ExtractedField(
        field_name=field_name,
        category=category,
        raw_value=raw_value,
        unit=unit,
        evidence=Evidence(
            document_name="test.pdf",
            page_number=2,
            section="Technical Data",
            source_text=f"{field_name} {raw_value}",
        ),
    )


def test_numeric_normalization():

    field = make_field(
        field_name="Rated Output Power",
        raw_value="5",
        unit="kW",
    )

    result = normalize_field(field)

    assert result.raw_value == "5"
    assert result.normalized_value == 5
    assert result.unit == "kW"


def test_decimal_normalization():

    field = make_field(
        field_name="Max Active Power",
        raw_value="5.5",
        unit="kW",
    )

    result = normalize_field(field)

    assert result.normalized_value == 5.5
    assert result.unit == "kW"


def test_percentage_normalization():

    field = make_field(
        field_name="Max Efficiency",
        raw_value="98.5%",
        unit="%",
        category=FieldCategory.PERFORMANCE,
    )

    result = normalize_field(field)

    assert result.raw_value == "98.5%"
    assert result.normalized_value == 98.5
    assert result.unit == "%"


def test_boolean_normalization():

    field = make_field(
        field_name="AC Short Circuit Protection",
        raw_value="Yes",
        unit=None,
        category=FieldCategory.PROTECTION,
    )

    result = normalize_field(field)

    assert result.normalized_value is True
    assert result.unit is None


def test_boolean_no_normalization():

    field = make_field(
        field_name="Surge Protection",
        raw_value="No",
        unit=None,
        category=FieldCategory.PROTECTION,
    )

    result = normalize_field(field)

    assert result.normalized_value is False


def test_text_is_preserved():

    field = make_field(
        field_name="Topology",
        raw_value="Transformerless",
        unit=None,
        category=FieldCategory.GENERAL_DATA,
    )

    result = normalize_field(field)

    assert result.normalized_value == "Transformerless"


def test_complex_value_is_preserved():

    field = make_field(
        field_name="Rated Output Voltage/Range",
        raw_value="220/380V, 230/400V",
        unit="V",
    )

    result = normalize_field(field)

    assert result.normalized_value == "220/380V, 230/400V"
    assert result.unit == "V"


def test_unit_normalization():

    field = make_field(
        field_name="Weight",
        raw_value="11",
        unit="kg",
        category=FieldCategory.GENERAL_DATA,
    )

    result = normalize_field(field)

    assert result.normalized_value == 11
    assert result.unit == "kg"


def test_list_normalization():

    fields = [
        make_field(
            field_name="Rated Output Power",
            raw_value="5",
            unit="kW",
        ),
        make_field(
            field_name="Max Efficiency",
            raw_value="98.5%",
            unit="%",
            category=FieldCategory.PERFORMANCE,
        ),
    ]

    results = normalize_fields(fields)

    assert len(results) == 2
    assert results[0].normalized_value == 5
    assert results[1].normalized_value == 98.5