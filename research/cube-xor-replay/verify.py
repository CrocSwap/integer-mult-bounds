#!/usr/bin/env python3
"""Full bounded row equality plus complete receipts and local controls."""
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import replay


def main():
    coverage = {"rows": 0, "coefficients": 0}
    for case in ("historical", "t6"):
        value = replay.run(case, "differential", coverage)
        print(f"PASS_CUBE_XOR_DIFFERENTIAL case={case}", flush=True)
    expected = {"rows": 4324, "coefficients": 8596927616}
    replay.require(coverage == expected, "Incomplete differential coverage")
    t6 = json.loads(value)
    replay.require(t6["binary_rank_lower_bound"] == 3088
                   and t6["specified_core_positive_deficit_excluded"] is False,
                   "Wrong bounded screen result")
    subprocess.run([sys.executable, "-I", "-O", "-B", str(HERE / "test_replay.py")],
                   check=True)
    print("PASS_CUBE_XOR_VERIFICATION rows=4324 coefficients=8596927616 "
          "t6_rank=3088 t6_excluded=false", flush=True)


if __name__ == "__main__":
    main()
