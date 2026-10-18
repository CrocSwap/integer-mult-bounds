#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Derive the portable P53 composition wrapper from the hardened H23 wrapper."""
import argparse, ast, hashlib, json
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--basis',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
a=p.parse_args();original=a.basis.read_bytes()
sha=lambda b:hashlib.sha256(b).hexdigest()
def need(v,m):
 if not v:raise ValueError(m)
need(sha(original)=='b567f190bdfdbbb9a569a140098b41f8af5931590d16d05064dbc3ae9f9aa165','exact hardened wrapper basis')
need(not a.out.exists(),'fresh output file')
body=original.decode();changes=[]
def replace(old,new):
 global body
 need(body.count(old)==1,'unique exact wrapper preimage: '+old[:60]);body=body.replace(old,new);changes.append({'old':old,'new':new})
replace('"""Complete H23 replay: fresh native providers and parent, then full admission.','"""Complete P53 composition: fresh native providers and parent, then full admission.')
replace("PARENT = HERE.parent / 't248-dirtentry-residue'\nEXPECTED = Q('0.001718659190248459079211') - Q(1, 10**46) - Q(1, 10**70)",'''SOURCE_HEAD = 'd01045dfb67428679618027dff552f1d032fa999'
SOURCE_MANIFEST = '44ed6a457e1d1ba24726f35db86dc9e551072dd9331a8fed3ad3f0efa33ff0be'
COMPARISON_SHA = 'eb3260be191774b931cff6e562978a2af27bbc6ff666ca8c1d387a2b18dc86fa'
ADMISSION_SHA = '8fb1e4382e714f1613f7ee26af45a721da2e418b7c065a442721cb22938fa8b5'
PREPARER_SHA = 'a256d553549aa6317a52308a37b6144bb84a293139d35a98a1f6df09df43e1a0'
HELPER_SHA256 = {
    'blocknorm_certificate.py': 'e5bfbad8e8e6cb4206f7ba92d333780f423918d8f217b474302346169e991f92',
    'lift_parent.py': '9a1edd7d4ab4a2f2ac8d15b42b7e40f93653d65026bac59e4c1ce80b486bd60e',
    'replica_parent.py': '48bdbf28f59d80edb266803ec61bf5e22e8fb5e5a0e2b88004b6039147589bd4',
    'reconstruct_replica.py': '5472811c24aef3852dc7e189dff5060076a6c0b25bfde928da50dcfe9b5bdc15',
}''')
replace('def authenticate_native(native, source, manifest_sha):','def authenticate_native(native, source, manifest_sha, package):')
replace("report['status'] == 'PASS_PR2833_FRESH_NATIVE_PREPARATION'","report['status'] == 'PASS_PR2853_FRESH_NATIVE_PREPARATION'")
replace("report['source_file_count'] == 541","report['source_file_count'] == 549")
replace("sha(PARENT / 'prepare_dirtentry_native_portable.py')","sha(package / 'prepare_aphase_native.py')")
replace("receipt['source_commit'] == 'pr2833-dirtentry'","receipt['source_commit'] == 'pr2853-dirtentry4'")
old_main=body[body.index('def main():'):body.index("\n\nif __name__ == '__main__':")]
new_main='''def authenticate_source(source):
    need(sha(source / 'MANIFEST.json') == SOURCE_MANIFEST, 'exact P53 manifest')
    pins = read(source / 'MANIFEST.json')
    need(len(pins) == 549 and tree(source, ('MANIFEST.json',)) == pins,
         'complete 549-file immutable P53 source')
    need(not list(source.rglob('__pycache__')) and not list(source.rglob('*.pyc')),
         'source contains no bytecode cache')
    claim_path = source / 'outer/OUTER-CLAIM.json'
    need(sha(claim_path) == COMPARISON_SHA, 'exact complete P53 comparison claim')
    claim = read(claim_path)
    need(Q(claim['kappa_rational']) == Q(claim['kappa']), 'full comparison decimal/rational equality')
    return pins


def authenticate_candidate(package, source):
    candidate_path = package / 'data/CANDIDATE.json'
    candidate = read(candidate_path)
    names = {'ORDER.json', 'FILL.json.gz', 'DISPATCH.json', 'PROFILE.json'}
    need(set(candidate['candidate_sha256']) == names, 'exact four candidate artifacts')
    before = {candidate_path: sha(candidate_path)}
    for name in sorted(names):
        path = package / 'data' / name
        need(not path.is_symlink() and sha(path) == candidate['candidate_sha256'][name],
             'frozen candidate ' + name)
        before[path] = sha(path)
    order = read(package / 'data/ORDER.json')
    T = candidate['replicas']
    need(type(T) is int and 1 <= T <= 1169 and len(order) == 9*T,
         'literal replica count and inherited physical cap')
    need(candidate['source_head'] == SOURCE_HEAD, 'frozen P53 candidate source')
    need(candidate['comparison_head'] == SOURCE_HEAD
         and candidate['comparison_claim_sha256'] == COMPARISON_SHA,
         'frozen P53 candidate comparison metadata')
    expected = Q(candidate['target'])
    need(expected == Q(candidate['complex_lower'])-Q(1, 10**46)-Q(1, 10**70),
         'candidate exact modern-layer target')
    previous = Q(read(source / 'outer/OUTER-CLAIM.json')['kappa_rational'])
    need(expected > previous, 'candidate must improve full exact P53 headline')
    return candidate, expected, T, before


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source', type=Path, required=True)
    ap.add_argument('--work', type=Path, required=True)
    ap.add_argument('--package', type=Path, default=HERE,
                    help='staged or installed composition package; defaults to this script directory')
    ap.add_argument('--predecessor', type=Path,
                    help='pinned t248-dirtentry-residue package containing vendor/pr2839 helpers')
    ap.add_argument('--jobs', type=int, default=24, choices=range(1, 81))
    ap.add_argument('--prepared-native', type=Path)
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()
    need(not sys.flags.optimize, 'assertions must be enabled')
    need(not a.source.is_symlink() and not a.package.is_symlink(), 'source/package must not be symlinks')
    source, work, package = a.source.resolve(), a.work.resolve(), a.package.resolve()
    predecessor_arg = a.predecessor or package.parent / 't248-dirtentry-residue'
    need(not predecessor_arg.is_symlink(), 'predecessor must not be a symlink')
    predecessor = predecessor_arg.resolve()
    need(not work.exists(), 'fresh work directory required')
    for immutable in (source, package, predecessor, HERE):
        need(not work.is_relative_to(immutable) and not immutable.is_relative_to(work),
             'work and sources must be disjoint')
    source_pins = authenticate_source(source)
    candidate, expected, T, before = authenticate_candidate(package, source)
    executable_pins = {package / 'admit_aphase_residue.py': ADMISSION_SHA,
                       package / 'prepare_aphase_native.py': PREPARER_SHA}
    helper = predecessor / 'vendor/pr2839'
    executable_pins.update({helper / name: pin for name, pin in HELPER_SHA256.items()})
    for path, pin in executable_pins.items():
        need(not path.is_symlink() and sha(path) == pin, 'pinned admission/native/helper executable ' + path.name)
    before.update(executable_pins)
    before[Path(__file__).resolve()] = sha(Path(__file__).resolve())
    comparison_path = source / 'outer/OUTER-CLAIM.json'
    before[comparison_path] = COMPARISON_SHA
    native = a.prepared_native.resolve() if a.prepared_native else work / 'native'
    native_binding = None
    if a.prepared_native:
        need(not a.prepared_native.is_symlink() and native.is_dir()
             and not work.is_relative_to(native) and not native.is_relative_to(work),
             'native cache and work disjoint')
        native_binding = authenticate_native(native, source, SOURCE_MANIFEST, package)
    commands = []
    if not a.prepared_native:
        commands.append(('fresh-native', [sys.executable, '-B',
            str(package / 'prepare_aphase_native.py'), '--source', str(source),
            '--out', str(native), '--jobs', str(min(4, a.jobs))]))
    commands.append(('complete-admission', [sys.executable, '-B',
        str(package / 'admit_aphase_residue.py'), '--source', str(source),
        '--fill', str(package / 'data/FILL.json.gz'), '--order', str(package / 'data/ORDER.json'),
        '--dispatch', str(package / 'data/DISPATCH.json'),
        '--native-cache', str(native / 'native-cache'),
        '--native-receipt', str(native / 'NATIVE-RECEIPT.json'),
        '--work', str(work / 'candidate'), '--replica-helper-dir', str(helper),
        '--reconstructor', str(helper / 'reconstruct_replica.py'),
        '--blocknorm-checker', str(helper / 'blocknorm_certificate.py'),
        '--comparison-claim', str(comparison_path),
        '--source-profile', 'pr2853', '--comparison-profile', 'pr2853',
        '--jobs', str(a.jobs)]))
    if a.dry_run:
        print(json.dumps({'status': 'PREFLIGHT_ONLY', 'replicas': T, 'expected_kappa': str(expected),
                          'native_authenticated': native_binding is not None, 'commands': commands}, indent=2))
        return
    work.mkdir(parents=True)
    env = child_environment(work)
    stages = []
    for name, argv in commands:
        start = time.monotonic()
        log = work / (name + '.log')
        with log.open('w', encoding='utf-8') as stream:
            proc = subprocess.run(argv, cwd=work, env=env, stdin=subprocess.DEVNULL,
                                  stdout=stream, stderr=subprocess.STDOUT)
        stages.append({'stage': name, 'argv': argv, 'exit_code': proc.returncode,
                       'seconds': time.monotonic()-start, 'log_sha256': sha(log)})
        (work / 'STAGES.json').write_text(json.dumps(stages, indent=2)+'\\n')
        need(proc.returncode == 0, 'failed '+name+'; see '+str(log))
        if name == 'fresh-native':
            native_binding = authenticate_native(native, source, SOURCE_MANIFEST, package)
        print('PASS', name, flush=True)
    result = read(work / 'candidate/RESULT.json')
    release = read(work / 'candidate/release/RELEASE-RECEIPT.json')
    need(result['status'] == 'PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE'
         and release['status'] == 'PASS_RELEASE', 'complete release statuses')
    need(Q(result['kappa']) == Q(release['kappa_decimal']) == expected
         and Q(result['complex_lower']) == Q(candidate['complex_lower']),
         'exact complete composition headline and complex endpoint')
    need(result['replicas'] == T and result['source_file_count'] == 549
         and result['source_upstream_head'] == SOURCE_HEAD
         and result['comparison_pr'] == 2853 and result['comparison_head'] == SOURCE_HEAD
         and result['comparison_claim_sha256'] == COMPARISON_SHA,
         'complete admission source, replica and comparison binding')
    need(result['profile'] == read(package / 'data/PROFILE.json'), 'literal complete paid profile')
    for field, name in [('fill_sha256', 'FILL.json.gz'), ('order_sha256', 'ORDER.json'),
                        ('dispatch_sha256', 'DISPATCH.json')]:
        need(result[field] == before[package / 'data' / name], 'complete admitted '+name+' identity')
    need(result['release_receipt_sha256'] == sha(work / 'candidate/release/RELEASE-RECEIPT.json')
         and result['package_manifest_sha256'] == release['manifest_sha256'],
         'release receipt and generated package binding')
    need(authenticate_source(source) == source_pins and before == {p: sha(p) for p in before},
         'immutable input drift')
    need(native_binding == authenticate_native(native, source, SOURCE_MANIFEST, package),
         'native protocol input drift')
    report = {'status': 'PASS_APHASE_RESIDUE_COMPLETE_REPLAY', 'kappa': str(expected), 'replicas': T,
              'source_head': SOURCE_HEAD, 'source_manifest_sha256': SOURCE_MANIFEST,
              'comparison_claim_sha256': COMPARISON_SHA,
              'fresh_native_this_invocation': a.prepared_native is None,
              'explicit_native_reuse': a.prepared_native is not None,
              'native_binding': native_binding,
              'candidate_result_sha256': sha(work / 'candidate/RESULT.json'),
              'executable_and_data_sha256': {str(p.relative_to(package)) if p.is_relative_to(package)
                                           else str(p): h for p, h in before.items()},
              'stages': stages,
              'scope': 'Conditional finite supplier and modern outer release; inherited all-size obligations remain.'}
    (work / 'RESULT.json').write_text(json.dumps(report, indent=2)+'\\n')
    print('PASS_APHASE_RESIDUE_COMPLETE_REPLAY', result['kappa_decimal'], flush=True)
'''
replace(old_main,new_main)
compile(body,'reproduce.py','exec')
# Preserve all native authentication logic except the five declared source/preparer arguments.
rev=body
for c in reversed(changes):
 need(rev.count(c['new'])==1,'unique reverse wrapper replacement');rev=rev.replace(c['new'],c['old'])
