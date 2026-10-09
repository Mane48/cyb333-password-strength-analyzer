"""Core password strength scoring and recommendation engine."""

from __future__ import annotations

import math
import re
import string
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set

from .patterns import find_pattern_issues

_WORDLIST_PATH = Path(__file__).resolve().parent / "wordlists" / "common_passwords.txt"


@dataclass
class AnalysisResult:
    """Structured outcome of a single password evaluation."""

    password_length: int
    score: int
    rating: str
    entropy_bits: float
    charset_size: int
    checks: Dict[str, bool] = field(default_factory=dict)
    issues: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    found_in_common_list: bool = False
    # Never echo the raw password in reports by default; kept optional for demos.
    password_preview: str = ""

    def to_dict(self) -> Dict:
        return asdict(self)


class PasswordAnalyzer:
    """Evaluate password strength against common attack patterns."""

    RATING_BANDS = (
        (0, 20, "Very Weak"),
        (21, 40, "Weak"),
        (41, 60, "Fair"),
        (61, 80, "Strong"),
        (81, 100, "Very Strong"),
    )

    def __init__(self, common_passwords: Optional[Iterable[str]] = None) -> None:
        if common_passwords is None:
            self._common: Set[str] = self._load_wordlist(_WORDLIST_PATH)
        else:
            self._common = {p.strip().lower() for p in common_passwords if p.strip()}

    @staticmethod
    def _load_wordlist(path: Path) -> Set[str]:
        if not path.is_file():
            return set()
        words: Set[str] = set()
        with path.open(encoding="utf-8") as handle:
            for line in handle:
                item = line.strip()
                if item and not item.startswith("#"):
                    words.add(item.lower())
        return words

    def analyze(self, password: str, *, reveal_preview: bool = False) -> AnalysisResult:
        if password is None:
            raise ValueError("password must be a string")

        length = len(password)
        has_lower = any(c.islower() for c in password)
        has_upper = any(c.isupper() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_symbol = any(c in string.punctuation for c in password)
        has_space = any(c.isspace() for c in password)

        charset = 0
        if has_lower:
            charset += 26
        if has_upper:
            charset += 26
        if has_digit:
            charset += 10
        if has_symbol:
            charset += len(string.punctuation)
        if has_space:
            charset += 1
        # Account for other unicode / non-ascii lightly.
        if any(ord(c) > 127 for c in password):
            charset += 50

        entropy = 0.0 if length == 0 or charset == 0 else length * math.log2(charset)

        issues: List[str] = []
        suggestions: List[str] = []
        score = 0

        # Length scoring (max 35)
        if length >= 16:
            score += 35
        elif length >= 12:
            score += 28
        elif length >= 10:
            score += 20
        elif length >= 8:
            score += 12
        elif length >= 6:
            score += 6
        else:
            issues.append("Password is shorter than 8 characters.")
            suggestions.append("Use at least 12–16 characters.")

        # Character-class scoring (max 30)
        class_count = sum([has_lower, has_upper, has_digit, has_symbol])
        score += class_count * 7
        if class_count < 3:
            issues.append("Uses fewer than three character classes.")
            suggestions.append(
                "Mix uppercase, lowercase, digits, and symbols (or use a long passphrase)."
            )

        # Entropy contribution (max 20)
        if entropy >= 80:
            score += 20
        elif entropy >= 60:
            score += 15
        elif entropy >= 40:
            score += 10
        elif entropy >= 28:
            score += 5

        found_common = password.lower() in self._common
        if found_common:
            issues.append("Password appears in the built-in common-password list.")
            suggestions.append("Avoid well-known passwords; generate a unique secret.")
            score -= 40

        pattern_issues = find_pattern_issues(password)
        issues.extend(pattern_issues)
        if pattern_issues:
            score -= min(25, 5 * len(pattern_issues))
            suggestions.append("Avoid sequences, keyboard walks, years, and repeated runs.")

        # Passphrase bonus: multiple words separated by spaces/hyphens/underscores.
        if len(re.findall(r"[A-Za-z]{3,}", password)) >= 3 and length >= 16:
            score += 10
            suggestions.append(
                "Good passphrase structure detected — keep it long and uncommon."
            )

        score = max(0, min(100, score))
        rating = self._rating_for_score(score)

        if score < 61 and "Use at least 12–16 characters." not in suggestions:
            suggestions.append("Prefer a long random password or a 4+ word passphrase.")
        if not suggestions and score >= 80:
            suggestions.append("Looks solid. Store it in a password manager; never reuse it.")

        preview = ""
        if reveal_preview and password:
            if length <= 2:
                preview = "*" * length
            else:
                preview = f"{password[0]}{'*' * (length - 2)}{password[-1]}"

        return AnalysisResult(
            password_length=length,
            score=score,
            rating=rating,
            entropy_bits=round(entropy, 2),
            charset_size=charset,
            checks={
                "min_length_8": length >= 8,
                "min_length_12": length >= 12,
                "has_lowercase": has_lower,
                "has_uppercase": has_upper,
                "has_digit": has_digit,
                "has_symbol": has_symbol,
                "not_common_password": not found_common,
                "no_obvious_patterns": len(pattern_issues) == 0,
            },
            issues=issues,
            suggestions=list(dict.fromkeys(suggestions)),
            found_in_common_list=found_common,
            password_preview=preview,
        )

    @classmethod
    def _rating_for_score(cls, score: int) -> str:
        for low, high, label in cls.RATING_BANDS:
            if low <= score <= high:
                return label
        return "Unknown"

    def analyze_many(
        self, passwords: Iterable[str], *, reveal_preview: bool = False
    ) -> List[AnalysisResult]:
        return [self.analyze(p, reveal_preview=reveal_preview) for p in passwords]
