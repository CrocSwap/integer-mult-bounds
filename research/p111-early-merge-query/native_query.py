"""Scoped exact native check of the PR1525 query block; no supplier or kappa."""
import sys,json,hashlib,importlib.util,time
from pathlib import Path
from collections import Counter
from fractions import Fraction as Q
P=Path(__file__).resolve().parent; ROOT=P.parent; V=P/'pr1060'
assert __debug__
for item in json.loads((V/'SOURCE-RECEIPT.json').read_text())['files']:
 f=V/Path(item['path']).relative_to('research/shared-carrier-decoder')
 assert hashlib.sha256(f.read_bytes()).hexdigest()==item['sha256']
sys.path.insert(0,str(V));from physical import Executor,Array,input_array
from model import basis,distance
spec=importlib.util.spec_from_file_location('pinned_clifford',V/'vendor/clifford_exact.py');cx=importlib.util.module_from_spec(spec);sys.modules[spec.name]=cx;spec.loader.exec_module(cx)
spec=importlib.util.spec_from_file_location('pinned_verify',V/'verify.py');pv=importlib.util.module_from_spec(spec);spec.loader.exec_module(pv)
seed=json.loads((P/'SEED.json').read_text());tree=json.loads((P/'TREE.json').read_text());audit=json.loads((P/'EXPECTED.json').read_text())
frames={1<<j:basis(c['frame'])for j,c in enumerate(seed['chosen'])};weights={1<<j:Q(c['coefficient'])/Q(c['normalization'])for j,c in enumerate(seed['chosen'])};children={s:(a,b)for s,a,b,r in tree['tree']};FULL=(1<<len(weights))-1
for e in audit['tree_events']:frames[e['mask']]=basis(e['frame'])
ops={s:cx.canonical_frame(9,U)for s,U in frames.items()};edge={};transposed={};profile=Counter();invoices=[]
for parent,(a,b)in children.items():
 for child in (a,b):
  d=distance(frames[child],frames[parent]);original=ops[child].adjoint().then(ops[parent]);record,compiled=cx.lower_child(original)
  assert record['rank']==d and compiled.tab==original.tab and compiled.zero_state()==original.zero_state()
  tr=pv.transpose_operator(cx,original);rt,ct=cx.lower_child(tr)
  assert rt['rank']==d and ct.tab==tr.tab and ct.zero_state()==tr.zero_state()
  edge[child,parent]=compiled;transposed[child,parent]=ct;profile[d]+=1
  invoices.append(dict(child=child,parent=parent,rank=d,forward=dict(Counter(g[0]for g in compiled.circuit)),transpose=dict(Counter(g[0]for g in ct.circuit))))
assert dict(profile)=={int(k):v for k,v in audit['transport_profile'].items()}
# Depth-first evaluation retains the more storage-intensive child first.
def need(s):
 if s not in children:return 1
 a,b=children[s];x,y=need(a),need(b);return x+1 if x==y else max(x,y)
order={s:tuple(sorted(pair,key=lambda x:need(x),reverse=True))for s,pair in children.items()}
fixtures=[]
for trial in range(2):
 ex=Executor(); logical={s:input_array(j,trial)for j,s in enumerate(weights)};sources={s:ex.apply(x.copy(),ops[s].circuit)for s,x in logical.items()};old={s:x.copy()for s,x in sources.items()};acc=input_array(len(weights),trial);y=ex.apply(acc.copy(),ops[FULL].circuit);live=set();peak=[0];counts=Counter()
 def forward(s):
  if s not in children:
   z=Array([0]*512,[0]*512);z.add(sources[s],weights[s]);live.add(s);peak[0]=max(peak[0],len(live));counts['weighted_source_copies']+=1;return z
  a,b=order[s];left=forward(a);right=forward(b)
  ex.apply(left,edge[a,s].circuit);ex.apply(right,edge[b,s].circuit);left.add(right,Q(1));counts['merge_adds']+=1;counts['temporary_discards']+=1;live.remove(a);live.remove(b);live.add(s);return left
 z=forward(FULL);y.add(z,Q(1));counts['target_adds']+=1;counts['temporary_discards']+=1;live.remove(FULL)
 expected=acc.copy()
 for s,x in logical.items():expected.add(x,weights[s])
 ex.apply(expected,ops[FULL].circuit)
 assert y.same(expected)and all(sources[s].same(old[s])for s in sources)and not live
 assert peak[0]==need(FULL)
 # Inverse transpose of the complete block shear on the dual literal frames.
 dual={s:pv.transpose_operator(cx,o.adjoint())for s,o in ops.items()}
 dl={s:input_array(j+30,trial)for j,s in enumerate(weights)};ds={s:ex.apply(x.copy(),dual[s].circuit)for s,x in dl.items()};dylogical=input_array(80,trial);dy=ex.apply(dylogical.copy(),dual[FULL].circuit);dyold=dy.copy();tcounts=Counter();tlive=[1];tpeak=[1]
 def back(s,z):
  if s not in children:
   ds[s].add(z,-weights[s]);tcounts['weighted_source_adds']+=1;tcounts['temporary_discards']+=1;tlive[0]-=1;return
  a,b=reversed(order[s]);other=z.copy();tcounts['branch_copies']+=1;tlive[0]+=1;tpeak[0]=max(tpeak[0],tlive[0]);ex.apply(z,transposed[a,s].circuit);back(a,z);ex.apply(other,transposed[b,s].circuit);back(b,other)
 tcounts['target_copies']=1;back(FULL,dy.copy());assert tlive[0]==0 and dy.same(dyold)
 for s,x in dl.items():
  exp=x.copy();exp.add(dylogical,-weights[s]);ex.apply(exp,dual[s].circuit);assert ds[s].same(exp)
 fixtures.append(dict(trial=trial,forward_peak_temporaries=peak[0],transpose_peak_temporaries=tpeak[0],forward_counts=dict(counts),transpose_counts=dict(tcounts),literal_gate_executions=dict(ex.counts)))
# A changed leaf coefficient is detectable on the dense fixture.
wrong=acc.copy()
for s,x in logical.items():wrong.add(x,weights[s]+(1 if s==1 else 0))
ex.apply(wrong,ops[FULL].circuit);assert not wrong.same(y)
out=dict(status='PASS_SCOPED_NATIVE_MERGE_QUERY_FORWARD_AND_INVERSE_TRANSPOSE',native_edges=len(edge),profile=dict(profile),rank_mass=sum(r*n for r,n in profile.items()),fixtures=fixtures,invoices=invoices,inputs={str(f.relative_to(P)):hashlib.sha256(f.read_bytes()).hexdigest()for f in [P/'SEED.json',P/'TREE.json',V/'vendor/clifford_exact.py',V/'physical.py',V/'verify.py']},scope='Exact signed Pauli and global phase equality certifies each native edge for all vectors. Two dense Gaussian fixtures per orientation independently exercise the whole local block. Forward original source streams and inverse-transpose target are unchanged. Clean temporary creation, discard, weighted copies, adapters and their owner/precision/tape charges remain explicit obligations. This is not a complete P111 supplier, owner packing, new kappa or formal multiplication proof.')
assert json.loads(json.dumps(out)) == json.loads((P/'NATIVE-EXPECTED.json').read_text()), 'native receipt mismatch'
print(out['status'],dict(profile),'scratch=4 each orientation; NO_NEW_KAPPA',flush=True)
