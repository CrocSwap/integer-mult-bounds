#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Integer-significand check of the directed reciprocal guard-bit lemma.

No primary checker or predecessor executable is imported. Every prefix
cell is half-open; its right endpoint is checked as a limiting value.
The finite census is separate from the quantified three-guard-bit proof.
"""
import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def round_step(c_num, c_bits, x_num, x_bits, precision):
    """Exact floor-rounded update, retaining all incoming iterate bits.

    c=c_num/2**c_bits, x=x_num/2**x_bits. The two products are integer
    products followed by exact floor divisions, including when x_bits
    exceeds the new working precision.
    """
    require(precision >= 1 and c_bits >= 0 and x_bits >= 0, "invalid dyadic precision")
    require(c_num >= 0 and x_num >= 0, "negative reciprocal input")
    prefix = c_num >> (c_bits - precision) if c_bits >= precision else c_num << (precision - c_bits)
    product = (prefix * x_num) >> x_bits
    new_num = (x_num * ((1 << (precision + 1)) - product)) >> x_bits
    return {"t": precision, "c_prefix": prefix, "u_num": product,
            "input_x_num": x_num, "input_x_bits": x_bits,
            "x_num": new_num, "x_bits": precision}


def reciprocal(c_num, c_bits, target, guards=3):
    """Return (numerator, fractional bits, full trace), with seed 5/8."""
    require(target >= 1 and guards >= 0, "invalid target or guard count")
    require((1 << c_bits) <= c_num < (2 << c_bits), "normalized reciprocal input is outside [1,2)")
    first = round_step(c_num, c_bits, 5, 3, 6)
    first["m"] = 1
    trace = [first]
    numerator, bits, m = first["x_num"], 6, 1
    while m < target:
        m = min(2 * m, target)
        stage = round_step(c_num, c_bits, numerator, bits, m + guards)
        stage["m"] = m
        trace.append(stage)
        numerator, bits = stage["x_num"], stage["x_bits"]
    return numerator, bits, trace


def residual_endpoints(c_num, c_bits, x_num, x_bits):
    """Signed numerators at both endpoints over the common power-of-two denominator."""
    denominator_bits = c_bits + x_bits
    unit = 1 << denominator_bits
    return unit - c_num * x_num, unit - (c_num + 1) * x_num, denominator_bits


def check_cell(c_num, c_bits, target, guards):
    numerator, bits, trace = reciprocal(c_num, c_bits, target, guards)
    for stage in trace:
        require(stage["x_num"] > 0, "iterate lost positivity")
        left, right, denominator_bits = residual_endpoints(c_num, c_bits, stage["x_num"], stage["x_bits"])
        require(max(abs(left), abs(right)) <= 1 << (denominator_bits - stage["m"] - 1),
                "prefix cell violates the stage residual invariant")
    left, right, denominator_bits = residual_endpoints(c_num, c_bits, numerator, bits)
    return trace, (left, right, denominator_bits)


def counterexamples():
    # These satisfy the general residual invariant; no reachability from the
    # fixed warm-up is asserted. The zero-guard witness must be distinct.
    cases = [(0, 1, 0, 49, 6), (1, 11, 3, 35, 6), (2, 11, 3, 35, 6)]
    result = []
    for guards, c_num, c_bits, x_num, x_bits in cases:
        initial_num = (1 << (c_bits + x_bits)) - c_num * x_num
        require(abs(initial_num) <= 1 << (c_bits + x_bits - 2), "counterexample misses initial invariant")
        stage = round_step(c_num, c_bits, x_num, x_bits, 2 + guards)
        residual_num = (1 << (c_bits + stage["x_bits"])) - c_num * stage["x_num"]
        require(abs(residual_num) * 8 > 1 << (c_bits + stage["x_bits"]),
                "insufficient-guard fixture no longer refutes the doubled target")
        result.append({"guards": guards, "c_num": c_num, "c_bits": c_bits,
                       "input_x_num": x_num, "input_x_bits": x_bits,
                       "initial_residual_num": initial_num,
                       "initial_residual_bits": c_bits + x_bits,
                       "output_x_num": stage["x_num"], "output_x_bits": stage["x_bits"],
                       "output_residual_num": residual_num,
                       "output_residual_bits": c_bits + stage["x_bits"],
                       "required_residual_bits": 3,
                       "reachable_from_fixed_warmup": "not asserted"})
    # Three guards do preserve the conclusion at these exact states.
    for _, c_num, c_bits, x_num, x_bits in cases:
        stage = round_step(c_num, c_bits, x_num, x_bits, 5)
        residual_num = (1 << (c_bits + 5)) - c_num * stage["x_num"]
        require(abs(residual_num) <= 1 << (c_bits + 2), "three-guard positive fixture failed")
    return result


def build_receipt(max_target=10):
    require(1 <= max_target <= 10, "finite domain must be p=1..max_target with max_target<=10")
    records, total_cells, stage_checks, retained_precision_cases = [], 0, 0, 0
    transcript = hashlib.sha256()
    for guards in (3, 5):
        for target in range(1, max_target + 1):
            c_bits = max(6, target + guards)
            cells = 1 << c_bits
            worst_abs, worst_c, worst_side, worst_signed, result_bits = -1, None, None, None, None
            target_stage_checks = 0
            for c_num in range(1 << c_bits, 2 << c_bits):
                trace, endpoints = check_cell(c_num, c_bits, target, guards)
                left, right, denominator_bits = endpoints
                for side, value in (("left", left), ("right_limit", right)):
                    if abs(value) > worst_abs:
                        worst_abs, worst_c, worst_side, worst_signed = abs(value), c_num, side, value
                if result_bits is None:
                    result_bits = denominator_bits
                require(result_bits == denominator_bits, "output denominator varies inside a target census")
                target_stage_checks += len(trace)
                retained_precision_cases += sum(stage["input_x_bits"] > stage["t"] for stage in trace)
                compact = [guards, target, c_num, c_bits,
                           [[s[key] for key in ("m", "t", "c_prefix", "u_num", "input_x_num",
                                               "input_x_bits", "x_num", "x_bits")] for s in trace]]
                transcript.update(json.dumps(compact, separators=(",", ":")).encode())
                transcript.update(b"\n")
            require(worst_abs <= 1 << (result_bits - target - 1), "final endpoint census missed its target")
            records.append({"guards": guards, "target": target, "c_prefix_bits": c_bits,
                            "cells": cells, "stage_cells": target_stage_checks,
                            "endpoint_checks": 2 * target_stage_checks,
                            "maximum_absolute_residual_num": worst_abs,
                            "residual_denominator_bits": result_bits,
                            "worst_c_cell_num": worst_c, "worst_endpoint": worst_side,
                            "worst_signed_residual_num": worst_signed})
            total_cells += cells
            stage_checks += target_stage_checks
    if max_target == 10:
        require(total_cells == 81920, "complete prefix-cell count differs from 81920")
        require(retained_precision_cases == 16384, "warm-up retention boundary coverage differs from 16384")
    return {"schema_version": 1, "checker": "integer-significand reciprocal prefix cells",
            "target_range": [1, max_target], "guard_counts": [3, 5],
            "rounding": "floor to t fractional bits; incoming x preserved exactly",
            "seed": {"numerator": 5, "fractional_bits": 3}, "warmup_precision": 6,
            "cell_domain": "all [k/2^T,(k+1)/2^T), 2^T<=k<2^(T+1), T=max(6,p+g)",
            "right_endpoint_semantics": "limiting residual for the cell's fixed trace",
            "total_cells": total_cells, "stage_cells": stage_checks,
            "endpoint_checks": 2 * stage_checks, "warmup_retention_cases": retained_precision_cases,
            "trace_fields": ["m", "t", "c_prefix", "u_num", "input_x_num",
                             "input_x_bits", "x_num", "x_bits"],
            "all_trace_sha256": transcript.hexdigest(), "censuses": records,
            "general_invariant_counterexamples": counterexamples(),
            "reachable_guard_optimality": "open; general-invariant counterexamples do not decide it"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", type=Path, help="check the complete computed receipt against this JSON")
    parser.add_argument("--write", type=Path, help="write a fresh receipt; existing files are not overwritten")
    parser.add_argument("--max-target", type=int, default=10, help="bounded diagnostic prefix of p=1..10")
    args = parser.parse_args()
    try:
        if args.write:
            require(not args.write.exists(), "output already exists")
        receipt = build_receipt(args.max_target)
        check_path = args.check or (HERE / "INDEPENDENT.json" if not args.write and args.max_target == 10 else None)
        if check_path:
            require(json.loads(check_path.read_text()) == receipt, "independent receipt differs")
        if args.write:
            with args.write.open("x") as stream:
                json.dump(receipt, stream, indent=2, sort_keys=True)
                stream.write("\n")
    except (OSError, ValueError) as error:
        parser.exit(1, "FAIL_RECIPROCAL_DIRECTED_GUARDS_INDEPENDENT: " + str(error) + "\n")
    print("PASS_RECIPROCAL_DIRECTED_GUARDS_INDEPENDENT "
          f"p=1..{args.max_target} cells={receipt['total_cells']} "
          f"stage_cells={receipt['stage_cells']} endpoint_checks={receipt['endpoint_checks']} "
          "guards=3,5 counterexamples=3")


if __name__ == "__main__":
    main()
