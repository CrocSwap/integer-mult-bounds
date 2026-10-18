# BLOCUS check: inputs for the B-locus m>=10 floor (THEORY.md).  UNIT=P112|P104|E8 [A2TRI=a,b,c].
# (a) label spans: labels of L\X span F2^9 and sup(co) has span of dim 8 for every deficient class co (so table entries are exact class-level costs)
# (b) per-term minimum of the restricted (X deleted both sides) class table; (c) inside relaxation for m'' = 9..11 terms;
# (d) Q_XX = square lower bound with X deleted on both sides (opt3u duality B&B, complete: all candidate spaces 1-dim);
# (e) (S): r(O_{u_i} \ (E6 u X)) spans r_i^perp, and B[X,s] = e_i there.
import os,sys,io,contextlib
os.environ['NDIM']='8'; os.environ['NT']='8'
from a2lib import *
import networkx as nx, opt3u
Xt=list(X); off=[u for u in range(v) if u not in Xt]
print(UNIT,'X',Xt,'v',v,flush=True)
assert blk(Brows,off,off)==9
defc=[]; NRM=[]
for co,w in cls.items():
    Oc=[u for u in bits(w) if u not in Xt]
    ns=nullspace([R[u] for u in Oc],8)
    if ns: assert len(ns)==1; defc.append(co); NRM.append(ns[0])
def _nz(x):
    i=next(k for k in range(8) if x[k]!=0); return tuple(a/x[i] for a in x)
assert len(set(_nz(x) for x in NRM))==len(NRM)  # distinct normals: a direction kills at most one class
sup=lambda co: [u for u in off if not (cls[co]>>u)&1]
dirs=[sup(co) for co in defc]
for d in dirs: assert blk(Brows,d,off)==8
f=[[blk(Brows,a,b) for b in dirs+[off]] for a in dirs+[off]]
n=len(dirs); pmin=min(min(r) for r in f)
print('(a) ok; deficient classes on L\\X:',n,' (b) per-term min',pmin,flush=True)
def solve(mt):
    Gr=nx.DiGraph(); Gr.add_node('s',demand=-mt); Gr.add_node('t',demand=mt)
    for i in range(n+1): Gr.add_edge('s',('r',i),capacity=1 if i<n else mt,weight=0)
    for j in range(n+1): Gr.add_edge(('c',j),'t',capacity=1 if j<n else mt,weight=0)
    for i in range(n+1):
        for j in range(n+1): Gr.add_edge(('r',i),('c',j),capacity=mt,weight=f[i][j])
    return nx.min_cost_flow_cost(Gr)
rel={mt:solve(mt) for mt in (8,9,10,11)}
print('(c) inside relaxation',rel,flush=True)
ph=[([0]*8 if u in Xt else list(L[u])) for u in range(v)]; qh=ph
out={}
for co,w in cls.items():
    Oc=bits(w); nr=nullspace([ph[u] for u in Oc],8); nc=nullspace([qh[u] for u in Oc],8)
    if nr or nc: out[co]=(len(Oc),nr,nc)
assert all(len(x[1])<=1 and len(x[2])<=1 for x in out.values())
buf=io.StringIO()
with contextlib.redirect_stdout(buf):
    QXX=opt3u.run(Xt,Xt,[0]*v,[0]*v,out,90,verbose=False,PH=(ph,qh))
print('(d) Q_XX',QXX,flush=True)
E6=[s for s in range(v) if all(Gm[x][s]==0 for x in Xt)]
for i in range(3):
    Sset=[s for s in O[i] if s not in E6 and s not in Xt]
    assert rank([R[s] for s in Sset],8)==7 and all(dot(R[s],R[Xt[i]])==0 for s in Sset)
    assert {tuple((Brows[x]>>s)&1 for x in Xt) for s in Sset}=={tuple(int(a==i) for a in range(3))}
assert rank([R[u] for u in Xt],8)==2
print('(e) ok')
caseA=QXX+2; caseB=QXX+(2*pmin-9); caseC=rel[9]
print('FLOOR B-locus m>=10:',min(caseA,caseB,caseC),' [J* square + T_r,T_c: %d; merging in J*: >= %d; |J*|>=9 unmerged: %d]'%(caseA,caseB,caseC))
