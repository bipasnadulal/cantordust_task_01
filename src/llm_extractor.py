import json
import os
from dotenv import load_dotenv

from groq import Groq

from schemas import ExtractedField

load_dotenv()

class GroqExtractor:
    """
    Uses Groq to extract structured specification fields
    from prepared datasheet context.
    """

    def __init__(
        self,
        model: str = "llama-3.3-70b-versatile",
    ):
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise RuntimeError(
                "GROQ_API_KEY environment variable is not set."
            )

        self.client = Groq(api_key=api_key)
        self.model = model

    def extract(
        self,
        context: str,
        target_model: str,
    ) -> list[ExtractedField]:

        system_prompt = """
You are a technical datasheet extraction system.

Extract specification fields from the supplied datasheet evidence.

Rules:
1. Extract only information supported by the evidence.
2. Do not invent values.
3. Preserve raw values exactly as they appear.
4. Extract values belonging to the TARGET MODEL only.
5. Every field must include evidence.
6. Evidence must contain document name and page number.
7. Do not calculate, normalize, compare, or reconcile values.
8. If a value cannot confidently be mapped to the target model, omit it.
8a. When a LAYOUT-PRESERVED MULTI-MODEL TABLE is provided, use TARGET MODEL COLUMN and MODEL COLUMNS as the primary mapping evidence.
8b. For rows with multiple model values, select only the value aligned to the TARGET MODEL COLUMN.
9. Return ONLY valid JSON.
10. Do not use Markdown or code fences.
"""

        user_prompt = f"""
TARGET MODEL:
{target_model}

DOCUMENT EVIDENCE:
{context}

Extract the technical specifications for the TARGET MODEL.

Return a JSON object with a single key named "fields".

The value of "fields" must be an array.

Each item in the "fields" array must have exactly this structure:

{{
    "field_name": "exact field label as it appears in the document",
    "category": "allowed category",
    "raw_value": "exact source value",
    "unit": "unit or null",
    "evidence": {{
        "document_name": "PDF filename",
        "page_number": 2,
        "section": "section or table heading",
        "source_text": "short supporting excerpt"
    }},
    "confidence": "high | medium | low",
    "extraction_note": "why confidence is not high, or null"
}}

FIELD NAME FORMAT (important):
- "field_name" must be the field's natural-language label exactly as
  written in the document (e.g. "Max. DC Input Power",
  "Grid Connection Standard"), title case, with punctuation preserved.
- Do NOT snake_case, lowercase, or otherwise reformat it. A downstream
  step canonicalizes field names across documents, and it depends on
  receiving the document's own wording consistently.

CONFIDENCE:
- "high": the value was read directly and unambiguously.
- "medium": the value required minor interpretation (e.g. combining
  a split cell, resolving an abbreviation).
- "low": the value was read positionally out of a flattened,
  multi-column table (e.g. picking the column for the target model
  out of several power ratings on one row), or the mapping to the
  target model is not fully certain.

Allowed categories:
product_identity
electrical
performance
protection
general_data
interface
standards
labeling
other

IMPORTANT:
The datasheet contains multiple model columns.
Only extract values confidently associated with:
{target_model}

If the context contains TARGET MODEL COLUMN, use that column position explicitly.
Do not assume that the first value in a row belongs to the target model.
Prefer the layout-preserved rows over flattened table output when they disagree.

Return ONLY the JSON object.
"""

        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0,
            max_tokens=8000,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
        )

        content = response.choices[0].message.content

        if not content:
            raise RuntimeError(
                "Groq returned an empty response."
            )

        content = content.strip()


        try:
            data = json.loads(content)

        except json.JSONDecodeError as exc:
            raise RuntimeError(
                "Groq returned invalid or incomplete JSON.\n"
                f"Response:\n{content}"
            ) from exc

        
        if isinstance(data, dict):

            if "fields" in data:
                data = data["fields"]

            elif "data" in data:
                data = data["data"]

            elif "results" in data:
                data = data["results"]

            else:
                list_values = [
                    value
                    for value in data.values()
                    if isinstance(value, list)
                ]

                if len(list_values) == 1:
                    data = list_values[0]
                else:
                    raise RuntimeError(
                "Groq returned a JSON object, but no "
                "extractable field array was found."
            )

        if not isinstance(data, list):
            raise RuntimeError(
                "Expected Groq response to contain a JSON array "
                "of extracted fields."
            )


        extracted_fields = []

        for index, item in enumerate(data):

            if not item.get("raw_value"):
                continue

            raw_value = item.get("raw_value")

            if raw_value is None or str(raw_value).strip() == "":
                continue

            try:
                field = ExtractedField.model_validate(item)

            except Exception as exc:
                raise RuntimeError(
                    f"Invalid extracted field at index {index}:\n"
                    f"{item}"
                ) from exc

            extracted_fields.append(field)

        return extracted_fields