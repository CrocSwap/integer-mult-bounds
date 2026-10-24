#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Source-bound execution evidence; substantial OpenAI Codex assistance.
"""Collect a completed local replay, or check its compact recorded evidence.

Collection checks actual local bytes before copying selected receipts. The public
check checks copied receipt integrity and recorded references, not omitted source,
runtime or native archives; it is not another scientific replay.
"""
import argparse
import copy
from datetime import datetime
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path, PurePosixPath

COMMIT = 'abc12f62e4fe9bfcb2e33c84703253c918668351'
WRAPPER = '9ec43247d2b3af6e4fce61173a4e59aa13b845792776289995cb108285f8aede'
SOURCE = 'fb47533a401d1d13719be8b9aab91fe5313931ca62d40dba336eab6a96275aa0'
MAIN = '20ecf2891d80b5acf18d980b2164fb44ea7faa90'
C = Q('.001730394391813963415120')
K = C-Q(1,10**46)-Q(1,10**70)
PROFILE = {'1':11747920,'2':3453480,'3':1112042,'4':486540,'5':103690,'8':38160,'48':202828}
WORDS = {'base':'6df3356808e29909776be8bc0faf03df983401a267c2d740d1ac2dbcaa278269','extra':'65624efec36b35934b750c1741ba2ad4e6df3cff86e44536b0c016ebddb0fb55'}
TOP = ['original-materialization','retiming-source','preserved-staged-review','new-retiming-review','fresh-native','literal-owners','full-admission']
INNER = {'owners':'reconstruct.py','parent-lift':'lift_parent.py','rebind':'new/rebind.py','discovery':'replay.py','outer-check_ledger.py':'outer/check_ledger.py','outer-independent_check.py':'outer/independent_check.py','release':'verify_release.py'}
NATIVE = ['native','ledgers','local-replay','wrappers','phases']
PATHS = {
    'WRAPPER-RESULT.json':'RESULT.json',
    'SOURCE-REBUILD-RESULT.json':'SOURCE-REBUILD-RESULT.json',
    'ADMISSION-RESULT.json':'retimed/admission/RESULT.json',
    'NATIVE-RESULT.json':'retimed/native/RESULT.json',
    'NATIVE-RECEIPT.json':'retimed/native/NATIVE-RECEIPT.json',
    'NATIVE-base-RESULT.json':'retimed/native/fresh-base/RESULT.json',
    'NATIVE-extra-RESULT.json':'retimed/native/fresh-extra/RESULT.json',
    'RELEASE-RECEIPT.json':'retimed/admission/release/RELEASE-RECEIPT.json',
}
SCOPE = ('Recorded execution evidence and original/public hash references only. '
         'The collector checked the completed local raw chain before publication; '
         'this public check neither authenticates omitted archives or unavailable '
         'original metadata bytes nor reruns native/owner/controller/outer checks. '
         'Two changed native providers were fresh; retained parent/native evidence '
         'was reused. The modern kappa remains conditional on inherited assumptions.')

def need(ok, message):
    if not ok:
        raise ValueError(message)

def digest(data):
    return hashlib.sha256(data).hexdigest()

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()

def read(path):
    return json.loads(path.read_bytes())

def normalized(raw):
    return raw.replace(str(Path.home()).encode(), b'$RESEARCH_WORKSPACE')

def safe(root, name):
    p = PurePosixPath(name)
    need(not p.is_absolute() and '..' not in p.parts and '\\' not in name, 'safe relative path')
    return root / name

def stages(rows, names, label):
    need([s['name'] for s in rows] == list(names), label+' exact stages')
    need(all(s['exit_code'] == 0 and s['seconds'] >= 0 for s in rows), label+' completed exits')
    need(all(s['command'][1] == '-B' for s in rows), label+' normal interpreter invocation')

