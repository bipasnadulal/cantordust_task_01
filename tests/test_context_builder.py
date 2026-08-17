from pathlib import Path
from context_builder import build_document_context
from pdf_extractor import extract_pdf
from product_identifier import find_5k_model

INPUT_DIR = Path('data/input')

def test_build_document_context():
    pdf_files = list(INPUT_DIR.glob("*.pdf"))
    assert len(pdf_files) >= 2

    for pdf_path in pdf_files:

        document = extract_pdf(pdf_path)

        model_result = find_5k_model(document)

        assert model_result is not None

        context = build_document_context(
            document,
            target_model=model_result["model"],
        )

        assert document["filename"] in context

        assert model_result["model"] in context

        assert " PAGE" in context

        assert "--- PAGE TEXT ---" in context

        assert "--- EXTRACTED TABLES ---" in context

        print("\n" + "=" * 80)
        print(pdf_path.name)
        print("=" * 80)

        print(context[:5000])