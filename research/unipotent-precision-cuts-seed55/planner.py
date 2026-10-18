"""Exact canonical-cut planning. Hanson Sun / OpenAI Codex, Apache-2.0.

The frozen predecessor supplies the instruction alphabet and interval emitter.
This module adds four contextual prefix states and a cap-constrained cut DAG.
"""
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def predecessor():
    pins = json.loads((HERE / "PREDECESSOR.json").read_text())
    for pin in pins["files"]:
        data = (HERE / pin["path"]).read_bytes()
        require(hashlib.sha256(data).hexdigest() == pin["sha256"],
                "predecessor SHA256: " + pin["path"])
        blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        require(blob == pin["git_blob"], "predecessor Git blob")
    spec = importlib.util.spec_from_file_location("frozen_pr1537", HERE / "sources/pr1537-model.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def identity(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def replay(word, initial):
    """Exact integer row propagation; halves must divide every coefficient."""
    rows = [r[:] for r in initial]
    peak = max(sum(map(abs, r)) for r in rows)
    witness = {"step": 0, "row": max(range(len(rows)), key=lambda j: sum(map(abs, rows[j])))}
    for i, (op, dst, src, num, den) in enumerate(word, 1):
        require(0 <= dst < len(rows) and 0 <= src < len(rows), "address")
        if op == "ADD":
            require(dst != src and num in (-1, 1) and den == 1, "ADD alphabet")
            rows[dst] = [a + num * b for a, b in zip(rows[dst], rows[src])]
        elif op == "SCALE":
            require(src == dst and (num, den) in ((2, 1), (1, 2)), "SCALE alphabet")
            require(all(num * a % den == 0 for a in rows[dst]), "nonintegral prefix")
            rows[dst] = [num * a // den for a in rows[dst]]
        else:
            raise ValueError("unknown instruction")
        norm = sum(map(abs, rows[dst]))
        if norm > peak:
            peak = norm
            witness = {"step": i, "row": dst}
    return rows, peak, witness


def prefix_readers(children, m, old):
    prefix = [[[0] * (2 * m) for _ in range(2)]]
    for child in children:
        r = old.total_reader(child)
        require(len(r) == 2 and all(len(row) == 2 * m for row in r), "reader shape")
        # Every block must be a I+b J. This is equivalent to RP=QR.
        require(all(r[1][2*j] == 0 and r[0][2*j] == r[1][2*j+1]
                    for j in range(m)), "reader not equivariant")
        prefix.append([[a + b for a, b in zip(x, y)] for x, y in zip(prefix[-1], r)])
    return prefix


def context(prefix, at, m, kind):
    """Full D,X,U rows at a canonical interval boundary, not isolated leaves."""
    n = 2 + 4 * m
    rows = identity(n)
    p, total = prefix[at], prefix[-1]
    for d in range(2):
        for j in range(2 * m):
            rows[d][2 + 2*m + j] += p[d][j]
            if kind == "forward_group":
                rows[d][2 + j] += p[d][j]
            elif kind == "forward_undo":
                rows[d][2 + j] += total[d][j]
            elif kind == "inverse_undo":
                rows[d][2 + j] += p[d][j] - total[d][j]
            else:
                require(kind == "inverse_group", "context kind")
    if kind in ("forward_group", "inverse_undo"):
        for j in range(2*m):
            rows[2+2*m+j][2+j] += 1
    return rows


def interval_word(children, a, b, m, old):
    return old.emit_group(children[a:b], 2 + 2*m, m, "carry")


def drop_output_return(word, length, old):
    tail = old.power([(0, 1)], 1-length)
    require(not tail or word[-len(tail):] == tail, "terminal output return")
    return word[:len(word)-len(tail)]


def graph(children, m, old, fuse_final=False):
    require(bool(children) and all(isinstance(c, dict) for c in children),
            "planner domain is a nonempty list of fixed leaves")
    prefix = prefix_readers(children, m, old)
    edges = []
    for a in range(len(children)):
        for b in range(a+1, len(children)+1):
            word = interval_word(children, a, b, m, old)
            peaks = []
            bill = Counter(op[0] for op in word)
            child_adds = sum(old.invoice(c, m, "carry")[0] for c in children[a:b])
            add, scale = bill["ADD"] - child_adds, bill["SCALE"]
            require((add, scale) == old.boundary_bill(b-a, m, "carry"), "literal boundary bill")
            fused = fuse_final and b == len(children)
            if fused:
                half = drop_output_return(word,b-a,old)
                removed = Counter(op[0] for op in word[len(half):])
                add -= removed["ADD"]
                scale -= removed["SCALE"]
                for before, after, sign in (("forward_group","forward_undo",-1),
                                             ("inverse_group","inverse_undo",1)):
                    transfer = [("ADD",2+2*m+j,2+j,sign,1) for j in range(2*m)]
                    center = half+transfer+old.inverse(half)
                    end, peak, _ = replay(center,context(prefix,a,m,before))
                    require(end == context(prefix,a,m,after),"fused interval endpoint")
                    counts = Counter(op[0] for op in center)
                    require(counts["ADD"] == 2*(child_adds+add)+2*m and
                            counts["SCALE"] == 2*scale,"fused literal bill")
                    peaks.append(peak)
            else:
                inv = old.inverse(word)
                for kind, at, ops in (("forward_group", a, word), ("forward_undo", b, inv),
                                      ("inverse_group", a, word), ("inverse_undo", b, inv)):
                    end, peak, _ = replay(ops, context(prefix, at, m, kind))
                    require(end == context(prefix, b if at == a else a, m, kind),
                            "interval endpoint")
                    peaks.append(peak)
            edges.append({"a": a, "b": b, "add": add, "scale": scale,
                          "peak": max(peaks), "contexts": peaks, "fused":fused})
    return edges


def solve(edges, k, cap, scale_price=1):
    """Minimum over all contiguous partitions, with deterministic tie-breaking."""
    require(type(cap) is int and cap >= 1 and scale_price > 0, "positive tariff/cap")
    best = [None] * (k+1)
    best[0] = (0, 0, 0, ())
    incoming = [[] for _ in range(k+1)]
    for edge in edges:
        incoming[edge["b"]].append(edge)
    for b in range(1, k+1):
        for edge in incoming[b]:
            prev = best[edge["a"]]
            if prev is None or edge["peak"] > cap:
                continue
            price, add, scale, cuts = prev
            candidate = (price + edge["add"] + scale_price * edge["scale"],
                         add + edge["add"], scale + edge["scale"], cuts+(b,))
            if best[b] is None or candidate < best[b]:
                best[b] = candidate
    if best[k] is None:
        return None
    price, add, scale, cuts = best[k]
    return {"cap": cap, "boundary_price": price, "boundary_add": add,
            "boundary_scale": scale, "cuts": list(cuts),
            "distances": [None if item is None else item[0] for item in best]}


def emit_partition(children, cuts, m, old, fuse_final=False):
    require(bool(cuts) and cuts[-1] == len(children) and
            all(type(x) is int for x in cuts) and
            all(a < b for a, b in zip([0]+list(cuts), cuts)), "partition cuts")
    word, a = [], 0
    for b in cuts:
        word.extend(interval_word(children, a, b, m, old))
        a = b
    if fuse_final:
        last_start = cuts[-2] if len(cuts)>1 else 0
        word = drop_output_return(word,len(children)-last_start,old)
    copy = [("ADD", 2+2*m+j, 2+j, 1, 1) for j in range(2*m)]
    return copy + word + old.inverse(copy) + old.inverse(word)


def expected(children, m, old):
    rows = identity(2+4*m)
    for d, r in enumerate(old.total_reader(children)):
        for j, coefficient in enumerate(r):
            rows[d][2+j] += coefficient
    return rows


def word_report(word, m, old):
    rows, forward, fw = replay(word, identity(2+4*m))
    inv_rows, backward, bw = replay(old.inverse(word), identity(2+4*m))
    bill = Counter(op[0] for op in word)
    return {"add": bill["ADD"], "scale": bill["SCALE"], "operations": len(word),
            "data_reads": 2*bill["ADD"]+bill["SCALE"], "data_writes": len(word),
            "instruction_reads": len(word), "forward_peak": forward, "inverse_peak": backward,
            "peak": max(forward, backward), "forward_witness": fw, "inverse_witness": bw}
