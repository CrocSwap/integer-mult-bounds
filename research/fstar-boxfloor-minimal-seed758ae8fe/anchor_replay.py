#!/usr/bin/env python3
"""KB5k anchor reproduction: run the vendored PR 2978 verify.py UNCHANGED on a
byte-copy of the vendored tree (so its receipts cannot touch pinned bytes) and
assert every recorded anchor marker, including the calibration values of the
PR 2914 engine lineage.

Prints PASS_KM_ANCHORS with the marker counts. Run: python3 -B anchor_replay.py
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
VEND = os.path.join(HERE, "predecessor", "pr2978")

REQUIRED = [
    r"^PASS_KJ_PINS pr2963-pins=14 own-pins=29",
    r"^PASS_FG_CONTROLS ",
    r"^PASS_FG_CALIBRATION tied_min=11/12 cex_min_1=18/19 mp=9/16 "
    r"chain=22 reach=0/12,8/19",
    r"^PASS_KJ_ANCHORS named=9x12 box-replay-in-box=12/12",
    r"^PASS_KJ_TAU0_DEMO cert=2 box=1",
    r"^PASS_KJ_COUNTEREXAMPLE v=3 tau=2/2/2 cert=3 box=2 r_box=2 "
    r"independent=3/2",
    r"^PASS_KJ_V2 configs=2842 box-equals-cert=2842 tau0-demo=2/1",
    r"^PASS_KJ_V3 configs=3023 box-equals-cert=2996 candidates=27",
    r"^PASS_KJ_ESCAPE escapes=19 kinds=E1x19 drops=0 box-gaps=0",
    r"^PASS_KJ_REALIZE candidates=27 realized=3 unrealizable-column=3 "
    r"not-found-in-cap=21 counterexamples=3",
    r"^PASS_KJ_WITHOUTLOSS verdict=counterexample v=3 tau>=1 cert=3>box=2",
    r"certificate digest 0b5b55f84375b37c",
]


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    tmp = os.path.join(tempfile.gettempdir(), "opencode", "agent-79",
                       "anchor-run")
    if os.path.isdir(tmp):
        shutil.rmtree(tmp)
    shutil.copytree(VEND, tmp)
    proc = subprocess.run(
        [sys.executable, "-B", os.path.join(tmp, "verify.py")],
        capture_output=True, text=True, encoding="utf-8", timeout=540)
    out = proc.stdout
    assert proc.returncode == 0, (proc.returncode, proc.stderr[-2000:])
    missing = []
    for pat in REQUIRED:
        if re.search(pat, out, re.M) is None:
            missing.append(pat)
    assert not missing, "missing anchor markers: %s" % missing
    print("PASS_KM_ANCHORS markers=%d digest=0b5b55f84375b37c "
          "vendored-verify=exit0" % len(REQUIRED))


if __name__ == "__main__":
    main()
