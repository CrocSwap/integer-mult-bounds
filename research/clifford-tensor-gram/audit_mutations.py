"""Check that semantic defects fail in private package copies.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
MUTATIONS = [
    ("omit final trace root", "range(1, 2*n+1)", "range(1, 2*n)", "Polynomial endpoints"),
    ("ignore inverse", "adjoint(operators[symbol]) if inverse else operators[symbol]",
     "operators[symbol]", "Signed-word complete endpoint"),
    ("omit final return", "enumerate(zip(left, right))", "enumerate(zip(left[:-1], right[:-1]))",
     "Zero-axis scalar group"),
    ("remove Gram normalization", "G(0))/d\n             for right", "G(0))\n             for right",
     "Independent dense norm"),
]


def audit(write=False):
    results = []
    for label, old, new, expected in MUTATIONS:
        for optimized in (False, True):
            with tempfile.TemporaryDirectory(prefix="clifford-gram-mutation-") as directory:
                target = Path(directory) / "package"
                shutil.copytree(HERE, target, ignore=shutil.ignore_patterns("__pycache__"))
                source = target / "certify.py"
                original = source.read_text(encoding="utf-8")
                if original.count(old) != 1:
                    raise ValueError("Mutation target is not unique: "+label)
                source.write_text(original.replace(old, new), encoding="utf-8")
                command = [sys.executable, "-I", "-W", "error", "-B"]
                if optimized:
                    command.append("-O")
                command += [str(target / "verify.py"), "--write"]
                run = subprocess.run(command, text=True, capture_output=True, timeout=180)
                if run.returncode == 0 or "ValueError: "+expected not in run.stderr:
                    raise ValueError("Mutation did not fail at its semantic check: "+label+"\n"+run.stdout+run.stderr)
                results.append({"mutation": label, "optimized": optimized, "rejection": expected})
    receipt = {"status": "PASS_CLIFFORD_GRAM_MUTATIONS", "cases": results}
    path = HERE / "MUTATIONS.json"
    if write:
        path.write_text(json.dumps(receipt, indent=2, sort_keys=True)+"\n", encoding="utf-8")
    elif json.loads(path.read_text(encoding="utf-8")) != receipt:
        raise ValueError("Committed mutation receipt mismatch")
    print(receipt["status"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Regenerate the mutation receipt")
    audit(parser.parse_args().write)
