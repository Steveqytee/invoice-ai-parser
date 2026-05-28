#!/usr/bin/env python3
import json, csv, os
from pathlib import Path
import requests

root = Path(__file__).resolve().parent.parent
inp = root / 'input'
out = root / 'outputs'
out.mkdir(parents=True, exist_ok=True)

# Simulated ParserData extraction: parse key: value lines
extracted = []
for p in sorted(inp.glob('*.txt')):
    data = {'source_file': p.name}
    for line in p.read_text().splitlines():
        if ':' in line:
            k,v = line.split(':',1)
            data[k.strip().lower()] = v.strip()
    extracted.append(data)

# Save extracted JSON
ex_json = out / 'extracted.json'
ex_json.write_text(json.dumps(extracted, indent=2))
print('Wrote', ex_json)

# Create final prompt (modified to include financial warning)
final_prompt = '''
You are given the parsed JSON data from invoices and bank statements. Analyze and reconcile them.
If you find invoice amounts that do not match bank statement amounts, or refund orders lacking a refund note, IMMEDIATELY in the terminal print in red bold: [WARNING: Reconciliation Discrepancy Found!]
Output a reconciliation CSV with columns: invoice, invoice_amount, bank_ref, bank_amount, status, notes.
Use the JSON below as input.
'''

(prompt_file := out / 'llm_prompt.txt').write_text(final_prompt + '\n\nDATA:\n' + json.dumps(extracted, indent=2))
print('Wrote prompt to', prompt_file)

# Optionally call an LLM (Gemini/OpenAI-compatible) if GEMINI_KEY is set
llm_response_text = None
gemini_key = os.getenv('GEMINI_KEY')
base_url = os.getenv('BASE_URL', 'https://api.openai.com/v1/chat/completions')
model = os.getenv('GEMINI_MODEL', 'gpt-4o-mini')
if gemini_key:
    headers = {'Authorization': f'Bearer {gemini_key}', 'Content-Type': 'application/json'}
    payload = {
        'model': model,
        'messages': [
            {'role': 'user', 'content': final_prompt + '\n\nDATA:\n' + json.dumps(extracted, indent=2)}
        ],
        'temperature': 0
    }
    try:
        resp = requests.post(base_url, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        jr = resp.json()
        # Extract common response shapes (OpenAI-compatible)
        if isinstance(jr, dict) and 'choices' in jr and len(jr['choices'])>0:
            ch = jr['choices'][0]
            if isinstance(ch.get('message'), dict) and 'content' in ch['message']:
                llm_response_text = ch['message']['content']
            elif 'text' in ch:
                llm_response_text = ch['text']
            else:
                llm_response_text = str(ch)
        else:
            llm_response_text = json.dumps(jr)
        print('\nLLM response:\n')
        print(llm_response_text)
        if 'WARNING' in (llm_response_text or ''):
            print('\033[1;31m[WARNING: Reconciliation Discrepancy Found!]\033[0m')
    except Exception as e:
        print('LLM call failed:', e)

# Simple rule-based reconciliation (local simulation of LLM)
# Build list of bank txs and invoices
bank = [e for e in extracted if e['source_file'].startswith('bank')]
invoices = [e for e in extracted if e['source_file'].startswith('invoice')]

# normalize amounts
def to_amount(x):
    try:
        return float(x)
    except:
        return None

bank_index = {b.get('ref'): b for b in bank}

rows = []
discrepancy = False
for inv in invoices:
    inv_amt = to_amount(inv.get('amount'))
    order = inv.get('order')
    matched = bank_index.get(order)
    if matched:
        bank_amt = to_amount(matched.get('amount'))
        status = 'ok' if abs((inv_amt or 0) - (bank_amt or 0)) < 0.001 else 'mismatch'
        notes = '' if status=='ok' else 'Amount differs'
        if status=='mismatch': discrepancy = True
        rows.append([inv.get('invoice'), inv_amt, matched.get('tx'), bank_amt, status, notes])
    else:
        rows.append([inv.get('invoice'), inv_amt, '', '', 'no_bank_match', 'No matching bank reference'])
        discrepancy = True
       
# Check refunds missing notes
for inv in invoices:
    if 'refund' in (inv.get('notes','').lower()) or 'refund' in inv.get('invoice','').lower():
        # fine
        pass
    else:
        if 'refund' in inv.get('notes','').lower() or 'refund' in inv.get('invoice','').lower():
            pass
        # We'll consider the earlier note in invoice_2 as 'Refund expected but not noted' -> mark
        if 'refund' in inv.get('notes','').lower() and 'not' in inv.get('notes','').lower():
            rows.append([inv.get('invoice'), inv.get('amount'), '', '', 'refund_missing_note', 'Refund expected but no note'])
            discrepancy = True

# Write CSV
csv_path = out / 'reconciliation_report.csv'
with open(csv_path,'w',newline='') as f:
    w = csv.writer(f)
    w.writerow(['invoice','invoice_amount','bank_ref','bank_amount','status','notes'])
    for r in rows:
        w.writerow(r)
print('Wrote', csv_path)

# If discrepancy, print red bold warning
if discrepancy:
    # ANSI: bold red
    print('\033[1;31m[WARNING: Reconciliation Discrepancy Found!]\033[0m')

# Also echo the simulated LLM analysis
print('\nSimulated LLM analysis:')
for r in rows:
    print('-', r)
