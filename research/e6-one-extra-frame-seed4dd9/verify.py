#!/usr/bin/env python3
"""Exact E6 one-extra rank-one decoder support-cell census (stdlib only)."""
from fractions import Fraction as F
from itertools import combinations, product
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise SystemExit("FAIL_E6_ONE_EXTRA_FRAME: " + message)


def dot(x, y):
    return sum((a * b for a, b in zip(x, y)), F(0))


def orient(v):
    v = tuple(v)
    first = next(x for x in v if x)
    return tuple(-x for x in v) if first < 0 else v


def e8_root_lines():
    """Recreate the canonical E8 line order used by pinned ade.E8()."""
    rows = []
    for i in range(8):
        for j in range(i + 1, 8):
            for sign in (1, -1):
                row = [F(0)] * 8
                row[i], row[j] = F(1), F(sign)
                rows.append(orient(row))
    for signs in product((1, -1), repeat=8):
        if signs.count(-1) % 2 == 0:
            rows.append(orient(F(s, 2) for s in signs))
    out, seen = [], set()
    for row in rows:
        if row not in seen:
            seen.add(row)
            out.append(row)
    return out


def qrank(matrix):
    a = [list(map(F, row)) for row in matrix]
    n = len(a)
    m = len(a[0]) if n else 0
    r = 0
    for c in range(m):
        pivot = next((i for i in range(r, n) if a[i][c]), None)
        if pivot is None:
            continue
        a[r], a[pivot] = a[pivot], a[r]
        scale = a[r][c]
        a[r] = [z / scale for z in a[r]]
        for i in range(n):
            if i != r and a[i][c]:
                scale = a[i][c]
                a[i] = [u - scale * v for u, v in zip(a[i], a[r])]
        r += 1
    return r


def solve_square(matrix, rhs):
    a = [list(map(F, row)) + [F(b)] for row, b in zip(matrix, rhs)]
    n = len(rhs)
    for c in range(n):
        pivot = next((i for i in range(c, n) if a[i][c]), None)
        if pivot is None:
            raise ValueError("singular matrix")
        a[c], a[pivot] = a[pivot], a[c]
        scale = a[c][c]
        a[c] = [z / scale for z in a[c]]
        for i in range(n):
            if i != c and a[i][c]:
                scale = a[i][c]
                a[i] = [u - scale * v for u, v in zip(a[i], a[c])]
    return [a[i][-1] for i in range(n)]


def f2rank_masks(rows):
    pivots = {}
    for row in rows:
        while row:
            bit = row.bit_length() - 1
            if bit in pivots:
                row ^= pivots[bit]
            else:
                pivots[bit] = row
                break
    return len(pivots)


def projective(vector):
    vector = tuple(map(F, vector))
    first = next(x for x in vector if x)
    return tuple(x / first for x in vector)


def encode_q(x):
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


def encode_matrix(matrix):
    return [[encode_q(x) for x in row] for row in matrix]


def e6_geometry():
    roots8 = e8_root_lines()
    require(len(roots8) == 120, "E8 line reconstruction count")
    r1 = roots8[0]
    r2 = next(row for row in roots8 if dot(row, r1) in (F(1), F(-1)))
    roots = [row for row in roots8 if dot(row, r1) == 0 and dot(row, r2) == 0]
    require(len(roots) == 36, "E6 root-line count")

    basis, basis_indices = [], []
    for index, row in enumerate(roots):
        if qrank(basis + [row]) > len(basis):
            basis.append(row)
            basis_indices.append(index)
        if len(basis) == 6:
            break
    require(len(basis) == 6, "E6 rational rank")

    columns = next(
        cols for cols in combinations(range(8), 6)
        if qrank([[row[c] for c in cols] for row in basis]) == 6
    )
    minor = [[basis[i][c] for c in columns] for i in range(6)]
    minor_t = [list(row) for row in zip(*minor)]
    coords = [solve_square(minor_t, [row[c] for c in columns]) for row in roots]
    for row, x in zip(roots, coords):
        require(tuple(sum((x[i] * basis[i][j] for i in range(6)), F(0)) for j in range(8)) == row,
                "basis coordinates reconstruct ambient E6 root")

    h = [[dot(basis[i], basis[j]) for j in range(6)] for i in range(6)]
    gram = [[sum((coords[t][i] * h[i][j] * coords[s][j]
                  for i in range(6) for j in range(6)), F(0))
             for s in range(36)] for t in range(36)]
    ambient_gram = [[dot(roots[t], roots[s]) for s in range(36)] for t in range(36)]
    require(gram == ambient_gram, "coordinate Gram equals ambient Gram")
    require(all(gram[t][t] == 2 for t in range(36)), "root norm two")

    b0 = [[int((1 + gram[t][s]) % 2) for s in range(36)] for t in range(36)]
    require(all(b0[t][s] == int(t == s or gram[t][s] == 0)
                for t in range(36) for s in range(36)), "dense E6 pairing definition")
    require(all(b0[t][s] == b0[s][t] for t in range(36) for s in range(36)), "pairing symmetry")

    serial_roots = [[encode_q(x) for x in row] for row in roots]
    root_digest = hashlib.sha256(json.dumps(serial_roots, separators=(",", ":")).encode()).hexdigest()
    return roots, coords, h, gram, b0, basis_indices, list(columns), root_digest


