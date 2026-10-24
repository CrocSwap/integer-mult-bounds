#!/usr/bin/env python3
"""Check the partial-prefix matching condition. Ali Romman, Codex assistance.

Apache-2.0. Use explicit exceptions so checks remain active under -O.
"""
from collections import Counter
from itertools import product
from pathlib import Path
import hashlib
import json
import sys


def require(condition, message):
    if not condition:
        raise ValueError(message)


def feasible_splits(points, n, length, omitted):
    require(type(n) is int and n >= 2 and type(length) is int
            and 4 <= length <= 1 << n and length % 2 == 0, "invalid cycle domain")
    require(type(omitted) is int and 0 <= omitted < n, "invalid omitted coordinate")
    require(2 <= len(points) <= length and len(set(points)) == len(points),
            "invalid prefix size")
    require(all(type(q) is int and 0 <= q < 1 << n for q in points), "invalid vertex")
    require(all((p ^ q).bit_count() == 1 for p, q in zip(points, points[1:])),
            "invalid path edge")
    remaining = length - len(points)
    seen = set(points)
    mask = ((1 << n) - 1) ^ (1 << omitted)

    def side(q):
        return (q & mask).bit_count() % 2

    a = sum(side(q) == 0 for q in points)
    b = len(points) - a
    stays = [0, 0]
    crossing = 0
    for p, q in zip(points, points[1:]):
        if side(p) == side(q):
            stays[side(p)] += 1
        else:
            crossing += 1
    if remaining == 0:
        return {(a, b)} if (points[-1] ^ points[0]).bit_count() == 1 else set()
    endpoints = {points[0], points[-1]}
    cheap = [0, 0]
    pairs = [0, 0]
    available = [0, 0]
    for q in range(1 << n):
        if q not in seen:
            j = side(q)
            available[j] += 1
            mate = q ^ (1 << omitted)
            if mate in endpoints:
                cheap[j] += 1
            elif mate not in seen and q < mate:
                pairs[j] += 1
    result = set()
    for x in range(max(0, remaining-available[1]), min(remaining, available[0])+1):
        totals = (a+x, b+remaining-x)
        added = (x, remaining-x)
        upper = []
        for j in (0, 1):
            one = min(cheap[j], added[j])
            upper.append(stays[j] + one + min(pairs[j], (added[j]-one)//2))
        low = max(crossing, 2 if min(totals) > 0 else 0,
                  *(2*totals[j]-2*upper[j] for j in (0, 1)))
        high = min(crossing+remaining+1,
                   *(2*totals[j]-2*stays[j] for j in (0, 1)))
        low += low % 2
        if low <= high:
            result.add(totals)
    return result


def canonical(word):
    names = {}
    return tuple(names.setdefault(d, len(names)) for d in word)


def direct_words(n, length):
    found = set()
    for word in product(range(n), repeat=length):
        points = [0]
        for d in word:
            points.append(points[-1] ^ (1 << d))
        if points[-1] == 0 and len(set(points[:-1])) == length:
            found.add(canonical(word))
    return found


def scan(n, length):
    counts = Counter()
    witness = None
    closed = set()
    controls = {}

    def walk(word, points, highest):
        nonlocal witness
        counts["prefixes"] += 1
        actual = [set() for _ in range(n)]
        if len(points) == length:
            if points[-1].bit_count() == 1:
                counts["cycles"] += 1
                closed.add(word + (points[-1].bit_length() - 1,))
                for v in range(n):
                    mask = ((1 << n) - 1) ^ (1 << v)
                    a = sum((q & mask).bit_count() % 2 == 0 for q in points)
                    actual[v].add((a, length - a))
        else:
            for d in range(min(highest + 1, n - 1) + 1):
                q = points[-1] ^ (1 << d)
                if q not in points:
                    child = walk(word + (d,), points + (q,), max(highest, d))
                    for v in range(n):
                        actual[v].update(child[v])
        if len(points) >= 2:
            for v in range(n):
                proposed = feasible_splits(points, n, length, v)
                counts["split_checks"] += 1
                require(actual[v] <= proposed, "false completion prune")
                counts["realizable_split_checks"] += len(actual[v])
                if not proposed:
                    counts["rejected_prefix_functionals"] += 1
                    r = length - len(points)
                    mask = ((1 << n) - 1) ^ (1 << v)
                    a = sum((q & mask).bit_count() % 2 == 0 for q in points)
                    b = len(points) - a
                    global_ok = any(max(a+x, b+r-x) <= 2*min(a+x, b+r-x)
                                    for x in range(r+1))
                    if r > 0 and points[-1].bit_count() <= r+1 and global_ok:
                        counts["strict_rejections_before_leaf"] += 1
                        if witness is None:
                            witness = {"word": word, "omitted": v, "points": points}
                if actual[v] and any(a != b for a,b in actual[v]):
                    controls.setdefault("unbalanced_completion", (word, v))
        return actual

    walk((), (0,), -1)
    if n <= 4 and length <= 8:
        require(closed == direct_words(n, length), "independent word enumeration differs")
    return {"n": n, "length": length, **dict(counts), "strict_witness": witness,
            "unbalanced_completion_control": controls.get("unbalanced_completion")}


def capacity_checks():
    # Enumerate choices independently of the greedy capacity formula.
    checked = 0
    for cheap in range(4):
        for pairs in range(5):
            for singles in range(4):
                costs = (1,) * cheap + (2,) * pairs
                for budget in range(cheap + 2*pairs + singles + 1):
                    best = max((sum(chosen) for chosen in product((0, 1), repeat=len(costs))
                                if sum(c*t for c,t in zip(costs, chosen)) <= budget), default=0)
                    one = min(cheap, budget)
                    greedy = one + min(pairs, (budget-one)//2)
                    require(best == greedy, "matching capacity differs")
                    checked += 1
    return checked


def invalid_controls():
    cases = [((0,1,0),3,6,0), ((0,3),3,6,0), ((0,1),3,5,0),
             ((0,1),3,10,0), ((0,1),3,6,3), ((0,8),3,6,0), ((0,),3,6,0)]
    for args in cases:
        try:
            feasible_splits(*args)
        except ValueError:
            continue
        raise ValueError("invalid input accepted")
    # Both types of final edge remain legal. Reusing an old interior does not.
    require(feasible_splits((0,1,3,2),2,4,0) == {(2,2)}, "crossing closure rejected")
    require(feasible_splits((0,2,3,1),2,4,0) == {(2,2)}, "preserving closure rejected")
    require(not feasible_splits((0,1,3,7),3,4,0), "non-edge closure accepted")
    return len(cases) + 3


def evidence():
    rows = [scan(n, length) for n,length in ((3,6),(4,8),(4,10),(5,12))]
    require([r["cycles"] for r in rows] == [4,29,110,3695], "cycle counts changed")
    require(all(r["strict_rejections_before_leaf"] > 0 for r in rows[1:]), "no strict gain")
    result = {"schema": "f7-prefix-matching-capacity/v1", "scope": "simple cycles only",
              "domains": rows, "capacity_cases": capacity_checks(),
              "semantic_controls": invalid_controls()}
    here = Path(__file__).resolve().parent
    result["source_sha256"] = {name: hashlib.sha256((here/name).read_bytes()).hexdigest()
                               for name in ("README.md", "verify.py", "TASK.json", "VERIFY.json", "SOURCES.json")}
    return result


def main():
    result = evidence()
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if sys.argv[1:] == ["--emit-receipt"]:
        print(encoded, end="")
    else:
        require(not sys.argv[1:], "unexpected argument")
        path = Path(__file__).resolve().with_name("RESULT.json")
        require(path.read_text(encoding="utf-8") == encoded, "receipt differs")
        print("PASS_F7_PREFIX_MATCHING_CAPACITY")


if __name__ == "__main__":
    main()
