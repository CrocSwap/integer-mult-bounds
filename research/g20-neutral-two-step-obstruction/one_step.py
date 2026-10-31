#!/usr/bin/env python3
"""Exact all-path paid-query floor for one fixed-frame G20 conjugation.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
Credits: Ali Romman (#5708), unpaidmoon (#6290), Nick Petalas (#6305), and their
retained predecessors. No predecessor executable is imported; arithmetic is integer.
"""
import argparse
from collections import Counter, defaultdict
from hashlib import sha256
import gzip
import json
from pathlib import Path
from types import ModuleType

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PREFIX = "research/g20-conjugation-admission/"

# Share the unchanged, hash-bound all-path accounting module with the joint checker.
_floor_path = HERE / "route_floor.py"
_floor_bytes = _floor_path.read_bytes()
if sha256(_floor_bytes).hexdigest() != "c807d8aa58fcdaf670639854b556d7b7b64291a4968bda9895133ab84f1023bf":
    raise ValueError("route-floor implementation changed")
_floor = ModuleType("g20_one_step_route_floor")
_floor.__file__ = str(_floor_path)
exec(compile(_floor_bytes, str(_floor_path), "exec"), _floor.__dict__)
graph = _floor.graph
collapsed_invoice = _floor.collapsed_invoice
signed_delta = _floor.signed_delta
sign_certificate = _floor.sign_certificate


def need(condition, message):
    if not condition:
        raise ValueError(message)




def examine_interval(records, left, right):
    a, b = records[left][1:3]
    need(records[left][:3] == records[right][:3], "equal endpoint ADDs")
    corrections = {}
    for index in range(left + 1, right):
        event = records[index]
        if event[0] in ("INIT", "ERASE"):
            if event[1] in (a, b):
                return None, "barrier"
        else:
            need(event[0] == "ADD", "scalar alphabet")
            d, s, frame = event[1:]
            if d == b and s == a:
                return None, "reversed"
            if d == b:
                corrections[index] = ("ADD", a, s, frame)
            elif s == a:
                corrections[index] = ("ADD", d, b, frame)
    return corrections, None


def changed_records(records, left, right, corrections):
    result = []
    for index, event in enumerate(records):
        if index in (left, right):
            continue
        result.append(event)
        if index in corrections:
            result.append(corrections[index])
    return result


def endpoint(records, width, owned):
    values = [1 << index for index in range(width)]
    for event in records:
        op, d = event[:2]
        if op == "ADD":
            need(d != event[2], "distinct ADD roles")
            values[d] ^= values[event[2]]
        else:
            need(op in ("INIT", "ERASE") and d in owned, "owned scalar opcode")
            need(op != "INIT" or values[d] == 0, "whole-zero initialization")
            values[d] = 0
    return values








def census(word, paths):
    edges, level, reachable = graph(paths)
    scalars = [tuple(e) for e in word["records"] if e[0] not in ("Q", "ZERO_Q")]
    width, owned = len(word["start"]), set(word["owned"])
    need(width == 685 and len(scalars) == 11930, "source shape")
    expected = [0 if i in owned else (1 << i) ^ ((1 << (i - 111)) if 111 <= i < 222 else 0)
                for i in range(width)]
    need(endpoint(scalars, width, owned) == expected, "source endpoint")
    base = Counter(e[4] for e in word["records"] if e[0] == "Q")
    replayed, missing, _, paid_new = collapsed_invoice(scalars, word["start"], word["final"], owned,
                                                      level, reachable, edges)
    need(missing is None and not paid_new and replayed == base, "source paid invoice")
    groups = defaultdict(list)
    for index, event in enumerate(scalars):
        if event[0] == "ADD":
            groups[event[1:3]].append(index)
    counts, outcomes, zero_contacts, shapes = Counter(), [], [], Counter()
    for gate, positions in sorted(groups.items()):
        for offset, left in enumerate(positions):
            for right in positions[offset + 1:]:
                counts["equal_pairs"] += 1
                corrections, rejection = examine_interval(scalars, left, right)
                if rejection:
                    counts[rejection] += 1
                    continue
                counts["eligible"] += 1
                if not corrections:
                    zero_contacts.append([left, right, list(gate)])
                changed = changed_records(scalars, left, right, corrections)
                need(endpoint(changed, width, owned) == expected, "changed full endpoint")
                invoice, missing, requests, paid_new = collapsed_invoice(
                    changed, word["start"], word["final"], owned, level, reachable, edges)
                row = {"first": left, "last": right, "gate": list(gate), "contacts": len(corrections)}
                if missing is not None:
                    counts["unreachable"] += 1
                    row["missing"] = list(missing)
                else:
                    counts["reachable"] += 1
                    delta = signed_delta(invoice, base)
                    sign = sign_certificate(delta)
                    counts["neutral" if sign == "zero" else "strict_loss"] += 1
                    shapes[tuple(map(tuple, delta))] += 1
                    row.update(collapsed_delta=delta, sign=sign,
                               new_requests=[list(pair) for pair in sorted(requests) if pair not in edges])
                    need(sign != "zero" or not paid_new, "zero lower bound attainer")
                outcomes.append(row)
    need(dict(counts) == {"equal_pairs": 2787, "eligible": 2270, "unreachable": 2035,
                          "reachable": 235, "strict_loss": 213, "neutral": 22,
                          "reversed": 517}, "exact domain/outcome counts: " + str(dict(counts)))
    need(len(edges) == 2369 and len(level) == 636 and sum(map(len, reachable.values())) == 23560,
         "exact graph coverage")
    need(len(zero_contacts) == 2, "zero-contact coverage")
    closure_hash = sha256(json.dumps([[a, sorted(reachable[a])] for a in sorted(reachable)],
                                    separators=(",", ":")).encode()).hexdigest()
    return {"graph": {"edges": len(edges), "frames": len(level),
                      "reachable_pairs": sum(map(len, reachable.values())), "maximum_level": max(level.values()),
                      "level_counts": {str(k): v for k, v in sorted(Counter(level.values()).items())},
                      "closure_sha256": closure_hash},
            "counts": dict(sorted(counts.items())), "base_paid": {str(k): v for k, v in sorted(base.items())},
            "zero_contacts": zero_contacts,
            "shapes": [{"delta": list(map(list, delta)), "count": count, "sign": sign_certificate(delta)}
                       for delta, count in sorted(shapes.items())], "outcomes": outcomes}


