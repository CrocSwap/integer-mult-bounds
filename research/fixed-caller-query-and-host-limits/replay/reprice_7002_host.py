"""Independent rational target budgets for the connected L18 caller."""
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import sys

root=Path(__file__).resolve().parent
sys.path.insert(0,str(root/"package"))
from verify import enclosure,SCALE
source=root/"connected7002"/"COALESCING-WINDOW.json"
receipt=json.loads(source.read_bytes())
native=json.loads((root/"connected7002"/"inputs/base_invoice.json").read_bytes())
C=json.loads((root/"connected7002"/"COST.json").read_bytes())["18"]
ports=104
stages=C["stages"]
repairs=ports*stages
def hist(d):
    return {int(k):v for k,v in d.items()}
t,p=map(hist,(receipt["T"],receipt["P"]))
assert p[1]==stages*hist(native["local_paid"])[1]+ports*C["paid_outside_native"]["1"]+repairs
assert t[1]==stages*hist(native["helpers"])[1]
assert sum(r*(t.get(r,0)-p.get(r,0)) for r in t.keys()|p.keys())==receipt["rank_surplus"]
def price(t,p,k):
    low=high=0
    for r in t.keys()|p.keys():
        c=t.get(r,0)-p.get(r,0)
        if not c:
            continue
        lo,hi=enclosure(r,k)
        low+=c*(lo if c>0 else hi)
        high+=c*(hi if c>0 else lo)
    return Fraction(low,SCALE),Fraction(high,SCALE)
report={}
for k in (Fraction(1,200),Fraction(1,100)):
    lo,hi=price(t,p,k)
    assert hi<0
    lower_minimum=(-hi)//1+1
    assert lower_minimum==(-lo)//1+1
    free=(lo+repairs,hi+repairs)
    assert free[0]>0
    eight_batched={**p,1:p[1]-repairs,8:p[8]+repairs//8}
    assert repairs%8==0
    eight=price(t,eight_batched,k)
    assert eight[1]<0
    allowed=repairs-lower_minimum
    report[str(k)]={"fixed_F_plus_H1_moment":list(map(str,(lo,hi))),
                    "minimum_removed_H1_equivalents_for_raw_positivity":lower_minimum,
                    "maximum_H1_equivalents_remaining":allowed,
                    "max_fraction_of_original_H1_repair_budget_remaining":str(Fraction(allowed,repairs)),
                    "free_repairs_moment":list(map(str,free)),
                    "hypothetical_same_rank_mass_rank8_pack_moment":list(map(str,eight))}
    print(k,"baseline",float(hi),"min H1 removed",lower_minimum,"allowed",allowed,"free",float(free[0]),"rank8 pack",float(eight[1]))
with (root/"PR7002-HOST-REPAIR-TARGET-BUDGET.json").open("x") as out:
    json.dump({"head":"ed1a0a83dfe5d28db9a971bcfc1403bcdc03a49b",
               "invoice_sha256":sha256(source.read_bytes()).hexdigest(),
               "paid_repairs":repairs,"at_targets":report,
               "scope":"Raw complex-side screening with optimistically coalesced coordinate idles and fixed native helper targets. Free and rank8 tariffs are hypothetical. No HOST implementation, ordinary cost, BIT, or outer admission."},out,indent=2)
