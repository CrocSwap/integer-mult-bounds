#!/usr/bin/env python3
"""Selected BIT alternate-carrier cuts; immutable bundled source.

Unlike PR7304, the target group has no original public pivot in this bank.
Apache-2.0; OpenAI assistance.
"""
from collections import Counter, defaultdict
from fractions import Fraction as F
from pathlib import Path
import gzip
import hashlib
import json

INPUT = Path(__file__).with_name("inputs") / "BIT-NATIVE-WORD.json.gz"
PIN = "e54523517d0f03e58352e647c403a5af3e525a57"
SOURCE = "research/paired-query-only-bit/retained/inputs/BIT-NATIVE-WORD.json.gz"
SHA = "51203e7fc75ba10bd3ac3f8e675759f47e13d262bea66b6600d1e515095cad78"

def need(test, message):
    if not test:
        raise ValueError(message)

def source():
    raw = INPUT.read_bytes()
    need(hashlib.sha256(raw).hexdigest() == SHA, "selected native bytes")
    return json.loads(gzip.decompress(raw))

def kernel(vectors, exterior):
    basis, out = {}, []
    for i, vector in enumerate(vectors):
        value, witness = vector & exterior, 1 << i
        while value:
            p = value.bit_length() - 1
            if p not in basis:
                basis[p] = value, witness
                break
            old, mask = basis[p]
            value ^= old
            witness ^= mask
        if not value:
            out.append(witness)
    return out

def combine(values, mask):
    out = 0
    while mask:
        bit = mask & -mask
        out ^= values[bit.bit_length() - 1]
        mask ^= bit
    return out

def parity(value):
    return value.bit_count() & 1

def witness(prefix, suffix, group, width):
    exterior = ((1 << width) - 1) ^ group
    left, right = kernel(prefix, exterior), kernel(suffix, exterior)
    if not left or not right:
        return None, (len(left), len(right), 0, 0)
    clean_left = [combine(prefix, a) for a in left]
    clean_right = [combine(suffix, b) for b in right]
    first = second = None
    for i, a in enumerate(left):
        if first is None and any(parity(a & b) for b in right):
            first = i
        if second is None and any(parity(clean_left[i] & d) for d in clean_right):
            second = i
    ranks = (len(left), len(right), int(first is not None), int(second is not None))
    if first is None or second is None:
        return None, ranks
    for a in (left[first], left[second], left[first] ^ left[second]):
        c = combine(prefix, a)
        b1 = next((b for b in right if parity(a & b)), None)
        b2 = next((b for b, d in zip(right, clean_right) if parity(c & d)), None)
        if b1 is None or b2 is None:
            continue
        for b in (b1, b2, b1 ^ b2):
            d = combine(suffix, b)
            if parity(a & b) == parity(c & d) == 1:
                need(not ((c | d) & exterior), "paired exterior support")
                return dict(a=a, b=b, c=c, d=d), ranks
    raise ValueError("two-linear-map witness construction")

def controls():
    positive, _ = witness([1, 2], [1, 2], 3, 2)
    need(positive is not None, "positive clean mode")
    summed, _ = witness([1, 2], [2, 1], 3, 2)
    need(summed is not None and summed["b"].bit_count() == 2,
         "a sum of kernel witnesses can be necessary")
    for label, prefix, suffix, group, width in (
            ("dirty_prefix", [5], [1], 1, 3),
            ("dirty_suffix", [1], [5], 1, 3),
            ("local_pair_only", [1], [2], 3, 2)):
        found, _ = witness(prefix, suffix, group, width)
        need(found is None, label + " must reject")
    return dict(clean_mode_passes=True, summed_mode_passes=True,
                dirty_prefix_rejected=True, dirty_suffix_rejected=True,
                local_pair_without_endpoint_pair_rejected=True)

