import pytest

from aiman.core.explainer import explain_command


def test_explain_passes_command_to_llm_and_returns_response(fake_llm):
    fake_llm._responses.append("tar: archive utility.\nSyntax: tar [options] files\nExample: tar -czf a.tar.gz dir/")
    result = explain_command("tar", fake_llm)
    assert "tar" in result.lower()
    assert fake_llm.calls[0]["user"] == "tar"


def test_explain_strips_whitespace_from_input(fake_llm):
    fake_llm._responses.append("ok")
    explain_command("  grep  ", fake_llm)
    assert fake_llm.calls[0]["user"] == "grep"


def test_explain_rejects_empty_input(fake_llm):
    with pytest.raises(ValueError):
        explain_command("   ", fake_llm)
