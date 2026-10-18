#!/usr/bin/env python3
"""Exact bounded census of E6 Gram decoders under elementary basis shears."""
from fractions import Fraction as F
from functools import lru_cache
from itertools import combinations, product
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
TARGET = 35


def require(ok, message):
    if not ok:
        raise SystemExit("FAIL_E6_SHEARED_FRAME: " + message)


def dot(x, y):
    return sum((u * v for u, v in zip(x, y)), F(0))


def transpose(a):
    return [list(row) for row in zip(*a)]


def mul(a, b):
    return [[sum((a[i][k] * b[k][j] for k in range(len(b))), F(0))
             for j in range(len(b[0]))] for i in range(len(a))]


def identity(n):
    return [[F(int(i == j)) for j in range(n)] for i in range(n)]


def orient(v):
    v = tuple(v)
    return tuple(-z for z in v) if next(z for z in v if z) < 0 else v


def roots_e8():
    """Exact canonical E8 line list, matching the pinned ADE source ordering."""
    rows = []
    for i in range(8):
        for j in range(i + 1, 8):
            for s in (1, -1):
                v = [F(0)] * 8
                v[i], v[j] = F(1), F(s)
                rows.append(orient(v))
    for signs in product((1, -1), repeat=8):
        if signs.count(-1) % 2 == 0:
            rows.append(orient(F(s, 2) for s in signs))
    seen, out = set(), []
    for row in rows:
        if row not in seen:
            seen.add(row)
            out.append(row)
    return out


def rank_q(a):
    a = [list(map(F, row)) for row in a]
    nr, nc, r = len(a), (len(a[0]) if a else 0), 0
    for c in range(nc):
        pivot = next((i for i in range(r, nr) if a[i][c]), None)
        if pivot is None:
            continue
        a[r], a[pivot] = a[pivot], a[r]
        d = a[r][c]
        a[r] = [x / d for x in a[r]]
        for i in range(nr):
            if i != r and a[i][c]:
                d = a[i][c]
                a[i] = [x - d * y for x, y in zip(a[i], a[r])]
        r += 1
    return r


def solve(a, b):
    n = len(b)
    z = [list(map(F, row)) + [F(rhs)] for row, rhs in zip(a, b)]
    for c in range(n):
        pivot = next((i for i in range(c, n) if z[i][c]), None)
        if pivot is None:
            raise ValueError("singular minor")
        z[c], z[pivot] = z[pivot], z[c]
        d = z[c][c]
        z[c] = [x / d for x in z[c]]
        for i in range(n):
            if i != c and z[i][c]:
                d = z[i][c]
                z[i] = [x - d * y for x, y in zip(z[i], z[c])]
    return [z[i][-1] for i in range(n)]


def inverse(a):
    n = len(a)
    z = [list(map(F, row)) + [F(int(i == j)) for j in range(n)]
         for i, row in enumerate(a)]
    for c in range(n):
        pivot = next((i for i in range(c, n) if z[i][c]), None)
        if pivot is None:
            raise ValueError("singular frame map")
        z[c], z[pivot] = z[pivot], z[c]
        d = z[c][c]
        z[c] = [x / d for x in z[c]]
        for i in range(n):
            if i != c and z[i][c]:
                d = z[i][c]
                z[i] = [x - d * y for x, y in zip(z[i], z[c])]
    return [row[n:] for row in z]


def projective(v):
    v = tuple(map(F, v))
    first = next(x for x in v if x)
    return tuple(x / first for x in v)


def qstr(x):
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


