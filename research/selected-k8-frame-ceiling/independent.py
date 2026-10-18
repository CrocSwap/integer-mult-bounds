#!/usr/bin/env python3
"""Separate bitset/event-graph and integer-root dual checker. Apache-2.0.

Shares only source binding/JSON utilities with the primary checker. Does not
import the retained frame model, LP generator, ceiling engine or primary code.
Gareth Davidson, with substantial OpenAI Codex assistance.
"""
from collections import Counter, defaultdict
from fractions import Fraction as Q
from functools import lru_cache
import importlib.util
import json
from math import isqrt
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("independent_sources", HERE / "common.py")
U = importlib.util.module_from_spec(spec)
spec.loader.exec_module(U)
need = U.need
FULL = (1 << 512)-1
SCALE = 1 << 256
BITS = 96
BASE_LO = Q(1690054109088, 10**15)
BASE_HI = Q(1690054109089, 10**15)
TARGET = Q(21, 20)*BASE_HI
RANKS = range(2, 10)


def elements(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length()-1
        mask ^= bit


@lru_cache(None)
def extend(frame, vector):
    if (frame >> vector) & 1:
        return frame
    return frame | sum(1 << (x ^ vector) for x in elements(frame))


def frame(vectors):
    result = 1
    for vector in vectors:
        need(type(vector) is int and 0 <= vector < 512, "frame-vector domain")
        result = extend(result, vector)
    return result


def dimension(space):
    size = space.bit_count()
    need(size > 0 and not size & (size-1), "subspace size")
    return size.bit_length()-1


@lru_cache(None)
def canonical_frame(space):
    pivots = {}
    for value in elements(space):
        v = value
        for p in sorted(pivots, reverse=True):
            if (v >> p) & 1:
                v ^= pivots[p]
        if v:
            p = v.bit_length()-1
            for k in list(pivots):
                if (pivots[k] >> p) & 1:
                    pivots[k] ^= v
            pivots[p] = v
    result = tuple(pivots[p] for p in sorted(pivots, reverse=True))
    need(frame(result) == space, "canonical-frame span")
    return result


@lru_cache(None)
def join(left, right):
    result = left
    for x in canonical_frame(right):
        result = extend(result, x)
    return result


@lru_cache(None)
def small_spaces(k):
    seen, todo = {1}, [1]
    while todo:
        sub = todo.pop()
        for x in range(1, 1 << k):
            other = extend(sub, x)
            if other not in seen:
                seen.add(other)
                todo.append(other)
    return tuple(sorted(seen))


def interval(lo, hi):
    need(lo & ~hi == 0, "independent empty interval")
    complement, current = [], lo
    for x in canonical_frame(hi):
        if not ((current >> x) & 1):
            complement.append(x)
            current = extend(current, x)
    need(current == hi and len(complement) <= 4, "complete quotient domain")
    result = []
    for sub in small_spaces(len(complement)):
        value = lo
        for bits in elements(sub):
            x = 0
            for j, c in enumerate(complement):
                if (bits >> j) & 1:
                    x ^= c
            value = extend(value, x)
        result.append(value)
    need(len(set(result)) == len(result), "independent duplicate frame")
    return sorted(result, key=lambda x: (dimension(x), canonical_frame(x)))


def operands(op):
    need(op[0] in ("add", "scale"), "scalar primitive")
    return op[1:3] if op[0] == "add" else op[1:2]


def scalar(rows, operations):
    for op in operations:
        if op[0] == "add":
            t, s = op[1:3]
            a = Q(op[3], op[4])
            for key, value in tuple(rows[s].items()):
                new = rows[t].get(key, Q(0)) + a*value
                if new:
                    rows[t][key] = new
                else:
                    rows[t].pop(key, None)
        else:
            t = op[1]
            a = Q(op[2], op[3])
            need(a, "invertible scale")
            rows[t] = {key: a*value for key, value in rows[t].items()}


def cone_caps(word, n, v, low):
    """Forward restricted columns, plus row covectors propagated through inverses."""
    main = word["A"]+word["cut"]+word["B"]
    response = [{r: Q(1)} if r >= 2*v else {} for r in range(n)]
    scalar(response, main)
    dirty = [response[r].copy() if v <= r < 2*v else {} for r in range(n)]
    scalar(dirty, word["precondition"])
    compensation = [["add", r, k, -a.numerator, a.denominator, []]
                    for r in range(v, 2*v) for k, a in sorted(dirty[r].items())]
    prefix = word["precondition"]+compensation+main
    columns = [{r: Q(1)} if r in low else {} for r in range(n)]
    scalar(columns, prefix)
    inverses = {q: {q: Q(1)} for q in low}
    for op in prefix:
        if op[0] == "add":
            t, s = op[1:3]
            a = Q(op[3], op[4])
            for row in inverses.values():
                if t in row:
                    new = row.get(s, Q(0))-a*row[t]
                    if new:
                        row[s] = new
                    else:
                        row.pop(s, None)
        else:
            t = op[1]
            a = Q(op[2], op[3])
            for row in inverses.values():
                if t in row:
                    row[t] /= a
    caps = {}
    for q, cap in low.items():
        support = set(inverses[q]) | {k for k in range(n) if q in columns[k]}
        for k in support-{q}:
            caps[k] = caps.get(k, FULL) & cap
    return caps


def build(word):
    v, n = 112, 704
    fixed = {}
    for q in range(n):
        start = frame([word["ports"][q]]) if q < v else 1
        if str(q) in word["start_extra"]:
            start = frame(word["start_extra"][str(q)])
        if v <= q < 2*v:
            p = word["ports"][q-v]
            end = sum(1 << x for x in range(512) if (x & p).bit_count() % 2 == 0)
        else:
            end = FULL
        if str(q) in word["helper_final"]:
            end = frame(word["helper_final"][str(q)])
        fixed[("S", q)], fixed[("E", q)] = start, end
    low = {int(q): frame(x) for q, x in word["helper_final"].items()}
    caps = cone_caps(word, n, v, low)
    levels = {int(t): frame(x) for t, x in word["target_levels"].items()}
    pins = {q: frame(x) for q, x in zip(word["centers"], word["center_frames"])}
    need(len(pins) == 8, "independent centre count")
    for t in range(v):
        need(v+t not in pins, "centre/target collision")
        pins[v+t] = levels.get(t, 1)
    for q, f in pins.items():
        fixed[("P", q)] = f
    centres = []
    for q, f in zip(word["centers"], word["center_frames"]):
        cur = frame(f)
        served = {levels.get(op[1]-v, 1) for op in word["cut"] if op[2] == q}
        for target in sorted(served, key=lambda x: -dimension(x)):
            need(target & ~cur == 0, "independent centre descent")
            if target != cur:
                centres.append(dimension(cur)-dimension(target))
            cur = target
    tail = [word["cleanup"][i][:-1]+[f] for i, f in word["early_cleanup"]]
    operations = word["A"]+word["B"]+tail
    nA, nB = len(word["A"]), len(word["B"])
    chains = {q: [("S", q)] for q in range(n)}
    order = [("S", q) for q in range(n)]
    at_cap = defaultdict(list)
    for i, op in enumerate(operations):
        if i == nA:
            for q in pins:
                node = ("P", q)
                chains[q].append(node)
                order.append(node)
        if i == nA+nB:
            for q, cap in caps.items():
                at_cap[chains[q][-1]].append(cap)
        node = ("G", i)
        order.append(node)
        for q in operands(op):
            chains[q].append(node)
    for q in range(n):
        node = ("E", q)
        chains[q].append(node)
        order.append(node)
    need(len(operations) > nA+nB, "selected word must have tail events")
    edges = Counter((a, b) for ch in chains.values() for a, b in zip(ch, ch[1:]))
    pred, succ = defaultdict(set), defaultdict(set)
    for a, b in edges:
        pred[b].add(a)
        succ[a].add(b)
    lo, hi = {}, {}
    for node in order:
        lower = 1
        for p in pred[node]:
            lower = join(lower, lo[p])
        lo[node] = fixed.get(node, lower)
        need(lower & ~lo[node] == 0, "independent fixed lower bound")
    for node in reversed(order):
        upper = FULL
        for child in succ[node]:
            upper &= hi[child]
        for cap in at_cap[node]:
            upper &= cap
        hi[node] = fixed.get(node, upper)
        need(hi[node] & ~upper == 0 and lo[node] & ~hi[node] == 0, "independent upper bound")
    given = {**fixed, **{("G", i): frame(op[-1]) for i, op in enumerate(operations)}}
    domains = {("G", i): interval(lo[("G", i)], hi[("G", i)])
               for i in range(len(operations)) if lo[("G", i)] != hi[("G", i)]}
    profile = Counter(centres)
    for (a, b), mult in edges.items():
        need(given[a] & ~given[b] == 0, "independent baseline nesting")
        d = dimension(given[b])-dimension(given[a])
        if d:
            profile[d] += mult
    need(dict(profile) == U.PROFILE, "independent baseline profile")
    for node, f in given.items():
        need(lo[node] & ~f == 0 and f & ~hi[node] == 0, "independent given frame interval")
    unseen, comps = set(domains), []
    while unseen:
        start = min(unseen, key=lambda x: x[1])
        todo, comp = [start], set()
        while todo:
            node = todo.pop()
            if node not in unseen:
                continue
            unseen.remove(node)
            comp.add(node)
            todo.extend((pred[node] | succ[node]) & unseen)
        comps.append(sorted(comp, key=lambda x: x[1]))
    graph = {"nodes_sha256": U.digest([[list(n), lo[n], hi[n]] for n in sorted(lo)]),
             "domains_sha256": U.digest([[list(n), sorted(domains[n])] for n in sorted(domains)]),
             "edges_sha256": U.digest([[list(a), list(b), k] for (a, b), k in sorted(edges.items())]),
             "cones_sha256": U.digest([[k, f] for k, f in sorted(caps.items())]),
             "node_count": len(lo), "edge_count": len(edges), "cone_registers": len(caps)}
    return dict(lo=lo, hi=hi, given=given, domains=domains, edges=edges, comps=comps,
                graph=graph, centres=centres, chains=chains)


def ceil_sqrt(n):
    r = isqrt(n)
    return r + int(r*r != n)


@lru_cache(None)
def child(r, a):
    """Enclose (r/73)*(73/r)^a with dyadic exponent brackets and integer square roots."""
    need(1 <= r <= 73 and 0 <= a < 1, "root oracle domain")
    lo = (73*SCALE)//r
    hi = (73*SCALE+r-1)//r
    integer_base = (lo, hi)
    roots = []
    for _ in range(BITS):
        lo, hi = isqrt(lo*SCALE), ceil_sqrt(hi*SCALE)
        roots.append((lo, hi))
    power = (a.numerator << BITS)//a.denominator
    def evaluate(k):
        need(0 <= k <= 1 << BITS, "dyadic exponent bracket")
        if k == 1 << BITS:
            return integer_base
        lower = upper = SCALE
        for j, (left, right) in enumerate(roots, 1):
            if (k >> (BITS-j)) & 1:
                lower = (lower*left)//SCALE
                upper = (upper*right+SCALE-1)//SCALE
        return lower, upper
    return Q(r*evaluate(power)[0], 73*SCALE), Q(r*evaluate(power+1)[1], 73*SCALE)


def charges(a):
    costs = {d: child(d, a) for d in range(1, 10)}
    return {d: (73*(costs[d][0]-d*costs[1][1]), 73*(costs[d][1]-d*costs[1][0])) for d in RANKS}


def check(data, duals, bounds):
    need(len(duals["components"]) == len(data["comps"]), "independent component coverage")
    stats = Counter()
    residuals = set()
    for comp, record in zip(data["comps"], duals["components"]):
        need(record["first"] == json.dumps(comp[0]) and record["nodes"] == len(comp), "independent component identity")
        members = set(comp)
        domain = data["domains"]
        unary = {n: {f: Counter() for f in domain[n]} for n in comp}
        pairs = {}
        for (a, b), mult in data["edges"].items():
            if a in members and b in members:
                pairs[(a, b)] = mult
            elif a in members:
                for f in domain[a]:
                    d = dimension(data["given"][b])-dimension(f)
                    need(f & ~data["given"][b] == 0, "independent unary nesting")
                    if d:
                        unary[a][f][d] += mult
            elif b in members:
                for f in domain[b]:
                    d = dimension(f)-dimension(data["given"][a])
                    need(data["given"][a] & ~f == 0, "independent unary nesting")
                    if d:
                        unary[b][f][d] += mult
        rows = {json.dumps(("N", n)) for n in comp}
        touching = defaultdict(list)
        for a, b in pairs:
            for side, node in enumerate((a, b)):
                touching[node].append((a, b, side))
                rows.update(json.dumps(("M", a, b, side, canonical_frame(f))) for f in domain[node])
        need(set(record["duals"]) <= rows, "independent unknown dual row")
        q = {k: {int(d): Q(v) for d, v in vec.items()} for k, vec in record["duals"].items()}
        need(all(d in RANKS for vec in q.values() for d in vec), "independent dual coordinate")
        def add_to(vec, key, sign):
            for d, v in q.get(json.dumps(key), {}).items():
                vec[d] = vec.get(d, Q(0))+sign*v
        def accept(vec):
            clean = {d: Q(vec.get(d, 0)) for d in RANKS}
            if any(clean.values()):
                for bound in bounds:
                    value = sum((v*bound[d][0 if v > 0 else 1] for d, v in clean.items() if v), Q(0))
                    need(value > 0, "independent reduced cost")
                stats["positive"] += 1
            else:
                stats["zero"] += 1
            residuals.add(tuple(str(clean[d]) for d in RANKS))
            stats["columns"] += 1
        objective, baseline = Counter(), Counter()
        for node in comp:
            add_to(objective, ("N", node), 1)
            baseline.update(unary[node][data["given"][node]])
            for f in domain[node]:
                vec = dict(unary[node][f])
                add_to(vec, ("N", node), -1)
                for a, b, side in touching[node]:
                    add_to(vec, ("M", a, b, side, canonical_frame(f)), 1)
                accept(vec)
        for (a, b), mult in pairs.items():
            d = dimension(data["given"][b])-dimension(data["given"][a])
            if d:
                baseline[d] += mult
            for left in domain[a]:
                for right in domain[b]:
                    if left & ~right:
                        continue
                    d = dimension(right)-dimension(left)
                    vec = {d: mult} if d else {}
                    add_to(vec, ("M", a, b, 0, canonical_frame(left)), -1)
                    add_to(vec, ("M", a, b, 1, canonical_frame(right)), -1)
                    accept(vec)
        need(all(objective[d] == baseline[d] for d in RANKS), "independent baseline dual identity")
        stats.update(components=1, rows=len(rows))
    stats["distinct_reduced_vectors"] = len(residuals)
    return dict(stats)


def main():
    U.source_bindings()
    expected = U.parse((HERE / "EXPECTED.json").read_bytes())
    data = build(U.word())
    need(data["graph"] == expected["graph"], "independent complete graph differs")
    dual = U.duals()
    need(U.digest(dual) == expected["duals_sha256"], "independent dual payload binding")
    for r in range(1, 73):
        lo, hi = child(r, Q(1, 2))
        need(lo*lo <= Q(r, 73) <= hi*hi, "square-root oracle calibration")
    need(child(37, 1-Q(1, 1 << 100))[1] >= 1, "dyadic exponent carry control")
    stats = check(data, dual, [charges(BASE_HI), charges(TARGET)])
    need(stats == expected["duality"], "independent dual coverage differs")
    margins = []
    for a in (BASE_LO, BASE_HI, TARGET):
        lo = sum((n*child(r, a)[0] for r, n in U.PROFILE.items()), Q(0))
        hi = sum((n*child(r, a)[1] for r, n in U.PROFILE.items()), Q(0))
        lo = (lo+Q(1646, 51)*child(51, a)[0])/Q(896, 9)
        hi = (hi+Q(1646, 51)*child(51, a)[1])/Q(896, 9)
        need(hi < 1 if a == BASE_LO else lo > 1, "independent ceiling sign")
        margins.append([str(a), str(lo-1), str(hi-1)])
    print("PASS_K8_FRAME_INDEPENDENT", "components="+str(stats["components"]),
          "columns="+str(stats["columns"]), "root_calibrations=72", "graph_and_duality_match=True")


if __name__ == "__main__":
    main()
