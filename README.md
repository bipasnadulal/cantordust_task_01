# Cantordust Task 1 - Datasheet Assessment Pipeline

A small prototype pipeline for extracting and comparing inverter specifications from two manufacturer datasheets.

The project takes two PDF datasheets, extracts their information, normalizes and maps the fields into a common structure, compares the two sources, and produces both machine-readable and human-readable assessment files.

The main goal of the implementation is to keep the source information traceable and make differences visible instead of silently guessing which value is correct.

---

## Project Status

**Prototype — working end-to-end, but still needs improvement.**

The complete pipeline is currently working from PDF input to final assessment output.

The main remaining limitation is PDF/table extraction. The supplied datasheets contain multiple model columns and complex layouts, so some values are not always associated with the correct model column during extraction.

Because of this, the final assessment should be treated as a draft that can identify useful agreements and potential conflicts, rather than as a final compliance decision.

---

## What the project currently does

The pipeline currently performs these steps:

```text
PDF 1
   \
    → PDF extraction
   /
PDF 2
     ↓
Target model identification
     ↓
Document context building
     ↓
LLM-based field extraction
     ↓
Value/unit normalization
     ↓
Canonical field mapping
     ↓
Cross-source reconciliation
     ↓
Ground-truth comparison matrix
     ↓
Assessment generation
     ↓
assessment.json
assessment.txt
draft.md
```

The pipeline is implemented using LangGraph for the main workflow.

# Features implemented

## 1. PDF extraction

The project extracts text and available table information from both PDF files.

The extraction also keeps information such as:

- page number
- section
- source text
- table information when available

This allows later stages to attach evidence to extracted fields.

### Current limitation

The PDFs are not simple one-column documents. Several technical specification tables contain multiple inverter models in the same table.

Because PDF extraction does not always preserve the original visual relationship between:

Specification → Model Column → Value

some extracted values can occasionally be associated with the wrong model.

This is currently the biggest limitation of the pipeline.

## 2. Product identification

The project identifies the target 5 kW model from each source document.

The current documents contain:

Source 1: SUN-5K-G06P3-EU-AM2-P1

Source 2: SUN-5K-G06P3-EU-AM2

The pipeline preserves these source-specific model names instead of modifying the original extracted values.

A comparison key is used when checking whether the two model identifiers belong to the same target product.

## 3. Context building

The extracted document information is converted into an LLM-readable context.

The context is built around the target model so that the extractor can focus on the relevant parts of the datasheets.

This is especially useful because the PDFs contain information for several inverter models.

## 4. LLM extraction

The project uses Groq for structured extraction.

The LLM returns structured fields instead of simply returning a paragraph of text.

An extracted field contains information such as:

- field_name
- category
- raw_value
- unit
- evidence

The LLM is mainly responsible for interpreting the document and extracting information.

The final comparison and assessment are handled by deterministic Python code.

## 5. Value normalization

Extracted values are normalized before comparison.

Examples:
"5" → 5
"5.5" → 5.5
"1,100" → 1100
"98.5%" → 98.5
"Yes" → True
"No" → False

Common unit formatting is also normalized:

- kw → kW
- v → V
- a → A
- hz → Hz
- db → dB
- years → year

The original raw_value is retained so that normalization does not remove the original source information.

## 6. Canonical field mapping

Different datasheets can use different names for the same specification.

The project maps these names into common field names.

For example:
Max. DC Input Power
Max. PV Input Power
↓
max_pv_input_power

Another example:
MPPT Operating Range
MPPT Voltage Range
↓
mppt_voltage_range

Other mappings include:
Noise
Noise Emission
↓
noise_emission

and:

Grid Connection Standard
Grid Regulation
↓
grid_connection_standard

This prevents simple naming differences from being incorrectly reported as conflicts.

The mapper uses explicit aliases rather than aggressive fuzzy matching. This was intentional because an incorrect fuzzy match could combine two different specifications.

## 7. Reconciliation

After normalization and canonicalization, fields from both sources are compared.

The pipeline currently distinguishes between:

