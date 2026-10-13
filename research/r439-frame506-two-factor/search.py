#!/usr/bin/env python3
"""Exact finite positive-integer destination-once search on two fixed factors.

Adapted for Eva Ayala with substantial OpenAI Codex assistance from Ross Richardson PR914; Apache-2.0.
Standard library only. This does not search arbitrary circuits or change kappa.
"""
import argparse
import gzip
import hashlib
import json
import random
from pathlib import Path

BASE = "407d52ff15b2217b6e22bce44728b4c3907b6515"
SOURCE = "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz"
SHA256 = "e3e301e62bc2b41dbf1ceac0acf3d35824ebeab1848c5a2142d4577b109da52f"
SEED = 18
FRAME = 506
START, END = 102, 128
ROOT = Path(__file__).resolve().parents[2]


def need(condition, message):
    if not condition:
        raise ValueError(message)


def identity(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def matrix(ops, registers):
    index = {r: i for i, r in enumerate(registers)}
    result = identity(len(registers))
    for destination, source in ops:
        d, s = index[destination], index[source]
        need(d != s, "self-donor operation is not permitted")
        result[d] = [a + b for a, b in zip(result[d], result[s])]
    return result


def solve(original_ops, registers, destination_priority):
    """Bellman search, compressed by the exact set of completed destinations.

    At a reachable subset, completed rows equal their target rows, others are
    unit rows. Its inverse is integral because every legal update is unimodular.
    Desired row minus its unit row times that inverse is the UNIQUE donor vector.
    Feasible iff its own coefficient is zero and all coefficients are nonnegative.
    Every positive integer coefficient c costs c elementary additions. Therefore
    these transitions exhaust all positive integer donor multisets and all orders.
    Identity rows are permitted one zero-cost write; including them covers all n!
    destination orders without changing the possible circuits or optimum.
    """
    n = len(registers)
    target = matrix(original_ops, registers)
    inverse = {0: identity(n)}
    best = {0: 0}
    path = {0: ()}
    rank = {i: k for k, i in enumerate(destination_priority)}
    path_key = {0: ()}
    feasible_paths = {0: 1}
    optimal_paths = {0: 1}
    attempted = feasible = 0
    transitions = {}
    for mask in range(1 << n):
        if mask not in best:
            continue
        inv = inverse[mask]
        for i in destination_priority:
            if mask >> i & 1:
                continue
            attempted += 1
            wanted = [value - int(i == j) for j, value in enumerate(target[i])]
            donor = tuple(sum(wanted[k] * inv[k][j] for k in range(n)) for j in range(n))
            if donor[i] != 0 or any(value < 0 for value in donor):
                continue
            feasible += 1
            next_mask = mask | (1 << i)
            transitions[(mask, i)] = donor
            next_inverse = [[inv[a][b] - inv[a][i] * donor[b] for b in range(n)] for a in range(n)]
            if next_mask in inverse:
                need(inverse[next_mask] == next_inverse, "hybrid inverse depends on history")
            else:
                inverse[next_mask] = next_inverse
            feasible_paths[next_mask] = feasible_paths.get(next_mask, 0) + feasible_paths[mask]
            value = best[mask] + sum(donor)
            key = path_key[mask] + (rank[i],)
            new_path = path[mask] + ((i, donor),)
            if next_mask not in best or value < best[next_mask]:
                best[next_mask] = value
                path[next_mask] = new_path
                path_key[next_mask] = key
                optimal_paths[next_mask] = optimal_paths[mask]
            elif value == best[next_mask]:
                optimal_paths[next_mask] += optimal_paths[mask]
                if key < path_key[next_mask]:
                    path[next_mask] = new_path
                    path_key[next_mask] = key
    final = (1 << n) - 1
    need(final in best, "no destination-once realization found")
    new_ops = [[registers[i], registers[j]] for i, donor in path[final]
               for j, coefficient in enumerate(donor) for _ in range(coefficient)]
    need(len(new_ops) == best[final], "operation count disagrees with Bellman minimum")
    need(matrix(new_ops, registers) == target, "new operations disagree with factor integer matrix")
    original_reverse = matrix(list(reversed(original_ops)), registers)
    new_reverse = matrix(list(reversed(new_ops)), registers)
    reverse_dominated = all(a <= b for aa, bb in zip(new_reverse, original_reverse)
                            for a, b in zip(aa, bb))
    return {
        "original_ops": original_ops,
        "new_ops": new_ops,
        "target_matrix": target,
        "original_additions": len(original_ops),
        "minimum_additions": best[final],
        "optimal_order": [registers[i] for i, _ in path[final]],
        "donor_coefficients": [list(donor) for _, donor in path[final]],
        "positive_reverse_matrix": new_reverse,
        "original_positive_reverse_matrix": original_reverse,
        "positive_reverse_entrywise_dominated": reverse_dominated,
        "coverage": {
            "domain": "all destination-once positive integer donor schedules of this fixed integer matrix; identity writes may have no donors",
            "destination_count": n,
            "subset_domain_size": 1 << n,
            "reachable_subsets": len(best),
            "attempted_transitions": attempted,
            "feasible_transitions": feasible,
            "rejected_transitions": attempted - feasible,
            "feasible_orders": feasible_paths[final],
            "minimum_cost_orders": optimal_paths[final],
            "stopping_rule": "all reachable subsets processed and all not-yet-written destinations tested",
            "completed": True,
        },
    }


def produce():
    data = (ROOT / SOURCE).read_bytes()
    need(hashlib.sha256(data).hexdigest() == SHA256, "source SHA256 mismatch")
    word = json.loads(gzip.decompress(data))
    block = word["B"][START:END]
    need(len(block) == 26 and all(f == FRAME and len(ss) == 1 for f, _, ss in block), "source block moved")
    registers = sorted({r for _, d, ss in block for r in [d, *ss]})
    priority = list(range(len(registers)))
    random.Random(SEED).shuffle(priority)
    cuts, witnesses = [], []
    for cut in range(START + 1, END):
        factors = []
        try:
            for a, b in ((START, cut), (cut, END)):
                old = [[d, s] for _, d, ss in word["B"][a:b] for s in ss]
                result = solve(old, registers, priority)
                result.update(start=a, end=b)
                factors.append(result)
        except ValueError as error:
            if str(error) != "no destination-once realization found":
                raise
            cuts.append(dict(cut=cut, feasible=False))
            continue
        cost = sum(f["minimum_additions"] for f in factors)
        cuts.append(dict(cut=cut, feasible=True, factor_minima=[f["minimum_additions"] for f in factors], total=cost))
        witnesses.append((cost, cut, factors))
    need(len(cuts) == 25, "cut coverage incomplete")
    cost, cut, factors = min(witnesses, key=lambda x: (x[0], x[1]))
    old_ops = [[d, s] for _, d, ss in block for s in ss]
    new_ops = [op for f in factors for op in f["new_ops"]]
    need(matrix(old_ops, registers) == matrix(new_ops, registers), "whole block integer identity failed")
    old_reverse, new_reverse = [matrix(list(reversed(ops)), registers) for ops in (old_ops, new_ops)]
    dominated = all(a <= b for aa, bb in zip(new_reverse, old_reverse) for a, b in zip(aa, bb))
    return dict(format="r439-frame506-two-factor-v1", classification="finite circuit construction", base_commit=BASE,
        assignment_seed=SEED, source_path=SOURCE, source_sha256=SHA256, source_range=[START, END], frame=FRAME,
        registers=registers, destination_priority=[registers[i] for i in priority], fixed_cuts=[START, cut, END],
        searched_cuts=cuts, stopping_rule="all25 original internal gate boundaries; all reachable hybrid subsets per factor",
        factors=factors, candidate_gates=[[FRAME,d,[s]] for d,s in new_ops], original_additions=len(old_ops),
        candidate_additions=cost, saved_additions=len(old_ops)-cost, integer_forward_identity=True,
        positive_reverse_entrywise_dominated=dominated, positive_reverse_identity=new_reverse==old_reverse,
        local_unit_norm_forward_then_reverse_max={name:max(map(sum,matrix(ops+list(reversed(ops)),registers)))
            for name,ops in (("original",old_ops),("candidate",new_ops))},
        scope="Minimum only in this union of25 two-factor destination-once positive integer schedule classes. Full-word admission verified separately. No arbitrary circuit optimum or new kappa.")


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args=parser.parse_args()
    result=produce();path=Path(__file__).with_name("CANDIDATE.json")
    if args.check:
        need(json.loads(path.read_text())==result,"regenerated candidate differs")
    else:
        path.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("PASS_FRAME506_SEARCH",result["fixed_cuts"],result["candidate_additions"],"cuts=25", "reverse_dominated="+str(result["positive_reverse_entrywise_dominated"]))

if __name__ == "__main__":
    main()
