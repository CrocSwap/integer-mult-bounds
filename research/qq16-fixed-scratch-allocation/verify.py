#!/usr/bin/env python3
"""Certify fixed-bank scratch allocation for the unchanged PR2707 word.

Nick Petalas. Apache-2.0. Native semantics and physical movement are outside scope.
"""

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
WORD_SHA256 = "5623b9cd62635d47f84e78135d817cfddec7ae31c154c565bf6e16cf5ed75475"
MAX_BYTES = 200_000
EVENTS = 3823
OUTPUTS = tuple(f"{p}{i}" for p in "ZW" for i in range(112))
BORROWED = frozenset(f"{p}{i}" for p in "XY" for i in range(112))
PRIVATE = frozenset(f"{p}{i}" for p in "FG" for i in range(8))
SCOPES = {"B1_current_query": 8, "future_logger_inverse": 8, "F0_inverse": 16}
COUNTS = {"add": 2704, "clear": 312, "line": 336, "map": 464,
          "begin": 3, "end": 3, "checkpoint": 1}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def unique(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def read_bytes(path):
    need(path.is_file() and not path.is_symlink(), "expected plain JSON file")
    with path.open("rb") as source:
        raw = source.read(MAX_BYTES + 1)
    need(len(raw) <= MAX_BYTES, "JSON byte capacity")
    return raw


def read_json(path):
    raw = read_bytes(path)
    return raw, json.loads(raw, object_pairs_hook=unique)


def touched(event):
    if event[0] == "checkpoint":
        return OUTPUTS
    if event[0] == "add":
        return event[1:3]
    if event[0] in ("clear", "line", "map"):
        return event[1:2]
    return []


def validate(word):
    """Validate types and the fixed instruction alphabet before traversing it."""
    need(type(word) is list and len(word) == EVENTS, "event capacity")
    shapes = {"clear": 3, "add": 4, "line": 4, "map": 5,
              "begin": 3, "end": 3, "checkpoint": 2}
    fields = set(OUTPUTS) | BORROWED | PRIVATE
    for event in word:
        need(type(event) is list and event and type(event[0]) is str, "event shape")
        op = event[0]
        need(op in shapes and len(event) == shapes[op], "instruction shape")
        need(type(event[1]) is str, "instruction name")
        if op in ("begin", "end"):
            need(event[1] in SCOPES and type(event[2]) is int
                 and event[2] == SCOPES[event[1]], "scope schema")
        elif op == "checkpoint":
            need(event[1] == "original_F0_outputs", "checkpoint schema")
        else:
            need(event[1] in fields and event[1] not in BORROWED, "illegal write")
            if op == "clear":
                need(type(event[2]) is str, "CLEAR frame")
            elif op == "add":
                need(type(event[2]) is str and event[2] in fields
                     and event[2] != event[1], "ADD source")
                need(type(event[3]) is str and event[3] in ("1", "-1", "1/4", "-1/4"),
                     "ADD coefficient")
            elif op == "line":
                need(type(event[2]) is int and 0 <= event[2] < 112
                     and type(event[3]) is int and event[3] in (-1, 1), "LINE schema")
            else:
                need(type(event[2]) is int and event[2] in (1, 2)
                     and type(event[3]) is int and 0 <= event[3] < 112
                     and type(event[4]) is bool, "MAP schema")
    need(dict(Counter(e[0] for e in word)) == COUNTS, "instruction invoice")


def lifetimes(word):
    """Keep first initialization, all data accesses, and literal cleanup."""
    known, active, rows, result = set(BORROWED), None, {}, []
    for index, event in enumerate(word):
        op = event[0]
        if op == "begin":
            need(active is None, "nested private scope")
            active, rows = event[1], {}
        elif op == "end":
            need(active == event[1] and len(rows) == event[2], "scope ownership")
            for name, access in sorted(rows.items()):
                first, last = access[0], access[-1]
                need(word[first][0] == "clear" and word[last][0] == "clear",
                     "scratch initialization/cleanup")
                reads = [i for i in access if word[i][0] != "clear"]
                need(bool(reads), "empty scratch lifetime")
                result.append({"scope": active, "field": name, "first": first,
                               "last_read": reads[-1], "last": last})
            known.difference_update(PRIVATE)
            active, rows = None, {}
        elif op != "checkpoint":
            dest = event[1]
            for name in touched(event):
                if name in PRIVATE:
                    need(active is not None, "scratch outside scope")
                    need(name[0] == "F" or SCOPES[active] == 16, "scratch capacity")
                    rows.setdefault(name, []).append(index)
            if op == "clear":
                known.add(dest)
            else:
                need(dest in known, "dirty destination read")
                if op == "add":
                    need(event[2] in known, "dirty source read")
    need(active is None and len(result) == 32, "complete scratch lifetime inventory")
    return result


def output_gaps(word):
    """Enumerate initial disposable dirt and every gap before a later CLEAR."""
    last = dict.fromkeys(OUTPUTS, -1)
    gaps = []
    for index, event in enumerate(word):
        if event[0] == "clear" and event[1] in last:
            name = event[1]
            gaps.append({"field": name, "after": last[name], "before": index})
        for name in touched(event):
            if name in last:
                last[name] = index
    # Final outputs are implicitly read at delivery; there is no final dead gap.
    need(all(i >= 0 for i in last.values()), "missing output bank")
    return gaps


def fits(row, gap, cleanup=True):
    stop = row["last"] if cleanup else row["last_read"]
    return gap["after"] < row["first"] and stop < gap["before"]


def check_allocation(rows, gaps, bindings, extra):
    """Check one constant binding per lifetime against the complete access model."""
    need(type(extra) is int and 0 <= extra <= 16, "private slot capacity")
    keys = {(r["scope"], r["field"]) for r in rows}
    need(type(bindings) is dict and set(bindings) == keys, "binding inventory")
    by_slot = {}
    for row in rows:
        slot = bindings[(row["scope"], row["field"])]
        need(type(slot) is str, "binding type")
        if slot in OUTPUTS:
            need(any(g["field"] == slot and fits(row, g) for g in gaps),
                 "output bank not disposable for complete scratch lifetime")
        else:
            need(slot in {f"P{i}" for i in range(extra)}, "unowned private slot")
        for other in by_slot.get(slot, []):
            need(row["last"] < other["first"] or other["last"] < row["first"],
                 "overlapping private lifetimes")
        by_slot.setdefault(slot, []).append(row)


def baseline(rows):
    return {(r["scope"], r["field"]):
            f"P{int(r['field'][1:]) + (8 if r['field'][0] == 'G' else 0)}" for r in rows}


def certificate(word):
    validate(word)
    rows, gaps = lifetimes(word), output_gaps(word)
    edges = [{"scope": r["scope"], "field": r["field"], "bank": g["field"]}
             for r in rows for g in gaps if fits(r, g)]
    need(not edges, "unexpected output alias opportunity")
    bindings = baseline(rows)
    check_allocation(rows, gaps, bindings, 16)
    final = [r for r in rows if r["scope"] == "F0_inverse"]
    clique = max(r["first"] for r in final)
    need(len(final) == 16 and all(r["first"] <= clique <= r["last"] for r in final),
         "sixteen-way private interference witness")
    last_read_edges = [{"scope": r["scope"], "field": r["field"], "bank": g["field"]}
                       for r in rows for g in gaps if fits(r, g, cleanup=False)]
    need({"scope": "F0_inverse", "field": "F4", "bank": "Z76"} in last_read_edges,
         "cleanup counterexample missing")
    return {"schema_version": 1, "source_sha256": WORD_SHA256, "events": len(word),
            "lifetimes": rows, "output_gaps": gaps, "alias_edges": edges,
            "last_read_only_edges": last_read_edges, "clique_event": clique,
            "minimum_extra_arrays_fixed_binding": 16, "output_arrays": 224,
            "borrowed_arrays": 224, "total_payload_arrays": 464}


def semantic_controls(word):
    """Exercise the public allocation predicate and actual chronology failures."""
    rows, gaps = lifetimes(word), output_gaps(word)
    original = baseline(rows)
    controls = []
    for scope, field, slot in [("B1_current_query", "F0", "W0"),
                               ("F0_inverse", "F4", "Z76"),
                               ("F0_inverse", "F0", "X0"),
                               ("F0_inverse", "G7", "P0")]:
        binding = dict(original)
        binding[(scope, field)] = slot
        controls.append((scope + "/" + field + "->" + slot, binding, 16))
    controls.append(("fifteen slots", original, 15))
    missing = dict(original)
    del missing[("F0_inverse", "G7")]
    controls.append(("missing binding", missing, 16))
    for label, binding, extra in controls:
        try:
            check_allocation(rows, gaps, binding, extra)
        except ValueError:
            continue
        raise ValueError("allocation control accepted: " + label)
    need(word[697] == ["clear", "F0", "wide"]
         and word[698] == ["add", "F0", "W0", "1"], "live-source collision witness")
    need(word[3794] == ["clear", "F4", "identity"]
         and word[3765] == ["clear", "Z76", "wide"], "late-cleanup witness")
    return len(controls)


def run(package, write=False):
    raw = read_bytes(package / "WORD.json")
    need(hashlib.sha256(raw).hexdigest() == WORD_SHA256, "source word drift")
    word = json.loads(raw, object_pairs_hook=unique)
    result = certificate(word)
    result["rejecting_controls"] = semantic_controls(word)
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    path = package / "RESULT.json"
    if write:
        with path.open("x") as target:
            need(target.write(encoded) == len(encoded), "short receipt write")
    else:
        _, receipt = read_json(path)
        need(json.dumps(receipt, sort_keys=True) == json.dumps(result, sort_keys=True),
             "typed receipt mismatch")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="create an absent receipt")
    args = parser.parse_args()
    result = run(PACKAGE, args.write)
    print("PASS_QQ16_FIXED_SCRATCH_ALLOCATION lifetimes=32 alias_edges=0 "
          f"minimum_extra={result['minimum_extra_arrays_fixed_binding']} no_new_kappa")


if __name__ == "__main__":
    main()
