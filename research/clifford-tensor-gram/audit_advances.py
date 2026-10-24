"""Reject compact-computation defects in private package copies.

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
    ("conjugate native C factor", "quadratic.py", "G.pair(1, sign)/2", "G.pair(1, -sign)/2", "Native trace phase"),
    ("ignore native inverse sign", "quadratic.py", "out.append((kind, gate[1], -gate[2]))",
     "out.append((kind, gate[1], gate[2]))", "Native entry phase"),
    ("omit output prefix constraint", "quadratic.py",
     "equations += [left.outputs[j] ^ x for j, x in enumerate(output_prefix)]",
     "equations += []", "Native partial inner product"),
    ("omit final native return", "compact.py", "enumerate(zip(left, right))",
     "enumerate(zip(left[:-1], right[:-1]))", "Compact complete endpoint"),
]


def audit(write=False):
    results = []
    for label, filename, old, new, expected in MUTATIONS:
        for optimized in (False, True):
            with tempfile.TemporaryDirectory(prefix="clifford-advance-mutation-") as directory:
                target = Path(directory) / "package"
                shutil.copytree(HERE, target, ignore=shutil.ignore_patterns("__pycache__"))
                source = target / filename
                original = source.read_text(encoding="utf-8")
                if original.count(old) != 1:
                    raise ValueError("Mutation target is not unique: "+label)
                source.write_text(original.replace(old, new), encoding="utf-8")
                command = [sys.executable, "-I", "-W", "error", "-B"]
                if optimized:
                    command.append("-O")
                command += [str(target / "verify_advances.py"), "--write"]
                run = subprocess.run(command, text=True, capture_output=True, timeout=180)
                if run.returncode == 0 or "ValueError: "+expected not in run.stderr:
                    raise ValueError("Mutation did not fail at its semantic check: "+label+"\n"+run.stdout+run.stderr)
                results.append({"mutation": label, "optimized": optimized, "rejection": expected})
    receipt = {"status": "PASS_CLIFFORD_ADVANCE_MUTATIONS", "cases": results}
    path = HERE / "ADVANCES-MUTATIONS.json"
    if write:
        path.write_text(json.dumps(receipt, indent=2, sort_keys=True)+"\n", encoding="utf-8")
    elif json.loads(path.read_text(encoding="utf-8")) != receipt:
        raise ValueError("Committed advance mutation receipt mismatch")
    print(receipt["status"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Regenerate the advance mutation receipt")
    audit(parser.parse_args().write)
