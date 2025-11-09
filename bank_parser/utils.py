# bank_parser/utils.py
import os, json, requests
from typing import Any, Dict, Union

# ========== OPTIONAL OCR / PDF DEPENDENCIES ==========
try:
    import pdfplumber
except ImportError:
    pdfplumber = None

try:
    from PIL import Image
except ImportError:
    Image = None

try:
    import pytesseract
except ImportError:
    pytesseract = None


# ========== ENVIRONMENT & MODEL CONFIG ==========
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
if not GEMINI_API_KEY:
    raise RuntimeError("❌ GEMINI_API_KEY not set. Run: set GEMINI_API_KEY=YOUR_KEY_HERE")

# Use the latest working model from list_models.py
GEMINI_MODEL = "models/gemini-2.5-flash"

# REST endpoints (Google AI Studio)
REST_UPLOAD_URL = f"https://generativelanguage.googleapis.com/upload/v1beta/files?key={GEMINI_API_KEY}"
REST_GEN_URL = f"https://generativelanguage.googleapis.com/v1beta/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"


# ========== DEFAULT PROMPTS ==========
DEFAULT_EXTRACTION_INSTRUCTIONS = """\
Return ONLY valid JSON with keys:
{
  "fields": {
    "account_info": {
      "bank_name": "",
      "account_holder_name": "",
      "masked_account_number": "",
      "statement_month": "",
      "statement_year": "",
      "account_type": ""
    },
    "summary": {
      "opening_balance": 0.0,
      "closing_balance": 0.0,
      "total_credits": 0.0,
      "total_debits": 0.0,
      "average_daily_balance": 0.0,
      "overdraft_count": 0,
      "nsf_count": 0
    },
    "transactions": [
      {
        "date": "YYYY-MM-DD",
        "description": "",
        "amount": 0.0,
        "balance": 0.0,
        "category": ""
      }
    ]
  }
}
- Mask account numbers except last 4 digits.
- Normalize currency symbols.
- Dates should follow YYYY-MM-DD format.
"""

DEFAULT_INSIGHTS_INSTRUCTIONS = """\
Given the extracted JSON (fields + summary + transactions), return a JSON object:
{"insights": ["...", "...", "..."]}
Focus on:
- Monthly income pattern
- Spending categories
- Overdrafts or low balance events
- Salary detection
- UPI or ATM spending patterns
Return ONLY JSON (no explanation).
"""


# ========== FILE READING & OCR ==========
def read_file_text(file_path: str) -> str:
    """Extract text from a PDF or image. Uses OCR if needed."""
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        if pdfplumber is None:
            raise RuntimeError("Install pdfplumber: pip install pdfplumber")

        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                t = page.extract_text() or ""
                text += t + "\n"

            # If no text found, fall back to OCR
            if not text.strip():
                print("⚙️ Using OCR on scanned PDF...")
                if pytesseract is None or Image is None:
                    raise RuntimeError("Install pillow + pytesseract for scanned PDFs.")
                for page in pdf.pages:
                    img = page.to_image(resolution=300).original
                    text += pytesseract.image_to_string(img) + "\n"

        return text.strip()

    elif ext in {".png", ".jpg", ".jpeg", ".bmp", ".tiff"}:
        if Image is None or pytesseract is None:
            raise RuntimeError("Install pillow + pytesseract for image OCR.")
        return pytesseract.image_to_string(Image.open(file_path))

    else:
        raise RuntimeError(f"Unsupported file type: {ext}")


# ========== GEMINI REST HELPERS ==========
def _rest_upload_file(file_path: str) -> str:
    """Uploads a file to Gemini REST endpoint and returns file URI."""
    with open(file_path, "rb") as f:
        meta = {"file": {"display_name": os.path.basename(file_path)}}
        res = requests.post(
            REST_UPLOAD_URL,
            files={"file": f},
            data={"json": json.dumps(meta)},
            timeout=120
        )

    if res.status_code != 200:
        raise RuntimeError(f"Upload failed: {res.status_code} {res.text}")

    data = res.json()
    return data["file"]["uri"]


