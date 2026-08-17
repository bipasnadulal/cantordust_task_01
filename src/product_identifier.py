import re

from schemas import Evidence

MODEL_PATTERN = re.compile(
    r"SUN-\d+(?:K)?-G06P3-[A-Z0-9-]+",
    re.IGNORECASE,
)

def normalize_model(model: str) -> str:
    """
    Normalize whitespace and line breaks in a model name.
    """

    model = model.replace("\n", "")
    model = model.replace(" ", "")

    return model.strip()

def find_models(extracted_document: dict) -> list[dict]:
    """
    Find model identifiers appearing in the extracted PDF text.

    Handles model identifiers split across PDF line breaks.
    """

    models = []

    for page in extracted_document["pages"]:
        text = page["text"]

        # Join only line breaks that occur before the continuation
        # of a model identifier.
        normalized_text = re.sub(
            r"(SUN-\d+K-G06P3)\s*\n\s*(-EU-AM2(?:-P1)?)",
            r"\1\2",
            text,
            flags=re.IGNORECASE,
        )

        matches = MODEL_PATTERN.findall(normalized_text)

        for match in matches:
            model = normalize_model(match)

            models.append(
                {
                    "model": model,
                    "evidence": Evidence(
                        document_name=extracted_document["filename"],
                        page_number=page["page_number"],
                        source_text=match,
                    ),
                }
            )

    return models

def find_5k_model(extracted_document: dict) -> dict | None:
    """
    Find the first model containing 5K.
    """

    models = find_models(extracted_document)

    for item in models:

        model = item["model"].upper()

        if "5K" in model:
            return item

    return None

def model_comparison_key(model: str) -> str:
    """
    Create a conservative comparison key for model identity.

    This is used only to determine whether two model identifiers
    represent the same base product.

    Source model strings themselves are never modified.
    """

    normalized = normalize_model(model).upper()

    # P1 is a product variant suffix used by one of the source
    # datasheets. For identity comparison, compare the base model.
    if normalized.endswith("-P1"):
        normalized = normalized[:-3]

    return normalized