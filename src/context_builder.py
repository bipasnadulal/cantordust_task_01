from schemas import Evidence


def build_page_context(page: dict) -> str:
    """
    Convert one extracted PDF page into structured LLM-readable text.

    The original page text and extracted tables are kept separate.
    """

    sections = []

    sections.append(
        f"PAGE {page['page_number']} "
    )


    sections.append("\n--- PAGE TEXT ---\n")

    text = page.get("text", "").strip()

    if text:
        sections.append(text)
    else:
        sections.append("[No text extracted from this page]")

  

    layout = page.get("layout_table")
    if layout:
        sections.append("\n--- LAYOUT-PRESERVED MULTI-MODEL TABLE ---\n")
        models = layout["models"]
        target_index = layout.get("target_index")
        sections.append("MODEL COLUMNS: " + " | ".join(f"{i+1}:{m}" for i, m in enumerate(models)))
        if target_index is not None:
            sections.append(f"TARGET MODEL COLUMN: {target_index + 1}")
        for row_index, row in enumerate(layout["rows"], start=1):
            values = row["values"]
            target_value = row.get("target_value", "")
            sections.append(
                f"TABLE ROW {row_index}: VALUES: " + " | ".join(values)
                + f" || TARGET MODEL VALUE: {target_value or '[shared/unclear]'}"
            )

    tables = page.get("tables", [])

    if tables:

        sections.append("\n--- EXTRACTED TABLES ---\n")

        for table_index, table in enumerate(tables, start=1):

            sections.append(
                f"--- TABLE {table_index} ---"
            )

            for row in table:

                row_values = [
                    str(value).strip() if value is not None else ""
                    for value in row
                ]

                sections.append(
                    " | ".join(row_values)
                )

    else:

        sections.append(
            "\n--- EXTRACTED TABLES ---\n"
            "[No tables extracted from this page]"
        )

    return "\n".join(sections)


def build_document_context(
    extracted_document: dict,
    target_model: str | None = None,
) -> str:
    """
    Build the complete context that can later be supplied to the LLM.
    """

    sections = []

    sections.append(
        " DOCUMENT INFORMATION "
    )

    sections.append(
        f"Document: {extracted_document['filename']}"
    )

    sections.append(
        f"Total pages: {extracted_document['page_count']}"
    )

    if target_model:

        sections.append(
            f"Target model: {target_model}"
        )

    sections.append(
        "\n DOCUMENT CONTENT "
    )

    for page in extracted_document["pages"]:

        sections.append(
            build_page_context(page)
        )

    return "\n\n".join(sections)