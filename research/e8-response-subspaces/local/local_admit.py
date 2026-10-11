"""Changed local gauge admission; explicit literal frozen response, dynamic exact charts.
Adapts PR396 symbolic lift and PR376/377 pure label/scalar/splice checks.
No unchanged public pipeline is executed. No global bank or kappa claim.
"""
import os,sys,json,gzip,hashlib,time,copy
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
sys.dont_write_bytecode=True
import argparse
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('candidate',type=Path)
parser.add_argument('output',type=Path)
parser.add_argument('--helper-baseline',type=Path,required=True)
parser.add_argument('--signed-baseline',type=Path,required=True)
parser.add_argument('--deps',type=Path,default=Path(__file__).resolve().parent/'deps')
parser.add_argument('--prior-phase',type=Path,default=Path(__file__).resolve().parent/'prior-phase')
args=parser.parse_args()
CP=args.candidate;OUT=args.output;OUT.mkdir(parents=True,exist_ok=True)
BASE=args.helper_baseline;SIGNED=args.signed_baseline;ROOT=args.deps;PHASE=ROOT/'clifford_exact.py';PRIOR=args.prior_phase
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(gzip.decompress(Path(p).read_bytes()) if Path(p).read_bytes()[:2]==b'\x1f\x8b' else Path(p).read_bytes())
REUSE=PRIOR/'SOURCE-REUSE.json'
inputs=[CP,BASE,SIGNED,REUSE,PHASE,Path(__file__),PRIOR/'CLIFFORD-REVIEW.json',PRIOR/'CLIFFORD-RECIPES.json']+list(ROOT.glob('*.py'))
pins={str(p):sha(p) for p in inputs};t0=time.monotonic();c=read(CP);old=read(BASE);signed=read(SIGNED);v,R,h=c['v'],c['R'],c['h'];n=2*v+R
assert v==120 and R==781 and h==9
headlen=len(c['A'])-len(old['A']);assert headlen>=0 and c['A'][headlen:]==old['A'] and c['B']==signed['B']
baseline=copy.deepcopy(old);baseline['A']=copy.deepcopy(c['A'][:headlen])+baseline['A']
for k in ['frames','start','ext']:baseline[k]=copy.deepcopy(c[k])
assert all(c[k]==old[k] for k in ['h','v','R','cst','ports','ret','scat','final'])
ext=dict(c['ext']);assert len(ext)==len(c['ext']) and all(2*v<=r<n and c['start'][r]==f for r,f in ext.items())
assert all(c['start'][r]==ext.get(r,0) for r in range(2*v,n))
minimal=OUT/'MINIMAL-PINS.json';minimal.write_text(json.dumps(dict(H=h,V=v,R=R,cst=c['cst'],N=c['N'])))
os.environ['CX_PINS']=str(minimal);sys.path.insert(0,str(ROOT));import complex_scalars as C,complex_labels as L,complex_splice as S

def flat(gs):
 result=[]
 for g in gs:
  assert g[0] in ('in','out')
  for r,a,b in g[3]:
   t,s=(r,g[2]) if g[0]=='out' else (g[2],r)
   assert t!=s and not(s>=2*v and t<v)
   assert not(v<=s<2*v) or v<=t<2*v
   result.append((t,s,Q(a,b)))
 return result
A0=C.flat(baseline['A']);B0=C.flat(baseline['B']);A=flat(c['A']);B=flat(c['B'])
helper=lambda xs:[e for e in xs if e[0]<v or e[0]>=2*v]
assert helper(A+B)==helper(A0+B0)
K=list(C.old_positive(A0,B0,baseline))

def raw_operator(z):
 rows=[{i:Q(1)} for i in range(n)];tot=None
 def ax(t,source,q):
  for k,a in list(source.items()):
   x=rows[t].get(k,Q(0))+q*a
   if x:rows[t][k]=x
   else:rows[t].pop(k,None)
 for part in ['A','B']:
  if part=='B':
   tot={k:dict(rows[r]) for k,r,f in z['ret']}
   for t,es in enumerate(z['scat']['table']):
    for k,a,b in es:ax(v+t,tot[k],Q(a,b))
  for t,s,q in flat(z[part]):ax(t,dict(rows[s]),q)
 return rows,tot
