"""Portable additive PR390 heterogeneous-bank admission on ordinary R781.

Usage: python -B hetero_replay.py PR390 COMPLEX_REPLAY SIGNED_REPLAY BASELINE BIT_PARENT OUT
Requires the exact generated leaf-source input inventory, a fresh ordinary prefix replay,
the corrected fresh signed bit replay, and unchanged assembly packages.
Prepared with OpenAI Codex assistance. Apache-2.0; inherited notices apply.
"""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
import argparse,copy,gzip,hashlib,importlib.util,io,json,math,os,re,subprocess,sys
assert __debug__ and sys.version_info>=(3,12)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def unzip(p):return json.loads(gzip.decompress(Path(p).read_bytes()))
def write(p,x):Path(p).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def load(name,p):
 spec=importlib.util.spec_from_file_location(name,p);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod
def gz(raw):
 from transport import deterministic_gzip
 return deterministic_gzip(raw)

def contains(U,V):
 for u in U:
  for v in V:
   if u>>(v.bit_length()-1)&1:u^=v
  if u:return False
 return True
def apply(row,t,s,q):
 assert t!=s
 for k,v in list(row[s].items()):
  z=row[t].get(k,Q(0))+q*v
  if z:row[t][k]=z
  else:row[t].pop(k,None)
def generate(c,original_audit):
 n=2*c['v']+c['R'];v=c['v'];fs=c['frames'];groups=c['A']+c['B'];cuts={};accepted=[]
 for old in original_audit['accepted']:
  a=copy.deepcopy(old);r=a['sink_helper'];last=max(i for i,g in enumerate(groups)if r in [g[2]]+[z[0]for z in g[3]]+(g[4]if g[0]=='out'else[]))
  assert groups[last][1]==a['frame'] and len(fs[a['frame']])==8
  a['cut_group']=last;cuts[last]=a;accepted.append(a)
 endpoints=c['final'][:]
 for a in accepted:endpoints[a['sink_helper']]=a['frame']
 cur=c['start'][:];hist=Counter();main=[];gi=0
 def climb(r,f):
  old=cur[r]
  if old==f:return
  assert len(fs[old])<len(fs[f]) and contains(fs[old],fs[f]),(r,old,f)
  hist[len(fs[f])-len(fs[old])]+=1;cur[r]=f
 for phase in ['A','centers','B']:
  if phase=='centers':
   for k,r,f in c['ret']:hist[len(fs[f])]+=1
   for t,rr in enumerate(c['scat']['table']):
    for k,a,b in rr:main.append((v+t,c['ret'][k][1],Q(a,b)))
   continue
  for g in c[phase]:
   for r in [g[2]]+[z[0]for z in g[3]]+(g[4]if g[0]=='out'else[]):climb(r,g[1])
   for r,a,b in g[3]:
    t,s=(r,g[2])if g[0]=='out'else(g[2],r);main.append((t,s,Q(a,b)))
   if gi in cuts:
    a=cuts[gi];r=a['sink_helper'];f=a['frame']
    for q in [r]+[z[0]for z in a['uncompute']]:climb(q,f)
    for q,num,den in a['uncompute']:main.append((r,q,Q(num,den)))
   gi+=1
 for r,f in enumerate(endpoints):climb(r,f)
 rows=[{i:Q(1)}for i in range(n)]
 for t,s,q in main:
  assert t>=v and not(v<=s<2*v)or(v<=t<2*v and v<=s<2*v)
  apply(rows,t,s,q)
 assert all(rows[i]=={i:Q(1)}for i in range(v))
 for t in range(v,2*v):assert {j:q for j,q in rows[t].items()if v<=j<2*v}=={t:Q(1)}
 sinks={a['sink_helper']for a in accepted}
 assert all(not any(j<v for j in rows[r])for r in sinks)
 prehelper=[(t,s,-q)for t,s,q in reversed(main)if t>=2*v and s>=2*v]
 pre_rows=[{i:Q(1)}for i in range(n)]
 for t,s,q in prehelper:apply(pre_rows,t,s,q)
 for t,s,q in main:apply(pre_rows,t,s,q)
 for r in range(2*v,n):assert {j:q for j,q in pre_rows[r].items()if j>=2*v}=={r:Q(1)}
 pretarget=[(t,s,-q)for t in range(v,2*v)for s,q in sorted(pre_rows[t].items())if s>=2*v]
 repair=[(r,s,-q)for r in range(2*v,n)for s,q in sorted(rows[r].items())if s<v]
 assert all(r not in sinks for r,s,q in repair)
 def enc(seq):return [[t,s,q.numerator,q.denominator]for t,s,q in seq]
 pre=dict(status=f'PASS_EXACT_{n}_COLUMN_ABSTRACT_FORWARD_HETEROGENEOUS_DIRTY_DECODER',n=n,sinks=sorted(sinks),
  pre_target_dirty_cancellation_gates=enc(pretarget),pre_helper_inverse_gates=enc(prehelper),
  post_source_inverse_gates=[],post_full_helper_clean_repair_gates=enc(repair),
  main_gates=len(main),scope='Explicitly regenerated rational pre/post scalar witness; full chronological phases, bank owners and finite invoice require separate admission.')
 final=[{i:Q(1)}for i in range(n)]
 for t,s,q in pretarget+prehelper+main+repair:apply(final,t,s,q)
 for r in range(n):
  want={r:Q(1)}
  if v<=r<2*v:want[r-v]=Q(1)
  assert final[r]==want,(r,final[r],want)
 oldH=Counter()
 for block in c['blocks'].values():oldH.update({int(k):v for k,v in block.items()})
 delta={k:hist[k]-oldH[k]for k in hist.keys()|oldH.keys()if hist[k]!=oldH[k]}
 audit=dict(accepted=accepted,local_histogram_delta=delta,local_mass_delta=sum(k*v for k,v in delta.items()),
  new_helper_endpoint_dimensions=sorted(Counter(len(fs[endpoints[r]])for r in range(2*v,n)).items()),
  exact_columns=n,source_rows_identity=True,all_target_and_helper_dirty_columns_restored=True,
  pre_target_count=len(pretarget),pre_helper_count=len(prehelper),post_repair_count=len(repair))
 return pre,audit

