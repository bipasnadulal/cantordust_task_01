from typing import TypedDict

from schemas import (
    AssessmentResult,
    ExtractedField,
    NormalizedField,
    ReconciledField,
)

#here the AssessmentState as the graph's shared notebook. Each node reads what previous nodes produced and adds its own result
class AssessmentState(TypedDict, total=False):
    """
    Shared state passed between LangGraph nodes.
    """

    # Input
    source_documents: list[str]

    # Extracted PDF documents
    source_1_document: dict
    source_2_document: dict

    # Product identification
    product_model: str
    source_1_model: str
    source_2_model: str

    # LLM contexts
    source_1_context: str
    source_2_context: str

    # LLM extraction
    source_1_extracted: list[ExtractedField]
    source_2_extracted: list[ExtractedField]

    # Normalization
    source_1_normalized: list[NormalizedField]
    source_2_normalized: list[NormalizedField]

    # Canonicalization
    source_1_canonical: list[NormalizedField]
    source_2_canonical: list[NormalizedField]

    # Reconciliation
    reconciled_fields: list[ReconciledField]

    ground_truth: list[ReconciledField]

    # Final assessment
    assessment: AssessmentResult

    # Human-readable client-facing draft (Markdown)
    draft: str
