#!/usr/bin/env python3
"""Read-only artifact/custody validation. Does not import or rerun research code."""
import gzip,hashlib,json
from fractions import Fraction as Q
from pathlib import Path
EXPECTED_EXPORT_MAP_SHA='169803dccc3cdc56b2b22636eae24117cd930e6f8bb15495ccafa9d5c085d4a9'
EXPECTED_PIN_COUNT=int('399')
CANDIDATE='03da65fb97ffaf4d0e9756f3867df588b162975f6015d8458821d05b5fcb006b'
CANDIDATE_GZIP='4d742e0b6e915cc3c3d31d18d5d2703c1f943c695c25d7c5a24f04626c1f5235'
FREEZE='f30224e5bfbb26c283bad46e599c44450081f0130ac0ff5a70871c0dd85a49a2'
def need(x,s):
    if not x:raise ValueError(s)
def digest(b):return hashlib.sha256(b).hexdigest()
def blob(b):return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def safe(s):
    p=Path(s);need(not p.is_absolute() and '..' not in p.parts and str(p)==s,'invalid package path');return p
def verify(package=None):
    p=Path(package or Path(__file__).resolve().parent).resolve();pins=read(p/'PINS.json')
    need(pins['schema']=='contact7620-file-pins/v1' and len(pins['files'])==EXPECTED_PIN_COUNT,'fixed complete file denominator')
    actual=set()
    for f in p.rglob('*'):
        need(not f.is_symlink(),'symbolic package entry')
        if f.is_file() and f!=p/'PINS.json':actual.add(f.relative_to(p).as_posix())
    need(actual==set(pins['files']),'complete package file inventory')
    for rel,row in pins['files'].items():
        f=p/safe(rel);b=f.read_bytes();need(len(b)==row['bytes'] and digest(b)==row['sha256'] and blob(b)==row['git_blob'],'file bytes '+rel)
    eb=(p/'EXPORT-MAP.json').read_bytes();need(digest(eb)==EXPECTED_EXPORT_MAP_SHA,'reviewed export map hash')
    export=json.loads(eb);freeze_bytes=(p/'evidence/ORIGINAL-FREEZE.json').read_bytes();need(digest(freeze_bytes)==export['freeze_sha256']==FREEZE,'scientific freeze identity')
    frozen=json.loads(freeze_bytes);rows=export['files'];fr=[r for r in rows if r['origin']=='frozen_input']
    need(len(frozen['files'])==export['frozen_file_count']==len(fr)==266,'fixed frozen-input denominator')
    need(len({r['package_path'] for r in rows})==len(rows) and {r['original_path'] for r in fr}=={r['path'] for r in frozen['files']},'export source and destination inventories')
    by_source={r['original_path']:r for r in fr}
    for r in frozen['files']:
        z=by_source[r['path']];need(z['sha256']==r['sha256'] and z['bytes']==r['bytes'],'original frozen bytes')
    for r in rows:
        rel=safe(r['package_path']);b=(p/rel).read_bytes();need(digest(b)==r['sha256'] and blob(b)==r['git_blob'] and len(b)==r['bytes'],'mapped evidence '+str(rel))
    need(export['candidate_canonical_sha256']==CANDIDATE,'export candidate')
    root=p/'replay/kappa-research-20261115b';fg=root/'compose7620/run/case';fgr=read(fg/'RESULT.json')
    need(fgr['status']=='PASS_DIFFERENTIAL_ONLY_PROVISIONAL_UNDER_COMMON_U' and len(fgr['receipt_hashes'])==12,'first gate scope and receipt denominator')
    for rel,h in fgr['receipt_hashes'].items():need(digest((fg/safe(rel)).read_bytes())==h,'first-gate receipt '+rel)
    cb=(fg/'built/candidate-word.json.gz').read_bytes();word=json.loads(gzip.decompress(cb));canonical=json.dumps(word,sort_keys=True,separators=(',',':')).encode()
    need(digest(cb)==CANDIDATE_GZIP and digest(canonical)==CANDIDATE and len(word['program'])==77188,'immutable candidate bytes and shape')
    exact=read(fg/'exact/status.json');rank=read(fg/'rankone/RANKONE.json');phase=read(fg/'physical/PHYSICAL.json');price=read(fg/'price/PRICE.json')
    need(exact['status']=='U_CONDITIONAL_LITERAL_EXACT_ONLY' and exact['changed_clear_count']==1 and exact['changed_interface_count']==12,'exact observation scope')
    need(rank['status']=='RANKONE_ONLY_UNQUALIFIED' and len(rank['clear_beta'])==167 and rank['source_covector']=={'902':'1','985':'1'} and rank['endpoint_beta']=={},'rank-one certificate inventory')
    need(phase['route_pairs_tested']==13 and phase['forward_columns']==phase['adjoint_columns']==6656,'changed-phase denominator')
    case=p/'evidence/qualification/run/case';final=read(case/'RESULT.json');res=read(case/'resources/RESOURCE-COMPARISON.json')
    need(final['status']=='PASS_QUALIFIED_CONDITIONAL_COMMON_U_KAPPA' and final['conditional_application_qualified'] is True,'full conditional qualification')
    need(final['supplier_U_implemented'] is False and final['same_original_premise_dominance_established'] is False and final['selected_frontier_changed'] is False,'preserved admission boundary')
    stages=final['stages'];need([r['name'] for r in stages]==['prepare','certificates','certificate-verifier','native','signed','resources'] and all(r['exit_code']==0 for r in stages),'complete six-stage execution')
    need(res['status']=='PASS_CONDITIONAL_COMMON_U_APPLICATION' and digest((case/'resources/RESOURCE-COMPARISON.json').read_bytes())==final['resource_comparison_sha256'],'complete resource receipt')
    work=case/'work';native=read(work/'producer54/validation_native/NATIVE-RESULT.json');signed=read(work/'producer54/validation_signed/RESULT.json');nr=read(work/'native.receipt.json');sr=read(work/'signed.receipt.json');identity=read(work/'QUALIFICATION-ID.json')
    need(native['status']=='PASS_CONTACT7620_COMPLETE_NATIVE' and native['word_canonical_sha256']==CANDIDATE and signed['status']=='PASS_CONTACT7620_COMPLETE_SIGNED_APPLICATION','application result identities')
    need(nr['run_id']==sr['run_id']==identity['run_id']==res['run_id'] and nr['exit']==sr['exit']==0,'fresh native/signed attempt')
    need(sr['stale_native_results_rejected']==2 and set(sr['stale_native_receipt_bindings_rejected'])=={'run_id','native_result_sha256','adapter_sha256','launcher_sha256'},'stale result/receipt controls')
    need(len(native['charts']['all_affected_pairs'])==837 and all(x['columns']==x['adjoint_columns']==512 and x['absolute_phase_verified'] for x in native['charts']['all_affected_pairs']),'full physical union')
    cat=signed['catalogue'];need(cat and cat[0]['catalogue_size']==3089 and sum(x['checked_maps'] for x in cat)==3089 and sum(x['main_boundary_pairs'] for x in cat)==104,'complete actual catalogue and boundaries')
    need(signed['source_resource']['status']=='DERIVED_FRESH_SOURCE_RESOURCE_ONLY' and signed['source_resource']['source_catalogue_rerun'] is False,'source resource scope')
    after=signed['price']['after'];need(sum(after['P'].values())==110111 and sum(after['T'].values())==22461 and after['S']==1424,'complete signed profile')
    need(Q(price['claim'])==Q(final['claim'])==Q(res['claim'])==Q('0.003661727792') and Q(price['gain_over_published_old_upper'])>0,'actual directed conditional claim')
    u=read(root/'qualification7620/COMMON-U.json');need(u['status']=='EXPLICIT_UNIMPLEMENTED_SUPPLIER_PREMISE' and res['supplier_premise_discharged'] is False,'unimplemented common U')
    guard=read(p/'evidence/qualification/run-control/RESULT.json');operational=read(p/'evidence/qualification/run/RESOURCE.json')
    need(guard['group_empty'] is True and guard['differential_case_completed'] is True and operational['differential_case_completed'] is True,'completed guarded service and cleanup')
    return {'status':'PASS_ARTIFACT_INTEGRITY_ONLY','files_checked':EXPECTED_PIN_COUNT,'frozen_inputs':266,'claim':'0.003661727792','scientific_code_executed':False,'supplier_U_implemented':False,'same_original_premise_dominance':False,'hosted_scientific_replay_inferred':False}
if __name__=='__main__':print(json.dumps(verify(),sort_keys=True))
