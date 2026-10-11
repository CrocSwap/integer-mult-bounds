"""Independent hierarchy-level legality checker for rekid (cancelling re-expression) rules.
Uses only: the pickled arrays (kids, need, content/frame for comparison only) and the 120 root lines read from the emitted word.
usage: rekid_check.py HIER.h WORD.json[.gz] BASE.h"""
import sys,gzip,json
from fractions import Fraction as Fr
from loadh import loadh
hier,wordp,basep=sys.argv[1:4]
h=loadh(hier); base=loadh(basep)
word=json.load(gzip.open(wordp,'rt') if wordp.endswith('.gz') else open(wordp))
lines=[tuple(x) for x in word['lines']]; V=120; N=len(h.kids)
den=2 if word['form']=='<x,y>/2' else 4
def ip(a,b):
    s=sum(x*y for x,y in zip(a,b)); assert s%den==0; return s//den
assert len(lines)==V and all(ip(a,a)==2 for a in lines)
# ---- my own span/closure over the 120 root lines
def reduce_basis(idx):
    rows=[];piv=[]
    for i in idx:
        v=[Fr(a) for a in lines[i]]
        for p,b in zip(piv,rows):
            if v[p]!=0:
                f=v[p]/b[p]; v=[x-f*y for x,y in zip(v,b)]
        nz=[k for k in range(8) if v[k]!=0]
        if nz: rows.append(v); piv.append(nz[0])
    return rows,piv
def inspan(i,rows,piv):
    v=[Fr(a) for a in lines[i]]
    for p,b in zip(piv,rows):
        if v[p]!=0:
            f=v[p]/b[p]; v=[x-f*y for x,y in zip(v,b)]
    return all(x==0 for x in v)
_c={}
def closure(mask):
    if mask in _c: return _c[mask]
    rows,piv=reduce_basis([i for i in range(V) if mask>>i&1])
    m=0
    for i in range(V):
        if mask>>i&1 or inspan(i,rows,piv): m|=1<<i
    _c[mask]=(m,len(rows)); return _c[mask]
def inside(a,b): return a&~b==0
HYP=[sum(1<<s for s in range(V) if ip(lines[t],lines[s])==0) for t in range(V)]
assert all(bin(x).count('1')==63 for x in HYP)
# ---- recompute everything from kids (do not trust pickled content/frame/dim)
order=[]; state=[0]*N
sys.setrecursionlimit(10000)
def visit(u):
    if state[u]==2: return
    assert state[u]==0,('CYCLE at',u)
    state[u]=1
    if u>=V:
        k=h.kids[u]; assert k is not None and len(k)==2 and k[0]!=k[1] and 0<=k[0]<N and 0<=k[1]<N,('bad kids',u,k)
        visit(k[0]); visit(k[1])
    state[u]=2; order.append(u)
for u in range(N): visit(u)
cont=[1<<s for s in range(V)]+[None]*(N-V); Fn=[closure(1<<s)[0] for s in range(V)]+[None]*(N-V); Dn=[1]*V+[None]*(N-V)
for u in order:
    if u<V: continue
    x,y=h.kids[u]; cont[u]=cont[x]^cont[y]
    Fn[u],Dn[u]=closure(Fn[x]|Fn[y])
print('symbols',N-V,'; DAG acyclic: OK')
print('recomputed content == pickled content:',all(cont[u]==h.content[u] for u in range(N)))
print('recomputed join-frame == pickled frame for', sum(Fn[u]==h.frame[u] for u in range(N)),'of',N,'; strictly inside:',[u for u in range(N) if Fn[u]!=h.frame[u] and inside(Fn[u],h.frame[u])],'; NOT inside:',[u for u in range(N) if not inside(Fn[u],h.frame[u])])
# ---- targets: exact XOR of reads equals HYP[t]; every read has frame inside the cap
for t in range(V):
    x=0
    for u in h.need[t]:
        x^=cont[u]
        assert inside(Fn[u],HYP[t]) and inside(h.frame[u],HYP[t]),('read frame leaves cap',t,u)
        assert inside(cont[u],HYP[t])
    assert x==HYP[t],('target XOR wrong',t)
