"""Portable finite admission. Fresh native suppliers by default; explicit bound reuse supported."""
import argparse,gzip,hashlib,json,os,shutil,subprocess,sys,tarfile,threading,time
from pathlib import Path
P=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--work',type=Path,required=True);ap.add_argument('--base-native-from',type=Path);ap.add_argument('--extra-native-from',type=Path);ap.add_argument('--parent-receipt-cache',type=Path);ap.add_argument('--new-base-native-from',type=Path);ap.add_argument('--new-extra-native-from',type=Path);ap.add_argument('--native-cache',type=Path);ap.add_argument('--audit-shards',type=int,default=4);a=ap.parse_args();work=a.work.resolve();assert __debug__ and not work.exists() and not work.is_relative_to(P)
def rd(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
pins=rd(P/'MANIFEST.json');actual={p.relative_to(P).as_posix() for p in P.rglob('*') if p.is_file() and p!=P/'MANIFEST.json'};assert actual==set(pins)
for rel,h in pins.items():assert sha(P/rel)==h,rel
work.mkdir();(work/'tmp').mkdir();env=dict(os.environ,TMPDIR=str(work/'tmp'),PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',PYTHONINTMAXSTRDIGITS='0',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
for k in ('PYTHONOPTIMIZE','WITNESS_DISCOVER','WITNESS_RECORD','WITNESS_SPEC'):env.pop(k,None)
env['AUDIT_FAST_SHARDS']=str(max(1,a.audit_shards))
stages=[];lock=threading.Lock()
def run(name,script,*args):
 t=time.monotonic();log=work/(name+'.log')
 with log.open('w') as f:r=subprocess.run([sys.executable,'-B',str(script),*map(str,args)],cwd=work,env=env,stdout=f,stderr=subprocess.STDOUT)
 with lock:stages.append(dict(name=name,exit_code=r.returncode,seconds=time.monotonic()-t,log_sha256=sha(log)));(work/'STAGES.json').write_text(json.dumps(stages,indent=2))
 assert r.returncode==0,(name,log.read_text()[-5000:]);print('PASS',name,flush=True)
old=P/'vendor/pr1297'
# The pinned input witness must be the exact retained predecessor, not merely a similar profile.
for n in ['PLAN.json','OWNERS.json.gz','GLOBAL-TEMPLATE.json.gz','DISPATCH.json','SPEC.json']:assert rd(P/'inputs'/n)==rd(old/n),n
env['FINE_ENGINE_CACHE']=str(work/'fine-cache')
run('fine-engine-oracle',P/'code/oracle_check.py')
opts=[]
for key,path in [('base',a.base_native_from),('extra',a.extra_native_from)]:
 if path:opts.extend(['--'+key+'-native-from',path.resolve()])
PARENT_STATUS='PASS_GLOBAL_MIXED_X54_FUSIONS_NATIVE_AND_STRICT_ADMISSION'
def retained_files_ok():
 # the retained package must be byte-for-byte the one every receipt below is bound to (same check as its own verify.py)
 vm=rd(old/'MANIFEST.json');have={p.relative_to(old).as_posix() for p in old.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p!=old/'MANIFEST.json'}
 assert have==set(vm),'retained package file set differs from its manifest'
 for rel,h in vm.items():assert sha(old/rel)==h,rel
def natives_bound(path,word):
 assert gzip.decompress((path/'local/FULL-WORD.json.gz').read_bytes())==gzip.decompress((old/word).read_bytes()),word
 st=rd(path/'STEPS.json');assert [x['step'] for x in st]==['native','ledgers','local-replay','wrappers','phases'] and all(x['exit_code']==0 for x in st)
rc=None;receipt=None
if a.parent_receipt_cache and a.base_native_from and a.extra_native_from:
 retained_files_ok();rc=a.parent_receipt_cache.resolve()/sha(old/'MANIFEST.json')
 if (rc/'RECEIPT.json').is_file():
  receipt=rd(rc/'RECEIPT.json')
  try:
   assert receipt['schema']=='parent-receipt/1' and receipt['vendor_manifest_sha256']==sha(old/'MANIFEST.json')
   assert receipt['claim_sha256']==sha(old/'CLAIM.json') and receipt['words']=={'base':sha(old/'gauge44-word.json.gz'),'extra':sha(old/'extra-word.json.gz')}
   for name,h in receipt['files'].items():assert sha(rc/name)==h,name
   pr=rd(rc/'RESULT.json');assert pr['status']==PARENT_STATUS and pr['kappa']==rd(old/'CLAIM.json')['kappa'] and pr['base_native_reuse'] is True and pr['extra_native_reuse'] is True
   natives_bound(a.base_native_from.resolve(),'gauge44-word.json.gz');natives_bound(a.extra_native_from.resolve(),'extra-word.json.gz')
  except (AssertionError,KeyError,OSError,ValueError) as exc:
   print('parent receipt rejected (%r); running the full retained admission'%(exc,),flush=True);receipt=None
if receipt:
 t0=time.monotonic();pl=work/'parent';pl.mkdir();lay=pl/'layout';lay.mkdir()
 with tarfile.open(old/'upstream-layout.tar.gz') as t:
  for m in t.getmembers():assert m.isfile() and not Path(m.name).is_absolute() and '..' not in Path(m.name).parts
  t.extractall(lay,filter='data')
 (lay/'globalmix51').mkdir();shutil.copytree(a.extra_native_from.resolve(),lay/'globalmix51/native-extra')
 with lock:stages.append(dict(name='retained-provider-and-parent-admission',reused_receipt=str(rc.name),exit_code=0,seconds=time.monotonic()-t0));(work/'STAGES.json').write_text(json.dumps(stages,indent=2))
 print('PASS retained-provider-and-parent-admission (hash-checked receipt)',flush=True)
else:
 run('retained-provider-and-parent-admission',old/'verify.py','--work',work/'parent',*opts)
 pr=rd(work/'parent/RESULT.json');assert pr['status']==PARENT_STATUS and pr['kappa']==rd(old/'CLAIM.json')['kappa']
 if rc is not None and a.base_native_from and a.extra_native_from:
  natives_bound(a.base_native_from.resolve(),'gauge44-word.json.gz');natives_bound(a.extra_native_from.resolve(),'extra-word.json.gz')
  rc.mkdir(parents=True,exist_ok=True);shutil.copy2(work/'parent/RESULT.json',rc/'RESULT.json');shutil.copy2(work/'parent/STAGES.json',rc/'STAGES.json')
  (rc/'RECEIPT.json').write_text(json.dumps(dict(schema='parent-receipt/1',vendor_manifest_sha256=sha(old/'MANIFEST.json'),claim_sha256=sha(old/'CLAIM.json'),words={'base':sha(old/'gauge44-word.json.gz'),'extra':sha(old/'extra-word.json.gz')},files={'RESULT.json':sha(rc/'RESULT.json'),'STAGES.json':sha(rc/'STAGES.json')}),indent=1)+'\n')
pre_words={'base':P/'new/gauge44-word-566.json.gz','extra':P/'new/extra-word-566.json.gz'}
new_words={'base':P/'new/borrow/words/BORROW-WORD-43base.json.gz','extra':P/'new/borrow/words/BORROW-WORD-43extra.json.gz'}
nat={};nat_err=[]
def new_native(key):
 try:
  w=new_words[key];reuse=getattr(a,'new_%s_native_from'%key);d=None;ws=sha(w)
  def tree(e):return {x.relative_to(e).as_posix():sha(x) for x in sorted(e.rglob('*')) if x.is_file() and x.name!='CACHE.json'}
  if reuse:d=reuse.resolve()
  elif a.native_cache:
   e=a.native_cache.resolve()/ws
   if (e/'CACHE.json').is_file():
    cj=rd(e/'CACHE.json')
    if cj.get('word_sha256')==ws and cj.get('files')==tree(e):d=e
  if d is None:
   d=work/('native-new-'+key);run('native-new-'+key,P/'new/run_native_borrow.py',w,d)
   if a.native_cache:
    root=a.native_cache.resolve();root.mkdir(parents=True,exist_ok=True);dst=root/ws
    if not dst.exists():
     tmp=root/('.tmp-%s-%d'%(ws,os.getpid()));shutil.copytree(d,tmp);(tmp/'CACHE.json').write_text(json.dumps(dict(word_sha256=ws,files=tree(tmp)),indent=1))
     try:tmp.rename(dst)
     except OSError:shutil.rmtree(tmp,ignore_errors=True)
  assert gzip.decompress((d/'local/FULL-WORD.json.gz').read_bytes())==gzip.decompress(w.read_bytes()),(key,'native directory is not bound to the shipped word')
  st_=rd(d/'STEPS.json');assert [x['step'] for x in st_]==['native','ledgers','local-replay','wrappers','phases'] and all(x['exit_code']==0 for x in st_)
  nat[key]=d
 except BaseException as exc:nat_err.append(exc)
nthreads=[threading.Thread(target=new_native,args=(k,)) for k in new_words]
for t_ in nthreads:t_.start()
def rebuild_chain():
 run('reconstruct-owners',P/'reconstruct.py','--out',work/'rebuilt-owners')
 for n in ['OWNERS.json.gz','ORDER.json','DISPATCH.json','PROFILE.json']:assert rd(work/'rebuilt-owners'/n)==rd(P/n),n
 run('lift-parent',P/'lift_parent.py','--owners',work/'rebuilt-owners','--out',work/'rebuilt-parent')
 for n in ['GLOBAL-TEMPLATE.json.gz','PLAN.json','CONSTRUCTION.json']:assert rd(work/'rebuilt-parent'/n)==rd(P/n),n
 assert rd(work/'rebuilt-parent/SPEC.json')['geometry']==rd(P/'SPEC.json')['geometry']
chain_err=[]
def chain_thread():
 try:rebuild_chain()
 except BaseException as exc:chain_err.append(exc)
chain=threading.Thread(target=chain_thread);chain.start()
for t_ in nthreads:t_.join()
if nat_err:raise nat_err[0]
SRCL=work/'parent/layout/joint1148-round45/source'
run('rebuild-words-566',P/'new/rebuild_chain.py')
run('rebuild-borrow-words',P/'new/rebuild_borrow.py')
for key_,w_ in pre_words.items():run('audit-local-566-'+key_,SRCL/'research/gauge44-slots/independent/audit_local.py','--word',w_,'--main',SRCL,'--output',work/('AUDIT-LOCAL-566-'+key_+'.json'))
run('rebind-566',P/'new/rebind.py',P,nat['base']/'local',nat['extra']/'local',work/'data-rebound')
run('lemmag-labels',P/'code/lemmag_stage.py',work/'LEMMAG-LABELS.json',nat['base'],nat['extra'],*[p_ for p_ in (a.base_native_from,a.extra_native_from) if p_])
STABLE=('LOCAL-CHECKS.json','CLIFFORD-RECIPES.json','RESIDUAL-ADAPTERS.json')
def bind_view(plan):
 plan=json.loads(json.dumps(plan))
 for desc in plan['provider_registry'].values():desc['artifact_sha256']={n:h for n,h in desc['artifact_sha256'].items() if n in STABLE}
 return plan
assert bind_view(rd(work/'data-rebound/PLAN.json'))==bind_view(rd(P/'new/PLAN.json')),'regenerated PLAN differs from new/PLAN.json beyond bind-rebound receipt hashes'
assert rd(work/'data-rebound/PROFILE.json')==rd(P/'new/PROFILE.json')
layout=work/'parent/layout';runtime=layout/'packing74';runtime.mkdir();data=runtime/'candidate';data.mkdir()
for n in ['replay.py','freeze_spec.py','audit_mixed.py','independent_core.py','geometry_controls.py','audit_fast.py']:shutil.copy2(P/n,runtime/n)
for n in ['code','construction']:shutil.copytree(P/n,runtime/n)
(runtime/'inputs').mkdir();shutil.copy2(P/'inputs/PR589-EXPECTED.json',runtime/'inputs/PR589-EXPECTED.json')
for n in ['PLAN.json','SPEC.json','PROFILE.json','OWNERS.json.gz','DISPATCH.json','CONSTRUCTION.json','GLOBAL-TEMPLATE.json.gz']:shutil.copy2((P/'new' if n in ('PLAN.json','SPEC.json','PROFILE.json') else P)/n,data/n)
shutil.copytree(nat['extra'],runtime/'native-extra')
base=nat['base']
run('strict-t74',runtime/'replay.py','--data',data,'--work',work/'strict','--local',base/'local')
run('geometry-controls',runtime/'geometry_controls.py','--source',layout/'joint1148-round45/source/research/complex-k492-owner-repair/vendor/multicold','--strict',work/'strict','--out',work/'GEOMETRY-CONTROLS.json')
chain.join()
if chain_err:raise chain_err[0]
r=rd(work/'strict/RESULT.json');assert r['status']=='PASS_STRICT_MIXED_T74_EXACT_FILL' and r['kappa']==rd(P/'CLAIM.json')['kappa'];assert len(rd(work/'GEOMETRY-CONTROLS.json')['rejected'])==6
result=dict(status='PASS_T74_EXACT_FILL_COMPLETE_FINITE_ADMISSION',kappa=r['kappa'],kappa_decimal=r['kappa_decimal'],manifest_sha256=sha(P/'MANIFEST.json'),native_reuse=dict(base=bool(a.base_native_from),extra=bool(a.extra_native_from)),provider_verification=pr['status'],roles=r['independent']['roles'],prefix_bits=r['independent']['prefix_bits'],charged_prefix_bits=r['independent']['charged_prefix_bits'],physical_row_coefficient=r['independent']['physical_row_coefficient'],row_limit=r['independent']['row_limit'],controls=dict(admission=114,bit=12,controller=15,independent_owner=8,geometry=6),stages=stages,scope=rd(P/'CLAIM.json')['scope'])
(work/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(result['status'],result['kappa_decimal'],flush=True)
