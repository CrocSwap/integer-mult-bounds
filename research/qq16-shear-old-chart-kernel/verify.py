#!/usr/bin/env python3
"""Exact checks for the scoped QQ16 old-chart kernel argument.

Apache-2.0. The three-query trace method is credited to Ross Richardson / PR2104;
packet binding follows commdata2338 / PR2153. Local maps and tail schedule are
credited to Ali Romman / PR1969, with the corrected tail binding from PR2174.
"""

from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PACKET = "research/joint-query/certificate.json.gz"
TAIL = "research/joint-query/evidence/QQ16-SELECTED-WITNESS.json"
RECIPE = "research/community-reconciliation-third100-audit/regenerated/pr377-outputs/work/odd-stages/RECIPE-9.json.gz"
A = [0, 7, 20, 27, 36, 46, 57, 111]
T = [21, 37, 47, 76, 81, 87, 92, 110]
U = [p for p in range(112) if p not in A + T]
AXES = tuple(1 << i for i in range(73))
MARKER = "PASS_QQ16_SHEAR_OLD_CHART_KERNEL"


class Failure(ValueError):
    pass


def need(condition, message):
    if not condition:
        raise Failure(message)


def read_json(raw, label):
    def pairs(items):
        result = {}
        for key, value in items:
            need(key not in result, label + ": duplicate JSON key " + key)
            result[key] = value
        return result

    def constant(value):
        raise Failure(label + ": nonfinite JSON value " + value)

    try:
        return json.loads(raw, object_pairs_hook=pairs, parse_constant=constant)
    except Failure:
        raise
    except (ValueError, UnicodeDecodeError, TypeError) as exc:
        raise Failure(label + ": invalid JSON: " + str(exc)) from exc


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def load_sources():
    manifest = read_json((HERE / "SOURCES.json").read_bytes(), "SOURCES.json")
    need(manifest.get("schema_version") == 1 and isinstance(manifest.get("files"), list),
         "source manifest schema")
    inputs, seen = {}, set()
    for entry in manifest["files"]:
        need(isinstance(entry, dict) and isinstance(entry.get("path"), str), "source entry")
        if entry.get("usage") != "input":
            continue
        path = entry["path"]
        need(path not in seen, "duplicate input path: " + path)
        seen.add(path)
        source = (ROOT / path).resolve()
        need(source.is_relative_to(ROOT), "source path escapes repository: " + path)
        try:
            raw = source.read_bytes()
        except OSError as exc:
            raise Failure("missing source input: " + path) from exc
        need(isinstance(entry.get("sha256"), str) and digest(raw) == entry["sha256"],
             "source digest: " + path)
        inputs[path] = raw
    required = {PACKET, TAIL, RECIPE}
    need(required <= inputs.keys(), "required input pins missing: " + ", ".join(sorted(required - inputs.keys())))
    return inputs


def eye(n, scale=1):
    return [[Q(scale if i == j else 0) for j in range(n)] for i in range(n)]


def transpose(a):
    need(bool(a) and all(len(row) == len(a[0]) for row in a), "matrix is rectangular")
    return [list(col) for col in zip(*a)]


def add(a, b, factor=1):
    need(len(a) == len(b), "vector addition shape")
    return [x + factor * y for x, y in zip(a, b)]


def scale(a, factor):
    return [factor * x for x in a]


def matmul(a, b):
    need(bool(a) and bool(b) and all(len(row) == len(a[0]) for row in a), "left matrix shape")
    need(all(len(row) == len(b[0]) for row in b) and len(a[0]) == len(b), "matrix product shape")
    bt = transpose(b)
    return [[sum((x * y for x, y in zip(row, col)), Q(0)) for col in bt] for row in a]


def mv(a, v):
    need(bool(a) and all(len(row) == len(v) for row in a), "matrix-vector shape")
    return [sum((x * y for x, y in zip(row, v)), Q(0)) for row in a]


