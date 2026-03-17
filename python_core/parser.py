from __future__ import annotations

import ast

from .ast_nodes import BinaryOp, FunctionCall, Node, Number, UnaryOp, Variable


ALLOWED_VARIABLES = {"x", "y", "z"}
ALLOWED_FUNCTIONS = {"sqrt", "sin", "cos", "tan", "abs", "exp", "log"}
ALLOWED_BINARY_OPS = {
    ast.Add: "+",
    ast.Sub: "-",
    ast.Mult: "*",
    ast.Div: "/",
    ast.Pow: "**",
}
ALLOWED_UNARY_OPS = {
    ast.UAdd: "+",
    ast.USub: "-",
}


class FormulaParseError(ValueError):
    pass


def parse_formula(formula: str) -> Node:
    try:
        parsed = ast.parse(formula, mode="eval")
    except SyntaxError as exc:
        raise FormulaParseError(str(exc)) from exc
    return _convert(parsed.body)


def _convert(node: ast.AST) -> Node:
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return Number(float(node.value))
        raise FormulaParseError(f"Unsupported constant: {node.value!r}")
    if isinstance(node, ast.Name):
        if node.id in ALLOWED_VARIABLES:
            return Variable(node.id)
        raise FormulaParseError(f"Unknown symbol: {node.id}")
    if isinstance(node, ast.UnaryOp):
        op = ALLOWED_UNARY_OPS.get(type(node.op))
        if op is None:
            raise FormulaParseError(f"Unsupported unary operator: {type(node.op).__name__}")
        return UnaryOp(op=op, operand=_convert(node.operand))
    if isinstance(node, ast.BinOp):
        op = ALLOWED_BINARY_OPS.get(type(node.op))
        if op is None:
            raise FormulaParseError(f"Unsupported binary operator: {type(node.op).__name__}")
        return BinaryOp(op=op, left=_convert(node.left), right=_convert(node.right))
    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name) or node.func.id not in ALLOWED_FUNCTIONS:
            raise FormulaParseError("Only approved math functions are allowed")
        return FunctionCall(
            name=node.func.id,
            args=tuple(_convert(arg) for arg in node.args),
        )
    raise FormulaParseError(f"Unsupported syntax: {type(node).__name__}")
