#!/usr/bin/env python3
"""Audit retained set/word pruning contracts; no seven-label enumeration.

Prepared for commdata2338 with substantial OpenAI Codex assistance.
Apache-2.0. The authenticated predecessor engines retain their authorship.
"""

import argparse
import ast
from collections import Counter
from hashlib import sha256
from itertools import combinations
import json
from math import comb
from pathlib import Path
import types


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OLD = "research/universal-f7-singleton-seedb859517b/engine.py"
COPIES = (
    OLD,
    "research/universal-f7-singleton-l20-seed06704c39/engine.py",
    "research/f7-17point-cover-audit-seedcfa215c2/vendor/pr2542_engine.py",
)
SET_MODULE = "research/f7-17point-cover-audit-seedcfa215c2/cover17.py"
CALLERS = (
    "research/universal-f7-singleton-seedb859517b/search.py",
    "research/universal-f7-singleton-seedb859517b/verify.py",
    "research/universal-f7-singleton-seedb859517b/test_engine.py",
    "research/universal-f7-singleton-l20-seed06704c39/verify.py",
    "research/universal-f7-singleton-l20-seed06704c39/census20.py",
    "research/f7-17point-cover-audit-seedcfa215c2/verify.py",
)
MARKER = "PASS_F7_SET_WORD_BOUNDARY"


class AuditFailure(Exception):
    """An explicit failure, including when Python runs with -O."""


def require(condition, message):
    if not condition:
        raise AuditFailure(message)


def source_bytes():
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    result = {}
    for row in manifest["files"]:
        if row["usage"] != "input":
            continue
        data = (ROOT / row["path"]).read_bytes()
        require(sha256(data).hexdigest() == row["sha256"],
                "source hash mismatch: " + row["path"])
        result[row["path"]] = data
    return result


def load_bytes(data, path):
    # Compile authenticated source directly, without reading a .pyc or
    # changing a frozen file. Both loaded modules use only the stdlib.
    module = types.ModuleType("audited_subject")
    module.__file__ = str(ROOT / path)
    exec(compile(data, module.__file__, "exec"), module.__dict__)
    return module


def prefixes(word):
    points = [0]
    for label in word:
        points.append(points[-1] ^ (1 << label))
    return points


def support(points):
    return {x ^ y for x in points for y in points}


def degrees(points):
    # Pairwise Hamming distances, unlike the subject's coordinate flips.
    return {x: sum((x ^ y).bit_count() == 1 for y in points) for x in points}


def split_points(points, weight=False):
    return tuple(tuple(x for x in sorted(points)
                       if ((x.bit_count() if weight else x) & 1) == parity)
                 for parity in (0, 1))


def within_excess(parts):
    return sum(comb(len(part), 2) - len({x ^ y for x, y in combinations(part, 2)})
               for part in parts)


def canonical_results(rows, n, split):
    result = []
    for even, odd in rows:
        points = tuple(sorted(even + odd))
        require(len(set(points)) == len(points), "duplicate point in result")
        require(0 in even, "normalization lost zero")
        require((even, odd) == split_points(points), "wrong bit-0 partition")
        require((len(even), len(odd)) == split, "wrong actual split")
        require(all(0 <= x < 1 << n for x in points), "point outside domain")
        result.append(points)
    require(len(result) == len(set(result)), "duplicate returned cover")
    return set(result)


def point_set_hash(point_sets):
    payload = json.dumps(sorted(point_sets), separators=(",", ":")).encode()
    return sha256(payload).hexdigest()


def subset_oracle(n):
    """Every zero-containing set, without capacity/collision/degree pruning."""
    size = 1 << n
    covers, filtered = {}, {}
    for mask in range(1 << (size - 1)):
        points = (0,) + tuple(x for x in range(1, size) if mask >> (x - 1) & 1)
        if len(support(points)) != size:
            continue
        split = tuple(map(len, split_points(points)))
        covers.setdefault(split, set()).add(points)
        if min(degrees(points).values()) >= 2:
            filtered.setdefault(split, set()).add(points)
    return covers, filtered


def forbidden_word_census(*args, **kwargs):
    raise AuditFailure("set-level check reached the word census")


def exhaustive_sets(subject):
    subject.cyclic_census = forbidden_word_census
    receipt = []
    for n in range(1, 5):
        oracle = subset_oracle(n)
        for split in oracle[0]:
            require(split in subject.set_level_splits(n, sum(split)),
                    f"set-level split selector loses a cover {(n, split)}")
        cases = []
        for s in range(1, (1 << (n - 1)) + 1):
            for t in range((1 << (n - 1)) + 1):
                for flag in (False, True):
                    expected = oracle[int(flag)].get((s, t), set())
                    actual = canonical_results(
                        subject.joint_covers(n, [(s, t)], require_min_degree=flag),
                        n, (s, t))
                    require(actual == expected, f"set disagreement {(n, s, t, flag)}")
                    cases.append({"split": [s, t], "minimum_degree_two": flag,
                                  "covers": len(actual),
                                  "sets_sha256": point_set_hash(actual)})
        receipt.append({"n": n, "all_sets": 1 << ((1 << n) - 1),
                        "covers": sum(map(len, oracle[0].values())),
                        "degree_two_covers": sum(map(len, oracle[1].values())),
                        "cases": cases})
    return receipt


