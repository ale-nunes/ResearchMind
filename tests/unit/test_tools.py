import pytest

from researchmind.tools.calculator import python_calculator
from researchmind.tools.notes import read_note, save_note


def test_calculator_arithmetic() -> None:
    assert python_calculator("(2 + 3) * 4") == "20"


def test_calculator_rejects_code() -> None:
    with pytest.raises(ValueError):
        python_calculator("__import__('os').system('whoami')")


def test_notes_round_trip(tmp_path) -> None:
    db = tmp_path / "notes.sqlite3"
    note_id = save_note("Test", "Research note", db)
    note = read_note(note_id, db)
    assert note is not None
    assert note["title"] == "Test"
    assert note["content"] == "Research note"


def test_missing_note(tmp_path) -> None:
    assert read_note(999, tmp_path / "notes.sqlite3") is None