- agrees
- conflict
- semantically_equivalent
- source_1_only
- source_2_only
- internal_inconsistency

This is useful because a field appearing in only one document is not automatically considered a product conflict.

For example:
Field exists in Source 1
Field does not exist in Source 2
is reported as:
source_1_only

rather than automatically being treated as a specification disagreement.

## 8. Ground-truth matrix

The reconciliation results are converted into a deterministic comparison matrix.

The matrix keeps:

- canonical field name
- Source 1 value
- Source 2 value
- comparison status
- source evidence

The final assessment is therefore based on the structured comparison rather than asking the LLM to decide the final result.

## 9. Assessment generation

The assessment layer produces the final result from the reconciliation data.

The output includes:

- overall status
- summary
- conflicts
- source-only fields
- internal inconsistencies
- priorities
- recommendations
- evidence
- checklist coverage

Important source-only fields are kept in the output instead of being treated as failures.

## 10. Output files

The pipeline produces three main outputs.

**assessment.json**

Machine-readable version of the assessment.

It contains structured information about:

- extracted fields
- reconciliation
- conflicts
- source-only information
- evidence
- recommendations
- checklist coverage
- final assessment

This can be used by another program or agent later.

**assessment.txt**

Human-readable version of the assessment.

It presents the comparison in a simpler format, including:

- SUMMARY
- MATERIAL REVIEW ITEMS
- SOURCE-ONLY INFORMATION
- COMPARISON MATRIX

**draft.md**

A more readable compliance-style draft generated from the assessment information.

It is intended to make the extracted result easier for a human to review.

## Current results

The current pipeline is able to successfully run through the entire workflow:

```
PDF input
↓
Extraction
↓
LLM extraction
↓
Normalization
↓
Canonicalization
↓
Reconciliation
↓
Assessment
↓
Output files
```

The generated output is therefore not manually written. It is produced from the supplied datasheets by the pipeline.

The current results contain a mixture of:

- correctly matched fields
- semantically equivalent fields
- genuine-looking differences
- source-only fields
- extraction-related differences
- fields requiring human review

This is expected at the current prototype stage.

## What is working well

The following parts are currently working:

- PDF files can be processed automatically.
- The target 5 kW model can be identified.
- Both source documents are processed independently.
- LLM extraction produces structured fields.
- Evidence is retained with extracted fields.
- Values and units are normalized.
- Different field names can be mapped to common names.
- Fields can be compared across the two documents.
- Source-only information is preserved.
- Conflicts are explicitly reported.
- Semantic equivalents can be identified.
- The comparison is converted into a deterministic matrix.
- JSON output is generated.
- Human-readable TXT output is generated.
- Markdown draft output is generated.
- The complete process is connected through LangGraph.

## What is not perfect yet

### PDF table/model-column extraction

This is the main weakness.

The datasheets contain multiple models in the same technical tables.

For example, the PDF may visually look like:
Specification 5K 6K 8K 10K

Max Input Power 6.5 ... ... ...

but the extracted PDF text may lose some of that column relationship.

The system can then see the correct row but have difficulty determining exactly which value belongs to the target 5K column.

This can create false conflicts or incorrect values.

### Some field names still require better semantic mapping

The canonical alias system has been improved considerably, but not every possible variation of a datasheet field is covered.

For example, two fields can be technically related without having exactly the same wording.

The current implementation handles a useful set of known aliases but does not attempt unrestricted semantic matching.

### Some conflicts may actually be extraction problems

A reported conflict does not necessarily mean the manufacturer changed the specification.

It can also mean:

PDF layout
↓
incorrect column association
↓
different extracted value
↓
reported conflict

For this reason, conflict results should be checked against the original PDF before being treated as confirmed product differences.

### Checklist information can be incomplete

Some information is simply not available in the supplied datasheets.

For example, physical labeling, complete importer paperwork, or actual laboratory test certificates cannot be reliably confirmed when those materials are not present in the input documents.

The pipeline reports these limitations instead of inventing information.

## Why the project keeps uncertainty

The pipeline intentionally does not hardcode the expected answers.

