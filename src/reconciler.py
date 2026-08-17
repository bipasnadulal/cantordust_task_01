# from schemas import (
#     NormalizedField,
#     ReconciledField,
#     ReconciliationStatus,
# )


# def _field_key(field: NormalizedField) -> str:
#     """
#     Create a comparison key for equivalent specification names.

#     The key is used only for matching. The original field name is
#     always preserved in the ReconciledField output.
#     """

#     name = field.field_name.strip().lower()

#     # Normalize punctuation.
#     for character in ".-_()/:":
#         name = name.replace(character, " ")

#     name = " ".join(name.split())

#     aliases = {
#         # Voltage terminology
#         "max pv input voltage": "max dc input voltage",
#         "maximum pv input voltage": "max dc input voltage",
#         "maximum dc input voltage": "max dc input voltage",

#         # Current terminology
#         "max operating pv input current": "max dc input current",
#         "maximum operating pv input current": "max dc input current",
#         "maximum dc input current": "max dc input current",

#         # Other common terminology
#         "maximum ac output current": "max ac output current",
#         "maximum active power": "max active power",

#         "number of mpp trackers": "no of mpp trackers",

#         "number of strings per mpp tracker":
#             "no of strings per mpp tracker",
#     }

#     return aliases.get(name, name)


# def _values_equal(
#     value_1: str | float | int | bool,
#     value_2: str | float | int | bool,
# ) -> bool:
#     """
#     Compare normalized values.
#     """

#     if isinstance(value_1, bool) or isinstance(value_2, bool):
#         return value_1 == value_2

#     if isinstance(value_1, (int, float)) and isinstance(
#         value_2, (int, float)
#     ):
#         return value_1 == value_2

#     return str(value_1).strip().lower() == str(value_2).strip().lower()


# def reconcile_fields(
#     source_1_fields: list[NormalizedField],
#     source_2_fields: list[NormalizedField],
# ) -> list[ReconciledField]:
#     """
#     Reconcile specifications from two sources.

#     Equivalent field names are matched using _field_key().

#     When a field exists in both sources, the field name and category
#     from source 1 are used as the canonical output representation.
#     """

#     source_1 = {}
#     source_2 = {}

#     # ---------------------------------------------------------
#     # Index source 1
#     # ---------------------------------------------------------

#     for field in source_1_fields:
#         key = _field_key(field)
#         source_1[key] = field

#     # ---------------------------------------------------------
#     # Index source 2
#     # ---------------------------------------------------------

#     for field in source_2_fields:
#         key = _field_key(field)
#         source_2[key] = field

#     # ---------------------------------------------------------
#     # Compare every unique specification
#     # ---------------------------------------------------------

#     all_keys = sorted(set(source_1.keys()) | set(source_2.keys()))

#     results = []

#     for key in all_keys:

#         field_1 = source_1.get(key)
#         field_2 = source_2.get(key)

#         # -----------------------------------------------------
#         # Source 1 only
#         # -----------------------------------------------------

#         if field_1 is not None and field_2 is None:

#             field_name = field_1.field_name
#             category = field_1.category

#             status = ReconciliationStatus.SOURCE_1_ONLY

#             explanation = (
#                 "This specification is present in source 1 but "
#                 "was not found in source 2."
#             )

#         # -----------------------------------------------------
#         # Source 2 only
#         # -----------------------------------------------------

#         elif field_1 is None and field_2 is not None:

#             field_name = field_2.field_name
#             category = field_2.category

#             status = ReconciliationStatus.SOURCE_2_ONLY

#             explanation = (
#                 "This specification is present in source 2 but "
#                 "was not found in source 1."
#             )

#         # -----------------------------------------------------
#         # Both sources
#         # -----------------------------------------------------

#         else:

#             assert field_1 is not None
#             assert field_2 is not None

#             # IMPORTANT:
#             # Source 1 is the canonical representation.
#             field_name = field_1.field_name
#             category = field_1.category

#             if _values_equal(
#                 field_1.normalized_value,
#                 field_2.normalized_value,
#             ):
#                 status = ReconciliationStatus.AGREES

#                 explanation = (
#                     "Both sources provide the same normalized value "
#                     "for this specification."
#                 )

#             else:
#                 status = ReconciliationStatus.CONFLICT

#                 explanation = (
#                     "Both sources provide this specification, but "
#                     "their normalized values are different."
#                 )


#         result = ReconciledField(
#             field_name=field_name,
#             category=category,
#             source_1=field_1,
#             source_2=field_2,
#             status=status,
#             explanation=explanation,
#         )

#         results.append(result)

#     return results

from collections import defaultdict

from schemas import (
    NormalizedField,
    ReconciledField,
    ReconciliationStatus,
)


def _field_key(field: NormalizedField) -> str:
    """
    Creates a stable comparison key from a canonical field name.
    """
    return field.field_name.strip().lower()


def _values_equal(
    value_1: str | float | int | bool,
    value_2: str | float | int | bool,
) -> bool:
    """
    Compare normalized values safely.

    Numeric values are compared numerically.
    Everything else is compared directly.
    """

    if isinstance(value_1, bool) or isinstance(value_2, bool):
        return value_1 == value_2

    if isinstance(value_1, (int, float)) and isinstance(value_2, (int, float)):
        return value_1 == value_2

    return str(value_1).strip().lower() == str(value_2).strip().lower()


def reconcile_fields(
    source_1_fields: list[NormalizedField],
    source_2_fields: list[NormalizedField],
) -> list[ReconciledField]:
    """
    Compare canonicalized fields from two source documents.

    The function does not guess mappings. Field mapping should already
    have happened before reconciliation.
    """

    source_1 = {_field_key(field): field for field in source_1_fields}
    source_2 = {_field_key(field): field for field in source_2_fields}

    all_keys = sorted(set(source_1) | set(source_2))

    results: list[ReconciledField] = []

    for key in all_keys:
        field_1 = source_1.get(key)
        field_2 = source_2.get(key)

        if field_1 is not None and field_2 is None:
            status = ReconciliationStatus.SOURCE_1_ONLY

            explanation = (
                "This specification is present in source 1 but "
                "was not found in source 2."
            )

        elif field_1 is None and field_2 is not None:
            status = ReconciliationStatus.SOURCE_2_ONLY

            explanation = (
                "This specification is present in source 2 but "
                "was not found in source 1."
            )

        else:
            assert field_1 is not None
            assert field_2 is not None

            if _values_equal(
                field_1.normalized_value,
                field_2.normalized_value,
            ):
                status = ReconciliationStatus.AGREES

                explanation = (
                    "Both sources provide the same normalized value "
                    "for this specification."
                )

            else:
                status = ReconciliationStatus.CONFLICT

                explanation = (
                    "Both sources provide this specification, but "
                    "their normalized values are different."
                )

        results.append(
            ReconciledField(
                field_name=(
                    field_1.field_name
                    if field_1 is not None
                    else field_2.field_name
                ),
                category=(
                    field_1.category
                    if field_1 is not None
                    else field_2.category
                ),
                source_1=field_1,
                source_2=field_2,
                status=status,
                explanation=explanation,
            )
        )

    return results