def run():
    tested_controls = controls()
    w = source()
    n, size = w["public"], w["public"] + w["owned_fields"]
    frames = {int(k): v for k, v in w["frames"].items()}
    grouped = defaultdict(list)
    for i in range(222, n):
        grouped[w["start"][i], w["final"][i]].append(i)
    groups = list(grouped.items())
    def included(a, b):
        return all(sum(F(x) * F(y) for x, y in zip(v, z)) == 0
                   for v in frames[a]["B"] for z in frames[b]["A"])
    eligible = defaultdict(list)
    for C in frames:
        for g, ((A, B), roles) in enumerate(groups):
            if frames[A]["dim"] < frames[C]["dim"] < frames[B]["dim"]:
                if included(A, C) and included(C, B):
                    eligible[C].append(g)
    group_masks = [sum(1 << i for i in roles) for _, roles in groups]
    group_sets = [set(roles) for _, roles in groups]
    where = w["start"] + [None] * (size - n)
    rows = [1 << i for i in range(n)] + [0] * (size - n)
    banks = defaultdict(set)
    for i, C in enumerate(where):
        if C is not None:
            banks[C].add(i)
    snapshots, contexts = {}, Counter()
    def observe(event, charts):
        states = []
        for C in sorted(charts & eligible.keys()):
            bank = sorted(banks[C])
            if not bank:
                continue
            gs = [g for g in eligible[C] if not (banks[C] & group_sets[g])]
            if gs:
                states.append((C, bank, [rows[i] for i in bank], gs))
                contexts["banks"] += 1
                contexts["bank_groups"] += len(gs)
        if states:
            snapshots[event] = states
    observe(-1, set(banks))
    for event, e in enumerate(w["program"]):
        op, a = e[:2]
        charts = {where[a]} if where[a] is not None else set()
        if op == "INIT":
            where[a], rows[a] = e[2], 0
            banks[e[2]].add(a)
            charts.add(e[2])
        elif op == "CLEAR":
            banks[where[a]].remove(a)
            where[a], rows[a] = None, 0
        elif op == "ADD":
            need(where[a] == where[e[2]] == e[3], "cocharted source ADD")
            rows[a] ^= rows[e[2]]
        elif op == "SWAP":
            b = e[2]
            charts.add(where[b])
            banks[where[a]].remove(a)
            banks[where[b]].remove(b)
            where[a], where[b] = where[b], where[a]
            rows[a], rows[b] = rows[b], rows[a]
            banks[where[a]].add(a)
            banks[where[b]].add(b)
        elif op == "MOVE":
            need(where[a] == e[2], "source MOVE entrance")
            banks[e[2]].remove(a)
            banks[e[3]].add(a)
            where[a] = e[3]
            charts.add(e[3])
        else:
            raise ValueError(op)
        observe(event, charts)
    need(where == w["final"] + [None] * (size - n), "original endpoints")
    for i, row in enumerate(rows[:n]):
        expected = (1 << i) ^ ((1 << (i - 111)) if 111 <= i < 222 else 0)
        need(row == expected, "original arbitrary-input map")
    columns = [1 << i for i in range(n)] + [0] * (size - n)
    ranks, survivors = Counter(), []
    for event in range(len(w["program"]) - 1, -2, -1):
        for C, bank, prefix, gs in snapshots.get(event, []):
            suffix = [columns[i] for i in bank]
            for g in gs:
                pair, dimensions = witness(prefix, suffix, group_masks[g], n)
                ranks[dimensions] += 1
                if pair is not None:
                    A, B = groups[g][0]
                    survivors.append(dict(event=event, chart=C, bank=bank,
                                          boundary_group=list(groups[g][0]),
                                          group_roles=groups[g][1],
                                          rank_split=[frames[C]["dim"]-frames[A]["dim"],
                                                      frames[B]["dim"]-frames[C]["dim"]],
                                          dimensions=list(dimensions), **pair))
        if event >= 0:
            e = w["program"][event]
            op, a = e[:2]
            if op in ("INIT", "CLEAR"):
                columns[a] = 0
            elif op == "ADD":
                columns[e[2]] ^= columns[a]
            elif op == "SWAP":
                columns[a], columns[e[2]] = columns[e[2]], columns[a]
    result = dict(status="ALTERNATIVE_CARRIER_PAIRED_SUPPORT_SCREEN", pin=PIN,
                  native_sha256=SHA,
                  groups=[dict(boundary=list(pair), count=len(roles)) for pair, roles in groups],
                  contexts=dict(contexts),
                  kernel_pairing_histogram={str(k): v for k, v in ranks.items()},
                  survivors=survivors,
                  controls=tested_controls,
                  scope="No original public pivot of target group in bank; unchanged paid word; alternate owned/other-group carriers; no theorem or kappa from a screen.")
    return result

if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
