#!/usr/bin/env python3
"""Cold, deterministic certificate replay; standard library only, Python >=3.12."""
import argparse
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import random

from checks import (need, ordered_trees, free_replay, dense_replay, invoice,
                    nonlinear_replay, check_record)
import borrow

ROOT = Path(__file__).resolve().parent
FIXTURES = (1, 2, 3, 4, 5, 8, 16, 27, 56, 64)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True).encode("ascii")


def sha(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def read_json(path):
    return json.loads(path.read_text(), object_pairs_hook=unique_pairs,
                      parse_constant=lambda s: need(False, "nonfinite JSON number"))


def sources():
    manifest = read_json(ROOT/"SOURCES.json")
    need(manifest["base_commit"] == "2921874911956718fcaaaf9396fe8267b3cfa9f0", "base pin")
    need(manifest["selected_kappa_at_base"] == "1661960547713947/1000000000000000000", "frontier pin")
    expected_vendor = {
        "vendor/pr822/reuse.py": "884a6c51d1173d6d07d31f480b6a710032b343b4",
        "vendor/pr822/NOTICE.md": "ee5da605c4a33f6d181bd5a04657313582a37fac",
        "vendor/pr822/PROOF.md": "236095404e7d1176b65a5f3160f6656d436a00c3",
    }
    need(set(manifest["vendor_files"]) == set(expected_vendor), "vendor inventory")
    for path, pin in manifest["vendor_files"].items():
        raw = (ROOT/path).read_bytes()
        blob = hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
        need(blob == pin["git_blob"] == expected_vendor[path], "original Git blob pin")
        need(hashlib.sha256(raw).hexdigest() == pin["sha256"], "vendor SHA256 pin")
        need(pin["source_commit"] == "8c5e1b557f59bca29139c4c2dcc65edfb808372b", "predecessor commit pin")
        need(pin["source_path"] == "research/echo-connector-reuse/"+Path(path).name, "predecessor path pin")
    required = {"borrow.py", "checks.py", "verify.py", "test_package.py"}
    need(set(manifest["implementation_sha256"]) == required, "implementation inventory")
    for path, digest in manifest["implementation_sha256"].items():
        need(hashlib.sha256((ROOT/path).read_bytes()).hexdigest() == digest, "implementation pin: "+path)
    return manifest


def predecessor():
    spec = importlib.util.spec_from_file_location("pinned_pr822", ROOT/"vendor/pr822/reuse.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def multiplicities(tree, multiplier=1):
    if type(tree) is int:
        return [multiplier]
    result = []
    weights = (2, 2) if len(tree) == 2 else (2, 4, 2)
    for child, weight in zip(tree, weights):
        result += multiplicities(child, multiplier*weight)
    return result


def nodes(tree):
    return 1 if type(tree) is int else 1+sum(nodes(c) for c in tree)


def dense_factors(n, length):
    # Finite domain, not a random search. Every row has norm at most two.
    rng = random.Random(56*1000+n*10+length)
    result = []
    for factor in range(n):
        matrix = [[0]*length for _ in range(length)]
        for row in range(length):
            for column in rng.sample(range(length), 2):
                matrix[row][column] = rng.choice((-1, 1))
        result.append(matrix)
    if length == 2:
        result[0] = [[1, 1], [0, 1]]
        if n > 1:
            result[1] = [[1, 0], [1, 1]]
    return result


def expect_rejection(function, message):
    try:
        function()
    except ValueError:
        return message
    raise ValueError("negative control unexpectedly accepted: "+message)


def mathematical_controls(tree8):
    labels = []
    word = list(borrow.instructions(((0, 1), 2, (3, 4))))
    bound = borrow.norm_bound(((0, 1), 2, (3, 4)), 2)
    for label, mutant in [
        ("omit cleanup leaf", word[:-1]),
        ("wrong sign", [(s, d, i, -q) if j == 0 else (s, d, i, q)
                         for j, (s, d, i, q) in enumerate(word)]),
        ("reverse factor order", [(s, d, 4-i, q) for s, d, i, q in word]),
    ]:
        labels.append(expect_rejection(lambda: free_replay(mutant, 5, 5, 1, bound), label))
    for label, record in [
        ("aliased ports", (1, 1, 0, 1)),
        ("write protected source", (1, 0, 0, 1)),
        ("out-of-range port", (0, 5, 0, 1)),
        ("boolean instruction integer", (False, 1, 0, 1)),
        ("zero sign", (0, 1, 0, 0)),
    ]:
        labels.append(expect_rejection(lambda: check_record(record, 5, 5), label))
    for label, f in [
        ("nonconsecutive leaves", lambda: list(borrow.instructions((1, 0)))),
        ("boolean leaf", lambda: list(borrow.instructions((False, 1)))),
        ("unary node", lambda: list(borrow.instructions((0,)))),
        ("negative pool", lambda: list(borrow.instructions((0, 1), -1))),
        ("noninteger pool", lambda: list(borrow.instructions((0, 1), 2.0))),
        ("invalid direction", lambda: list(borrow.instructions((0, 1), sign=0))),
        ("too few ports", lambda: list(borrow.instructions(((0, 1), (2, 3)), 1))),
        ("underpriced prefix", lambda: free_replay(word, 5, 5, 1, 1)),
    ]:
        labels.append(expect_rejection(f, label))
    initial = [-7, -4, -1, 2, 5]
    nonlinear_word = list(borrow.instructions(tree8))
    corrupted = nonlinear_replay(nonlinear_word, initial)
    need(corrupted == [-7, 23, 5, 2, 5], "fixed nonlinear witness changed")
    restored = nonlinear_replay([(s, d, i, -q) for s, d, i, q in reversed(nonlinear_word)], corrupted)
    need(restored == initial, "nonlinear full inverse failed")
    old = predecessor()
    old_budget = old.resources(tree8, [1]*8)[0]
    old_initial = [-7, -4]+[-1, 2, 5][:old_budget]
    old_final = nonlinear_replay(list(old.instructions(tree8, old_budget)), old_initial)
    need(old_final[:1]+old_final[2:] == old_initial[:1]+old_initial[2:], "old nonlinear restoration")
    return {"rejections": labels, "nonlinear_boundary": {
        "tree": tree8, "initial": initial, "borrowed_final": corrupted,
        "literal_inverse_final": restored, "sibling_initial": old_initial,
        "sibling_final": old_final}}


def compute():
    pins = sources()
    old = predecessor()
    bills, plans, candidate_count = borrow.unit_plan(64)
    coverage, free_checks, comparable_words = [], 0, 0
    small_max_terms = 0
    for n in range(1, 8):
        trees = ordered_trees(n)
        coverage.append({"factors": n, "trees": len(trees)})
        minimum = None
        for tree in trees:
            _, calls, reserved, sibling, depth = borrow.resources(tree)
            need(old.resources(tree, [1]*n) == (sibling, calls), "predecessor resource mismatch")
            minimum = calls if minimum is None else min(minimum, calls)
            positive = list(borrow.instructions(tree))
            negative = list(borrow.instructions(tree, sign=-1))
            need(negative == [(s, d, i, -q) for s, d, i, q in reversed(positive)], "literal inverse mismatch")
            need(len(positive) == calls == sum(multiplicities(tree)), "literal call bill")
            prior = list(old.instructions(tree, sibling))
            need([(i, q) for s, d, i, q in positive] == [(i, q) for s, d, i, q in prior], "changed factor/sign word")
            comparable_words += 1
            h = borrow.norm_bound(tree, 2)
            for q, word in [(1, positive), (-1, negative)]:
                evidence = free_replay(word, n, 5, q, h)
                small_max_terms = max(small_max_terms, evidence["peak_terms_per_row"])
                free_checks += 1
        need(minimum == bills[n], "DP disagrees with exhaustive tree minimum")
    need(sum(c["trees"] for c in coverage) == 861, "small tree coverage")
    fixtures = []
    for n in FIXTURES:
        tree = plans[n-1]
        _, calls, reserved, sibling, depth = borrow.resources(tree)
        need(calls == bills[n], "DP witness bill")
        need(old.resources(tree, [1]*n) == (sibling, calls), "large predecessor resources")
        words = {
            "borrowed": (3, list(borrow.instructions(tree))),
            "sibling": (sibling, list(old.instructions(tree, sibling))),
            "reserved": (reserved, list(borrow.reserved_instructions(tree))),
        }
        free = {}
        for q in (1, -1):
            word = list(borrow.instructions(tree, sign=q))
            free[str(q)] = free_replay(word, n, 5, q, borrow.norm_bound(tree, 2))
            free_checks += 1
        dense = {}
        for length in (2, 3):
            matrices = dense_factors(n, length)
            k = max(1, max(sum(abs(a) for a in row) for m in matrices for row in m))
            need(k <= 2, "factor norm domain")
            h = borrow.norm_bound(tree, k)
            initial_max = 7
            precision = (initial_max*h).bit_length()+1
            for allocator, (dirty, word) in words.items():
                rows = dirty+2
                initial = [[((r*length+j)*3) % 15-7 for j in range(length)] for r in range(rows)]
                bill = invoice(word, n, rows, length, precision, nodes(tree), multiplicities(tree))
                for q in (1, -1):
                    actual_word = word if q == 1 else [(s, d, i, -sign) for s, d, i, sign in reversed(word)]
                    actual = dense_replay(actual_word, matrices, initial, q, initial_max*h)
                    actual_bill = invoice(actual_word, n, rows, length, precision, nodes(tree), multiplicities(tree))
                    for key in ("multiplications", "add_subtract", "zero_assignments", "reads", "writes", "primitive_commands", "head_steps_cells"):
                        need(actual[key] == actual_bill[key], "dense invoice mismatch: "+key)
                    need(actual["peak_absolute_scalar_or_data"] < 2**(precision-1), "signed precision headroom")
                    dense[f"{allocator}_L{length}_sign{q}"] = {"invoice": actual_bill, "replay": actual}
        binary = borrow.balanced_binary(n)
        binary_word = list(borrow.instructions(binary, dirty_rows=2))
        free_replay(binary_word, n, 4, 1, borrow.norm_bound(binary, 2))
        free_checks += 1
        fixtures.append({
            "factors": n, "tree": tree, "calls": calls, "depth": depth,
            "dirty_rows": {"borrowed_cap": 3, "sibling": sibling, "reserved": reserved},
            "leaf_multiplicities": multiplicities(tree), "norm_bound_K2": borrow.norm_bound(tree, 2),
            "word_sha256": {name: sha(word) for name, (s, word) in words.items()},
            "free_module": free, "dense": dense,
            "balanced_binary": {"calls": len(binary_word), "borrowed_cap": 2,
                                "reserved": borrow.resources(binary)[2]},
        })
    main = next(row for row in fixtures if row["factors"] == 56)
    need((main["calls"], main["dirty_rows"]["sibling"], main["dirty_rows"]["reserved"]) == (1568, 5, 9), "primary comparator")
    need(old.optimize([1]*56, 5)[0] == 1568, "pinned five-row DP comparator")
    old_four_row_control = expect_rejection(lambda: old.optimize([1]*56, 4),
                                            "PR822 four-row cap infeasible at n=56")
    return {
        "schema": 1, "seed": 56, "contract": "exact additive endomorphisms only",
        "source_manifest_sha256": hashlib.sha256((ROOT/"SOURCES.json").read_bytes()).hexdigest(),
        "base_commit": pins["base_commit"], "coverage": coverage,
        "free_module_checks": free_checks, "small_factor_sign_word_comparisons": comparable_words,
        "small_max_terms_per_row": small_max_terms,
        "predecessor_capacity_control": old_four_row_control,
        "unit_planner": {"limit": 64, "candidates": candidate_count, "bills": bills[1:]},
        "fixtures": fixtures, "controls": mathematical_controls(plans[7]),
        "selected_kappa_changed": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="author: regenerate EXPECTED.json")
    parser.add_argument("--receipt", type=Path, help="write recomputed receipt to an external path")
    args = parser.parse_args()
    result = compute()
    if args.write:
        (ROOT/"EXPECTED.json").write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
    else:
        need(canonical(result) == canonical(read_json(ROOT/"EXPECTED.json")), "certificate differs from replay")
    if args.receipt:
        args.receipt.write_bytes(canonical(result)+b"\n")
    print(json.dumps({"status": "PASS", "receipt_sha256": sha(result), "trees": 861,
                      "free_module_checks": result["free_module_checks"],
                      "primary_calls": 1568, "primary_dirty_rows": 3,
                      "primary_sibling_rows": 5, "kappa_changed": False}, sort_keys=True))


if __name__ == "__main__":
    main()
