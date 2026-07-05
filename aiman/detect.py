"""
Decides which of the three modes a raw text blob belongs to, when the user
didn't call an explicit subcommand.

Heuristic (deliberately simple — see README "Design notes"):
  - single token, and it's a real binary on this machine   -> "explain"
  - multiple tokens, first token is a real binary          -> "check"
  - multiple tokens, first token is NOT a real binary       -> "generate"
  - single token, NOT a real binary                         -> "generate"
    (e.g. "delete" isn't a binary; treat as an English fragment)

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

    if len(tokens) == 1:
        return "explain" if is_known_binary(first) else "generate"

    if is_known_binary(first):
        return "explain"

    return "generate"

    return "generate"
