"""Portable aggregate. Every executable is original code; all upstream files stay inert."""
from pathlib import Path
import argparse,json,hashlib,os,subprocess,sys,time
import support
HERE=support.HERE
STEPS=[
 'matching/check_scalar_and_seams.py','matching/path_census.py',
 'closure/build_cache.py','closure/search_closure.py','closure/combine_screen.py','closure/emit_candidates.py',
 'arithmetic/prepare_prices.py','arithmetic/check_stage_roots.py',
 'bridge15/check_bridge.py','bridge15/check_scalar_bounds.py',
 'weighted/check_transport.py','weighted/check_target_chronology.py','weighted/check_scalar_recurrence.py','weighted/check_reorder_transport.py',
 'certificates/check_seam_charts.py','certificates/check_candidate_charts.py','certificates/check_role_banks.py','certificates/check_fallback.py',
 'arithmetic/check_scalar_counts.py','arithmetic/check_seam_contract.py','arithmetic/bind_weighted_invoice.py','arithmetic/bind_finite_receipts.py',
]
RECEIPTS=[
 'matching/scalar_and_seams892.json','matching/full_path_census892.json',
 'closure/response-cache-summary.json','closure/screen-summary.json','closure/best-residue-unions.json',
 'arithmetic/baseline-receipt.json','arithmetic/provisional892-candidate19-pricing.json','arithmetic/candidate15-pricing.json','arithmetic/stage-root-receipt.json',
 'bridge15/bridge-result.json','bridge15/scalar-bounds-result.json',
 'weighted/transport-result.json','weighted/target-chronology-result.json','weighted/scalar-recurrence-result.json','weighted/reorder-transport-result.json',
 'certificates/weighted892-seam-charts.json','certificates/rebound-candidate19-charts.json','certificates/weighted892-candidate19-bank-receipt.json','certificates/candidate15-charts.json','certificates/candidate15-bank-receipt.json',
 'arithmetic/weighted892-scalar-count-contract.json','arithmetic/weighted892-seam-cost-contract.json','arithmetic/weighted892-finite-invoice-bound.json','arithmetic/candidate15-finite-invoice-bound.json',
]
def canonical(value):
 if isinstance(value,dict):return {k:canonical(v)for k,v in sorted(value.items())if k not in ('seconds','elapsed_seconds','runtime_seconds')}
 if isinstance(value,list):return [canonical(x)for x in value]
 if isinstance(value,str):
  for path,label in ((support.OUTPUT,'$OUTPUT'),(support.INPUTS,'$INPUTS'),(HERE,'$PACKAGE')):
   value=value.replace(str(path),label)
 return value
def summary():
 out={}
 for name in RECEIPTS:
  value=canonical(json.loads((support.OUTPUT/name).read_text()));raw=json.dumps(value,sort_keys=True,separators=(',',':')).encode()
  out[name]=dict(sha256=hashlib.sha256(raw).hexdigest(),status=value.get('status')if isinstance(value,dict)else None)
 return dict(source_head=support.HEAD,receipt_count=len(out),normalization='Exclude only elapsed-time keys; replace absolute package/input/output roots by labels.',receipts=out)
def run(check=False,tests=False,record=False):
 if not __debug__:raise RuntimeError('Assertions must remain enabled')
 start=time.monotonic();support.verify_inputs();support.materialize_word()
 for step in STEPS:
  begun=time.monotonic();log=support.out('logs',step.replace('/','__')+'.log')
  with log.open('w')as handle:result=subprocess.run([sys.executable,str(HERE/step)],stdout=handle,stderr=subprocess.STDOUT)
  if result.returncode:raise RuntimeError(f'{step} failed; inspect {log}\n'+log.read_text()[-5000:])
  print(f'PASS {step} ({time.monotonic()-begun:.2f}s)',flush=True)
 for name in ('candidate15.json','candidate19-residue4.json'):
  assert (support.OUTPUT/'closure'/name).read_bytes()==(HERE/'witnesses'/name).read_bytes(),'Declared bounded search witness mismatch: '+name
 if tests:
  for folder in ('.','closure','arithmetic','bridge15','weighted','certificates'):
   files=list((HERE/folder).glob('test_*.py'));assert files,'Missing regression tests: '+folder
   log=support.out('logs','tests-'+folder+'.log')
   with log.open('w')as handle:r=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(HERE/folder),'-p','test_*.py','-v'],stdout=handle,stderr=subprocess.STDOUT)
   if r.returncode:raise RuntimeError(f'{folder} tests failed:\n'+log.read_text())
   print(log.read_text(),flush=True)
 current=summary();expected=HERE/'expected/receipts.json'
 if record:expected.write_text(json.dumps(current,indent=2)+'\n')
 if check:
  wanted=json.loads(expected.read_text());assert current==wanted,'Deterministic receipt mismatch; do not replace expected results without review.'
 report=dict(status='PASS_PINNED_P10_AGGREGATE',source_head=support.HEAD,verified_inputs=len(support.pins()['files']),receipt_count=current['receipt_count'],tests_requested=tests,expected_receipts_match=bool(check),kappa='0.000769661484777339',remaining_conditions='Explicit inherited133 raw crossing, compiler/prime/complex/full-C/all-size interfaces; no complete final raw-frame/hash regeneration.')
 support.out('aggregate-result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2),flush=True);print(f'Runtime {time.monotonic()-start:.3f}s',flush=True);return report
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');parser.add_argument('--tests',action='store_true');parser.add_argument('--record-expected',action='store_true',help='Maintainer-only: write new expected receipt digests after independent review.')
 args=parser.parse_args();run(args.check,args.tests,args.record_expected)