def bind(HERE,PR,ORD,SIGNED,BASELINE,BIT_PARENT):
 OUT=HERE/'full';NATIVE=ORD/'work/complex-nine-native'
 ENG=PR/'public/381/source/research/e8-nine-stage-kappa/complex377/work/pr361/code/engines'
 def label(p):
  for base,name in [(ORD,'ordinary'),(SIGNED,'signed'),(HERE,'extension'),(PR,'pr390')]:
   if p.is_relative_to(base):return name+'/'+p.relative_to(base).as_posix()
  raise AssertionError('unlabelled binding')
 candidate=read(HERE/'candidate.json');verified=read(ORD/'VERIFICATION.json')
 assert verified['candidate_sha256']==sha(HERE/'candidate.json')==sha(ORD/'candidate.json')=='468460de3bb2ebf6c89b3156fdd332623596f7f6ae74324362862324cf71a98c'
 assert verified['status']=='PASS_SOURCE_BOUND_PR390_PREFIX_TWO_ALIAS_TWO_FRAMES_ORDINARY_NINE_STAGE'
 assert len(verified['stages'])==10
 if len(verified['stages'])==10:
  assert read(ORD/'EXTENSION.json')['status']=='PASS_MAIN_ONLY_TARGET_READ_EXTENSION_CONTROLS'
 for stage in verified['stages']:assert sha(ORD/'logs'/(stage['stage']+'.log'))==stage['log_sha256']
 assert sha(ORD/'SOURCE-DIFFS.json')==verified['source_diffs_sha256']
 phase_review=read(NATIVE/'CLIFFORD-REVIEW.json');recipes=read(NATIVE/'CLIFFORD-RECIPES.json')
 assert phase_review['frames']==950 and phase_review['all_child_equalities_include_global_phase']
 assert phase_review['recipe_sha256']==sha(NATIVE/'CLIFFORD-RECIPES.json')
 ordinary=unzip(NATIVE/'GLOBAL-TEMPLATE.json.gz')
 assert ordinary['exact_data_phase_recipe_sha256']==sha(NATIVE/'DATA-PHASES.json')
 assert read(NATIVE/'local-admission/UPSTREAM-GUARD.json')['precision_guard']['semantic_C1']==1
 local=unzip(OUT/'hetero/HETEROGENEOUS-TEMPLATE.json.gz');global_template=unzip(OUT/'hetero/GLOBAL-HETEROGENEOUS-TEMPLATE.json.gz')
 global_review=read(OUT/'hetero/GLOBAL-HETEROGENEOUS-RECEIPT.json');bill=read(OUT/'hetero/RESULT.json');bank=read(OUT/'HETEROBANKS.json');bankreview=read(OUT/'BANK-REVIEW.json');endpoints=read(OUT/'hetero/BANK-ENDPOINT-PHASE.json')
 rawglobal=gzip.decompress((OUT/'hetero/GLOBAL-HETEROGENEOUS-TEMPLATE.json.gz').read_bytes())
 assert hashlib.sha256(rawglobal).hexdigest()==global_review['template_sha256']
 phase={(x['old'],x['new']):x for x in recipes['children']}
 for x in local['new_phase_recipes']:
  key=x['old'],x['new']
  if key in phase:assert phase[key]==x
  phase[key]=x
 local_hist={};used=set()
 for orientation,events in local['local_programs'].items():
  H=Counter()
  for e in events:
   if e[0]=='climb':old,new,rank=e[3],e[4],e[5]
   elif e[0]=='center':old,new,rank=e[2],e[3],e[4]
   else:continue
   assert (old,new)in phase and phase[old,new]['rank']==rank
   used.add((old,new));H[rank]+=1
  local_hist[orientation]=H
  assert H==Counter({int(k):v for k,v in bill['local_profile'].items()})
  assert 2*len(local['lowered_scalar_programs'][orientation])==bill['physical_checks'][orientation]['real_component_primitive_upper']==165628
  assert bill['physical_checks'][orientation]['independent_live_columns']==1021
  assert bill['physical_checks'][orientation]['all_private_restored_zero']
 assert local_hist['forward']==local_hist['backward']
 H=Counter();calls=global_template['calls'];assert len(calls)==288
 for call in calls:
  assert len(call['owners'])==1021
  H.update(local_hist[call['orientation']])
 assert global_template['recipe']==ordinary['recipe']
 for idle in ordinary['idle_children']:
  assert idle['replicas']==8
  H[idle['rank']]+=32
 assert len(global_template['bank_padding'])==28035
 for pad in global_template['bank_padding']:assert pad['rank']==1;H[1]+=1
 assert H==Counter({int(k):v for k,v in bill['profile'].items()})
 assert sum(H.values())==bill['paid_calls']==1236771
 assert sum(k*v for k,v in H.items())==bill['rank_mass']==4284387
 m,stock,physical=73,58827,59618
 assert bill['live']==bank['live']==stock and bill['physical']==physical and m*stock-bill['rank_mass']==9984
 assert len(bank['assignments'])==32*781==bankreview['assignments']
 assert bankreview['stage_replica_pair_owner_checks']==9*32*4
 assert len(endpoints['endpoints'])==2 and len(local['new_phase_recipes'])==4
 assert global_template['cover_final_correction']['charged_calls']==stock
 assert global_review['endpoint_adapters']==576
 pg=bill['invoice'];group=2**1296*math.prod(2**(2*i)-1 for i in range(1,37));physical_stock=group*physical
 assert pg['physical_stock_bits']==physical_stock.bit_length()==2644
 assert pg['physical_row_coefficient']==2*physical_stock.bit_length()+9909+252==15449<20161
 assert pg['halving_degree']==2 and m*m>2*max(H)**2
 assert pg['induction_gap_multiple_B']==2*(m-max(H))-1==49
 assert pg['router_bits']<30000 and pg['literal_bits']<100000 and pg['required_C0_bits']<210000
 M=load('hetero_bound_moment',ENG/'moment.py');B=load('hetero_bound_other',ENG/'base_two_moment.py')
 b=Q(bill['coarse']);assert b==Q(501324526735289,5*10**17)
 fallback=32*m*m*sum(H.values());bounds=[]
 for x in [b,b+Q(1,10**18)]:
  a=M.moment(H,m,stock,x,True);lo,hi=B.moment(m,stock,list(H.items()),x);bl,bh=B.moment(m,stock,[(1,fallback)],x)
  independent=(lo+Q(1,10**16)*bl,hi+Q(1,10**16)*bh)
  bounds.append(dict(saving=str(x),original=list(map(str,a)),independent=list(map(str,independent))))
 assert Q(bounds[0]['original'][1])<1<Q(bounds[1]['original'][0])
 assert Q(bounds[0]['independent'][1])<1<Q(bounds[1]['independent'][0])
 bindings=[ORD/'VERIFICATION.json',ORD/'SOURCE-DIFFS.json',NATIVE/'CLIFFORD-REVIEW.json',NATIVE/'CLIFFORD-RECIPES.json',NATIVE/'DATA-PHASES.json',HERE/'ADAPTATION.json',HERE/'GENERATION.json',OUT/'RESULT.json',OUT/'hetero/RESULT.json',OUT/'hetero/HETEROGENEOUS-TEMPLATE.json.gz',OUT/'hetero/BANK-ENDPOINT-PHASE.json',OUT/'hetero/GLOBAL-HETEROGENEOUS-RECEIPT.json',OUT/'HETEROBANKS.json',OUT/'BANK-REVIEW.json']
 supplier=dict(status='PASS_FRESH_NINE_STAGE_COMPLEX_INTERFACE',b=str(b),m=m,W=stock,histogram=H,bounds=bounds,
  template_sha256=global_review['template_sha256'],finite_invoice=pg,semantic_C1=1,
  candidate_sha256=sha(HERE/'candidate.json'),complete_local_phase_edges=len(used),new_local_phase_edges=4,
  source_hashes={label(p):sha(p)for p in bindings},
  scope='Finite research composition of PR390 prefix/heterogeneous restoration with independently admitted R781 aliases and two frames. Exact phases combine fresh ordinary950frame recipes and4 freshly checked donor transitions plus both endpoint adapters. Inherits sufficient target-to-target/unequal endpoint dirty compiler extension and all-size local, compressed-window, correlated-bank, complete-stream, precision/recovery, row and analytic interfaces. Not a new Lean theorem.')
 write(HERE/'COMPLEX-SUPPLIER.json',supplier)
 signed=read(SIGNED/'RECEIPT.json');assert signed['status']=='PASS_FULL_FRESH_COMPOSITION_AND_SIGNED_BIT_SUPPLEMENT'
 priced=read(SIGNED/'composition/baseline/replay/unsplit-bit/kappa-input.json');finite=read(SIGNED/'validation/FINITE.json')
 assert finite['coefficient']==56223565818967 and finite['payload_prefix_bits']==71
 assembly=load('hetero_outer',BASELINE/'assembly.py').run(BIT_PARENT,priced,finite,supplier)
 write(HERE/'ASSEMBLY.json',assembly)
 receipt=dict(status='PASS_BOUND_HETEROGENEOUS_COMPLEX_AND_VERIFIED_SIGNED_SEVEN_STAGE_BIT_RESEARCH_COMPOSITION',
  complex_b=str(b),bit_c=priced['bit_coarse'],kappa=assembly['kappa'],binding=assembly['binding'],
  complex_supplier_sha256=sha(HERE/'COMPLEX-SUPPLIER.json'),assembly_sha256=sha(HERE/'ASSEMBLY.json'),
  signed_bit_receipt_sha256=sha(SIGNED/'RECEIPT.json'),ordinary_base_verification_sha256=sha(ORD/'VERIFICATION.json'),
  same_raw_candidate_as_ordinary=True,source_files_unchanged=True,
  scope='Both exact moment engines, fallbacks, adjacent-grid controls,8 finite continuations and47 outer strict constraints execute freshly. Retains all documented conditional interfaces and counted-C_full qualification.')
 write(HERE/'COMPOSITION-RECEIPT.json',receipt);print(receipt['status'],receipt['kappa'],float(Q(receipt['kappa'])));return receipt

