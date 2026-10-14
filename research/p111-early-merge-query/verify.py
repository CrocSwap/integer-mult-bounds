"""Audit one early-merge query tree and a favorable complete-volume screen.
No native/owner admission or kappa follows from this optimistic calculation.
"""
import ast,gzip,json,importlib.util,hashlib
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
from decimal import Decimal,localcontext
p=Path(__file__).resolve().parent;root=p.parent
assert __debug__, 'Run with assertions enabled'
for name,h in json.loads((p/'MANIFEST.json').read_text()).items():
 assert hashlib.sha256((p/name).read_bytes()).hexdigest()==h, ('source pin',name)
spec=importlib.util.spec_from_file_location('price',p/'vendor/pr1134_verify.py');price=importlib.util.module_from_spec(spec);spec.loader.exec_module(price)
w=json.loads(gzip.decompress((p/'inputs/word-base.json.gz').read_bytes()));seed=json.loads((p/'SEED.json').read_text());tree=json.loads((p/'TREE.json').read_text());v=112;n=2*v+w['report']['R'];b=seed['puncture'];m=len(seed['chosen']);S=price.span
# Replay arbitrary input and dirty columns to every copied row.
rows=[{i:Q(1)}for i in range(n)];leaves={};by_event={x['after_A_event']:(j,x)for j,x in enumerate(seed['chosen'])};assert len(by_event)==m
for k,e in enumerate(w['precondition']+w['A']):
 t=e[1]
 if e[0]=='add':price.add_row(rows[t],Q(e[3],e[4]),rows[e[2]])
 else:rows[t]={i:x*Q(e[2],e[3])for i,x in rows[t].items()}
 event=k-len(w['precondition'])
 if event in by_event:
  j,c=by_event[event];scale=Q(c['coefficient'])/Q(c['normalization']);leaves[1<<j]=dict(frame=tuple(c['frame']),row={i:scale*x for i,x in rows[c['register']].items()},ready=event)
assert len(leaves)==m
# Every captured value and frame remains unchanged through the end of A.
for j,c in enumerate(seed['chosen']):
 assert rows[c['register']]=={i:x/(Q(c['coefficient'])/Q(c['normalization']))for i,x in leaves[1<<j]['row'].items()}
 for e in w['A'][c['after_A_event']+1:]:
  assert e[1]!=c['register']
  if c['register'] in price.operands(e):assert S(tuple(e[-1]))==S(tuple(c['frame']))
children={s:(a,b,r)for s,a,b,r in tree['tree']};nodes=dict(leaves);hist=Counter();events=[]
def visit(s):
 if s in nodes:return nodes[s]
 a,b,r=children[s];left=visit(a);right=visit(b);U=price.basis(left['frame']+right['frame']);assert len(U)==r and S(left['frame'])<=S(U)and S(right['frame'])<=S(U)
 for node in [left,right]:
  delta=len(U)-len(price.basis(node['frame']))
  if delta:hist[delta]+=1
 row=dict(left['row']);price.add_row(row,Q(1),right['row']);ready=max(left['ready'],right['ready']);nodes[s]=dict(frame=U,row=row,ready=ready);events.append(dict(mask=s,left=a,right=b,ready=ready,frame=list(U)));return nodes[s]
result=visit((1<<m)-1);H=price.basis(x for x in range(512)if not (x&w['ports'][b]).bit_count()%2);assert S(result['frame'])==S(H)
query={i:Q(sum(x*y for x,y in zip(w['root_lines'][b],w['root_lines'][i])),2)for i in range(v)if i!=b};query={i:x for i,x in query.items()if x};clean={i:x for i,x in result['row'].items()if i<v};assert clean==query
rank_mass=sum(r*c for r,c in hist.items());assert rank_mass==tree['internal_rank_sum']+8-sum(len(x['frame'])for x in seed['chosen'])==39
dirt={i:x for i,x in result['row'].items()if i>=v};nonzero_initial_frames=[i for i in dirt if w['start_extra'].get(str(i),[])]
# Eager chronological merge evaluation; copies leave original registers unchanged.
live=set();peak=0;pending=dict(children)
for j,c in sorted(enumerate(seed['chosen']),key=lambda q:q[1]['after_A_event']):
 live.add(1<<j);peak=max(peak,len(live));changed=True
 while changed:
  changed=False
  for s,(a,z,r)in list(pending.items()):
   if a in live and z in live:live.remove(a);live.remove(z);live.add(s);del pending[s];changed=True
