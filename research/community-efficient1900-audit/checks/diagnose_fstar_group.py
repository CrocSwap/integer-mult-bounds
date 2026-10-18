"""Exact small counterexamples; imports pinned PR engines without running censuses."""
from pathlib import Path
from fractions import Fraction as F
import importlib.util, json, hashlib, itertools
P=Path('/tmp/pr-efficient1900')
reports={}
for number in (2890,2901,2914):
    path=next((P/'sources'/str(number)).glob('research/*/verify.py'))
    spec=importlib.util.spec_from_file_location('fstar'+str(number),path)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    p=[(1,1,1),(1,1,1),(1,2,3)]
    q=[(2,-1,0),(2,-1,0),(-1,1,0)]
    model=mod.model(p,q); a=[1,1,1]
    got,wit=mod.completion(model,a)
    # Independent exhaustive definition over subsets, orders, and b labels.
    best=0; winner=None
    for count in range(1,4):
      for kept in itertools.combinations(range(3),count):
       for order in itertools.permutations(kept):
        for bs in itertools.product(range(4),repeat=count):
         b=[0]*3
         for t,x in zip(kept,bs):b[t]=x
         if any((a[t]&b[t]).bit_count()%2!=1 for t in kept):continue
         if any(model['M'][t][s]==0 and (a[t]&b[s]).bit_count()%2 for i,t in enumerate(order) for s in order[i+1:]):continue
         if count>best:best=count;winner=dict(a=a,b=b,kept=list(kept),order=list(order))
    assert model['M']==[[1,1,0],[1,1,0],[0,0,1]]
    assert got==1 and best==2 and mod.replay_witness(model,winner)
    reports[str(number)]={'head':json.loads((P/f'{number}.json').read_text())['headRefOid'],'engine_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'fixed_a_completion':dict(P=p,Q=q,M=model['M'],a=a,reported=got,exact_bruteforce=best,valid_witness=winner,explanation='completion chooses numerically largest feasible bitmask, not maximum cardinality; mask4 has one line, mask3 has two.')}
    if number==2914:
      mdl=mod.load_model('cex_min_1.json');ad=mod.anchor_data(mdl)
      witness=json.loads((path.parent/'data/cex_min_1.witness.json').read_text())
      assert mod.replay_witness(mdl,witness)
      found=None
      for t in witness['kept']:
       for ai in range(8):
        for bi in range(8):
         w=json.loads(json.dumps(witness));w['a'][t]=ai;w['b'][t]=bi
         if mod.replay_witness(mdl,w) and not mod.in_box(mdl,ad,w)[0]:
          found=dict(changed_line=t,a=ai,b=bi,anchor_a=ad['a0'][t],anchor_b=ad['b0'][t],size=len(w['kept']),witness=w);break
        if found:break
       if found:break
      reports[str(number)]['outside_box_single_pair_probe']=found or 'none found; not a proof of universal containment'
# False nonparallel branch of C5: every off-diagonal entry vanishes.
p=[(1,1,0),(0,1,0),(0,0,1)];q=[(1,0,0),(-1,1,0),(0,0,1)]
m=[[sum(x*y for x,y in zip(u,v)) for v in q] for u in p]
assert m==[[1,0,0],[0,1,0],[0,0,1]] and p[0][1]*q[0][0]!=p[0][0]*q[0][1]
reports['2890']['C5_counterexample']=dict(P=p,Q=q,M=m,vertex=0,neighbors=[1,2],mutual_edge=[1,2],explanation='p(0),q(0) nonparallel with nonzero pairing. Neighborhood is not empty. Mapping these to orthogonal e2,e1 does not preserve the pairing.')
# Counterexample to "same anchor and odd-diagonal sets exactly when gamma=0".
p=[F(1,2),F(1,2),F(1)];q=[F(1),F(1),F(1)]
diag=sum(x*y for x,y in zip(p,q));assert diag==2
reports['2901']['corollary_only_if_counterexample']=dict(P=[[str(x) for x in p]],Q=[[str(x) for x in q]],M=[[2]],gamma=-1,anchor=[],odd_diagonal=[],explanation='Both sets are empty even though gamma=-1. gamma=0 is sufficient, not necessary for equality on an instance.')
for number,rec in reports.items():
 (P/f'check-{number}-counterexamples.json').write_text(json.dumps(dict(status='counterexamples_verified',**rec),indent=2)+'\n')
 print(number,'completion',rec['fixed_a_completion']['reported'],'versus',rec['fixed_a_completion']['exact_bruteforce'],'outside_box',rec.get('outside_box_single_pair_probe',{}))
