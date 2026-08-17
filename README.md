# Datasheet Reconciliation Pipeline

# SunBridge Trading - Nepal Import Assessment (Task 1)

A Python-based document reconciliation pipeline for comparing two inverter datasheets for the same product.

The goal of this project is to extract important product specifications from two PDF documents, normalize the extracted information, compare the two sources, and produce a deterministic assessment showing where the documents agree, conflict, or require review.

## What the Pipeline Does

The pipeline follows these main steps:

1. Extract text and tables from both PDF datasheets.
2. Identify the target 5K inverter model.
3. Build relevant document context for the identified product.
4. Use an LLM to extract structured fields from each document.
5. Normalize values and units into a consistent representation.
6. Map different field names to common canonical names.
7. Reconcile the fields between the two sources.
8. Build a ground-truth matrix from the reconciliation results.
9. Generate a final assessment in JSON and text format.

The main idea is to keep the LLM responsible for **information extraction**, while the comparison and assessment logic is handled deterministically in Python.

## Project Structure

```text
cantordust_task1/
│
├── data/
│   └── input/
│       ├── datasheet_sun-4-12k-g06p3-eu-am2-p1_231007_en.pdf
│       └── datasheet_sun-4-15k-g06p3-eu-am2_240318_en.pdf
│
├── src/
│   ├── assessment.py
│   ├── context_builder.py
│   ├── field_mapper.py
│   ├── graph.py
│   ├── graph_nodes.py
│   ├── graph_state.py
│   ├── ground_truth.py
│   ├── llm_extractor.py
│   ├── normalizer.py
│   ├── output.py
│   ├── pdf_extractor.py
│   ├── product_identifier.py
│   ├── reconciler.py
│   ├── runner.py
│   └── schemas.py
│
├── tests/
│   ├── test_assessment.py
│   ├── test_context_builder.py
│   ├── test_field_mapper.py
│   ├── test_ground_truth.py
│   ├── test_llm_extractor.py
│   ├── test_normalizer.py
│   ├── test_product_identifier.py
│   ├── test_reconciler.py
│   └── test_schemas.py
│
├── output/
│   ├── assessment.json
│   └── assessment.txt
│
└── README.md
```

The workflow is implemented using LangGraph.

```
PDF Documents
     │
     ▼
Extract Documents
     │
     ▼
Identify Product
     │
     ▼
Build Context
     │
     ├───────────────┐
     ▼               ▼
Extract Source 1   Extract Source 2
     │               │
     └───────┬───────┘
             ▼
      Normalize Fields
             │
             ▼
     Canonicalize Fields
             │
             ▼
        Reconcile
             │
             ▼
      Ground Truth Matrix
             │
             ▼
         Assessment
             │
             ▼
       JSON / TXT Output

```

## Field Normalization

Extracted values are normalized before comparison.

For example:

1,100 → 1100
98.5% → 98.5
Yes → True
No → False
kW → kW
kw → kW
years → year

The original extracted value is still preserved as raw_value, so normalization does not remove the original evidence.

## Field Mapping

Different datasheets may use different names for the same specification.

For example:

Max. DC Input Power
Max DC Input Power
Max. PV Input Power
Max PV Input Power

are mapped to:

max_pv_input_power

The mapper only changes the field identity. It does not modify the value.

A conservative exact-alias approach is used instead of fuzzy matching to avoid accidentally treating different specifications as the same field.

## Reconciliation

After normalization and canonicalization, fields from both sources are compared.

The reconciliation process classifies fields into statuses such as:

AGREES
CONFLICTS
SOURCE 1 ONLY
SOURCE 2 ONLY
SEMANTICALLY EQUIVALENT
UNCERTAIN

This makes the comparison explicit instead of relying on the LLM to decide the final result.

## Ground Truth

The reconciled fields are used to create a ground-truth matrix.

This provides a deterministic representation of the expected comparison result and is then used by the final assessment step.

## Final Assessment

The final assessment contains:

identified product model
overall assessment status
total number of fields
number of agreements
number of conflicts
source-only fields
fields requiring review
supporting evidence from the documents

The assessment is generated in both:

output/assessment.json
output/assessment.txt

The JSON format is intended for machine-readable use, while the text output provides a more human-readable summary.

Running the Project

Create and activate the virtual environment:

python -m venv .venv
.venv\Scripts\Activate.ps1

Install the required dependencies:

pip install -r requirements.txt

Set the Groq API key:

$env:GROQ_API_KEY="your_api_key_here"

Run the assessment using the two source PDFs.

Running Tests

The project includes unit tests for the main parts of the pipeline.

Run all tests with:

```bash
pytest -v
```

The tests cover areas including:

PDF/product identification
document context building
schema validation
normalization
field mapping
reconciliation
ground-truth generation
final assessment
LLM extraction
Design Approach

A key design decision in this project was to separate extraction from decision-making.

The LLM is used to extract structured information from the documents because datasheets can have different layouts and wording.

After extraction, the rest of the pipeline uses deterministic Python logic for:

normalization
canonical field mapping
reconciliation
ground-truth generation
assessment

This makes the final comparison easier to test, understand, and reproduce.

Limitations

The current implementation is designed around the provided inverter datasheets and the target product identification logic.

Some fields may require additional aliases if future datasheets use different terminology.

The LLM extraction step also depends on the configured Groq API key and model response.

Output

The final results are available as:

output/assessment.json
output/assessment.txt
output/draft.md

These files contain the completed comparison and assessment for the two provided source documents, plus a human-readable draft for SunBridge's import agent.

Post-Submission Fix

A field-name canonicalization bug was found and fixed after the initial run: the extraction prompt did not force a single field-name format, so some LLM responses came back already snake_cased (e.g. "grid_regulation") while the alias table was keyed on natural-language wording (e.g. "grid regulation"). Snake_cased responses fell through to a near-no-op fallback instead of matching their alias, causing the same underlying spec from the two documents to be reported as two separate "only in one source" fields instead of one agree/conflict.

Fix: `field_mapper.canonicalize_field_name` now also tries the alias table with underscores/hyphens converted to spaces, and passes through values that are already exactly canonical. The extraction prompt was also tightened to request natural-language field names consistently (defense in depth). Four regression tests were added in `tests/test_field_mapper.py` covering this exact scenario.

Re-running the deterministic half of the pipeline (`reprocess.py`, no LLM call needed since extraction was already cached) against the original run's data changed the reconciliation from 76 fields / 9 agree / 67 one-source-only to 57 fields / 19 agree / 17 real conflicts / 21 one-source-only — a much more accurate picture of where the two datasheets actually agree, actually conflict, and are actually missing information.

Also added in this pass:

- `checklist_coverage` in the assessment output, explicitly reporting on all 5 of the brief's checklist categories (product identity, manufacturer identity, test evidence, labeling, importer paperwork) — including the ones with zero fields, with a stated reason and what to request instead of silently omitting them.
- A top-priority review item surfacing the model-code mismatch between sources (`SUN-5K-G06P3-EU-AM2-P1` vs `SUN-5K-G06P3-EU-AM2`), previously only visible as a single buried field row.
- `output/draft.md` — the human-readable, client-facing document the brief asks for, template-rendered from the same validated `AssessmentResult` as the JSON (so it can't drift from it).
- `confidence` / `extraction_note` fields on extracted/normalized fields (schema + prompt), for future runs to capture extraction-time uncertainty per field.
