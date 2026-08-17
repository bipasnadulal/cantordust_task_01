import re

from schemas import NormalizedField

# Canonical field aliases
# Different datasheets may use slightly different names for the same
# specification. We map those names to one canonical field name.
#
# IMPORTANT:
# This mapping changes ONLY the field identity.
# It does NOT change the value.

FIELD_ALIASES = {
    
    # Product identity
    
    "model": "model",
    
    # PV / DC input

    "max. dc input power": "max_pv_input_power",
    "max dc input power": "max_pv_input_power",
    "max. pv input power": "max_pv_input_power",
    "max pv input power": "max_pv_input_power",

    "max. dc input voltage": "max_pv_input_voltage",
    "max dc input voltage": "max_pv_input_voltage",
    "max. pv input voltage": "max_pv_input_voltage",
    "max pv input voltage": "max_pv_input_voltage",

    "start-up dc input voltage": "startup_pv_input_voltage",
    "startup dc input voltage": "startup_pv_input_voltage",
    "start-up voltage": "startup_pv_input_voltage",
    "startup voltage": "startup_pv_input_voltage",
    "start up voltage": "startup_pv_input_voltage",

    "mppt operating range": "mppt_voltage_range",
    "mppt voltage range": "mppt_voltage_range",
    "mppt operating voltage range": "mppt_voltage_range",

    "rated pv input voltage": "rated_pv_input_voltage",

    "max. dc input current": "max_pv_input_current",
    "max dc input current": "max_pv_input_current",
    "max. operating pv input current": "max_pv_input_current",
    "max operating pv input current": "max_pv_input_current",

    "max. short circuit current": "max_pv_short_circuit_current",
    "max short circuit current": "max_pv_short_circuit_current",
    "max. input short circuit current": "max_pv_short_circuit_current",
    "max input short circuit current": "max_pv_short_circuit_current",

    "no. of mpp trackers": "mpp_tracker_count",
    "no. of mpp trackers/": "mpp_tracker_count",
    "mpp tracker count": "mpp_tracker_count",

    "no. of strings per mpp tracker": "strings_per_mpp_tracker",
    "strings per mpp tracker": "strings_per_mpp_tracker",

  
    # AC output
    "rated output power": "rated_ac_output_power",
    "rated ac output active power": "rated_ac_output_power",
    "rated ac output power": "rated_ac_output_power",

    "max. active power": "max_active_power",

    "max ac output apparent power": "max_ac_output_apparent_power",

    "rated ac grid output current": "rated_ac_output_current",
    "rated ac output current": "rated_ac_output_current",

    "max. ac output current": "max_ac_output_current",
    "max ac output current": "max_ac_output_current",

    "rated output voltage/range": "rated_output_voltage_range",

    "rated grid frequency": "rated_grid_frequency",
    "rated output grid frequency/range": "rated_grid_frequency",
    "rated output grid frequency range": "rated_grid_frequency",

    "operating phase": "operating_phase",

    "grid connection form": "grid_connection_form",

    "total harmonics current distortion": "thdi",
    "total current harmonic distortion": "thdi",
    "thdi": "thdi",

    "power factor adjustment range": "power_factor_range",

    # Performance

    "max. efficiency": "max_efficiency",
    "max efficiency": "max_efficiency",

    "euro efficiency": "euro_efficiency",

    "mppt efficiency": "mppt_efficiency",


    # Protection

    "dc reverse-polarity protection": "dc_reverse_polarity_protection",
    "dc polarity reverse connection protection": "dc_reverse_polarity_protection",

    "ac short circuit protection": "ac_short_circuit_protection",
    "ac output short circuit protection": "ac_short_circuit_protection",

    "ac output overcurrent protection": "ac_output_overcurrent_protection",

    "output overvoltage protection": "ac_output_overvoltage_protection",
    "ac output overvoltage protection": "ac_output_overvoltage_protection",

    "insulation resistance protection": "insulation_resistance_protection",
    "dc terminal insulation impedance monitoring": "insulation_resistance_protection",

    "ground fault monitoring": "ground_fault_monitoring",
    "ground fault current monitoring": "ground_fault_monitoring",

    "anti-islanding protection": "anti_islanding_protection",
    "island protection monitoring": "anti_islanding_protection",

    "temperature protection": "temperature_protection",
    "thermal protection": "temperature_protection",

    "surge protection": "surge_protection",
    "surge protection level": "surge_protection_level",

    "integrated dc switch": "integrated_dc_switch",

    # General data
    "cabinet size": "cabinet_dimensions",

    "weight": "weight",

    "topology": "topology",
    "inverter topology": "topology",

    "internal consumption": "internal_consumption",

    "running temperature": "operating_temperature_range",
    "operating temperature range": "operating_temperature_range",

    "ingress protection": "ingress_protection",
    "ingress protection(ip) rating": "ingress_protection",
    "ingress protection rating": "ingress_protection",
    "ingress protection (ip) rating": "ingress_protection",

    "permissible altitude": "permissible_altitude",

    "noise emission": "noise_emission",
    "noise": "noise_emission",

    "cooling concept": "cooling_concept",
    "type of cooling": "cooling_concept",

    "warranty": "warranty",

    "operating surroundings humidity": "operating_humidity",
    "permissible ambient humidity": "operating_humidity",


    # Interface

    "display": "display",

    "interface": "communication_interface",
    "communication interface": "communication_interface",

    "remote software upload": "remote_software_upload",

    "remote change of operating parameters": (
        "remote_operating_parameter_change"
    ),

  
    # Standards

    "grid connection standard": "grid_connection_standard",
    "grid regulation": "grid_connection_standard",

    "safety / emc standard": "safety_emc_standard",
    "safety emc/standard": "safety_emc_standard",

    "thermal protection": "temperature_protection",

"grid regulation": "grid_connection_standard",

"ground fault current monitoring": "ground_fault_monitoring",

"dc terminal insulation impedance monitoring": "insulation_resistance_protection",

"island protection monitoring": "anti_islanding_protection",

"ac output short circuit protection": "ac_short_circuit_protection",

"type of cooling": "cooling_concept",

"permissible ambient humidity": "operating_humidity",

"over voltage category": "overvoltage_category",

}


