import pytest
import typing

class FakeLLMClient:
    """
    Test double for LLMClient. Queue up canned responses; each call to
    .complete() pops the next one. Records every call for assertions.
    """

    def __init__(self, responses=None):
        self._responses = list(responses or [])
        self.calls = []

    def complete(self, system: str, user: str) -> str:
        self.calls.append({"system": system, "user": user})
        if not self._responses:
            raise AssertionError("FakeLLMClient ran out of queued responses")
        return self._responses.pop(0)

    def stream(self, system: str, user: str) -> typing.Iterator[str]:
        response = self.complete(system, user)
        yield response



@pytest.fixture
def fake_llm():
    return FakeLLMClient()
