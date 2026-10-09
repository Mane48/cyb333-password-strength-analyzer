# Password Strength Analyzer (CYB333 Security Automation)

Python CLI tool that evaluates password strength for security-awareness and automation workflows. It scores passwords using length, character-class diversity, estimated entropy, a built-in common-password list, and weak-construction pattern checks (sequences, keyboard walks, years, repeats). It then prints actionable improvement suggestions.

This repository is the course project for **CYB333 Security Automation** at National University.

## Objectives

- Automate password-quality assessment instead of relying on ad-hoc manual checks
- Detect weak patterns commonly abused in credential stuffing and guessing attacks
- Produce human-readable and machine-readable (JSON) reports suitable for demos or pipelines
- Keep the implementation dependency-light (runtime uses the Python standard library)

## Features

- Interactive prompt mode (password not echoed)
- Single-password CLI evaluation
- Batch mode from a text file (one password per line)
- JSON report export
- Built-in common-password wordlist (customizable)
- Pattern heuristics: repeats, sequences, keyboard walks, year-like numbers, class imbalance
- Masked preview option (first/last character only)

## Requirements

- Python **3.10+**
- Runtime: **no third-party packages required**
- Optional for development/docs:
  - `pytest`
  - `python-docx` (regenerate submission Word documents)

## Setup

```bash
# Clone (after you push / have the repo URL)
git clone https://github.com/Mane48/cyb333-password-strength-analyzer.git
cd cyb333-password-strength-analyzer

# Optional virtual environment
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
# macOS/Linux
# source .venv/bin/activate

pip install -r requirements.txt
```

## Usage

### Interactive (recommended)

```bash
python main.py --prompt
```

### Single password (useful for demos; avoid in shared terminals)

```bash
python main.py --password "Summer2024!"
```

### Batch file

```bash
python main.py --file samples/passwords.txt --reveal-preview
```

### JSON output / report file

```bash
python main.py --file samples/passwords.txt --json -o samples/demo_report.json
```

### Custom wordlist

```bash
python main.py --password "hunter2" --wordlist password_analyzer/wordlists/common_passwords.txt
```

## Example output

```text
=== Result ===
Length:          11
Score:           18/100
Rating:          Very Weak
Entropy (bits):  72.1
Charset size:    94
Common list hit: False
Checks:
  [PASS] min_length_8
  [FAIL] min_length_12
  ...
Issues:
  - Contains a 4-digit year-like number.
Suggestions:
  - Avoid sequences, keyboard walks, years, and repeated runs.
```

## Project layout

```text
main.py                      # CLI entry point
password_analyzer/
  analyzer.py                # Scoring engine
  patterns.py                # Pattern heuristics
  cli.py                     # Argument parsing / report formatting
  wordlists/common_passwords.txt
samples/passwords.txt        # Demo inputs
tests/test_analyzer.py       # pytest suite
submissions/                 # Course Word-doc drafts for Navigate upload
scripts/generate_submissions.py
```

## Running tests

```bash
pip install pytest
pytest -q
```

## Security notes

- Do **not** commit real production passwords or API keys.
- Batch files in this repo are synthetic demo values only.
- Prefer `--prompt` over putting secrets on the command line (shell history risk).

## AI tools disclosure (course requirement)

AI assistants (including Cursor) were used to help scaffold the repository, draft documentation, and accelerate implementation of scoring heuristics. All code was reviewed and adapted for this course. Personal reflection sections in the final report are reserved for the student author and are not AI-authored.

## Author

Emmanuel Sanchez Salazar  
Course: CYB333 Security Automation  
Project: Password Strength Analyzer
