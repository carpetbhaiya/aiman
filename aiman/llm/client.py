"""
Single choke point for all LLM calls.

Nothing else in the codebase should import `anthropic` directly. That
means:
- Tests mock this one class instead of monkeypatching a SDK deep inside
  three other modules.
- Swapping providers (or adding a local model fallback) is a one-file change.
"""
from __future__ import annotations

import os
import typing
from typing import Protocol

from aiman.config import load_config


class LLMClient(Protocol):
    def complete(self, system: str, user: str) -> str:
        """Send a single-turn prompt, return the raw text response."""
        ...


class OllamaLLMClient:
    """Real implementation, used at runtime."""

    def __init__(self, model: str | None = None, host: str | None = None):
        cfg = load_config()
        self.model = model or cfg.get("model", "qwen3:14b")
        # Use config host or fallback to default
        self._host = host or cfg.get("host", "http://localhost:11434")

        # Imported lazily so importing this module (and testing everything
        # around it) never requires the ollama package to be configured.
        from ollama import Client
        
        self._client = Client(host=self._host)

    def complete(self, system: str, user: str) -> str:
        response = self._client.chat(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            options={"num_predict": 1024},
        )
        return response["message"]["content"]

    def stream(self, system: str, user: str) -> typing.Iterator[str]:
        response = self._client.chat(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            options={"num_predict": 1024},
            stream=True
        )
        for chunk in response:
            if "message" in chunk and "content" in chunk["message"]:
                yield chunk["message"]["content"]


def get_default_client() -> LLMClient:
    return OllamaLLMClient()
