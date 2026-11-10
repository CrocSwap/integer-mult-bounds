"""Enclose the real 75-job normalized schedule's savings and remaining gaps."""
from collections import Counter
from fractions import Fraction as F
import json
from pathlib import Path

root=Path(__file__).resolve().parent
src=root/"reprice_7002_host.py"
ns={"__file__":str(src)}
exec(src.read_text().split("report={}")[0],ns)
price,ports,t,p,C,native,stages=(ns[k] for k in ("price","ports","t","p","C","native","stages"))
new=json.loads((root/"PR7002-IDLE-PROJECTOR-ORDER-SEARCH.json").read_text())
old=json.loads((root/"PR7002-NONCOORDINATE-IDLE-WORD.json").read_text())
new_idle={int(k):ports*v for k,v in new["rank_histogram"].items()}
old_idle={int(k):ports*v for k,v in old["idle_rank_profile"].items()}
assert sum(r*n for r,n in new_idle.items())==sum(r*n for r,n in old_idle.items())
def invoice(idle):
    paid=Counter({int(k):stages*v for k,v in native["local_paid"].items()})
    paid.update(idle)
    paid[1]+=ports*(stages+C["paid_outside_native"]["1"])
    assert sum(r*n for r,n in paid.items())==sum(r*n for r,n in p.items())
    return paid
result={}
for k in (F(".004"),F(".005")):
    saving=price(old_idle,new_idle,k)
    assert saving[0]>0
    gap=price(t,invoice(new_idle),k)
    assert gap[1]<0
    floor=(-gap[1])//1+1
    assert floor==(-gap[0])//1+1
    result[str(k)]={"exact_104_port_saving":list(map(str,saving)),
                   "new_margin":list(map(str,gap)),"remaining_rank_one_equivalents":floor}
    print(k,"saving",float(saving[0]),"margin",float(gap[1]),"still need",floor,flush=True)
with (root/"PR7002-75-JOB-COMPOSITION-PRICE.json").open("x") as out:
    json.dump({"jobs_per_port":sum(new["rank_histogram"].values()),"tests":result,
               "scope":"Exact normalized schedule with the retained F+H1 tariff. Physical packed IDLE and basis costs, BIT and outer admission remain open."},out,indent=2)
