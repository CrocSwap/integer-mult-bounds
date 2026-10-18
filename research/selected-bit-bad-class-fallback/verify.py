#!/usr/bin/env python3
"""Source-bound exact replay; missing evidence never regenerates itself.

Ross Richardson with substantial OpenAI Codex assistance. Apache-2.0.
"""

import argparse
from copy import deepcopy
import hashlib
from itertools import product
import json
from math import gcd
from pathlib import Path
import re
import sys
import tarfile

PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(PACKAGE))
import fallback as F
import oracle as O

ROOT = PACKAGE.parents[1]
INPUTS = (
    "research/complex-t16-rare-pattern-exchanges/upstream1087.tar.gz",
    "research/e8-bit-p111-tuned/tune/EXPECTED.json",
    "research/e8-bit-p111-tuned/vendor/pr510/e8-r480-nine-stage/code/assemble9.py",
    "research/five-stage-source527-banks/proof/three-stage-cover-bit.tex",
    "research/five-stage-source527-banks/proof/three-stage-cover-rows.tex",
)
MEMBER_SHA = "15f6986a476bac76bcdc0bfcf51da115389b46f1950d2766b6822f757888b13a"


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"))
                          .encode()).hexdigest()


def bind_sources(root=ROOT, manifest_path=None):
    manifest = json.loads((manifest_path or PACKAGE / "SOURCES.json").read_text())
    pins = [x for x in manifest["files"] if x["usage"] == "input"]
    F.require(len(pins) == len(INPUTS) and {x["path"] for x in pins} == set(INPUTS),
              "complete external-input set")
    bound = {}
    for entry in pins:
        data = (root / entry["path"]).read_bytes()
        observed = hashlib.sha256(data).hexdigest()
        F.require(observed == entry["sha256"], "source SHA256: " + entry["path"])
        git_blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        F.require(git_blob == entry["git_blob"], "source Git blob: " + entry["path"])
        bound[entry["path"]] = observed
    with tarfile.open(root / INPUTS[0]) as archive:
        member = archive.extractfile("code/assemble.py").read()
    F.require(hashlib.sha256(member).hexdigest() == MEMBER_SHA, "assembler member SHA256")
    text = member.decode()
    match = re.search(r"BIT_L,BIT_T=(\d+),(\d+);BIT_K=\(BIT_L-1\)//2;BIT_M=1\+7\*BIT_L", text)
    F.require(match is not None, "selected BIT dimension binding")
    stages, replicas = map(int, match.groups())
    m = 1 + 7 * stages
    record_pin = next(x for x in pins if x["path"] == INPUTS[1])
    F.require("BIT_BLOB='" + record_pin["git_blob"] + "'" in text,
              "selected assembler binds exact BIT receipt")
    record = json.loads((root / INPUTS[1]).read_text())
    bit, profile = record["nine"]["bit"], record["nine"]["profile"]
    F.require((stages, replicas, m, bit["physical"], bit["maxchild"]) ==
              (9, 32, 64, 28425, 42), "selected context differs")
    F.require(max(map(int, profile)) == bit["maxchild"], "selected maximum rank")
    pricer = (root / INPUTS[2]).read_text()
    F.require("fb = 32 * m * m * E" in pricer and "N = 2 * m" in pricer,
              "retained fallback price binding")
    return {"m": m, "N": 2 * m, "live_roles": bit["live"],
            "physical_roles": bit["physical"], "rank": bit["maxchild"],
            "edge_occurrences": sum(profile.values()),
            "retained_round_child_allowance": 32 * m * m,
            "retained_source_child_allowance": 24 * m * m + 6 * m - 6,
            "input_sha256": bound, "assembler_member_sha256": MEMBER_SHA}


def topology(operations):
    return [op[:3] if op[0] != "sign" else op[:] for op in operations]


