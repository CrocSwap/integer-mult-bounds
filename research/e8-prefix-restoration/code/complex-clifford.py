# Changed-certificate adaptation of PR377, preserving exact Gaussian phase checks.
"""Exact representatives and child decompositions for all fixed E8 frame edges.
Every decomposition keeps a single child of the advertised rank and two
explicit monomial adapters; equality includes the Gaussian global phase.
"""
import sys,json,gzip,hashlib,time,random,os
from pathlib import Path
sys.dont_write_bytecode=True
base=Path(os.environ.get("COMPLEX_PUBLIC",str(Path(__file__).resolve().parent/"public")))/"381/source/research/e8-nine-stage-kappa/complex377"
sys.path.insert(0,str(base/"work/odd-stages"))
from pathlib import Path
from collections import Counter
from clifford_exact import *
t0=time.monotonic();out=Path(os.environ.get('COMPLEX_OUTPUT',str(Path(__file__).resolve().parent/'complex-admission')));out.mkdir(exist_ok=True)
c=json.load(gzip.open(Path(os.environ.get('COMPLEX_PUBLIC',str(Path(__file__).resolve().parent/'public')))/'378/source/research/e8-complex-far-retiming/data/gcert1-e8-r783-far.json.gz'));n=c['h'];frames=c['frames'];ops=[]
def preimage(op):return [x|(z<<n) for x,z,p in inverse(op.tab)[n:]]
for i,U in enumerate(frames):
 op=canonical_frame(n,U);L=[u|(u<<n) for u in U]+[v<<n for v in nullspace(U,n)]
 assert rank(L)==n and rank(L+preimage(op))==n
 assert rank([x for x,z,p in op.tab[n:]])==len(U)
 ops.append(op)
print('canonical exact circuits and preimage labels',len(ops),'PASS',flush=True)
cur=c['start'][:];edges=set()
for phase in ['A','B']:
 for gate in c[phase]:
  f=gate[1];rs=[gate[2]]+[z[0] for z in gate[3]]+(gate[4] if gate[0]=='out' else [])
  for r in rs:
   if cur[r]!=f:edges.add((cur[r],f));cur[r]=f
for r,f in enumerate(c['final']):
 if cur[r]!=f:edges.add((cur[r],f));cur[r]=f
for k,r,f in c['ret']:edges.add((f,0));edges.add((0,f))
assert cur==c['final'];recipes=[];hist=Counter()
for i,(a,b) in enumerate(sorted(edges)):
 op=ops[a].adjoint().then(ops[b]);rec,compiled=lower_child(op);want=abs(len(frames[a])-len(frames[b]));assert rec['rank']==want
 hist[want]+=1;recipes.append(dict(old=a,new=b,**rec))
 if i%200==0:print('children',i,'/',len(edges),'seconds',time.monotonic()-t0,flush=True)
# Old source/target representatives retained by the source invocation are
# C_q and F C_q^{-1}; full and zero are already exactly F and I.
adapters=[]
F=fourier(n)
for p,q in enumerate(c['ports']):
 for role,old,f in [('source',cgate(n,q),c['start'][p]),('target',cgate(n,q).adjoint().then(F),c['final'][c['v']+p])]:
  op=old.adjoint().then(ops[f]);rec,compiled=lower_child(op);assert rec['rank']==0
  adapters.append(dict(port=p,role=role,frame=f,**rec))
# Full-column checks on independently generated small circuits check the
# tableau/global-phase reconciliation against literal Gaussian amplitudes.
rng=random.Random(739361);tests=[]
for h in range(1,5):
 cols=0
 for z in range(32):
  a=ident(h)
  for _ in range(10):
   kind=rng.randrange(5)
   if kind==0:a=a.then(cgate(h,1<<rng.randrange(h),rng.choice([-1,1])))
   elif kind==1:a=a.then(xgate(h,rng.randrange(1<<h)))
   elif kind==2:
    Q=[0]*h
    for i in range(h):
     for j in range(i,h):
      if rng.randrange(2):Q[i]|=1<<j;Q[j]|=1<<i
    a=a.then(diag(h,Q))
   else:a=a.then(perm(h,transpose(basis_extend([rng.randrange(1,1<<h) for _ in range(h)],h),h)))
  rec,b=lower_child(a)
  for col in range(1<<h):assert a.zero_state(col)==b.zero_state(col);cols+=1
  bad=b.then(Op(h,identity(h),[('phase',1)]));assert bad.zero_state()!=a.zero_state()
 tests.append(dict(h=h,circuits=32,all_address_columns=cols,wrong_global_phase_rejected=32))
raw=json.dumps(dict(children=recipes,endpoint_adapters=adapters),sort_keys=True,separators=(',',':')).encode();(out/'CLIFFORD-RECIPES.json').write_bytes(raw)
result=dict(status='PASS_EXACT_GAUSSIAN_CLIFFORD_LOCAL_FRAMES_AND_CHILDREN',frames=len(frames),distinct_directed_edges=len(edges),ranks=dict(hist),endpoint_adapters=len(adapters),recipe_sha256=hashlib.sha256(raw).hexdigest(),all_child_equalities_include_global_phase=True,small_full_column_controls=tests,seconds=time.monotonic()-t0,scope='Fixed E8 local frames, every used nested transition, copied-center directions and old/new endpoint adapters. Does not by itself admit nine-stage global cover, routing or all-size theorem.')
(out/'CLIFFORD-REVIEW.json').write_text(json.dumps(result,indent=2));print(result,flush=True)