def rref(rows):
    need(bool(rows) and all(len(row) == len(rows[0]) for row in rows), "elimination matrix shape")
    a = [list(map(Q, row)) for row in rows]
    pivots = []
    for j in range(len(a[0])):
        pivot = next((i for i in range(len(pivots), len(a)) if a[i][j]), None)
        if pivot is None:
            continue
        r = len(pivots)
        a[pivot], a[r] = a[r], a[pivot]
        a[r] = [x / a[r][j] for x in a[r]]
        for i in range(len(a)):
            if i != r and a[i][j]:
                k = a[i][j]
                a[i] = [x - k * y for x, y in zip(a[i], a[r])]
        pivots.append(j)
        if len(pivots) == len(a):
            break
    return a, pivots


def rank(a):
    return len(rref(a)[1])


def inverse(a):
    n = len(a)
    reduced, pivots = rref([list(row) + ident for row, ident in zip(a, eye(n))])
    need(pivots == list(range(n)), "selected chart matrix is invertible")
    return [row[n:] for row in reduced]


def columns(a, ports):
    return [[row[p] for p in ports] for row in a]


def rows(a, ports):
    return [a[p][:] for p in ports]


def parse_rational_rows(sparse_rows, nrows, ncols, label):
    need(isinstance(sparse_rows, list) and len(sparse_rows) == nrows, label + " row count")
    out = []
    for row in sparse_rows:
        need(isinstance(row, dict), label + " sparse row")
        need(all(isinstance(k, str) and k.isdecimal() and int(k) < ncols for k in row),
             label + " column key")
        values = []
        for j in range(ncols):
            value = row.get(str(j), 0)
            need(type(value) is int or isinstance(value, str), label + " rational encoding")
            try:
                values.append(Q(value))
            except (ValueError, ZeroDivisionError) as exc:
                raise Failure(label + " invalid rational") from exc
        out.append(values)
    return out


def parse_packet(raw):
    try:
        packet = read_json(gzip.decompress(raw), "QQ16 packet")
    except (OSError, EOFError) as exc:
        raise Failure("QQ16 packet gzip") from exc
    need((packet.get("A_ports"), packet.get("T_ports"), packet.get("U_ports")) == (A, T, U),
         "packet A/T/U partition")
    need(set(A + T + U) == set(range(112)) and len(set(A + T + U)) == 112,
         "packet ports are disjoint and complete")
    R = parse_rational_rows(packet.get("R_rows"), 8, 112, "R_rows")
    K = parse_rational_rows(packet.get("K_rows"), 112, 8, "K_rows")
    return packet, R, K


def check_packet_grams(R, K):
    ru = columns(R, U)
    need(matmul(ru, transpose(ru)) == eye(8, 48), "ordinary Gram R_U R_U^T = 48I")
    need(all(sum((R[i][p] * R[i][p] for i in range(8)), Q(0)) == 4 for p in U),
         "ordinary column norm 4")
    for label, ports in (("A", A), ("T", T)):
        block = columns(R, ports)
        need(matmul(block, transpose(block)) == eye(8, 4), "selected " + label + " Gram = 4I")
        section = rows(K, ports)
        need(matmul(block, section) == matmul(section, block) == eye(8),
             "selected " + label + " query/section two-sided inverse")
    need(K == [[R[j][i] / 4 for j in range(8)] for i in range(112)],
         "K_rows equals R transpose divided by 4")
    ku = rows(K, U)
    common_products = []
    for stage in range(3):
        need(matmul(ru, ku) == eye(8, 12), "common-chart R_%d K_(%d,U) = 12I" % (stage, stage))
        common_products.append("12I")
    return {"ordinary_gram": "48I", "ordinary_columns": 96, "ordinary_column_norm": 4,
            "selected_grams": ["4I", "4I"], "common_chart_Rs_KsU": common_products}


def binary_apply(g, vector):
    result = 0
    while vector:
        bit = vector & -vector
        result ^= g[bit.bit_length() - 1]
        vector ^= bit
    return result


def binary_product(left, right):
    return tuple(binary_apply(left, vector) for vector in right)


