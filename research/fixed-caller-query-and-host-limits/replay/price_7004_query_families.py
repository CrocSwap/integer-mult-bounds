"""Measure what an entire caller-level QUERY family would buy on pinned invoices."""
from collections import Counter
from fractions import Fraction as F
from pathlib import Path
import json
root=Path(__file__).resolve().parent
ref=root/"reprice_7002_host.py"
ns={"__file__":str(ref)}
exec(ref.read_text().split("report={}")[0],ns)
price=ns["price"]
caller=json.loads((root/"PR7000-CALLER.json").read_text())
c={name:len(typ["ports"]) for name,typ in caller["types"].items()}
data=json.loads((root/"PR7004-RESULT.json").read_text())
bit=json.loads((root/"PR7001-RESULT.json").read_text())
complex_pair=tuple({int(r):v for r,v in data["invoice"][key].items()} for key in ("T","P"))
bit_pair=tuple({int(r):v for r,v in bit[key].items()} for key in ("targets","paid"))
result={}
for k in (F(".004"),F(".005")):
    cases={}
    for name,(target,paid) in (("complex",complex_pair),("bit",bit_pair)):
        lo,hi=price(target,paid,k)
        case={"signed_moment":list(map(str,(lo,hi))),
              "minimum_rank_one_equivalent":max(0,(-hi)//1+1)}
        if name=="complex":
            case["after_one_A_query_removed"]=list(map(str,(lo+c["A"],hi+c["A"])))
            case["after_one_A_and_one_B_query_removed"]=list(map(str,(lo+sum(c.values()),hi+sum(c.values()))))
        cases[name]=case
        print(k,name,"margin",float(hi),"need",case["minimum_rank_one_equivalent"])
    print(k,"complex after one A query",float(F(cases["complex"]["after_one_A_query_removed"][1])))
    result[str(k)]=cases
with (root/"PR7004-QUERY-FAMILY-TARGET-PRICE.json").open("x") as out:
    json.dump({"queries_by_family":dict(Counter(e[0] for e in caller["events"] if e[1]=="QUERY")),
               "ports":c,"target_prices":result,
               "scope":"Exact raw-moment bounds with fixed targets, using source-bound complex and BIT invoices. Query removal is a hypothetical change and not an operator identity, physical or outer admission."},out,indent=2)
