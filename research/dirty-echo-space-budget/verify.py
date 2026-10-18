"""Replay the exact space/call certificate and its scoped negative controls."""

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

SOURCE_PINS = {
    628: (
        "0768f97d06c623b8211e651543c66135796b62bf",
        "research/prime-power-cyclic-scan",
        ("dirty.py", "weighted.py", "check.py", "scan.py", "interval_kernel.py", "DIRTY-PROOF.md", "NOTICE.md"),
    ),
    673: (
        "156f259b99723468cfdd2b5d47d0ba894f09bea7",
        "research/cyclic-dirty-commutator-audit",
        ("echo.py", "ECHO-PROOF.md"),
    ),
    689: (
        "0dedef12f05f9a06faf9d4e1c8b1462c0e3bff3a",
        "research/ternary-dirty-composition",
        ("ternary.py", "NOTICE.md"),
    ),
    758: (
        "a164f06263e438ead570b169e5b7103aa45bf228",
        "research/space-capped-dirty-echo",
        ("planner.py", "NOTICE.md"),
    ),
}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate_sources():
    raw = (ROOT / "SOURCES.json").read_bytes()
    manifest = json.loads(raw)
    need(manifest["base_commit"] == "66849e1475c930fd7732b1a0067ffee7e1e95f60", "base commit changed")
    expected = {
        f"vendor/pr{pr}/{name}": (pr, commit, f"{directory}/{name}")
        for pr, (commit, directory, names) in SOURCE_PINS.items()
        for name in names
    }
    seen = set()
    for record in manifest["files"]:
        name = record["local_path"]
        need(name in expected and name not in seen, "unexpected or repeated source path")
        seen.add(name)
        need((record["source_pr"], record["source_commit"], record["source_path"]) == expected[name],
             "source provenance changed: " + name)
        actual = hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
        need(actual == record["sha256"], "source hash mismatch: " + name)
    need(seen == set(expected), "source inventory is incomplete")
    return {"files": len(seen), "manifest_sha256": hashlib.sha256(raw).hexdigest(),
            "base_commit": manifest["base_commit"],
            "heads": {str(pr): pin[0] for pr, pin in SOURCE_PINS.items()}}


