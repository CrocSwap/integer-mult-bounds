"""Check the exact four-state gauge lower bound and its equality case."""

from collections import Counter
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from itertools import product
from pathlib import Path
import argparse
import gzip
import json


def native_costs(word, native, lines, review):
    lagrangians = list(map(review.lagrangian, word["frames"]))
    transformed = []
    for state in range(4):
        current = lagrangians
        for bit, line in enumerate(lines):
            if (state >> bit) & 1:
                current = [review.transform(rows, line) for rows in current]
        transformed.append(current)
    cache = {}
    for _, _, before, after, old, _, _ in native:
        if (before, after) in cache:
            continue
        table = [[len(review.gf2_basis(transformed[i][before] + transformed[j][after])) - 9 - old
                  for j in range(4)] for i in range(4)]
        review.check(table[0][0] == 0, "Original four-state edge rank")
        review.check(all(table[i][j] == table[0][i ^ j] for i in range(4) for j in range(4)),
                     "Four-state XOR rank rule")
        cache[before, after] = table[0]
    return [cache[e[2], e[3]] for e in native]


def check_lower_graph(receipt, edges, native, count, review, require_rigidity, objective_key):
    saved = {(u, v): weight for u, v, weight in receipt["edges"]}
    review.check(len(saved) == len(receipt["edges"]) and saved == edges, "Separable lower graph")
    cover = receipt["negative_cover"]
    review.check(len(set(cover)) == len(cover) and set(cover) <= set(range(count)), "Lower graph cover")
    review.check(all(set(pair) & set(cover) for pair, weight in edges.items() if weight < 0), "Lower negative cover")
    expected = set(product((0, 1), repeat=len(cover)))
    seen, energies, rigidity = set(), [], []
    for case in receipt["cases"]:
        fixed = dict(case["fixed"])
        review.check(set(fixed) == set(cover), "Lower graph fixed vertices")
        branch = tuple(fixed[node] for node in cover)
        review.check(branch in expected and branch not in seen, "Lower graph branch coverage")
        seen.add(branch)
        energy, capacity, flow, _ = review.check_flow_cut(case, edges, count, fixed, case[objective_key])
        energies.append(energy)
        if energy == 0 and require_rigidity:
            rigidity.append(review.zero_cut_rigidity(capacity, flow, count, fixed, native))
    review.check(seen == expected and min(energies) == receipt["minimum"] == 0, "Lower graph minimum")
    return dict(flow_cut_cases=len(energies), minimum=0, zero_cut_rigidity=rigidity)


def main(args):
    spec = spec_from_file_location("review", Path(__file__).with_name("review_wire_gauge.py"))
    review = module_from_spec(spec)
    spec.loader.exec_module(review)
    raw = args.certificate.read_bytes()
    certificate = json.loads(gzip.decompress(raw))
    review.check(certificate["source_base"] == review.BASE and certificate["lines"] == [128, 256], "Four-state source and gauge")
    word, programs = review.load_source()
    review.check_orientation_duality(word, programs)
    native = review.rebuild_graph(word, programs["forward"], certificate)
    costs = native_costs(word, native, certificate["lines"], review)
    interactions = Counter(delta[3] - delta[1] - delta[2] for delta in costs)
    review.check(dict(interactions) == {int(k): v for k, v in certificate["interaction_counts"].items()},
                 "Four-state interaction inventory")
    lowers = [Counter(), Counter()]
    for edge, delta in zip(native, costs):
        weights = delta[1:3]
        if delta[3] < sum(weights):
            review.check(weights == [1, 1] and delta[3] == 0, "A different interaction needs a new lower bound")
            weights = [0, 0]
        review.check(all(delta[state] >= sum(weights[j] for j in range(2) if state & (1 << j))
                         for state in range(4)), "Edgewise separable lower bound")
        if edge[0] != edge[1]:
            for j in range(2):
                lowers[j][tuple(sorted(edge[:2]))] += weights[j]
    count = len(certificate["graph"]["labels"])
    review.check(len(certificate["separable_bound"]) == 2, "Separable graph count")
    records = [check_lower_graph(receipt, {pair: w for pair, w in lower.items() if w}, native, count, review, True, "rank_delta")
               for receipt, lower in zip(certificate["separable_bound"], lowers)]
    review.check(certificate["certified_lower_bound"] == 0, "Four-state lower bound")
    thresholds = []
    if "thresholds" in certificate:
        review.check([rec["cap"] for rec in certificate["thresholds"]] == list(range(1, 10)),
                     "Four-state threshold coverage")
        for receipt in certificate["thresholds"]:
            cap = receipt["cap"]
            review.check(receipt["scale"] == 2 and len(receipt["lower_graphs"]) == 2,
                         "Doubled separable threshold scale")
            lowers = [Counter(), Counter()]
            for edge, rank_delta in zip(native, costs):
                rank = edge[4]
                review.check(all(0 <= rank + d <= 9 for d in rank_delta), "Four-state native rank range")
                delta = [min(rank + change, cap) - min(rank, cap) for change in rank_delta]
                deficit = max(0, delta[1] + delta[2] - delta[3])
                weights = [2 * delta[1] - deficit, 2 * delta[2] - deficit]
                review.check(all(2 * delta[state] >= sum(weights[j] for j in range(2) if state & (1 << j))
                                 for state in range(4)), "Doubled edgewise threshold bound")
                if edge[0] != edge[1]:
                    for j in range(2):
                        lowers[j][tuple(sorted(edge[:2]))] += weights[j]
            bounds = [check_lower_graph(rec, {pair: w for pair, w in lower.items() if w}, native, count, review, False, "objective_delta")
                      for rec, lower in zip(receipt["lower_graphs"], lowers)]
            review.check(receipt["twice_certified_lower_bound"] == 0, "Four-state threshold lower bound")
            thresholds.append(dict(cap=cap, minimum=0, flow_cut_cases=sum(r["flow_cut_cases"] for r in bounds)))
    result = dict(status="PASS_FOUR_STATE_GAUGE_RANK_AND_RIGIDITY", source_base=review.BASE,
                  certificate_sha256=sha256(raw).hexdigest(), gauges=["I", "C_128", "C_256", "C_128 C_256"],
                  rank_lower_bound=0, maximum_total_negative_rank_mass=sum(max(0, -min(delta)) for delta in costs),
                  lower_graphs=records, forward_backward_gauge_graph_isomorphism=True,
                  thresholds=thresholds,
                  equality_case="Both bits are constant on all 1971 native-edge components; only eight isolated final zero components are free.",
                  not_used="The exploratory solver status, solver lower bound, and saved state were not used as proof.")
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"] + " cases=" + str(sum(r["flow_cut_cases"] for r in records)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--certificate", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    main(parser.parse_args())
