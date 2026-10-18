#!/usr/bin/env python3
"""Replay both unmodified PR225 checkers in separate temporary source trees.

Optional historical reproduction, not the independent verifier. Python >= 3.11
is required by the preserved source. Ross Richardson / OpenAI Codex, Apache-2.0.
"""
import importlib.util
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("reconciliation", HERE / "verify.py")
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


def main():
    capsule = checker.load()
    checker.run(capsule)
    for label, head in (("reviewed", checker.OLD), ("current", checker.NEW)):
        with tempfile.TemporaryDirectory(prefix="pr225-" + label + "-") as directory:
            root = Path(directory)
            inventory = capsule.inventory(head)
            for path in inventory:
                target = root / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(capsule.read(head, path))
            source = capsule.json(head, checker.PACKAGE + "/SOURCE.json")
            for pin in source["suppliers"].values():
                target = root / pin["local_path"]
                target.parent.mkdir(parents=True, exist_ok=True)
                raw = capsule.read(pin["commit"], pin["path"])
                if target.exists():
                    checker.require(target.read_bytes() == raw, "restored source conflict")
                else:
                    target.write_bytes(raw)
            print("Unmodified original replay:", label, head, flush=True)
            subprocess.run([sys.executable, "-I", "-B", str(root / checker.PACKAGE / "verify.py"), "--check"],
                           cwd=root, check=True, timeout=180)
    print("PASS_PR225_ORIGINAL_REPLAYS reviewed_profiles=4 current_profiles=6")


if __name__ == "__main__":
    main()
