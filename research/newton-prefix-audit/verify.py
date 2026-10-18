#!/usr/bin/env python3
"""Bounded, source-bound verification of the Section 09 numerical routines.

Hanson Sun, with substantial OpenAI Codex assistance. Apache-2.0.
All acceptance comparisons are exact and remain active under python -O.
"""
import argparse
from collections import Counter
from fractions import Fraction as F
import hashlib
import importlib.util
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def module(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + ".py"))
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


fixed = module("fixed")
rational = module("rational")


def require(ok, message):
    if not ok:
        raise ValueError(message)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def source_check():
    inventory = json.loads((HERE / "SOURCES.json").read_text())
    live = {}
    for row in inventory["files"]:
        if row["usage"] == "input":
            data = (ROOT / row["path"]).read_bytes()
            actual = hashlib.sha256(data).hexdigest()
            require(actual == row["sha256"], "source drift: " + row["path"])
            live[row["path"]] = actual
    upstream = json.loads((ROOT / "upstream/manifest.json").read_text())
    require(upstream["commit"] == "adc7f1241b42e322a6451854ab7e4b4c146bf78a", "upstream commit drift")
    for short in ("build/sections/09-exact-arithmetic.tex", "build/sections/00-introduction.tex", "LICENSE"):
        require(upstream["files"][short]["sha256"] == live["upstream/" + short], "upstream source pin mismatch")
    return {"base_commit": inventory["base_commit"], "upstream_commit": upstream["commit"], "inputs": live}


def reciprocal_cell(k, bits, target, xn, xb):
    x, lo, hi = F(xn, 2 ** xb), F(k, 2 ** bits), F(k + 1, 2 ** bits)
    error = max(abs(1 - lo * x), abs(1 - hi * x))
    slack = F(1, 2 ** (target + 1)) - error
    require(slack >= 0, f"reciprocal cell bound: p={target}, k={k}, bits={bits}, x={x}")
    return slack


def root_cell(k, bits, target, xn, xb):
    x, lo, hi = F(xn, 2 ** xb), F(k, 2 ** bits), F(k + 1, 2 ** bits)
    eps = F(1, 2 ** (target + 1))
    require(x >= eps, "root lower endpoint must be nonnegative before squaring")
    lower, upper = lo - (x - eps) ** 2, (x + eps) ** 2 - hi
    require(lower >= 0 and upper >= 0, f"root cell bound: p={target}, k={k}, bits={bits}, x={x}")
    return lower, upper


def check_reciprocal_trace(k, bits, trace):
    c = F(k, 2 ** bits)
    previous = F(5, 8)
    for m, t, ct, un, nxt in trace:
        delta, c_prefix, u, x = F(1, 2 ** t), F(ct, 2 ** t), F(un, 2 ** t), F(nxt, 2 ** t)
        eta1, eta2 = u - c_prefix * previous, x - previous * (2 - u)
        eps = 1 - c * previous
        require(-delta < eta1 <= 0 and -delta < eta2 <= 0, "reciprocal rounding interval")
        identity = eps ** 2 - c * (c - c_prefix) * previous ** 2 + c * previous * eta1 - c * eta2
        require(1 - c * x == identity, "signed reciprocal residual identity")
        require(abs(1 - c * x) <= F(1, 2 ** (m + 1)), "reciprocal stage invariant")
        previous = x


def check_root_trace(k, bits, trace):
    c, previous = F(k, 2 ** bits), F(3, 2)
    for m, t, ct, j, zn, zb, qt, nxt, inner in trace:
        delta, c_prefix = F(1, 2 ** t), F(ct, 2 ** t)
        z, quotient, x = F(zn, 2 ** zb), F(qt, 2 ** t), F(nxt, 2 ** t)
        d = previous / F(2) ** j
        v = z / F(2) ** j
        require(F(1, 2) <= previous <= F(5, 2), "root incoming interval")
        require(j in (-1, 0, 1) and 1 <= d < 2, "root normalized inner argument")
        require(abs(1 - d * z) <= delta / 2, "nested reciprocal residual")
        require(abs(v - 1 / previous) <= delta, "unnormalized reciprocal error")
        require(-delta < quotient - c_prefix * v <= 0, "quotient rounding interval")
        require(abs(quotient - c / previous) <= 7 * delta, "quotient error")
        require(-delta < x - (previous + quotient) / 2 <= 0, "root update rounding interval")
        require(quotient < 12 and v < 3, "fixed integer guard bounds")
        previous = x


