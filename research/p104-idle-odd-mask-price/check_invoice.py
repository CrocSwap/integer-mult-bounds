#!/usr/bin/env python3
"""Exact histogram/rational-interval control of #7113 and SchemaCostB.

Uses only Python integers/Fraction.  Every power is bracketed by an integer
100th-root inequality, not a floating-point approximation.  This validates
arithmetic/accounting for the pinned input, not Lean Legal or the hypotheses
of a high-k theorem.  Source details are in RESULT.md.
"""
from collections import Counter
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
CALLER = HERE / "expected_ODD-TYPE-AB-CALLER.json"
assert sha256(CALLER.read_bytes()).hexdigest() == (
    "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc"
)
data = json.loads(CALLER.read_text())
assert data["schema"] == "mixed-root-caller/1"
k = data["stages"]
assert k == 17 and len(data["events"]) == 4783
stages = [e for e in data["events"] if e[0] == "J"]
assert [e[1] for e in stages] == list(range(1, k + 1))
assert sum(len(t["ports"]) for t in data["types"].values()) == 104
assert set(data["types"]["A"]["ports"]).isdisjoint(data["types"]["B"]["ports"])
assert data["types"]["A"]["alpha2"] == "-1"
assert data["types"]["A"]["beta2"] == "0"
for event in stages:
    _, stage, a, b = event
    assert len(a) == 4 and len(set(a)) == 4 and all(0 <= x < 36 for x in a)
    assert len(b) == 4 and b[0] != b[1]
    assert all(36 <= x < 72 for x in b[:2]) and b[2:] == ["-1", "1/2"]
    assert 1 <= stage <= k


def clean(c):
    return {a: b for a, b in sorted(c.items()) if b}


def add(dest, rank, amount):
    dest[rank] += amount


bytype = {}
target_total, paid_total = Counter(), Counter()
for t, ty in data["types"].items():
    n, ports, rows = ty["roles"], len(ty["ports"]), ty["diagonal"]
    assert n == len(rows) == 36
    assert ports == {"A": 96, "B": 8}[t]
    target, paid, mdl, corrections = Counter(), Counter(), Counter(), Counter()
    opcounts, idle_odd = Counter(), []
    for row in rows:
        assert len(row) == k + 2 and row[:2] == [-1, 0]
        assert set(row[2:]) <= {0, 1} and sum(row[2:]) >= 1
        add(target, (row[0] % 2) + 8 * sum(row[2:]), 1)
    q = 0
    for index, ev in enumerate(data["events"]):
        if ev[0] != t:
            continue
        op = ev[1]
        opcounts[op] += 1
        if op == "QUERY":
            assert ev[4] % 2 == 1
            add(paid, 1, 1)
            q += 1
        elif op in ("IDLE_ONE", "IDLE_ODD"):
            S = ev[3]
            assert len(S) == len(set(S)) and all(1 <= stage <= k for stage in S)
            d = len(S)
            add(paid, 8 * d + (op == "IDLE_ODD"), 1)
            if d:
                add(mdl, 8 * d, 1)
            if op == "IDLE_ODD":
                assert ev[4] % 2 == 1
                q += 1
                corrections[d] += 1
                idle_odd.append((index, d, S))
        else:
            assert op in {"ADD", "SCALE", "SWAP", "LAMBDA"}, ev
    # In jA there are four singleton D-incidence events and two q-odd
    # host columns per stage; in jB there are two of each.
    contacts = {"A": 4, "B": 2}[t]
    add(mdl, 8, contacts * k)
    iota = 2 * k + q
    assert iota == n + 2 and q == n - (2 * k - 2) == 4

    repo = Counter(target)
    repo.subtract(paid)
    add(repo, 8, -contacts * k)
    model = Counter(target)
    model.subtract(mdl)
    add(model, 1, -q)
    delta = Counter()
    for d, count in corrections.items():
        if d:
            add(delta, 8 * d, count)
        add(delta, 1, count)
        add(delta, 8 * d + 1, -count)
    difference = Counter(repo)
    difference.subtract(model)
    assert clean(difference) == clean(delta)
    bytype[t] = dict(ports=ports, target=target, paid=paid, model=model,
                     repo=repo, delta=delta, corrections=corrections,
                     opcounts=opcounts, odd=idle_odd, q=q)
    for rank, count in target.items():
        add(target_total, rank, ports * count)
    for rank, count in paid.items():
        add(paid_total, rank, ports * count)

