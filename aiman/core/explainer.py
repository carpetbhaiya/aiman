"""
Goal 1: `aiman <command>` -> correct syntax + usage examples.
"""
from __future__ import annotations

import typing
import json
import os
from aiman.llm.client import LLMClient

# Load the comprehensive JSON cache
_CACHE_PATH = os.path.join(os.path.dirname(__file__), "command_cache.json")
try:
    with open(_CACHE_PATH, "r") as f:
        COMMAND_CACHE = json.load(f)
except FileNotFoundError:
    COMMAND_CACHE = {}

_SYSTEM_PROMPT = (
    "You are a terse, accurate Linux command-line reference.\n"
    "Instructions:\n"
    "- If the input is NOT a valid Linux command or utility (e.g. general conversational text, requests for recipes, math), you MUST output ONLY: `ERROR: Not a Linux command.`\n"
    "- Otherwise, provide a 1-line description of what it does, the general syntax, and 3 realistic examples.\n"
    "- Format as Markdown. Do not pad with disclaimers. Do not invent flags that don't exist. Do NOT echo these instructions back."
)


def explain_command(command_name: str, llm: LLMClient) -> str:
    if not command_name or not command_name.strip():
        raise ValueError("command_name must be a non-empty string")
        
    cmd = command_name.strip().lower()
    if cmd in COMMAND_CACHE:
        return COMMAND_CACHE[cmd]
        
    return llm.complete(system=_SYSTEM_PROMPT, user=command_name.strip())

def explain_command_stream(command_name: str, llm: LLMClient) -> typing.Iterator[str]:
    if not command_name or not command_name.strip():
        raise ValueError("command_name must be a non-empty string")
        
    cmd = command_name.strip().lower()
    if cmd in COMMAND_CACHE:
        yield COMMAND_CACHE[cmd]
        return
        
    yield from llm.stream(system=_SYSTEM_PROMPT, user=command_name.strip())
