#!/usr/bin/env python3
"""Read-only artifact/custody validation. Does not import or rerun research code."""
import gzip,hashlib,json
from fractions import Fraction as Q
from pathlib import Path
EXPECTED_EXPORT_MAP_SHA='4d8063e313b74a4d3fede7537d49ea4fcdfc3dc89480c32d4be503d20fc28844'
EXPECTED_PIN_COUNT=int('475')
CANDIDATE='fd8aa08c7654791f9f6255898a83c06c8d114f22ab7bc7e6763c4fff2c015277'
CANDIDATE_GZIP='8a261c8db77e16921376a2b63fba45ad288e31fdaaa63d10f289bb07d7e0c665'
FREEZE='9ddf5e1e163ae02f08b7107068f92091f5274474b54b4e85f07622b12fe19e42'
PAIR_MANIFEST_SHA='9cdb49d017a0c941d7ca47bb7e3152ef55ced0310e7a49af38622c20f83025e1'
SOURCE_PAIR_FILE_SHA='15c8dc7965635ea926a39b45dc37c577fc339ae245333c194604a351ec8866f2'
SOURCE_CANON='48e1845e6b24832731705a3ff096b22d2b807428f7d625d06b45adfe3b5a738c'
def need(x,s):
    if not x:raise ValueError(s)
def digest(b):return hashlib.sha256(b).hexdigest()
def blob(b):return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def safe(s):
    p=Path(s);need(not p.is_absolute() and '..' not in p.parts and str(p)==s,'invalid package path');return p
def verify_native_pairs(ledger,manifest,pairs):
    # This semantic boundary is independently testable before global pins.
    # A zero or self-consistently altered denominator cannot be a pass.
    need(manifest['schema']=='compose7623-native-pairs/v1' and manifest['candidate_canonical_sha256']==CANDIDATE and manifest['source_canonical_sha256']==SOURCE_CANON,'pair manifest candidate/source identity')
    def unique(name,count):
        rows=manifest[name]
        need(isinstance(rows,list) and len(rows)==count,'pair manifest denominator '+name)
        values=[]
        for item in rows:
            need(isinstance(item,list) and len(item)==2 and all(type(v) is int and v>=0 for v in item),'pair shape '+name)
            values.append(tuple(item))
        need(len(set(values))==count,'duplicate manifest pair '+name)
        return set(values)
    source=unique('source_vs7481_pairs',964);pinned=unique('pinned_source_pairs',964)
    direct=unique('candidate_vs7481_pairs',963);route=unique('splice_route_pairs',13)
    union=unique('full_validation_pairs',964)
    need(union==(source|pinned|direct|route) and manifest['source_affected_count']==964,'source and complete pair union')
    info=ledger['native']
    need(info['candidate_pair_count']==964 and info['source_pair_count']==964 and info['candidate_vs7481_pair_count']==963,'ledger pair denominators')
    need(info['candidate_pair_manifest_sha256']==PAIR_MANIFEST_SHA and info['source_pair_file_sha256']==SOURCE_PAIR_FILE_SHA,'source-bound pair manifest pins')
    need(isinstance(pairs,list) and len(pairs)==964,'native pair receipt denominator')
    keys=[]
    for row in pairs:
        pair=row['pair'];need(isinstance(pair,list) and len(pair)==2 and all(type(v) is int and v>=0 for v in pair),'native pair shape')
        need(row['columns']==row['adjoint_columns']==512 and row['absolute_phase_verified'] is True,'native pair coverage')
        keys.append(tuple(pair))
    need(len(set(keys))==964 and set(keys)==union,'native pair identity or duplicate')
    return True


