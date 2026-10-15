"""Exact, read-only verification of a ten-contact P104 capture obstruction.

Standard library only. No producer, scheduler, SMT solver or native compiler is
imported. The written first-contact proof is in README.md. Two finite engines
independently count legal orders: cap-membership signatures and actual subspaces.
Prepared for commdata2338 with substantial OpenAI Codex assistance. Apache-2.0.
"""

import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction
from functools import lru_cache
import hashlib
import json
from pathlib import Path


PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
WITNESS = "research/p104-native-channel/inputs/LOWRANK-WITNESS.json"
WITNESS_SHA256 = "0f541bef7f19fdeffd67157684e9f03d785f42c89973632f508fc1a0452b580e"
CORE_IDS = (631, 745, 799, 807, 945, 1154, 1160, 1267)
ROOM = (32, 196)
FULL = frozenset(range(512))


def need(condition, message):
    if not condition:
        raise ValueError(message)


def strict_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            need(key not in result, "duplicate JSON key: " + key)
            result[key] = value
        return result

    def nonfinite(value):
        raise ValueError("nonfinite JSON value: " + value)

    return json.loads(raw, object_pairs_hook=pairs, parse_constant=nonfinite)


def canonical(value):
    # Comparing serialized JSON also distinguishes True from 1.
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def basis(vectors):
    """Independent binary row reduction, using highest-bit pivots."""
    rows = {}
    for value in vectors:
        need(type(value) is int and 0 <= value < 512, "invalid frame vector")
        for pivot in sorted(rows, reverse=True):
            if value >> pivot & 1:
                value ^= rows[pivot]
        if value:
            pivot = value.bit_length() - 1
            for old in rows:
                if rows[old] >> pivot & 1:
                    rows[old] ^= value
            rows[pivot] = value
    return tuple(rows[p] for p in sorted(rows, reverse=True))


def contains(rows, value):
    for row in rows:
        if value >> (row.bit_length() - 1) & 1:
            value ^= row
    return value == 0


def span(vectors):
    """Independent explicit-vector implementation; no row reduction."""
    result = {0}
    for value in vectors:
        result |= {x ^ value for x in tuple(result)}
    return frozenset(result)


def join(left, right):
    return frozenset(x ^ y for x in left for y in right)


def dimension(space):
    size = len(space)
    need(size > 0 and size & (size - 1) == 0, "not a power-of-two space")
    return size.bit_length() - 1


def extract(witness):
    program = witness["program"]
    need(len(program) == 4058, "wrong source program length")
    queries = {}
    for index, event in enumerate(program):
        if (event[0] == "add" and event[1].startswith("Q")
                and event[2].startswith("G") and Fraction(event[3]) == 1):
            need(event[2] not in queries, "duplicate positive G query")
            queries[event[2]] = {"event_id": index, "query": event[1],
                                 "frame": event[4]}
    need(len(queries) == 32, "wrong query-cap inventory")
    first_query = min(q["event_id"] for q in queries.values())
    captures = []
    for index, event in enumerate(program[:first_query]):
        if event[0] == "add" and event[1].startswith("G") and event[2].startswith("X"):
            captures.append({"event_id": index, "helper": event[1],
                             "source": event[2], "coefficient": str(Fraction(event[3]))})
    need(len(captures) == 416, "wrong original capture inventory")
    by_id = {e["event_id"]: e for e in captures}
    core = [by_id[i] for i in CORE_IDS]
    core += [{"event_id": "carrier-X2", "helper": "B0", "source": "X2", "coefficient": "1"},
             {"event_id": "carrier-X4", "helper": "B0", "source": "X4", "coefficient": "1"}]
    names = sorted({e[k] for e in core for k in ("helper", "source")})
    helpers = sorted({e["helper"] for e in core})
    initial = {v: span(witness["initial_frames"].get(v, [])) for v in names}
    cap_rows = {g: queries[g]["frame"] if g != "B0" else list(ROOM) for g in helpers}
    caps = {g: span(rows) for g, rows in cap_rows.items()}
    for g in helpers:
        need(initial[g] == frozenset({0}), "helper must start in frame zero")
    return core, names, helpers, initial, caps, cap_rows, queries, captures


