#!/usr/bin/env python3
"""Check the full forward pair-consistent frame optimum without a solver.

Produced by Nick Petalas. Claim type: finite exact optimization certificate.
"""
import copy
import gzip
import hashlib
import json
import platform
from collections import Counter

from model import HERE, authenticate, build_model, load_graph, mathematical_digest, need
from powers import SCALE, polynomial_interval, price_interval


def histogram(counts, selected, constant):
    result = Counter(constant)
    for variable in selected:
        result.update(counts[variable])
    return [result[rank] for rank in range(1, 10)]


def primal_check(model, selected):
    need(isinstance(selected, list) and len(selected) <= len(model["counts"]), "Primal inventory")
    need(all(type(j) is int and 0 <= j < len(model["counts"]) for j in selected), "Primal index")
    need(len(set(selected)) == len(selected), "Primal uniqueness")
    support = set(selected)
    for row, rhs in zip(model["rows"], model["rhs"]):
        need(sum(value for j, value in row.items() if j in support) == rhs, "Primal marginal equation")
    return histogram(model["counts"], selected, model["constant"])


def dual_remainders(model, dual):
    need(len(dual) == len(model["rows"]), "Dual row inventory")
    need(all(isinstance(row, list) and len(row) == 5 for row in dual), "Dual price basis")
    need(all(type(x) is int and abs(x) <= 256 for row in dual for x in row), "Dual coefficient bound")
    reduced = [[hist.get(rank, 0) for rank in range(1, 6)] for hist in model["counts"]]
    for row, vector in zip(model["rows"], dual):
        for variable, value in row.items():
            for k in range(5):
                reduced[variable][k] -= value * vector[k]
    return reduced


def dual_check(model, dual, prices):
    need(all(set(hist) <= set(range(6)) for hist in model["counts"]), "Variable rank basis")
    reduced = dual_remainders(model, dual)
    distinct = Counter(tuple(row) for row in reduced)
    positive = []
    for vector in distinct:
        if any(vector):
            lower, _ = polynomial_interval(vector, prices)
            need(lower > 0, "Dual reduced-cost sign")
            positive.append(lower)
    objective = [model["constant"].get(rank, 0) for rank in range(1, 10)]
    for rhs, vector in zip(model["rhs"], dual):
        for k, value in enumerate(vector):
            objective[k] += rhs * value
    return objective, {"distinct_reduced_costs": len(distinct),
                       "zero_reduced_cost_columns": distinct[(0, 0, 0, 0, 0)],
                       "strict_signs": len(positive),
                       "minimum_positive_lower_over_scale": [min(positive), SCALE]}


def certificate_check(model, certificate, prices):
    need(certificate["schema_version"] == 1, "Certificate schema")
    need(certificate["model_sha256"] == mathematical_digest(model), "Mathematical model digest")
    primal = primal_check(model, certificate["primal_ones"])
    dual, signs = dual_check(model, certificate["dual"], prices)
    source = [model["source"].get(rank, 0) for rank in range(1, 10)]
    need(primal == dual == source, "Coefficientwise primal-dual-source equality")
    need(primal == certificate["optimum_histogram"], "Certificate objective")
    return primal, signs


def rejection(action, message):
    try:
        action()
    except ValueError as error:
        need(message in str(error), "Unexpected rejection reason")
        return message
    raise ValueError("Mutation accepted: " + message)


def controls(model, certificate, prices):
    results = []
    changed = certificate["primal_ones"][:-1]
    results.append(rejection(lambda: primal_check(model, changed), "Primal marginal equation"))
    results.append(rejection(lambda: primal_check(model, [-1]), "Primal index"))
    changed = certificate["primal_ones"] + certificate["primal_ones"][:1]
    results.append(rejection(lambda: primal_check(model, changed), "Primal uniqueness"))
    dual = copy.deepcopy(certificate["dual"])
    dual[0][0] += 1
    results.append(rejection(lambda: dual_check(model, dual, prices), "Dual reduced-cost sign"))
    dual = copy.deepcopy(certificate["dual"])
    dual.pop()
    results.append(rejection(lambda: dual_check(model, dual, prices), "Dual row inventory"))
    changed = dict(model)
    changed["rows"] = model["rows"][:-1]
    results.append(rejection(lambda: certificate_check(changed, certificate, prices), "Mathematical model digest"))
    changed = dict(certificate)
    changed["optimum_histogram"] = certificate["optimum_histogram"][:]
    changed["optimum_histogram"][0] -= 1
    results.append(rejection(lambda: certificate_check(model, changed, prices), "Certificate objective"))
    results.append(rejection(lambda: price_interval(0), "Rank domain"))
    return results


def actual_assignment(schedule, model, selected):
    support = set(selected)
    values = schedule.original_values[:]
    for i, variables in model["variables"].items():
        chosen = [k for k, j in enumerate(variables) if j in support]
        need(len(chosen) == 1, "Integral frame marginal")
        values[i] = model["domains"][i][chosen[0]]
    schedule.graph.check(values)
    return sum(a != b for a, b in zip(values, schedule.original_values))


def main():
    inputs = authenticate()
    frame, schedule = load_graph(inputs)
    model = build_model(frame, schedule)
    raw_certificate = gzip.decompress((HERE / "CERTIFICATE.json.gz").read_bytes())
    need(len(raw_certificate) <= 1048576, "Certificate size")
    certificate = json.loads(raw_certificate)
    prices = {rank: price_interval(rank) for rank in range(1, 10)}
    optimum, signs = certificate_check(model, certificate, prices)
    changed = actual_assignment(schedule, model, certificate["primal_ones"])
    rejected = controls(model, certificate, prices)
    hashes = {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
              for path in sorted(HERE.iterdir()) if path.is_file()}
    result = {"status": "PASS_PAIR_CONSISTENT_FRAME_OPTIMUM", "claim_type": "finite exact optimization certificate",
              "orientation": "forward", "saving": "15108879/5000000000", "optimum_histogram_ranks_1_to_9": optimum,
              "nodes": len(schedule.graph.fixed), "mapped_edges": model["mapped_edges"],
              "flexible_contacts": len(model["domains"]), "marginal_choices": sum(map(len, model["domains"].values())),
              "columns": len(model["counts"]), "equalities": len(model["rows"]),
              "nonzero_coefficients": sum(map(len, model["rows"])), "attainer_changed_frames": changed,
              "dual": signs, "controls": rejected, "python": platform.python_version(), "sha256": hashes}
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
