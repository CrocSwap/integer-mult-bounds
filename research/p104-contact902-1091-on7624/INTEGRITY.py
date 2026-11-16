#!/usr/bin/env python3
"""Read-only package integrity and receipt checks; never runs research code."""
import hashlib,json,runpy
from fractions import Fraction
from pathlib import Path

MAP_SHA='ef2818204ea012a8cd12e1319f8353fb62cc9dd0e20554934f3e58e99bd7dee6'
PIN_COUNT=int('985')
FREEZE='f0655f411e5e53b390e8d6f85e9789040f83f434e20fb034813ebe0269a8b934'
PREVIOUS_FREEZE='4b8ff9e31be998b83515807ac3860d38476df2f1fedd7d6ee91c4b909555d272'
OLD_FREEZE='0ef4032f4c1124de335bad3c1ef94b8a14a7926ec84fa608b0686c0ec8ee13aa'
CUSTODY='3ba37fb1cea86b9944d3b42c6baa7c0e4dc8bd8ab6c0d8fd9272cec9ce29af0a'
SIGNED_CUSTODY='9d875ef2e10abaf5b4e71e082df3b64e970931c092ef17e46d3a81173c9751f2'

def need(v,m):
    if not v: raise ValueError(m)
def sha(b): return hashlib.sha256(b).hexdigest()
def blob(b): return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def read(p): return json.loads(p.read_bytes())
def safe(s):
    p=Path(s);need(not p.is_absolute() and '..' not in p.parts and str(p)==s,'invalid mapped path');return p

