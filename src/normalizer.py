
from schemas import ExtractedField, NormalizedField


def normalize_number(value: str) -> int | float:
    """
    Convert a simple numeric string into int or float.

    Examples:
        "5"      -> 5
        "5.5"    -> 5.5
        "98.5"   -> 98.5
        "1,100"  -> 1100
    """

    cleaned = value.strip().replace(",", "")

    number = float(cleaned)

    if number.is_integer():
        return int(number)

    return number


def normalize_percentage(value: str) -> float:
    """
    Convert a percentage string into its numeric representation.

    Examples:
        "98.5%" -> 98.5
        "<3%"   -> 3.0

    The comparison operator is intentionally not preserved
    in normalized_value. The original value remains available
    through raw_value.
    """

    cleaned = value.strip()

    cleaned = cleaned.replace("%", "")
    cleaned = cleaned.replace("<", "")
    cleaned = cleaned.replace(">", "")

    return float(cleaned)


def normalize_boolean(value: str) -> bool | str:
    """
    Normalize explicit Yes/No values.

    Unknown values are returned unchanged rather than guessed.
    """

    cleaned = value.strip().lower()

    if cleaned == "yes":
        return True

    if cleaned == "no":
        return False

    return value


def normalize_value(
    raw_value: str,
    unit: str | None,
) -> str | float | int | bool:
    """
    Normalize a raw extracted value.

    This function changes representation only.
    It does not attempt to determine whether the value
    is factually correct.
    """

    value = raw_value.strip()

    # Explicit boolean values
    boolean_value = normalize_boolean(value)

    if isinstance(boolean_value, bool):
        return boolean_value

    # Percentages
    if unit == "%" or "%" in value:
        try:
            return normalize_percentage(value)
        except ValueError:
            return value

    # Simple numeric values
    try:
        return normalize_number(value)
    except ValueError:
        pass

    # Everything else remains a string.
    return value


def normalize_field(
    field: ExtractedField,
) -> NormalizedField:
    """
    Convert one ExtractedField into a NormalizedField.
    """

    normalized_value = normalize_value(
        raw_value=field.raw_value,
        unit=field.unit,
    )

    normalized_unit = field.unit

    # Normalize common unit spelling/casing.
    if normalized_unit:
        normalized_unit = normalized_unit.strip()

        if normalized_unit.lower() == "years":
            normalized_unit = "year"

        elif normalized_unit.lower() == "℃":
            normalized_unit = "°C"

        elif normalized_unit.lower() == "db":
            normalized_unit = "dB"

        elif normalized_unit.lower() == "kw":
            normalized_unit = "kW"

        elif normalized_unit.lower() == "v":
            normalized_unit = "V"

        elif normalized_unit.lower() == "a":
            normalized_unit = "A"

        elif normalized_unit.lower() == "hz":
            normalized_unit = "Hz"

        elif normalized_unit.lower() == "m":
            normalized_unit = "m"

        elif normalized_unit.lower() == "w":
            normalized_unit = "W"

    return NormalizedField(
        field_name=field.field_name,
        category=field.category,
        raw_value=field.raw_value,
        normalized_value=normalized_value,
        unit=normalized_unit,
        evidence=field.evidence,
        confidence=field.confidence,
        extraction_note=field.extraction_note,
    )


def normalize_fields(
    fields: list[ExtractedField],
) -> list[NormalizedField]:
    """
    Normalize a list of extracted fields.
    """

    return [
        normalize_field(field)
        for field in fields
    ]