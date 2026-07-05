import json

import pytest

from aiman.core.generator import generate_command, _extract_code_block


def test_generate_extracts_command_from_code_block(fake_llm):
    fake_llm._responses.append(
        "```bash\nfind . -name '*.pdf' -mtime -1\n```\nFinds pdfs modified in the last day."
    )
    # second call is the internal safety re-check
    fake_llm._responses.append(json.dumps({"verdict": "safe", "reasons": []}))

    result = generate_command("list all pdfs modified today", fake_llm)

    assert result["extracted_command"] == "find . -name '*.pdf' -mtime -1"
    assert result["safety"].verdict == "safe"


def test_generate_runs_generated_command_back_through_safety_check(fake_llm):
    # Model (mis)behaves and generates something destructive.
    fake_llm._responses.append("```bash\nrm -rf /\n```\n")
    result = generate_command("clean up my whole disk", fake_llm)

    # rm -rf / is caught by static rules -> no second (LLM) call needed
    assert result["safety"].verdict == "dangerous"
    assert result["safety"].source == "static"


def test_generate_rejects_empty_input(fake_llm):
    with pytest.raises(ValueError):
        generate_command("", fake_llm)


@pytest.mark.parametrize("text,expected", [
    ("```\nls -la\n```", "ls -la"),
    ("```bash\ngrep -r foo .\n```", "grep -r foo ."),
    # Scenario 1: No language tag, just backticks (tar)
    ("```\ntar -czvf backup.tar.gz /etc\n```\nBacks up the /etc directory.", "tar -czvf backup.tar.gz /etc"),
    # Scenario 2: Single inline backticks (chmod)
    ("`chmod +x script.sh`\nMakes the script executable.", "chmod +x script.sh"),
    # Scenario 3: No backticks at all (ffmpeg)
    ("ffmpeg -i input.mp4 output.avi\nConverts the mp4 video to avi format.", "ffmpeg -i input.mp4 output.avi"),
    # Scenario 4: No backticks, empty lines before command (curl)
    ("\n\ncurl -O https://example.com/file.zip\n\nDownloads the file.", "curl -O https://example.com/file.zip"),
    # Empty cases
    ("```\n\n```", None),
    ("", None),
])
def test_extract_code_block_variants(text, expected):
    assert _extract_code_block(text) == expected
