"""Pinned visit/finite-field helper retained from the author exploration."""
from collections import defaultdict
from functools import lru_cache
FULL=(1<<512)-1

def need(ok, label):
    if not ok:
        raise ValueError(label)

@lru_cache(None)
def basis(mask):
    pivots = {}
    while mask:
        low = mask & -mask
        value = low.bit_length() - 1
        mask -= low
        for p in sorted(pivots, reverse=True):
            if value >> p & 1:
                value ^= pivots[p]
        if value:
            pivots[value.bit_length() - 1] = value
    return tuple(pivots[p] for p in sorted(pivots, reverse=True))

def span(vectors):
    values = {0}
    for value in vectors:
        values |= {x ^ value for x in values}
    return sum(1 << x for x in values)

@lru_cache(None)
def join(a, b):
    return span((*basis(a), *basis(b)))

def dim(mask):
    return mask.bit_count().bit_length() - 1

def comparable(a, b):
    return a & b in (a, b)

def visit_components(word):
    visits, parents = [], []
    current = [None] * (word["public"] + word["owned_fields"])

    def new(r, chart, entrance, frozen):
        index = len(visits)
        visits.append({"id": index, "owner": r, "chart": chart,
                       "entrance": entrance, "exit": None,
                       "frozen": frozen, "scalar_events": []})
        parents.append(index)
        current[r] = index

    def find(a):
        while parents[a] != a:
            parents[a] = parents[parents[a]]
            a = parents[a]
        return a

    for r, chart in enumerate(word["initial"]):
        new(r, chart, None, "public entrance")
    for i, event in enumerate(word["program"]):
        op, r = event[:2]
        if op == "INIT":
            need(current[r] is None, "fresh INIT")
            new(r, event[2], None, "INIT")
        elif op == "CLEAR":
            visit = visits[current[r]]
            need(visit["chart"] == event[2], "CLEAR chart")
            visit["frozen"] = "CLEAR"
            current[r] = None
        elif op == "MOVE":
            need(bool(event[4]) == (r >= word["public"]), "MOVE ownership bit")
            visit = visits[current[r]]
            need(visit["chart"] == event[2], "MOVE entrance")
            visit["exit"] = i
            new(r, event[3], i, None)
        else:
            visit = visits[current[r]]
            need(visit["chart"] == event[-1], "scalar chart")
            visit["scalar_events"].append(i)
            if op in ("ADD", "COPY"):
                other = visits[current[event[2]]]
                need(other["chart"] == visit["chart"], "cocharted operands")
                other["scalar_events"].append(i)
                parents[find(visit["id"])] = find(other["id"])
    for r in range(word["public"]):
        visit = visits[current[r]]
        need(visit["chart"] == word["final"][r], "public exit")
        visit["frozen"] = "public exit"
    groups = defaultdict(list)
    for visit in visits:
        groups[find(visit["id"])].append(visit)
    return visits, list(groups.values())
