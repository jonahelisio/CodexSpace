from __future__ import annotations

from .ast_nodes import BinaryOp, FunctionCall, Node, Number, UnaryOp, Variable


PRECEDENCE = {
    "+": 10,
    "-": 10,
    "*": 20,
    "/": 20,
    "**": 30,
    "u+": 40,
    "u-": 40,
}


def to_formula(node: Node) -> str:
    return _render(node, parent_precedence=0, right_child=False)


def _render(node: Node, parent_precedence: int, right_child: bool) -> str:
    if isinstance(node, Number):
        if float(node.value).is_integer():
            return str(int(node.value))
        return repr(node.value)
    if isinstance(node, Variable):
        return node.name
    if isinstance(node, FunctionCall):
        return f"{node.name}({', '.join(_render(arg, 0, False) for arg in node.args)})"
    if isinstance(node, UnaryOp):
        prec = PRECEDENCE[f"u{node.op}"]
        text = f"{node.op}{_render(node.operand, prec, False)}"
        if prec < parent_precedence:
            return f"({text})"
        return text
    if isinstance(node, BinaryOp):
        prec = PRECEDENCE[node.op]
        left = _render(node.left, prec, False)
        right_prec = prec - 1 if node.op == "**" else prec
        right = _render(node.right, right_prec, True)
        text = f"{left} {node.op} {right}"
        need_parens = prec < parent_precedence
        if node.op == "**" and right_child and prec <= parent_precedence:
            need_parens = True
        if need_parens:
            return f"({text})"
        return text
    raise TypeError(f"Unsupported node type: {type(node).__name__}")
