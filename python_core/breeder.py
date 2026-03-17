from __future__ import annotations

import json
import random
from dataclasses import dataclass, replace
from itertools import product

from .ast_nodes import BinaryOp, FunctionCall, Node, Number, UnaryOp, Variable
from .parser import parse_formula
from .serializer import to_formula
from .validator import ValidationResult, count_nodes, validate_formula


@dataclass(frozen=True)
class BredFormula:
    formula: str
    validation: ValidationResult


def breed_formulas(
    formula_a: str,
    formula_b: str,
    *,
    rng: random.Random | None = None,
) -> tuple[str, str]:
    rng = rng or random.Random()
    tree_a = parse_formula(formula_a)
    tree_b = parse_formula(formula_b)

    paths_a = list(_iter_paths(tree_a))
    paths_b = list(_iter_paths(tree_b))
    path_a = rng.choice(paths_a)
    path_b = rng.choice(paths_b)

    subtree_a = _get_subtree(tree_a, path_a)
    subtree_b = _get_subtree(tree_b, path_b)
    child_a = _replace_subtree(tree_a, path_a, subtree_b)
    child_b = _replace_subtree(tree_b, path_b, subtree_a)
    return to_formula(child_a), to_formula(child_b)


@dataclass(frozen=True)
class OffspringAnalysis:
    parent_a_nodes: int
    parent_b_nodes: int
    raw_swap_pairs: int
    unique_child_formulas: int
    valid_formulas: int
    interesting_formulas: int


@dataclass(frozen=True)
class LabeledOffspring:
    formula: str
    label: str
    validation: ValidationResult


def analyze_offspring_space(formula_a: str, formula_b: str) -> OffspringAnalysis:
    tree_a = parse_formula(formula_a)
    tree_b = parse_formula(formula_b)
    paths_a = list(_iter_paths(tree_a))
    paths_b = list(_iter_paths(tree_b))

    unique_formulas: set[str] = set()
    valid_formulas = 0
    interesting_formulas = 0

    for path_a, path_b in product(paths_a, paths_b):
        subtree_a = _get_subtree(tree_a, path_a)
        subtree_b = _get_subtree(tree_b, path_b)
        child_a = to_formula(_replace_subtree(tree_a, path_a, subtree_b))
        child_b = to_formula(_replace_subtree(tree_b, path_b, subtree_a))
        unique_formulas.add(child_a)
        unique_formulas.add(child_b)

    for formula in unique_formulas:
        result = validate_formula(formula)
        if result.valid:
            valid_formulas += 1
            if _is_interesting(result):
                interesting_formulas += 1

    return OffspringAnalysis(
        parent_a_nodes=count_nodes(tree_a),
        parent_b_nodes=count_nodes(tree_b),
        raw_swap_pairs=len(paths_a) * len(paths_b),
        unique_child_formulas=len(unique_formulas),
        valid_formulas=valid_formulas,
        interesting_formulas=interesting_formulas,
    )


def enumerate_labeled_offspring(formula_a: str, formula_b: str) -> list[LabeledOffspring]:
    tree_a = parse_formula(formula_a)
    tree_b = parse_formula(formula_b)
    paths_a = list(_iter_paths(tree_a))
    paths_b = list(_iter_paths(tree_b))

    seen: set[str] = set()
    labeled: list[LabeledOffspring] = []

    for path_a, path_b in product(paths_a, paths_b):
        subtree_a = _get_subtree(tree_a, path_a)
        subtree_b = _get_subtree(tree_b, path_b)
        child_a = to_formula(_replace_subtree(tree_a, path_a, subtree_b))
        child_b = to_formula(_replace_subtree(tree_b, path_b, subtree_a))
        for formula in (child_a, child_b):
            if formula in seen:
                continue
            seen.add(formula)
            validation = validate_formula(formula)
            labeled.append(
                LabeledOffspring(
                    formula=formula,
                    label=_label_validation(validation),
                    validation=validation,
                )
            )

    labeled.sort(key=lambda item: (_label_rank(item.label), -_score(item.validation), item.formula))
    return labeled


def labeled_offspring_to_jsonable(items: list[LabeledOffspring]) -> list[dict[str, object]]:
    payload: list[dict[str, object]] = []
    for item in items:
        payload.append(
            {
                "formula": item.formula,
                "label": item.label,
                "validation": {
                    "valid": item.validation.valid,
                    "reason": item.validation.reason,
                    "node_count": item.validation.node_count,
                    "depth": item.validation.depth,
                    "semantic_flags": list(item.validation.semantic_flags),
                    "sample_min": item.validation.sample_min,
                    "sample_max": item.validation.sample_max,
                    "sample_zeroish_count": item.validation.sample_zeroish_count,
                    "sample_negative_count": item.validation.sample_negative_count,
                    "sample_positive_count": item.validation.sample_positive_count,
                },
            }
        )
    return payload