def fixed_witnesses(subject):
    word = tuple(map(int, "01021323"))
    trace = prefixes(word)
    points = tuple(sorted(set(trace)))
    require(trace == [0, 1, 3, 2, 6, 4, 12, 8, 0], "wrong old counterexample")
    require(len(support(points)) == 16 and len(points) == 8, "not a simple cover")
    bit_parts, weight_parts = split_points(points), split_points(points, True)
    require(tuple(map(len, bit_parts)) == (6, 2), "wrong bit split")
    require(tuple(map(len, weight_parts)) == (4, 4), "wrong weight split")
    require(within_excess(bit_parts) == 8, "wrong bit collision excess")
    require(within_excess(weight_parts) == 0, "wrong weight collision excess")
    old_control = {}
    for budget in (None, 5, 9):
        row = subject.cyclic_census(4, 8, budget=budget, simple=True,
                                   prefix=word, max_nodes=100)
        old_control[str(budget)] = {k: row[k] for k in ("nodes", "leaves", "hits")}
        require(row["hits"] == (0 if budget == 5 else 1), "old prune control failed")
    right = canonical_results(subject.joint_covers(4, [(6, 2)]), 4, (6, 2))
    wrong = canonical_results(subject.joint_covers(4, [(4, 4)]), 4, (4, 4))
    require(points in right and points not in wrong, "actual-size boundary failed")

    short = tuple(map(int, "010122"))
    short_trace = prefixes(short)
    short_set = tuple(sorted(set(short_trace)))
    require(short_trace[-1] == 0 and Counter(short) == {0: 2, 1: 2, 2: 2},
            "three-label witness does not restore")
    require(len(support(short_set)) == 8, "three-label witness does not cover")
    require(min(degrees(short_set).values()) == 1, "degree-one witness lost")
    unfiltered = canonical_results(subject.joint_covers(3, [(3, 2)]), 3, (3, 2))
    filtered = canonical_results(subject.joint_covers(3, [(3, 2)], True), 3, (3, 2))
    require(short_set in unfiltered and not filtered, "degree-filter counterexample failed")
    require(len(unfiltered) == 18, "three-label split control changed")

    # T puts weight parity in output bit 0. It changes the singleton alphabet.
    transform = lambda x: (x & ~1) | (x.bit_count() & 1)
    moved = tuple(sorted(map(transform, points)))
    require(all(transform(transform(x)) == x for x in range(16)), "T not invertible")
    require(all(transform(x ^ y) == transform(x) ^ transform(y)
                for x in range(16) for y in range(16)), "T not linear")
    require(len(support(moved)) == 16, "linear map lost coverage")
    require(min(degrees(points).values()) == 2 and degrees(moved)[12] == 0,
            "adjacency transport counterexample failed")
    require(moved in wrong, "transformed set not at bit split (4,4)")
    moved_filtered = canonical_results(subject.joint_covers(4, [(4, 4)], True), 4, (4, 4))
    require(moved not in moved_filtered, "degree filter should reject isolated point")
    return {"old_parity": {"word": "01021323", "prefixes": trace,
                           "bit0_split": [6, 2], "weight_split": [4, 4],
                           "bit0_excess": 8, "weight_excess": 0,
                           "wrong_budget": 5, "actual_bit0_budget": 9,
                           "actual_old_engine": old_control},
            "degree_counterexample": {"word": "010122", "prefixes": short_trace,
                                      "points": short_set, "coverage": 8,
                                      "length": 6, "minimum_restored_length": 6,
                                      "minimum_degree": 1, "split": [3, 2],
                                      "unfiltered_covers": 18, "filtered_covers": 0},
            "linear_transport": {"points": points, "transformed": moved,
                                 "degrees_before": sorted(degrees(points).values()),
                                 "degrees_after": sorted(degrees(moved).values()),
                                 "isolated_vertex": 12}}


