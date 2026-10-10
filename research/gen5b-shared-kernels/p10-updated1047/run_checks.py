"""Portable aggregate of original checkers. Upstream programs remain inert text."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys,time
import support
STEPS=[
 ('matching/audit_matching.py',['--graph-only']),
 ('matching/select_matching.py',[]),('matching/audit_matching.py',[]),
 ('matching/census_matching.py',[]),('arithmetic/price.py',[]),
 ('arithmetic/check_second_moment.py',[]),
 ('admission/check_transport.py',[]),('admission/check_target_chronology.py',[]),
 ('admission/check_scalar_recurrence.py',[]),('admission/check_reorder_transport.py',[]),
 ('finite/check_charts.py',[]),('finite/check_banks.py',[]),('finite/bind_finite.py',[]),
]
RECEIPTS=[
 'matching/matching-result.json','matching/audit-result.json','matching/weighted890-delta.json',
 'arithmetic/baseline-receipt.json','arithmetic/weighted890-price.json','arithmetic/arithmetic-result.json','arithmetic/second-moment-result.json',
 'admission/transport-result.json','admission/target-chronology-result.json','admission/scalar-recurrence-result.json','admission/reorder-transport-result.json',
 'finite/chart-receipt.json','finite/bank-receipt.json','finite/finite-invoice-bound.json',
]

def canonical(value):
 if isinstance(value,dict):return {k:canonical(v) for k,v in sorted(value.items())if k not in ('seconds','elapsed_seconds','runtime_seconds')}
 if isinstance(value,list):return [canonical(x)for x in value]
 if isinstance(value,str):
  for path,label in ((support.OUTPUT,'$OUTPUT'),(support.INPUTS,'$INPUTS'),(support.HERE,'$PACKAGE'),(support.HERE.parent,'$AUTHORED')):value=value.replace(str(path),label)
 return value

def summary():
 rows={}
 for name in RECEIPTS:
  value=canonical(json.loads((support.OUTPUT/name).read_text()))
  # Paths inside the finite dependency binding are normalized, not dropped.
  raw=json.dumps(value,sort_keys=True,separators=(',',':')).encode()
  rows[name]=dict(sha256=hashlib.sha256(raw).hexdigest(),status=value.get('status'))
 return dict(source_head=support.HEAD,word_sha256=support.WORD_SHA,source_manifest_sha256=support.sha(support.HERE/'inputs.json'),receipt_count=len(rows),normalization='Remove elapsed-time keys and replace only declared absolute package/input/output/authored roots. All other receipt fields are checked.',receipts=rows)

def check_packet_files():
 path=support.HERE/'FILES.json'
 if not path.exists():return
 manifest=json.loads(path.read_text())
 for name,row in manifest['files'].items():
  raw=(support.HERE/name).read_bytes();assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['sha256'],'Frozen packet changed: '+name
 assert manifest['source_head']==support.HEAD and manifest['published_base_head']=='022266b4f6a3e09b75ff664008ddbb732e9672f9'

def run(check=False,tests=False,record=False):
 support.require_assertions();check_packet_files();support.verify_inputs();support.verify_dependencies();support.materialize_word();start=time.monotonic()
 for index,(step,args)in enumerate(STEPS):
  log=support.out('logs',f'{index:02d}-'+step.replace('/','__')+'.log');begun=time.monotonic()
  with log.open('w')as handle:r=subprocess.run([sys.executable,str(support.HERE/step),*args],stdout=handle,stderr=subprocess.STDOUT)
  if r.returncode:raise RuntimeError(f'{step} failed; inspect {log}\n'+log.read_text()[-6000:])
  print(f'PASS {step} ({time.monotonic()-begun:.2f} s)',flush=True)
 test_count=0
 if tests:
  for folder in ('.','arithmetic','admission','finite'):
   log=support.out('logs','tests-'+folder.replace('.','root')+'.log')
   with log.open('w')as handle:r=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(support.HERE/folder),'-p','test_*.py','-v'],stdout=handle,stderr=subprocess.STDOUT)
   if r.returncode:raise RuntimeError(f'{folder} tests failed:\n'+log.read_text())
   import re
   count=re.search(r'Ran (\d+) tests?',log.read_text());assert count,'No test count: '+folder;test_count+=int(count.group(1));print(log.read_text(),flush=True)
 current=summary();expected=support.HERE/'expected/receipts.json'
 if record:expected.write_text(json.dumps(current,indent=2)+'\n')
 if check:assert current==json.loads(expected.read_text()),'Deterministic receipt mismatch. Expected evidence is not replaced automatically.'
 finite=json.loads((support.OUTPUT/'finite/finite-invoice-bound.json').read_text())
 result=dict(status='PASS_PINNED_UPDATED1047_WEIGHTED890_AGGREGATE',source_head=support.HEAD,word_sha256=support.WORD_SHA,verified_input_files=len(support.pins()['files']),receipt_count=len(RECEIPTS),regression_tests=test_count,expected_receipts_match=bool(check),baseline_kappa='0.000769553898621543',conditional_kappa='0.000769997773182046',finite_coefficient=finite['finite_invoice']['coefficient'],payload_bound=finite['scalar_payload']['bound'],scope='Fresh finite evidence with explicit inherited 133 raw crossing, compiler/prime/complex/full-C/all-size hypotheses. No complete final raw frame/hash regeneration.')
 support.out('aggregate-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));print(f'Runtime {time.monotonic()-start:.3f} s');return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');p.add_argument('--tests',action='store_true');p.add_argument('--record-expected',action='store_true',help='Maintainer-only, after reviewing all finite gates and dependency hashes.')
 a=p.parse_args();run(a.check,a.tests,a.record_expected)
