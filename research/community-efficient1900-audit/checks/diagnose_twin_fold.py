"""PR2832: one global fold cannot cancel distinct proportionality ratios."""
from pathlib import Path
import importlib.util,json,hashlib
import numpy as np
P=Path('/tmp/pr-efficient1900');pkg=P/'sources/2832/research/decoder-floors-reduction';src=pkg/'checks/e8.py'
spec=importlib.util.spec_from_file_location('e8',src);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
X=m.G[np.ix_(m.P112,m.F0i)];B=((1+m.G)%2)[np.ix_(m.P112,m.P112)];BB=np.block([[B,B],[B,B]])
def rank(rows):
    piv={}
    for row in rows:
        x=sum(int(a%2)<<i for i,a in enumerate(row))
        while x:
            h=x.bit_length()-1
            if h in piv:x^=piv[h]
            else:piv[h]=x;break
    return len(piv)
cols=[];costs=[]
for i in range(8):
 for sign in (1,-1):
  v=np.r_[X[:,i],sign*X[:,i]];cols.append(v)
  idx=np.flatnonzero(v);costs.append(rank(BB[np.ix_(idx,idx)]))
Pmat=np.array(cols).T;Qnumer=Pmat.copy();summ=Pmat@Qnumer.T
# Q=Qnumer/8: exact target diag(G/2,G/2), since XX^T=2G.
GG=m.G[np.ix_(m.P112,m.P112)];zero=np.zeros_like(GG)
assert np.array_equal(X@X.T,2*GG)
assert np.array_equal(summ,4*np.block([[GG,zero],[zero,GG]]))
assert costs==[8]*16 and sum(costs)==128
# All16terms meet both calls; each input half is proportional with ratio +/-1.
assert all(np.any(v[:112]) and np.any(v[112:]) for v in cols)
assert all(np.array_equal(v[112:],sign*v[:112]) for v,sign in zip(cols,[1,-1]*8))
# To kill ratio+1 needs lambda=-1; ratio-1 needs lambda=+1: incompatible.
receipt=dict(number=2832,head=json.loads((P/'2832.json').read_text())['headRefOid'],status='verified_proof_gap',e8_source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),roles_per_call=112,terms=16,column_recipe='For each coordinate x_i and sign s in {+1,-1}, p=(x_i,s*x_i), q=p/8.',exact_target='diag(G/2,G/2); every entry, including cross blocks, verified exactly with integer numerators',per_term_costs=costs,total_cost=128,all_terms_MD=True,dangling_terms=0,proportionality_ratios=[1,-1],cancelling_lambdas=[-1,1],claimed_under_H_lower_bound=256,per_call_restriction_terms=[16,16],advertised_8_plus_e=8,conclusion='The proof cannot choose a single fold parameter that cancels all merely proportional MD terms. Its stated H-consequence would require256 for this128-cost network; this is a gap in that conditional argument, not a proof or refutation of H. A common proportionality ratio (or common annihilating subspace) is an additional sufficient premise. The m=8k+e assertion also does not bound the number of terms surviving each single-call restriction by8+e.')
(P/'check-2832-twin-fold.json').write_text(json.dumps(receipt,indent=2)+'\n');print('VERIFIED:16 proportional MD terms, cost128, incompatible cancelling ratios+/-1; each restriction has16terms, not8.')
