"""Disposable registered replay adapter; scientific programs unchanged."""
from pathlib import Path
import json, subprocess, sys, tempfile
root = Path(__file__).resolve().parent
with tempfile.TemporaryDirectory(prefix="mac-cf6a-replay-") as temp:
    out = Path(temp) / "run"
    subprocess.run([sys.executable, "-I", "-B", str(root / "run_verification.py"), "--out", str(out)], check=True)
    runs = json.loads((out / "RUNS.json").read_bytes())["runs"]
    if len(runs) != 4 or any(r["returncode"] != 0 or not r["owned_child_reaped"] for r in runs):
        raise RuntimeError("Incomplete scoped verification")
print("PASS_REGISTERED_SUPPLIED_WORD_AND_INVOICE_ONLY")