def owner_route(packet, event):
    need(isinstance(event, list) and len(event) >= 3 and event[0] == "cover_map",
         "literal cover-map alignment event")
    key = event[2]
    entry = packet.get("map_registry", {}).get(key)
    need(isinstance(entry, dict), "literal alignment map registry entry")
    route = entry.get("owner_right_matrix_columns")
    need(isinstance(route, list) and len(route) == 73 and
         all(type(v) is int and 0 <= v < 1 << 73 for v in route), "73-bit owner route")
    return tuple(route)


def alignment_routes(packet, events, offset):
    need(len(events) == 112, "literal route alignment width")
    result = []
    for p, event in enumerate(events):
        need(event[1] == ["L", offset + p], "literal route field order")
        result.append(owner_route(packet, event))
    return result


def packet_routes(packet):
    programs = packet.get("programs", {})
    f0 = programs.get("F_0", [])
    need(len(f0) > 1 and f0[0][:3] == ["retained_core", "forward", 0], "stage-zero forward word")
    need(f0[1][:2] == ["cover_sweep", "X_A_fused_query"], "stage-zero identity boundary")
    need(not any(event[0] == "cover_map" for event in f0[:1]), "stage-zero identity routes")
    routes = [[tuple(1 << i for i in range(73)) for _ in range(112)]]
    for stage in (1, 2):
        word = programs.get("F_" + str(stage), [])
        need(len(word) > 113 and word[0][:3] == ["retained_core", "forward", stage],
             "stage-%d forward word" % stage)
        need(word[113][:2] == ["cover_sweep", "X_A_fused_query"],
             "stage-%d initial alignment boundary" % stage)
        routes.append(alignment_routes(packet, word[1:113], 0))
    backward = programs.get("B_1_2", [])
    future = [i for i, e in enumerate(backward) if e[:2] == ["cover_sweep", "future_E_t"]]
    current = [i for i, e in enumerate(backward) if e[:2] == ["cover_sweep", "Y_U_from_X_T"]]
    need(len(future) == len(current) == 1, "unique B_1_2 current/future alignment blocks")
    fi, ci = future[0], current[0]
    future_events = backward[fi - 112:fi]
    current_events = backward[ci - 120:ci - 8]
    selected_events = backward[ci - 8:ci]
    need(alignment_routes(packet, future_events, 112) == routes[2],
         "B_1_2 future alignment equals literal F_2 initial alignment")
    need(alignment_routes(packet, current_events, 112) == routes[1],
         "B_1_2 current alignment equals literal F_1 initial alignment")
    need(len(selected_events) == len(T), "B_1_2 selected current alignment width")
    need([e[1] for e in selected_events] == [["L", p] for p in T],
         "B_1_2 selected current field order")
    need([owner_route(packet, e) for e in selected_events] == [routes[1][p] for p in T],
         "B_1_2 selected routes equal current F_1 routes")
    for stage, stage_routes in enumerate(routes):
        for route in stage_routes:
            need(binary_product(route, route) == AXES, "owner route involution stage %d" % stage)
            need(all((x & y).bit_count() % 2 == int(i == j)
                     for i, x in enumerate(route) for j, y in enumerate(route)),
                 "owner route orthogonality stage %d" % stage)
    return routes


def distinct_relative_routes(routes):
    reports = []
    for s, t in ((0, 1), (0, 2), (1, 2)):
        relative = [binary_product(routes[s][p], routes[t][p]) for p in U]
        need(len(set(relative)) == 96, "relative-route collision for stages %d,%d" % (s, t))
        reports.append({"stages": [s, t], "distinct_ordinary_routes": len(set(relative))})
    return reports


def source_moment_report(R, routes):
    route_pairs = distinct_relative_routes(routes)
    ru = columns(R, U)
    gram = matmul(ru, transpose(ru))
    weighted = [[sum((sum((R[k][p] ** 2 for k in range(8)), Q(0)) * R[i][p] * R[j][p]
                        for p in U), Q(0)) for j in range(8)] for i in range(8)]
    need(weighted == eye(8, 192), "cross-Gram identity coefficient 192I")
    trace = 3 * sum((gram[i][i] for i in range(8)), Q(0))
    square_trace = 3 * sum((x * x for row in gram for x in row), Q(0))
    square_trace += 2 * 3 * sum((weighted[i][i] for i in range(8)), Q(0))
    rank_lower = Q(trace * trace, square_trace)
    residual = rank_lower - 16
    need(trace == 1152 and square_trace == 64512, "three-query trace moments")
    need(rank_lower == Q(144, 7), "three-query rank lower bound")
    need(residual == Q(32, 7), "old-chart residual lower bound")
    return {"trace_per_owner": str(trace), "square_trace_per_owner": str(square_trace),
            "rank_lower_per_owner": str(rank_lower), "residual_lower_per_owner": str(residual),
            "integer_bound": "ceil(32N/7)", "relative_routes": route_pairs}


