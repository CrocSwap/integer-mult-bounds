#!/usr/bin/env python3
"""Exact finite verification of the PR589 dirty block-509 replacement.

Prepared for anudeepadi with substantial OpenAI Codex assistance; Apache-2.0.
Uses eumemic's unchanged PR555 checker for geometry and H1-H5; the truth
table, set-valued replay, path comparison and positive matrices below are
separate implementations. No full multiplication theorem is claimed.
"""
import argparse
import copy
import gzip
import hashlib
import importlib.util
import json
from collections import Counter
from itertools import pairwise
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz"
CHECKER = "research/e8-bit-p111-tuned/code/xcheck_p.py"
REGISTERS = [17, 22, 33, 38, 50, 60, 67, 77, 87, 92, 468]


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sources():
    pins = json.loads((HERE / "SOURCES.json").read_text())
    for name, expected in pins["files"].items():
        need(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected,
             "Source hash mismatch: " + name)
    return pins


def cleanup(word):
    v = word["v"]
    full = next(i for i, frame in enumerate(word["frames"]) if len(frame) == v)
    word["C"] = [[full, d, list(ss)] for _, d, ss in reversed(word["A"] + word["B"])
                 if not v <= d < 2 * v]


def build(word, recipe):
    need((recipe["phase"], recipe["start"], recipe["stop"], recipe["frame"])
         == ("B", 283, 314, 509), "Wrong block")
    need(recipe["registers"] == REGISTERS, "Register identities changed")
    ops = recipe["replacement_local_ops"]
    need(all(len(op) == 2 and all(type(i) is int and 0 <= i < 11 for i in op)
             and op[0] != op[1] for op in ops), "Invalid local operation")
    candidate = copy.deepcopy(word)
    candidate["B"][283:314] = [[509, REGISTERS[d], [REGISTERS[s]]] for d, s in ops]
    cleanup(candidate)
    return candidate


def truth_table(gates):
    index = {r: i for i, r in enumerate(REGISTERS)}
    table = []
    for value in range(1 << 11):
        wires = [(value >> i) & 1 for i in range(11)]
        for frame, d, ss in gates:
            need(frame == 509 and len(ss) == 1, "Not a binary block-509 gate")
            need(d in index and ss[0] in index and d != ss[0], "Unexpected block wire")
            wires[index[d]] = (wires[index[d]] + wires[index[ss[0]]]) % 2
        table.append(sum(bit << i for i, bit in enumerate(wires)))
    return table


def positive_matrix(gates):
    index = {r: i for i, r in enumerate(REGISTERS)}
    matrix = [[int(i == j) for j in range(11)] for i in range(11)]
    for _, d, ss in gates:
        need(len(ss) == 1, "Nonbinary positive transfer")
        a, b = index[d], index[ss[0]]
        matrix[a] = [x + y for x, y in zip(matrix[a], matrix[b])]
    return matrix


def set_replay(word):
    """Each set lists independent input columns, including every dirty helper."""
    v = word["v"]
    values = [{r} for r in range(2 * v + word["R"])]
    after_b = None
    for phase in ("D", "A", "scatter", "B", "C"):
        if phase == "scatter":
            retained = [values[r].copy() for r in word["ret"]]
            for t, row in enumerate(word[phase]):
                for k in row:
                    values[v + t].symmetric_difference_update(retained[k])
        else:
            for _, d, ss in word[phase]:
                for s in ss:
                    values[d].symmetric_difference_update(values[s])
        if phase == "B":
            after_b = [sorted(row) for row in values]
    expected = [{r, r - v} if v <= r < 2 * v else {r} for r in range(len(values))]
    need(values == expected, "Independent arbitrary-input endpoint failed")
    return {"columns": len(values), "after_B_sha256": digest(after_b),
            "endpoint_sha256": digest([sorted(row) for row in values])}


def paths(word):
    result = [[f] for f in word["start"]]
    for phase in ("D", "A", "B", "C"):
        for f, d, ss in word[phase]:
            for r in [d] + ss:
                if result[r][-1] != f:
                    result[r].append(f)
    for r, f in enumerate(word["final"]):
        if result[r][-1] != f:
            result[r].append(f)
    return result


def invoice(word):
    counts = {phase: sum(len(ss) for _, _, ss in word[phase]) for phase in ("D", "A", "B", "C")}
    counts["scatter"] = sum(map(len, word["scatter"]))
    counts["total"] = sum(counts.values())
    return counts


