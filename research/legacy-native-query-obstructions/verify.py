"""Run the saved exact checks in a new output directory."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

if not __debug__:
    raise RuntimeError("Assertions must remain enabled")
root = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument("--work", type=Path, required=True)
args = parser.parse_args()
work = args.work.resolve()
if work.exists():
    raise FileExistsError(work)
for entry in json.loads((root / "SOURCE-MANIFEST.json").read_text())["files"]:
    if hashlib.sha256((root / entry["path"]).read_bytes()).hexdigest() != entry["sha256"]:
        raise ValueError("SOURCE_HASH " + entry["path"])
work.mkdir(parents=True)
shutil.copytree(root / "source", work / "source")
checks = [
    "native-dual-number-proof/check.py",
    "native-dual-independent/check.py",
    "native-finite-proof/check.py",
    "native-shear-continuation/independent-audit/check.py",
    "native-shear-continuation/independent-audit/positive_five_check.py",
]
child_env = os.environ.copy()
child_env.pop("PYTHONOPTIMIZE", None)
results = []
for index, name in enumerate(checks):
    script = work / "source" / name
    started = time.monotonic()
    result = subprocess.run([sys.executable, "-B", str(script)], cwd=script.parent,
                            capture_output=True, text=True, env=child_env, timeout=120)
    (work / f"check-{index}.stdout.log").write_text(result.stdout)
    (work / f"check-{index}.stderr.log").write_text(result.stderr)
    results.append({"check": name, "exit_code": result.returncode,
                    "seconds": time.monotonic() - started})
    (work / "RUN.json").write_text(json.dumps(results, indent=2) + "\n")
    if result.returncode:
        raise RuntimeError("CHECK_FAILED " + name)
print("PASS_LEGACY_NATIVE_QUERY_OBSTRUCTIONS checks=5")