def audit_template(plan):
    """All indexed slots are present, even if their coefficients are zero."""
    n = plan["N"]
    additions = [op for op in plan["reductions"] if op[0] == "add"]
    F.require([op[1:3] for op in additions] ==
              [[i, k] for k in range(n) for i in range(n) if i != k],
              "complete fixed shear skeleton")
    F.require([op[1:3] for op in plan["operations"] if op[0] == "pair"] ==
              [[i, n - 1] for i in range(n - 1)], "complete diagonal-pair skeleton")


def expect_rejection(thunk, error, name):
    try:
        thunk()
    except error:
        return name
    raise F.ContractError("control unexpectedly accepted: " + name)


def exhaustive_small_rings():
    rows = []
    for q, w in [(3, 1), (3, 2), (5, 1), (5, 2)]:
        modulus = q ** w
        count, max_swaps, max_additions = 0, 0, 0
        for a, b, c, d in product(range(modulus), repeat=4):
            if (a * d - b * c) % modulus not in {1, modulus - 1}:
                continue
            matrix = [[a, b], [c, d]]
            plan = F.compile_fallback(matrix, q, w)
            O.audit_plan(matrix, plan)
            O.audit_template(plan)
            audit_template(plan)
            F.require(F.execute_rows(plan["lowered_operations"], F.identity(2), modulus)
                      == matrix, "primary/independent small-ring disagreement")
            count += 1
            max_swaps = max(max_swaps, sum(x[0] == "swap" for x in plan["reductions"]))
            max_additions = max(max_additions, sum(x[0] == "add" for x in plan["reductions"]))
        expected = 2 * q ** (3 * w - 2) * (q * q - 1)
        F.require(count == expected, "complete determinant +/-1 census")
        rows.append({"q": q, "w": w, "modulus": modulus, "matrices": count,
                     "maximum_row_swaps": max_swaps, "shear_slots": max_additions})
    return rows


def select_units(modulus, n, offset=0):
    out, x = [], 1 + offset
    while len(out) < n:
        if gcd(x, modulus) == 1:
            out.append(x % modulus)
        x += 1
    return out


def selected_dimension_cases(m, rank):
    rows = []
    for q, w in [(3, 2), (5, 3), (7, 1)]:
        modulus = q ** w
        projector = F.bad_projector(m, rank, q, modulus)
        independent = O.bad_chart_operator(m, rank, q, w)
        F.require(projector == independent["projector"], "independent split-rank chart")
        F.require(F.multiply(projector, projector, modulus) == projector,
                  "split projector identity")
        matrix = F.residual(projector, modulus)
        F.require(matrix == independent["residual"], "independent residual conjugacy")
        F.require(F.multiply(matrix, matrix, modulus) == F.identity(2 * m),
                  "residual involution")
        units = select_units(modulus, m, 1) + [1] * m
        weighted = F.conjugate_diagonal(matrix, units, modulus)
        unweighted_plan = F.compile_fallback(matrix, q, w)
        plan = F.compile_fallback(weighted, q, w)
        F.require(plan["pivots"] == unweighted_plan["pivots"], "diagonal pivot covariance")
        F.require(topology(plan["operations"]) == topology(unweighted_plan["operations"]),
                  "diagonal full-template covariance")
        audit_template(plan)
        O.audit_template(plan)
        O.audit_plan(weighted, plan)
        F.require(F.execute_rows(plan["operations"], F.identity(2 * m), modulus) == weighted,
                  "primary full operator")
        costs = [F.charge(plan, f) for f in (1, 2, 3, 5)]
        for cost in costs:
            F.require(cost["children"] <= cost["source_allowance"] < cost["selected_round_allowance"],
                      "complete fallback allowance")
            F.require(max(cost["reversed_child_histogram"]) <= cost["f"], "child width bound")
        rows.append({"q": q, "w": w, "N": 2 * m, "rank": rank,
                     "projector_sha256": digest(projector), "matrix_sha256": digest(weighted),
                     "plan_sha256": digest(plan), "P00": projector[0][0],
                     "low_P00": projector[0][0] % q, "costs": costs,
                     "operator_coefficients_per_check": (2 * m) ** 2})
    return rows


