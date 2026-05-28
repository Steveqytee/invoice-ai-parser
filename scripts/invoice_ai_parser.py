#!/usr/bin/env python3
"""
Invoice AI Parser - Enterprise Financial Reconciliation & Audit
Parses invoices and bank statements, performs intelligent anomaly detection
"""
import json
import csv
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import List, Dict, Tuple
import sys

@dataclass
class AuditFinding:
    """Represents a single audit finding"""
    severity: str  # CRITICAL, WARNING, INFO
    category: str
    invoice_id: str
    order_id: str
    description: str
    amount_discrepancy: float = 0.0
    recommendation: str = ""

class InvoiceAIParser:
    def __init__(self, input_dir: Path, output_dir: Path):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.invoices: List[Dict] = []
        self.transactions: List[Dict] = []
        self.findings: List[AuditFinding] = []
        
    def load_data(self):
        """Load invoices and bank statements from JSON files"""
        # Load invoices
        invoices_file = self.input_dir / 'invoices.json'
        if invoices_file.exists():
            self.invoices = json.loads(invoices_file.read_text())
            print(f"✓ Loaded {len(self.invoices)} invoices")
        
        # Load bank statements
        bank_file = self.input_dir / 'bank_statements.json'
        if bank_file.exists():
            self.transactions = json.loads(bank_file.read_text())
            print(f"✓ Loaded {len(self.transactions)} bank transactions")
    
    def parse_and_reconcile(self) -> Dict:
        """Main reconciliation logic with AI-like intelligent auditing"""
        reconciliation = {
            'summary': {
                'total_invoices': len(self.invoices),
                'total_transactions': len(self.transactions),
                'total_invoice_amount': sum(inv.get('total_amount', 0) for inv in self.invoices),
                'total_bank_received': sum(tx.get('amount', 0) for tx in self.transactions if tx.get('amount', 0) > 0),
                'audit_timestamp': datetime.now().isoformat(),
            },
            'matched_items': [],
            'unmatched_invoices': [],
            'unmatched_transactions': [],
            'audit_findings': []
        }
        
        # Index transactions by order reference
        tx_by_ref = {tx.get('reference'): tx for tx in self.transactions}
        tx_matched = set()
        
        # Match each invoice with bank transactions
        for invoice in self.invoices:
            inv_id = invoice.get('invoice_id')
            order_id = invoice.get('order_id')
            inv_amount = invoice.get('total_amount', 0)
            inv_status = invoice.get('status', 'unknown')
            
            tx = tx_by_ref.get(order_id)
            
            if tx:
                tx_matched.add(tx.get('transaction_id'))
                tx_amount = tx.get('amount', 0)
                match_data = {
                    'invoice_id': inv_id,
                    'order_id': order_id,
                    'customer': invoice.get('customer_name'),
                    'invoice_amount': inv_amount,
                    'transaction_id': tx.get('transaction_id'),
                    'bank_amount': tx_amount,
                    'transaction_date': tx.get('transaction_date'),
                    'status': 'matched'
                }
                reconciliation['matched_items'].append(match_data)
                
                # INTELLIGENT AUDIT: Check for amount mismatches
                if abs(tx_amount - inv_amount) > 0.01:
                    discrepancy = tx_amount - inv_amount
                    finding = AuditFinding(
                        severity='CRITICAL' if abs(discrepancy) > 1000 else 'WARNING',
                        category='AMOUNT_MISMATCH',
                        invoice_id=inv_id,
                        order_id=order_id,
                        description=f'Invoice amount ({inv_amount}) does not match bank payment ({tx_amount})',
                        amount_discrepancy=discrepancy,
                        recommendation='Contact customer to confirm payment amount'
                    )
                    self.findings.append(finding)
            else:
                # No matching bank transaction
                if inv_status == 'paid':
                    finding = AuditFinding(
                        severity='CRITICAL',
                        category='PAYMENT_MISSING',
                        invoice_id=inv_id,
                        order_id=order_id,
                        description=f'Invoice marked as paid but no matching bank transaction found',
                        recommendation='Check if payment is in-transit or check wire reference details'
                    )
                    self.findings.append(finding)
                
                reconciliation['unmatched_invoices'].append({
                    'invoice_id': inv_id,
                    'order_id': order_id,
                    'customer': invoice.get('customer_name'),
                    'amount': inv_amount,
                    'status': inv_status,
                    'due_date': invoice.get('due_date'),
                    'notes': invoice.get('notes')
                })
        
        # Find bank transactions with no matching invoice (possible fraud/error)
        for tx in self.transactions:
            if tx.get('transaction_id') not in tx_matched:
                ref = tx.get('reference', 'UNKNOWN')
                tx_amount = tx.get('amount', 0)
                
                if ref == 'UNKNOWN' or not any(inv.get('order_id') == ref for inv in self.invoices):
                    finding = AuditFinding(
                        severity='WARNING',
                        category='UNMATCHED_TRANSACTION',
                        invoice_id='N/A',
                        order_id=ref,
                        description=f'Bank transaction {tx.get("transaction_id")} has no matching invoice (${abs(tx_amount)})',
                        recommendation='Verify transaction source and update invoice reference or create new invoice'
                    )
                    self.findings.append(finding)
                    
                reconciliation['unmatched_transactions'].append({
                    'transaction_id': tx.get('transaction_id'),
                    'date': tx.get('transaction_date'),
                    'reference': ref,
                    'amount': tx_amount,
                    'description': tx.get('description'),
                    'note': tx.get('note', '')
                })
        
        # INTELLIGENT AUDIT: Check for overdue invoices
        today = datetime.now()
        for invoice in self.invoices:
            if invoice.get('status') == 'overdue':
                finding = AuditFinding(
                    severity='WARNING',
                    category='OVERDUE_PAYMENT',
                    invoice_id=invoice.get('invoice_id'),
                    order_id=invoice.get('order_id'),
                    description=f'Invoice is overdue (due: {invoice.get("due_date")})',
                    recommendation='Send payment reminder to customer'
                )
                self.findings.append(finding)
        
        # INTELLIGENT AUDIT: Check for partial payments needing follow-up
        for finding in self.findings:
            if finding.category == 'AMOUNT_MISMATCH' and finding.amount_discrepancy < 0:
                finding.category = 'UNDERPAYMENT'
                finding.severity = 'CRITICAL'
        
        reconciliation['audit_findings'] = [asdict(f) for f in self.findings]
        return reconciliation
    
    def generate_audit_report_csv(self, reconciliation: Dict):
        """Generate comprehensive CSV audit report"""
        csv_path = self.output_dir / 'reconciliation_audit_report.csv'
        
        with open(csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow(['RECONCILIATION AUDIT REPORT', '', '', '', ''])
            writer.writerow(['Generated:', datetime.now().isoformat(), '', '', ''])
            writer.writerow(['', '', '', '', ''])
            
            # Summary section
            summary = reconciliation['summary']
            writer.writerow(['SUMMARY', '', '', '', ''])
            writer.writerow(['Total Invoices:', summary['total_invoices'], '', '', ''])
            writer.writerow(['Total Invoice Amount:', f"${summary['total_invoice_amount']:,.2f}", '', '', ''])
            writer.writerow(['Total Bank Received:', f"${summary['total_bank_received']:,.2f}", '', '', ''])
            writer.writerow(['', '', '', '', ''])
            
            # Matched items
            writer.writerow(['MATCHED INVOICES', 'Invoice ID', 'Order ID', 'Invoice Amount', 'Bank Amount', 'Status'])
            for item in reconciliation['matched_items']:
                writer.writerow(['', item['invoice_id'], item['order_id'], 
                               f"${item['invoice_amount']:,.2f}", f"${item['bank_amount']:,.2f}", 
                               item['status']])
            writer.writerow(['', '', '', '', ''])
            
            # Audit findings
            writer.writerow(['AUDIT FINDINGS', 'Severity', 'Category', 'Invoice ID', 'Description', 'Recommendation'])
            for finding in reconciliation['audit_findings']:
                writer.writerow(['', finding['severity'], finding['category'], finding['invoice_id'],
                               finding['description'], finding['recommendation']])
            writer.writerow(['', '', '', '', ''])
            
            # Unmatched invoices
            if reconciliation['unmatched_invoices']:
                writer.writerow(['UNMATCHED INVOICES', 'Invoice ID', 'Customer', 'Amount', 'Status', 'Notes'])
                for inv in reconciliation['unmatched_invoices']:
                    writer.writerow(['', inv['invoice_id'], inv['customer'], f"${inv['amount']:,.2f}", 
                                   inv['status'], inv['notes']])
            
            writer.writerow(['', '', '', '', ''])
            
            # Unmatched transactions
            if reconciliation['unmatched_transactions']:
                writer.writerow(['UNMATCHED TRANSACTIONS', 'Transaction ID', 'Date', 'Amount', 'Description', 'Note'])
                for tx in reconciliation['unmatched_transactions']:
                    writer.writerow(['', tx['transaction_id'], tx['date'], f"${tx['amount']:,.2f}", 
                                   tx['description'], tx['note']])
        
        print(f"✓ Generated audit report: {csv_path}")
        return csv_path
    
    def print_audit_summary(self, reconciliation: Dict):
        """Print formatted audit summary with color-coded warnings"""
        findings = reconciliation['audit_findings']
        
        print("\n" + "="*80)
        print("FINANCIAL AUDIT SUMMARY".center(80))
        print("="*80)
        
        # Count by severity
        critical = sum(1 for f in findings if f['severity'] == 'CRITICAL')
        warning = sum(1 for f in findings if f['severity'] == 'WARNING')
        info = sum(1 for f in findings if f['severity'] == 'INFO')
        
        if critical > 0:
            print(f"\n\033[1;31m🚨 CRITICAL ISSUES FOUND: {critical}\033[0m")
        if warning > 0:
            print(f"\033[1;33m⚠️  WARNINGS: {warning}\033[0m")
        if info > 0:
            print(f"\033[1;34mℹ️  INFO: {info}\033[0m")
        
        if critical > 0 or warning > 0:
            print("\n" + "-"*80)
            print("DETAILED FINDINGS:")
            print("-"*80)
            
            for finding in findings:
                severity = finding['severity']
                if severity == 'CRITICAL':
                    color = '\033[1;31m'  # Red bold
                    icon = '❌'
                elif severity == 'WARNING':
                    color = '\033[1;33m'  # Yellow bold
                    icon = '⚠️'
                else:
                    color = '\033[1;34m'  # Blue bold
                    icon = 'ℹ️'
                
                reset = '\033[0m'
                print(f"\n{color}{icon} [{finding['severity']}] {finding['category']}{reset}")
                print(f"   Invoice: {finding['invoice_id']} | Order: {finding['order_id']}")
                print(f"   Issue: {finding['description']}")
                if finding['amount_discrepancy']:
                    print(f"   Discrepancy: ${finding['amount_discrepancy']:,.2f}")
                print(f"   Action: {finding['recommendation']}")
        else:
            print("\n✅ All invoices reconciled successfully!")
        
        print("\n" + "="*80 + "\n")
    
    def run(self) -> Dict:
        """Execute full pipeline"""
        print("\n📊 Invoice AI Parser - Enterprise Financial Reconciliation")
        print("="*60)
        
        self.load_data()
        print("\n🔍 Performing intelligent reconciliation and audit...")
        reconciliation = self.parse_and_reconcile()
        
        # Save JSON output
        json_path = self.output_dir / 'reconciliation_data.json'
        json_path.write_text(json.dumps(reconciliation, indent=2))
        print(f"✓ Saved reconciliation data: {json_path}")
        
        # Generate CSV report
        self.generate_audit_report_csv(reconciliation)
        
        # Print summary
        self.print_audit_summary(reconciliation)
        
        return reconciliation

if __name__ == '__main__':
    root = Path(__file__).resolve().parent.parent
    parser = InvoiceAIParser(
        input_dir=root / 'input',
        output_dir=root / 'outputs'
    )
    reconciliation = parser.run()
    
    # Exit with status based on critical findings
    critical_count = sum(1 for f in reconciliation['audit_findings'] if f['severity'] == 'CRITICAL')
    sys.exit(1 if critical_count > 0 else 0)
