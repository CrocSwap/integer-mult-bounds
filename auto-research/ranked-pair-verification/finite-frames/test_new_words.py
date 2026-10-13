#!/usr/bin/env python3
"""Run seven inherited PR60 tampering controls against the bundled new words.

An explicit checkout at PR60's exact pin is required. These controls supplement
complete basis replay; they do not prove checker completeness or transfer.
"""
import argparse
import gzip
import importlib.util
import json
from pathlib import Path
import sys
import unittest

sys.dont_write_bytecode = True
from pinned_upstream import PACKAGE, PR60_PIN, validate_checkout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pr60", type=Path, required=True)
    args = parser.parse_args()
    upstream, _ = validate_checkout(args.pr60, PR60_PIN)
    source = upstream / "tests/test_joint_reclaim.py"
    spec = importlib.util.spec_from_file_location("pinned_adversarial_controls", source)
    controls = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(controls)

    class NewWordControls(controls.JointReclamationControls):
        @classmethod
        def setUpClass(cls):
            cls.words = {h: json.loads(gzip.decompress(
                (PACKAGE / f"finite-frames/pair-ranked-word-{h}.json.gz").read_bytes()))
                for h in (23, 25)}

    names = ["test_omitted_literal_xor_is_rejected", "test_self_xor_is_rejected",
             "test_non_nested_operation_frame_is_rejected", "test_aliased_terminal_role_is_rejected",
             "test_missing_copied_center_is_rejected", "test_omitted_transition_cannot_reduce_paid_profile",
             "test_understated_physical_width_is_rejected"]
    result = unittest.TextTestRunner(verbosity=2).run(
        unittest.TestSuite(NewWordControls(name) for name in names))
    if not result.wasSuccessful():
        sys.exit(1)


if __name__ == "__main__":
    main()
