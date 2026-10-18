#!/usr/bin/env python3
"""QQ16 transcript-capacity source checks and exact rational controls.

Prepared for commdata2338, with substantial OpenAI Codex assistance.
Apache-2.0. The trace method is credited to Ross Richardson / PR2104. No predecessor
executable is imported. Quantified claims are proved in PROOF.md.
"""
import argparse
from copy import deepcopy
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PACKET = "research/joint-query/certificate.json.gz"
TAIL = "research/joint-query/evidence/QQ16-SELECTED-WITNESS.json"
BASE = "0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2"
A = [0, 7, 20, 27, 36, 46, 57, 111]
T = [21, 37, 47, 76, 81, 87, 92, 110]
U = [p for p in range(112) if p not in A + T]
AXES = tuple(1 << i for i in range(73))
MARKER = "PASS_QQ16_TRANSCRIPT_CAPACITY"


class Failure(ValueError):
    pass


def need(condition, message):
    if not condition:
        raise Failure(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def read_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            need(key not in result, "duplicate JSON key")
            result[key] = value
        return result
    def nonfinite(value):
        raise Failure("nonfinite JSON: " + value)
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=nonfinite)


def sources(repo):
    manifest = read_json((HERE / "SOURCES.json").read_bytes())
    need(manifest["base_commit"] == BASE, "source base")
    result = {}
    for entry in manifest["files"]:
        if entry["usage"] != "input":
            continue  # Historical provenance is checked by research_package.py.
        raw = (repo / entry["path"]).read_bytes()
        need(digest(raw) == entry["sha256"], "source digest: " + entry["path"])
        result[entry["path"]] = raw
    need({PACKET, TAIL} <= result.keys(), "required source inventory")
    return result


def transpose(a):
    return [list(col) for col in zip(*a)]


def eye(n, scale=1):
    return [[scale * int(i == j) for j in range(n)] for i in range(n)]


def mul(a, b):
    need(len(a[0]) == len(b), "matrix shape")
    return [[sum(x*y for x, y in zip(row, col)) for col in zip(*b)] for row in a]


def mv(a, v):
    return [sum(x*y for x, y in zip(row, v)) for row in a]


def plus(a, b):
    return [x+y for x, y in zip(a, b)]


def neg(v):
    return [-x for x in v]


def sub(a, b):
    return plus(a, neg(b))


def rref(rows):
    a = [list(map(Q, row)) for row in rows]
    need(bool(a) and len({len(row) for row in a}) == 1, "rectangular matrix")
    pivots = []
    for j in range(len(a[0])):
        k = next((i for i in range(len(pivots), len(a)) if a[i][j]), None)
        if k is None:
            continue
        r = len(pivots)
        a[k], a[r] = a[r], a[k]
        scale = a[r][j]
        a[r] = [x/scale for x in a[r]]
        for i in range(len(a)):
            if i != r and a[i][j]:
                factor = a[i][j]
                a[i] = [x-factor*y for x, y in zip(a[i], a[r])]
        pivots.append(j)
        if len(pivots) == len(a):
            break
    return a, pivots


def rank(a):
    return len(rref(a)[1])


def nullspace(a):
    reduced, pivots = rref(a)
    result = []
    for j in range(len(a[0])):
        if j in pivots:
            continue
        v = [Q(0)]*len(a[0])
        v[j] = Q(1)
        for i, p in enumerate(pivots):
            v[p] = -reduced[i][j]
        result.append(v)
    return result


def inverse(a):
    n = len(a)
    reduced, pivots = rref([row+ident for row, ident in zip(a, eye(n))])
    need(pivots == list(range(n)), "invertible selected section")
    return [row[n:] for row in reduced]


def binary_apply(columns, vector):
    result = 0
    while vector:
        bit = vector & -vector
        result ^= columns[bit.bit_length()-1]
        vector ^= bit
    return result


def binary_product(left, right):
    return tuple(binary_apply(left, x) for x in right)


