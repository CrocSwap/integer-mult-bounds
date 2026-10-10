#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
#
# Global majorant contraction search for the h=22 coordinated complex witness.
#
# Contribution: @dataisfire, 2026.
# Developed with substantial OpenAI ChatGPT assistance.
#
# This adapts existing repository concavity-majorant / min-cut machinery.
# Floating optimization nominates candidates only; exact repository verifiers
# certify the resulting physical frames and exponent.
#
import gzip,json,math
from pathlib import Path
from collections import Counter,defaultdict,deque

HERE=Path(__file__).resolve().parent
P=Path("research/coordinated-frames-and-entrance-banks/selected/complex")
BASE=HERE/"baseline"
OUT=Path("/tmp/pr186-majorant-replay")
OUT.mkdir(parents=True,exist_ok=True)
H=22
M=66

def loadgz(n):
    return json.loads(gzip.decompress((P/f"{n}.json.gz").read_bytes()))

g=loadgz("graph")
w=loadgz("word")
fw=loadgz("frames")
changes=json.loads(gzip.decompress((BASE/"physical-frames.json.gz").read_bytes()))
pairs=loadgz("physical-pairs")
profile=json.loads(gzip.decompress((BASE/"profile.json.gz").read_bytes()))
srec=json.loads((BASE/"sinks.json").read_text())

def basis(rows):
    b={}
    for x in map(int,rows):
        for p,y in sorted(b.items(),reverse=True):
            if (x>>p)&1:
                x^=y
        if x:
            p=x.bit_length()-1
            for q,y in list(b.items()):
                if (y>>p)&1:
                    b[q]=y^x
            b[p]=x
    return tuple(b[p] for p in sorted(b,reverse=True))

def perp(rows):
    rows=basis(rows)
    piv={x.bit_length()-1:x for x in rows}
    out=[]
    for j in range(H):
        if j in piv:
            continue
        x=1<<j
        for p,r in piv.items():
            if (r>>j)&1:
                x|=1<<p
        out.append(x)
    z=basis(out)
    assert len(z)+len(rows)==H
    return z

def within(A,B):
    return len(basis(tuple(A)+tuple(B)))==len(B)

def fmt(C):
    return {str(k):v for k,v in sorted(C.items()) if v}

FULL=basis(1<<i for i in range(H))
EMPTY=()

N=len(w["ops"])
R=loadgz("profile-before")["R"]
sources={int(k):v for k,v in w["sources"].items()}

# Node value spans.
spans=[()]*len(g["args"])
for n,args in enumerate(g["args"]):
    spans[n]=(g["inputs"][n],) if args is None else \
             basis(spans[args[0]]+spans[args[1]])

# Compiler and current effective operation frames.
compiler=[perp(fw["annihilators"][node])
          for a,b,node in w["ops"]]
F=list(compiler)
for i,U in changes:
    F[int(i)]=basis(U)

# Pairing / physical roles.
aliases={int(b):int(a) for a,b,t in pairs}
donors={int(a):int(b) for a,b,t in pairs}
deadline={int(b):t for a,b,t in pairs}
live=set(range(R))-set(aliases)

selected={z["role"]:z for z in w["selected"]}

starts=[EMPTY]*R
for n,s in sources.items():
    starts[s]=(g["inputs"][n-1],)
for s,z in selected.items():
    starts[s]=perp(z["annihilator"])

rootframes=[]
for r in g["roots"]:
    if r["kind"]=="center":
        U=spans[r["node"]]
    else:
        U=perp(g["inputs"][t] for t in r["targets"])
    rootframes.append(U)

rframe={s:rootframes[j] for j,s in enumerate(w["rootroles"])}
rkind={s:g["roots"][j]["kind"] for j,s in enumerate(w["rootroles"])}

roleops=[[] for _ in range(R)]
for i,(a,b,node) in enumerate(w["ops"]):
    roleops[a].append(i)
    roleops[b].append(i)

def O(i): return ("o",int(i))
def B(U): return ("b",basis(U))

def frame(ep,X):
    return X[ep[1]] if ep[0]=="o" else ep[1]

def chain(s):
    q=[B(starts[s])]
    q += [O(i) for i in roleops[s]]
    if s in rframe:
        q.append(B(rframe[s]))
    q.append(B(FULL))
    return q

# All legality edges, separately from paid edges.
legal=set()
paid=[]

def legal_edge(a,b):
    legal.add((a,b))

def paid_edge(a,b):
    paid.append((a,b))
    legal_edge(a,b)

