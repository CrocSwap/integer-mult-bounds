#!/usr/bin/env python3
"""Independent exact past/future coframe history check at every owned MOVE.

Research checkpoint, not a new supplier. All public input rows remain arbitrary.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import gzip
import json
import time

ROOT = Path(__file__).resolve().parent
PIN = "acee323696b18914bd863d55341f92112b48d3d1dc1443c276efb6c396fcc0a9"


def need(ok, label):
    if not ok:
        raise ValueError(label)


def add(a, b, c):
    need(a is not b, "row alias")
    for k, x in b.items():
        y = a.get(k, 0) + c * x
        if y:
            a[k] = y
        else:
            a.pop(k, None)


def key(frame):
    # Enumerating at most 512 addresses gives an independent canonical key.
    span = {0}
    for v in frame:
        span |= {x ^ v for x in span}
    return tuple(sorted(span))


def reduce(row, basis):
    row = row.copy()
    while row:
        pivot = min(row)
        if pivot not in basis:
            return row
        add(row, basis[pivot], -row[pivot])
    return row


def put(basis, row):
    row = reduce(row, basis)
    if not row:
        return False
    p = min(row)
    a = row[p]
    basis[p] = {k: v / a for k, v in row.items()}
    return True


def run(source=ROOT / "inputs/WORD.json.gz", author=None, kernel=None):
    start = time.monotonic()
    raw = source.read_bytes()
    need(sha256(raw).hexdigest() == PIN, "source byte pin")
    word = json.loads(gzip.decompress(raw))
    frames = list(map(key, word["frames"]))
    events = word["program"]
    cuts = {i: e for i, e in enumerate(events) if e[0] == "MOVE" and e[4]}
    need(len(cuts) == 47, "complete owned-MOVE set")
    past = {frames[e[3]]: {} for e in cuts.values()}
    future = {frames[e[2]]: {} for e in cuts.values()}
    public = word["public"]
    rows = [{i: Q(1)} for i in range(public)] + [None] * word["owned_fields"]
    chart = word["initial"].copy() + [None] * word["owned_fields"]
    departures = []
    answers = {}
    counts = Counter()
    past_controls = 0

    for owner, f in enumerate(word["initial"]):
        if frames[f] in past:
            put(past[frames[f]], rows[owner])

    for i, e in enumerate(events):
        if i % 128 == 0:
            need(time.monotonic() - start < 60, "bounded first-stage runtime")
        op, a = e[:2]
        counts[op] += 1
        if op == "MOVE":
            old, new = e[2:4]
            need(chart[a] == old and rows[a] is not None, "MOVE live source")
            if i in cuts:
                h = past[frames[new]]
                remainder = reduce(rows[a], h)
                trial = {p: r.copy() for p, r in h.items()}
                if remainder:
                    need(put(trial, rows[a]), "inserted target raises rank")
                need(not reduce(rows[a], trial), "inserted target becomes member")
                need(not h or not reduce(h[min(h)], h), "existing history member")
                past_controls += 1
                answers[i] = {
                    "event": i, "owner": a, "source": old, "destination": new,
                    "rank": abs(len(word["frames"][old]) - len(word["frames"][new])),
                    "target": rows[a].copy(), "earlier_B_hit": not remainder,
                    "earlier_B_rank": len(h),
                }
            if frames[old] in future:
                departures.append((i, frames[old], rows[a].copy()))
            chart[a] = new
            if frames[new] in past:
                put(past[frames[new]], rows[a])
        elif op == "INIT":
            need(a >= public and chart[a] is None and rows[a] is None, "owned INIT")
            chart[a], rows[a] = e[2], {}
        elif op == "CLEAR":
            need(a >= public and chart[a] == e[2], "owned CLEAR")
            if frames[e[2]] in future:
                departures.append((i, frames[e[2]], rows[a].copy()))
            chart[a], rows[a] = None, None
        elif op == "SCALE":
            need(chart[a] == e[-1], "scalar chart")
            q = Q(e[2])
            need(q, "nonzero scale")
            rows[a] = {k: q * v for k, v in rows[a].items()}
        elif op in ("ADD", "COPY"):
            b = e[2]
            need(a != b and chart[a] == chart[b] == e[-1], "coframed contact")
            if op == "COPY":
                need(a >= public and not rows[a], "fresh zero COPY")
            add(rows[a], rows[b], Q(e[3]))
        else:
            raise ValueError(op)
    need(chart == word["final"] + [None] * word["owned_fields"], "all endpoints")
    for a, f in enumerate(word["final"]):
        if frames[f] in future:
            put(future[frames[f]], rows[a])
    # Strictly later: never insert a candidate's own outgoing row before its query.
    departures.sort(key=lambda z: z[0], reverse=True)
    j = 0
    future_controls = 0
    for i in sorted(cuts, reverse=True):
        while j < len(departures) and departures[j][0] > i:
            _, f, row = departures[j]
            put(future[f], row)
            j += 1
        h = future[frames[cuts[i][2]]]
        rec = answers[i]
        rec["later_A_hit"] = not reduce(rec["target"], h)
        rec["later_A_rank"] = len(h)
        future_controls += int(rec["later_A_hit"])
        rec["target"] = {str(k): str(v) for k, v in sorted(rec["target"].items())}

    need(author is not None, "fresh author temporal replay supplied")
    old = author
    need(old["source_sha256"] == PIN, "author source pin")
    for r in old["records"]:
        got = answers[r["event"]]
        for name in ("owner", "source", "destination", "rank", "earlier_B_hit",
                     "earlier_B_rank", "later_A_hit", "later_A_rank"):
            need(got[name] == r[name], "independent temporal comparison " + name)
        need(got["target"] == r["target_row"], "independent complete target row")
    need(kernel is not None and kernel["source_sha256"] == PIN, "fresh source census supplied")
    for r in kernel["records"]:
        if r["owned"]:
            # A live source witness remains available immediately after the MOVE.
            need(answers[r["event"]]["later_A_hit"] == r["source"]["inside"],
                 "later source hits exactly the 31 live-source controls")
    need(not any(r["earlier_B_hit"] for r in answers.values()), "all earlier B misses")
    need(future_controls == 31, "31 genuine later-source positive controls")
    out = {
        "status": "INDEPENDENT_EXACT_ALL_47_OWNED_TEMPORAL_FILTERS",
        "source_sha256": PIN, "instructions": len(events), "owned_MOVEs": len(cuts),
        "earlier_hits": sum(r["earlier_B_hit"] for r in answers.values()),
        "later_hits": future_controls, "independent_author_cases": len(old["records"]),
        "inserted_arrival_controls": past_controls, "past_subspaces": len(past),
        "future_subspaces": len(future), "event_counts": dict(counts),
        "seconds": time.monotonic()-start, "records": list(answers.values()),
        "scope": "Unchanged native history, arbitrary public inputs, coframed ordinary caches. No physical supplier or kappa claim.",
    }
    print(json.dumps({k:v for k,v in out.items() if k!="records"}, indent=2))
    return out


# Called read-only by verify.py with fresh author and source-census results.