def verify(package=None):
    p=Path(package or Path(__file__).resolve().parent).resolve();pins=read(p/'PINS.json');need(pins['schema']=='contact7624-pins/v1' and len(pins['files'])==PIN_COUNT,'fixed pin count')
    actual=set()
    for f in p.rglob('*'):
        need(not f.is_symlink(),'package symlink')
        if f.is_file() and f!=p/'PINS.json': actual.add(f.relative_to(p).as_posix())
    need(actual==set(pins['files']),'package inventory')
    for rel,row in pins['files'].items():
        b=(p/safe(rel)).read_bytes();need(len(b)==row['bytes'] and sha(b)==row['sha256'] and blob(b)==row['git_blob'],'pinned bytes '+rel)
    mb=(p/'EXPORT-MAP.json').read_bytes();need(sha(mb)==MAP_SHA,'fixed export map')
    m=json.loads(mb);need(m['schema']=='contact7624-offline-export/v1' and m['candidate_canonical_sha256']=='df521d552dc35de6271e67655e4f9c466bc9247d37a5196b85613870209106a2','export identity')
    fb=(p/'evidence/SIGNED-COMPLETION-FREEZE.json').read_bytes();need(sha(fb)==FREEZE==m['freeze_sha256'],'completion freeze')
    f=json.loads(fb);rows=m['files'];frozen=[r for r in rows if r['origin']=='frozen_input'];need(len(f['files'])==len(frozen)==m['frozen_file_count']==502 and sum(x['bytes'] for x in f['files'])==m['frozen_byte_count']==118905629,'freeze denominator')
    need(len({r['package_path'] for r in rows})==len(rows) and len({r['original_path'] for r in frozen})==502,'mapping uniqueness')
    index={r['original_path']:r for r in frozen};need(set(index)=={r['path'] for r in f['files']},'freeze paths')
    for r in f['files']:
        q=index[r['path']];need(q['sha256']==r['sha256'] and q['bytes']==r['bytes'],'freeze mapping')
    previous_bytes=(p/'evidence/CONTINUATION-FREEZE.json').read_bytes();need(sha(previous_bytes)==PREVIOUS_FREEZE==m['predecessor_freeze_sha256'],'predecessor freeze')
    previous=json.loads(previous_bytes);need(len(previous['files'])==393,'predecessor freeze count')
    for r in previous['files']:need(r['path'] in index and index[r['path']]['sha256']==r['sha256'] and index[r['path']]['bytes']==r['bytes'],'predecessor frozen closure')
    for r in rows:
        b=(p/safe(r['package_path'])).read_bytes();need(len(b)==r['bytes'] and sha(b)==r['sha256'] and blob(b)==r['git_blob'],'mapped bytes')
    old=(p/'evidence/ORIGINAL-FULL-FREEZE.json').read_bytes();need(sha(old)==OLD_FREEZE==m['original_full_freeze_sha256'] and len(json.loads(old)['files'])==300,'original freeze')
    for r in json.loads(old)['files']:
        need(r['path'] in index and index[r['path']]['sha256']==r['sha256'] and index[r['path']]['bytes']==r['bytes'],'original frozen closure')
    root=p/'evidence/round';case=root/'qualification7624_signed_completion/run/case';newcontrol=root/'qualification7624_signed_completion/control';previouscase=root/'qualification7624_continuation/run/case';control=root/'qualification7624_continuation/control';oldcase=root/'qualification7624/run/case'
    failed=read(root/'compose7624/run/case/RESULT.json');gate=root/'compose7624_completion/run/case';corrected=read(gate/'RESULT.json')
    need(failed['status']=='INCOMPLETE' and failed['qualified_kappa'] is False and corrected['status']=='PASS_DIFFERENTIAL_ONLY_PROVISIONAL_UNDER_COMMON_U' and corrected['qualified_kappa'] is False,'failed and corrected first gates')
    need(corrected['original_failed_controller_sha256']==sha((root/'compose7624/control/RESULT.json').read_bytes()),'failed controller binding')
    for rel,digest in corrected['receipt_hashes'].items():need(sha((gate/safe(rel)).read_bytes())==digest,'corrected first gate receipt')
    final=read(case/'RESULT.json');guard=read(control/'RESULT.json');res=read(root/'qualification7624_signed_completion/run/RESOURCE.json');allow=read(control/'ALLOW.json');partial=read(oldcase/'PARTIAL.json');previous_result=read(previouscase/'RESULT.json');newguard=read(newcontrol/'RESULT.json');newallow=read(newcontrol/'ALLOW.json')
    need(final['status']=='PASS_QUALIFIED_CONDITIONAL_COMMON_U_KAPPA' and final['conditional_application_qualified'] is True and final['supplier_U_implemented'] is False and final['same_original_premise_dominance_established'] is False and final['selected_frontier_changed'] is False,'claim scope')
    need([(r['name'],r['exit_code']) for r in final['stages']]==[('signed',0),('resources',0)] and final['retained_predecessor_stages']==['prepare','certificates','certificate-verifier','native'] and final['retained_failed_signed_attempt'] is True,'two completion stages')
    need(previous_result['status']=='INCOMPLETE' and previous_result['conditional_application_qualified'] is False and [(r['name'],r['exit_code']) for r in previous_result['stages']]==[('certificate-verifier',0),('native',0),('signed',1)],'failed signed continuation')
    need(partial['status']=='INCOMPLETE' and partial['conditional_application_qualified'] is False and [(r['name'],r['exit_code']) for r in partial['stages']]==[('prepare',0),('certificates',0)] and previous_result['predecessor_partial_sha256']==sha((oldcase/'PARTIAL.json').read_bytes()),'interrupted predecessor custody')
    inv=read(root/'recovery7624/INTERRUPTED-RUN-INVENTORY.json');need(inv['file_count']==len(inv['files'])==77 and len({r['path'] for r in inv['files']})==77,'interrupted inventory count')
    for item in inv['files']:
        b=(root/'qualification7624'/safe(item['path'])).read_bytes();need(len(b)==item['bytes'] and sha(b)==item['sha256'],'interrupted inventory bytes')
    seed=read(root/'recovery7624/PREPARED-SEED.json');need(len(seed['files'])==58 and len({r['path'] for r in seed['files']})==58 and seed['status']=='PREPARED_ONLY_NATIVE_SIGNED_UNEXECUTED','seed count')
    for item in seed['files']:
        b=(oldcase/'work'/safe(item['path'])).read_bytes();need(len(b)==item['bytes'] and sha(b)==item['sha256'],'prepared seed bytes')
    need(guard['differential_case_completed'] is False and guard['group_empty'] is True and guard['returncode']==1 and allow['freeze_sha256']==PREVIOUS_FREEZE,'failed continuation guard')
    need(newguard['differential_case_completed'] is True and newguard['group_empty'] is True and type(newguard['returncode']) is int and newguard['returncode']==0 and newguard['audit_capture_valid'] is True and res['differential_case_completed'] is True and newallow['freeze_sha256']==FREEZE and newallow['guard_only'] is False,'completion guard and audit cleanup')
    for key,rel in [('native_receipt_sha256','work/native.receipt.json'),('signed_receipt_sha256','work/signed.receipt.json'),('resource_comparison_sha256','resources/RESOURCE-COMPARISON.json')]: need(final[key]==sha((case/rel).read_bytes()),'receipt '+key)
    need(final['certificate_verifier_sha256']==sha((previouscase/'certificate-verifier/status.json').read_bytes()),'retained certificate verifier')
    need(sha((case/'work/native.receipt.json').read_bytes())==sha((previouscase/'work/native.receipt.json').read_bytes())=='cafc2c05b287d9c4e732fbff0c57a438e6848faecb0c333f78377ce9ab74467e','retained native receipt')
    need(sha((case/'work/producer54/validation_native/NATIVE-RESULT.json').read_bytes())==sha((previouscase/'work/producer54/validation_native/NATIVE-RESULT.json').read_bytes())=='2cf79508c3dbffb56a1f0609710ccc921590dd4747850279edefe8f71238b682','retained native result')
    prior_audit=read(case/'PREDECESSOR-AUDIT-CAPTURE.json');need(prior_audit['status']=='ARCHIVED' and prior_audit['rows']==2 and prior_audit['bytes']==566 and prior_audit['sha256']==sha((case/'PREDECESSOR-AUDIT.jsonl').read_bytes())=='ca23807a4b1d9675daf67903608a6d874e37b94c70109a45fa73732ee8123841','failed audit raw custody')
    signed_audit_path=newcontrol/'SIGNED-AUDIT.jsonl';need(not signed_audit_path.is_symlink(),'signed audit symlink')
    signed_audit_bytes=signed_audit_path.read_bytes() if signed_audit_path.exists() else None
    runpy.run_path(str(p/'semantic.py'))['verify_audit_capture'](newguard['audit_capture'],signed_audit_bytes)
    custody_raw=(root/'observations/RUN-CUSTODY.json').read_bytes();need(sha(custody_raw)==CUSTODY,'author custody pin');custody=json.loads(custody_raw)
    need(custody['status']=='AUTHOR_OBSERVED_RUNNING_GUARDED_QUALIFICATION' and custody['freeze_sha256']==PREVIOUS_FREEZE and custody['author_side_observation_not_independent_attestation'] is True,'custody scope')
    need(custody['retained_predecessor_partial_sha256']==sha((oldcase/'PARTIAL.json').read_bytes()) and custody['recovery_sha256']==sha((root/'recovery7624/RECOVERY.json').read_bytes()),'custody predecessor binding')
    for name,d in custody['control_file_sha256'].items():need(sha((control/safe(name)).read_bytes())==d,'custody control')
    ready=read(control/'READY.json');verified=read(control/'GUARD-VERIFIED.json');need(custody['ready']==ready and custody['guard']==verified and custody['allow']==allow and custody['unit']==allow['unit']==verified['unit']==guard['unit'],'custody unit')
    need(verified['verified_before_release'] is True and ready['source_executed'] is False and guard['source_released'] is True and ready['cgroup']==verified['properties']['ControlGroup']==guard['properties']['ControlGroup'] and str(ready['pid'])==str(verified['properties']['MainPID'])==str(guard['properties']['MainPID']),'custody release')
    chain=custody['processes'];need(len(chain)==4 and chain[0]['pid']==ready['pid'],'custody process count')
    for i,row in enumerate(chain):
        need(row['cgroup'].endswith(ready['cgroup']) and (i==0 or row['ppid']==chain[i-1]['pid']),'custody process chain')
    for row,suffix in zip(chain,('/qualification7624_continuation/run_once.py','/qualification7624_continuation/job.py','/qualification7624/application.py','/qualification7624_continuation/run/case/work/producer54/validation_native/run.py')):
        need(any(x.endswith(suffix) for x in row['script_paths']),'custody process executable')
    work=case/'work';identity=read(work/'QUALIFICATION-ID.json');ledger=read(work/'CONTACT7624-ADAPTERS.json');need(identity==custody['qualification_identity'] and custody['adapter_sha256']==sha((work/'CONTACT7624-ADAPTERS.json').read_bytes()) and custody['launcher_sha256']==sha((work/'CONTACT7624-LAUNCHER.py').read_bytes()),'custody identity')
    signed_custody_bytes=(root/'observations/SIGNED-CUSTODY.json').read_bytes();need(sha(signed_custody_bytes)==SIGNED_CUSTODY,'signed author custody pin');sc=json.loads(signed_custody_bytes)
    need(sc['status']=='AUTHOR_OBSERVED_RUNNING_GUARDED_SIGNED_COMPLETION' and sc['freeze_sha256']==FREEZE and sc['author_side_observation_not_independent_attestation'] is True and sc['native_execution_is_retained_not_current'] is True,'signed custody scope')
    for name,d in sc['control_file_sha256'].items():need(sha((newcontrol/safe(name)).read_bytes())==d,'signed custody control')
    srdy=read(newcontrol/'READY.json');sg=read(newcontrol/'GUARD-VERIFIED.json')
    need(sc['ready']==srdy and sc['guard']==sg and sc['allow']==newallow and sc['unit']==newallow['unit']==sg['unit']==newguard['unit'] and sc['unit']!=custody['unit'],'distinct completion unit')
    need(sg['verified_before_release'] is True and srdy['source_executed'] is False and newguard['source_released'] is True and srdy['cgroup']==sg['properties']['ControlGroup']==newguard['properties']['ControlGroup'] and str(srdy['pid'])==str(sg['properties']['MainPID'])==str(newguard['properties']['MainPID']),'signed release binding')
    chain=sc['processes'];need(len(chain)==4 and chain[0]['pid']==srdy['pid'],'signed process count')
    for i,row in enumerate(chain):need(row['cgroup'].endswith(srdy['cgroup']) and (i==0 or row['ppid']==chain[i-1]['pid']),'signed process chain')
    for row,suffix in zip(chain,('/qualification7624_signed_completion/run_once.py','/qualification7624_signed_completion/job.py','/qualification7624/application.py','/qualification7624_signed_completion/run/case/work/producer54/validation_signed/run.py')):
        need(any(x.endswith(suffix) for x in row['script_paths']),'signed process executable')
    need(sc['qualification_identity']==identity and sc['adapter_sha256']==custody['adapter_sha256'] and sc['launcher_sha256']==custody['launcher_sha256'] and sc['retained_native_receipt_sha256']==final['native_receipt_sha256'] and sc['retained_native_result_sha256']=='2cf79508c3dbffb56a1f0609710ccc921590dd4747850279edefe8f71238b682' and sc['predecessor_audit_capture']==prior_audit,'signed custody identity')
    nr=read(work/'native.receipt.json');sr=read(work/'signed.receipt.json');native=read(work/'producer54/validation_native/NATIVE-RESULT.json');signed=read(work/'producer54/validation_signed/RESULT.json')
    need(native['status']=='PASS_CONTACT7624_COMPLETE_NATIVE' and signed['status']=='PASS_CONTACT7624_COMPLETE_SIGNED_APPLICATION' and native['word_canonical_sha256']==identity['candidate_canonical_sha256'] and nr['run_id']==sr['run_id']==identity['run_id'] and nr['exit']==sr['exit']==0,'actual application identity')
    for label,receipt,result_path in [('native',nr,work/'producer54/validation_native/NATIVE-RESULT.json'),('signed',sr,work/'producer54/validation_signed/RESULT.json')]:
        need(receipt['stage']==label and receipt['candidate_canonical_sha256']==identity['candidate_canonical_sha256'] and receipt['adapter_sha256']==custody['adapter_sha256'] and receipt['launcher_sha256']==custody['launcher_sha256'] and receipt[label+'_result_sha256']==sha(result_path.read_bytes()),'stage and result binding '+label)
    need(sr['stale_native_results_rejected']>=3 and set(sr['stale_native_receipt_bindings_rejected'])=={'run_id','native_result_sha256','adapter_sha256','launcher_sha256'} and set(sr['native_inventory_consumer_controls'])=={'missing_pair','substituted_pair','duplicate_pair','empty_pairs','boolean_pair','malformed_row'} and all(v is True for v in sr['native_inventory_consumer_controls'].values()),'consumer controls')
    sem=runpy.run_path(str(p/'semantic.py'));pairb=(work/'frozen-composition/CONTACT7624-PAIRS.json').read_bytes();need(sha(pairb)==sem['PAIR_SHA'],'pair pin');sem['verify_native_pairs'](ledger,json.loads(pairb),native['charts']['all_affected_pairs']);sem['verify_signed'](signed)
    signed_dir=work/'producer54/validation_signed';need(sha((signed_dir/'adapted/short_native_catalogue.py').read_bytes())==signed['catalogue_generator_sha256'],'protected catalogue generator pin')
    sr_source=signed['source_resource'];need(len(sr_source['logs'])==7 and sr_source['candidate_native_receipt_sha256']==sha((work/'producer54/validation_native/NATIVE-RESULT.json').read_bytes()),'derived source seven bindings')
    sem['verify_source7'](root/'observations/source7-observed',(signed_dir/'SOURCE-RESOURCE.json').read_bytes(),identity,newallow['unit'])
    for item in sr_source['logs']:
        need(sha((signed_dir/('SOURCE-'+item['check']+'.log')).read_bytes())==item['sha256'],'derived source log')
    source_bytes=(work/'frozen-composition/7624-NATIVE.json').read_bytes();need(sha(source_bytes)=='88de25922ac37156fcaee215467c0109cca9d4d2e326a49c0aa329ebb600e6e2','pinned source native receipt')
    package=p/'replay/kappa-research-20261116b/inputs/pr7624/research/p104-w2-primal-dual-bypass';pin_bytes=(package/'PINS.json').read_bytes();need(sha(pin_bytes)=='6a84e8ce4a23a9d60d388e2f42f583903d0a275b4be27e1c42738385b236a4a3','source package pins receipt');source_pins=json.loads(pin_bytes)
    need(len(source_pins)==33 and {x.relative_to(package).as_posix() for x in package.rglob('*') if x.is_file()}==set(source_pins)|{'PINS.json'},'34-file source package inventory')
    for rel,h in source_pins.items():need(sha((package/safe(rel)).read_bytes())==h,'source package pin')
    source_rows=json.loads(source_bytes)['charts']['all_affected_pairs'];need(len(source_rows)==1075,'source native denominator')
    source_pairs=[]
    for row in source_rows:
        pair=row['pair'];need(isinstance(pair,list) and len(pair)==2 and all(type(x) is int and x>=0 for x in pair) and type(row['columns']) is int and row['columns']==512 and type(row['adjoint_columns']) is int and row['adjoint_columns']==512 and row['absolute_phase_verified'] is True,'source pair and columns');source_pairs.append(tuple(pair))
    need(len(set(source_pairs))==1075 and set(source_pairs)=={tuple(x) for x in json.loads(pairb)['pinned_source_pairs']},'source pair receipt identity')
    cert=previouscase/'certificate-verifier';cs=read(cert/'status.json');cb=(cert/'fresh/certificate.json').read_bytes();need(cs['status']=='PASS_FRESH_204_CERTIFICATE_REPLAY' and cs['source_count']==cs['candidate_count']==204 and cs['fresh_report_sha256']==sha(cb),'fresh certificate receipt');sem['verify_certificates'](json.loads(cb))
    resource=read(case/'resources/RESOURCE-COMPARISON.json');need(resource['status']=='PASS_CONDITIONAL_COMMON_U_APPLICATION' and resource['supplier_premise_discharged'] is False,'resource scope')
    need(Fraction(final['claim'])==Fraction(resource['claim']) and Fraction(final['claim'])>=Fraction('0.003665370499') and Fraction(resource['gain_over_7624_raw_upper'])>0,'conditional claim binding')
    common=read(p/'replay/kappa-research-20261116b/qualification7624/COMMON-U.json');tariff=common['finite_same_tariff_assumptions']
    need(common['status']=='EXPLICIT_UNIMPLEMENTED_SUPPLIER_PREMISE' and tariff['ordinary_source_units_per_lifetime_pair']==4000 and tariff['scalar_services_per_INIT_or_CLEAR']==32 and tariff['scalar_elementary_coefficient_per_service']==2**20 and tariff['precision_context_cap']==4096 and tariff['fixed_banks_signed']==1156,'common U assumptions')
    return {'status':'PASS_ARTIFACT_INTEGRITY_ONLY','files_checked':PIN_COUNT,'frozen_inputs':502,'scientific_code_executed':False,'supplier_U_implemented':False,'selected_frontier_changed':False}

if __name__=='__main__': print(json.dumps(verify(),sort_keys=True))
