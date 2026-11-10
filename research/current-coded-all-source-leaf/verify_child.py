"""Re-execute complete source-bound rank-two child and meaningful failures.

Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import json
from check_child import run
from all_leaf_sources import HERE, need


def main():
    results = []
    for mode in ("success", "cutoff", "parity"):
        actual = run(mode)
        expected = json.loads((HERE/"receipts"/("rank2-"+mode+".json")).read_text())
        need(actual == expected, "complete physical rank-two "+mode+" receipt")
        results.append(dict(mode=mode, physical_actions=actual["physical_actions"]))
        print("PASS_RANK_TWO_PHYSICAL_"+mode.upper(), flush=True)
    print("PASS_CURRENT_CODED_ALL_SOURCE_CHILD", json.dumps(results, sort_keys=True))


if __name__ == "__main__":
    main()
