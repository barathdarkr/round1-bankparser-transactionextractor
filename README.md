README — DevOps Intern Tasks (Round 1)
Repository Structure

round1/
│
├── TransactionExtractor/           # Task 1
│   ├── extract_transactions.py
│   ├── sample_log.txt
│   └── README.docx
│
└── bank_parser/                    # Task 2
    ├── process_bank_statement.py
    ├── utils.py
    ├── prompt_extraction.txt
    ├── prompt_insights.txt
    ├── output.json
    └── README.md

Task 1 — Transaction Value Extractor (Regex Parser)

A Python-based regex parser that extracts structured transaction details from unformatted log text.
It identifies patterns of the form:
TXN:<TYPE> | AMT:<AMOUNT> | ID:<ALPHANUMERIC>
and returns a list of tuples (txn_type, amount, txn_id).

Features
•	Parses multiline transaction logs
•	Handles decimals and comma-separated amounts
•	Ignores malformed or lowercase tags
•	Case-sensitive (TXN, AMT, ID only)
•	Clean float formatting
•	CLI-ready for file input or string parsing
Example Input / Output
Input (sample_log.txt):

TXN:CREDIT | AMT:1,250.50 | ID:AB123
TXN:DEBIT  | AMT:500 | ID:XY789
TXN: DEBIT|AMT:1000|ID:XYZ42
TXN:CREDIT | AMT:200.75 | ID:LMN55

Output:

Transaction Value Extractor (Regex Parser)
============================================

Extracted Transactions:
01. CREDIT  |    1250.50 | ID: AB123
02. DEBIT   |     500.00 | ID: XY789
03. DEBIT   |    1000.00 | ID: XYZ42
04. CREDIT  |     200.75 | ID: LMN55

Done 

Regex Pattern
Field	Regex	Description
TXN	TXN:\s*([A-Z]+)	Captures uppercase transaction type
AMT	AMT:\s*([\d,]+(?:\.\d+)?)	Handles commas & decimals
ID	ID:\s*([A-Za-z0-9]+)	Captures alphanumeric IDs
Separator	\s*\|\s*	Flexible spacing

Full pattern:
r"TXN:\s*([A-Z]+)\s*\|\s*AMT:\s*([\d,]+(?:\.\d+)?)\s*\|\s*ID:\s*([A-Za-z0-9]+)"

Running the Script

cd C:\Users\round1\TransactionExtractor
python extract_transactions.py sample_log.txt

Output will print structured transactions in the console.

Usage in Code

from extract_transactions import extract_transactions

log = '''
TXN:CREDIT | AMT:1,250.50 | ID:AB123
TXN:DEBIT | AMT:500 | ID:XY789
'''

print(extract_transactions(log))
# [('CREDIT', 1250.5, 'AB123'), ('DEBIT', 500.0, 'XY789')]

Task 2 — Bank Statement Parser (Gemini AI + OCR)

A bank statement parser powered by Google Gemini 2.5 Flash that extracts transaction data, balances,
and financial insights from PDFs or scanned images.
It handles both text-based and scanned statements using pdfplumber, Pillow, and Tesseract OCR,
then structures results into JSON.

Features
•	Supports PDF + Image files
•	Uses OCR for scanned PDFs
•	Extracts structured fields & transactions
•	Generates AI-based insights
•	Masks account numbers automatically
•	Computes balance consistency checks
•	Stores all results in output.json
Workflow
1.	Read bank statement file (PDF / JPG / PNG)
2.	Extract text using pdfplumber + OCR (if needed)
3.	Send to Gemini API for structured extraction
4.	Post-process → validate balances + mask sensitive data
5.	Generate financial insights from extracted data

Output JSON Structure

{
  "fields": {
    "account_info": {
      "bank_name": "HDFC Bank",
      "account_holder_name": "John Smith",
      "masked_account_number": "****7890",
      "statement_month": "October",
      "statement_year": 2025,
      "account_type": "Savings"
    },
    "summary": {
      "opening_balance": 175800.00,
      "closing_balance": 591800.00,
      "total_credits": 510000.00,
      "total_debits": 94000.00
    },
    "transactions": [
      {
        "date": "2025-09-15",
        "description": "ATM Withdrawal - Mumbai",
        "amount": -500.00,
        "balance": 12500.00,
        "category": "ATM Cash"
      }
    ]
  },
  "insights": [
    "High frequency of ATM withdrawals.",
    "Account maintained > ₹10,000 average balance."
  ],
  "quality": {
    "warnings": [],
    "gemini_extraction_used": true
  }
}

How to Run

Install dependencies:
pip install google-genai pdfplumber pytesseract pillow requests

Set your Gemini API key:
set GEMINI_API_KEY=your_api_key_here

Run the parser:
python -m bank_parser.process_bank_statement bankstatement.pdf --out output.json

Tech Stack
•	Language: Python 3.11
•	AI Model: Gemini 2.5 Flash (Google AI Studio)
•	Libraries: pdfplumber, Pillow, pytesseract, requests
•	OCR Engine: Tesseract
•	Integration: Gemini REST API
Quality Features
•	Balance mismatch detection
•	Duplicate transaction checks
•	OCR confidence tracking
•	Missing section alerts
•	Masked sensitive fields
🏁 License
This repository is open-sourced under the MIT License. You may freely use, modify, and distribute the code with attribution.