def source_impact(sources):
    calls = []
    for path in CALLERS:
        for node in ast.walk(ast.parse(sources[path])):
            if not isinstance(node, ast.Call):
                continue
            name = node.func.id if isinstance(node.func, ast.Name) else getattr(node.func, "attr", "")
            budgeted = name == "cyclic_census" and any(k.arg == "budget" for k in node.keywords)
            if name == "joint_covers" or budgeted:
                if name == "joint_covers":
                    require(len(node.args) == 2 and not node.keywords,
                            "retained caller enables a new filter or argument")
                calls.append({"path": path, "line": node.lineno,
                              "kind": "set_actual_sizes" if name == "joint_covers" else "invalid_word_budget",
                              "call": ast.unparse(node)})
    require(sum(c["kind"] == "set_actual_sizes" for c in calls) == 4, "set caller inventory changed")
    require(sum(c["kind"] == "invalid_word_budget" for c in calls) == 6, "word caller inventory changed")
    imports = {}
    for path in (SET_MODULE, "research/f7-17point-cover-audit-seedcfa215c2/search17.py"):
        names = []
        for node in ast.walk(ast.parse(sources[path])):
            if isinstance(node, ast.Import):
                names.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                names.append(node.module)
        require(set(names) <= {"functools", "json", "sys", "time", "pathlib"},
                "new non-stdlib set-module dependency")
        imports[path] = sorted(names)
    cover = load_bytes(sources[SET_MODULE], SET_MODULE)
    row_counts = {}
    for s, t in ((9, 8), (8, 9), (10, 7), (7, 10), (11, 6), (6, 11)):
        rows = cover.sharp_rows(7, s, t)
        lo, hi = ((3, 0) if s == 10 else (0, 3) if t == 10
                  else (5, 0) if s == 11 else (0, 5) if t == 11 else (0, 0))
        survivors = cover.surviving_rows(7, s, t, lo, hi)["rows"]
        require(len(survivors) == (2 if 11 in (s, t) else 0), "conditional set rows changed")
        row_counts[f"{s},{t}"] = {"unfiltered_rows": len(rows["rows"]),
                                  "assumed_excess_floors": [lo, hi],
                                  "conditional_survivors": survivors}
    native_path = "research/universal-f7-singleton-l20-census-complete-seedfd938f30/f7_census.c"
    native_text = sources[native_path].decode()
    anchors = ("#define BUDGET 27", "if (nq & 1) {", "if (coll + newcoll > BUDGET) continue;")
    native_rule = {}
    for anchor in anchors:
        require(anchor in native_text, "native word-rule anchor changed")
        native_rule[anchor] = native_text[:native_text.index(anchor)].count("\n") + 1
    return {"scope": "six pinned Python caller files plus the PR2691 native rule; not every repository call site",
            "calls": sorted(calls, key=lambda c: (c["path"], c["line"])),
            "native_word_rule": {"path": native_path, "anchors": native_rule},
            "set_module_imports": imports,
            "conditional_rows_without_word_census": row_counts,
            "large_sidon_floor_censuses_replayed": False,
            "corrected_n7_word_censuses_replayed": False}


def controls(data):
    subject = load_bytes(data, OLD)
    try:
        subject.joint_covers(3, [(3, 2)], max_nodes=1)
    except OverflowError:
        pass
    else:
        raise AuditFailure("node cap was accepted as a complete result")
    # Mutate only the in-memory subject; frozen inputs remain unchanged.
    old = b"budget = A + B - even_nonzero"
    new = b"budget = 2 * (((s + t) // 2) * (((s + t) // 2) - 1) // 2) - even_nonzero"
    require(data.count(old) == 1, "balanced-budget mutation anchor changed")
    mutant = load_bytes(data.replace(old, new), OLD)
    points = tuple(sorted(set(prefixes(tuple(map(int, "01021323"))))))
    returned = canonical_results(mutant.joint_covers(4, [(6, 2)]), 4, (6, 2))
    require(points not in returned, "balanced-size mutant survived witness")
    return {"cap_raises": True, "balanced_size_mutant_rejected": True,
            "partition_misinterpretation_rejected": True,
            "degree_filter_counterexample_detected": True,
            "linear_map_adjacency_loss_detected": True}


def compute():
    sources = source_bytes()
    require(all(sources[path] == sources[OLD] for path in COPIES), "old copies differ")
    subject = load_bytes(sources[OLD], OLD)
    witnesses = fixed_witnesses(subject)
    receipt = exhaustive_sets(subject)
    result = {"schema_version": 1, "kind": "scoped_source_audit_and_finite_certificate",
              "subjects": {p: sha256(sources[p]).hexdigest() for p in COPIES},
              "all_sets": sum(r["all_sets"] for r in receipt),
              "exact_domain_comparisons": sum(len(r["cases"]) for r in receipt),
              "small_domain": receipt, "witnesses": witnesses,
              "source_impact": source_impact(sources),
              "controls": controls(sources[OLD])}
    require(result["all_sets"] == 32906 and result["exact_domain_comparisons"] == 200,
            "finite domain coverage changed")
    return result


def compare_receipt(actual, expected):
    # JSON normalizes tuple/list representation; compare every field.
    require(json.loads(json.dumps(actual)) == expected, "receipt mismatch")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="print recomputed receipt; write nothing")
    args = parser.parse_args()
    result = compute()
    if args.emit:
        print(json.dumps(result, indent=2, sort_keys=True))
        return
    compare_receipt(result, json.loads((HERE / "RESULT.json").read_text()))
    print(f"{MARKER} sets=32906 comparisons=200 degree_counterexample=010122 no_new_kappa")


if __name__ == "__main__":
    main()