def fixture(C):
    # Distinct upper/lower unipotents give noncommuting selected A/T charts.
    P = [
        {"A": [[1, 1], [0, 1]], "T": [[1, 0], [1, 1]]},
        {"A": [[2, 1], [1, 1]], "T": [[1, 1], [0, 1]]},
        {"A": [[1, 2], [0, 1]], "T": [[1, 0], [0, Q(1, 2)]]},
    ]
    E = [{kind: inverse(P[s][kind]) for kind in ("A", "T")} for s in range(3)]
    need(matmul(P[0]["A"], P[0]["T"]) != matmul(P[0]["T"], P[0]["A"]),
         "fixture selected A/T charts do not commute")
    need(matmul(C, inverse(C)) == matmul(inverse(C), C) == eye(2), "fixture shear C invertible")
    B = []
    for start in (0, 2, 4):
        B.append([[Q(int(j == start + i)) for j in range(6)] for i in range(2)])
    K = [scale_row(transpose(b), 12) for b in B]
    L = matmul(matmul(E[1]["T"], C), P[0]["A"])
    M = matmul(add_matrix(E[2]["A"], matmul(E[2]["T"], C)), P[0]["A"])
    return {"P": P, "E": E, "B": B, "K": K, "C": C, "L": L, "M": M}


def scale_row(a, factor):
    return [[factor * x for x in row] for row in a]


def add_matrix(a, b, factor=1):
    need(len(a) == len(b) and all(len(x) == len(y) for x, y in zip(a, b)), "matrix addition shape")
    return [[x + factor * y for x, y in zip(ar, br)] for ar, br in zip(a, b)]


def query(ch, stage, side):
    return add(add(mv(ch["B"][stage], side[0]), mv(ch["E"][stage]["A"], side[1])),
                   mv(ch["E"][stage]["T"], side[2]))


def forward(ch, pair):
    x, y = pair
    q = query(ch, 0, x)
    z = add(x[0], mv(ch["K"][0], q), -1)
    a = mv(ch["E"][0]["A"], x[1])
    a = add(add(scale(a, -1), mv(ch["B"][0], z), -1), scale(q, 11), -1)
    nx = [z, mv(ch["P"][0]["A"], a), mv(ch["P"][0]["T"], q)]
    ny = [add(y[0], z), add(add(x[1], y[1]), nx[1], -1), add(add(x[2], y[2]), nx[2], -1)]
    return [nx, ny], q


def backward(ch, future, pair):
    x, y = pair
    u = [v[:] for v in y]
    u[1] = add(u[1], mv(future["P"]["A"], add(mv(future["B"], y[0]),
                                                       mv(future["E"]["T"], y[2]))))
    a = mv(ch["E"][1]["T"], x[2])
    b = query(ch, 1, u)
    v = [part[:] for part in u]
    v[2] = add(v[2], mv(ch["P"][1]["T"], add(a, b, -1)))
    rv = query(ch, 1, v)
    ny = [add(v[0], mv(ch["K"][1], rv)), v[1],
          add(v[2], mv(ch["P"][1]["T"], scale(rv, 12)), -1)]
    nx = [add(x[0], y[0], -1), add(add(x[1], y[1]), ny[1], -1),
          add(add(x[2], y[2]), ny[2], -1)]
    return [nx, ny]


