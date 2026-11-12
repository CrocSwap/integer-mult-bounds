"""Replay both bounded suites normally and under -O; compare exact receipts."""
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
SUITES = (
    ("general", "verify_general.py", "PASS_ONLINE_RANK_CONTROL"),
    ("selected", "verify_selected.py", "PASS_SELECTED_UNIFORM_CONTROL"),
)


def main():
    receipts = {}
    for name, script, expected in SUITES:
        outputs = []
        for optimized in (False, True):
            command = [sys.executable] + (["-O"] if optimized else [])
            command += ["-B", str(HERE / script)]
            result = subprocess.run(command, cwd=HERE, capture_output=True,
                                    text=True, timeout=120, check=True)
            if result.stderr:
                raise ValueError("unexpected stderr from " + script)
            receipt = json.loads(result.stdout)
            if receipt.get("status") != expected:
                raise ValueError("unexpected status from " + script)
            outputs.append(result.stdout)
            receipts[name + ("_optimized" if optimized else "_normal")] = receipt
        if outputs[0] != outputs[1]:
            raise ValueError("normal/-O output differs for " + script)
    print(json.dumps({"status": "PASS_SELECTED_RANK_CONTROL_PACKAGE",
                      "normal_optimized_byte_equal": True,
                      "receipts": receipts}, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