def e6_data():
    e8 = roots_e8()
    require(len(e8) == 120, "canonical E8 roots")
    alpha = e8[0]
    beta = next(r for r in e8 if dot(r, alpha) in (F(1), F(-1)))
    roots = [r for r in e8 if dot(r, alpha) == 0 and dot(r, beta) == 0]
    require(len(roots) == 36, "E6 root lines")

    basis, basis_ids = [], []
    for i, r in enumerate(roots):
        if rank_q(basis + [r]) > len(basis):
            basis.append(r)
            basis_ids.append(i)
        if len(basis) == 6:
            break
    require(len(basis) == 6, "E6 rank six")
    cols = next(c for c in combinations(range(8), 6)
                if rank_q([[r[j] for j in c] for r in basis]) == 6)
    minor = [[basis[i][j] for j in cols] for i in range(6)]
    x = [solve(transpose(minor), [r[j] for j in cols]) for r in roots]
    require(all(tuple(sum((x[t][i] * basis[i][j] for i in range(6)), F(0))
                        for j in range(8)) == roots[t] for t in range(36)),
            "exact root coordinates")
    h = [[dot(basis[i], basis[j]) for j in range(6)] for i in range(6)]
    g = mul(mul(x, h), transpose(x))
    require(g == [[dot(u, v) for v in roots] for u in roots], "Gram reconstruction")
    require(all(g[i][i] == 2 for i in range(36)), "root norms")
    b0 = [[int((1 + g[i][j]) % 2) for j in range(36)] for i in range(36)]
    require(all(b0[i][j] == int(i == j or g[i][j] == 0)
                for i in range(36) for j in range(36)), "B0 definition")
    root_payload = [[qstr(z) for z in row] for row in roots]
    digest = hashlib.sha256(json.dumps(root_payload, separators=(",", ":")).encode()).hexdigest()
    return roots, x, h, g, b0, basis_ids, list(cols), digest


def directions(x):
    root = {projective(row) for row in x}
    ternary = {projective(v) for v in product((F(-1), F(0), F(1)), repeat=6) if any(v)}
    union = sorted(root | ternary)
    require(len(root) == 36 and len(ternary) == 364 and len(union) == 365,
            "root/ternary direction domains")
    return sorted(root), sorted(ternary), union


def shears():
    out = []
    for i in range(6):
        for j in range(6):
            if i == j:
                continue
            for eps in (-1, 1):
                a = identity(6)
                a[i][j] = F(eps)
                out.append({"i": i, "j": j, "epsilon": eps, "A": a})
    require(len(out) == 60, "signed elementary transvection count")
    return out


def mask(v):
    return sum((1 << i) for i, z in enumerate(v) if z)


def masks_to_ids(value):
    return [i for i in range(36) if (value >> i) & 1]


def rank_masks(b0):
    @lru_cache(maxsize=100000)
    def get(row_mask, col_mask):
        cols = masks_to_ids(col_mask)
        pivots = {}
        for t in masks_to_ids(row_mask):
            bits = 0
            for j, s in enumerate(cols):
                if b0[t][s]:
                    bits |= 1 << j
            while bits:
                p = bits.bit_length() - 1
                if p in pivots:
                    bits ^= pivots[p]
                else:
                    pivots[p] = bits
                    break
        return len(pivots)
    return get


def factors(x, h, a, lam, amap, inva, bad=None):
    """Return the seven factor vectors for an arbitrary invertible 6x6 A."""
    c = [sum((inva[i][k] * a[k] for k in range(6)), F(0)) for i in range(6)]
    ka = mul(h, transpose(inva))
    pcols = mul(x, amap)
    qcols = mul(x, ka)
    xa = [sum((x[t][k] * a[k] for k in range(6)), F(0)) for t in range(36)]
    ps = [[pcols[t][j] for t in range(36)] for j in range(6)] + [xa]
    qs = [[qcols[t][j] - lam * c[j] * xa[t] for t in range(36)] for j in range(6)] + [[lam * z for z in xa]]
    if bad == "wrong-sign":
        qs[6] = [-z for z in qs[6]]
    elif bad == "omit-seventh":
        qs[6] = [F(0)] * 36
    return ps, qs


def identity_holds(ps, qs, g, terms=7):
    return all(sum((ps[j][t] * qs[j][s] for j in range(terms)), F(0)) == g[t][s]
               for t in range(36) for s in range(36))