def admissible(pairing, gram):
    v = len(gram)
    return (all(pairing[t][t] == 1 for t in range(v))
            and all(pairing[t][s] == pairing[s][t] for t in range(v) for s in range(v))
            and all(not pairing[t][s] or t == s or gram[t][s] == 0
                    for t in range(v) for s in range(v)))


def support(vector):
    return [i for i, value in enumerate(vector) if value]


def block_rank(pairing, row_support, col_support):
    masks = []
    for t in row_support:
        mask = 0
        for j, s in enumerate(col_support):
            if pairing[t][s]:
                mask |= 1 << j
        masks.append(mask)
    return f2rank_masks(masks)


def factor_columns(coords, h, a, lam, corrupt=None):
    """Return the seven Q^36 factor columns; corrupt is a negative control."""
    ps = [[coords[t][i] for t in range(36)] for i in range(6)]
    pa = [sum((coords[t][k] * a[k] for k in range(6)), F(0)) for t in range(36)]
    ps.append(pa)
    qs = []
    for i in range(6):
        coeff = [h[k][i] - lam * a[i] * a[k] for k in range(6)]
        qs.append([sum((coords[t][k] * coeff[k] for k in range(6)), F(0)) for t in range(36)])
    qs.append([lam * z for z in pa])
    if corrupt == "wrong-sign-last":
        qs[6] = [-z for z in qs[6]]
    elif corrupt == "omit-last":
        qs[6] = [F(0)] * 36
    return ps, qs


def reconstructs_gram(ps, qs, gram):
    return all(sum((ps[j][t] * qs[j][s] for j in range(7)), F(0)) == gram[t][s]
               for t in range(36) for s in range(36))


def cost_at(coords, h, pairing, a, lam):
    ps, qs = factor_columns(coords, h, a, lam)
    ranks = [block_rank(pairing, support(p), support(q)) for p, q in zip(ps, qs)]
    active = [bool(p) and bool(q) for p, q in zip(ps, qs)]
    require(all(active), "each enumerated point is a genuine seven-total decoder")
    return ranks, sum(ranks), sum(max(5, r) for r in ranks)


def lambda_cells(coords, h, a):
    cuts = {F(0)}
    for i in range(6):
        for t in range(36):
            intercept = sum((coords[t][k] * h[k][i] for k in range(6)), F(0))
            slope = a[i] * sum((coords[t][k] * a[k] for k in range(6)), F(0))
            if slope:
                breakpoint = intercept / slope
                if breakpoint:
                    cuts.add(breakpoint)
    ordered = sorted(cuts)
    samples = {point for point in ordered if point}
    samples.update((left + right) / 2 for left, right in zip(ordered, ordered[1:]))
    samples.add(ordered[0] - 1)
    samples.add(ordered[-1] + 1)
    require(F(0) not in samples, "zero lambda excluded")
    require(len(samples) == 2 * len(ordered), "complete point-and-interval representative count")
    return sorted(samples), len(ordered) - 1


def scan(coords, h, pairing, directions):
    rows = []
    cells_per_direction = []
    breakpoint_counts = []
    for direction_index, a in enumerate(directions):
        samples, nonzero_breakpoints = lambda_cells(coords, h, a)
        cells_per_direction.append(len(samples))
        breakpoint_counts.append(nonzero_breakpoints)
        for lam in samples:
            ranks, raw, charged = cost_at(coords, h, pairing, a, lam)
            rows.append((charged, raw, direction_index, lam, ranks))
    return rows, cells_per_direction, breakpoint_counts