need(rev.encode()==original,'complete byte rollback to hardened H23 wrapper')
old_ast,new_ast=ast.parse(original),ast.parse(body)
for name in ('need','read','sha','tree','child_environment'):
 o=next(x for x in old_ast.body if isinstance(x,ast.FunctionDef) and x.name==name)
 n=next(x for x in new_ast.body if isinstance(x,ast.FunctionDef) and x.name==name)
 need(ast.dump(o)==ast.dump(n),'unchanged utility/LF descendant shim '+name)
def constant(tree,name):return ast.literal_eval(next(x.value for x in tree.body if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in x.targets)))
need(constant(old_ast,'LF_SHIM')==constant(new_ast,'LF_SHIM'),'byte-identical inherited LF shim')
a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(body,encoding='utf-8',newline='\n')
record={'status':'PASS_PORTABLE_P53_WRAPPER_DERIVATION','source_path':'research/t248-residue-exchange/reproduce.py','source_sha256':sha(original),'target_path':a.out.name,'target_sha256':sha(body.encode()),'exact_preimages':changes,'preserved':'Complete native authentication, four five-stage chains, full source/cache identity and16 distinct retained parent stages. LF_SHIM and descendant environment byte/AST identical.','changes':'P53 source/comparator/native pins; pinned predecessor helpers; generic exact candidate T/profile/endpoint; optional staged --package and explicit --predecessor; default fresh native and explicit fully authenticated prepared native.'}
a.out.with_name('WRAPPER-DERIVATION.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({k:record[k] for k in ('status','source_sha256','target_sha256')},indent=2))
