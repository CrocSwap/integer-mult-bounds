# FEWSTOPS vacate search (reorder + chart change). State: chi[e] = chart (frame id) of every public-involving event.
# Feasible iff (a) every public register's event charts form a chain init<=...<=final, (b) block-DAG + per-register
# chart-order edges acyclic (then any topological order is a legal schedule with identical rows [P]).
# Move: vacate level C of register r: re-chart each of r's events at C to a level shared with its partner.
from ls import *
from sched import build_blocks, regs_of
from collections import defaultdict, deque
import sys, pickle
setup(W)
P0=[e for e in P if not (e[0]=='MOVE' and e[1]<n)]
cur=list(W['initial']); chi=[None]*len(P0); j=0
for e in P:
    if e[0]=='MOVE' and e[1]<n: cur[e[1]]=e[3]; continue
    rs=[r for r in regs_of(e) if r<n]
    if rs: chi[j]=cur[rs[0]]
    j+=1
blocks,bidx=build_blocks(P0)
NE=len(P0)
pinned=[e[0]=='ADD' and ((e[1]>=n)!=(e[2]>=n)) for e in P0]
evs={r:[i for B in blocks.get(r,[]) for i in B] for r in range(n)}
initm=[SM_[x] for x in W['initial']]; finm=[SM_[x] for x in W['final']]
def levels(r):
    return sorted(set(chi[i] for i in evs[r]), key=lambda c:dm(SM_[c]))
def chain_ok(r):
    ls_=[SM_[c] for c in levels(r)]; prev=initm[r]
    for m in ls_:
        if prev&m!=prev: return False
        prev=m
    return prev&finm[r]==prev
def rcost(r):
    ch=[initm[r]]+[SM_[c] for c in levels(r)]+[finm[r]]; t=0.0
    for a,b in zip(ch,ch[1:]):
        if a!=b: t+=f(dm(b)-dm(a))
    return t
def acyclic():
    # nodes: events 0..NE-1, then block nodes and level nodes
    adj=defaultdict(list); nid=[NE]
    def newnode():
        nid[0]+=1; return nid[0]-1
    for r,B in blocks.items():
        for a,b in zip(B,B[1:]):
            x=newnode()
            for i in a: adj[i].append(x)
            for i in b: adj[x].append(i)
    for r in range(n):
        byl=defaultdict(list)
        for i in evs[r]: byl[chi[i]].append(i)
        lv=sorted(byl, key=lambda c:dm(SM_[c]))
        for a,b in zip(lv,lv[1:]):
            x=newnode()
            for i in byl[a]: adj[i].append(x)
            for i in byl[b]: adj[x].append(i)
    V=nid[0]; indeg=[0]*V
    for u,L in adj.items():
        for v in L: indeg[v]+=1
    dq=deque(v for v in range(V) if indeg[v]==0); seen=0; order=[]
    while dq:
        u=dq.popleft(); seen+=1
        if u<NE: order.append(u)
        for v in adj.get(u,()):
            indeg[v]-=1
            if indeg[v]==0: dq.append(v)
    return seen==V, order
def try_vacate(r,c):
    mine=[i for i in evs[r] if chi[i]==c]
    if any(pinned[i] for i in mine): return None
    lv_r=set(levels(r))-{c}
    plan={}
    for i in mine:
        e=P0[i]
        if e[0]=='SCALE':
            cands=lv_r
        else:
            p=e[2] if e[1]==r else e[1]
            cands=lv_r & set(levels(p))
        if not cands: return None
        # prefer the nearest level by dim
        plan[i]=sorted(cands,key=lambda x:abs(dm(SM_[x])-dm(SM_[c])))
    return plan
def apply_plan(r,c,plan):
    old={i:chi[i] for i in plan}
    touched={r}
    for i in plan:
        for x in regs_of(P0[i]):
            if x<n: touched.add(x)
    before=sum(rcost(x) for x in touched)
    # try first-choice; if acyclic fails, try alternatives per event greedily (one pass)
    for i,cs in plan.items(): chi[i]=cs[0]
    ok=all(chain_ok(x) for x in touched)
    if ok:
        ac,_=acyclic(); ok=ac
    if ok:
        after=sum(rcost(x) for x in touched)
        if after<before-1e-12: return before-after
    for i,v in old.items(): chi[i]=v
    return None
def to_word(order):
    cid=list(W['initial']); out=[]
    for i in order:
        e=P0[i]
        for r in regs_of(e):
            if r<n and cid[r]!=chi[i]:
                out.append(['MOVE',r,cid[r],chi[i],False]); cid[r]=chi[i]
        op=e[0]
        if op=='SCALE' and e[1]<n: out.append(['SCALE',e[1],e[2],chi[i]])
        elif op=='ADD' and e[1]<n and e[2]<n: out.append(['ADD',e[1],e[2],e[3],chi[i]])
        else: out.append(e)
    for r in range(n):
        if cid[r]!=W['final'][r]: out.append(['MOVE',r,cid[r],W['final'][r],False])
    W2=dict(W); W2['program']=out; return W2
if __name__=='__main__':
    from check import check
    ac,order=acyclic(); print('original acyclic',ac)
    cand=[]
    for r in range(n):
        lv=levels(r)
        for c in lv:
            if SM_[c]==initm[r] or SM_[c]==finm[r]: continue
            pl=try_vacate(r,c)
            if pl is not None: cand.append((r,c,pl))
    print('vacate candidates passing level-sharing filter',len(cand)); sys.stdout.flush()
    tot=0; acc=0
    for r,c,pl in cand:
        if c not in levels(r): continue
        pl=try_vacate(r,c)
        if pl is None: continue
        g=apply_plan(r,c,pl)
        if g: tot+=g; acc+=1; print('accepted',r,kind(r),'level dim',dm(SM_[c]),'gain',round(g,5)); sys.stdout.flush()
    print('accepted',acc,'cost gain@kf',tot)
    ac,order=acyclic(); W2=to_word(order); pickle.dump(W2,open('W_V.pkl','wb'))
    print(check(W2,'vacate'))