def prefix_census():
    rows, comparisons, inner_comparisons = [], 0, 0
    for p in range(1, 9):
        bits, scale = p + 5, 2 ** (p + 5)
        transcript = hashlib.sha256()
        reciprocal_min = root_lower_min = root_upper_min = None
        reciprocal_witness = root_lower_witness = root_upper_witness = None
        for k in range(scale, 2 * scale):
            xn, xb, trace = fixed.reciprocal(k, bits, p)
            expected, oracle_trace = rational.inverse(F(k, scale), p)
            require(F(xn, 2 ** xb) == expected and trace == oracle_trace, "independent reciprocal disagreement")
            check_reciprocal_trace(k, bits, trace)
            comparisons += len(trace)
            slack = reciprocal_cell(k, bits, p, xn, xb)
            if reciprocal_min is None or slack < reciprocal_min:
                reciprocal_min, reciprocal_witness = slack, k
            for m, t, ct, u, nxt in trace:
                reciprocal_cell(k, bits, m, nxt, t)
            transcript.update(json.dumps(["reciprocal", k, xn, xb, trace], separators=(",", ":")).encode() + b"\n")
        for k in range(scale, 4 * scale):
            xn, xb, trace = fixed.square_root(k, bits, p)
            expected, oracle_trace = rational.root(F(k, scale), p)
            require(F(xn, 2 ** xb) == expected and trace == oracle_trace, "independent root disagreement")
            check_root_trace(k, bits, trace)
            comparisons += len(trace)
            inner_comparisons += sum(len(row[-1]) for row in trace)
            lower, upper = root_cell(k, bits, p, xn, xb)
            if root_lower_min is None or lower < root_lower_min:
                root_lower_min, root_lower_witness = lower, k
            if root_upper_min is None or upper < root_upper_min:
                root_upper_min, root_upper_witness = upper, k
            for m, t, ct, j, zn, zb, qt, nxt, inner in trace:
                require(j in (-1, 0, 1), "root normalization exponent")
                root_cell(k, bits, m, nxt, t)
            transcript.update(json.dumps(["root", k, xn, xb, trace], separators=(",", ":")).encode() + b"\n")
        rows.append({"target": p, "prefix_bits": bits, "reciprocal_cells": scale, "root_cells": 3 * scale,
                     "minimum_reciprocal_residual_slack": str(reciprocal_min), "reciprocal_witness_k": reciprocal_witness,
                     "minimum_root_lower_square_slack": str(root_lower_min), "root_lower_witness_k": root_lower_witness,
                     "minimum_root_upper_square_slack": str(root_upper_min), "root_upper_witness_k": root_upper_witness,
                     "all_operation_transcript_sha256": transcript.hexdigest()})
    return {"target_precisions": list(range(1, 9)), "reciprocal_cells": 16320, "root_cells": 48960,
            "outer_step_comparisons": comparisons, "inner_step_comparisons": inner_comparisons, "per_target": rows}


def check_division(a, b, n, prepared, counter):
    q, r, trial = fixed.divide(a, b, n, prepared)
    require((q, r) == divmod(a, b), f"division recovery: {(a, b, n)}")
    require(abs(trial - q) <= 1, "division trial not adjacent")
    counter[str(q - trial)] += 1
    return q, r, trial


def check_integer_root(a, n, counter):
    result, trial = fixed.integer_root(a, n)
    require(result == math.isqrt(a), f"integer root recovery: {(a, n)}")
    require(abs(trial - result) <= 1, "root trial not adjacent")
    counter[str(result - trial)] += 1
    return result, trial


