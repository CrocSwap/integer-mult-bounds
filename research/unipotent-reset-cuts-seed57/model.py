"""Canonical reset-cut DAG. Hanson Sun / OpenAI Codex, Apache-2.0.

The child/return emitter is Sagar Thakrar's byte-pinned PR1537 implementation.
Only the positions of full canonical resets are changed here.
"""

import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def require(ok, message):
    if not ok:
        raise ValueError(message)


def source_check():
    pins = json.loads((HERE / "PREDECESSORS.json").read_text())
    for item in pins["files"]:
        raw = (HERE / item["path"]).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == item["sha256"], "source SHA256: " + item["path"])
        blob = b"blob " + str(len(raw)).encode() + b"\0" + raw
        require(hashlib.sha1(blob).hexdigest() == item["git_blob"], "source Git blob: " + item["path"])
    return pins


source_check()
spec = importlib.util.spec_from_file_location("pinned_pr1537", HERE / "references/pr1537_model.py")
predecessor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(predecessor)


def eye(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def prefixes(children, m):
    out = [[[0] * (2 * m) for _ in range(2)]]
    for child in children:
        r = child["reader"]
        require(len(r) == 2 and all(len(row) == 2 * m for row in r), "reader dimensions")
        require(all(type(x) is int for row in r for x in row), "integer reader")
        for j in range(m):
            require(r[1][2*j] == 0 and r[0][2*j] == r[1][2*j+1], "reader does not intertwine")
        out.append([[x + y for x, y in zip(a, b)] for a, b in zip(out[-1], r)])
    return out


def cut_state(sums, i, m, context):
    """Canonical matrix at a segment entrance, independent of earlier cuts.

    Coordinates are D, X, U. Contexts: forward echo/forward group (ff),
    forward echo/inverse group (fr), inverse echo/forward group (rf),
    inverse echo/inverse group (rr). The inverse-group index is its right cut.
    """
    n = 2 + 4 * m
    rows = eye(n)
    total, partial = sums[-1], sums[i]
    if context in ("ff", "rr"):
        for j in range(2*m):
            rows[2+2*m+j][2+j] = 1
    for d in range(2):
        for j in range(2*m):
            rows[d][2+2*m+j] = partial[d][j]
            rows[d][2+j] = {
                "ff": partial[d][j], "fr": total[d][j],
                "rf": 0, "rr": partial[d][j] - total[d][j],
            }[context]
    return rows


def trace(word, initial):
    """Exact integral row propagation, with divisibility checked at each half."""
    rows = [row[:] for row in initial]
    n = len(rows)
    peak = max(sum(map(abs, row)) for row in rows)
    witness = {"step": 0, "row": max(range(n), key=lambda r: sum(map(abs, rows[r])))}
    adds = scales = reads = travel = 0
    head = 0
    for step, (op, dst, src, num, den) in enumerate(word, 1):
        require(0 <= src < n and 0 <= dst < n, "invalid data address")
        if op == "ADD":
            require(dst != src and num in (-1, 1) and den == 1, "invalid ADD")
            rows[dst] = [x + num*y for x, y in zip(rows[dst], rows[src])]
            adds += 1
            reads += 2
            travel += abs(head-src) + abs(src-dst)
        else:
            require(op == "SCALE" and src == dst and (num, den) in ((2, 1), (1, 2)), "invalid SCALE")
            require(all((num*x) % den == 0 for x in rows[dst]), "nonintegral prefix")
            rows[dst] = [num*x // den for x in rows[dst]]
            scales += 1
            reads += 1
            travel += abs(head-dst)
        head = dst
        mass = sum(map(abs, rows[dst]))
        if mass > peak:
            peak = mass
            witness = {"step": step, "row": dst}
    return rows, {"ADD": adds, "SCALE": scales, "total": adds+scales,
                  "data_reads": reads, "data_writes": adds+scales,
                  "instruction_reads": adds+scales, "data_head_travel": travel,
                  "peak": peak, "witness": witness}


def graph(children, m):
    sums = prefixes(children, m)
    edges = []
    for i in range(len(children)):
        for j in range(i+1, len(children)+1):
            word = predecessor.emit_group(children[i:j], 2+2*m, m, "carry")
            inv = predecessor.inverse(word)
            peaks = {}
            for context, start, end, program in (
                ("ff", i, j, word), ("fr", j, i, inv),
                ("rf", i, j, word), ("rr", j, i, inv),
            ):
                got, evidence = trace(program, cut_state(sums, start, m, context))
                require(got == cut_state(sums, end, m, context), "segment endpoint: " + context)
                peaks[context] = evidence["peak"]
            a, s = predecessor.boundary_bill(j-i, m, "carry")
            edges.append({"i": i, "j": j, "ADD": a, "SCALE": s,
                          "peak": max(peaks.values()), "peaks": peaks})
    return edges


def shortest(edges, k, cap, scale_price=1):
    require(type(cap) is int and cap >= 1, "positive integer cap")
    require(type(scale_price) is int and scale_price >= 1, "positive integer SCALE tariff")
    incoming = [[] for _ in range(k+1)]
    for e in edges:
        if e["peak"] <= cap:
            incoming[e["j"]].append(e)
    distances, previous = [None]*(k+1), [None]*(k+1)
    distances[0] = 0
    for j in range(1, k+1):
        candidates = [(distances[e["i"]] + e["ADD"] + scale_price*e["SCALE"], e["i"])
                      for e in incoming[j] if distances[e["i"]] is not None]
        if candidates:
            distances[j], previous[j] = min(candidates)
    if distances[-1] is None:
        return {"cap": cap, "cost": None, "cuts": None, "distances": distances}
    cuts = [k]
    while cuts[-1]:
        cuts.append(previous[cuts[-1]])
    return {"cap": cap, "cost": distances[-1], "cuts": list(reversed(cuts)), "distances": distances}


def bellman_check(edges, k, result, scale_price=1):
    """Check a lower-bound potential plus an attaining path, without optimizing."""
    cap, dist, cuts = result["cap"], result["distances"], result["cuts"]
    require(len(dist) == k+1 and dist[0] == 0, "invalid distance dimensions/origin")
    for e in edges:
        if e["peak"] <= cap and dist[e["i"]] is not None:
            require(dist[e["j"]] is not None, "reachable vertex marked unreachable")
            require(dist[e["j"]] <= dist[e["i"]] + e["ADD"] + scale_price*e["SCALE"], "Bellman lower bound")
    require(result["cost"] == dist[-1], "terminal potential")
    if cuts is None:
        require(dist[-1] is None, "missing attaining path")
        return
    require(cuts[0] == 0 and cuts[-1] == k and all(i < j for i,j in zip(cuts, cuts[1:])), "invalid cuts")
    lookup = {(e["i"], e["j"]): e for e in edges}
    path = [lookup[i,j] for i,j in zip(cuts, cuts[1:])]
    require(all(e["peak"] <= cap for e in path), "path exceeds cap")
    require(sum(e["ADD"] + scale_price*e["SCALE"] for e in path) == result["cost"], "path fails to attain lower bound")


def emit(children, m, cuts):
    require(cuts[0] == 0 and cuts[-1] == len(children) and all(i < j for i,j in zip(cuts, cuts[1:])), "invalid partition")
    word = []
    for i,j in zip(cuts, cuts[1:]):
        word += predecessor.emit_group(children[i:j], 2+2*m, m, "carry")
    copy = [("ADD", 2+2*m+j, 2+j, 1, 1) for j in range(2*m)]
    return copy + word + predecessor.inverse(copy) + predecessor.inverse(word)


def complete_bill(children, m, cuts):
    child_adds = sum(sum(abs(x) for row in t["reader"] for x in row) + m for t in children)
    bills = [predecessor.boundary_bill(j-i, m, "carry") for i,j in zip(cuts, cuts[1:])]
    return 2*child_adds+4*m+2*sum(a for a,s in bills), 2*sum(s for a,s in bills)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def frontier(edges, k):
    out, best = [], None
    for cap in sorted({e["peak"] for e in edges}):
        result = shortest(edges, k, cap)
        bellman_check(edges, k, result)
        if result["cost"] is not None and (best is None or result["cost"] < best):
            out.append(result)
            best = result["cost"]
    return out
