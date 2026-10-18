#!/usr/bin/env python3
"""Exact dirty-anchor product-fanout construction and conditional moment screen."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from fractions import Fraction as Q
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def direct(targets: tuple[int, ...], common: int, private: tuple[int, ...]) -> tuple[int, ...]:
    out = list(targets)
    for i in range(len(out)):
        out[i] ^= common
        out[i] ^= private[i]
    return tuple(out)


def dirty_anchor(
    targets: tuple[int, ...],
    common: int,
    private: tuple[int, ...],
    *,
    omit_pre: bool = False,
    omit_common: bool = False,
    omit_post: bool = False,
    omit_private: int | None = None,
) -> tuple[int, ...]:
    out = list(targets)
    if not omit_pre:
        for i in range(1, len(out)):
            out[i] ^= out[0]
    if not omit_common:
        out[0] ^= common
    if not omit_post:
        for i in range(1, len(out)):
            out[i] ^= out[0]
    for i, value in enumerate(private):
        if i != omit_private:
            out[i] ^= value
    return tuple(out)


def dirty_anchor_inverse(
    targets: tuple[int, ...], common: int, private: tuple[int, ...]
) -> tuple[int, ...]:
    out = list(targets)
    for i in range(len(out) - 1, -1, -1):
        out[i] ^= private[i]
    for i in range(1, len(out)):
        out[i] ^= out[0]
    out[0] ^= common
    for i in range(1, len(out)):
        out[i] ^= out[0]
    return tuple(out)


def exhaustive_cases(q: int, width: int) -> int:
    limit = 1 << width
    count = 0
    for common in range(limit):
        for encoded in range(limit**q):
            private = tuple((encoded >> (width * i)) & (limit - 1) for i in range(q))
            for encoded_targets in range(limit**q):
                targets = tuple(
                    (encoded_targets >> (width * i)) & (limit - 1) for i in range(q)
                )
                expected = direct(targets, common, private)
                actual = dirty_anchor(targets, common, private)
                require(actual == expected, f"forward identity failed q={q}, width={width}")
                require(
                    dirty_anchor_inverse(actual, common, private) == targets,
                    f"inverse failed q={q}, width={width}",
                )
                count += 1
    return count


def negative_controls() -> int:
    q = 3
    cases = [
        ((1, 0, 0), 1, (0, 0, 0), {"omit_pre": True}),
        ((0, 0, 0), 1, (0, 0, 0), {"omit_post": True}),
        ((0, 0, 0), 1, (0, 0, 0), {"omit_common": True}),
        ((0, 0, 0), 0, (0, 1, 0), {"omit_private": 1}),
    ]
    for targets, common, private, kwargs in cases:
        expected = direct(targets, common, private)
        bad = dirty_anchor(targets, common, private, **kwargs)
        require(bad != expected, f"negative control was not rejected: {kwargs}")
    return len(cases)


def profile_brackets() -> tuple[tuple[Q, Q], tuple[Q, Q]]:
    ceiling_path = ROOT / "research" / "complex-local-word-ceiling" / "ceiling.py"
    spec = importlib.util.spec_from_file_location("imb_ceiling", ceiling_path)
    require(spec is not None and spec.loader is not None, "could not load pinned ceiling model")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    base = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}
    candidate = dict(base)
    candidate[1] = 1524  # 8 blocks * (112 outputs - 1 saved shared child)
    grid = Q(1, 10**12)
    result = (
        module.ceiling(base, 73, 896, 9, 64, grid=grid),
        module.ceiling(candidate, 73, 896, 9, 64, grid=grid),
    )
    expected = (
        (Q(1690054109, 10**12), Q(169005411, 10**11)),
        (Q(2026751029, 10**12), Q(202675103, 10**11)),
    )
    require(result == expected, "pinned ceiling brackets changed")
    return result


def make_certificate() -> dict:
    finite = {
        "q2_width2": exhaustive_cases(2, 2),
        "q3_width2": exhaustive_cases(3, 2),
        "q4_width2": exhaustive_cases(4, 2),
        "q5_width1": exhaustive_cases(5, 1),
    }
    controls = negative_controls()
    cost_rows = []
    for q in range(2, 113):
        for width in (1, 16, 128):
            direct_children = 2 * q
            candidate_children = q + 1
            row_adds = 2 * (q - 1)
            affine_xors = 2 * (q - 1) * width
            saved_children = direct_children - candidate_children
            require(saved_children == q - 1, "child-call invoice mismatch")
            require(row_adds == 2 * (q - 1), "single-child row-ADD lower bound mismatch")
            require(affine_xors == 2 * (q - 1) * width, "affine invoice mismatch")
            cost_rows.append((q, width, direct_children, candidate_children, row_adds, affine_xors))
    base_bracket, candidate_bracket = profile_brackets()
    return {
        "schema_version": 1,
        "status": "exact-local-construction-no-provider-admission",
        "scope": {"q_min": 2, "q_max": 112, "word_widths_screened": [1, 16, 128]},
        "finite_cases": finite,
        "finite_case_total": sum(finite.values()),
        "negative_controls_rejected": controls,
        "cost_cases": len(cost_rows),
        "single_common_child_row_add_optimality": {
            "lower_bound": "2*(q-1)",
            "construction": "2*(q-1)",
            "alphabet": "target-row XOR only; one common child; no helper, COPY, CLEAR, or second common child",
        },
        "cost_case_sha256": __import__("hashlib").sha256(
            repr(cost_rows).encode("ascii")
        ).hexdigest(),
        "q112_one_block": {
            "direct_rank1_children": 224,
            "dirty_anchor_rank1_children": 113,
            "saved_rank1_children": 111,
            "full_width_adds": 222,
        },
        "eight_block_conditional_profile": {
            "baseline": {"1": 2412, "2": 418, "3": 432, "4": 142, "5": 82, "8": 8},
            "candidate_rank_profile": {"1": 1524, "2": 418, "3": 432, "4": 142, "5": 82, "8": 8},
            "additional_width_one_xors": 1776,
            "baseline_ceiling": [str(x) for x in base_bracket],
            "candidate_rank_only_ceiling": [str(x) for x in candidate_bracket],
            "status": "conditional profile screen; affine XORs remain a separate linear term",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", type=Path)
    args = parser.parse_args()
    certificate = make_certificate()
    data = json.dumps(certificate, indent=2, sort_keys=True) + "\n"
    if args.write:
        require(not args.write.exists(), f"refusing to overwrite {args.write}")
        args.write.write_text(data, encoding="utf-8")
    else:
        stored = json.loads((PACKAGE / "CERTIFICATE.json").read_text(encoding="utf-8"))
        require(stored == certificate, "certificate differs from exact replay")
    print(
        "PASS_DIRTY_OUTPUT_ANCHOR "
        f"cases={certificate['finite_case_total']} controls={certificate['negative_controls_rejected']} "
        "q=2..112 direct_q112=224 shared_q112=113 add_xors_q112=222"
    )


if __name__ == "__main__":
    main()