# Every literal role chain is a legality constraint.
for s in range(R):
    q=chain(s)
    for a,b in zip(q,q[1:]):
        legal_edge(a,b)

# Explicit donor -> recipient-gauge splice legality.
for a,b,t in pairs:
    a=int(a); b=int(b)
    last=roleops[a][-1]
    legal_edge(O(last),B(starts[b]))

# Final sink roles are removed from LOCAL paid accounting.
sink_roles={x["role"] for x in srec["sinks"]}

fixed_local=Counter()

for s in sorted(live):
    # Fixed additions in physical.py / check_sinks.
    if s in sources.values():
        fixed_local[1]+=1
    for t in (s,donors.get(s)):
        if t is not None and rkind.get(t)=="center":
            fixed_local[len(rframe[t])]+=1

    if s in sink_roles:
        # check_sinks subtracts the entire sink role trajectory:
        # prefix children plus rank18 -> full rank22 child 4.
        continue

    q=chain(s)
    if s in donors:
        q=q[:-1]+chain(donors[s])
    for a,b in zip(q,q[1:]):
        paid_edge(a,b)

# Reconstruct the FINAL 46-sink target chronology.
phase=set(w["phase1"])
chron=w["phase1"]+[i for i in range(N) if i not in phase]
when={i:j for j,i in enumerate(chron)}

read_at={}
for z in reversed(w["selected"]):
    d=deadline.get(z["role"])
    pos=len(phase) if d is None else when[d]
    read_at.setdefault(pos,[]).append(z)

by_write={i:item for item in srec["sinks"] for i in item["writes"]}
after={item["writes"][-1]:item for item in srec["sinks"]}

cur=[B(EMPTY) for _ in range(g["v"])]

def target_move(t,dst):
    src=cur[t]
    paid_edge(src,dst)
    cur[t]=dst

for pos,i in enumerate(chron):
    for z in read_at.get(pos,()):
        U=perp(z["annihilator"])
        for t in z["targets"]:
            target_move(t,B(U))

    if i in by_write:
        item=by_write[i]
        target_move(item["pivot"],O(i))

    if i in after:
        item=after[i]
        U=rootframes[item["root_index"]]
        for t in item["targets"]:
            target_move(t,B(U))

for j,r in enumerate(g["roots"]):
    if r["kind"]=="side" and w["rootroles"][j] not in sink_roles:
        U=rootframes[j]
        for t in r["targets"]:
            target_move(t,B(U))

for t,q in enumerate(g["inputs"]):
    target_move(t,B(perp((q,))))

# Validate baseline legality.
for a,b in legal:
    A,Bb=frame(a,F),frame(b,F)
    assert within(A,Bb),("baseline nesting",a,b,len(A),len(Bb))

# Validate paid histograms against the exact frozen sink certificate.
local_dynamic=Counter()
target_dynamic=Counter()

# Rebuild local dynamic separately to make the comparison transparent.
for s in sorted(live):
    if s in sink_roles:
        continue
    q=chain(s)
    if s in donors:
        q=q[:-1]+chain(donors[s])
    for a,b in zip(q,q[1:]):
        A,Bb=frame(a,F),frame(b,F)
        d=len(Bb)-len(A)
        if d:
            local_dynamic[d]+=1

local_check=local_dynamic+fixed_local
assert fmt(local_check)==srec["local_histogram"], \
       ("local histogram mismatch",fmt(local_check),srec["local_histogram"])

# Target paid edges are the suffix of paid after local paid edges; easier:
# replay target chronology numerically from endpoints by detecting against
# expected frozen target histogram directly using a second construction.
target_check=Counter()
cur2=[B(EMPTY) for _ in range(g["v"])]

def count_move(t,dst):
    src=cur2[t]
    A,Bb=frame(src,F),frame(dst,F)
    assert within(A,Bb)
    d=len(Bb)-len(A)
    if d:
        target_check[d]+=1
    cur2[t]=dst

for pos,i in enumerate(chron):
    for z in read_at.get(pos,()):
        U=perp(z["annihilator"])
        for t in z["targets"]:
            count_move(t,B(U))
    if i in by_write:
        item=by_write[i]
        count_move(item["pivot"],O(i))
    if i in after:
        item=after[i]
        U=rootframes[item["root_index"]]
        for t in item["targets"]:
            count_move(t,B(U))

for j,r in enumerate(g["roots"]):
    if r["kind"]=="side" and w["rootroles"][j] not in sink_roles:
        for t in r["targets"]:
            count_move(t,B(rootframes[j]))

