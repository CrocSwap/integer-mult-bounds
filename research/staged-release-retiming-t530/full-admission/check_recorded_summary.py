#!/usr/bin/env python3
"""Check the PUBLIC NORMALIZED RECORDED SUMMARY with standard-library code.

This intentionally has a narrower scope than the private archive checker. It
checks public-file integrity, declared original/public normalization hashes and
internal recorded status/profile/receipt references. The original full source,
runtime and native archives are not supplied or authenticated by this check.
Original hashes are historical metadata, NOT hashes of the normalized bytes.
Run reproduce.py --materialize-only for fresh source reconstruction; omit that
flag for the separate complete scientific replay with inherited assumptions.
"""
from pathlib import Path, PurePosixPath
from fractions import Fraction as Q
import argparse
import hashlib
import json

SOURCE = 'fb47533a401d1d13719be8b9aab91fe5313931ca62d40dba336eab6a96275aa0'
PROFILE = {'1':11747920,'2':3453480,'3':1112042,'4':486540,'5':103690,'8':38160,'48':202828}
LOCAL = {'1':2437,'2':724,'3':226,'4':102,'5':20,'8':8}
C = Q('0.001730394391813963415120')
K = C-Q(1,10**46)-Q(1,10**70)
STAGES = ['owners','parent-lift','rebind','discovery','outer-check_ledger.py','outer-independent_check.py','release']
PARENT = 'e0eefc96567fbb45e19e6de0ca295381dbe0e686c08ddc783639b065c7c791d4'
RETAINED = {'base':'e8e6e78ff7422275c38324499e1f33fb2ecd30de9503aef2b8f1ee80d8c4df8e','extra':'7b0e9fbda32749aabc7e156d9fe09bceb0624a178628fe69e5dfea783462f905'}
NATIVE_STAGES = ['native','ledgers','local-replay','wrappers','phases']
WORDS = {'base':'6df3356808e29909776be8bc0faf03df983401a267c2d740d1ac2dbcaa278269','extra':'65624efec36b35934b750c1741ba2ad4e6df3cff86e44536b0c016ebddb0fb55'}

def need(value, label):
    if not value:
        raise ValueError(label)

def digest(data):
    return hashlib.sha256(data).hexdigest()

def file_sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):
            h.update(b)
    return h.hexdigest()

def jread(path):
    return json.loads(path.read_text())

