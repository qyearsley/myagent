"""Tests for search_files: match format, directory pruning, and the result cap.

The cap and the pruning both exist to keep the model's context from being
flooded, so they are worth pinning down.
"""

from functions.search_files import search_files


def test_reports_matches_as_path_line_content(sandbox):
    assert search_files(str(sandbox), "VALUE") == "pkg/util.py:1:VALUE = 1"


def test_reports_when_nothing_matches(sandbox):
    assert search_files(str(sandbox), "absent") == "No matches found for 'absent'"


def test_searches_only_within_the_given_subdirectory(sandbox):
    (sandbox / "top.txt").write_text("VALUE\n")
    result = search_files(str(sandbox), "VALUE", "pkg")
    assert "util.py" in result
    assert "top.txt" not in result


def test_skips_noise_directories(sandbox):
    (sandbox / "__pycache__").mkdir()
    (sandbox / "__pycache__" / "cached.py").write_text("VALUE\n")
    assert "__pycache__" not in search_files(str(sandbox), "VALUE")


def test_skips_files_it_cannot_decode(sandbox):
    (sandbox / "blob.bin").write_bytes(b"\xff\xfe\x00 VALUE\n")
    assert "blob.bin" not in search_files(str(sandbox), "VALUE")


def test_caps_the_number_of_results(sandbox, monkeypatch):
    monkeypatch.setattr("functions.search_files.MAX_RESULTS", 3)
    (sandbox / "many.txt").write_text("match\n" * 10)

    result = search_files(str(sandbox), "match")

    assert result.count("many.txt") == 3
    assert "stopped at 3 matches" in result
