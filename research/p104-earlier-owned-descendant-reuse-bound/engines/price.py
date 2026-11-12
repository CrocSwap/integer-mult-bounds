from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations
from json import dumps,loads
from pathlib import Path
from runpy import run_path

R=Path(__file__).resolve().parents[1]
PINS={"inputs/R198.json":"f7cbbca8b9b17405427dd7bb8a132e53b34f1c4646918d7a9bf174f1531add49",
      "inputs/R92-PRICE.json":"05d7a5ebdd2eeedd6c8f534e8e2eeac22484daf9f387f4a6b88cc9eed22a6b8f",
      "inputs/pricing.py":"f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182"}
for name,h in PINS.items():
    assert sha256((R/name).read_bytes()).hexdigest()==h
rows=loads((R/"inputs/R198.json").read_bytes())["records"]
p=loads((R/"inputs/R92-PRICE.json").read_bytes())
k=Q(p["old_crossing_upper"])
cost=run_path(str(R/"inputs/pricing.py"))["cost"]
keys=[r["key"] for r in rows]
assert len(keys)==8 and keys==sorted(keys)
one={rank:cost({rank:17},k) for *_,rank in keys}
cases=[]
for i,key in enumerate(keys):
    for l in range(1,i+1):
        for j in combinations(range(i),l):
            charts={keys[t][3] for t in j}-{key[3]}
            paid=1+len(charts)
            gross=[v-17*paid for v in one[key[4]]]
            assert gross[0]>0 or gross[1]<0
            cases.append({"target":i,"donors":j,"new_rank1":paid,
                          "gross":gross,"price_positive":gross[0]>0})
assert len(cases)==247
print(dumps({"pins":PINS,"keys":keys,"head":p["head"],"caller":p["caller_head"],
             "scope":"one rank-one target lift and one rank-one descent per distinct non-target source chart; ordinary free",
             "cases":cases,"positive_count":sum(x["price_positive"] for x in cases)},
            indent=2,sort_keys=True,default=str))
