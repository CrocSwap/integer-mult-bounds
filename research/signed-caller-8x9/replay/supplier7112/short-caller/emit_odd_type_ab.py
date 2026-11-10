"""Emit the 8+9 type-A root and join it to the exact signed type-B branch."""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import json

from host34 import eye,add,sc
from lower import lower_frame,backwards,unit
from signed_model import signed_model

root=Path(__file__).resolve().parent
data=json.loads((root/"SHORT-TYPE-A-ROOT.json").read_text())
source=json.loads((root.parents[1]/"supplier7108/CALLER.json").read_text())
B=json.loads((root/"ODD-TYPE-B-CALLER.json").read_text())
shape=(B['stages']//2,B['stages']-B['stages']//2)
W=next(r for r in data["candidates"] if r and tuple(r["shape"])==shape)
a,b=shape
L=a+b
n=W["roles"]
h=n//2
I=eye(n)
def sparse(row):
    return {i:q for i,v in enumerate(row) if (q:=Q(v))}
def dot(x,y):
    return sum(q*y.get(i,0) for i,q in x.items())
def axpy(x,y,s):
    return {i:t for i in x.keys()|y.keys() if (t:=x.get(i,0)+s*y.get(i,0))}
def basis(x,y,pivot_x=None,pivot_y=None):
    assert not dot(x,y)
    i=pivot_x if pivot_x is not None else next(i for i,q in x.items() if unit(q))
    assert unit(x[i])
    j=pivot_y if pivot_y is not None else next(j for j,q in y.items() if unit(q))
    w={i:1/x[i]}
    u=axpy({j:1/y[j]},x,-w.get(j,0)/y[j])
    assert dot(y,u)==dot(w,x)==1 and dot(w,u)==dot(y,x)==0
    return u,x,y,w
def tag(events):
    return [['A',*e[1:]] for e in events]
alpha=Q(source["types"]["A"]["alpha2"])
assert unit(alpha)
prefix={}
suffix={}
stages={}
diag=[[-1,0]+[int(mask>>j&1) for j in range(L)] for mask in W["masks"]]

def one_idle(row,hub,sgn,ids):
    # Passive vector e_row with dual e_row^t±2 e_hub^t. Its
    # projector commutes with the active maps throughout ids.
    return [['A','ADD',row,hub,str(2*sgn)],['A','IDLE_ONE',row,ids],
            ['A','ADD',row,hub,str(-2*sgn)]]
for j in range(1,L+1):
    left=j<=a
    arms=(j,j+h)
    hubs=(0,h)
    pairs=[(sparse(x),sparse(y)) for x,y in W["stage_pairs"][j-1]]
    U,X,Y,Z=basis(*pairs[0],hubs[0],arms[0])
    V,M,N,P=basis(*pairs[1],hubs[1],arms[1])
    r,s,u,v=arms[0],hubs[0],hubs[1],arms[1]
    columns=[U,X,M,V];rows=[Y,Z,P,N]
    frame=tag(lower_frame(columns,rows,[r,s,u,v]))
    pre=frame+[['A','LAMBDA',r,1],['A','LAMBDA',v,-1]]
    post=[['A','LAMBDA',r,-1],['A','LAMBDA',v,1]]
    if alpha!=1:
        pre.append(['A','SCALE',v,str(1/alpha)])
        post.append(['A','SCALE',v,str(alpha)])
    post+=[['A','ADD',s,r,'-1'],['A','ADD',u,v,'-1']]+list(backwards(frame))
    # Check the idles plus the two active planes equal the entire mask.
    active=[[sum(c.get(i,0)*w.get(k,0) for c,w in zip(columns,rows)) for k in range(n)] for i in range(n)]
    used={i for i,mask in enumerate(W["masks"]) if mask>>(j-1)&1}
    target=[[Q(i==k and i in used) for k in range(n)] for i in range(n)]
    for hub,arm in zip(hubs,arms):
        eligible=range(hub+1,arm) if left else range(arm+1,hub+h)
        for idle in eligible:
            active[idle][idle]+=1
            active[idle][hub]+=(-2 if left else 2)
    assert active==target,(j,active,target)
    prefix[j]=pre
    suffix[j]=post
    stages[j]=[r,s,u,v]
# Commute the left idles to the end of their half and the right idles to
# its beginning. A passive projector commutes with all stage masks in its
# interval, and different passive idles in a half annihilate each other.
for hub in (0,h):
    for arm in range(1,a):
        suffix[a]+=one_idle(hub+arm,hub,-1,list(range(arm+1,a+1)))
for x,y in W["thin_pairs"]:
    u,v,w,z=basis(sparse(x),sparse(y))
    dest,src=0,1
    frame=tag(lower_frame([v,u],[z,w],[dest,src]))
    suffix[a]+=frame+[['A','LAMBDA',src,1],['A','QUERY',dest,src,-1],['A','LAMBDA',src,-1],
                       ['A','ADD',dest,src,'-1']]+list(backwards(frame))
for hub in (0,h):
    for arm in range(a+2,L+1):
        suffix[a]+=one_idle(hub+arm,hub,1,list(range(a+1,arm)))
suffix[L]+=[['A','LAMBDA',i,-1] for i in range(n)]
offset=n
Broles=len(B["types"]["B"]["diagonal"])
def shift(e):
    assert e[0]=="B"
    out=e.copy()
    out[2]+=offset
    if e[1] in ("ADD","SWAP","QUERY"):out[3]+=offset
    return out
events=[]
for e in B["events"]:
    if e[0]=="B":
        events.append(shift(e))
    else:
        assert e[0]=="J"
        j=e[1]
        events+=prefix[j]
        s,t,al,be=e[3]
        events.append(["J",j,stages[j],[s+offset,t+offset,al,be]])
        events+=suffix[j]
Adef=source["types"]["A"]|{"offset":0,"roles":n,"diagonal":diag}
Bdef=source["types"]["B"]|{"offset":offset,"roles":Broles,"diagonal":B["types"]["B"]["diagonal"]}
C=source|{"stages":L,"roles":n+Broles,"ambient_rank":8*L+9,
          "types":{"A":Adef,"B":Bdef},"events":events}
ind=signed_model()
report=ind.caller(C)
assert not report["bad_outputs"],report
r=json.loads((root.parent/"RESULT.json").read_text())
target=Counter()
paid=Counter()
for ty,d in C["types"].items():
    target.update({k:len(d["ports"])*v for k,v in Counter(1+8*sum(row[2:]) for row in d["diagonal"]).items()})
for e in events:
    if e[0]=="J":continue
    ports=len(C["types"][e[0]]["ports"])
    if e[1]=="QUERY":paid[1]+=ports
    elif e[1] in ("IDLE_ONE","IDLE_ODD"):paid[8*len(e[3])+(e[1]=="IDLE_ODD")]+=ports
for name,c in (("helpers",target),("paid",paid)):
    c.update({int(k):v*L for k,v in r["native"][name].items()})
invoice=next(x for x in json.loads((root/"SHORT-CALLER-RAW-PRICE.json").read_text())["rows"] if tuple(x["shape"])==shape)
assert all(c==Counter({int(k):v for k,v in invoice[label].items()}) for label,c in (("target",target),("paid",paid)))
with (root/"ODD-TYPE-AB-CALLER.json").open("x") as f:
    json.dump(C,f,separators=(",",":"))
with (root/"ODD-TYPE-AB-REPLAY.json").open("x") as f:
    json.dump({"caller_sha256":sha256((root/"ODD-TYPE-AB-CALLER.json").read_bytes()).hexdigest(),
               "source_word_sha256":r["word_canonical_sha256"],"replay":report,"shape":list(shape),
               "target":dict(target),"paid":dict(paid),"raw_bracket":invoice["bracket"],
               "scope":"Exact emitted signed Laurent caller endpoint and recomputed native/caller paid and target profiles. Physical address bindings, independent branch-source composition, ordinary units, precision and outer gates are still required."},f,indent=2)
print("PASS exact short A+B",len(events),"events",report["max_terms"],invoice["bracket"],flush=True)
