Overview

An AI-powered Python tool that extracts key financial data and generates insights from bank statements (PDF or image) using Google Gemini (Generative AI). It automatically detects whether the document is digital or scanned, applies OCR if needed, and returns structured JSON output.

Objective
1. Read and process PDF or image bank statements.
2. Use Gemini API to extract account details, transaction summary, and insights.
3. Mask sensitive details and return valid JSON.

Setup Instructions
1️⃣ Install Dependencies:
pip install google-genai pdfplumber pytesseract pillow requests

2️⃣ Set the Gemini API Key:
Windows (CMD):
setx GEMINI_API_KEY "YOUR_API_KEY_HERE"

macOS/Linux:
export GEMINI_API_KEY="YOUR_API_KEY_HERE" 
▶️ Running the Project
🧪 Test Mode (No API calls):
python -m bank_parser.process_bank_statement bankstaement.pdf --test --out output.json

 Real Mode (Gemini Extraction):
python -m bank_parser.process_bank_statement bankstaement.pdf --out output.json

 Output Structure

The program produces a JSON file with three keys: fields, insights, and quality.

 Folder Structure
bank_parser/
├── utils.py                     # Core OCR & Gemini logic
├── process_bank_statement.py    # Main execution script
├── prompt_extraction.txt        # Extraction schema instructions
├── prompt_insights.txt          # Financial insights prompt
└── README.md                    # Documentation

 Privacy & Security
- Account numbers automatically masked (last 4 digits only).
- No source file content is stored.
- API keys handled securely via environment variables.
 Known Limitations
- Large PDFs (>10 pages) may exceed Gemini Flash token limit.
- Use models/gemini-2.5-pro for long statements.
- OCR quality depends on scan clarity.
- Currency symbols limited to ₹, $, €.

📜 License
For educational and research use only.
