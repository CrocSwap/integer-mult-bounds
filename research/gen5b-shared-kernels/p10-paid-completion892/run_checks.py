"""Reproduce paid bank completion and independent audits from any working directory."""
from pathlib import Path
import argparse, hashlib, json, os, re, subprocess, sys, time
import support
ADMISSION_STEPS = ['check_transport.py','check_target_chronology.py','check_scalar_recurrence.py','check_reorder_transport.py','check_source_target_geometry.py','check_reorder_controls.py']
RECEIPTS = ['admission/ADMISSION-RESULT.json','admission/MANIFEST.json'] + ['admission/'+n for n in support.ADMISSION_OUTPUTS] + ['frame/SOURCE-GEOMETRY-CORRECTION.json','bank/split_49_11/RESULT.json','bank/split_49_11/GENERIC-RESULT.json','bank/split_49_11/LOWERING-PLAN.json','bank/split_49_11/ARITHMETIC-RESULT.json','lowering/RESULT.json','lowering/endpoint.json','lowering/invoice.json','lowering/local-scalar-binding.json','lowering/expanded-operand-receipts.json','audit/AUDIT-RESULT.json','audit/LOWERING-AUDIT-RESULT.json','audit/LOWERING-REVIEW.json','audit/FINAL-AUDIT.json','frame/RESULT.json','frame/VALIDATION.json','full-frame/RESULT.json','audit/LOCAL-AUDIT.json','audit/GLOBAL-AUDIT.json']

def canonical(value):
    if isinstance(value, dict): return {canonical(k):canonical(v) for k,v in sorted(value.items()) if k not in ('seconds','elapsed_seconds','runtime_seconds')}
    if isinstance(value, list): return [canonical(v) for v in value]
    if isinstance(value, str):
        for path, label in [(support.OUTPUT,'$OUTPUT'),(support.INPUTS,'$INPUTS'),(support.HERE,'$PACKAGE'),(support.HERE.parent,'$AUTHORED')]: value=value.replace(str(path),label)
    return value

def summary():
    rows={}
    for name in RECEIPTS:
        value=canonical(json.loads((support.OUTPUT/name).read_text()))
        rows[name]={'sha256':hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest(),'status':value.get('status') if isinstance(value,dict) else None}
    return {'source_head':support.HEAD,'word_sha256':support.WORD_SHA,'receipt_count':len(rows),'normalization':'Remove elapsed-time fields and replace only declared absolute roots, including dictionary keys. All remaining receipt fields are checked.','receipts':rows}

def check_packet():
    path=support.HERE/'FILES.json'
    if path.exists():
        manifest=json.loads(path.read_text())
        assert manifest['published_base_head']=='2becb0e4ad80afa37f0059a1e49d09e1752fd3d4'
        assert manifest['preserved_existing_file_count']==283
        for name,row in manifest['files'].items():
            p=support.HERE/name
            assert p.stat().st_size==row['bytes'] and support.sha(p)==row['sha256'], 'Frozen packet changed: '+name

def execute(name, args=None, env=None, tests=False):
    path=Path(name); args=args or []
    label=path.name if path.is_absolute() else str(path).replace('/','__')
    log=support.out('logs',label+'.log'); start=time.monotonic()
    command=[sys.executable,str(path if path.is_absolute() else support.HERE/path),*args]
    with log.open('w') as stream:
        result=subprocess.run(command,env=env,stdout=stream,stderr=subprocess.STDOUT)
    if result.returncode: raise RuntimeError(str(name)+' failed:\n'+log.read_text()[-7000:])
    print(f'PASS {name} ({time.monotonic()-start:.2f} s)',flush=True)
    return log.read_text()

def test_folder(folder):
    label='root' if folder=='.' else folder.replace('/','__'); log=support.out('logs','tests-'+label+'.log')
    with log.open('w') as stream:
        result=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(support.HERE/folder),'-p','test_*.py','-v'],stdout=stream,stderr=subprocess.STDOUT)
    if result.returncode: raise RuntimeError(log.read_text())
    match=re.search(r'Ran (\d+) tests?',log.read_text()); assert match
    print(log.read_text(),flush=True); return int(match.group(1))

