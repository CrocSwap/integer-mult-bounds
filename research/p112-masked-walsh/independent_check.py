#!/usr/bin/env python3
"""Independent exact replay of the P112 masked-Walsh two-total census.

This file deliberately has no imports from the accompanying proof or geometry
code. It consumes only GEOMETRY.json and, when present, compares its summary
with RESULT.json.
"""

from collections import Counter
from itertools import combinations, product
import hashlib
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
N = 112


def need(ok, message):
    if not ok:
        raise ValueError(message)


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def parity(x):
    return x.bit_count() & 1


def as_int_rows(data, key, aliases=()):
    value = None
    for name in (key, *aliases):
        if name in data:
            value = data[name]
            break
    need(value is not None, f"geometry missing {key}")
    return [[int(x) for x in row] for row in value]


def matrix_rank(rows):
    """GF(2) rank of packed integer rows, by independent pivot elimination."""
    pivots = {}
    for value in rows:
        while value:
            pivot = value.bit_length() - 1
            previous = pivots.get(pivot)
            if previous is None:
                pivots[pivot] = value
                break
            value ^= previous
    return len(pivots)


def rank_self_checks():
    need(matrix_rank([0b01, 0b10, 0b11]) == 2, "rank test: independent pair")
    need(matrix_rank([0b101, 0b011, 0b110]) == 2, "rank test: dependent rows")
    need(matrix_rank([0, 0, 0]) == 0, "rank test: zero matrix")
    need(matrix_rank([0b111]) == 1, "rank test: one row")


