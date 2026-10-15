#!/usr/bin/env python3
"""Exact bounded search for E6 rank-four projected-Gram decoders."""
from __future__ import annotations

import argparse
import json
from fractions import Fraction
from hashlib import sha256
from itertools import combinations, product
from pathlib import Path

TARGET = 22
FLOOR = 5
AXES = range(8)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def canonical_line(v):
    first = next(x for x in v if x)
    return tuple(v if first > 0 else (-x for x in v))


def e6_lines():
    """Return exact E6 root lines, scaled by 2, in the pinned E8 realization."""
    roots = []
    for i, j in combinations(AXES, 2):
        for a, b in product((2, -2), repeat=2):
            v = [0] * 8
            v[i], v[j] = a, b
            roots.append(tuple(v))
    for signs in product((-1, 1), repeat=8):
        if sum(x < 0 for x in signs) % 2 == 0:
            roots.append(tuple(signs))
    r1 = (2, 2, 0, 0, 0, 0, 0, 0)
    r2 = (2, 0, 2, 0, 0, 0, 0, 0)
    lines = sorted({canonical_line(v) for v in roots if dot(v, r1) == 0 and dot(v, r2) == 0})
    require(len(lines) == 36, f"expected 36 E6 lines, got {len(lines)}")
    require(all(dot(v, v) == 8 for v in lines), "root norm control failed")
    return lines


def rank_q(rows):
    if not rows:
        return 0
    a = [[Fraction(x) for x in row] for row in rows]
    m, n = len(a), len(a[0])
    r = 0
    for c in range(n):
        pivot = next((i for i in range(r, m) if a[i][c]), None)
        if pivot is None:
            continue
        a[r], a[pivot] = a[pivot], a[r]
        value = a[r][c]
        a[r] = [x / value for x in a[r]]
        for i in range(m):
            if i != r and a[i][c]:
                factor = a[i][c]
                a[i] = [x - factor * y for x, y in zip(a[i], a[r])]
        r += 1
        if r == m:
            break
    return r


def rank_f2(rows):
    """Rank of integer bit rows over F2; each row is one Python int."""
    pivots = {}
    for value in rows:
        x = value
        while x:
            pivot = x.bit_length() - 1
            if pivot in pivots:
                x ^= pivots[pivot]
            else:
                pivots[pivot] = x
                break
    return len(pivots)


def submatrix_rank(b_rows, row_support, col_support):
    positions = {c: k for k, c in enumerate(col_support)}
    rows = []
    for r in row_support:
        bits = 0
        row = b_rows[r]
        for c, k in positions.items():
            if (row >> c) & 1:
                bits |= 1 << k
        rows.append(bits)
    return rank_f2(rows)


def adapted_pairing(lines, matrix):
    n = len(lines)
    b = [0] * n
    for t in range(n):
        b[t] |= 1 << t
        for s in range(t + 1, n):
            if dot(lines[t], lines[s]) == 0 and matrix[t][s] == 0 and matrix[s][t] == 0:
                b[t] |= 1 << s
                b[s] |= 1 << t
    return b


def check_pairing(lines, matrix, b_rows):
    n = len(lines)
    require(len(matrix) == n and len(b_rows) == n, "matrix dimension mismatch")
    for t in range(n):
        require((b_rows[t] >> t) & 1, "pairing diagonal is not one")
        require(matrix[t][t] != 0, "decoder diagonal is zero")
        for s in range(n):
            if (b_rows[t] >> s) & 1:
                require(t == s or dot(lines[t], lines[s]) == 0,
                        f"pairing has a one on nonorthogonal lines ({t},{s})")
                if t != s:
                    require(matrix[t][s] == 0, f"decoder violates pairing zero ({t},{s})")


