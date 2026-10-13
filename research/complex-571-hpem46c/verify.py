"""Spec-driven official replay: rebuild every provider word from pinned sources through typed construction steps,
localize each word with the unchanged vendor pipeline, then run the spec-driven global admission and assembly.
Prepared with Claude Code assistance. Apache-2.0; see NOTICE.md. Pinned external sources are unchanged packages.
Everything this script runs is named in data/SPEC.json "build" and must be one of the allowlisted step types below;
the spec contains no scripts or commands, only step types, pinned source files, recipes and expected hashes.
"""
import argparse,gzip,hashlib,json,os,subprocess,sys,time,shutil,threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
assert __debug__, 'Assertions required'
P=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--work',type=Path,required=True)
ap.add_argument('--spec',type=Path,default=P/'data/SPEC.json',help=argparse.SUPPRESS)
ap.add_argument('--jobs',type=int,default=min(8,os.cpu_count() or 4),help='parallel provider chains')
ap.add_argument('--source',action='append',default=[],help='NAME=DIR pinned source package (default: sibling directory named in the spec)')
ap.add_argument('--check-pins',action='store_true',help='check package and source pins, then stop')
ap.add_argument('--until',choices=('locals','all'),default='all',help=argparse.SUPPRESS)
ap.add_argument('--reuse-baseline',type=Path,help=argparse.SUPPRESS)
ap.add_argument('--reuse-local',action='append',default=[],help=argparse.SUPPRESS)
a=ap.parse_args();O=a.work.resolve();SPECFILE=a.spec.resolve();SPEC=json.loads(SPECFILE.read_bytes());BUILD=SPEC['build']
DISCOVER=os.environ.get('WITNESS_DISCOVER')=='1';discovered={}
given=dict(x.split('=',1)for x in a.source)
SRC={name:Path(given.get(name,P.parent/src['dir'])).resolve()for name,src in BUILD['sources'].items()};S=SRC['multicold']
def read(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def content(p):return hashlib.sha256(gzip.decompress(p.read_bytes())).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2)+'\n',newline='\n')
def tree(root,skip):return{f.relative_to(root).as_posix():sha(f)for f in root.rglob('*')if f.is_file()and f!=root/skip and'__pycache__'not in f.parts}
def pinned(where,key,got,label):
 """Compare against the spec value; a discovery build (propose.py) records values the spec does not yet hold."""
 if key in where:assert got==where[key],'BUILD PIN MISMATCH %s.%s: expected %s got %s'%(label,key,where[key],got)
 else:assert DISCOVER,'BUILD PIN MISSING %s.%s'%(label,key);discovered[label+'.'+key]=got
 return got
if SPECFILE==P/'data/SPEC.json':assert tree(P,'MANIFEST.json')==read(P/'MANIFEST.json'),'package MANIFEST'
for name,src in BUILD['sources'].items():
 root=SRC[name];manifest=read(root/'MANIFEST.json')
 assert sha(root/'MANIFEST.json')==src['manifest_sha256'],name+' manifest pin'
 if src.get('full_tree'):assert tree(root,'MANIFEST.json')==manifest,name+' tree'
 files=manifest.get('files',manifest)
 for rel,value in src['files'].items():assert sha(root/rel)==value==files[rel],(name,rel)
def ref(r,pin=True):
 """'pkg:rel' (this package) or 'NAME:rel' (a pinned file of source NAME)."""
 kind,rel=r.split(':',1)
 if kind=='pkg':return P/rel
 assert rel in BUILD['sources'][kind]['files'],'unpinned source file '+r
 return SRC[kind]/rel