def initial_state(ch, c, coefficient=-11, M=None):
    L, matrix = ch["L"], ch["M"] if M is None else M
    lc, mc = mv(L, c), mv(matrix, c)
    w = [Q(0), Q(0)] + scale(lc, coefficient) + mc
    xa, xt = scale(mv(ch["P"][0]["A"], c), -1), mv(ch["P"][0]["T"], c)
    ya, yt = scale(mv(ch["P"][0]["A"], c), 1), scale(xt, -1)
    return [[w, xa, xt], [[Q(0)] * 6, ya, yt]], w


def shear(pair, C, y_sign=-1):
    x, y = pair
    out = [[v[:] for v in x], [v[:] for v in y]]
    out[0][2] = add(out[0][2], mv(C, x[1]))
    out[1][2] = add(out[1][2], mv(C, x[1]), y_sign)
    return out


def selected_sums(pair):
    return [add(pair[0][i], pair[1][i]) for i in (1, 2)]


def require_selected_invisible(pair):
    if any(any(vector) for side in pair for vector in side[1:]):
        raise Failure("selected invisibility: a post-B1 A/T coordinate is nonzero")


def run_witness(ch, c, coefficient=-11, M=None, shear_y_sign=-1):
    original, w = initial_state(ch, c, coefficient, M)
    pair_sums = selected_sums(original)
    after_f, f0 = forward(ch, original)
    need(selected_sums(after_f) == pair_sums, "selected pair sum after F0")
    after_shear = shear(after_f, ch["C"], shear_y_sign)
    need(selected_sums(after_shear) == pair_sums, "selected pair sum after paired shear")
    q2 = query(ch, 2, after_shear[1])
    after_b = backward(ch, {"P": {"A": ch["P"][2]["A"]}, "B": ch["B"][2], "E": {"T": ch["E"][2]["T"]}},
                       after_shear)
    need(selected_sums(after_b) == pair_sums, "selected pair sum after B1")
    return {"initial": original, "w": w, "f0": f0, "q0": mv(ch["B"][0], original[0][0]),
            "q2": q2, "after_f": after_f, "after_shear": after_shear, "after_b": after_b}


def rank_intersection_fixture(ch):
    S = ch["B"][0] + ch["B"][1] + ch["B"][2]
    zero = [[Q(0), Q(0)] for _ in range(2)]
    H = zero + scale_row(ch["L"], -11) + ch["M"]
    joined = [list(row) + list(extra) for row, extra in zip(S, H)]
    rs, rh, rjoin = rank(S), rank(H), rank(joined)
    exact_intersection = rs + rh - rjoin
    analytic_lower = rs + rh - len(S)
    need(rs == 6 and rh == 2 and rjoin == 6, "exact-elimination fixture ranks")
    need(exact_intersection == analytic_lower == 2, "fixture intersection is sharp")
    return {"rank_S": rs, "rank_H": rh, "rank_join": rjoin,
            "intersection_dimension": exact_intersection, "sharp": True}


def reject(function, expected):
    try:
        function()
    except Failure as exc:
        need(expected in str(exc), "negative control rejected for wrong reason: " + str(exc))
    else:
        raise Failure("negative control accepted: " + expected)


