#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Clocked e252 ingress and preservation checks on the pinned #7830 word."""
from functools import cache
from hashlib import sha256
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
import importlib.util
sys.path.insert(0, str(HERE))
import literal

spec = importlib.util.spec_from_file_location("old_receiver", HERE / "old_receiver.py")
native = importlib.util.module_from_spec(spec)
spec.loader.exec_module(native)
native.INPUTS = HERE.parent / "inputs"
extract_forward = native.extract_forward
make_basis = native.make_basis
quotient = native.quotient
support = native.support
prior_file = HERE.parent / "receipts/two-banks.json"
for path, digest in {
    HERE / "old_receiver.py": "c9db4b7720b70cc1a35913fb8e75c2797b366c6cf23af0676b48b0bb50b5d918",
    prior_file: "57230b4ef81a2a2f65e6c29bf0178cbe489f06315b671083fe2c85e56af4a664",
    native.INPUTS / "WORD.json.gz": "d28f0d28d9d87d5fe57b8ef19e12faf98014f0bbef781987ce22daaa82f21cb9",
    HERE / "literal.py": "4021766d87fa791a43a78a6665c9260b7ba3772d8b2db6e9c84b6a3d51a1305c",
}.items():
    if sha256(path.read_bytes()).hexdigest() != digest:
        raise ValueError("Source digest changed: " + path.name)
word = native.load("WORD.json.gz")
prior = json.loads(prior_file.read_bytes())
assert literal.canonical(word) == prior["source"]["word"]
assert literal.canonical({k: word[k] for k in ("frames", "start", "final")}) == prior["source"]["layout"]
assert word["public"] == 680 and word["start"][252] == 0 and word["final"][252] == 1
_, routes, stock, readers = extract_forward(word)
chart = literal.Charts(word["frames"])
BIT = 252
HELD = {740, 753}
PROTECTED = HELD | {3553}
rows = {i: row for bank in readers.values() for i, (row, _) in bank.items() if i >= 0}

def clock(i):
    return routes[i][2] if i in routes else len(word["program"])

@cache
def early(bank, t):
    return {i: row for i, row in stock.get(bank, {}).items() if i not in routes or clock(i) < t}

def marked(row):
    return (row >> BIT) & 1

def source(bank, t):
    return [i for i, row in early(bank, t).items() if marked(row)]

@cache
def grade(a, b):
    try:
        return chart.leg(a, b)
    except ValueError:
        return None

def packet(i):
    a, b, t = routes[i]
    return {"slot": i, "source": a, "receiver": b, "clock": t, "grade": grade(a, b),
            "input": support(rows[i]), "local": support(readers[a][i][1])}

def residual(bank, read, withdrawn, t=None):
    refs = make_basis(row for i, row in early(bank, clock(read) if t is None else t).items()
                      if i not in withdrawn)
    return quotient(refs, readers[bank][read][0])

def old_reader(bank, withdrawn, except_for=()):
    for read, (row, _) in readers[bank].items():
        if read in except_for:
            continue
        q = residual(bank, read, withdrawn)
        if q:
            return {"role": ~read if read < 0 else read, "terminal": read < 0,
                    "clock": clock(read), "input": support(row), "residual": support(q)}

def list_retargets(dest, before):
    candidates = []
    for i, (a, b, t) in routes.items():
        if t >= before:
            break
        if i not in PROTECTED and b != dest and grade(a, dest) == grade(a, b) and source(a, t):
            witness = old_reader(b, {i})
            assert witness, (dest, i)
            candidates.append({"old": packet(i), "source_e252": source(a, t), "old_witness": witness})
    return candidates

layered = []
for read, live, count in [(1366, [752, 1363], 15), (2292, [1362, 2291], 3),
                          (1758, [1755], 112), (1890, [1887], 145)]:
    producer, _, before = routes[read]
    candidates = []
    for i, row in early(producer, before).items():
        assert not marked(row)
        if i not in routes:
            continue
        src = source(routes[i][0], clock(i))
        witness = old_reader(producer, {i}, {read})
        if src:
            assert witness and not marked(sum(1 << j for j in witness["input"]))
            assert not any(marked(row) for row in early(producer, witness["clock"]).values())
        candidates.append({"arrival": packet(i), "source_e252": src, "old_witness": witness})
    assert [x["arrival"]["slot"] for x in candidates if x["source_e252"]] == live
    retargets = list_retargets(producer, before)
    assert len(retargets) == count
    layered.append({"crossing": packet(read), "producer_initial_axes": [
        i for i in stock[producer] if i not in routes], "existing_arrivals": candidates,
        "same_grade_destination_retargets": retargets})

for producer, pair, demands in [(127, {752, 1363}, (1364, 1365)), (507, {1362, 2291}, (2293, 2300))]:
    before = max(map(clock, demands))
    residuals = [residual(producer, d, pair, before) for d in demands]
    assert len(make_basis(residuals)) == 2 and not any(map(marked, residuals))
    assert not any(marked(row) for row in early(producer, before).values())
    next(x for x in layered if x["crossing"]["source"] == producer)["joint"] = {
        "changed_arrivals": sorted(pair), "protected_reads": [packet(d) for d in demands],
        "old_quotient_basis_supports": [support(q) for q in residuals],
        "old_rank": 2, "required_rank_with_e252": 3,
    }

cuts = []
for case in prior["cut"]["cases"]:
    region = set(case["banks"])
    peer, = region - {266}
    crossings = [i for i, (a, b, _) in routes.items() if a not in region and b in region and i not in HELD]
    assert set(crossings) == {x["label"] for x in case["outside_edges_into_cut"]}
    exits = [i for i in readers[266] if routes[i][1] not in region]
    marked_exits = [i for i in exits if marked(rows[i])]
    first, last = min(map(clock, marked_exits)), max(map(clock, marked_exits))
    assert not any(early(b, 0) for b in region)
    rejected = []
    for i in crossings:
        a, b, t = routes[i]
        assert not marked(rows[i])
        if b == 266:
            basis = make_basis([rows[740]] + [rows[j] for j in crossings if j != i and clock(j) < last])
            assert len(make_basis(quotient(basis, rows[j]) for j in exits)) == 2
            reason = "two independent protected exterior directions for one edited crossing"
        elif t >= first:
            assert t > last
            reason = "original arrival later than every protected e252 exterior read"
        else:
            assert i in {1758, 1890}
            record = next(x for x in layered if x["crossing"]["slot"] == i)
            assert all(x["old_witness"] and x["old_witness"]["clock"] < t
                       for x in record["existing_arrivals"])
            reason = "every prior arrival is necessary for an unmodified earlier old read"
        rejected.append(packet(i) | {"reason": reason})
    cuts.append({"peer": peer, "protected_exits": [packet(i) for i in exits],
                 "first_e252_exit": first, "last_e252_exit": last, "crossings": rejected})

price = prior["invoice"]
print(json.dumps({"status": "excluded_at_original_clocks_with_protected_readers",
                  "goal": prior["goal"], "step": "s15-binary-early-source", "source": prior["source"],
                  "public_axis": {"index": 252, "start_chart": 0, "final_chart": 1},
                  "layered_ingress": layered, "five_peer_cut": cuts,
                  "invoice_from_pinned_s11_full_replay": {k: price[k] for k in (
                      "trial", "native_calls", "baseline", "hypothetical_fixed_grade_recode",
                      "hypothetical_one_extra_grade_one_per_call", "directed_credit")}}, sort_keys=True,
                 indent=2))