if a.check_pins:print('PINS OK',SPEC['name'],sha(SPECFILE));raise SystemExit(0)
assert not O.exists() and not any(O.is_relative_to(x)for x in (P,*SRC.values()))
O.mkdir(parents=True);steps=[];lock=threading.Lock();start=time.monotonic()
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',PYTHONINTMAXSTRDIGITS='0',MULTICOLD_SOURCE=str(S),GAIN_PR564_SOURCE=str(S),WITNESS_SPEC=str(SPECFILE));env.pop('PYTHONOPTIMIZE',None);env.pop('WITNESS_DISCOVER',None)
def run(name,script,*args):
 log=O/(name+'.log');t=time.monotonic();print('RUN',name,flush=True)
 with log.open('w')as f:code=subprocess.call([sys.executable,'-B',str(S/'code/run_portable.py'),str(script),*map(str,args)],stdout=f,stderr=subprocess.STDOUT,env=env)
 with lock:steps.append(dict(name=name,exit_code=code,seconds=round(time.monotonic()-t,3),log_sha256=sha(log)));dump(O/'STAGES.json',steps)
 if code:raise RuntimeError(name+' failed\n'+log.read_text()[-6000:])
 print('PASS',name,flush=True)
B=S/'vendor/pr558';F=B/'vendor/pr552';V=F/'complex-global/vendor531';GK=F/'complex-local/static44/gk'
if a.reuse_baseline:baseline=a.reuse_baseline.resolve()
else:baseline=O/'baseline558';run('frozen558-full-replay',B/'verify.py','--work',baseline)
SEL=baseline/'reconstruction/static44/SELECTION.json';RAW=baseline/'reconstruction/promoted/FULL-WORD.json.gz'
def omissions(path,s,label):pinned(s,'omission_controls',len(read(path)['controls']),label)
# Allowlisted step types: (constructor, paired omission audit), all scripts from the pinned multicold source.
def cold_kernel(word,s,out,tag):
 recipe=ref(s['recipe']);pinned(s,'recipe_sha256',sha(recipe),tag)
 run(tag+'-construction',S/'code/build_cold_kernel.py','--input',word,'--recipe',recipe,'--gk-dir',GK,'--out',out)
 run(tag+'-omissions',S/'code/audit_kernel_controls.py','--word',out/'FULL-WORD.json.gz','--recipe',recipe,'--out',out/'KERNEL-OMISSION-CONTROLS.json')
 omissions(out/'KERNEL-OMISSION-CONTROLS.json',s,tag)
def finalize(word,recipe,tag):
 """Discovery only: a new recipe whose output hash is still open is pinned by a first build that must fail exactly at
 the final output-hash assertion (every kernel check passed); the printed hash is written into a final recipe."""
 r=read(recipe);h=r.get('output_content_sha256','')
 if len(h)==64 and all(c in '0123456789abcdef'for c in h):return recipe
 assert DISCOVER,'recipe output hash not pinned: '+tag
 r['output_content_sha256']='0'*64;probe=O/(tag+'-probe');probe.mkdir();dump(probe/'RECIPE.json',r)
 p=subprocess.run([sys.executable,'-B',str(S/'code/run_portable.py'),str(S/'code/build_multicut_kernels.py'),'--input',str(word),'--recipe',str(probe/'RECIPE.json'),'--gk-dir',str(GK),'--out',str(probe/'out')],capture_output=True,text=True,env=env)
 last=(p.stderr.strip().splitlines()or[''])[-1];assert p.returncode and last.startswith('AssertionError: ')and len(last)==16+64,'probe build failed before the output hash:\n'+p.stderr[-3000:]
 r['output_content_sha256']=last[16:];final=O/(tag+'-RECIPE.json');final.write_text(json.dumps(r,indent=1)+'\n',newline='\n')
 discovered[tag+'.final_recipe']=str(final);return final
def multicut(word,s,out,tag):
 recipe=finalize(word,ref(s['recipe']),tag);pinned(s,'recipe_sha256',sha(recipe),tag)
 run(tag+'-construction',S/'code/build_multicut_kernels.py','--input',word,'--recipe',recipe,'--gk-dir',GK,'--out',out)
 run(tag+'-omissions',S/'code/audit_multicold_controls.py','--word',out/'FULL-WORD.json.gz','--recipe',recipe,'--out',out/'MULTICOLD-OMISSION-CONTROLS.json')
 omissions(out/'MULTICOLD-OMISSION-CONTROLS.json',s,tag)
