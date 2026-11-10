"""Check whether QUERY directions can merge with each other or a retained HOST shear."""
from collections import defaultdict
from fractions import Fraction as F
from pathlib import Path
import json,random

root=Path(__file__).resolve().parent
src=(root/"screen_7000_transported_idle_projectors.py").read_text()
ns={"__file__":str(root/"screen_7000_transported_idle_projectors.py")}
exec(src[:src.index("def signatures(")],ns)
data,PM,IM,HALF,mod=map(ns.get,("data","PM","IM","HALF","mod"))
def normalized(vec):
    z=next(x for x in vec if x)
    z=pow(z,-1,PM)
    return tuple(x*z%PM for x in vec)
def directions(q,D):
    n=data["roles"]
    rows=[[int(i==j) for j in range(n)] for i in range(n)]
    cols=[r.copy() for r in rows]
    signature={}
    def record(key,d,s):
        signature[key]=(normalized(cols[d]),normalized(rows[s]))
    def add(d,s,c):
        rows[d]=[(x+c*y)%PM for x,y in zip(rows[d],rows[s])]
        cols[s]=[(x-c*y)%PM for x,y in zip(cols[s],cols[d])]
    def scale(r,c):
        rows[r]=[x*c%PM for x in rows[r]]
        cols[r]=[x*pow(c,-1,PM)%PM for x in cols[r]]
    for i,(tag,op,*a) in enumerate(data["events"]):
        if tag=="J":
            s,d,x,y=a[0]
            record(("A","host",i,0),d,s)
            add(d,s,pow(q,-1,PM))
            record(("A","host",i,1),x,y)
            add(x,y,mod(data["types"]["A"]["alpha2"])*q%PM)
            for r in a[0]: scale(r,D[op])
            s,t,alpha,beta=a[1]
            record(("B","host",i,0),s,t)
            add(s,t,mod(alpha)*q%PM)
            record(("B","host",i,1),t,s)
            add(t,s,mod(beta)*pow(q,-1,PM)%PM)
            for r in (s,t):scale(r,D[op])
        elif op in ("ADD","QUERY"):
            d,s,c=a
            if op=="QUERY":
                record((tag,"query",i,0),d,s)
            add(d,s,mod(c) if op=="ADD" else pow(q,c%4,PM))
        elif op=="SWAP":
            s,d=a
            rows[s],rows[d]=rows[d],rows[s]
            cols[s],cols[d]=cols[d],cols[s]
        elif op=="SCALE":
            scale(a[0],mod(a[1]))
        elif op=="LAMBDA":
            v=a[1]
            scale(a[0],((1+v*IM)+(1-v*IM)*q*q)*HALF%PM)
        elif op=="IDLE_ONE":
            value=1
            for j in a[1]:value=value*D[j]%PM
            scale(a[0],value)
        else:raise ValueError(op)
    assert rows==ns["ns"]["replay_matrix"](data,q,D)
    return signature
rng=random.Random(722)
all_sigs=defaultdict(list)
for q in (1,IM,PM-1,PM-IM)*2:
    D={j:rng.randrange(2,PM) for j in range(1,19)}
    for key,pair in directions(q,D).items():
        all_sigs[key].append(pair)
matches=[]
tested=0
for first,a in all_sigs.items():
    if first[1]!="query":continue
    for second,b in all_sigs.items():
        if second==first or second[0]!=first[0] or (second[1]=="query" and second<first):
            continue
        tested+=1
        v=all(x[0]==y[0] for x,y in zip(a,b))
        u=all(x[1]==y[1] for x,y in zip(a,b))
        if v or u:matches.append({"query":first,"other":second,"same_range":v,"same_source":u})
with (root/"PR7000-QUERY-HOST-TRANSPORT-CONTACTS.json").open("x") as out:
    json.dump({"tested_pairs":tested,"matches":matches,"sample_count":8,
               "scope":"Conjugated shear image and source directions at the original prefixes in the fixed operator word. Exact finite-field evaluations exclude proportionality over the dyadic formal ring if any evaluation differs. General resynthesis is outside this screen."},out,indent=2)
print("pairs tested",tested,"range or source matches",len(matches))
for x in matches:print(x)
