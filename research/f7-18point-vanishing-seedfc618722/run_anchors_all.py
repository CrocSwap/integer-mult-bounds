"""Runner: re-walk both heavy anchors from EMPTY receipts, resumably.

Repeatedly invokes the byte-vendored anchors.py (per-sub-shard receipts in
ANCHOR-PROGRESS.json) until each mode prints PASS_ANCHORS_<MODE>.  The receipt
file must not exist beforehand: a walk against a committed receipt is receipt
validation, not recomputation (PR 2911's recorded correction).  Modes run
sequentially because both write the same receipt file.

Usage: python3 -I -B run_anchors_all.py [k10b3|k11b4] [--seconds S]
"""

import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
PY = sys.executable

MODES_ALL = ["k10b3", "k11b4"]


def run_mode(mode, seconds):
    rounds = 0
    while True:
        rounds += 1
        t0 = time.time()
        proc = subprocess.run(
            [PY, "-I", "-B", str(HERE / "anchors.py"), mode, "--seconds", str(seconds)],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        out = (proc.stdout or "") + (proc.stderr or "")
        sys.stdout.write(out)
        sys.stdout.flush()
        if proc.returncode != 0:
            print("ANCHOR_RUNNER %s exit=%d round=%d" % (mode, proc.returncode, rounds))
            return False
        if "PASS_ANCHORS_" in out:
            print("ANCHOR_RUNNER %s complete rounds=%d" % (mode, rounds), flush=True)
            return True
        print(
            "ANCHOR_RUNNER %s checkpoint round=%d wall=%.1fs" % (mode, rounds, time.time() - t0),
            flush=True,
        )


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    seconds = "540"
    if "--seconds" in sys.argv:
        seconds = sys.argv[sys.argv.index("--seconds") + 1]
    modes = args if args else MODES_ALL
    progress = HERE / "ANCHOR-PROGRESS.json"
    if not progress.exists():
        print("ANCHOR_RUNNER fresh receipts confirmed (no ANCHOR-PROGRESS.json)", flush=True)
    else:
        print("ANCHOR_RUNNER WARNING receipts already exist", flush=True)
    for mode in modes:
        if not run_mode(mode, seconds):
            raise SystemExit("anchor mode failed: %s" % mode)
    print("ANCHOR_RUNNER ALL COMPLETE", flush=True)


if __name__ == "__main__":
    main()
