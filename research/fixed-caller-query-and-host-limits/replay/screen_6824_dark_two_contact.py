"""Screen two-contact repairs whose individual baseline effects vanish."""
from collections import defaultdict
from fractions import Fraction as F
import json
from pathlib import Path

root=Path(__file__).resolve().parent
initial=root/"search_6824_host_entrance_contacts.py"
ns={"__file__":str(initial)}
exec(initial.read_text().split("after=[None]")[0],ns)
w,n,N,events,ports,native,columns,sink=(ns[k] for k in ("w","n","N","events","ports","native","outputs","sink"))
after=[None]*len(events)
def tag(col):
    return not col,sink(col)
for i in range(len(events)-1,-1,-1):
    op,d,*args=events[i]
    if op=="MOVE":
        continue
    r=args[0] if op in ("ADD","COPY") else d
    after[i]=(r,tag(columns[r]))
    if op in ("ADD","COPY"):
        native.add(columns[r],columns[d],F(args[1]))
    elif op=="SCALE":
        columns[d]={k:F(args[0])*v for k,v in columns[d].items()}
    else:
        columns[d]={}
suffix=[tag(v) for v in columns]
rows=[{r:F(1)} if r<n else {} for r in range(N)]
frames=w["initial"]+[None]*w["owned_fields"]
groups=defaultdict(set)
ordered=sorted(ports)
bit={port:1<<i for i,port in enumerate(ordered)}
reachable=[0]*N
hits={}
legal_dark_entry=set()
legal_dark_exit=set()
def scan(frame,cut):
    if frame is None:
        return
    registers=groups[frame]
    zero_live=[r for r in registers if not rows[r]]
    # Look for the second edit before admitting first contacts at this cut.
    # A same-cut first contact can go directly into the second source, so
    # check it explicitly after the additions below.
    dark=[r for r in registers if suffix[r][0]]
    sources={}
    for r in registers:
        if len(rows[r])==1:
            (i,c),=rows[r].items()
            if i-112 in bit:
                sources[r]=bit[i-112]
    union=0
    for mask in sources.values():
        union|=mask
    if dark:
        for r in dark:
            available=union if r not in sources else 0
            if r in sources:
                for s,mask in sources.items():
                    if s!=r:
                        available|=mask
            if available:
                reachable[r]|=available
                legal_dark_entry.add(r)
    zero_union=0
    for r in zero_live:
        zero_union|=reachable[r]
    for dst in registers:
        sig=suffix[dst][1]
        if not sig:
            continue
        port,_=sig
        if any(r!=dst for r in zero_live):
            legal_dark_exit.add(port)
        if zero_union&bit[port] and port not in hits:
            for src in zero_live:
                if src!=dst and reachable[src]&bit[port]:
                    hits[port]=[cut,dst,src]
                    break
for r,f in enumerate(frames):
    if f is not None:
        groups[f].add(r)
for f in list(groups):
    scan(f,0)
for i,event in enumerate(events):
    op,d,*args=event
    affected={frames[d]}
    if after[i] is not None:
        affected.add(frames[after[i][0]])
    if op=="MOVE":
        groups[frames[d]].remove(d)
        frames[d]=args[1]
        groups[frames[d]].add(d)
    elif op=="CLEAR":
        groups[frames[d]].remove(d)
        frames[d]=None
        rows[d]={}
        reachable[d]=0
    elif op=="INIT":
        frames[d]=args[0]
        groups[frames[d]].add(d)
        rows[d]={}
        reachable[d]=0
    elif op=="SCALE":
        rows[d]={k:F(args[0])*v for k,v in rows[d].items()}
    else:
        src=args[0]
        if op=="COPY":
            reachable[d]=reachable[src]
        else:
            reachable[d]|=reachable[src]
        native.add(rows[d],rows[src],F(args[1]))
    if after[i] is not None:
        r,value=after[i]
        suffix[r]=value
    affected.add(frames[d])
    for f in affected:
        scan(f,i+1)
with (root/"PR6824-TWO-CONTACT-DARK-REACHABILITY.json").open("x") as f:
    json.dump({"reachable_ports":hits,"dark_entry_registers":len(legal_dark_entry),
               "potential_dark_exit_ports":len(legal_dark_exit),"cuts":len(events)+1,
               "scope":"Necessary path condition. First edit reads pure Y into a baseline suffix-zero register; second edit reads a baseline-zero source into an isolated X+Y suffix. Existing linear dependencies are granted even if their coefficients cancel. Baseline COPY is modeled as transfer with zero destination."},f,indent=2)
print("dark entries",len(legal_dark_entry),"dark exit ports",len(legal_dark_exit),"reachable",len(hits),flush=True)