actual,tot=raw_operator(c);ref,reftot=raw_operator(baseline);assert actual==ref and tot==reftot
assert all(actual[v+t].get(r,Q(0))==0 for t in range(v) for r in ext)
assert all({k:a for k,a in actual[v+t].items() if v<=k<2*v}=={v+t:Q(1)} for t in range(v))
print('PASS raw all dirty columns; gauged K=0; frozen helper cleanup',n,len(ext),flush=True)

# Guard adaptation is explicit, source-preserving, and has dynamic rank-mass equality.
labeltext=(ROOT/'complex_labels.py').read_text()
labeltext=labeltext.replace('need(c.get("ext")==[], "baseline has no exterior-gauged helper inputs")','ext=dict(c.get("ext",[])); need(len(ext)==len(c.get("ext",[])), "duplicate gauged inputs"); need(all(2*v<=r<n and start_frame==c["start"][r] for r,start_frame in ext.items()), "explicit gauged helper endpoints")')
labeltext=labeltext.replace('need(all(f==0 for f in start[2*v:]) and all(f==1 for f in final[2*v:]), "helper endpoints")','need(all(start[r]==ext.get(r,0) for r in range(2*v,n)) and all(f==1 for f in final[2*v:]), "explicit helper entrance and full final endpoints")')
labeltext=labeltext.replace('mass==c["N"]==R*h+2*v*(h-1)+c["cst"]','mass==c["N"]==R*h+2*v*(h-1)+c["cst"]-sum(dim[f] for f in ext.values())')
assert 'baseline has no exterior-gauged' not in labeltext
ns=dict(L.__dict__);exec(compile(labeltext,'explicit-dynamic-gauge-label-admission','exec'),ns);checks=ns['replay_label_counts'](c)
(OUT/'ADAPTED-LABELS.py').write_text(labeltext)

# Literal scalar schedules: baseline zero-X response, actual main, same helper cleanup.
def initial(symbolic):
 return {('L',i):{(i,'T_%d_inverse'%ext[i] if symbolic and i in ext else 'I'):Q(1)} for i in range(n)}
def apply(reg,e):
 op=e[0]
 if op=='recursive_center':return
 t=e[1]
 if op=='clear':reg[t]={}
 elif op=='copy':reg[t]=dict(reg.get(e[2],{}))
 elif op=='add':
  src=dict(reg.get(e[2],{}));q=Q(e[3],e[4]);row=reg.setdefault(t,{})
  for k,a in src.items():
   z=row.get(k,Q(0))+q*a
   if z:row[k]=z
   else:row.pop(k,None)
 else:raise AssertionError(op)
def expect(symbolic,ori):
 want=initial(symbolic)
 for t in range(v):
  if ori=='forward':want[('L',v+t)][(t,'I')]=Q(1)
  else:want[('L',t)][(v+t,'I')]=Q(-1)
 return want
words={};bills={};scalar={}
for ori in ['forward','backward']:
 seq=[(p,e) for p,es in [('old_response',C.old_word(ori,K)),('main',C.main_scalar(ori,A,B,c)),('cleanup',C.cleanup(ori,A0+B0))] for e in es]
 life=C.lifecycle(seq,c);bills[ori]=C.bill(seq)
 for symbolic in [False,True]:
  g=initial(symbolic)
  if symbolic:
   # Physical I-chart old response precedes entrance normalization.
   pre=initial(False)
   for e in C.old_word(ori,K):apply(pre,e)
   for i in range(n):
    if i in ext:assert pre[('L',i)]=={(i,'I'):Q(1)}
    else:g[('L',i)]=dict(pre[('L',i)])
   for e in list(C.main_scalar(ori,A,B,c))+list(C.cleanup(ori,A0+B0)):apply(g,e)
  else:
   for p,e in seq:apply(g,e)
  want=expect(symbolic,ori)
  assert all(g[k]==row for k,row in want.items()),(ori,symbolic,next((k for k in want if g[k]!=want[k]),None))
  assert all(not row for k,row in g.items() if k[0]!='L')
 words[ori]=seq;scalar[ori]=dict(independent_live_columns=n,dirty_helpers=R,symbolic_distinct_entrance_tokens=['I']+['T_%d_inverse'%f for f in sorted(set(ext.values()))],normalized_helper_endpoint_unchanged=True,private_work_erased=True,lifecycle=life)
 print('PASS both charts scalar orientation',ori,bills[ori]['totals']['real_component_primitive_steps'],flush=True)

