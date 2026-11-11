#!/usr/bin/env python3
"""Replay the exact two-blocker exclusion and its directed price controls."""
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory


PACKAGE = Path(__file__).resolve().parent
VENDOR = PACKAGE / "vendor"
ROUND = "kappa-scalar-two-20261110T2315Z"
PLANNER = f"{ROUND}/evidence/planner/two_blockers.py"
LEGACY = "kappa-two-blockers-20261110T1036Z/evidence/two_blockers.py"
SCRIPT_PINS = {
    PLANNER: "152b0f6c80e0f7a47b078fb35bd91b35fbfd63fa2d2da17cf66ded05f51846f0",
    LEGACY: "a5b5855f3016a77d991fb53536cae388221a7cf9529fe58c376141bc7656e0c3",
}


def unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate dependency path {key}")
        result[key] = value
    return result


def load(path):
    return json.loads(path.read_bytes(), object_pairs_hook=unique)


def authenticate():
    try:
        json.loads('{"script.py":"first","script.py":"second"}', object_pairs_hook=unique)
    except ValueError:
        pass
    else:
        raise RuntimeError("Duplicate dependency path control failed")
    pins = load(PACKAGE / "DEPENDENCIES.json")
    files = {p.relative_to(VENDOR).as_posix(): p for p in VENDOR.rglob("*") if p.is_file()}
    assert pins.keys() == files.keys()
    for key, path in files.items():
        assert not path.is_symlink() and sha256(path.read_bytes()).hexdigest() == pins[key], key
    for key, digest in SCRIPT_PINS.items():
        assert pins[key] == digest
    print(f"PASS_PATH_KEYED_PINS {len(pins)}", flush=True)


def checked(script, expected, cache, *args):
    process = subprocess.run(
        [sys.executable, "-E", "-S", "-B", "-X", f"pycache_prefix={cache}", str(script),
         *map(str, args)],
        cwd=PACKAGE, check=True, stdout=subprocess.PIPE,
    )
    assert process.stdout == expected.read_bytes(), expected.relative_to(PACKAGE)
    print(f"PASS {expected.relative_to(VENDOR)}", flush=True)


def main():
    assert __debug__ and sys.version_info[:2] == (3, 12)
    authenticate()
    word, result, caller = (VENDOR / "inputs" / name
                            for name in ("WORD.json.gz", "RESULT.json", "CALLER.json"))
    local = VENDOR / ROUND / "evidence"
    planner, overlap, price = (local / d for d in ("planner", "overlap", "price"))
    with TemporaryDirectory(prefix="p104-two-blocker-") as directory:
        scratch = Path(directory)
        cache = scratch / "cache"
        checked(planner / "validate.py", planner / "PLANNER.json", cache, word)
        checked(planner / "validate_all.py", planner / "ALL.json", cache, word)
        checked(overlap / "validate.py", overlap / "OVERLAP.json", cache, word)
        for mode, name, count in (("all-terms", "ALL", 73461), ("overlap", "OVERLAP", 8)):
            journal = scratch / f"{name}.jsonl"
            expected = price / f"{name}.json"
            checked(price / "price_two.py", expected, cache, word, result, caller, journal, "--mode", mode)
            receipt = load(expected)
            assert receipt["counts"]["placements"] == count
            assert receipt["unresolved"] == 0 and receipt["pending"] is None
            for key, digest in SCRIPT_PINS.items():
                assert receipt["dependencies"][key] == digest
            if mode == "all-terms":
                assert journal.read_bytes() == (price / "ALL.jsonl").read_bytes()
            else:
                assert not journal.read_bytes()
    print("PASS_P104_TWO_BLOCKER_EXCLUSION all_terms=73461 overlap=8 no_verified_gain")


if __name__ == "__main__":
    main()
