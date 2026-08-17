from pathlib import Path

from pdf_extractor import extract_pdf

from schemas import AssessmentResult

from product_identifier import (find_5k_model, model_comparison_key)
from context_builder import build_document_context
from llm_extractor import GroqExtractor
from normalizer import normalize_fields
from field_mapper import canonicalize_fields
from reconciler import reconcile_fields
from ground_truth import build_ground_truth_matrix
from assessment import build_assessment
from draft import build_draft

from graph_state import AssessmentState

#adding the graph nodes
def identify_product(state: AssessmentState) -> dict:
    """
    Identify the target product model from both extracted documents.
    """

    source_1_result = find_5k_model(
        state["source_1_document"]
    )

    source_2_result = find_5k_model(
        state["source_2_document"]
    )

    if source_1_result is None:
        raise ValueError(
            "Could not identify 5K model in source 1."
        )

    if source_2_result is None:
        raise ValueError(
            "Could not identify 5K model in source 2."
        )

    model_1 = source_1_result["model"]
    model_2 = source_2_result["model"]

    if model_comparison_key(model_1) != model_comparison_key(model_2):
        raise ValueError(
            "Target models differ between source documents: "
            f"{model_1} vs {model_2}"
        )

    return {
        "product_model": model_1,
        "source_1_model": model_1,
        "source_2_model": model_2,
    }

def build_context(state: AssessmentState) -> dict:
    """
    Build LLM-readable context for both documents.
    """

    target_model = state["product_model"]

    source_1_context = build_document_context(
        state["source_1_document"],
        target_model=target_model,
    )

    source_2_context = build_document_context(
        state["source_2_document"],
        target_model=target_model,
    )

    return {
        "source_1_context": source_1_context,
        "source_2_context": source_2_context,
    }

def extract_source_1(state: AssessmentState) -> dict:
    """
    Extract structured fields from source 1.
    """

    extractor = GroqExtractor()

    fields = extractor.extract(
        context=state["source_1_context"],
        target_model=state["product_model"],
    )

    return {
        "source_1_extracted": fields,
    }

def extract_source_2(state: AssessmentState) -> dict:
    """
    Extract structured fields from source 2.
    """

    extractor = GroqExtractor()

    fields = extractor.extract(
        context=state["source_2_context"],
        target_model=state["product_model"],
    )

    return {
        "source_2_extracted": fields,
    }

def normalize_source_fields(
    state: AssessmentState,
) -> dict:
    """
    Normalize extracted fields from both sources.
    """

    source_1_normalized = normalize_fields(
        state["source_1_extracted"]
    )

    source_2_normalized = normalize_fields(
        state["source_2_extracted"]
    )

    return {
        "source_1_normalized": source_1_normalized,
        "source_2_normalized": source_2_normalized,
    }

def canonicalize_source_fields(
    state: AssessmentState,
) -> dict:
    """
    Convert field names to canonical names before reconciliation.
    """

    source_1_canonical = canonicalize_fields(
        state["source_1_normalized"]
    )

    source_2_canonical = canonicalize_fields(
        state["source_2_normalized"]
    )

    return {
        "source_1_canonical": source_1_canonical,
        "source_2_canonical": source_2_canonical,
    }

# def reconcile_sources(
#     state: AssessmentState,
# ) -> dict:
#     """
#     Compare canonicalized fields from both sources.
#     """

#     reconciled_fields = reconcile_fields(
#         state["source_1_canonical"],
#         state["source_2_canonical"],
#     )

#     return {
#         "reconciled_fields": reconciled_fields,
#     }

def reconcile_sources(
    state: AssessmentState,
) -> dict:
    """
    Compare canonicalized fields from both sources.
    """

    print("\n" + "=" * 80)
    print("SOURCE 1 CANONICAL FIELDS")
    print("=" * 80)

    for field in state["source_1_canonical"]:
        print(
            f"{field.field_name} | "
            f"raw={field.raw_value!r} | "
            f"normalized={field.normalized_value!r} | "
            f"unit={field.unit!r}"
        )

    print("\n" + "=" * 80)
    print("SOURCE 2 CANONICAL FIELDS")
    print("=" * 80)

    for field in state["source_2_canonical"]:
        print(
            f"{field.field_name} | "
            f"raw={field.raw_value!r} | "
            f"normalized={field.normalized_value!r} | "
            f"unit={field.unit!r}"
        )

    print("=" * 80)

    reconciled_fields = reconcile_fields(
        state["source_1_canonical"],
        state["source_2_canonical"],
    )

    return {
        "reconciled_fields": reconciled_fields,
    }


def build_ground_truth(
    state: AssessmentState,
) -> dict:
    """
    Build the deterministic ground-truth matrix.
    """

    matrix = build_ground_truth_matrix(
        state["reconciled_fields"]
    )

    return {
        "ground_truth": matrix,
    }

def create_assessment(
    state: AssessmentState,
) -> dict:
    """
    Build the final deterministic assessment.
    """

    assessment = build_assessment(
        product_model=state["product_model"],
        source_documents=state["source_documents"],
        reconciled_fields=state["ground_truth"],
        source_1_model=state.get("source_1_model"),
        source_2_model=state.get("source_2_model"),
    )

    return {
        "assessment": assessment,
    }

def generate_draft(
    state: AssessmentState,
) -> dict:
    """
    Build the human-readable, client-facing draft document from the
    already-validated assessment (deterministic template rendering,
    same as create_assessment — no LLM call).
    """

    draft = build_draft(
        assessment=state["assessment"],
        source_documents=state["source_documents"],
    )

    return {
        "draft": draft,
    }

def extract_documents(state: AssessmentState) -> dict:
    """
    Extract text and tables from both source PDFs.
    """

    documents = state["source_documents"]

    if len(documents) != 2:
        raise ValueError(
            "Assessment requires exactly two source documents."
        )

    source_1_document = extract_pdf(
        Path(documents[0])
    )

    source_2_document = extract_pdf(
        Path(documents[1])
    )

    return {
        "source_1_document": source_1_document,
        "source_2_document": source_2_document,
    }