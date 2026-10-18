#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Complete H23 replay: fresh native providers and parent, then full admission.

Marius-Paul Dumitrean, with substantial OpenAI Codex assistance.
PR2848 orchestration by Yiyang Lu and retained contributors is acknowledged.
"""
import argparse
from fractions import Fraction as Q
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
PARENT = HERE.parent / 't248-dirtentry-residue'
EXPECTED = Q('0.001718659190248459079211') - Q(1, 10**46) - Q(1, 10**70)
PARENT_MANIFEST = 'e0eefc96567fbb45e19e6de0ca295381dbe0e686c08ddc783639b065c7c791d4'
NATIVE_STAGES = ['native', 'ledgers', 'local-replay', 'wrappers', 'phases']
# Byte-identical LF shim from the retained PR2843 native protocol
# (portable_prepare_native.py SHA256 cb32e36f3e435652b7fab857c94e0dbb925b56ce7bb5daeecc223b0fc6993012).
# The same adapter reaches both admission and every ordinary Python child.
LF_SHIM = """from pathlib import Path
_original_write_text = Path.write_text
def _task_write_text(self, data, encoding=None, errors=None, newline=None):
    return _original_write_text(self, data, encoding=encoding, errors=errors,
                                newline='\\n' if newline is None else newline)
Path.write_text = _task_write_text
"""
sys.dont_write_bytecode = True


def need(value, message):
    if not value:
        raise ValueError(message)


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tree(root, exclude=()):
    result = {}
    for path in sorted(root.rglob('*')):
        need(not path.is_symlink(), 'symlink in authenticated native tree')
        if path.is_file():
            relative = path.relative_to(root).as_posix()
            if relative not in exclude:
                result[relative] = sha(path)
    return result


def child_environment(work):
    adapter = work / 'process-lf-adapter'
    adapter.mkdir()
    (adapter / 'sitecustomize.py').write_text(LF_SHIM, encoding='utf-8', newline='\n')
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1',
               PYTHONINTMAXSTRDIGITS='0', OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1',
               MKL_NUM_THREADS='1', NUMEXPR_NUM_THREADS='1')
    env['PYTHONPATH'] = str(adapter) + (os.pathsep + env['PYTHONPATH'] if env.get('PYTHONPATH') else '')
    for key in ('PYTHONOPTIMIZE', 'WITNESS_SPEC', 'WITNESS_DISCOVER', 'WITNESS_RECORD'):
        env.pop(key, None)
    return env


def authenticate_native(native, source, manifest_sha):
    report = read(native / 'RESULT.json')
    receipt = read(native / 'NATIVE-RECEIPT.json')
    cache = native / 'native-cache'
    need(report['status'] == 'PASS_PR2833_FRESH_NATIVE_PREPARATION'
         and report['source_manifest_sha256'] == manifest_sha
         and report['source_file_count'] == 541
         and report['native_receipt_sha256'] == sha(native / 'NATIVE-RECEIPT.json')
         and report['preparer_sha256'] == sha(PARENT / 'prepare_dirtentry_native_portable.py'),
         'prepared-native completion and source binding')
    need(receipt['status'] == 'PASS_COMPOSED_FRESH_NATIVE_PROVIDERS_AND_AUTHENTICATED_CACHE'
         and receipt['source_commit'] == 'pr2833-dirtentry'
         and receipt['manifest_sha256'] == manifest_sha,
         'native source protocol binding')
    need(tree(cache) == receipt['cache_files'], 'complete native/parent cache hashes')
    need(receipt['fresh_current_provider_count'] == 2
         and receipt['fresh_retained_native_count'] == 2
         and receipt['reused_retained_native_count'] == 0
         and receipt['fresh_retained_parent'] is True
         and receipt['reused_retained_parent'] is False,
         'four fresh native chains and retained parent in prepared protocol')
    stages = read(native / 'STAGES.json')
    need(report['stages'] == stages and len(stages) == 5
         and {s['name'] for s in stages} == {'native-base', 'native-extra',
             'native-retained-base', 'native-retained-extra', 'retained-parent'}
         and all(s['exit_code'] == 0 for s in stages), 'five successful native preparation stages')

    def bind_word(word):
        entry = cache / sha(word)
        need(read(entry / 'local/FULL-WORD.json.gz') == read(word), 'complete native word binding')
        steps = read(entry / 'STEPS.json')
        need([s['step'] for s in steps] == NATIVE_STAGES
             and all(s['exit_code'] == 0 for s in steps), 'five successful native stages')
        return entry

    for tag in ('base', 'extra'):
        word = source / ('new/borrow/words/BORROW-WORD-43' + tag + '.json.gz')
        entry = bind_word(word)
        binding = receipt['providers'][tag]
        need(binding['word_sha256'] == sha(word)
             and tree(entry, ('CACHE.json',)) == binding['complete_native_files'],
             'current native full-tree binding')
    old = source / 'vendor/pr1297'
    need(sha(old / 'MANIFEST.json') == PARENT_MANIFEST
         and tree(old, ('MANIFEST.json',)) == read(old / 'MANIFEST.json'),
         'complete retained parent source')
    retained = {tag: old / name for tag, name in
                (('base', 'gauge44-word.json.gz'), ('extra', 'extra-word.json.gz'))}
    for word in retained.values():
        bind_word(word)
    parent_dir = cache / '_receipts' / PARENT_MANIFEST
    need(sha(parent_dir / 'RECEIPT.json') == receipt['retained_parent_receipt_sha256'],
         'retained parent receipt binding')
    parent_receipt = read(parent_dir / 'RECEIPT.json')
    need(parent_receipt['schema'] == 'parent-receipt/1'
         and parent_receipt['vendor_manifest_sha256'] == PARENT_MANIFEST
         and parent_receipt['claim_sha256'] == sha(old / 'CLAIM.json')
         and parent_receipt['words'] == {tag: sha(word) for tag, word in retained.items()},
         'retained parent source/claim/word binding')
    need(set(parent_receipt['files']) == {'RESULT.json', 'STAGES.json'}
         and set(tree(parent_dir)) == {'RECEIPT.json', 'RESULT.json', 'STAGES.json'},
         'complete retained parent receipt files')
    need(all(sha(parent_dir / name) == digest for name, digest in parent_receipt['files'].items()),
         'retained parent receipt file hashes')
    parent_stages = read(parent_dir / 'STAGES.json')
    expected = {name + '-' + tag for tag in ('base', 'extra') for name in
                ('literal-word', 'independent-local', 'fusion-controls', 'x54-controls',
                 'kernel543-controls', 'kernel-controls', 'leaver-premise')}
    expected.update(('literal-construct', 'strict-global'))
    need(len(parent_stages) == 16 and {s['name'] for s in parent_stages} == expected
         and all(s['exit_code'] == 0 for s in parent_stages),
         'sixteen successful retained parent stages')
    parent = read(parent_dir / 'RESULT.json')
    need(parent['status'] == 'PASS_GLOBAL_MIXED_X54_FUSIONS_NATIVE_AND_STRICT_ADMISSION'
         and parent['kappa'] == read(old / 'CLAIM.json')['kappa']
         and parent['stages'] == parent_stages
         and parent['base_native_reuse'] is True and parent['extra_native_reuse'] is True,
         'retained parent PASS/claim/stage binding')
    return {'native_receipt_sha256': sha(native / 'NATIVE-RECEIPT.json'),
            'result_sha256': sha(native / 'RESULT.json'), 'cache_files': receipt['cache_files']}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source', type=Path, required=True)
    ap.add_argument('--work', type=Path, required=True)
    ap.add_argument('--jobs', type=int, default=24, choices=range(1, 81))
    ap.add_argument('--prepared-native', type=Path)
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()
    need(not sys.flags.optimize, 'assertions must be enabled')
    need(not a.source.is_symlink(), 'source must not be a symlink')
    source, work = a.source.resolve(), a.work.resolve()
    need(not work.exists(), 'fresh work directory required')
    for immutable in (source, HERE, PARENT):
        need(not work.is_relative_to(immutable) and not immutable.is_relative_to(work),
             'work and sources must be disjoint')
    # Execute only the pinned parent's source authenticator, with bytecode disabled.
    auth_path = PARENT / 'materialize_source.py'
    auth = {'__name__': 'pinned_source_authenticator', '__file__': str(auth_path)}
    exec(compile(auth_path.read_bytes(), str(auth_path), 'exec'), auth)
    source_pins = auth['authenticate_source'](source)
    candidate = read(HERE / 'data/CANDIDATE.json')
    need(Q(candidate['target']) == EXPECTED, 'exact frozen H23 target')
    before = {p: sha(p) for p in [HERE / 'data/CANDIDATE.json',
              HERE / 'admit_residue_successor.py', PARENT / 'CLAIM.json']}
    for name, pin in candidate['candidate_sha256'].items():
        path = HERE / 'data' / name
        need(sha(path) == pin, 'frozen candidate ' + name)
        before[path] = pin
    native = a.prepared_native.resolve() if a.prepared_native else work / 'native'
    native_binding = None
    if a.prepared_native:
        need(native.is_dir() and not work.is_relative_to(native)
             and not native.is_relative_to(work), 'native cache and work disjoint')
        native_binding = authenticate_native(native, source, auth['MANIFEST_SHA'])
    helper = PARENT / 'vendor/pr2839'
    commands = []
    if not a.prepared_native:
        commands.append(('fresh-native', [sys.executable, '-B',
            str(PARENT / 'prepare_dirtentry_native_portable.py'), '--source', str(source),
            '--out', str(native), '--jobs', str(min(4, a.jobs))]))
    commands.append(('complete-admission', [sys.executable, '-B',
        str(HERE / 'admit_residue_successor.py'), '--source', str(source),
        '--fill', str(HERE / 'data/FILL.json.gz'), '--order', str(HERE / 'data/ORDER.json'),
        '--dispatch', str(HERE / 'data/DISPATCH.json'),
        '--native-cache', str(native / 'native-cache'),
        '--native-receipt', str(native / 'NATIVE-RECEIPT.json'),
        '--work', str(work / 'candidate'), '--replica-helper-dir', str(helper),
        '--reconstructor', str(helper / 'reconstruct_replica.py'),
        '--blocknorm-checker', str(helper / 'blocknorm_certificate.py'),
        '--comparison-claim', str(PARENT / 'CLAIM.json'),
        '--source-profile', 'pr2833', '--comparison-profile', 'pr2848',
        '--jobs', str(a.jobs)]))
    if a.dry_run:
        print(json.dumps({'status': 'PREFLIGHT_ONLY', 'commands': commands}, indent=2))
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
                       'seconds': time.monotonic() - start, 'log_sha256': sha(log)})
        (work / 'STAGES.json').write_text(json.dumps(stages, indent=2) + '\n')
        need(proc.returncode == 0, 'failed ' + name + '; see ' + str(log))
        if name == 'fresh-native':
            native_binding = authenticate_native(native, source, auth['MANIFEST_SHA'])
        print('PASS', name, flush=True)
    result = read(work / 'candidate/RESULT.json')
    release = read(work / 'candidate/release/RELEASE-RECEIPT.json')
    need(result['status'] == 'PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE'
         and release['status'] == 'PASS_RELEASE', 'complete release statuses')
    need(Q(result['kappa']) == Q(release['kappa_decimal']) == EXPECTED,
         'exact complete H23 headline')
    need(result['release_receipt_sha256'] == sha(work / 'candidate/release/RELEASE-RECEIPT.json')
         and result['package_manifest_sha256'] == release['manifest_sha256'],
         'release receipt and generated package binding')
    need(auth['authenticate_source'](source) == source_pins
         and before == {p: sha(p) for p in before}, 'immutable input drift')
    need(native_binding == authenticate_native(native, source, auth['MANIFEST_SHA']),
         'native protocol input drift')
    report = {'status': 'PASS_H23_COMPLETE_REPLAY', 'kappa': str(EXPECTED),
              'fresh_native_this_invocation': a.prepared_native is None,
              'explicit_native_reuse': a.prepared_native is not None,
              'native_binding': native_binding,
              'candidate_result_sha256': sha(work / 'candidate/RESULT.json'),
              'executable_and_data_sha256': {str(p.relative_to(HERE)) if p.is_relative_to(HERE)
                                           else str(p): h for p, h in before.items()},
              'stages': stages,
              'scope': 'Conditional finite supplier and modern outer release; inherited all-size obligations remain.'}
    (work / 'RESULT.json').write_text(json.dumps(report, indent=2) + '\n')
    print('PASS_H23_COMPLETE_REPLAY', result['kappa_decimal'], flush=True)


if __name__ == '__main__':
    main()
