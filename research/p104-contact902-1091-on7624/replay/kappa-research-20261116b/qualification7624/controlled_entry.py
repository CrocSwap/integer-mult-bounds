#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Release the whole research job only after actual cgroup readback."""
import argparse
import json
import os
from pathlib import Path
import sys
import time

parser = argparse.ArgumentParser()
parser.add_argument("--control", type=Path, required=True)
parser.add_argument("--out", type=Path, required=True)
parser.add_argument("--freeze-sha", required=True)
parser.add_argument("--unit", required=True)
args = parser.parse_args()
ready = {"pid":os.getpid(),"cgroup":Path("/proc/self/cgroup").read_text().strip().split("::")[-1],
         "affinity":sorted(os.sched_getaffinity(0)),"source_executed":False}
with (args.control / "READY.pending").open("x") as stream:
    json.dump(ready, stream)
(args.control/"READY.pending").rename(args.control/"READY.json")
deadline = time.monotonic()+30
allow_path = args.control/"ALLOW.json"
while not allow_path.exists() and time.monotonic()<deadline:
    time.sleep(.01)
if not allow_path.exists():
    raise RuntimeError("no verified cgroup release")
allow = json.loads(allow_path.read_text())
if allow["unit"] != args.unit or allow["freeze_sha256"] != args.freeze_sha:
    raise ValueError("release binding")
if allow["guard_only"]:
    print("PASS_GUARD_ONLY_NO_SOURCE",flush=True)
else:
    root = Path(__file__).resolve().parent
    os.execv(sys.executable,[sys.executable,"-I","-B",str(root/"run_once.py"),
             "--out",str(args.out),"--freeze-sha",args.freeze_sha])
