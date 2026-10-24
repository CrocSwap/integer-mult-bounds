#!/usr/bin/env python3
"""Independent symbolic replay of the emitted p19 native macro word."""
import gzip
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def add(left, right, coefficient=1):
    out = dict(left)
    for key, value in right.items():
        out[key] = out.get(key, 0) + coefficient * value
        if not out[key]:
            del out[key]
    return out


def left(row, symbol):
    return {(source, (symbol,) + path): value for (source, path), value in row.items()}


def replay(events):
    rows = [{(role, ()): 1} for role in range(38)]
    coded = [False] * 38
    scratch = 0
    chronology = []
    for event in events:
        op = event["op"]
        if op == "CODE":
            role = event["role"]
            need(len(event.get("port_wrappers", {})) == 112,
                 "source-bound code wrapper set")
            need(all(all(item[0] in ("P", "D", "X", "phase")
                         for item in wrapper["word"])
                     for wrappers in event["port_wrappers"].values()
                     for wrapper in wrappers.values()),
                 "source-bound wrapper vocabulary")
            if event["word"] == [["C", -1]]:
                need(not coded[role], "duplicate code load")
                coded[role] = True
                scratch += event["owned_scratch"]
                rows[role] = left(rows[role], "C^-1")
            else:
                need(coded[role], "unloaded role was not coded")
                coded[role] = False
                scratch -= event["owned_scratch"]
                rows[role] = left(rows[role], "C")
        elif op == "CENTER_FREE_FULL":
            x, y = event["roles"]
            need(coded[y], "forward/reverse source is not coded")
            if event["direction"] == "forward":
                rows[y] = add(rows[y], left(left(rows[x], "Q^-1"), "C^-1"))
            else:
                rows[x] = add(rows[x], left(left(rows[y], "C"), "Q"), -1)
        elif op == "LETTER":
            x, y = event["roles"]
            rows[x] = left(rows[x], "R")
            rows[y] = left(rows[y], "R")
        elif op == "PAID_IDLE":
            x, y = event["roles"]
            for _ in range(event["power"]):
                rows[x] = left(rows[x], "R")
                rows[y] = left(rows[y], "R")
        elif op == "ADD":
            rows[event["dst"]] = add(rows[event["dst"]], rows[event["src"]],
                                      event["coefficient"])
        elif op == "SIGNED_SWAP":
            x, y = event["roles"]
            rows[x], rows[y] = rows[y], {key: -value for key, value in rows[x].items()}
        else:
            raise ValueError(op)
        chronology.append({"op": op, "coded": [i for i, value in enumerate(coded) if value],
                           "scratch": scratch, "terms": sum(len(row) for row in rows)})
    need(not any(coded), "coded role at endpoint")
    need(scratch == 0, "owned scratch at endpoint")
    return rows, chronology


def main():
    receipt = json.loads(gzip.decompress((HERE / "P19_NATIVE_MACRO.json.gz").read_bytes()))
    forward = json.loads((HERE / "P19_FORWARD_PROGRAM.json").read_text())
    reverse = json.loads((HERE / "P19_REVERSE_PROGRAM.json").read_text())
    rows, chronology = replay(receipt["events"])
    need(len(chronology) == 259, "macro chronology length")
    need(all(row for row in rows), "empty symbolic endpoint row")
    counts = Counter(event["op"] for event in receipt["events"])
    need(counts["CODE"] == 38 and counts["CENTER_FREE_FULL"] == 39,
         "unit macro counts")
    need(forward["status"] == "PASS_LITERAL_FORWARD_QUERY_PROGRAM",
         "literal forward program")
    need(reverse["status"] == "PASS_LITERAL_REVERSE_LETTER_PROGRAM",
         "literal reverse program")
    need(forward["owned_work_final_zero"] and reverse["endpoint"]["owned_scratch_blank"],
         "owned cleanup")
    need(forward["p19_rank_one_query_calls"] == 2240 and
         reverse["reverse_rank_one_corrections"] == 4256,
         "literal direction resource counts")
    out = {
        "status": "PASS_P19_NATIVE_MACRO_REPLAY",
        "events": len(chronology),
        "arbitrary_symbolic_rows": 38,
        "endpoint": {"all_roles_uncoded": True, "owned_scratch_blank": True},
        "operator": "P19_STATE_TRACE plus literal forward/reverse owned-work programs",
        "macro_receipt": "P19_NATIVE_MACRO.json.gz",
        "chronology": chronology,
    }
    (HERE / "P19_NATIVE_MACRO_REPLAY.json").write_text(
        json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": out["status"], "events": len(chronology)}, sort_keys=True))


if __name__ == "__main__":
    main()