PROMOTER=('larger_gain','providers/build_entrance_promotions.py',('providers/coupled_frames_base.py','providers/search_suffix_kernels.py'))
def frame_only(source,word,recipes):
 """Independent check that a promotion changed only entrance frames: identical scalar operations, start_extra changed
 exactly at the recipe pivots (old -> new frame), frame fields only on scalar events, report changes limited."""
 assert source.keys()==word.keys()
 for section in source:
  if section in ('A','cut','B','cleanup','precondition'):
   assert len(source[section])==len(word[section])
   assert all(x[:-1]==y[:-1]for x,y in zip(source[section],word[section])),'scalar operation changed'
  elif section not in ('start_extra','report'):assert source[section]==word[section],'fixed field changed: '+section
 entrances=dict(source['start_extra'])
 for r in recipes:
  k=str(r['pivot']);assert sorted(entrances[k])==sorted(r['old_frame']) and len(r['new_frame'])==len(r['old_frame'])+1,'wrong old entrance '+k
  entrances[k]=word['start_extra'][k];assert sorted(entrances[k])==sorted(r['new_frame']),'wrong new entrance '+k
 assert word['start_extra']==entrances,'entrance changed outside the recipe'
 allowed={'local_profile','local_rank_mass','entrance_rank','entering_helpers','width_inventory'}
 assert source['report'].keys()==word['report'].keys() and all(source['report'][k]==word['report'][k]for k in source['report']if k not in allowed)
def promote(word,s,out,tag):
 src,builder,deps=PROMOTER;recipe=ref(s['recipe']);pinned(s,'recipe_sha256',sha(recipe),tag)
 for f in deps:ref(src+':'+f)
 run(tag+'-construction',ref(src+':'+builder),'--word',word,'--recipes',recipe,'--gk-dir',GK,'--out',out)
 a,b,r=read(word),read(out/'FULL-WORD.json.gz'),read(recipe);frame_only(a,b,r)
 import copy
 rejected=[]
 for name,mut in (('reverted_promotion',lambda w:w['start_extra'].__setitem__(str(r[0]['pivot']),list(r[0]['old_frame']))),
  ('scalar_operation_changed',lambda w:w['B'][0].insert(0,'mutated')),('extra_entrance_changed',lambda w:w['start_extra'].__setitem__(next(k for k in w['start_extra']if k not in{str(x['pivot'])for x in r}),[])),
  ('fixed_field_changed',lambda w:w.__setitem__('cut',w['cut'][:-1]))):
  w=copy.deepcopy(b);mut(w)
  try:frame_only(a,w,r)
  except(AssertionError,KeyError,IndexError,TypeError):rejected.append(name)
  else:raise AssertionError('frame-only control accepted: '+name)
 dump(out/'FRAME-ONLY-CONTROLS.json',dict(status='PASS_FRAME_ONLY_PROMOTION_TRANSFER',promotions=len(r),controls=rejected))
 omissions(out/'FRAME-ONLY-CONTROLS.json',s,tag)
JOINT=('joint_prefix',('code/build_joint_prefix.py','code/audit_joint_prefix.py','code/audit_multicold_controls.py'))
def joint_prefix(word,s,out,tag):
 """PR575's unchanged joint-prefix constructor with its paired audits: all-kernel omissions, rank-five omissions and
 the independent literal-prefix/coverage audit (variant and kernel recipe named in the step)."""
 src,(builder,audit,omit)=JOINT;recipe=ref(s['recipe']);kern=ref(s['kernel_recipes']);pinned(s,'recipe_sha256',sha(recipe),tag);pinned(s,'kernel_recipes_sha256',sha(kern),tag)
 assert s['variant'] in ('eightcold','width7')
 run(tag+'-construction',ref(src+':'+builder),'--input',word,'--recipe',recipe,'--variant',s['variant'],'--gk-dir',GK,'--out',out)
 shutil.copyfile(RAW.parent/'PROMOTION.json',out/'PROMOTION.json')
 run(tag+'-all-kernel-omissions',ref(src+':'+omit),'--word',out/'FULL-WORD.json.gz','--recipe',kern,'--out',out/'ALL-KERNEL-CONTROLS.json')
 run(tag+'-rank5-omissions',B/'code/audit_promoted_scalar.py',out/'FULL-WORD.json.gz',SEL,out/'RANK5-CONTROLS.json')
 run(tag+'-independent-joint-prefix-and-coverage',ref(src+':'+audit),'--source',word,'--word',out/'FULL-WORD.json.gz','--recipe',recipe,'--variant',s['variant'],'--kernel-recipes',kern,'--controls',out/'ALL-KERNEL-CONTROLS.json','--rank5-controls',out/'RANK5-CONTROLS.json','--promotion',out/'PROMOTION.json','--selection',SEL,'--out',out/'JOINT-PREFIX-AUDIT.json')
 j=read(out/'JOINT-PREFIX-AUDIT.json');assert j['status']=='PASS_INDEPENDENT_LITERAL_PREFIX_AND_FINAL_KERNEL_COVERAGE'
 c=read(out/'ALL-KERNEL-CONTROLS.json');assert all(x['forward_rejected'] and x['reflected_rejected'] for x in c['controls'])
 omissions(out/'ALL-KERNEL-CONTROLS.json',s,tag);pinned(s,'rank5_controls',len(read(out/'RANK5-CONTROLS.json')['controls']),tag)
 pinned(s,'joint_negative_controls',len(j['negative_controls_rejected']),tag)
