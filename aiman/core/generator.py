"""
Goal 2: `aiman "plain english"` -> the shell command that does it.
"""
from __future__ import annotations

from aiman.llm.client import LLMClient
from aiman.core.safety import assess_command

import platform
try:
    _os_info = platform.freedesktop_os_release().get("PRETTY_NAME", platform.system())
except Exception:
    _os_info = platform.system() + " " + platform.release()

_SYSTEM_PROMPT = (
    f"You translate plain-English requests into a single Linux shell command "
    f"(or a short pipeline). The user is running on: {_os_info}. "
    "Respond with:\n"
    "1. The command, on its own line, in a code block.\n"
    "2. One short line explaining what it does.\n"
    "Prefer the safest command that satisfies the request literally — do not "
    "add destructive flags (e.g. -f, --force, -rf) unless the user explicitly "
    "asked for them. If the request is ambiguous, pick the most common safe "
    "interpretation and say so in one line."
)


def generate_command(description: str, llm: LLMClient) -> dict:
    """
    Returns {"raw_response": str, "safety": SafetyResult}.

    Every generated command is run back through the safety checker before
    being handed to the user — an AI-generated command is not exempt from
    the same scrutiny as a pasted one.
    """
    if not description or not description.strip():
        raise ValueError("description must be a non-empty string")

    raw_response = llm.complete(system=_SYSTEM_PROMPT, user=description.strip())
    generated_command = _extract_code_block(raw_response)
    safety = assess_command(generated_command, llm) if generated_command else None

    return {
        "raw_response": raw_response,
        "extracted_command": generated_command,
        "safety": safety,
    }


def _extract_code_block(text: str) -> str | None:
    if "```" not in text:
        # No code fence — fall back to the first non-empty line.
        for line in text.splitlines():
            if line.strip():
                return line.strip()
        return None
    parts = text.split("```")
    if len(parts) < 2:
        return None
    block = parts[1]
    lines = [ln for ln in block.splitlines() if ln.strip()]
    if not lines:
        return None
    # Strip a language hint like "bash" if it's the whole first line.
    if lines[0].strip().isalpha() and len(lines) > 1:
        lines = lines[1:]
    return "\n".join(lines).strip() if lines else None
