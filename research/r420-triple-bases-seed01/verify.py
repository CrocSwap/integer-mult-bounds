#!/usr/bin/env python3
"""Exact closed three-helper census on one R420 decoder. Apache-2.0.

Sagar Thakrar, with substantial OpenAI Codex assistance. The starting recipe
is Adam Gall's PR1206; full-word checks reuse PR708 and eumemic's PR543.
"""
import argparse
from collections import Counter, deque
import copy
import gzip
import hashlib
import importlib.util
from itertools import combinations, permutations
import json
from pathlib import Path
import random

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
IDENTITY = (1, 2, 4)
GENERATORS = tuple(permutations(range(3), 2))


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def transform(rows, chain):
    rows = [set(r) for r in rows]
    for a, b in chain:
        for row in rows:
            if a in row:
                row.symmetric_difference_update({b})
    return rows


def construct(word, chain):
    tail = word["A"][-9:]
    need([g[1] for g in tail] == word["ret"] and all(g[0] == 1 for g in tail), "FULL decoder suffix")
    pool = set.union(*(set(g[2]) for g in tail)) - set(word["ret"])
    need(all(len(g) == 2 and g[0] != g[1] and set(g) <= pool for g in chain), "helper operands")
    prefix = [[1, a, [b]] for a, b in chain]
    rows = transform([g[2] for g in tail], chain)
    result = copy.deepcopy(word)
    result["A"] = word["A"][:-9] + prefix + [
        [f, d, sorted(r)] for (f, d, _), r in zip(tail, rows)] + prefix[::-1]
    result["C"] = [[1, d, list(s)] for _, d, s in reversed(result["A"] + result["B"])
                   if not word["v"] <= d < 2 * word["v"]]
    return result


def fixed_point(rows, pool):
    rng = random.Random(1)
    chain, rounds = [], []
    while True:
        scores = [(sum(1 if b in r else -1 for r in rows if a in r) - 2,
                   rng.random(), a, b) for a in pool for b in pool if a != b]
        gain, _, a, b = max(scores)
        rounds.append({"pairs": len(scores), "positive": sum(x[0] > 0 for x in scores),
                       "best_gain": gain, "chosen": [a, b] if gain > 0 else None})
        if gain <= 0:
            return chain, rows, rounds
        chain.append([a, b])
        rows = transform(rows, [[a, b]])


def step(state, a, b):
    result = list(state)
    result[b] ^= result[a]
    return tuple(result)


def group():
    paths = {IDENTITY: ()}
    queue = deque(paths)
    while queue:
        state = queue.popleft()
        for a, b in GENERATORS:
            child = step(state, a, b)
            if child not in paths:
                paths[child] = paths[state] + ((a, b),)
                queue.append(child)
    validate_group(paths)
    return paths


def validate_group(paths):
    # A binary 3x3 matrix is invertible iff its seven nonzero combinations differ.
    invertible = {s for s in permutations(range(1, 8), 3)
                  if len({s[0], s[1], s[2], s[0]^s[1], s[0]^s[2],
                          s[1]^s[2], s[0]^s[1]^s[2]}) == 7}
    need(set(paths) == invertible and len(paths) == 168, "GL3 completeness")


def shortest_paths(target, paths):
    if target == IDENTITY:
        return [()]
    found = []
    for a, b in GENERATORS:
        parent = step(target, a, b)
        if len(paths[parent]) + 1 == len(paths[target]):
            found.extend(path + ((a, b),) for path in shortest_paths(parent, paths))
    return found


def census(rows, pool, paths):
    columns = [sum(1 << i for i, row in enumerate(rows) if a in row) for a in pool]
    histogram, positive = Counter(), []
    for indices in combinations(range(len(pool)), 3):
        a, b, c = (columns[i] for i in indices)
        weights = [x.bit_count() for x in (0, a, b, a^b, c, a^c, b^c, a^b^c)]
        old = weights[1] + weights[2] + weights[4]
        for state, path in sorted(paths.items()):
            gain = old - sum(weights[k] for k in state) - 2 * len(path)
            histogram[gain] += 1
            if gain > 0:
                positive.append({"helpers": [pool[i] for i in indices],
                                 "state": list(state), "gain": gain,
                                 "shortest_length": len(path)})
    return dict(sorted(histogram.items())), positive