# Emit actual label walk, retaining frozen baseline old response and exact original cleanup.
emittext=(ROOT/'complex_splice.py').read_text();emittext=emittext[emittext.index('def emit(c,ori):'):emittext.index('def contains(U,V):')]
a=emittext.index('    K=[]');b=emittext.index("    yield ('phase','old_response')",a);emittext=emittext[:a]+'    K=list(FROZEN_K)\n'+emittext[b:]
ns=dict(S.__dict__,flat=flat,FROZEN_K=K);exec(compile(emittext,'literal-frozen-nonY-response-gauge-main','exec'),ns);emitter=ns['emit']
programs={};local={}
for ori in ['forward','backward']:
 ev=list(emitter(c,ori));local[ori]=S.validate(ev,c,ori,{'checks':checks},bills);local[ori]['mutation_controls']=S.controls(ev,c,ori,{'checks':checks},bills);programs[ori]=ev
 print('PASS emitted frames, scalar projection, lifetimes',ori,flush=True)
(OUT/'ADAPTED-EMITTER.py').write_text(emittext)
# Exact algebraic omission controls for every unit entrance gate.
original,_=raw_operator(old);head=c['A'][:headlen];head_targets={t for t,s,q in flat(head)};head_sources={s for t,s,q in flat(head)}
assert not head_targets&head_sources and head_sources==set(ext)
controls=[]
for gi,g in enumerate(head):
 for t,s,q in flat([g]):
  leak=[-q*original[v+i].get(t,Q(0)) for i in range(v)]
  assert any(leak),'zero-response donor omission is not a valid control'
  controls.append(dict(group=gi,target=t,gauged_source=s,nonzero_Y_coordinates=sum(bool(a) for a in leak),one_nonzero_coefficient=str(next(a for a in leak if a))))
