# Pair-cost table of an A2-family member and the m >= 10 "in-colspace" arithmetic (HUNT-A2 section 3(B)).
# Model: factors in the realisation's spaces (P = A X, Q = B Y). A row normal x has support R(x) = {u : a_u . x != 0}; by the exact rank formula the cost of a term
# depends only on the label classes avoided by R(x) and A(y). The catalogue lists the (1-dim, here) deficiency directions: a normal outside the catalogue behaves as 'full support'.
# After merging terms with parallel normals (cost does not rise), WLOG row normals are pairwise non-parallel and so are column normals, so each catalogue direction is used at most once.
# The relaxation below minimises the sum of pair costs over m' >= 9 terms using each catalogue row / column direction at most once (no duality / independence constraints), exact DP.
# usage: UNIT=P112 python pairtable.py gen|tie [LOWER_BOUND]     gen: first random member with the exact iff pattern; tie: the member of data/tie_<UNIT>.json (P112, E8)
import sys, json, os, random
from a2lib import *
mode=sys.argv[1] if len(sys.argv)>1 else 'gen'
if mode=='tie':
    D=json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','data','tie_%s.json'%UNIT)))
    th=tuple(Fr(x) for x in D['theta']); zX=tuple(Fr(x) for x in D['zX'])
else:
    rnd=random.Random(1)       # first random member with the exact iff pattern (as in a2fam.py)
    while True:
        th=tuple(Fr(rnd.randint(-9,9)) for _ in range(4)); zX=tuple(Fr(rnd.randint(-50,50),rnd.randint(1,7)) for _ in range(3))
        if pattern_ok(Mof(*build(th,zX)))==0: break
A,B=build(th,zX); M=Mof(A,B); assert pattern_ok(M)==0 and rank(A,9)==9 and rank(B,9)==9
out=catalogue(A,B)
assert all(len(x[1])<=1 and len(x[2])<=1 for x in out.values())      # every deficiency space is 1-dim
def norm(x):
    i=next(k for k in range(9) if x[k]!=0); return tuple(a/x[i] for a in x)
rd=sorted(set(norm(x[1][0]) for x in out.values() if x[1])); cd=sorted(set(norm(x[2][0]) for x in out.values() if x[2]))
supp=lambda vecs,x:[u for u in range(v) if dot(vecs[u],x)!=0]
Rr=[supp(A,d) for d in rd]+[list(range(v))]; Ac=[supp(B,e) for e in cd]+[list(range(v))]
f=[[blk(Brows,a,b) for b in Ac] for a in Rr]
nr,nc=len(rd),len(cd)
e9=[i for i,d in enumerate(rd) if all(x==0 for x in d[:8])]; assert len(e9)==1; e9=e9[0]
print('%s %s: row directions %d (incl. e9), column directions %d, table %dx%d (last = full support)'%(UNIT,mode,nr,nc,nr+1,nc+1))
for i,row in enumerate(f): print('  row',i,'(e9)' if i==e9 else '    ',row)
nonE9=[f[i][j] for i in range(nr+1) if i!=e9 for j in range(nc+1)]
print('min over non-e9 rows:',min(nonE9),'| entries below 7 among non-e9 rows:',sorted(set((i,j,f[i][j]) for i in range(nr+1) if i!=e9 for j in range(nc+1) if f[i][j]<7)))
print('e9 row:',f[e9])
import networkx as nx
def relax(mt):
    # exact min-cost flow: row slots (each real row direction capacity 1, 'full' unlimited) -> column slots (same); exactly mt terms (units of flow)
    G=nx.DiGraph(); G.add_node('s',demand=-mt); G.add_node('t',demand=mt)
    for i in range(nr+1): G.add_edge('s',('r',i),capacity=1 if i<nr else mt,weight=0)
    for j in range(nc+1): G.add_edge(('c',j),'t',capacity=1 if j<nc else mt,weight=0)
    for i in range(nr+1):
        for j in range(nc+1): G.add_edge(('r',i),('c',j),capacity=mt,weight=f[i][j])
    return nx.min_cost_flow_cost(G)
vals={mt:relax(mt) for mt in range(9,16)}
print('relaxation optimum by number of terms m\' (distinct catalogue directions, no duality):',vals)
print('RESULT',UNIT,mode,'min10plus',min(vals[m] for m in range(10,16)),'relax9',vals[9])
# ---- assertions (HUNT-A2 section 3(B) arithmetic: non-e9 pair costs >= 7, except 6 only in the single 2-kill column; e9 row >= 2, or 1 in the 2-kill column) ----
low=sorted(set((i,j,f[i][j]) for i in range(nr+1) if i!=e9 for j in range(nc+1) if f[i][j]<7))
cols_low=sorted(set(j for _,j,_ in low))
assert all(c==6 for _,_,c in low) and len(cols_low)<=1, low
assert min(f[e9][j] for j in range(nc+1) if j not in cols_low)>=2 and min(f[e9])>=1
if cols_low: assert f[e9][cols_low[0]]==1
assert len(set(len(Ac[j]) for j in cols_low))<=1
LB=int(sys.argv[2]) if len(sys.argv)>2 else 0
assert min(vals[m] for m in range(10,16))>=LB, (vals,LB)
print('PASS pair table %s %s: non-e9 minimum %d (%s), e9 row minimum %d; relaxation for m\' >= 10 terms is %d >= %d'%(UNIT,mode,min(nonE9),'6 only in one column' if cols_low else 'no 6',min(f[e9]),min(vals[m] for m in range(10,16)),LB))
