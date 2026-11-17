import pytest

from word_count import count_lines_with_word


def test_counts_each_line_once_even_if_word_repeats(tmp_path):
    # Proves we count lines, not occurrences. Catches a bug where a line with
    # the word twice is counted twice, or a line is missed.
    f = tmp_path / "a.txt"
    f.write_text("error one\nok\nerror error\nERROR again\n", encoding="utf-8")
    assert count_lines_with_word(f, "error") == 3


def test_empty_file_and_empty_word(tmp_path):
    # Proves the edge cases: an empty file gives 0, and an empty word is
    # rejected. Catches the bug where "" matches every line and inflates counts.
    f = tmp_path / "empty.txt"
    f.write_text("", encoding="utf-8")
    assert count_lines_with_word(f, "x") == 0
    with pytest.raises(ValueError):
        count_lines_with_word(f, "")
