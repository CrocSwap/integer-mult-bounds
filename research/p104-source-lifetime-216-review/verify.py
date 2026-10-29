#!/usr/bin/env python3
"""Check the P104 lifetime-floor arithmetic and frozen input hashes.

The geometric census and proof are upstream and are not reimplemented here.
"""
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
LOCAL_PINS = {
    "research/p104-native-channel/inputs/LOWRANK-WITNESS.json":
        "0f541bef7f19fdeffd67157684e9f03d785f42c89973632f508fc1a0452b580e",
    "research/p104-native-channel/inputs/P104-FIXTURE.json":
        "516c06f6ec3cb84be588c546108de897650288576dd5fbf5fe44b9c5546ad8a4",
    "research/complex-local-word-ceiling/ceiling.py":
        "86a1432870b3b21d8454106ec9162fddc0471472d9214c590a1420f2426cedfc",
}


def require(condition, message):
    if not condition:
        raise SystemExit("FAIL_P104_LIFETIME_FLOOR_216: " + message)


def main():
    for rel, expected in LOCAL_PINS.items():
        actual = hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()
        require(actual == expected, "frozen input hash mismatch: " + rel)

    facts = json.loads((HERE / "FINITE-RESULTS.json").read_text())
    upstream = json.loads((HERE / "UPSTREAM-PINS.json").read_text())
    require(upstream["commit"] == facts["source_commit"],
            "finite census is not bound to the recorded upstream commit")
    require(upstream["replay"]["result"].startswith("PASS_P104_RANK1_MIXER_TOP "),
            "upstream replay receipt is missing its pass marker")
    census = facts["census"]
    require(census["targets"] == 104, "wrong target count")
    require(census["certified_targets"] + census["permissive_targets"] == 104,
            "certified/permissive split does not cover all targets")
    exempt = census["exempt_target_ids"]
    require(len(exempt) == census["both_halves_Tprime_full_good_targets"] == 12,
            "wrong singular-mixing exception count")
    require(census["Tprime_pairs_full"] == 1038, "wrong singular-mixing pair census")

    a = (census["certified_targets"] - len(exempt)
         - 2 * census["permissive_targets"])
    excess = (a + 3) // 4
    floor = facts["arrival_floor"] + excess
    require(a == 32 and excess == 8 and floor == 216,
            "the exact integer floor does not reproduce")
    print("PASS_P104_LIFETIME_FLOOR_216_ARITHMETIC certified=84 permissive=20 "
          "exempt=12 A=32 excess=8 floor=216")


if __name__ == "__main__":
    main()
