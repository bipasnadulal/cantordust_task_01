# from pathlib import Path

# from context_builder import build_document_context
# from llm_extractor import GroqExtractor
# from pdf_extractor import extract_pdf
# from product_identifier import find_5k_model


# INPUT_DIR = Path("data/input")


# def test_groq_extraction():

#     pdf_path = sorted(INPUT_DIR.glob("*.pdf"))[0]

#     document = extract_pdf(pdf_path)

#     model_result = find_5k_model(document)

#     assert model_result is not None

#     target_model = model_result["model"]

#     context = build_document_context(
#         document,
#         target_model=target_model,
#     )

#     extractor = GroqExtractor()

#     fields = extractor.extract(
#         context=context,
#         target_model=target_model,
#     )

#     assert isinstance(fields, list)

#     assert len(fields) > 0

#     for field in fields:

#         assert field.field_name

#         assert field.raw_value

#         assert field.evidence.document_name

#         assert field.evidence.page_number >= 1

#         print(
#             "\nFIELD:",
#             field.field_name,
#             "\nCATEGORY:",
#             field.category,
#             "\nRAW VALUE:",
#             field.raw_value,
#             "\nUNIT:",
#             field.unit,
#             "\nPAGE:",
#             field.evidence.page_number,
#             "\nEVIDENCE:",
#             field.evidence.source_text,
#         )

from pathlib import Path
from unittest.mock import MagicMock

from context_builder import build_document_context
from llm_extractor import GroqExtractor
from pdf_extractor import extract_pdf
from product_identifier import find_5k_model


INPUT_DIR = Path("data/input")


def test_groq_extraction(monkeypatch):

    pdf_path = sorted(INPUT_DIR.glob("*.pdf"))[0]

    document = extract_pdf(pdf_path)

    model_result = find_5k_model(document)

    assert model_result is not None

    target_model = model_result["model"]

    context = build_document_context(
        document,
        target_model=target_model,
    )

    # Mock Groq so this test does NOT consume API quota.
    mock_response = MagicMock()

    mock_response.choices[0].message.content = """
    {
        "fields": [
            {
                "field_name": "Max DC Input Power",
                "category": "electrical",
                "raw_value": "1100 W",
                "unit": "W",
                "evidence": {
                    "document_name": "datasheet_sun-4-12k-g06p3-eu-am2-p1_231007_en.pdf",
                    "page_number": 2,
                    "section": "Electrical Data",
                    "source_text": "Max. DC Input Power: 1100 W"
                }
            },
            {
                "field_name": "Max DC Input Voltage",
                "category": "electrical",
                "raw_value": "1000 V",
                "unit": "V",
                "evidence": {
                    "document_name": "datasheet_sun-4-12k-g06p3-eu-am2-p1_231007_en.pdf",
                    "page_number": 2,
                    "section": "Electrical Data",
                    "source_text": "Max. DC Input Voltage: 1000 V"
                }
            }
        ]
    }
    """

    mock_client = MagicMock()

    mock_client.chat.completions.create.return_value = mock_response

    # Replace Groq inside llm_extractor with our mock.
    monkeypatch.setattr(
        "llm_extractor.Groq",
        lambda api_key: mock_client,
    )

    # Avoid requiring the real API key for this unit test.
    monkeypatch.setenv(
        "GROQ_API_KEY",
        "test-key",
    )

    extractor = GroqExtractor()

    fields = extractor.extract(
        context=context,
        target_model=target_model,
    )

    assert isinstance(fields, list)

    assert len(fields) > 0

    for field in fields:

        assert field.field_name

        assert field.raw_value

        assert field.evidence.document_name

        assert field.evidence.page_number >= 1