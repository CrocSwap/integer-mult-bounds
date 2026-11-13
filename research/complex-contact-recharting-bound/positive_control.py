#!/usr/bin/env python3
"""A source-bound nonzero control, already incorporated in the latest word."""
from collections import Counter
from pathlib import Path
import gzip
import hashlib
import json
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import core as R

raw = (HERE / "inputs/canonical-selected-WORD.json.gz").read_bytes()
R.need(hashlib.sha256(raw).hexdigest() == "2b94953dc14a122e3ef089633f05b58ec689ec5156feb7c784ed3e137dc01883", "canonical positive source pin")
word = json.loads(gzip.decompress(raw))
visits, groups = R.visit_components(word)
vertex = {v["id"]: j for j, group in enumerate(groups) for v in group}
ent = {v["entrance"]: vertex[v["id"]] for v in visits if v["entrance"] is not None}
ext = {v["exit"]: vertex[v["id"]] for v in visits if v["exit"] is not None}
chart = [R.span(word["frames"][g[0]["chart"]]) for g in groups]
selected = [j for j, group in enumerate(groups) if {v["owner"] for v in group} == {47, 158, 923} and R.dim(chart[j]) == 4]
R.need(len(selected) == 1, "known complete visit component")
new = chart.copy()
new[selected[0]] = R.span([268, 139, 76, 45, 28])
moves = [(ext[i], ent[i], e[4]) for i, e in enumerate(word["program"]) if e[0] == "MOVE"]
R.need(all(R.comparable(new[a], new[b]) if owned else new[a] & new[b] == new[a] for a, b, owned in moves), "known recharting legal")
before = Counter(abs(R.dim(chart[a]) - R.dim(chart[b])) for a, b, _ in moves)
after = Counter(abs(R.dim(new[a]) - R.dim(new[b])) for a, b, _ in moves)
delta = {r: after[r] - before[r] for r in after.keys() | before.keys() if after[r] != before[r]}
R.need(delta == {1: 1, 2: -2, 3: 1}, "positive control full paid change")
R.need(-sum(c * min(r, 2) for r, c in delta.items()) == 1, "nonzero concave saving detected")
print("PASS_SOURCE_BOUND_POSITIVE_CONTROL", delta, "min(r,2) saving=1; pre-incorporated, not novel")