def controls(original, candidate, checked, reference, block):
    results = {}

    def must_fail(name, action, message):
        try:
            action()
        except (ValueError, reference.Reject) as error:
            need(message in str(error), name + " rejected for an unexpected reason: " + str(error))
            results[name] = str(error)
        else:
            raise ValueError("Control accepted: " + name)

    old_table = truth_table(original["B"][283:314])
    must_fail("deleted_block_gate", lambda: need(truth_table(block[1:]) == old_table,
              "Block map differs"), "Block map differs")
    wrong = copy.deepcopy(block)
    wrong[12][2] = [87]  # The factored read needs 17, not just one summand.
    must_fail("wrong_common_sum_read", lambda: need(truth_table(wrong) == old_table,
              "Block map differs"), "Block map differs")
    mutant = copy.deepcopy(candidate)
    del mutant["C"][0]
    must_fail("omitted_cleanup", lambda: set_replay(mutant), "endpoint failed")
    mutant = copy.deepcopy(candidate)
    mutant["B"][283][0] = checked.ZERO
    audit = copy.copy(checked)
    audit.w = mutant
    must_fail("unpaid_frame_zero", audit.full, "climb not nested")
    mutant = copy.deepcopy(candidate)
    mutant["C"] = copy.deepcopy(original["C"])
    audit = copy.copy(checked)
    audit.w = mutant
    audit.full()  # Equal inverse maps: deliberately NOT a scalar counterexample.
    h, c, _ = audit.interface()
    need(not h["H4_C_literal_reverse_at_full"] and all(c.values()), "Stale C control misclassified")
    results["stale_cleanup"] = "scalar endpoint passes; literal H4 fails"
    wrong_matrix = positive_matrix(block)
    wrong_matrix[0][0] += 2  # Same F2 map, but invalid positive invoice.
    before = positive_matrix(original["B"][283:314])
    must_fail("parity_invisible_positive_inflation", lambda: need(
        all(b <= a for row_a, row_b in zip(before, wrong_matrix) for a, b in zip(row_a, row_b)),
        "Positive transfer increased"), "Positive transfer increased")
    # A test that silently fixes the incoming carrier to zero misses its lost identity term.
    clean_only = old_table[:1024]
    dropped_carrier = old_table[:1024] + old_table[:1024]
    need(dropped_carrier[:1024] == clean_only, "Dirty-input scope control broken")
    need(dropped_carrier != old_table, "Dirty carrier was not independently tested")
    results["zero_carrier_scope_control"] = "1024 clean-carrier inputs pass; full 2048-input test rejects"
    return results


def verify():
    pins = sources()
    original = json.loads(gzip.decompress((ROOT / SOURCE).read_bytes()))
    recipe = json.loads((HERE / "recipe.json").read_text())
    search = load_module("p111_block509_search", HERE / "search.py")
    need(recipe == search.synthesize(), "Recipe or bounded-search coverage differs")
    need(recipe["source"] == SOURCE and recipe["source_sha256"] == pins["files"][SOURCE],
         "Recipe source is not pinned")
    candidate = build(original, recipe)
    old = original["B"][283:314]
    new = candidate["B"][283:283 + len(recipe["replacement_local_ops"])]
    need(len(old) == 31 and len(new) == 26, "Unexpected circuit length")
    need(truth_table(old) == truth_table(new), "Block map differs")
    need(paths(original) == paths(candidate), "Register frame path changed")
    need(all(original[k] == candidate[k] for k in original if k not in ("B", "C")),
         "Exterior word field changed")
    transfers = {}
    for name, before, after in (("forward", old, new), ("reverse", old[::-1], new[::-1])):
        a, b = positive_matrix(before), positive_matrix(after)
        need(all(y <= x for ar, br in zip(a, b) for x, y in zip(ar, br)), "Positive transfer increased")
        transfers[name] = {"baseline": a, "candidate": b, "entrywise_nonincreasing": True}
    independent_old, independent_new = set_replay(original), set_replay(candidate)
    need(independent_old == independent_new, "Complete operator differs")
    reference = load_module("p111_block509_reference", ROOT / CHECKER)
    checked, labels, full, h, c, _ = reference.check(candidate)
    need(all(h.values()) and all(c.values()), "Original interface failed")
    baseline_check = copy.copy(checked)
    baseline_check.w = original
    baseline_check.full()
    h0, c0, _ = baseline_check.interface()
    need(all(h0.values()) and all(c0.values()), "Baseline interface failed")
    profile = Counter()
    for path in paths(candidate):
        for a, b in pairwise(path):
            profile[checked.fdim[b] - checked.fdim[a]] += 1
    copies = [row["rank"] for row in full["totals"]]
    profile.update(copies)
    need(copies == [7] * 9 and sum(rank * count for rank, count in profile.items()) == 5129,
         "Paid mass or copied ranks changed")
    bills = {"baseline": invoice(original), "candidate": invoice(candidate)}
    need(bills["baseline"]["total"] == 24305 and bills["candidate"]["total"] == 24295,
         "Incorrect complete XOR accounting")
    report = {"status": "PASS_P111_DIRTY_BLOCK509", "base_commit": pins["base_commit"],
              "baseline_word_sha256": digest(original), "candidate_word_sha256": digest(candidate),
              "recipe_sha256": digest(recipe), "local_inputs_checked": 2048,
              "local_gates": {"baseline": 31, "candidate": 26},
              "independent_replay": independent_new, "labels": labels,
              "hypotheses": h, "conclusion": c, "unchanged_register_paths": len(paths(candidate)),
              "local_paid_profile": dict(sorted(profile.items())), "local_rank_mass": 5129,
              "retained_copy_ranks": copies, "scalar_additions": bills,
              "positive_transfer": transfers,
              "controls": controls(original, candidate, checked, reference, new),
              "scope": "Finite circuit and inherited H1-H5; no new supplier exponent or kappa."}
    return original, candidate, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Fresh directory for both complete words and result")
    parser.add_argument("--write-certificate", action="store_true", help="Record the fully checked local certificate")
    args = parser.parse_args()
    if args.output:
        need(not args.output.exists(), "Output directory already exists")
    original, candidate, report = verify()
    receipt = HERE / "CERTIFICATE.json"
    if args.write_certificate:
        receipt.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        need(canonical(report) == canonical(json.loads(receipt.read_text())), "Certificate differs")
    if args.output:
        args.output.mkdir(parents=True)
        for name, word in (("baseline", original), ("candidate", candidate)):
            (args.output / (name + ".json.gz")).write_bytes(gzip.compress(canonical(word), mtime=0))
        (args.output / "RESULT.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print("PASS_P111_DIRTY_BLOCK509 block=31->26 ADDs=24305->24295 inputs=2048 columns=661 controls=7 no_new_kappa")


if __name__ == "__main__":
    main()
