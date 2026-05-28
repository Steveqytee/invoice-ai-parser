"""
parserdata_extract_prompt_json.py
---------------------------------
Batch-extract structured data from financial documents (PDFs and images) using the Parserdata API.
Uses prompt-based extraction easy to tweak without changing a schema.

Requirements:
    pip install requests

Usage:
    1. Set your API key and input folder in the CONFIGURATION section below.
    2. Run:  python parserdata_extract_prompt_json.py
"""

import glob
import json
import mimetypes
import os
import sys
from pathlib import Path

import requests

# ───────────────────────────────────────
#  CONFIGURATION (only edit this section)
# ───────────────────────────────────────

# Paste your Parserdata API key here, or set the PARSERDATA_API_KEY env var.
# Get a free key (35 credits) at: https://parserdata.com/?ref=dev
API_KEY = os.getenv("PARSERDATA_API_KEY", "your_api_key_here")

# Folder containing your invoices. Supports PDF, JPG, PNG, WebP.
# Examples:
#   Windows:  r"C:\Users\Admin\Downloads\invoices\*"
#   Mac/Linux: "/home/user/invoices/*"
INPUT_GLOB = r"C:\Users\Admin\Downloads\invoices\*"

# Prompt-based extraction: plain-English description of what to pull out.
# Edit freely, no schema syntax required.
# Tip: be specific about line item sub-fields to get the cleanest output.
PROMPT = (
    "Extract the following fields from this invoice: "
    "invoice number, invoice date, due date, vendor name, vendor address, "
    "buyer name, buyer address, line items (description, quantity, unit price, "
    "net amount), subtotal, tax amount, and total amount. "
    "Also extract payment terms and any reference numbers if present."
)

# Where to save individual JSON results. Defaults to an "extracted" subfolder
# next to this script.
OUTPUT_DIR = Path(__file__).parent.parent / "extracted"

# ────────────────────────────────────────
#  CONSTANTS (no edits needed below here)
# ────────────────────────────────────────

API_ENDPOINT  = "https://api.parserdata.com/v1/extract"
HEADERS       = {"X-API-Key": API_KEY}
SUPPORTED_EXT = {".pdf", ".png", ".jpg", ".jpeg", ".webp"}


# ─────────
#  HELPERS
# ─────────

def validate_config():
    """Fail fast with a clear message if configuration is missing."""
    if API_KEY == "your_api_key_here":
        sys.exit(
            "❌  No API key found.\n"
            "    Set PARSERDATA_API_KEY in your environment, or paste your key\n"
            "    into the API_KEY variable at the top of this script.\n"
            "    Get a free key at: https://parserdata.com/?ref=dev"
        )


def collect_files(pattern: str) -> list:
    """Glob for supported invoice files and return their Paths."""
    all_paths = glob.glob(pattern)
    files = [
        Path(p) for p in all_paths
        if Path(p).suffix.lower() in SUPPORTED_EXT and Path(p).is_file()
    ]
    if not files:
        sys.exit(
            f"❌  No supported files found matching: {pattern}\n"
            f"    Supported formats: {', '.join(SUPPORTED_EXT)}\n"
            "    Check your INPUT_GLOB path."
        )
    return files


def friendly_http_error(status_code: int, body: str) -> str:
    """Return a plain-English explanation for common Parserdata error codes."""
    messages = {
        400: "400 Bad Request: the request is invalid. "
             "Ensure you provide either a file (multipart), file_url, or file.content, "
             "and include either a prompt or a schema describing what to extract.",
        401: "401 Unauthorized: your API key was rejected. "
             "Re-copy it and check for extra spaces.",
        402: "402 Payment Required: your free credits are exhausted. "
             "Upgrade your plan at https://parserdata.com",
        404: "404 Not Found: the API endpoint does not exist. "
             "Check that you are calling https://api.parserdata.com/v1/extract",
        429: "429 Too Many Requests: you're hitting the rate limit. Wait and retry.",
        500: "500 Internal Server Error: Parserdata encountered an internal error. "
             "Try again shortly.",

        503: "503 Service Unavailable: the service is temporarily unavailable. "
             "Try again later.",
    }
    return messages.get(status_code, f"HTTP {status_code} - {body[:300]}")


def extract_one(file: Path):
    """
    Send a single invoice to the Parserdata API and return the parsed result,
    or None if the request failed.
    """
    mime = mimetypes.guess_type(str(file))[0] or "application/octet-stream"

    with file.open("rb") as f:
        response = requests.post(
            API_ENDPOINT,
            headers=HEADERS,
            files={"file": (file.name, f, mime)},
            data={"prompt": PROMPT},
            timeout=300,
        )

    if response.status_code != 200:
        print(f"  ❌  {friendly_http_error(response.status_code, response.text)}")
        return None

    return response.json()


def save_result(result: dict, source_file: Path) -> Path:
    """Write the extracted data to OUTPUT_DIR/<filename>.json."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / (source_file.stem + ".json")
    # Parserdata wraps data under "result"; unwrap it if present
    payload = result.get("result", result)
    with out_path.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)
    return out_path


def print_summary(result: dict):
    """Print a quick human-readable summary for one invoice."""
    payload = result.get("result", result)
    print(f"  Vendor  : {payload.get('vendor_name', '-')}")
    print(f"  Invoice#: {payload.get('invoice_number', '-')}")
    print(f"  Date    : {payload.get('invoice_date', '-')}")
    print(f"  Total   : {payload.get('total_amount', '-')}")
    items = payload.get("line_items", [])
    if isinstance(items, list):
        print(f"  Items   : {len(items)} line item(s) extracted")


# ──────
#  MAIN
# ──────

def main():
    validate_config()
    files = collect_files(INPUT_GLOB)

    print(f"\n📂  Found {len(files)} invoice(s) to process.")
    print(
        "ℹ️   Credit reminder: each page costs 1 credit (free tier = 35 credits).\n"
        "    Multi-page invoices count per page, keep an eye on your usage.\n"
    )

    succeeded, failed = 0, 0

    for file in files:
        print(f"\n{'-' * 55}")
        print(f"📄  {file.name}  ({file.stat().st_size / 1024:.1f} KB)")
        print("⏳  Extracting …")

        result = extract_one(file)

        if result is None:
            failed += 1
            continue

        out_path = save_result(result, file)
        print_summary(result)
        print(f"  💾  Saved -> {out_path}")
        succeeded += 1

    # Final report
    print(f"\n{'═' * 55}")
    print(f"✅  Done.  {succeeded} succeeded  |  {failed} failed")
    if succeeded:
        print(f"📁  Results saved in: {OUTPUT_DIR.resolve()}")
    if failed:
        print("⚠️   Check the error messages above for failed files.")
    print()


if __name__ == "__main__":
    main()
