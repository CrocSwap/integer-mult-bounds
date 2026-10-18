#!/usr/bin/env python3
"""Exact QQ16 residual audit: retained R certificate and transvection routes.

No predecessor executable is imported. The independent oracle instead uses
reverse covectors and chart-axis swaps. Apache-2.0; OpenAI Codex assistance.
"""
import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
import gzip
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tarfile

HERE = Path(__file__).resolve().parent
BASE = "0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2"
ARCHIVE = "research/community-frontier1042-audit/selected-replay.tar.gz"
PHASE_MEMBER = "t16/global/base/work/complex-nine-native/DATA-PHASES.json"
PHASE_SHA = "c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa"
PACKET = "research/joint-query/certificate.json.gz"
TAIL = "research/joint-query/evidence/QQ16-SELECTED-WITNESS.json"
A = [0, 7, 20, 27, 36, 46, 57, 111]
T = [21, 37, 47, 76, 81, 87, 92, 110]
U = [p for p in range(112) if p not in A + T]
AXES = tuple(1 << k for k in range(73))

class CheckError(ValueError):
    pass

def require(ok, why):
    if not ok:
        raise CheckError(why)

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()

def authenticate(repo):
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    require(manifest["base_commit"] == BASE, "source base")
    sources = {}
    for entry in manifest["files"]:
        path = entry["path"]
        raw = subprocess.check_output(["git", "show", BASE + ":" + path], cwd=repo)
        blob = subprocess.check_output(["git", "rev-parse", BASE + ":" + path], cwd=repo).decode().strip()
        require(digest(raw) == entry["sha256"] and blob == entry["git_blob"], "provenance: " + path)
        if entry["usage"] == "input":
            require((repo / path).read_bytes() == raw, "live source: " + path)
            sources[path] = raw
    require({ARCHIVE, PACKET, TAIL} <= sources.keys(), "required source inventory")
    return sources

def load_inputs(sources):
    packet = json.loads(gzip.decompress(sources[PACKET]))
    require((packet["A_ports"], packet["T_ports"], packet["U_ports"]) == (A, T, U), "selected port partition")
    require(len(packet["R_rows"]) == 8, "eight query rows")
    R = [[Q(row.get(str(p), 0)) for p in range(112)] for row in packet["R_rows"]]
    require(all(x.denominator == 1 for row in R for x in row), "integer R")
    R = [[int(x) for x in row] for row in R]
    with tarfile.open(fileobj=io.BytesIO(sources[ARCHIVE]), mode="r:gz") as archive:
        members = [m for m in archive.getmembers() if m.name == PHASE_MEMBER]
        require(len(members) == 1 and members[0].isfile(), "unique phase member")
        raw = archive.extractfile(members[0]).read()
        require(digest(raw) == PHASE_SHA, "phase member digest")
        phases = json.loads(raw)
    return R, phases, json.loads(sources[TAIL])

def apply(columns, x):
    y = 0
    while x:
        bit = x & -x
        y ^= columns[bit.bit_length() - 1]
        x ^= bit
    return y

def compose(left, right):
    return tuple(apply(left, c) for c in right)

def routes_from_transvections(phases):
    require(phases["m"] == 73 and len(phases["recipes"]) == 112, "phase dimensions")
    routes = [[], [], []]
    for p, record in enumerate(phases["recipes"]):
        require(record["port"] == p, "phase port order")
        chart = [record["q"]] + record["idle_children"][0]["orthogonal_axes"][:8]
        require(len(chart) == 9 and all(0 < c < 512 for c in chart), "local chart support")
        require(all((x & y).bit_count() % 2 == int(i == j)
                    for i, x in enumerate(chart) for j, y in enumerate(chart)), "chart orthogonality")
        routes[0].append(AXES)
        for stage in (1, 2):
            normals = [chart[i + 1] ^ AXES[9 + 8 * (stage - 1) + i] for i in range(8)]
            matrix = tuple(x ^ apply(normals, sum(((x & n).bit_count() % 2) << i
                                                 for i, n in enumerate(normals))) for x in AXES)
            require(compose(matrix, matrix) == AXES, "route inverse")
            require(all((x & y).bit_count() % 2 == int(i == j)
                        for i, x in enumerate(matrix) for j, y in enumerate(matrix)), "route orthogonality")
            routes[stage].append(matrix)
    return routes

def gram(R, ports):
    return [[sum(R[i][p] * R[j][p] for p in ports) for j in range(8)] for i in range(8)]

def diagonal(k):
    return [[k * int(i == j) for j in range(8)] for i in range(8)]

