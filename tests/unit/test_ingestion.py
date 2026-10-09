from pathlib import Path

import pytest

from researchmind.rag.ingestion import read_source


def test_read_text_file(tmp_path: Path) -> None:
    source = tmp_path / "sample.txt"
    source.write_text("hello world", encoding="utf-8")
    assert read_source(source) == [(1, "hello world")]


def test_unsupported_extension_raises(tmp_path: Path) -> None:
    source = tmp_path / "sample.csv"
    source.write_text("a,b", encoding="utf-8")
    with pytest.raises(ValueError, match="Unsupported file type"):
        read_source(source)
