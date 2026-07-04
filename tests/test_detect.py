import pytest

from aiman.detect import detect_mode


def test_single_known_binary_is_explain():
    # 'ls' exists on essentially every Linux/CI box
    assert detect_mode("ls") == "explain"


def test_english_sentence_is_generate():
    assert detect_mode("list all pdfs modified today") == "generate"


def test_full_command_with_real_binary_is_check():
    assert detect_mode("rm -rf /") == "check"


def test_full_command_with_unknown_first_token_is_generate():
    assert detect_mode("please delete my temp files") == "generate"


def test_empty_input_raises():
    with pytest.raises(ValueError):
        detect_mode("   ")


def test_whitespace_is_trimmed_before_tokenizing():
    assert detect_mode("   ls   ") == "explain"
