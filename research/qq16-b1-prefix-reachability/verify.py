#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Certify an exact B1 prefix inverse and a hybrid reachable-collision lift."""

from __future__ import annotations

import gzip
import hashlib
import json
import sys
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CUT = 11795
DATA = "research/joint-query/certificate.json.gz"
DATA_SHA = "a5ed85fac5ebf3c091482a113ab0d351eb5a7892fe2841a35e16017ec1ff49f7"
PROOF_SHA = "188e184bb4beb802eb51eaac9229d6e2f266604382f3a0f55e63ab08ca8a42d9"
README_SHA = "24cdb4d8a32e091122f53b19c21d415127b38d2419c9cbf8ffbe0d85c2e077a8"
ZERO = (Q(0),) * 4


def need(ok: bool, reason: str) -> None:
    if not ok:
        raise ValueError(reason)


def authenticate_claim() -> None:
    claim = json.loads((HERE / "CLAIM.json").read_text())
    need(
        claim["head"] == "4fa77102119e345e02e1e5d3167221e8eb793ff1", "predecessor head"
    )
    expected = {
        "source/PR3258-PROOF.md": PROOF_SHA,
        "source/PR3258-README.md": README_SHA,
    }
    need(
        len(claim["files"]) == 2
        and {r["file"] for r in claim["files"]} == set(expected),
        "predecessor file set",
    )
    for row in claim["files"]:
        raw = (HERE / row["file"]).read_bytes()
        need(
            hashlib.sha256(raw).hexdigest() == row["sha256"] == expected[row["file"]],
            "predecessor bytes",
        )
        blob = b"blob " + str(len(raw)).encode() + b"\0" + raw
        need(
            hashlib.sha1(blob, usedforsecurity=False).hexdigest() == row["git_blob"],
            "predecessor blob",
        )


def load() -> tuple[dict, list]:
    pins = json.loads((HERE / "SOURCES.json").read_text())
    pin = next(p for p in pins["files"] if p["path"] == DATA)
    raw = (ROOT / DATA).read_bytes()
    need(pin["sha256"] == DATA_SHA, "literal packet hash pin")
    need(
        len(raw) < 1_000_000 and hashlib.sha256(raw).hexdigest() == DATA_SHA,
        "packet pin",
    )
    decoded = gzip.decompress(raw)
    need(len(decoded) < 12_000_000, "packet capacity")
    packet = json.loads(decoded)
    events = []
    for event in packet["programs"]["B_1_2"]:
        if event[0] == "retained_core":
            events.extend(packet["core_words"][event[1]])
        elif event[0] in {"private_sweep", "cover_sweep"}:
            events.extend(event[2])
        else:
            events.append(event)
    need(len(events) == 27019, "B1 event count")
    need(events[CUT] == ["climb", "A", 470, 0, 5, 1], "child binding")
    need(
        events[CUT + 1] == ["scalar", ["add", ["L", 524], ["L", 470], -1, 2], 5],
        "halfADD binding",
    )
    return packet, events


def scalar(event: list) -> list | None:
    return event[1] if event[0] == "scalar" else None


def is_clear(event: list) -> bool:
    op = scalar(event)
    return op is not None and op[0] == "clear"


def audit_epoch(block: list, start: int) -> dict:
    need(2 <= len(block) <= 100, "epoch event bound")
    field = block[0][1][1]
    need(field[0] == "C" and 0 <= field[1] < 8, "private clear namespace")
    need(block[-1][1] == ["clear", field], "matching private clears")
    controls, targets = set(), set()
    collect = deliver = native = 0
    delivery_started = False
    for event in block[1:-1]:
        op = scalar(event)
        if op is not None:
            need(op[0] == "add" and op[4] != 0, "epoch ADD only")
            dst, src = op[1:3]
            if dst == field:
                need(not delivery_started and src[0] == "L", "collector phase")
                controls.add(src[1])
                collect += 1
            else:
                need(src == field and dst[0] == "L", "delivery edge")
                targets.add(dst[1])
                deliver += 1
                delivery_started = True
        else:
            need(
                event[0] == "native_line"
                and event[1] == field
                and not delivery_started,
                "only private native maps before delivery",
            )
            native += 1
    need(
        collect > 0 and deliver > 0 and controls.isdisjoint(targets),
        "shear disjointness",
    )
    need(all(0 <= i < 704 for i in controls | targets), "ordinary field capacity")
    return {
        "start": start,
        "stop": start + len(block) - 1,
        "field": field[1],
        "controls": sorted(controls),
        "targets": sorted(targets),
        "collect": collect,
        "deliver": deliver,
        "native": native,
    }


