#!/usr/bin/env python3
"""Offline native source replay of TI local dirty-response schedules."""
from pathlib import Path,PurePosixPath
import argparse,concurrent.futures,hashlib,json,os,shutil,subprocess,sys,time,zipfile
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent

def load(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(b,s):
 if not b:raise RuntimeError(s)
def write(p,j):Path(p).write_text(json.dumps(j,indent=2)+'\n',encoding='utf-8')
def norm(x):
 if isinstance(x,dict):return{k:norm(v)for k,v in x.items()if k not in('seconds','label','local_scalar_stream')}
 if isinstance(x,list):return list(map(norm,x))
 return x

def main():
 ap=argparse.ArgumentParser(description=__doc__)
 ap.add_argument('--output',type=Path,required=True);ap.add_argument('--cxx',default='g++');ap.add_argument('--boost-include',type=Path)
 ap.add_argument('--reuse-base-output',type=Path,help='Explicitly authenticate exact completed base files/binaries; never counted as fresh base compilation')
 a=ap.parse_args();need(__debug__ and sys.version_info>=(3,11)and sys.byteorder=='little','Unoptimized Python3.11+ little-endian required')
 O=a.output.resolve();need(not O.exists() and O!=HERE and HERE not in O.parents,'Fresh output outside package required')
 M=load(HERE/'MANIFEST.json')['files'];actual={p.relative_to(HERE).as_posix()for p in HERE.rglob('*')if p.is_file()and p!=HERE/'MANIFEST.json'}
 need(actual==set(M),'Package membership')
 for n,h in M.items():need(sha(HERE/n)==h,'Package hash '+n)
 R=load(HERE/'RESULT.json');O.mkdir(parents=True);start=time.monotonic()
 for n in ('logs','tmp','bin','sources','inventory'):(O/n).mkdir()
 env={**os.environ,'TEMP':str(O/'tmp'),'TMP':str(O/'tmp'),'PYTHONDONTWRITEBYTECODE':'1','PYTHONUTF8':'1'}
 def run(label,cmd):
  print(label,flush=True)
  with(O/'logs'/(label+'.log')).open('w',encoding='utf-8')as f:r=subprocess.run(list(map(str,cmd)),cwd=O,env=env,stdout=f,stderr=subprocess.STDOUT)
  need(r.returncode==0,label+' failed; inspect log')
 def extract(name):
  ar=HERE/'vendor'/(name+'.zip');need(sha(ar)==R['archives'][name],'Archive hash '+name)
  entries=load(HERE/'vendor'/(name+'-inventory.json'))['files'];dest=O/'sources'/name;dest.mkdir()
  with zipfile.ZipFile(ar)as z:
   need(len(z.namelist())==len(entries)and set(z.namelist())==set(entries),'Archive membership '+name)
   for info in z.infolist():
    p=PurePosixPath(info.filename);need(not p.is_absolute()and '..'not in p.parts and '\\'not in info.filename and ':'not in info.filename,'Unsafe archive path')
    need((info.external_attr>>16)&0o170000!=0o120000,'Symlink archive entry')
    data=z.read(info);need(hashlib.sha256(data).hexdigest()==entries[info.filename],'Archive member hash '+info.filename)
    q=dest/info.filename;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(data)
  return dest
 base,k37,t10,c304=[extract(n)for n in ('base','response37','transport10','complex304')]
 if a.reuse_base_output:
  B=a.reuse_base_output.resolve();reuse=load(HERE/'REUSE-BASE.json')
  need(reuse['source_package_manifest_sha256']==sha(base/'MANIFEST.json'),'Inherited publication source binding')
  for n,h in reuse['files'].items():need(sha(B/n)==h,'Completed base file '+n)
  need(load(B/'CERTIFICATE.json')['package_manifest_sha256']==reuse['bound_replay_old_manifest_sha256'],'Exact base replay/prose rebind')
 else:
  B=O/'base-replay';cmd=[sys.executable,'-X','utf8','-B',base/'verify.py','--output',B,'--cxx',a.cxx]
  if a.boost_include:cmd+=['--boost-include',a.boost_include.resolve()]
  run('full-inherited-base-source',cmd)
  need(load(B/'CERTIFICATE.json')['package_manifest_sha256']==sha(base/'MANIFEST.json'),'Fresh base manifest binding')
 bc=load(B/'CERTIFICATE.json')
 need(bc['status']=='PASS_SOURCE_BOUND_WEIGHTED1915_RANK_MODULAR159_RETIMING112_AND_EXACT47','Completed inherited base')
 need(bc['word_sha256']==sha(B/'retiming51/COHORT249-RECORDS.bin')==R['base_word_sha256'],'Literal admitted base word')
 if a.reuse_base_output:
  need(bc['kappa']==load(base/'RESULT.json')['kappa'],'Completed base claim binding')
 need(bc['inventory_receipt_sha256']['FIXED-PRICE.json']==sha(B/'inventory/FIXED-PRICE.json')and len(load(B/'inventory/FIXED-PRICE.json')['strict_constraints'])==47,'Completed base exact47')
 # These tools are always freshly compiled, including in explicit base-reuse mode.
 sources={p.stem:p for p in(HERE/'code').glob('*.cpp')}
 sources.update({n:base/'code'/(n+'.cpp')for n in ('export-guard','banks','finite')})
 sources['global-exact']=k37/'code/global.cpp'
 sources['frame-prime-guard']=B/'round5-source/utility/frame-prime-guard.cpp'
 sources['local-response-transport']=t10/'local-response-transport.cpp'
 # An authenticated reuse retains the exact utility source from the frozen base archive.
 if a.reuse_base_output:
  with zipfile.ZipFile(base/'vendor/round5.zip')as z:
   data=z.read('utility/frame-prime-guard.cpp')
  need(hashlib.sha256(data).hexdigest()==load(base/'vendor/ROUND5-ARCHIVE-MANIFEST.json')['files']['utility/frame-prime-guard.cpp'],'Prime utility frozen source')
  u=O/'sources/frame-prime-guard.cpp';u.write_bytes(data);sources['frame-prime-guard']=u
 exe=lambda n:O/'bin'/(n+('.exe'if os.name=='nt'else''))
 def compile_one(item):
  n,p=item;cmd=[a.cxx,'-O2','-std=c++17','-I',HERE/'code','-I',base/'vendor','-I',base/'code']
  if a.boost_include:cmd+=['-I',a.boost_include.resolve()]
  run('compile-'+n,cmd+[p,'-o',exe(n)])
 with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:list(pool.map(compile_one,sorted(sources.items())))
 current=B/'retiming51';reorder_receipts=[]
 for i in (1,2):
  D=O/('reorder'+str(i));sel=HERE/'inputs'/('reorder'+str(i)+'.json')
  run('frozen-reorder-'+str(i),[exe('reorder-emit'),current,sel,D]);need(sha(D/'COHORT249-RECORDS.bin')==R['reordered_words'][i-1],'Actual reordered word')
  run('independent-commutation-controls-'+str(i),[exe('reorder-check'),current,D,D/'COMMUTATION-CHECK.json'])
  need(load(D/'COMMUTATION-CHECK.json')['negative_controls_rejected']==6,'Executed six commuting controls')
  run('original-integer-source-spans-'+str(i),[exe('source-span'),D,sel,D/'SOURCE-SPANS.json'])
  reorder_receipts.append({n:sha(D/n)for n in ('FROZEN-REORDER.json','COMMUTATION-CHECK.json','SOURCE-SPANS.json')});current=D
 kr=O/'response37-replay';cmd=[sys.executable,'-X','utf8','-B',k37/'replay37.py','--predecessor',current,'--output',kr,'--cxx',a.cxx,'--include',base/'vendor']
 if a.boost_include:cmd+=['--include',a.boost_include.resolve()]
 run('response37-fresh-source-and-controls',cmd)
 kc=load(kr/'CERTIFICATE.json');need(kc['status']=='PASS_SOURCE_BOUND_RANK_MODULAR37_NATIVE_REPLAY'and kc['compiled_here']and kc['all_controls_passed']and kc['source_baseline_restored'],'Fresh37 complete admission')
 current=kr/kc['final_directory'];need(sha(current/'COHORT249-RECORDS.bin')==R['gauged_word_sha256'],'Actual37 word')
 tr=O/'transport10-replay';run('ten-local-response-transports-and-controls',[sys.executable,'-X','utf8','-B',t10/'compose.py','--predecessor',current,'--native-bin',O/'bin','--output',tr])
 tc=load(tr/'CERTIFICATE.json');need(tc['status']=='PASS_FROZEN_LOCAL_RESPONSE_TRANSPORT_WITH_EXECUTED_CONTROLS'and tc['integer_plus2_rejected']and tc['omitted_compensation_rejected'],'Ten transports and both integer/omission controls')
 current=tr/'final';need(sha(current/'COHORT249-RECORDS.bin')==R['word_sha256'],'Final literal word')
 C=O/'complex304-replay';cmd=[sys.executable,'-X','utf8','-B',c304/'verify-complex.py','--output',C,'--cxx',a.cxx]
 if a.boost_include:cmd+=['--boost-include',a.boost_include.resolve()]
 run('actual-complex304-fresh-source-and-controls',cmd)
 cc=load(C/'CERTIFICATE.json');need(cc['status']=='PASS_FRESH_SOURCE_BOUND_STRONGER_COMPLEX_ADMISSION'and cc['manifest_sha256']==sha(c304/'MANIFEST.json'),'Actual complex source admission')
 need(cc['native_sha256']==sha(C/'NATIVE.json')and cc['program_compressed_sha256']==R['complex_program_sha256']and load(C/'NATIVE.json')['fourier_saving']==R['complex_saving'],'Actual complex program native binding')
 run('actual-guard-view',[sys.executable,'-X','utf8','-B',base/'helpers/prepare-actual-guard.py',current,O/'actual-guard'])
 run('all-actual-frame-state-rank-guards',[exe('export-guard'),O/'actual-guard',O/'ACTUAL-GUARD.json'])
 D=O/'inventory'
 for name in ('249-states.json','frames.json','249-DONOR-OWNERSHIP.json','COHORT249-RECORDS.bin','COHORT249-INITIAL.json','COHORT249-FINAL.json','COHORT249-FRAMES.json','COHORT249-REPLAY.json'):shutil.copyfile(current/name,D/name)
 shutil.copyfile(current/'COHORT249-RECORDS.bin',D/'249-records.bin')
 st=load(D/'249-states.json');st['final']=load(D/'COHORT249-FINAL.json');write(D/'249-states.json',st)
 run('all-final-global-columns',[exe('global-exact'),D/'COHORT249-RECORDS.bin',D/'249-states.json',D/'GLOBAL.json'])
 rec=load(D/'COHORT249-REPLAY.json');guard=load(O/'ACTUAL-GUARD.json')
 need({str(k):v for k,v in load(D/'GLOBAL.json')['local_raw_H']}==rec['histogram']==guard['histogram'],'Actual global/physical histogram')
 need(guard['rank_mass']==rec['new_rank_mass']==R['rank_mass'],'Actual physical rank mass')
 run('complete-final-banks',[exe('banks'),D,D/'COHORT249-INITIAL.json',D/'COHORT249-FRAMES.json',D,'ti-local-response-schedules'])
 bank=load(D/'BANK-REVIEW.json');need(bank['actual_helper_roles']==R['helpers']and bank['normalized_stock']==R['normalized_stock']and bank['literal_stock']==R['literal_stock']and bank['new_entrance_rank']==R['entrance_rank'],'Actual bank and entrance stock binding')
 run('exact-final-inventory-price',[exe('price-complex304'),D/'COHORT249-REPLAY.json',D/'BANK-REVIEW.json',C/'NATIVE.json',D/'PRICE.json'])
 run('complete-final-finite-invoice',[exe('finite'),D/'COHORT249-RECORDS.bin',D/'PRICE.json',D/'BANK-REVIEW.json',D/'GLOBAL.json',D/'FINITE.json'])
 run('dual-engine-final-fixed-prime-and47',[exe('fixed-complex304'),D/'PRICE.json',D/'FINITE.json',C/'NATIVE.json',D/'FIXED-PRICE.json'])
 fixed=load(D/'FIXED-PRICE.json');need(fixed['kappa']==R['kappa']and len(fixed['strict_constraints'])==47,'Final exact kappa/all47 binding')
 for p in sorted((HERE/'expected').glob('*.json')):
  actual=O/p.name if p.name=='ACTUAL-GUARD.json'else D/p.name
  need(norm(load(actual))==norm(load(p)),'Exact reference receipt '+p.name)
 for n,h in M.items():need(sha(HERE/n)==h,'Package changed '+n)
 for name in ('base','response37','transport10','complex304'):
  for n,h in load(HERE/'vendor'/(name+'-inventory.json'))['files'].items():need(sha(O/'sources'/name/n)==h,'Extracted source changed '+name+'/'+n)
 if a.reuse_base_output:
  for n,h in reuse['files'].items():need(sha(B/n)==h,'Reused base changed '+n)
 write(O/'CERTIFICATE.json',dict(status='PASS_SOURCE_BOUND_TI_LOCAL_RESPONSE_SCHEDULES_AND_EXACT47',package_manifest_sha256=sha(HERE/'MANIFEST.json'),kappa=R['kappa'],decimal=R['decimal'],word_sha256=R['word_sha256'],base_output_explicitly_reused=bool(a.reuse_base_output),base_certificate_sha256=sha(B/'CERTIFICATE.json'),fresh_extension_compilation=True,reorder_receipts=reorder_receipts,response37_certificate_sha256=sha(kr/'CERTIFICATE.json'),transport10_certificate_sha256=sha(tr/'CERTIFICATE.json'),complex304_certificate_sha256=sha(C/'CERTIFICATE.json'),actual_complex_native_sha256=sha(C/'NATIVE.json'),actual_guard_sha256=sha(O/'ACTUAL-GUARD.json'),inventory_receipts={n:sha(D/n)for n in ('BANK-REVIEW.json','GLOBAL.json','PRICE.json','FINITE.json','FIXED-PRICE.json')},fresh_executable_sha256={p.name:sha(p)for p in(O/'bin').iterdir()if p.is_file()},all_controls_executed=True,conditional=True,lean_certificate=False,published=False,seconds=time.monotonic()-start))
 print('PASS conditional kappa = '+R['decimal'],flush=True)
if __name__=='__main__':main()
