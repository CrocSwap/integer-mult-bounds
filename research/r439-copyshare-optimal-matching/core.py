"""Literal restored-pair recipe and invoice. Apache-2.0; @CubeJerry with Codex.

The recipe is credited to PR848/1782/1805/2487. No solver is imported here.
"""
from __future__ import annotations

import copy
import gzip
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def load_word():
    return json.loads(gzip.decompress((ROOT / WORD).read_bytes()))


def columns(word):
    """Packed columns used only by nomination, not the dual verifier."""
    v = word["v"]
    col = {}
    for f, d, src in word["D"]:
        need(f == 0 and v <= d < 2*v, "original D shape")
        need(len(src) == len(set(src)), "duplicate original D operand")
        for s in src:
            need(s >= 2*v, "original D helper")
            if s not in word["ret"]:
                col[s] = col.get(s, 0) ^ (1 << (d-v))
    return col


def construct(word, pairs):
    pool = set(columns(word))
    used = set()
    for pair in pairs:
        need(isinstance(pair, list) and len(pair) == 2, "pair format")
        a, b = pair
        need(type(a) is int and type(b) is int, "pair integer")
        need(a != b and a in pool and b in pool, "pair domain")
        need(a not in used and b not in used, "pair overlap")
        used.update(pair)
    result = copy.deepcopy(word)
    pre = [[0, a, [b]] for a, b in pairs]
    body = []
    for f, d, src in word["D"]:
        row = set(src)
        for a, b in pairs:
            if a in row:
                row.symmetric_difference_update({b})
        body.append([f, d, sorted(row)])
    result["D"] = pre + body + list(reversed(pre))
    return result


def instructions(word):
    events = []
    for section in ("D", "A"):
        events.extend(("add", d, s) for _, d, src in word[section] for s in src)
    temp = 2*word["v"] + word["R"]
    for j, helper in enumerate(word["ret"]):
        events.append(("copy", temp, helper))
        events.extend(("add", word["v"]+i, temp)
                      for i, src in enumerate(word["scatter"]) if j in src)
        events.append(("erase", temp, helper))
    for section in ("B", "C"):
        events.extend(("add", d, s) for _, d, src in word[section] for s in src)
    return events


def ordered(events, reverse=False):
    if not reverse:
        return events
    return [({"copy": "erase", "erase": "copy"}.get(op, op), d, s)
            for op, d, s in reversed(events)]


def invoice(word):
    events = instructions(word)
    peaks = []
    n = 2*word["v"] + word["R"]
    for reverse in (False, True):
        values = [1]*n + [0]
        peak = 1
        for op, d, s in ordered(events, reverse):
            values[d] = (values[d]+values[s] if op == "add" else
                         values[s] if op == "copy" else 0)
            peak = max(peak, values[d])
        peaks.append(peak)
    f, b = peaks
    local, nine = 64*f**3*b**2, 2**18*f**5*b**4
    return {"ADDs": sum(op == "add" for op, _, _ in events),
            "D_ADDs": sum(len(src) for _, _, src in word["D"]),
            "F": f, "B": b, "local_bits": local.bit_length(),
            "nine_stage_bits": nine.bit_length(),
            "local_guard": local < 2**104, "nine_stage_guard": nine < 2**192}


def suffix(word, values):
    """Positive suffix, used only for the nomination's forward proxy."""
    values = list(values)
    for section in ("A", "scatter", "B", "C"):
        if section == "scatter":
            for i, src in enumerate(word[section]):
                values[word["v"]+i] += sum(values[word["ret"][j]] for j in src)
        else:
            for _, d, src in word[section]:
                values[d] += sum(values[s] for s in src)
    return values
