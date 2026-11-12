from collections import Counter
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
from json import dumps,loads
from pathlib import Path
from runpy import run_path

ROOT=Path(__file__).resolve().parent
PINS={
 "inputs/7334-WORD.json.gz":"4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
 "inputs/R92-PRICE.json":"05d7a5ebdd2eeedd6c8f534e8e2eeac22484daf9f387f4a6b88cc9eed22a6b8f",
 "inputs/pricing.py":"f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
}
for name,h in PINS.items():
    assert sha256((ROOT/name).read_bytes()).hexdigest()==h
w=loads(decompress((ROOT/"inputs/7334-WORD.json.gz").read_bytes()))
p=loads((ROOT/"inputs/R92-PRICE.json").read_bytes())
rows=[]
for i,e in enumerate(w["program"]):
    if e[0]=="MOVE" and e[4] is True:
        _,role,a,b,_=e
        r=len(w["frames"][a])-len(w["frames"][b])
        if r>1 and len(w["frames"][b])==1:
            rows.append([i,role,a,b,r])
assert len(rows)==8 and Counter(r[-1] for r in rows)=={2:4,4:3,5:1}
stock=Counter()
for *_,r in rows:
    stock[r]+=17
    stock[1]-=17
cost=run_path(str(ROOT/"inputs/pricing.py"))["cost"]
bounds=cost(stock,Q(p["old_crossing_upper"]))
assert 0<bounds[0]<=bounds[1]<289
print(dumps({"pins":PINS,"head":p["head"],"caller":p["caller_head"],
             "census":rows,"gross":bounds,"whole_relaxation_strict_upper":289},
             indent=2,sort_keys=True,default=str))
