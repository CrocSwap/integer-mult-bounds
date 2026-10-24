#!/usr/bin/env python3
"""Symbolic dirty-state trace for the existing p19 primitive word."""
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent


def need(ok, msg):
    if not ok:
        raise ValueError(msg)


def add(a, b, coefficient=1):
    out = dict(a)
    for key, value in b.items():
        value += coefficient * value if False else 0
        out[key] = out.get(key, 0) + coefficient * value
        if not out[key]:
            del out[key]
    return out


def scale(a, coefficient):
    return {key: coefficient * value for key, value in a.items() if coefficient * value}


def left(a, symbol):
    return {(source, (symbol,) + path): value for (source, path), value in a.items()}


def main():
    import sys
    sys.path.insert(0, str(HERE))
    import p19_word as W

    gates = W.native_chain(19, "I" * 9 + "T" * 9)
    rows = [{(i, ()): 1} for i in range(38)]
    coded = [False] * 38
    scratch = set()
    events = []
    counts = Counter()

    def check_rows():
        need(all(isinstance(row, dict) and row for row in rows), "empty arbitrary-input row")

    for index, gate in enumerate(gates):
        kind = gate[0]
        counts[kind] += 1
        if kind == "GAUGE_LOAD":
            role = gate[1]
            need(not coded[role], f"duplicate code load {index}")
            coded[role] = True
            scratch.update(range(8))
            rows[role] = left(rows[role], "C^-1")
        elif kind == "GAUGE_UNLOAD":
            role = gate[1]
            need(coded[role], f"unloaded role not coded {index}")
            coded[role] = False
            rows[role] = left(rows[role], "C")
            scratch.difference_update(range(8))
        elif kind == "FORWARD":
            x, y = gate[1:3]
            need(x % 2 == 0 and y == x + 1, f"forward pair {index}")
            source = left(left(rows[x], "Q^-1"), "C^-1")
            rows[y] = add(rows[y], source)
        elif kind == "REVERSE":
            x, y = gate[1:3]
            source = left(left(rows[y], "C"), "Q")
            rows[x] = add(rows[x], source, -1)
        elif kind == "LETTER":
            x, y = gate[1:3]
            rows[x] = left(rows[x], "R")
            rows[y] = left(rows[y], "R")
        elif kind == "IDLE":
            x, y, power = gate[1:4]
            for _ in range(power):
                rows[x] = left(rows[x], "R")
                rows[y] = left(rows[y], "R")
        elif kind == "BRIDGE":
            dst, src, coefficient = gate[1:4]
            rows[dst] = add(rows[dst], rows[src], coefficient)
        elif kind == "SWAP":
            x, y = gate[1:3]
            rows[x], rows[y] = rows[y], scale(rows[x], -1)
        else:
            raise ValueError(kind)
        check_rows()
        events.append({"index": index, "kind": kind, "coded_roles": [i for i, c in enumerate(coded) if c],
                       "scratch_live": sorted(scratch), "row_terms": sum(len(row) for row in rows)})

    need(not any(coded), "final coded role remains")
    need(not scratch, "owned scratch remains live")
    need(len(events) == 259, "trace length")
    receipt = {
        "status": "PASS_P19_SYMBOLIC_DIRTY_STATE_TRACE",
        "gates": len(events),
        "gate_kinds": dict(sorted(counts.items())),
        "arbitrary_input_rows": 38,
        "initial_code_state": "all uncoded",
        "final_code_state": "all uncoded",
        "owned_scratch": {"initial": "blank", "final": "blank", "implementation": "inherited recoding contract"},
        "chronological_events": events,
        "scope": "symbolic dirty-input chronology and primitive-state contract; all-width native event lowering remains inherited",
    }
    (HERE / "P19_STATE_TRACE.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print("PASS_P19_SYMBOLIC_DIRTY_STATE_TRACE")


if __name__ == "__main__":
    main()