def validate(records, evidence):
    """Semantic checks shared by raw collection, public check and rejection controls."""
    a = records['ATTEMPT.json']
    need(a['schema'] == 'public-end-to-end-attempt/1', 'attempt schema')
    need(a.get('exit_code') == 0 and a.get('finished_at'), 'completed exit-zero attempt required')
    start, finish = [datetime.fromisoformat(a[k]) for k in ('started_at','finished_at')]
    need(finish >= start and a['seconds'] >= 0, 'completed time interval')
    need(a['package_files_unchanged'] is True, 'publication inputs unchanged during replay')
    need(a['publication_commit'] == COMMIT and a['wrapper_sha256'] == WRAPPER, 'executed commit and wrapper')
    command = a['command']
    need(len(command) == 7 and command[1] == '-B' and command[3] == '--repo' and command[5] == '--work', 'full wrapper argv without external allocation or materialize-only')
    need(command[2].endswith('/full-admission/reproduce.py'), 'public wrapper entry point')
    repo, work = command[4].rstrip('/'), command[6].rstrip('/')
    pub = repo+'/research/staged-release-retiming-t530/full-admission'
    need(command[2] == pub+'/reproduce.py', 'wrapper within recorded repo')
    need(a['package_before']['research/staged-release-retiming-t530/full-admission/reproduce.py'] == WRAPPER, 'before-run wrapper binding')
    top = records['WRAPPER-RESULT.json']
    need(top['status'] == 'PASS_RETIMER_T530_COMPLETE_CONDITIONAL_RELEASE', 'complete wrapper result')
    need(top['source_manifest_sha256'] == SOURCE and Q(top['kappa']) == K, 'wrapper source and modern kappa')
    stages(top['stages'], TOP, 'wrapper')
    scripts = [pub+'/vendor/staged-width-t530/replay.py', pub+'/scripts/integrate.py',
               work+'/retimed/source/new/borrow/review_staged3605.py',
               work+'/retimed/source/new/borrow/review_release_retime.py',
               work+'/retimed/prepare_extension_native.py',
               pub+'/vendor/staged-width-t530/owners/portable_expand.py',
               work+'/retimed/admit_extension.py']
    need([s['command'][2] for s in top['stages']] == scripts, 'wrapper stage script identities')
    need(top['stages'][5]['command'][3:] == ['--out',work+'/allocation'], 'fresh internal literal allocation')
    argv = top['stages'][6]['command']
    for flag, path in {'--source':'retimed/source','--fill':'FILL-legacy.json.gz','--order':'allocation/ORDER.json','--dispatch':'allocation/DISPATCH.json','--native-cache':'retimed/native/native-cache','--native-receipt':'retimed/native/NATIVE-RECEIPT.json','--work':'retimed/admission'}.items():
        need(argv.count(flag) == 1 and argv[argv.index(flag)+1] == work+'/'+path, 'internal admission input '+flag)
    rebuilt = records['SOURCE-REBUILD-RESULT.json']
    need(rebuilt['status'] == 'PASS_PUBLIC_SOURCE_REBUILD_654_FILES' and rebuilt['source_manifest_sha256'] == SOURCE and rebuilt['source_files'] == 654, 'fresh source reconstruction')
    need(rebuilt['main_commit'] == MAIN and rebuilt['exported_inputs'] == 540, 'pinned main reconstruction')
    need(rebuilt['stages'] == [{k:s[k] for k in ['name','exit_code','log_sha256']} for s in top['stages'][:4]], 'source reconstruction stage chain')
    native, nr = records['NATIVE-RESULT.json'], records['NATIVE-RECEIPT.json']
    original = lambda name:evidence['files'][name]['original_sha256']
    need(native['status'] == 'PASS_TWO_FRESH_SHARED_KERNEL_NATIVE_CHAINS_AUTHENTICATED_PARENT_REUSE' and native['source_manifest_sha256'] == SOURCE, 'fresh native completion')
    need(native['native_receipt_sha256'] == original('NATIVE-RECEIPT.json'), 'native receipt hash chain')
    need(nr['status'] == 'PASS_COMPOSED_FRESH_NATIVE_PROVIDERS_AND_AUTHENTICATED_CACHE' and nr['manifest_sha256'] == SOURCE, 'native receipt source')
    need(nr['fresh_current_provider_count'] == 2 and nr['fresh_retained_native_count'] == 0 and nr['fresh_retained_parent'] is False and nr['reused_retained_native_count'] == 2 and nr['reused_retained_parent'] is True, 'fresh changed providers and explicit retained reuse')
    need(set(nr['providers']) == set(WORDS), 'exact native providers')
    stages(native['stages'], ['fresh-current-base','fresh-current-extra'], 'native')
    for row, (kind, word) in zip(native['stages'], WORDS.items()):
        fresh = records['NATIVE-'+kind+'-RESULT.json']
        need(row['result_sha256'] == original('NATIVE-'+kind+'-RESULT.json'), 'fresh provider result binding')
        need(nr['providers'][kind]['word_sha256'] == fresh['word_sha256'] == word and fresh['status'] == 'PASS_COMPLETE_T74_NATIVE_REPLAY', 'fresh provider word and status')
        need([s['step'] for s in fresh['steps']] == NATIVE and all(s['exit_code'] == 0 for s in fresh['steps']), 'five fresh native gates')
    admission, release = records['ADMISSION-RESULT.json'], records['RELEASE-RECEIPT.json']
    need(admission['status'] == 'PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE', 'complete nested admission')
    need(admission['native_receipt_sha256'] == original('NATIVE-RECEIPT.json') and admission['source_manifest_sha256'] == SOURCE and admission['source_file_count'] == 654, 'nested admission source/native binding')
    need(admission['profile'] == PROFILE and admission['replicas'] == 530 and admission['actual_expected_helpers'] == 408, 'nested profile and dimensions')
    need(Q(admission['complex_lower']) == C and Q(admission['kappa']) == Q(admission['kappa_decimal']) == K, 'exact modern endpoint')
    stages(admission['stages'], INNER, 'admission')
    inner_scripts = [work+'/retimed/admission/'+('layout/packing74/replay.py' if name == 'discovery' else 'package/'+path) for name,path in INNER.items()]
    need([s['command'][2] for s in admission['stages']] == inner_scripts, 'nested script identities')
    need(admission['release_receipt_sha256'] == original('RELEASE-RECEIPT.json'), 'terminal receipt hash chain')
    need(release['status'] == 'PASS_RELEASE' and Q(release['kappa_decimal']) == K and release['manifest_sha256'] == admission['package_manifest_sha256'], 'terminal release and runtime manifest')
    observed = evidence['local_byte_checks']
    need(observed['source_manifest_sha256'] == SOURCE and observed['source_file_count'] == 654 and observed['main_export_count'] == 540, 'recorded local source checks')
    need(observed['package_manifest_sha256'] == admission['package_manifest_sha256'], 'recorded runtime manifest check')
    need(observed['literal_rows'] == 1946160 and observed['literal_payload_sha256'] == '9f82e7d4abfcb52cd6d969e37e07415516856d7af85192010f3fc142dbaad246', 'recorded full literal allocation check')
    for key, rows in [('top_stages',top['stages']),('admission_stages',admission['stages']),('native_stages',native['stages'])]:
        bindings = observed[key]
        need([b['name'] for b in bindings] == [s['name'] for s in rows], 'recorded local stage set '+key)
        for b, s in zip(bindings, rows):
            need(b['log_sha256'] == s['log_sha256'], 'recorded local stage log '+s['name'])
            if 'script_sha256' in s:
                need(b['script_sha256'] == s['script_sha256'], 'recorded local executed script '+s['name'])
    return {'status':'PASS_RECORDED_FRESH_WRAPPER_CHAIN','top_stages':7,'admission_stages':7,'fresh_current_providers':2,'kappa':str(K),'executed_commit':COMMIT,'wrapper_sha256':WRAPPER,'scope':SCOPE}

