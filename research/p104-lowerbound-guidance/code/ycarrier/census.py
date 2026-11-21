# YCARRIER census: where the y-carrier condition can hold on P104 (exact, stdlib).
import sys, random, pickle
from collections import Counter
sys.path.insert(0,'<word-rung-package>/tools')
import pricekit as pk
W=pk.load('<word-rung-package>/data/t7669.json.gz')
P=W['ports']; PS=set(P); h=9
dot=lambda a,b: bin(a&b).count('1')&1
print('port weights',Counter(bin(p).count('1') for p in P), 'all q.q odd:',all(dot(p,p) for p in P))
ev=[sum(1 for p in P if p!=t and not dot(t,p)) for t in P]
print('even partners per port',Counter(ev))
def span(B):
    S={0}
    for b in B: S|={x^b for x in S}
    return S
def perp(S): return [x for x in range(1,512) if all(not dot(x,s) for s in S)]
# exact: fraction of d-dim charts a with >=1 carrier port (port in a^perp), d=8,7,6 via K=a^perp of dim 1,2,3
def ksubs(k):
    # enumerate k-dim subspaces of F2^9 via reduced row echelon (canonical: each subspace once)
    seen=set(); out=[]
    def rec(basis,start):
        if len(basis)==k:
            S=frozenset(span(basis))
            if S not in seen: seen.add(S); out.append(S)
            return
        for v in range(start,512):
            if v not in span(basis): rec(basis+[v],v+1)
    return None
def count_exact(k):
    # count k-subspaces by number of ports they contain, using canonical RREF enumeration
    from itertools import combinations
    cnt=Counter(); tot=0
    # RREF: pivots p1>p2>..; vectors with leading bit at pivot, zero at other pivots
    def gen(pivs):
        free=[[b for b in range(piv) if b not in pivs] for piv in pivs]
        def rec(i,acc):
            if i==len(pivs): yield acc; return
            fb=free[i]
            for m in range(1<<len(fb)):
                v=1<<pivs[i]
                for j,b in enumerate(fb):
                    if m>>j&1: v|=1<<b
                yield from rec(i+1,acc+[v])
        yield from rec(0,[])
    for pivs in combinations(range(9),k):
        for B in gen(list(pivs)):
            S=span(B); c=sum(1 for x in S if x in PS); cnt[c]+=1; tot+=1
    return tot,cnt
res={}
for k in (1,2,3,4):
    tot,cnt=count_exact(k)
    has=tot-cnt[0]
    res[9-k]=(tot,has,dict(cnt))
    print('chart dim d=%d: #charts %d, with>=1 carrier port %d (%.4f), carrier-count hist %s'%(9-k,tot,has,has/tot,dict(sorted(cnt.items()))))
pickle.dump(res,open('census.pkl','wb'))
# t7669: 8-dim frames used by owned moves; normal vector; is it a port? ports inside
F=W['frames']; n=W['public']; prog=W['program']
d8=Counter()
for e in prog:
    if e[0]=='MOVE' and e[1]>=n:
        for f in (e[2],e[3]):
            if len(F[f])==8: d8[f]+=1
for f,c in d8.items():
    S=span(F[f]); nv=[x for x in range(1,512) if all(not dot(x,s) for s in F[f])]
    print('t7669 owned 8-dim chart',f,'normal',nv,'normal is port:',nv[0] in PS,'ports inside',sum(1 for p in P if p in S),'uses',c)