for t,q in enumerate(g["inputs"]):
    count_move(t,B(perp((q,))))

expected_target={k:v for k,v in srec["target_histogram"].items()
                 if int(k)>0 and v}
assert fmt(target_check)==expected_target, \
       ("target histogram mismatch",fmt(target_check),expected_target)

print("BASELINE GRAPH RECONSTRUCTION: PASS")
print("operations:",N)
print("legality edges:",len(legal))
print("paid edges:",len(paid))
print("local histogram:",fmt(local_check))
print("target histogram:",fmt(target_check))

# ------------------------------------------------------------
# Least feasible contraction schedule.
# ------------------------------------------------------------

pred=defaultdict(list)
reverse_edges=[]

for a,b in legal:
    if b[0]=="o":
        pred[b[1]].append(a)
    if a[0]=="o" and b[0]=="o" and a[1]>=b[1]:
        reverse_edges.append((a,b))

print("non-forward op->op edges:",len(reverse_edges))
if reverse_edges:
    print("examples:",reverse_edges[:10])
    raise SystemExit("Need general topological solver before continuing")

L=[None]*N

for i,(aa,bb,node) in enumerate(w["ops"]):
    # word operation node IDs are graph node index + 1
    rows=list(spans[node-1])
    for p in pred[i]:
        if p[0]=="o":
            assert p[1]<i
            rows.extend(L[p[1]])
        else:
            rows.extend(p[1])

    U=basis(rows)
    assert within(U,F[i]),("least candidate escaped current frame",i)
    L[i]=U

# Verify complete least schedule legal.
for a,b in legal:
    A=frame(a,L)
    Bb=frame(b,L)
    assert within(A,Bb),("least nesting",a,b,len(A),len(Bb))

drops=Counter(len(F[i])-len(L[i]) for i in range(N))
print("least schedule rank-drop histogram:",
      dict(sorted((k,v) for k,v in drops.items() if k)))
print("least mutable operations:",sum(k>0 for k in drops for _ in range(drops[k])))

# ------------------------------------------------------------
# Contraction majorant.
# f(r)=r log(66/r), increasing + concave for 0<=r<=22.
# Local/target children occur with common multiplicity 3, irrelevant
# to the minimizing cut.
# ------------------------------------------------------------

def ent(r):
    assert 0<=r<=H,r
    return 0.0 if r==0 else r*math.log(M/r)

u=[0.0]*N
hard_arcs=set()
force_zero=set()
concavity=0.0
allowed01=0
forbidden01=0

# Hard legality for every literal physical edge.
for a,b in legal:
    if a[0]=="o" and b[0]=="o":
        i,j=a[1],b[1]
        # Forbidden state: source remains F_i, target contracts to L_j.
        if not within(F[i],L[j]):
            hard_arcs.add((j,i))
    elif a[0]=="b" and b[0]=="o":
        j=b[1]
        if not within(a[1],L[j]):
            force_zero.add(j)

# Objective contributions only for PAID edges.
for a,b in paid:
    A0=frame(a,F); B0=frame(b,F)
    r=len(B0)-len(A0)
    assert r>=0 and within(A0,B0)
    E00=ent(r)

    if a[0]=="o" and b[0]=="o":
        i,j=a[1],b[1]
        di=len(F[i])-len(L[i])
        dj=len(F[j])-len(L[j])

        E10=ent(r+di)       # source contracts only
        E11=ent(r+di-dj)    # both contract

        u[i]+=E10-E00
        u[j]+=E11-E10

        if within(F[i],L[j]):
            E01=ent(r-dj)
            defect=E00+E11-E10-E01
            assert defect>-1e-8,(i,j,defect)
            concavity+=max(0.0,defect)
            allowed01+=1
        else:
            hard_arcs.add((j,i))
            forbidden01+=1

    elif a[0]=="o":
        i=a[1]
        di=len(F[i])-len(L[i])
        u[i]+=ent(r+di)-E00

    elif b[0]=="o":
        j=b[1]
        dj=len(F[j])-len(L[j])
        assert r-dj>=0
        u[j]+=ent(r-dj)-E00

# ------------------------------------------------------------
# Dinic min-cut.
# selected/source-side node means "use contracted L_i".
# ------------------------------------------------------------