def high_lift_template_cases():
    rows = []
    for q in (3, 5):
        modulus = q * q
        lows = [a for a in product(range(q), repeat=4)
                if (a[0] * a[3] - a[1] * a[2]) % q in {1, q - 1}]
        classes, lifts = 0, 0
        for low in lows:
            reference = None
            for high in product(range(q), repeat=4):
                v = [a + q * b for a, b in zip(low, high)]
                if (v[0] * v[3] - v[1] * v[2]) % modulus not in {1, modulus - 1}:
                    continue
                plan = F.compile_fallback([v[:2], v[2:]], q, 2)
                shape = (plan["pivots"], topology(plan["operations"]), topology(plan["lowered_operations"]))
                if reference is None:
                    reference = shape
                F.require(shape == reference, "common low-class high-lift topology")
                lifts += 1
            F.require(reference is not None, "low class has determinant-sign lifts")
            classes += 1
        a = F.compile_fallback([[1, 0], [0, 1]], q, 2)
        b = F.compile_fallback([[1, q], [0, 1]], q, 2)
        F.require(a["reductions"] != b["reductions"] and
                  topology(a["operations"]) == topology(b["operations"]),
                  "zero-slot high-lift positive control")
        rows.append({"q": q, "w": 2, "low_classes": classes, "full_lifts": lifts,
                     "zero_coefficient_changes_without_topology_change": True})
    return rows


def batched_field_cases():
    rows = []
    q, w, m, rank = 3, 2, 2, 1
    modulus = q ** w
    matrix = F.residual(F.bad_projector(m, rank, q, modulus), modulus)
    for atoms in (1, 2, 3, 5):
        weights = [select_units(modulus, 2 * m, 2 * j) for j in range(atoms)]
        block = F.compile_weighted_block(matrix, weights, q, w)
        for orientations in product((1, -1), repeat=2 * m):
            audit = O.audit_weighted_block(matrix, weights, block, spectator_fields=3,
                                           field_positions=[1, 2, 4, 5],
                                           orientations=list(orientations))
            rows.append({"q": q, "w": w, "N": 2 * m, "plan_sha256": digest(block),
                         "coverage": audit})
    return rows


