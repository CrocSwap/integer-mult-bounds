"""Fresh pinned baseline, then exact zero-frame target restoration replay."""
import argparse,hashlib,json,os,signal,subprocess,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--base',type=Path,required=True,help='Pinned PR272 research/filtered-kernel-target120 directory');ap.add_argument('--cleanup-base',type=Path,required=True,help='Pinned PR271 research/cleanup-sandwich-272 directory');ap.add_argument('--output',type=Path,required=True);ap.add_argument('--cxx',default='g++');ap.add_argument('--boost-include',type=Path);args=ap.parse_args()
assert not sys.flags.optimize,'assertions required'
BASE=args.base.resolve();CLEAN=args.cleanup_base.resolve();OUT=args.output.resolve();START=time.monotonic()
assert not OUT.exists(),'choose a fresh output directory'
assert HERE not in OUT.parents and BASE not in OUT.parents,'output must be outside source packages'
def load(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(BASE/'MANIFEST.json')=='c235b9c0bd17a369fa6fd6c936ea8bf17bbb8085bca65e2bf2b3530c44fcb199','pinned baseline manifest'
source=load(HERE/'SOURCE.json');
for name,h in source['cleanup']['files'].items():assert sha(CLEAN/name)==h,('pinned cleanup file',name)
manifest=load(HERE/'MANIFEST.json')['files']
assert {p.relative_to(HERE).as_posix() for p in HERE.rglob('*') if p.is_file() and p.name!='MANIFEST.json'}==set(manifest),'package inventory'
for name,h in manifest.items():assert sha(HERE/name)==h,name
OUT.mkdir(parents=True)
for name in ['logs','review','compiler','temporal']:(OUT/name).mkdir()
def run(name,cmd):
 print(name,flush=True)
 with (OUT/'logs'/(name+'.log')).open('w') as f:
  p=subprocess.Popen(list(map(str,cmd)),cwd=OUT,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
  try:rc=p.wait(timeout=min(600,max(1,3600-(time.monotonic()-START))))
  except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGTERM);p.wait();raise RuntimeError(name+' timed out')
  assert rc==0,(name,rc)
B=OUT/'baseline272';cmd=[sys.executable,'-B',BASE/'verify.py','--output',B,'--cxx',args.cxx]
if args.boost_include:cmd+=['--boost-include',args.boost_include.resolve()]
run('00-fresh-baseline272',cmd)
cert=load(B/'CERTIFICATE.json');assert cert['status']=='PASS_NINE_NATIVE_CHECKERS_EXACT_RETIMING_AND_PINNED_RECEIPTS' and cert['baseline_regenerated_from_source']
assert cert['kappa']=='712074434532274423885827/1000000000000000000000000000'
D=OUT/'cleanup271';run('01-pinned-cleanup271',[sys.executable,'-B',CLEAN/'verify.py','--base',BASE,'--replay',B,'--output',D,'--boost-include',args.boost_include.resolve() if args.boost_include else Path('/usr/include'),'--cxx',args.cxx]);assert load(D/'CERTIFICATE.json')['kappa']=='713662156389609974540991/1000000000000000000000000000'
X=D/'export';LEAD=OUT/'lead';binary=lambda n:B/'bin'/n
run('01-retiming',[sys.executable,'-B',HERE/'code/plateau_retiming.py',X,D/'lead',HERE/'selection.json',LEAD])
run('02-target-caps',[sys.executable,'-B',HERE/'code/verify_target_roles.py',X,LEAD])
run('03-integer-spans',[sys.executable,'-B',HERE/'code/verify_plateau_spans.py',X,LEAD,LEAD/'PLATEAU-RETIMING.json'])
run('04-legality',[binary('cohort-legality-independent'),X,LEAD,OUT/'review/INDEPENDENT-LEGALITY.json'])
run('05-prefix',[binary('cohort-prefix-independent'),X,LEAD,OUT/'review/INDEPENDENT-PREFIX.json'])
run('06-banks',[binary('cohort-bank-review'),X,LEAD/'COHORT249-INITIAL.json',LEAD/'COHORT249-FRAMES.json',OUT/'compiler','zero_frame_target_restores'])
run('06b-cleanup-endpoints',[sys.executable,'-B',HERE/'code/verify_cleanup_endpoints.py',B,D,OUT,CLEAN])
run('07-five-stage',[binary('cohort-five-stage-columns'),LEAD/'COHORT249-RECORDS.bin',OUT/'temporal/COHORT-FIVE-STAGE-COLUMNS.json'])
run('08-price',[binary('cohort-price'),LEAD/'COHORT249-REPLAY.json',LEAD/'COHORT-EXACT-PRICE.json'])
run('09-invoice',[binary('cohort-finite-invoice'),LEAD/'COHORT249-RECORDS.bin',LEAD/'COHORT-EXACT-PRICE.json',OUT/'compiler/BANK-REVIEW.json',OUT/'temporal/COHORT-FIVE-STAGE-COLUMNS.json',OUT/'temporal/COHORT-FINITE-INVOICE.json'])
run('10-fixed-price',[binary('fixed-price'),LEAD/'COHORT-EXACT-PRICE.json',OUT/'temporal/COHORT-FINITE-INVOICE.json',LEAD/'FIXED-PRICE.json'])
run('11-independent-bitsets',[sys.executable,'-B',HERE/'code/independent_word_audit.py',OUT])
fixed=load(LEAD/'FIXED-PRICE.json');retime=load(LEAD/'PLATEAU-RETIMING.json');expected=load(HERE/'expected.json')
result={'status':'PASS_FRESH_BASELINE_CLEANUP_AND_TARGET_RESTORES','kappa':fixed['kappa'],'word_sha256':sha(LEAD/'COHORT249-RECORDS.bin'),'histogram_delta':retime['delta'],'paid_calls':retime['paid_calls'],'rank_mass':retime['rank_mass'],'selected_blocks':len(retime['selected']),'changed_gates':load(LEAD/'TARGET-ROLE-AUDIT.json')['changed_gates'],'baseline_regenerated_from_source':True,'conditional_all_size_interfaces_retained':True,'elapsed_seconds':time.monotonic()-START}
for k,v in expected.items():assert result[k]==v,k
for name,h in manifest.items():assert sha(HERE/name)==h,name
for name,h in source['cleanup']['files'].items():assert sha(CLEAN/name)==h,('cleanup changed during execution',name)
assert sha(BASE/'MANIFEST.json')==source['baseline']['manifest_sha256']
for name,h in load(BASE/'MANIFEST.json')['files'].items():assert sha(BASE/name)==h,('baseline changed during execution',name)
(OUT/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
