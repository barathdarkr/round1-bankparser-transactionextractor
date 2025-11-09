# bank_parser/process_bank_statement.py
import json, argparse, os
from typing import Dict, Any

from bank_parser.utils import (
    read_file_text,
    gemini_extract_json_from_file,
    gemini_insights_from_fields,
    normalize_amount,
    mask_account_number,
    validate_balances,
    compute_quality_metrics,
)

def _mock_result() -> Dict[str, Any]:
    return {
        "fields": {
            "account_info": {
                "bank_name": "HDFC Bank",
                "account_holder_name": "BARATH R",
                "masked_account_number": "****1234",
                "statement_month": "October",
                "statement_year": 2025,
                "account_type": "savings"
            },
            "summary": {
                "opening_balance": 15000.0,
                "closing_balance": 17350.0,
                "total_credits": 9000.0,
                "total_debits": 6650.0,
                "average_daily_balance": 16200.0,
                "overdraft_count": 0,
                "nsf_count": 0
            },
            "transactions": [
                {"date":"2025-10-01","description":"Salary UPI","amount":9000.0,"balance":24000.0,"category":"Income"},
                {"date":"2025-10-03","description":"ATM Withdrawal","amount":-2000.0,"balance":22000.0,"category":"ATM Cash"},
                {"date":"2025-10-12","description":"Swiggy","amount":-350.0,"balance":21650.0,"category":"Food"}
            ]
        },
        "insights": [
            "Account maintained > ₹15,000 average balance in Oct.",
            "Incoming salary detected on 1 Oct; consider auto-sweep to FD.",
            "Cash withdrawals low; UPI preferred."
        ],
        "quality": {"warnings": [], "duplicates_detected": False, "gemini_extraction_used": False}
    }

def process_bank_statement(file_path: str, test_mode: bool = False) -> Dict[str, Any]:
    if test_mode:
        return _mock_result()

    # 1) Extract structured JSON via Gemini directly from the FILE (upload + prompt)
    extracted = gemini_extract_json_from_file(file_path)

    # If Gemini returned raw text / error, still pass it onward (but keep moving)
    fields = extracted.get("fields", {}) if isinstance(extracted, dict) else {}

    # 2) Post-process: mask account numbers, normalize amounts, validate balances
    try:
        acct = fields.get("account_info", {}) or {}
        if "account_number" in acct:
            acct["masked_account_number"] = mask_account_number(acct.get("account_number", ""))
        # normalize numeric summary
        summary = fields.get("summary", {}) or {}
        for k in ["opening_balance","closing_balance","total_credits","total_debits","average_daily_balance"]:
            if k in summary:
                summary[k] = normalize_amount(summary[k])
        fields["summary"] = summary
        fields["account_info"] = acct

        # validate balances
        validate_balances(fields)

    except Exception:
        pass

    # 3) Insights from final JSON
    insights_obj = gemini_insights_from_fields({"fields": fields})
    insights = insights_obj.get("insights", []) if isinstance(insights_obj, dict) else []

    # 4) Quality meta
    quality = compute_quality_metrics({"fields": fields})

    return {"fields": fields, "insights": insights, "quality": quality}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("file_path", help="Path to bank statement (PDF or image)")
    ap.add_argument("--out", default="output.json", help="Output JSON file")
    ap.add_argument("--test", action="store_true", help="Use mock data (no external calls)")
    args = ap.parse_args()

    data = process_bank_statement(args.file_path, test_mode=args.test)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"💾 Wrote: {os.path.abspath(args.out)}")
