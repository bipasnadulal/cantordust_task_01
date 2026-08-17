from schemas import (
    Evidence,
    ExtractedField,
    FieldCategory,
)
from normalizer import normalize_field
from field_mapper import (
    canonicalize_field,
    canonicalize_field_name,
    canonicalize_fields,
)


def make_normalized_field(
    field_name: str,
    raw_value: str = "5",
    unit: str | None = "kW",
) :

    extracted = ExtractedField(
        field_name=field_name,
        category=FieldCategory.ELECTRICAL,
        raw_value=raw_value,
        unit=unit,
        evidence=Evidence(
            document_name="test.pdf",
            page_number=2,
            section="Technical Data",
            source_text=f"{field_name} {raw_value}",
        ),
    )

    return normalize_field(extracted)


def test_dc_input_power_alias():

    result = canonicalize_field_name(
        "Max. DC Input Power"
    )

    assert result == "max_pv_input_power"


def test_pv_input_power_alias():

    result = canonicalize_field_name(
        "Max. PV Input Power"
    )

    assert result == "max_pv_input_power"


def test_dc_input_current_alias():

    result = canonicalize_field_name(
        "Max. DC Input Current"
    )

    assert result == "max_pv_input_current"


def test_operating_pv_current_alias():

    result = canonicalize_field_name(
        "Max. Operating PV Input Current"
    )

    assert result == "max_pv_input_current"


def test_short_circuit_current_alias():

    result = canonicalize_field_name(
        "Max. Input Short Circuit Current"
    )

    assert result == "max_pv_short_circuit_current"


def test_case_and_whitespace_are_normalized():

    result = canonicalize_field_name(
        "   MAX. DC INPUT POWER   "
    )

    assert result == "max_pv_input_power"


def test_unknown_field_uses_conservative_fallback():

    result = canonicalize_field_name(
        "Some New Specification"
    )

    assert result == "some_new_specification"


def test_canonicalize_field_preserves_value():

    field = make_normalized_field(
        field_name="Max. PV Input Power",
        raw_value="6.5",
        unit="kW",
    )

    result = canonicalize_field(field)

    assert result.field_name == "max_pv_input_power"
    assert result.raw_value == "6.5"
    assert result.normalized_value == 6.5
    assert result.unit == "kW"


def test_canonicalize_field_preserves_evidence():

    field = make_normalized_field(
        field_name="Max. PV Input Power",
        raw_value="6.5",
        unit="kW",
    )

    result = canonicalize_field(field)

    assert result.evidence.document_name == "test.pdf"
    assert result.evidence.page_number == 2
    assert result.evidence.section == "Technical Data"


def test_canonicalize_multiple_fields():

    fields = [
        make_normalized_field(
            "Max. DC Input Power",
            "6.5",
            "kW",
        ),
        make_normalized_field(
            "Max. PV Input Voltage",
            "1100",
            "V",
        ),
        make_normalized_field(
            "Max. Operating PV Input Current",
            "13",
            "A",
        ),
    ]

    results = canonicalize_fields(fields)

    assert results[0].field_name == "max_pv_input_power"
    assert results[1].field_name == "max_pv_input_voltage"
    assert results[2].field_name == "max_pv_input_current"


# ---------------------------------------------------------------------
# Regression tests for the snake_case / natural-language field-name
# mismatch bug: the extraction prompt does not force a single format,
# and some LLM responses come back already snake_cased (e.g.
# "grid_regulation") instead of natural-language wording
# (e.g. "grid regulation"). Both must resolve to the same canonical
# name, or two documents describing the same spec get split into two
# separate, unmatched fields downstream.
# ---------------------------------------------------------------------

def test_snake_case_alias_matches_same_canonical_as_natural_wording():

    natural = canonicalize_field_name("Grid Connection Standard")
    snake_case = canonicalize_field_name("grid_regulation")

    assert natural == snake_case == "grid_connection_standard"


def test_snake_case_alias_matches_for_rated_output_power():

    natural = canonicalize_field_name("Rated Output Power")
    snake_case = canonicalize_field_name("rated_ac_output_active_power")

    assert natural == snake_case == "rated_ac_output_power"


def test_already_canonical_value_passes_through_unchanged():

    # If the LLM happens to return the canonical name directly, it
    # must not be mangled by the fallback branch.
    result = canonicalize_field_name("max_pv_input_power")

    assert result == "max_pv_input_power"


def test_two_sources_with_different_field_name_formats_merge():

    source_1_field = make_normalized_field(
        "Grid Connection Standard",
        "IEC 61727, IEC 62116, EN 50549",
        None,
    )

    source_2_field = make_normalized_field(
        "grid_regulation",
        "IEC 61727, IEC 62116, CEI 0-21, EN 50549",
        None,
    )

    canonical_1 = canonicalize_field(source_1_field)
    canonical_2 = canonicalize_field(source_2_field)

    # Same canonical field name means the reconciler will compare them
    # as one field (agree/conflict) instead of reporting two separate
    # "only in one source" gaps.
    assert canonical_1.field_name == canonical_2.field_name == (
        "grid_connection_standard"
    )