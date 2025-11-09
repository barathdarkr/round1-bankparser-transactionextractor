 Transaction Value Extractor (Regex Parser)
 Overview
This project is part of the DevOps Intern Task Round 1. It implements a Python-based Regex Parser that automatically extracts structured transaction details from unformatted text logs. The script scans through mixed transaction lines and extracts details in the following pattern:

TXN:<TYPE> | AMT:<AMOUNT> | ID:<ALPHANUMERIC>

It then returns a structured list of tuples (txn_type, amount, txn_id) for further analysis or downstream processing.
 Features
•	Parses complex multiline transaction logs
•	Handles decimals and comma-separated amounts (e.g., 1,000.50)
•	Ignores invalid or malformed lines
•	Case-sensitive — only matches uppercase field tags (TXN, AMT, ID)
•	Outputs clean, float-formatted values
•	CLI-ready script for file input or direct log text
 Example Input / Output
Example Log (sample_log.txt):
TXN:CREDIT | AMT:1,250.50 | ID:AB123
TXN:DEBIT  | AMT:500 | ID:XY789
TXN: DEBIT|AMT:1000|ID:XYZ42
TXN:CREDIT | AMT:200.75 | ID:LMN55
Expected Output:
 Transaction Value Extractor (Regex Parser)
============================================

 Extracted Transactions:
01. CREDIT  |    1250.50 | ID: AB123
02. DEBIT   |     500.00 | ID: XY789
03. DEBIT   |    1000.00 | ID: XYZ42
04. CREDIT  |     200.75 | ID: LMN55

Done 
 Regex Pattern Explanation
Field	Regex Component	Description
TXN Type	TXN:\s*([A-Z]+)	Captures uppercase word after TXN:
Amount	AMT:\s*([\d,]+(?:\.\d+)?)	Captures amounts with commas & decimals
Transaction ID	ID:\s*([A-Za-z0-9]+)	Captures alphanumeric transaction ID
Pipe separation	\s*\|\s*	Allows flexible spacing between fields

Full regex used:
pattern = r"TXN:\s*([A-Z]+)\s*\|\s*AMT:\s*([\d,]+(?:\.\d+)?)\s*\|\s*ID:\s*([A-Za-z0-9]+)"
 How to Run
Prerequisites:
- Python 3.8 or higher
Navigate to project folder:
cd C:\Users\round1\TransactionExtractor
Run the script:
python extract_transactions.py sample_log.txt
Expected Output:
Structured list of extracted transactions printed in console.
Example in Code
from extract_transactions import extract_transactions

log = '''
TXN:CREDIT | AMT:1,250.50 | ID:AB123
TXN:DEBIT  | AMT:500 | ID:XY789
'''

result = extract_transactions(log)
print(result)
# [('CREDIT', 1250.50, 'AB123'), ('DEBIT', 500.0, 'XY789')]
 Folder Structure
TransactionExtractor/
│
├── extract_transactions.py   # Main parser script
├── sample_log.txt             # Example input log
└── README.docx                # Documentation file
 License
This project is open-sourced under the MIT License. You may freely use and modify it with proper attribution.