def _rest_generate(parts: list) -> str:
    """Generate content using Gemini REST API. Includes detailed diagnostics."""
    payload = {
        "contents": [{"role": "user", "parts": parts}],
        "generationConfig": {
            "temperature": 0.2,
            "topK": 40,
            "topP": 0.95,
            "maxOutputTokens": 8192  # increased from 4096
        }
    }

    r = requests.post(REST_GEN_URL, json=payload, timeout=180)
    if r.status_code != 200:
        raise RuntimeError(f"Gemini error {r.status_code}: {r.text}")

    data = r.json()

    # Print token usage for large files
    tokens_used = data.get("usageMetadata", {}).get("totalTokenCount", 0)
    if tokens_used > 4000:
        print(f"⚠️ Gemini used {tokens_used} tokens — consider switching to gemini-2.5-pro for large PDFs.\n")

    # Validate Gemini output
    if "candidates" not in data:
        print("\n--- ⚠️ Gemini Response Diagnostic ---")
        print(json.dumps(data, indent=2))
        print("------------------------------------\n")
        raise RuntimeError("Gemini returned unexpected response (no 'candidates').")

    try:
        content = data["candidates"][0].get("content", {})
        parts_out = content.get("parts", [])

        if not parts_out:
            reason = data["candidates"][0].get("finishReason", "")
            if reason == "MAX_TOKENS":
                print("\n⚠️ Gemini hit the MAX_TOKENS limit — partial output only.\n")
                return "(Gemini output truncated due to token limit)"
            else:
                print("\n⚠️ Gemini returned no parts. Debug info below:\n")
                print(json.dumps(data, indent=2))
                return "(No content returned from Gemini)"

        return "".join(p.get("text", "") for p in parts_out).strip()

    except Exception as e:
        print("\n--- ⚠️ Gemini Response Diagnostic ---")
        print(json.dumps(data, indent=2))
        print("------------------------------------\n")
        raise RuntimeError(f"Parsing Gemini response failed: {e}")


# ========== JSON EXTRACTION / INSIGHTS ==========
def gemini_extract_json_from_file(file_path: str, extraction_prompt_path="prompt_extraction.txt") -> Dict[str, Any]:
    """Uploads a bank statement and extracts structured JSON fields."""
    file_uri = _rest_upload_file(file_path)
    instr = _read_text_file(extraction_prompt_path, DEFAULT_EXTRACTION_INSTRUCTIONS)

    text = _rest_generate([
        {"file_data": {"file_uri": file_uri}},
        {"text": instr}
    ])

    # Clean JSON fences if present
    if text.startswith("```"):
        text = text.strip("`").replace("json\n", "").replace("json\r\n", "")

    try:
        return json.loads(text)
    except Exception as e:
        return {"raw_text": text, "error": f"JSON parse error: {e}"}


def gemini_insights_from_fields(extracted_json: Dict[str, Any], insights_prompt_path="prompt_insights.txt") -> Dict[str, Any]:
    """Generates human-readable insights from structured JSON."""
    instr = _read_text_file(insights_prompt_path, DEFAULT_INSIGHTS_INSTRUCTIONS)
    payload = json.dumps(extracted_json, ensure_ascii=False)

    text = _rest_generate([
        {"text": f"{instr}\n\nHere is the extracted JSON:\n{payload}"}
    ])

    if text.startswith("```"):
        text = text.strip("`").replace("json\n", "").replace("json\r\n", "")

    try:
        out = json.loads(text)
        if isinstance(out, dict) and "insights" in out:
            return out
        return {"insights": [text]}
    except Exception:
        return {"insights": [text]}


# ========== HELPER FUNCTIONS ==========
def _read_text_file(path: str, default_text: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return default_text


def mask_account_number(s: str) -> str:
    digits = [c for c in s if c.isdigit()]
    return "****" + "".join(digits[-4:]) if len(digits) >= 4 else "****"


def normalize_amount(v: Union[str, float, int]) -> Union[float, None]:
    if isinstance(v, (float, int)):
        return float(v)
    try:
        s = str(v).replace(",", "").replace("₹", "").replace("$", "").replace("€", "").strip()
        return float(s)
    except Exception:
        return None


def validate_balances(fields: Dict[str, Any]) -> None:
    s = fields.get("summary", {}) or {}
    ob = s.get("opening_balance")
    cb = s.get("closing_balance")
    tc = s.get("total_credits", 0) or 0
    td = s.get("total_debits", 0) or 0

    if isinstance(ob, (int, float)) and isinstance(cb, (int, float)):
        expected = float(ob) + float(tc) - float(td)
        if abs(float(cb) - expected) > 5.0:
            s["balance_mismatch_warning"] = True

    fields["summary"] = s


def compute_quality_metrics(extracted_json: Dict[str, Any]) -> Dict[str, Any]:
    q = {"ocr_confidence": None, "warnings": [], "duplicates_detected": False, "gemini_extraction_used": True}
    try:
        tx = extracted_json.get("fields", {}).get("transactions", [])
        if not tx:
            q["warnings"].append("No transactions extracted.")
    except Exception:
        q["warnings"].append("Unexpected JSON structure from Gemini.")
    return q
