#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact scalar/support audit of PR2308's named P112 frame pair.

Prepared for commdata2338 with substantial OpenAI Codex assistance.
No predecessor executable is imported except the authenticated interval engine.
"""
import argparse
from fractions import Fraction as Q
from hashlib import sha1, sha256
import importlib.util
from itertools import combinations, product
import json
from pathlib import Path
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
ARCHIVE = "research/community-frontier1094-audit/selected-replay.tar.gz"
MEMBER = "candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json"
CEILING = "research/complex-local-word-ceiling/ceiling.py"


class Invalid(ValueError):
    pass


def require(ok, message):
    if not ok:
        raise Invalid(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def authenticate(raw, pin):
    require(sha256(raw).hexdigest() == pin["sha256"], "source SHA256 mismatch")
    blob = sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    require(blob == pin["git_blob"], "source Git blob mismatch")


def load_sources():
    pins = json.loads((HERE / "SOURCES.json").read_text())
    for pin in pins["files"]:
        if pin["usage"] == "input":
            authenticate((ROOT / pin["path"]).read_bytes(), pin)
    require(len(pins["external_files"]) == 1, "external input inventory")
    pin = pins["external_files"][0]
    raw = (ROOT / pin["path"]).read_bytes()
    authenticate(raw, pin)
    return json.loads(raw), pin


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def inner(a, b):
    z = dot(a, b)
    require(z % 4 == 0, "nonintegral E8 inner product")
    return z // 4


def roots():
    # PR968's root-line order, reconstructed without importing its executable.
    out = []
    for i, j in combinations(range(8), 2):
        for sign in (1, -1):
            v = [0] * 8
            v[i], v[j] = 2, 2 * sign
            out.append(tuple(v))
    out += [(1, *s) for s in product((1, -1), repeat=7) if s.count(-1) % 2 == 0]
    require(len(out) == 120 and len(set(out)) == 120, "root-line enumeration")
    require(all(dot(v, v) == 8 for v in out), "root normalization")
    return out


def f2_rank(masks):
    pivots = {}
    for v in masks:
        while v:
            p = v.bit_length() - 1
            if p in pivots:
                v ^= pivots[p]
            else:
                pivots[p] = v
                break
    return len(pivots)


def dense_binary_rank(matrix):
    """Second arithmetic route: explicit Boolean row elimination."""
    a = [row[:] for row in matrix]
    if not a:
        return 0
    rank = 0
    for col in range(len(a[0])):
        p = next((i for i in range(rank, len(a)) if a[i][col]), None)
        if p is None:
            continue
        a[rank], a[p] = a[p], a[rank]
        for i in range(rank + 1, len(a)):
            if a[i][col]:
                a[i] = [x ^ y for x, y in zip(a[i], a[rank])]
        rank += 1
        if rank == len(a):
            break
    return rank


def pivot_columns(matrix):
    a = [[Q(x) for x in row] for row in matrix]
    pivots = []
    for col in range(len(a[0])):
        rank = len(pivots)
        p = next((i for i in range(rank, len(a)) if a[i][col]), None)
        if p is None:
            continue
        a[rank], a[p] = a[p], a[rank]
        v = a[rank][col]
        a[rank] = [x / v for x in a[rank]]
        for i in range(rank + 1, len(a)):
            v = a[i][col]
            a[i] = [x - v * y for x, y in zip(a[i], a[rank])]
        pivots.append(col)
        if len(pivots) == len(a):
            break
    return pivots


def determinant(matrix):
    """Independent fraction-free determinant for an integer square minor."""
    a = [row[:] for row in matrix]
    n, previous, sign = len(a), 1, 1
    require(n and all(len(row) == n for row in a), "square determinant input")
    for k in range(n - 1):
        p = next((i for i in range(k, n) if a[i][k]), None)
        if p is None:
            return 0
        if p != k:
            a[k], a[p], sign = a[p], a[k], -sign
        pivot = a[k][k]
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                numerator = pivot * a[i][j] - a[i][k] * a[k][j]
                require(numerator % previous == 0, "Bareiss divisibility")
                a[i][j] = numerator // previous
            a[i][k] = 0
        previous = pivot
    return sign * a[-1][-1]


def geometry(cert):
    lines = roots()
    gram = [[inner(a, b) for b in lines] for a in lines]
    rows = cert["q_to_line"]
    mapping = {row["line"]: row["q"] for row in rows}
    live = sorted(mapping)
    require(len(rows) == len(mapping) == len(set(mapping.values())) == 112, "map is not a bijection")
    frame0 = []
    for i in range(4):
        for sign in (1, -1):
            v = [0] * 8
            v[2 * i], v[2 * i + 1] = 2, 2 * sign
            frame0.append(lines.index(tuple(v)))
    require(set(live) == set(range(120)) - set(frame0), "wrong P112 puncture")
    with tarfile.open(ROOT / ARCHIVE, "r:gz") as tf:
        data = json.load(tf.extractfile(MEMBER))
    qlabels = sorted(int(row["q"]) for row in data["recipes"])
    require(sorted(mapping.values()) == qlabels, "selected port binding")
    require(all(((mapping[a] & mapping[b]).bit_count() & 1) == ((gram[a][b] + 1) & 1)
                for a in live for b in live), "selected label pairing mismatch")
    deleted = sorted({q for q in range(512) if q.bit_count() in (3, 7)} - set(qlabels))
    require(len(deleted) == 8, "deleted labels")
    require(all(((mapping[a] & q).bit_count() & 1) == ((gram[a][b] + 1) & 1)
                for a in live for q, b in zip(deleted, frame0)), "deleted-frame signatures")
    require(f2_rank(qlabels) == 9, "selected labels do not span ambient space")
    lattice_basis = [(2,-2,0,0,0,0,0,0), (0,2,-2,0,0,0,0,0),
                     (0,0,2,-2,0,0,0,0), (0,0,0,2,-2,0,0,0),
                     (0,0,0,0,2,-2,0,0), (0,0,0,0,0,2,-2,0),
                     (0,0,0,0,0,2,2,0), (-1,)*8]
    rbits = cert["witness"]["r_bits"]
    require(len(rbits) == 8 and all(type(v) is int and v in (0, 1) for v in rbits), "r bits")
    rroot = [sum(rbits[k] * lattice_basis[k][j] for k in range(8)) for j in range(8)]
    beta = {a: inner(rroot, lines[a]) & 1 for a in live}
    choices = [r for r in range(512) if all(((r & mapping[a]).bit_count() & 1)
               == 1 - beta[a] for a in live)]
    require(len(choices) == 1, "physical shared direction not uniquely bound")
    r = choices[0]
    require(r.bit_count() & 1, "shared direction is not anisotropic")
    frames = cert["witness"]["frames"]
    require(len(frames) == 2 and frames[0] != frames[1], "two distinct frames required")
    for frame in frames:
        require(len(frame) == len(set(frame)) == 8 and set(frame) <= set(live), "frame inventory")
        require(all(gram[a][b] == 0 for a, b in combinations(frame, 2)), "nonorthogonal frame")
        require(all(beta[a] == 1 for a in frame), "frame incompatible with direction")
    union = sorted(set(frames[0]) | set(frames[1]))
    targets = [a for a in live if beta[a] == 0]
    planes = {a: [mapping[a], r] if a in union else [mapping[a]] for a in live}
    require(all(f2_rank(planes[a]) == 2 and (mapping[a] & r).bit_count() % 2 == 0
                for a in union), "invalid plane port")
    return lines, gram, mapping, live, frames, union, targets, r, planes


def pairing_rank(rows, cols, planes):
    left = [q for a in rows for q in planes[a]]
    right = [q for b in cols for q in planes[b]]
    matrix = [[(a & b).bit_count() & 1 for b in right] for a in left]
    rank = f2_rank([sum(v << j for j, v in enumerate(row)) for row in matrix])
    require(rank == dense_binary_rank(matrix), "binary rank engines disagree")
    return rank


def outer_sum(terms, n):
    out = [[Q(0) for _ in range(n)] for _ in range(n)]
    for u, v in terms:
        for i, x in enumerate(u):
            if x:
                for j, y in enumerate(v):
                    if y:
                        out[i][j] += x * y
    return out


def fitting_faults(matrix, live, planes):
    faults = []
    for i, a in enumerate(live):
        for j, b in enumerate(live):
            if i == j:
                if matrix[i][j] != 1:
                    faults.append([a, b, str(matrix[i][j])])
            elif matrix[i][j] and pairing_rank([a], [b], planes):
                faults.append([a, b, str(matrix[i][j])])
    return faults


def cost_screen(union_size, extra):
    spec = importlib.util.spec_from_file_location("p112_audit_ceiling", ROOT / CEILING)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    local = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}
    saving = Q(35491136290869, 20000000000000000)
    interval = module.relax(local, 73, 896, 9, 64 + extra, saving, unpaid=1 + Q(union_size, 112))
    return {"upgraded_ports": union_size, "extra_centre_charge": extra,
            "unpaid": str(1 + Q(union_size, 112)), "saving": str(saving),
            "moment_interval": list(map(str, interval)),
            "decision": "passes" if interval[1] < 1 else "fails" if interval[0] > 1 else "unresolved"}


def compute(cert):
    lines, g, mapping, live, frames, union, targets, r, planes = geometry(cert)
    n = len(live)
    index = {a: i for i, a in enumerate(live)}
    baseline = [[Q(g[a][b], 2) for b in live] for a in live]
    reference = frames[0]
    def first_frame(prefix, candidates):
        if len(prefix) == 8:
            return prefix
        for i, a in enumerate(candidates):
            found = first_frame(prefix + [a], [b for b in candidates[i + 1:] if g[a][b] == 0])
            if found is not None:
                return found
        return None
    require(first_frame([], [a for a in live if a not in targets]) == reference,
            "reference is not PR2308's lexicographically first frame in this family")
    # a = sum_s <a,s>/2 * s in the first orthogonal root frame.
    # Thus M = D B, D[a,s]=<a,s>, B[s,b]=<s,b>/2 on the beta-zero set.
    d = [[g[a][s] for s in reference] for a in union]
    bmat = [[Q(g[s][b], 2) if b in targets else Q(0) for b in live] for s in reference]
    require(all(sum(d[i][k] * bmat[k][j] for k in range(8)) ==
                (g[a][b] if b in targets else 0)
                for i, a in enumerate(union) for j, b in enumerate(live)), "shared factorization")
    require(len(pivot_columns(bmat)) == 8, "reference correction basis rank")
    correction_terms, term_receipts = [], []
    for k in range(8):
        u = [Q(0)] * n
        for i, a in enumerate(union):
            u[index[a]] = -Q(d[i][k], 2)
        v = bmat[k]
        rows = [a for a in live if u[index[a]]]
        cols = [b for b in live if v[index[b]]]
        charge = pairing_rank(rows, cols, planes)
        correction_terms += [(u, v), (v, u)]
        term_receipts.append({"column": k, "row_support": rows, "column_support": cols,
                              "pairing_rank_per_direction": charge})
    # The natural eight-term P112 decoder uses the deleted orthogonal frame,
    # not the ordinary coordinate axes of this doubled-root presentation.
    deleted_frame = sorted(set(range(120)) - set(live))
    base_terms = [([Q(g[a][s]) for a in live], [Q(g[b][s], 4) for b in live])
                  for s in deleted_frame]
    require(outer_sum(base_terms, n) == baseline, "coordinate decoder identity")
    correction = outer_sum(correction_terms, n)
    partial = [[baseline[i][j] + correction[i][j] for j in range(n)] for i in range(n)]
    expected = [[Q(0) if ((a in union and b in targets) or (b in union and a in targets))
                 else baseline[i][j] for j, b in enumerate(live)] for i, a in enumerate(live)]
    require(partial == expected, "literal bidirectional correction map")
    faults = fitting_faults(partial, live, planes)
    require(len(faults) == 32 and all(a in union and b in union for a, b, _ in faults),
            "unexpected partial endpoint faults")
    rectangle_columns = union + targets
    rect2 = [[2 * int(a == b) - g[a][b] for b in rectangle_columns] for a in union]
    require(all(pairing_rank([a], [b], planes) > 0 for a in union for b in rectangle_columns),
            "rectangle is not fully constrained")
    pivots = pivot_columns(rect2)
    require(len(pivots) == len(union), "forced correction rectangle lacks full row rank")
    minor = [[row[j] for j in pivots] for row in rect2]
    det = determinant(minor)
    require(det != 0, "integer rectangle minor is singular")
    trows = [lines[a] for a in targets]
    tpivots = pivot_columns(list(map(list, zip(*trows))))
    require(len(tpivots) == 8, "complement roots do not span rank eight")
    tdet = determinant([list(trows[i]) for i in tpivots])
    require(tdet != 0, "complement root determinant")
    missing = [[2 * int(a == b) - g[a][b] for b in union] for a in union]
    missing_rank = len(pivot_columns(missing))
    require(missing_rank == 8, "missing within-union block rank")
    base_supports = [[a for a in live if g[a][s]] for s in deleted_frame]
    base_costs = [pairing_rank(support, support, planes) for support in base_supports]
    old_planes = {a: [mapping[a]] for a in live}
    old_costs = [pairing_rank(support, support, old_planes) for support in base_supports]
    correction_cost = 2 * sum(t["pairing_rank_per_direction"] for t in term_receipts)
    parity_rank = f2_rank([sum((v & 1) << j for j, v in enumerate(row)) for row in d])
    require(parity_rank == 1 and correction_cost == 40, "named witness invoices changed")
    require(old_costs == [8] * 8 and base_costs == [9] * 4 + [8] * 4, "coordinate decoder cost binding")
    controls = []
    def passed(name, ok):
        require(ok, "control failed: " + name)
        controls.append(name)
    doubled = [[2 * v for v in row] for row in d]
    halved = [[v / 2 for v in row] for row in bmat]
    passed("coefficient_gauge_changes_parity_not_map_or_support",
           f2_rank([sum((v & 1) << j for j, v in enumerate(row)) for row in doubled]) == 0
           and all((d[i][k] != 0) == (doubled[i][k] != 0) for i in range(len(union)) for k in range(8))
           and all(sum(doubled[i][k] * halved[k][j] for k in range(8)) ==
                   sum(d[i][k] * bmat[k][j] for k in range(8)) for i in range(len(union)) for j in range(n)))
    passed("omitted_scalar_factor", outer_sum(correction_terms[1:], n) != correction)
    bad_d = [row[:] for row in d]
    bad_d[0][0] += 1
    passed("wrong_coefficient", any(sum(bad_d[0][k] * bmat[k][j] for k in range(8)) !=
                                  sum(d[0][k] * bmat[k][j] for k in range(8)) for j in range(n)))
    passed("line_mask_misses_plane_faults", not fitting_faults(partial, live, old_planes) and bool(faults))
    passed("duplicate_port_count", len(frames[0]) + len(frames[1]) == 16 and len(union) == 12)
    fixed = [row[:] for row in partial]
    for a in union:
        for b in union:
            fixed[index[a]][index[b]] = Q(a == b)
    passed("repaired_scalar_fitting_positive", not fitting_faults(fixed, live, planes)
           and any(fixed[i][j] != 0 for i in range(n) for j in range(n) if i != j))
    a, b, value = faults[0]
    x, y = [Q(0)] * n, [Q(0)] * n
    x[index[b]], y[index[a]] = Q(1), Q(11)
    after = y[:]
    for u, v in base_terms + correction_terms:
        total = dot(v, x)
        after = [z + c * total for z, c in zip(after, u)]
    passed("dirty_wrong_source_counterexample", after[index[a]] == 11 + Q(value)
           and after[index[a]] != 11 and x[index[b]] == 1)
    for source in range(n):
        for target in range(n):
            require(sum(u[target] * v[source] for u, v in base_terms + correction_terms)
                    == partial[target][source], "formal scalar source column")
    # ADDs are only Y <- Y + u*(v^T X); verify all target-dirt basis columns too.
    for target in range(n):
        dirt = [Q(i == target) for i in range(n)]
        actual = dirt[:]
        for u, v in base_terms + correction_terms:
            total = dot(v, [Q(0)] * n)
            actual = [z + c * total for z, c in zip(actual, u)]
        require(actual == dirt, "formal target-dirt column")
    controls.append("all_224_formal_input_columns")
    corrupt = [row[:] for row in minor]
    corrupt[-1] = corrupt[0][:]
    passed("dependent_rank_certificate", determinant(corrupt) == 0)
    wrong_cert = json.loads(json.dumps(cert))
    wrong_cert["q_to_line"][0]["q"], wrong_cert["q_to_line"][1]["q"] = (
        wrong_cert["q_to_line"][1]["q"], wrong_cert["q_to_line"][0]["q"])
    try:
        geometry(wrong_cert)
    except Invalid:
        controls.append("wrong_label_map")
    else:
        raise Invalid("control failed: wrong_label_map")
    screens = {"predecessor_hypothesis": cost_screen(16, 8),
               "actual_union_only": cost_screen(12, 8),
               "actual_union_first_rejected_integer_charge": cost_screen(12, 9),
               "forced_rectangle_floor": cost_screen(12, 12),
               "literal_correction": cost_screen(12, 40)}
    require(screens["predecessor_hypothesis"]["decision"] == "passes" and
            screens["actual_union_only"]["decision"] == "passes" and
            screens["actual_union_first_rejected_integer_charge"]["decision"] == "fails" and
            screens["forced_rectangle_floor"]["decision"] == "fails", "budget verdict")
    return {"schema_version": 1, "kind": "scoped scalar-factor pricing audit and proof",
            "source_pr": 2308, "source_head": "7653e0cc72527c1e7fc02499122d383713ee9d54",
            "physical_shared_direction": r, "frames": frames,
            "union": union, "intersection": sorted(set(frames[0]) & set(frames[1])),
            "complement_ports": targets, "complement_rank_witness": {
                "line_ids": [targets[i] for i in tpivots], "doubled_root_determinant": tdet},
            "coefficient_parity_rank": parity_rank, "rescaled_coefficient_parity_rank": 0,
            "correction_terms": term_receipts, "correction_COPY_cost": correction_cost,
            "deleted_frame_decoder_basis": deleted_frame,
            "original_deleted_frame_COPY_ranks": old_costs, "plane_deleted_frame_COPY_ranks": base_costs,
            "literal_total_COPY_cost_before_missing_repair": sum(base_costs) + correction_cost,
            "forbidden_nonzero_entries": faults, "missing_union_block_rank": missing_rank,
            "forced_rectangle": {"rows": union, "columns": rectangle_columns,
                "twice_entries": rect2, "rank": len(pivots), "minor_column_positions": pivots,
                "minor_determinant": det, "any_additive_scalar_correction_COPY_floor": len(union)},
            "dirty_counterexample": {"target_line": a, "source_line": b,
                "target_q": mapping[a], "source_q": mapping[b], "initial_target": "11",
                "output_target": str(after[index[a]]), "required_target": "11"},
            "scalar_columns_checked": 224, "controls": controls, "screens": screens,
            "limits": ["one named pair; no all-pair census", "additive scalar factors retain G/2",
                "no global COPY optimum or operator-valued lower bound", "no native or chronological realization",
                "screen keeps predecessor local profile; changed profiles require repricing",
                "no supplier admission, selected cold replay, or new kappa"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, help="also write verified receipt to a new file exclusively")
    args = parser.parse_args()
    cert, _ = load_sources()
    result = compute(cert)
    expected = json.loads((HERE / "RESULT.json").read_text())
    require(canonical(result) == canonical(expected), "receipt mismatch")
    if args.out:
        with args.out.open("x") as f:
            json.dump(result, f, indent=2)
            f.write("\n")
    print("PASS_P112_SHARED_CORRECTION_COST_AUDIT union=12 parity_rank=1 correction_COPY=40 "
          "forbidden_entries=32 additive_COPY_floor=12 five_percent_screen=FAIL controls="
          + str(len(result["controls"])) + " no_new_kappa")


if __name__ == "__main__":
    main()