It would be possible to manually insert known values and make the final output look cleaner, but that would hide whether the extraction pipeline actually works.

Instead, the project keeps:

- raw value
- normalized value
- canonical field
- source evidence
- comparison status

This makes it possible to inspect where a result came from and identify where the pipeline needs improvement.

## Project structure

```
cantordust_task1/
│
├── data/
│ └── input/
│ ├── datasheet_sun-4-12k-g06p3-eu-am2-p1_231007_en.pdf
│ └── datasheet_sun-4-15k-g06p3-eu-am2_240318_en.pdf
│
├── src/
│ ├── assessment.py
│ ├── context_builder.py
│ ├── field_mapper.py
│ ├── graph.py
│ ├── graph_nodes.py
│ ├── graph_state.py
│ ├── ground_truth.py
│ ├── llm_extractor.py
│ ├── normalizer.py
│ ├── output.py
│ ├── pdf_extractor.py
│ ├── product_identifier.py
│ ├── reconciler.py
│ └── schemas.py
│
├── main.py
├── requirements.txt
├── README.md
└── outputs/
├── assessment.json
├── assessment.txt
└── draft.md
```

## Setup and installation

### 1. Clone the repository

Open PowerShell or a terminal and run:

```bash
git clone https://github.com/bipasnadulal/cantordust_task_01
```

Then enter the project directory:

```bash
cd cantordust_task1
```

### 2. Create a virtual environment

On Windows:

```bash
python -m venv .venv
```

### 3. Activate the virtual environment

.venv\Scripts\Activate.ps1

After activation, the terminal should show something similar to:

(.venv) PS C:...\cantordust_task1>

If PowerShell blocks activation, you can use:

Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

and then activate again:

.venv\Scripts\Activate.ps1

### Install dependencies

Run:

```bash
pip install -r requirements.txt
```

This installs the libraries required by the project.

### Configure the Groq API key

The LLM extraction stage requires a Groq API key.

For the current PowerShell session:

```bash
$env:GROQ_API_KEY="your_groq_api_key"
```

For example:

```bash
$env:GROQ_API_KEY="gsk_xxxxxxxxxxxxxxxxx"
```

### Run the project

Make sure the virtual environment is active.

Then run:

```bash
python main.py   data/input/datasheet_sun-4-12k-g06p3-eu-am2-p1_231007_en.pdf
data/input/datasheet_sun-4-15k-g06p3-eu-am2_240318_en.pdf
```

The two paths are the two input datasheets.

### After running

The generated results can be inspected in the project's output location.

The main files to check are:

- assessment.json
- assessment.txt
- draft.md

The easiest file to read first is:
assessment.txt

Then inspect:
assessment.json

if you need the structured data.

The Markdown draft is useful when reviewing the result in a more readable format.

The important part is to check the generated evidence rather than judging the final number alone.

## Known improvement areas

If this project is continued, the first improvement should be the PDF extraction/model-column problem.

A stronger extraction layer should reconstruct the table more explicitly:

```
PDF table
↓
detect headers
↓
identify model columns
↓
identify target 5K column
↓
associate each row with the correct column
↓
send clean structured context to the LLM
```

This would likely improve the factual quality of the final comparison more than simply adding more field aliases.

Other useful future improvements would be:

- better extraction confidence scores
- stronger semantic comparison
- better handling of multi-value specifications
- validation rules for suspicious numerical values
- more precise source evidence
- better handling of document revisions
- automated regression tests using known extraction cases

## Final status

This is currently a working prototype rather than a production-ready compliance system.

The complete pipeline is implemented and executable, and it produces structured and human-readable results.

The strongest part of the system is the overall processing architecture:

```
Extract
↓
Identify
↓
Structure
↓
Normalize
↓
Map
↓
Compare
↓
Assess
```

The weakest part is the reliability of extracting values from complex multi-column PDF layouts.

The current output should therefore be used as a draft assessment and review aid, with suspicious conflicts checked against the original source documents.

The project is intentionally transparent about these limitations rather than presenting uncertain extraction results as guaranteed facts.
