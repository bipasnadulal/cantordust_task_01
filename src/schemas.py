from enum import Enum

from pydantic import BaseModel, Field, ConfigDict


class FieldCategory(str, Enum):
    """
    Broad category of a specification field.
    """

    PRODUCT_IDENTITY = "product_identity"
    ELECTRICAL = "electrical"
    PERFORMANCE = "performance"
    PROTECTION = "protection"
    GENERAL_DATA = "general_data"
    INTERFACE = "interface"
    STANDARDS = "standards"
    LABELING = "labeling"
    MANUFACTURER_IDENTITY = "manufacturer_identity"
    TEST_EVIDENCE = "test_evidence"
    IMPORTER_PAPERWORK = "importer_paperwork"
    OTHER = "other"


class ConfidenceLevel(str, Enum):
    """
    Extraction-time confidence for a single field value.
    """

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ReconciliationStatus(str, Enum):
    """
    Result of comparing information between two sources.
    """

    AGREES = "agrees"
    CONFLICT = "conflict"
    SOURCE_1_ONLY = "source_1_only"
    SOURCE_2_ONLY = "source_2_only"
    SEMANTICALLY_EQUIVALENT = "semantically_equivalent"
    INTERNAL_INCONSISTENCY = "internal_inconsistency"
    UNCERTAIN = "uncertain"


class ReviewPriority(str, Enum):
    """
    Priority of a finding for human review.
    """

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"



class Evidence(BaseModel):
    """
    Identifies where a piece of information came from.
    """

    document_name: str = Field(
        description="Name of the source PDF."
    )

    page_number: int = Field(
        ge=1,
        description="Page number where the evidence appears."
    )

    section: str | None = Field(
        default=None,
        description="Section or table heading associated with the evidence."
    )

    source_text: str = Field(
        description="Short excerpt from the source document supporting the value."
    )


class ExtractedField(BaseModel):
    """
    A specification value extracted from a document.
    """

    field_name: str = Field(
        description="Name of the specification field."
    )

    category: FieldCategory = Field(
        description="Category of the specification."
    )

    raw_value: str = Field(
        description="Value exactly as represented in the source document."
    )

    unit: str | None = Field(
        default=None,
        description="Unit associated with the value, if applicable."
    )

    evidence: Evidence = Field(
        description="Source evidence supporting the extracted value."
    )

    confidence: ConfidenceLevel = Field(
        default=ConfidenceLevel.MEDIUM,
        description=(
            "Extraction-time confidence. LOW means the value required "
            "positional/contextual reasoning (e.g. picking a column out "
            "of a flattened multi-model table) rather than an "
            "unambiguous direct read."
        ),
    )

    extraction_note: str | None = Field(
        default=None,
        description=(
            "Optional note explaining why confidence is not HIGH, e.g. "
            "'value read positionally from a multi-column table'."
        ),
    )


class NormalizedField(BaseModel):
    """
    A normalized representation of an extracted field.
    """

    field_name: str = Field(
        description="Canonical name of the specification field."
    )

    category: FieldCategory = Field(
        description="Category of the specification."
    )

    raw_value: str = Field(
        description="Original value from the source."
    )

    normalized_value: str | float | int | bool = Field(
        description="Normalized value used for comparison."
    )

    unit: str | None = Field(
        default=None,
        description="Normalized unit."
    )

    evidence: Evidence = Field(
        description="Evidence supporting the value."
    )

    confidence: ConfidenceLevel = Field(
        default=ConfidenceLevel.MEDIUM,
        description="Extraction-time confidence carried over from ExtractedField.",
    )

    extraction_note: str | None = Field(
        default=None,
        description="Optional note explaining low/medium confidence.",
    )



class ProductDocument(BaseModel):
    """
    Structured information about one datasheet.
    """

    document_name: str = Field(
        description="PDF filename."
    )

    manufacturer: str | None = Field(
        default=None,
        description="Manufacturer identified in the document."
    )

    model: str = Field(
        description="Exact product model identified in the document."
    )

    rated_power_kw: float | None = Field(
        default=None,
        description="Rated output power in kW."
    )

    fields: list[NormalizedField] = Field(
        default_factory=list,
        description="Normalized specification fields extracted from the document."
    )



class ReconciledField(BaseModel):
    """
    Comparison of one specification between two documents.
    """

    field_name: str = Field(
        description="Canonical field being compared."
    )

    category: FieldCategory = Field(
        description="Category of the field."
    )

    source_1: NormalizedField | None = Field(
        default=None,
        description="Value extracted from the first source."
    )

    source_2: NormalizedField | None = Field(
        default=None,
        description="Value extracted from the second source."
    )

    status: ReconciliationStatus = Field(
        description="Result of comparing the two sources."
    )

    explanation: str = Field(
        description="Reason for the reconciliation result."
    )


class ReviewItem(BaseModel):
    """
    A finding that may require human attention.
    """

    field_name: str = Field(
        description="Specification or issue being reviewed."
    )

    category: FieldCategory = Field(
        description="Category of the issue."
    )

    priority: ReviewPriority = Field(
        description="Importance of the issue."
    )

    status: ReconciliationStatus = Field(
        description="Classification of the finding."
    )

    description: str = Field(
        description="Human-readable explanation of the issue."
    )

    recommendation: str = Field(
        description="Recommended action for the reviewer."
    )

    evidence: list[Evidence] = Field(
        default_factory=list,
        description="Evidence supporting the finding."
    )


class ChecklistCoverage(BaseModel):
    """
    Coverage status of one item on the brief's 5-point checklist.
    """

    category: FieldCategory = Field(
        description="Checklist category being reported on."
    )

    field_count: int = Field(
        description="Number of reconciled fields found in this category."
    )

    present: bool = Field(
        description="Whether any field was found for this category."
    )

    note: str = Field(
        description=(
            "Why the category is empty and what to do about it, when "
            "present is False. Empty string when present is True."
        ),
    )


class AssessmentResult(BaseModel):
    """
    Final structured result produced by the assessment pipeline.
    """

    product_model: str

    source_documents: list[str]

    specifications: list[ReconciledField] = Field(
        default_factory=list
    )

    review_items: list[ReviewItem] = Field(
        default_factory=list
    )

    checklist_coverage: list[ChecklistCoverage] = Field(
        default_factory=list,
        description=(
            "Coverage of the brief's 5-point checklist (product identity, "
            "manufacturer identity, test evidence, labeling, importer "
            "paperwork), including categories with zero fields."
        ),
    )

    overall_status: str = Field(
        description="Overall assessment status."
    )

    summary: str = Field(
        description="Human-readable summary of the assessment."
    )