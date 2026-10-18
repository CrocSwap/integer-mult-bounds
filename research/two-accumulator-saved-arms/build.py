#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Apply one set of the eight saved-arm recipes to the selected local word."""
import argparse
import copy
import gzip
import hashlib
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE_HASH = "c2b294300760e1fd6eeab8c22c4d13e4633dca40e52cac8da0d68163a76e3ca8"


def source():
    raw = gzip.decompress((HERE / "inputs/SEVEN-SLOT-WORD.json.gz").read_bytes())
    if hashlib.sha256(raw).hexdigest() != SOURCE_HASH:
        raise ValueError("selected source hash")
    return json.loads(raw)


def construct(mask):
    if type(mask) is not int or not 0 <= mask < 256:
        raise ValueError("mask must be an integer from 0 through 255")
    word = source()
    recipes = json.loads((HERE / "RECIPES.json").read_text())
    chosen = [r for r in recipes if mask >> r["group"] & 1]
    removed, insertions, correction = set(), {}, []
    profile = Counter({int(k): v for k, v in word["report"]["local_profile"].items()})
    widths = Counter({int(k): v for k, v in word["report"]["width_inventory"].items()})
    for recipe in chosen:
        for i, expected in recipe["remove_B"]:
            if word["B"][i] != expected or i in removed:
                raise ValueError("B gate pin or overlapping recipes")
            removed.add(i)
        at = recipe["insert_before_B"]
        if at in insertions:
            raise ValueError("overlapping insertion sites")
        insertions[at] = copy.deepcopy(recipe["insert_B"])
        for i, expected, replacement in recipe["cleanup_changes"]:
            if word["cleanup"][i] != expected:
                raise ValueError("cleanup gate pin")
            word["cleanup"][i] = copy.deepcopy(replacement)
        helper = str(recipe["partial_helper"])
        if len(word["start_extra"][helper]) != 1 or len(word["helper_final"][helper]) != 8:
            raise ValueError("helper endpoint pin")
        del word["start_extra"][helper]
        del word["helper_final"][helper]
        correction.extend(copy.deepcopy(recipe["full_cleanup_corrections"]))
        profile.update({int(k): v for k, v in recipe["local_delta"].items()})
        widths[7] -= 1
        widths[9] += 1
    gates = []
    for i, gate in enumerate(word["B"]):
        gates.extend(insertions.get(i, []))
        if i not in removed:
            gates.append(gate)
    word["B"] = gates
    word["cleanup"] = correction + word["cleanup"]
    word["early_cleanup"] = [[i + len(correction), frame] for i, frame in word["early_cleanup"]]
    word["report"]["local_profile"] = {str(k): v for k, v in sorted(profile.items()) if v}
    word["report"]["local_rank_mass"] = sum(k * v for k, v in profile.items())
    word["report"]["width_inventory"] = {str(k): v for k, v in sorted(widths.items()) if v}
    word["refactored_cleanup"]["saved_arm_groups"] = [r["group"] for r in chosen]
    return word


def write(word, path):
    raw = json.dumps(word, sort_keys=True, separators=(",", ":")).encode()
    path.write_bytes(gzip.compress(raw, mtime=0))
    return hashlib.sha256(raw).hexdigest()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mask", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(write(construct(args.mask), args.output))
