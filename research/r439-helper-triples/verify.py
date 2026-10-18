#!/usr/bin/env python3
"""Independent finite verification of the bounded R439 helper-triple search.

Ross Richardson, with substantial OpenAI Codex assistance. Apache-2.0.
Reuses the pinned PR926 owning/native checkers with their credit intact.
"""
import argparse
import copy
import gzip
import hashlib
import itertools
import json
from pathlib import Path
import random
import runpy
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PRE = ROOT / "research/r439-two-sided-compensation"
C = runpy.run_path(str(PRE / "common.py"))
V = runpy.run_path(str(PRE / "verify.py"))
need = C["need"]
load = C["load"]


def same(a, b, message):
    need(C["canonical"](a) == C["canonical"](b), message)


def check_pins():
    manifest = load(HERE / "SOURCES.json")
    for name, expected in manifest["files"].items():
        need(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected,
             "source pin: " + name)
    C["pins"](ROOT)
    return manifest


def invert(matrix):
    """Ordinary Boolean Gaussian elimination; no builder or word reversal."""
    rows = [[(matrix[i] >> j) & 1 for j in range(3)] + [int(i == j) for j in range(3)]
            for i in range(3)]
    for j in range(3):
        pivot = next((i for i in range(j, 3) if rows[i][j]), None)
        need(pivot is not None, "singular triple matrix")
        rows[j], rows[pivot] = rows[pivot], rows[j]
        for i in range(3):
            if i != j and rows[i][j]:
                rows[i] = [a ^ b for a, b in zip(rows[i], rows[j])]
    return [[rows[i][3 + j] for j in range(3)] for i in range(3)]


def check_group(entries):
    # Enumerate every independent ordered triple directly, independently of BFS.
    domain = set()
    for rows in itertools.product(range(1, 8), repeat=3):
        span = {0}
        for row in rows:
            span |= {x ^ row for x in tuple(span)}
        if len(span) == 8:
            domain.add(rows)
    need(len(domain) == 168, "direct GL(3,2) domain")
    words = {}
    for entry in entries:
        matrix, word = tuple(entry["matrix"]), entry["word"]
        need(matrix in domain and matrix not in words, "group domain or duplicate")
        current = [[int(i == j) for j in range(3)] for i in range(3)]
        for operation in word:
            need(len(operation) == 2 and all(type(x) is int and 0 <= x < 3 for x in operation),
                 "typed triple operation")
            d, s = operation
            need(d != s, "self operation")
            current[d] = [a ^ b for a, b in zip(current[d], current[s])]
        same([sum(b << j for j, b in enumerate(row)) for row in current], list(matrix), "word matrix")
        words[matrix] = word
    need(set(words) == domain and words[(1, 2, 4)] == [], "complete group")
    # Realizing paths give upper bounds; all neighbor inequalities give lower bounds.
    # Therefore these lengths are exact distances for all six directed generators.
    edges = 0
    for matrix, word in words.items():
        for d in range(3):
            for s in range(3):
                if d == s:
                    continue
                nxt = list(matrix)
                nxt[d] ^= nxt[s]
                need(abs(len(word) - len(words[tuple(nxt)])) <= 1, "group distance edge")
                edges += 1
    return words, edges


def literal_bill(word):
    bill = V["bill"](word)
    f, b = bill["F"], bill["B"]
    return {k: bill[k] for k in ("F", "B", "D_adds", "native_ADDs")} | {
        "local_expression": 64 * f ** 3 * b ** 2,
        "nine_stage_expression": (1 << 18) * f ** 5 * b ** 4}


def assemble(parent, rows, target, pairs, replacements):
    transformed = [set(row) for row in rows]
    operations = []
    for index, pair in enumerate(pairs):
        if index in replacements:
            c, word = replacements[index]
            labels = [*pair, c]
            operations.extend((labels[d], labels[s]) for d, s in word)
        else:
            operations.append(pair)
    for d, s in operations:
        for row in transformed:
            if d in row:
                row.symmetric_difference_update({s})
    v = parent["v"]
    preparation = [[0, 2 * v + d, [2 * v + s]] for d, s in operations]
    middle = [[0, v + i, [2 * v + j for j in sorted(row)]] for i, row in enumerate(transformed)]
    result = copy.deepcopy(parent)
    result["D"] = preparation + target + middle + target[::-1] + preparation[::-1]
    return result, len(preparation)


