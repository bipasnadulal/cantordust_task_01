"""
Renders the human-readable, client-facing draft the brief asks for:
"the document SunBridge would actually hand to the import agent."

This is deterministic template rendering off the already-validated
AssessmentResult — it cannot drift from the structured JSON because it
is built from the same Pydantic objects, not from a separate LLM call.
"""

from schemas import (
    AssessmentResult,
    FieldCategory,
    ReconciliationStatus,
    ReviewPriority,
)

CATEGORY_TITLES = {
    FieldCategory.PRODUCT_IDENTITY: "Product Identity",
    FieldCategory.MANUFACTURER_IDENTITY: "Manufacturer Identity",
    FieldCategory.ELECTRICAL: "Electrical Specifications",
    FieldCategory.PERFORMANCE: "Performance",
    FieldCategory.PROTECTION: "Protection Features",
    FieldCategory.GENERAL_DATA: "General Data",
    FieldCategory.INTERFACE: "Interface",
    FieldCategory.STANDARDS: "Standards & Certifications",
    FieldCategory.TEST_EVIDENCE: "Test Evidence",
    FieldCategory.LABELING: "Labeling",
    FieldCategory.IMPORTER_PAPERWORK: "Importer Paperwork",
    FieldCategory.OTHER: "Other",
}

# Order the checklist-relevant categories the way the brief lists them,
# then everything else.
CATEGORY_ORDER = [
    FieldCategory.PRODUCT_IDENTITY,
    FieldCategory.MANUFACTURER_IDENTITY,
    FieldCategory.ELECTRICAL,
    FieldCategory.PERFORMANCE,
    FieldCategory.PROTECTION,
    FieldCategory.STANDARDS,
    FieldCategory.TEST_EVIDENCE,
    FieldCategory.LABELING,
    FieldCategory.IMPORTER_PAPERWORK,
    FieldCategory.GENERAL_DATA,
    FieldCategory.INTERFACE,
    FieldCategory.OTHER,
]

STATUS_LABELS = {
    ReconciliationStatus.AGREES: "Confirmed (both sources agree)",
    ReconciliationStatus.SEMANTICALLY_EQUIVALENT: "Confirmed (equivalent wording)",
    ReconciliationStatus.CONFLICT: "⚠ Conflicting values between sources",
    ReconciliationStatus.SOURCE_1_ONLY: "Only in source 1 — unconfirmed",
    ReconciliationStatus.SOURCE_2_ONLY: "Only in source 2 — unconfirmed",
    ReconciliationStatus.UNCERTAIN: "Uncertain",
    ReconciliationStatus.INTERNAL_INCONSISTENCY: "⚠ Internally inconsistent",
}


def _field_value(field) -> str:
    if field is None:
        return "—"

    value = f"{field.raw_value}"

    if field.unit:
        value += f" {field.unit}"

    return value


def _render_spec_row(spec) -> str:
    label = spec.field_name.replace("_", " ").title()
    value_1 = _field_value(spec.source_1)
    value_2 = _field_value(spec.source_2)
    status = STATUS_LABELS.get(spec.status, spec.status.value)

    return f"| {label} | {value_1} | {value_2} | {status} |"


def build_draft(assessment: AssessmentResult, source_documents: list[str]) -> str:
    lines: list[str] = []

    lines.append(f"# Compliance Draft — {assessment.product_model}")
    lines.append("")
    lines.append(
        "Prepared for SunBridge's import agent. This draft summarizes "
        "what the two supplier datasheets say about this inverter, "
        "where they agree, and what still needs to be confirmed before "
        "the paperwork is finalized."
    )
    lines.append("")
    lines.append("**Source documents:**")
    for doc in source_documents:
        lines.append(f"- {doc}")
    lines.append("")
    lines.append(f"**Overall status:** {assessment.overall_status}")
    lines.append("")

    # --- Top-line callouts: critical/high priority items first -----
    critical_items = [
        item
        for item in assessment.review_items
        if item.priority in (ReviewPriority.CRITICAL, ReviewPriority.HIGH)
    ]

    if critical_items:
        lines.append("## ⚠ What Needs Attention Before Filing")
        lines.append("")
        for item in critical_items:
            lines.append(f"- **{item.field_name}** ({item.priority.value}): {item.description}")
            lines.append(f"  - *Recommendation:* {item.recommendation}")
        lines.append("")

    # --- Checklist coverage -----------------------------------------
    lines.append("## Brief Checklist Coverage")
    lines.append("")
    lines.append("| Checklist item | Covered? | Notes |")
    lines.append("|---|---|---|")

    for cov in assessment.checklist_coverage:
        title = CATEGORY_TITLES.get(cov.category, cov.category.value)
        covered = f"Yes ({cov.field_count} field(s))" if cov.present else "No"
        note = cov.note if cov.note else "—"
        lines.append(f"| {title} | {covered} | {note} |")

    lines.append("")

    # --- Specifications by category ---------------------------------
    specs_by_category: dict[FieldCategory, list] = {}

    for spec in assessment.specifications:
        specs_by_category.setdefault(spec.category, []).append(spec)

    lines.append("## Specifications")
    lines.append("")

    for category in CATEGORY_ORDER:
        specs = specs_by_category.get(category, [])

        if not specs:
            continue

        title = CATEGORY_TITLES.get(category, category.value)
        lines.append(f"### {title}")
        lines.append("")
        lines.append("| Field | Source 1 | Source 2 | Status |")
        lines.append("|---|---|---|---|")

        for spec in sorted(specs, key=lambda s: s.field_name):
            lines.append(_render_spec_row(spec))

        lines.append("")

    # --- What's still unclear ----------------------------------------
    remaining = [
        item
        for item in assessment.review_items
        if item.priority not in (ReviewPriority.CRITICAL, ReviewPriority.HIGH)
    ]

    lines.append("## What's Still Unclear")
    lines.append("")

    if not remaining:
        lines.append("No additional open items beyond those flagged above.")
    else:
        for item in remaining:
            lines.append(f"- **{item.field_name}** ({item.priority.value}, {item.status.value}): {item.description}")

    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(assessment.summary)
    lines.append("")

    return "\n".join(lines)
