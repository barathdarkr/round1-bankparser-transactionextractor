"""
===========================================================
Task 1 – Transaction Value Extractor (Regex Capture Challenge)
===========================================================

Author : Barath R
Email  : barathasm3002@gmail.com
Date   : 2025-11-09
-----------------------------------------------------------
Description:
-------------
Parses multiline transaction logs containing entries like:
    TXN:<TYPE> | AMT:<AMOUNT> | ID:<ALPHANUMERIC>

Extracts all valid matches using regular expressions only and returns:
    [(txn_type, amount, txn_id), ...]

Strictly enforces uppercase labels (TXN, AMT, ID) and numeric format.
Handles commas, decimals, and whitespace variations.

Example:
---------
Input:
    TXN:CREDIT | AMT:1,250.50 | ID:AB123
    TXN:DEBIT  | AMT:500 | ID:XY789

Output:
    [('CREDIT', 1250.50, 'AB123'), ('DEBIT', 500.0, 'XY789')]
-----------------------------------------------------------
"""

import re
import sys
from typing import List, Tuple, Optional


# --------------------------
# Core Extraction Function
# --------------------------
def extract_transactions(log_text: str) -> List[Tuple[str, float, str]]:
    """
    Extracts transaction details matching:
      TXN:<TYPE> | AMT:<AMOUNT> | ID:<ALPHANUMERIC>

    Args:
        log_text (str): Raw multiline string containing log entries.

    Returns:
        List[Tuple[str, float, str]]: A list of (txn_type, amount, txn_id)
                                      or [] if none found.

    Raises:
        TypeError: If the input is not a string.
    """

    if not isinstance(log_text, str):
        raise TypeError("Input must be a string containing transaction logs.")

    # ✅ Robust regex pattern
    pattern = re.compile(
        r"""
        TXN:\s*([A-Z]+)\s*              # Capture transaction type (uppercase only)
        \|\s*AMT:\s*([\d,]+(?:\.\d+)?)  # Capture amount (commas + decimals)
        \s*\|\s*ID:\s*([A-Za-z0-9]+)    # Capture alphanumeric ID
        """,
        re.VERBOSE,
    )

    matches = pattern.findall(log_text)
    results: List[Tuple[str, float, str]] = []

    for txn_type, amount_str, txn_id in matches:
        # Normalize numeric string → float
        try:
            normalized_amount = float(amount_str.replace(",", ""))
        except ValueError:
            # Skip malformed entries gracefully
            continue

        results.append((txn_type, normalized_amount, txn_id))

    return results


# --------------------------
# Optional CLI Interface
# --------------------------
def _read_file(file_path: str) -> Optional[str]:
    """Utility to read log text from a file safely."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
    except Exception as e:
        print(f"⚠️ Error reading file: {e}")
    return None


def main():
    """
    Command-line interface:
        python extract_transactions.py log.txt
    or
        python extract_transactions.py
        (then paste log text manually)
    """

    print("💳 Transaction Value Extractor (Regex Parser)")
    print("============================================")

    # If a file path is provided
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        log_data = _read_file(file_path)
        if log_data is None:
            sys.exit(1)
    else:
        print("Paste or type transaction logs below (Ctrl+D to end):\n")
        log_data = sys.stdin.read()

    extracted = extract_transactions(log_data)
    if not extracted:
        print("\n⚠️  No valid transaction entries found.")
    else:
        print("\n✅ Extracted Transactions:")
        for i, (txn_type, amt, txn_id) in enumerate(extracted, 1):
            print(f"{i:02d}. {txn_type:7s} | {amt:10.2f} | ID: {txn_id}")

    print("\nDone ✔")


# --------------------------
# Unit Tests (Quick Check)
# --------------------------
def _run_internal_tests():
    """Basic verification tests for the regex logic."""

    tests = [
        # ✅ Basic log
        (
            '''
            TXN:CREDIT | AMT:1,250.50 | ID:AB123
            TXN:DEBIT  | AMT:500 | ID:XY789
            ''',
            [("CREDIT", 1250.50, "AB123"), ("DEBIT", 500.0, "XY789")],
        ),

        # ✅ Messy spacing
        (
            'TXN: DEBIT|AMT:1000|ID:XYZ42 TXN:CREDIT | AMT:200.75 | ID:LMN55',
            [("DEBIT", 1000.0, "XYZ42"), ("CREDIT", 200.75, "LMN55")],
        ),

        # ✅ No matches
        ('TXN CREDIT AMT 123 ID 999', []),

        # ✅ Mixed case (ignored)
        ('Txn:Credit | Amt:50 | Id:abc999', []),

        # ✅ Multiple mixed entries
        (
            '''
            TXN:CREDIT | AMT:10,000.00 | ID:TXN001
            INVALID LINE
            TXN:DEBIT | AMT:5,500.25 | ID:ABC987
            TXN:CREDIT | AMT:250 | ID:XYZ111
            ''',
            [("CREDIT", 10000.0, "TXN001"), ("DEBIT", 5500.25, "ABC987"), ("CREDIT", 250.0, "XYZ111")],
        ),
    ]

    for i, (log, expected) in enumerate(tests, start=1):
        result = extract_transactions(log)
        assert result == expected, f"❌ Test {i} failed: {result} != {expected}"
    print("✅ All internal regex tests passed!")


# --------------------------
# Script Entry Point
# --------------------------
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        _run_internal_tests()
    else:
        main()
"""
===========================================================
Task 1 – Transaction Value Extractor (Regex Capture Challenge)
===========================================================

