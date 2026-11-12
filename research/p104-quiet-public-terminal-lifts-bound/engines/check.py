"""Check the entire current quiet-tail stock without decoding the native word."""
from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PINS = {
    "inputs/7314-CONTACT.json": "dcd1eae5bcfb56cf3b5cad3038e7bfc8d7456bade4937554b3596119b9717e4e",
    "inputs/7334-CHANGED.json": "f4d3f6ca2d87f8cd68c01ac9f77b69bd5a796f92bd567cea8afe3ac7c72e8e4b",
    "inputs/R92-PRICE.json": "05d7a5ebdd2eeedd6c8f534e8e2eeac22484daf9f387f4a6b88cc9eed22a6b8f",
    "inputs/R136-LEAD.json": "df42aba453a35097d87933dbad69e829baaa6fafeb35b56712fb631352eaebe2",
    "inputs/R136-REVERSE.json": "e2298f10dd9c23a4efb249f8d5a5f9763389885b8c1bf7ac2781b7dae2c929a8",
    "inputs/7334-construct.py": "ecb39578063d7f09153a85370a3b9bb7cbf8b36ff9891033a1cce7a2fe7f7fda",
}


def unique(items):
    result = dict(items)
    if len(result) != len(items):
        raise ValueError("duplicate key")
    return result


def load(name):
    raw = (ROOT / name).read_bytes()
    if sha256(raw).hexdigest() != PINS[name]:
        raise ValueError(f"changed {name}")
    return json.loads(raw, object_pairs_hook=unique) if name.endswith(".json") else raw


def main():
    assert __debug__
    old = load("inputs/7314-CONTACT.json")
    changed = load("inputs/7334-CHANGED.json")
    current = load("inputs/R92-PRICE.json")
    lead = load("inputs/R136-LEAD.json")
    reverse = load("inputs/R136-REVERSE.json")
    load("inputs/7334-construct.py")
    assert old["head"] == "9d0119eb12fbd9fa534b48cd37b68e7099757b91"
    assert old["events"] == 76461 and old["visited"] == 1101 and not old["unvisited"]
    predecessor = {row["h"]: row for row in old["rows"] if (row["initial"],row["final"]) == (3,127)}
    assert len(predecessor) == 616 and all(x["last"] is not None and x["status"] == "last_not_move"
                                          for x in predecessor.values())
    cohort = set(current["endpoint_cohort"])
    assert len(cohort) == len(current["endpoint_cohort"]) == 615
    assert predecessor.keys() - cohort == {319} and cohort <= predecessor.keys()
    assert lead["head"] == reverse["head"] == current["head"]
    assert lead["caller"] == reverse["caller"] == current["caller_head"]
    assert reverse["roles_visited"] == 615 and not lead["unresolved"] and not reverse["unresolved"]
    affected = set(changed["roles"]) & cohort
    assert len(changed["roles"]) == 14 and len(affected) == 6
    assert lead["anchors"] == reverse["anchors"] and set(map(int,lead["anchors"])) == affected
    fields = ("roles","first_exterior","exterior_event_count")
    assert [[g[k] for k in fields] for g in lead["groups"]] == [[g[k] for k in fields] for g in reverse["groups"]]
    exceptions = []
    for group in lead["groups"]:
        h, = group["roles"]
        clock, role, other, op, coefficient = group["first_exterior"]
        terminal = lead["anchors"][str(h)]
        assert h in affected and clock > terminal and h in (role,other) and op == "ADD"
        exceptions.append([h,terminal,clock,role,other,coefficient])
    assert len(exceptions) == 6
    print(json.dumps({"pins":PINS,"head":current["head"],"scope":sorted(cohort),
                      "inherited":sorted(cohort-affected),"current_after_last_move":exceptions,
                      "quiet_tails":[],"compatible_saving_upper":"0","unresolved":[]},
                     sort_keys=True,indent=2))


if __name__ == "__main__":
    main()
