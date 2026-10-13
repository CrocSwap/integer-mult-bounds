#!/usr/bin/env python3
"""Opt-in, source-pinned replay of the historical joint-frame certificate."""
import argparse
from collections import Counter
from hashlib import sha256
import importlib
import json
from pathlib import Path
import sys
import unittest

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
sys.path.insert(0, str(PACKAGE))
from kernel import screened_rank


def require(ok, message):
    if not ok:
        raise ValueError(message)


def check_sources(root=ROOT):
    """Fail before importing the historical code if a pinned input changed."""
    require(not sys.flags.optimize, "Historical assertions must remain enabled")
    manifest = json.loads((PACKAGE / "SOURCE.json").read_text())
    for name, pin in manifest["files"].items():
        file = (root / name).resolve()
        require(file.is_relative_to(root.resolve()), "Source path escapes root")
        require(file.is_file() and sha256(file.read_bytes()).hexdigest() == pin["sha256"],
                "Source pin mismatch: " + name)
    require(sha256((PACKAGE / "EXPECTED.json").read_bytes()).hexdigest()
            == manifest["expected_certificate_sha256"], "Expected certificate pin mismatch")
    return manifest


def load_audit(engine, check_every_rank=False):
    check_sources()
    sys.path.insert(0, str(ROOT / "scripts"))
    audit = importlib.import_module("audit_joint_frames")
    reference = audit.rational_rank
    audit.rank.cache_clear()
    stats = Counter()

    def rank(matrix):
        stats["calls"] += 1
        if engine == "reference":
            answer = reference(matrix)
        else:
            answer = screened_rank(matrix, reference, stats)
        if check_every_rank:
            require(answer == reference(matrix), "Per-matrix rational rank mismatch")
            stats["individually_compared"] += 1
        stats["rank_" + str(answer)] += 1
        return answer

    audit.rational_rank = rank
    return audit, stats


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--engine", choices=("reference", "screened"), default="screened")
    parser.add_argument("--check-every-rank", action="store_true")
    parser.add_argument("--tests", action="store_true", help="Run unchanged joint-frame tests")
    parser.add_argument("--stats", type=Path, help="Fresh path for per-run counts")
    args = parser.parse_args()
    audit, stats = load_audit(args.engine, args.check_every_rank)
    if args.tests:
        suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"),
                                                   pattern="test_joint_frames.py")
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        require(result.testsRun == 8 and result.wasSuccessful(), "Historical tests failed")
        print("PASS_HISTORICAL_JOINT_FRAME_TESTS tests=8")
    else:
        certificate = audit.serializable(audit.certificate())
        encoded = json.dumps(certificate, sort_keys=True, indent=2) + "\n"
        require(encoded == (PACKAGE / "EXPECTED.json").read_text(),
                "Complete historical certificate differs")
        print(encoded, end="")
    if args.stats:
        with args.stats.open("x") as stream:
            stream.write(json.dumps(dict(stats), sort_keys=True, indent=2) + "\n")


if __name__ == "__main__":
    main()