def owner(packet, event):
    need(event[0] == "cover_map", "literal cover-map event")
    columns = tuple(packet["map_registry"][event[2]]["owner_right_matrix_columns"])
    need(len(columns) == 73 and all(type(x) is int and 0 < x < 1 << 73 for x in columns),
         "73-dimensional owner route")
    return columns


def packet_inputs(packet):
    need((packet["A_ports"], packet["T_ports"], packet["U_ports"]) == (A, T, U), "port partition")
    R = [[Q(row.get(str(p), 0)) for p in range(112)] for row in packet["R_rows"]]
    need(len(R) == 8 and all(x.denominator == 1 for row in R for x in row), "integer query matrix")
    R = [[int(x) for x in row] for row in R]
    routes = [[AXES]*112]
    for s in (1, 2):
        word = packet["programs"][f"F_{s}"]
        first = next(i for i, e in enumerate(word) if e[0] == "cover_sweep")
        need(first == 113 and word[first][1] == "X_A_fused_query", "forward alignment boundary")
        alignment = word[1:first]
        need([e[1] for e in alignment] == [["L", p] for p in range(112)], "forward aligned fields")
        routes.append([owner(packet, e) for e in alignment])
    need(packet["programs"]["F_0"][1][:2] == ["cover_sweep", "X_A_fused_query"], "stage-zero identity")
    word = packet["programs"]["B_1_2"]
    future = next(i for i, e in enumerate(word) if e[:2] == ["cover_sweep", "future_E_t"])
    current = next(i for i, e in enumerate(word) if e[:2] == ["cover_sweep", "Y_U_from_X_T"])
    for s, alignment in ((2, word[future-112:future]), (1, word[current-120:current-8])):
        need([e[1] for e in alignment] == [["L", 112+p] for p in range(112)], "backward aligned fields")
        need([owner(packet, e) for e in alignment] == routes[s], "forward/backward route binding")
    selected = word[current-8:current]
    need([e[1] for e in selected] == [["L", p] for p in T], "backward selected aligned fields")
    need([owner(packet, e) for e in selected] == [routes[1][p] for p in T], "selected route binding")
    for row in routes:
        for g in row:
            need(binary_product(g, g) == AXES, "owner route involution")
            need(all((x & y).bit_count() % 2 == int(i == j)
                     for i, x in enumerate(g) for j, y in enumerate(g)), "owner route orthogonality")
    return R, routes


def gram(R, ports):
    columns = [[row[p] for p in ports] for row in R]
    return mul(columns, transpose(columns))


def source_rank_report(R, routes):
    need(gram(R, U) == eye(8, 48), "ordinary Gram")
    need(gram(R, A) == gram(R, T) == eye(8, 4), "selected unit minors")
    need(all(sum(row[p]**2 for row in R) == 4 for p in U), "column norms")
    pairs = []
    for s, t in ((0, 1), (0, 2), (1, 2)):
        relative = [binary_product(routes[s][p], routes[t][p]) for p in U]
        need(len(set(relative)) == 96, "relative-route collision")
        # Collision-free routes leave precisely these diagonal port products.
        coefficient = [[sum(sum(row[p]**2 for row in R)*R[i][p]*R[j][p] for p in U)
                        for j in range(8)] for i in range(8)]
        need(coefficient == eye(8, 192), "cross-Gram identity coefficient")
        pairs.append({"stages": [s, t], "distinct": len(set(relative)),
                      "relative_routes_sha256": digest(canonical(relative)),
                      "identity_coefficient": coefficient})
    trace = 3*sum(gram(R, U)[i][i] for i in range(8))
    square = 3*sum(x*x for row in gram(R, U) for x in row)
    square += 2*sum(sum(p["identity_coefficient"][i][i] for i in range(8)) for p in pairs)
    stack = Q(trace*trace, square)
    need(stack == Q(144, 7), "three-query rank bound")
    defect = stack-8
    need(defect == Q(88, 7) and 12 < defect < 13, "transcript threshold")
    return {"R_sha256": digest(canonical(R)), "pairs": pairs,
            "trace_per_owner": trace, "square_trace_per_owner": square,
            "stack_rank_lower_per_owner": str(stack), "defect_rank_lower_per_owner": str(defect),
            "residual_lower_per_owner_by_q": {str(q): str(max(0, defect-q)) for q in range(17)},
            "first_width_not_excluded": 13, "full_initial_R2_residual_lower_per_owner": str(defect-8)}


