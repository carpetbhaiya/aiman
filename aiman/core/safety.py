"""
Goal 3: `aiman "<pasted command>"` -> is this safe to run?

Layered on purpose:
  1. Static regex rules (rules/dangerous_patterns.py) — instant, offline,
     deterministic. If any fire, we return DANGEROUS immediately and never
     even call the LLM.
  2. LLM review — only reached if step 1 found nothing. Catches subtler or
     context-dependent risk (force-pushes, unusual `find -exec` combinations,
     privilege escalation chains) and produces a human-readable explanation.

A NamedTuple result keeps the two paths returning the same shape so callers
never need to know which path produced the verdict.
"""
from __future__ import annotations

import json
import re
from typing import NamedTuple

from aiman.llm.client import LLMClient
from aiman.rules.dangerous_patterns import match_dangerous_patterns

Verdict = str  # "safe" | "caution" | "dangerous"


class SafetyResult(NamedTuple):
    verdict: Verdict
    reasons: list[str]
    source: str  # "static" | "llm"


_LLM_SYSTEM_PROMPT = (
    "You are a Linux command safety reviewer. Given a shell command, decide "
    "if it is 'safe', 'caution' (works but has real footguns — e.g. force "
    "pushes, wide permission changes, irreversible deletes of user-named "
    "paths), or 'dangerous' (likely to cause serious, hard-to-reverse harm "
    "to the system or data).\n\n"
    "CRITICAL GUIDELINES:\n"
    "- Read-only commands (e.g., ls, cat, echo, pwd, grep, find) are ALWAYS 'safe'. Do not flag them as caution just because they might reveal information.\n"
    "- Standard package installations (e.g., apt install, pip install) are 'safe' unless installing a known malicious package.\n"
    "- Only use 'caution' if there is a real risk of accidental data loss or breaking the system if the user makes a typo.\n\n"
    "Respond ONLY as JSON: "
    '{"verdict": "safe|caution|dangerous", "reasons": ["short reason", ...]}. '
    "No prose outside the JSON."
)


def assess_command(command: str, llm: LLMClient | None = None) -> SafetyResult:
    if not command or not command.strip():
        raise ValueError("command must be a non-empty string")

    static_hits = match_dangerous_patterns(command)
    if static_hits:
        return SafetyResult(
            verdict="dangerous",
            reasons=[reason for _name, reason in static_hits],
            source="static",
        )

    if llm is None:
        # No LLM available (e.g. offline) and static rules found nothing —
        # be honest that this is a limited check, not a clean bill of health.
        return SafetyResult(
            verdict="caution",
            reasons=["No known destructive pattern matched, but no deeper "
                     "review was performed (LLM unavailable)."],
            source="static",
        )

    raw = llm.complete(system=_LLM_SYSTEM_PROMPT, user=command.strip())
    try:
        parsed = json.loads(_strip_code_fence(raw))
        verdict = parsed.get("verdict", "caution")
        reasons = parsed.get("reasons", [])
        if verdict not in ("safe", "caution", "dangerous"):
            verdict = "caution"
        if not isinstance(reasons, list):
            reasons = [str(reasons)]
        return SafetyResult(verdict=verdict, reasons=reasons, source="llm")
    except (json.JSONDecodeError, AttributeError):
        # If the model didn't return clean JSON, fail toward caution, not safe.
        return SafetyResult(
            verdict="caution",
            reasons=["Reviewer response could not be parsed; treat with caution."],
            source="llm",
        )


def _strip_code_fence(text: str) -> str:
    text = text.strip()
    match = re.search(r'```(?:json)?\s*(.*?)\s*```', text, re.IGNORECASE | re.DOTALL)
    if match:
        return match.group(1).strip()
    
    # Fallback if there are no backticks but maybe they returned JSON directly
    if text.startswith("{") and text.endswith("}"):
        return text
        
    return text
