#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Krzysztof Wójt; substantial assistance from OpenAI Codex and Luna.
"""Finite evaluation of the supplied labeled family only; no global coverage claim."""
from __future__ import annotations
import hashlib, json, time
from itertools import product
from pathlib import Path

N, FREE = 15, (12, 13, 14)
PATTERNS = tuple(product((1, 2), repeat=3))
EXPECTED = {
    (1,1,1):(729,729,693,36,36,0), (1,1,2):(2916,2916,1908,1008,1008,0),
    (1,2,1):(2916,2916,1908,1008,1008,0), (1,2,2):(11664,15552,8208,7344,7200,144),
    (2,1,1):(2916,2916,1908,1008,1008,0), (2,1,2):(11664,15552,8208,7344,7200,144),
    (2,2,1):(11664,15552,8208,7344,7200,144), (2,2,2):(46656,78336,60480,17856,17856,0),
}

def require(ok, message):
    if not ok:
        raise RuntimeError(message)

def pair_options(s_i):
    if s_i == 1:
        # The diagonal leaf needs one free neighbor; its mate needs two.
        return tuple(((x,), tuple(y for y in FREE if y != x)) for x in FREE)
    if s_i == 2:
        # Preserve ordered leaf labels and choose distinct free labels.
        return tuple(((x,), (y,)) for x in FREE for y in FREE if x != y)
    raise ValueError(s_i)

def fixed_rows(s):
    rows = [set() for _ in range(N)]
    def add(b, d):
        require(d not in rows[b], ("duplicate fixed edge", b, d)); rows[b].add(d)
    for i in range(3):
        for j in range(3):
            if i != j: add(i, j)
        add(i, 3+i); add(3+i, i)
        for k in range(2):
            leaf = 6+2*i+k; add(3+i, leaf); add(leaf, 3+i)
    for i, s_i in enumerate(s):
        for k in range(s_i):
            leaf = 6+2*i+k; add(leaf, leaf)
    return tuple(tuple(sorted(row)) for row in rows)

def matrix_index():
    index = {}
    for mask in range(1 << 9):
        rd = tuple(sum((mask >> (3*i+j)) & 1 for j in range(3)) for i in range(3))
        cd = tuple(sum((mask >> (3*i+j)) & 1 for i in range(3)) for j in range(3))
        index.setdefault((rd, cd), []).append(mask)
    return index

MATRIX_INDEX = matrix_index()

def assemble_rows(base, b_attach, d_attach, mask):
    rows = [list(row) for row in base]
    for b, ds in b_attach.items(): rows[b].extend(ds)
    for d, bs in d_attach.items():
        for b in bs: rows[b].append(d)
    for i in range(3):
        for j in range(3):
            if (mask >> (3*i+j)) & 1: rows[12+i].append(12+j)
    rows = tuple(tuple(sorted(row)) for row in rows)
    require(all(len(r) == 3 and len(set(r)) == 3 for r in rows), "B cubic/simplicity")
    cols = [0]*N
    for row in rows:
        for d in row: cols[d] += 1
    require(cols == [3]*N, "D cubic degree")
    return rows

def adjacency(rows):
    adj = [[] for _ in range(2*N)]
    for b, ds in enumerate(rows):
        for d in ds: adj[b].append(N+d); adj[N+d].append(b)
    return tuple(tuple(sorted(ns)) for ns in adj)

