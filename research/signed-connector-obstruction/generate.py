#!/usr/bin/env python3
"""Generate only this package's exact finite certificate (standard library)."""
import hashlib
import itertools as it
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SEED = 53
REP = ((1, 1, 1), (1, 1, -1), (1, -1, 0))
# A read (i, sign) means y_i += sign * A_i z; B means z += sign * B_j x_j.
WORD = [("B", 0, -1), ("B", 0, -1), ("A", 2, -1),
        ("B", 0, 1), ("B", 1, -1), ("A", 1, -1), ("A", 2, 1),
        ("B", 2, -1), ("A", 0, -1), ("B", 0, 1),
        ("B", 1, 1), ("A", 1, 1), ("B", 2, 1), ("A", 0, 1)]


def canonical(v):
    for x in v:
        if x:
            return tuple(x * y for y in v)
    return v


DIRECTIONS = sorted({canonical(v) for v in it.product((-1, 0, 1), repeat=3)}
                - {(0, 0, 0)})


def source_paths():
    records = []
    for order in sorted(set(it.permutations((0, 0, 1, 1, 2, 2)))):
        for signs in it.product((-1, 1), repeat=3):
            seen = [0] * 3
            q = [0] * 3
            states = [tuple(q)]
            for j in order:
                q[j] += signs[j] * (1 if seen[j] == 0 else -1)
                seen[j] += 1
                states.append(tuple(q))
            diffs = {canonical(tuple(b - a for a, b in zip(s, t)))
                     for i, s in enumerate(states) for t in states[i + 1:]}
            mask = sum(1 << k for k, v in enumerate(DIRECTIONS) if v in diffs)
            records.append({"order": order, "first_signs": signs, "mask": mask})
    return records


def matrix_mask(rows):
    return sum(1 << k for k in {DIRECTIONS.index(canonical(tuple(row)))
                               for row in rows if any(row)})


def orbit():
    results = {}
    for rp in it.permutations(range(3)):
        for cp in it.permutations(range(3)):
            for rs in it.product((-1, 1), repeat=3):
                for cs in it.product((-1, 1), repeat=3):
                    rows = tuple(tuple(rs[i] * cs[j] * REP[rp[i]][cp[j]]
                                       for j in range(3)) for i in range(3))
                    word = []
                    for kind, old, s in WORD:
                        j = (rp if kind == "A" else cp).index(old)
                        sign = (rs if kind == "A" else cs)[j]
                        word.append((kind, j, s * sign))
                    results.setdefault(rows, word)
    return results


def inverse(word):
    return [(*op[:-1], -op[-1]) for op in reversed(word)]


def lower(factors, source, target, pool):
    if len(factors) == 1:
        return [(factors[0], source, target, 1)]
    split = len(factors) // 2
    connector, *rest = pool
    right = lower(factors[:split], source, connector, rest)
    left = lower(factors[split:], connector, target, rest)
    return right + left + inverse(right) + inverse(left)


def lower_word(word, factors):
    result = []
    for kind, j, sign in word:
        source, target = (j, 6) if kind == "B" else (6, 3 + j)
        part = lower(factors[(0 if kind == "B" else 3) + j], source, target,
                     [7, 8, 9])
        result += part if sign == 1 else inverse(part)
    return result


def stars(rows, by):
    result = []
    if by == "column":
        for j in range(3):
            active = [(i, rows[i][j]) for i in range(3) if rows[i][j]]
            if active:
                result += [("B", j, 1)]
                result += [("A", i, s) for i, s in active]
                result += [("B", j, -1)]
                result += [("A", i, -s) for i, s in reversed(active)]
    else:
        for i, row in enumerate(rows):
            active = [(j, s) for j, s in enumerate(row) if s]
            if active:
                result += [("B", j, s) for j, s in active]
                result += [("A", i, 1)]
                result += [("B", j, -s) for j, s in reversed(active)]
                result += [("A", i, -1)]
    return result


def build():
    paths = source_paths()
    masks = {p["mask"] for p in paths}
    missing = []
    covered = 0
    unsigned_covered = 0
    for flat in it.product((-1, 0, 1), repeat=9):
        rows = tuple(tuple(flat[3*i:3*i+3]) for i in range(3))
        wanted = matrix_mask(rows)
        if any(wanted & mask == wanted for mask in masks):
            covered += 1
            unsigned_covered += all(x >= 0 for x in flat)
        else:
            missing.append(rows)
    family = orbit()
    if set(missing) != set(family):
        raise RuntimeError("obstruction orbit and finite classification disagree")
    fixture = missing[SEED % len(missing)]
    factors = []
    cursor = 0
    for length in range(2, 8):
        factors.append(list(range(cursor, cursor + length)))
        cursor += length
    lowered = lower_word(WORD, factors)
    row_word, col_word = stars(REP, "row"), stars(REP, "column")
    # Compact path digest is supplementary; verification reconstructs every path.
    path_json = json.dumps(paths, separators=(",", ":"), sort_keys=True).encode()
    return {
        "format": "signed-connector-obstruction-v1",
        "seed": SEED,
        "base": "91a2094f2e022930069e8cfdc810a3ea1b81cd09",
        "coefficient_domain": [-1, 0, 1],
        "shape": [3, 3],
        "directions": DIRECTIONS,
        "closed_source_paths": len(paths),
        "path_sha256": hashlib.sha256(path_json).hexdigest(),
        "distinct_path_masks": sorted(masks),
        "support_bound_attained": covered,
        "unsigned_patterns_attained": unsigned_covered,
        "obstructed_patterns": missing,
        "canonical": {"matrix": REP, "word": WORD,
                      "support_lower_bound": 12, "minimum_queries": 14},
        "seed_fixture": {"index": SEED % len(missing), "matrix": fixture,
                         "word": family[fixture]},
        "recursive": {
            "factor_lengths": list(range(2, 8)), "factors": factors,
            "live_roles": 10, "dirty_arrays": 4,
            "word": lowered, "leaf_calls": len(lowered),
            "row_star_word": row_word, "column_star_word": col_word,
            "row_star_leaves": len(lower_word(row_word, factors)),
            "column_star_leaves": len(lower_word(col_word, factors)),
        },
        "scope": "Exact finite restricted-query classification; no supplier or kappa claim."
    }


if __name__ == "__main__":
    (ROOT / "CERTIFICATE.json").write_text(json.dumps(build(), indent=2) + "\n")
    print("WROTE_SIGNED_CONNECTOR_CERTIFICATE")