def independent_search(original, parent, previous, candidate, certificate):
    words, edges = check_group(certificate["group"])
    rows, _, target = V["frozen_parent"](original, parent)
    pairs = V["helper_pairs"](load(PRE / "CERTIFICATE.json"), original["R"])
    columns = [{i for i, row in enumerate(rows) if j in row} for j in range(original["R"])]
    singletons = sorted(set(range(original["R"])) - {j for pair in pairs for j in pair})
    inverse = {matrix: invert(matrix) for matrix in words}
    rng = random.Random(12)
    census_hash, nominees, scores = hashlib.sha256(), [], 0
    for index, (a, b) in enumerate(pairs):
        for c in singletons:
            local = [columns[a], columns[b], columns[c]]
            sums = {}
            for bits in itertools.product((0, 1), repeat=3):
                support = set()
                for bit, column in zip(bits, local):
                    if bit:
                        support.symmetric_difference_update(column)
                sums[bits] = len(support)
            old_cost = 2 + len(columns[a]) + len(columns[a] ^ columns[b]) + len(columns[c])
            for matrix in sorted(words):
                word = words[matrix]
                new_cost = 2 * len(word) + sum(sums[tuple(inverse[matrix][i][j] for i in range(3))]
                                                for j in range(3))
                gain, tie = old_cost - new_cost, rng.getrandbits(64)
                census_hash.update(C["canonical"]([index, c, list(matrix), gain, tie]) + b"\n")
                scores += 1
                if gain > 0:
                    nominees.append((-gain, tie, index, c, matrix, word))
    same(scores, certificate["scores"], "complete search count")
    same(scores, 192 * 55 * 168, "declared search domain")
    same(census_hash.hexdigest(), certificate["census_sha256"], "independent entire census")
    same(len(nominees), certificate["positive_nominees"], "positive census")
    same((len(pairs), len(singletons)), (certificate["pair_count"], certificate["singleton_count"]), "domain dimensions")
    baseline, _ = assemble(parent, rows, target, pairs, {})
    same(baseline, previous, "PR926 reconstruction")
    same(literal_bill(baseline), certificate["baseline"], "baseline literal bill")
    replacements, used, accepted, rejected, conflicts = {}, set(), [], [], 0
    instructions = 0
    for neg_gain, tie, index, c, matrix, word in sorted(nominees):
        if index in replacements or c in used:
            conflicts += 1
            continue
        trial_replacements = {**replacements, index: (c, word)}
        trial, _ = assemble(parent, rows, target, pairs, trial_replacements)
        bill = literal_bill(trial)
        instructions += 2 * len(V["stream"](trial))
        entry = {"pair_index": index, "singleton": c, "matrix": list(matrix), "word": word,
                 "gain": -neg_gain, "bill": bill}
        if bill["local_expression"] >= 1 << 104 or bill["nine_stage_expression"] >= 1 << 192:
            rejected.append(entry)
        else:
            replacements, used = trial_replacements, used | {c}
            accepted.append(entry)
    for name, value in (("accepted", accepted), ("rejected", rejected), ("conflicts", conflicts)):
        same(value, certificate[name], "guarded pass: " + name)
    rebuilt, h = assemble(parent, rows, target, pairs, replacements)
    same(rebuilt, candidate, "independently rebuilt word")
    same(literal_bill(candidate), certificate["result"], "candidate literal bill")
    same(C["digest"](candidate), certificate["candidate_sha256"], "candidate canonical digest")
    same(sum(x["gain"] for x in accepted), certificate["saved_ADDs"], "all restoration costs")
    need(certificate["baseline"]["native_ADDs"] - certificate["result"]["native_ADDs"] == certificate["saved_ADDs"], "total saving")
    return {"group_matrices": len(words), "distance_edges": edges, "scores": scores,
            "guarded_words": len(accepted) + len(rejected), "literal_positive_instructions": instructions,
            "accepted": len(accepted), "rejected": len(rejected), "helper_preparations": h}, h


