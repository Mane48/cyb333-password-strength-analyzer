"""Heuristic pattern detectors for weak password construction."""

from __future__ import annotations

import re
from typing import List

# Common keyboard walks (rows + diagonals-ish), lowercase for matching.
_KEYBOARD_SEQUENCES = (
    "qwertyuiop",
    "asdfghjkl",
    "zxcvbnm",
    "1234567890",
    "qwerty",
    "asdfgh",
    "zxcvbn",
    "1qaz2wsx",
    "qazwsx",
)

_SEQUENCE_RE = re.compile(
    r"(?:0123|1234|2345|3456|4567|5678|6789|7890|"
    r"abcd|bcde|cdef|defg|efgh|fghi|ghij|hijk|ijkl|jklm|klmn|lmno|mnop|"
    r"nopq|opqr|pqrs|qrst|rstu|stuv|tuvw|uvwx|vwxy|wxyz)",
    re.IGNORECASE,
)


def find_pattern_issues(password: str) -> List[str]:
    """Return human-readable pattern weaknesses found in *password*."""
    issues: List[str] = []
    lower = password.lower()

    if re.search(r"(.)\1{2,}", password):
        issues.append("Contains 3+ repeated characters in a row (e.g. aaa, 111).")

    if _SEQUENCE_RE.search(lower):
        issues.append("Contains an obvious alphabetic or numeric sequence.")

    for seq in _KEYBOARD_SEQUENCES:
        if len(seq) >= 4 and seq in lower:
            issues.append(f"Contains a keyboard pattern ({seq}).")
            break
        if len(seq) >= 4 and seq[::-1] in lower:
            issues.append(f"Contains a reversed keyboard pattern ({seq[::-1]}).")
            break

    if re.fullmatch(r"\d+", password):
        issues.append("Password is digits-only.")

    if re.fullmatch(r"[A-Za-z]+", password):
        issues.append("Password is letters-only (no digits or symbols).")

    # Year-like suffix/prefix often used in "Password2024!" style secrets.
    if re.search(r"(19|20)\d{2}", password):
        issues.append("Contains a 4-digit year-like number.")

    return issues
