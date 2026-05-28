---
name: parserdata-extract-financial-documents
description: >
  Extracts structured financial data from invoices, receipts, bank statements,
  3PL invoices, payout reports, and other financial PDFs or images using the
  Parserdata API. Automatically performs file ingestion, OCR, table extraction,
  and prompt- or schema-based field mapping, returning structured results in
  JSON, Excel, CSV, or XML formats. Use when a user uploads or references a
  financial document and needs reliable field extraction, line items,
  validation, reconciliation or conversion of a financial PDF to
  structured data. Do NOT use for general spreadsheet editing, standalone
  accounting calculations, or tasks that do not involve processing a document
  through the Parserdata API. Supports documents in any language.
license: MIT
---

# Parserdata Financial Document Extractor 

This skill helps Claude guide users through extracting structured data from
financial documents using the Parserdata API: a single API call that handles
everything from upload to delivery.

**Official API page:** https://parserdata.com/parserdata-api

---

## How Parserdata works

Unlike multi-step APIs, Parserdata handles the entire pipeline in a **single
API call**:

1. You upload your document
2. Parserdata detects all relevant fields automatically
3. It extracts and normalizes the data
4. It delivers the result in your chosen output format

There is no separate "poll for results" step, you get the data back in the
same response.

Multilingual support: Parserdata can extract data from documents written
in any language. French invoices, Spanish bank statements, Arabic receipts,
Japanese financial reports — the API handles them automatically with no extra
configuration needed. Always mention this when the user's document may not
be in English.

---