COAL=('frame_coalescing','code/build_frames.py')
def frame_coalesce(word,s,out,tag):
 """PR583's unchanged frame-coalescence constructor (it re-checks profiles, scalar operations, widths and helper
 responses and rejects every omission/over-promotion control), plus an independent check that only the recipe's
 gate frames changed (old -> new) and every other field of the word is identical."""
 src,builder=COAL;recipe=ref(s['recipe']);pinned(s,'recipe_sha256',sha(recipe),tag)
 run(tag+'-construction',ref(src+':'+builder),'--input',word,'--recipe',recipe,'--gk-dir',GK,'--out',out)
 r=read(recipe);c=read(out/'FRAME-CONSTRUCTION.json');assert c['status']=='PASS_SIX_EXACT_FRAME_COALESCENCES'
 assert len(c['negative_controls_rejected'])==2*len(r['changes']);pinned(s,'negative_controls',len(c['negative_controls_rejected']),tag)
 x,y=read(word),read(out/'FULL-WORD.json.gz');ch={(z['section'],z['index']):z for z in r['changes']};assert len(ch)==len(r['changes'])
 assert x.keys()==y.keys() and all(x[k]==y[k]for k in x if k not in('A','B','report'))
 for part in ('A','B'):
  assert len(x[part])==len(y[part])
  for i,(u,v) in enumerate(zip(x[part],y[part])):
   z=ch.pop((part,i),None)
   if z is None:assert u==v,'frame changed outside the recipe %s %d'%(part,i)
   else:assert u==z['before'] and v==z['after'] and u[:-1]==v[:-1],'wrong coalescence %s %d'%(part,i)
 assert not ch,'recipe change outside A/B'
 assert all(x['report'][k]==y['report'][k]for k in x['report']if k not in('local_profile','local_rank_mass','status'))
