from pathlib import Path
from pdf_extractor import extract_pdf
from product_identifier import (find_5k_model, model_comparison_key)

INPUT_DIR = Path('data/input')

def test_find_5k_models():
    pdf_files = list(INPUT_DIR.glob("*.pdf"))
    assert len(pdf_files) >=2

    for pdf_path in pdf_files:
        document = extract_pdf(pdf_path)
        result = find_5k_model(document)
        assert result is not None
        assert "5K" in result['model'].upper()

        print(
            f"\n{pdf_path.name}"
            f"\n5K model: {result['model']}"
            f"\nPage: {result['evidence'].page_number}"
        )

def test_model_comparison_ignores_p1_variant_suffix():
    assert (
        model_comparison_key("SUN-5K-G06P3-EU-AM2-P1")
        == "SUN-5K-G06P3-EU-AM2"
    )


def test_model_comparison_preserves_different_models():
    assert (
        model_comparison_key("SUN-5K-G06P3-EU-AM2")
        != "SUN-6K-G06P3-EU-AM2"
    )