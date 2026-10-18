#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Check every recipe subset, arbitrary private centre inputs, and the owner bound."""
import argparse
import contextlib
import copy
import io
import json
import sys
import tempfile
import time
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import audit_local as A
import build as B
import owner_bound as O


def augmented_program(word):
    rows = [{r: Q(1)} for r in range(704)]
    for gate in word["A"] + word["cut"] + word["B"]:
        A.apply(gate, rows)
    dirt = [{k: x for k, x in rows[r].items() if k >= 224}
            if 112 <= r < 224 else {} for r in range(704)]
    for gate in word["precondition"]:
        A.apply(gate, dirt)
    compensation = [["add", r, k, -x.numerator, x.denominator, []]
                    for r in range(112, 224) for k, x in sorted(dirt[r].items())]
    cut = []
    for gate in word["cut"]:
        cut.append(gate)
        private = list(gate)
        private[2] = 704 + word["centers"].index(gate[2])
        cut.append(private)
    early = {i for i, _ in word["early_cleanup"]}
    return (word["precondition"] + compensation + word["A"] + cut + word["B"]
            + [word["cleanup"][i] for i, _ in word["early_cleanup"]]
            + [gate for i, gate in enumerate(word["cleanup"]) if i not in early])


def private_centres(base, changed):
    for key in ("A", "cut", "centers", "center_frames"):
        assert base[key] == changed[key]
    for dual in (False, True):
        maps = []
        for word in (base, changed):
            rows = [{r: Q(1)} for r in range(712)]
            for gate in augmented_program(word):
                A.apply(gate, rows, dual)
            maps.append(rows)
        assert maps[0] == maps[1], ("private centre input map", dual)
    return {"columns": 712, "orientations": ["forward", "inverse_transpose"],
            "scope": "Each centre read has an independent arbitrary additive input. This checks the scalar interface, not a new global physical stream."}


def audit(word, directory, name):
    path = directory / (name + ".json.gz")
    digest = B.write(word, path)
    receipt = directory / (name + "-AUDIT.json")
    with contextlib.redirect_stdout(io.StringIO()):
        A.run(path, receipt)
    result = json.loads(receipt.read_text())
    assert result["content_sha256"] == digest
    return {"content_sha256": digest, "local_profile": result["local_profile"],
            "width_inventory": result["width_inventory"]}


def controls(directory):
    controls = {}
    word = B.construct(1)
    missing = copy.deepcopy(word)
    del missing["cleanup"][0]
    missing["early_cleanup"] = [[i - 1, f] for i, f in missing["early_cleanup"]]
    low = copy.deepcopy(word)
    low["helper_final"]["448"] = B.source()["helper_final"]["448"]
    for name, changed, reason in (("missing_dirty_column_restore", missing, "endpoint failure"),
                                  ("unpaid_low_helper_end", low, "pre-wrapper touch of residual helper")):
        try:
            audit(changed, directory, name)
        except RuntimeError as error:
            assert reason in str(error), (name, str(error))
            controls[name] = str(error)
        else:
            raise AssertionError("accepted control " + name)
    try:
        B.construct(256)
    except ValueError as error:
        controls["out_of_domain_mask"] = str(error)
    else:
        raise AssertionError("accepted mask 256")
    return controls


def main():
    if not __debug__:
        raise RuntimeError("verification requires assertions; do not use -O")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    begin = time.monotonic()
    results = []
    with tempfile.TemporaryDirectory(prefix="saved-arm-check-") as scratch:
        directory = Path(scratch)
        rejected = controls(directory)
        for mask in range(256):
            word = B.construct(mask)
            result = audit(word, directory, "mask-" + str(mask))
            result["mask"] = mask
            even = sum(mask >> i & 1 for i in (0, 2, 4, 6))
            odd = sum(mask >> i & 1 for i in (1, 3, 5, 7))
            expected = dict(O.LOCAL)
            expected[1] -= 2 * even
            expected[2] += 2 * even + odd
            assert result["local_profile"] == {str(k): n for k, n in expected.items()}
            assert sum(int(r) * n for r, n in result["local_profile"].items()) == 5586 + 2 * (even + odd)
            assert word["report"]["local_rank_mass"] == sum(int(r) * n for r, n in result["local_profile"].items())
            results.append(result)
            if mask % 32 == 31:
                print("checked", mask + 1, "of 256 exact local words", flush=True)
    private = private_centres(B.source(), B.construct(255))
    bound = O.verify()
    report = {"status": "PASS_TWO_ACCUMULATOR_SAVED_ARM_FAMILY", "masks": results,
              "private_centres": private, "owner_bound": bound, "rejected_controls": rejected,
              "elapsed_seconds": time.monotonic() - begin,
              "scope": "All 256 fixed local recipes are checked. The proof permits arbitrary per-call mixtures and all positive replica counts. It does not classify all two-accumulator programs."}
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(report["status"], flush=True)


if __name__ == "__main__":
    main()
