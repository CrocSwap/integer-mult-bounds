"""Independent portable replay of the separate PR322/323 paid892 companion."""
from pathlib import Path
import argparse,hashlib,json,os,re,subprocess,sys,time
import companion as packet
EXPERIMENT_STEPS=['check_composition.py','check_changed_banks.py','price_candidate.py','price_cases.py','check_controls.py']
LATER_STEPS=['admission/build_local.py','admission/validate_local.py','admission/check_frozen_experiment.py','lowering/lower_combined.py','lowering/check_emitted_projectors.py','audit/check_source_composition.py','audit/check_banks_price.py','audit/check_global_frames.py']
RECEIPTS=['experiment/'+x for x in ['RESULT.json','BANK-RESULT.json','PRICE-RESULT.json','CASE-PRICES.json','CONTROLS.json','MANIFEST.json']]+['admission/'+x for x in ['RESULT.json','VALIDATION.json','EXPERIMENT-CROSSCHECK.json']]+['lowering/'+x for x in ['RESULT.json','PROJECTOR-CONTROLS.json','invoice.json']]+['audit/'+x for x in ['SOURCE-AUDIT.json','BANK-PRICE-AUDIT.json','GLOBAL-AUDIT.json']]
def execute(name,args=None):
    args=args or [];file=Path(name);file=file if file.is_absolute()else packet.HERE/file
    log=packet.OUTPUT/'logs'/((str(name)if not Path(name).is_absolute()else file.name).replace('/','__')+'.log');log.parent.mkdir(parents=True,exist_ok=True);start=time.monotonic()
    with log.open('w')as stream:r=subprocess.run([sys.executable,str(file),*args],env=packet.child_env(),stdout=stream,stderr=subprocess.STDOUT)
    if r.returncode:raise RuntimeError(str(name)+' failed:\n'+log.read_text()[-7000:])
    print(f'PASS {name} ({time.monotonic()-start:.2f} s)',flush=True)
def tests(folder):
    log=packet.OUTPUT/'logs'/('tests-'+('root'if folder=='.'else folder)+'.log');log.parent.mkdir(parents=True,exist_ok=True)
    with log.open('w')as stream:r=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(packet.HERE/folder),'-p','test_*.py','-v'],env=packet.child_env(),stdout=stream,stderr=subprocess.STDOUT)
    if r.returncode:raise RuntimeError(log.read_text())
    m=re.search(r'Ran (\d+) tests?',log.read_text());assert m;print(log.read_text(),flush=True);return int(m.group(1))
def summary():
    rows={}
    for name in RECEIPTS:
        value=packet.portable(packet.read(packet.OUTPUT/name));raw=json.dumps(value,sort_keys=True,separators=(',',':')).encode()
        rows[name]={'sha256':hashlib.sha256(raw).hexdigest(),'status':value.get('status')if isinstance(value,dict)else None}
    return {'base_packet_files_sha256':packet.BASE_FILES_SHA,'base_word_sha256':packet.WORD_SHA,'source_manifest_sha256':packet.sha(packet.SOURCE_PROVENANCE),'receipt_count':len(rows),'normalization':'Replace only declared absolute roots, including dictionary keys; mathematical fields and dependency hashes remain intact.','receipts':rows}
def check_packet(allow_unfrozen=False):
    path=packet.HERE/'FILES.json'
    assert path.exists() or allow_unfrozen, 'FILES.json is required for a frozen replay'
    if path.exists():
        for name,row in packet.read(path)['files'].items():
            p=packet.HERE/name;assert p.stat().st_size==row['bytes']and packet.sha(p)==row['sha256'],name

def finish(check=False,record=False,test_count=13):
    packet.verify_base();packet.verify_experiment();current=summary();path=packet.HERE/'expected/receipts.json'
    if record:path.write_text(json.dumps(current,indent=2)+'\n')
    if check:assert current==packet.read(path),'Expected receipt hashes differ; they are never replaced automatically.'
    local=packet.read(packet.ADMISSION/'RESULT.json');global_=packet.read(packet.LOWERING/'RESULT.json');audit=packet.read(packet.AUDIT/'GLOBAL-AUDIT.json');price=packet.read(packet.EXPERIMENT/'PRICE-RESULT.json')
    assert audit['program_binding']==global_['full_program_sha256']and audit['all_global_stage_records']==116772600
    assert (local['retimings'],local['new_kernels'],local['moves'])==(4,3,133)
    result={'status':'PASS_PORTABLE_PR322_PR323_PAID892_COMPANION','base_packet_files_sha256':packet.BASE_FILES_SHA,'base_word_sha256':packet.WORD_SHA,'source_heads':local['source_heads'],'source_manifest_sha256':packet.sha(packet.SOURCE_PROVENANCE),'tests':test_count,'hard_experiment_controls':17,'receipt_count':len(RECEIPTS),'expected_receipts_match':bool(check),'conditional_saving_kappa':price['assembly']['kappa'],'local_records':389222,'global_frame_records':116772600,'literal_stock':658255,'literal_calls':15006605,'literal_rank_mass':65703100,'literal_deficit':122400,'maximum_rank':42,'phases':725,'paid_completions':5,'paid_completion_rank':20,'program_sha256':audit['program_binding'],'source_and_global_independent_audits_passed':True,'upstream_programs_executed':False,'unconditional_all_size_theorem':False,'scope':'Exact retiming/kernel composition, local records, changed bank charts, literal global frame IR, all fees and independent exact price. Generic primitive/compiler-prime, restored-row, ordinary-leaf, complex/full-C, precision/recovery and analytic all-size interfaces remain inherited.'}
    (packet.OUTPUT/'aggregate-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));return result

def run(check=False,run_tests=False,record=False,reuse_base=False):
    packet.require_assertions();check_packet(allow_unfrozen=record);packet.verify_base_code();packet.verify_sources()
    if not reuse_base:execute(packet.BASE_CODE/'run_checks.py',['--check','--tests'])
    packet.verify_base()
    for name in EXPERIMENT_STEPS:execute('experiment/'+name)
    packet.freeze_experiment()
    for name in LATER_STEPS:execute(name)
    count=tests('admission')
    if run_tests:count+=tests('.')
    return finish(check,record,count)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');p.add_argument('--tests',action='store_true');p.add_argument('--record-expected',action='store_true');p.add_argument('--reuse-base-output',action='store_true',help='Reuse predecessor outputs only after checking all 31 frozen receipts, every pinned code file and both emitted manifests.')
    a=p.parse_args();run(a.check,a.tests,a.record_expected,a.reuse_base_output)