def support_cells(x, h, a, amap, inva):
    c = [sum((inva[i][k] * a[k] for k in range(6)), F(0)) for i in range(6)]
    k = mul(h, transpose(inva))
    xa = [sum((x[t][z] * a[z] for z in range(6)), F(0)) for t in range(36)]
    intercepts = [[sum((x[t][z] * k[z][j] for z in range(6)), F(0))
                   for t in range(36)] for j in range(6)]
    cuts = {F(0)}
    for j in range(6):
        for t in range(36):
            slope = c[j] * xa[t]
            if slope:
                point = intercepts[j][t] / slope
                if point:
                    cuts.add(point)
    ordered = sorted(cuts)
    samples = {z for z in ordered if z}
    samples.update((u + v) / 2 for u, v in zip(ordered, ordered[1:]))
    samples.add(ordered[0] - 1)
    samples.add(ordered[-1] + 1)
    require(F(0) not in samples and len(samples) == 2 * len(ordered), "exact lambda cell representatives")
    return sorted(samples), len(ordered) - 1, intercepts, c, xa


def admissible(pairing, gram):
    return (all(pairing[i][i] == 1 for i in range(36))
            and all(pairing[i][j] == pairing[j][i] for i in range(36) for j in range(36))
            and all(not pairing[i][j] or i == j or gram[i][j] == 0
                    for i in range(36) for j in range(36)))


def search_matrix(x, h, g, b0, rank, directions_all, frame):
    a_map = frame["A"]
    inva = inverse(a_map)
    pcols = mul(x, a_map)
    p_masks_by_dir = []
    for a in directions_all:
        xa = [sum((x[t][k] * a[k] for k in range(6)), F(0)) for t in range(36)]
        p_masks_by_dir.append([mask([pcols[t][j] for t in range(36)]) for j in range(6)] + [mask(xa)])
    hist_raw, hist_charged, term_counts = {}, {}, {}
    cells_total = breakpoints_total = 0
    min_row = None
    min_raw = None
    target_witnesses = []
    target_count = 0
    degenerate = 0
    for ai, a in enumerate(directions_all):
        samples, nbreak, intercepts, c, xa = support_cells(x, h, a, a_map, inva)
        cells_total += len(samples)
        breakpoints_total += nbreak
        p_masks = p_masks_by_dir[ai]
        for lam in samples:
            col_masks = [mask([intercepts[j][t] - lam * c[j] * xa[t] for t in range(36)])
                         for j in range(6)] + [mask([lam * z for z in xa])]
            ranks = [rank(p_masks[j], col_masks[j]) for j in range(7)]
            active = sum(bool(p_masks[j]) and bool(col_masks[j]) for j in range(7))
            raw = sum(ranks)
            charged = sum(max(5, ranks[j]) for j in range(7)
                          if p_masks[j] and col_masks[j])
            hist_raw[raw] = hist_raw.get(raw, 0) + 1
            hist_charged[charged] = hist_charged.get(charged, 0) + 1
            term_counts[active] = term_counts.get(active, 0) + 1
            degenerate += (active < 7)
            row = {"charged": charged, "raw": raw, "direction_index": ai,
                   "a": [qstr(z) for z in a], "lambda": qstr(lam),
                   "active_totals": active, "ranks": ranks}
            if min_row is None or (charged, raw, ai, lam) < (min_row["charged"], min_row["raw"], min_row["direction_index"], F(min_row["lambda"])):
                min_row = row
            if min_raw is None or raw < min_raw["raw"]:
                min_raw = row
            if charged <= TARGET and active == 7 and len(target_witnesses) < 20:
                target_witnesses.append(row)
            if charged <= TARGET and active == 7:
                target_count += 1
    return {
        "transvection": {**{k: frame[k] for k in ("i", "j", "epsilon")},
                         "matrix": [[qstr(z) for z in row] for row in frame["A"]]},
        "cells": cells_total,
        "distinct_nonzero_breakpoints": breakpoints_total,
        "minimum_raw": min_raw,
        "minimum_charged": min_row,
        "raw_histogram": {str(k): hist_raw[k] for k in sorted(hist_raw)},
        "charged_histogram": {str(k): hist_charged[k] for k in sorted(hist_charged)},
        "active_total_histogram": {str(k): term_counts[k] for k in sorted(term_counts)},
        "degenerate_cells": degenerate,
        "seven_total_cost_le_35_count": target_count,
        "target_witnesses_first20": target_witnesses,
    }


