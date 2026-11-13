#!/usr/bin/env python3
"""Exact pure-Python gate for all frozen-boundary chart-corridor choices."""
from collections import Counter
from itertools import product
from pathlib import Path
import gzip
import hashlib
import json
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import core as R

PIN = "acee323696b18914bd863d55341f92112b48d3d1dc1443c276efb6c396fcc0a9"


def choices(entrance, ceiling):
    complement, current = [], entrance
    for vector in R.basis(ceiling):
        if not current >> vector & 1:
            complement.append(vector)
            current = R.join(current, (1 << vector) | 1)
    R.need(current == ceiling, "full quotient basis")
    out = {entrance}
    for bits in range(1, 1 << len(complement)):
        vector = 0
        for j, value in enumerate(complement):
            if bits >> j & 1:
                vector ^= value
        out |= {R.join(old, (1 << vector) | 1) for old in tuple(out)}
    R.need(all(a & entrance == entrance and a & ceiling == a for a in out), "subspace interval")
    return sorted(out, key=lambda a: (R.dim(a), a))


def run(source=None, expected_sha=PIN, require_zero=True, extra_frozen=()):
    source = source or (HERE / "inputs/pr7481-WORD.json.gz")
    raw = Path(source).read_bytes()
    R.need(hashlib.sha256(raw).hexdigest() == expected_sha, "exact word pin")
    word = json.loads(gzip.decompress(raw))
    visits, groups = R.visit_components(word)
    chart = [R.span(word["frames"][g[0]["chart"]]) for g in groups]
    frozen = [any(v["frozen"] for v in g) or j in extra_frozen for j, g in enumerate(groups)]
    vertex = {v["id"]: j for j, g in enumerate(groups) for v in g}
    ent = {v["entrance"]: vertex[v["id"]] for v in visits if v["entrance"] is not None}
    ext = {v["exit"]: vertex[v["id"]] for v in visits if v["exit"] is not None}
    moves = [(i, ext[i], ent[i], e[4]) for i, e in enumerate(word["program"]) if e[0] == "MOVE"]
    upper = [set() for _ in groups]
    lower = [set() for _ in groups]
    for _, a, b, owned in moves:
        if not owned:
            R.need(chart[a] & chart[b] == chart[a] and R.dim(chart[a]) < R.dim(chart[b]), "public ascending edge")
            upper[a].add(b)
            lower[b].add(a)
    floor = [1] * len(groups)
    for a in sorted(range(len(groups)), key=lambda a: R.dim(chart[a])):
        if frozen[a]:
            floor[a] = chart[a]
        else:
            for b in lower[a]:
                floor[a] = R.join(floor[a], floor[b])
    cap = [R.FULL] * len(groups)
    for a in sorted(range(len(groups)), key=lambda a: R.dim(chart[a]), reverse=True):
        if frozen[a]:
            cap[a] = chart[a]
        else:
            for b in upper[a]:
                cap[a] &= cap[b]
        R.need(chart[a] & cap[a] == chart[a], "reachable ceiling")
    free = {a for a in range(len(groups)) if not frozen[a] and floor[a] != cap[a]}
    owned_internal = [a for a, g in enumerate(groups) if not frozen[a] and any(v["owner"] >= word["public"] for v in g)]
    R.need(all(floor[a] & chart[a] == floor[a] and chart[a] & cap[a] == chart[a] for a in range(len(groups))), "complete public corridor bounds")
    adjacent = {a: set() for a in free}
    for _, a, b, _ in moves:
        if a in free and b in free:
            adjacent[a].add(b)
            adjacent[b].add(a)
    factors, left = [], free.copy()
    while left:
        queue = [left.pop()]
        found = set(queue)
        while queue:
            a = queue.pop()
            for b in adjacent[a] - found:
                found.add(b)
                left.discard(b)
                queue.append(b)
        factors.append(sorted(found))
    factors.sort()
    options = {a: choices(floor[a], cap[a]) for a in free}
    for a in free:
        R.need(chart[a] in options[a], "original chart in complete domain")
        R.need(len(options[a]) == (1,2,5,16)[R.dim(cap[a])-R.dim(floor[a])], "Gaussian interval cardinality")
    receipts = []
    for factor in factors:
        incident = [(i, a, b, owned) for i, a, b, owned in moves if a in factor or b in factor]
        old = Counter(abs(R.dim(chart[a]) - R.dim(chart[b])) for _, a, b, _ in incident)
        maxima, profiles, total = [0] * 9, [], 0
        for picked in product(*(options[a] for a in factor)):
            total += 1
            selected = dict(zip(factor, picked))
            frame = lambda a: selected.get(a, chart[a])
            if any(frame(a) & frame(b) != frame(a) for _, a, b, owned in incident if not owned):
                continue
            if any(not R.comparable(frame(a), frame(b)) for _, a, b, owned in incident if owned):
                continue
            new = Counter(abs(R.dim(frame(a)) - R.dim(frame(b))) for _, a, b, _ in incident)
            delta = {r: new[r] - old[r] for r in new.keys() | old.keys() if new[r] != old[r]}
            savings = [-sum(c * min(r, k) for r, c in delta.items()) for k in range(1, 10)]
            maxima = [max(a, b) for a, b in zip(maxima, savings)]
            profiles.append({"choice_dimensions": list(map(R.dim, picked)), "paid_delta": delta, "extreme_savings": savings})
        R.need(bool(profiles), "original legal assignment retained")
        if require_zero:
            R.need(maxima == [0] * 9, "all exact concave generators")
        receipts.append({"factor": factor, "cases": total, "feasible": len(profiles), "choice_counts": [len(options[a]) for a in factor], "maximum_extreme_savings": maxima, "profiles": profiles})
    result = {"status": "PASS_COMPLETE_CONTACT_RECHARTING_CONCAVE_GATE", "source_sha256": expected_sha,
              "source_events": len(word["program"]), "components": len(groups), "move_positions": len(moves),
              "free_components": sorted(free), "free_count": len(free), "original_paid": dict(sorted(Counter(abs(R.dim(chart[a])-R.dim(chart[b])) for _,a,b,_ in moves).items())), "owned_internal_components": owned_internal,
              "independent_factors": len(factors), "total_factor_cases": sum(a["cases"] for a in receipts),
              "feasible_factor_cases": sum(a["feasible"] for a in receipts), "factors": receipts,
              "scope": "All per-component charts in the public floor/cap corridors; frozen external/lifecycle boundaries and scalar contacts fixed; public ascent retained; owned maps comparable in either direction. Actual positive-child ranks bounded below by dimension gaps, all ordinary maps granted free. Exact zero for every increasing concave rank price; no new kappa or unrestricted source obstruction."}
    if not require_zero:
        result["status"] = "CONTROL_OPTIMIZER_RESULT"
    return result


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
