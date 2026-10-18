#!/usr/bin/env python3
"""Run the complete replay and both semantic and packaging control suites."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import replay
import test_package
import test_semantics


def main():
    module = replay.load()
    receipt = replay.run(module, "epochs")
    semantic = test_semantics.run()
    package = test_package.run()
    replay.need(semantic == json.loads((ROOT / "SEMANTIC-CONTROLS.json").read_text()),
                "semantic control receipt differs")
    replay.need(package == json.loads((ROOT / "PACKAGE-CONTROLS.json").read_text()),
                "packaging control receipt differs")
    print(json.dumps({"status": "PASS", "proof_additions": 37044, "hints_checked": 1409475,
                      "receipt_sha256": hashlib.sha256(replay.canonical(receipt)).hexdigest(),
                      "semantic_cases": semantic["accepted"] + semantic["rejected"],
                      "truth_table_lemma_checks": semantic["truth_table_lemma_checks"],
                      "package_negative_controls": package["negative_controls"],
                      "new_kappa": False}, sort_keys=True))


if __name__ == "__main__":
    main()
