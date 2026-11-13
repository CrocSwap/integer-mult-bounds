"""Run independent native, signed invoice, ordinary, and interval gates."""
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
from random import Random
import gzip
import json

from signed_model import signed_model
from interval_gate import gate,moment
import signed_child
root=Path(__file__).resolve().parent
cpath=root/"ODD-TYPE-AB-CALLER.json"
C=json.loads(cpath.read_bytes())
r=json.loads((root.parent/"RESULT.json").read_text())
w=json.loads(gzip.decompress((root.parent/"WORD.json.gz").read_bytes()))
digest=sha256(json.dumps(w,sort_keys=True,separators=(",",":")).encode()).hexdigest()
assert digest==r["word_canonical_sha256"]
ind=signed_model()
N=r["native"]|{name:{int(j):x for j,x in r["native"][name].items()} for name in ("helpers","paid","rises")}
actual_native=ind.native(w)
assert actual_native==N and not N["bad_inputs"], "Fresh complete native inventory and arbitrary-input adjoint"
odd_grid=json.loads((root/"ODD-CALLER-EXACT-GRID.json").read_text())
assert odd_grid["caller_sha256"]==sha256(cpath.read_bytes()).hexdigest()
code=(root/"independent.py").read_text()
f=code[code.index("def invoices("):code.index("def main(")]
assert f.count("assert calls==18")==f.count("calls=18;")==1
f=f.replace("assert calls==18","assert calls==C['stages']")
f=f.replace("calls=18;","calls=C['stages'];")
f=f.replace("elif e[1]=='IDLE_ONE':P[8*len(e[3])]+=ports","elif e[1] in ('IDLE_ONE','IDLE_ODD'):P[8*len(e[3])+(e[1]=='IDLE_ODD')]+=ports")
f=f.replace("queryroute=sum(p*1000*(2+(e[4]==-1)) for e in qr)",
            "queryroute=sum(p*1000*(2+(e[4]==-1)) for e in qr)\n  fusedroute=sum(36500*p for e in C['events'] if e[:2]==[ty,'IDLE_ODD'])")
f=f.replace("idle_routes=idleroute,query_routes=queryroute)","idle_routes=idleroute,query_routes=queryroute,fused_routes=fusedroute)")
exec(compile(f,str(root/"independent.py"),"exec"),ind.__dict__)
invoice=ind.invoices(w,C,N)
reference=json.loads((root/"ODD-TYPE-AB-REPLAY.json").read_text())
for t,k in (("T","target"),("P","paid")):
    assert {str(x):y for x,y in invoice[t].items()}==reference[k]
ordinary=ind.ordinary(w,C,N)
surcharge=0
for e in C["events"]:
    if e[0]=="J" or e[1] not in ("ADD","SCALE"):
        continue
    q=Q(e[-1]);a,d=abs(q.numerator),q.denominator
    def smooth(x):
        assert x>0
        for p in (2,3,5):
            while x%p==0:x//=p
        return x==1
    assert smooth(d)
    if e[1]=="SCALE":assert smooth(a)
    surcharge+=len(C["types"][e[0]]["ports"])*4*(a.bit_length()+d.bit_length()+1+(a.bit_count() if e[1]=="ADD" else 0))
ordinary["all_caller_scalar_surcharge"]=surcharge
conversions=2*sum(t["roles"]*len(t["ports"]) for t in C["types"].values())
scale=int(odd_grid["caller_odd_scale"])
# Two scale/reciprocal services, conservatively using the complete
# binary numerator and denominator lengths for every owner.
extra=conversions*4*(scale.bit_length()+1+scale.bit_count())
ordinary["charged_caller_odd_conversions"]=extra
ordinary["conservative_total"]+=surcharge+extra
ordinary["margin_to_billion"]=10**9-ordinary["conservative_total"]
print("ordinary bill",ordinary["conservative_total"],flush=True)
assert ordinary["margin_to_billion"]>0
claim=Q('0.003647081039689')
tested=claim+Q(7,10**17)
while tested>=Q(reference["raw_bracket"][0]):
    tested=claim+(tested-claim)/10
bracket=reference["raw_bracket"]
g=gate(invoice,claim,tested,*bracket,r["gate"]["BIT_pin"])
try:
    gate(invoice,claim,Q(bracket[0]),*bracket,r["gate"]["BIT_pin"])
except AssertionError:
    crossing_probe_rejected=True
else:
    raise AssertionError("Probe at lower crossing unexpectedly accepted")
prior={int(j):v for j,v in r["invoice"]["T"].items()}
for j,v in r["invoice"]["P"].items():prior[int(j)]=prior.get(int(j),0)-v
assert moment(prior,claim)[1]<0
signed_child.LAYOUT=C["ambient_rank"]
stages=sorted({e[3][0] for e in C["events"] if e[:2]==["B","IDLE_ODD"]})
rng=Random(0)
routes=[signed_child.check_finite(j,width,rng) for j in stages for width in (1,2,3)]
record={"caller_sha256":sha256(cpath.read_bytes()).hexdigest(),"native_sha256":digest,
        "invoice":invoice,"ordinary":ordinary,"compiler_outer":g,"finite_rank9_fields":routes,
        "crossing_probe_rejected":crossing_probe_rejected,"scope":"Fresh complete changed-native arbitrary-input adjoint; fresh exact signed caller and invoice, ordinary source-unit upper bill, inherited numerical compiler and outer inequalities, and signed rank9 child finite field routes. Fresh integrated physical native/caller and changed-word precision/occurrence application remain separate."}
with (root/"ODD-ADMISSION-PARTIAL.json").open("x") as f:json.dump(record,f,indent=2)
print("PASS partial signed short gates",ordinary["conservative_total"],g["claim"],g["outer"],flush=True)