PINS={
 'complex-hetero-compose.py':('f8320faafc3e08b829d85a583cc34bec6e0578368ae4411200724a79a6899b30','52692efb9d75ddc5848064677609caadf5f7ef32b3c33fa9c2d623cf91b13540'),
 'complex-bank-phase.py':('1d44489885d458a667448d0064e3d83071424d2e17c4460a76dbf379be1395db','b8a6203055813c15d0cdda38b00b2870658d8518cc8d48a4601c54bcc9a8a2ae'),
 'root-heterobanks.cpp':('adede905249e1d6c6de1d774f51344c9e8391091beedb2c3c90b4c079881fe3a','767f8bcb2f25b7e86f4093fa4ee57490eb14cbce566c94507524f1e1b8a1cd70'),
 'bit-heterobank-review.py':('d6a9ee5e1a7695facd9962de006b8e4c5422fffc6bb6bd7cdebff908711f22a8','8efd3467791d91691e64fa3afe44ee45aa1e88fb0b6a3b03f9e0fad7090c4bc1'),
 'root-global.py':('6a534ba1de6a49470687e80ce5e4243021aed5a289429187eae676ca9d65cfeb','2c3a26de4bc68fd70bbb507e37d379471cc290d256d574347ad0efb683635edc')}
MAPPING={783:781,1023:1021,3131:3123,3123:3115,58899:58827,59692:59618,58898:58826,28107:28035}
CANDIDATE='468460de3bb2ebf6c89b3156fdd332623596f7f6ae74324362862324cf71a98c'
def manifest(pr):
 mf=pr/'INPUTS.json';wanted=read(mf)['files']
 assert read(mf)['status']=='PASS_EXACT_SOURCE_LEAVES_AND_CANONICAL_REGENERATED_PREWHITE'
 assert not any(p.is_symlink()for p in pr.rglob('*'))
 actual={p.relative_to(pr).as_posix():sha(p)for p in pr.rglob('*')if p.is_file()and p!=mf}
 assert actual==wanted,'Missing, changed or unlisted generated input'
 return sha(mf)