def integer_census():
    division_count = root_count = 0
    division_corrections, root_corrections = Counter(), Counter()
    transcript = hashlib.sha256()
    for n in range(1, 9):
        for b in range(1, 2 ** n):
            prepared = fixed.reciprocal(b, b.bit_length() - 1, 2 * n + 4)
            oracle, _ = rational.inverse(F(b, 2 ** (b.bit_length() - 1)), 2 * n + 4)
            require(F(prepared[0], 2 ** prepared[1]) == oracle, "integer divisor reciprocal port")
            for a in range(2 ** n):
                answer = check_division(a, b, n, prepared, division_corrections)
                transcript.update(f"d:{n}:{a}:{b}:{answer}\n".encode())
                division_count += 1
        for a in range(2 ** n):
            answer = check_integer_root(a, n, root_corrections)
            transcript.update(f"s:{n}:{a}:{answer}\n".encode())
            root_count += 1
    require(division_count == 86870 and root_count == 510, "incomplete integer domain")
    return {"supplied_widths": list(range(1, 9)), "division_inputs": division_count, "root_inputs": root_count,
            "division_corrections": dict(sorted(division_corrections.items())), "root_corrections": dict(sorted(root_corrections.items())),
            "transcript_sha256": transcript.hexdigest()}


def boundary_census():
    widths = [9, 15, 16, 17, 31, 32, 33, 63, 64, 65, 84, 85, 127, 128, 129, 168]
    transcript = hashlib.sha256()
    divisions = roots = 0
    corrections_d, corrections_s = Counter(), Counter()
    for n in widths:
        limit = 2 ** n
        values = {0, 1, 2, 3, limit - 1, limit - 2, limit // 2 - 1, limit // 2, limit // 2 + 1}
        for r in (2 ** (n // 2 - 1), math.isqrt(limit - 1), 2 ** (n // 2) - 1):
            values.update(a for a in (r * r - 1, r * r, r * r + 1) if 0 <= a < limit)
        for b in sorted(values - {0}):
            prepared = fixed.reciprocal(b, b.bit_length() - 1, 2 * n + 4)
            oracle, oracle_trace = rational.inverse(F(b, 2 ** (b.bit_length() - 1)), 2 * n + 4)
            require(F(prepared[0], 2 ** prepared[1]) == oracle and prepared[2] == oracle_trace, "large reciprocal port")
            numerators = values | {b - 1, b} | ({b + 1} if b + 1 < limit else set())
            for a in sorted(numerators):
                answer = check_division(a, b, n, prepared, corrections_d)
                transcript.update(f"d:{n}:{a}:{b}:{answer}\n".encode())
                divisions += 1
        for a in sorted(values):
            answer = check_integer_root(a, n, corrections_s)
            if a:
                e = (a.bit_length() - 1) // 2
                primary = fixed.square_root(a, 2 * e, 2 * n + 4)
                oracle, oracle_trace = rational.root(F(a, 2 ** (2 * e)), 2 * n + 4)
                require(F(primary[0], 2 ** primary[1]) == oracle and primary[2] == oracle_trace, "large root port")
            transcript.update(f"s:{n}:{a}:{answer}\n".encode())
            roots += 1
    return {"supplied_widths": widths, "division_inputs": divisions, "root_inputs": roots,
            "division_corrections": dict(sorted(corrections_d.items())), "root_corrections": dict(sorted(corrections_s.items())),
            "transcript_sha256": transcript.hexdigest()}


def rejected(fn):
    try:
        fn()
    except ValueError:
        return True
    return False


def semantic_controls():
    controls = {}
    def concrete_witness(kind, p, k, bits, xn, xb):
        x, eps = F(xn, 2 ** xb), F(1, 2 ** (p + 1))
        for extra in range(0, 5):
            c = F((k << extra) + (1 << extra) - 1, 2 ** (bits + extra))
            fails = abs(1 - c * x) > eps if kind == "reciprocal" else not ((x - eps) ** 2 <= c <= (x + eps) ** 2)
            if fails:
                return str(c)
        raise ValueError("mutation has no explicit interior counterexample")
    def bad_reciprocal(name, p, k, bits, **options):
        xn, xb, _ = fixed.reciprocal(k, bits, p, **options)
        require(rejected(lambda: reciprocal_cell(k, bits, p, xn, xb)), "control survived: " + name)
        controls[name] = {"target": p, "k": k, "prefix_bits": bits, "output": str(F(xn, 2 ** xb)),
                          "counterexample_c": concrete_witness("reciprocal", p, k, bits, xn, xb)}
    def bad_root(name, p, k, bits, **options):
        xn, xb, _ = fixed.square_root(k, bits, p, **options)
        require(rejected(lambda: root_cell(k, bits, p, xn, xb)), "control survived: " + name)
        controls[name] = {"target": p, "k": k, "prefix_bits": bits, "output": str(F(xn, 2 ** xb)),
                          "counterexample_c": concrete_witness("root", p, k, bits, xn, xb)}
    bad_reciprocal("omitted_reciprocal_warmup", 1, 64, 6, warmup=False)
    bad_root("omitted_root_warmup", 1, 64, 6, warmup=False)
    bad_root("wrong_inner_normalization_scale", 1, 255, 6, normalization_offset=1)
    # First failing cell in a declared bounded mutation domain, retained exactly.
    for kind, evaluator, checker in (("reciprocal", fixed.reciprocal, reciprocal_cell), ("root", fixed.square_root, root_cell)):
        for mutation, kwargs, p in (("zero_guard_bits", {"guard": 0}, 3), ("stale_six_bit_prefix", {"stale": 6}, 8)):
            bits, scale = p + 5, 2 ** (p + 5)
            witness = None
            for k in range(scale, (2 if kind == "reciprocal" else 4) * scale):
                xn, xb, _ = evaluator(k, bits, p, **kwargs)
                if rejected(lambda: checker(k, bits, p, xn, xb)):
                    witness = {"target": p, "k": k, "prefix_bits": bits, "output": str(F(xn, 2 ** xb)),
                               "counterexample_c": concrete_witness(kind, p, k, bits, xn, xb)}
                    break
            require(witness is not None, "control had no witness: " + kind + mutation)
            controls[kind + "_" + mutation] = witness
    require(fixed.correct_division(9, 3, 2, high=False) != divmod(9, 3), "division increment control")
    require(fixed.correct_division(14, 5, 3, low=False) != divmod(14, 5), "division decrement control")
    require(fixed.correct_root(16, 3, high=False) != math.isqrt(16), "root increment control")
    require(fixed.correct_root(15, 4, low=False) != math.isqrt(15), "root decrement control")
    controls["omitted_division_increment"] = {"a": 9, "b": 3, "trial": 2, "approximation": "23/8"}
    controls["omitted_division_decrement"] = {"a": 14, "b": 5, "trial": 3, "approximation": "3"}
    controls["omitted_root_increment"] = {"a": 16, "trial": 3, "approximation": "31/8"}
    controls["omitted_root_decrement"] = {"a": 15, "trial": 4, "approximation": "4"}
    for name, fn in (("zero_divisor", lambda: fixed.divide(1, 0, 1)),
                     ("overflow_input", lambda: fixed.integer_root(256, 8)),
                     ("zero_target", lambda: fixed.reciprocal(1, 0, 0)),
                     ("unnormalized_reciprocal", lambda: fixed.reciprocal(2, 0, 1)),
                     ("unnormalized_root", lambda: fixed.square_root(4, 0, 1))):
        require(rejected(fn), "input control survived: " + name)
        controls[name] = "rejected"
    return controls


def build_receipt():
    return {"schema_version": 1, "status": "PASS_BOUNDED_NEWTON_PREFIX_AUDIT", "assignment_seed": 84,
            "scope": "All real normalized inputs for p=1..8 by prefix cells; finite integer recovery domains. No all-precision or fixed-tape theorem, supplier admission, or kappa claim.",
            "sources": source_check(), "prefix_cells": prefix_census(), "integer_recovery": integer_census(),
            "boundary_recovery": boundary_census(), "semantic_controls": semantic_controls()}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write-receipt", type=Path, help="explicit output path; normal verification writes nothing")
    ap.add_argument("--receipt", type=Path, default=HERE / "CERTIFICATE.json")
    args = ap.parse_args()
    actual = build_receipt()
    if args.write_receipt:
        args.write_receipt.write_text(json.dumps(actual, indent=2, sort_keys=True) + "\n")
    else:
        require(actual == json.loads(args.receipt.read_text()), "certificate mismatch or incomplete coverage")
    print("PASS_BOUNDED_NEWTON_PREFIX_AUDIT "
          f"cells=65280 division_inputs={actual['integer_recovery']['division_inputs']} "
          f"root_inputs={actual['integer_recovery']['root_inputs']} "
          f"controls={len(actual['semantic_controls'])} receipt_sha256={digest(actual)}")


if __name__ == "__main__":
    main()
