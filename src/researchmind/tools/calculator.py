"""Safe arithmetic calculator based on a restricted Python AST."""

import ast
import math
import operator
from collections.abc import Callable
from typing import cast

_ALLOWED_BINARY = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}

_ALLOWED_UNARY = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}

BinaryOperation = Callable[[int | float, int | float], int | float]
UnaryOperation = Callable[[int | float], int | float]


def python_calculator(expression: str) -> str:
    """Evaluate arithmetic only; reject names, calls, attributes, and oversized expressions."""
    if len(expression) > 200:
        raise ValueError("Expression is too long (maximum 200 characters).")

    try:
        tree = ast.parse(expression, mode="eval")
        result = _evaluate(tree.body)
    except (SyntaxError, ZeroDivisionError, OverflowError) as exc:
        raise ValueError(f"Invalid arithmetic expression: {exc}") from exc

    if not math.isfinite(float(result)):
        raise ValueError("Result must be finite.")

    return str(result)


def _evaluate(node: ast.AST) -> int | float:
    if (
        isinstance(node, ast.Constant)
        and isinstance(node.value, (int, float))
        and not isinstance(node.value, bool)
    ):
        if abs(node.value) > 10**12:
            raise ValueError("Numeric literal is too large.")
        return node.value

    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_BINARY:
        left = _evaluate(node.left)
        right = _evaluate(node.right)

        if isinstance(node.op, ast.Pow) and abs(right) > 10:
            raise ValueError("Exponent magnitude must not exceed 10.")

        binary_operation = cast(
            BinaryOperation,
            _ALLOWED_BINARY[type(node.op)],
        )
        value = binary_operation(left, right)

        if abs(value) > 10**100:
            raise ValueError("Result is too large.")

        return value

    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_UNARY:
        unary_operation = cast(
            UnaryOperation,
            _ALLOWED_UNARY[type(node.op)],
        )
        return unary_operation(_evaluate(node.operand))

    raise ValueError("Only numeric literals and arithmetic operators are allowed.")
