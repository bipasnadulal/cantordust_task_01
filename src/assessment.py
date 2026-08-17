from collections import Counter

from schemas import (
    AssessmentResult,
    ChecklistCoverage,
    FieldCategory,
    ReconciledField,
    ReconciliationStatus,
    ReviewItem,
    ReviewPriority,
)
from ground_truth import (
    determine_overall_status,
    build_review_items,
)

# The brief's 5-point checklist. Categories are reported on even when
# zero fields were found for them, with an explicit reason, rather than
# silently omitted.
CHECKLIST_CATEGORIES: list[tuple[FieldCategory, str]] = [
    (
        FieldCategory.PRODUCT_IDENTITY,
        "Not expected to be empty for a datasheet.",
    ),
    (
        FieldCategory.MANUFACTURER_IDENTITY,
        "Datasheets typically omit factory address/company registration "
        "details. Request from the manufacturer or a certificate of "
        "conformity directly.",
    ),
    (
        FieldCategory.TEST_EVIDENCE,
        "Datasheets summarize compliance but rarely embed test reports. "
        "Request the underlying test certificates (e.g. CE/IEC test "
        "reports) from the manufacturer or SunBridge's compliance file.",
    ),
    (
        FieldCategory.LABELING,
        "Physical label/nameplate content is not reproduced in a "
        "datasheet PDF. Request nameplate photos or the label artwork "
        "file directly.",
    ),
    (
        FieldCategory.IMPORTER_PAPERWORK,
        "Importer-of-record paperwork (e.g. customs declarations) is "
        "outside the scope of a manufacturer datasheet. Request from "
        "SunBridge's import/customs team.",
    ),
]


def build_checklist_coverage(
    reconciled_fields: list[ReconciledField],
    product_model: str | None = None,
) -> list[ChecklistCoverage]:
    """Address every item in the brief's checklist.

    ``present`` means the checklist topic is addressed in the assessment,
    not that the datasheets contain every requested document or field.
    This prevents genuine scope gaps (e.g. customs paperwork or nameplate
    photos) from being mistaken for extraction failures.
    """

    counts = Counter(field.category for field in reconciled_fields)

    notes = {
        FieldCategory.PRODUCT_IDENTITY: (
            "Target model/variant is identified; model-code differences are surfaced for review."
        ),
        FieldCategory.MANUFACTURER_IDENTITY: (
            "Manufacturer identity is part of the source evidence; verify legal/factory details against the final supplier documents."
        ),
        FieldCategory.TEST_EVIDENCE: (
            "Standards/compliance claims are extracted where present. Actual test certificates are not included in the datasheets and must be requested."
        ),
        FieldCategory.LABELING: (
            "Label-relevant information such as model, ratings and ingress protection is reported. Physical nameplate artwork/photos are not provided."
        ),
        FieldCategory.IMPORTER_PAPERWORK: (
            "Importer-side customs/commercial paperwork is outside the supplied datasheets and is explicitly flagged as follow-up."
        ),
    }

    coverage = []
    for category, _ in CHECKLIST_CATEGORIES:
        count = counts.get(category, 0)
        if category == FieldCategory.PRODUCT_IDENTITY and product_model:
            count = max(count, 1)
        if category == FieldCategory.TEST_EVIDENCE:
            count = max(count, counts.get(FieldCategory.STANDARDS, 0))

        coverage.append(
            ChecklistCoverage(
                category=category,
                field_count=count,
                present=True,
                note=notes[category],
            )
        )

    return coverage


def build_variant_review_item(
    model_1: str | None,
    model_2: str | None,
) -> ReviewItem | None:
    """
    Surface a model-code mismatch between the two source documents as
    an explicit, top-priority finding, rather than leaving it to be
    discovered inside a single buried field row.
    """

    if not model_1 or not model_2:
        return None

    if model_1.strip().upper() == model_2.strip().upper():
        return None

    return ReviewItem(
        field_name="model",
        category=FieldCategory.PRODUCT_IDENTITY,
        priority=ReviewPriority.CRITICAL,
        status=ReconciliationStatus.CONFLICT,
        description=(
            f"The two source documents identify the product with "
            f"different model codes: source 1 uses '{model_1}' and "
            f"source 2 uses '{model_2}'. This may mean the two "
            "documents describe different variants of the same base "
            "product rather than an identical part."
        ),
        recommendation=(
            "Confirm with the manufacturer/SunBridge whether these "
            "codes represent the same shippable unit or genuinely "
            "different variants before relying on either datasheet "
            "as authoritative for compliance."
        ),
        evidence=[],
    )


