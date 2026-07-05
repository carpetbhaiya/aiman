"""
Decides which of the three modes a raw text blob belongs to, when the user
didn't call an explicit subcommand.

Heuristic (deliberately simple — see README "Design notes"):
  - first token is a real binary on this machine  -> "explain"
    (both single commands like `ls` and full commands like `rm -rf /`)
  - first token is NOT a real binary              -> "generate"
    (e.g. "delete my temp files" is treated as plain English)

This is intentionally NOT an NLP classifier. It is a fast, explainable
guess. Ambiguous cases should be resolved with explicit subcommands
(`aiman explain|gen|check`), not by making this function smarter.
"""
from __future__ import annotations

import shutil


def is_known_binary(token: str) -> bool:
    return shutil.which(token) is not None


def detect_mode(raw_input: str) -> str:
    text = raw_input.strip()
    if not text:
        raise ValueError("input must be non-empty")

    tokens = text.split()
    first = tokens[0]

    if is_known_binary(first):
        return "explain"

    return "generate"