def controls():
    edges, level, reach = graph({"0:1": [[0, 1, 1]], "1:2": [[1, 2, 2]]})
    need(reach[0] == {1, 2} and level[2] == 3, "two-edge reachability control")
    need((0, 2) not in edges, "new route control")
    try:
        graph({"0:1": [[0, 1, 1]], "1:2": [[1, 2, 2]], "0:2": [[0, 2, 2]]})
    except ValueError as error:
        need(str(error) == "exact rank potential", "potential rejection reason")
    else:
        raise ValueError("inconsistent potential accepted")
    bill, missing, _, _ = collapsed_invoice([("ADD", 0, 1, 2)], [0, 0], [2, 2], set(), level, reach, edges)
    need(missing is None and bill == {3: 2}, "all concatenated ranks charged")
    bill, missing, _, _ = collapsed_invoice([("ADD", 0, 1, 2)], [2, 0], [2, 2], set(), level, reach, edges)
    need(missing is None and bill == {3: 1}, "same frame costs zero")
    bill, missing, _, _ = collapsed_invoice([], [2], [0], set(), level, reach, edges)
    need(bill is None and missing == (2, 0), "unreachable final return rejects")
    bill, missing, _, _ = collapsed_invoice([("ERASE", 0, 2), ("ADD", 1, 0, 1)],
                                           [0, 0], [2, 0], {0}, level, reach, edges)
    need(missing is None and bill == {}, "zero-source ADD skips all routes")
    bill, missing, _, _ = collapsed_invoice([("ERASE", 0, 0), ("ADD", 0, 1, 2), ("ERASE", 0, 2)],
                                           [0, 0], [2, 2], {0}, level, reach, edges)
    need(missing is None and bill == {3: 1}, "zero destination route free but source paid")
    outer = ("ADD", 0, 1, 0)
    for middle, rejection in [(("ADD", 1, 0, 0), "reversed"), (("ERASE", 0, 0), "barrier")]:
        need(examine_interval([outer, middle, outer], 0, 2)[1] == rejection, "A2 barrier rejection")
    word = [outer, ("ADD", 1, 2, 1), outer]
    corr, rejection = examine_interval(word, 0, 2)
    need(rejection is None and endpoint(changed_records(word, 0, 2, corr), 3, set())
         == endpoint(word, 3, set()), "A2 positive identity")
    need(endpoint(changed_records(word, 0, 2, {}), 3, set()) != endpoint(word, 3, set()),
         "missing correction changes endpoint")
    try:
        sign_certificate([[1, 1], [2, -2], [3, 1]])
    except ValueError:
        pass
    else:
        raise ValueError("profitable delta called a loss")
    return 12


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, help="write exact new certificate outside checkout")
    args = parser.parse_args()
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    inputs = {}
    for source in manifest["files"]:
        if source["usage"] == "input":
            raw = (ROOT / source["path"]).read_bytes()
            need(sha256(raw).hexdigest() == source["sha256"], "source bytes: " + source["path"])
            inputs[source["path"]] = raw
    result = census(json.loads(gzip.decompress(inputs[PREFIX + "WORD.json.gz"])),
                    json.loads(inputs[PREFIX + "PATHS.json"]))
    result["controls"] = controls()
    if args.write:
        need(not args.write.resolve().is_relative_to(ROOT), "certificate output outside checkout")
        args.write.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        saved = json.loads((HERE / "ONE-STEP.json").read_text())
        need(json.dumps(result, sort_keys=True, separators=(",", ":"))
             == json.dumps(saved, sort_keys=True, separators=(",", ":")),
             "complete typed certificate equality")
    print(json.dumps({"counts": result["counts"], "graph": result["graph"], "controls": result["controls"]}, sort_keys=True))
    print("PASS_G20_MULTIHOP_CONJUGATION_FLOOR")


if __name__ == "__main__":
    main()