def gate_move_coalesce(word,s,out,tag):
 """This package's code/build_gate_moves.py (PR583's constructor extended by commuting gate moves): every passed gate
 must commute, helper responses and widths are unchanged, cleanup follows the inherited inverse rule, and every
 omission/over-promotion/unmoved control is rejected; then the same independent comparison as frame_coalesce."""
 recipe=ref(s['recipe']);pinned(s,'recipe_sha256',sha(recipe),tag)
 run(tag+'-construction',P/'code/build_gate_moves.py','--input',word,'--recipe',recipe,'--gk-dir',GK,'--out',out)
 r=read(recipe);c=read(out/'FRAME-CONSTRUCTION.json');assert c['status']=='PASS_EXACT_GATE_MOVE_FRAME_COALESCENCES'
 assert len(c['negative_controls_rejected'])==2*len(r['changes'])+len(r['moves']);pinned(s,'negative_controls',len(c['negative_controls_rejected']),tag)
 x,y=read(word),read(out/'FULL-WORD.json.gz')
 for m in r['moves']:L=x[m['section']];L.insert(m['to'],L.pop(m['from']))
 ch={(z['section'],z['index']):z for z in r['changes']};assert len(ch)==len(r['changes'])
 assert x.keys()==y.keys() and all(x[k]==y[k]for k in x if k not in('A','B','cleanup','report'))
 for part in ('A','B'):
  assert len(x[part])==len(y[part])
  for i,(u,v) in enumerate(zip(x[part],y[part])):
   z=ch.pop((part,i),None)
   if z is None:assert u==v,'gate changed outside the recipe %s %d'%(part,i)
   else:assert u==z['before'] and v==z['after'] and u[:-1]==v[:-1],'wrong coalescence %s %d'%(part,i)
 assert not ch,'recipe change outside A/B'
 meta=('width_inventory','entering_helpers','entrance_rank');assert all(x['report'][k]==y['report'][k]for k in x['report']if k not in('local_profile','local_rank_mass','status')+meta)
 sys.path.insert(0,str(GK));import gk_common as GC;GC.V=112;ws=GC.widths_of(y)
 assert y['report']['width_inventory']=={str(k):v for k,v in sorted(Counter(ws).items())} and y['report']['entering_helpers']==sum(v<9 for v in ws) and y['report']['entrance_rank']==sum(9-v for v in ws),'descriptive width metadata not normalized'
def hyperplane_end(word,s,out,tag):
 """This package's code/build_hpe.py: cleanup gates that commute with the whole skipped cleanup prefix run right after B
 at the join frame U of their registers, and the helper ends at U (residual T_U T_E^-1, width |U|-|E|; Lemma C, nested
 children, Lemma A).  Paired audit: code/hpe_controls_atc.py (exact replay of the reordered program plus HPE raw-word
 mutations).  Then an independent comparison: only early_cleanup, helper_final and the paid profile change."""
 recipe=ref(s['recipe']);pinned(s,'recipe_sha256',sha(recipe),tag)
 run(tag+'-construction',P/'code/build_hpe.py','--input',word,'--recipe',recipe,'--out',out)
 run(tag+'-controls',P/'code/hpe_controls_atc.py',out/'FULL-WORD.json.gz',F/'complex-local/inputs/phase-baseline/CANONICAL-WORD.json.gz',out)
 c=read(out/'HPE-ATC-CONTROLS.json');assert c['status']=='PASS_HPE_RAW_WORD_CONTROLS';pinned(s,'negative_controls',len(c['rejected']),tag)
 r=read(recipe);x,y=read(word),read(out/'FULL-WORD.json.gz')
 assert set(y)==set(x)|{'early_cleanup','helper_final'} and 'early_cleanup' not in x and all(x[k]==y[k]for k in x if k!='report')
 assert y['early_cleanup']==[[z['cleanup_index'],z['frame']]for z in r['changes']] and y['helper_final']=={str(z['helper']):z['frame']for z in r['changes']}
 assert x['report'].keys()==y['report'].keys() and all(x['report'][k]==y['report'][k]for k in x['report']if k not in('local_profile','local_rank_mass','width_inventory'))
 inv=Counter({int(k):n for k,n in x['report']['width_inventory'].items()})
 for z in r['changes']:e=len(x['start_extra'][str(z['helper'])]);inv[9-e]-=1;inv[len(z['frame'])-e]+=1
 assert y['report']['width_inventory']=={str(k):n for k,n in sorted(inv.items())if n},'descriptive width metadata not |final|-|start|'
