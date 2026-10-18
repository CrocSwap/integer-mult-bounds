#!/usr/bin/env python3
"""Independent check of PR2389's QQ16 optimal read-set classification.

Written from main's sources only (no code from PR2354 or PR2389 is imported or
copied).  Exact integer / Fraction arithmetic.  Routes used here:

* classification by the complement identity  V cap {c_S=0} = ker R_T  (T=U-S)
  and the column matroid of the 8-row centre matrix (no 88-dimensional kernel);
* lower bound rank(H|V) >= 66 from linear independence of the 47 first-axis
  owner functions f_b(d)=bit_0(d b) on registered owners (47x47 0/1 minor),
  not from a 17-owner evaluation minor.

Usage:  python3 -B verify.py            (replay + controls, compare RESULT.json)
        python3 -B verify.py --emit F   (write a fresh receipt to new path F)

Prepared by thakrarsagar with substantial AI assistance from Claude
(Anthropic, Claude Opus 5.5).  Apache-2.0.
"""
from __future__ import annotations

import argparse
import copy
import gzip
import hashlib
import io
import json
import tarfile
from fractions import Fraction
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
PACKET = "research/joint-query/certificate.json.gz"
ARCHIVE = "research/community-frontier1042-audit/selected-replay.tar.gz"
MEMBER = "t16/global/base/work/complex-nine-native/DATA-PHASES.json"
PINS = {
    PACKET: "a5ed85fac5ebf3c091482a113ab0d351eb5a7892fe2841a35e16017ec1ff49f7",
    ARCHIVE: "22c3f4dce4b897a1d423d1388801933e288b6a6b1906cb15e1b16a5eb68db754",
}
MEMBER_SHA256 = "c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa"

# Finite claims audited (PR2389 head aed06c8f8d60ce97b7eb3a7c6c17ad12cbe1e863,
# README + RESULT.json; PR2354 head 308ebc7405303bb7ed91b012bb705949c6091a16).
# These are *claims to compare against*, never inputs to the computation.
CLAIMS = {
    "axis_group_count": 47,
    "unread_axis": 2,
    "unread_group_size": 30,
    "unread_group_rank": 8,
    "group_rank_sum": 74,
    "V_dimension": 88,
    "H_on_V_rank": 66,
    "optimal_read_set_count": 45,
    "mandatory_ports": [1, 2, 3, 4, 5, 93, 94, 95, 96, 97, 98, 99, 100, 101,
                        102, 103, 104, 105, 106, 107, 108, 109],
    "nuisance_coordinate_count": 29,
    "coloop_ports": [77],
    "port77_swap_count": 44,
    "optimal_omissions": [6, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 22,
                          23, 24, 25, 26, 28, 29, 30, 31, 32, 33, 34, 35, 38,
                          39, 40, 41, 42, 43, 77, 78, 79, 80, 82, 83, 84, 85,
                          86, 88, 89, 90, 91],
    "dual_vector_up_to_sign": [-1, 0, 1, 0, 1, 0, 1, 0],
    "dual_value_on_77": -4,
    "alpha_nonzero_values": ["-1/2", "1/2"],
}


