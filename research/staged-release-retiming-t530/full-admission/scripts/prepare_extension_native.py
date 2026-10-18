# SPDX-License-Identifier: Apache-2.0
"""Two fresh changed-word native chains; explicit authenticated parent reuse.
Yiyang (@Lyy-iiis), with substantial OpenAI Codex assistance.
Derived from the PR2839/PR2848 native preparation lineage, retaining validators.
"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from importlib import metadata
import argparse,hashlib,json,gzip,os,platform,shutil,subprocess,sys,time
sys.dont_write_bytecode=True
SOURCE_SHA='fb47533a401d1d13719be8b9aab91fe5313931ca62d40dba336eab6a96275aa0'
SOURCE_FILES=654
SOURCE_COMMIT='local-staged644-660-two-release-retimings'
PARENT_SHA='e0eefc96567fbb45e19e6de0ca295381dbe0e686c08ddc783639b065c7c791d4'
OLD_RECEIPT_SHA='f90cafe84385533a0eeb96356f385b646f402ff85cd05154c47a81c783023d9d'
def need(ok,why):
 if not ok:raise ValueError(why)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b)if p.suffix=='.gz'else b)
def write(p,v):p.write_text(json.dumps(v,sort_keys=True,indent=2)+'\n')
def tree(p,exclude=()):
 out={}
 for f in sorted(p.rglob('*')):
  need(not f.is_symlink(),'no cache/source symlinks')
  if f.is_file()and f.relative_to(p).as_posix()not in exclude:out[f.relative_to(p).as_posix()]=sha(f)
 return out

def main():
 ap=argparse.ArgumentParser()
 for n in ['source','retained-cache','retained-receipt','out']:ap.add_argument('--'+n,type=Path,required=True)
 ap.add_argument('--jobs',type=int,default=2);a=ap.parse_args();source=a.source.resolve();out=a.out.resolve();oldcache=a.retained_cache.resolve()
 need(not sys.flags.optimize and 1<=a.jobs<=2,'assertions enabled and max2 jobs')
 need(sha(source/'MANIFEST.json')==SOURCE_SHA and len(read(source/'MANIFEST.json'))==SOURCE_FILES and tree(source,('MANIFEST.json',))==read(source/'MANIFEST.json'),'complete immutable derived source')
 need(not list(source.rglob('__pycache__'))and not list(source.rglob('*.pyc')),'source free of bytecode and cache folders')
 before=tree(source);oldreceipt=read(a.retained_receipt)
 need(sha(a.retained_receipt)==OLD_RECEIPT_SHA and tree(oldcache)==oldreceipt['cache_files'],'complete PR2848 retained native/cache evidence')
 old=source/'vendor/pr1297';need(sha(old/'MANIFEST.json')==PARENT_SHA and tree(old,('MANIFEST.json',))==read(old/'MANIFEST.json'),'unchanged retained source')
 prdir=oldcache/'_receipts'/PARENT_SHA;need(sha(prdir/'RECEIPT.json')==oldreceipt['retained_parent_receipt_sha256'],'retained parent receipt identity');pr=read(prdir/'RECEIPT.json')
 need(pr['vendor_manifest_sha256']==PARENT_SHA and pr['claim_sha256']==sha(old/'CLAIM.json'),'retained parent source claim')
 for name,h in pr['files'].items():need(sha(prdir/name)==h,'retained parent result binding')
 need(read(prdir/'RESULT.json')['status']=='PASS_GLOBAL_MIXED_X54_FUSIONS_NATIVE_AND_STRICT_ADMISSION' and read(prdir/'RESULT.json')['kappa']==read(old/'CLAIM.json')['kappa'],'retained full parent admission')
 pstages=read(prdir/'STAGES.json');need(len(pstages)==16 and all(s['exit_code']==0 for s in pstages),'all16 retained parent stages')
 need(not out.exists()and not out.is_relative_to(source)and not out.is_relative_to(oldcache),'fresh external native work');out.mkdir(parents=True);cache=out/'native-cache';cache.mkdir()
 steps=['native','ledgers','local-replay','wrappers','phases']
 for tag,name in [('base','gauge44-word.json.gz'),('extra','extra-word.json.gz')]:
  word=old/name;key=sha(word);need(pr['words'][tag]==key,'retained word hash');entry=oldcache/key
  need(read(entry/'local/FULL-WORD.json.gz')==read(word),'retained complete literal word');st=read(entry/'STEPS.json');need([s['step']for s in st]==steps and all(s['exit_code']==0 for s in st),'retained native five stages')
  cj=read(entry/'CACHE.json');need(cj['word_sha256']==key and cj['files']==tree(entry,('CACHE.json',)),'retained full native files')
  shutil.copytree(entry,cache/key)
 shutil.copytree(prdir,cache/'_receipts'/PARENT_SHA)
 versions={}
 for name in ['numpy','scipy','sympy','mpmath','psutil','gmpy2']:
  try:versions[name]=metadata.version(name)
  except metadata.PackageNotFoundError:versions[name]=None
 write(out/'ENVIRONMENT.json',dict(python=platform.python_version(),executable=sys.executable,dependency_versions=versions,assertions_enabled=True))
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',PYTHONINTMAXSTRDIGITS='0',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
 for k in ['PYTHONOPTIMIZE','WITNESS_SPEC','WITNESS_DISCOVER','WITNESS_RECORD']:env.pop(k,None)
 driver=source/'new/fastnative/run_native.py';start=time.monotonic();stages=[];words={t:source/('new/borrow/words/BORROW-WORD-43'+t+'.json.gz')for t in ['base','extra']}
 def fresh(tag):
  word=words[tag];work=out/('fresh-'+tag);cmd=[sys.executable,'-B',str(driver),str(word),str(work)];log=out/('native-'+tag+'.log');begin=time.monotonic()
  with log.open('w')as f:r=subprocess.run(cmd,cwd=out,env=env,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT)
  need(r.returncode==0,'fresh native '+tag+' failed; '+str(log));res=read(work/'RESULT.json');need(res['status']=='PASS_COMPLETE_T74_NATIVE_REPLAY'and res['word_sha256']==sha(word),'fresh native result')
  entry=cache/sha(word);shutil.copytree(work/'native',entry);need(read(entry/'local/FULL-WORD.json.gz')==read(word),'fresh complete literal word')
  st=read(entry/'STEPS.json');need([s['step']for s in st]==steps and all(s['exit_code']==0 for s in st),'fresh native five stages')
  checks=read(entry/'local/LOCAL-CHECKS.json');can=read(entry/'local/CANONICAL-WORD.json.gz')
  need(can['R']==408 and len(can['centers'])==8 and len(can['zero_buffers'])==91,'complete physical ABI')
  for orientation in ['forward','backward']:need(checks[orientation]['all_columns']==632 and checks[orientation]['paid_profile']==read(word)['report']['local_profile'],'actual all-column native profile')
  write(entry/'CACHE.json',dict(word_sha256=sha(word),files=tree(entry)))
  rec=dict(name='fresh-current-'+tag,exit_code=0,command=cmd,script_sha256=sha(driver),log_sha256=sha(log),result_sha256=sha(work/'RESULT.json'),seconds=time.monotonic()-begin);print('PASS',rec['name'],flush=True);return rec
 with ThreadPoolExecutor(max_workers=a.jobs)as pool:stages=list(pool.map(fresh,['base','extra']))
 need(tree(source)==before and tree(oldcache)==oldreceipt['cache_files']and sha(a.retained_receipt)==OLD_RECEIPT_SHA,'read-only input drift')
 rec=dict(status='PASS_COMPOSED_FRESH_NATIVE_PROVIDERS_AND_AUTHENTICATED_CACHE',source_commit=SOURCE_COMMIT,manifest_sha256=SOURCE_SHA,providers={t:dict(word_sha256=sha(w),complete_native_files=tree(cache/sha(w),('CACHE.json',)))for t,w in words.items()},retained_parent_receipt_sha256=sha(cache/'_receipts'/PARENT_SHA/'RECEIPT.json'),cache_files=tree(cache),fresh_current_provider_count=2,fresh_retained_native_count=0,reused_retained_native_count=2,fresh_retained_parent=False,reused_retained_parent=True,retained_reuse_receipt_sha256=OLD_RECEIPT_SHA)
 write(out/'NATIVE-RECEIPT.json',rec);write(out/'STAGES.json',stages);write(out/'RESULT.json',dict(status='PASS_TWO_FRESH_SHARED_KERNEL_NATIVE_CHAINS_AUTHENTICATED_PARENT_REUSE',source_manifest_sha256=SOURCE_SHA,native_receipt_sha256=sha(out/'NATIVE-RECEIPT.json'),preparer_sha256=sha(Path(__file__)),environment_sha256=sha(out/'ENVIRONMENT.json'),stages=stages,seconds=time.monotonic()-start,scope='Fresh changed base/extra native chains; two unchanged retained native chains and16-stage parent admission explicitly reused by exact full-tree receipts. No owner/controller/outer admission yet.'))
 print('PASS_TWO_FRESH_SHARED_KERNEL_NATIVE_CHAINS_AUTHENTICATED_PARENT_REUSE',flush=True)
if __name__=='__main__':main()
