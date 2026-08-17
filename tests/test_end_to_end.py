# from pathlib import Path

# from graph import build_assessment_graph


# INPUT_DIR = Path("data/input")


# def test_full_assessment_pipeline():

#     pdfs = sorted(INPUT_DIR.glob("*.pdf"))

#     assert len(pdfs) == 2

#     graph = build_assessment_graph()

#     result = graph.invoke(
#         {
#             "source_documents": [
#                 str(pdfs[0]),
#                 str(pdfs[1]),
#             ]
#         }
#     )

#     # ---------------------------------------------------------
#     # Product identification
#     # ---------------------------------------------------------

#     assert result["product_model"] == (
#         "SUN-5K-G06P3-EU-AM2-P1"
#     )

#     # ---------------------------------------------------------
#     # PDF extraction
#     # ---------------------------------------------------------

#     assert result["source_1_document"]
#     assert result["source_2_document"]

#     # ---------------------------------------------------------
#     # LLM extraction
#     # ---------------------------------------------------------

#     assert result["source_1_extracted"]
#     assert result["source_2_extracted"]

#     # ---------------------------------------------------------
#     # Normalization
#     # ---------------------------------------------------------

#     assert result["source_1_normalized"]
#     assert result["source_2_normalized"]

#     # ---------------------------------------------------------
#     # Canonicalization
#     # ---------------------------------------------------------

#     assert result["source_1_canonical"]
#     assert result["source_2_canonical"]

#     # ---------------------------------------------------------
#     # Reconciliation
#     # ---------------------------------------------------------

#     assert result["reconciled_fields"]

#     # ---------------------------------------------------------
#     # Final assessment
#     # ---------------------------------------------------------

#     assert result["assessment"] is not None

#     assert (
#         result["assessment"].product_model
#         == "SUN-5K-G06P3-EU-AM2-P1"
#     )

#     assert result["assessment"].specifications

#     print("\n=== END-TO-END ASSESSMENT ===")
#     print(result["assessment"].summary)

from pathlib import Path

from graph import build_assessment_graph
from schemas import Evidence, ExtractedField


INPUT_DIR = Path("data/input")


def fake_extract(
    self,
    context: str,
    target_model: str,
) -> list[ExtractedField]:

    assert target_model == "SUN-5K-G06P3-EU-AM2-P1"
    """
    Deterministic replacement for GroqExtractor.extract().

    This keeps the E2E test independent of:
    - Groq API availability
    - API keys
    - token limits
    - network failures
    - model response variability

    The real LangGraph pipeline still runs all downstream stages.
    """

    # Determine which source document this context belongs to.
    if "datasheet_sun-4-12k-g06p3-eu-am2-p1_231007_en.pdf" in context:
        document_name = (
            "datasheet_sun-4-12k-g06p3-eu-am2-p1_231007_en.pdf"
        )
        page_number = 2

    elif "datasheet_sun-4-15k-g06p3-eu-am2_240318_en.pdf" in context:
        document_name = (
            "datasheet_sun-4-15k-g06p3-eu-am2_240318_en.pdf"
        )
        page_number = 2

    else:
        raise AssertionError(
            "Mock extractor received an unknown document context."
        )

    evidence = lambda text: Evidence(
        document_name=document_name,
        page_number=page_number,
        section="Electrical",
        source_text=text,
    )

    return [
        ExtractedField(
            field_name="Max. DC Input Voltage",
            category="electrical",
            raw_value="1100",
            unit="V",
            evidence=evidence(
                "Max. DC Input Voltage: 1100 V"
            ),
        ),
        ExtractedField(
            field_name="Max. DC Input Current",
            category="electrical",
            raw_value="20",
            unit="A",
            evidence=evidence(
                "Max. DC Input Current: 20 A"
            ),
        ),
        ExtractedField(
            field_name="Max. Efficiency",
            category="performance",
            raw_value="98.2%",
            unit="%",
            evidence=evidence(
                "Max. Efficiency: 98.2%"
            ),
        ),
    ]


def test_full_assessment_pipeline(monkeypatch):
    """
    Test the complete LangGraph assessment pipeline.

    Only the external Groq extraction call is mocked.
    Everything else runs for real.
    """

    pdfs = sorted(INPUT_DIR.glob("*.pdf"))

    assert len(pdfs) == 2

    # ---------------------------------------------------------
    # Mock only the external LLM call.
    # ---------------------------------------------------------

    monkeypatch.setattr(
        "graph_nodes.GroqExtractor.extract",
        fake_extract,
    )

    # ---------------------------------------------------------
    # Build the real LangGraph.
    # ---------------------------------------------------------

    graph = build_assessment_graph()

    # ---------------------------------------------------------
    # Invoke the real pipeline.
    # ---------------------------------------------------------

    result = graph.invoke(
        {
            "source_documents": [
                str(pdfs[0]),
                str(pdfs[1]),
            ]
        }
    )

    # ---------------------------------------------------------
    # Verify final graph state.
    # ---------------------------------------------------------

    assert result["product_model"] == (
    "SUN-5K-G06P3-EU-AM2-P1"
)

    assert "assessment" in result

    assessment = result["assessment"]

    assert assessment.product_model == (
    "SUN-5K-G06P3-EU-AM2-P1"
)

    assert len(assessment.specifications) == 3

    # ---------------------------------------------------------
    # Verify reconciliation.
    # ---------------------------------------------------------

    statuses = {
        field.field_name: field.status.value
        for field in assessment.specifications
    }

    assert statuses["max_pv_input_voltage"] == "agrees"
    assert statuses["max_pv_input_current"] == "agrees"
    assert statuses["max_efficiency"] == "agrees"

    # ---------------------------------------------------------
    # Verify final assessment.
    # ---------------------------------------------------------

    assert assessment.overall_status == "agrees"

    assert assessment.review_items == []

    assert "Product: SUN-5K-G06P3-EU-AM2-P1." in (
    assessment.summary
)

    assert "3 specification fields" in (
        assessment.summary
    )

    assert "3 fields agree" in (
        assessment.summary
    )

    assert "No fields require human review." in (
        assessment.summary
    )