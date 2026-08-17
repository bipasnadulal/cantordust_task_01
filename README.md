# Cantordust Task 1 — Datasheet Assessment Pipeline

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
