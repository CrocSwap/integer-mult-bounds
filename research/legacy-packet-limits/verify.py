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
run_root = work / "source"
checks = [
    ("packet-joint-basis/run_checks.py", ["--run", str(run_root), "--work", str(work / "joint-results")]),
]
for name in ("zero", "four", "eight"):
    checks.append(("productive-joint-research/screen_delayed_injection.py", [
        "--word", str(run_root / "frontier/refresh-6/replay564-root" / (name + "-cold-local/CANONICAL-WORD.json.gz")),
        "--out", str(run_root / "productive-joint-research" / (name.upper() + "-DELAYED-INJECTION.json")),
    ]))
checks.append(("productive-joint-research/check_delayed_injection.py", []))
child_env = os.environ.copy()
child_env.pop("PYTHONOPTIMIZE", None)
results = []
for index, (name, arguments) in enumerate(checks):
    script = work / "source" / name
    started = time.monotonic()
    result = subprocess.run([sys.executable, "-B", str(script)] + arguments, cwd=script.parent,
                            capture_output=True, text=True, env=child_env, timeout=180)
    (work / f"check-{index}.stdout.log").write_text(result.stdout)
    (work / f"check-{index}.stderr.log").write_text(result.stderr)
    results.append({"check": name, "exit_code": result.returncode,
                    "seconds": time.monotonic() - started})
    (work / "RUN.json").write_text(json.dumps(results, indent=2) + "\n")
    if result.returncode:
        raise RuntimeError("CHECK_FAILED " + name)
print("PASS_LEGACY_PACKET_LIMITS checks=5")