def build_assessment(
    product_model: str,
    source_documents: list[str],
    reconciled_fields: list[ReconciledField],
    source_1_model: str | None = None,
    source_2_model: str | None = None,
) -> AssessmentResult:
    """
    Build the final structured assessment result.

    This function combines:
    - reconciled specifications
    - overall comparison status
    - human review items
    - checklist coverage (including empty categories, with reasons)
    - deterministic summary

    No LLM call is made here.
    """

    review_items = build_review_items(reconciled_fields)

    variant_item = build_variant_review_item(
        source_1_model or product_model,
        source_2_model,
    )

    if variant_item is not None:
        review_items = [variant_item] + review_items

    priority_order = {
        ReviewPriority.CRITICAL: 0,
        ReviewPriority.HIGH: 1,
        ReviewPriority.MEDIUM: 2,
        ReviewPriority.LOW: 3,
    }

    review_items.sort(key=lambda item: priority_order[item.priority])

    checklist_coverage = build_checklist_coverage(reconciled_fields, product_model=product_model)

    overall_status = determine_overall_status(reconciled_fields)

    summary = build_summary(
        product_model=product_model,
        source_documents=source_documents,
        reconciled_fields=reconciled_fields,
        review_items=review_items,
        checklist_coverage=checklist_coverage,
    )

    return AssessmentResult(
        product_model=product_model,
        source_documents=source_documents,
        specifications=reconciled_fields,
        review_items=review_items,
        checklist_coverage=checklist_coverage,
        overall_status=overall_status,
        summary=summary,
    )


def build_summary(
    product_model: str,
    source_documents: list[str],
    reconciled_fields: list[ReconciledField],
    review_items: list[ReviewItem],
    checklist_coverage: list[ChecklistCoverage] | None = None,
) -> str:
    """
    Create a deterministic human-readable assessment summary.
    """

    status_counts = Counter(
        field.status for field in reconciled_fields
    )

    total = len(reconciled_fields)

    agrees = status_counts.get(
        ReconciliationStatus.AGREES,
        0,
    )

    equivalent = status_counts.get(
        ReconciliationStatus.SEMANTICALLY_EQUIVALENT,
        0,
    )

    conflicts = status_counts.get(
        ReconciliationStatus.CONFLICT,
        0,
    )

    source_1_only = status_counts.get(
        ReconciliationStatus.SOURCE_1_ONLY,
        0,
    )

    source_2_only = status_counts.get(
        ReconciliationStatus.SOURCE_2_ONLY,
        0,
    )

    uncertain = status_counts.get(
        ReconciliationStatus.UNCERTAIN,
        0,
    )

    internal_inconsistency = status_counts.get(
        ReconciliationStatus.INTERNAL_INCONSISTENCY,
        0,
    )

    status = determine_overall_status(reconciled_fields)

    summary_parts = [
        f"Product: {product_model}.",
        f"Compared {total} specification fields across "
        f"{len(source_documents)} source documents.",
        f"{agrees} fields agree.",
    ]

    if equivalent:
        summary_parts.append(
            f"{equivalent} fields are semantically equivalent."
        )

    if conflicts:
        summary_parts.append(
            f"{conflicts} fields conflict."
        )

    if source_1_only:
        summary_parts.append(
            f"{source_1_only} fields appear only in source 1."
        )

    if source_2_only:
        summary_parts.append(
            f"{source_2_only} fields appear only in source 2."
        )

    if uncertain:
        summary_parts.append(
            f"{uncertain} fields are uncertain."
        )

    if internal_inconsistency:
        summary_parts.append(
            f"{internal_inconsistency} fields contain internal inconsistencies."
        )

    if review_items:
        summary_parts.append(
            f"{len(review_items)} item(s) require human review."
        )
    else:
        summary_parts.append(
            "No fields require human review."
        )

    summary_parts.append(
        f"Overall assessment status: {status}."
    )

    if checklist_coverage:
        not_present = [c.category.value for c in checklist_coverage if not c.present]
        if not_present:
            summary_parts.append(
                "Checklist gaps remain for: "
                + ", ".join(not_present)
                + ". These are explicitly noted as follow-up items rather than treated as extraction failures."
            )

    return " ".join(summary_parts)