def positive_fixture():
    identities = eye(2)
    swap = [[Q(0), Q(1)], [Q(1), Q(0)]]
    reports = []
    noncommuting = fixture(swap)
    need(matmul(noncommuting["E"][2]["T"], swap) != matmul(swap, noncommuting["E"][2]["T"]),
         "fixture shear C does not commute with selected chart")
    for C, label in ((identities, "identity"), (swap, "noncommuting")):
        ch = fixture(C)
        controls = {"basis_vectors": 2}
        for i in range(2):
            c = [Q(int(j == i)) for j in range(2)]
            result = run_witness(ch, c)
            p0a = mv(ch["P"][0]["A"], c)
            cp0a = mv(C, p0a)
            zero2 = [Q(0)] * 2
            expected_f = [[result["w"], p0a, zero2],
                          [result["w"], scale(p0a, -1), zero2]]
            need(result["after_f"] == expected_f, "every conserved F0 output coordinate")
            expected_shear = [[result["w"], p0a, cp0a],
                              [result["w"], scale(p0a, -1), scale(cp0a, -1)]]
            need(result["after_shear"] == expected_shear, "every paired-shear output coordinate")
            need(result["q0"] == [0, 0], "retained q0 is zero")
            need(result["f0"] == [0, 0], "F0 query history is zero")
            need(result["q2"] == [0, 0], "future B2 query is zero")
            need(mv(ch["B"][0], result["w"]) == [0, 0] and
                 mv(ch["B"][1], result["w"]) == scale(mv(ch["L"], c), -11) and
                 mv(ch["B"][2], result["w"]) == mv(ch["M"], c),
                 "constructed w satisfies B0/B1/B2 equations")
            need(any(v for side in result["initial"] for vec in side[1:] for v in vec),
                 "original selected defect is nonzero")
            need(result["w"] == [Q(0), Q(0)] + scale(mv(ch["L"], c), -11) + mv(ch["M"], c),
                 "constructed ordinary vector satisfies all three B_s equations")
            h = add(result["w"], mv(ch["K"][1], mv(ch["L"], c)))
            expected = [[Q(0)] * 6, [Q(0)] * 2, [Q(0)] * 2]
            need(result["after_b"][0] == expected and result["after_b"][1] == [h, [Q(0)] * 2, [Q(0)] * 2],
                 "all post-B1 output coordinates equal the ordered kernel form")
            require_selected_invisible(result["after_b"])
        reports.append({"C": label, "basis_vectors": controls["basis_vectors"],
                        "f0_q0_q2_zero": True, "selected_outputs_zero": True,
                        "finite_rational_regression_only": True})
    return reports, rank_intersection_fixture(noncommuting)


def negative_controls(R, routes, events, trajectory):
    bad_R = [row[:] for row in R]
    bad_R[0][U[0]] += 1
    reject(lambda: check_packet_grams(bad_R, [[Q(0)] * 8 for _ in range(112)]),
           "ordinary Gram")
    bad_routes = [[list(stage) for stage in route_set] for route_set in routes]
    bad_routes[1][U[1]] = bad_routes[1][U[0]]
    reject(lambda: distinct_relative_routes(bad_routes), "relative-route collision")

    C = [[Q(1), Q(0)], [Q(0), Q(1)]]
    ch = fixture(C)
    c = [Q(1), Q(0)]
    state, _ = initial_state(ch, c)
    after_f, _ = forward(ch, state)
    wrong = shear(after_f, C, 1)
    reject(lambda: need(selected_sums(wrong) == selected_sums(after_f), "selected pair sum"),
           "selected pair sum")

    for c in ([Q(1), Q(0)], [Q(0), Q(1)]):
        bad_ten = run_witness(ch, c, coefficient=-10)
        reject(lambda bad=bad_ten: require_selected_invisible(bad["after_b"]), "selected invisibility")

    swapped = [[Q(0), Q(1)], [Q(1), Q(0)]]
    ch = fixture(swapped)
    reverse_M = matmul(add_matrix(ch["E"][2]["A"], matmul(swapped, ch["E"][2]["T"])),
                       ch["P"][0]["A"])
    for c in ([Q(1), Q(0)], [Q(0), Q(1)]):
        reversed_result = run_witness(ch, c, M=reverse_M)
        reject(lambda result=reversed_result: require_selected_invisible(result["after_b"]),
               "selected invisibility")

    tail = events[2:]
    first_negative = next(i for i, event in enumerate(tail)
                          if event.get("kind") == "bridge" and event.get("coefficient") == -1)
    omitted = tail[:first_negative] + tail[first_negative + 1:]
    reject(lambda: replay_tail(omitted, trajectory), "backward tail source is zero")
    return ["changed_R_gram", "duplicate_relative_route", "wrong_shear_sign_pair_sum",
            "coefficient_minus_10_invisible", "reversed_M_factor_invisible", "omitted_first_negative_bridge"]