# PR2384 (commdata2338, head b9ef408b1cb0fcd34ab1f1bdbe645573d5de188f): a
# second-chart-axis hidden input on the unread ports.  Only its finite source
# facts are rechecked here; its zero-observation proof is inherited.
WITNESS_2384 = {
    "ports": [44, 49, 58, 70],
    "coefficients": [-1, -1, -1, 1],
    "chart_axis_index": 1,
    "axes": [25, 145, 4, 4],
    "B0h_identity_owner": [-1, 0, -1, 0, 0, -1, 0, -1],
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


# ----------------------------------------------------------------- sources
def load_sources(root=ROOT):
    raw = {}
    for path, pin in PINS.items():
        data = (root / path).read_bytes()
        require(hashlib.sha256(data).hexdigest() == pin, "source pin " + path)
        raw[path] = data
    packet = json.loads(gzip.decompress(raw[PACKET]))
    with tarfile.open(fileobj=io.BytesIO(raw[ARCHIVE]), mode="r:gz") as tar:
        found = [m for m in tar.getmembers() if m.name == MEMBER]
        require(len(found) == 1 and found[0].isfile(), "unique archive member")
        member = tar.extractfile(found[0]).read()
    require(hashlib.sha256(member).hexdigest() == MEMBER_SHA256, "member pin")
    return packet, json.loads(member)


def parse(packet, phases):
    """Return (A, T, U, R as 8x112 ints, first axis per port, owners)."""
    A, T, U = packet["A_ports"], packet["T_ports"], packet["U_ports"]
    require(len(A) == 8 and len(T) == 8 and len(U) == 96, "partition sizes")
    require(sorted(A + T + U) == list(range(112)), "partition of 112 ports")
    rows = packet["R_rows"]
    require(len(rows) == 8, "eight centre rows")
    R = []
    for row in rows:
        require(all(0 <= int(k) < 112 for k in row), "column index range")
        vals = [Fraction(row.get(str(p), "0")) for p in range(112)]
        require(all(v.denominator == 1 for v in vals), "integral R")
        R.append([int(v) for v in vals])
    m = phases["m"]
    recipes = phases["recipes"]
    require(m == 73 and len(recipes) == 112, "phase geometry")
    axes = {}
    for idx, rec in enumerate(recipes):
        require(int(rec["port"]) == idx, "recipe order")
        ax = rec["idle_children"][0]["orthogonal_axes"]
        require(len(ax) >= 8 and 0 < ax[0] < (1 << m), "chart axis")
        axes[idx] = ax[0]
    identity = tuple(1 << j for j in range(m))
    owners = {"identity": identity}
    seen = {identity}
    for key in sorted(packet["map_registry"], key=lambda k: int(k[1:])):
        cols = packet["map_registry"][key]["owner_right_matrix_columns"]
        if isinstance(cols, str):
            cols = json.loads(cols)
        cols = tuple(int(x) for x in cols)
        require(len(cols) == m, "owner matrix width")
        if cols not in seen:
            seen.add(cols)
            owners[key] = cols
    return A, T, U, R, axes, owners


# ---------------------------------------------------- exact linear algebra
def bareiss_rank(matrix):
    """Rank of an integer matrix by fraction-free elimination (exact)."""
    a = [list(r) for r in matrix]
    if not a or not a[0]:
        return 0
    nrows, ncols = len(a), len(a[0])
    rank, prev = 0, 1
    for col in range(ncols):
        piv = next((i for i in range(rank, nrows) if a[i][col] != 0), None)
        if piv is None:
            continue
        a[rank], a[piv] = a[piv], a[rank]
        for i in range(rank + 1, nrows):
            for j in range(col + 1, ncols):
                q, r = divmod(a[rank][col] * a[i][j] - a[i][col] * a[rank][j], prev)
                require(r == 0, "Bareiss division must be exact")
                a[i][j] = q
            a[i][col] = 0
        prev = a[rank][col]
        rank += 1
        if rank == nrows:
            break
    return rank


def bareiss_det(square):
    a = [list(r) for r in square]
    n, sign, prev = len(a), 1, 1
    for k in range(n - 1):
        piv = next((i for i in range(k, n) if a[i][k] != 0), None)
        if piv is None:
            return 0
        if piv != k:
            a[k], a[piv] = a[piv], a[k]
            sign = -sign
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                q, r = divmod(a[k][k] * a[i][j] - a[i][k] * a[k][j], prev)
                require(r == 0, "Bareiss det division")
                a[i][j] = q
        prev = a[k][k]
    return sign * a[n - 1][n - 1]


def nullspace(matrix):
    """Right kernel basis (Fractions) of a small matrix via reduced echelon form."""
    a = [[Fraction(x) for x in r] for r in matrix]
    nrows, ncols = len(a), len(a[0])
    pivcols, r = [], 0
    for c in range(ncols):
        p = next((i for i in range(r, nrows) if a[i][c] != 0), None)
        if p is None:
            continue
        a[r], a[p] = a[p], a[r]
        inv = 1 / a[r][c]
        a[r] = [x * inv for x in a[r]]
        for i in range(nrows):
            if i != r and a[i][c] != 0:
                f = a[i][c]
                a[i] = [x - f * y for x, y in zip(a[i], a[r])]
        pivcols.append(c)
        r += 1
    basis = []
    for free in (c for c in range(ncols) if c not in pivcols):
        v = [Fraction(0)] * ncols
        v[free] = Fraction(1)
        for i, pc in enumerate(pivcols):
            v[pc] = -a[i][free]
        basis.append(v)
    return basis


def independent_rows(rows, target):
    """Greedy exact (Fraction) selection of linearly independent rows."""
    chosen, basis, pivots = [], [], []
    for i, r in enumerate(rows):
        v = [Fraction(x) for x in r]
        for pc, bv in zip(pivots, basis):
            if v[pc] != 0:
                f = v[pc] / bv[pc]
                v = [x - f * y for x, y in zip(v, bv)]
        nz = next((j for j, x in enumerate(v) if x != 0), None)
        if nz is not None:
            basis.append(v)
            pivots.append(nz)
            chosen.append(i)
            if len(chosen) == target:
                break
    return chosen


def matvec(M, v):
    return [sum(x * y for x, y in zip(row, v)) for row in M]


def gf2_apply(columns, vector):
    """d b over GF(2): XOR of the owner's columns selected by the bits of b."""
    out, j = 0, 0
    while vector:
        if vector & 1:
            out ^= columns[j]
        vector >>= 1
        j += 1
    return out


def dot(u, v):
    return sum(x * y for x, y in zip(u, v))


# --------------------------------------------------------------- the check
def compute(packet, phases, witness_2384=WITNESS_2384):
    A, T, U, R, axes, owners = parse(packet, phases)
    col = {p: [R[k][p] for k in range(8)] for p in range(112)}

    def gram(ports):
        return [[sum(R[i][p] * R[j][p] for p in ports) for j in range(8)] for i in range(8)]

    def colrank(ports):
        return bareiss_rank([[col[p][k] for p in ports] for k in range(8)])

    scalar = lambda s: [[s if i == j else 0 for j in range(8)] for i in range(8)]
    rank_RU = colrank(U)
    dim_V = len(U) - rank_RU

    # (a) first-axis groups; L = direct sum of L_b(c) = R_{C_b} c_{C_b}
    groups = {}
    for p in U:
        groups.setdefault(axes[p], []).append(p)
    group_records = [{"axis": b, "ports": groups[b], "rank": colrank(groups[b])}
                     for b in sorted(groups)]
    rank_L = sum(g["rank"] for g in group_records)
    redundant = [g for g in group_records if g["rank"] < len(g["ports"])]
    require(len(redundant) == 1, "exactly one axis group with dependent columns")
    C, unread_axis = redundant[0]["ports"], redundant[0]["axis"]
    RC = [[col[p][k] for p in C] for k in range(8)]
    rank_RC = colrank(C)

    # K = ker L = ker R_C (all other groups have independent columns)
    K = nullspace(RC)
    require(len(K) == len(C) - rank_RC, "dim ker R_C")
    require(len(K) == len(U) - rank_L, "ker L = ker R_C")
    for v in K:
        require(all(x == 0 for x in matvec(RC, v)), "kernel vector")
    support = sorted(C[j] for j in range(len(C)) if any(v[j] != 0 for v in K))
    nuisance = {str(C[j]): next(i for i, v in enumerate(K) if v[j] != 0)
               for j in range(len(C)) if C[j] in support}
    coloops = sorted(set(C) - set(support))
    for q in coloops:
        require(colrank([p for p in C if p != q]) == rank_RC - 1, "coloop deletion")
    for q in support:
        require(colrank([p for p in C if p != q]) == rank_RC, "non-coloop deletion")

    # (b) complement classification.  For |S| = rank(H|V) = dim V - dim K,
    # S is an exact terminal read set iff V cap {c_S=0} = ker R_T (T = U - S)
    # equals K.  Necessity of supp(K) in T, then |T| = |supp K| + 1 forces
    # T = supp(K) + {x}, and K = ker R_T iff rank R_T = 8.
    require(len(U) - (dim_V - len(K)) == len(support) + 1,
            "complement size |U| - rank(H|V) equals |supp K| + 1")
    left = nullspace([col[p] for p in support])  # rows r_p^T: w with w r_p = 0
    rank_supp = colrank(support)
    require(len(left) == 8 - rank_supp, "left kernel dimension")
    candidates = [p for p in U if p not in support]
    valid, ranks = [], {}
    for x in candidates:
        ranks[x] = colrank(support + [x])
        by_dual = len(left) == 1 and dot(left[0], col[x]) != 0
        require((ranks[x] == 8) == by_dual, "rank test agrees with dual-vector test")
        if ranks[x] == 8:
            valid.append(x)
    optimal_sets = [sorted(set(candidates) - {x}) for x in valid]
    mandatory = sorted(set(candidates) - set(valid))
    swaps = [x for x in valid if x not in C]

    # coordinate relation c_q + sum_p alpha_p c_p = 0 from w R_U c = 0
    relation, w_norm, wq_norm = None, None, None
    if len(left) == 1 and len(coloops) == 1:
        w, q = left[0], coloops[0]
        require(all(dot(w, col[p]) == 0 for p in support), "w annihilates supp K")
        wq = dot(w, col[q])
        relation = {str(p): str(dot(w, col[p]) / wq) for p in candidates}
        scale = abs(next(x for x in w if x != 0))
        w_norm = [str(x / scale) for x in w]
        wq_norm = str(wq / scale)

    # source binding of the first axis: for every ordinary port p and stage
    # s = 1..8 some registered owner maps the 8-axis chart of p (first axis
    # first) onto e_{9+8(s-1)+i}, i = 0..7  (the route premise behind B_s h = 0)
    routed, route_names = 0, set()
    for p in U:
        chart = phases["recipes"][p]["idle_children"][0]["orthogonal_axes"][:8]
        require(chart[0] == axes[p], "first axis is chart axis 0")
        by_image = {}
        for name, cols in owners.items():
            by_image.setdefault(gf2_apply(cols, chart[0]), []).append(name)
        for s in range(1, 9):
            base = 9 + 8 * (s - 1)
            hits = [n for n in by_image.get(1 << base, [])
                    if all(gf2_apply(owners[n], chart[i]) == 1 << (base + i) for i in range(8))]
            route_names.update(hits)
            routed += bool(hits)

    # (c) owner bit-function independence on registered owners
    axis_list = sorted(groups)
    names = list(owners)
    rows = [[gf2_apply(owners[n], b) & 1 for b in axis_list] for n in names]
    chosen = independent_rows(rows, len(axis_list))
    # sensitivity only (not used for the claim): transposed action convention
    transpose_rank = len(independent_rows(
        [[(owners[n][0] & b).bit_count() & 1 for b in axis_list] for n in names],
        len(axis_list)))
    # sensitivity only: the route owners alone do not certify independence
    route_rows = [rows[i] for i, n in enumerate(names) if n in route_names]
    route_rank = len(independent_rows(route_rows, len(axis_list)))
    route_id_rank = len(independent_rows([rows[0]] + route_rows, len(axis_list)))
    minor = [rows[i] for i in chosen]
    det = bareiss_det(minor) if len(minor) == len(axis_list) else 0
    independent = det != 0
    # Injective F (owners x axes) => H(c)|_D = 0 iff every L_b(c) = 0, hence
    # ker(H|V) = ker L = K and rank(H|V) = dim V - dim K on the whole owner set.
    rank_H_V = dim_V - len(K) if independent else None

    # (e) PR2384's witness against the classification (PR2389 open question 1)
    wit = witness_2384
    w_axes = [phases["recipes"][p]["idle_children"][0]["orthogonal_axes"][wit["chart_axis_index"]]
              for p in wit["ports"]]
    w_relation = [sum(R[k][p] * x for p, x in zip(wit["ports"], wit["coefficients"]))
                  for k in range(8)]
    w_b0_identity = [sum(R[k][p] * x * (b & 1) for p, x, b in
                         zip(wit["ports"], wit["coefficients"], w_axes)) for k in range(8)]
    w_hits = sorted({p for S in optimal_sets for p in S} & set(wit["ports"]))
    witness = {
        "ports": wit["ports"],
        "axes_from_source": w_axes,
        "column_relation": w_relation,
        "B0h_identity_owner": w_b0_identity,
        "support_within_nuisance": set(wit["ports"]) <= set(support),
        "optimal_sets_reading_support": w_hits,
    }

    return {
        "pr2384_witness_check": witness,
        "ordinary_gram_is_48I": gram(U) == scalar(48),
        "selected_gram_is_4I": gram(A) == scalar(4),
        "rank_R_U": rank_RU,
        "V_dimension": dim_V,
        "axis_group_count": len(group_records),
        "axis_groups": group_records,
        "group_rank_sum": rank_L,
        "unread_axis": unread_axis,
        "unread_group": C,
        "unread_group_rank": rank_RC,
        "K_dimension": len(K),
        "nuisance_coordinates": support,
        "nuisance_witness_kernel_basis_index": nuisance,
        "coloop_ports": coloops,
        "eligible_ports": candidates,
        "complement_ranks": {str(x): ranks[x] for x in candidates},
        "optimal_omissions": valid,
        "optimal_read_set_count": len(optimal_sets),
        "optimal_read_sets": optimal_sets,
        "mandatory_ports": mandatory,
        "port77_swaps": swaps,
        "dual_vector_normalized": w_norm,
        "dual_value_on_coloop_normalized": wq_norm,
        "coordinate_relation": relation,
        "registered_routes_checked": routed,  # (p, s) pairs with a route
        "owner_rows_available": len(rows),
        "transpose_convention_rank_sensitivity": transpose_rank,
        "route_owner_count": len(route_names),
        "route_owner_function_rank": route_rank,
        "identity_plus_route_owner_function_rank": route_id_rank,
        "minor_owners_that_are_routes": sorted(n for i, n in enumerate(names)
                                              if i in chosen and n in route_names),
        "owner_axes": axis_list,
        "owner_minor_names": [names[i] for i in chosen],
        "owner_minor_rows": minor,
        "owner_minor_determinant": det,
        "owner_functions_independent": independent,
        "H_on_V_rank": rank_H_V,
    }


def check(res, claims=CLAIMS):
    require(res["rank_R_U"] == 8, "rank R_U")
    require(res["V_dimension"] == claims["V_dimension"], "dim V")
    require(res["axis_group_count"] == claims["axis_group_count"], "group count")
    require(res["unread_axis"] == claims["unread_axis"], "unread axis")
    require(len(res["unread_group"]) == claims["unread_group_size"], "unread group size")
    require(res["unread_group_rank"] == claims["unread_group_rank"], "unread group rank")
    require(res["group_rank_sum"] == claims["group_rank_sum"], "rank L")
    require(res["owner_functions_independent"], "owner bit functions independent")
    require(len(res["owner_minor_rows"]) == res["axis_group_count"], "square owner minor")
    require(all(x in (0, 1) for row in res["owner_minor_rows"] for x in row), "0/1 minor")
    require(res["H_on_V_rank"] == claims["H_on_V_rank"], "rank H|V")
    require(len(res["nuisance_coordinates"]) == claims["nuisance_coordinate_count"],
            "nuisance count")
    require(res["coloop_ports"] == claims["coloop_ports"], "coloop port")
    require(res["optimal_read_set_count"] == claims["optimal_read_set_count"], "set count")
    require(all(len(s) == claims["H_on_V_rank"] for s in res["optimal_read_sets"]), "set size")
    require(res["mandatory_ports"] == claims["mandatory_ports"], "mandatory ports")
    require(len(res["port77_swaps"]) == claims["port77_swap_count"], "port-77 swaps")
    require(res["optimal_omissions"] == claims["optimal_omissions"], "omissions")
    dual = [Fraction(x) for x in res["dual_vector_normalized"]]
    target = [Fraction(x) for x in claims["dual_vector_up_to_sign"]]
    require(dual in (target, [-x for x in target]), "dual vector up to sign")
    sign = 1 if dual == target else -1
    require(Fraction(res["dual_value_on_coloop_normalized"]) * sign == claims["dual_value_on_77"],
            "w r_77")
    alphas = {p: Fraction(v) for p, v in res["coordinate_relation"].items()
              if int(p) not in res["coloop_ports"]}
    nonzero = sorted(p for p, v in alphas.items() if v != 0)
    require(sorted({str(v) for v in alphas.values() if v != 0}) == claims["alpha_nonzero_values"],
            "alpha values")
    require(len(nonzero) == claims["port77_swap_count"], "nonzero alpha count")
    require(sorted(int(p) for p in nonzero) == sorted(res["port77_swaps"]),
            "swap set equals support of the relation")
    w = res["pr2384_witness_check"]
    require(w["support_within_nuisance"] and not w["optimal_sets_reading_support"],
            "PR2384 witness unread by all optimal sets")
    require(w["axes_from_source"] == WITNESS_2384["axes"], "PR2384 second-axis source binding")
    require(all(x == 0 for x in w["column_relation"]), "PR2384 column relation sum r_p c_p = 0")
    require(w["B0h_identity_owner"] == WITNESS_2384["B0h_identity_owner"]
            and any(w["B0h_identity_owner"]), "PR2384 nonzero target at identity owner")
    # checked last so that perturbation controls report a semantic failure first
    require(res["registered_routes_checked"] == 96 * 8, "registered common-axis route binding")
    require(res["ordinary_gram_is_48I"] and res["selected_gram_is_4I"], "Gram identities")


# ---------------------------------------------------------- negative controls
def controls(packet, phases):
    names = {}

    def reject(name, make):
        try:
            made = make()
            p2, ph2, cl2 = made[:3]
            check(compute(p2, ph2, *made[3:]), cl2)
        except (ValueError, TypeError, ZeroDivisionError) as exc:
            names[name] = "%s: %s" % (type(exc).__name__, exc)
            return
        raise ValueError("negative control accepted: " + name)

    def perturbed_R():
        # port 1 is mandatory because w r_1 = 0; one changed entry breaks that
        p2 = copy.deepcopy(packet)
        row = p2["R_rows"][0]
        row["1"] = str(Fraction(row.get("1", "0")) + 1)
        return p2, phases, CLAIMS

    def perturbed_R_gram_only():
        # changes no rank or classification: only the Gram identity sees it
        p2 = copy.deepcopy(packet)
        row = p2["R_rows"][3]
        row["77"] = str(Fraction(row.get("77", "0")) + 1)
        return p2, phases, CLAIMS

    def swapped_axis():
        ph2 = copy.deepcopy(phases)
        a = ph2["recipes"][77]["idle_children"][0]["orthogonal_axes"]
        b = ph2["recipes"][6]["idle_children"][0]["orthogonal_axes"]
        a[0], b[0] = b[0], a[0]
        return packet, ph2, CLAIMS

    def identity_owner_only():
        p2 = copy.deepcopy(packet)
        p2["map_registry"] = {}
        return p2, phases, CLAIMS

    claim_mutations = [
        ("coloop moved from 77 to 78", {"coloop_ports": [78]}),
        ("wrong optimal set count 46", {"optimal_read_set_count": 46}),
        ("unique optimal set claim", {"optimal_read_set_count": 1}),
        ("65-read threshold claim", {"H_on_V_rank": 65}),
        ("mandatory port 109 dropped",
         {"mandatory_ports": [p for p in CLAIMS["mandatory_ports"] if p != 109]}),
        ("omission 77 replaced by 76",
         {"optimal_omissions": sorted([p for p in CLAIMS["optimal_omissions"] if p != 77] + [76])}),
    ]
    def witness_moved():
        moved = dict(WITNESS_2384, ports=[44, 49, 58, 1])
        return packet, phases, CLAIMS, moved

    def witness_sign():
        flipped = dict(WITNESS_2384, coefficients=[-1, -1, -1, -1])
        return packet, phases, CLAIMS, flipped

    reject("PR2384 witness port 70 moved to mandatory port 1", witness_moved)
    reject("PR2384 witness coefficient sign flipped", witness_sign)
    reject("perturbed R entry (row 0, port 1)", perturbed_R)
    reject("perturbed R entry (row 3, port 77), Gram-only detection", perturbed_R_gram_only)
    reject("swapped first axes of ports 77 and 6", swapped_axis)
    reject("identity owner only (no registered owners)", identity_owner_only)
    for name, delta in claim_mutations:
        reject(name, lambda d=delta: (packet, phases, dict(CLAIMS, **d)))
    return names


def receipt():
    packet, phases = load_sources()
    res = compute(packet, phases)
    check(res)
    ctl = controls(packet, phases)
    res["owner_minor_determinant"] = str(res["owner_minor_determinant"])
    return {
        "schema": "qq16-readset-matroid-independent-v1",
        "status": "PASS_QQ16_READSET_INDEPENDENT",
        "source_sha256": dict(PINS, **{ARCHIVE + "!" + MEMBER: MEMBER_SHA256}),
        "audited_heads": {"PR2389": "aed06c8f8d60ce97b7eb3a7c6c17ad12cbe1e863",
                          "PR2354": "308ebc7405303bb7ed91b012bb705949c6091a16",
                          "PR2384": "b9ef408b1cb0fcd34ab1f1bdbe645573d5de188f"},
        "pr2384_witness_claim": WITNESS_2384,
        "claims_compared": CLAIMS,
        "computed": res,
        "rejected_controls": ctl,
        "scope": ("Finite exact check on the fixed 96-port common-first-axis family; "
                  "no kappa, no supplier, no native schedule replay."),
    }


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--emit", type=Path, help="write a fresh receipt to a NEW path")
    args = ap.parse_args(argv)
    rec = receipt()
    text = json.dumps(rec, indent=1, sort_keys=True) + "\n"
    if args.emit:
        with open(args.emit, "x", encoding="utf-8") as fh:
            fh.write(text)
    else:
        stored = (PACKAGE / "RESULT.json").read_text(encoding="utf-8")
        require(stored == text, "RESULT.json differs from fresh replay")
    r = rec["computed"]
    print("PASS_QQ16_READSET_INDEPENDENT rank_H_V=%d optimal_sets=%d mandatory=%d "
          "nuisance=%d swaps77=%d owner_minor=%dx%d pr2384_witness_unread_by_all=%s "
          "controls=%d no_new_kappa"
          % (r["H_on_V_rank"], r["optimal_read_set_count"], len(r["mandatory_ports"]),
             len(r["nuisance_coordinates"]), len(r["port77_swaps"]),
             len(r["owner_minor_rows"]), len(r["owner_axes"]),
             not r["pr2384_witness_check"]["optimal_sets_reading_support"],
             len(rec["rejected_controls"])))


if __name__ == "__main__":
    main()
