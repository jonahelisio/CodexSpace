from __future__ import annotations

import ast
import math
from dataclasses import dataclass
from typing import Callable, Iterable


FORMULA_LIBRARY: dict[str, str] = {
    "sphere": "x**2 + y**2 + z**2 - 1",
    "torus": "(sqrt(x**2 + y**2) - 1.2)**2 + z**2 - 0.16",
    "cylinder": "x**2 + y**2 - 0.64",
    "ellipsoid": "(x/1.5)**2 + (y/1.0)**2 + (z/0.7)**2 - 1",
    "hyperboloid": "x**2 + y**2 - z**2 - 0.5",
    "wavy": "sin(3*x) + cos(3*y) + sin(3*z) - 0.3",
    "cubic": "x**3 + y**3 + z**3 - x*y*z - 1",
    "saddle": "x**2 - y**2 + z**2 - 0.5",
    "banchoff_chmutov": "x**4 + y**4 + z**4 - (x**2 + y**2 + z**2)",
    "barth_sextic": (
        "4*(x**2 - y**2)*(y**2 - z**2)*(z**2 - x**2) - "
        "(1 + 2*sqrt(5))*(x**2 + y**2 + z**2 - 1)**2"
    ),
    "gyroid": "sin(x)*cos(y) + sin(y)*cos(z) + sin(z)*cos(x)",
}

SAFE_FUNCTIONS: dict[str, Callable[..., float]] = {
    "sqrt": math.sqrt,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "abs": abs,
    "exp": math.exp,
    "log": math.log,
}

SAFE_CONSTANTS: dict[str, float] = {
    "pi": math.pi,
    "e": math.e,
}


@dataclass(frozen=True)
class GridSpec:
    bound: float = 2.0
    resolution: int = 30

    @property
    def step(self) -> float:
        return (self.bound * 2.0) / max(self.resolution - 1, 1)

    def axis(self) -> list[float]:
        if self.resolution <= 1:
            return [0.0]
        return [
            -self.bound + index * self.step
            for index in range(self.resolution)
        ]


@dataclass(frozen=True)
class FieldSample:
    x: float
    y: float
    z: float
    value: float
    region: str


class UnsafeFormulaError(ValueError):
    pass


def _validate_ast(node: ast.AST) -> None:
    allowed_nodes = (
        ast.Expression,
        ast.BinOp,
        ast.UnaryOp,
        ast.Call,
        ast.Name,
        ast.Load,
        ast.Constant,
        ast.Add,
        ast.Sub,
        ast.Mult,
        ast.Div,
        ast.Pow,
        ast.USub,
        ast.UAdd,
    )
    for child in ast.walk(node):
        if not isinstance(child, allowed_nodes):
            raise UnsafeFormulaError(f"Unsupported syntax: {type(child).__name__}")
        if isinstance(child, ast.Call):
            if not isinstance(child.func, ast.Name) or child.func.id not in SAFE_FUNCTIONS:
                raise UnsafeFormulaError("Only approved math functions are allowed")
        if isinstance(child, ast.Name):
            if child.id not in {"x", "y", "z", *SAFE_FUNCTIONS.keys(), *SAFE_CONSTANTS.keys()}:
                raise UnsafeFormulaError(f"Unknown symbol: {child.id}")


def compile_formula(formula: str) -> Callable[[float, float, float], float]:
    parsed = ast.parse(formula, mode="eval")
    _validate_ast(parsed)
    compiled = compile(parsed, "<formula>", "eval")

    def evaluator(x: float, y: float, z: float) -> float:
        scope = {
            "__builtins__": {},
            **SAFE_FUNCTIONS,
            **SAFE_CONSTANTS,
            "x": x,
            "y": y,
            "z": z,
        }
        value = eval(compiled, scope, {})
        if isinstance(value, complex):
            raise ValueError("Complex values are not supported")
        numeric = float(value)
        if not math.isfinite(numeric):
            raise ValueError("Formula produced a non-finite value")
        return numeric

    return evaluator


def classify_value(value: float, epsilon: float = 0.1) -> str:
    if value < -epsilon:
        return "negative"
    if value > epsilon:
        return "positive"
    return "surface"


def iter_samples(
    formula: str,
    grid: GridSpec,
    epsilon: float = 0.1,
) -> Iterable[FieldSample]:
    evaluator = compile_formula(formula)
    axis = grid.axis()
    for x in axis:
        for y in axis:
            for z in axis:
                value = evaluator(x, y, z)
                yield FieldSample(
                    x=x,
                    y=y,
                    z=z,
                    value=value,
                    region=classify_value(value, epsilon),
                )


def collect_samples(
    formula: str,
    grid: GridSpec,
    epsilon: float = 0.1,
) -> list[FieldSample]:
    return list(iter_samples(formula=formula, grid=grid, epsilon=epsilon))


def summarize_samples(samples: Iterable[FieldSample]) -> dict[str, float]:
    counts = {"negative": 0, "surface": 0, "positive": 0}
    min_value = math.inf
    max_value = -math.inf
    total = 0
    for sample in samples:
        counts[sample.region] += 1
        min_value = min(min_value, sample.value)
        max_value = max(max_value, sample.value)
        total += 1
    return {
        "total": total,
        "negative": counts["negative"],
        "surface": counts["surface"],
        "positive": counts["positive"],
        "min_value": min_value if total else math.nan,
        "max_value": max_value if total else math.nan,
    }