def collect(work, attempt, package, log, out):
    need(not out.exists(), 'fresh evidence output directory required')
    a = read(attempt)
    need(a.get('exit_code') == 0 and a.get('finished_at'), 'completed exit-zero attempt required')
    need(Path(a['command'][6]).resolve() == work and Path(a['command'][2]).resolve() == package/'reproduce.py', 'requested local run identity')
    repo = Path(a['command'][4]).resolve()
    need(sha(package/'reproduce.py') == WRAPPER == a['wrapper_sha256'], 'unchanged actual executed wrapper')
    need(sha(log) == a['stdout_sha256'], 'actual complete wrapper stdout')
    # Check all pre-run public files, without including new documentation/evidence.
    for name, expected in a['package_before'].items():
        need(sha(safe(repo,name)) == expected, 'unchanged original publication file '+name)
    source = work/'retimed/source'
    manifest = read(source/'MANIFEST.json')
    need(sha(source/'MANIFEST.json') == SOURCE and len(manifest) == 654, 'actual frozen source manifest')
    for name, expected in manifest.items():
        need(sha(safe(source,name)) == expected, 'actual source file '+name)
    main = read(package/'MAIN-INPUTS.json')
    need(main['base_commit'] == MAIN and len(main['sha256']) == 540, 'actual main export pins')
    for name, expected in main['sha256'].items():
        need(sha(safe(work/'main-files',name)) == expected, 'actual main export '+name)
    paths = {'ATTEMPT.json':attempt, **{name:work/rel for name,rel in PATHS.items()}}
    raw = {name:p.read_bytes() for name,p in paths.items()}
    records = {name:json.loads(data) for name,data in raw.items()}
    admission = work/'retimed/admission'
    native = work/'retimed/native'
    runtime = admission/'package'
    runtime_manifest = read(runtime/'MANIFEST.json')
    runtime_hash = sha(runtime/'MANIFEST.json')
    for name, expected in runtime_manifest.items():
        need(sha(safe(runtime,name)) == expected, 'actual admitted runtime '+name)
    def bind(rows, base):
        need(rows == read(base/'STAGES.json'), 'actual separate stage file identity')
        bindings = []
        for s in rows:
            script = Path(s['command'][2]); script_hash = sha(script)
            log_name = 'native-'+s['name'].removeprefix('fresh-current-') if base == native else s['name']
            log_path = base/(log_name+'.log')
            need(sha(log_path) == s['log_sha256'], 'actual stage log '+s['name'])
            if 'script_sha256' in s:
                need(script_hash == s['script_sha256'], 'actual executed script '+s['name'])
            if base == admission:
                need(runtime_manifest[INNER[s['name']]] == script_hash, 'executed script in admitted runtime')
            bindings.append({'name':s['name'],'script_sha256':script_hash,'log_sha256':s['log_sha256']})
        return bindings
    top_bindings = bind(records['WRAPPER-RESULT.json']['stages'],work)
    inner_bindings = bind(records['ADMISSION-RESULT.json']['stages'],admission)
    native_bindings = bind(records['NATIVE-RESULT.json']['stages'],native)
    nr = records['NATIVE-RECEIPT.json']
    need(sha(work/'prepared/predecessor/NATIVE-RECEIPT.json') == nr['retained_reuse_receipt_sha256'], 'actual retained native reuse receipt')
    for name, expected in nr['cache_files'].items():
        need(sha(safe(native/'native-cache',name)) == expected, 'actual native cache '+name)
    need(sha(native/'ENVIRONMENT.json') == records['NATIVE-RESULT.json']['environment_sha256'], 'actual native environment')
    need(sha(work/'retimed/prepare_extension_native.py') == records['NATIVE-RESULT.json']['preparer_sha256'], 'actual native preparer')
    with gzip.open(work/'allocation/FILL.json.gz','rb') as f:
        fill_bytes = f.read()
    fill = json.loads(fill_bytes)
    need(fill['columns'] == ['time','helper','owner_replica','child','port','offset'] and not fill.get('dispatch_overrides',[]), 'literal allocation shape')
    fill['dispatch_overrides'] = []
    expected_legacy = digest(json.dumps(fill,separators=(',',':')).encode())
    legacy_hash = hashlib.sha256()
    with gzip.open(work/'FILL-legacy.json.gz','rb') as f:
        for block in iter(lambda:f.read(1024*1024), b''):
            legacy_hash.update(block)
    need(expected_legacy == legacy_hash.hexdigest(), 'internal legacy fill preserves complete allocation')
    ar = records['ADMISSION-RESULT.json']
    for field, rel in [('fill','FILL-legacy.json.gz'),('order','allocation/ORDER.json'),('dispatch','allocation/DISPATCH.json')]:
        need(sha(work/rel) == ar[field+'_sha256'], 'admitted literal input '+field)
    public = {name:normalized(body) for name,body in raw.items()}
    evidence = {'schema':'fresh-public-wrapper-evidence/1','scope':SCOPE,
        'normalization':'Only the local home-directory prefix is replaced by $RESEARCH_WORKSPACE in selected metadata; hashes refer to original raw files unless explicitly public_sha256.',
        'files':{name:{'original_sha256':digest(raw[name]),'public_sha256':digest(body),'normalization':'none' if body == raw[name] else 'workspace-prefix-to-token'} for name,body in public.items()},
        'local_byte_checks':{'source_manifest_sha256':SOURCE,'source_file_count':654,'main_export_count':540,'package_manifest_sha256':runtime_hash,'runtime_file_count':len(runtime_manifest),'native_cache_files':len(nr['cache_files']),'literal_rows':len(fill['rows']),'literal_payload_sha256':digest(fill_bytes),'top_stages':top_bindings,'admission_stages':inner_bindings,'native_stages':native_bindings}}
    validate(records,evidence)
    # Nothing is published until every raw-byte and semantic predicate succeeds.
    out.mkdir(parents=True)
    for name, body in public.items():
        (out/name).write_bytes(body)
    (out/'EVIDENCE.json').write_text(json.dumps(evidence,sort_keys=True,indent=2)+'\n')
    return check(out)