def verify(package=None):
    p=Path(package or Path(__file__).resolve().parent).resolve();pins=read(p/'PINS.json')
    need(pins['schema']=='contact7623-file-pins/v1' and len(pins['files'])==EXPECTED_PIN_COUNT,'fixed complete file denominator')
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
    need(len(frozen['files'])==export['frozen_file_count']==len(fr)==321 and sum(r['bytes'] for r in frozen['files'])==export['frozen_byte_count']==45965679,'fixed frozen-input denominator')
    need(len({r['package_path'] for r in rows})==len(rows) and {r['original_path'] for r in fr}=={r['path'] for r in frozen['files']},'export source and destination inventories')
    by_source={r['original_path']:r for r in fr}
    for r in frozen['files']:
        z=by_source[r['path']];need(z['sha256']==r['sha256'] and z['bytes']==r['bytes'],'original frozen bytes')
    for r in rows:
        rel=safe(r['package_path']);b=(p/rel).read_bytes();need(digest(b)==r['sha256'] and blob(b)==r['git_blob'] and len(b)==r['bytes'],'mapped evidence '+str(rel))
    need(export['candidate_canonical_sha256']==CANDIDATE,'export candidate')
    first_bytes=(p/'evidence/first-gate/ORIGINAL-FREEZE.json').read_bytes()
    need(digest(first_bytes)=='34c2a3b102024eb9e655a16dc307b2443ba62b3e1461c9fa40b3426726739be8','first-gate freeze')
    first=json.loads(first_bytes);need(len(first['files'])==99,'first-gate frozen denominator')
    for entry in first['files']:
        need(entry['path'] in by_source and by_source[entry['path']]['sha256']==entry['sha256'] and by_source[entry['path']]['bytes']==entry['bytes'],'first-gate source closure')
    fg_guard=read(p/'evidence/first-gate/control/RESULT.json');fg_allow=read(p/'evidence/first-gate/control/ALLOW.json')
    need(fg_guard['group_empty'] is True and fg_guard['differential_case_completed'] is True and fg_allow['freeze_sha256']==digest(first_bytes),'first-gate guarded execution')
    root=p/'replay/kappa-research-20261116';fg=root/'compose7623/run/case';fgr=read(fg/'RESULT.json')
    need(fgr['status']=='PASS_DIFFERENTIAL_ONLY_PROVISIONAL_UNDER_COMMON_U' and len(fgr['receipt_hashes'])==13,'first gate scope and receipt denominator')
    for rel,h in fgr['receipt_hashes'].items():need(digest((fg/safe(rel)).read_bytes())==h,'first-gate receipt '+rel)
    cb=(fg/'built/candidate-word.json.gz').read_bytes();word=json.loads(gzip.decompress(cb));canonical=json.dumps(word,sort_keys=True,separators=(',',':')).encode()
    need(digest(cb)==CANDIDATE_GZIP and digest(canonical)==CANDIDATE and len(word['program'])==77271,'immutable candidate bytes and shape')
    exact=read(fg/'exact/status.json');rank=read(fg/'rankone/RANKONE.json');phase=read(fg/'physical/PHYSICAL.json');price=read(fg/'price/PRICE.json')
    need(exact['status']=='U_CONDITIONAL_LITERAL_EXACT_ONLY' and exact['changed_clear_count']==1 and exact['changed_interface_count']==12,'exact observation scope')
    need(rank['status']=='RANKONE_ONLY_UNQUALIFIED' and len(rank['clear_beta'])==180 and rank['source_covector']=={'902':'1','985':'1'} and rank['endpoint_beta']=={},'rank-one certificate inventory')
    need(phase['route_pairs_tested']==13 and phase['forward_columns']==phase['adjoint_columns']==6656,'changed-phase denominator')
    case=p/'evidence/qualification/run/case';final=read(case/'RESULT.json');res=read(case/'resources/RESOURCE-COMPARISON.json')
    need(final['status']=='PASS_QUALIFIED_CONDITIONAL_COMMON_U_KAPPA' and final['conditional_application_qualified'] is True,'full conditional qualification')
    need(final['supplier_U_implemented'] is False and final['same_original_premise_dominance_established'] is False and final['selected_frontier_changed'] is False,'preserved admission boundary')
    stages=final['stages'];need([r['name'] for r in stages]==['prepare','certificates','certificate-verifier','native','signed','resources'] and all(r['exit_code']==0 for r in stages),'complete six-stage execution')
    need(res['status']=='PASS_CONDITIONAL_COMMON_U_APPLICATION' and digest((case/'resources/RESOURCE-COMPARISON.json').read_bytes())==final['resource_comparison_sha256'],'complete resource receipt')
    work=case/'work';native=read(work/'producer54/validation_native/NATIVE-RESULT.json');signed=read(work/'producer54/validation_signed/RESULT.json');nr=read(work/'native.receipt.json');sr=read(work/'signed.receipt.json');identity=read(work/'QUALIFICATION-ID.json')
    need(native['status']=='PASS_CONTACT7623_COMPLETE_NATIVE' and native['word_canonical_sha256']==CANDIDATE and signed['status']=='PASS_CONTACT7623_COMPLETE_SIGNED_APPLICATION','application result identities')
    need(nr['run_id']==sr['run_id']==identity['run_id']==res['run_id'] and nr['exit']==sr['exit']==0,'fresh native/signed attempt')
    need(sr['stale_native_results_rejected']==3 and set(sr['stale_native_receipt_bindings_rejected'])=={'run_id','native_result_sha256','adapter_sha256','launcher_sha256'},'stale result/receipt controls')
    ledger=read(work/'CONTACT7623-ADAPTERS.json');pairs=native['charts']['all_affected_pairs']
    pair_path=work/'frozen-composition/CONTACT7623-PAIRS.json';pair_bytes=pair_path.read_bytes()
    need(digest(pair_bytes)==PAIR_MANIFEST_SHA,'actual source-bound candidate pair manifest')
    verify_native_pairs(ledger,json.loads(pair_bytes),pairs)
    cat=signed['catalogue'];need(cat and sum(x['checked_maps'] for x in cat)==cat[0]['catalogue_size'] and sum(x['main_boundary_pairs'] for x in cat)==104,'complete actual catalogue and boundaries')
    cursor=0
    for row in cat:
        need(row['slice_start']==cursor and row['slice_stop']-cursor==row['checked_maps'] and row['catalogue_size']==cat[0]['catalogue_size'] and row['word_sha256']==CANDIDATE_GZIP and row['phase_control_rejected'],'catalogue slice identity')
        cursor=row['slice_stop']
    need(cursor==cat[0]['catalogue_size'],'catalogue final slice')
    need(signed['source_resource']['status']=='DERIVED_FRESH_SOURCE_RESOURCE_ONLY' and signed['source_resource']['source_catalogue_rerun'] is False,'source resource scope')
    after=signed['price']['after'];need(sum(after['P'].values())==110111 and sum(after['T'].values())==22461 and after['S']==1424,'complete signed profile')
    need(Q(price['claim'])==Q(final['claim'])==Q(res['claim'])==Q('0.003663028410') and Q(price['gain_over_published_old_upper'])>0,'actual directed conditional claim')
    u=read(root/'qualification7623/COMMON-U.json');tariff=u['finite_same_tariff_assumptions']
    need(u['status']=='EXPLICIT_UNIMPLEMENTED_SUPPLIER_PREMISE' and res['supplier_premise_discharged'] is False and tariff['ordinary_source_units_per_lifetime_pair']==4000 and tariff['scalar_services_per_INIT_or_CLEAR']==32 and tariff['scalar_elementary_coefficient_per_service']==2**20 and tariff['precision_context_cap']==4096 and 'ALL allocation' in tariff['ordinary_scope'] and 'not a measured reset constant or a spare allowance' in tariff['ordinary_scope'],'unimplemented full-extent common U tariff')
    certificate=read(case/'certificate-verifier/status.json')
    need(certificate['status']=='PASS_SOURCE_AND_CANDIDATE_PUBLIC_CLEAR_RELATIONS_ONLY' and len(certificate['verifications'])==2 and all(x['exit_code']==0 for x in certificate['verifications']),'both 180-CLEAR relation verifications')
    custody=read(p/'evidence/RUN-CUSTODY.json')
    need(custody['status']=='AUTHOR_OBSERVED_RUNNING_GUARDED_QUALIFICATION' and custody['qualification_identity']==identity and custody['adapter_sha256']==digest((work/'CONTACT7623-ADAPTERS.json').read_bytes()) and custody['freeze_sha256']==FREEZE,'author observed run identity')
    source7=p/'evidence/source7-observed'
    if source7.exists():
        observation=read(source7/'OBSERVATION.json');source_resource=work/'producer54/validation_signed/SOURCE-RESOURCE.json'
        need(observation['status']=='AUTHOR_OBSERVED_COMPLETED_SOURCE7_INTERMEDIATE_FILES' and observation['run_id']==identity['run_id'] and observation['source_resource_sha256']==digest(source_resource.read_bytes()),'author observed source resource identity')
        source_meta=read(source_resource);captured={x['name']:x for x in observation['files']}
        need(len(captured)==len(observation['files'])==19,'source7 capture denominator')
        need({q.name for q in source7.iterdir()}==set(captured)|{'OBSERVATION.json'},'source7 exact capture inventory')
        for name,item in captured.items():
            b=(source7/name).read_bytes();need(len(b)==item['bytes'] and digest(b)==item['sha256'],'source7 capture '+name)
        need(len(source_meta['check_sha256'])==7 and all(captured[name]['sha256']==h for name,h in source_meta['check_sha256'].items()),'source7 output receipts')
        need(all(captured[name]['sha256']==h for name,h in source_meta['adapter']['adapted_sha256'].items()),'source7 adapted script receipts')
        for name,key in (('DERIVED-NATIVE.json','source_native_derived_sha256'),('WORD.json.gz','source_word_gzip_sha256'),('ODD-TYPE-AB-CALLER.json','caller_sha256'),('CURRENT-PRICE.json','source_current_price_sha256'),('COHORT-PRICE.json','source_cohort_price_sha256')):
            need(captured[name]['sha256']==source_meta[key],'source7 source evidence '+name)
    else:need(export['source7_capture']=='unavailable_not_independently_captured','missing declared source7 capture')
    guard=read(p/'evidence/qualification/run-control/RESULT.json');operational=read(p/'evidence/qualification/run/RESOURCE.json')
    need(guard['unit']==custody['unit'] and guard['properties']['ControlGroup']==custody['ready']['cgroup'] and str(guard['properties']['MainPID'])==str(custody['ready']['pid']),'author observed guarded identity')
    need(guard['group_empty'] is True and guard['differential_case_completed'] is True and operational['differential_case_completed'] is True,'completed guarded service and cleanup')
    return {'status':'PASS_ARTIFACT_INTEGRITY_ONLY','files_checked':EXPECTED_PIN_COUNT,'frozen_inputs':321,'claim':'0.003663028410','scientific_code_executed':False,'supplier_U_implemented':False,'same_original_premise_dominance':False,'hosted_scientific_replay_inferred':False}
if __name__=='__main__':print(json.dumps(verify(),sort_keys=True))