# Fully execute a changed scalar schedule for sampled first/last controls.
for gi in sorted(set([0,headlen//2,headlen-1])):
 bad=copy.deepcopy(c);bad['A'][gi][3].pop(0);badA=flat(bad['A']);g=initial(True);pre=initial(False)
 for e in C.old_word('forward',K):apply(pre,e)
 for i in range(v,2*v):g[('L',i)]=dict(pre[('L',i)])
 for e in list(C.main_scalar('forward',badA,B,bad))+list(C.cleanup('forward',A0+B0)):apply(g,e)
 assert any(g[('L',i)]!=expect(True,'forward')[('L',i)] for i in range(v,2*v))

# New/reflected exact phase pairs only; unchanged pairs retain pinned prior recipes.
sys.path.insert(0,str(PHASE.parent));import clifford_exact as X
priorreview=read(PRIOR/'CLIFFORD-REVIEW.json');priorrecipes=read(PRIOR/'CLIFFORD-RECIPES.json')
assert priorreview['status']=='PASS_EXACT_GAUSSIAN_CLIFFORD_LOCAL_FRAMES_AND_CHILDREN' and priorreview['all_child_equalities_include_global_phase']
reuse=read(REUSE)
canonical=lambda z:hashlib.sha256(json.dumps(z,sort_keys=True,separators=(',',':')).encode()).hexdigest()
assert canonical(signed)==reuse['signed_baseline_canonical_sha256'] and canonical(old)==reuse['helper_baseline_canonical_sha256']
assert priorreview['certificate_sha256']==reuse['phase_audited_certificate_gzip_sha256']
assert pins[str(PRIOR/'CLIFFORD-REVIEW.json')]==reuse['prior_review_sha256'] and pins[str(PRIOR/'CLIFFORD-RECIPES.json')]==reuse['prior_recipes_sha256']
assert pins[str(PHASE)]==reuse['engine_sha256']
assert priorreview['engine_sha256']==pins[str(PHASE)]
assert priorreview['recipe_sha256']==sha(PRIOR/'CLIFFORD-RECIPES.json')
oldpairs={(tuple(signed['frames'][a['old']]),tuple(signed['frames'][a['new']])) for a in priorrecipes['children']}
newpairs=set()
for ori,events in programs.items():
 for e in events:
  if e[0]=='climb':a,b=e[3:5]
  elif e[0]=='center':a,b=e[2:4]
  else:continue
  pair=tuple(c['frames'][a]),tuple(c['frames'][b])
  if pair not in oldpairs:newpairs.add(pair)
newpairs|={(b,a) for a,b in newpairs};recipes=[];cache={}
def canonical(basis):
 if basis not in cache:cache[basis]=X.canonical_frame(h,list(basis))
 return cache[basis]
for a,b in sorted(newpairs):
 op=canonical(a).adjoint().then(canonical(b));rec,compiled=X.lower_child(op)
 assert rec['rank']==abs(len(a)-len(b)) and compiled.tab==op.tab and compiled.zero_state()==op.zero_state()
 recipes.append(dict(old_basis=a,new_basis=b,**rec))
entrycharts={}
for f in sorted(set(ext.values())):
 basis=tuple(c['frames'][f]);TE=canonical(basis);entry=TE.adjoint().then(TE);rec,compiled=X.lower_child(entry)
 assert rec['rank']==0 and compiled.tab==X.ident(h).tab and compiled.zero_state()==X.ident(h).zero_state()
 entrycharts[str(f)]=dict(basis=basis,formal_normalized_input_token='T_%d_inverse'%f,physical_initial_chart='T_%d'%f,entry_adapter_rank=0,entry_recipe=rec,endpoint_residual='F*T_%d_inverse'%f,endpoint_residual_owner='architecture two-sided bank normalization receipt required')
 print('PASS entry exact Gaussian chart identity',f,flush=True)
(OUT/'NEW-PHASE-RECIPES.json').write_text(json.dumps(recipes,sort_keys=True,separators=(',',':')))
(OUT/'ENTRY-CHARTS.json').write_text(json.dumps(entrycharts,indent=2))
raw=json.dumps(dict(candidate_sha256=pins[str(CP)],local_programs=programs,bills=bills,checks=checks,local_profile=checks['invocation_histogram'],entry_charts=entrycharts),sort_keys=True,separators=(',',':')).encode();(OUT/'LOCAL-PROGRAMS.json.gz').write_bytes(gzip.compress(raw,mtime=0))
assert pins=={p:sha(p) for p in pins}
result=dict(status='PASS_CHANGED_GAUGE_LOCAL_RAW_DIRTY_SYMBOLIC_BOTH_ORIENTATIONS_FRAMES_LIFETIMES_AND_NEW_PHASES',candidate_sha256=pins[str(CP)],helper_baseline_sha256=pins[str(BASE)],gauges=len(ext),entrance_frames=len(entrycharts),entrance_rankmass=sum(len(c['frames'][f]) for f in ext.values()),unit_entrance_gates=headlen,all_raw_columns=n,raw_operator_equals_same_entrance_nonY_baseline=True,gauged_K_columns_zero=True,helper_cleanup_subword_equal=True,scalar_checks=scalar,checks=checks,local_checks=local,bills=bills,new_and_reflected_exact_phase_pairs=len(recipes),reused_pinned_old_phase_pairs=len(oldpairs),all_new_phase_equalities_include_Gaussian_global_phase=True,entrance_omission_algebraic_controls=controls,sampled_full_symbolic_omission_controls=len(set([0,headlen//2,headlen-1])),local_programs_uncompressed_sha256=hashlib.sha256(raw).hexdigest(),new_phase_recipes_sha256=sha(OUT/'NEW-PHASE-RECIPES.json'),entry_charts_sha256=sha(OUT/'ENTRY-CHARTS.json'),source_hashes=pins,seconds=time.monotonic()-t0,scope='Changed finite local normalization and explicit main/response/cleanup, both orientations and independent formal entrance operators. Requires architecture exact two-sided residual/global bank/owner/phase integration and root price/outer assembly; inherited all-size contracts remain conditional. No new kappa or Lean theorem claim.')
(OUT/'RESULT.json').write_text(json.dumps(result,indent=2));print(result['status'],'gauges',len(ext),'phases',len(recipes),'seconds',result['seconds'],flush=True)