def bind_tail(raw_recipe, witness):
    try:
        recipe = read_json(gzip.decompress(raw_recipe), "RECIPE-9")
    except (OSError, EOFError) as exc:
        raise Failure("RECIPE-9 gzip") from exc
    need(len(recipe) == 19 and recipe[-1] == {"kind": "terminal", "pairs": 4},
         "retained 19-event schedule boundary")
    locals_all = [event for event in recipe if event.get("kind") == "local"]
    need([(e.get("stage"), e.get("pair"), e.get("reverse")) for e in locals_all] == [
        (0, 0, False), (1, 0, True), (2, 0, False), (3, 1, True), (4, 1, False),
        (5, 2, True), (6, 2, False), (7, 3, True), (8, 3, False)],
        "retained local pair schedule")
    tail = recipe[2:]
    trajectory = witness.get("trajectory_after_B1")
    need(len(tail) == len(trajectory) == 17, "retained tail/witness event coverage")
    for actual, old in zip(tail, trajectory):
        for key in ("kind", "stage", "src", "dst", "coefficient"):
            if key in actual or key in old:
                need(actual.get(key) == old.get(key), "retained tail/witness event binding: " + key)
    return tail


def replay_tail(events, trajectory):
    # Each entry is a coefficient of arbitrary formal h, not a numeric witness.
    x, y = [Q(0)] * 4, [Q(1), Q(0), Q(0), Q(0)]
    for i, event in enumerate(events):
        kind = event.get("kind")
        if kind == "bridge":
            src, dst, coefficient = event.get("src"), event.get("dst"), event.get("coefficient")
            need(src in range(4) and dst in range(4) and src != dst and coefficient in (-1, 1),
                 "tail bridge domain")
            x[dst] += coefficient * x[src]
            y[src] -= coefficient * y[dst]
        elif kind == "local":
            stage, pair = event.get("stage"), event.get("pair")
            need(stage in range(2, 9) and pair in range(4) and event.get("reverse") == bool(stage % 2),
                 "tail local event domain")
            if event["reverse"]:
                need(y[pair] == 0, "backward tail source is zero")
                x[pair] -= y[pair]
            else:
                need(x[pair] == 0, "forward tail source is zero")
                y[pair] += x[pair]
        else:
            need(kind == "terminal" and event.get("pairs") == 4, "tail terminal event")
            x, y = y, [-value for value in x]
        need(i < len(trajectory), "tail has excess events")
        state = [value for pair in zip(x, y) for value in pair]
        expected = trajectory[i].get("ordinary")
        need(expected is not None and state == [Q(value) for value in expected],
             "tail trajectory state at event %d" % i)
    need(len(events) == len(trajectory), "tail event count")
    need(y[0] == 0 and x[0] == 1, "final completed-X Y=0 and former-Y X0=h")
    return {"events": len(events), "local_pairs_stages_0_to_8": [0, 0, 0, 1, 1, 2, 2, 3, 3],
            "final_completed_X_named_Y": str(y[0]), "final_former_Y_named_X0": str(x[0]),
            "arbitrary_formal_h": True}


def verify():
    raw = load_sources()
    packet, R, K = parse_packet(raw[PACKET])
    witness = read_json(raw[TAIL], "QQ16 selected witness")
    need((witness.get("A"), witness.get("T"), witness.get("U")) == (A, T, U),
         "tail witness A/T/U binding")
    gram_report = check_packet_grams(R, K)
    routes = packet_routes(packet)
    moment_report = source_moment_report(R, routes)

    fixtures, sharp = positive_fixture()
    events = bind_tail(raw[RECIPE], witness)
    tail_report = replay_tail(events, witness["trajectory_after_B1"])
    recipe = read_json(gzip.decompress(raw[RECIPE]), "RECIPE-9")
    controls = negative_controls(R, routes, recipe, witness["trajectory_after_B1"])
    return {"scope": "scoped rational fixture and retained-source checks; not a formal proof or native replay",
            "sources_sha256": {path: digest(value) for path, value in sorted(raw.items())},
            "packet": gram_report, "moment_recheck": moment_report,
            "positive_fixtures": fixtures, "fixture_intersection": sharp,
            "tail": tail_report, "negative_controls": controls}


def main():
    try:
        result = verify()
    except Failure as exc:
        print("FAIL_QQ16_SHEAR_OLD_CHART_KERNEL: " + str(exc), file=sys.stderr)
        return 1
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    print(MARKER)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