# Reverse index: canonical value -> canonical value.
# Lets an already-canonical (snake_case) name pass through unchanged
# instead of falling through to the fallback branch.
_CANONICAL_VALUES = set(FIELD_ALIASES.values())


def clean_field_name(field_name: str) -> str:
    """
    Clean a field name before alias lookup.

    This handles small formatting differences such as:
        "Max. DC Input Power "
        "MAX. DC INPUT POWER"
        "Max. DC Input Power"
    """

    value = field_name.strip().lower()

    # Normalize whitespace.
    value = re.sub(r"\s+", " ", value)

    return value


def _spaced_variant(cleaned: str) -> str:
    """
    Produce a space-separated variant of a cleaned field name.

    The extraction prompt asks the LLM for a "canonical field name"
    without specifying a format. In practice some responses come back
    already snake_cased (e.g. "grid_regulation") while the alias table
    is keyed on natural-language wording with spaces
    (e.g. "grid regulation"). Without this normalization, snake_cased
    responses silently miss the alias table and fall through to the
    conservative fallback, which is close to a no-op for strings that
    are already snake_case — causing the same underlying field from two
    sources to be treated as two different fields.
    """

    variant = cleaned.replace("_", " ").replace("-", " ")
    variant = re.sub(r"\s+", " ", variant).strip()
    return variant


def canonicalize_field_name(field_name: str) -> str:
    """
    Convert a source field name into its canonical field name.

    If no explicit alias exists, create a safe fallback based on
    the cleaned field name.

    We do NOT use fuzzy matching here because an incorrect fuzzy
    match could merge two genuinely different specifications.
    """

    cleaned = clean_field_name(field_name)

    # 1. Direct alias match (handles natural-language wording, e.g.
    #    "Max. DC Input Power").
    if cleaned in FIELD_ALIASES:
        return FIELD_ALIASES[cleaned]

    # 2. If the LLM already returned an exact canonical value
    #    (e.g. "max_pv_input_power"), accept it as-is.
    fallback = re.sub(r"[^a-z0-9]+", "_", cleaned)
    fallback = fallback.strip("_")

    if fallback in _CANONICAL_VALUES:
        return fallback

    # 3. Try the alias table again treating underscores/hyphens as
    #    spaces. This catches snake_cased responses that correspond to
    #    an alias keyed on natural-language wording
    #    (e.g. "grid_regulation" -> "grid regulation" -> alias match).
    spaced = _spaced_variant(cleaned)

    if spaced in FIELD_ALIASES:
        return FIELD_ALIASES[spaced]

    # 4. Conservative fallback: no alias found in either format.
    return fallback


def canonicalize_field(
    field: NormalizedField,
) -> NormalizedField:
    """
    Return a copy of a NormalizedField with its field name replaced
    by the canonical field name.

    The raw value, normalized value, unit, category, and evidence
    remain unchanged.
    """

    canonical_name = canonicalize_field_name(
        field.field_name
    )

    return field.model_copy(
        update={
            "field_name": canonical_name,
        }
    )


def canonicalize_fields(
    fields: list[NormalizedField],
) -> list[NormalizedField]:
    """
    Canonicalize a list of normalized fields.
    """

    return [
        canonicalize_field(field)
        for field in fields
    ]