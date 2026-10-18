#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""A separate read/write-set audit of every private epoch in the B1 prefix."""

import gzip
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def check(ok, message):
    if not ok:
        raise ValueError(message)


def load_word():
    packet = json.loads(
        gzip.decompress(
            (ROOT / "research/joint-query/certificate.json.gz").read_bytes()
        )
    )
    word = []
    for item in packet["programs"]["B_1_2"]:
        if item[0] == "retained_core":
            word += packet["core_words"][item[1]]
        elif item[0] in ["private_sweep", "cover_sweep"]:
            word += item[2]
        else:
            word.append(item)
    return word


def main():
    word = load_word()
    expected = json.loads((HERE / "RESULT.json").read_text())["private_epochs"]
    active, rows = None, []
    for index, event in enumerate(word[:11795]):
        if event[0] != "scalar":
            if active is not None:
                check(
                    event[:2] == ["native_line", ["C", active["field"]]],
                    "private map identity",
                )
            continue
        gate = event[1]
        if gate[0] == "clear":
            check(gate[1][0] == "C", "no erased ordinary state")
            if active is None:
                active = {
                    "start": index,
                    "field": gate[1][1],
                    "read": set(),
                    "write": set(),
                }
            else:
                check(active["field"] == gate[1][1], "matching private register")
                check(active["read"].isdisjoint(active["write"]), "unchanged controls")
                rows.append(
                    (
                        active["start"],
                        index,
                        sorted(active["read"]),
                        sorted(active["write"]),
                    )
                )
                active = None
        elif active is not None:
            check(gate[0] == "add", "linear collector syntax")
            target, source = gate[1:3]
            if target[0] == "C":
                active["read"].add(source[1])
            else:
                check(source == ["C", active["field"]], "private delivery source")
                active["write"].add(target[1])
        else:
            check(gate[1][0] == "L", "no live private dependency outside epochs")
            check(gate[0] in ["add", "scale"], "elementary ordinary gate")
            if gate[0] == "add":
                check(gate[1] != gate[2] and gate[2][0] == "L", "distinct ordinary ADD")
            else:
                check(gate[2] != 0, "invertible scalar")
    check(active is None, "zero private cut")
    target = [(r["start"], r["stop"], r["controls"], r["targets"]) for r in expected]
    check(rows == target and len(rows) == 16, "independent epoch receipt")
    print("PASS_INDEPENDENT_B1_PREFIX_EPOCHS")


if __name__ == "__main__":
    main()