def breed_until_valid(
    formula_a: str,
    formula_b: str,
    *,
    attempts: int = 25,
    rng: random.Random | None = None,
) -> tuple[str, str, ValidationResult, ValidationResult]:
    rng = rng or random.Random()
    last_a = ""
    last_b = ""
    last_result_a = ValidationResult(False, "not_run", 0, 0)
    last_result_b = ValidationResult(False, "not_run", 0, 0)
    for _ in range(attempts):
        last_a, last_b = breed_formulas(formula_a, formula_b, rng=rng)
        last_result_a = validate_formula(last_a)
        last_result_b = validate_formula(last_b)
        if last_result_a.valid and last_result_b.valid:
            return last_a, last_b, last_result_a, last_result_b
    return last_a, last_b, last_result_a, last_result_b


def breed_until_interesting(
    formula_a: str,
    formula_b: str,
    *,
    attempts: int = 50,
    rng: random.Random | None = None,
) -> tuple[BredFormula, BredFormula]:
    rng = rng or random.Random()
    best_pair: tuple[BredFormula, BredFormula] | None = None
    best_score: tuple[int, int, int, int] | None = None

    for _ in range(attempts):
        child_a, child_b = breed_formulas(formula_a, formula_b, rng=rng)
        result_a = validate_formula(child_a)
        result_b = validate_formula(child_b)
        bred_a = BredFormula(child_a, result_a)
        bred_b = BredFormula(child_b, result_b)
        pair_score = (_score(result_a), _score(result_b))
        normalized_score = tuple(sorted(pair_score, reverse=True))
        if best_score is None or normalized_score > best_score:
            best_score = normalized_score
            best_pair = (bred_a, bred_b)

        if _is_interesting(result_a) and _is_interesting(result_b):
            return bred_a, bred_b

    if best_pair is None:
        raise RuntimeError("Failed to produce any offspring")
    return best_pair


def _is_interesting(result: ValidationResult) -> bool:
    if not result.valid:
        return False
    flags = set(result.semantic_flags)
    return "sign_variation" in flags and "surface_band_detected" in flags and "constant_or_flat" not in flags


def _label_validation(result: ValidationResult) -> str:
    if not result.valid:
        reason = result.reason
        if reason.startswith("parse_error"):
            return "failed_to_evaluate"
        if "complex" in reason or "math domain" in reason:
            return "malformed_but_salvageable"
        if "evaluation_error" in reason or "non_finite" in reason:
            return "numerically_unstable"
        return "structurally_weird"
    flags = set(result.semantic_flags)
    if "constant_or_flat" in flags:
        return "degenerate_but_valid"
    if "sign_variation" in flags and "surface_band_detected" in flags:
        return "stable_surface_candidate"
    if "sign_variation" in flags:
        return "stable_sign_structure"
    if "surface_band_detected" in flags:
        return "surface_band_only"
    return "valid_other"


def _label_rank(label: str) -> int:
    order = {
        "stable_surface_candidate": 0,
        "stable_sign_structure": 1,
        "surface_band_only": 2,
        "malformed_but_salvageable": 3,
        "numerically_unstable": 4,
        "structurally_weird": 5,
        "degenerate_but_valid": 6,
        "valid_other": 4,
        "failed_to_evaluate": 7,
    }
    return order.get(label, 99)


def _score(result: ValidationResult) -> int:
    if not result.valid:
        return -1000
    flags = set(result.semantic_flags)
    score = 0
    if "sign_variation" in flags:
        score += 5
    if "surface_band_detected" in flags:
        score += 3
    if "constant_or_flat" in flags:
        score -= 6
    if "single_sign_only" in flags:
        score -= 2
    if "no_surface_band_detected" in flags:
        score -= 3
    score += min(result.sample_zeroish_count, 4)
    return score


def _iter_paths(node: Node, path: tuple[str | int, ...] = ()) -> list[tuple[str | int, ...]]:
    paths = [path]
    if isinstance(node, UnaryOp):
        paths.extend(_iter_paths(node.operand, path + ("operand",)))
    elif isinstance(node, BinaryOp):
        paths.extend(_iter_paths(node.left, path + ("left",)))
        paths.extend(_iter_paths(node.right, path + ("right",)))
    elif isinstance(node, FunctionCall):
        for index, arg in enumerate(node.args):
            paths.extend(_iter_paths(arg, path + (index,)))
    return paths


def _get_subtree(node: Node, path: tuple[str | int, ...]) -> Node:
    current = node
    for step in path:
        if isinstance(step, int):
            if not isinstance(current, FunctionCall):
                raise TypeError("Integer path step requires FunctionCall")
            current = current.args[step]
        else:
            current = getattr(current, step)
    return current


def _replace_subtree(node: Node, path: tuple[str | int, ...], replacement: Node) -> Node:
    if not path:
        return replacement
    head, *tail = path
    tail_tuple = tuple(tail)
    if isinstance(head, int):
        if not isinstance(node, FunctionCall):
            raise TypeError("Integer path step requires FunctionCall")
        args = list(node.args)
        args[head] = _replace_subtree(args[head], tail_tuple, replacement)
        return replace(node, args=tuple(args))
    child = getattr(node, head)
    return replace(node, **{head: _replace_subtree(child, tail_tuple, replacement)})