def cross_coefficient(R, routes, s, t, ports=U):
    """Group equal relative routes, then compute sum_g C_g C_g^T exactly."""
    grouped = {}
    for p in ports:
        g = compose(routes[s][p], routes[t][p])  # checked involutions
        matrix = grouped.setdefault(g, diagonal(0))
        for i in range(8):
            for j in range(8):
                matrix[i][j] += R[i][p] * R[j][p]
    result = [[sum(sum(C[i][k] * C[j][k] for k in range(8)) for C in grouped.values())
               for j in range(8)] for i in range(8)]
    return len(grouped), result

def route_report(R, routes):
    norms = [sum(row[p] ** 2 for row in R) for p in U]
    require(norms == [4] * 96, "ordinary column norms")
    require(gram(R, U) == diagonal(48), "ordinary Gram")
    require(gram(R, A) == gram(R, T) == diagonal(4), "selected dyadic unit minors")
    pairs = {}
    for s, t in ((0, 1), (0, 2), (1, 2)):
        count, coefficient = cross_coefficient(R, routes, s, t)
        require(count == 96, "distinct relative routes")
        require(coefficient == diagonal(192), "cross identity coefficient")
        pairs[f"{s},{t}"] = {"distinct_routes": count, "identity_coefficient": coefficient,
                             "normalized_trace": sum(coefficient[i][i] for i in range(8))}
    trace = 3 * sum(gram(R, U)[i][i] for i in range(8))
    square = 3 * sum(x*x for row in gram(R, U) for x in row) + 2 * sum(p["normalized_trace"] for p in pairs.values())
    bound = Q(trace * trace, square)
    require(bound > 16, "positive residual rank")
    return {"R_dense_sha256": digest(canonical(R)),
            "routes_U96_stage_major_sha256": digest(canonical([routes[s][p] for s in range(3) for p in U])),
            "ordinary_column_norms": dict(sorted(Counter(map(str, norms)).items())),
            "ordinary_gram": gram(R, U), "pairs": pairs,
            "trace_per_cover_owner": trace, "square_trace_per_cover_owner": square,
            "stacked_rank_lower_per_cover_owner": str(bound),
            "missing_A_dimension_lower_per_cover_owner": str(bound - 16)}