assert clean(target_total) == dict([(9,416),(17,416),(25,416),(33,416),
    (41,416),(49,416),(57,416),(65,416),(73,208),(137,208)])
assert clean(paid_total) == dict([(1,384),(8,656),(9,32),(16,416),
    (24,416),(32,416),(40,416),(48,416),(56,416),(64,208)])
assert bytype["A"]["corrections"] == Counter()
assert bytype["B"]["corrections"] == Counter({1: 4})

# Bracket n^(99/100) by L/D and (L+1)/D, by checking
# L^100 <= n^99 D^100 < (L+1)^100.  n is a nonnegative integer.
D = 10 ** 18
cache = {}


def root_bounds(n):
    if n in cache:
        return cache[n]
    if n == 0:
        return Fraction(0), Fraction(0)
    rad = pow(n, 99) * pow(D, 100)
    lo, hi = 0, n * D + 1
    while lo + 1 < hi:
        mid = (lo + hi) // 2
        if pow(mid, 100) <= rad:
            lo = mid
        else:
            hi = mid
    assert pow(lo, 100) <= rad < pow(lo + 1, 100)
    cache[n] = Fraction(lo, D), Fraction(lo + 1, D)
    return cache[n]


def bounds(hist):
    lower = upper = Fraction(0)
    for rank, count in hist.items():
        a, b = root_bounds(rank)
        if count >= 0:
            lower += count * a
            upper += count * b
        else:
            lower += count * b
            upper += count * a
    return lower, upper


def delta(d):
    h = Counter()
    if d:
        add(h, 8*d, 1)
    add(h, 1, 1)
    add(h, 8*d+1, -1)
    return h


def scale(interval, factor):
    assert factor >= 0
    return tuple(x * factor for x in interval)


def fmt(interval):
    # Outward-rounded decimal representation of the exact rational enclosure.
    scale10 = 10 ** 20
    lo, hi = interval
    ilo = lo.numerator * scale10 // lo.denominator
    ihi = -((-hi.numerator * scale10) // hi.denominator)
    def render(i):
        sign = "-" if i < 0 else ""
        i = abs(i)
        return f"{sign}{i // scale10}.{i % scale10:020d}"
    return "[" + render(ilo) + ", " + render(ihi) + "]"


# A concrete local event falsifies the proposed uniform 0.05 correction.
assert bounds(delta(7))[1] < Fraction(1, 20)
assert bounds(delta(8))[0] > Fraction(1, 20)
# Check the entire encoded range, not just the endpoints, by exact intervals.
for d in range(1, 26):
    assert bounds(delta(d))[1] < bounds(delta(d + 1))[0]
assert bounds(delta(26))[1] < Fraction(62, 1000)
assert bounds(delta(0)) == (0, 0)

for t in ("A", "B"):
    x = bytype[t]
    print(f"{t}: ports={x['ports']}, Q={x['q']}, operations={clean(x['opcounts'])}")
    print("  targets:", clean(x["target"]))
    print("  paid:", clean(x["paid"]))
    print("  odd idles (0-based index, size, stages):", x["odd"])
    print("  104/k * repo in", fmt(scale(bounds(x["repo"]), Fraction(104, k))))
    print("  cHatQ from event invoice in", fmt(scale(bounds(x["model"]), Fraction(104, k))))
    print("  repo - (k/104)*cHatQ in", fmt(bounds(x["delta"])))

for d in (1, 7, 8, 17, 26, 77):
    print(f"delta({d}) in", fmt(bounds(delta(d))))
print("weighted 7113 correction in", fmt(scale(bounds(delta(1)), Fraction(8 * 4, k))))
weighted = Counter()
for t in ("A", "B"):
    for rank, count in bytype[t]["repo"].items():
        add(weighted, rank, bytype[t]["ports"] * count)
print("weighted 7113 real repo / k in", fmt(scale(bounds(weighted), Fraction(1, k))))
print("PASS: exact histograms, symbolic identities, interval certificates, controls")
