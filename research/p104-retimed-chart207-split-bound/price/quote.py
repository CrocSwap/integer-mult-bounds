"""Complete fixed-paid rank-nine to rank-eight plus rank-one handoff quote."""
from collections import Counter
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import runpy

PINS={
 "ADMITTED.json":"c95300e9bca27e44a25c82d794f88cbf70757c142806b0e4c590ea29feb81a13",
 "RANK-STOCK.json":"4a7841699dd17688f6aada5c902a2a91e94558b2b1b4460c46b0e55aa95b3f9f",
 "pricing.py":"f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
}
ROOT=Path(__file__).resolve().parent/"inputs"
raw={}
for name,digest in PINS.items():
    data=(ROOT/name).read_bytes()
    if sha256(data).hexdigest()!=digest:
        raise ValueError("changed pinned input: "+name)
    raw[name]=data
base=json.loads(raw["RANK-STOCK.json"])
admit=json.loads(raw["ADMITTED.json"])
assert base["head"]==admit["head"]=="aaeec8c0acf01e99a5f331ef363a698d9c084ace"
assert admit["exit"]==0 and admit["status"]=="independently_reproduced_comparable"
k=Fraction(base["crossing_upper"])
assert k==Fraction(admit["crossing"][1])
paid, targets = (Counter({int(r):v for r,v in base[key].items()})
                 for key in ("old_complete_paid","complete_targets"))
new=targets.copy()
delta={1:17,8:17,9:-17}
new.update(delta)
pre,post=targets.copy(),new.copy()
pre.subtract(paid)
post.subtract(paid)
assert sum(paid.values())==110519 and sum(targets.values())==22461 and sum(new.values())==22478
assert sum(r*v for r,v in pre.items())==sum(r*v for r,v in post.items())==1424
cost=runpy.run_path(str(ROOT/"pricing.py"))["cost"]
old_margin,new_margin,credit=(cost(x,k) for x in (pre,post,delta))
assert old_margin[1]<0<new_margin[0] and 0<credit[0]<=credit[1]<1
print(json.dumps(dict(head=base["head"],kappa=admit["kappa"],old_crossing_upper=str(k),inputs=PINS,
    paid=paid,old_targets=targets,new_targets=new,productive_delta=delta,paid_delta={},
    signed_rank_surplus=1424,empty_credits=0,old_margin=list(map(str,old_margin)),
    new_margin=list(map(str,new_margin)),one_edit_optimistic_credit=list(map(str,credit)),
    margin_with_one_added_raw_rank_one_upper=str(new_margin[1]-1),
    geometry_stock_cap=13,simultaneous_edits_cap=1,qualification="price only, no literal chart support tested"),
    sort_keys=True,indent=2))
