#!/usr/bin/env python3
"""Exact finite positive-integer destination-once search on two fixed factors.

Prepared by Ross Richardson (@RossRichardson) with substantial OpenAI Codex assistance; Apache-2.0.
Standard library only. This does not search arbitrary circuits or change kappa.
"""
import argparse
import gzip
import hashlib
import json
import random
from pathlib import Path

BASE = "f567884aeb8851b6e794af1184119a3bfbe1e631"
SOURCE = "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz"
SHA256 = "e3e301e62bc2b41dbf1ceac0acf3d35824ebeab1848c5a2142d4577b109da52f"
SEED = 13
FRAME = 524
CUTS = ((449, 466), (466, 490))
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
    need(reverse_dominated, "factor positive reverse matrix is not entrywise dominated")
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
    block = word["B"][CUTS[0][0]:CUTS[-1][1]]
    need(len(block) == 41 and all(f == FRAME and len(ss) == 1 for f, _, ss in block),
         "source range is not the pinned 41-gate singleton frame524 block")
    registers = sorted({r for _, t, ss in block for r in [t, *ss]})
    need(registers == sorted(word["frames"][FRAME]), "block register union differs from frame524")
    priority = list(range(len(registers)))
    random.Random(SEED).shuffle(priority)
    factors = []
    for start, end in CUTS:
        old = [[t, s] for _, t, ss in word["B"][start:end] for s in ss]
        result = solve(old, registers, priority)
        result.update({"start": start, "end": end})
        factors.append(result)
    original_ops = [op for result in factors for op in result["original_ops"]]
    new_ops = [op for result in factors for op in result["new_ops"]]
    need(matrix(original_ops, registers) == matrix(new_ops, registers), "full block integer forward identity failed")
    old_reverse = matrix(list(reversed(original_ops)), registers)
    new_reverse = matrix(list(reversed(new_ops)), registers)
    need(all(a <= b for aa, bb in zip(new_reverse, old_reverse) for a, b in zip(aa, bb)),
         "full block positive reverse domination failed")
    need({r for op in new_ops for r in op} == set(registers), "new block omits a source register")
    return {
        "format": "r439-frame524-fixed-factor-search-v1",
        "classification": "finite circuit construction and exhaustive fixed-factor minimum",
        "base_commit": BASE,
        "assignment_seed": SEED,
        "source_path": SOURCE,
        "source_sha256": SHA256,
        "source_range": [CUTS[0][0], CUTS[-1][1]],
        "frame": FRAME,
        "registers": registers,
        "destination_priority": [registers[i] for i in priority],
        "fixed_cuts": [CUTS[0][0], CUTS[0][1], CUTS[1][1]],
        "factors": factors,
        "candidate_gates": [[FRAME, t, [s]] for t, s in new_ops],
        "original_additions": len(original_ops),
        "candidate_additions": len(new_ops),
        "saved_additions": len(original_ops) - len(new_ops),
        "integer_forward_identity": True,
        "positive_reverse_entrywise_dominated": True,
        "positive_reverse_identity": new_reverse == old_reverse,
        "local_unit_norm_forward_then_reverse_max": {
            "original": max(map(sum, matrix(original_ops + list(reversed(original_ops)), registers))),
            "candidate": max(map(sum, matrix(new_ops + list(reversed(new_ops)), registers))),
        },
        "scope": "Two fixed source LU factors only; no arbitrary-circuit optimum, new recursive profile, full-theorem proof, or new kappa is asserted.",
        "attribution": "Ross Richardson (@RossRichardson), with substantial OpenAI Codex assistance; depends on the selected PR589 word and predecessor R439 construction. Apache-2.0.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("CANDIDATE.json"))
    parser.add_argument("--check", action="store_true", help="compare exact regenerated JSON with existing output")
    args = parser.parse_args()
    result = produce()
    if args.check:
        need(json.loads(args.output.read_text()) == result, "regenerated candidate differs from saved candidate")
    else:
        args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"source_sha256": SHA256, "factor_minima": [x["minimum_additions"] for x in result["factors"]],
                      "original_additions": result["original_additions"], "candidate_additions": result["candidate_additions"],
                      "integer_forward_identity": True, "positive_reverse_entrywise_dominated": True}, sort_keys=True))


if __name__ == "__main__":
    main()
