#!/usr/bin/env python3
"""Exact finite corroboration of PROOF.md; no universal theorem acceptance.

Krzysztof Wojt with substantial OpenAI Codex assistance. Apache-2.0.
Standard library only; read-only and independent of Git/network/predecessor code.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
from itertools import product
import json
from math import comb
from pathlib import Path
import runpy


PACKAGE = Path(__file__).resolve().parent


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def multiplicity(h: int) -> int:
    require(type(h) is int and h >= 2 and h % 2 == 0, "even integer h >= 2 required")
    return 2 ** (h - 2) + (-1) ** (h // 2) * 2 ** (h // 2 - 1)


def claimed_rank(h: int) -> int:
    d = multiplicity(h)
    return 1 if h == 2 else 2 ** h - 1 - d


def pack(row: list[int] | tuple[int, ...]) -> tuple[int, int]:
    return tuple(sum(1 << j for j, x in enumerate(row) if x % 3 == c)
                 for c in (1, 2))


def add(a: tuple[int, int], b: tuple[int, int]) -> tuple[int, int]:
    a1, a2 = a
    b1, b2 = b
    an, bn = a1 | a2, b1 | b2
    return ((a1 & ~bn) | (b1 & ~an) | (a2 & b2),
            (a2 & ~bn) | (b2 & ~an) | (a1 & b1))


def packed_rank(rows: list[tuple[int, int]]) -> int:
    basis = {}
    for row in rows:
        require(row[0] & row[1] == 0, "overlapping ternary digit masks")
        while row[0] | row[1]:
            pivot = (row[0] | row[1]) & -(row[0] | row[1])
            if row[1] & pivot:
                row = (row[1], row[0])
            if pivot not in basis:
                basis[pivot] = row
                break
            b1, b2 = basis[pivot]
            row = add(row, (b2, b1))
    return len(basis)


def interior_rows(h: int) -> list[tuple[int, int]]:
    """Build I-A directly by enumerating nonzero submasks of each complement."""
    full = (1 << h) - 1
    rows = []
    for u in range(1, full):
        complement = full ^ u
        v, twos = complement, 0
        while v:
            twos |= 1 << (v - 1)
            v = (v - 1) & complement
        rows.append((1 << (u - 1), twos))
    return rows


def tensor_action(vector: list[int], h: int) -> list[int]:
    """Apply K^{tensor h} by local two-coordinate steps, in F3."""
    require(len(vector) == 1 << h, "tensor dimension mismatch")
    result = vector[:]
    for bit in range(h):
        stride = 1 << bit
        for start in range(0, len(result), 2 * stride):
            for offset in range(stride):
                lo, hi = start + offset, start + offset + stride
                a, b = result[lo], result[hi]
                result[lo], result[hi] = (a + b) % 3, a
    return result


def sub(a: list[int], b: list[int]) -> list[int]:
    return [(x - y) % 3 for x, y in zip(a, b, strict=True)]


def polynomial_columns(h: int) -> tuple[list[list[int]], list[list[int]]]:
    """Check T^4=I, MP=0, P^2=P and MG=GM=I-P on every basis column."""
    n = 1 << h
    ps, gs = [], []
    for j in range(n):
        e = [int(i == j) for i in range(n)]
        t = [e]
        for _ in range(4):
            t.append(tensor_action(t[-1], h))
        require(t[4] == e, "T^4 is not I")
        p = [sum(row[i] for row in t[:4]) % 3 for i in range(n)]
        g = sub(t[2], t[1])
        require(tensor_action(p, h) == p, "MP is nonzero")
        # On an eigenvalue-one vector, I+T+T^2+T^3 is multiplication by 4=1.
        pp = p[:]
        current = p[:]
        for _ in range(3):
            current = tensor_action(current, h)
            pp = [(x + y) % 3 for x, y in zip(pp, current, strict=True)]
        require(pp == p, "P is not idempotent")
        require(sub(g, tensor_action(g, h)) == sub(e, p), "MG != I-P")
        me = sub(e, t[1])
        tme = tensor_action(me, h)
        require(sub(tensor_action(tme, h), tme) == sub(e, p), "GM != I-P")
        require(p[0] == p[-1], "full kernel projector endpoints differ")
        if h <= 4:
            require(t[1] == [int((i & j) == 0) for i in range(n)],
                    "tensor action disagrees with literal disjointness")
        ps.append(p)
        gs.append(g)
    require([[gs[j][i] for j in (0, n - 1)] for i in (0, n - 1)]
            == [[0, 0], [0, 1]], "incorrect G endpoint block")
    require(all(ps[j][i] == 0 for i in (0, n - 1) for j in (0, n - 1)),
            "incorrect P endpoint block")
    require(packed_rank([pack(c) for c in ps]) == multiplicity(h),
            "projector rank differs from integer eigenspace count")
    return ps, gs


def kernel_count(matrix: list[list[int]]) -> tuple[int, int]:
    """Count every ternary input via two complete half-input syndrome tables."""
    n = len(matrix)
    columns = list(zip(*matrix, strict=True))

    def syndromes(part: list[tuple[int, ...]]) -> Counter:
        table = Counter({(0,) * n: 1})
        for col in part:
            nxt = Counter()
            for key, count in table.items():
                for coefficient in range(3):
                    nxt[tuple((x + coefficient * y) % 3
                              for x, y in zip(key, col, strict=True))] += count
            table = nxt
        return table

    cut = n // 2
    left, right = syndromes(columns[:cut]), syndromes(columns[cut:])
    count = sum(value * right.get(tuple((-x) % 3 for x in key), 0)
                for key, value in left.items())
    return count, 3 ** cut + 3 ** (n - cut)


def rejection_controls(independent: dict, ps: list[list[int]], gs: list[list[int]]) -> list[str]:
    rejected = []
    for h in (-2, 0, 1, 3, 5, 4.0, True):
        try:
            claimed_rank(h)
        except ValueError:
            rejected.append(f"invalid_dimension_{h!r}")
        else:
            raise ValueError(f"invalid h accepted: {h!r}")
    require(2 ** 2 - 1 - multiplicity(2) != claimed_rank(2), "h=2 control lost")
    rejected.append("omit_h2_exception")
    require(14 - multiplicity(4) != claimed_rank(4), "wrong nullity control lost")
    rejected.append("keep_full_kernel_nullity_after_deletion")
    for endpoint in ("empty", "full"):
        value = independent["full_subset_matrix_I_minus_K_tensor_h"]["4"][
            f"rank_after_deleting_{endpoint}_subset"]
        require(value != claimed_rank(4), "single-endpoint deletion control lost")
        rejected.append(f"delete_only_{endpoint}")
    # A wrong-sign G has the wrong endpoint block and violates MG=I-P.
    h, n = 4, 16
    e = [int(i == 0) for i in range(n)]
    t1 = tensor_action(e, h)
    t2 = tensor_action(t1, h)
    bad_g = [(x + y) % 3 for x, y in zip(t2, t1, strict=True)]
    require(sub(bad_g, tensor_action(bad_g, h)) != sub(e, ps[0]),
            "wrong-sign group inverse control lost")
    rejected.append("G_equals_T_squared_plus_T")
    bad_p = [(2 * x) % 3 for x in ps[0]]
    require(sub(gs[0], tensor_action(gs[0], h)) != sub(e, bad_p),
            "scaled projector control lost")
    rejected.append("scale_projector_by_two")
    return rejected


def verify() -> dict:
    separate = runpy.run_path(str(PACKAGE / "independent.py"))
    independent = separate["collect_results"]()
    dense_rank = separate["rank_mod3"]
    # Exhaustive small rectangular matrices test all ternary pivot coefficients.
    matrices = 0
    for digits in product(range(3), repeat=6):
        rows = [list(digits[:3]), list(digits[3:])]
        require(packed_rank([pack(r) for r in rows]) == dense_rank(rows),
                "packed rank disagrees with separate dense elimination")
        matrices += 1
    ranks = {}
    for h in (2, 4, 6, 8, 10):
        rank = packed_rank(interior_rows(h))
        require(rank == claimed_rank(h), f"literal interior rank fails at h={h}")
        ranks[str(h)] = rank
        if h <= 8:
            require(rank == independent["proper_nonempty_subset_matrix_I_minus_A"][str(h)]["rank_mod_3"],
                    "independent literal matrix rank disagrees")
    multiplicities = {}
    for h in range(2, 202, 2):
        exact = sum(comb(h, k) for k in range(h + 1) if (h + 2 * k) % 8 == 0)
        require(exact == multiplicity(h), "integer multiplicity formula fails")
        multiplicities[str(h)] = exact
    polys = {}
    for h in (2, 4, 6, 8):
        ps, gs = polynomial_columns(h)
        polys[str(h)] = {"columns": 1 << h, "projector_rank": multiplicity(h)}
        if h == 4:
            controls = rejection_controls(independent, ps, gs)
    counts = {}
    for h in (2, 4):
        _, _, matrix = separate["proper_subset_matrices"](h)
        count, partial_inputs = kernel_count(matrix)
        expected = 3 ** (len(matrix) - claimed_rank(h))
        require(count == expected, "complete kernel count disagrees")
        counts[str(h)] = {"kernel_vectors": count, "covered_inputs": 3 ** len(matrix),
                          "enumerated_half_inputs": partial_inputs}
    return {"ranks": ranks, "independent_literal_ranks": independent,
            "packed_rank_small_matrices": matrices,
            "multiplicity_formula_checks": len(multiplicities),
            "polynomial_identity_checks": polys, "complete_kernel_counts": counts,
            "rejection_controls": controls, "new_kappa": None}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit-results", action="store_true",
                        help="print regenerated finite evidence; write no files")
    args = parser.parse_args()
    result = verify()
    if args.emit_results:
        print(json.dumps(result, indent=2, sort_keys=True))
        return
    expected = json.loads((PACKAGE / "RESULTS.json").read_text(encoding="utf-8"))
    require(result == expected, "finite evidence differs from committed RESULTS.json")
    hashes = {p.name: sha256(p.read_bytes()).hexdigest()
              for p in sorted(PACKAGE.iterdir()) if p.is_file()}
    print(json.dumps({"checks": result, "package_sha256": hashes}, sort_keys=True))
    print("PASS_EVEN_TERNARY_DISJOINTNESS_RANK finite_corroboration_only no_new_kappa")


if __name__ == "__main__":
    main()