def main():
 parser=argparse.ArgumentParser(description=__doc__)
 for name in ['pr390','complex_replay','signed_replay','baseline','bit_parent','output']:parser.add_argument(name,type=Path)
 a=parser.parse_args();PR,ORD,SIGNED,BASELINE,BIT_PARENT,HERE=[getattr(a,name).resolve()for name in ['pr390','complex_replay','signed_replay','baseline','bit_parent','output']]
 assert not HERE.exists()
 for source in [PR,ORD,SIGNED,BASELINE,BIT_PARENT]:assert source.is_dir()and not HERE.is_relative_to(source)
 for p in [HERE,PR,ORD,SIGNED,BASELINE,BIT_PARENT,Path(sys.executable).resolve()]:assert not any(c.isspace()for c in str(p))
 source_manifest=manifest(PR)
 assert sha(BASELINE/'assembly.py')=='fe545811e9e858c9ca616d64f3348b797319a51f1dfa8097588ab117bf78e82c'
 verified=read(ORD/'VERIFICATION.json')
 assert verified['candidate_sha256']==sha(ORD/'candidate.json')==CANDIDATE
 assert read(SIGNED/'RECEIPT.json')['status']=='PASS_FULL_FRESH_COMPOSITION_AND_SIGNED_BIT_SUPPLEMENT'
 HERE.mkdir(parents=True);(HERE/'code').mkdir();OUT=HERE/'full';OUT.mkdir()
 before={str(p):sha(p)for p in [ORD/'VERIFICATION.json',ORD/'SOURCE-DIFFS.json',ORD/'candidate.json',SIGNED/'RECEIPT.json',BASELINE/'assembly.py']}
 old=unzip(PR/'data/prefix18.json.gz');original_audit=read(PR/'data/sink-audit.json')
 original_pre,original_check=generate(old,original_audit);frozen_pre=read(PR/'data/prewhite.json')
 for key in ['pre_target_dirty_cancellation_gates','pre_helper_inverse_gates','post_source_inverse_gates','post_full_helper_clean_repair_gates']:assert original_pre[key]==frozen_pre[key]
 assert [x['cut_group']for x in original_check['accepted']]==[x['cut_group']for x in original_audit['accepted']]
 raw=(ORD/'candidate.json').read_bytes();c=json.loads(raw);pre,audit=generate(c,original_audit)
 (HERE/'candidate.json').write_bytes(raw);(HERE/'candidate.json.gz').write_bytes(gz(raw))
 write(HERE/'prewhite.json',pre);write(HERE/'sink-audit.json',audit)
 write(HERE/'GENERATION.json',dict(status='PASS_EXACT_REGENERATED_R781_PRECONDITIONER_AND_SINK_FRAME_WALK_ONLY',candidate_sha256=CANDIDATE,
  baseline_regeneration_matches_all_four_literal_prepost_lists=True,upstream_commit='0e790f2dfb64e17bdee154aee151bb0c1dddb28e',audit=audit,
  source_hashes={name:sha(PR/name)for name in ['data/prefix18.json.gz','data/prewhite.json','data/sink-audit.json']},
  output_hashes={name:sha(HERE/name)for name in ['candidate.json','candidate.json.gz','prewhite.json','sink-audit.json']}))
 pattern=re.compile(r'(?<!\d)('+('|'.join(map(str,MAPPING)))+r')(?!\d)');files={}
 for name,(oldhash,newhash)in PINS.items():
  raw=(PR/'code'/name).read_bytes();assert hashlib.sha256(raw).hexdigest()==oldhash
  counts={}
  def replace(match):
   old=int(match.group());counts[str(old)]=counts.get(str(old),0)+1;return str(MAPPING[old])
  adapted=pattern.sub(replace,raw.decode()).encode();assert hashlib.sha256(adapted).hexdigest()==newhash
  (HERE/'code'/name).write_bytes(adapted);files[name]=dict(source_sha256=oldhash,derived_sha256=newhash,literal_counts=counts)
 write(HERE/'ADAPTATION.json',dict(source_commit='0e790f2dfb64e17bdee154aee151bb0c1dddb28e',mapping=MAPPING,files=files,
  rationale='Exact R781 counts:64rank8+24928rank9 slots;8 heterogeneous banks+3115 padded banks/stage;58827live,59618physical,28035padding. Assertions preserved.'))
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',COMPLEX_PUBLIC=str(PR/'public'),COMPLEX_CERT=str(HERE/'candidate.json.gz'),
  COMPLEX_OUTPUT=str(OUT/'hetero'),COMPLEX_SINK_AUDIT=str(HERE/'sink-audit.json'),COMPLEX_PREWHITE=str(HERE/'prewhite.json'))
 for key in ['PYTHONOPTIMIZE','CX_PINS','CX_SOURCE_PINS','CX_RECORD','CX_RECEIPT']:env.pop(key,None)
 steps=[]
 def run(name,cmd,extra=None,negative=False):
  print('CHECK',name,flush=True);e=dict(env);e.update(extra or {})
  with (OUT/(name+'.log')).open('w')as log:result=subprocess.run(list(map(str,cmd)),env=e,stdout=log,stderr=subprocess.STDOUT)
  if negative:
   assert result.returncode!=0 and 'AssertionError: forward all independent live columns'in(OUT/(name+'.log')).read_text()
  else:assert result.returncode==0,(name,result.returncode)
  steps.append(dict(stage=name,log_sha256=sha(OUT/(name+'.log'))))
 def py(name,file,*args,extra=None,negative=False):run(name,[sys.executable,'-B',HERE/'code'/file,*args],extra,negative)
 py('heterogeneous-local','complex-hetero-compose.py')
 py('heterogeneous-endpoint-phases','complex-bank-phase.py')
 binary=OUT/('heterobanks.exe'if os.name=='nt'else'heterobanks')
 run('compile-banks',[env.get('CXX','g++'),'-O2','-std=c++17','-I'+str(PR/'public/381/source/research/e8-nine-stage-kappa/code/bit/checkers'),HERE/'code/root-heterobanks.cpp','-o',binary])
 run('literal-bank-geometry',[binary,HERE/'candidate.json',OUT/'HETEROBANKS.json'])
 py('independent-bank-review','bit-heterobank-review.py','--banks',OUT/'HETEROBANKS.json','--certificate',HERE/'candidate.json.gz','--sink-audit',HERE/'sink-audit.json','--output',OUT/'BANK-REVIEW.json')
 env.update(HETEROBANKS=str(OUT/'HETEROBANKS.json'),BANK_PHASE=str(OUT/'hetero/BANK-ENDPOINT-PHASE.json'),BANK_REVIEW=str(OUT/'BANK-REVIEW.json'))
 py('global-template','root-global.py')
 controls=[]
 for name in ['missing-sink-uncompute','reversed-preconditioning-order']:
  target=OUT/name;target.mkdir();pa,pp=copy.deepcopy(audit),copy.deepcopy(pre)
  if name=='missing-sink-uncompute':pa['accepted'][0]['uncompute'].pop(0)
  else:
   u,v='pre_target_dirty_cancellation_gates','pre_helper_inverse_gates';pp[u],pp[v]=pp[v],pp[u]
  write(target/'sink-audit.json',pa);write(target/'prewhite.json',pp)
  py(name,'complex-hetero-compose.py',extra=dict(COMPLEX_OUTPUT=str(target/'out'),COMPLEX_SINK_AUDIT=str(target/'sink-audit.json'),COMPLEX_PREWHITE=str(target/'prewhite.json')),negative=True)
  controls.append(name)
 cx=read(OUT/'hetero/RESULT.json')
 write(OUT/'RESULT.json',dict(status='PASS_FRESH_R781_HETEROGENEOUS_LOCAL_BOTH_ORIENTATIONS_ENDPOINT_PHASES_BANKS_GLOBAL_TEMPLATE_AND_FINITE_MOMENT',candidate_sha256=CANDIDATE,
  steps=steps,complex_b=cx['coarse'],local_profile=cx['local_profile'],live=cx['live'],physical=cx['physical'],invoice=cx['invoice'],
  source_adaptation_sha256=sha(HERE/'ADAPTATION.json'),preconditioning_sha256=sha(HERE/'GENERATION.json'),negative_controls_rejected=controls,
  outputs_sha256={name:sha(OUT/name)for name in ['hetero/RESULT.json','hetero/BANK-ENDPOINT-PHASE.json','hetero/GLOBAL-HETEROGENEOUS-RECEIPT.json','BANK-REVIEW.json','HETEROBANKS.json']}))
 receipt=bind(HERE,PR,ORD,SIGNED,BASELINE,BIT_PARENT)
 assert receipt['kappa']=='1001644754304116452673767/1000000000000000000000000000'
 assert manifest(PR)==source_manifest and before=={p:sha(p)for p in before}
 receipt.update(portable_replay_sha256=sha(Path(__file__)),pr390_leaf_input_manifest_sha256=source_manifest,
  source_hashes_unchanged=True,full_clean_extension_replay=True,negative_controls_rejected=controls,
  scientific_outputs_sha256={name:sha(HERE/name)for name in ['COMPOSITION-RECEIPT.json','COMPLEX-SUPPLIER.json','ASSEMBLY.json','GENERATION.json','ADAPTATION.json']})
 write(HERE/'RECEIPT.json',receipt)
if __name__=='__main__':main()
