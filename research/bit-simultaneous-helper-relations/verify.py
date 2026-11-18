#!/usr/bin/env python3
"""Recompute the sharp signed-margin envelope from the two pinned source files."""
import argparse
import json
from itertools import combinations
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from flags import Birth, charge_orientation, clean_flag, decompose, group_basis
from invoice_bound import whole_caller
from sharp import attaining_edit, mixed_example, root_interval
from word import Bank, CALLER, NATIVE, check_frames, invoice, replay, require, source


def negative_controls():
    def rejects(message, function):
        try:
            function()
        except ValueError as error:
            require(str(error) == message, "mutation failed at the wrong check")
        else:
            raise ValueError("accepted control: " + message)

    rejects("original bank dependence", lambda: clean_flag([Bank(1, 1, 1), Bank(2, 1, 1)], 0))
    terminal = [Birth(0, 1, 1), Birth(1, 2, 2), Birth(2, 4, 1)]
    rejects("terminal tariff run", lambda: group_basis([0, 1, 2], terminal, False, [(0, 2)]))

    # A mixed rank-two birth cannot be assigned separate unit-price charges.
    rejects("mixed flag at a higher-price birth", lambda: decompose({0: [Bank(0, 3, 2)]}, [1, 2]))
    # Both small groups are needed here. Projecting all mixing onto the large group would miss it.
    rejects("mixed small-block flag", lambda: decompose({0: [Bank(0, 6, 1)]}, [1, 2, 4]))
    return ["dependent source bank", "swap across unequal prices", "mixed above-unit birth",
            "relation between two small blocks"]


def maximizers(groups):
    # Each admissible pivot set describes a binary echelon cell.
    total = 1
    for group in groups:
        if group["target_rank"] == 6:
            continue  # Its unique relation is forced off/on away from the switch.
        allowed = group["neutral_pivot_indices"]
        count = 0
        for k in range(len(allowed) + 1):
            for pivots in combinations(allowed, k):
                count += 1 << sum(p - i for i, p in enumerate(pivots))
        group["neutral_subspace_count"] = count
        total *= count
    return {"off_switch": total, "at_switch": 2 * total}


def calculate():
    word = source(NATIVE)
    caller = source(CALLER)
    receipt = {"pricing": "t=1-eta; delta=paid saved minus targets surrendered",
               "price_saving_switch_open_interval": root_interval(), "source_frames": check_frames(word)}
    for transpose, name in ((False, "forward"), (True, "transpose")):
        banks, groups, frames = replay(word, transpose)
        result = charge_orientation(banks, groups, frames, transpose)
        result["maximizing_subspace_tuples"] = maximizers(result["groups"])
        result["rank_six_witness"] = attaining_edit(banks, groups, frames)
        if not transpose:
            receipt["full_caller"] = invoice(caller, banks, groups, frames)
            receipt["mixed_example"] = mixed_example(banks[50])
        else:
            require(invoice(caller, banks, groups, frames) == receipt["full_caller"], "orientation invoice")
        receipt[name] = result
    receipt["global_raw_ceiling"] = whole_caller(receipt["full_caller"], [receipt["forward"], receipt["transpose"]])
    receipt["controls"] = negative_controls()
    return receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="print the regenerated certificate")
    args = parser.parse_args()
    result = calculate()
    rendered = json.dumps(result, indent=2)
    if args.emit:
        print(rendered)
    else:
        require(json.loads(rendered) == json.loads((HERE / "RESULT.json").read_bytes()), "certificate mismatch")
        print("PASS_BIT_SIMULTANEOUS_HELPER_ENVELOPE groups=9 helpers=437 orientations=2 calls=36")
