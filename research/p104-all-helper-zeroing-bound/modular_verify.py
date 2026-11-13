#!/usr/bin/env python3
"""Independent modular obstruction to helper-zeroing gains on exact #7481.

Nonzero residues prove nonzero rational coefficients. This checker needs no
floating point optimization, exact rational row census, or author flow code.
"""
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path
import gzip
import hashlib
import json

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "inputs/WORD.json.gz"
ASSIGNMENT = ROOT / "ASSIGNMENT.json"
SOURCE_SHA = "acee323696b18914bd863d55341f92112b48d3d1dc1443c276efb6c396fcc0a9"
PRIME = 65521


def need(ok, why):
    if not ok:
        raise ValueError(why)


def scalar(q):
    q = Fraction(q)
    need(q.denominator % PRIME != 0, "source denominator invertible modulo prime")
    return q.numerator * pow(q.denominator, -1, PRIME) % PRIME


def rank(vectors):
    pivots = {}
    for x in vectors:
        need(type(x) is int and 0 <= x < 512, "binary frame vector")
        while x:
            k = x.bit_length()
            if k not in pivots:
                pivots[k] = x
                break
            x ^= pivots[k]
    return len(pivots)


def validate_funding(word, records, helpers):
    assigned, charges = {}, defaultdict(list)
    target = {h: abs(len(word["frames"][word["initial"][h]])
                     - len(word["frames"][word["final"][h]])) for h in helpers}
    for a in records:
        event, h, r = a["event"], a["assigned_helper"], a["rank"]
        need(event not in assigned, "no duplicated funded MOVE")
        need(0 <= event < len(word["program"]), "funded event in source")
        e = word["program"][event]
        need(e[0] == "MOVE", "funded event is MOVE")
        need(r == abs(len(word["frames"][e[2]]) - len(word["frames"][e[3]])),
             "funded paid rank equals source")
        need(h in helpers and target[h] == a["target_rank"], "funded helper target equals source")
        assigned[event] = h
        charges[h].append(r)
    for h, rs in charges.items():
        need((len(rs) == 1 and rs[0] <= target[h])
             or (sorted(rs) == [1, 1] and target[h] >= 4),
             "helper covers its complete assigned price for 1/2<=t<=1")
    return assigned, charges


def check(word, records, projected=None):
    need(all(PRIME % d for d in range(2, 257)), "prime modulus")
    n = word["public"]
    mains = set(word["live"]) | {i + 112 for i in word["live"]}
    mains |= set(word["hosted"]["X2"]) | set(word["hosted"]["Y2"])
    helpers = set(range(n)) - mains
    need(n == 1501 and len(mains) == 400 and len(helpers) == 1101, "source partition")
    for v in word["frames"]:
        need(rank(v) == len(v), "all source frame dimensions exact")
    assigned, charges = validate_funding(word, records, helpers)
    boundary_groups = defaultdict(set)
    for h in helpers:
        boundary_groups[word["initial"][h], word["final"][h]].add(h)
    rows = [{i: 1} if i < n else {} for i in range(n + word["owned_fields"])]
    where = word["initial"][:] + [None] * word["owned_fields"]
    paid, checked, witnesses = Counter(), Counter(), []
    for event, e in enumerate(word["program"]):
        op, a = e[:2]
        if op == "MOVE":
            need(where[a] == e[2], "literal source chart")
            r = abs(len(word["frames"][e[2]]) - len(word["frames"][e[3]]))
            paid[r] += 1
            if event in assigned:
                h = assigned[event]
                need(rows[a].get(h, 0) != 0, "assigned helper has nonzero exact coefficient")
                witnesses.append([event, h, rows[a][h]])
                checked["funded"] += 1
                if projected is not None:
                    group = (word["initial"][h], word["final"][h])
                    projected[event] = {
                        "group": group, "rank": r,
                        "target_rank": abs(len(word["frames"][group[1]])
                                           - len(word["frames"][group[0]])),
                        "row": {j: v for j, v in rows[a].items()
                                if j in boundary_groups[group]},
                    }
            else:
                h = next((h for h in rows[a] if h in mains), None)
                need(h is not None, "every unfunded MOVE has a nonzero main coefficient")
                witnesses.append([event, h, rows[a][h]])
                checked["main_obstructed"] += 1
            where[a] = e[3]
        elif op == "INIT":
            need(where[a] is None, "fresh INIT")
            rows[a], where[a] = {}, e[2]
        elif op == "CLEAR":
            need(where[a] == e[2], "source CLEAR chart")
            rows[a], where[a] = {}, None
        elif op == "SCALE":
            need(where[a] == e[-1], "coframed SCALE")
            q = scalar(e[2])
            rows[a] = {h: v * q % PRIME for h, v in rows[a].items() if v * q % PRIME}
        elif op in ("ADD", "COPY"):
            b, q = e[2], scalar(e[3])
            need(a != b and where[a] == where[b] == e[-1], "coframed distinct scalar contact")
            if op == "COPY":
                need(not rows[a], "COPY destination is zero modulo prime")
                rows[a] = {}
            for h, v in rows[b].items():
                c = (rows[a].get(h, 0) + q * v) % PRIME
                if c:
                    rows[a][h] = c
                else:
                    rows[a].pop(h, None)
        else:
            raise ValueError("unknown opcode " + op)
    need(where == word["final"] + [None] * word["owned_fields"], "all source endpoints")
    need(sum(paid.values()) == 6279 and checked == {"funded": 468, "main_obstructed": 5811},
         "every original MOVE covered")
    need(all(rows[h] == {h: 1} for h in helpers), "source helper endpoints modulo prime")
    return {"status": "PASS_INDEPENDENT_MODULAR_COLD_SUBSET_CERTIFICATE",
            "modulus": PRIME, "source_sha256": SOURCE_SHA,
            "events": len(word["program"]), "move_coverage": dict(checked),
            "paid_histogram": dict(sorted(paid.items())),
            "charged_helpers": len(charges),
            "repeated_charges": {str(h): rs for h, rs in charges.items() if len(rs) > 1},
            "nonzero_witnesses_sha256": hashlib.sha256(json.dumps(witnesses).encode()).hexdigest(),
            "universal_kappa_interval": "0<=kappa<=1/2",
            "scope": "Fixed source operations; only zero original helper inputs and omit MOVEs whose entire latent value becomes identically zero. No new kappa."}


def run(projected=None):
    raw = SOURCE.read_bytes()
    need(hashlib.sha256(raw).hexdigest() == SOURCE_SHA, "exact source bytes")
    return check(json.loads(gzip.decompress(raw)), json.loads(ASSIGNMENT.read_text()), projected)


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
