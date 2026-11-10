"""Find equal transported IDLE projections in the full public caller."""
from collections import defaultdict
from fractions import Fraction as F
from pathlib import Path
import json,random

root=Path(__file__).resolve().parent
data=json.loads((root/"PR7000-CALLER.json").read_bytes())
src=(root/"jclib_6936.py").read_text()
ns={"__file__":str(root/"jclib_6936.py")}
exec(src[:src.index("CONST =")]+src[src.index("PM ="):src.index("# ---------------------------------------------------------------- own resynthesis")],ns)
PM,IM,HALF=(ns[k] for k in ("PM","IM","HALF"))
def mod(value):
    x=F(value)
    return x.numerator*pow(x.denominator,-1,PM)%PM
def signatures(q,ds):
    n=data["roles"]
    eye=[[int(i==j) for j in range(n)] for i in range(n)]
    rows=[r.copy() for r in eye]
    columns=[r.copy() for r in eye]
    out={}
    qi=pow(q,-1,PM)
    a2=mod(data["types"]["A"]["alpha2"])
    def add(d,s,c):
        rows[d]=[(x+c*y)%PM for x,y in zip(rows[d],rows[s])]
        columns[s]=[(x-c*y)%PM for x,y in zip(columns[s],columns[d])]
    def scale(r,c):
        rows[r]=[x*c%PM for x in rows[r]]
        ci=pow(c,-1,PM)
        columns[r]=[x*ci%PM for x in columns[r]]
    for i,(tag,op,*a) in enumerate(data["events"]):
        if tag=="J":
            s,d,x,y=a[0]
            add(d,s,qi)
            add(x,y,a2*q%PM)
            for r in a[0]:
                scale(r,ds[op])
            s,t,al,be=a[1]
            alpha,beta=mod(al),mod(be)
            add(s,t,alpha*q%PM)
            add(t,s,beta*qi%PM)
            scale(s,ds[op])
            scale(t,ds[op])
        elif op=="ADD":
            add(a[0],a[1],mod(a[2]))
        elif op=="SWAP":
            s,d=a
            rows[s],rows[d]=rows[d],rows[s]
            columns[s],columns[d]=columns[d],columns[s]
        elif op=="SCALE":
            scale(a[0],mod(a[1]))
        elif op=="LAMBDA":
            s=a[1]
            scale(a[0],((1+s*IM)+(1-s*IM)*q*q)*HALF%PM)
        elif op=="QUERY":
            add(a[0],a[1],pow(q,a[2]%4,PM))
        elif op=="IDLE_ONE":
            r,labels=a
            pivot=next(x for x in rows[r] if x)
            out[i]=(tuple(x*pow(pivot,-1,PM)%PM for x in rows[r]),tuple(x*pivot%PM for x in columns[r]))
            c=1
            for stage in labels:
                c=c*ds[stage]%PM
            scale(r,c)
        else:
            raise ValueError(op)
    assert rows==ns["replay_matrix"](data,q,ds)
    assert all(sum(x*y for x,y in zip(row,col))%PM==(i==j)
               for i,row in enumerate(rows) for j,col in enumerate(columns))
    return out
rnd=random.Random(931)
groups=defaultdict(list)
points=[(q,{stage:rnd.randrange(2,PM) for stage in range(1,19)}) for q in (1,IM,PM-1,PM-IM)*2]
keys=defaultdict(list)
for q,ds in points:
    for i,sig in signatures(q,ds).items():
        keys[i].append(sig)
for i,values in keys.items():
    groups[(data["events"][i][0],tuple(values))].append(i)
matches=[]
for group in groups.values():
    if len(group)<2:
        continue
    matches.append([{"index":i,"event":data["events"][i]} for i in group])
with (root/"PR7000-TRANSPORTED-IDLE-PROJECTORS.json").open("x") as out:
    json.dump({"sample_points":len(points),"jobs":len(keys),"potential_equal_projector_groups":matches,
               "scope":"Exact finite-field full caller prefix/inverse propagation across all four q roots and two D tuples. If two projections differ in any sampled field evaluation they cannot be identical over the pinned dyadic formal ring. Coincidence only gives a candidate."},out,indent=2)
print("idle jobs",len(keys),"projector matches",len(matches),flush=True)
