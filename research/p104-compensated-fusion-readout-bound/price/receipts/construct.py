# SPDX-License-Identifier: Apache-2.0
"""Fuse helper 319's two paid lifts through a coframed scalar block."""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
import gzip
from hashlib import sha256
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
SOURCE = "0358b9f6e0340fb3e5aa46c747c558b32a5280cbf9cd92c3b9de627dd18a9a4f"
BLOCK = (40222, 40840, 42609, 43022, 43023, 43024, 43025, 43026, 43028,
         43030, 43403, 43491, 43535, 43696, 43698, 43887, 45365, 45396)
R, PEER, READOUT = 319, 1081, 1467
LOW, MIDDLE, HIGH = 1089, 207, 127
CLOCK = 44616
AUX = 1567


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(word):
    return json.dumps(word, sort_keys=True, separators=(",", ":")).encode()


def roles(e):
    return e[1:3] if e[0] in ("ADD", "COPY") else e[1:2]


def span(basis):
    s = {0}
    for x in basis:
        s |= {x ^ y for y in s}
    return s


def local_certificate(word):
    need(sha256(canonical(word)).hexdigest() == SOURCE, "Exact #7314 word")
    p, n = word["program"], word["public"]
    scope = set(BLOCK)
    touched = sorted({r for t in BLOCK for r in roles(p[t])})
    need(all(p[t][0] in ("ADD", "SCALE") and p[t][-1] == MIDDLE for t in BLOCK)
         and max(touched) < n, "One coframed public scalar block")
    bounds = {}
    for r in touched:
        contacts = [t for t, e in enumerate(p) if e[0] != "MOVE" and r in roles(e)]
        body = [t for t in BLOCK if r in roles(p[t])]
        first, last = body[0], body[-1]
        need([t for t in contacts if first <= t <= last] == body,
             "No intervening contact on a moved participant")
        bounds[r] = (max((t for t in contacts if t < first), default=-1) + 1,
                     min((t for t in contacts if t > last), default=len(p)))
    lo, hi = max(x[0] for x in bounds.values()), min(x[1] for x in bounds.values())
    need((lo, hi) == (CLOCK, 45718), "Joint legal block clock")
    need(p[43029] == ["MOVE", R, LOW, MIDDLE, False] and
         p[46308] == ["MOVE", R, MIDDLE, HIGH, False], "Both replaced paid lifts")
    f = {r: Q(0) for r in touched}
    f[R], f[PEER] = Q(1), Q(-1)
    for t in BLOCK:
        e = p[t]
        if e[0] == "ADD":
            f[e[1]] += Q(e[3]) * f[e[2]]
        else:
            f[e[1]] *= Q(e[2])
    b = {r: Q(0) for r in touched}
    b[R] = b[READOUT] = Q(1)
    for t in reversed(BLOCK):
        e = p[t]
        if e[0] == "ADD":
            b[e[2]] += Q(e[3]) * b[e[1]]
        else:
            b[e[1]] *= Q(e[2])
    need({r: v for r, v in f.items() if v} == {PEER: -1, READOUT: 1},
         "Exact forward image of bypass direction")
    need({r: v for r, v in b.items() if v} == {R: 1}, "Exact dirty-output readout")
    return {"coframe": MIDDLE, "block": list(BLOCK), "roles": touched,
            "clock_range": [lo, hi], "forward": {str(PEER): "-1", str(READOUT): "1"},
            "adjoint": {str(R): "1"}}


def construct(word):
    cert = local_certificate(word)
    touched = set(cert["roles"])
    p, n = word["program"], word["public"]
    out = deepcopy(word)
    aux = AUX
    need(n <= aux < n + out["owned_fields"], "Reuse a declared owned label")
    active = word["initial"] + [None] * out["owned_fields"]
    spaces = list(map(span, word["frames"]))
    ranks = list(map(len, word["frames"]))
    tape = []

    def append(e):
        op, r = e[:2]
        if op == "MOVE":
            a, b, owned = e[2:]
            need(active[r] == a and owned == (r >= n) and
                 (spaces[a] < spaces[b] or owned and spaces[b] < spaces[a]), "Legal literal MOVE")
            active[r] = b
        elif op == "INIT":
            need(r >= n and active[r] is None, "Clean owned lifetime start")
            active[r] = e[2]
        elif op == "CLEAR":
            need(r >= n and active[r] == e[2], "Owned lifetime ends in its chart")
            active[r] = None
        else:
            for q in roles(e):
                f = e[-1]
                if q in touched and active[q] != f:
                    append(["MOVE", q, active[q], f, False])
                need(active[q] == f, "Literal coframe")
        tape.append(e)

    skipped = set(BLOCK)
    for t, e in enumerate(p):
        if t == CLOCK:
            append(["ADD", PEER, R, "1", LOW])
            append(["INIT", aux, MIDDLE])
            for q in BLOCK:
                event = p[q].copy()
                for i in (1, 2) if event[0] == "ADD" else (1,):
                    if event[i] == R:
                        event[i] = aux
                append(event)
            append(["CLEAR", aux, MIDDLE])
            append(["ADD", PEER, R, "-1", HIGH])
            append(["ADD", READOUT, R, "1", HIGH])
            append(["ADD", R, READOUT, "-1", HIGH])
        if t in skipped or e[0] == "MOVE" and e[1] in touched:
            continue
        append(e)
    for r in touched:
        if active[r] != word["final"][r]:
            append(["MOVE", r, active[r], word["final"][r], False])
    need(active == word["final"] + [None] * out["owned_fields"], "All output charts and erasures")
    need(["MOVE", R, LOW, HIGH, False] in tape, "Direct rank-six lift")

    def paid(events):
        return Counter(abs(ranks[e[2]] - ranks[e[3]]) for e in events if e[0] == "MOVE")

    delta = paid(tape)
    delta.subtract(paid(p))
    need({r: v for r, v in delta.items() if v} == {1: -1, 5: -1, 6: 1},
         "Complete paid histogram delta")
    out["program"] = tape
    return out


if __name__ == "__main__":
    word = json.loads(gzip.decompress(Path(sys.argv[1]).read_bytes()))
    out = construct(word)
    Path(sys.argv[2]).write_bytes(gzip.compress(canonical(out), compresslevel=6, mtime=0))
