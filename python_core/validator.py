from __future__ import annotations

import math
from dataclasses import dataclass, field

from .ast_nodes import BinaryOp, FunctionCall, Node, Number, UnaryOp, Variable
from .parser import FormulaParseError, parse_formula


SAFE_FUNCTIONS = {
    "sqrt": math.sqrt,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "abs": abs,
    "exp": math.exp,
    "log": math.log,
}


@dataclass(frozen=True)
class ValidationResult:
    valid: bool
    reason: str
    node_count: int
    depth: int
    semantic_flags: tuple[str, ...] = field(default_factory=tuple)
    sample_min: float = math.nan
    sample_max: float = math.nan
    sample_zeroish_count: int = 0
    sample_negative_count: int = 0
    sample_positive_count: int = 0


def validate_formula(
    formula: str,
    *,
    max_nodes: int = 200,
    max_depth: int = 32,
    sample_points: tuple[tuple[float, float, float], ...] = (
        (-1.0, -1.0, -1.0),
        (-1.0, -1.0, 0.0),
        (-1.0, -1.0, 1.0),
        (-1.0, 0.0, -1.0),
        (-1.0, 0.0, 0.0),
        (-1.0, 0.0, 1.0),
        (-1.0, 1.0, -1.0),
        (-1.0, 1.0, 0.0),
        (-1.0, 1.0, 1.0),
        (0.0, -1.0, -1.0),
        (0.0, -1.0, 0.0),
        (0.0, -1.0, 1.0),
        (0.0, 0.0, -1.0),
        (0.0, 0.0, 0.0),
        (0.0, 0.0, 1.0),
        (0.0, 1.0, -1.0),
        (0.0, 1.0, 0.0),
        (0.0, 1.0, 1.0),
        (1.0, -1.0, -1.0),
        (1.0, -1.0, 0.0),
        (1.0, -1.0, 1.0),
        (1.0, 0.0, -1.0),
        (1.0, 0.0, 0.0),
        (1.0, 0.0, 1.0),
        (1.0, 1.0, -1.0),
        (1.0, 1.0, 0.0),
        (1.0, 1.0, 1.0),
    ),
    zero_epsilon: float = 0.1,
    variation_epsilon: float = 1e-6,
) -> ValidationResult:
    try:
        tree = parse_formula(formula)
    except FormulaParseError as exc:
        return ValidationResult(False, f"parse_error: {exc}", 0, 0)

    node_count = count_nodes(tree)
    depth = tree_depth(tree)
    if node_count > max_nodes:
        return ValidationResult(False, f"too_many_nodes: {node_count}", node_count, depth)
    if depth > max_depth:
        return ValidationResult(False, f"too_deep: {depth}", node_count, depth)

    try:
        evaluator = make_evaluator(tree)
        sample_values: list[float] = []
        for point in sample_points:
            value = evaluator(*point)
            if not math.isfinite(value):
                return ValidationResult(False, "non_finite_value", node_count, depth)
            sample_values.append(value)
    except Exception as exc:
        return ValidationResult(False, f"evaluation_error: {exc}", node_count, depth)

    sample_min = min(sample_values)
    sample_max = max(sample_values)
    zeroish_count = sum(1 for value in sample_values if abs(value) <= zero_epsilon)
    negative_count = sum(1 for value in sample_values if value < -zero_epsilon)
    positive_count = sum(1 for value in sample_values if value > zero_epsilon)

    semantic_flags: list[str] = []
    if abs(sample_max - sample_min) <= variation_epsilon:
        semantic_flags.append("constant_or_flat")
    if negative_count == 0 and positive_count == 0:
        semantic_flags.append("no_sign_separation")
    elif negative_count == 0 or positive_count == 0:
        semantic_flags.append("single_sign_only")
    else:
        semantic_flags.append("sign_variation")
    if zeroish_count == 0:
        semantic_flags.append("no_surface_band_detected")
    else:
        semantic_flags.append("surface_band_detected")

    return ValidationResult(
        True,
        "ok",
        node_count,
        depth,
        semantic_flags=tuple(semantic_flags),
        sample_min=sample_min,
        sample_max=sample_max,
        sample_zeroish_count=zeroish_count,
        sample_negative_count=negative_count,
        sample_positive_count=positive_count,
    )


def count_nodes(node: Node) -> int:
    if isinstance(node, (Number, Variable)):
        return 1
    if isinstance(node, UnaryOp):
        return 1 + count_nodes(node.operand)
    if isinstance(node, BinaryOp):
        return 1 + count_nodes(node.left) + count_nodes(node.right)
    if isinstance(node, FunctionCall):
        return 1 + sum(count_nodes(arg) for arg in node.args)
    raise TypeError(f"Unsupported node type: {type(node).__name__}")


def tree_depth(node: Node) -> int:
    if isinstance(node, (Number, Variable)):
        return 1
    if isinstance(node, UnaryOp):
        return 1 + tree_depth(node.operand)
    if isinstance(node, BinaryOp):
        return 1 + max(tree_depth(node.left), tree_depth(node.right))
    if isinstance(node, FunctionCall):
        return 1 + max(tree_depth(arg) for arg in node.args)
    raise TypeError(f"Unsupported node type: {type(node).__name__}")


def make_evaluator(node: Node):
    def evaluate(x: float, y: float, z: float) -> float:
        return _eval(node, x, y, z)

    return evaluate


def _eval(node: Node, x: float, y: float, z: float) -> float:
    if isinstance(node, Number):
        return node.value
    if isinstance(node, Variable):
        return {"x": x, "y": y, "z": z}[node.name]
    if isinstance(node, UnaryOp):
        value = _eval(node.operand, x, y, z)
        return value if node.op == "+" else -value
    if isinstance(node, BinaryOp):
        left = _eval(node.left, x, y, z)
        right = _eval(node.right, x, y, z)
        if node.op == "+":
            return left + right
        if node.op == "-":
            return left - right
        if node.op == "*":
            return left * right
        if node.op == "/":
            return left / right
        if node.op == "**":
            return left ** right
    if isinstance(node, FunctionCall):
        function = SAFE_FUNCTIONS[node.name]
        return function(*(_eval(arg, x, y, z) for arg in node.args))
    raise TypeError(f"Unsupported node type: {type(node).__name__}")