def tail_report(events):
    x, y = [0]*4, [1, 0, 0, 0]
    history, stages = [], []
    for e in events:
        if e["kind"] == "bridge":
            src, dst, c = e["src"], e["dst"], e["coefficient"]
            need(src in range(4) and dst in range(4) and src != dst and c in (-1, 1), "bridge domain")
            x[dst] += c*x[src]
            y[src] -= c*y[dst]
        elif e["kind"] == "local":
            s = e["stage"]
            need(s in range(2, 9), "tail stage domain")
            need((x if s % 2 == 0 else y)[s//2 % 4] == 0, "nonzero active tail source")
            stages.append(s)
        else:
            need(e["kind"] == "terminal", "tail event")
            x, y = y, neg(x)
        state = [value for pair in zip(x, y) for value in pair]
        need(state == e["ordinary"], "tail stored state")
        history.append(state)
    need(stages == list(range(2, 9)), "tail stage coverage")
    need(x == [1, 0, 0, 0] and y == [0]*4, "former-Y endpoint")
    return {"states": history, "later_local_stages": stages, "terminal_completed_X": [0]*4}


def fixture_data():
    # Three 2x6 ordinary queries with a full six-row stack; not the actual cover.
    B = [eye(6)[i:i+2] for i in (0, 2, 4)]
    LA = [[[1, 1], [0, 1]], [[1, 0], [1, 1]], [[2, 1], [1, 1]]]
    LT = [[[1, 0], [1, 1]], [[1, 1], [1, 2]], [[1, 2], [0, 1]]]
    PA, PT = [inverse(a) for a in LA], [inverse(t) for t in LT]
    KU = [[[Q(12)*x for x in row] for row in transpose(b)] for b in B]
    return B, LA, LT, PA, PT, KU


def initial(h, data):
    B, LA, LT, PA, PT, _ = data
    b0, b2 = mv(B[0], h), mv(B[2], h)
    xa = neg(plus(mv(PA[0], b0), mv(PA[2], b2)))
    xt = mv(PT[0], mv(LA[0], mv(PA[2], b2)))
    return [h, xa, xt, [Q(0)]*6, neg(xa), neg(xt)]


def full_query(state, s, data):
    B, LA, LT, _, _, _ = data
    xu, xa, xt = state[:3]
    return plus(mv(B[s], xu), plus(mv(LA[s], xa), mv(LT[s], xt)))


def forward(state, data):
    _, LA, LT, PA, PT, KU = data
    xu, xa, xt, yu, ya, yt = state
    f = full_query(state, 0, data)
    a = mv(PA[0], mv(LT[0], xt))
    t = mv(PT[0], f)
    u = sub(xu, mv(KU[0], f))
    return [u, a, t, plus(yu, u), sub(plus(xa, ya), a), sub(plus(xt, yt), t)], f


def backward(state, data):
    B, LA, LT, PA, PT, KU = data
    xu, xa, xt, yu, ya, yt = state
    ua = plus(ya, mv(PA[2], plus(mv(B[2], yu), mv(LT[2], yt))))
    a = mv(LT[1], xt)
    b = plus(mv(B[1], yu), plus(mv(LA[1], ua), mv(LT[1], yt)))
    out_yu = plus(yu, mv(KU[1], a))
    out_yt = sub(yt, mv(PT[1], plus(b, [11*x for x in a])))
    out_xt = mv(PT[1], plus(b, [12*x for x in a]))
    return [sub(xu, yu), sub(plus(xa, ya), ua), out_xt, out_yu, ua, out_yt]


def erased_family_check(state, h, data):
    after_f, f = forward(state, data)
    after_b = backward(after_f, data)
    need(not any(f), "nonzero F0 history")
    need(after_b == [[0]*6, [0]*2, [0]*2, h, [0]*2, [0]*2], "erased two-call endpoint")
    return after_f


def ordered_fixture():
    data = fixture_data()
    B, LA, LT, PA, PT, _ = data
    need(mul(LA[0], LA[2]) != mul(LA[2], LA[0]), "noncommuting fixture")
    basis = nullspace(B[1])
    defects, queries, F_A = [], [], []
    for h in basis:
        state = initial(h, data)
        after_f = erased_family_check(state, h, data)
        xa, xt = state[1:3]
        recovered0 = neg(plus(mv(LA[0], xa), mv(LT[0], xt)))
        recovered2 = mv(LA[2], mv(PA[0], mv(LT[0], xt)))
        need(recovered0 == mv(B[0], h) and recovered2 == mv(B[2], h), "joint defect inverse")
        q = full_query(state, 2, data)
        formula = sub(mv(LT[2], mv(PT[0], mv(LA[0], mv(PA[2], mv(B[2], h))))),
                      mv(LA[2], mv(PA[0], mv(B[0], h))))
        need(q == formula, "ordered full-source query")
        defects.append(xa+xt)
        queries.append(q)
        F_A.append(after_f[1])
    J, C = transpose(defects), transpose(queries)
    need(rank(J) == 4 and rank(C) == 2, "fixture capacities")
    hidden_coefficients = nullspace(C)
    hidden = mul(J, transpose(hidden_coefficients))
    need(rank(hidden) == 2, "full-source residual dimension")
    h = [sum(c*b[i] for c, b in zip(hidden_coefficients[0], basis)) for i in range(6)]
    state = initial(h, data)
    after_f = erased_family_check(state, h, data)
    need(not any(full_query(state, 2, data)) and any(state[1]+state[2]), "invisible full-source witness")
    # A saved F0 A endpoint is EXTRA information, not part of the old observations.
    need(any(after_f[1]), "transient A observation matters")
    # The proposed full query differs from ordinary B2; substitution is unsound.
    need(any(mv(B[2], h)), "full/ordinary-query distinction")
    bpair = transpose([mv(B[0], v)+mv(B[2], v) for v in basis])
    need(rank(bpair) == 4 and rank(bpair+J) == 4, "two-record recovery on family")
    saved = C+transpose(F_A)
    need(rank(saved) == 4, "saved-transient-A capacity control")
    return {"centre_dimension": 2, "ordinary_dimension": 6, "kernel_dimension": len(basis),
            "joint_defect_rank": rank(J), "full_query_rank": rank(C),
            "hidden_defect_rank": rank(hidden), "two_record_rank": rank(bpair),
            "full_query_plus_saved_F0_A_rank": rank(saved),
            "hidden_h": list(map(str, h)), "hidden_initial_X_A": list(map(str, state[1])),
            "hidden_initial_X_T": list(map(str, state[2])),
            "hidden_full_R2_X": list(map(str, full_query(state, 2, data))),
            "hidden_B2_X_U": list(map(str, mv(B[2], h))),
            "transient_F0_X_A": list(map(str, after_f[1]))}


def rank_lemma_controls():
    # Exact small models of dim J(ker C)>=rank(J)-rank(C), independent of QQ16.
    J = [[1, 0, 2, 0, 0], [0, 1, 0, 0, 0], [0, 0, 0, 1, 0]]
    records = [
        [[0]*5], [[1, 0, 0, 0, 0]], [[1, 0, 2, 0, 0], [0, 1, 0, 0, 0]],
        J, [[1, 2, 0, 1, 0], [2, 4, 0, 2, 0]],
        [[0, 0, 0, 0, 1]], eye(5),
    ]
    reports = []
    for C in records:
        kernel = nullspace(C)
        actual = rank(mul(J, transpose(kernel))) if kernel else 0
        identity = rank(C+J)-rank(C)
        lower = max(0, rank(J)-rank(C))
        need(actual == identity and actual >= lower, "rank-restriction lemma")
        reports.append({"record_rank": rank(C), "defect_rank": rank(J),
                        "remaining": actual, "lower": lower})
    need(any(x["remaining"] == x["lower"] > 0 for x in reports), "sharp positive rank fixture")
    need(any(x["remaining"] > x["lower"] for x in reports), "bound need not be sharp")
    need(reports[3]["remaining"] == 0, "sufficient-record control")
    return reports


def reject(function, expected):
    try:
        function()
    except Failure as exc:
        need(expected in str(exc), "unexpected control rejection: " + str(exc))
    else:
        raise Failure("control accepted: " + expected)


def negative_controls(packet, R, routes, events):
    bad = deepcopy(R)
    bad[0][U[0]] += 1
    reject(lambda: source_rank_report(bad, routes), "ordinary Gram")
    bad_routes = deepcopy(routes)
    bad_routes[1][U[1]] = bad_routes[1][U[0]]
    reject(lambda: source_rank_report(R, bad_routes), "relative-route collision")
    altered = deepcopy(packet)
    altered["programs"]["F_1"][1][1] = ["L", 1]
    reject(lambda: packet_inputs(altered), "forward aligned fields")
    bad_tail = deepcopy(events)
    i = next(i for i, e in enumerate(bad_tail) if e.get("coefficient") == -1)
    bad_tail[i]["coefficient"] = 1
    reject(lambda: tail_report(bad_tail), "tail stored state")
    data = fixture_data()
    h = nullspace(data[0][1])[-1]
    bad_state = initial(h, data)
    bad_state[2] = mv(data[3][2], mv(data[1][0], mv(data[4][0], mv(data[0][2], h))))
    bad_state[5] = neg(bad_state[2])
    reject(lambda: erased_family_check(bad_state, h, data), "nonzero F0 history")
    state = initial(h, data)
    state[1] = [0, 0]
    state[4] = [0, 0]
    reject(lambda: erased_family_check(state, h, data), "nonzero F0 history")
    reject(lambda: read_json('{"q":1,"q":2}'), "duplicate JSON key")
    reject(lambda: read_json('{"q":NaN}'), "nonfinite JSON")
    return ["changed_R", "collapsed_route", "misbound_field", "wrong_bridge_sign",
            "commuted_section_order", "missing_A_compensation", "duplicate_key", "nonfinite_number"]


def build(repo):
    raw = sources(repo)
    packet = read_json(gzip.decompress(raw[PACKET]))
    witness = read_json(raw[TAIL])
    need((witness["A"], witness["T"], witness["U"]) == (A, T, U), "tail port binding")
    R, routes = packet_inputs(packet)
    events = witness["trajectory_after_B1"]
    return {"schema": 1, "status": MARKER, "kind": "scoped proof with finite source checks",
            "source_rank": source_rank_report(R, routes), "tail": tail_report(events),
            "ordered_fixture": ordered_fixture(), "rank_lemma_controls": rank_lemma_controls(),
            "negative_controls": negative_controls(packet, R, routes, events),
            "source_sha256": {p: digest(v) for p, v in sorted(raw.items())}}


def validate(expected, actual):
    need(canonical(expected) == canonical(actual), "complete receipt mismatch")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", type=Path, default=ROOT)
    ap.add_argument("--certificate", type=Path, default=HERE / "RESULT.json")
    ap.add_argument("--write", type=Path, help="generate a new receipt, refusing overwrite")
    args = ap.parse_args()
    result = build(args.repo.resolve())
    if args.write:
        with args.write.open("x") as output:
            output.write(json.dumps(result, indent=2, sort_keys=True)+"\n")
        print("GENERATED_QQ16_TRANSCRIPT_CAPACITY")
        return
    expected = read_json(args.certificate.read_bytes())
    validate(expected, result)
    for change in (True, "88/7 altered"):
        mutant = deepcopy(expected)
        mutant["source_rank"]["defect_rank_lower_per_owner"] = change
        reject(lambda: validate(mutant, result), "complete receipt mismatch")
    print(MARKER + " defect>=88|G|/7 q<=12_excluded full_R2_X_insufficient")


if __name__ == "__main__":
    main()
