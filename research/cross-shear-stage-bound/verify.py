#!/usr/bin/env python3
"""Finite checks for the cross-shear stage bound; not a theorem prover.

Python standard library only. Original controller sources are hash-checked;
only the inspected, dependency-free recipe function is evaluated.
"""

import argparse
import ast
from collections import Counter
from fractions import Fraction
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = (
    "research/e8-bit-r420/vendor/pr510/e8-r480-nine-stage/vendor/"
    "e8-r715-eleven-stage-whole/code/global_k.py"
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def identity(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def rank_q(matrix):
    """Gaussian elimination over Q, independent of all repository engines."""
    a = [[Fraction(x) for x in row] for row in matrix]
    r = 0
    for col in range(len(a[0])):
        pivot = next((i for i in range(r, len(a)) if a[i][col]), None)
        if pivot is None:
            continue
        a[r], a[pivot] = a[pivot], a[r]
        divisor = a[r][col]
        a[r] = [x / divisor for x in a[r]]
        for i in range(r + 1, len(a)):
            if a[i][col]:
                factor = a[i][col]
                a[i] = [x - factor * y for x, y in zip(a[i], a[r])]
        r += 1
        if r == len(a):
            break
    return r


def potential_q(matrix):
    d = len(matrix) // 2
    return rank_q([r[:d] for r in matrix[:d]]) + rank_q(
        [r[d:] for r in matrix[d:]]
    )


def target(d):
    """The signed swap before the terminal exchange: (X,Y) -> (-Y,X)."""
    eye = identity(d)
    return [[0] * d + [-x for x in row] for row in eye] + [
        row + [0] * d for row in eye
    ]


def word(pairs):
    """Independent scalar expansion of the credited borrowing chain.

    Each tuple is (paid/free, destination, source, coefficient). Coordinates
    are grouped as all X banks followed by all Y banks, unlike the source.
    """
    out = [("paid", pairs, 0, 1)]
    for j in range(pairs):
        out.append(("paid", j, pairs + j, -1))
        if j + 1 < pairs:
            out.extend([("free", j, j + 1, 1),
                        ("free", pairs + j + 1, pairs + j, -1)])
        out.append(("paid", pairs + j, j, 1))
        if j + 1 < pairs:
            out.extend([("free", j, j + 1, -1),
                        ("free", pairs + j + 1, pairs + j, 1)])
    for j in range(pairs - 2, -1, -1):
        out.extend([("free", j + 1, j, 1),
                    ("free", pairs + j, pairs + j + 1, -1)])
    return out


def apply(matrix, op, width):
    _, dst, src, coefficient = op
    for k in range(width):
        i, j = dst * width + k, src * width + k
        matrix[i] = [x + coefficient * y for x, y in zip(matrix[i], matrix[j])]


def replay(pairs, width, ops, audit=False):
    require(pairs >= 1 and width >= 1, "positive block dimensions required")
    matrix = identity(2 * pairs * width)
    trace = [2 * pairs * width]
    paid = 0
    for op in ops:
        kind, dst, src, coefficient = op
        require(kind in ("paid", "free") and 0 <= dst < 2 * pairs
                and 0 <= src < 2 * pairs and dst != src and coefficient != 0,
                "invalid elementary block operation")
        same_half = (dst < pairs) == (src < pairs)
        require(same_half == (kind == "free"), "operation violates its block class")
        before = potential_q(matrix) if audit else None
        apply(matrix, op, width)
        if audit:
            after = potential_q(matrix)
            if op[0] == "paid":
                require(before - after <= width, "rank drop exceeds the call cap")
                require(paid != 0 or after == before, "first call changes potential")
                trace.append(after)
                paid += 1
            else:
                require(before == after, "within-block bridge changes potential")
    return matrix, trace


def source_checks():
    pins = json.loads((HERE / "SOURCE-PINS.json").read_text())
    for relative, expected in pins["files"].items():
        actual = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
        require(actual == expected, "source pin mismatch: " + relative)
    tree = ast.parse((ROOT / SOURCE).read_text())
    functions = [n for n in tree.body if isinstance(n, ast.FunctionDef)
                 and n.name == "recipe"]
    require(len(functions) == 1, "expected one pinned recipe function")
    namespace = {"__builtins__": {"dict": dict, "range": range, "reversed": reversed}}
    code = compile(ast.Module(body=functions, type_ignores=[]), SOURCE, "exec")
    exec(code, namespace)
    for p in range(1, 17):
        expanded = []
        events = namespace["recipe"](p)
        require(events[-1] == {"kind": "exchange"}, "terminal exchange changed")
        for e in events[:-1]:
            if e["kind"] == "local":
                j = e["pair"]
                expanded.append(("paid", j, p + j, -1) if e["reverse"]
                                else ("paid", p + j, j, 1))
            elif e["kind"] == "bridge":
                d, s, c = e["dst"], e["src"], e["coefficient"]
                expanded.extend([("free", d, s, c), ("free", p + s, p + d, -c)])
            else:
                raise ValueError("unexpected pinned event")
        require(expanded == word(p), "independent word differs from source recipe")
    return len(pins["files"])


def witnesses():
    domain = [(p, 1) for p in range(1, 17)] + [
        (p, v) for p in range(1, 7) for v in (2, 3)
    ]
    rows = []
    for p, v in domain:
        ops = word(p)
        result, trace = replay(p, v, ops, audit=True)
        require(result == target(p * v), "wrong signed swap")
        exchange = result[p * v:] + [[-x for x in r] for r in result[:p * v]]
        require(exchange == identity(2 * p * v), "signed exchange does not restore")
        require(trace == [2 * p * v] + list(range(2 * p * v, -1, -v)),
                "witness does not saturate each available rank drop")
        rows.append({"pairs": p, "width": v, "paid_calls": 2 * p + 1,
                     "bridge_shears": 6 * (p - 1), "potential_after_paid": trace})
    return rows


def rank_f2(rows):
    pivots = {}
    for value in rows:
        while value:
            col = value.bit_length() - 1
            if col not in pivots:
                pivots[col] = value
                break
            value ^= pivots[col]
    return len(pivots)


def potential_f2(rows):
    return rank_f2([x & 3 for x in rows[:2]]) + rank_f2([x >> 2 for x in rows[2:]])


def combine(bits, rows):
    return (rows[0] if bits & 1 else 0) ^ (rows[1] if bits & 2 else 0)


def exhaustive_f2():
    """All GL(4,2) prefixes, all rank-one cross calls, all GL(2,2)^2 bridges."""
    matrices = [(packed & 3, packed >> 2) for packed in range(16)]
    rank_one = [a for a in matrices if rank_f2(a) == 1]
    gl2 = [a for a in matrices if rank_f2(a) == 2]
    counts = Counter()
    drops = Counter()
    for packed in range(65536):
        m = tuple((packed >> (4 * i)) & 15 for i in range(4))
        if rank_f2(m) != 4:
            continue
        counts["invertible_prefixes"] += 1
        phi = potential_f2(m)
        diagonal = not any(x >> 2 for x in m[:2]) and not any(x & 3 for x in m[2:])
        for e in rank_one:
            for lower in (True, False):
                result = (m[:2] + tuple(m[2 + i] ^ combine(e[i], m[:2]) for i in range(2))
                          if lower else
                          tuple(m[i] ^ combine(e[i], m[2:]) for i in range(2)) + m[2:])
                drop = phi - potential_f2(result)
                require(-1 <= drop <= 1, "F2 cross-call rank inequality failed")
                drops[str(drop)] += 1
                counts["rank_one_transitions"] += 1
                if diagonal:
                    require(drop == 0, "F2 first-call zero progress failed")
                    counts["first_call_checks"] += 1
        for s in gl2:
            for t in gl2:
                result = tuple(combine(row, m[:2]) for row in s) + tuple(
                    combine(row, m[2:]) for row in t)
                require(potential_f2(result) == phi, "F2 bridge invariance failed")
                counts["bridge_transitions"] += 1
    require(counts == {"invertible_prefixes": 20160, "rank_one_transitions": 362880,
                       "first_call_checks": 648, "bridge_transitions": 725760},
            "incomplete finite census")
    return {**dict(counts), "rank_drop_histogram": dict(sorted(drops.items()))}


def negative_controls():
    counts = Counter()
    for p in range(1, 7):
        ops = word(p)
        for i, op in enumerate(ops):
            omitted = ops[:i] + ops[i + 1:]
            damaged = replay(p, 1, omitted)[0]
            require(damaged != target(p), "omitted operation accepted")
            if op[0] == "paid":
                require(potential_q(damaged) > 0,
                        "too few calls reached an antidiagonal endpoint")
            counts["omitted_" + op[0]] += 1
            changed = list(ops)
            changed[i] = (*op[:3], -op[3])
            require(replay(p, 1, changed)[0] != target(p), "wrong sign accepted over Q")
            counts["wrong_sign_" + op[0]] += 1

    # Three full-rank shears swap two-dimensional blocks. They are outside a
    # rank-one cap: removing that hypothesis invalidates a five-call bound.
    full_width = [("paid", 1, 0, 1), ("paid", 0, 1, -1), ("paid", 1, 0, 1)]
    matrix, trace = replay(1, 2, full_width, audit=True)
    require(matrix == target(2) and len(full_width) < 5, "rank-cap control failed")
    require(rank_q(identity(2)) > 1, "rank-two call admitted under rank-one cap")
    counts["rank_cap_is_necessary"] = 1

    # The terminal exchange is deliberately outside the allowed bridge class.
    swap = target(2)
    require(potential_q(identity(4)) == 4 and potential_q(swap) == 0,
            "free-swap control failed")
    require(any(x for row in swap[:2] for x in row[2:]),
            "cross-block exchange incorrectly classified as block diagonal")
    counts["terminal_exchange_is_not_a_bridge"] = 1

    # Identity is not a swap, and singular diagonal maps are not free bridges.
    require(identity(4) != target(2), "identity mistaken for endpoint")
    counts["endpoint_hypothesis_is_necessary"] = 1
    singular = identity(4)
    singular[0] = [0] * 4
    require(rank_q(singular) < 4 and potential_q(singular) < 4,
            "singular-bridge control failed")
    counts["singular_bridge_changes_potential"] = 1

    # Check that the two rank engines are not silently using the same field.
    require(rank_q([[1, 1], [1, -1]]) == 2 and rank_f2([3, 3]) == 1,
            "field distinction failed")
    counts["rational_vs_binary_rank"] = 1
    return dict(sorted(counts.items()))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-result", type=Path,
                        help="write the freshly computed finite evidence to a new file")
    args = parser.parse_args()
    result = {
        "status": "PASS_CROSS_SHEAR_STAGE_BOUND",
        "base_commit": "66849e1475c930fd7732b1a0067ffee7e1e95f60",
        "input_files_checked": source_checks(),
        "source_recipe_pairs_checked": list(range(1, 17)),
        "rational_witnesses": witnesses(),
        "exhaustive_f2": exhaustive_f2(),
        "negative_controls": negative_controls(),
        "scope": "Finite supporting evidence for the written rank proof; no physical supplier, all-size, or multiplication-theorem verification.",
    }
    if args.write_result:
        with args.write_result.open("x") as out:
            out.write(json.dumps(result, indent=2) + "\n")
    else:
        expected = json.loads((HERE / "RESULT.json").read_text())
        require(result == expected, "finite evidence differs from RESULT.json")
    print(result["status"], "28 rational witnesses; 20160 F2 prefixes;",
          "362880 cross-call and 725760 bridge transitions")


if __name__ == "__main__":
    main()
