#!/usr/bin/env python3
"""Rebuild the pinned upstream and every composed finite check offline."""
from pathlib import Path, PurePosixPath
import argparse,concurrent.futures,hashlib,json,os,subprocess,sys,time,zipfile
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent

def load(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(b,s):
 if not b:raise RuntimeError(s)
def norm(x):
 if isinstance(x,dict):return {k:norm(v)for k,v in x.items()if k not in ('seconds','local_scalar_stream')}
 if isinstance(x,list):return list(map(norm,x))
 return x

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--cxx',default='g++');ap.add_argument('--boost-include',type=Path);a=ap.parse_args()
 need(__debug__,'Assertions must be enabled');need(sys.version_info>=(3,11),'Python 3.11+');need(sys.byteorder=='little','Little-endian host required')
 out=a.output.resolve();need(out!=HERE and HERE not in out.parents,'Output outside package');need(not out.exists(),'Fresh output required')
 manifest=load(HERE/'MANIFEST.json')['files'];actual={p.relative_to(HERE).as_posix()for p in HERE.rglob('*')if p.is_file()and p.name!='MANIFEST.json'}
 need(actual==set(manifest),'Package membership mismatch')
 for n,h in manifest.items():need(sha(HERE/n)==h,'Package hash mismatch: '+n)
 result=load(HERE/'RESULT.json');out.mkdir(parents=True)
 for d in ['logs','bin','tmp','upstream','base','sinks','kernels','retimed','transported','restored','final']:(out/d).mkdir()
 env=os.environ.copy();env.update(TEMP=str(out/'tmp'),TMP=str(out/'tmp'),PYTHONUTF8='1',PYTHONDONTWRITEBYTECODE='1')
 start=time.monotonic()
 def run(label,cmd):
  print(label,flush=True)
  with (out/'logs'/(label+'.log')).open('w',encoding='utf-8')as f:r=subprocess.run(list(map(str,cmd)),cwd=out,env=env,stdout=f,stderr=subprocess.STDOUT)
  need(r.returncode==0,label+' failed; inspect '+str(out/'logs'/(label+'.log')))
 archive=load(HERE/'vendor/PR276-SOURCE-MANIFEST.json')['files']
 with zipfile.ZipFile(HERE/'vendor/pr276-source.zip')as z:
  need(len(z.namelist())==len(archive)and set(z.namelist())==set(archive),'Upstream archive membership')
  for info in z.infolist():
   n=PurePosixPath(info.filename);need(not n.is_absolute()and '..'not in n.parts and '\\'not in info.filename and ':'not in info.filename,'Unsafe archive path')
   data=z.read(info);need(hashlib.sha256(data).hexdigest()==archive[info.filename],'Upstream hash: '+info.filename)
   p=out/'upstream'/info.filename;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
 own=load(out/'upstream/MANIFEST.json')['files']
 need(all(archive.get(n)==h for n,h in own.items()),'Upstream internal manifest')
 def exe(name):return out/'bin'/(name+('.exe'if os.name=='nt'else''))
 def compile_one(p):
  cmd=[a.cxx,'-O2','-std=c++17','-I',HERE/'vendor']
  if a.boost_include:cmd+=['-I',a.boost_include.resolve()]
  run('compile-'+p.stem,cmd+[p,'-o',exe(p.stem)])
 def compile_all():
  with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:list(pool.map(compile_one,sorted((HERE/'code').glob('*.cpp'))))
 with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:
  jobs=[pool.submit(compile_all),pool.submit(run,'upstream-nine-stages',[sys.executable,'-X','utf8','-B',out/'upstream/verify.py','--output',out/'upstream-audit'])]
  for j in jobs:j.result()
 need(load(out/'upstream-audit/verification.json')['inputs_unchanged'],'Upstream mutated')
 run('export',[sys.executable,'-X','utf8','-B',HERE/'code/export276.py',out/'upstream',out/'base'])
 need(sha(out/'base/249-records.bin')==result['baseline_word_sha256'],'Baseline word mismatch')
 run('sink-transform',[exe('sink-transform'),out/'base',HERE/'inputs/sinks.json',out/'sinks'])
 run('sink-independent',[exe('sink-audit'),out/'base',out/'sinks',out/'SINK-AUDIT.json'])
 need(sha(out/'sinks/249-records.bin')==result['sink_word_sha256'],'Sink word mismatch')
 run('kernel-remap',[exe('kernel-remap'),HERE/'inputs/kernel-original.json',out/'sinks',out/'mapped.json'])
 need(load(out/'mapped.json')==load(HERE/'inputs/kernel-remapped.json'),'Frozen remap mismatch')
 run('kernel-transform',[exe('kernel-transform'),out/'sinks',out/'mapped.json',out/'kernels'])
 need(sha(out/'kernels/COHORT249-RECORDS.bin')==result['kernel_word_sha256'],'Kernel word mismatch')
 run('retiming',[exe('retime279'),out/'sinks',out/'kernels',HERE/'inputs/retiming.json',out/'retimed'])
 need(sha(out/'retimed/COHORT249-RECORDS.bin')==result['retimed_word_sha256'],'Retimed word mismatch')
 run('transport',[exe('transport'),out/'sinks',out/'retimed',out/'sinks/OLD-TO-NEW.json',HERE/'inputs/entrances60.json',out/'transported'])
 need(sha(out/'transported/COHORT249-RECORDS.bin')==result['transported_word_sha256'],'Transported word mismatch')
 run('restore',[exe('restore'),out/'sinks',out/'transported',out/'restored'])
 need(sha(out/'restored/COHORT249-RECORDS.bin')==result['restored_word_sha256'],'Restored word mismatch')
 for name in ['249-records.bin','frames.json','249-DONOR-OWNERSHIP.json']:(out/'restored'/name).write_bytes((out/'sinks'/name).read_bytes())
 run('targets',[exe('target'),out/'restored',out/'restored',HERE/'inputs/targets220.json',out/'final',out/'base/249-records.bin',out/'sinks/OLD-TO-NEW.json'])
 run('target-grams',[exe('target-gram'),out/'restored',out/'final',out/'final/TARGET279-GRAM.json'])
 D=out/'final';X=out/'restored' 
 need(sha(D/'COHORT249-RECORDS.bin')==result['final_word_sha256'],'Retimed word mismatch')
 jobs=[('independent-legality',[exe('legality'),X,D,D/'LEGALITY.json']),('independent-prefix',[exe('prefix'),X,D,D/'PREFIX.json']),('bank-charts',[exe('banks'),X,D/'COHORT249-INITIAL.json',D/'COHORT249-FRAMES.json',D,'gen4-composed-endpoints120']),('five-stage-columns',[exe('global'),D/'COHORT249-RECORDS.bin',X/'249-states.json',D/'GLOBAL.json'])]
 with concurrent.futures.ThreadPoolExecutor(max_workers=3)as pool:list(pool.map(lambda j:run(*j),jobs))
 run('exact-price',[exe('price'),D/'COHORT249-REPLAY.json',D/'BANK-REVIEW.json',D/'PRICE.json'])
 run('finite-invoice',[exe('finite'),D/'COHORT249-RECORDS.bin',D/'PRICE.json',D/'BANK-REVIEW.json',D/'GLOBAL.json',D/'FINITE.json'])
 run('fixed-prime',[exe('fixed'),D/'PRICE.json',D/'FINITE.json',D/'FIXED-PRICE.json'])
 need(load(D/'FIXED-PRICE.json')['kappa']==result['kappa'],'Final exact kappa mismatch')
 receipts={}
 for p in sorted((HERE/'expected').glob('*.json')):
  actual=D/p.name;need(actual.is_file(),'Missing receipt '+p.name);got=norm(load(actual));want=norm(load(p));need(got==want,'Receipt mismatch '+p.name);receipts[p.name]=got
 for n,h in manifest.items():need(sha(HERE/n)==h,'Package mutated: '+n)
 cert=dict(status='PASS_SOURCE_REGENERATED_COMPOSITION',kappa=result['kappa'],kappa_decimal=result['kappa_decimal'],upstream_fresh_nine_stages=True,retained_all_size_assumptions=True,lean_certificate=False,final_word_sha256=result['final_word_sha256'],package_manifest_sha256=sha(HERE/'MANIFEST.json'),seconds=time.monotonic()-start,receipts=receipts)
 (out/'CERTIFICATE.json').write_text(json.dumps(cert,indent=2)+'\n',encoding='utf-8')
 print('PASS kappa = '+result['kappa_decimal'],flush=True)
if __name__=='__main__':main()
