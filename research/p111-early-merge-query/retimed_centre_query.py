"""Reuse paid terminal centre moves to gather a late query at FULL.
Scoped physical interface, not a complete changed scatter or owner admission.
"""
import sys,json,gzip,hashlib,importlib.util
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
p=Path(__file__).resolve().parent;r=p.parent;V=p/'pr1060';sys.path.insert(0,str(V));from physical import Array,Executor,input_array
from model import basis
assert __debug__
for name,h in json.loads((p/'MANIFEST.json').read_text()).items():assert hashlib.sha256((p/name).read_bytes()).hexdigest()==h,('source pin',name)
sp=importlib.util.spec_from_file_location('cx',V/'vendor/clifford_exact.py');cx=importlib.util.module_from_spec(sp);sys.modules['cx']=cx;sp.loader.exec_module(cx)
sp=importlib.util.spec_from_file_location('pv',V/'verify.py');pv=importlib.util.module_from_spec(sp);sp.loader.exec_module(pv)
w=json.loads(gzip.decompress((p/'inputs/word-base.json.gz').read_bytes()));seed=json.loads((p/'CENTRE-SEED.json').read_text());terms=seed['terms'];pivot=0;full=basis([1<<j for j in range(9)]);TF=cx.canonical_frame(9,full);U=[basis(x['frame'])for x in terms];alpha=[Q(x['weight'])for x in terms]
# Recompute the full source and dirty coefficient query from pinned A.
sp=importlib.util.spec_from_file_location('ar',p/'vendor/pr1134_verify.py');ar=importlib.util.module_from_spec(sp);sp.loader.exec_module(ar)
rows=[{i:Q(1)}for i in range(224+w['report']['R'])]
for e in w['precondition']+w['A']:
 if e[0]=='add':ar.add_row(rows[e[1]],Q(e[3],e[4]),rows[e[2]])
 else:rows[e[1]]={i:x*Q(e[2],e[3])for i,x in rows[e[1]].items()}
query={}
for item in terms:ar.add_row(query,Q(item['weight']),rows[item['center']])
beta=seed['puncture']
for i in range(112):
 if i!=beta:assert query.get(i,0)==Q(sum(a*b for a,b in zip(w['root_lines'][beta],w['root_lines'][i])),2)
assert {str(i):str(x)for i,x in query.items()if i>=112}==seed['dirty_coefficients']
assert str(query.get(beta,0))==seed['omitted_source_coefficient']
normal=next(x for x in range(1,512)if all(not(x&z).bit_count()%2 for z in U[pivot]));E=(normal,);TE=cx.canonical_frame(9,E)
# Exact chronological availability: no remaining B or early-tail use prevents moving these centres early.
for item in terms:
 role=item['center']
 assert all(role not in(e[1:3]if e[0]=='add'else e[1:2])for e in w['B'])
 assert all(role not in(w['cleanup'][i][1:3]if w['cleanup'][i][0]=='add'else w['cleanup'][i][1:2])for i,_ in w['early_cleanup'])
 assert role<112 or str(role)not in w['helper_final']

def transpose(o):return pv.transpose_operator(cx,o)
def compile(o,rank):
 receipt,c=cx.lower_child(o);assert receipt['rank']==rank and c.tab==o.tab and c.zero_state()==o.zero_state();return c
frames=[cx.canonical_frame(9,z)for z in U];moves=[compile(T.adjoint().then(TF),1)for T in frames];dualmoves=[compile(transpose(T.adjoint()),1)for T in moves];copy=compile(TF.adjoint().then(TE),8);dualcopy=compile(transpose(copy),8)

def scale(x,q):
 out=Array([0]*512,[0]*512);out.add(x,q);return out
fixtures=[]
for trial in range(2):
 ex=Executor();x=[input_array(j,trial)for j in range(len(terms))];yl=input_array(20,trial);vals=[ex.apply(a.copy(),T.circuit)for a,T in zip(x,frames)];y=ex.apply(yl.copy(),TE.circuit)
 for j in range(len(vals)):ex.apply(vals[j],moves[j].circuit)
 vals[pivot]=scale(vals[pivot],alpha[pivot])
 for j in range(len(vals)):
  if j!=pivot:vals[pivot].add(vals[j],alpha[j])
 tmp=ex.apply(vals[pivot].copy(),copy.circuit);y.add(tmp,Q(1))
 for j in reversed(range(len(vals))):
  if j!=pivot:vals[pivot].add(vals[j],-alpha[j])
 vals[pivot]=scale(vals[pivot],1/alpha[pivot]);expected=yl.copy()
 for a,c in zip(x,alpha):expected.add(a,c)
 assert y.same(ex.apply(expected,TE.circuit))and all(a.same(ex.apply(b.copy(),TF.circuit))for a,b in zip(vals,x))
 # Same chronological inverse-transpose word: promote dual frames, dual shears, dual copy, inverse dual shears.
 ds=[ex.apply(a.copy(),transpose(T.adjoint()).circuit)for a,T in zip(x,frames)];dy=ex.apply(yl.copy(),transpose(TE.adjoint()).circuit);dkeep=dy.copy()
 for j in range(len(ds)):ex.apply(ds[j],dualmoves[j].circuit)
 ds[pivot]=scale(ds[pivot],1/alpha[pivot])
 for j in range(len(ds)):
  if j!=pivot:ds[j].add(ds[pivot],-alpha[j])
 ds[pivot].add(ex.apply(dy.copy(),dualcopy.circuit),Q(-1))
 for j in reversed(range(len(ds))):
  if j!=pivot:ds[j].add(ds[pivot],alpha[j])
 ds[pivot]=scale(ds[pivot],alpha[pivot]);dualF=transpose(TF.adjoint())
 for j in range(len(ds)):
  exp=x[j].copy();exp.add(yl,-alpha[j]);assert ds[j].same(ex.apply(exp,dualF.circuit))
 assert dy.same(dkeep);fixtures.append(dict(trial=trial,forward_and_inverse_transpose=True))
out=dict(status='PASS_SCOPED_RETIMED_CENTRE_QUERY_NATIVE',centres=[x['center']for x in terms],weights=[str(x)for x in alpha],endpoint_line=E,charged_profile={1:len(terms),8:1},old_profile={1:len(terms),8:1},incremental_recursive_calls=0,scalar_gather_and_undo_adds=2*(len(terms)-1),scalar_scales=2,copy_blocks=1,peak_temporary_streams=1,fixtures=fixtures,scope=__doc__+' Four existing terminal rank-one centre moves are retimed after the seven unchanged zero-endpoint copies and before the new query copy. Their absence from B and early tails is checked. New copy FULL to E has rank8, replacing the old rank8 copy; the other centres and all logical centre outputs are restored. New query has a different dirty response and target endpoint. Retained B is incompatible; complete scatter, dirty compensation, owner/hosting, precision/tape and outer admission remain unproved. No new kappa.',source_sha256=hashlib.sha256((p/'inputs/word-base.json.gz').read_bytes()).hexdigest())
assert json.loads(json.dumps(out))==json.loads((p/'RETIMED-EXPECTED.json').read_text()),'retimed receipt mismatch'
print(out['status'],'incremental recursive calls',out['incremental_recursive_calls'],'NO_NEW_KAPPA',flush=True)
