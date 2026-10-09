
import pytest

from researchmind.tools import python_calculator


def test_calculator_rejects_python_code() -> None:
    with pytest.raises(ValueError):
        python_calculator(
            '__import__("os").system("whoami")'
        )


def test_calculator_accepts_arithmetic() -> None:
    result = python_calculator("(1200 * 0.15) + 40")
    assert float(result) == 220.0