def check_controls(roots, x, h, g, b0, directions_all):
    # Exact decoder identities at A=I and a nontrivial elementary transvection.
    frames = [identity(6), identity(6)]
    frames[1][0][1] = F(1)
    a = directions_all[0]
    for amap in frames:
        inva = inverse(amap)
        ps, qs = factors(x, h, a, F(1), amap, inva)
        require(identity_holds(ps, qs, g), "positive exact decoder identity")
        badp, badq = factors(x, h, a, F(1), amap, inva, "wrong-sign")
        require(not identity_holds(badp, badq, g), "wrong-sign negative control")
        badp, badq = factors(x, h, a, F(1), amap, inva, "omit-seventh")
        require(not identity_holds(badp, badq, g), "omitted seventh-term negative control")
    require(admissible(b0, g), "B0 positive admissibility control")
    bad = [row[:] for row in b0]
    edge = next((i, j) for i in range(36) for j in range(i + 1, 36) if g[i][j])
    i, j = edge
    bad[i][j] = bad[j][i] = 1
    require(not admissible(bad, g), "inadmissible-pairing negative control")
    return {"identity_fixtures": 2, "wrong_sign_rejections": 2,
            "omitted_term_rejections": 2, "inadmissible_edge_rejection": True}


def json_cost_hist(items, field):
    out = {}
    for item in items:
        for k, v in item[field].items():
            out[int(k)] = out.get(int(k), 0) + v
    return {str(k): out[k] for k in sorted(out)}


def aggregate(shard_results, meta, controls):
    all_results = [r for part in shard_results for r in part["transvections"]]
    raw_hist = json_cost_hist(all_results, "raw_histogram")
    charged_hist = json_cost_hist(all_results, "charged_histogram")
    active_hist = json_cost_hist(all_results, "active_total_histogram")
    best_charged = min(all_results, key=lambda r: (r["minimum_charged"]["charged"], r["minimum_charged"]["raw"]))
    best_raw = min(all_results, key=lambda r: (r["minimum_raw"]["raw"], r["minimum_raw"]["charged"]))
    witnesses = [w for r in all_results for w in r["target_witnesses_first20"]]
    target_count = sum(r["seven_total_cost_le_35_count"] for r in all_results)
    return {
        "schema_version": 1,
        "status": "completed" if target_count else "scoped-negative-result",
        "base_commit": "0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2",
        "assignment_seed": "b401f2874293cab50e88e4bd7068a949",
        "task_id": "complex-rank-shape-decoder",
        "priority_revision": 4,
        "selected_record_sha256": "10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32",
        "geometry": meta,
        "controls": controls,
        "domain": {
            "signed_transvections": len(all_results),
            "direction_count": 365,
            "root_directions": 36,
            "projective_ternary_directions": 364,
            "direction_union_count": 365,
            "lambda_domain": "all nonzero rational lambda, split at all exact support breakpoints",
            "support_cells": sum(r["cells"] for r in all_results),
            "distinct_nonzero_breakpoints": sum(r["distinct_nonzero_breakpoints"] for r in all_results),
            "degenerate_cells_with_fewer_than_7_active_totals": sum(r["degenerate_cells"] for r in all_results),
        },
        "result": {
            "minimum_raw_cost": best_raw["minimum_raw"]["raw"],
            "minimum_raw_witness": best_raw["minimum_raw"],
            "minimum_fully_charged_cost": best_charged["minimum_charged"]["charged"],
            "minimum_fully_charged_witness": best_charged["minimum_charged"],
            "raw_cost_histogram": raw_hist,
            "charged_cost_histogram": charged_hist,
            "active_total_count_histogram": active_hist,
            "seven_active_cost_le_35_witnesses_first20_per_matrix": witnesses,
            "positive_target_witness_count": target_count,
            "no_seven_active_cost_le_35": target_count == 0,
        },
        "per_transvection": all_results,
        "limits": [
            "Only the 60 signed elementary transvections A=I+epsilon E_ij are searched.",
            "Only the union of the 36 root directions and projective {-1,0,1}^6 directions in the pinned basis is searched.",
            "No arbitrary GL6(Q) basis change, arbitrary rational correction direction, different base decoder, or sparse pairing is covered.",
            "No physical source/copy/frame/hosting/restoration/precision mapping or selected-supplier profile is established.",
        ],
    }


