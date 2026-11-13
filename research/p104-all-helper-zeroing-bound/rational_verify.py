#!/usr/bin/env python3
"""Exact rational replay, adapted from the independently authored source census.

Prepared for CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from collections import Counter, defaultdict
from fractions import Fraction as F
from functools import lru_cache
from pathlib import Path
import gzip
import hashlib
import json

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "inputs/WORD.json.gz"
SOURCE_SHA = "acee323696b18914bd863d55341f92112b48d3d1dc1443c276efb6c396fcc0a9"


def need(ok, label):
    if not ok:
        raise ValueError(label)


@lru_cache(None)
def rational(text):
    return F(text)


def add(dst, src, q):
    need(dst is not src, "separate ADD operands")
    for h, value in src.items():
        value = value if q == 1 else -value if q == -1 else q * value
        value += dst.get(h, 0)
        if value:
            dst[h] = value
        else:
            dst.pop(h, None)


def run():
    raw = SOURCE.read_bytes()
    need(hashlib.sha256(raw).hexdigest() == SOURCE_SHA, "exact rational source bytes")
    w = json.loads(gzip.decompress(raw))
    records = json.loads((HERE / "ASSIGNMENT.json").read_text())
    assignment = {a["event"]: a for a in records}
    need(len(assignment) == len(records) == 468, "exact unique assignment count")
    n = w["public"]
    mains = set(w["live"]) | {i + 112 for i in w["live"]}
    mains |= set(w["hosted"]["X2"]) | set(w["hosted"]["Y2"])
    helpers = set(range(n)) - mains
    need(len(mains) == 400 and len(helpers) == 1101, "native main/helper partition")
    rows = [{i: F(1)} if i < n else {} for i in range(n + w["owned_fields"])]
    charts = w["initial"][:] + [None] * w["owned_fields"]
    paid, coverage, charges = Counter(), Counter(), defaultdict(list)
    for event, e in enumerate(w["program"]):
        op, a = e[:2]
        if op == "MOVE":
            need(charts[a] == e[2], "literal MOVE entrance")
            r = abs(len(w["frames"][e[2]]) - len(w["frames"][e[3]]))
            paid[r] += 1
            support = set(rows[a])
            need(bool(support), "no unconditional zero MOVE")
            if support & mains:
                need(event not in assignment, "funded census is exactly main-free")
                coverage["main_obstructed"] += 1
            else:
                need(event in assignment, "every main-free MOVE funded")
                z = assignment[event]
                h = z["assigned_helper"]
                need(h in helpers and h in support and z["rank"] == r,
                     "exact nonzero helper coefficient and paid rank")
                target = abs(len(w["frames"][w["initial"][h]])
                             - len(w["frames"][w["final"][h]]))
                need(z["target_rank"] == target, "source productive rank")
                charges[h].append((r, target))
                coverage["funded"] += 1
            charts[a] = e[3]
        elif op == "INIT":
            need(charts[a] is None, "fresh owned INIT")
            rows[a], charts[a] = {}, e[2]
        elif op == "CLEAR":
            need(charts[a] == e[2], "owned CLEAR chart")
            rows[a], charts[a] = {}, None
        elif op == "SCALE":
            need(charts[a] == e[-1], "scalar chart")
            q = rational(e[2])
            rows[a] = {h: q * v for h, v in rows[a].items() if q * v}
        elif op in ("ADD", "COPY"):
            b, q = e[2], rational(e[3])
            need(charts[a] == charts[b] == e[-1], "cocharted scalar contact")
            if op == "COPY":
                need(not rows[a], "COPY into ideal zero")
                rows[a] = {}
            add(rows[a], rows[b], q)
        else:
            raise ValueError(op)
    need(charts == w["final"] + [None] * w["owned_fields"], "all endpoint charts")
    need(all(rows[h] == {h: F(1)} for h in helpers), "all exact helper endpoints")
    need(all(not (set(rows[a]) & helpers) for a in mains), "no helper leaks into main outputs")
    for group in charges.values():
        if len(group) == 1:
            need(group[0][0] <= group[0][1], "singleton price monotonicity")
        else:
            need(group == [(1, 4), (1, 4)], "only double charge has exact square-root funding")
    need(coverage == {"main_obstructed": 5811, "funded": 468}, "complete source coverage")
    need(len(charges) == 467, "exact funding helper count")
    return {"status": "PASS_EXACT_RATIONAL_COLD_SUBSET_CERTIFICATE",
            "source_sha256": SOURCE_SHA, "move_coverage": dict(coverage),
            "paid_histogram": dict(sorted(paid.items())), "charged_helpers": len(charges),
            "all_helper_endpoints_restored": True, "no_helper_leaks_into_mains": True}


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
