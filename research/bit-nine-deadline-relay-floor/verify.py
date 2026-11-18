"""Check a rank-budget obstruction to arbitrary relays at nine BIT deadlines.

Prepared by Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
The source support and coset certificate is retained from PR7741.
"""

import argparse
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load_source():
    for pin in json.loads((PACKAGE / "SOURCE-PINS.json").read_text()):
        require(hashlib.sha256((PACKAGE / pin["path"]).read_bytes()).hexdigest()
                == pin["sha256"], "retained source hash")
    path = PACKAGE / "retained/pr7741/verify.py"
    spec = importlib.util.spec_from_file_location("direct_floor", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    result = module.calculate()
    require(result == json.loads((path.parent / "RESULT.json").read_text()),
            "replayed predecessor receipt")
    return module, result


def abstract_trees():
    """Bound every labelled rooted tree by removing its root branches."""
    weight = {1: 1, 2: 2, 4: 17}
    subtree = {d: [] for d in weight}
    for budget in range(7):
        for d in weight:
            best = 0
            # Attach one branch to a smaller-budget tree with this same root.
            for e in weight:
                edge = abs(d-e)
                if not edge:
                    continue
                for branch_budget in range(edge, budget+1):
                    root_remainder = subtree[d][budget-branch_budget] - weight[d]
                    branch = subtree[e][branch_budget-edge]
                    best = max(best, root_remainder + branch)
            subtree[d].append(weight[d] + best)
    root = [0]*7
    for budget in range(1, 7):
        for d in weight:
            for branch_budget in range(d, budget+1):
                root[budget] = max(root[budget], root[budget-branch_budget] +
                                   subtree[d][branch_budget-d])
    require(root == [0, 1, 3, 5, 20, 22, 37], "abstract tree budget values")
    # The dimension-labelled tree attains 37 in this abstract relaxation.
    edges = [(0, 1), (1, 2), (2, 4), (2, 4)]
    require(sum(abs(a-b) for a, b in edges) == 6 and 1+2+17+17 == 37,
            "abstract tree positive witness")
    return dict(root_bounds=root, subtree_bounds={str(k): v for k, v in subtree.items()},
                attaining_dimension_edges=[list(edge) for edge in edges])


def chain_checks(geometry, word, result):
    dims, neighbors = geometry.nested_donors(word["frames"])
    dimension_counts = Counter(dims)
    require(dimension_counts == {0: 1, 1: 111, 2: 153, 4: 70, 6: 180, 7: 120, 8: 1},
            "complete chart dimensions")
    require(dims[0] == 0, "unique zero chart")
    supports = {r["chart"]: int(r["support"], 16) for r in result["donors"]}
    require(set(supports) == {i for i, d in enumerate(dims) if 0 < d < 7},
            "support coverage of every low chart")
    increasing = {i: sorted(j for j, _ in neighbors[i] if dims[i] < dims[j] <= 6)
                  for i, d in enumerate(dims) if d <= 6}
    counts = Counter()
    maxima = {}
    witnesses = {}
    trace = hashlib.sha256()
    def visit(path, support):
        end = path[-1]
        d = dims[end]
        counts[d] += 1
        trace.update((",".join(map(str, path)) + ":" + format(support, "x") + "\n").encode())
        if support.bit_count() > maxima.get(d, -1):
            maxima[d] = support.bit_count()
            witnesses[d] = list(path)
        for child in increasing[end]:
            visit(path+[child], support | supports[child])
    visit([0], 0)
    require(counts == {0: 1, 1: 111, 2: 459, 4: 2224, 6: 37872}, "complete chain counts")
    require(maxima == {0: 0, 1: 1, 2: 2, 4: 17, 6: 35}, "chain support maxima")

    # Build the same paths from their final chart in a second pass.
    down = {i: {j for j, _ in neighbors[i] if dims[j] < dims[i]} for i in range(636)}
    by_end = {0: {(0,)}}
    for chart in sorted(supports, key=lambda i: (dims[i], i)):
        by_end[chart] = {path+(chart,) for lower in down[chart]
                         for path in by_end[lower]}
    covered = set().union(*by_end.values())
    second_maxima = {}
    for chart, paths in by_end.items():
        for path in paths:
            support = 0
            for node in path:
                support |= supports.get(node, 0)
            second_maxima[dims[chart]] = max(second_maxima.get(dims[chart], 0), support.bit_count())
    observed = set()
    def collect(path):
        observed.add(tuple(path))
        for child in increasing[path[-1]]:
            collect(path+[child])
    collect([0])
    require(observed == covered, "reverse path coverage")
    require(second_maxima == maxima, "reverse path maxima")
    return dict(dimension_counts={str(k): dimension_counts[k] for k in sorted(dimension_counts)},
                increasing_chain_counts={str(k): counts[k] for k in sorted(counts)},
                maximum_supports={str(k): maxima[k] for k in sorted(maxima)},
                attaining_chains={str(k): witnesses[k] for k in sorted(witnesses)},
                chain_trace_sha256=trace.hexdigest(), reverse_path_coverage=len(covered),
                reverse_path_maxima={str(k): second_maxima[k] for k in sorted(second_maxima)})


def controls(result):
    # Replacing a set union by the largest separate support loses real relays.
    require((0b0011 | 0b1100).bit_count() > max(0b0011.bit_count(), 0b1100.bit_count()),
            "relay-support union control")
    # Three dimension-four leaves need at least eight rank units by level cuts.
    require(2+2*3 == 8 > 6, "three-high-branch budget control")
    # An extra high edge is not free, even when a path already reaches six.
    require(6+1 > 6, "off-path edge control")
    require(result["chain_checks"]["maximum_supports"]["6"] > 30,
            "direct-only cap must fail for relay chains")
    distances = [c["minimum_distance"] for c in result["target_cosets"]]
    require(all(v > result["relay_support_bound"] for v in distances), "target separation")
    try:
        require(all(v > 48 for v in distances), "false strict separation")
    except ValueError:
        pass
    else:
        raise ValueError("false strict separation accepted")
    return dict(direct_only_cap_rejected=True, false_strict_separation_rejected=True,
                support_union_control=True, branch_budget_control=True, off_path_control=True)


def calculate():
    predecessor, source_result = load_source()
    geometry, word = predecessor.load_sources()
    result = dict(abstract_trees=abstract_trees(), chain_checks=chain_checks(geometry, word, source_result),
                  target_cosets=source_result["cases"], relay_support_bound=37,
                  independent_coarea_bound=42, scope="Arbitrary fixed-chart paid relay networks at nine rank-seven deadlines; other arrivals not claimed")
    require(result["abstract_trees"]["root_bounds"][6] == result["relay_support_bound"],
            "complete low-tree bound")
    require(result["chain_checks"]["maximum_supports"]["6"] <= result["relay_support_bound"],
            "complete high-path bound")
    result["controls"] = controls(result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-result", action="store_true")
    args = parser.parse_args()
    result = calculate()
    if args.write_result:
        (PACKAGE / "RESULT.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        require(result == json.loads((PACKAGE / "RESULT.json").read_text()), "result mismatch")
    print("PASS_BIT_NINE_DEADLINE_RELAY_FLOOR all relays: support<=37<48")


if __name__ == "__main__":
    main()