def ordinary_field(event: list) -> int:
    kind = event[0]
    if kind in {"native_line", "cover_map"}:
        need(event[1][0] == "L", "ordinary map namespace")
        role = event[1][1]
    elif kind == "climb":
        role = event[2]
    else:
        need(kind in {"adapter", "residual_adapter"}, "known opaque map")
        role = event[2]
    need(type(role) is int and 0 <= role < 704, "ordinary map field")
    return role


def compile_prefix(events: list) -> tuple[list, list]:
    prefix, units, epochs = events[:CUT], [], []
    index = 0
    for _ in range(CUT):
        if index == CUT:
            return units, epochs
        event = prefix[index]
        if is_clear(event):
            stop = next(
                (
                    j
                    for j in range(index + 1, min(index + 100, CUT))
                    if is_clear(prefix[j])
                ),
                None,
            )
            need(stop is not None, "closed private epoch")
            block = prefix[index : stop + 1]
            epochs.append(audit_epoch(block, index))
            units.append(["epoch", block])
            index = stop + 1
            continue
        op = scalar(event)
        if op is not None:
            need(
                op[0] in {"add", "scale"} and op[1][0] == "L",
                "invertible ordinary scalar",
            )
            need(
                0 <= op[1][1] < 704 and op[-1] != 0,
                "scalar destination and denominator",
            )
            if op[0] == "add":
                need(
                    op[2][0] == "L" and 0 <= op[2][1] < 704 and op[1] != op[2],
                    "distinct ADD fields",
                )
            else:
                need(op[2] != 0, "nonzero SCALE")
        elif event[0] != "phase":
            ordinary_field(event)
        units.append(["event", event])
        index += 1
    need(index == CUT, "prefix work bound")
    return units, epochs


def add(target: tuple, source: tuple, coefficient: Q) -> tuple:
    return tuple(a + coefficient * b for a, b in zip(target, source, strict=True))


def opaque(value: tuple, event: list, *, inverse: bool = False) -> tuple:
    """Noncommuting exact GL4 substitution, not an evaluator of native recipes."""
    code = hashlib.sha256(json.dumps(event).encode()).digest()[0]
    shift, numerator = code % 4, 1 + code % 3
    if inverse:
        changed = list(value)
        changed[1] -= Q(numerator, 2) * changed[0]
        return tuple(changed[(i - shift) % 4] for i in range(4))
    changed = [value[(i + shift) % 4] for i in range(4)]
    changed[1] += Q(numerator, 2) * changed[0]
    return tuple(changed)


def epoch_action(state: list, block: list, *, inverse: bool) -> None:
    private = ZERO
    for event in block[1:-1]:
        op = scalar(event)
        if op is None:
            private = opaque(private, event)
        elif op[1][0] == "C":
            private = add(private, state[op[2][1]], Q(op[3], op[4]))
        else:
            coefficient = Q(op[3], op[4]) * (-1 if inverse else 1)
            state[op[1][1]] = add(state[op[1][1]], private, coefficient)


def run(state: list, units: list, *, inverse: bool = False) -> list:
    need(
        len(state) == 704 and all(len(v) == 4 for v in state),
        "substitution state shape",
    )
    state = state.copy()
    for kind, item in reversed(units) if inverse else units:
        if kind == "epoch":
            epoch_action(state, item, inverse=inverse)
            continue
        op = scalar(item)
        if op is not None:
            role = op[1][1]
            if op[0] == "add":
                coefficient = Q(op[3], op[4]) * (-1 if inverse else 1)
                state[role] = add(state[role], state[op[2][1]], coefficient)
            else:
                coefficient = Q(op[2], op[3])
                state[role] = tuple(
                    v * (1 / coefficient if inverse else coefficient)
                    for v in state[role]
                )
        elif item[0] != "phase":
            role = ordinary_field(item)
            state[role] = opaque(state[role], item, inverse=inverse)
    return state