def load(root):
    evidence = read(root/'EVIDENCE.json')
    need(evidence['schema'] == 'fresh-public-wrapper-evidence/1', 'evidence schema')
    need(set(evidence['files']) == {'ATTEMPT.json',*PATHS}, 'exact selected receipt set')
    records = {}
    for name, pin in evidence['files'].items():
        raw = safe(root,name).read_bytes()
        need(digest(raw) == pin['public_sha256'], 'public receipt bytes '+name)
        need(pin['normalization'] in ('none','workspace-prefix-to-token'), 'normalization rule')
        need(b'/Users/' not in raw, 'no original macOS home-directory prefix')
        if pin['normalization'] == 'none':
            need(pin['original_sha256'] == pin['public_sha256'], 'unchanged receipt hash')
        records[name] = json.loads(raw)
    return records,evidence

def check(root):
    return validate(*load(root))

def controls(root):
    records,evidence = load(root)
    validate(records,evidence)
    mutations = {
        'incomplete_attempt':lambda r,e:r['ATTEMPT.json'].pop('finished_at'),
        'external_allocation':lambda r,e:r['ATTEMPT.json']['command'].extend(['--allocation','/external/allocation']),
        'missing_nested_gate':lambda r,e:r['ADMISSION-RESULT.json']['stages'].pop(4),
        'stale_terminal_receipt':lambda r,e:r['ADMISSION-RESULT.json'].__setitem__('release_receipt_sha256','0'*64),
    }
    rejected = {}
    for name, mutate in mutations.items():
        r,e = copy.deepcopy(records),copy.deepcopy(evidence)
        mutate(r,e)
        try:
            validate(r,e)
        except ValueError as exc:
            rejected[name] = str(exc)
        else:
            raise ValueError('control accepted: '+name)
    return {'status':'PASS_FOUR_FRESH_EVIDENCE_REJECTION_CONTROLS','controls':rejected,'scope':'Semantic controls bypass public-file hash checks; no scientific replay.'}

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest='action',required=True)
    c = sub.add_parser('collect')
    for name in ('work','attempt','package','log','out'):
        c.add_argument('--'+name,type=Path,required=True)
    for name in ('check','controls'):
        sub.add_parser(name).add_argument('--root',type=Path,required=True)
    args = ap.parse_args()
    if args.action == 'collect':
        result = collect(*(getattr(args,n).resolve() for n in ('work','attempt','package','log','out')))
    else:
        result = (check if args.action == 'check' else controls)(args.root.resolve())
    print(json.dumps(result,sort_keys=True,indent=2))

if __name__ == '__main__':
    main()
