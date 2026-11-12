from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from json import dumps,loads
from pathlib import Path
from runpy import run_path

ROOT=Path(__file__).resolve().parent
PINS={"inputs/R92-PRICE.json":"05d7a5ebdd2eeedd6c8f534e8e2eeac22484daf9f387f4a6b88cc9eed22a6b8f",
      "inputs/pricing.py":"f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182"}
for name,h in PINS.items():
    assert sha256((ROOT/name).read_bytes()).hexdigest()==h
old=loads((ROOT/"inputs/R92-PRICE.json").read_bytes())
k=Q(old["old_crossing_upper"])
cost=run_path(str(ROOT/"inputs/pricing.py"))["cost"]
delta=Counter({5:17,1:-17})
gross=cost(delta,k)
stock=Counter({int(r):n for r,n in old["old_targets"].items()})
stock.subtract({int(r):n for r,n in old["old_paid"].items()})
stock.update(delta)
assert 0<gross[0]<=gross[1]<68
print(dumps({"pins":PINS,"head":old["head"],"caller":old["caller_head"],
             "clock":39811,"owner":1503,"shadow":1504,"old_move":[520,595,5],
             "new_move":[3,595,1],"signed_delta":delta,"gross":gross,
             "full_old_probe_after":cost(stock,Q(old["probe"])),
             "eight_slot_raw_relaxation_below":289},default=str,indent=2,sort_keys=True))