STEPS={'hyperplane_end':hyperplane_end,'cold_kernel':cold_kernel,'multicut':multicut,'greedy_kernels':multicut,'promote':promote,'joint_prefix':joint_prefix,'frame_coalesce':frame_coalesce,'gate_move_coalesce':gate_move_coalesce}
def build_word(pid,d):
 base=d['base'];assert base['kind']in('frozen558_promoted','source_file'),base['kind']
 word=RAW if base['kind']=='frozen558_promoted' else ref(base['file'])
 pinned(base,'content_sha256',content(word),pid+'.base')
 for i,s in enumerate(d['steps']):
  tag='%s-step%d-%s'%(pid,i,s['type']);out=O/tag
  if s['type']=='frozen558_scalar_audits':
   # inherited static44 and rank-five omission audits on a frozen558-descended word
   out.mkdir();run(tag+'-static44',F/'complex-local/static44/audit_scalar.py',word,SEL,out/'STATIC44-SCALAR-AUDIT.json')
   shutil.copyfile(RAW.parent/'PROMOTION.json',word.parent/'PROMOTION.json')
   run(tag+'-rank5',B/'code/audit_promoted_scalar.py',word,SEL,out/'PROMOTED-SCALAR-AUDIT.json');continue
  assert s['type'] in STEPS,'step type not allowlisted: '+s['type']
  pinned(s,'input_content_sha256',content(word),tag)
  STEPS[s['type']](word,s,out,tag);word=out/'FULL-WORD.json.gz'
  pinned(s,'output_content_sha256',content(word),tag)
 pinned(d,'word_content_sha256',content(word),pid)
 return word
def localize(pid,word):
 local=O/(pid+'-local')
 # HPE words (helper_final present) use this package's generalised native chain; every other word the unchanged vendor531 one
 hp='helper_final' in read(word);NC=(lambda f:P/'code'/('hpe_'+f))if hp else(lambda f:V/'code'/f)
 run(pid+'-all-columns-native-frames',NC('audit_and_transport.py'),'--raw',word,'--routing',F/'complex-local/inputs/phase-baseline/CANONICAL-WORD.json.gz','--out',local)
 run(pid+'-both-reflected-ledgers',NC('emit_local.py'),local)
 run(pid+'-independent-local-controls',NC('audit_local.py'),local)
 run(pid+'-normalized-wrappers',NC('adapters_local.py'),local/'CANONICAL-WORD.json.gz',local/'RESIDUAL-ADAPTERS.json',local/'WRAPPER-CHECKS.json')
 run(pid+'-all-phase-edges',B/'code/phases_full.py',local,V/'vendor/clifford')
 r=BUILD['providers'][pid].get('retained_local')
 if r:  # a pinned retained local must be reproduced byte for byte (phase review up to timing)
  for name in ('CANONICAL-WORD.json.gz','LOCAL-PROGRAMS.json.gz','LOCAL-CHECKS.json','INDEPENDENT-LOCAL-REPLAY.json','RESIDUAL-ADAPTERS.json','WRAPPER-CHECKS.json','CLIFFORD-RECIPES.json'):
   assert sha(local/name)==sha(ref(r+'/'+name)),(pid,name)
  fresh,old=read(local/'CLIFFORD-REVIEW.json'),read(ref(r+'/CLIFFORD-REVIEW.json'))
  assert {k:v for k,v in fresh.items()if k!='seconds'}=={k:v for k,v in old.items()if k!='seconds'}
 return local
reuse=dict(x.split('=',1)for x in a.reuse_local)
words={}
def provider(pid):
 word=words[pid]=build_word(pid,BUILD['providers'][pid])
 return Path(reuse[pid]).resolve()if pid in reuse else localize(pid,word)
with ThreadPoolExecutor(max(1,min(a.jobs,len(BUILD['providers']))))as pool:
 futures={pid:pool.submit(provider,pid)for pid in sorted(BUILD['providers'])};locals_={pid:f.result()for pid,f in futures.items()}