def tail_trace(events):
    """Recompute the inherited tail on its one formal ordinary vector h."""
    x, y = [0]*4, [1, 0, 0, 0]
    result, stages = [], []
    for event in events:
        kind = event["kind"]
        if kind == "bridge":
            src, dst, c = event["src"], event["dst"], event["coefficient"]
            require(0 <= src < 4 and 0 <= dst < 4 and src != dst and c in (-1, 1), "bridge domain")
            x[dst] += c * x[src]
            y[src] -= c * y[dst]
        elif kind == "local":
            s = event["stage"]
            require(s in range(2, 9), "tail stage")
            bank = (s // 2) % 4
            require((x if s % 2 == 0 else y)[bank] == 0, "active tail source is zero")
            stages.append(s)
        else:
            require(kind == "terminal", "tail event kind")
            x, y = y, [-v for v in x]
        result.append({"kind": kind, "x": x.copy(), "y": y.copy()})
    require(stages == list(range(2, 9)), "complete tail stage coverage")
    require(x == [1, 0, 0, 0] and y == [0]*4, "tail endpoint")
    return result

def matrix_rank(matrix):
    a = [list(map(Q, row)) for row in matrix]
    rank = 0
    for col in range(len(a[0])):
        pivot = next((i for i in range(rank, len(a)) if a[i][col]), None)
        if pivot is None:
            continue
        a[rank], a[pivot] = a[pivot], a[rank]
        scale = a[rank][col]
        a[rank] = [x / scale for x in a[rank]]
        for i in range(rank + 1, len(a)):
            if a[i][col]:
                scale = a[i][col]
                a[i] = [x - scale*y for x, y in zip(a[i], a[rank])]
        rank += 1
        if rank == len(a):
            break
    return rank

def finite_regular_fixture():
    """Complete C3xC3 regular example, not a claim about the actual cover.

    One centre coordinate, nine ordinary ports, route s*p for B_s. Taking
    the same mean-zero field in every port gives an explicit hidden h.
    """
    points = [(i, j) for i in range(3) for j in range(3)]
    index = {g: i for i, g in enumerate(points)}
    B = []
    for s in range(3):
        rows = []
        for g in points:
            row = [0]*81
            for p, point in enumerate(points):
                at = ((g[0]+s*point[0]) % 3, (g[1]+s*point[1]) % 3)
                row[9*p+index[at]] = 1
            rows.append(row)
        B.append(rows)
    e, h = [1, -1]+[0]*7, ([1, -1]+[0]*7)*9
    query = lambda s, v: [sum(a*b for a,b in zip(row,v)) for row in B[s]]
    require(query(1,h) == query(2,h) == [0]*9, "fixture hidden queries")
    require(query(0,h) == [9*v for v in e], "fixture old query")
    stack = sum(B, [])
    actual_rank, old_rank = matrix_rank(stack), matrix_rank(B[1]+B[2])
    require((actual_rank,old_rank) == (25,17), "fixture complete ranks")
    H = [[sum(a*b for a,b in zip(x,y)) for y in stack] for x in stack]
    trace, square = sum(H[i][i] for i in range(27)), sum(x*x for row in H for x in row)
    lower = Q(trace*trace,square)
    require(actual_rank >= lower > 18, "fixture trace bound")
    # Selected sections are identities in this illustrative model. The
    # general ordered proof supplies the arbitrary-chart assertion.
    xa, ya = [-v for v in query(0,h)], query(0,h)
    f0 = [u+v for u,v in zip(query(0,h),xa)]
    require(f0 == [0]*9 and any(xa), "fixture initial A and F query")
    selected_after_f0 = [a+b for a,b in zip(xa,ya)]
    require(selected_after_f0 == [0]*9, "fixture selected F endpoint")
    q2, b1 = query(2,h), query(1,h)
    require(q2 == b1 == [0]*9, "fixture B query cancellation")
    require([a-b for a,b in zip(h,h)] == [0]*81, "fixture ordinary B endpoint")
    return {"group":"C3xC3", "cover_size":9, "matrix_shape":[27,81],
            "stacked_rank":actual_rank, "two_query_rank":old_rank,
            "exact_missing_dimension":actual_rank-old_rank, "trace":trace,
            "square_trace":square, "rank_bound":str(lower), "explicit_h":h,
            "B0_h":query(0,h), "B1_h":b1, "B2_h":q2, "initial_A":xa,
            "F0_query":f0, "after_B1_only_YU":True}

def rejected(call, message):
    try:
        call()
    except CheckError as error:
        require(message in str(error), "wrong rejection: " + str(error))
    else:
        raise CheckError("negative control unexpectedly accepted: " + message)

def controls(R, routes, events):
    bad_R = deepcopy(R)
    bad_R[0][U[0]] += 1
    rejected(lambda: route_report(bad_R,routes), "ordinary column norms")
    bad_routes = deepcopy(routes)
    bad_routes[1][U[1]] = bad_routes[1][U[0]]
    rejected(lambda: route_report(R,bad_routes), "distinct relative routes")
    bad_events = deepcopy(events)
    minus = next(i for i,e in enumerate(bad_events) if e["kind"] == "bridge" and e["coefficient"] == -1)
    del bad_events[minus]
    rejected(lambda: tail_trace(bad_events), "active tail source is zero")
    return ["changed_column", "collapsed_route", "omitted_cancelling_bridge"]

def build(repo):
    sources = authenticate(repo)
    R, phases, witness = load_inputs(sources)
    routes = routes_from_transvections(phases)
    report = route_report(R,routes)
    events = witness["trajectory_after_B1"]
    trace = tail_trace(events)
    for event,state in zip(events,trace):
        require(event["ordinary"] == [z for pair in zip(state["x"],state["y"]) for z in pair], "inherited tail receipt")
    return {"schema":1, "status":"PASS_QQ16_EXTRA_QUERY_RESIDUAL", "route_audit":report,
            "tail":trace, "finite_fixture":finite_regular_fixture(),
            "negative_controls":controls(R,routes,events),
            "source_sha256":{k:digest(v) for k,v in sorted(sources.items())},
            "scope":"Fixed F0/B1 and retained observations plus side-effect-free B2 X_U; written rank/existence theorem and finite source checks; no native tariff, full controller or new kappa."}

def validate(receipt,actual):
    require(type(receipt) is dict and canonical(receipt) == canonical(actual), "complete fixed receipt")

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo",type=Path,default=HERE.parents[1])
    parser.add_argument("--write",type=Path,help="explicitly generate a NEW receipt; refuses overwrite")
    parser.add_argument("--certificate",type=Path,default=HERE / "RESULT.json")
    args = parser.parse_args()
    actual = build(args.repo.resolve())
    if args.write:
        with args.write.open("x") as file:
            json.dump(actual,file,indent=2,sort_keys=True)
            file.write("\n")
        print("GENERATED_QQ16_EXTRA_QUERY_RESIDUAL " + str(args.write))
        return
    receipt = json.loads(args.certificate.read_text())
    validate(receipt,actual)
    print(actual["status"] + " rank_stack>=144|G|/7 missing_A>=ceil(32|G|/7) no_new_kappa")

if __name__ == "__main__":
    main()