def c4_by_trace(adj):
    # For a simple graph, tr(A^4)=2m+4*sum_v C(deg(v),2)+8*C4.
    trace = 0
    for v in range(len(adj)):
        walks2 = {}
        for u in adj[v]:
            for w in adj[u]: walks2[w] = walks2.get(w, 0)+1
        trace += sum(x*x for x in walks2.values())
    m = sum(map(len, adj))//2
    baseline = 2*m + 4*sum(len(ns)*(len(ns)-1)//2 for ns in adj)
    numerator = trace-baseline
    require(numerator >= 0 and numerator % 8 == 0, ("trace(A^4) identity", trace, baseline))
    return numerator//8

def c6_by_length3_paths(rows):
    # In a C4-free bipartite graph, distinct simple 3-paths between opposite
    # nonneighbors are internally disjoint; choose(p3,2) counts C6s at each
    # endpoint, which has a unique antipode. Call only after the C4 check.
    d_to_b = [[] for _ in range(N)]
    for b, ds in enumerate(rows):
        for d in ds: d_to_b[d].append(b)
    rowsets = [set(ds) for ds in rows]; p3 = [[0]*N for _ in range(N)]
    for b, ds in enumerate(rows):
        for d0 in ds:
            for b1 in d_to_b[d0]:
                if b1 != b:
                    for d1 in rows[b1]:
                        if d1 != d0 and d1 not in rowsets[b]: p3[b][d1] += 1
    through_b, through_d = [0]*N, [0]*N
    for b in range(N):
        for d in range(N):
            if d not in rowsets[b]:
                k = p3[b][d]; q = k*(k-1)//2
                through_b[b] += q; through_d[d] += q
    tb, td = sum(through_b), sum(through_d)
    require(tb == td and tb % 3 == 0, ("C6 antipode totals", tb, td))
    return tuple(through_b+through_d), tb//3

def literal_cycles(adj, length):
    found = set()
    for start in range(len(adj)):
        path, used = [start], {start}
        def visit():
            cur = path[-1]
            if len(path) == length:
                if start in adj[cur]:
                    fwd = tuple(path); rev = (start,)+tuple(reversed(path[1:]))
                    found.add(min(fwd, rev))
                return
            for nxt in adj[cur]:
                if nxt <= start or nxt in used: continue
                used.add(nxt); path.append(nxt); visit(); path.pop(); used.remove(nxt)
        visit()
    return found

def cycle_incidence(cycles):
    counts = [0]*(2*N)
    for cycle in cycles:
        for v in cycle: counts[v] += 1
    return tuple(counts)

def run_controls(witness):
    c4rows = [[] for _ in range(N)]; c4rows[0], c4rows[1] = [0,1], [0,1]
    a = adjacency(c4rows)
    require(c4_by_trace(a) == 1 and len(literal_cycles(a, 4)) == 1, "planted C4 control")
    # Two 6-cycles share B0, so its incidence must be two and C4 count zero.
    overlap = [[] for _ in range(N)]
    overlap[0] = [0,2,3,5]
    overlap[1], overlap[2], overlap[3], overlap[4] = [0,1], [1,2], [3,4], [4,5]
    a = adjacency(overlap); pi, pc = c6_by_length3_paths(overlap); cycles = literal_cycles(a, 6)
    require(c4_by_trace(a) == 0 and pc == 2 and max(pi) == 2, "overlap C6 path control")
    require(len(cycles) == 2 and cycle_incidence(cycles) == pi, "overlap C6 DFS control")
    raw = witness.get("rows")
    require(isinstance(raw, list) and len(raw) == N, "witness rows schema")
    rows = tuple(tuple(sorted(r)) for r in raw)
    require(all(len(r) == 3 and len(set(r)) == 3 for r in rows), "witness cubic rows")
    declared = witness.get("six_cycles")
    require(isinstance(declared, list) and len(declared) == 4, "witness declares four C6s")
    a = adjacency(rows); pi, pc = c6_by_length3_paths(rows); cycles = literal_cycles(a, 6)
    require(c4_by_trace(a) == 0 and pc == 4 and len(cycles) == 4, "witness C6 count")
    require(cycle_incidence(cycles) == pi, "witness C6 incidence disagreement")
    return rows, {"planted_c4":1, "overlap_c6s":2, "witness_c6s":len(cycles)}

def main():
    witness = json.loads(Path(__file__).with_name("WITNESS.json").read_text(encoding="utf-8"))
    witness_rows, controls = run_controls(witness)
    witness_key = tuple(tuple(sorted(r)) for r in witness_rows); witness_seen = False
    started = time.monotonic()
    totals = dict(attachments=0, graphs=0, c4_rejected=0, c4_free=0, multi_c6_rejected=0)
    winners, pattern_results, seen = [], [], set()
    for s in PATTERNS:
        if time.monotonic()-started > 240: raise TimeoutError("enumeration exceeded four minutes")
        bo, do = tuple(pair_options(x) for x in s), tuple(pair_options(x) for x in s)
        item = dict(s=list(s), attachments=0, graphs=0, c4_rejected=0, c4_free=0,
                    multi_c6_rejected=0, winners=0)
        digest = hashlib.sha256(); base = fixed_rows(s)
        for bchoices in product(*bo):
            for dchoices in product(*do):
                item["attachments"] += 1; totals["attachments"] += 1
                ba, da, rr, cc = {}, {}, [3]*3, [3]*3
                for i, pair in enumerate(bchoices):
                    for k, ds in enumerate(pair):
                        ba[6+2*i+k] = ds
                        for d in ds: cc[d-12] -= 1
                for i, pair in enumerate(dchoices):
                    for k, bs in enumerate(pair):
                        da[6+2*i+k] = bs
                        for b in bs: rr[b-12] -= 1
                require(min(rr+cc) >= 0 and sum(rr) == sum(cc), ("residual degrees", s))
                for mask in MATRIX_INDEX.get((tuple(rr), tuple(cc)), ()):
                    rows = assemble_rows(base, ba, da, mask); item["graphs"] += 1; totals["graphs"] += 1
                    adj = adjacency(rows)
                    if c4_by_trace(adj):
                        item["c4_rejected"] += 1; totals["c4_rejected"] += 1; continue
                    item["c4_free"] += 1; totals["c4_free"] += 1
                    incidence, count = c6_by_length3_paths(rows)
                    if max(incidence) > 1:
                        item["multi_c6_rejected"] += 1; totals["multi_c6_rejected"] += 1; continue
                    require(count == 4, ("admitted C6 count", s, count))
                    key = tuple(tuple(r) for r in rows)
                    require(key not in seen, ("duplicate labeled graph", s)); seen.add(key)
                    witness_seen |= key == witness_key
                    digest.update(json.dumps(rows, separators=(",", ":")).encode("ascii")+b"\n")
                    item["winners"] += 1; winners.append((s, rows, adj, incidence, count))
        observed = tuple(item[k] for k in ("attachments", "graphs", "c4_rejected", "c4_free", "multi_c6_rejected", "winners"))
        require(observed == EXPECTED[s], ("per-pattern count drift", s, observed, EXPECTED[s]))
        item["rows_sha256"] = digest.hexdigest(); pattern_results.append(item)
    require(totals == dict(attachments=91125, graphs=134469, c4_rejected=91521, c4_free=42948,
                           multi_c6_rejected=42516), ("global count drift", totals))
    require(len(winners) == 432 and len(seen) == 432, "winner total/uniqueness drift")
    require(witness_seen, "WITNESS rows absent from admitted winners")
    for s, rows, adj, incidence, count in winners:
        cycles = literal_cycles(adj, 6)
        require(len(cycles) == count and cycle_incidence(cycles) == incidence, ("literal DFS mismatch", s))
    result = {"marker":"PASS finite supplied-family evaluation",
        "scope":"Explicit labeled normal-form family only; no global coverage claim.",
        "per_pattern":pattern_results,
        "totals":{**totals, "winners":len(winners), "literal_dfs_winners":len(winners)},
        "witness":{"canonical_rows_admitted":witness_seen, "literal_c6_count":controls["witness_c6s"]},
        "controls":controls}
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))

if __name__ == "__main__":
    main()
