#!/usr/bin/env python3
"""Exact corroboration of the joint-correction theorem and its sharp range."""

import ast
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from arithmetic import digit_core, prepare, reduce_pair, separate_core

PAIRS = {(0, 0), (0, 1), (1, 1), (1, 2)}
PACKAGE = Path(__file__).resolve().parent


def require(ok, message):
    if not ok:
        raise ValueError(message)


def check_input(context, x):
    p, q1, q2, _twice_q2, _limit = context
    actual = reduce_pair(context, x)
    expected = (x % q1, x % q2)
    require(actual[:2] == expected, "wrong remainders")
    a, r = divmod(x, p)
    require(actual[2] == (a - x // q1, a - x // q2), "wrong corrections")
    require(actual[2] in PAIRS and len(actual[3]) == 2, "joint tree contract")
    separate = separate_core(context, a, r)
    require(separate[:3] == actual[:3], "separate baseline disagreement")
    return actual[2], len(separate[3])


def exhaustive():
    count = 0
    histogram = {pair: 0 for pair in sorted(PAIRS)}
    depths = set()
    for p in range(2, 65):
        context = prepare(p)
        seen = set()
        for x in range(context[4]):
            pair, separate_depth = check_input(context, x)
            seen.add(pair)
            histogram[pair] += 1
            depths.add(separate_depth)
            count += 1
        require(seen == PAIRS, "four leaves are not all reached")
    require(depths == {2, 3}, "separate comparison depths")
    return count, {str(k): v for k, v in histogram.items()}


def sharpness(p):
    context = prepare(p)
    witnesses = (0, p, p + 1, p * (p + 1))
    observed = {check_input(context, x)[0] for x in witnesses}
    require(observed == PAIRS, "four explicit witnesses")
    x = context[4]
    a, r = divmod(x, p)
    fifth = (a - x // (p + 1), a - x // (p + 2))
    require(fifth == (2, 2) and fifth not in observed, "fifth boundary leaf")
    require(digit_core(context, a, r)[:2] != (x % (p + 1), x % (p + 2)), "outside-prefix control")
    return 5


def boundary_grid():
    count = 0
    for bits in (2, 8, 16, 64, 256, 1024):
        p = 1 << bits
        context = prepare(p)
        for a in sorted({0, 1, p // 2, p // 2 + 1, p, p + 1}):
            candidates = {0, p - 1}
            for threshold in (a, 2 * a, 2 * a - (p + 2)):
                for offset in (-1, 0, 1):
                    candidates.add(threshold + offset)
            for r in sorted(candidates):
                if 0 <= r < p:
                    check_input(context, a * p + r)
                    count += 1
        count += sharpness(p)
    return count


def rejects(function, *args):
    try:
        function(*args)
    except ValueError:
        return
    raise ValueError("negative control accepted")


def controls():
    context = prepare(8)
    count = 0
    for p in (True, 1, 0, -1, 3.0, "4", 1 << 4096):
        rejects(prepare, p)
        count += 1
    for x in (True, -1, context[4], context[4] + 1, 1.0, "1"):
        rejects(reduce_pair, context, x)
        count += 1
    # Strict equality at each branch boundary is semantically necessary.
    require(reduce_pair(context, 9)[2] == (0, 1), "d=0 control")
    require(reduce_pair(context, 10)[2] == (0, 0), "e=0 control")
    require(reduce_pair(context, 48 + 2)[2] == (1, 1), "e=-q2 control")
    count += 3
    # Different output moduli or an omitted correction must change a residue.
    require(reduce_pair(context, 8)[:2] != (8 % 8, 8 % 10), "wrong modulus control")
    require(reduce_pair(context, 8)[:2] != (-1, -2), "omitted correction control")
    return count + 2


def inspect_core():
    path = PACKAGE / "arithmetic.py"
    tree = ast.parse(path.read_text())
    core = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "digit_core")
    nodes = list(ast.walk(core))
    forbidden = (ast.Call, ast.For, ast.While, ast.Div, ast.FloorDiv, ast.Mod, ast.Mult)
    require(not any(isinstance(node, forbidden) for node in nodes), "unpriced core operation")
    comparisons = [node for node in nodes if isinstance(node, ast.Compare)]
    require(len(comparisons) == 3, "static branch predicates")
    require(all(len(node.ops) == 1 and isinstance(node.ops[0], ast.Lt) for node in comparisons), "comparison grammar")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    count, histogram = exhaustive()
    sharp = sum(sharpness(p) for p in range(2, 65))
    result = {
        "exhaustive_inputs": count,
        "correction_histogram": histogram,
        "small_radix_sharpness_witnesses": sharp,
        "large_radix_boundary_cases": boundary_grid(),
        "rejection_controls": controls(),
        "arithmetic_sha256": inspect_core(),
    }
    print(json.dumps(result, sort_keys=True))
    print("PASS_JOINT_ADJACENT_REMAINDERS")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, TypeError) as error:
        sys.exit("FAIL_JOINT_ADJACENT_REMAINDERS: " + str(error))
