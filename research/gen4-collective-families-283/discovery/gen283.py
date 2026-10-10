#!/usr/bin/env python3
"""Pin-generating twin of PR283's verify.py for a staged package: same stage order and commands, but recorded instead of asserted.
Reuses an existing upstream audit/export (--reuse DIR) to save the nine-stage replay. Writes fresh receipts into <pkg>/expected,
updates RESULT.json shas/kappa and inputs/kernel-remapped.json, then regenerates MANIFEST.json."""
from pathlib import Path, PurePosixPath
import argparse,concurrent.futures,hashlib,json,os,shutil,subprocess,sys,time,zipfile
sys.dont_write_bytecode=True
def load(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(b,s):
 if not b:raise RuntimeError(s)
def norm(x):
 if isinstance(x,dict):return {k:norm(v)for k,v in x.items()if k not in ('seconds','local_scalar_stream')}
 if isinstance(x,list):return list(map(norm,x))
 return x
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--pkg',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--reuse',type=Path);ap.add_argument('--cxx',default='clang++');ap.add_argument('--boost-include',type=Path);ap.add_argument('--stop-after',default='');ap.add_argument('--skip-audit',action='store_true');a=ap.parse_args()
 HERE=a.pkg.resolve();out=a.output.resolve();need(not out.exists(),'Fresh output required');result=load(HERE/'RESULT.json');out.mkdir(parents=True)
 for d in ['logs','bin','tmp','upstream','base','sinks','kernels','retimed','transported','restored','final']:(out/d).mkdir()
 env=os.environ.copy();env.update(TEMP=str(out/'tmp'),TMP=str(out/'tmp'),PYTHONUTF8='1',PYTHONDONTWRITEBYTECODE='1');start=time.monotonic();timing={}
 def run(label,cmd):
  t=time.monotonic();print(label,flush=True)
  with (out/'logs'/(label+'.log')).open('w',encoding='utf-8')as f:r=subprocess.run(list(map(str,cmd)),cwd=out,env=env,stdout=f,stderr=subprocess.STDOUT)
  timing[label]=time.monotonic()-t;need(r.returncode==0,label+' failed; inspect '+str(out/'logs'/(label+'.log')))
 def exe(name):return out/'bin'/name
 def compile_one(p):
  cmd=[a.cxx,'-O2','-std=c++17','-I',HERE/'vendor']
  if a.boost_include:cmd+=['-I',a.boost_include.resolve()]
  run('compile-'+p.stem,cmd+[p,'-o',exe(p.stem)])
 with concurrent.futures.ThreadPoolExecutor(max_workers=4)as pool:list(pool.map(compile_one,sorted((HERE/'code').glob('*.cpp'))))
 if a.skip_audit:
  archive=load(HERE/'vendor/PR276-SOURCE-MANIFEST.json')['files']
  with zipfile.ZipFile(HERE/'vendor/pr276-source.zip')as z:
   for info in z.infolist():
    data=z.read(info);need(hashlib.sha256(data).hexdigest()==archive[info.filename],'Upstream hash: '+info.filename)
    p=out/'upstream'/info.filename;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
  run('export',[sys.executable,'-X','utf8','-B',HERE/'code/export276.py',out/'upstream',out/'base'])
 elif a.reuse:
  for d in ('upstream','base','upstream-audit'):
   shutil.rmtree(out/d,ignore_errors=True);shutil.copytree(a.reuse/d,out/d)
  print('reused upstream audit + export from',a.reuse,flush=True)
 else:
  archive=load(HERE/'vendor/PR276-SOURCE-MANIFEST.json')['files']
  with zipfile.ZipFile(HERE/'vendor/pr276-source.zip')as z:
   for info in z.infolist():
    data=z.read(info);need(hashlib.sha256(data).hexdigest()==archive[info.filename],'Upstream hash: '+info.filename)
    p=out/'upstream'/info.filename;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
  run('upstream-nine-stages',[sys.executable,'-X','utf8','-B',out/'upstream/verify.py','--output',out/'upstream-audit'])
  need(load(out/'upstream-audit/verification.json')['inputs_unchanged'],'Upstream mutated')
  run('export',[sys.executable,'-X','utf8','-B',HERE/'code/export276.py',out/'upstream',out/'base'])
 need(sha(out/'base/249-records.bin')==result['baseline_word_sha256'],'Baseline word mismatch')
 run('sink-transform',[exe('sink-transform'),out/'base',HERE/'inputs/sinks.json',out/'sinks'])
 run('sink-independent',[exe('sink-audit'),out/'base',out/'sinks',out/'SINK-AUDIT.json'])
 need(sha(out/'sinks/249-records.bin')==result['sink_word_sha256'],'Sink word mismatch')
 run('kernel-remap',[exe('kernel-remap'),HERE/'inputs/kernel-original.json',out/'sinks',out/'mapped.json'])
 run('kernel-transform',[exe('kernel-transform'),out/'sinks',out/'mapped.json',out/'kernels'])
 new=dict(kernel_word_sha256=sha(out/'kernels/COHORT249-RECORDS.bin'))
 if a.stop_after=='kernel':print(json.dumps(new));return
 run('retiming',[exe('retime279'),out/'sinks',out/'kernels',HERE/'inputs/retiming.json',out/'retimed']);new['retimed_word_sha256']=sha(out/'retimed/COHORT249-RECORDS.bin')
 run('transport',[exe('transport'),out/'sinks',out/'retimed',out/'sinks/OLD-TO-NEW.json',HERE/'inputs/entrances60.json',out/'transported']);new['transported_word_sha256']=sha(out/'transported/COHORT249-RECORDS.bin')
 run('restore',[exe('restore'),out/'sinks',out/'transported',out/'restored']);new['restored_word_sha256']=sha(out/'restored/COHORT249-RECORDS.bin')
 for name in ['249-records.bin','frames.json','249-DONOR-OWNERSHIP.json']:(out/'restored'/name).write_bytes((out/'sinks'/name).read_bytes())
 run('targets',[exe('target'),out/'restored',out/'restored',HERE/'inputs/targets220.json',out/'final',out/'base/249-records.bin',out/'sinks/OLD-TO-NEW.json'])
 run('target-grams',[exe('target-gram'),out/'restored',out/'final',out/'final/TARGET279-GRAM.json'])
 D=out/'final';X=out/'restored';new['final_word_sha256']=sha(D/'COHORT249-RECORDS.bin')
 jobs=[('independent-legality',[exe('legality'),X,D,D/'LEGALITY.json']),('independent-prefix',[exe('prefix'),X,D,D/'PREFIX.json']),('bank-charts',[exe('banks'),X,D/'COHORT249-INITIAL.json',D/'COHORT249-FRAMES.json',D,'gen4-composed-endpoints120']),('five-stage-columns',[exe('global'),D/'COHORT249-RECORDS.bin',X/'249-states.json',D/'GLOBAL.json'])]
 with concurrent.futures.ThreadPoolExecutor(max_workers=3)as pool:list(pool.map(lambda j:run(*j),jobs))
 run('exact-price',[exe('price'),D/'COHORT249-REPLAY.json',D/'BANK-REVIEW.json',D/'PRICE.json'])
 run('finite-invoice',[exe('finite'),D/'COHORT249-RECORDS.bin',D/'PRICE.json',D/'BANK-REVIEW.json',D/'GLOBAL.json',D/'FINITE.json'])
 run('fixed-prime',[exe('fixed'),D/'PRICE.json',D/'FINITE.json',D/'FIXED-PRICE.json'])
 fp=load(D/'FIXED-PRICE.json');new['kappa']=fp['kappa'];new['kappa_decimal']=fp.get('kappa_decimal',result['kappa_decimal'])
 # --- re-pin the staged package
 changed=[]
 for k,v in new.items():
  if result.get(k)!=v:changed.append((k,result.get(k),v));result[k]=v
 result['gen4coll_composition']='PR283 package + gen4coll collective families (see inputs/kernel-original.json gen4coll_added_rows)'
 (HERE/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
 shutil.copy(out/'mapped.json',HERE/'inputs/kernel-remapped.json')
 for p in sorted((HERE/'expected').glob('*.json')):
  actual=D/p.name;need(actual.is_file(),'Missing receipt '+p.name)
  if norm(load(actual))!=norm(load(p)):changed.append(('expected/'+p.name,'receipt','replaced'))
  shutil.copy(actual,p)
 files={}
 for p in HERE.rglob('*'):
  if p.is_file()and p.name!='MANIFEST.json':files[p.relative_to(HERE).as_posix()]=sha(p)
 man=load(HERE/'MANIFEST.json');man['files']=dict(sorted(files.items()));(HERE/'MANIFEST.json').write_text(json.dumps(man,indent=1)+'\n')
 (out/'GEN283-SUMMARY.json').write_text(json.dumps(dict(changed_pins=changed,timing=timing,seconds=time.monotonic()-start),indent=1,default=str)+'\n')
 print('GENERATED; kappa',new['kappa'],new['kappa_decimal'],'changed pins',len(changed),'seconds',time.monotonic()-start,flush=True)
if __name__=='__main__':main()
