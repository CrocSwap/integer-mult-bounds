#!/usr/bin/env python3
"""Exact premises for the QQ16 adaptive-coordinate theorem.

Prepared for commdata2338 with substantial OpenAI Codex assistance.
Apache-2.0. No predecessor executable is imported. Checks survive Python -O.
"""
import argparse
from collections import defaultdict
from fractions import Fraction
from functools import lru_cache
from hashlib import sha256
import gzip
import json
from math import gcd, lcm
from pathlib import Path
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVE = "research/community-frontier1042-audit/selected-replay.tar.gz"
PACKET = "research/joint-query/certificate.json.gz"
DATA_MEMBER = "t16/global/base/work/complex-nine-native/DATA-PHASES.json"
DATA_SHA = "c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(x):
    return json.dumps(x, sort_keys=True, separators=(",", ":"))


def digest(x):
    return sha256(canonical(x).encode()).hexdigest()


def rref(rows):
    a = [list(map(Fraction, row)) for row in rows]
    need(a and a[0] and all(len(r) == len(a[0]) for r in a), "matrix dimensions")
    pivots = []
    for col in range(len(a[0])):
        k = len(pivots)
        choice = next((i for i in range(k, len(a)) if a[i][col]), None)
        if choice is None:
            continue
        a[k], a[choice] = a[choice], a[k]
        v = a[k][col]
        a[k] = [x / v for x in a[k]]
        for i in range(len(a)):
            if i != k and a[i][col]:
                v = a[i][col]
                a[i] = [x - v * y for x, y in zip(a[i], a[k])]
        pivots.append(col)
        if len(pivots) == len(a):
            break
    return a, pivots


def rank(rows):
    return len(rref(rows)[1])