print('targets: 120/120 XOR of reads == the 63-line cap exactly; every read symbol (recomputed and stored frame) inside the cap')
# ---- needed set (reachable from need[] through current kids)
needed=set(); st=[u for t in range(V) for u in h.need[t]]
while st:
    u=st.pop()
    if u in needed: continue
    needed.add(u)
    if u>=V: st.extend(h.kids[u])
print('needed symbols (non-source)',len([u for u in needed if u>=V]),'of',N-V)
# consumers
cons={u:[] for u in range(N)}
for c in needed:
    if c>=V:
        for k in h.kids[c]: cons[k].append(('rule',c))
for t in range(V):
    for u in h.need[t]: cons[u].append(('target',t))
# ---- the rekid'd rules
rk=[w for w in range(V,N) if base.kids[w]!=h.kids[w]]
print('rekid rules (kids differ from the pre-rekid FP hierarchy):',rk)
bad=0
for w in rk:
    x,y=h.kids[w]; ox=base.kids[w]
    ok=[]
    ok.append(('content',cont[x]^cont[y]==cont[w]==base.content[w]))
    ok.append(('x,y exist & distinct, != w',x!=y and w not in (x,y)))
    ok.append(('w not an ancestor of x or y (acyclic)',True))   # visit() asserted acyclicity
    ok.append(('x,y frames inside w frame',inside(Fn[x],h.frame[w]) and inside(Fn[y],h.frame[w])))
    ok.append(('join(x,y)==stored frame[w]',closure(Fn[x]|Fn[y])[0]==h.frame[w]))
    ok.append(('w needed',w in needed))
    ok.append(('x,y needed',x in needed and y in needed))
    # consumers: frame[w] inside consumer gate frame (rule: join frame of consumer; target: cap)
    cok=True
    for kind,c in cons[w]:
        if kind=='rule': cok&=inside(Fn[w],Fn[c]) and inside(h.frame[w],h.frame[c])
        else: cok&=inside(Fn[w],HYP[c]) and inside(h.frame[w],HYP[c])
    ok.append(('consumers (%s) all above w'%','.join('%s%d'%(k[0][0],c) for k,c in [(a,a[1]) for a in cons[w]]),cok))
    # cancelled lines
    ov=cont[x]&cont[y]; ovl=[s for s in range(V) if ov>>s&1]
    ok.append(('cancelled sources %s lie in frames of both operands'%ovl,all(Fn[x]>>s&1 and Fn[y]>>s&1 for s in ovl)))
    # x,y reach their own operands only inside the frame of w: recursively all descendants' frames inside frame[w]
    def desc(u,acc):
        if u in acc: return
        acc.add(u)
        if u>=V: [desc(k,acc) for k in h.kids[u]]
    D=set(); desc(x,D); desc(y,D)
    ok.append(('all descendants of x,y have frames inside frame[w]',all(inside(Fn[u],h.frame[w]) for u in D)))
    good=all(v for _,v in ok); bad+=not good
    print(' w=%d dim %d  old kids %s -> new (%d,%d)  dims (%d,%d)  |c|=(%d,%d,%d) overlap=%d  consumers=%s  %s'%(w,Dn[w],ox,x,y,Dn[x],Dn[y],bin(cont[x]).count('1'),bin(cont[y]).count('1'),bin(cont[w]).count('1'),len(ovl),cons[w],'OK' if good else 'FAIL'))
    for n,v in ok:
        if not v: print('     FAILED:',n)
# every other needed rule: kids frames inside frame
badall=[u for u in needed if u>=V and not (inside(Fn[h.kids[u][0]],Fn[u]) and inside(Fn[h.kids[u][1]],Fn[u]))]
print('all needed rules: operand frames inside own gate frame:', 'OK' if not badall else badall)
print('RESULT:', 'ALL REKID RULES LEGAL' if bad==0 else '%d REKID RULES FAIL'%bad)
