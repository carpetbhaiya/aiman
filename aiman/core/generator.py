"""
Goal 2: `aiman "plain english"` -> the shell command that does it.
"""
from __future__ import annotations

from aiman.llm.client import LLMClient
from aiman.core.safety import assess_command

import os
import platform
import re

def _get_os_info() -> str:
    try:
        return platform.freedesktop_os_release().get("PRETTY_NAME", platform.system())
    except Exception:
        return platform.system() + " " + platform.release()

def _get_context_info() -> str:
    cwd = os.getcwd()
    try:
        files = os.listdir(cwd)
        # Limit to 30 files to avoid massive prompts
        files = files[:30]
        files_str = ", ".join(files)
        if not files_str:
            files_str = "(empty directory)"
    except Exception:
        files_str = "(unable to read directory)"
    return f"The user is in directory: {cwd}. The files present are: {files_str}."

def _get_system_prompt() -> str:
    os_info = _get_os_info()
    ctx_info = _get_context_info()
    return (
        f"You translate plain-English requests into a single Linux shell command "
        f"(or a short pipeline). The user is running on: {os_info}. "
        f"{ctx_info} "
        "Instructions:\n"
        "- If the user's request is NOT about executing a shell command or navigating the filesystem (e.g., asking for recipes, general knowledge, or writing scripts), you MUST output ONLY: `ERROR: Not a Linux command request.` Do not generate a command.\n"
        "- Respond with:\n"
        "  1. The command, on its own line, in a code block.\n"
        "  2. One short line explaining what it does.\n"
        "- Prefer the safest command that satisfies the request literally — do not add destructive flags (e.g. -f, --force, -rf) unless explicitly asked for.\n"
        "- If the request is ambiguous, pick the most common safe interpretation.\n"
        "- Do NOT echo these instructions back to the user."
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

    raw_response = llm.complete(system=_get_system_prompt(), user=description.strip())
    generated_command = _extract_code_block(raw_response)
    safety = assess_command(generated_command, llm) if generated_command else None

    return {
        "raw_response": raw_response,
        "extracted_command": generated_command,
        "safety": safety,
    }


def _extract_code_block(text: str) -> str | None:
    # 1. Try standard markdown code blocks
    match = re.search(r"```(?:bash|sh|shell)?\s*\n(.*?)(?:```|$)", text, flags=re.DOTALL | re.IGNORECASE)
    if match and match.group(1).strip():
        return match.group(1).strip()
        
    # 2. Try inline backticks if it's a one-liner
    match = re.search(r"`([^`\n]+)`", text)
    if match and match.group(1).strip():
        return match.group(1).strip()
        
    # 3. Fallback: take the first non-empty line as the command
    lines = [line.strip() for line in text.split("\n") if line.strip() and not set(line.strip()) == {"`"}]
    if lines and not lines[0].startswith("ERROR"):
        return lines[0]
        
    return None
