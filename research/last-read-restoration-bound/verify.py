#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Finite corroboration produced by Nick Petalas. Writes no files."""

from collections import Counter
from hashlib import sha256
from itertools import permutations, product
import json
from pathlib import Path
import sys


def require(condition, message):
    if not condition:
        raise ValueError(message)


def finite_case(source_size, work_size, output_size, all_targets):
    require(1 <= source_size <= 4, "source size bound")
    require(1 <= work_size <= 4 and 1 <= output_size <= 4, "state size bounds")
    targets = tuple(product(range(output_size), repeat=source_size))
    if not all_targets:
        require(source_size == output_size, "identity target domain")
        targets = (tuple(range(source_size)),)
    suffixes = tuple(permutations(range(work_size)))
    outputs = tuple(product(range(output_size), repeat=work_size))
    counts = Counter()
    maxima = []
    for target in targets:
        maximum = 0
        bound = max(Counter(target).values())
        for prefix in product(range(work_size), repeat=source_size):
            for suffix in suffixes:
                final = tuple(suffix[w] for w in prefix)
                for readout in outputs:
                    delivered = tuple(readout[w] for w in prefix)
                    for initial in range(work_size):
                        score = sum(final[x] == initial and delivered[x] == target[x]
                                    for x in range(source_size))
                        require(score <= bound, "literal joint-success bound")
                        maximum = max(maximum, score)
                        counts[score] += 1
        require(maximum == bound, "sharp bound for every target")
        maxima.append(maximum)
    return {"source_size": source_size, "workspace_size": work_size,
            "output_size": output_size, "targets": len(targets),
            "protocols": sum(counts.values()), "input_runs": source_size * sum(counts.values()),
            "joint_success_histogram": dict(sorted(counts.items())), "attaining_maxima": maxima}


def add(left, right, q, sign=1):
    require(len(left) == len(right), "equal vector lengths")
    return tuple((a + sign * b) % q for a, b in zip(left, right))


def target_value(x, rank, q):
    require(len(x) == rank + 1 and 1 <= rank <= 2, "target shape")
    return tuple((x[j] + (j + 1) * x[-1]) % q for j in range(rank))


def execute(kind, x, initial_work, initial_output, q):
    """Literal logical updates; return cut output, final work and output."""
    rank = len(initial_work)
    value = target_value(x, rank, q)
    work, out = initial_work, initial_output
    if kind == "guess":
        return out, work, out
    if kind == "early":
        out = add(out, value, q)
        return out, work, out
    if kind == "feedback":
        work, out = out, work
        work = add(work, value, q)
        cut = out
        work, out = out, work
        return cut, work, out
    require(kind in ("deferred", "reread", "erase"), "known program")
    out = add(out, work, q, -1)
    work = add(work, value, q)
    cut = out
    out = add(out, work, q)
    if kind == "reread":
        work = add(work, target_value(x, rank, q), q, -1)
    if kind == "erase":
        require(not any(initial_work), "erasure control has clean initial work")
        work = (0,) * rank
    return cut, work, out


def gate_case(q, rank):
    require(q in (2, 3, 5) and rank in (1, 2), "fixed prime-field domain")
    inputs = tuple(product(range(q), repeat=rank + 1))
    states = tuple(product(range(q), repeat=rank))
    outcomes = {name: Counter() for name in ("deferred", "guess", "reread", "feedback", "early")}
    mixtures = [Counter() for _ in range(5)]
    clean_erasure = Counter()
    hidden_log = Counter()
    for work, out in product(states, repeat=2):
        for x in inputs:
            expected = add(out, target_value(x, rank, q), q)
            for name, counts in outcomes.items():
                cut, final_work, final_out = execute(name, x, work, out, q)
                if name != "early":
                    wanted_cut = work if name == "feedback" else out
                    if name in ("deferred", "reread"):
                        wanted_cut = add(out, work, q, -1)
                    require(cut == wanted_cut, "no source dependence at deferred cut")
                counts[(final_out == expected, final_work == work)] += 1
            for numerator in range(5):
                for coin in range(4):
                    name = "deferred" if coin < numerator else "guess"
                    _, final_work, final_out = execute(name, x, work, out, q)
                    mixtures[numerator][(final_out == expected, final_work == work)] += 1
            if not any(work):
                _, end_work, end_out = execute("erase", x, work, out, q)
                clean_erasure[(end_out == expected, end_work == work)] += 1
            initial_log = (0,) * rank
            log = add(initial_log, target_value(x, rank, q), q)
            logged_out = add(out, log, q)
            visible_work = work
            hidden_log[(logged_out == expected, (visible_work, log) == (work, initial_log))] += 1
    return check_gate_counts(q, rank, len(inputs), len(states), outcomes,
                             mixtures, clean_erasure, hidden_log)


def encoded_counts(counts):
    return {f"output_{int(a)}_workspace_{int(b)}": n for (a, b), n in sorted(counts.items())}