def candidate(lines, u, v):
    p = [tuple(root[k] for k in u) for root in lines]
    q = [tuple(root[k] for k in v) for root in lines]
    if rank_q(p) != 4 or rank_q(q) != 4:
        return None
    matrix = [[dot(p[t], q[s]) for s in range(36)] for t in range(36)]
    if any(matrix[t][t] == 0 for t in range(36)):
        return None
    b_rows = adapted_pairing(lines, matrix)
    check_pairing(lines, matrix, b_rows)
    ranks = []
    for j in range(4):
        row_support = [t for t in range(36) if p[t][j] != 0]
        col_support = [s for s in range(36) if q[s][j] != 0]
        ranks.append(submatrix_rank(b_rows, row_support, col_support))
    charged = [max(FLOOR, rank) for rank in ranks]
    return {
        "u": list(u),
        "v": list(v),
        "raw_ranks": ranks,
        "charged_terms": charged,
        "cost": sum(charged),
        "pairing_sha256": sha256(b"".join(x.to_bytes(5, "little") for x in b_rows)).hexdigest(),
        "matrix_sha256": sha256(repr(matrix).encode()).hexdigest(),
    }


def orthogonality_positive_control(lines):
    gram = [[dot(a, b) for b in lines] for a in lines]
    require(all(gram[i][i] == 8 for i in range(36)), "Gram diagonal control failed")
    for i in range(36):
        for j in range(36):
            if i != j and dot(lines[i], lines[j]) == 0:
                require(gram[i][j] == 0, "Gram orthogonality control failed")
    b0 = []
    for i in range(36):
        bits = 1 << i
        for j in range(36):
            if i != j and dot(lines[i], lines[j]) == 0:
                bits |= 1 << j
        b0.append(bits)
    check_pairing(lines, gram, b0)
    nonorthogonal = next((i, j) for i in range(36) for j in range(i + 1, 36)
                         if dot(lines[i], lines[j]) != 0)
    bad_pairing = b0[:]
    i, j = nonorthogonal
    bad_pairing[i] |= 1 << j
    try:
        check_pairing(lines, gram, bad_pairing)
    except ValueError:
        pass
    else:
        raise ValueError("negative control failed to reject a nonorthogonal pairing edge")
    bad_gram = [row[:] for row in gram]
    bad_gram[0][0] = 0
    try:
        check_pairing(lines, bad_gram, b0)
    except ValueError:
        pass
    else:
        raise ValueError("negative control failed to reject a zero decoder diagonal")
    return gram, b0


def small_rank_controls():
    require(rank_f2([0b001, 0b010, 0b100]) == 3, "F2 identity rank control failed")
    require(rank_f2([0b111, 0b111, 0b111]) == 1, "F2 all-ones rank control failed")


def scan(lines, pairs):
    tested = 0
    valid = 0
    best = None
    best_ties = 0
    target_hits = []
    valid_candidates = []
    for u, v in pairs:
        tested += 1
        result = candidate(lines, u, v)
        if result is None:
            continue
        valid += 1
        valid_candidates.append(result)
        key = (result["cost"], tuple(result["u"]), tuple(result["v"]))
        if best is None or key < best[0]:
            best = (key, result)
            best_ties = 1
        elif key[0] == best[0][0]:
            best_ties += 1
        if result["cost"] <= TARGET:
            target_hits.append(result)
    return {"tested": tested, "valid": valid, "best": None if best is None else best[1],
            "best_ties": best_ties, "target_hits": target_hits,
            "valid_candidates": valid_candidates}


def required_zero_graph(lines, u, v):
    p = [tuple(root[k] for k in u) for root in lines]
    q = [tuple(root[k] for k in v) for root in lines]
    matrix = [[dot(p[t], q[s]) for s in range(36)] for t in range(36)]
    adj = [0] * 36
    reasons = {}
    for t in range(36):
        for s in range(t + 1, 36):
            tags = []
            if dot(lines[t], lines[s]) != 0:
                tags.append("nonorthogonal")
            if matrix[t][s] != 0:
                tags.append("M_ts_nonzero")
            if matrix[s][t] != 0:
                tags.append("M_st_nonzero")
            if tags:
                adj[t] |= 1 << s
                adj[s] |= 1 << t
                reasons[(t, s)] = tags
    return adj, reasons


