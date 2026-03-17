from __future__ import annotations

from dataclasses import dataclass
from typing import Union


@dataclass(frozen=True)
class Number:
    value: float


@dataclass(frozen=True)
class Variable:
    name: str


@dataclass(frozen=True)
class UnaryOp:
    op: str
    operand: "Node"


@dataclass(frozen=True)
class BinaryOp:
    op: str
    left: "Node"
    right: "Node"


@dataclass(frozen=True)
class FunctionCall:
    name: str
    args: tuple["Node", ...]


Node = Union[Number, Variable, UnaryOp, BinaryOp, FunctionCall]