def load_geometry(path):
    data = json.loads(path.read_text())
    roots = as_int_rows(data, "roots")
    frame = as_int_rows(data, "frame")
    raw_labels = data.get("labels")
    raw_duals = data.get("duals")
    need(raw_labels is not None and raw_duals is not None,
         "geometry missing labels or duals")
    if raw_labels and isinstance(raw_labels[0], int):
        label_masks = [int(v) for v in raw_labels]
        labels = [[(v >> (8-k)) & 1 for k in range(9)] for v in label_masks]
    else:
        labels = [[int(x) for x in row] for row in raw_labels]
        label_masks = [sum((v & 1) << (8-k) for k, v in enumerate(row))
                       for row in labels]
    if raw_duals and isinstance(raw_duals[0], int):
        dual_masks = [int(v) for v in raw_duals]
        duals = [[(v >> (8-k)) & 1 for k in range(9)] for v in dual_masks]
    else:
        duals = [[int(x) for x in row] for row in raw_duals]
        dual_masks = [sum((v & 1) << (8-k) for k, v in enumerate(row))
                      for row in duals]
    x = as_int_rows(data, "X", ("x",))
    need(len(roots) == len(labels) == len(duals) == len(x) == N,
         "geometry row count must be 112")
    need(len(frame) == 8 and all(len(r) == 8 for r in frame),
         "frame must contain eight 8-coordinate roots")
    need(all(len(r) == 8 for r in roots), "roots must have eight coordinates")
    need(all(len(r) == 9 for r in labels + duals), "labels/duals must be 9-bit rows")
    need(all(len(r) == 8 for r in x), "X must have eight columns")

    # Independent binding of X and the binary pairing to the supplied roots.
    need(all(dot(r, r) == 8 for r in roots), "scaled root norm is not 8")
    need(all(dot(f, f) == 8 for f in frame), "scaled frame-root norm is not 8")
    need(all(set(row) <= {-1, 0, 1} for row in x), "X has entries outside {-1,0,1}")
    for i, root in enumerate(roots):
        for j, f in enumerate(frame):
            need(dot(root, f) == 4 * x[i][j], f"X/root-frame mismatch at ({i},{j})")

    # For scaled-by-2 E8 roots, G_ij=<r_i,r_j>/4 and XX^T=2G.
    gram = [[dot(roots[i], roots[j]) // 4 for j in range(N)] for i in range(N)]
    for i in range(N):
        for j in range(N):
            ip = dot(roots[i], roots[j])
            need(ip % 4 == 0, f"nonintegral E8 Gram entry at ({i},{j})")
            need(dot(x[i], x[j]) == ip // 2,
                 f"XX^T != 2G at ({i},{j})")

    # Pairing stored as dual_i = label_i S. This checks all 112^2 entries
    # against the independently reconstructed Gram matrix.
    for i in range(N):
        need(len(duals[i]) == 9, "bad dual label width")
        for j in range(N):
            actual = parity(dual_masks[i] & label_masks[j])
            expected = (1 + gram[i][j]) & 1
            need(actual == expected, f"binary label pairing mismatch at ({i},{j})")

    xcols = [[x[i][j] for i in range(N)] for j in range(8)]
    return roots, frame, labels, duals, x, label_masks, dual_masks, xcols


def run_census(geometry):
    roots, frame, labels, duals, x, label_masks, dual_masks, xcols = geometry

    # Direct pairing table, independent of any packed-matrix helper in the
    # source package. Rows encode L_i S L_j^T in port order.
    pairing_rows = []
    for i in range(N):
        row = 0
        for j in range(N):
            row |= parity(dual_masks[i] & label_masks[j]) << j
        pairing_rows.append(row)

    beta_cache = {}
    projected_source_cache = {}

    def beta(reader_support, source_support):
        key = (reader_support, source_support)
        found = beta_cache.get(key)
        if found is not None:
            return found
        projected = projected_source_cache.get(source_support)
        if projected is None:
            sources = [j for j in range(N) if (source_support >> j) & 1]
            projected = []
            for i in range(N):
                packed = 0
                for k, j in enumerate(sources):
                    packed |= ((pairing_rows[i] >> j) & 1) << k
                projected.append(packed)
            projected_source_cache[source_support] = projected
        rows = []
        readers = reader_support
        while readers:
            bit = readers & -readers
            i = bit.bit_length() - 1
            rows.append(projected[i])
            readers ^= bit
        value = matrix_rank(rows)
        beta_cache[key] = value
        return value

    col_support = []
    for col in xcols:
        col_support.append(sum((v != 0) << i for i, v in enumerate(col)))

    small_pairs = list(product((-1, 0, 1), repeat=2))

    def support(values):
        return sum((value != 0) << i for i, value in enumerate(values))

    matrices = []
    for ap, bp, aq, bq in product((-1, 0, 1), repeat=4):
        if ap * bq - bp * aq in (-1, 1):
            matrices.append((ap, bp, aq, bq))
    need(len(matrices) == 40, f"expected 40 unimodular matrices, got {len(matrices)}")

    total_hist = Counter()
    per_pair = []
    minima = []
    max_identity_checked = 0
    expected_count = 0

    for p, q in combinations(range(8), 2):
        hist = Counter()
        min_cost = 10**9
        max_cost = -1
        min_cases = []
        xp, xq = xcols[p], xcols[q]
        xps, xqs = col_support[p], col_support[q]
        d_support = {uv: support([uv[0]*xp[i] + uv[1]*xq[i] for i in range(N)])
                     for uv in small_pairs}

        for h in range(1, 512):
            z = [((xp[i] + xq[i]) if parity(h & label_masks[i]) == 0 else 0)
                 for i in range(N)]
            w = [((xp[i] - xq[i]) if parity(h & label_masks[i]) == 1 else 0)
                 for i in range(N)]
            zs, ws = support(z), support(w)
            rp_support = {uv: support([2*xp[i] - uv[0]*z[i] - uv[1]*w[i]
                                       for i in range(N)]) for uv in small_pairs}
            rq_support = {uv: support([2*xq[i] - uv[0]*z[i] - uv[1]*w[i]
                                       for i in range(N)]) for uv in small_pairs}

            for ap, bp, aq, bq in matrices:
                cost = (48 + beta(xps, rp_support[(ap, bp)])
                        + beta(xqs, rq_support[(aq, bq)])
                        + beta(d_support[(ap, aq)], zs)
                        + beta(d_support[(bp, bq)], ws))
                hist[cost] += 1
                total_hist[cost] += 1
                expected_count += 1
                if cost < min_cost:
                    min_cost, min_cases = cost, []
                if cost == min_cost and len(min_cases) < 4:
                    min_cases.append((h, (ap, bp, aq, bq)))
                max_cost = max(max_cost, cost)

        need(sum(hist.values()) == 511 * 40, f"wrong count for pair {(p,q)}")
        # Independently multiply the full matrix identity for one actual
        # minimizer per coordinate pair, after the support-only census.
        h0, a0 = min_cases[0]
        ap, bp, aq, bq = a0
        z0 = [((xp[i] + xq[i]) if parity(h0 & label_masks[i]) == 0 else 0)
              for i in range(N)]
        w0 = [((xp[i] - xq[i]) if parity(h0 & label_masks[i]) == 1 else 0)
              for i in range(N)]
        rp0 = [2*xp[i] - ap*z0[i] - bp*w0[i] for i in range(N)]
        rq0 = [2*xq[i] - aq*z0[i] - bq*w0[i] for i in range(N)]
        d10 = [ap*xp[i] + aq*xq[i] for i in range(N)]
        d20 = [bp*xp[i] + bq*xq[i] for i in range(N)]
        for i in range(N):
            for j in range(N):
                lhs2 = 2 * sum(x[i][k] * x[j][k] for k in range(8))
                rhs2 = sum(2*xcols[k][i]*xcols[k][j]
                           for k in range(8) if k not in (p, q))
                rhs2 += xp[i]*rp0[j] + xq[i]*rq0[j]
                rhs2 += d10[i]*z0[j] + d20[i]*w0[j]
                need(rhs2 == lhs2,
                     f"exact identity failed for pair {(p,q)}, h={h0}, A={a0}")
        max_identity_checked += 1

        per_pair.append({"pair": [p, q], "histogram": dict(sorted(hist.items())),
                         "minimum": min_cost, "maximum": max_cost})
        minima.append((min_cost, p, q, min_cases))

    need(expected_count == 28 * 511 * 40 == 572320,
         f"wrong total candidate count: {expected_count}")
    result = {"global_histogram": dict(sorted(total_hist.items())),
              "per_pair": per_pair, "count": expected_count,
              "minimum": min(total_hist), "maximum": max(total_hist),
              "minimizers": [{"pair": [p, q], "h": h, "A": list(a)}
                             for value, p, q, cases in minima if value == min(total_hist)
                             for h, a in cases],
              "beta_cache_entries": len(beta_cache),
              "endpoint_identity_checks": max_identity_checked}

    # Relax coefficients to all reals. For fixed cut, a residual coordinate
    # can vanish only when its active scalar is in {-2,-1,0,1,2}; every other
    # real value has the same support as the representative 3. Thus six
    # representatives per active coefficient give the exact minimum of each
    # original residual beta term. A nonzero real combination of xp,xq has
    # only five support types, represented by the listed coefficient pairs.
    # Minimize these four terms independently, which is optimistic because it
    # ignores that one coefficient matrix must realize all four choices.
    residual_coefficients = (-2, -1, 0, 1, 2, 3)
    reader_types = ((1, 0), (0, 1), (1, 1), (1, -1), (1, 3))
    relaxation_hist = Counter()
    relaxation_nonzero_min = 10**9
    for p, q in combinations(range(8), 2):
        xp, xq = xcols[p], xcols[q]
        xps, xqs = col_support[p], col_support[q]
        reader_supports = [support([u*xp[i] + v*xq[i] for i in range(N)])
                            for u, v in reader_types]
        for h in range(1, 512):
            z = [((xp[i] + xq[i]) if parity(h & label_masks[i]) == 0 else 0)
                 for i in range(N)]
            w = [((xp[i] - xq[i]) if parity(h & label_masks[i]) == 1 else 0)
                 for i in range(N)]
            zs, ws = support(z), support(w)
            best_p = min(beta(xps, support([2*xp[i] - a*z[i] - b*w[i]
                                            for i in range(N)]))
                         for a in residual_coefficients
                         for b in residual_coefficients)
            best_q = min(beta(xqs, support([2*xq[i] - a*z[i] - b*w[i]
                                            for i in range(N)]))
                         for a in residual_coefficients
                         for b in residual_coefficients)
            best_z = min(beta(ds, zs) for ds in reader_supports)
            best_w = min(beta(ds, ws) for ds in reader_supports)
            lower = 48 + best_p + best_q + best_z + best_w
            relaxation_hist[lower] += 1
            if zs and ws:
                relaxation_nonzero_min = min(relaxation_nonzero_min, lower)
    need(sum(relaxation_hist.values()) == 28 * 511,
         "wrong all-real relaxation cut count")
    need(relaxation_nonzero_min < 10**9,
         "no cuts with both Walsh sources nonzero")
    result["relaxation"] = {
        "histogram": dict(sorted(relaxation_hist.items())),
        "minimum": min(relaxation_hist),
        "nonzero_sources_minimum": relaxation_nonzero_min,
        "cut_pairs": sum(relaxation_hist.values()),
        "critical_coefficients": [-2, -1, 0, 1, 2],
        "generic_representative": 3,
    }
    return result


def normalize_hist(hist):
    return {str(k): int(v) for k, v in sorted(hist.items(), key=lambda kv: int(kv[0]))}


def compare_parent(result, path):
    parent = json.loads(path.read_text())
    parent_hist = parent.get("global_histogram", parent.get("histogram"))
    need(parent_hist is not None, "RESULT.json missing global_histogram/histogram")
    need(normalize_hist(parent_hist) == normalize_hist(result["global_histogram"]),
         "global histogram differs from RESULT.json")
    for parent_key, own_key in (("cases", "count"), ("minimum", "minimum"),
                                ("maximum", "maximum")):
        need(parent[parent_key] == result[own_key], f"summary field differs: {parent_key}")
    parent_pairs = parent.get("per_pair")
    need(parent_pairs is not None, "RESULT.json missing per_pair")
    need(len(parent_pairs) == 28 and len({tuple(row["pair"]) for row in parent_pairs}) == 28,
         "missing or duplicated pair receipts")
    mine = {(tuple(row["pair"]), row["minimum"], row.get("maximum"),
             tuple(normalize_hist(row["histogram"]).items()))
            for row in result["per_pair"]}
    theirs = {(tuple(row["pair"]), row["minimum"], row.get("maximum"),
                tuple(normalize_hist(row["histogram"]).items()))
               for row in parent_pairs}
    need(mine == theirs, "per-pair census differs from RESULT.json")
    print("RESULT.json comparison: global histogram and per-pair histograms/min/max match")
    need("relaxation" in parent, "missing all-real relaxation receipt")
    if "relaxation" in parent:
        expected_relax = parent["relaxation"]
        actual_relax = result["relaxation"]
        need(normalize_hist(expected_relax["histogram"]) ==
             normalize_hist(actual_relax["histogram"]),
             "all-real relaxation histogram differs from RESULT.json")
        for key in ("minimum", "nonzero_sources_minimum", "cut_pairs",
                    "critical_coefficients", "generic_representative"):
            need(expected_relax[key] == actual_relax[key],
                 f"all-real relaxation field differs: {key}")
        print("RESULT.json comparison: all-real relaxation fields match")


def main():
    rank_self_checks()
    geometry_path = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "GEOMETRY.json"
    result_path = Path(sys.argv[2]) if len(sys.argv) > 2 else HERE / "RESULT.json"
    geometry = load_geometry(geometry_path)
    print(f"Geometry verified: {geometry_path}")
    result = run_census(geometry)
    encoded = json.dumps(result["global_histogram"], sort_keys=True).encode()
    print(f"Candidates: {result['count']}")
    print(f"Cost range: {result['minimum']}..{result['maximum']}")
    print(f"Global histogram: {json.dumps(result['global_histogram'], sort_keys=True)}")
    print(f"Histogram SHA256: {hashlib.sha256(encoded).hexdigest()}")
    print(f"Beta cache entries: {result['beta_cache_entries']}")
    print(f"Exact identity checks at running minima: {result['endpoint_identity_checks']}")
    print(f"Global minimum witnesses (first 4): {json.dumps(result['minimizers'][:4], sort_keys=True)}")
    print(f"All-real relaxation: {json.dumps(result['relaxation'], sort_keys=True)}")
    compare_parent(result, result_path)
    print("PASS_P112_MASKED_WALSH_INDEPENDENT")


if __name__ == "__main__":
    main()
