"""Runner: complete the F2^5 vanishing census (verify.py classify) resumably.

Repeatedly invokes verify.py classify (per-shard receipts in
CENSUS-PROGRESS.json) until the PASS_F7_18POINT_CLASSIFY marker appears.
The receipt file must not exist beforehand for a full recomputation.

Usage: python3 -I -B run_classify_all.py [--seconds S]
"""

import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
PY = sys.executable


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    seconds = "540"
    if "--seconds" in sys.argv:
        seconds = sys.argv[sys.argv.index("--seconds") + 1]
    progress = HERE / "CENSUS-PROGRESS.json"
    if not progress.exists():
        print("CLASSIFY_RUNNER fresh receipts confirmed (no CENSUS-PROGRESS.json)", flush=True)
    else:
        print("CLASSIFY_RUNNER WARNING receipts already exist", flush=True)
    rounds = 0
    while True:
        rounds += 1
        t0 = time.time()
        proc = subprocess.run(
            [PY, "-I", "-B", str(HERE / "verify.py"), "classify", "--seconds", seconds],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        out = (proc.stdout or "") + (proc.stderr or "")
        sys.stdout.write(out)
        sys.stdout.flush()
        if proc.returncode != 0:
            print("CLASSIFY_RUNNER exit=%d round=%d" % (proc.returncode, rounds))
            raise SystemExit(proc.returncode)
        if "PASS_F7_18POINT_CLASSIFY" in out:
            print("CLASSIFY_RUNNER complete rounds=%d" % rounds, flush=True)
            return
        print(
            "CLASSIFY_RUNNER checkpoint round=%d wall=%.1fs" % (rounds, time.time() - t0),
            flush=True,
        )


if __name__ == "__main__":
    main()
