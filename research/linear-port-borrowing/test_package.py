#!/usr/bin/env python3
"""Package rejection checks; run from any directory, Python >=3.12."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent


def run(path):
    return subprocess.run([sys.executable, "-B", "-O", str(path/"verify.py")],
                          text=True, capture_output=True, timeout=180)


def main():
    labels = []
    with tempfile.TemporaryDirectory(prefix="linear-port-controls-") as folder:
        base = Path(folder)
        for filename in ("borrow.py", "checks.py", "verify.py", "test_package.py",
                         "vendor/pr822/reuse.py", "vendor/pr822/NOTICE.md", "vendor/pr822/PROOF.md"):
            trial = base/"trial"
            shutil.copytree(ROOT, trial)
            with (trial/filename).open("ab") as f:
                f.write(b"\n# changed source\n")
            result = run(trial)
            if result.returncode == 0 or "pin" not in result.stderr:
                raise ValueError("source mutation accepted or wrong failure: "+filename)
            labels.append("modified "+filename)
            shutil.rmtree(trial)
        for label, mutate in [
            ("undercharged calls", lambda x: x["fixtures"][-2].update(calls=1567)),
            ("undercharged rows", lambda x: x["fixtures"][-2]["dirty_rows"].update(borrowed_cap=2)),
            ("undercharged precision", lambda x: x["fixtures"][-2]["dense"]["borrowed_L2_sign1"]["invoice"].update(precision_bits=1)),
            ("undercharged routing", lambda x: x["fixtures"][-2]["dense"]["borrowed_L2_sign1"]["invoice"].update(head_steps_cells=0)),
            ("float instead of integer", lambda x: x.update(seed=56.0)),
        ]:
            trial = base/"trial"
            shutil.copytree(ROOT, trial)
            expected = json.loads((trial/"EXPECTED.json").read_text())
            mutate(expected)
            (trial/"EXPECTED.json").write_text(json.dumps(expected))
            result = run(trial)
            if result.returncode == 0 or "certificate differs" not in result.stderr:
                raise ValueError("receipt mutation accepted or wrong failure: "+label)
            labels.append(label)
            shutil.rmtree(trial)
        trial = base/"trial"
        shutil.copytree(ROOT, trial)
        path = trial/"SOURCES.json"
        path.write_text(path.read_text().replace('"base_commit":', '"base_commit":"duplicate","base_commit":', 1))
        result = run(trial)
        if result.returncode == 0 or "duplicate JSON key" not in result.stderr:
            raise ValueError("duplicate JSON key accepted or wrong failure")
        labels.append("duplicate manifest key")
    print(json.dumps({"status": "PASS", "rejected": len(labels), "controls": labels}, sort_keys=True))


if __name__ == "__main__":
    main()
