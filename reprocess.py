"""
Re-run the deterministic half of the pipeline (canonicalize -> reconcile
-> ground truth -> assessment -> draft) against the ALREADY-EXTRACTED
data committed in output/assessment.json, using the fixed field_mapper
and the new checklist-coverage / variant-mismatch / draft logic.

This does not call Groq again. The original run already captured
source_1_normalized / source_2_normalized (pre-canonicalization) and
the raw parsed PDF documents, so everything downstream of extraction
can be rebuilt deterministically and compared against the original
(buggy) output.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from schemas import NormalizedField  # noqa: E402
from field_mapper import canonicalize_fields  # noqa: E402
from reconciler import reconcile_fields  # noqa: E402
from ground_truth import build_ground_truth_matrix  # noqa: E402
from assessment import build_assessment  # noqa: E402
from draft import build_draft  # noqa: E402
from product_identifier import find_5k_model  # noqa: E402
from output import save_json, save_report  # noqa: E402


def main():
    input_path = Path("output/assessment.json")
    cached = json.loads(input_path.read_text(encoding="utf-8"))

    source_1_normalized = [
        NormalizedField.model_validate(f) for f in cached["source_1_normalized"]
    ]
    source_2_normalized = [
        NormalizedField.model_validate(f) for f in cached["source_2_normalized"]
    ]

    # --- Re-canonicalize with the fixed field_mapper -----------------
    source_1_canonical = canonicalize_fields(source_1_normalized)
    source_2_canonical = canonicalize_fields(source_2_normalized)

    # --- Reconcile / ground truth (unchanged logic, now fed correct
    #     canonical names) -------------------------------------------
    reconciled_fields = reconcile_fields(source_1_canonical, source_2_canonical)
    ground_truth = build_ground_truth_matrix(reconciled_fields)

    # --- Recover exact per-source model codes for the variant callout
    source_1_model = find_5k_model(cached["source_1_document"])["model"]
    source_2_model = find_5k_model(cached["source_2_document"])["model"]

    product_model = cached["product_model"]
    source_documents = cached["source_documents"]

    assessment = build_assessment(
        product_model=product_model,
        source_documents=source_documents,
        reconciled_fields=ground_truth,
        source_1_model=source_1_model,
        source_2_model=source_2_model,
    )

    draft = build_draft(assessment=assessment, source_documents=source_documents)

    result = {
        "source_documents": source_documents,
        "source_1_document": cached["source_1_document"],
        "source_2_document": cached["source_2_document"],
        "product_model": product_model,
        "source_1_model": source_1_model,
        "source_2_model": source_2_model,
        "source_1_normalized": [f.model_dump() for f in source_1_normalized],
        "source_2_normalized": [f.model_dump() for f in source_2_normalized],
        "source_1_canonical": [f.model_dump() for f in source_1_canonical],
        "source_2_canonical": [f.model_dump() for f in source_2_canonical],
        "reconciled_fields": [f.model_dump() for f in reconciled_fields],
        "ground_truth": [f.model_dump() for f in ground_truth],
        "assessment": assessment,
        "draft": draft,
    }

    save_json(result, "output/assessment.json")
    save_report(result, "output/assessment.txt")
    Path("output/draft.md").write_text(draft, encoding="utf-8")

    # --- Print a before/after summary for sanity-checking -----------
    before_specs = cached["assessment"]["specifications"]
    before_status_counts = {}
    for s in before_specs:
        before_status_counts[s["status"]] = before_status_counts.get(s["status"], 0) + 1

    after_status_counts = {}
    for f in reconciled_fields:
        after_status_counts[f.status.value] = after_status_counts.get(f.status.value, 0) + 1

    print("BEFORE (buggy canonicalization):", len(before_specs), "fields ->", before_status_counts)
    print("AFTER  (fixed canonicalization): ", len(reconciled_fields), "fields ->", after_status_counts)
    print()
    print("Source 1 model:", source_1_model)
    print("Source 2 model:", source_2_model)
    print()
    print("Checklist coverage:")
    for c in assessment.checklist_coverage:
        print(f"  {c.category.value}: present={c.present} count={c.field_count}")


if __name__ == "__main__":
    main()
