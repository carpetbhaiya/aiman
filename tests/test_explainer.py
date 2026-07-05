import pytest

from aiman.core.explainer import explain_command, explain_command_stream


def test_explain_passes_command_to_llm_if_not_in_cache(fake_llm):
    # 'htop' is not in the cache, so it should hit the LLM
    fake_llm._responses.append("htop: interactive process viewer")
    result = explain_command("htop", fake_llm)
    assert "htop" in result.lower()
    assert len(fake_llm.calls) == 1
    assert fake_llm.calls[0]["user"] == "htop"


def test_explain_strips_whitespace_from_input_for_llm(fake_llm):
    # 'awk' is not in the cache
    fake_llm._responses.append("ok")
    explain_command("  awk  ", fake_llm)
    assert len(fake_llm.calls) == 1
    assert fake_llm.calls[0]["user"] == "awk"


def test_explain_uses_cache_if_present(fake_llm):
    # 'ls' is in the cache
    result = explain_command("ls", fake_llm)
    assert "**`ls`**: Lists directory contents" in result
    # The LLM should NOT have been called
    assert len(fake_llm.calls) == 0


def test_explain_stream_uses_cache_if_present(fake_llm):
    # 'tar' is in the cache
    stream = explain_command_stream("tar", fake_llm)
    chunks = list(stream)
    
    assert len(chunks) == 1
    assert "**`tar`**: Tape archiver utility" in chunks[0]
    # The LLM should NOT have been called
    assert len(fake_llm.calls) == 0


def test_explain_rejects_empty_input(fake_llm):
    with pytest.raises(ValueError):
        explain_command("   ", fake_llm)
