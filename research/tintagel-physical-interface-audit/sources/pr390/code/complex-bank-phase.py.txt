"""Exact rank-zero endpoint adapters for the two rank-eight residual banks."""
import sys,os,json,gzip,hashlib,time
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;PUB=Path(os.environ.get('COMPLEX_PUBLIC',str(HERE/'public')));BASE=PUB/'381/source/research/e8-nine-stage-kappa/complex377';CP=Path(os.environ.get('COMPLEX_CERT',str(PUB/'378/source/research/e8-complex-far-retiming/data/gcert1-e8-r783-far.json.gz')));OUT=Path(os.environ.get('COMPLEX_OUTPUT',str(HERE/'complex-bank-phase')));OUT.mkdir(exist_ok=True)
sys.path.insert(0,str(BASE/'work/odd-stages'));from clifford_exact import *
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();sources={str(CP):sha(CP),str(BASE/'work/odd-stages/clifford_exact.py'):sha(BASE/'work/odd-stages/clifford_exact.py')};c=json.load(gzip.open(CP));recipes=[]
for fid in [206,221]:
 E=c['frames'][fid];assert len(E)==8
 perp=nullspace(E,9);assert len(perp)==1;q=perp[0];assert q.bit_count()%2==1 and q!=511
 j=0 if not q&1 else next(i for i in range(1,9) if not q>>i&1);w=q^(1<<j);cols=[]
 for b in range(9):
  swapped=j if b==0 else 0 if b==j else b;x=1<<swapped
  if (w&x).bit_count()%2:x^=w
  cols.append(x)
 assert cols[0]==q and all(((x&y).bit_count()%2)==(i==j) for i,x in enumerate(cols) for j,y in enumerate(cols))
 Urows=transpose(cols,9)
 Pu=perm(9,Urows);C8=ident(9)
 for i in range(1,9):C8=C8.then(cgate(9,1<<i))
 # Conjugate coordinate factors along q-perp. Use explicit sequence conventions,
 # and independently compare its binary preimage to the canonical E frame.
 routed=Pu.adjoint().then(C8).then(Pu)
 canonical=canonical_frame(9,E)
 pre=lambda op:[x|(z<<9) for x,z,p in inverse(op.tab)[9:]]
 assert rank(pre(routed)+pre(canonical))==9
 relative=canonical.adjoint().then(routed)
 rec,compiled=lower_child(relative);assert rec['rank']==0
 # Exact Clifford compiler includes signed Pauli tableau and scalar-phase
 # equality on a nonzero Gaussian state, not merely equal binary frames.
 assert relative.tab==compiled.tab and relative.zero_state()==compiled.zero_state()
 recipes.append(dict(frame=fid,perp_port=q,orthogonal_columns=cols,orthogonal_rows=Urows,endpoint_rank=8,coordinate_axes=list(range(1,9)),canonical_to_orthogonal_coordinate_adapter=rec))
assert sources=={p:sha(p) for p in sources}
result=dict(status='PASS_EXACT_RANK_EIGHT_BANK_ENDPOINT_PHASE_ADAPTERS',endpoints=recipes,source_hashes=sources,scope='Finite local9 Gaussian rank-zero adapter; global owner permutation and heterogeneous bank tiling are audited separately by root. The adapter must be emitted and charged, not inferred free from equal binary frames.')
(OUT/'BANK-ENDPOINT-PHASE.json').write_text(json.dumps(result,indent=2));print('PASS exact Gaussian rank8 bank endpoint adapters',[(r['frame'],r['perp_port']) for r in recipes],flush=True)

