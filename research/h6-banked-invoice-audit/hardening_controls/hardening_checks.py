#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Execution-hygiene controls only; no H6 mathematical cases or producer JSON.

Uses a synthetic import closure with the original path/loading topology, and
executes the real original/patched appendix.main with explicit test doubles
for build, controls, source replay, and final authentication. The original
appendix bytes are hash-checked. These are not real upstream invoice replays.
"""
import argparse
import hashlib
import importlib.machinery
import importlib.util
import json
import os
from pathlib import Path
import py_compile
import subprocess
import sys
import tempfile
import types

HERE = Path(__file__).resolve().parent
LAUNCHER = HERE/'patch_tree/authenticated_run.py'
OLD = HERE/'original/h6_full_pr1424_appendix/appendix.py'
NEW = HERE/'patch_tree/h6_full_pr1424_appendix/appendix.py'
HASHES = {
    'old': 'cc43d4c89e32497caff1a8cd6f0ddd54c5fc1619c00d2e70ffe08ec52d473640',
    'new': '69b1981b049df19655c497387741ab04c93a40d82b48135b157b4d472f3ae345',
    'launcher': '704ee91443ea892c1fd296fafb5fe0b1a66e881f311620e2dcc0db1154e84449',
}


def need(test, message):
    if not test:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def direct(path, name, sha=None):
    data = path.read_bytes()
    if sha is not None:
        need(digest(data) == sha, 'test source SHA256: '+str(path))
    module = types.ModuleType(name)
    module.__file__ = str(path)
    exec(compile(data, str(path), 'exec', dont_inherit=True), module.__dict__)
    return module


def command(*arguments):
    return [sys.executable, '-I', '-B'] + (['-O'] if sys.flags.optimize else []) + [
        str(Path(__file__).resolve()), *map(str, arguments)]


def invoke(*arguments):
    return subprocess.run(command(*arguments), capture_output=True, text=True,
                          timeout=45)


LOAD = '''import importlib.util
from pathlib import Path
import sys

def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod
'''


def make_closure(root, explicit=False, snapshot=False, fail=False):
    """Harmless source/CACHED strings, not substituted scientific assertions."""
    api = direct(LAUNCHER, 'fixture_launcher', HASHES['launcher'])
    prefix = api.ORIGINAL
    bank = prefix+'/vendor/research/niemeier-lattices/workbench/paid-controller/banked.py'
    portable = bank.replace('banked.py', 'portable.py')
    costs = prefix+'/vendor/research/niemeier-lattices/code/costs.py'
    screen = prefix+'/vendor/research/leech-lattice/code/screen.py'
    entry = (api.APPENDIX+'/appendix.py') if explicit else prefix+'/audit.py'
    sources = {
        prefix+'/model.py': 'MARKER = "SOURCE"\n',
        prefix+'/source_bindings.py': LOAD+'''MARKER = "SOURCE"
def import_banked():
    return load(Path(__file__).parent/'vendor/research/niemeier-lattices/workbench/paid-controller/banked.py', 'h6_authenticated_banked')
''',
        portable: '''from pathlib import Path
MARKER = "SOURCE"
PACKAGE = Path(__file__).resolve().parents[2]
''',
        bank: LOAD+'''MARKER = "SOURCE"
sys.path.insert(0, str(Path(__file__).parent))
import portable
c = load(portable.PACKAGE/'code/costs.py', 'niemeier_costs')
''',
        costs: LOAD+'''MARKER = "SOURCE"
engine = load(Path(__file__).resolve().parents[2]/'leech-lattice/code/screen.py', 'frozen_niemeier_moment_bounds')
''',
        screen: 'MARKER = "SOURCE"\n',
    }
    top = LOAD+'''import json
MARKER = "SOURCE"
root = Path(__file__).resolve().parents[1]
(root/'ENTERED').write_text('entered')
'''
    if snapshot:
        top += '''p=root/'h6_banked_invoice_audit/model.py'
p.write_bytes(p.read_bytes().replace(b'SOURCE',b'ALTERD'))
'''
    if fail:
        top += "raise ValueError('forced entry failure')\n"
    if explicit:
        top += '''model = load(root/'h6_banked_invoice_audit/model.py', 'h6_appendix_model')
source_bindings = load(root/'h6_banked_invoice_audit/source_bindings.py', 'h6_appendix_bindings')
'''
    else:
        top += '''sys.path.insert(0, str(root/'h6_banked_invoice_audit'))
import model, source_bindings
'''
    top += '''b = source_bindings.import_banked()
print(json.dumps([MARKER, model.MARKER, source_bindings.MARKER,
                  b.MARKER, b.portable.MARKER, b.c.MARKER, b.c.engine.MARKER]))
'''
    sources[entry] = top
    manifest = {}
    stamp = 1700000000000000000
    for relative, text in sources.items():
        path = root/relative
        path.parent.mkdir(parents=True, exist_ok=True)
        current = text.encode('utf-8')
        cached = current.replace(b'MARKER = "SOURCE"', b'MARKER = "CACHED"')
        need(len(current) == len(cached), 'timestamp fixture equal source length')
        path.write_bytes(cached)
        os.utime(path, ns=(stamp, stamp))
        py_compile.compile(str(path), doraise=True, optimize=sys.flags.optimize,
                           invalidation_mode=py_compile.PycInvalidationMode.TIMESTAMP)
        path.write_bytes(current)
        os.utime(path, ns=(stamp, stamp))
        manifest[relative] = digest(current)
    (root/'fixture-manifest.json').write_text(json.dumps(manifest))
    (root/'entry.txt').write_text(entry)


def loader_worker(root, mode):
    api = direct(LAUNCHER, 'worker_launcher', HASHES['launcher'])
    entry = (root/'entry.txt').read_text()
    manifest = json.loads((root/'fixture-manifest.json').read_text())
    if mode == 'unchecked':
        spec = importlib.util.spec_from_file_location('__main__', root/entry)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return
    before = importlib.machinery.SourceFileLoader.get_code
    argv = sys.argv
    path = sys.path[:]
    main = sys.modules.get('__main__')
    try:
        api.run_authenticated(root, entry, [], manifest)
    finally:
        need(importlib.machinery.SourceFileLoader.get_code is before, 'loader not restored')
        need(sys.argv is argv and sys.path == path and sys.modules.get('__main__') is main,
             'process state not restored')


def appendix_worker(root, version, failure, source):
    app = direct(OLD if version == 'old' else NEW, 'ordering_fixture', HASHES[version])
    print('TEST DOUBLE ONLY: no real invoice/controls/source replay is executed.', flush=True)
    evidence = {'test_double': True, 'cases': [], 'author_source': {'fixture': 'author'}}
    result = {'rejected': [], 'positive': []}
    deps = [{'fixture': 'dependency'}]
    events = []

    def maybe(label):
        events.append(label)
        if failure == label:
            raise ValueError('injected '+label+' failure')

    def fake_build(*args):
        maybe('build')
        return evidence

    def fake_controls(*args):
        maybe('controls')
        return result

    def fake_source(*args):
        maybe('source_replay')

    def author():
        maybe('final_author')
        return evidence['author_source']

    def authenticate():
        maybe('final_dependencies')
        return deps

    app.load_original = lambda root: (None, types.SimpleNamespace(authenticate=authenticate), [], deps)
    app.build, app.controls, app.replay_source = fake_build, fake_controls, fake_source
    app.author_binding = author
    sys.argv = [str(OLD if version == 'old' else NEW),
                '--controls-output', str(root/'TEST_DOUBLE_CONTROLS.json')]
    if failure == 'validation':
        (root/'INPUT.json').write_text('{}\n')
        sys.argv += ['--evidence', str(root/'INPUT.json')]
    else:
        sys.argv += ['--output', str(root/'TEST_DOUBLE_EVIDENCE.json')]
    if source:
        sys.argv.append('--source')
    try:
        app.main()
    finally:
        (root/'events.json').write_text(json.dumps(events))


def run_checks(group):
    rows = []
    def add(name, proc=None, **details):
        row = {'test': name, 'result': 'PASS', **details}
        if proc is not None:
            row.update(returncode=proc.returncode, stdout=proc.stdout, stderr=proc.stderr)
        rows.append(row)
        print('PASS '+name, flush=True)

    for key, path in [('old', OLD), ('new', NEW), ('launcher', LAUNCHER)]:
        need(digest(path.read_bytes()) == HASHES[key], 'complete source hash '+key)
    need(OLD.read_bytes().split(b'\ndef main():')[0] ==
         NEW.read_bytes().split(b'\ndef main():')[0], 'non-main prefix changed')
    add('Original appendix authenticated; every byte preceding main unchanged')
    for redirect in ('--original', '--ori', '--orig=/untrusted'):
        cmd = [sys.executable, '-I', '-B'] + (['-O'] if sys.flags.optimize else [])
        p = subprocess.run(cmd+[str(LAUNCHER), 'appendix', redirect],
                           capture_output=True, text=True, timeout=45)
        need(p.returncode != 0 and 'Use launcher --root' in p.stderr,
             'source-root override was not rejected')
        add('Launcher rejects source-root override '+redirect, p)
    with tempfile.TemporaryDirectory(prefix='h6-hardening-') as temp:
        temp = Path(temp)
        if group in ('all','loader'):
            for explicit in (False, True):
                root = temp/('explicit' if explicit else 'ordinary')
                root.mkdir()
                make_closure(root, explicit=explicit)
                unguarded = invoke('--worker', 'loader', root, 'unchecked')
                need(unguarded.returncode == 0 and json.loads(unguarded.stdout) == ['CACHED']*7,
                     'cached reference not witnessed: '+unguarded.stderr)
                add(('Explicit' if explicit else 'Ordinary')+' closure: seven stale caches witnessed', unguarded)
                guarded = invoke('--worker', 'loader', root, 'guarded')
                need(guarded.returncode == 0 and json.loads(guarded.stdout) == ['SOURCE']*7,
                     'guard failed to compile authenticated closure: '+guarded.stderr)
                add(('Explicit' if explicit else 'Ordinary')+' closure: seven authenticated sources executed', guarded)

            root = temp/'snapshot'; root.mkdir(); make_closure(root, snapshot=True)
            p = invoke('--worker', 'loader', root, 'guarded')
            need(p.returncode == 0 and json.loads(p.stdout) == ['SOURCE']*7, 'authenticated snapshot lost')
            need(b'ALTERD' in (root/'h6_banked_invoice_audit/model.py').read_bytes(), 'snapshot mutation absent')
            add('Compile retained authenticated bytes, not a later source reread (synthetic only)', p)

            root = temp/'corrupt'; root.mkdir(); make_closure(root)
            with (root/'h6_banked_invoice_audit/model.py').open('ab') as f:
                f.write(b' ')
            p = invoke('--worker', 'loader', root, 'guarded')
            need(p.returncode != 0 and 'Source SHA256 mismatch' in p.stderr and
                 not (root/'ENTERED').exists(), 'preexecution hash gate failed')
            add('Preexisting one-byte source change rejected before entrypoint', p)

            root = temp/'exception'; root.mkdir(); make_closure(root, fail=True)
            p = invoke('--worker', 'loader', root, 'guarded')
            need(p.returncode != 0 and 'forced entry failure' in p.stderr and
                 'not restored' not in p.stderr, 'exception restoration failed')
            add('Loader/argv/path/main restored after entrypoint exception', p)

        if group in ('all','failures'):
            for version in ('old', 'new'):
                root = temp/(version+'-source-fail'); root.mkdir()
                p = invoke('--worker', 'appendix', root, version, 'source_replay', 'yes')
                exists = [(root/name).exists() for name in ('TEST_DOUBLE_EVIDENCE.json','TEST_DOUBLE_CONTROLS.json')]
                need(p.returncode != 0 and 'injected source_replay failure' in p.stderr,
                     'source failure not propagated')
                need(exists == ([True, True] if version == 'old' else [False, False]),
                     'unexpected output publication: '+str(exists))
                add(version+' appendix: injected source replay failure, output existence '+str(exists),
                    p, evidence_exists=exists[0], controls_exists=exists[1])

            for failure in ('build', 'controls', 'final_author', 'final_dependencies', 'validation'):
                root = temp/failure; root.mkdir()
                p = invoke('--worker', 'appendix', root, 'new', failure, 'yes')
                need(p.returncode != 0, 'injected failure accepted: '+failure)
                need(not (root/'TEST_DOUBLE_EVIDENCE.json').exists() and
                     not (root/'TEST_DOUBLE_CONTROLS.json').exists(), 'failed check left requested output')
                add('Patched appendix: '+failure+' failure leaves neither requested output', p)

        if group in ('all','success'):
            successes = []
            for version, source in (('old','yes'), ('new','yes'), ('new','no')):
                root = temp/(version+'-success-'+source); root.mkdir()
                p = invoke('--worker', 'appendix', root, version, 'none', source)
                need(p.returncode == 0, 'positive ordering fixture failed: '+p.stderr)
                pair = [(root/name).read_bytes() for name in
                        ('TEST_DOUBLE_EVIDENCE.json','TEST_DOUBLE_CONTROLS.json')]
                if successes:
                    need(pair == successes[0], 'successful serialization changed')
                successes.append(pair)
                events = json.loads((root/'events.json').read_text())
                need(('source_replay' in events) == (source == 'yes'), 'wrong requested source mode')
                add(version+' appendix: successful test-double serialization, source='+source,
                    p, output_hashes=list(map(digest,pair)), events=events)

            root=temp/'no-overwrite'; root.mkdir()
            dest=root/'TEST_DOUBLE_EVIDENCE.json'; dest.write_bytes(b'KEEP\n')
            p=invoke('--worker','appendix',root,'new','none','yes')
            need(p.returncode != 0 and 'FileExistsError' in p.stderr and dest.read_bytes()==b'KEEP\n',
                 'exclusive creation changed')
            need(not (root/'TEST_DOUBLE_CONTROLS.json').exists(), 'unexpected second output')
            add('Existing evidence refuses overwrite and keeps original bytes',p)
    return {'schema':'h6-execution-hardening-tests-v1',
            'python':sys.version,'optimization':sys.flags.optimize,'group':group,
            'scope':'Synthetic import closure and test-double-driven real appendix.main only; no producer evidence JSON or real upstream invoice replay.',
            'checked_code_hashes':HASHES,'tests':rows}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path)
    parser.add_argument('--group',choices=('all','loader','failures','success'),default='all')
    args=parser.parse_args()
    receipt=run_checks(args.group)
    if args.output:
        with args.output.open('x',encoding='utf-8',newline='\n') as f:
            json.dump(receipt,f,sort_keys=True,indent=2); f.write('\n')
    print('PASS %d scoped execution-hygiene tests; no new mathematical cases' % len(receipt['tests']))


if __name__ == '__main__':
    if sys.argv[1:2] == ['--worker']:
        kind, root, *rest = sys.argv[2:]
        if kind == 'loader':
            loader_worker(Path(root),rest[0])
        elif kind == 'appendix':
            appendix_worker(Path(root),rest[0],rest[1],rest[2]=='yes')
        else:
            raise ValueError('Unknown worker')
    else:
        main()
