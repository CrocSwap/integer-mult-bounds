# SPDX-License-Identifier: Apache-2.0
"""Reproduce the PR3042 scalar contraction and its unchanged recursive bill."""

import argparse
import gzip
import hashlib
import json
from pathlib import Path

from contract import NEW, OLD, START, expected_cleanup, operator, produce, projected_block
from frames import registers, require, trace
from minimality import TARGET, exclude_two

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
LOCAL = {1: 2433, 2: 712, 3: 232, 4: 108, 5: 18, 8: 8}
FILES = {"frames.py", "vendor/WORD-base.json.gz", "vendor/WORD-extra.json.gz",
         "vendor/PROFILE.json", "vendor/CREDITS.md", "vendor/NOTICE"}


def read(path):
    raw = path.read_bytes()
    require(len(raw) <= 3_000_000, "bounded compressed/JSON input")
    if path.suffix == ".gz":
        raw = gzip.decompress(raw)
    require(len(raw) <= 8_000_000, "bounded decoded input")
    return json.loads(raw)


def check_pins(package=PACKAGE):
    records = read(package / "VENDOR.json")["files"]
    require(len(records) == len(FILES) and {r["path"] for r in records} == FILES,
            "complete vendor inventory")
    for record in records:
        path = package / record["path"]
        require(path.resolve().is_relative_to(package), "contained source path")
        require(hashlib.sha256(path.read_bytes()).hexdigest() == record["sha256"],
                f"source digest: {record['path']}")
    sources = read(package / "SOURCES.json")
    require(len(sources["files"]) <= 8, "bounded live inputs")
    for record in sources["files"]:
        if record["usage"] == "input":
            path = ROOT / record["path"]
            require(path.resolve().is_relative_to(ROOT), "contained live input")
            require(hashlib.sha256(path.read_bytes()).hexdigest() == record["sha256"],
                    f"live input digest: {record['path']}")
    return len(records)


def validate_word(word):
    for section, maximum in (("A", 20000), ("B", 20000), ("restore", 1000),
                             ("cleanup", 60000), ("warps", 704)):
        require(len(word[section]) <= maximum, f"bounded {section}")
    require(set(word["helper_final"]) <= {str(i) for i in range(704)}, "helper IDs")
    require(type(word["prelude_events"]) is int
            and 0 <= word["prelude_events"] <= len(word["A"]), "prelude address")


def same_operator(before, after):
    require(operator(before, range(704)) == operator(after, range(704)),
            "arbitrary-dirty restore operators differ")


def verify_pair(parent, candidate):
    validate_word(parent)
    validate_word(candidate)
    require(set(parent) == set(candidate), "same word sections")
    same_operator(parent["restore"], candidate["restore"])
    before, after = trace(parent), trace(candidate)
    require(before["profile"] == after["profile"] == LOCAL, "unchanged local profile")
    require(before["widths"] == after["widths"], "unchanged ordered widths")
    for old_history, new_history in zip(before["histories"], after["histories"], strict=True):
        require([item[1:] for item in old_history] == [item[1:] for item in new_history],
                "unchanged per-register frame itinerary")
    require(parent["cleanup"] == expected_cleanup(parent), "source cleanup")
    require(candidate["cleanup"] == expected_cleanup(candidate), "derived inverse cleanup")
    require(parent["cleanup"][:33] == candidate["cleanup"][:33]
            and parent["cleanup"][37:] == candidate["cleanup"][36:],
            "one inverse cleanup hunk")
    require(operator(parent["cleanup"][33:37], (22, 934))
            == operator(candidate["cleanup"][33:36], (22, 934))
            == {22: {22: -1, 934: 1}, 934: {22: -1}}, "dirty private-buffer identity")
    changed = {key for key in parent if parent[key] != candidate[key]}
    require(changed == {"restore", "cleanup"}, "only restore and cleanup change")
    require(parent["restore"][START:START + 4] == OLD, "literal preimage")
    expected = parent["restore"][:START] + NEW + parent["restore"][START + 4:]
    require(candidate["restore"] == expected, "one exact contraction")
    buffers = {r for gate in candidate["cleanup"] for r in registers(gate) if r >= 704}
    require(buffers == {704 + int(r) for r in candidate["helper_final"]}, "91 buffers")
    require({int(r): n for r, n in candidate["report"]["local_profile"].items()} == LOCAL,
            "reported profile")
    lengths = {section: [len(parent[section]), len(candidate[section])]
               for section in ("A", "B", "restore", "cleanup")}
    require(lengths["restore"] == [212, 211] and lengths["cleanup"] == [5216, 5215],
            "one forward and one inverse gate saved")
    word_bytes = json.dumps(candidate, sort_keys=True, separators=(",", ":")).encode()
    return {"section_lengths": lengths, "local_profile": LOCAL,
            "contracted_word_sha256": hashlib.sha256(word_bytes).hexdigest(),
            "helper_count": len(after["widths"]), "private_buffers": len(buffers),
            "unchanged_frame_itineraries": 704}


def shortest_block():
    target = {22: {230: -1}, 230: {22: 1, 230: -1}}
    require(operator(OLD, (22, 230)) == operator(NEW, (22, 230)) == target,
            "the explicit three-gate map is (-y,x-y)")
    lifted = [[(1, -1), (0, -1)], [(0, 1), (1, -2)]]
    require(projected_block(OLD) == projected_block(NEW) == lifted,
            "identity over Q[P]/(P^2-P)")
    return {"minimum_gates": 3, "matrix": TARGET, "idempotent_lift": lifted,
            "two_gate_exclusions": exclude_two(), "inverse_minimum_gates": 3,
            "inverse_two_gate_exclusions": exclude_two(((-1, 1), (-1, 0)))}


def whole_bill():
    before = {int(r): n for r, n in read(
        ROOT / "research/rank7-joint-endframes/allocation/PROFILE.json").items()}
    source = {int(r): n for r, n in read(PACKAGE / "vendor/PROFILE.json").items()}
    delta = {1: -12, 2: 6}
    require(source == {r: n + 666 * delta.get(r, 0) for r, n in before.items()},
            "source complete profile versus PR2979")
    mass = sum(r * n for r, n in source.items())
    require(mass == 74 * 65088 == 4816512, "complete rank mass")
    return {"profile": source, "profile_delta": {}, "rank_mass": mass,
            "physical_families": 66304 + 408 + 8 + 91 + 2, "calls": 666,
            "listed_adds_removed_per_complete_local_word": 2,
            "kappa_improvement_claimed": False}


def audit():
    pins = check_pins()
    variants = {}
    for variant in ("base", "extra"):
        parent = read(PACKAGE / f"vendor/WORD-{variant}.json.gz")
        validate_word(parent)
        candidate = produce(parent)
        variants[variant] = verify_pair(parent, candidate)
    return {"status": "PASS_RANK7_RESTORE_CONTRACTION", "vendor_pins": pins,
            "variants": variants, "block": shortest_block(), "bill": whole_bill(),
            "scope": "Exact scalar contraction and unchanged frame/recursive invoice. "
                     "Inherited native, ownership, physical, precision, all-size and "
                     "outer obligations are not replayed or newly admitted."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit-word", choices=("base", "extra"),
                        help="verify both providers and emit the contracted word")
    args = parser.parse_args()
    result = audit()
    if args.emit_word:
        parent = read(PACKAGE / f"vendor/WORD-{args.emit_word}.json.gz")
        result = produce(parent)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