dump(O/'LOCALS.json',dict(locals={pid:str(l)for pid,l in locals_.items()},words={pid:str(w)for pid,w in words.items()},baseline=str(baseline),discovered=discovered))
if a.until=='locals':print('LOCALS READY');raise SystemExit(0)
assert not DISCOVER
G=O/'mixed-global'
run('bind-providers',P/'code/bind_providers_portable.py','--baseline',baseline,*[x for pid,l in sorted(locals_.items())for x in('--provider','%s=%s'%(pid,l))],'--plan',P/'data/PLAN.json','--out',G)
run('emit-controller',P/'code/emit_allcold.py','--base',G/'base','--owners',P/'data/OWNERS.json.gz','--plan',G/'PLAN.json','--out',G/'hosted')
(G/'audit').mkdir()
run('independent-controller-and-controls',P/'code/audit_allcold.py',G/'base',G/'hosted',G/'audit/ASYNC-AUDIT.json','--mutation-controls')
run('fresh-invoice',P/'code/invoice_allcold.py','--base',G/'base','--hosted',G/'hosted','--audit',G/'audit','--out',G/'audit','--retained-invoice',V/'evidence/audit/PREFIX-AND-INVOICE.json')
run('conservative-and-native-exact-assembly',P/'code/assemble.py',S,G,O/'ASSEMBLY.json')
run('admission-controls',P/'code/assembly_controls.py','--source-package',S,'--owner',G/'audit/OWNERS-AND-PROFILE.json','--invoice',G/'audit/PREFIX-AND-INVOICE.json','--out',O/'ASSEMBLY-CONTROLS.json')
run('phase-timing-portability-controls',P/'code/phase_timing_controls.py',S,G/'base',G/'audit',O/'PHASE-TIMING-CONTROLS.json')
run('actual-recompression-and-rebound-controls',P/'code/generated_identity_controls.py','--base',G/'base','--audit',G/'audit','--out',O/'GENERATED-IDENTITY-CONTROLS.json')
X=SPEC['expected']
for pid,local in locals_.items():
 r=read(local/'INDEPENDENT-LOCAL-REPLAY.json');ph=read(local/'CLIFFORD-REVIEW.json')
 assert len(r['negative_controls_rejected'])==SPEC['providers'][pid]['native_negative_controls'] and r['paid_profiles']['forward']==r['paid_profiles']['backward']
 assert ph['status']=='PASS_NEW_WORD_EXACT_LOCAL_PHASE_RECIPES' and ph['all_child_equalities_include_global_phase']is True and ph['directed_edges']==SPEC['providers'][pid]['phase_edges'] and ph['endpoint_adapters']==224
assert len(read(G/'audit/ASYNC-AUDIT.json')['mutations_rejected'])==X['mutations_rejected']
assert len(read(O/'ASSEMBLY-CONTROLS.json')['rejected_controls'])==X['assembly_controls_rejected']
z=read(O/'ASSEMBLY.json');assert Q(z['kappa_decimal'])==Q(X['kappa_decimal']) and Q(z['conservative_kappa_decimal'])==Q(X['conservative_kappa_decimal'])
assert {str(k):v for k,v in z['complex_profile'].items()}==X['global_profile'] and z['provider_counts']==X['provider_counts']
r=dict(status=SPEC['build']['status'],kappa=z['kappa'],kappa_decimal=z['kappa_decimal'],complex_lower=z['complex_lower'],bit_lower=z['bit_lower'],conservative_kappa_decimal=z['conservative_kappa_decimal'],conservative_complex_lower=z['conservative_complex_lower'],global_profile=z['complex_profile'],provider_counts=z['provider_counts'],surcharge_model=z['surcharge_model'],seconds=time.monotonic()-start,reused=dict(baseline=bool(a.reuse_baseline),locals=sorted(reuse)),scope=z['scope']);dump(O/'RESULT.json',r)
paths=['PHASE-TIMING-CONTROLS.json','GENERATED-IDENTITY-CONTROLS.json','mixed-global/audit/IDLE-REMAINDER-FRAMES.json','RESULT.json','ASSEMBLY.json','ASSEMBLY-CONTROLS.json','mixed-global/BINDING.json','mixed-global/audit/ASYNC-AUDIT.json','mixed-global/audit/OWNERS-AND-PROFILE.json','mixed-global/audit/PREFIX-AND-INVOICE.json']
paths+=sorted(f.relative_to(O).as_posix()for f in O.glob('*-step*/*.json'))
for pid in sorted(set(locals_)-set(reuse)):
 for fn in ('INDEPENDENT-LOCAL-REPLAY.json','CLIFFORD-REVIEW.json','WRAPPER-CHECKS.json'):paths.append(pid+'-local/'+fn)
dump(O/'RECEIPT.json',dict(status=r['status'],steps=steps,artifacts={name:sha(O/name)for name in paths},manifest_sha256=sha(P/'MANIFEST.json'),spec_sha256=sha(SPECFILE),source_manifest_sha256={n:sha(SRC[n]/'MANIFEST.json')for n in SRC}))
print(json.dumps(r,indent=2))