def find_clique_at_least_six(adj):
    """Find a six-clique in a required-zero graph, or exhaustively return None."""
    def visit(candidates, chosen):
        if len(chosen) >= 6:
            return chosen[:6]
        if len(chosen) + candidates.bit_count() < 6:
            return None
        remaining = candidates
        while remaining:
            bit = remaining & -remaining
            remaining ^= bit
            vertex = bit.bit_length() - 1
            found = visit(remaining & adj[vertex], chosen + [vertex])
            if found is not None:
                return found
        return None
    return visit((1 << len(adj)) - 1, [])


def run():
    small_rank_controls()
    lines = e6_lines()
    orthogonality_positive_control(lines)
    axes4 = list(combinations(AXES, 4))
    principal = scan(lines, ((u, u) for u in axes4))
    result = {"root_lines": len(lines), "root_sha256": sha256(repr(lines).encode()).hexdigest(),
              "target_cost": TARGET, "per_total_floor": FLOOR,
              "principal": principal, "pivot": None}
    if not principal["target_hits"]:
        ordered = ((u, v) for u in axes4 for v in axes4)
        result["pivot"] = scan(lines, ordered)
    if result["pivot"] is not None and not result["pivot"]["target_hits"]:
        clique_receipts = []
        for item in result["pivot"]["valid_candidates"]:
            u, v = tuple(item["u"]), tuple(item["v"])
            adjacency, reasons = required_zero_graph(lines, u, v)
            clique = find_clique_at_least_six(adjacency)
            if clique is not None:
                pairs = []
                for i, t in enumerate(clique):
                    for s in clique[i + 1:]:
                        pairs.append({"pair": [t, s], "reasons": reasons[(min(t, s), max(t, s))]})
                clique_receipts.append({"u": list(u), "v": list(v), "clique": clique, "pairs": pairs})
            else:
                clique_receipts.append({"u": list(u), "v": list(v), "clique": None})
        result["rank5_gram_clique_screen"] = {
            "candidate_count": len(result["pivot"]["valid_candidates"]),
            "six_clique_count": sum(x["clique"] is not None for x in clique_receipts),
            "receipts": clique_receipts,
        }
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="write the canonical RESULT.json")
    args = parser.parse_args()
    result = run()
    result_path = Path(__file__).with_name("RESULT.json")
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.write:
        result_path.write_text(encoded, encoding="utf-8", newline="\n")
    else:
        require(result_path.is_file(), "missing RESULT.json; regenerate with --write")
        expected = json.loads(result_path.read_text(encoding="utf-8"))
        require(expected == result, "stored RESULT.json differs from exact replay")
    principal = result["principal"]
    print("E6_PROJECTED_GRAM_SCREEN", end=" ")
    print(f"roots={result['root_lines']} principal={principal['tested']} valid={principal['valid']} "
          f"best_cost={None if principal['best'] is None else principal['best']['cost']}", end=" ")
    if principal["target_hits"]:
        print(f"target_hits={len(principal['target_hits'])} winner={principal['target_hits'][0]}")
        return
    pivot = result["pivot"]
    if pivot is None:
        print("ERROR: expected the ordered-projection pivot")
        raise SystemExit(1)
    print(f"ordered={pivot['tested']} valid={pivot['valid']} "
          f"best_cost={None if pivot['best'] is None else pivot['best']['cost']} "
          f"best={pivot['best']}")
    require(not pivot["target_hits"], "unexpected target candidate; inspect exact witness")
    print("NO_COST_LE_22_IN_DECLARED_PROJECTED_GRAM_FAMILY")
    c = result.get("rank5_gram_clique_screen")
    if c is not None:
        print(f"RANK5_GRAM_PAIRING_CLIQUES candidates={c['candidate_count']} "
              f"six_cliques={c['six_clique_count']}")
        if c["six_clique_count"] == c["candidate_count"]:
            print("NO_RANK5_GRAM_PAIRING_FOR_DECLARED_PROJECTED_DECODERS")
    print("PASS_E6_ADAPTED_PAIRING_CONTROLS_AND_RESULT")
    print("RESULT_SHA256", sha256(encoded.encode()).hexdigest())


if __name__ == "__main__":
    main()
