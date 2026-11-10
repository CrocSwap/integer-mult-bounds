"""Screen necessary tensor-factor cancellations for two coframe repairs."""
from collections import defaultdict
from fractions import Fraction as F
from pathlib import Path
import json

root=Path(__file__).resolve().parent
initial=root/"search_6824_host_entrance_contacts.py"
ns={"__file__":str(initial)}
exec(initial.read_text().split("def sink(")[0],ns)
w,n,N,events,ports,native,B=(ns[k] for k in ("w","n","N","events","ports","native","outputs"))
A=[{i:F(1)} if i<n else {} for i in range(N)]
frames=w["initial"]+[None]*w["owned_fields"]
after=[None]*len(events)
for i in range(len(events)-1,-1,-1):
    op,d,*a=events[i]
    if op=="MOVE":
        continue
    r=a[0] if op in ("ADD","COPY") else d
    after[i]=r,B[r]
    if op in ("ADD","COPY"):
        B[r]=B[r].copy()
        native.add(B[r],B[d],F(a[1]))
    elif op=="SCALE":
        B[r]={k:v*F(a[0]) for k,v in B[r].items()}
    else:
        B[r]={}
groups=defaultdict(set)
for i,f in enumerate(frames):
    if f is not None:
        groups[f].add(i)

def pure_y(row):
    if len(row)==1:
        i=next(iter(row))
        if i-112 in ports:
            return i-112
    return None

def isolated(row):
    if len(row)==2:
        p=min(row)
        if p in ports and row.get(p+112)==row[p]:
            return p
    return None

def canon(row):
    if not row:
        return ()
    p=row[min(row)]
    return tuple(sorted((k,v/p) for k,v in row.items()))

# If first suffix is zero, later baseline donor must cancel the first
# donor's non-Y terms. If later donor is zero, earlier baseline suffix
# must supply the residual after subtracting the second suffix's X part.
dark_prefix=defaultdict(dict)
pure_suffix=defaultdict(dict)
out_A={}
out_B={}
count_A=set()
count_B=set()
cache={}
def norm_suffix(d):
    v=B[d]
    if d not in cache or cache[d][0] is not v:
        cache[d]=(v,canon(v))
    return cache[d][1]

def scan(affected,changed,cut):
    for f in sorted(affected):
        registers=groups[f]
        for dst in sorted(registers):
            if not B[dst]:
                for src in sorted(registers-{dst}):
                    if src not in changed and dst not in changed:
                        continue
                    a=A[src]
                    for y in a:
                        p=y-112
                        if p in ports:
                            key=canon({k:v for k,v in a.items() if k!=y})
                            dark_prefix[p].setdefault(key,(cut,src,dst))
        # Add all newly available first contacts from pure Y donors.
        for r in sorted(registers&changed):
            p=pure_y(A[r])
            if p is not None:
                for dst in registers-{r}:
                    if B[dst]:
                        pure_suffix[p].setdefault(norm_suffix(dst),(cut,r,dst))
            if B[r]:
                for src in registers-{r}:
                    p=pure_y(A[src])
                    if p is not None:
                        pure_suffix[p].setdefault(norm_suffix(r),(cut,src,r))

    for f in sorted(affected):
        registers=groups[f]
        zero={r for r in registers if not A[r]}
        for dst in sorted(registers):
            p=isolated(B[dst])
            if p is not None and p not in out_A:
                for src in sorted(registers-{dst}):
                    a=A[src]
                    if not a or p+112 in a:
                        continue
                    count_A.add(p)
                    key=canon(a)
                    if key in dark_prefix[p]:
                        out_A[p]=(dark_prefix[p][key],(cut,src,dst))
                        break
            if not zero-{dst}:
                continue
            for p,b in B[dst].items():
                if p not in ports or p in out_B:
                    continue
                count_B.add(p)
                residual={i:-v/b for i,v in B[dst].items()}
                residual[p]+=1
                residual[p+112]=residual.get(p+112,0)+1
                key=canon({i:v for i,v in residual.items() if v})
                if key and key in pure_suffix[p]:
                    out_B[p]=(pure_suffix[p][key],(cut,min(zero-{dst}),dst))
scan(set(groups),set(range(N)),0)
for i,event in enumerate(events):
    op,d,*a=event
    changed={d}
    if after[i]:
        changed.add(after[i][0])
    affected={frames[r] for r in changed}
    if op=="MOVE":
        groups[frames[d]].remove(d)
        frames[d]=a[1]
        groups[frames[d]].add(d)
    elif op=="INIT":
        frames[d]=a[0]
        groups[frames[d]].add(d)
        A[d]={}
    elif op=="CLEAR":
        groups[frames[d]].remove(d)
        frames[d]=None
        A[d]={}
    elif op=="SCALE":
        A[d]={k:F(a[0])*v for k,v in A[d].items()}
    else:
        native.add(A[d],A[a[0]],F(a[1]))
    if after[i]:
        r,v=after[i]
        B[r]=v
    affected.update(frames[r] for r in changed)
    scan(affected-{None},changed,i+1)

with (root/"PR6824-TWO-EDIT-MIXED-CANCELLATION.json").open("x") as out:
    json.dump({"prefix_signature_counts":{p:len(x) for p,x in dark_prefix.items()},
               "tested_later_isolated_sink_ports":len(count_A),"tested_later_zero_source_ports":len(count_B),
               "first_suffix_zero_candidates":out_A,"second_donor_zero_candidates":out_B,
               "scope":"Necessary temporal cancellation matches for the one-zero-factor cases of two coframe ADDs. Transfer amplitude, COPY legality and full endpoint replay still required for survivors. Both-zero dark path tested separately."},out,indent=2)
print("tested",len(count_A),len(count_B),"cancellation candidates",len(out_A),len(out_B),flush=True)