Author : Barath R
Email  : barathasm3002@gmail.com
Date   : 2025-11-09
-----------------------------------------------------------
Description:
-------------
Parses multiline transaction logs containing entries like:
    TXN:<TYPE> | AMT:<AMOUNT> | ID:<ALPHANUMERIC>

Extracts all valid matches using regular expressions only and returns:
    [(txn_type, amount, txn_id), ...]

Strictly enforces uppercase labels (TXN, AMT, ID) and numeric format.
Handles commas, decimals, and whitespace variations.

Example:
---------
Input:
    TXN:CREDIT | AMT:1,250.50 | ID:AB123
    TXN:DEBIT  | AMT:500 | ID:XY789

Output:
    [('CREDIT', 1250.50, 'AB123'), ('DEBIT', 500.0, 'XY789')]
-----------------------------------------------------------
"""

import re
import sys
from typing import List, Tuple, Optional


# --------------------------
# Core Extraction Function
# --------------------------
def extract_transactions(log_text: str) -> List[Tuple[str, float, str]]:
    """
    Extracts transaction details matching:
      TXN:<TYPE> | AMT:<AMOUNT> | ID:<ALPHANUMERIC>

    Args:
        log_text (str): Raw multiline string containing log entries.

    Returns:
        List[Tuple[str, float, str]]: A list of (txn_type, amount, txn_id)
                                      or [] if none found.

    Raises:
        TypeError: If the input is not a string.
    """

    if not isinstance(log_text, str):
        raise TypeError("Input must be a string containing transaction logs.")

    # ✅ Robust regex pattern
    pattern = re.compile(
        r"""
        TXN:\s*([A-Z]+)\s*              # Capture transaction type (uppercase only)
        \|\s*AMT:\s*([\d,]+(?:\.\d+)?)  # Capture amount (commas + decimals)
        \s*\|\s*ID:\s*([A-Za-z0-9]+)    # Capture alphanumeric ID
        """,
        re.VERBOSE,
    )

    matches = pattern.findall(log_text)
    results: List[Tuple[str, float, str]] = []

    for txn_type, amount_str, txn_id in matches:
        # Normalize numeric string → float
        try:
            normalized_amount = float(amount_str.replace(",", ""))
        except ValueError:
            # Skip malformed entries gracefully
            continue

        results.append((txn_type, normalized_amount, txn_id))

    return results


# --------------------------
# Optional CLI Interface
# --------------------------
def _read_file(file_path: str) -> Optional[str]:
    """Utility to read log text from a file safely."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
    except Exception as e:
        print(f"⚠️ Error reading file: {e}")
    return None


def main():
    """
    Command-line interface:
        python extract_transactions.py log.txt
    or
        python extract_transactions.py
        (then paste log text manually)
    """

    print("💳 Transaction Value Extractor (Regex Parser)")
    print("============================================")

    # If a file path is provided
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        log_data = _read_file(file_path)
        if log_data is None:
            sys.exit(1)
    else:
        print("Paste or type transaction logs below (Ctrl+D to end):\n")
        log_data = sys.stdin.read()

    extracted = extract_transactions(log_data)
    if not extracted:
        print("\n⚠️  No valid transaction entries found.")
    else:
        print("\n✅ Extracted Transactions:")
        for i, (txn_type, amt, txn_id) in enumerate(extracted, 1):
            print(f"{i:02d}. {txn_type:7s} | {amt:10.2f} | ID: {txn_id}")

    print("\nDone ✔")


# --------------------------
# Unit Tests (Quick Check)
# --------------------------
def _run_internal_tests():
    """Basic verification tests for the regex logic."""

    tests = [
        # ✅ Basic log
        (
            '''
            TXN:CREDIT | AMT:1,250.50 | ID:AB123
            TXN:DEBIT  | AMT:500 | ID:XY789
            ''',
            [("CREDIT", 1250.50, "AB123"), ("DEBIT", 500.0, "XY789")],
        ),

        # ✅ Messy spacing
        (
            'TXN: DEBIT|AMT:1000|ID:XYZ42 TXN:CREDIT | AMT:200.75 | ID:LMN55',
            [("DEBIT", 1000.0, "XYZ42"), ("CREDIT", 200.75, "LMN55")],
        ),

        # ✅ No matches
        ('TXN CREDIT AMT 123 ID 999', []),

        # ✅ Mixed case (ignored)
        ('Txn:Credit | Amt:50 | Id:abc999', []),

        # ✅ Multiple mixed entries
        (
            '''
            TXN:CREDIT | AMT:10,000.00 | ID:TXN001
            INVALID LINE
            TXN:DEBIT | AMT:5,500.25 | ID:ABC987
            TXN:CREDIT | AMT:250 | ID:XYZ111
            ''',
            [("CREDIT", 10000.0, "TXN001"), ("DEBIT", 5500.25, "ABC987"), ("CREDIT", 250.0, "XYZ111")],
        ),
    ]

    for i, (log, expected) in enumerate(tests, start=1):
        result = extract_transactions(log)
        assert result == expected, f"❌ Test {i} failed: {result} != {expected}"
    print("✅ All internal regex tests passed!")


# --------------------------
# Script Entry Point
# --------------------------
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        _run_internal_tests()
    else:
        main()
