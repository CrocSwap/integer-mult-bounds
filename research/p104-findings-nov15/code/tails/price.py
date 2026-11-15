import sys,json,collections
sys.path.insert(0,'.')
from bound import *   # recomputes; uses argv files
R=json.load(open('../need.json'))
def stayP(P,key):
    x=byst[tuple(key)]; k=x['k']; h=x['hops']; a,b=h[k-1],h[k]; P[a]-=1;P[b]-=1;P[a+b]+=1
def wayP(P,h,G):
    I=info(h); t=I['tail']
    for a,b in zip(t,t[1:]): P[abs(M.dim[b]-M.dim[a])]-=1
    new=[I['L']]+([G] if I['L']!=G else [])+[I['F']]
    for a,b in zip(new,new[1:]): P[abs(M.dim[b]-M.dim[a])]+=1
def evalset(stays,rehome_free):
    P=collections.Counter(nat['P']); used={}
    for r in stays:
        stayP(P,r['key'])
        for c,G,s,_ in r['req']:
            if fin[c]!=127: continue
            if c in used:
                if used[c]!=G: return None
                continue
            used[c]=G
            if s=='ok': wayP(P,c,G)
            elif s=='L-not-under-G' and not rehome_free:
                return None
    return kap(P)
def g(k): return '%+.4f%%'%(100*(float(k)/float(K0)-1))
print('--- per stay, exact PRICEKIT (stay drop + its waypoints; L-not-under-G helpers re-homed at ZERO cost = upper bound)')
cand=[]
for r in R:
    if not r['chainA'] and not r['legal']: continue
    k0=evalset([dict(r,req=[])],True); k=evalset([r],True)
    print(r['key'],'m %.2f'%r['m'],'drop alone',g(k0),'with waypoints',g(k),'legal(no rehome)',r['legal'],collections.Counter(x[2] for x in r['req']))
    cand.append((k,r))
# loose model: ignore main-col/owned, chain on helper cols only
loose=[]
for r in R:
    gs=collections.defaultdict(set)
    for c,G,s,_ in r['req']:
        if fin[c]==127: gs[c].add(G)
    if r['req'] and all(all(sub(a,b) or sub(b,a) for a in v for b in v) for v in gs.values()): loose.append(r)
print('loose A (ignore main-col/owned junk):',len(loose),'stays')
# greedy joint
def greedy(L):
    L=sorted(L,key=lambda r:-r['m']); S=[]
    for r in L:
        if evalset(S+[r],True) is not None and evalset(S+[r],True)>(evalset(S,True) if S else K0): S.append(r)
    return S,evalset(S,True) if S else K0
S,k=greedy([r for _,r in cand]); print('A-strict joint',len(S),g(k))
S,k=greedy(loose); print('A-loose joint',len(S),g(k),[tuple(r['key'][:2]) for r in S][:20])
P=collections.Counter(nat['P']); [stayP(P,r['key']) for r in S]; print('A-loose same stays, drops only (no waypoint cost)',g(kap(P)))
