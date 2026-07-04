"""
Goal 1: `aiman <command>` -> correct syntax + usage examples.
"""
from __future__ import annotations

from aiman.llm.client import LLMClient

_SYSTEM_PROMPT = (
    "You are a terse, accurate Linux command-line reference. Given a command "
    "or utility name, respond with:\n"
    "1. One-line description of what it does.\n"
    "2. The general syntax pattern.\n"
    "3. 3 short, realistic example invocations with a one-line explanation each.\n"
    "Do not pad with disclaimers. Do not invent flags that don't exist. If the "
    "input isn't a real command, say so plainly instead of guessing."
)


def explain_command(command_name: str, llm: LLMClient) -> str:
    if not command_name or not command_name.strip():
        raise ValueError("command_name must be a non-empty string")
    return llm.complete(system=_SYSTEM_PROMPT, user=command_name.strip())