def run(check=False, tests=False, record=False):
    support.require_assertions(); check_packet(); support.verify_inputs(); support.verify_dependencies(); support.materialize_word()
    env=dict(os.environ,P10U_INPUTS=str(support.INPUTS),P10U_OUTPUT=str(support.BASE_OUTPUT))
    materialize='import sys;sys.path.insert(0,sys.argv[1]);import support;support.verify_dependencies();support.materialize_word()'
    subprocess.run([sys.executable,'-c',materialize,str(support.BASE_CODE)],env=env,check=True)
    for name in ['matching/census_matching.py','arithmetic/price.py','admission/check_transport.py','finite/check_charts.py']:
        execute(support.BASE_CODE/name,env=env)
    for name in ADMISSION_STEPS: execute('admission/'+name)
    count=test_folder('admission'); support.finalize_admission(count)
    for name,args in [ ('frame/check_descended_sources.py',[]),('bank/check_paid_completion.py',['49,11']),('bank/check_generic_lowering.py',['49,11']),('bank/check_price_and_assembly.py',[]),('bank/check_phase_plan.py',[]),('lowering/lower_incremental.py',[]),('audit/audit_contract.py',[]),('audit/audit_lowering.py',[]),('audit/review_incremental_lowering.py',[]),('audit/finalize_audit.py',[]),('frame/build_local.py',[]),('frame/validate_local.py',[]),('lowering/bind_full_frames.py',[]),('audit/check_full_frame.py',[]),('audit/check_global_frame.py',[])]: execute(name,args)
    return finish(check,tests,record,count)

def finish(check=False,tests=False,record=False,count=17):
    if tests: count+=test_folder('.')
    current=summary(); expected=support.HERE/'expected/receipts.json'
    if record: expected.write_text(json.dumps(current,indent=2)+'\n')
    if check: assert current==json.loads(expected.read_text()), 'Deterministic receipt mismatch. Expected evidence is never replaced automatically.'
    bank=json.loads((support.BANK/'split_49_11/RESULT.json').read_text()); price=json.loads((support.BANK/'split_49_11/ARITHMETIC-RESULT.json').read_text()); lower=json.loads((support.LOWER/'RESULT.json').read_text()); review=json.loads((support.AUDIT/'LOWERING-REVIEW.json').read_text())
    assert lower['exact_new_completion_integration_verified'] and lower['phase_count']==730
    assert review['expanded_scalar_records']==100887900 and review['boundary_records']==921600
    local_audit=json.loads((support.AUDIT/'LOCAL-AUDIT.json').read_text()); global_audit=json.loads((support.AUDIT/'GLOBAL-AUDIT.json').read_text()); full=json.loads((support.OUTPUT/'full-frame/RESULT.json').read_text())
    assert global_audit['all_global_stage_records']==116772900 and global_audit['all_copy_negative_directions_rejected']
    assert local_audit['frames']==15034 and local_audit['source_bound_descents']==480
    assert full['full_program_binding_sha256']==global_audit['program_binding']
    result={'status':'PASS_PAID_COMPLETION892_PORTABLE_AGGREGATE','source_head':support.HEAD,'word_sha256':support.WORD_SHA,'split':[49,11],'new_incremental_gate_closed_conditionally':True,'regression_tests':count,'receipt_count':len(RECEIPTS),'expected_receipts_match':bool(check),'conditional_kappa':price['assembly']['kappa_decimal'],'literal_profile':bank['literal_profile'],'compositional_program_sha256':review['program_sha256'],'full_frame_program_sha256':full['full_program_binding_sha256'],'local_records':389223,'global_frame_records':116772900,'rationally_nondegenerate_frames':15034,'copied_work_positive_projector_overrides':100,'actual_local_raw_frame_word_regenerated':True,'all_300_global_frame_streams_materialized_and_hashed':True,'production_primitive_compiler_executed':False,'unconditional_all_size_theorem':False,'scope':'The added paid-completion integration is verified. The concrete final local frame word and all 300 global frame streams are rebuilt. Generic primitive compilation, uniform prime supply, complex/full-C supplier, analytic and all-size interfaces remain explicit premises.'}
    support.out('aggregate-result.json').write_text(json.dumps(result,indent=2)+'\n'); print(json.dumps(result,indent=2)); return result
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');p.add_argument('--tests',action='store_true');p.add_argument('--record-expected',action='store_true')
    a=p.parse_args();run(a.check,a.tests,a.record_expected)
