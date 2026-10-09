"""Command-line interface for the Password Strength Analyzer."""

from __future__ import annotations

import argparse
import getpass
import json
import sys
from pathlib import Path
from typing import List, Optional

from .analyzer import PasswordAnalyzer


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="password-analyzer",
        description=(
            "Analyze password strength against length, character diversity, "
            "common-password lists, and weak construction patterns."
        ),
    )
    parser.add_argument(
        "-p",
        "--password",
        help="Password to evaluate (prefer --prompt for interactive use).",
    )
    parser.add_argument(
        "--prompt",
        action="store_true",
        help="Prompt for a password without echoing it to the terminal.",
    )
    parser.add_argument(
        "-f",
        "--file",
        type=Path,
        help="Path to a text file with one password per line (batch mode).",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Optional path to write a JSON report.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print JSON to stdout instead of a human-readable summary.",
    )
    parser.add_argument(
        "--reveal-preview",
        action="store_true",
        help="Include a masked password preview (first/last char only).",
    )
    parser.add_argument(
        "--wordlist",
        type=Path,
        help="Optional custom common-password wordlist (one entry per line).",
    )
    return parser


def _load_passwords_from_file(path: Path) -> List[str]:
    if not path.is_file():
        raise FileNotFoundError(f"Input file not found: {path}")
    lines = path.read_text(encoding="utf-8").splitlines()
    return [line.rstrip("\n\r") for line in lines if line.strip()]


def _format_human(index: Optional[int], result) -> str:
    header = f"Result #{index}" if index is not None else "Result"
    lines = [
        f"=== {header} ===",
        f"Length:          {result.password_length}",
        f"Score:           {result.score}/100",
        f"Rating:          {result.rating}",
        f"Entropy (bits):  {result.entropy_bits}",
        f"Charset size:    {result.charset_size}",
        f"Common list hit: {result.found_in_common_list}",
    ]
    if result.password_preview:
        lines.append(f"Preview:         {result.password_preview}")
    lines.append("Checks:")
    for key, value in result.checks.items():
        mark = "PASS" if value else "FAIL"
        lines.append(f"  [{mark}] {key}")
    if result.issues:
        lines.append("Issues:")
        for issue in result.issues:
            lines.append(f"  - {issue}")
    if result.suggestions:
        lines.append("Suggestions:")
        for tip in result.suggestions:
            lines.append(f"  - {tip}")
    return "\n".join(lines)


def main(argv: Optional[List[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    sources = sum(bool(x) for x in (args.password, args.prompt, args.file))
    if sources != 1:
        parser.error("Specify exactly one of: --password, --prompt, or --file")

    if args.wordlist:
        words = args.wordlist.read_text(encoding="utf-8").splitlines()
        analyzer = PasswordAnalyzer(common_passwords=words)
    else:
        analyzer = PasswordAnalyzer()

    passwords: List[str]
    if args.file:
        passwords = _load_passwords_from_file(args.file)
    elif args.prompt:
        passwords = [getpass.getpass("Enter password to analyze: ")]
    else:
        passwords = [args.password]

    results = analyzer.analyze_many(passwords, reveal_preview=args.reveal_preview)
    payload = [r.to_dict() for r in results]

    if args.output:
        args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        chunks = []
        multi = len(results) > 1
        for idx, result in enumerate(results, start=1):
            chunks.append(_format_human(idx if multi else None, result))
        print("\n\n".join(chunks))
        if args.output:
            print(f"\nJSON report written to: {args.output}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
