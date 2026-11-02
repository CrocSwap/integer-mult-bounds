#!/usr/bin/env python3
"""Bounded complete scanner conformance; historical repository replay deferred."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    import adapter
finally:
    sys.path.pop(0)

HERE = Path(__file__).resolve().parent
FIXTURE_ENV = None


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def git(root, *args):
    require(FIXTURE_ENV is not None, 'authenticated fixture environment initialized')
    env = dict(FIXTURE_ENV(), GIT_AUTHOR_NAME='Fixture', GIT_AUTHOR_EMAIL='fixture@example.invalid',
               GIT_COMMITTER_NAME='Fixture', GIT_COMMITTER_EMAIL='fixture@example.invalid',
               GIT_AUTHOR_DATE='2000-01-01T00:00:00+0000', GIT_COMMITTER_DATE='2000-01-01T00:00:00+0000')
    return subprocess.run(['git', '--no-replace-objects', *args], cwd=root, env=env,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True).stdout


def write(root, name, data):
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def commit(root, message):
    git(root, 'add', '-f', '-A')
    git(root, '-c', 'commit.gpgsign=false', 'commit', '-qm', message)
    return git(root, 'rev-parse', 'HEAD').decode().strip()


def fixture(root):
    git(root, 'init', '-q', '--object-format=sha1', '--initial-branch=main')
    for key, value in [('core.attributesFile', '/dev/null'), ('core.autocrlf', 'false'),
                       ('core.excludesFile', '/dev/null'),
                       ('core.hooksPath', '/dev/null'), ('commit.gpgsign', 'false'),
                       ('diff.opaque.binary', 'true'), ('core.fsmonitor', 'false')]:
        git(root, 'config', key, value)
    old_a, old_b = b'target-A-old\n', b'target-B-old\n'
    a, b = sha(old_a), sha(old_b)
    targets = {'docs/alpha.txt': (a, 'modified'), 'research/beta.dat': (a, 'modified'),
               'upstream/gamma.dat': (b, 'deleted')}
    for name, data in [('docs/alpha.txt', old_a), ('research/beta.dat', old_a),
                       ('upstream/gamma.dat', old_b), ('docs/unpinned.dat', b'unreferenced-old')]:
        write(root, name, data)
    attrs = b'policy/00-bin.dat -diff\npolicy/01-text.txt diff\npolicy/02-custom.dat diff=opaque\npolicy/ascii-custom.dat diff=opaque\n'
    write(root, '.gitattributes', attrs)
    ordinary = b'Pin ' + a.encode() + b'\n'
    pinners = {}
    for name in ['docs/unchanged.txt', 'docs/repinned.txt', 'docs/removed.txt', 'policy/ascii-text.txt']:
        write(root, name, ordinary)
        pinners[name] = {a}
    write(root, 'policy/ascii-custom.dat', ordinary)
    weird = ['docs/line\nname', 'docs/line\rname', 'docs/[x]*?.txt', ':(exclude)colon.txt']
    for name in weird:
        write(root, name, a.encode() + b' repeat ' + a.encode() + b' ' + b.encode() + b'\n')
        pinners[name] = {a, b}
    nul = b'\0' + a.encode() + b'\n'
    for name in ['policy/00-bin.dat', 'policy/01-text.txt', 'policy/02-custom.dat', 'policy/03-auto.dat']:
        write(root, name, nul)
    pinners['policy/01-text.txt'] = {a}
    crossing = b'a' * (adapter.CHUNK - 31) + a.encode() + b'fff\n'
    for name in ['cross/a.txt', 'cross/b.txt']:
        write(root, name, crossing)
        pinners[name] = {a}
    for i in range(32):
        write(root, 'inert/copy-%02d.dat' % i, b'No wanted digest in this duplicate object.\n')
    base = commit(root, 'base')
    write(root, 'docs/alpha.txt', b'target-A-new-one\n')
    write(root, 'research/beta.dat', b'target-A-new-two\n')
    (root / 'upstream/gamma.dat').unlink()
    write(root, 'docs/unpinned.dat', b'unreferenced-new')
    write(root, 'docs/repinned.txt', b'old digest removed\n')
    (root / 'docs/removed.txt').unlink()
    write(root, 'docs/added.txt', a.encode() + b' ' + b.encode())
    head = commit(root, 'mixed')
    write(root, 'docs/unpinned.dat', b'unreferenced-third')
    nohit = commit(root, 'no-hit')
    git(root, 'checkout', '-q', base)
    write(root, 'docs/alpha.txt', b'only living target changed\n')
    living = commit(root, 'living')
    return base, head, nohit, living, targets, pinners


def expected_pins(targets, pinners):
    result = []
    for pinner, digests in pinners.items():
        state = {'docs/repinned.txt': 'repinned', 'docs/removed.txt': 'pinner_removed'}.get(pinner, 'stale')
        for target, (digest, change) in targets.items():
            if digest in digests:
                result.append({'pinned': target, 'change': change, 'pinner': pinner,
                               'sha256': digest, 'state': state,
                               'frozen': target.startswith(('research/', 'upstream/'))})
    return sorted(result, key=lambda row: (not row['frozen'], row['state'] != 'stale', row['pinned'], row['pinner']))


def report(module, root, base, head, optimized=False, **options):
    if optimized:
        with adapter.installed(module, **options) as hook:
            value = module.check(root, base, head)
        return value, hook.metrics
    return module.check(root, base, head), None


def cli(root, base, head, flags):
    observed = []
    for mode in ('predecessor', 'reuse', 'prefilter'):
        command = [sys.executable, '-I', '-W', 'error', '-B']
        if not __debug__:
            command.append('-O')
        command += [str(HERE / 'adapter.py'), mode, '--root', str(root), '--base', base, '--head', head] + flags
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30)
        require(not result.stderr, 'CLI stderr: ' + mode + ':' + result.stderr.decode(errors='replace'))
        observed.append((result.returncode, result.stdout))
    require(observed[0] == observed[1] == observed[2], 'complete CLI stdout/exit conformance')
    return {'flags': flags, 'exit': observed[0][0], 'stdout_sha256': sha(observed[0][1])}


def policy_controls(module, root, base, digest):
    patterns = ('grep', '-I', '-l', '-z', '-F', '-e', digest, base, '--')
    result = module.git(root, *patterns, check=False)
    found = {entry.decode().split(':', 1)[1] for entry in result.stdout.split(b'\0') if entry}
    aliases = {'policy/00-bin.dat', 'policy/01-text.txt', 'policy/02-custom.dat', 'policy/03-auto.dat'}
    require(found & aliases == {'policy/01-text.txt'}, 'actual per-path force-binary/force-text policy')
    require('policy/ascii-text.txt' in found and 'policy/ascii-custom.dat' not in found, 'custom diff binary driver classification')
    return {'binary_representative_false_negative': ['policy/01-text.txt'],
            'text_representative_false_positives': sorted(aliases - {'policy/01-text.txt'}),
            'custom_driver_ascii_alias_excluded': True}


def fallback_controls(module, root, base, head, expected):
    controls = {}
    value, metrics = report(module, root, base, head, True, max_argument_bytes=1)
    require(value == expected and metrics['fallbacks'], 'oversize argument fallback')
    controls['argument_bound'] = metrics['fallbacks']
    for key in ('submodule.recurse', 'grep.recurseSubmodules'):
        git(root, 'config', key, 'true')
        try:
            value, metrics = report(module, root, base, head, True)
            require(value == expected and metrics['fallbacks'], 'recursive configuration fallback')
            controls[key] = metrics['fallbacks']
        finally:
            git(root, 'config', '--unset-all', key)
    with adapter.installed(module) as hook:
        with patch.object(hook, 'candidates', side_effect=ValueError('injected raw-reader failure')):
            value = module.check(root, base, head)
        require(value == expected and hook.metrics['fallbacks'], 'reader error fallback')
        controls['reader_error'] = hook.metrics['fallbacks']
    before = module.git(root, 'grep', '--not-a-real-option', check=False)
    with adapter.installed(module):
        after = module.git(root, 'grep', '--not-a-real-option', check=False)
    require((before.returncode, before.stdout, before.stderr) == (after.returncode, after.stdout, after.stderr), 'unsupported call delegates exact error')
    controls['unsupported_call_error_preserved'] = True
    return controls


def actual_alias_control(module, root, base, head, expected):
    with adapter.installed(module) as hook:
        original = hook.candidates
        def dropped(*args):
            return [p for p in original(*args) if p not in ('cross/b.txt', 'docs/line\nname')]
        with patch.object(hook, 'candidates', side_effect=dropped):
            bad = module.check(root, base, head)
    missing = [row for row in expected['pins'] if row not in bad['pins']]
    require(bad != expected and len(missing) == 5, 'actual alias-drop mutant must lose five complete rows')
    return {'classification': 'corrupted candidate expansion, not an accepted scanner', 'missing_rows': missing}


def fixture_run(raw):
    predecessor, reuse = adapter.load_source('predecessor', raw), adapter.load_source('reuse', raw)
    with tempfile.TemporaryDirectory(prefix='pinned-prefilter-') as scratch:
        root = Path(scratch)
        base, head, nohit, living, targets, pinners = fixture(root)
        old, _ = report(predecessor, root, base, head)
        reused, _ = report(reuse, root, base, head)
        new, metrics = report(reuse, root, base, head, True)
        require(old == reused == new, 'complete three-way controlled report equality')
        require(new['pins'] == expected_pins(targets, pinners), 'independently specified complete pin rows')
        require(len(new['pins']) == 26 and new['stale'] == 22 and new['frozen_stale'] == 13, 'explicit mixed classification counts')
        require(not metrics['fallbacks'] and metrics['unique_blob_reads'] == metrics['unique_tree_blobs'], 'each unique tree blob streamed once')
        require(metrics['candidate_aliases'] == metrics['final_grep_pathspecs'] < metrics['regular_tree_paths'], 'all candidate aliases passed to Git')
        policy = policy_controls(reuse, root, base, targets['docs/alpha.txt'][0])
        missing = actual_alias_control(reuse, root, base, head, new)
        fallback = fallback_controls(reuse, root, base, head, new)
        empty, _ = report(reuse, root, head, head, True)
        require(empty['changed_files'] == 0 and not empty['pins'], 'empty diff conformance')
        no_match, none_metrics = report(reuse, root, head, nohit, True)
        baseline_none, _ = report(predecessor, root, head, nohit)
        require(no_match == baseline_none and not no_match['pins'] and none_metrics['fallbacks'], 'empty candidates delegate original no-match behavior')
        living_report, _ = report(reuse, root, base, living, True)
        require(living_report['stale'] == 11 and living_report['frozen_stale'] == 0, 'living-only advisory contract')
        commands = [cli(root, base, head, flags) for flags in ([], ['--json'], ['--strict'], ['--json', '--strict'])]
        living_cli = [cli(root, base, living, flags) for flags in ([], ['--strict'])]
        require([x['exit'] for x in living_cli] == [0, 1], 'default advisory versus strict exit')
        return {'schema_version': 1, 'scope': 'bounded complete controlled Git fixture; canonical154-row historical replay deferred',
                'source_manifest_sha256': adapter.MANIFEST_SHA,
                'fixture_commits': {'base': base, 'head': head, 'nohit': nohit, 'living': living},
                'complete_report': new, 'complete_report_sha256': sha(adapter.canonical(new).encode()),
                'observed_work': metrics, 'no_match_work': none_metrics, 'policy_counterexamples': policy,
                'actual_alias_drop_control': missing, 'fallback_controls': fallback,
                'full_cli_conformance': commands, 'living_default_strict': living_cli,
                'limits': ['Raw unique blob requests and final Git candidate pathspecs are different work units; no decompression,filesystem I/O,memory or speed gain inferred.',
                           'Valid stable Git objects and inherited UTF8 path contract; no universal failure or Windows lifecycle claim.',
                           'Original Git retains every candidate path text/binary decision; no representative policy cache or cross-scan cache.',
                           'No shared scanner/CI installation,scientific/native replay,kappa or frontier change.']}


def run():
    raw = adapter.authenticated()
    global FIXTURE_ENV
    FIXTURE_ENV = adapter.helper_module(raw['research_package.py']).git_source_env
    env = {key: value for key, value in FIXTURE_ENV().items() if not key.startswith('GIT_')}
    env.update(GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL=os.devnull)
    with patch.dict(os.environ, env, clear=True):
        return fixture_run(raw)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--emit', action='store_true')
    args = parser.parse_args()
    result = run()
    if args.emit:
        print(adapter.canonical(result))
    else:
        retained = HERE / 'RESULT.json'
        require(retained.is_file(), 'retained RESULT.json required')
        observed = adapter.decode(retained.read_bytes())
        require(type(observed) is dict and type(observed.get('schema_version')) is int and observed['schema_version'] == 1, 'typed receipt schema')
        require(adapter.canonical(observed) == adapter.canonical(result), 'strict complete receipt comparison')
        print('PASS_PINNED_DIGEST_BLOB_PREFILTER')


if __name__ == '__main__':
    main()
