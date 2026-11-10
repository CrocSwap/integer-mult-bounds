"""Locate exact nonzero first-order Y->X contacts with both sides mixed."""
from collections import defaultdict,Counter
from fractions import Fraction as F
from pathlib import Path
import json

root=Path(__file__).resolve().parent
source=root/"search_6824_host_entrance_contacts.py"
ns={"__file__":str(source)}
exec(source.read_text().split("def sink(")[0],ns)
w,n,N,events,ports,native=(ns[k] for k in ("w","n","N","events","ports","native"))
suffix=[{i:F(1)} if i<n else {} for i in range(N)]
after=[None]*len(events)
for i in range(len(events)-1,-1,-1):
    op,d,*a=events[i]
    if op=="MOVE":
        continue
    changed=a[0] if op in ("ADD","COPY") else d
    after[i]=(changed,suffix[changed])
    if op in ("ADD","COPY"):
        suffix[changed]=suffix[changed].copy()
        native.add(suffix[changed],suffix[d],F(a[1]))
    elif op=="SCALE":
        suffix[d]={k:F(a[0])*v for k,v in suffix[d].items()}
    else:
        suffix[d]={}
rows=[{i:F(1)} if i<n else {} for i in range(N)]
frames=w["initial"]+[None]*w["owned_fields"]
from_y=defaultdict(set)
to_x=defaultdict(set)
sample=defaultdict(dict)
def update(r,removing=False):
    f=frames[r]
    if f is None:
        return
    for table, values in ((from_y,(i-112 for i in rows[r] if i-112 in ports)),
                          (to_x,(i for i in suffix[r] if i in ports))):
        for port in values:
            if removing:
                table[port,f].remove(r)
            else:
                table[port,f].add(r)
def save(cut,port,d,s,frame):
    if d==s:
        return
    a,b=rows[s],suffix[d]
    assert a.get(port+112) and b.get(port)
    # Keep distinct exact outer-product directions with compact support.
    # Large supports remain counted, but are not exported as recipes.
    histogram[port][(min(len(a),32),min(len(b),32))]+=1
    if len(a)*len(b)>160:
        return
    key=(tuple(sorted(a.items())),tuple(sorted(b.items())))
    sample[port].setdefault(key,(cut,d,s,frame))
def scan(changed,cut):
    for r in changed:
        frame=frames[r]
        if frame is None:
            continue
        for y in rows[r]:
            if y-112 in ports:
                for dst in to_x[y-112,frame]:
                    save(cut,y-112,dst,r,frame)
        for x in suffix[r]:
            if x in ports:
                for src in from_y[x,frame]:
                    save(cut,x,r,src,frame)
histogram=defaultdict(Counter)
for i in range(N):
    update(i)
scan(range(N),0)
for i,event in enumerate(events):
    op,d,*a=event
    changed={d}
    if after[i] is not None:
        changed.add(after[i][0])
    for r in changed:
        update(r,True)
    if op=="MOVE":
        frames[d]=a[1]
    elif op=="INIT":
        frames[d]=a[0]
        rows[d]={}
    elif op=="CLEAR":
        frames[d]=None
        rows[d]={}
    elif op=="SCALE":
        rows[d]={k:F(a[0])*v for k,v in rows[d].items()}
    else:
        native.add(rows[d],rows[a[0]],F(a[1]))
    if after[i] is not None:
        r,col=after[i]
        suffix[r]=col
    for r in changed:
        update(r)
    scan(changed,i+1)

def describe(bucket):
    return [[list(edit),[[k,str(v)] for k,v in a],[[k,str(v)] for k,v in b]]
            for (a,b),edit in bucket.items()]
summary={str(port):{"contacts_by_support":[[a,b,count] for (a,b),count in sorted(histogram[port].items())],
                   "compact_directions":describe(sample[port])}
         for port in sorted(ports)}
with (root/"PR6824-MIXED-FIRST-ORDER-HOST-CONTACTS.json").open("x") as f:
    json.dump({"ports":summary,"scope":"Exact first-order contacts on fixed normalized chronology. Large support contacts counted only. Extra tensor entries and higher-order interactions still have to cancel."},f)
print("ports with first-order effect",sum(bool(histogram[p]) for p in ports),
      "ports with compact directions",sum(bool(sample[p]) for p in ports),
      "compact directions",sum(map(len,sample.values())),flush=True)