def load_module(name, relative_path):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative_path)
    need(spec is not None and spec.loader is not None, "cannot load " + relative_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def tree_text(plan):
    if not plan.children:
        return "."
    return "(" + ",".join(tree_text(child) for child in plan.children) + ")"


def compare_baselines(table):
    from schedule import multiplicities, word

    original = load_module("space_budget_pr673", "vendor/pr673/echo.py")
    ternary = load_module("space_budget_pr689", "vendor/pr689/ternary.py")
    count = 50
    comparisons = []
    for budget in (6, 7, 8):
        candidates = []
        for fanout in range(2, count + 1):
            scratch, calls = original.resources(count, fanout)
            if scratch <= budget:
                candidates.append((calls, scratch, "PR673", fanout))
        calls, scratch = ternary.resources(count)
        if scratch <= budget:
            candidates.append((calls, scratch, "PR689", 3))
        calls, scratch, source, fanout = min(candidates)
        if source == "PR673":
            baseline_word = tuple(original.instructions(0, count, 0, 1, 2, fanout))
            baseline_peak = max(max(src, dst) for src, dst, _, _ in baseline_word) - 1
        else:
            baseline_word = tuple(ternary.word(count))
            baseline_peak = max(max(src, dst) for _, src, dst, _ in baseline_word) - 1
        need(len(baseline_word) == calls and baseline_peak == scratch, "baseline word/resource mismatch")
        plan = table[budget][count]
        counts = multiplicities(plan)
        expanded = tuple(word(plan))
        need(counts == [sum(command[0] == index for command in expanded) for index in range(count)],
             "public multiplicities disagree with the actual word")
        need(plan.calls <= calls and sum(counts) == plan.calls, "invalid cost comparison")
        comparisons.append({
            "factors": count, "scratch_budget": budget, "scratch_used": plan.scratch,
            "baseline_source": source, "baseline_fanout": fanout,
            "baseline_scratch": scratch, "baseline_calls": calls,
            "minimum_calls": plan.calls, "saved_calls": calls - plan.calls,
            "root_partition": [child.factors for child in plan.children],
            "tree": tree_text(plan), "factor_multiplicities": counts,
            "all_feasible_pinned_baselines": [list(candidate) for candidate in sorted(candidates)],
        })
    need([row["baseline_calls"] for row in comparisons] == [2752, 1568, 1568], "baseline changed")
    return comparisons


def compare_concurrent(table):
    from checks import polynomial_execute, polynomial_expected, polynomial_initial

    concurrent = load_module("space_budget_pr758", "vendor/pr758/planner.py")
    domain = [(15, budget) for budget in range(4, 9)] + [(27, 6)]
    domain += [(50, budget) for budget in (6, 7, 8)]
    records = []
    for count, budget in domain:
        result = concurrent.optimize([1] * count, budget)
        plan = table[budget][count]
        need(result["price"] == result["calls"] == plan.calls, "concurrent uniform optimum differs")
        forward = tuple(concurrent.word(result["tree"]))
        inverse = tuple(concurrent.word(result["tree"], -1))
        need(len(forward) == plan.calls, "concurrent word count differs")
        need(result["scratch"] <= budget, "concurrent word exceeds scratch budget")
        state = polynomial_initial(result["scratch"])
        polynomial_execute(state, forward)
        need(state == polynomial_expected(count, result["scratch"]), "concurrent ordered product failed")
        polynomial_execute(state, inverse)
        need(state == polynomial_initial(result["scratch"]), "concurrent inverse failed")
        records.append({"factors": count, "scratch_budget": budget,
                        "calls": result["calls"], "scratch_used": result["scratch"]})
    return {"source_pr": 758, "source_commit": SOURCE_PINS[758][0], "cases": records,
            "scope": "Uniform-price agreement and exact symbolic forward/inverse words only; "
                     "not review of the full PR or its weighted and numerical claims."}


def certificate():
    sources = authenticate_sources()
    from checks import run_checks
    from rounded_check import run_rounded_checks
    from schedule import plan_table

    table = plan_table(64, 8)
    return {
        "format": "ordered-dirty-echo-space-budget-v1",
        "status": "passed",
        "assignment_seed": 50,
        "sources": sources,
        "domain": {"factors": [1, 64], "scratch_budget": [0, 8],
                   "coverage": "all 576 cells; null denotes infeasibility",
                   "tree_encoding": "a leaf is '.', an internal node is its comma-separated children in parentheses",
                   "objective": "minimum uniform leaf calls in static ordered all-dirty echo trees"},
        "costs_by_budget": [[None if plan is None else plan.calls for plan in row[1:]] for row in table],
        "main_witnesses": compare_baselines(table),
        "concurrent_comparison": compare_concurrent(table),
        "independent_checks": run_checks(),
        "rounded_execution": run_rounded_checks(),
        "scope": "Exact grammar-specific cost certificate and finite implementation evidence. "
                 "The all-size lower-bound and attainment statements use the written induction. "
                 "No new kappa, common-label supplier, practical runtime or full multiplication proof.",
    }


def main():
    need(sys.version_info >= (3, 11), "Python 3.11 or newer is required by the pinned rounded-leaf verifier")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, help="write recomputed evidence to a new file")
    args = parser.parse_args()
    result = certificate()
    if args.write is not None:
        with args.write.open("x") as output:
            output.write(json.dumps(result, indent=2) + "\n")
    else:
        expected = json.loads((ROOT / "EXPECTED.json").read_text())
        actual_json = json.dumps(result, sort_keys=True, separators=(",", ":"), allow_nan=False)
        expected_json = json.dumps(expected, sort_keys=True, separators=(",", ":"), allow_nan=False)
        need(actual_json == expected_json, "recomputed certificate differs from EXPECTED.json")
    print("PASS_DIRTY_ECHO_SPACE_BUDGET: n=50, arrays=6, leaves=2752->2304")


if __name__ == "__main__":
    main()