def nullspace(rows):
    """Primitive integer vectors forming a basis of a rational kernel."""
    a, pivots = rref(rows)
    result = []
    for j in range(len(a[0])):
        if j in pivots:
            continue
        v = [Fraction(0) for _ in a[0]]
        v[j] = 1
        for i, p in enumerate(pivots):
            v[p] = -a[i][j]
        multiple = lcm(*(x.denominator for x in v))
        integers = [int(x * multiple) for x in v]
        divisor = gcd(*integers)
        result.append([x // divisor for x in integers])
    return result


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def determinant(rows):
    """Fraction-free determinant with checked exact divisions."""
    a = [r[:] for r in rows]
    n = len(a)
    need(n and all(len(r) == n for r in a), "square determinant")
    previous, sign = 1, 1
    for k in range(n - 1):
        i = next((i for i in range(k, n) if a[i][k]), None)
        if i is None:
            return 0
        if i != k:
            a[k], a[i] = a[i], a[k]
            sign = -sign
        pivot = a[k][k]
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                value, rem = divmod(a[i][j] * pivot - a[i][k] * a[k][j], previous)
                need(rem == 0, "nonexact determinant division")
                a[i][j] = value
            a[i][k] = 0
        previous = pivot
    return sign * a[-1][-1]


def certify_nonzero_minor(matrix, claimed):
    actual = determinant(matrix)
    need(actual != 0 and actual == claimed, "nonzero exact minor")


def act(columns, v):
    answer = 0
    for i, column in enumerate(columns):
        if v >> i & 1:
            answer ^= column
    return answer


def swap_axes(basis, stage, v):
    """Simultaneous orthogonal swaps, evaluated on the original vector."""
    result = v
    for i, b in enumerate(basis):
        difference = b ^ (1 << (9 + 8 * (stage - 1) + i))
        if (v & difference).bit_count() % 2:
            result ^= difference
    return result


def load():
    sources = json.loads((HERE / "SOURCES.json").read_text())
    pins = {r["path"]: r["sha256"] for r in sources["files"] if r["usage"] == "input"}
    need(set(pins) == {ARCHIVE, PACKET,
        "research/joint-query/evidence/JOINT-QUERY-TRANSFER.md",
        "research/joint-query/evidence/QQ16-SELECTED-WITNESS.json"}, "complete declared source set")
    for path, expected in pins.items():
        need(sha256((ROOT / path).read_bytes()).hexdigest() == expected, "source hash: " + path)
    with tarfile.open(ROOT / ARCHIVE) as archive:
        members = [m for m in archive.getmembers() if m.name == DATA_MEMBER]
        need(len(members) == 1 and members[0].isfile(), "unique data member")
        raw = archive.extractfile(members[0]).read()
        need(sha256(raw).hexdigest() == DATA_SHA, "data member hash")
        data = json.loads(raw)
    packet = json.loads(gzip.decompress((ROOT / PACKET).read_bytes()))
    return packet, data, pins


def decision_tree_controls():
    """Enumerate every adaptive choice on finite, exact oracle problems."""
    inputs = tuple(range(16))
    queries = tuple(tuple((x >> i) & 1 for x in inputs) for i in range(4))
    queries += (tuple(x.bit_count() % 2 for x in inputs),)
    target = tuple(((x & 1) ^ ((x >> 1) & 1),
                    ((x >> 2) & 1) ^ ((x >> 3) & 1)) for x in inputs)

    def solve(qs, labels):
        @lru_cache(None)
        def rec(cell):
            if len({labels[x] for x in cell}) == 1:
                return (0, Fraction(0))
            candidates = []
            for q in qs:
                parts = defaultdict(list)
                for x in cell:
                    parts[q[x]].append(x)
                if len(parts) == 1:
                    continue
                children = [(len(v), rec(tuple(v))) for v in parts.values()]
                worst = 1 + max(cost[0] for _, cost in children)
                mean = 1 + sum(Fraction(n, len(cell)) * cost[1] for n, cost in children)
                candidates.append((worst, mean))
            need(candidates, "oracle cannot distinguish target")
            return min(c[0] for c in candidates), min(c[1] for c in candidates)
        result = rec(inputs)
        return result, rec.cache_info().currsize

    exact, states = solve(queries, target)
    need(exact == (3, Fraction(3)), "adaptive parity oracle optimum")
    dense, _ = solve(queries + (target,), target)
    need(dense == (1, Fraction(1)), "one dense vector query escapes scalar count")
    nonlinear = tuple((x & 1) or ((x >> 1) & 1) for x in inputs)
    nonlin, _ = solve(queries[:4], nonlinear)
    need(nonlin == (2, Fraction(3, 2)), "nonlinear target permits early leaves")
    cell = [x for x in inputs if queries[0][x] == queries[1][x] == 0]
    need(len({target[x] for x in cell}) > 1, "false two-query decoder refuted")
    return {"domain": "F2^4, five scalar linear queries", "states": states,
            "optimal_worst_queries": exact[0], "optimal_mean_queries": str(exact[1]),
            "dense_vector_query_optimum": dense[0],
            "nonlinear_OR_mean_queries": str(nonlin[1])}


def build():
    packet, data, pins = load()
    U, A = packet["U_ports"], packet["A_ports"]
    need(len(U) == 96 and len(set(U)) == 96 and len(A) == 8, "port partition")
    R = [[Fraction(row.get(str(p), "0")) for p in range(112)] for row in packet["R_rows"]]
    need(len(R) == 8 and all(x.denominator == 1 for row in R for x in row), "integer R")
    R = [[int(x) for x in row] for row in R]
    RU = [[r[p] for p in U] for r in R]
    RA = [[r[p] for p in A] for r in R]
    need([[dot(x, y) for y in RU] for x in RU] ==
         [[48 * int(i == j) for j in range(8)] for i in range(8)], "ordinary Gram")
    need([[dot(x, y) for y in RA] for x in RA] ==
         [[4 * int(i == j) for j in range(8)] for i in range(8)], "selected section")
    basis = [recipe["idle_children"][0]["orthogonal_axes"][:8] for recipe in data["recipes"]]
    need(len(basis) == 112 and [r["port"] for r in data["recipes"]] == list(range(112)), "chart order")
    registry = {tuple(m["owner_right_matrix_columns"]) for m in packet["map_registry"].values()}
    identity = tuple(1 << i for i in range(73))
    need(identity in registry, "identity registry entry")
    routes = []
    for bs in basis:
        need(all(0 < b < 512 for b in bs), "chart axes in first nine coordinates")
        need([[(x & y).bit_count() % 2 for y in bs] for x in bs] ==
             [[int(i == j) for j in range(8)] for i in range(8)], "orthonormal chart")
        port_routes = []
        for s in range(1, 9):
            route = tuple(swap_axes(bs, s, v) for v in identity)
            need(route in registry, "registered route")
            need([act(route, b) for b in bs] == [1 << (9 + 8 * (s - 1) + i) for i in range(8)], "common axes")
            port_routes.append(route)
        routes.append(port_routes)
    owners = [identity] + [routes[p][0] for p in range(16)]
    E = [[R[k][p] * (act(owner, basis[p][0]) & 1) for p in U]
         for owner in owners for k in range(8)]
    need(all(any(act(owner, basis[p][0]) & 1 for owner in owners) for p in U), "nonzero coordinate functions")
    groups = defaultdict(list)
    for p in U:
        groups[basis[p][0]].append(p)
    group_ranks = {b: rank([[r[p] for p in ps] for r in R]) for b, ps in groups.items()}
    C = groups[2]
    S = [p for p in U if p not in C]
    need(len(C) == 30 and len(S) == 66 and group_ranks[2] == 8, "30/66 decomposition")
    need(all(group_ranks[b] == len(ps) for b, ps in groups.items() if b != 2), "outside groups independent")
    need(sum(group_ranks.values()) == 74, "group upper bound")

    V = nullspace(RU)
    need(len(V) == 88 and all(dot(r, v) == 0 for r in RU for v in V), "kernel basis")
    EV = [[dot(row, v) for v in V] for row in E]
    # A certificate directly on V; the predecessor instead certifies rank
    # 74 on the full coefficient space. Both describe the same family.
    row_ids = rref(list(map(list, zip(*EV))))[1]
    col_ids = rref([EV[i] for i in row_ids])[1]
    need(len(row_ids) == len(col_ids) == 66, "defect rank")
    minor = [[EV[i][j] for j in col_ids] for i in row_ids]
    det = determinant(minor)
    certify_nonzero_minor(minor, det)

    RC = [[r[p] for p in C] for r in R]
    K = nullspace(RC)
    need(len(K) == 22 and all(dot(r, v) == 0 for r in RC for v in K), "invisible kernel")
    # Exactly one coordinate of C vanishes on ker(H). Classify optimal
    # leaves instead of presuming that the original attaining set is unique.
    nuisance = []
    coloops = []
    for j, p in enumerate(C):
        v = next((v for v in K if v[j]), None)
        deletion_rank = rank([[x for i, x in enumerate(row) if i != j] for row in RC])
        if v is None:
            need(deletion_rank == 7, "coloop deletion rank")
            coloops.append(p)
        else:
            need(deletion_rank == 8, "non-coloop deletion rank")
            nuisance.append({"port": p, "kernel_vector": v, "coordinate_value": v[j]})
    need(coloops == [77] and len(nuisance) == 29, "exact nuisance/coloop classification")
    duals = nullspace([[R[k][p] for k in range(8)] for p in C if p != 77])
    need(len(duals) == 1, "one-dimensional dual space")
    w = duals[0]
    beta = dot(w, [r[77] for r in R])
    need(beta != 0, "coloop dual normalization")
    alpha = {p: Fraction(dot(w, [r[p] for r in R]), beta) for p in S}
    eligible = sorted(S + [77])
    relation = {p: alpha.get(p, Fraction(1)) for p in eligible}
    need(all(v[U.index(77)] + sum(alpha[p] * v[U.index(p)] for p in S) == 0 for v in V),
         "coordinate relation on V")
    optimal_omissions = [p for p in eligible if relation[p] != 0]
    need(len(optimal_omissions) == 45, "45 candidate optimal sets")
    candidate_ranks = []
    for omitted_port in eligible:
        read = [p for p in eligible if p != omitted_port]
        QV = [[v[U.index(p)] for v in V] for p in read]
        actual_rank = rank(QV)
        remaining = [p for p in U if p not in read]
        restriction_rank = 66 + rank([[r[p] for p in remaining] for r in R]) - 8
        need(actual_rank == restriction_rank, "independent coordinate restriction rank")
        need(actual_rank == (66 if omitted_port in optimal_omissions else 65), "optimal-set classification")
        candidate_ranks.append({"omitted_port": omitted_port, "rank": actual_rank})
        if omitted_port != 77 and omitted_port in optimal_omissions:
            for v in V:
                recovered = (-v[U.index(77)] - sum(alpha[p] * v[U.index(p)]
                    for p in S if p != omitted_port)) / alpha[omitted_port]
                need(recovered == v[U.index(omitted_port)], "exchange decoder")
    # Explicit all-owner decoder: sum_{p in S} r_p c_p (f_bp - f_2).
    reconstructed = [[R[k][p] * ((act(owner, basis[p][0]) & 1) - (act(owner, 2) & 1))
                      if p in S else 0 for p in U]
                     for owner in owners for k in range(8)]
    need(all(dot(e, v) == dot(d, v) for e, d in zip(E, reconstructed) for v in V),
         "attaining decoder on complete kernel basis")
    # The all-owner identity follows formally from grouping by the first
    # axis and R_U c=0; no independence of arbitrary bit functions is used.
    for i, owner in enumerate(owners):
        for k in range(8):
            need([x - y for x, y in zip(E[8*i+k], reconstructed[8*i+k])] ==
                 [(act(owner, 2) & 1) * x for x in RU[k]], "decoder difference factors through R_U")

    rejected = []
    def reject(label, f):
        try:
            f()
        except ValueError:
            rejected.append(label)
        else:
            raise ValueError("control accepted: " + label)
    bad = [r[:] for r in minor]
    bad[-1] = bad[0][:]
    reject("singular defect minor", lambda: certify_nonzero_minor(bad, det))
    reject("wrong determinant", lambda: certify_nonzero_minor(minor, det + 1))
    reject("identity owner substituted for whole array", lambda: need(rank(E[:8]) == 66, "owner rank"))
    reject("identity substituted as stage-one route", lambda: need(act(identity, basis[1][0]) == 1 << 9, "route"))
    omitted = [r[:] for r in reconstructed]
    q = U.index(S[0])
    for row in omitted:
        row[q] = 0
    reject("one attaining port omitted", lambda: need(all(dot(e, v) == dot(d, v)
        for e, d in zip(E, omitted) for v in V), "65-port decoder"))
    wrong_sign = [[R[k][p] * ((act(owner, basis[p][0]) & 1) + (act(owner, 2) & 1))
                   if p in S else 0 for p in U] for owner in owners for k in range(8)]
    reject("wrong f2 decoder sign", lambda: need(all(dot(e, v) == dot(d, v)
        for e, d in zip(E, wrong_sign) for v in V), "decoder sign"))
    reject("65 scalar queries claimed enough", lambda: need(65 >= len(row_ids), "rank budget"))
    reject("C coordinate declared constant on invisible kernel", lambda: need(all(v[0] == 0 for v in K), "nuisance"))
    reject("unique optimal set claimed", lambda: need(len(optimal_omissions) == 1, "45 optimal sets"))
    zero_relation_port = next(p for p in eligible if relation[p] == 0)
    reject("zero relation coefficient used for exchange", lambda: need(
        next(row["rank"] for row in candidate_ranks if row["omitted_port"] == zero_relation_port) == 66,
        "singular exchanged read set"))
    reject("JSON Boolean substituted for integer", lambda: need(canonical({"rank": True}) == canonical({"rank": 1}), "type"))
    toy = decision_tree_controls()
    return {"schema": "qq16-adaptive-coordinate-reads-v1", "status": "PASS_QQ16_ADAPTIVE_READS",
            "source_hashes": pins, "data_member_sha256": DATA_SHA,
            "ordinary_dimension": 96, "V_dimension": 88, "H_on_V_rank": 66,
            "H_kernel_dimension": 22, "axis_groups": len(groups),
            "registered_nonzero_routes": 896, "owner_evaluations": 17,
            "V_basis_sha256": digest(V),
            "defect_minor": {"rows": row_ids, "basis_columns": col_ids,
                             "determinant": str(det), "matrix": minor},
            "original_attaining_read_set": S, "unread_axis2_group": C,
            "eligible_optimal_ports": eligible, "optimal_omissions": optimal_omissions,
            "optimal_read_set_count": len(optimal_omissions), "candidate_read_ranks": candidate_ranks,
            "coloop_ports": coloops, "dual_vector": w, "dual_normalizer": beta,
            "coordinate_relation": {str(p): str(a) for p, a in relation.items()},
            "nuisance_witnesses": nuisance,
            "decoder_basis_equalities": len(V) * len(E),
            "adaptive_tree_control": toy, "rejecting_controls": rejected,
            "claim": "Exact side-effect-free coordinate-oracle recovery on the credited rational family; not full controller recovery or a physical cost."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", type=Path, help="Create a new deterministic receipt exclusively")
    args = parser.parse_args()
    result = build()
    if args.emit:
        with args.emit.open("x") as f:
            json.dump(result, f, indent=2, sort_keys=True)
            f.write("\n")
    else:
        expected = json.loads((HERE / "RESULT.json").read_text())
        need(canonical(result) == canonical(expected), "complete receipt equality")
    print("PASS_QQ16_ADAPTIVE_READS defect=66 optimum=66 optimal_sets=45 "
          "nuisance_coordinates=29 controls=" + str(len(result["rejecting_controls"])) + " no_new_kappa")


if __name__ == "__main__":
    main()