def prefix_bounds(word):
    """Literal positive ADD/COPY/ERASE replay, matching columns_k.cpp's bill."""
    n = 2 * word["v"] + word["R"]
    events = []
    for section in ("D", "A", "scatter", "B", "C"):
        if section == "scatter":
            for k, q in enumerate(word["ret"]):
                events.append(("copy", n, q))
                events.extend(("add", word["v"] + t, n)
                              for t, row in enumerate(word["scatter"]) if k in row)
                events.append(("erase", n, q))
        else:
            events.extend(("add", d, s) for _, d, sources in word[section] for s in sources)
    bounds = []
    for reverse in (False, True):
        values, largest, opened = [1] * (n + 1), 1, False
        for op, d, s in (reversed(events) if reverse else events):
            if op == "add":
                need(s != n or opened, "read outside copy lifetime")
                values[d] += values[s]
                largest = max(largest, values[d])
            elif (op == "copy") != reverse:
                need(not opened, "overlapping copied temporary")
                values[d], opened = values[s], True
            else:
                need(opened, "erase without copy")
                values[d], opened = 0, False
        need(not opened, "unclosed copied temporary")
        bounds.append(largest)
    payload = 64 * bounds[0] ** 3 * bounds[1] ** 2
    return {"forward": bounds[0], "reverse": bounds[1], "payload": str(payload),
            "bits": payload.bit_length(), "native_104_bit_admitted": payload < 2 ** 104,
            "pr1206_wrapper_admitted": payload.bit_length() < 104}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", action="store_true", help="print fresh JSON instead of comparing certificate")
    parser.add_argument("--output", type=Path, help="fresh scratch directory for literal words")
    args = parser.parse_args()
    need(__debug__, "run without -O: the inherited geometry checker uses assertions")
    for pin in json.loads((HERE / "SOURCES.json").read_text())["files"]:
        if pin["usage"] == "input":
            need(hashlib.sha256((ROOT / pin["path"]).read_bytes()).hexdigest() == pin["sha256"],
                 "source pin: " + pin["path"])
    word = json.loads(gzip.decompress((ROOT / "research/e8-bit-r420/data/bitE8mut-r420.json.gz").read_bytes()))
    prior = load("prior", ROOT / "research/r420-decoder-sharing/verify.py")
    audit = load("audit", ROOT / "research/r420-decoder-sharing/audit.py")
    independent = load("triple_independent", HERE / "independent.py")
    initial = json.loads((HERE / "PREDECESSOR.json").read_text())["chain"]
    rows = [set(g[2]) for g in word["A"][-9:]]
    pool = sorted(set.union(*rows) - set(word["ret"]))
    need(len(pool) == 80, "helper pool")
    extension, rows, rounds = fixed_point(transform(rows, initial), pool)
    chain = initial + extension
    paths = group()
    histogram, positive = census(rows, pool, paths)
    independent_result = independent.census(rows, pool)
    need(histogram == independent_result["histogram"], "independent complete histogram")
    need(positive == independent_result["positive"], "independent improving matrices")
    fixed = construct(word, chain)
    checker = prior.load_checker()
    words = {"original": word, "pr1206": construct(word, initial), "fixed": fixed}
    escapes = []
    for entry in positive:
        state = tuple(entry["state"])
        alternatives = shortest_paths(state, paths)
        need(len(alternatives) == 1, "positive matrix has another shortest preparation")
        gates = [[entry["helpers"][a], entry["helpers"][b]] for a, b in alternatives[0]]
        inverse_state = IDENTITY
        for a, b in reversed(alternatives[0]):
            inverse_state = step(inverse_state, a, b)
        need(len(shortest_paths(inverse_state, paths)) == 1, "another shortest restoration")
        unilateral = [sum(1 if b in r else -1 for r in rows if a in r) - 2 for a, b in gates]
        candidate = construct(word, chain + gates)
        name = "escape" + str(len(escapes))
        words[name] = candidate
        bill = prefix_bounds(candidate)
        need(not bill["native_104_bit_admitted"], "an escape passes the precision screen")
        need(entry["gain"] == 1 and max(unilateral) <= 0, "escape premise changed")
        escapes.append({**entry, "gates": gates, "unilateral_gains": unilateral,
                        "shortest_preparations": 1, "shortest_restorations": 1,
                        "bounds": bill})
    checks = {}
    for name, candidate in words.items():
        _, _, _, hypotheses, conclusions, _ = checker.check(candidate)
        need(all(hypotheses.values()) and all(conclusions.values()), name + " original H1-H5")
        comparison = audit.compare(word, candidate)
        need(comparison["status"] == "PASS", name + " full dirty/frame comparison")
        checks[name] = {"canonical_sha256": hashlib.sha256(canonical(candidate)).hexdigest(),
                       "complete_ADDs": prior.additions(candidate), "bounds": prefix_bounds(candidate),
                       "columns": comparison["symbolic_columns"],
                       "checks": comparison["checks"]}
    controls = []

    def reject(name, action):
        try:
            action()
        except (ValueError, checker.Reject):
            controls.append(name)
        else:
            raise ValueError("accepted control: " + name)

    candidate = words["escape1"]
    missing = copy.deepcopy(candidate)
    missing["A"].pop()
    reject("missing helper restoration", lambda: need(audit.compare(word, missing)["status"] == "PASS", "dirty mismatch"))
    wrong = copy.deepcopy(candidate)
    length = len(chain) + 2
    wrong["A"][-length:] = wrong["A"][-length:][::-1]
    reject("forward order restoration", lambda: need(audit.compare(word, wrong)["status"] == "PASS", "order mismatch"))
    wrong = copy.deepcopy(candidate)
    wrong["A"][-length-9:-length] = word["A"][-9:]
    reject("untransformed decoder", lambda: need(audit.compare(word, wrong)["status"] == "PASS", "read mismatch"))
    stale = copy.deepcopy(candidate)
    stale["C"] = word["C"]
    checker.Word(stale).full()
    reject("scalar valid stale cleanup", lambda: need(checker.Word(stale).interface()[0]["H4_C_literal_reverse_at_full"], "H4"))
    early = copy.deepcopy(candidate)
    early["A"][-2*length-9][0] = 0
    reject("wrong preparation frame", lambda: checker.Word(early).full())
    reject("retained helper operand", lambda: construct(word, [[word["ret"][0], pool[0]]]))
    reject("unpaid restoration cost", lambda: need(
        prior.additions(fixed) - prior.additions(candidate) ==
        2 * (positive[1]["gain"] + positive[1]["shortest_length"]), "literal invoice differs"))
    reject("admit over-budget escape", lambda: need(escapes[0]["bounds"]["native_104_bit_admitted"], "precision"))
    incomplete = dict(paths)
    incomplete.pop(tuple(positive[1]["state"]))
    reject("missing improving matrix", lambda: validate_group(incomplete))
    need(checks["original"]["bounds"]["native_104_bit_admitted"], "precision positive control")
    report = {"status": "PASS_R420_TRIPLE_BASES_PRECISION_BOUNDARY", "seed": 1,
              "pool": pool, "extension": extension, "single_shear_rounds": rounds,
              "group_distance_histogram": dict(sorted(Counter(map(len, paths.values())).items())),
              "triples": 82160, "matrices_per_triple": 168, "cases": sum(histogram.values()),
              "gain_histogram": histogram, "escapes": escapes, "words": checks,
              "independent_cases": independent_result["cases"], "negative_controls": controls,
              "new_kappa": False}
    report = json.loads(json.dumps(report))
    if args.report:
        print(json.dumps(report, indent=2))
    else:
        need(report == json.loads((HERE / "CERTIFICATE.json").read_text()), "certificate mismatch")
        print("PASS_R420_TRIPLE_BASES_PRECISION_BOUNDARY cases=13802880 escapes=4 admitted=0 columns=660 controls=9 no_new_kappa")
    if args.output:
        args.output.mkdir(parents=True, exist_ok=False)
        for name, candidate in words.items():
            (args.output / (name + ".json")).write_bytes(canonical(candidate) + b"\n")


if __name__ == "__main__":
    main()