def nearest(value: int, precision: int) -> int:
    step = 1 << max(0, abs(value).bit_length() - precision)
    lower, residue = divmod(abs(value), step)
    increment = 2 * residue > step or (2 * residue == step and lower % 2)
    return (-1 if value < 0 else 1) * (lower + int(increment)) * step


def rounded_pair(precision: int, small: int) -> tuple:
    """One predecessor rank-one pair in its right-monomial chart, q=4."""
    large = 4 << (precision + 1)
    plus, minus = nearest(large + small, precision), nearest(large - small, precision)
    result = (plus // 2, minus // 2, plus // 2, -minus // 2)
    need(plus == minus == large, "uniform midpoint collision")
    destination = tuple(nearest(-v // 2, precision) for v in result)
    return result, destination


def substitution_checks(units: list) -> dict:
    records = []
    for precision in (2, 8, 53):
        outputs, entries = [], []
        for small in (-4, 0, 4):
            cut = [ZERO] * 704
            cut[470] = (Q(4 << (precision + 1)), Q(0), Q(small), Q(0))
            entry = run(cut, units, inverse=True)
            need(run(entry, units) == cut, "exact full prefix right inverse")
            need(run(run(entry, units), units, inverse=True) == entry, "left inverse")
            entries.append(entry)
            result, destination = rounded_pair(precision, small)
            after = cut.copy()
            after[470], after[524] = result, destination
            outputs.append(after)
        need(entries[0] != entries[1] != entries[2], "distinct complete entries")
        need(outputs[0] == outputs[1] == outputs[2], "identical complete cut state")
        records.append(
            {"precision": precision, "reachable_entries": 3, "returned_states": 1}
        )
    return {
        "model": "exact noncommuting GL4 substitution, not native numerical replay",
        "fixtures": records,
    }


def compute() -> dict:
    authenticate_claim()
    _, events = load()
    units, epochs = compile_prefix(events)
    need(len(epochs) == 16, "all private epochs accounted for")
    need(
        all(row["native"] == (1 if i < 8 else 0) for i, row in enumerate(epochs)),
        "private native sites",
    )
    local = []
    for precision in (2, 3, 8, 24, 53, 104, 2046):
        returns = [rounded_pair(precision, c) for c in (-4, 0, 4)]
        need(returns[0] == returns[1] == returns[2], "local family control")
        local.append(precision)
    return {
        "prefix_events": CUT,
        "collapsed_units": len(units),
        "private_epochs": epochs,
        "event_kinds": dict(sorted(Counter(e[0] for e in events[:CUT]).items())),
        "local_collision_precisions": local,
        "inverse_substitution": substitution_checks(units),
        "theorem": (
            "Exact prefix bijective under invertible map contracts; "
            "collision lift requires a compatible local cut space"
        ),
        "not_checked": [
            "fully rounded prefix",
            "F0-to-B1 entry reachability",
            "native embedding of PR3258 local reference",
            "global caller entry format",
            "actual native payload execution",
            "full producer restoration",
            "physical costs",
            "supplier admission",
        ],
    }


def main() -> None:
    need(sys.argv[1:] in [[], ["--emit"]], "usage: verify.py [--emit]")
    result = compute()
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if sys.argv[1:] == ["--emit"]:
        print(text, end="")
        return
    need(
        json.loads(text) == json.loads((HERE / "RESULT.json").read_text()),
        "receipt equality",
    )
    print(
        "PASS_QQ16_B1_PREFIX_REACHABILITY epochs=16 ordinary=704 "
        "cut=11795 hybrid_only no_new_kappa"
    )


if __name__ == "__main__":
    main()