def controls(original, candidate, certificate, reference, h):
    names = []

    def bad_boundary(name, changed):
        need(V["boundary_columns"](changed) != reference, "control incorrectly accepted: " + name)
        names.append(name)

    changed = copy.deepcopy(candidate)
    del changed["D"][:h]
    observed = V["boundary_columns"](changed)
    need(observed[:222] == reference[:222] and observed[222:] != reference[222:], "dirty-helper control separation")
    bad_boundary("omit helper preparation; clean-helper inputs alone miss it", changed)
    changed = copy.deepcopy(candidate)
    del changed["D"][h:h + 306]
    observed = V["boundary_columns"](changed)
    need(observed[222:] == reference[222:] and observed[111:222] != reference[111:222], "dirty-target control separation")
    bad_boundary("omit target preparation; helper-only tests miss it", changed)
    changed = copy.deepcopy(candidate)
    changed["D"][-h:] = changed["D"][:h]
    bad_boundary("restore helper words in forward order", changed)
    changed = copy.deepcopy(candidate)
    changed["D"][-h - 306:-h] = changed["D"][h:h + 306]
    bad_boundary("restore target word in forward order", changed)
    changed = copy.deepcopy(candidate)
    changed["D"].pop()
    bad_boundary("omit helper restoration operation", changed)
    changed = copy.deepcopy(candidate)
    changed["D"].pop(-h - 1)
    bad_boundary("omit target restoration operation", changed)
    changed = copy.deepcopy(candidate)
    changed["D"][h + 306][2].pop()
    bad_boundary("omit transformed middle coefficient", changed)
    changed = copy.deepcopy(candidate)
    for operation in changed["D"][:h]:
        operation[1], operation[2][0] = operation[2][0], operation[1]
    bad_boundary("transpose helper entrance directions", changed)
    # This accepted control ensures restoration work cannot disappear from the bill.
    neutral = copy.deepcopy(candidate)
    neutral["D"][:0] = [[0, 222, [223]], [0, 222, [223]]]
    need(V["boundary_columns"](neutral) == reference, "neutral-pair endpoint")
    need(literal_bill(neutral)["native_ADDs"] == literal_bill(candidate)["native_ADDs"] + 2, "charge cancelling pair")
    # Exact boundary equality is deliberately insufficient to certify the envelope.
    rejected = certificate["rejected"]
    need(rejected and all(x["bill"]["nine_stage_expression"] >= 1 << 192
                         or x["bill"]["local_expression"] >= 1 << 104 for x in rejected), "guard negative controls")
    names.append("all rejected nominees violate an exact integer cap")
    bad_group = copy.deepcopy(certificate["group"])
    bad_group[1]["word"] = []
    try:
        check_group(bad_group)
    except ValueError:
        names.append("corrupt shortest-word certificate")
    else:
        raise ValueError("group mutation accepted")
    return {"rejected": names, "neutral_pair_extra_ADDs": 2}


def run(output, skip_native=False):
    manifest = check_pins()
    certificate = load(HERE / "CERTIFICATE.json")
    need(certificate["format"] == "r439-helper-triples/1" and type(certificate["seed"]) is int
         and certificate["seed"] == 12, "certificate format and seed")
    need(certificate["stopping_rule"] == "one sorted pass through every strict-gain representative; no restart", "stopping rule")
    output.mkdir(parents=True, exist_ok=False)
    print("rebuild entire bounded search", flush=True)
    generated = output / "regenerated"
    subprocess.run([sys.executable, "-I", "-B", str(HERE / "search.py"), "--output", str(generated)], check=True)
    same(load(generated / "CERTIFICATE.json"), certificate, "full certificate regeneration")
    candidate = load(HERE / "candidate.json.gz")
    same(load(generated / "candidate.json.gz"), candidate, "full canonical word regeneration")
    original = load(ROOT / C["WORD"])
    parent = load(PRE / "vendor/pr915/candidate.json.gz")
    previous = load(PRE / "candidate.json.gz")
    print("independent GL(3,2), set-valued census and literal guards", flush=True)
    search, h = independent_search(original, parent, previous, candidate, certificate)
    words = {"baseline": original, "parent": parent, "previous": previous, "candidate": candidate}
    reference = V["boundary_columns"](original)
    for word in words.values():
        V["outside_d"](original, word)
        for reverse in (False, True):
            need(V["boundary_columns"](word, reverse) == reference, "661 arbitrary-input D columns")
    print("all-column restoration, controls and unchanged owning E8 checks", flush=True)
    negative = controls(original, candidate, certificate, reference, h)
    source = V["source_checks"](ROOT, words)
    result = {"status": "PASS_R439_HELPER_TRIPLES_FINITE", "base_commit": manifest["base_commit"],
              "search": search, "bill": certificate["result"], "saved_ADDs": certificate["saved_ADDs"],
              "D_boundary_columns": 661, "D_words_times_directions": 8,
              "controls": negative, "source_checks": source,
              "candidate_sha256": C["digest"](candidate)}
    if not skip_native:
        print("unchanged native legality and 5/9/11-stage checks", flush=True)
        native = runpy.run_path(str(HERE / "native.py"))["run"](
            ROOT, ROOT / C["WORD"], PRE / "vendor/pr915/candidate.json.gz",
            HERE / "candidate.json.gz", output / "native")
        result["native"] = native
        result["source_bound_precision"] = V["nine_stage_bound"](ROOT, native)
    else:
        result["status"] = "PASS_R439_HELPER_TRIPLES_PYTHON_ONLY"
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="new directory retaining all evidence")
    parser.add_argument("--python-only", action="store_true", help="explicitly skip C++ checks; partial evidence")
    parser.add_argument("--record", action="store_true", help="write a new EXPECTED.json; never overwrite")
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="r439-triples-") as temporary:
        output = args.output or Path(temporary) / "run"
        report = run(output, args.python_only)
        if args.record:
            need(not args.python_only, "cannot record incomplete evidence")
            C["write"](HERE / "EXPECTED.json", report)
        elif not args.python_only:
            same(report, load(HERE / "EXPECTED.json"), "entire expected receipt")
        C["write"](output / "REPORT.json", report)
    print(report["status"] + ": 11,980 -> 11,840 ADDs; 40 helper triples; no new kappa")


if __name__ == "__main__":
    main()
