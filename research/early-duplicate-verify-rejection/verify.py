#!/usr/bin/env python3
"""Source-bound opt-in VERIFY object-key regression; no live runner is patched.

Prepared for ToikY with substantial OpenAI Codex assistance. Apache-2.0.
Canonical tooling credit: Douglas Colkitt, Tekalign, Ali Romman PR5728 and the
retained source/environment/exporter contributors. No scientific replay.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tarfile
import tempfile
import time

P = Path(__file__).resolve().parent
BASE = '7c49fe32c55de02c2c873655c804b16e4c3fef0a'
PACKAGE = 'research/metadata-json-fixture'
PATCH_SHA = '8469283da97d727d8d6c160b70837ca11db213219f95818825771651b9b56f10'
PATCHED_SHA = '0fbefb2c648388b9b131d70c232d169e46a59762f95ae2957c1e187d590022e9'
EXPECTED = {
    'vendor/research_package.py': ('scripts/research_package.py', 52346,
        'e1256016e7f51827d04fa2179255989f639ae1d97afaa9c16265f85a0c6abd70',
        '091b4c8f58bac9a9580d76025b887dc5c873d05f'),
    'vendor/export_research_package.py': ('scripts/export_research_package.py', 12446,
        '7126afaebff2328b8d64ba1ce992c497103820284f52d4590a558f97f13965fe',
        '25b0a12a8073f589867ca7f2e564ea5ae011bdf5'),
    'vendor/agent-task-catalog.json': ('docs/research/agent-task-catalog.json', 82822,
        'ead6cdc9d0af6d58e8a49744d8ec8c7c15e13d2ba93c276c434bcf9b51b93a81',
        '3404fbdd5e7529a0674eef26114b5071e4586cec'),
}
MARKER = b'INERT_FIXTURE_DISPATCH\n'
MARKER_PROGRAM = (b'from pathlib import Path\n'
                  b'Path(__file__).with_name("dispatch-marker.txt").write_bytes('
                  + repr(MARKER).encode() + b')\n'
                  b'print("PASS_INERT_FIXTURE_MARKER")\n')
GLOBAL_SECONDS = 165
CHILD_SECONDS = 20


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def git_blob(raw):
    return hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()


def encoded(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'),
                       ensure_ascii=True, allow_nan=False) + '\n').encode()


def unique(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, 'duplicate authenticated metadata key: ' + key)
        result[key] = value
    return result


def bad_number(value):
    raise ValueError('non-integer authenticated metadata number: ' + value)


def authenticate():
    pin_raw = (P / 'SOURCE-PINS.json').read_bytes()
    pins = json.loads(pin_raw, object_pairs_hook=unique,
                      parse_float=bad_number, parse_constant=bad_number)
    need(type(pins.get('schema_version')) is int and pins['schema_version'] == 1,
         'source pin schema')
    rows = pins.get('files')
    need(type(rows) is list and len(rows) == len(EXPECTED), 'source pin inventory')
    need({x.get('local_path') for x in rows} == set(EXPECTED), 'source pin paths')
    data = {}
    for row in rows:
        local = row['local_path']
        source_path, size, digest, blob = EXPECTED[local]
        need(row.get('source_commit') == BASE and row.get('source_path') == source_path
             and row.get('source_repository') == 'CrocSwap/integer-mult-bounds',
             'source pin identity: ' + local)
        need(type(row.get('bytes')) is int and row['bytes'] == size
             and row.get('sha256') == digest and row.get('git_blob') == blob,
             'source pin value: ' + local)
        raw = (P / local).read_bytes()
        need(len(raw) == size and sha(raw) == digest and git_blob(raw) == blob,
             'source bytes: ' + local)
        data[source_path] = raw
    patch = (P / 'STRICT-VERIFY.patch').read_bytes()
    need(len(patch) == 1742 and sha(patch) == PATCH_SHA, 'patch bytes')
    return data, sha(pin_raw)


class Trial:
    def __init__(self, root, context):
        self.root = root
        self.context = context
        self.deadline = time.monotonic() + GLOBAL_SECONDS
        self.env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
        for key in ('PYTHONPATH', 'PYTHONHOME', 'PYTHONOPTIMIZE', 'PYTHONSTARTUP',
                    'PYTHONINSPECT', 'PYTHONPYCACHEPREFIX'):
            self.env.pop(key, None)
        self.env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM='1',
                        GIT_TERMINAL_PROMPT='0', GIT_NO_REPLACE_OBJECTS='1',
                        PYTHONDONTWRITEBYTECODE='1', PYTHONIOENCODING='utf-8')

    def remaining(self):
        seconds = self.deadline - time.monotonic()
        need(seconds > 0, 'global tooling budget exhausted')
        return min(CHILD_SECONDS, seconds)

    def git(self, *args):
        command = ['git', '-c', 'maintenance.auto=false', '-c', 'gc.auto=0', *args]
        completed = subprocess.run(command, cwd=self.root, env=self.env,
                                   capture_output=True, timeout=self.remaining(), check=False)
        need(completed.returncode == 0,
             'fixture Git failure: ' + completed.stderr.decode('utf-8', 'replace'))
        return completed.stdout

    def command(self, argv, label):
        start = datetime.now(timezone.utc).isoformat()
        tick = time.perf_counter()
        budget = self.remaining()
        process = subprocess.Popen(argv, cwd=self.root, env=self.env,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   start_new_session=True)
        try:
            out, err = process.communicate(timeout=budget)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            out, err = process.communicate(timeout=3)
            self.context['commands'].append({'label': label, 'argv': argv,
                'started_at': start, 'seconds': time.perf_counter() - tick,
                'returncode': process.returncode, 'timeout': True,
                'stdout': out.decode('utf-8', 'replace'),
                'stderr': err.decode('utf-8', 'replace')})
            raise ValueError('source command timeout: ' + label)
        self.context['commands'].append({'label': label, 'argv': argv,
            'started_at': start, 'seconds': time.perf_counter() - tick,
            'returncode': process.returncode, 'timeout': False,
            'stdout': out.decode('utf-8', 'replace'),
            'stderr': err.decode('utf-8', 'replace')})
        return process.returncode, out, err


def write(root, name, raw):
    target = root / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(raw)


def pretty(value):
    return (json.dumps(value, indent=2, ensure_ascii=True) + '\n').encode()


def insert_before(raw, needle, inserted):
    need(raw.count(needle) == 1, 'fixture insertion must be unique')
    return raw.replace(needle, inserted + needle, 1)


def fixture_cases(task, sources, manifest):
    task_raw, source_raw, verify_raw = map(pretty, (task, sources, manifest))
    base = {'task': task_raw, 'sources': source_raw, 'verify': verify_raw}
    cases = []

    def add(name, changes=None, duplicate_key=None, array_boundary=False):
        value = dict(base)
        if changes:
            value.update(changes)
        value.update(name=name, duplicate_key=duplicate_key, array_boundary=array_boundary)
        cases.append(value)

    add('unambiguous')
    inputs = b'  "inputs": [\n'
    add('same_value_inputs', {'verify': insert_before(verify_raw, inputs,
        b'  "inputs": ["input.txt"],\n')}, 'inputs')
    add('conflicting_inputs', {'verify': insert_before(verify_raw, inputs,
        b'  "inputs": ["missing.txt"],\n')}, 'inputs')
    add('escaped_inputs', {'verify': insert_before(verify_raw, inputs,
        b'  "inpu\\u0074s": ["missing.txt"],\n')}, 'inputs')
    checks = b'      "checks": "Inert marker only"'
    add('nested_checks', {'verify': insert_before(verify_raw, checks,
        b'      "checks": "Earlier ignored description",\n')}, 'checks')
    author = b'  "author": "Metadata Fixture"'
    add('TASK_policy_unchanged', {'task': insert_before(task_raw, author,
        b'  "author": "Earlier ignored author",\n')})
    usage = b'      "usage": "provenance"'
    add('SOURCES_policy_unchanged', {'sources': insert_before(source_raw, usage,
        b'      "usage": "Earlier ignored usage",\n')})
    numeric = dict(manifest)
    numeric['extension'] = {'float': 0.5, 'nan': float('nan'), 'infinity': float('inf')}
    add('numeric_extension_policy_unchanged', {'verify': pretty(numeric)})
    array = dict(manifest)
    array['inputs'] = ['input.txt', 'input.txt']
    add('duplicate_input_array_remains_outside_patch', {'verify': pretty(array)},
        array_boundary=True)
    need(len(cases) == 9, 'case count')
    return cases


def classify(case, phase, operation, code, out, err, marker):
    duplicate = case['duplicate_key']
    reject = duplicate is not None and (phase == 'patched' or operation == 'export')
    if operation == 'export' and case['array_boundary']:
        reject = True
    if reject:
        expected = ('duplicate declared input' if case['array_boundary'] else
                    ('duplicate export JSON key: ' if operation == 'export' else
                     'duplicate VERIFY.json key: ') + duplicate)
        need(code == 1 and out == b'' and err == (expected + '\n').encode(),
             'wrong rejection: ' + case['name'] + '/' + phase + '/' + operation)
        need(marker is None, 'rejected case dispatched fixture command')
        return {'verdict': 'rejected', 'diagnostic': expected}
    need(code == 0 and err == b'', 'unexpected failure: ' + case['name'] + '/' + phase + '/' + operation)
    if operation == 'validate':
        need(out == b'PASS_PACKAGE_METADATA_AND_PINS (not a mathematical acceptance check)\n',
             'metadata positive marker')
        semantic = {'marker': 'PASS_PACKAGE_METADATA_AND_PINS'}
    elif operation == 'plan':
        planned = json.loads(out, object_pairs_hook=unique)
        need(planned == {'include': [{'package': PACKAGE}]}, 'planner selection changed')
        semantic = planned
    elif operation == 'export':
        prefix = b'PASS_RESEARCH_EXPORT '
        need(out.startswith(prefix), 'export positive marker')
        receipt = json.loads(out[len(prefix):], object_pairs_hook=unique)
        need(set(receipt) == {'commit', 'package', 'files'} and receipt['package'] == PACKAGE
             and type(receipt['files']) is int and receipt['files'] == 6,
             'export receipt shape')
        semantic = {'marker': 'PASS_RESEARCH_EXPORT', 'package': PACKAGE, 'files': 6}
    else:
        expected = ('CHECK Inert marker only\nPASS_INERT_FIXTURE_MARKER\n'
                    'PASS_REGISTERED_RESEARCH_PACKAGE ' + PACKAGE + ' outcome=partial\n').encode()
        need(out == expected and marker == MARKER, 'positive dispatch marker')
        semantic = {'marker': 'PASS_REGISTERED_RESEARCH_PACKAGE', 'inert_marker_written': True}
    if operation != 'dispatch':
        need(marker is None, 'non-dispatch operation executed fixture command')
    return {'verdict': 'accepted', 'semantic_output': semantic}


def run_suite(data, context):
    need(sys.version_info[:2] == (3, 12), 'harness requires Python3.12')
    need(os.name == 'posix', 'bounded process-group harness currently qualified for POSIX only')
    need(shutil.which('git') is not None, 'local Git executable required')
    rows = []
    archive_equalities = []
    case_manifest = []
    with tempfile.TemporaryDirectory(prefix='verify-duplicate-fixture-') as tmp:
        work = Path(tmp)
        root = work / 'repo'
        root.mkdir()
        trial = Trial(root, context)
        for name, raw in data.items():
            write(root, name, raw)
        write(root, 'input.txt', b'harmless exported metadata fixture input\n')
        trial.git('init', '-q')
        for key, value in [('user.name', 'Metadata Fixture'), ('user.email', 'fixture@example.invalid'),
                           ('core.autocrlf', 'false'), ('commit.gpgsign', 'false'),
                           ('core.hooksPath', os.devnull)]:
            trial.git('config', key, value)
        trial.git('add', 'scripts', 'docs', 'input.txt')
        trial.git('commit', '-qm', 'Synthetic base: exact canonical tooling/data')
        base = trial.git('rev-parse', 'HEAD').decode().strip()
        catalog = json.loads(data['docs/research/agent-task-catalog.json'])
        cards = [item for track in catalog['tracks'] for item in track['tasks']
                 if item['id'] == 'portable-replay']
        need(len(cards) == 1, 'one original portable card')
        task = {'schema_version': 1, 'task_id': 'portable-replay', 'priority_revision': 8,
                'base_commit': base, 'original_card': cards[0], 'scope_status': 'changed',
                'actual_scope': 'Metadata-only synthetic fixture; no scientific claim.',
                'scope_change_reason': 'Compare registered and export interpretation on exact committed metadata.',
                'bottleneck_link': 'One reproducible metadata exportability boundary.',
                'stop_rule': 'Only bounded metadata and inert marker commands.',
                'outcome': 'partial', 'evidence': 'Local tooling fixture, not scientific acceptance.',
                'author': 'Metadata Fixture', 'ai_assistance': 'OpenAI Codex tooling regression fixture.',
                'open_questions': [{'question': 'Does exact metadata interpretation agree?',
                    'why_it_matters': 'Decides only a tooling boundary.',
                    'first_step': 'Use unchanged committed fixtures.',
                    'blocked_by': 'No scientific implication is supplied.'}]}
        sources = {'schema_version': 1, 'base_commit': base, 'files': []}
        for name, usage in [('docs/research/agent-task-catalog.json', 'provenance'), ('input.txt', 'input')]:
            raw = (root / name).read_bytes()
            sources['files'].append({'path': name, 'usage': usage,
                                    'git_blob': git_blob(raw), 'sha256': sha(raw)})
        manifest = {'schema_version': 1, 'status': 'ready', 'python': '3.12', 'requirements': [],
                    'commands': [{'argv': ['{python}', '-B', '{package}/verify.py'],
                                  'timeout_seconds': 5, 'checks': 'Inert marker only'}],
                    'inputs': ['input.txt']}
        write(root, PACKAGE + '/README.md', b'# Inert fixture\n\n## Open next questions\n\nMetadata interpretation only.\n')
        write(root, PACKAGE + '/verify.py', MARKER_PROGRAM)
        cases = fixture_cases(task, sources, manifest)
        context['fixture_base'] = base
        for case in cases:
            write(root, 'scripts/research_package.py', data['scripts/research_package.py'])
            for field, name in [('task', 'TASK.json'), ('sources', 'SOURCES.json'), ('verify', 'VERIFY.json')]:
                write(root, PACKAGE + '/' + name, case[field])
            trial.git('add', PACKAGE)
            trial.git('commit', '-qm', 'Fixture case ' + case['name'])
            head = trial.git('rev-parse', 'HEAD').decode().strip()
            context.setdefault('fixture_heads', {})[case['name']] = head
            archive_reference = None
            case_manifest.append({'case': case['name'], 'duplicate_key': case['duplicate_key'],
                                  'array_boundary': case['array_boundary']})
            for phase in ['original', 'patched']:
                if phase == 'patched':
                    trial.git('apply', '--check', '--', str(P / 'STRICT-VERIFY.patch'))
                    context['git_apply_checks'] = context.get('git_apply_checks', 0) + 1
                    trial.git('apply', '--', str(P / 'STRICT-VERIFY.patch'))
                    context['git_apply_applications'] = context.get('git_apply_applications', 0) + 1
                expected_runner = EXPECTED['vendor/research_package.py'][2] if phase == 'original' else PATCHED_SHA
                need(sha((root / 'scripts/research_package.py').read_bytes()) == expected_runner,
                     'source phase runner hash')
                need(sha((root / 'scripts/export_research_package.py').read_bytes()) ==
                     EXPECTED['vendor/export_research_package.py'][2], 'exporter changed')
                for mode in ['normal', 'optimized']:
                    options = [sys.executable, '-W', 'error', '-B']
                    if mode == 'optimized':
                        options.insert(1, '-O')
                    for operation in ['validate', 'plan', 'export', 'dispatch']:
                        marker_path = root / PACKAGE / 'dispatch-marker.txt'
                        need(not marker_path.exists(), 'leftover marker')
                        raw = (root / PACKAGE / 'VERIFY.json').read_bytes()
                        need(raw == trial.git('show', head + ':' + PACKAGE + '/VERIFY.json') == case['verify'],
                             'working/committed manifest mismatch')
                        archive = work / (case['name'] + '-' + phase + '-' + mode + '.tar')
                        if operation == 'export':
                            argv = options + [str(root / 'scripts/export_research_package.py'), 'export',
                                '--package', PACKAGE, '--ref', head, '--output', str(archive)]
                        elif operation == 'plan':
                            argv = options + [str(root / 'scripts/research_package.py'), '--changed-since', base]
                        else:
                            argv = options + [str(root / 'scripts/research_package.py'), '--package', PACKAGE]
                            if operation == 'validate':
                                argv.append('--check-only')
                        label = '/'.join([case['name'], phase, mode, operation])
                        code, out, err = trial.command(argv, label)
                        context['commands'][-1].update({
                            'fixture_head': head, 'manifest_sha256': sha(raw),
                            'source_phase': phase, 'runner_sha256': expected_runner,
                            'exporter_sha256': EXPECTED['vendor/export_research_package.py'][2],
                            'working_runner_patch_intentional': phase == 'patched'})
                        marker = marker_path.read_bytes() if marker_path.exists() else None
                        normalized = classify(case, phase, operation, code, out, err, marker)
                        if marker_path.exists():
                            marker_path.unlink()
                        need((root / PACKAGE / 'VERIFY.json').read_bytes() == raw,
                             'command mutated manifest')
                        need(sha((root / 'scripts/research_package.py').read_bytes()) == expected_runner,
                             'command mutated source phase')
                        if operation == 'export':
                            if normalized['verdict'] == 'accepted':
                                archive_bytes = archive.read_bytes()
                                if archive_reference is None:
                                    archive_reference = archive_bytes
                                else:
                                    need(archive_bytes == archive_reference, 'matched export bytes changed')
                                with tarfile.open(archive, 'r:') as reader:
                                    members = reader.getmembers()
                                    need(len(members) == 7 and all(x.isfile() for x in members),
                                         'positive archive inventory')
                                    need(reader.extractfile(PACKAGE + '/VERIFY.json').read() == raw,
                                         'archive manifest differs')
                            else:
                                need(not archive.exists(), 'rejected export left archive')
                        rows.append({'case': case['name'], 'source_phase': phase, 'mode': mode,
                                     'operation': operation, 'returncode': code, **normalized})
            archive_equalities.append({'case': case['name'], 'accepted_export_bytes_equal':
                                       archive_reference is not None})
            write(root, 'scripts/research_package.py', data['scripts/research_package.py'])
            need(trial.git('status', '--porcelain') == b'', 'unplanned fixture worktree changes')
        need(not list(root.rglob('*.pyc')), 'fixture bytecode appeared')
    need(len(rows) == 144, 'full outcome table count')
    return {'cases': case_manifest, 'outcomes': rows, 'export_comparisons': archive_equalities}


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('--raw-context-out', type=Path,
                        help='optional explicit context receipt outside the package; omitted in CI')
    args = parser.parse_args()
    context_target = None
    context = {'schema_version': 1, 'commands': [],
               'scope': 'Tiny tooling fixtures and inert marker only; no scientific replay.'}
    try:
        if args.raw_context_out is not None:
            need(not args.raw_context_out.resolve().is_relative_to(P), 'context must be outside package')
            context_target = args.raw_context_out
        data, pin_sha = authenticate()
        table = run_suite(data, context)
        receipt = {'schema_version': 1, 'status': 'PASS_EARLY_DUPLICATE_VERIFY_REJECTION',
                   'source_base': BASE, 'source_manifest_sha256': pin_sha,
                   'source_sha256': {name: value[2] for name, value in EXPECTED.items()},
                   'patch_sha256': PATCH_SHA, 'candidate_runner_sha256': PATCHED_SHA,
                   'fixture_cases': len(table['cases']),
                   'actual_source_cli_commands': len(table['outcomes']),
                   'accepted_outcomes': sum(x['verdict'] == 'accepted' for x in table['outcomes']),
                   'rejected_outcomes': sum(x['verdict'] == 'rejected' for x in table['outcomes']),
                   'inert_marker_dispatches': sum(x.get('semantic_output', {}).get(
                       'inert_marker_written', False) for x in table['outcomes']),
                   'git_apply_checks': context['git_apply_checks'],
                   'git_apply_applications': context['git_apply_applications'],
                   'source_phases': ['original', 'patched'], 'modes': ['normal', 'optimized'],
                   'operations': ['validate', 'plan', 'export', 'dispatch'],
                   'outcome_table_sha256': sha(encoded(table)), 'profile': table,
                   'scope': 'VERIFY object-key early rejection only. TASK/SOURCES/numeric policies unchanged. '
                            'Duplicate input-array entries remain a demonstrated exportability limitation. '
                            'No metadataPASS-implies-export, security, scientific or global-inventory guarantee.',
                   'execution_scope': 'POSIX process-group bounds; CPython3.12 and local Git; '
                                      'no live/shared runner or workflow modified; source programs run only in fixtures.'}
        package_hashes = {f.relative_to(P).as_posix(): sha(f.read_bytes())
                          for f in sorted(P.rglob('*')) if f.is_file()}
        receipt['package_sha256'] = package_hashes
        context['status'] = receipt['status']
        print(json.dumps(receipt, sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False))
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
        context['status'] = 'FAIL'
        context['error'] = str(error)
        print('FAIL_EARLY_DUPLICATE_VERIFY_REJECTION: ' + str(error), file=sys.stderr)
        raise SystemExit(1)
    finally:
        if context_target is not None:
            context_target.parent.mkdir(parents=True, exist_ok=True)
            context_target.write_bytes(encoded(context))


if __name__ == '__main__':
    main()
