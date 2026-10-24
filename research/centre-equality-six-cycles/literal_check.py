#!/usr/bin/env python3
# Copyright 2026 Krzysztof Wójt
# Licensed under the Apache License, Version 2.0.
# Prepared with substantial OpenAI Codex and Luna assistance.
# Predecessor attribution is retained in the package README.
"""Independent literal-DFS verifier for WITNESS.json; standard library only."""
from collections import Counter
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path

ROWS = (
    (1,2,3),(0,2,4),(0,1,5),(0,6,7),(1,8,9),(2,10,11),(3,6,12),(3,13,14),
    (4,8,12),(4,9,13),(5,10,12),(5,11,14),(6,9,11),(7,8,14),(7,10,13),
)
C6 = frozenset({
    (0,16,2,15,1,17),(4,23,8,19,9,24),
    (5,25,10,20,11,26),(7,28,14,22,13,29),
})
C6_SETS = frozenset((tuple(sorted(v for v in c if v < 15)),
                     tuple(sorted(v-15 for v in c if v >= 15))) for c in C6)
FREE = {"B": (3,6,12), "D": (3,6,12)}

def need(ok, msg):
    if not ok:
        raise RuntimeError(msg)
def digest(x):
    return sha256(json.dumps(x, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
def valid(rows):
    if type(rows) is not list or len(rows) != 15:
        return False
    cols = [0]*15
    for row in rows:
        if type(row) is not list or len(row) != 3:
            return False
        if any(type(d) is not int or not 0 <= d < 15 for d in row) or len(set(row)) != 3:
            return False
        for d in row:
            cols[d] += 1
    return cols == [3]*15
def graph(rows):
    a = [[] for _ in range(30)]
    for b, ds in enumerate(rows):
        for d in ds:
            a[b].append(15+d); a[15+d].append(b)
    return tuple(tuple(sorted(x)) for x in a)
def canon(path):
    p = tuple(path)
    return min(q[i:]+q[:i] for q in (p, tuple(reversed(p))) for i in range(len(q)))
def cycles(adj, length, roots=None):
    found = set()
    for start in range(len(adj)) if roots is None else roots:
        def dfs(path, used):
            if len(path) == length:
                if start in adj[path[-1]]:
                    found.add(canon(path))
                return
            for v in adj[path[-1]]:
                if v != start and v not in used:
                    dfs(path+(v,), used | {v})
        dfs((start,), {start})
    return found
def ncomponents(adj):
    unseen, n = set(range(len(adj))), 0
    while unseen:
        n += 1; todo = [unseen.pop()]
        while todo:
            for v in adj[todo.pop()]:
                if v in unseen:
                    unseen.remove(v); todo.append(v)
    return n
def mm(a, b):
    bt = tuple(zip(*b))
    return [[sum(x*y for x,y in zip(row,col)) for col in bt] for row in a]
def cycle_sets(found):
    return frozenset((tuple(sorted(v for v in c if v < 15)),
                      tuple(sorted(v-15 for v in c if v >= 15))) for c in found)
def witness_sets(w):
    items = w.get("six_cycles")
    need(type(items) is list and len(items) == 4, "six_cycles must have four records")
    out = []
    for item in items:
        need(type(item) is dict and set(item) == {"B","D"}, "malformed cycle record")
        sides = []
        for side in ("B","D"):
            xs = item[side]
            need(type(xs) is list and len(xs) == 3
                 and all(type(x) is int and 0 <= x < 15 for x in xs)
                 and len(set(xs)) == 3, "malformed cycle labels")
            sides.append(tuple(sorted(xs)))
        out.append(tuple(sides))
    need(len(set(out)) == len(out), "duplicate witness cycle")
    return frozenset(out)
def perfect_matchings(points):
    points = tuple(points)
    if not points:
        yield ()
        return
    x = points[0]
    for y in points[1:]:
        rest = tuple(z for z in points[1:] if z != y)
        for tail in perfect_matchings(rest):
            yield tuple(sorted(((x,y),)+tail))
def duad_baseline():
    duads = tuple(combinations(range(6),2))
    synthemes = tuple(sorted(set(perfect_matchings(range(6)))))
    rows = [[j for j,m in enumerate(synthemes) if d in m] for d in duads]
    need(len(synthemes) == 15 and valid(rows), "bad duad fixture")
    a = graph(rows); c4, c6, c8 = cycles(a,4), cycles(a,6), cycles(a,8)
    need(ncomponents(a) == 1 and not c4 and not c6 and len(c8) == 90,
         "duad baseline failed")
    return {"duads":15,"synthemes":15,"components":1,"c4":0,"c6":0,"c8":90,
            "c8_digest":digest(sorted(c8))}

def run():
    p = Path(__file__).with_name("WITNESS.json")
    raw = p.read_bytes(); w = json.loads(raw)
    need(type(w.get("schema_version")) is int and w["schema_version"] == 1,
         "unsupported witness schema")
    rows = w.get("rows")
    need(valid(rows) and tuple(tuple(r) for r in rows) == ROWS, "rows fail strict/exact checks")
    a = graph(rows); need(ncomponents(a) == 1, "candidate disconnected")
    c4, c6, c8 = cycles(a,4), cycles(a,6), cycles(a,8)
    need(not c4 and c6 == C6 and cycle_sets(c6) == C6_SETS, "C4/C6 census mismatch")
    need(witness_sets(w) == C6_SETS, "WITNESS six_cycles mismatch")
    seen_b = {v for c in c6 for v in c if v < 15}
    seen_d = {v-15 for c in c6 for v in c if v >= 15}
    free = {"B":tuple(v for v in range(15) if v not in seen_b),
            "D":tuple(v for v in range(15) if v not in seen_d)}
    need(len(seen_b) == len(seen_d) == 12 and free == FREE, "C6 disjointness/free set mismatch")
    listed = w.get("cycle_free_vertices")
    need(type(listed) is dict and set(listed) == {"B","D"}, "bad cycle_free_vertices")
    for side in ("B","D"):
        xs = listed[side]
        need(type(xs) is list and all(type(x) is int for x in xs)
             and tuple(xs) == free[side], "listed cycle-free vertices mismatch")
    c = [[int(d in row) for d in range(15)] for row in rows]
    ct = [list(x) for x in zip(*c)]
    e = [[x-4*c[i][j]-1 for j,x in enumerate(row)] for i,row in enumerate(mm(mm(c,ct),c))]
    hist = Counter(x for row in e for x in row)
    need(hist == Counter({-1:12,0:201,1:12}), "defect histogram mismatch")
    q = mm(e,ct); need(q == [list(x) for x in zip(*q)], "E C^T not symmetric")
    pos = {(i,j) for i,r in enumerate(e) for j,x in enumerate(r) if x == 1}
    neg = {(i,j) for i,r in enumerate(e) for j,x in enumerate(r) if x == -1}
    partial = lambda s: len(s) == len({i for i,_ in s}) == len({j for _,j in s}) == 12
    need(partial(pos) and partial(neg), "defect supports not partial matchings")
    ix, px = {}, {}
    for k,cyc in enumerate(sorted(c6)):
        for z,v in enumerate(cyc):
            ix[v],px[v] = k,z
    need(all(ix[b] == ix[d+15] and (px[b]-px[d+15]) % 6 == 3 for b,d in pos),
         "positive support not opposite in same C6")
    need(all(ix[b] != ix[d+15] for b,d in neg), "negative support does not cross cycles")

    # Strict malformed-label controls; bool is deliberately not an integer ID.
    boolean = [list(r) for r in ROWS]; boolean[0][0] = True
    duplicate = [list(r) for r in ROWS]; duplicate[0] = [1,1,3]
    bad_range = [list(r) for r in ROWS]; bad_range[0] = [1,2,15]
    need(not valid(boolean) and not valid(duplicate) and not valid(bad_range),
         "malformed-row control accepted")

    # Degree-preserving 2-switch: removes one C6 and creates four.
    switched = [set(r) for r in ROWS]
    switched[0].remove(1); switched[0].add(0)
    switched[1].remove(0); switched[1].add(1)
    switched = [sorted(r) for r in switched]; sa = graph(switched)
    s4, s6 = cycles(sa,4), cycles(sa,6)
    need(valid(switched) and ncomponents(sa) == 1 and not s4 and len(s6) == 7
         and len(s6-c6) == 4 and len(c6-s6) == 1, "edge-mutation control failed")
    sample = min(c6)
    need({canon(q[i:]+q[:i]) for q in (sample,tuple(reversed(sample))) for i in range(6)} == {sample}
         and (c6-{sample}) != C6, "rotation/reversal or omitted-cycle control failed")

    # Two squares joined by a bridge: all roots find both; root 0 alone misses one.
    small = [[] for _ in range(8)]
    for u,v in ((0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),(3,4)):
        small[u].append(v); small[v].append(u)
    all4, root4 = cycles(small,4), cycles(small,4,roots=(0,))
    need(ncomponents(small) == 1 and len(all4) == 2 and len(root4) == 1
         and len(all4-root4) == 1, "omitted-root control failed")
    baseline = duad_baseline()

    result = {
        "marker":"CENTRE_EQUALITY_SIX_CYCLES_LITERAL_V1","status":"PASS",
        "checks":{"cubic_connected":True,"c4":0,"c6":4,"girth":6,
                  "cycle_free_vertices":True,"defect_symmetric":True,
                  "positive_opposite_matching":12,"negative_cross_cycle_matching":12},
        "counters":{"vertices":30,"edges":45,"c8":len(c8),
                    "defect_histogram":{str(k):hist[k] for k in (-1,0,1)},
                    "mutation_c6":len(s6),"root_control":[len(all4),len(root4)]},
        "sha256":{"witness":sha256(raw).hexdigest(),"rows":digest(rows),
                  "c6":digest(sorted(c6)),"defect":digest(e)},
        "duad_perfect_matching_baseline":baseline,
        "dfs":"literal simple paths from every root; closing-edge test; all rotations/reversal canonicalized",
    }
    print(json.dumps(result,sort_keys=True,separators=(",",":")))

if __name__ == "__main__":
    run()
