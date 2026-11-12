"""Price removal of two odd target factors and two Type A query calls."""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path

ROOT = Path(__file__).resolve().parent
PINS = {
    "inputs/CALLER.json":"255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
    "inputs/R92-PRICE.json":"05d7a5ebdd2eeedd6c8f534e8e2eeac22484daf9f387f4a6b88cc9eed22a6b8f",
    "inputs/pricing.py":"f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
}
raw = {}
for name, pin in PINS.items():
    raw[name] = (ROOT/name).read_bytes()
    assert sha256(raw[name]).hexdigest() == pin
base,c = (loads(raw[k]) for k in ("inputs/R92-PRICE.json","inputs/CALLER.json"))
A = c["types"]["A"]
assert len(A["ports"]) == 96 and len(A["diagonal"]) == 36
ranks = [1+8*sum(row[2:]) for row in A["diagonal"]]
assert all(row[0:2] == [-1,0] for row in A["diagonal"])
assert [i for i,r in enumerate(ranks) if r == max(ranks)] == [0,18] and max(ranks)==137
assert [t for t,e in enumerate(c["events"]) if e[:2]==["A","QUERY"]]==[1516,1580,1659,1721]
p,t = (Counter({int(r):v for r,v in base[key].items()}) for key in ("old_paid","old_targets"))
stock = t.copy()
stock.subtract(p)
assert (sum(p.values()),sum(t.values()),sum(r*n for r,n in stock.items()))==(110519,22461,1424)
delta = {1:192,136:192,137:-192}
edit = stock.copy()
edit.update(delta)
assert sum(r*n for r,n in edit.items())==1424
cost = run_path(str(ROOT/"inputs/pricing.py"))["cost"]
q = {}
for label in ("old_crossing_upper","probe","moonshot"):
    k=Q(base[label])
    gross=cost(delta,k)
    q[label]=dict(gross=list(map(str,gross)), complete=list(map(str,cost(edit,k))),
                  whole_two_pairs_relaxed_upper=str(2*gross[1]))
assert Q(q["probe"]["complete"][0]) > 0
print(dumps(dict(head=base["head"],caller=base["caller_head"],pins=PINS,roots=[0,18],paid=110327,productive=22461,
                 paid_delta={1:-192},productive_delta={136:192,137:-192},quote=q,whole_compatible_relaxation=2),
            indent=2,sort_keys=True))