def check_gate_counts(q, rank, input_count, state_count, outcomes, mixtures, erased, log):
    total = input_count * state_count**2
    joint = total // q**rank
    require(total % q**rank == 0, "integral fibre count")
    require(outcomes["deferred"] == {(True, True): joint, (True, False): total - joint},
            "exact-output attaining program")
    require(outcomes["guess"] == {(True, True): joint, (False, True): total - joint},
            "exact-restoration attaining program")
    for name in ("reread", "feedback", "early"):
        require(outcomes[name] == {(True, True): total}, "changed-premise escape: " + name)
    require(erased == {(True, True): input_count * state_count}, "noninjective escape")
    require(log == {(True, True): joint, (True, False): total - joint}, "complete hidden log debt")
    for numerator, counts in enumerate(mixtures):
        require(sum(counts.values()) == 4 * total, "four actual coin outcomes")
        require(counts[(True, True)] == 4 * joint, "mixture joint boundary")
        require(counts[(False, True)] == (4 - numerator) * (total - joint), "output error frontier")
        require(counts[(True, False)] == numerator * (total - joint), "workspace error frontier")
        require(not counts[(False, False)], "no unnecessary double failure")
    require(outcomes["deferred"][(True, True)] * q**(rank + 1) > total,
            "attaining program rejects a one-digit stronger bound")
    return {"q": q, "rank": rank, "source_dimension": rank + 1,
            "dirty_output_input_cases": total,
            "programs": {n: encoded_counts(c) for n, c in outcomes.items()},
            "mixtures": [encoded_counts(c) for c in mixtures],
            "clean_erasure": encoded_counts(erased), "complete_log": encoded_counts(log)}


def matrix_rank(matrix, q):
    require(matrix and len(matrix) <= 3, "bounded rank rows")
    columns = len(matrix[0])
    require(1 <= columns <= 3 and all(len(row) == columns for row in matrix), "bounded rank columns")
    rows = [list(row) for row in matrix]
    rank = 0
    for column in range(columns):
        pivot = next((i for i in range(rank, len(rows)) if rows[i][column] % q), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        inverse = pow(rows[rank][column] % q, -1, q)
        rows[rank] = [v * inverse % q for v in rows[rank]]
        for i in range(len(rows)):
            if i != rank:
                coefficient = rows[i][column] % q
                rows[i] = [(a - coefficient * b) % q for a, b in zip(rows[i], rows[rank])]
        rank += 1
    return rank


def multiply(left, right, q):
    require(len(left[0]) == len(right), "product shape")
    return tuple(tuple(sum(a * b for a, b in zip(row, column)) % q for column in zip(*right))
                 for row in left)


def linear_cases():
    histograms = {}
    for q in (2, 3):
        matrices = tuple((v[:2], v[2:]) for v in product(range(q), repeat=4))
        for matrix in matrices:
            images = {tuple(sum(a * b for a, b in zip(row, x)) % q for row in matrix)
                      for x in product(range(q), repeat=2)}
            require(len(images) == q**matrix_rank(matrix, q), "independent image-size rank oracle")
        invertible = tuple(a for a in matrices if matrix_rank(a, q) == 2)
        counts = Counter()
        for suffix in invertible:
            for cut in matrices:
                residual = multiply(suffix, cut, q)
                residual_rank = matrix_rank(residual, q)
                require(residual_rank == matrix_rank(cut, q), "invertible suffix preserves cut rank")
                for readout in matrices:
                    demand = multiply(readout, cut, q)
                    demand_rank = matrix_rank(demand, q)
                    require(demand_rank <= residual_rank, "deferred target rank versus final debt")
                    counts[(demand_rank, residual_rank)] += 1
        histograms[str(q)] = {f"target_{a}_debt_{b}": n for (a, b), n in sorted(counts.items())}
    return histograms


def rejection_controls():
    rejected = 0
    for args in ((0, 2, 2, True), (5, 2, 2, True), (2, 0, 2, True),
                 (2, 5, 2, True), (2, 2, 0, True), (2, 2, 5, True), (2, 2, 3, False)):
        try:
            finite_case(*args)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("invalid finite domain accepted")
    for q, rank in ((4, 1), (2, 0), (2, 3)):
        try:
            gate_case(q, rank)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("invalid gate domain accepted")
    require(rejected == 10, "all invalid domains rejected")
    return rejected


def package_hashes(here):
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    hashes = {}
    for name in names:
        path = here / name
        require(path.is_file() and not path.is_symlink(), "regular local package file")
        with path.open("rb") as source:
            raw = source.read(1024 * 1024 + 1)
        require(0 < len(raw) <= 1024 * 1024, "package file byte bound")
        hashes[name] = sha256(raw).hexdigest()
    return hashes


def main():
    require(len(sys.argv) == 1, "no command-line arguments are accepted")
    finite = [finite_case(4, 2, 2, True), finite_case(3, 3, 3, True),
              finite_case(4, 4, 4, False)]
    gates = [gate_case(q, r) for q in (2, 3, 5) for r in (1, 2)]
    result = {"claim_type": "scoped_proof_with_finite_corroboration",
              "finite_state_domains": finite, "gate_domains": gates,
              "linear_rank_histograms": linear_cases(),
              "invalid_domain_rejections": rejection_controls(), "no_new_kappa": True}
    result["package_sha256"] = package_hashes(Path(__file__).resolve().parent)
    print(json.dumps(result, sort_keys=True))
    print("PASS_LAST_READ_RESTORATION_BOUND")


if __name__ == "__main__":
    main()