def semantic_controls():
    matrix = F.residual(F.bad_projector(2, 1, 3, 9), 9)
    plan = F.compile_fallback(matrix, 3, 2)
    controls = []

    def corrupted(name, change):
        bad = deepcopy(plan)
        change(bad)
        controls.append(expect_rejection(lambda: O.audit_plan(matrix, bad),
                                         O.OracleError, name))

    def drop_nonunit(p):
        p["lowered_operations"] = [op for op in p["lowered_operations"]
            if not (op[0] == "lower" and op[3] != 0 and op[3] % 3 == 0)]
    corrupted("nonzero_nonunit_shears_omitted", drop_nonunit)
    corrupted("inverse_chronology_reversed", lambda p: p.update(operations=list(reversed(p["operations"]))))
    corrupted("inverse_addition_sign_lost", lambda p: p.update(operations=[
        op[:3] + [-op[3] % 9] if op[0] == "add" else op for op in p["operations"]]))
    corrupted("paired_diagonal_order", lambda p: p.update(lowered_operations=[
        op[:3] + [pow(op[3], -1, 9)] if op[0] == "weighted_swap" else op
        for op in p["lowered_operations"]]))
    corrupted("nonunit_weight_inverse", lambda p: p["lowered_operations"].insert(0, ["weighted_swap", 0, 1, 3]))
    corrupted("wrong_pivot_itinerary", lambda p: p["pivots"].__setitem__(0, 1))
    sign_matrix = [[8, 0], [0, 1]]
    sign_plan = F.compile_fallback(sign_matrix, 3, 2)
    sign_plan["operations"] = [op for op in sign_plan["operations"] if op[0] != "sign"]
    controls.append(expect_rejection(lambda: O.audit_plan(sign_matrix, sign_plan),
                                     O.OracleError, "fixed_determinant_sign_omitted"))
    controls.append(expect_rejection(lambda: F.compile_fallback([[3, 0], [0, 1]], 3, 2),
                                     F.ContractError, "no_unit_pivot"))
    controls.append(expect_rejection(lambda: F.compile_fallback([[2, 0], [0, 1]], 3, 2),
                                     F.ContractError, "determinant_outside_signed_domain"))
    identity_plan = F.compile_fallback(F.identity(2), 3, 2)
    identity_plan["reductions"] = []
    O.audit_plan(F.identity(2), identity_plan)
    controls.append(expect_rejection(lambda: audit_template(identity_plan),
                                     F.ContractError, "missing_zero_shear_slots"))
    pair_plan = F.compile_fallback([[0, 1], [1, 0]], 3, 2)
    pair_plan["operations"] = [op for op in pair_plan["operations"] if op[0] != "pair"]
    O.audit_plan([[0, 1], [1, 0]], pair_plan)
    controls.append(expect_rejection(lambda: audit_template(pair_plan),
                                     F.ContractError, "missing_identity_pair_slot"))
    one_swap = [["weighted_swap", 0, 1, [2, 4, 5]]]
    targets = [[[0, a], [pow(a, -1, 9), 0]] for a in [2, 4, 5]]
    O.audit_fields(targets[0], one_swap, 9, atoms=3, matrices_by_atom=targets)
    controls.append(expect_rejection(lambda: O.audit_fields(targets[0], one_swap, 9,
        atoms=3, matrices_by_atom=targets, omit_tail_reversal=True),
        O.OracleError, "unpaid_tail_reversal"))
    return controls


def build_result(root=ROOT):
    context = bind_sources(root)
    return {"schema_version": 1, "status": "PASS_SELECTED_BIT_BAD_CLASS_FALLBACK",
            "no_new_kappa": True, "selected_context": context,
            "small_ring_census": exhaustive_small_rings(),
            "high_lift_templates": high_lift_template_cases(),
            "selected_dimension_cases": selected_dimension_cases(context["m"], context["rank"]),
            "batched_field_cases": batched_field_cases(), "rejecting_controls": semantic_controls(),
            "scope": "Abstract ADDRESS fallback and conditional child tariff; all-parameter proof in PROOF.md. No emitted selected residual, physical/tape realization, full cold replay or new stock/exponent claim."}


def check_receipt(path, observed):
    supplied = json.loads(path.read_text())
    # JSON canonicalization also makes integer histogram keys portable; direct
    # Python == would accept bool-for-int substitutions in other receipt fields.
    F.require(json.dumps(supplied, sort_keys=True, separators=(",", ":")) ==
              json.dumps(observed, sort_keys=True, separators=(",", ":")),
              "fixed result receipt differs")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=ROOT)
    parser.add_argument("--result", type=Path, default=PACKAGE / "RESULT.json")
    parser.add_argument("--write-result", type=Path)
    args = parser.parse_args()
    if args.write_result:
        path = args.write_result.resolve()
        F.require(not path.exists() and PACKAGE not in path.parents,
                  "new receipt must be outside package and must not exist")
    else:
        F.require(args.result.is_file(), "fixed receipt is missing")
    result = build_result(args.source_root)
    if args.write_result:
        with args.write_result.open("x") as stream:
            json.dump(result, stream, indent=2, sort_keys=True)
            stream.write("\n")
    else:
        check_receipt(args.result, result)
    count = sum(x["matrices"] for x in result["small_ring_census"])
    print(f"PASS_SELECTED_BIT_BAD_CLASS_FALLBACK matrices={count} m=64 allowance=98682 controls={len(result['rejecting_controls'])} no_new_kappa")


if __name__ == "__main__":
    main()
