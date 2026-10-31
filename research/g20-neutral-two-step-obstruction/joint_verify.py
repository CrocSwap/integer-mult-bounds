"""Two-step G20 census with arbitrary finite paths of retained route edges.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
Combines the indexed scalar domain from worker C and independently developed
all-path accounting from worker D. Retains #5708/#6290/#6305 attribution.
"""
from collections import Counter
from hashlib import sha256
from pathlib import Path
from types import ModuleType
import argparse
import gzip
import json

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
DIRECT_SHA = "b0d62e1faa9aaa7bdde5aac5b55b5d226272461238fa960cc0ad0df0b054bb47"
JOINT_SHA = "1d22c6df716c4065b4155f4f46f9ba1c82b3e6153fbaf5b13f4ff4f29cb33e30"


def need(condition, reason):
    if not condition:
        raise ValueError(reason)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def module(name, filename, expected):
    path = PACKAGE / filename
    raw = path.read_bytes()
    need(sha256(raw).hexdigest() == expected, "implementation bytes: " + filename)
    result = ModuleType(name)
    result.__file__ = str(path)
    exec(compile(raw, str(path), "exec"), result.__dict__)
    return result


def graph_receipt(edges, level, reachable):
    closure = [[a, sorted(reachable[a])] for a in sorted(reachable)]
    return {"edges": len(edges), "frames": len(level),
            "reachable_pairs": sum(map(len, reachable.values())),
            "level_counts": dict(sorted(Counter(level.values()).items())),
            "closure_sha256": sha256(json.dumps(closure, separators=(",", ":")).encode()).hexdigest()}


def branch_audit(primary, floor, word, first, old_branch, graph, base, endpoint):
    edges, level, reachable = graph
    owned, rows, counts, shapes = set(word["owned"]), [], Counter(), Counter()
    candidates = list(primary.candidates(first))
    need(len(candidates) == len(old_branch["outcomes"]), "second-domain cardinality")
    for candidate, old in zip(candidates, old_branch["outcomes"], strict=True):
        left, right, a, b, corrections = candidate
        header = [left, right, a, b, len(corrections)]
        need(header == old[:5], "complete second-domain recipe equality")
        changed = primary.rewrite(first, candidate)
        need(primary.scalar_rows(changed, len(word["start"]), owned) == endpoint,
             "all-column second endpoint")
        bill, missing, requests, paid_new = floor.collapsed_invoice(
            changed, word["start"], word["final"], owned, level, reachable, edges)
        delta = None if missing is not None else floor.signed_delta(bill, base)
        if missing is None:
            sign = floor.sign_certificate(delta)
            need(sign != "zero" or not paid_new, "zero lower bound must have direct paid attainer")
            need(sign != "zero" or (old[5] is None and old[6] == []), "neutral set unchanged")
            counts["neutral" if sign == "zero" else "strict_loss"] += 1
            counts["newly_reachable"] += old[5] is not None
            shapes[tuple(map(tuple, delta))] += 1
        else:
            counts["unreachable"] += 1
            need(old[5] is not None, "lost a formerly direct route")
        counts["candidates"] += 1
        rows.append(header + [missing, delta, sorted(paid_new)])
    return {"first": old_branch["first"], "counts": dict(sorted(counts.items())),
            "shapes": [[shape, count] for shape, count in sorted(shapes.items())], "outcomes": rows}


def census(primary, floor):
    word, records, direct_edges = primary.load_inputs()
    paths = json.loads((ROOT / "research/g20-conjugation-admission/PATHS.json").read_bytes())
    graph = floor.graph(paths)
    edges, level, reachable = graph
    need(edges == direct_edges, "same primitive route table")
    data = gzip.decompress((PACKAGE / "CERTIFICATE.json.gz").read_bytes())
    need(sha256(data).hexdigest() == DIRECT_SHA, "direct certificate mismatch")
    direct = json.loads(data)
    owned = set(word["owned"])
    endpoint = [0 if i in owned else (1 << i) ^ ((1 << (i - 111)) if 111 <= i < 222 else 0)
                for i in range(len(word["start"]))]
    need(primary.scalar_rows(records, len(word["start"]), owned) == endpoint, "source endpoint")
    base, missing = primary.emit(records, word["start"], word["final"], owned, edges)
    need(missing is None and dict(base) == {int(k): v for k, v in direct["base_paid"].items()},
         "direct reference invoice")
    first = primary.identify_first(word, records, edges, base, endpoint)
    need(len(first) == len(direct["branches"]) == 14, "first-domain cardinality")
    branches = []
    for candidate, old_branch in zip(first, direct["branches"], strict=True):
        left, right, a, b, corrections = candidate
        need([left, right, a, b, len(corrections)] == old_branch["first"], "first-domain recipe")
        changed = primary.rewrite(records, candidate)
        branches.append(branch_audit(primary, floor, word, changed, old_branch, graph, base, endpoint))
    totals = Counter()
    for branch in branches:
        totals.update(branch["counts"])
    need(totals == {"candidates": 31719, "unreachable": 28466, "strict_loss": 2956,
                    "neutral": 297, "newly_reachable": 280}, "joint domain and outcomes")
    need(len(edges) == 2369 and len(level) == 636 and sum(map(len, reachable.values())) == 23560,
         "graph coverage")
    return {"schema": "g20-joint-neutral-route-closure/v1", "graph": graph_receipt(*graph),
            "counts": dict(sorted(totals.items())), "branches": branches,
            "direct_certificate_sha256": DIRECT_SHA, "primary_controls": primary.controls(),
            "route_floor_controls": floor.controls()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    expected = None
    if args.output is None:
        expected = gzip.decompress((PACKAGE / "JOINT-CERTIFICATE.json.gz").read_bytes())
        need(sha256(expected).hexdigest() == JOINT_SHA, "joint certificate mismatch")
    primary = module("g20_frozen_indexed_primary", "verify.py",
                     "30e916093afd3f859f26a6e257f66659452999c13d1d3164f1e6d733b297e488")
    floor = module("g20_frozen_route_floor", "route_floor.py",
                   "c807d8aa58fcdaf670639854b556d7b7b64291a4968bda9895133ab84f1023bf")
    result = census(primary, floor)
    payload = canonical(result)
    if args.output:
        need(not args.output.resolve().is_relative_to(ROOT), "output must be outside checkout")
        args.output.write_bytes(payload)
    else:
        need(payload == expected, "complete joint certificate mismatch")
    print(json.dumps({"counts": result["counts"], "graph": result["graph"],
                      "certificate_sha256": sha256(payload).hexdigest()}, sort_keys=True))
    print("PASS_G20_JOINT_ROUTE_CLOSURE candidates=31719 unreachable=28466 strict_loss=2956 neutral=297 new_reachable=280")


if __name__ == "__main__":
    main()