def check_first_contact_premises(core, helpers, initial, caps):
    """Check the finite hypotheses of the written injection argument."""
    sources = sorted({e["source"] for e in core})
    pairs = []
    for source in sources:
        neighbors = [e["helper"] for e in core if e["source"] == source]
        need(len(neighbors) == 2 and len(set(neighbors)) == 2,
             "each source must have two distinct required contacts")
        need(len(initial[source]) == 2, "source must start in a nonzero line")
        allowed = [h for h in helpers if initial[source] <= caps[h]]
        need(sorted(neighbors) == allowed, "a nonincident cap admits a source label")
        pairs.append(tuple(sorted(neighbors)))
    need(len(set(pairs)) == len(pairs), "two sources use the same helper pair")
    need(len(sources) > len(helpers), "no first-contact pigeonhole deficit")
    return {"sources": len(sources), "helpers": len(helpers), "deficit": len(sources) - len(helpers)}


def signature_census(core, names, helpers, initial, caps):
    """Count every legal permutation via exact cap-membership signatures."""
    width = len(helpers)
    mask = (1 << width) - 1
    index = {v: i for i, v in enumerate(names)}
    edges = [(index[e["helper"]], index[e["source"]]) for e in core]
    forbidden = [1 << helpers.index(v) if v in helpers else 0 for v in names]
    initial_state = sum(sum((not initial[v] <= caps[h]) << k for k, h in enumerate(helpers))
                        << (width * i) for i, v in enumerate(names))
    rejected = 0

    @lru_cache(None)
    def visit(remaining, state):
        nonlocal rejected
        if not remaining:
            return 1, ()
        count, example = 0, ()
        for i, (a, b) in enumerate(edges):
            if not remaining >> i & 1:
                continue
            merged = (state >> (width * a) & mask) | (state >> (width * b) & mask)
            if merged & (forbidden[a] | forbidden[b]):
                rejected += 1
                continue
            updated = state & ~((mask << (width * a)) | (mask << (width * b)))
            updated |= (merged << (width * a)) | (merged << (width * b))
            ways, tail = visit(remaining ^ (1 << i), updated)
            count += ways
            if ways and not example:
                example = (i,) + tail
        return count, example

    count, example = visit((1 << len(core)) - 1, initial_state)
    return {"legal_orders": count, "states": visit.cache_info().currsize,
            "rejected_moves": rejected,
            "example": [core[i]["event_id"] for i in example]}


def subspace_census(core, names, initial, caps):
    """Second implementation: actual sets of vectors, with no signature code."""
    index = {name: i for i, name in enumerate(names)}
    endpoints = [(index[e["helper"]], index[e["source"]]) for e in core]

    @lru_cache(None)
    def count(todo, frames):
        if not todo:
            return 1
        total = 0
        for event in todo:
            a, b = endpoints[event]
            common = join(frames[a], frames[b])
            if any(names[v] in caps and not common <= caps[names[v]] for v in (a, b)):
                continue
            after = list(frames)
            after[a] = after[b] = common
            total += count(tuple(i for i in todo if i != event), tuple(after))
        return total

    answer = count(tuple(range(len(core))), tuple(initial[v] for v in names))
    return {"legal_orders": answer, "states": count.cache_info().currsize}


def replay_order(core, order, initial, caps):
    need(len(order) == len(core) and Counter(order) == Counter(e["event_id"] for e in core),
         "order omits or repeats a required contact")
    by_id = {e["event_id"]: e for e in core}
    frames = dict(initial)
    for event_id in order:
        event = by_id[event_id]
        a, b = event["helper"], event["source"]
        common = join(frames[a], frames[b])
        need(common <= caps.get(a, FULL) and common <= caps.get(b, FULL),
             "contact exceeds its fixed cap")
        frames[a] = frames[b] = common
    return frames


def must_reject(function):
    try:
        function()
    except ValueError:
        return
    raise ValueError("a rejection control was accepted")


