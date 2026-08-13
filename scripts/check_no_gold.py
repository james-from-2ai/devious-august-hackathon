#!/usr/bin/env python3
"""Fail the commit if a gold set or answer key is being added to this repo.

This repo is shared with every pair. The gold answers live in the scorer
repo and must never appear here, not even briefly in a commit that is
later reverted, since git keeps the object forever.

Runs two checks:
  1. Filename patterns: anything matching gold* or answers*
  2. Content sniff: a staged .jsonl carrying a gold_answer / accept_if /
     reject_if key, whatever it happens to be named

Installed via pre-commit, and also callable directly:
    python scripts/check_no_gold.py           # checks staged files
    python scripts/check_no_gold.py a.py b.py # checks named files
"""

import fnmatch
import os
import subprocess
import sys

BANNED_NAME_PATTERNS = ["gold*", "answers*", "*answer_key*", "*answerkey*"]

# Keys that only ever appear in a gold record. calibration.jsonl is the
# sanctioned teaching file and is allowed to carry scores and categories,
# so those are deliberately not on this list.
BANNED_CONTENT_KEYS = ['"gold_answer"', '"accept_if"', '"reject_if"',
                       '"rubric_notes"', '"source_locator"']


def staged_files():
    out = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
        capture_output=True, text=True, check=False)
    return [line for line in out.stdout.splitlines() if line.strip()]


def name_violations(paths):
    bad = []
    for path in paths:
        base = os.path.basename(path).lower()
        for pattern in BANNED_NAME_PATTERNS:
            if fnmatch.fnmatch(base, pattern):
                bad.append((path, f"filename matches {pattern!r}"))
                break
    return bad


def content_violations(paths):
    bad = []
    for path in paths:
        if not path.lower().endswith((".jsonl", ".json")):
            continue
        if not os.path.exists(path):
            continue
        try:
            with open(path, encoding="utf-8", errors="replace") as fh:
                text = fh.read()
        except OSError:
            continue
        hits = [k for k in BANNED_CONTENT_KEYS if k in text]
        if hits:
            bad.append((path, f"contains gold record keys: {', '.join(hits)}"))
    return bad


def main():
    paths = sys.argv[1:] or staged_files()
    if not paths:
        return 0

    bad = name_violations(paths) + content_violations(paths)
    if not bad:
        return 0

    print("BLOCKED: gold set material cannot be committed to this repo.\n",
          file=sys.stderr)
    for path, why in bad:
        print(f"  {path}\n      {why}", file=sys.stderr)
    print("\nThe gold answers belong in hackathon-scorer only. If this is a "
          "false positive, rename the file rather than bypassing the hook.",
          file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
