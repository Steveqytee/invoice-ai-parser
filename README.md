# Invoice AI Parser - Enterprise Financial Reconciliation

An intelligent invoice parser and financial reconciliation system designed for enterprise automation. Automatically analyzes invoices and bank statements to detect anomalies, discrepancies, and audit issues.

## 🎯 Features

- **Intelligent Reconciliation**: Matches invoices to bank transactions with smart anomaly detection
- **Automated Audit**: Identifies critical issues like underpayments, missing payments, and overdue invoices
- **Color-Coded Alerts**: Visual alerts in terminal (🚨 CRITICAL, ⚠️ WARNING, ℹ️ INFO)
- **Comprehensive Reports**: Generates audit-ready CSV and JSON reports
- **Enterprise-Ready**: Built for financial teams, accountants, and CFOs

## 📊 What It Detects

| Issue | Severity | Example |
|-------|----------|---------|
| **Underpayment** | 🔴 CRITICAL | Invoice $22K, payment only $10K received |
| **Payment Missing** | 🔴 CRITICAL | Invoice marked paid but no bank record |
| **Unmatched Transactions** | 🟡 WARNING | Bank transfer with no invoice reference |
| **Overdue Payments** | 🟡 WARNING | Invoice past due date with no payment |
| **Reconciliation Gaps** | 🟡 WARNING | Invoice/bank amounts don't match |

## 🚀 Quick Start

### 1. Prepare Test Data

Create JSON files in `input/`:

**`input/invoices.json`** - Array of invoice objects with fields:
```json
{
  "invoice_id": "INV-2026-001",
  "order_id": "ORD-20260501-A001",
  "customer_name": "Company Name",
  "total_amount": 12100.00,
  "status": "paid|pending|overdue",
  "notes": "Payment notes"
}
```

**`input/bank_statements.json`** - Array of transaction objects:
```json
{
  "transaction_id": "TX-2026-0501-001",
  "reference": "ORD-20260501-A001",
  "amount": 12100.00,
  "transaction_date": "2026-05-08"
}
```

### 2. Run Parser

```bash
python3 scripts/invoice_ai_parser.py
```

### 3. Review Results

- **Terminal Output**: Colored audit summary with findings
- **`outputs/reconciliation_audit_report.csv`**: Formatted audit report for spreadsheets
- **`outputs/reconciliation_data.json`**: Structured data for integrations

## 📋 Example Output

```
📊 Invoice AI Parser - Enterprise Financial Reconciliation
============================================================
✓ Loaded 4 invoices
✓ Loaded 5 bank transactions

🚨 CRITICAL ISSUES FOUND: 1
⚠️  WARNINGS: 3

❌ [CRITICAL] UNDERPAYMENT
   Invoice: INV-2026-002 | Order: ORD-20260505-B002
   Issue: Invoice amount (22000.0) does not match bank payment (10000.0)
   Discrepancy: $-12,000.00
   Action: Contact customer to confirm payment amount
```

## 🤖 Smart Auditing Logic

The parser uses rule-based logic to:

1. **Match invoices to transactions** by order reference
2. **Detect amount mismatches** - flags if paid amount differs from invoice
3. **Find unmatched items** - invoices with no payment or transactions with no invoice
4. **Check payment status** - validates overdue invoices
5. **Calculate discrepancies** - provides $ amount of mismatches
6. **Prioritize alerts** - classifies by severity (CRITICAL vs WARNING)

## 💰 Real-World Use Cases

- **E-Commerce Finance**: Track customer payments vs. invoices
- **SaaS Billing**: Reconcile subscription payments
- **B2B Finance**: Audit enterprise contracts and POs
- **Accounting Automation**: Auto-detect manual entry errors
- **Fraud Detection**: Flag suspicious unmatched transactions

## 📁 Project Structure

```
.
├── input/
│   ├── invoices.json          # Your invoice data
│   └── bank_statements.json   # Your bank transactions
├── scripts/
│   └── invoice_ai_parser.py   # Main parser (runs reconciliation)
├── outputs/
│   ├── reconciliation_data.json         # Structured output
│   └── reconciliation_audit_report.csv  # Human-readable report
└── README.md
```

## 🔧 Customization

Edit `scripts/invoice_ai_parser.py` to:

- Add custom anomaly detection rules
- Modify severity thresholds (e.g., flag discrepancies > $500)
- Integrate with your accounting system API
- Add email alerts for CRITICAL findings

## 📌 Status Codes

| Status | Meaning |
|--------|---------|
| `matched` | Invoice matched to bank transaction with correct amount |
| `no_bank_match` | Invoice shows no corresponding bank transaction |
| `amount_mismatch` | Invoice and bank amount differ |
| `unmatched_tx` | Bank transaction with no matching invoice |

## 🛡️ Enterprise Features

✅ Comprehensive audit trail  
✅ Color-coded severity levels  
✅ CSV export for Excel/accounting software  
✅ JSON API-ready output  
✅ Reconciliation summary statistics  
✅ Detailed finding recommendations  

---

## 📚 Inspiration & References

This project was inspired by **ParserData's financial document processing framework**:
- **Ref**: https://github.com/parserdata/parserdata-ai-agents-integration
- **Concept**: Automated extraction and reconciliation of financial data
- **Approach**: Building scalable solutions for financial data quality and automation

While this is an independent implementation, the core inspiration came from ParserData's approach to handling financial documents and extraction workflows.

---

**Version**: 1.0  
**Use Case**: Enterprise Financial Automation  
**Tested Scenarios**: E-commerce invoicing, partial payments, overdue tracking, unmatched transactions