class Dinic:
    def __init__(self,n):
        self.n=n
        self.g=[[] for _ in range(n)]

    def add(self,u,v,c):
        if c<=1e-12 or u==v:
            return
        a=[v,float(c),None]
        b=[u,0.0,a]
        a[2]=b
        self.g[u].append(a)
        self.g[v].append(b)

    def flow(self,s,t):
        total=0.0
        INF=1e100
        while True:
            lev=[-1]*self.n
            lev[s]=0
            q=deque([s])
            while q:
                x=q.popleft()
                for e in self.g[x]:
                    if e[1]>1e-10 and lev[e[0]]<0:
                        lev[e[0]]=lev[x]+1
                        q.append(e[0])
            if lev[t]<0:
                break

            it=[0]*self.n

            def dfs(v,f):
                if v==t:
                    return f
                while it[v]<len(self.g[v]):
                    e=self.g[v][it[v]]
                    if e[1]>1e-10 and lev[e[0]]==lev[v]+1:
                        z=dfs(e[0],min(f,e[1]))
                        if z>1e-10:
                            e[1]-=z
                            e[2][1]+=z
                            return z
                    it[v]+=1
                return 0.0

            while True:
                z=dfs(s,INF)
                if z<=1e-10:
                    break
                total+=z
        return total

    def reachable(self,s):
        seen=[False]*self.n
        seen[s]=True
        q=deque([s])
        while q:
            v=q.popleft()
            for e in self.g[v]:
                if e[1]>1e-10 and not seen[e[0]]:
                    seen[e[0]]=True
                    q.append(e[0])
        return seen

S=N
T=N+1
D=Dinic(N+2)

hard=1.0+sum(abs(x) for x in u)

for j,i in hard_arcs:
    D.add(j,i,hard)

for j in force_zero:
    D.add(j,T,hard)

for i,z in enumerate(u):
    if z>0:
        D.add(i,T,z)
    elif z<0:
        D.add(S,i,-z)

D.flow(S,T)
reach=D.reachable(S)

selected=[i for i in range(N)
          if reach[i] and L[i]!=F[i]]

X=list(F)
for i in selected:
    X[i]=L[i]

# Full exact legality check on selected cut.
for a,b in legal:
    A=frame(a,X); Bb=frame(b,X)
    assert within(A,Bb),("selected nesting",a,b,len(A),len(Bb))

def objective(X):
    z=0.0
    Hc=Counter()
    for a,b in paid:
        A=frame(a,X); Bb=frame(b,X)
        assert within(A,Bb)
        r=len(Bb)-len(A)
        if r:
            Hc[r]+=1
        z+=ent(r)
    return z,Hc

baseE,baseH=objective(F)
newE,newH=objective(X)

proxy=sum(u[i] for i in selected)

print()
print("MAJORANT CUT RESULT")
print("selected operations:",len(selected))
print("proxy delta:",repr(proxy))
print("actual paid entropy delta:",repr(newE-baseE))
print("hard arcs:",len(hard_arcs))
print("forced zero:",len(force_zero))
print("paid feasible target-only contractions:",allowed01)
print("paid forbidden target-only contractions:",forbidden01)
print("total concavity majorant:",repr(concavity))

delta={
    r:newH[r]-baseH[r]
    for r in sorted(set(baseH)|set(newH))
    if newH[r]!=baseH[r]
}
print("paid histogram delta:",delta)

# Full override list relative to compiler, suitable for the current physical()
# interface if we decide to test this candidate.
out=[]
for i in range(N):
    if X[i]!=compiler[i]:
        out.append([i,list(X[i])])

(OUT/"physical-frames.json").write_text(
    json.dumps(out,separators=(",",":"))+"\n"
)

receipt={
    "selected":selected,
    "selected_count":len(selected),
    "proxy_delta":proxy,
    "actual_paid_entropy_delta":newE-baseE,
    "hard_arcs":len(hard_arcs),
    "forced_zero":len(force_zero),
    "least_mutable":sum(1 for i in range(N) if L[i]!=F[i]),
    "current_override_count":len(changes),
    "candidate_override_count":len(out),
    "paid_histogram_delta":{str(k):v for k,v in delta.items()},
}
(OUT/"search-result.json").write_text(
    json.dumps(receipt,indent=2)+"\n"
)

print("current override count:",len(changes))
print("candidate override count:",len(out))
print("wrote",OUT/"search-result.json")
print("wrote",OUT/"physical-frames.json")

if selected and newE < baseE-1e-9:
    print("DISCOVERY: STRICT PAID-ENTROPY IMPROVEMENT")
elif not selected:
    print("NO CHANGE in this least-schedule binary neighborhood")
else:
    print("No certified strict improvement")
