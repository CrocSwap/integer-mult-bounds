#!/usr/bin/env python3
"""Compare independent generic, binary and ternary censuses to the declared classification."""
from collections import Counter
from dataclasses import astuple
from hashlib import sha256
import json
from pathlib import Path
import sys

PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0,str(PACKAGE))
from binary_oracle import enumerate_pairs
from construction_check import labeled_codes, need
from matching_oracle import census as generic_census
from signatures import TYPES, Profile, multiplicity, profiles, verdict
from ternary_oracle import census as ternary_census


def counts(key, n):
    symbols = [(key >> (4*j)) & 15 for j in range(n)]
    need(all(s in TYPES for s in symbols), "oracle reported a forbidden mask")
    return tuple(symbols.count(s) for s in TYPES)


def digest(codes, n):
    return sha256(b"".join(x.to_bytes((n+1)//2,"little") for x in sorted(codes))).hexdigest()


def full_gl4():
    tally = Counter()
    for pattern in range(1<<16):
        source = [(pattern >> (4*i)) & 15 for i in range(4)]
        rows = [x | (16 << i) for i,x in enumerate(source)]
        for j in range(4):
            pivot = next((i for i in range(j,4) if rows[i] & (1<<j)), None)
            if pivot is None:
                break
            rows[j],rows[pivot] = rows[pivot],rows[j]
            for i in range(4):
                if i != j and rows[i] & (1<<j):
                    rows[i] ^= rows[j]
        else:
            key = 0
            for j in range(4):
                bit = 1 << j
                s = int(bool((source[0]|source[1]) & bit)) + 2*int(bool((source[2]|source[3]) & bit))
                inverse_row = rows[j] >> 4
                r = int(bool(inverse_row & 3)) + 2*int(bool(inverse_row & 12))
                key += (4*s+r) << (4*j)
            tally[key] += 1
    return tally


def binary_grids():
    grids, six = {}, {}
    for n in range(2,7):
        for p in range(1,n):
            q = n-p
            left, right, tally = enumerate_pairs(n,p)
            need(set(tally) == labeled_codes(p,q,True), "binary space census disagrees")
            need(sum(tally.values()) == left*(1 << (p*q)), "binary complement count")
            grids[f"{p}+{q}"] = dict(first_spaces=left, second_spaces=right, pairs=sum(tally.values()),
                                     codes=len(tally), code_sha256=digest(tally,n))
            if p == q == 2:
                full = full_gl4()
                need({k:36*v for k,v in tally.items()} == full, "full binary GL4 multiplicities")
            if p == q == 3:
                for key, amount in tally.items():
                    row = counts(key,n)
                    if row in six:
                        need(six[row] == amount, "unequal binary counts under relabeling")
                    six[row] = amount  # ordered space pairs per labeled signature
    return grids, six


def generic_grids():
    out = {}
    for p,q,chart in [(2,2,False),(1,5,True),(2,4,True),(3,3,True)]:
        meta, raw = generic_census(p,q,chart)
        expected = {astuple(v) for v in profiles(p+q) if verdict(p,q,v) == "ok"}
        classes = {counts(key,p+q) for key in raw}
        need(classes == expected, "generic perfect-matching profiles disagree")
        need(sum(raw.values()) == meta["nonsingular"], "generic support multiplicities")
        if not chart:
            need(set(raw) == labeled_codes(p,q), "full four-port support patterns")
        out[f"{p}+{q}"] = dict(**meta, chart=chart, fixed_order_codes=len(raw),
                                classes=len(classes), labeled_codes=sum(multiplicity(Profile(*k).symbols()) for k in classes))
    return out


def build_census():
    binary, pair2 = binary_grids()
    ternary = {}
    pair3 = {}
    for d in (2,3):
        summary, grouped = ternary_census(2*d,d)
        expected = {astuple(v) for v in profiles(2*d) if verdict(d,d,v) == "ok"}
        need(set(grouped) == expected, "ternary projective census disagrees")
        ternary[f"{d}+{d}"] = dict(**summary, classes=len(grouped))
        for key, total in grouped.items():
            per_label, rem = divmod(total,multiplicity(Profile(*key).symbols()))
            need(rem == 0 and per_label > 0, "ternary orbit multiplicity")
            if d == 3:
                pair3[key] = per_label
    pairs = {k:(pair2.get(k,0),v) for k,v in pair3.items()}
    report = {"binary":binary, "generic":generic_grids(), "ternary":ternary,
              "literal_GL4_F2":20160, "all_mixed_six_port_pairs":list(pairs[(0,0,0,0,0,0,6)])}
    return report, pairs


def main():
    report, pairs = build_census()
    expected = json.loads((PACKAGE/"RESULT.json").read_bytes())["censuses"]
    need(json.loads(json.dumps(report)) == expected, "stored census summary differs")
    rows = json.loads((PACKAGE/"SIX-PORTS.json").read_bytes())
    observed = {tuple(r["counts"]):tuple(r["pairs_per_label_F2_F3"]) for r in rows}
    need(len(rows) == len(observed) and pairs == observed, "stored per-label multiplicity differs")
    print(json.dumps({"status":"PASS_TWO_BLOCK_INDEPENDENT_CENSUSES","result":report},sort_keys=True))


if __name__ == "__main__":
    main()