def run_shard(shard_id):
    roots, x, h, g, b0, basis_ids, cols, digest = e6_data()
    root_dirs, ternary_dirs, all_dirs = directions(x)
    controls = check_controls(roots, x, h, g, b0, all_dirs)
    frames = shears()
    require(shard_id in (0, 1), "shard id must be 0 or 1")
    chunk = frames[shard_id * 30:(shard_id + 1) * 30]
    rank = rank_masks(b0)
    results = [search_matrix(x, h, g, b0, rank, all_dirs, frame) for frame in chunk]
    meta = {
        "root_lines": 36,
        "canonical_root_sha256": digest,
        "basis_root_indices": basis_ids,
        "ambient_basis_columns": cols,
        "basis_gram": [[qstr(z) for z in row] for row in h],
        "pairing_B0_rank_F2": rank((1 << 36) - 1, (1 << 36) - 1),
        "transvection_definition": "A=I+epsilon*E_ij; i!=j; epsilon in {-1,+1}",
    }
    return {"schema_version": 1, "shard": shard_id, "transvections": results,
            "geometry": meta, "controls": controls}


def run_pilot():
    roots, x, h, g, b0, *_ = e6_data()
    _, _, all_dirs = directions(x)
    rank = rank_masks(b0)
    frame = shears()[0]
    result = search_matrix(x, h, g, b0, rank, all_dirs, frame)
    print("PILOT", json.dumps({"transvection": result["transvection"],
                              "cells": result["cells"],
                              "min_raw": result["minimum_raw"],
                              "min_charged": result["minimum_charged"],
                              "target_count": result["seven_total_cost_le_35_count"]}, sort_keys=True))


def main():
    args = sys.argv[1:]
    if args == ["--smoke"]:
        roots, x, h, g, b0, *_ = e6_data()
        _, _, all_dirs = directions(x)
        controls = check_controls(roots, x, h, g, b0, all_dirs)
        print("PASS_E6_SHEARED_FRAME_SMOKE", controls)
        return
    if args == ["--pilot"]:
        run_pilot()
        return
    if args == ["--aggregate"]:
        s0 = json.loads((HERE / "SHARD-0.json").read_text())
        s1 = json.loads((HERE / "SHARD-1.json").read_text())
        certificate = aggregate([s0, s1], s0["geometry"], s0["controls"])
        (HERE / "CERTIFICATE.json").write_text(json.dumps(certificate, indent=2) + "\n")
        print("WROTE_CERTIFICATE", certificate["domain"]["support_cells"],
              "minimum_charged", certificate["result"]["minimum_fully_charged_cost"],
              "targets", certificate["result"]["positive_target_witness_count"])
        return
    if len(args) != 2 or args[0] not in ("--emit-shard", "--shard") or args[1] not in ("0", "1"):
        raise SystemExit("usage: verify.py --smoke | --pilot | --emit-shard {0,1} | --aggregate | --shard {0,1}")
    shard_id = int(args[1])
    computed = run_shard(shard_id)
    shard_path = HERE / f"SHARD-{shard_id}.json"
    if args[0] == "--emit-shard":
        shard_path.write_text(json.dumps(computed, indent=2) + "\n")
        print("WROTE", shard_path, "cells", sum(x["cells"] for x in computed["transvections"]))
        return
    require(shard_path.exists(), f"SHARD-{shard_id}.json missing")
    expected = json.loads(shard_path.read_text())
    require(computed == expected, f"shard {shard_id} differs from its certificate")
    cert_path = HERE / "CERTIFICATE.json"
    require(cert_path.exists(), "CERTIFICATE.json missing")
    s0 = json.loads((HERE / "SHARD-0.json").read_text())
    s1 = json.loads((HERE / "SHARD-1.json").read_text())
    combined = aggregate([s0, s1], computed["geometry"], computed["controls"])
    require(combined == json.loads(cert_path.read_text()), "aggregate certificate mismatch")
    print("PASS_E6_SHEARED_FRAME_SHARD", shard_id,
          "transvections", len(computed["transvections"]),
          "cells", sum(x["cells"] for x in computed["transvections"]))


if __name__ == "__main__":
    main()
