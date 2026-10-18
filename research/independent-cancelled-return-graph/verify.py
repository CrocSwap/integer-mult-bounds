#!/usr/bin/env python3
"""Source-bound independent audit of PR1563. Default execution is read-only.

Sricharan Vagvala, substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from bisect import bisect_right
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import engine as e

SOURCE_HEAD = "e7d1ebfc3093a704b55c14ea4d10d0d0bdfdd0db"
FIXTURE_HEAD = "407f00df6ca0bf86b455b5640f18ec2f62ee77b9"
PIN_MANIFEST_SHA256 = "350e3f77192d449655c3c4acd069be5078f49107c58a9b3292e01322e1f45ccb"


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def no_duplicates(items):
    answer = {}
    for key, value in items:
        e.require(key not in answer, "duplicate JSON key: " + key)
        answer[key] = value
    return answer


def load_json(path):
    def reject_constant(value):
        raise ValueError("nonfinite JSON: " + value)
    return json.loads(path.read_text(), object_pairs_hook=no_duplicates, parse_constant=reject_constant)


def source_receipt(root=HERE):
    raw = (root / "PREDECESSOR.json").read_bytes()
    e.require(hashlib.sha256(raw).hexdigest() == PIN_MANIFEST_SHA256, "pin manifest drift")
    pins = load_json(root / "PREDECESSOR.json")
    e.require(pins["construction_head"] == SOURCE_HEAD and
              pins["original_fixture_head"] == FIXTURE_HEAD, "exact source heads")
    for pin in pins["files"]:
        data = (root / pin["path"]).read_bytes()
        e.require(hashlib.sha256(data).hexdigest() == pin["sha256"], "source SHA256: " + pin["path"])
        blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        e.require(blob == pin["git_blob"], "source Git blob: " + pin["path"])
    receipt = load_json(root / "sources/pr1563-RESULT.json")
    e.require(receipt["status"] == "PASS_PRECISION_CAPPED_UNIPOTENT_CUTS" and
              receipt["fixture_seed"] == 53 and receipt["predecessor_head"] == FIXTURE_HEAD,
              "source receipt domain")
    return receipt


def check_source_graph(edges, receipt):
    e.require(len(edges) == 1431, "complete interval coverage")
    e.require([(x["a"], x["b"]) for x in edges] ==
              [(a, b) for a in range(53) for b in range(a+1, 54)], "interval inventory")
    e.require(digest(edges) == receipt["edges_sha256"], "source interval graph digest")


def primal_dual(record, edges, readers, m, cancel=True):
    k = len(readers)
    suffix = e.suffix_optimum(edges, k, record["cap"])
    e.require(suffix[0] == record["boundary_price"], "independent suffix optimum")
    prefix = record["distances"]
    e.require(len(prefix) == k+1 and prefix[0] == 0, "source prefix potential")
    for edge in edges:
        a, b = edge["a"], edge["b"]
        if edge["peak"] <= record["cap"] and prefix[a] is not None:
            e.require(prefix[b] is not None and prefix[b] <= prefix[a]+edge["add"]+edge["scale"],
                      "source potential edge inequality")
    lookup = {(x["a"], x["b"]): x for x in edges}
    a = add = scale = peak = 0
    for b in record["cuts"]:
        e.require(type(b) is int and a < b <= k, "witness cut order")
        edge = lookup[a, b]
        e.require(edge["peak"] <= record["cap"], "witness cap")
        add += edge["add"]
        scale += edge["scale"]
        peak = max(peak, edge["peak"])
        a = b
    e.require(a == k and add == record["boundary_add"] and scale == record["boundary_scale"] and
              add+scale == prefix[k] == suffix[0], "complete primal/dual invoice")
    word = e.partition_word(readers, record["cuts"], m, cancel)
    n = 2+4*m
    e.require(e.apply(word, e.identity(n))[0] == e.expected_endpoint(readers, m), "whole dirty endpoint")
    e.require(e.apply(e.undo(word), e.identity(n))[0] == e.expected_endpoint(readers, m, -1),
              "whole literal inverse endpoint")
    report = e.word_report(word, n)
    e.require(canonical(report) == canonical(record["word"]), "whole source word report")
    child_bill = sum(e.bill(e.leaf(r, m))[0] for r in readers)
    e.require(report["add"] == 2*child_bill+4*m+2*add and report["scale"] == 2*scale,
              "all child/copy/return charges")
    e.require(report["peak"] == peak <= record["cap"], "interval-to-full-word peak")
    return suffix


def cap_sweep(edges, receipt):
    thresholds = sorted({x["peak"] for x in edges})
    caps = set(thresholds) | {max(1, x-1) for x in thresholds}
    # Seed 82 deliberately probes both sides of powers 2^8 through 2^14.
    caps |= {2**b + delta for b in range(8, 15) for delta in (-1, 0, 1)}
    source_points = [(x["cap"], x["boundary_price"]) for x in receipt["frontier"]]
    source_caps = [x[0] for x in source_points]
    decisions, frontier, previous = [], [], None
    for cap in sorted(caps):
        cost = e.suffix_optimum(edges, 53, cap)[0]
        index = bisect_right(source_caps, cap)-1
        expected = None if index < 0 else source_points[index][1]
        e.require(cost == expected, "complete cap-decision sweep")
        decisions.append([cap, cost])
        if cap in thresholds and cost is not None and (previous is None or cost < previous):
            frontier.append([cap, cost])
            previous = cost
    e.require(canonical(frontier) == canonical(source_points), "all 35 frontier points")
    return decisions, frontier


def small_partition_control():
    """Complete direct-word check in a new small fixture, independent of the DAG."""
    readers, m, k = e.fixture(8, 2, 82), 2, 8
    edges, _, _ = e.edge_checks(readers, m, rational_finals=False)
    lookup = {(x["a"], x["b"]): x for x in edges}
    records = []
    for mask in range(1 << (k-1)):
        cuts = [i for i in range(1, k) if mask & (1 << (i-1))] + [k]
        word = e.partition_word(readers, cuts, m)
        report = e.word_report(word, 2+4*m)
        e.require(e.apply(word, e.identity(2+4*m))[0] == e.expected_endpoint(readers, m),
                  "small all-dirty endpoint")
        a = boundary = predicted_peak = 0
        for b in cuts:
            edge = lookup[a, b]
            boundary += edge["add"]+edge["scale"]
            predicted_peak = max(predicted_peak, edge["peak"])
            a = b
        e.require(report["peak"] == predicted_peak, "small decomposition peak")
        child_bill = sum(e.bill(e.leaf(r, m))[0] for r in readers)
        e.require(report["operations"] == 2*child_bill+4*m+2*boundary,
                  "small complete invoice")
        records.append([predicted_peak, boundary])
    thresholds = sorted({max(1, peak+d) for peak, _ in records for d in (-1, 0)})
    for cap in thresholds:
        costs = [cost for peak, cost in records if peak <= cap]
        e.require(e.suffix_optimum(edges, k, cap)[0] == (min(costs) if costs else None),
                  "small exhaustive optimum")
    return {"fixture_seed": 82, "children": k, "pairs": m, "partitions": len(records),
            "cap_decisions": len(thresholds), "partition_digest": digest(records)}


def controls(readers, edges, states, receipt):
    rejected = []
    def reject(name, callback):
        try:
            callback()
        except (ValueError, KeyError):
            rejected.append(name)
            return
        raise ValueError("negative control accepted: " + name)
    def distinct(actual, expected, message):
        e.require(actual == expected, message)
    clone = lambda value: json.loads(json.dumps(value))
    used = set()
    for record in receipt["frontier"] + receipt["caps"]:
        a = 0
        for b in record["cuts"]:
            used.add((a, b))
            a = b
    unused = next(x for x in edges if x["fused"] and (x["a"], x["b"]) not in used and x["b"]-x["a"] > 1)
    bad = clone(edges)
    bad[edges.index(unused)]["contexts"][1] += 1
    reject("unused_terminal_edge", lambda: check_source_graph(bad, receipt))
    point = clone(next(x for x in receipt["caps"] if x["cap"] == 4096))
    point["boundary_price"] -= 1
    reject("undercharged_full_cost", lambda: primal_dual(point, edges, readers, 5))
    point = clone(receipt["frontier"][-1])
    point["distances"][-1] += 1
    reject("false_prefix_potential", lambda: primal_dual(point, edges, readers, 5))
    reject("nonintegral_halving", lambda: e.apply([("SCALE", 1, 1, 1, 2)], e.identity(2)))
    reject("illegal_coefficient", lambda: e.apply([("ADD", 0, 1, 2, 1)], e.identity(2)))
    reject("duplicate_cut", lambda: e.partition_word(readers, [1, 1, 53], 5))
    wrong = clone(readers)
    wrong[0][1][0] = 1
    reject("nonintertwining_reader", lambda: e.interval(wrong, 0, 53, 5, True))
    ops = e.interval(readers, 0, 53, 5, True)
    missing_unload = e.transfer(5, 1) + ops + e.undo(ops)
    reject("missing_source_unload", lambda: distinct(e.apply(missing_unload, e.identity(22))[0],
                                                    e.expected_endpoint(readers, 5), "unload endpoint"))
    wrong_inverse = e.transfer(5, 1)+ops+e.transfer(5, -1)+list(reversed(ops))
    reject("reversal_without_inverse", lambda: distinct(e.apply(wrong_inverse, e.identity(22))[0],
                                                       e.expected_endpoint(readers, 5), "inverse endpoint"))
    canonical_midpoint = e.interval(readers, 0, 53, 5, False)
    reject("midpoint_observer", lambda: distinct(e.apply(ops, states["fg"][0])[0],
                                                e.apply(canonical_midpoint, states["fg"][0])[0],
                                                "midpoint observation"))
    middle = e.interval(readers, 20, 36, 5, False)
    correct = e.apply(middle, states["fg"][20])[1]
    stale = e.apply(middle, states["fg"][0])[1]
    reject("fresh_output_context", lambda: distinct(stale, correct, "accumulated output"))
    q = [("ADD", 0, 1, 1, 1)]
    aliased_unload = [("ADD", 1, 0, 1, 1)]
    reject("aliased_unload_commutation", lambda: distinct(e.apply(q+aliased_unload+e.undo(q), e.identity(2))[0],
                                                        e.apply(aliased_unload, e.identity(2))[0],
                                                        "disjoint-register premise"))
    reject("duplicate_json", lambda: json.loads('{"cost":1,"cost":2}', object_pairs_hook=no_duplicates))
    extra = [("SCALE", 1, 1, 2, 1), ("SCALE", 1, 1, 1, 2)]
    reject("endpoint_only_precision", lambda: distinct(e.apply(extra, e.identity(2))[1], 1, "prefix-only fault"))
    return {"rejected": rejected, "unused_terminal_interval": [unused["a"], unused["b"]],
            "stale_context": {"interval": [20, 36], "correct": correct, "stale": stale}}


def build(root=HERE):
    source = source_receipt(root)
    readers = e.fixture()
    edges, states, coverage = e.edge_checks(readers, 5)
    check_source_graph(edges, source)
    decisions, frontier = cap_sweep(edges, source)
    checked_words = set()
    suffix_receipts = []
    for record in source["frontier"]+source["caps"]:
        suffix = primal_dual(record, edges, readers, 5)
        checked_words.add(tuple(record["cuts"]))
        suffix_receipts.append({"cap": record["cap"], "suffix": suffix})
    used_terminal = {cuts[-2] if len(cuts) > 1 else 0 for cuts in checked_words}
    return {"schema_version": 1, "status": "PASS_INDEPENDENT_CANCELLED_RETURN_GRAPH",
            "assignment_seed": 82, "base_commit": "0a201997097b8a89b638f3a2afcb35db4184c8b2",
            "source_head": SOURCE_HEAD, "fixture_head": FIXTURE_HEAD,
            "domain": {"children": 53, "pairs": 5, "coordinates": 22, "fixture_seed": 53,
                       "partitions_represented_by_graph": 2**52, "intervals": len(edges),
                       "terminal_edges": 53, "terminal_edges_absent_from_source_schedules": 53-len(used_terminal)},
            "coverage": {**coverage, "chronological_contexts": sum(map(len, states.values())),
                         "integer_basis_columns": coverage["contextual_executions"]*22,
                         "source_schedule_records": len(source["frontier"])+len(source["caps"]),
                         "distinct_source_words": len(checked_words), "cap_decisions": len(decisions)},
            "edges": edges, "edges_sha256": digest(edges), "frontier": frontier,
            "cap_decisions_sha256": digest(decisions), "suffix_potentials": suffix_receipts,
            "small_exhaustion": small_partition_control(),
            "controls": controls(readers, edges, states, source),
            "scope": "Independent finite audit of the fixed PR1563 graph and complete words; no native/physical, rounding, recursive-cap, kappa or multiplication-theorem claim."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="print a freshly rebuilt certificate")
    args = parser.parse_args()
    try:
        receipt = build()
        if args.emit:
            print(json.dumps(receipt, sort_keys=True, indent=2))
        else:
            expected = load_json(HERE / "CERTIFICATE.json")
            e.require(canonical(receipt) == canonical(expected), "audit certificate mismatch")
            print("PASS_INDEPENDENT_CANCELLED_RETURN_GRAPH intervals=1431 terminal=53 "
                  "contexts=5618 fraction_columns=2332 frontier=35 no_new_kappa")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.exit(1, str(exc)+"\n")


if __name__ == "__main__":
    main()
