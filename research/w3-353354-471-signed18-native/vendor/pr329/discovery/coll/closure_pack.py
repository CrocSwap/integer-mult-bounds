"""Shared-donor kernel search: per entrance E, maximum-weight closure (pivot -> donors of its representation in a cost-ordered response basis; several bases and common cut points), lazy global greedy over entrances with helper exclusivity; env ORDERS, NT, SEED, NOISE, EXCLUDE (comma list), PRELOAD. Usage: closure_pack.py HELPERS.pkl POOL.pkl [POOL2.pkl ...] OUT.json
Chafik Boukhalfa (chafreaky), Anthropic Claude assistance; Apache-2.0."""
import pickle,sys,math,collections,json,random,heapq,os
from collections import deque
d=pickle.load(open(sys.argv[1],'rb'));OUT=sys.argv[-1];mem={};BAS={}
for path in sys.argv[2:-1]:
    P=pickle.load(open(path,'rb'))
    for k,val in P.items():
        if isinstance(val,tuple):basis,L=val
        else:basis,L=[list(k)],val
        key=tuple(map(tuple,basis));mem[key]=list(L);BAS[key]=basis
ORDERS=int(os.environ.get('ORDERS','6'));NT=int(os.environ.get('NT','4'));SEED=int(os.environ.get('SEED','1'))
ff=d['firstframe'];ft=d['ftab'];resp=d['resp'];lr=d['lastread'];tc=d['touch']
phi=lambda r:0.0 if r<=0 else r*math.log(100/r);dim=lambda s:ft[ff[s]]['dim']
PGe=lambda s,e:-(phi(dim(s)-e)-phi(dim(s)))
DCe=lambda s,e:phi(e)+phi(dim(s)-e)-phi(dim(s))
def rank(vs):
    b={};r=0
    for x in vs:
        while x:
            h=x.bit_length()-1
            if h in b:x^=b[h]
            else:b[h]=x;r+=1;break
    return r
def maxflow_closure(prof,req,cost):
    # nodes: 0=S,1=T, pivots, donors
    P=list(prof);D=sorted({m for p in P for m in req[p]})
    idx={('p',p):i+2 for i,p in enumerate(P)};idx.update({('d',m):i+2+len(P) for i,m in enumerate(D)})
    N=2+len(P)+len(D);g=[[] for _ in range(N)]
    def add(a,b,c):g[a].append([b,c,len(g[b])]);g[b].append([a,0,len(g[a])-1])
    INF=1e18
    for p in P:
        add(0,idx[('p',p)],prof[p])
        for m in req[p]:add(idx[('p',p)],idx[('d',m)],INF)
    for m in D:
        if cost[m]>0:add(idx[('d',m)],1,cost[m])
    flow=0
    while True:
        lvl=[-1]*N;lvl[0]=0;q=deque([0])
        while q:
            a=q.popleft()
            for b,c,r in g[a]:
                if c>1e-12 and lvl[b]<0:lvl[b]=lvl[a]+1;q.append(b)
        if lvl[1]<0:break
        it=[0]*N
        def dfs(a,f):
            if a==1:return f
            while it[a]<len(g[a]):
                e=g[a][it[a]];b,c,r=e
                if c>1e-12 and lvl[b]==lvl[a]+1:
                    x=dfs(b,min(f,c))
                    if x>1e-12:e[1]-=x;g[b][r][1]+=x;return x
                it[a]+=1
            return 0
        while True:
            x=dfs(0,INF)
            if x<=1e-12:break
            flow+=x
    seen=[False]*N;seen[0]=True;q=deque([0])
    while q:
        a=q.popleft()
        for b,c,r in g[a]:
            if c>1e-12 and not seen[b]:seen[b]=True;q.append(b)
    selP=[p for p in P if seen[idx[('p',p)]]];selD=sorted({m for p in selP for m in req[p]})
    val=sum(prof[p] for p in selP)-sum(cost[m] for m in selD)
    return val,selP,selD
