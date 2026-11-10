"""Find one coframed scalar insertion realizing the HOST entrance transvection."""
from collections import defaultdict
from fractions import Fraction as F
import gzip, hashlib, json
from pathlib import Path
import sys

root=Path(__file__).resolve().parent
src=root/"supplier6824"/"F6824.json.gz"
sys.path.insert(0,str(src.parent))
import native
w=json.loads(gzip.decompress(src.read_bytes()))
replay=native.replay(w)
expected=json.loads((root/"connected7002/inputs/base_invoice.json").read_text())
assert {str(k):v for k,v in replay["paid"].items()}==expected["local_paid"]
assert {str(k):v for k,v in replay["helpers"].items()}==expected["helpers"]
n=w["public"]
N=n+w["owned_fields"]
events=w["program"]
ports=set(w["live"])
outputs=[{i:F(1)} if i<n else {} for i in range(N)]
def sink(row):
    if len(row)!=2:
        return None
    x=min(row)
    if x in ports and row.get(x+112)==row[x]:
        return x,row[x]
    return None

after=[None]*len(events)
for i in range(len(events)-1,-1,-1):
    e=events[i]
    op,d=e[:2]
    changed=e[2] if op in ("ADD","COPY") else d if op!="MOVE" else None
    if changed is None:
        continue
    after[i]=changed,sink(outputs[changed])
    if op in ("ADD","COPY"):
        native.add(outputs[changed],outputs[d],F(e[3]))
    elif op=="SCALE":
        outputs[d]={k:v*F(e[2]) for k,v in outputs[d].items()}
    else:
        outputs[d]={}
back=[sink(row) for row in outputs]
assert all(back[x]==(x,1) for x in ports)

def donor(row):
    if len(row)!=1:
        return None
    (r,c),=row.items()
    return (r-112,c) if r-112 in ports else None

rows=[{i:F(1)} if i<n else {} for i in range(N)]
frames=w["initial"]+[None]*w["owned_fields"]
by_donor=defaultdict(set)
by_sink=defaultdict(set)
def add_keys(reg):
    frame=frames[reg]
    if frame is None:
        return
    s=donor(rows[reg])
    if s is not None:
        by_donor[s[0],frame].add((reg,s[1]))
    z=back[reg]
    if z is not None:
        by_sink[z[0],frame].add((reg,z[1]))

def remove_keys(reg):
    frame=frames[reg]
    if frame is None:
        return
    s=donor(rows[reg])
    if s is not None:
        by_donor[s[0],frame].remove((reg,s[1]))
    z=back[reg]
    if z is not None:
        by_sink[z[0],frame].remove((reg,z[1]))

def candidates(changed,cut):
    for reg in changed:
        f=frames[reg]
        if f is None:
            continue
        s=donor(rows[reg])
        z=back[reg]
        if s is not None:
            for dst,beta in by_sink[s[0],f]:
                if reg!=dst:
                    coeff=-1/(s[1]*beta)
                    if coeff.denominator&(coeff.denominator-1)==0 and abs(coeff)+1<2**16:
                        yield s[0],(cut,dst,reg,str(coeff),f)
        if z is not None:
            for src,alpha in by_donor[z[0],f]:
                if reg!=src:
                    coeff=-1/(alpha*z[1])
                    if coeff.denominator&(coeff.denominator-1)==0 and abs(coeff)+1<2**16:
                        yield z[0],(cut,reg,src,str(coeff),f)

hits=defaultdict(set)
for i in range(N):
    add_keys(i)
for port,edit in candidates(range(N),0):
    hits[port].add(edit)
for i,e in enumerate(events):
    op,d=e[:2]
    changed={d}
    if after[i] is not None:
        changed.add(after[i][0])
    for reg in changed:
        remove_keys(reg)
    if op=="MOVE":
        frames[d]=e[3]
    elif op=="INIT":
        frames[d]=e[2]
        rows[d]={}
    elif op=="CLEAR":
        frames[d]=None
        rows[d]={}
    elif op=="SCALE":
        rows[d]={k:F(e[2])*v for k,v in rows[d].items()}
    else:
        native.add(rows[d],rows[e[2]],F(e[3]))
    if after[i] is not None:
        b,back_after=after[i]
        back[b]=back_after
    for reg in changed:
        add_keys(reg)
    for port,edit in candidates(changed,i+1):
        hits[port].add(edit)
assert frames[:n]==w["final"]
assert all(row==({i:F(1),i-112:F(1)} if i-112 in ports else {i:F(1)} if i<n else {}) for i,row in enumerate(rows))
with (root/"PR6824-FREE-HOST-ENTRANCE-CONTACTS.json").open("x") as f:
    json.dump({"source_sha256":hashlib.sha256(src.read_bytes()).hexdigest(),"native_head":"2a7ca44fbda3abaa4df355b183ed7d7478eef7c1",
               "ports":len(ports),"cuts":len(events)+1,"hits":{str(port):sorted(edits) for port,edits in sorted(hits.items())},
               "scope":"Normalized arbitrary-input word. A single ADD whose donor is a scalar times pure Y and whose suffix response is a scalar times (X+Y) realizes exactly the desired entrance shear. Composed and physical claims require further replay."},f,indent=2)
print("cuts",len(events)+1,"hit ports",len(hits),"hits",sum(map(len,hits.values())))
