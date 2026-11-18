"""Check the pinned input bytes and the complete application receipt."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import need, provenance, read, receipt
from application import CLAIM, verify

if __name__ == "__main__":
    need(sys.flags.optimize == 0, "source compiler assertions enabled")
    pins = provenance()
    result = verify()
    receipt("application", result)
    charts = [read(f"results/catalogue-{i}.json") for i in range(3)]
    need([r["shard"] for r in charts] == [0, 1, 2] and {r["total_pairs"] for r in charts} == {2962}
         and sum(r["checked_pairs"] for r in charts) == 2962
         and sum(r["ports"] for r in charts) == 104 and sum(r["contacts"] for r in charts) == 1664,
         "complete registered catalogue coverage")
    dense = {tuple(pair) for r in charts for pair in r["dense_pairs"]}
    need({(3, 498), (498, 127), (3, 595), (595, 127)} <= dense, "all four split routes have dense checks")
    print("PASS_COMPOSED_APPLICATION", CLAIM, result["paid"], result["productive"], pins)
