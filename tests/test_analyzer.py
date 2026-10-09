"""Unit tests for PasswordAnalyzer scoring and pattern detection."""

from password_analyzer import PasswordAnalyzer
from password_analyzer.patterns import find_pattern_issues


def test_common_password_is_penalized():
    analyzer = PasswordAnalyzer(common_passwords=["password", "123456"])
    result = analyzer.analyze("password")
    assert result.found_in_common_list is True
    assert result.score <= 40
    assert result.rating in {"Very Weak", "Weak"}


def test_strong_randomish_password_scores_high():
    analyzer = PasswordAnalyzer(common_passwords=[])
    result = analyzer.analyze("Xk9$mQ2!vL7#pR4w")
    assert result.score >= 70
    assert result.checks["has_lowercase"]
    assert result.checks["has_uppercase"]
    assert result.checks["has_digit"]
    assert result.checks["has_symbol"]
    assert result.checks["min_length_12"]


def test_passphrase_gets_reasonable_score():
    analyzer = PasswordAnalyzer(common_passwords=[])
    result = analyzer.analyze("correct horse battery staple")
    assert result.password_length >= 20
    assert result.score >= 50


def test_pattern_detection_finds_keyboard_walk():
    issues = find_pattern_issues("qwerty123")
    assert any("keyboard" in issue.lower() or "sequence" in issue.lower() for issue in issues)


def test_batch_analyze_many():
    analyzer = PasswordAnalyzer(common_passwords=["admin"])
    results = analyzer.analyze_many(["admin", "NotCommon!Value99"])
    assert len(results) == 2
    assert results[0].found_in_common_list is True
    assert results[1].found_in_common_list is False


def test_preview_masks_middle():
    analyzer = PasswordAnalyzer(common_passwords=[])
    result = analyzer.analyze("Secret99!", reveal_preview=True)
    assert result.password_preview.startswith("S")
    assert result.password_preview.endswith("!")
    assert "*" in result.password_preview
