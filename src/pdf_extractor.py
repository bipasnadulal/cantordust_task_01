from pathlib import Path

import pymupdf
import pdfplumber
import re



def _build_layout_preserved_table(page):
    """Build coordinate-aware model columns and target-column rows."""
    words = page.extract_words()
    model_words = [w for w in words if re.fullmatch(r"SUN-\d+K-G06P3", w["text"], re.I)]
    if len(model_words) < 2:
        return None

    model_words.sort(key=lambda w: w["x0"])
    models = [w["text"] for w in model_words]
    centers = [(w["x0"] + w["x1"]) / 2 for w in model_words]
    target_index = next((i for i, m in enumerate(models) if re.search(r"SUN-5K-G06P3", m, re.I)), None)

    # Use actual pdfplumber table cell coordinates where available. This is
    # more reliable than the flattened table text for multi-column rows.
    rows = []
    for table in page.find_tables():
        for row in table.rows:
            cells = []
            target_value = ""
            for cell in row.cells:
                if not cell:
                    cells.append("")
                    continue
                text = page.crop(cell).extract_text(x_tolerance=2, y_tolerance=2) or ""
                text = " ".join(text.split())
                cells.append(text)
                if text and target_index is not None:
                    center_x = (cell[0] + cell[2]) / 2
                    nearest = min(range(len(centers)), key=lambda i: abs(centers[i] - center_x))
                    if nearest == target_index:
                        target_value = text
            if cells and any(cells):
                rows.append({"values": cells, "target_value": target_value})

    return {
        "models": models,
        "target_index": target_index,
        "rows": rows,
    }

def extract_pdf(pdf_path: Path) -> dict:
    """
    Extract text and tables from every page of a PDF.

    Each page keeps its text and tables together so that
    we can preserve the evidence location.
    """

    pages = []

    with pymupdf.open(pdf_path) as text_pdf, pdfplumber.open(pdf_path) as table_pdf:

        page_count = len(text_pdf)

        for page_number in range(page_count):

            text_page = text_pdf[page_number]
            table_page = table_pdf.pages[page_number]

            text = text_page.get_text("text")

            tables = table_page.extract_tables()
            layout_table = _build_layout_preserved_table(table_page)

            pages.append(
                {
                    "page_number": page_number + 1,
                    "text": text,
                    "tables": tables,
                    "layout_table": layout_table,
                }
            )

    return {
        "filename": pdf_path.name,
        "path": str(pdf_path),
        "page_count": page_count,
        "pages": pages,
    }


def build_document_text(extracted_document: dict) -> str:
    """
    Build a clean text representation of the extracted PDF.

    Page boundaries are explicitly marked so that the LLM
    can retain page-level evidence.
    """

    sections = []

    for page in extracted_document["pages"]:

        page_number = page["page_number"]

        sections.append(
            f"\n===== PAGE {page_number} =====\n"
        )

        sections.append(page["text"])

    return "\n".join(sections)