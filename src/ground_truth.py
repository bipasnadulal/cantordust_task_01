from collections import Counter

from schemas import (
    ReconciledField,
    ReconciliationStatus,
    ReviewItem,
    ReviewPriority,
    FieldCategory,
)


def build_ground_truth_matrix(
    reconciled_fields: list[ReconciledField],
) -> list[ReconciledField]:
    """
    Build the ground truth matrix from reconciled fields.

    The reconciliation results are already the source of truth.
    This function preserves them while ensuring a consistent
    field ordering.
    """

    return sorted(
        reconciled_fields,
        key=lambda field: (
            field.category.value,
            field.field_name.lower(),
        ),
    )


def determine_overall_status(
    reconciled_fields: list[ReconciledField],
) -> str:
    """
    Determine the overall status of the comparison.

    Priority:
    1. Internal inconsistency
    2. Conflict
    3. Uncertain
    4. Source-only
    5. Otherwise agrees
    """

    statuses = {field.status for field in reconciled_fields}

    if ReconciliationStatus.INTERNAL_INCONSISTENCY in statuses:
        return "conflict"

    if ReconciliationStatus.CONFLICT in statuses:
        return "conflict"

    if ReconciliationStatus.UNCERTAIN in statuses:
        return "uncertain"

    if (
        ReconciliationStatus.SOURCE_1_ONLY in statuses
        or ReconciliationStatus.SOURCE_2_ONLY in statuses
    ):
        return "incomplete"

    return "agrees"


def build_review_items(
    reconciled_fields: list[ReconciledField],
) -> list[ReviewItem]:
    """
    Convert important reconciliation findings into human-review items.
    """

    review_items = []

    for field in reconciled_fields:

        if field.status == ReconciliationStatus.CONFLICT:
            priority = ReviewPriority.HIGH

            description = (
                f"The value for '{field.field_name}' differs between "
                "the two source documents."
            )

            recommendation = (
                "Review both source documents and determine whether "
                "the difference represents a product revision, "
                "specification change, or extraction issue."
            )

        elif field.status == ReconciliationStatus.INTERNAL_INCONSISTENCY:
            priority = ReviewPriority.CRITICAL

            description = (
                f"An internal inconsistency was detected for "
                f"'{field.field_name}'."
            )

            recommendation = (
                "Manually inspect the source document because "
                "the specification appears internally inconsistent."
            )

        elif field.status == ReconciliationStatus.UNCERTAIN:
            priority = ReviewPriority.MEDIUM

            description = (
                f"The comparison for '{field.field_name}' "
                "could not be determined with sufficient confidence."
            )

            recommendation = (
                "Review the source evidence and verify the field manually."
            )

        elif field.status in (
            ReconciliationStatus.SOURCE_1_ONLY,
            ReconciliationStatus.SOURCE_2_ONLY,
        ):
            priority = ReviewPriority.LOW

            description = (
                f"'{field.field_name}' appears in only one "
                "of the two source documents."
            )

            recommendation = (
                "Check whether the specification was removed, added, "
                "renamed, or omitted in the other document."
            )

        else:
            continue

        review_items.append(
            ReviewItem(
                field_name=field.field_name,
                category=field.category,
                priority=priority,
                status=field.status,
                description=description,
                recommendation=recommendation,
                evidence=_collect_evidence(field),
            )
        )

    return review_items


def _collect_evidence(
    field: ReconciledField,
):
    """
    Collect evidence from both available sources.
    """

    evidence = []

    if field.source_1 is not None:
        evidence.append(field.source_1.evidence)

    if field.source_2 is not None:
        evidence.append(field.source_2.evidence)

    return evidence