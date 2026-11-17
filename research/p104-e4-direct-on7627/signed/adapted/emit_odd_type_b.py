"""Emit and independently replay the 8+9 type-B signed caller."""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import json

from signed_model import signed_model
import mirrored
from host34 import tr,m
import lower
def smooth(n):
    if not n:return False
    for prime in (2,3,5):
        while n%prime==0:n//=prime
    return n==1
def unit(q):
    q=Q(q)
    return smooth(abs(q.numerator)) and smooth(q.denominator)
lower.unit=unit
lower.dyadic=lambda q:smooth(Q(q).denominator)
lower_frame,backwards=lower.lower_frame,lower.backwards
root=Path(__file__).resolve().parent
witness=json.loads((root/"ODD-UNIT-DYADIC-TAPES.json").read_text())
group_path=root/"ODD-LOCALIZED-GROUPING.json"
grouped=json.loads(group_path.read_text())
p=root/"odd_unit_dyadic_tapes.py"
ns={"__file__":str(p)}
exec(compile(p.read_text().split("srcpath=root/",1)[0],str(p),"exec"),ns)
N,half,stages=ns["n"],ns["a"],ns["stages"]
chosen=min((g for g in grouped["results"] if "idles" in g),
           key=lambda g:g["idle_basis_ops"]+g["host_basis_ops"])
tape=next(v for v in witness["dyadic_tapes"] if [v["closure"],*v["padding"]]==chosen["parameter"])
blocks=[[[Q(q) for q in row] for row in v] for v in tape["sequence"]]
frames=[]
ns["tape"](blocks,frames=frames)
masks=ns["masks"]()
phase=(half,half,half+1,half+1)
core_plus_phase=N+len(phase)
diag=[[-1,0]+[int(i in ms) for ms in masks] for i in range(N)]
diag += [[-1,0]+[int(k==j) for k in range(1,stages+1)] for j in phase]
events=[]
def idle(stage,v,w):
    x={r:Q(q) for r,q in w};y={r:Q(q) for r,q in v}
    p=min(x,key=lambda r:(not unit(x[r]),r))
    L=lower_frame([x],[y],[p])
    return L+[['B','IDLE_ONE',p,stage]]+list(backwards(L))
def host(j):
    x,y,active=frames[j-1]
    C=[{i:q for i,q in enumerate(row) if q} for row in y]
    W=[{i:q for i,q in enumerate(row) if q} for row in tr(x)]
    s,t=0,1
    L=lower_frame(C,W,[s,t])
    B=tr(active)
    b,d=B[0]
    K=[[Q(1),Q(0)],[b/2,d/2]]
    R=[[Q(0),Q(2)],[Q(-1,2),Q(0)]]
    assert unit(d/2) and m(R,K)==m(K,B)
    frame=L+[['B','SCALE',t,str(d/2)]]
    if b:frame.append(['B','ADD',t,s,str(b/2)])
    before=frame+[['B','ADD',t,s,'-1/2'],['B','ADD',s,t,'1'],['B','LAMBDA',s,1]]
    after=[['B','LAMBDA',s,-1]]+list(backwards(frame))
    return before,after

groups=[(mask,v,w) for mask,v,w in chosen["idles"] if isinstance(mask,list)]
singles=[(mask,v,w) for mask,v,w in chosen["idles"] if isinstance(mask,int)]
for j in range(1,stages+1):
    for t,v,w in singles:
        if j==t:events.extend(idle([j],v,w))
    for i,p in enumerate(phase):
        if j==p:events.append(['B','IDLE_ODD',N+i,[j],-1])
    before,after=host(j)
    events.extend(before)
    events.append(['J',j,list(range(core_plus_phase,core_plus_phase+4)),[0,1,'-1','1/2']])
    events.extend(after)
    if j==half:
        for mask,v,w in groups:events.extend(idle(mask,v,w))
events.extend(['B','LAMBDA',r,-1] for r in range(N))
C={"stages":stages,"roles":core_plus_phase+4,
   "types":{"A":{"offset":core_plus_phase,"diagonal":[],"alpha2":"1"},"B":{"offset":0,"diagonal":diag}},
   "events":events}
# Dummy A rails supply the other half of the literal J interface. They
# are independent of B and excluded from this type-B-only certificate.
bill=Counter(8*len(e[3])+(e[1]=="IDLE_ODD") for e in events if e[:2] in (['B','IDLE_ONE'],['B','IDLE_ODD']))
expected=Counter({8:2*stages,9:4})
expected.update(8*j for length in (half,stages-half) for j in range(2,length) for _ in range(2))
assert bill==expected
ind=signed_model()
result=ind.caller(C)
assert not result["bad_outputs"],result
mutant=next(i for i,e in enumerate(events) if e[:2]==["B","ADD"])
assert ind.caller(C,mutant)["bad_outputs"]
with (root/"ODD-TYPE-B-CALLER.json").open("x") as f:json.dump(C,f,separators=(",",":"))
record={"grouping_sha256":sha256(group_path.read_bytes()).hexdigest(),
        "caller_sha256":sha256((root/"ODD-TYPE-B-CALLER.json").read_bytes()).hexdigest(),
        "parameter":chosen["parameter"],"bill":dict(bill),"signed_replay":result,
        "mutation_rejects":mutant,"scope":"Full exact signed Laurent endpoint of the emitted 8+9 type-B branch, literal J opcodes, localized basis changes and all idle ranks. Excludes the four dummy A rails and all physical or precision admission."}
with (root/"ODD-TYPE-B-REPLAY.json").open("x") as f:json.dump(record,f,indent=2)
print("PASS exact short type B",len(events),"events",bill,flush=True)