def summarize_hist(rows, column):
    hist = {}
    for row in rows:
        key = row[column]
        hist[key] = hist.get(key, 0) + 1
    return {str(k): hist[k] for k in sorted(hist)}


def build_certificate():
    roots, coords, h, gram, b0, basis_indices, columns, root_digest = e6_geometry()
    require(admissible(b0, gram), "B0 admissibility")
    b0_rank = f2rank_masks([sum((b0[t][s] << s for s in range(36)), 0) for t in range(36)])

    # Positive controls: the six-term square decoder and two one-extra exact identities.
    square_ps = [[coords[t][i] for t in range(36)] for i in range(6)]
    square_qs = [[sum((coords[t][k] * h[k][i] for k in range(6)), F(0))
                  for t in range(36)] for i in range(6)]
    square_ranks = [block_rank(b0, support(p), support(q)) for p, q in zip(square_ps, square_qs)]
    require(all(sum((square_ps[j][t] * square_qs[j][s] for j in range(6)), F(0)) == gram[t][s]
                for t in range(36) for s in range(36)), "six-term Gram decoder identity")
    require(square_ranks == [6, 7, 6, 6, 6, 6], "six-term reference ranks")

    roots_directions = sorted({projective(a) for a in coords})
    ternary_directions = sorted({projective(v) for v in product((F(-1), F(0), F(1)), repeat=6) if any(v)})
    directions = sorted(set(roots_directions) | set(ternary_directions))
    require(len(roots_directions) == 36, "root-direction count")
    require(len(ternary_directions) == 364, "projective ternary count")
    require(len(directions) == 365, "union direction count")

    # Exact positive identity fixtures, plus controls for both cancellation signs and omission.
    a_root = roots_directions[0]
    a_ternary = directions[92]
    require(reconstructs_gram(*factor_columns(coords, h, a_root, F(1)), gram),
            "root-direction one-extra identity positive control")
    require(reconstructs_gram(*factor_columns(coords, h, a_ternary, F(1)), gram),
            "ternary one-extra identity positive control")
    require(not reconstructs_gram(*factor_columns(coords, h, a_ternary, F(1), "wrong-sign-last"), gram),
            "wrong-sign cancellation negative control")
    require(not reconstructs_gram(*factor_columns(coords, h, a_ternary, F(1), "omit-last"), gram),
            "omitted extra term negative control")

    # The initial root-only search is retained as a comparison for the one bounded pivot.
    root_rows, root_cell_counts, _ = scan(coords, h, b0, roots_directions)
    all_rows, cell_counts, breakpoint_counts = scan(coords, h, b0, directions)
    root_min = min(root_rows)
    best = min(all_rows)
    min_raw = min(row[1] for row in all_rows)
    charged_hist = summarize_hist(all_rows, 0)
    raw_hist = summarize_hist(all_rows, 1)
    minimizers = [row for row in all_rows if row[0] == best[0]]
    require(root_min[0] == 42 and root_min[1] == 42, "root-only pilot result")
    require(sum(root_cell_counts) == 566, "root-only support-cell coverage")
    require(sum(cell_counts) == 4672, "full support-cell coverage")
    require(min_raw == 40 and best[0] == 40, "minimum raw and charged costs")
    require(all(row[0] == row[1] for row in all_rows), "all seven block ranks meet the per-total floor")
    require(charged_hist == {"40": 6, "41": 6, "42": 12, "43": 143, "44": 4505},
            "charged-cost histogram")
    require(not any(row[0] <= 35 for row in all_rows), "no fully charged cost-35 witness")
    require(not any(row[1] <= 35 for row in all_rows), "no raw cost-35 witness")

    # A deliberate pairing corruption must violate the forced-zero condition.
    nonorthogonal = next((t, s) for t in range(36) for s in range(t + 1, 36) if gram[t][s])
    corrupt = [row[:] for row in b0]
    t, s = nonorthogonal
    corrupt[t][s] = corrupt[s][t] = 1
    require(not admissible(corrupt, gram), "nonorthogonal-edge negative control")

    # Map sorted direction tuples to readable exact vectors in the certificate.
    def encode_row(row):
        return [encode_q(x) for x in row]
    encoded_minimizers = [
        {"direction_index": row[2], "a": encode_row(directions[row[2]]),
         "lambda": encode_q(row[3]), "ranks": row[4], "raw": row[1], "charged": row[0]}
        for row in minimizers
    ]
    certificate = {
        "schema_version": 1,
        "status": "scoped-negative-result",
        "base_commit": "0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2",
        "selected_record_sha256": "10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32",
        "assignment_seed": "4dd9ff38bfc63aa200c17c947da92d9e",
        "task_id": "complex-rank-shape-decoder",
        "priority_revision": 4,
        "root_input": {
            "source": "research/root-unit-decoder-lemmas/lib/ade.py:E6b/E8 line order",
            "root_lines": 36,
            "canonical_root_sha256": root_digest,
            "basis_root_indices": basis_indices,
            "ambient_basis_columns": columns,
            "basis_gram": encode_matrix(h),
            "pairing_B0_rank_F2": b0_rank,
        },
        "model": {
            "terms": 7,
            "pairing": "B0_tt=1; off-diagonal B0_ts=1 iff Gram G_ts=0",
            "per_term_floor_w": 5,
            "fully_charged_cost": "sum(max(5, rank_F2(B0[R_j,A_j])))",
            "raw_cost": "sum(rank_F2(B0[R_j,A_j]))",
            "identity": "G = sum_{i=1}^6 X e_i (X(H e_i-lambda a_i a))^T + (Xa)(lambda Xa)^T",
        },
        "positive_controls": {
            "six_term_reference_ranks": square_ranks,
            "six_term_reference_raw_and_charged_cost": sum(square_ranks),
            "one_extra_exact_identity_fixtures": 2,
        },
        "negative_controls": [
            "wrong sign on the seventh correction fails exact Gram identity",
            "omitting the seventh term fails exact Gram identity",
            "turning on a B0 edge between nonorthogonal roots fails admissibility",
        ],
        "initial_root_direction_slice": {
            "directions": len(roots_directions),
            "support_cells": sum(root_cell_counts),
            "minimum_raw": min(row[1] for row in root_rows),
            "minimum_charged": min(row[0] for row in root_rows),
        },
        "bounded_domain": {
            "root_directions": len(roots_directions),
            "projective_ternary_directions": len(ternary_directions),
            "unique_union_directions": len(directions),
            "lambda_domain": "all nonzero rational lambda; exact nonzero breakpoints and one rational representative per open interval",
            "support_cells": len(all_rows),
            "all_support_cells_have_seven_active_terms": True,
            "min_cells_per_direction": min(cell_counts),
            "max_cells_per_direction": max(cell_counts),
            "sum_distinct_nonzero_breakpoints": sum(breakpoint_counts),
        },
        "result": {
            "minimum_raw_cost": min_raw,
            "minimum_fully_charged_cost": best[0],
            "charged_cost_histogram": charged_hist,
            "raw_cost_histogram": raw_hist,
            "no_raw_or_charged_cost_at_most_35": True,
            "minimum_witnesses": encoded_minimizers,
        },
        "limits": [
            "Only the rank-one redundant extension of this pinned six-term Gram factorization is searched.",
            "The direction set is the union of the 36 E6 root lines and all projective {-1,0,1}^6 directions in the pinned basis.",
            "No claim is made about arbitrary rational directions, arbitrary seven-term decoders, sparse pairings, or other decoder identities.",
            "No source/copy/frame/hosting/restoration/precision/interface supplier mapping or kappa improvement is established.",
        ],
    }
    return certificate


def main():
    certificate = build_certificate()
    path = HERE / "CERTIFICATE.json"
    if sys.argv[1:] == ["--emit"]:
        path.write_text(json.dumps(certificate, indent=2) + "\n")
        print("WROTE_CERTIFICATE", path)
    elif sys.argv[1:]:
        raise SystemExit("usage: verify.py [--emit]")
    else:
        require(path.exists(), "CERTIFICATE.json is missing")
        expected = json.loads(path.read_text())
        require(certificate == expected, "computed result differs from CERTIFICATE.json")
        result = certificate["result"]
        domain = certificate["bounded_domain"]
        print("PASS_E6_ONE_EXTRA_FRAME",
              f"directions={domain['unique_union_directions']}",
              f"support_cells={domain['support_cells']}",
              f"min_raw={result['minimum_raw_cost']}",
              f"min_charged={result['minimum_fully_charged_cost']}",
              "target=35", "scoped_negative_result")


if __name__ == "__main__":
    main()