def check(root):
    pins=jread(root/'PUBLIC-PINS.json')
    need(pins['schema']=='public-retiming-summary-files/1','public pin schema')
    actual={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() and p.name not in {'PUBLIC-PINS.json','PUBLIC-CHECK-RESULT.json'}}
    need(set(pins['sha256'])==actual,'complete public summary file inventory')
    for name,h in pins['sha256'].items():
        p=PurePosixPath(name)
        need(not p.is_absolute() and '..' not in p.parts,'unsafe evidence path')
        need(file_sha(root/name)==h,'recorded file hash: '+name)
    provenance=jread(root/'PUBLIC-PROVENANCE.json')
    need(provenance['schema']=='public-normalized-recorded-summary/1','normalization provenance schema')
    for name,record in provenance['files'].items():
        need(file_sha(root/name)==record['public_sha256'],'public normalization digest '+name)
        need(record['normalization'] in ('none','workspace-prefix-to-token'),'documented normalization rule')
        if record['normalization']=='none':
            need(record['original_sha256']==record['public_sha256'],'unchanged bytes really unchanged')
    def recorded_sha(path):
        # This is an ORIGINAL HASH DECLARATION. It does not authenticate unavailable raw bytes.
        name=path.relative_to(root).as_posix()
        return provenance['files'][name]['original_sha256'] if name in provenance['files'] else file_sha(path)
    def metadata(prefix,expected,names):
        data={}
        for name in names:
            path=root/'evidence'/prefix/name
            need(recorded_sha(path)==expected[name],'selected original metadata digest '+name)
            data[name]=path.read_bytes()
        return data
    ev=root/'evidence'
    rebuilt=jread(ev/'PUBLIC-SOURCE-REBUILD-RESULT.json')
    need(rebuilt['status']=='PASS_PUBLIC_SOURCE_REBUILD_654_FILES' and rebuilt['source_manifest_sha256']==SOURCE and rebuilt['source_files']==654,'recorded public source rebuild')
    need(rebuilt['main_commit']=='20ecf2891d80b5acf18d980b2164fb44ea7faa90' and rebuilt['exported_inputs']==540,'recorded pinned main export')
    need([s['name'] for s in rebuilt['stages']]==['original-materialization','retiming-source','preserved-staged-review','new-retiming-review'] and all(s['exit_code']==0 for s in rebuilt['stages']),'recorded public source rebuild gates')
    manifest=jread(ev/'SOURCE-MANIFEST.json')
    need(recorded_sha(ev/'SOURCE-MANIFEST.json')==SOURCE and len(manifest)==654,'frozen source manifest')
    need(recorded_sha(ev/'retained-parent-CLAIM.json')==manifest['vendor/pr1297/CLAIM.json'],'selected retained source claim')
    source={'vendor/pr1297/CLAIM.json':(ev/'retained-parent-CLAIM.json').read_bytes()}
    nr=jread(ev/'NATIVE-NATIVE-RECEIPT.json')
    need(nr['status']=='PASS_COMPOSED_FRESH_NATIVE_PROVIDERS_AND_AUTHENTICATED_CACHE','native receipt status')
    need(set(nr['providers'])=={'base','extra'},'exact fresh provider set')
    need(nr['manifest_sha256']==SOURCE and nr['fresh_current_provider_count']==2,'two fresh changed providers')
    need(nr['reused_retained_native_count']==2 and nr['reused_retained_parent'] is True and nr['fresh_retained_parent'] is False,'explicit retained reuse')
    nr_result=jread(ev/'NATIVE-RESULT.json')
    need(nr_result['status']=='PASS_TWO_FRESH_SHARED_KERNEL_NATIVE_CHAINS_AUTHENTICATED_PARENT_REUSE','native preparation completion')
    need(nr_result['native_receipt_sha256']==recorded_sha(ev/'NATIVE-NATIVE-RECEIPT.json'),'native receipt chain')
    need(nr_result['source_manifest_sha256']==SOURCE,'native source chain')
    need(nr_result['environment_sha256']==recorded_sha(ev/'NATIVE-ENVIRONMENT.json'),'native environment chain')
    need(nr_result['preparer_sha256']==recorded_sha(root/'scripts/prepare_extension_native.py'),'actual native preparer binding')
    need(nr_result['stages']==jread(ev/'NATIVE-STAGES.json'),'native stage identity')
    need([s['name'] for s in nr_result['stages']]==['fresh-current-base','fresh-current-extra'],'exact two fresh native stages')
    old_receipt=jread(ev/'RETAINED-REUSE-RECEIPT.json')
    need(nr['retained_reuse_receipt_sha256']==recorded_sha(ev/'RETAINED-REUSE-RECEIPT.json'),'actual retained reuse receipt')
    parent_dir='_receipts/'+PARENT+'/'
    names=[parent_dir+n for n in ['RECEIPT.json','RESULT.json','STAGES.json']]
    for word in RETAINED.values():
        names.extend([word+'/STEPS.json',word+'/CACHE.json'])
    for kind,word in WORDS.items():
        need(nr['providers'][kind]['word_sha256']==word,'changed word binding')
        names.extend([word+'/STEPS.json',word+'/local/LOCAL-CHECKS.json',word+'/local/INDEPENDENT-LOCAL-REPLAY.json'])
    native=metadata('native-summary',nr['cache_files'],names)
    pr=json.loads(native[parent_dir+'RECEIPT.json'])
    need(digest(native[parent_dir+'RECEIPT.json'])==nr['retained_parent_receipt_sha256']==old_receipt['retained_parent_receipt_sha256'],'retained parent receipt chain')
    need(pr['schema']=='parent-receipt/1' and pr['vendor_manifest_sha256']==PARENT==manifest['vendor/pr1297/MANIFEST.json'],'retained parent manifest')
    need(pr['claim_sha256']==manifest['vendor/pr1297/CLAIM.json'] and pr['words']==RETAINED,'retained parent claim and words')
    need(set(pr['files'])=={'RESULT.json','STAGES.json'},'retained parent receipt file set')
    for name,h in pr['files'].items():
        need(digest(native[parent_dir+name])==h,'retained parent result file binding')
    parent_result=json.loads(native[parent_dir+'RESULT.json'])
    parent_stages=json.loads(native[parent_dir+'STAGES.json'])
    need(parent_result['status']=='PASS_GLOBAL_MIXED_X54_FUSIONS_NATIVE_AND_STRICT_ADMISSION','retained parent complete status')
    need(parent_result['base_native_reuse'] is True and parent_result['extra_native_reuse'] is True,'retained parent reuse explicit')
    need(parent_result['kappa']==json.loads(source['vendor/pr1297/CLAIM.json'])['kappa'],'retained parent exact kappa')
    need(parent_result['stages']==parent_stages and len(parent_stages)==16 and all(s['exit_code']==0 for s in parent_stages),'retained parent sixteen stages')
    for kind,word in RETAINED.items():
        need(word==manifest['vendor/pr1297/'+('gauge44-word.json.gz' if kind=='base' else 'extra-word.json.gz')],'retained literal word source')
        st=json.loads(native[word+'/STEPS.json'])
        need([x['step'] for x in st]==NATIVE_STAGES and all(x['exit_code']==0 for x in st),'retained native five stages')
        cj=json.loads(native[word+'/CACHE.json'])
        subset={k.removeprefix(word+'/'):h for k,h in nr['cache_files'].items() if k.startswith(word+'/') and k!=word+'/CACHE.json'}
        need(cj['word_sha256']==word and cj['files']==subset,'complete retained native cache')
    for name,h in nr['cache_files'].items():
        if name.startswith(parent_dir) or any(name.startswith(w+'/') for w in RETAINED.values()):
            need(old_receipt['cache_files'][name]==h,'retained cache exact inherited bytes')
    for s in nr_result['stages']:
        need(s['exit_code']==0,'fresh native exit status')
        kind=s['name'].split('-')[-1]
        need(s['log_sha256']==recorded_sha(ev/('native-'+kind+'.log')),'fresh native log chain')
        need(s['result_sha256']==recorded_sha(ev/('native-'+kind+'-RESULT.json')),'fresh native result chain')
        need(s['script_sha256']==manifest['new/fastnative/run_native.py'],'fresh native actual script source')
        fresh=jread(ev/('native-'+kind+'-RESULT.json'))
        need(fresh['status']=='PASS_COMPLETE_T74_NATIVE_REPLAY' and fresh['word_sha256']==WORDS[kind],'fresh native status and word')
        need([q['step'] for q in fresh['steps']]==NATIVE_STAGES and all(q['exit_code']==0 for q in fresh['steps']),'fresh native full five-stage receipt')
    for kind,word in WORDS.items():
        need(nr['providers'][kind]['complete_native_files']=={k.removeprefix(word+'/'):h for k,h in nr['cache_files'].items() if k.startswith(word+'/') and k!=word+'/CACHE.json'},'complete fresh provider cache binding')
        st=json.loads(native[word+'/STEPS.json'])
        need([x['step'] for x in st]==NATIVE_STAGES and all(x['exit_code']==0 for x in st),'five native gates')
        checks=json.loads(native[word+'/local/LOCAL-CHECKS.json'])
        for orientation in ['forward','backward']:
            row=checks[orientation]
            need(row['paid_profile']==LOCAL and row['all_columns']==632 and row['zero_buffers_returned_to_zero']==91,'native profile/columns/buffers')
    result=jread(ev/'ADMISSION-RESULT.json')
    need(result['status']=='PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE','complete admission status')
    need(result['source_manifest_sha256']==SOURCE and result['source_file_count']==654,'admission source binding')
    need(result['native_receipt_sha256']==recorded_sha(ev/'NATIVE-NATIVE-RECEIPT.json'),'admission native binding')
    need(result['profile']==PROFILE and result['replicas']==530 and result['actual_expected_helpers']==408,'admission profile/dimensions')
    need(Q(result['complex_lower'])==C and Q(result['kappa'])==Q(result['kappa_decimal'])==K,'exact certified endpoint')
    need(K>Q('0.001730071864705779882540'),'strict improvement over PR3626 before its margins')
    stages=jread(ev/'ADMISSION-STAGES.json')
    need(stages==result['stages'] and [x['name'] for x in stages]==STAGES,'seven-stage receipt chain')
    bindings=jread(ev/'STAGE-SCRIPT-BINDINGS.json')
    for s in stages:
        need(s['exit_code']==0,'admission stage exit status')
        need(s['log_sha256']==recorded_sha(ev/'logs'/(s['name']+'.log')),'admission log binding '+s['name'])
        need(s['script_sha256']==recorded_sha(root/bindings[s['name']]),'admission script binding '+s['name'])
    package_manifest=jread(ev/'PACKAGE-MANIFEST.json')
    package_hash=recorded_sha(ev/'PACKAGE-MANIFEST.json')
    need(result['package_manifest_sha256']==package_hash,'final package manifest chain')
    stage_sources={'owners':'reconstruct.py','parent-lift':'lift_parent.py','rebind':'new/rebind.py','discovery':'replay.py','outer-check_ledger.py':'outer/check_ledger.py','outer-independent_check.py':'outer/independent_check.py','release':'verify_release.py'}
    for stage in stages:
        need(stage['script_sha256']==package_manifest[stage_sources[stage['name']]],'execution script in admitted package')
    selected=['CLAIM.json','outer/LEDGER.json','outer/B.json','outer/OUTER-CLAIM.json','new/SPEC.json']
    packed=metadata('runtime-summary',package_manifest,selected)
    spec=json.loads(packed['new/SPEC.json'])
    need(spec['expected']['global_profile']==PROFILE and Q(spec['expected']['complex_lower'])==C,'frozen final specification')
    ledger=json.loads(packed['outer/LEDGER.json'])
    need(Q(ledger['rows']['struct_boundary_radix_union']['kappa']['rational'])==K,'modern ledger headline chain')
    outer_claim=json.loads(packed['outer/OUTER-CLAIM.json'])
    b=json.loads(packed['outer/B.json'])
    need(Q(outer_claim['kappa'])==Q(outer_claim['kappa_rational'])==K,'outer claim headline')
    need(b['profile']==PROFILE and b['live']==474880 and Q(b['b'])<C<Q(b['b_above_endpoint']),'outer/supplier endpoint bracket')
    rr=jread(ev/'RELEASE-RECEIPT.json')
    need(rr['status']=='PASS_RELEASE' and Q(rr['kappa_decimal'])==K,'terminal release status and kappa')
    need(rr['manifest_sha256']==package_hash and result['release_receipt_sha256']==recorded_sha(ev/'RELEASE-RECEIPT.json'),'terminal release receipt chain')
    supplier=jread(ev/'SUPPLIER-RESULT.json')
    need(supplier['status']=='PASS_T74_EXACT_FILL_COMPLETE_FINITE_ADMISSION' and supplier['manifest_sha256']==package_hash,'completed supplier manifest binding')
    need(supplier['stages']==jread(ev/'SUPPLIER-STAGES.json') and all(s['exit_code']==0 for s in supplier['stages']),'supplier execution stages')
    need(any(s['name']=='staged-release-retime-review' for s in supplier['stages']),'new retiming reviewer executed')
    need(Q(supplier['kappa'])==Q(json.loads(packed['CLAIM.json'])['kappa']),'legacy supplier claim is separate from modern outer headline')
    need(supplier['controls']=={'admission':139,'bit':12,'controller':15,'independent_owner':8,'geometry':6},'inherited rejection gates retained')
    asm=jread(ev/'ASSEMBLY.json')
    need(asm['status']=='PASS_GAUGE44_NATIVE_EXACT_GLOBAL_ASSEMBLY' and len(asm['outer'])==47,'strict supplier assembly')
    need(asm['complex_profile']==PROFILE and Q(asm['complex_lower'])==C,'assembly profile/endpoint')
    invoice=jread(ev/'PREFIX-AND-INVOICE.json')
    need(invoice['status']=='PASS_INDEPENDENT_MIXED_ASYNC_SCALAR_PREFIX_AND_FINITE_INVOICE','prefix/invoice status')
    need(invoice['physical']==475389 and invoice['live']==474880 and invoice['helpers']==408 and invoice['private_zero_buffers']==91,'physical stock')
    need(invoice['global_prefix_bits']==1479 and invoice['charged_prefix_bits']==2048,'global prefix reserve')
    need(set(invoice['strict_checks'])=={'local_primitive_bound','logical','router','literal','mass','precision','tape','row','halving'},'complete finite invoice gate set')
    need(invoice['blocknorm']['required_reserve_bits']==1512 and all(v is True for v in invoice['strict_checks'].values()),'complete finite invoice gates')
    need(invoice['complete_invocation_sweeps']==4770 and len(invoice['selected_calls'])==4770,'whole-call prefix coverage')
    need(invoice['owner_audit_sha256']==recorded_sha(ev/'OWNER-AUDIT.json'),'prefix owner chain')
    need(invoice['controller_audit_sha256']==recorded_sha(ev/'CONTROLLER-AUDIT.json'),'prefix controller chain')
    need(set(invoice['providers'])=={'extra','gauge44'},'exact current invoice providers')
    for pid,provider in invoice['providers'].items():
        word=WORDS['base' if pid=='gauge44' else 'extra']
        for name,h in provider['artifacts'].items():
            need(nr['cache_files'][word+'/local/'+name]==h,'invoice native artifact binding '+pid+'/'+name)
        need(set(provider['artifacts'])=={x.removeprefix(word+'/local/') for x in nr['cache_files'] if x.startswith(word+'/local/')},'complete invoice provider artifact set')
        need(provider['paid_profile']==LOCAL,'invoice changed provider bill')
        for orient,bits in [('forward',89),('backward',95)]:
            need(provider['local'][orient]['prefix_bits']==bits,'native prefix')
    return {'status':'PASS_PUBLIC_RECORDED_SUMMARY_BINDINGS','recorded_source_files':654,'recorded_fresh_native_providers':2,'recorded_admission_stages':7,'profile':PROFILE,'kappa':str(K),'physical':475389,'global_prefix_bits':1479,'required_reserve_bits':1512,'payload_bits':2048,'scope':'Public normalized summary integrity and internal recorded original-hash references only. No authentication of omitted full archives or unavailable original metadata bytes, no fresh native/owner/controller/outer replay, and no unconditional theorem.'}

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parent)
    a=ap.parse_args()
    print(json.dumps(check(a.root.resolve()),indent=2,sort_keys=True))
