"""Arbitrary-cwd replay of the fresh PR325 partner-retiming finite certificate."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys,time,re
import packet325 as packet
STEPS=['source/check_retimings.py','frame/build_local.py','frame/validate_local.py','bank/check_base_ledger.py','bank/check_admitted_banks.py','bank/price_admitted_profile.py','bank/check_controls.py','bank/check_full_frame_binding.py','audit/check_geometry.py','audit/check_events.py','audit/check_full_frames.py','audit/check_bank_price.py','lowering/prepare_fresh.py','lowering/lower_pr325.py','lowering/check_geometry.py','lowering/check_emission_controls.py','audit/check_global.py','audit/check_chart_units.py','audit/finalize_audit.py']
RECEIPTS=['source/RESULT.json','source/MANIFEST.json','frame/RESULT.json','frame/VALIDATION.json','frame/MANIFEST.json','frame/ARBITRARY-DIRTY-AUDIT-BINDING.json']+['bank/'+n for n in ['BASE-LEDGER.json','BANK-RESULT.json','PRICE-RESULT.json','CONTROLS.json','FRAME-BINDING.json','MANIFEST.json']]+['audit/'+n for n in ['GEOMETRY-RESULT.json','EVENT-AUDIT.json','FULL-FRAME-AUDIT.json','BANK-PRICE-AUDIT.json','GLOBAL-AUDIT.json','GLOBAL-CHART-BOUNDS.json','ASSERTION-CONTROLS.json','FINAL-AUDIT.json','MANIFEST.json']]+['prepared/PREPARATION.json','prepared/MANIFEST.json']+['global/'+n for n in ['RESULT.json','MANIFEST.json','GEOMETRY-CONTROLS.json','EMISSION-CONTROLS.json','invoice.json']]
def check_packet(allow_unfrozen=False):
 p=packet.HERE/'FILES.json';assert p.exists()or allow_unfrozen,'FILES.json is required for a frozen replay'
 if p.exists():
  for name,row in packet.read(p)['files'].items():
   f=packet.HERE/name;assert f.stat().st_size==row['bytes']and packet.sha(f)==row['sha256'],name
def execute(name):
 log=packet.OUTPUT/'logs'/(name.replace('/','__')+'.log');log.parent.mkdir(parents=True,exist_ok=True);start=time.monotonic()
 with log.open('w')as out:r=subprocess.run([sys.executable,str(packet.HERE/name)],env=packet.child_env(),stdout=out,stderr=subprocess.STDOUT)
 if r.returncode:raise RuntimeError(name+' failed:\n'+log.read_text()[-7000:])
 print(f'PASS {name} ({time.monotonic()-start:.2f} s)',flush=True)
def tests(folder):
 log=packet.OUTPUT/'logs'/('tests-'+('root'if folder=='.'else folder)+'.log')
 with log.open('w')as out:r=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(packet.HERE/folder),'-p','test_*.py','-v'],env=packet.child_env(),stdout=out,stderr=subprocess.STDOUT)
 if r.returncode:raise RuntimeError(log.read_text())
 m=re.search(r'Ran (\d+) tests?',log.read_text());assert m;print(log.read_text(),flush=True);return int(m.group(1))
def assertion_controls():
 checks=['check_geometry.py','check_events.py','check_full_frames.py','check_bank_price.py','check_global.py','check_chart_units.py'];controls={}
 for name in checks:
  code=packet.HERE/'audit'/name;r=subprocess.run([sys.executable,'-O',str(code)],env=packet.child_env(),capture_output=True,text=True)
  assert r.returncode!=0 and 'Assertions must be enabled'in r.stderr
  controls[name]={'return_code':r.returncode,'checker_sha256':packet.sha(code)}
 packet.dump(packet.AUDIT/'ASSERTION-CONTROLS.json',{'status':'PASS_ALL_SIX_OPTIMIZED_MODE_REJECTIONS','controls':controls})
def summary():
 rows={}
 for n in RECEIPTS:
  v=packet.portable(packet.read(packet.OUTPUT/n));raw=json.dumps(v,sort_keys=True,separators=(',',':')).encode();rows[n]={'sha256':hashlib.sha256(raw).hexdigest(),'status':v.get('status')if isinstance(v,dict)else None}
 return {'source_head':packet.HEAD,'source_word_gzip_sha256':packet.WORD,'input_manifest_sha256':packet.sha(packet.HERE/'inputs.json'),'receipt_count':len(rows),'normalization':'Only declared absolute roots in JSON keys and values are normalized; dependency hashes and mathematical evidence remain intact.','receipts':rows}
def finish(check=False,record=False,count=22):
 packet.verify_frame_binding();packet.verify_bank();current=summary();expected=packet.HERE/'expected/receipts.json'
 if record:expected.write_text(json.dumps(current,indent=2)+'\n')
 if check:assert current==packet.read(expected),'Expected receipt hashes differ; they are never silently replaced.'
 for root in [packet.PREPARED,packet.GLOBAL]:
  for n,h in packet.read(root/'MANIFEST.json').items():assert packet.sha(root/n)==h,n
 a=packet.read(packet.AUDIT/'GLOBAL-AUDIT.json');g=packet.read(packet.GLOBAL/'RESULT.json');price=packet.read(packet.BANK/'PRICE-RESULT.json')
 final=packet.read(packet.AUDIT/'FINAL-AUDIT.json');assert final['finite_gate_closed']and final['global_program_sha256']==g['full_program_sha256']
 for n,h in packet.read(packet.AUDIT/'MANIFEST.json')['files'].items():assert packet.sha((packet.HERE/'audit'/n)if n.endswith('.py')else packet.AUDIT/n)==h,n
 assert a['program_binding']==g['full_program_sha256']and a['all_global_stage_records']==119604000
 assert g['invoice']['coefficient']==price['finite_coefficient']==24857617667871401
 assert price['assembly']['kappa_decimal']=='0.000770612425424136'
 result={'status':'PASS_PORTABLE_FRESH_PR325_480_RETIMING_FINITE_CERTIFICATE','source_head':packet.HEAD,'word_gzip_sha256':packet.WORD,'source_manifest_sha256':packet.sha(packet.HERE/'inputs.json'),'regression_tests':count,'bank_negative_controls':21,'emission_negative_controls':12,'receipt_count':len(RECEIPTS),'expected_receipts_match':bool(check),'retimings':480,'local_records':398660,'frames':12885,'global_stage_records':119604000,'namespaces':300,'phases':720,'positive_copy_overrides':100,'stock':658800,'children':14514000,'rank_mass':65757600,'deficit':122400,'max_rank':42,'completion_children':0,'finite_coefficient':24857617667871401,'conditional_saving_kappa':price['assembly']['kappa_decimal'],'program_sha256':a['program_binding'],'address_geometry_distinguished_from_F2_payload':True,'all_finite_common_array_frame_hypotheses_verified':True,'old_role_frame_or_selection_data_imported':False,'upstream_programs_executed':False,'unconditional_all_size_theorem':False,'scope':'Fresh PR325 source word with exactly 480 independently derived partner-mix retimings. All finite source, frame, arbitrary-dirty array-lifting premises, bank, full global IR, invoice and price gates pass. Production primitive/compiler, prime eligibility, restored rows, ordinary leaves, complex/full-C, precision/recovery and analytic all-size interfaces remain inherited.'}
 (packet.OUTPUT/'aggregate-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));return result
def run(check=False,run_tests=False,record=False):
 packet.require_assertions();check_packet(record);packet.setup_data()
 for name in STEPS:
  if name=='audit/finalize_audit.py':assertion_controls()
  execute(name)
  if name=='source/check_retimings.py':packet.freeze_source()
  if name=='audit/check_full_frames.py':packet.freeze_frame()
  if name=='bank/check_full_frame_binding.py':packet.freeze_bank()
 count=tests('source')+tests('frame')
 if run_tests:count+=tests('.')
 return finish(check,record,count)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');p.add_argument('--tests',action='store_true');p.add_argument('--record-expected',action='store_true');a=p.parse_args();run(a.check,a.tests,a.record_expected)