assert live=={(1<<m)-1}and not pending
# Independently recount actual source/target climbs in the current base word.
start=[(x,)for x in w['ports']]+[()for _ in range(n-v)]
for i,U in w['start_extra'].items():start[int(i)]=tuple(U)
cur=list(start);role=[Counter()for _ in range(n)];paid=Counter()
def climb(i,U):
 U=price.basis(U);assert S(cur[i])<=S(U);d=len(U)-len(cur[i]);cur[i]=U
 if d:role[i][d]+=1;paid[d]+=1
for sec in ['A','B']:
 for e in w[sec]:
  for i in price.operands(e):climb(i,e[-1])
for index,U in w['early_cleanup']:
 for i in price.operands(w['cleanup'][index]):climb(i,U)
full=price.basis(range(1,512));ends=[full]*v+[price.basis(x for x in range(512)if not (x&port).bit_count()%2)for port in w['ports']]+[full]*w['report']['R']
for i,U in w['helper_final'].items():ends[int(i)]=price.basis(U)
for i,U in enumerate(ends):climb(i,U)
paid[8]+=8;assert paid==Counter({int(k):x for k,x in w['report']['local_profile'].items()})
removed=role[b]+role[v+b];assert sum(r*c for r,c in removed.items())==16
profile=paid.copy();profile.subtract(removed);profile[8]-=1;profile[7]+=1;profile.update(hist);assert all(x>=0 for x in profile.values())
width_mass=sum(len(ends[i])-len(start[i])for i in range(2*v,n));idle=111*(6*8+4*(16+32+48))-9*(width_mass+rank_mass);assert idle>=0
exponent=Q(json.loads((p/'BASELINE.json').read_text())['complex_lower']);lo,hi=price.moment(profile,idle,exponent)
out=dict(status='PASS_EXACT_QUERY_TREE_SCALAR_FRAMES_AND_FAVORABLE_SCREEN',puncture=b,transport_profile=dict(hist),transport_rank=rank_mass,direct_transport_rank=seed['optimistic_transport_rank'],copies=m,merges=len(events),peak_temporary_streams=peak,dirty_columns=len(dirt),dirty_coefficients={str(i):str(x)for i,x in dirt.items()},dirty_columns_with_nonzero_initial_frames=nonzero_initial_frames,tree_events=events,removed_data_profile=dict(removed),local_profile=dict(profile),old_helper_width_mass=width_mass,relaxed_idle_mass=idle,endpoint=str(exponent),optimistic_moment_lower=str(lo),optimistic_moment_upper=str(hi),optimistic_moment_display=price.show((lo+hi)/2),scope='Exact merged query on current base-word prefix rows, including arbitrary dirty coefficients and literal containing frames. Original streams untouched; all temporary allocations and final physical disposal require admission. Favorable screen deletes original puncture paths and one COPY rank, grants compensation/initial frames/host packing free; not a realizable global assembly, exact lower bound for other trees, or kappa claim.')
assert json.loads(json.dumps(out))==json.loads((p/'EXPECTED.json').read_text()), 'receipt mismatch'
print('PASS_SCOPED_EARLY_MERGE_QUERY rank=39 direct=86 exact_clean_and_dirty_columns; NO_NEW_KAPPA')
print(out['optimistic_moment_display'])