rng=random.Random(SEED)
EXCL={int(x) for x in os.environ.get('EXCLUDE','').split(',') if x}
for k in mem:mem[k]=[s for s in mem[k] if s not in EXCL]
def solve_line(u,taken,free):
    G=[s for s in mem[u] if s not in taken]
    if len(G)<2:return None
    e=len(BAS[u]);cost={s:(0.0 if s in free else DCe(s,e)) for s in G}
    ts=sorted(set(lr[s] for s in G));cands=[]
    for t in ts:
        S=[s for s in G if lr[s]<=t<tc[s]]
        if len(S)>=2:cands.append((len(S)-rank([resp[s] for s in S]),t,S))
    cands=[c for c in cands if c[0]>0]
    if not cands:return None
    cands.sort(key=lambda c:(-c[0],-c[1]));best=None;seenS=set()
    for k,t,S in cands[:NT]:
        key=tuple(S)
        if key in seenS:continue
        seenS.add(key)
        for o in range(ORDERS):
            order=sorted(S,key=lambda s:cost[s]*(1+(0.5*rng.random() if o else 0))+(1e-3*rng.random() if o else 0))
            basis={};req={};prof={}
            for s in order:
                x=resp[s];combo=set()
                while x:
                    h=x.bit_length()-1
                    if h in basis:bx,bc=basis[h];x^=bx;combo^=bc
                    else:break
                if x:basis[x.bit_length()-1]=(x,combo|{s})
                else:req[s]=sorted(combo);prof[s]=PGe(s,e)
            if not prof:continue
            val,P,Dn=maxflow_closure(prof,req,cost)
            if val>1e-9 and (best is None or val>best[0]):best=(val,t,[(p,req[p]) for p in P],Dn)
    return best
taken=set();free=collections.defaultdict(set);heap=[];sol={}
PRE=json.load(open(os.environ['PRELOAD'])) if os.environ.get('PRELOAD') else []
for e in PRE:taken.add(e['pivot']);taken.update(e['donors'])
lines=list(mem)
for i,u in enumerate(lines):
    b=solve_line(u,taken,free[u])
    if b:heap.append((-b[0]*(1+float(os.environ.get('NOISE','0'))*rng.random()),i));sol[i]=b
heapq.heapify(heap);print('lines with positive closure',len(heap),'upper sum',-sum(h[0] for h in heap),flush=True)
sel=[dict(pivot=e['pivot'],donors=e['donors'],basis=e['basis'],cut=max(lr[m] for m in [e['pivot']]+e['donors'])) for e in PRE];total=0.0
while heap:
    nv,i=heapq.heappop(heap);u=lines[i]
    b=solve_line(u,taken,free[u])
    if not b:continue
    NZ=float(os.environ.get('NOISE','0'))
    key=-b[0]*(1+NZ*rng.random())
    if heap and key>heap[0][0]+1e-9 and nv!=key:heapq.heappush(heap,(key,i));continue
    val,t,ents,Dn=b;total+=val
    for p,D in ents:
        sel.append(dict(pivot=p,donors=D,basis=BAS[u],cut=max(lr[m] for m in [p]+D)));taken.add(p)
    for m in Dn:taken.add(m);free[u].add(m)
    # allow the same line again (donors free)
    mem[u]=[s for s in mem[u] if s not in taken or s in free[u]]
    b2=solve_line(u,taken-free[u],free[u])
    if b2:heapq.heappush(heap,(-b2[0],i))
    print('accept rank',len(BAS[u]),'val %.3f'%val,'pivots',len(ents),'donors',len(Dn),'total %.3f'%total,flush=True)
print('entries',len(sel),'phi gain',-total)
print('donor-count hist',sorted(collections.Counter(len(e['donors']) for e in sel).items()))
print('pivot dims',sorted(collections.Counter(dim(e['pivot']) for e in sel).items()))
json.dump(sel,open(OUT,'w'))