def build(witness):
    core, names, helpers, initial, caps, cap_rows, queries, captures = extract(witness)
    premise = check_first_contact_premises(core, helpers, initial, caps)
    sources = sorted({e["source"] for e in core})
    membership = {}
    for source in sources:
        label = next(x for x in initial[source] if x)
        membership[source] = {h: contains(basis(cap_rows[h]), label) for h in helpers}
        need(all(membership[source][h] == (label in caps[h]) for h in helpers),
             "row-reduction / explicit-span membership disagreement")
    fast = signature_census(core, names, helpers, initial, caps)
    exact = subspace_census(core, names, initial, caps)
    need(fast["legal_orders"] == exact["legal_orders"] == 0, "core is feasible")
    deletions = []
    for i, omitted in enumerate(core):
        reduced = core[:i] + core[i + 1:]
        a = signature_census(reduced, names, helpers, initial, caps)
        b = subspace_census(reduced, names, initial, caps)
        need(a["legal_orders"] == b["legal_orders"] > 0, "deletion control failed")
        replay_order(reduced, a["example"], initial, caps)
        must_reject(lambda: check_first_contact_premises(reduced, helpers, initial, caps))
        deletions.append({"omitted": omitted["event_id"], "signature": a, "subspace": b})

    # Every original capture remains possible without the added carrier.
    all_initial = {v: span(rows) for v, rows in witness["initial_frames"].items()}
    all_caps = {g: span(q["frame"]) for g, q in queries.items()}
    baseline = replay_order(captures, [e["event_id"] for e in captures], all_initial, all_caps)
    baseline_summary = {"captures": len(captures), "helpers": len(all_caps),
                        "final_G_dimensions": dict(sorted((g, dimension(baseline[g])) for g in all_caps))}

    relaxed = []
    for helper in ("G1", "B0"):
        enlarged = dict(caps)
        enlarged[helper] = FULL
        must_reject(lambda: check_first_contact_premises(core, helpers, initial, enlarged))
        a = signature_census(core, names, helpers, initial, enlarged)
        b = subspace_census(core, names, initial, enlarged)
        need(a["legal_orders"] == b["legal_orders"] > 0, "relaxed-cap control failed")
        replay_order(core, a["example"], initial, enlarged)
        relaxed.append({"helper": helper, "legal_orders": a["legal_orders"], "example": a["example"]})

    wrong_initial = dict(initial)
    wrong_initial["X4"] = initial["X2"]
    must_reject(lambda: check_first_contact_premises(core, helpers, wrong_initial, caps))
    must_reject(lambda: replay_order(core, [e["event_id"] for e in core][:-1], initial, caps))
    return {"schema_version": 1, "source_sha256": WITNESS_SHA256,
            "room": list(ROOM), "contacts": core,
            "source_labels": {v: sorted(initial[v] - {0}) for v in sources},
            "helper_caps": cap_rows,
            "query_bindings": {g: queries[g] for g in helpers if g != "B0"},
            "membership": membership, "first_contact_premises": premise,
            "signature_census": fast, "subspace_census": exact,
            "single_contact_deletions": deletions,
            "original_capture_control": baseline_summary,
            "relaxed_cap_controls": relaxed,
            "rejected_controls": ["ten_single_contact_deletions_in_proof_checker",
                                  "G1_cap_enlargement_in_proof_checker",
                                  "B0_cap_enlargement_in_proof_checker",
                                  "wrong_initial_source_label", "omitted_contact_in_order",
                                  "changed_coefficient_in_certificate", "changed_count_in_certificate",
                                  "boolean_for_integer_in_certificate", "duplicate_JSON_key"]}


def compare(expected, supplied):
    need(canonical(expected) == canonical(supplied), "certificate differs from exact reconstruction")


def certificate_controls(expected):
    wrong = deepcopy(expected)
    wrong["contacts"][0]["coefficient"] = "-2"
    must_reject(lambda: compare(expected, wrong))
    wrong = deepcopy(expected)
    wrong["signature_census"]["legal_orders"] = 1
    must_reject(lambda: compare(expected, wrong))
    wrong = deepcopy(expected)
    wrong["first_contact_premises"]["deficit"] = True
    must_reject(lambda: compare(expected, wrong))
    must_reject(lambda: strict_json('{"a": 0, "a": 1}'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--certificate", type=Path, default=PACKAGE / "CERTIFICATE.json")
    parser.add_argument("--write-certificate", type=Path,
                        help="write the exact reconstruction exclusively to a new file")
    args = parser.parse_args()
    raw = (ROOT / WITNESS).read_bytes()
    need(hashlib.sha256(raw).hexdigest() == WITNESS_SHA256, "pinned witness changed")
    expected = build(strict_json(raw))
    certificate_controls(expected)
    if args.write_certificate:
        with args.write_certificate.open("x") as handle:
            handle.write(json.dumps(expected, sort_keys=True, indent=2) + "\n")
    else:
        compare(expected, strict_json(args.certificate.read_bytes()))
    print("PASS_P104_CARRIER_CAPTURE_ORDER contacts=10 sources=5 helpers=4 "
          "legal_orders=0 deletion_controls=10 original_captures=416 no_new_kappa")


if __name__ == "__main__":
    main()
