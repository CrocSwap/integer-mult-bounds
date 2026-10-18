#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Materialize and price the admitted 205-pair selected-R439 D wrap."""

import argparse
import copy
import gzip
import hashlib
import importlib.util
import json
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCES = HERE / "SOURCES.json"
CERTIFICATE = HERE / "CERTIFICATE.json"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    need(spec is not None and spec.loader is not None, "cannot load " + str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify_source_pins():
    manifest = json.loads(SOURCES.read_text())
    actual = {}
    for entry in manifest["files"]:
        path = entry["path"]
        if entry["usage"] != "input":
            continue
        raw = (ROOT / path).read_bytes()
        actual[path] = digest(raw)
        need(actual[path] == entry["sha256"], "source SHA-256 mismatch: " + path)
    return actual


def failures(hypotheses, conclusions):
    return sorted(
        name
        for name, result in list(hypotheses.items()) + list(conclusions.items())
        if not result
    )


def boundary_rows(word, bound):
    forward = bound.literal_rows(word)
    reverse = bound.literal_rows(word, reverse=True)
    return forward, reverse


def run():
    input_hashes = verify_source_pins()
    h2 = load_module(
        "r439_h2sem_predecessor",
        ROOT / "research/r439-copyshare-h2sem-admission/verify.py",
    )
    bound = load_module(
        "r439_bound_predecessor",
        ROOT / "research/r439-bsection-stars-seed01/verify.py",
    )
    original = json.loads(gzip.decompress(h2.WORD.read_bytes()))
    checker = h2.load_checker()

    # The matching is inherited exactly from PR848/PR1782; no matching search
    # or optimizer seed is changed in this contribution.
    pairs, census = h2.nominate_d(original, h2.SEED)
    need(census["operands"] == 430, "helper pool changed")
    need(census["matching_pairs"] == 205, "fixed matching size changed")
    need(census["matching_saving"] == 6231, "fixed matching invoice changed")
    need(census["best_pair"] == [277, 434] and census["best_saving"] == 65,
         "single-pair positive control changed")
    candidate = h2.construct_d(original, pairs)

    # Positive control: the pinned source word itself meets every inherited
    # H1-H5 and U/J/K/C check and has the expected semantic D boundary.
    _, _, _, base_h, base_c, _ = checker.check(original)
    need(all(base_h.values()) and all(base_c.values()), "pinned baseline checker failed")
    base_d, base_cut, base_shape, base_n = h2.d_shape(original, checker)
    need(base_shape, "baseline D boundary shape")
    base_k = h2.raw_K(original, checker)
    need(base_n == base_k, "baseline semantic D != raw K")

    cand_d, cand_cut, cand_shape, cand_n = h2.d_shape(candidate, checker)
    need(cand_shape and cand_d == base_d, "candidate D map changed")
    need(cand_cut == base_cut, "candidate chronological cut state changed")
    need(cand_n == base_n == base_k, "candidate semantic N != pinned raw K")
    need(h2.raw_K(candidate, checker) == base_k, "candidate raw K changed")
    cond1, cond2 = h2.h2sem_conditions(candidate)
    need(cond1 and cond2, "candidate violates H2-sem")
    need(h2.literal_N(candidate) != cand_n,
         "candidate should expose the inherited gate-local K mismatch")
    _, _, _, cand_h, cand_c, _ = checker.check(candidate)
    expected_failures = sorted(
        ["H2_D_frame0_targets_from_helpers", "K_equals_D"]
    )
    need(failures(cand_h, cand_c) == expected_failures,
         "unexpected inherited checker failures")

    # Compare the full 661-column map forward and backward, plus exact register
    # frame paths and the paid frame-transition/rank profile.
    base_forward, base_reverse = boundary_rows(original, bound)
    cand_forward, cand_reverse = boundary_rows(candidate, bound)
    need(len(cand_forward) == len(cand_reverse) == 661,
         "unexpected formal-column count")
    need(cand_forward == base_forward, "full forward dirty-input map changed")
    need(cand_reverse == base_reverse, "full reverse dirty-input map changed")
    need(bound.frame_paths(candidate) == bound.frame_paths(original),
         "register frame paths changed")
    base_owner = bound.owner(original)
    cand_owner = bound.owner(candidate)
    need(cand_owner["profile"] == base_owner["profile"], "paid profile changed")
    need(sum(rank * count for rank, count in cand_owner["profile"].items()) == 5129,
         "paid rank mass changed")

    # The literal ADD stream is checked against the repository's record
    # exporter. Every helper setup/restoration ADD is included in both bills.
    base_bill = bound.literal_bounds(original)
    cand_bill = bound.literal_bounds(candidate)
    bound.guard(base_bill)
    bound.guard(cand_bill)
    need(base_bill["native_ADDs"] == 24305, "baseline ADD count changed")
    need(cand_bill["native_ADDs"] == 18074, "candidate ADD count changed")
    need(base_bill["D_adds"] == 18085 and cand_bill["D_adds"] == 11854,
         "D source-ADD invoice changed")
    need(base_bill["native_ADDs"] - cand_bill["native_ADDs"] == 6231,
         "complete ADD saving does not match fixed-pair invoice")
    need(base_bill["local_bits"] == 93 and cand_bill["local_bits"] == 95,
         "local precision bill changed")
    need(base_bill["nine_stage_bits"] == 177 and cand_bill["nine_stage_bits"] == 180,
         "nine-stage precision bill changed")
    with tempfile.TemporaryDirectory(prefix="r439-copyshare-priced-") as temp:
        work = Path(temp)
        base_export = bound.exporter(original, work / "base")
        cand_export = bound.exporter(candidate, work / "candidate")
    for label, bill, exported in (
        ("baseline", base_bill, base_export),
        ("candidate", cand_bill, cand_export),
    ):
        need(exported["adds"] == bill["native_ADDs"], label + " exporter ADD count")
        need(exported["copies"] == exported["erasures"] == 9,
             label + " COPY/ERASE invoice")
        need(exported["forward"] == bill["F"], label + " forward envelope")
        need(exported["reverse"] == bill["B"], label + " reverse envelope")
        need(exported["payload_bits"] == bill["local_bits"],
             label + " local payload precision")

    # Failure controls: missing restoration, a wrong restored helper, a
    # nonzero-frame helper gate, and synthetic bills immediately beyond both
    # declared precision limits must all be rejected.
    controls = []

    def reject(label, action):
        try:
            action()
        except (ValueError, KeyError):
            controls.append(label)
            return
        raise ValueError("negative control accepted: " + label)

    def require_same_boundary(word):
        forward, reverse = boundary_rows(word, bound)
        need(forward == base_forward and reverse == base_reverse,
             "full boundary mismatch")

    def require_h2sem(word):
        one, two = h2.h2sem_conditions(word)
        need(one and two, "H2-sem condition failed")

    unbalanced = h2.construct_d(original, pairs, restore=False)
    reject(
        "missing_restore_breaks_full_boundary",
        lambda: require_same_boundary(unbalanced),
    )
    wrong_restore = {a: a for a, _ in pairs}
    wrong_restore[pairs[0][0]] = pairs[0][1]
    misrestored = h2.construct_d(original, pairs, restore_map=wrong_restore)
    reject(
        "wrong_restore_destination_breaks_boundary",
        lambda: require_same_boundary(misrestored),
    )
    shifted = copy.deepcopy(candidate)
    shifted["D"][0][0] = 1
    reject(
        "nonzero_frame_helper_gate_fails_H2_sem",
        lambda: require_h2sem(shifted),
    )
    reject(
        "local_precision_over_104_rejected",
        lambda: bound.guard({"local_bits": 105, "nine_stage_bits": 180}),
    )
    reject(
        "nine_stage_precision_over_192_rejected",
        lambda: bound.guard({"local_bits": 95, "nine_stage_bits": 193}),
    )

    cert = {
        "status": "PASS_R439_COPYSHARE_PRICED_WRAP",
        "scope": "One fixed seed-42 205-pair wrapper on the pinned selected R439 word; no matching optimality claim.",
        "source_sha256": input_hashes,
        "matching": census,
        "wrapper": {
            "pairs": len(pairs),
            "extra_prep_restore_gates": 2 * len(pairs),
            "D_gates": {"base": len(original["D"]), "candidate": len(candidate["D"])},
            "semantic_H2": {"zero_frame_distinct_operands": cond1,
                             "no_target_feedback": cond2},
            "semantic_N_equals_raw_K": cand_n == base_k,
            "inherited_failed_flags": expected_failures,
            "columns_checked_each_direction": len(cand_forward),
            "cut_state_equal": cand_cut == base_cut,
            "frame_paths_equal": bound.frame_paths(candidate) == bound.frame_paths(original),
            "paid_profile": {str(k): v for k, v in sorted(cand_owner["profile"].items())},
            "paid_rank_mass": 5129,
        },
        "invoice": {
            "native_ADDs": {"base": base_bill["native_ADDs"],
                             "candidate": cand_bill["native_ADDs"],
                             "saving": base_bill["native_ADDs"] - cand_bill["native_ADDs"]},
            "D_source_ADDs": {"base": base_bill["D_adds"], "candidate": cand_bill["D_adds"]},
            "F": {"base": base_bill["F"], "candidate": cand_bill["F"]},
            "B": {"base": base_bill["B"], "candidate": cand_bill["B"]},
            "local_bits": {"base": base_bill["local_bits"], "candidate": cand_bill["local_bits"], "limit": 104},
            "nine_stage_bits": {"base": base_bill["nine_stage_bits"], "candidate": cand_bill["nine_stage_bits"], "limit": 192},
            "exporter_record_sha256": {"base": base_export["record_sha256"],
                                        "candidate": cand_export["record_sha256"]},
            "copies_and_erasures": {"base": [base_export["copies"], base_export["erasures"]],
                                    "candidate": [cand_export["copies"], cand_export["erasures"]]},
        },
        "negative_controls": controls,
        "limits": [
            "The 205-pair matching is inherited from PR848/PR1782; optimality is not claimed.",
            "This is a local R439 word construction; selected-supplier adoption, hosting, outer assembly, and kappa are not claimed.",
            "The inherited H2/K flags remain false; admission uses the scoped H2-sem contract.",
        ],
    }
    return cert


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="write the deterministic certificate")
    args = parser.parse_args()
    cert = run()
    if args.write:
        CERTIFICATE.write_text(json.dumps(cert, indent=2, sort_keys=True) + "\n")
    else:
        expected = json.loads(CERTIFICATE.read_text())
        need(cert == expected, "certificate mismatch; use --write only for an intentional update")
    print(
        "PASS_R439_COPYSHARE_PRICED_WRAP pairs=205 ADDs=24305->18074 saved=6231 "
        "F=49347->75381 B=1113070->1196402 guards=95/104,180/192 "
        "profile_mass=5129 controls=5 no_kappa"
    )


if __name__ == "__main__":
    main()
