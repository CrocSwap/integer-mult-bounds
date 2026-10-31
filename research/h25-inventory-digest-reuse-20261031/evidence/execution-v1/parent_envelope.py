"""Fixed independent postchecks inside outer GNU time; no target imports.

Run from the parent execution-v1 root under timeout --foreground -s INT.
Subprocess guard remains in our session/group; SIGINT is forwarded once so its
finally can kill/reap its own target. Timeout KILL can still leave incomplete
checks, which never qualify. No retry or alternate output path is supported.
"""
import hashlib
import json
import os
from pathlib import Path
import signal
import stat
import subprocess
import sys

WORKSPACE = Path('/home/d3lerium/.codex/.chatgpt-projects/g-p-6ad5817fd84881918865926b6fd51453')
HERE = Path(__file__).resolve().parent
ROOT = WORKSPACE / 'outputs/h25-data-handling-20261028/streams/digest-reuse-20261031/execution-v1'
STAGE_SHA = '59d4a2b48b508954491e9e14c0bb310722484a703e4b281ed50a4656fbd8e4a9'
RUNNER_SHA = '32633e40364d824c9f942af1ad2934da9701117328364c7c3f418b21b2e8054a'
PACKAGE_SHA = '159a85d5fd9c06d80c30635a7be27ef102be5943c75cff144cbe05bed85edd7e'
RUNTIME_SHA = 'ad2655b40ae2340048526a02d9a4215341112ef27f565c32a7ea5a87e80a0061'
JOBS_SHA = 'b3d1672402716f718abb73f3f2fd6298a7c2e4ef920780d7d226acd1ef66b185'
JOBS = {
    'inventory-controls-normal': ('inventory-controls', 'controls', 0),
    'inventory-controls-O': ('inventory-controls', 'controls', 1),
    'inventory-baseline-1': ('inventory-baseline', 'baseline', 0),
    'inventory-candidate-1': ('inventory-candidate', 'candidate', 0),
    'inventory-candidate-2': ('inventory-candidate', 'candidate', 0),
    'inventory-baseline-2': ('inventory-baseline', 'baseline', 0),
}
ORIGINAL = ('valid', 'list-pins', 'wrong-digest', 'missing', 'extra', 'extra-nonexact',
            'symlink', 'root-symlink', 'changed-mode', 'fresh-call-after-mutation', 'restored')
ORIGINAL_OUTCOMES = ('value', 'value', 'error', 'error', 'error', 'value', 'error', 'error', 'value', 'error', 'value')
ADDED = ('counts-valid', 'counts-list-pins', 'counts-wrong-digest-prefix', 'malformed-pin-before-sha',
         'nonlist-pin-not-coerced', 'sorted-first-failure', 'empty-pin-undeclared-before-read',
         'incomplete-after-traversal', 'counts-nonexact-extra', 'fresh-copy', 'copy-byte-mutation',
         'source-still-valid-after-copy-mutation', 'fresh-mode-change-and-boundary-rejection',
         'fresh-byte-mutation', 'fresh-repin-current-bytes', 'fresh-restored')


def need(condition, message):
    if not condition:
        raise RuntimeError(message)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode('ascii')


def small(path):
    need(path.is_file() and not path.is_symlink(), 'Missing/symlinked metadata: ' + str(path))
    with path.open('rb') as stream:
        raw = stream.read(1048577)
    need(len(raw) <= 1048576, 'Metadata exceeds1MiB')
    return raw


def trusted_json(path, expected):
    raw = small(path)
    need(digest(raw) == expected, 'Metadata identity changed: ' + str(path))
    return json.loads(raw)


def identity(info):
    return (info.st_dev, info.st_ino, info.st_mode, info.st_size, info.st_mtime_ns, info.st_ctime_ns)


def pin(path):
    need(path.is_absolute() and path.resolve() == path, 'Unresolved/symlinked path: ' + str(path))
    before = path.lstat()
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, 'rb', buffering=0) as stream:
        opened = os.fstat(stream.fileno())
        need(stat.S_ISREG(opened.st_mode), 'Nonregular file: ' + str(path))
        count, hasher = 0, hashlib.sha256()
        while count < opened.st_size:
            raw = stream.read(min(65536, opened.st_size - count))
            need(bool(raw), 'File ended early: ' + str(path))
            count += len(raw)
            hasher.update(raw)
        after = os.fstat(stream.fileno())
    need(identity(before) == identity(opened) == identity(after) == identity(path.lstat()),
         'File changed during read: ' + str(path))
    return {'sha256': hasher.hexdigest(), 'bytes': count, 'mode': stat.S_IMODE(after.st_mode)}


def check_files(entries):
    errors = []
    for path, expected in entries:
        try:
            actual = pin(path)
            need(all(actual[key] == value for key, value in expected.items()), 'File identity changed: ' + str(path))
        except BaseException as error:
            errors.append(type(error).__name__ + ': ' + str(error))
    need(not errors, 'Custody failures: ' + '; '.join(errors))
    return {'files_checked': len(entries)}


def stage_check(stage):
    declared = trusted_json(stage / 'STAGE.json', STAGE_SHA)
    need(declared['runner_sha256'] == RUNNER_SHA, 'Stage runner binding differs')
    expected = declared['files']
    paths = list(stage.rglob('*'))
    need(not any(path.is_symlink() for path in paths), 'Stage symlink')
    actual = {str(path.relative_to(stage)) for path in paths if path.is_file() and path.name != 'STAGE.json'}
    need(actual == set(expected), 'Stage file census differs')
    check_files([(stage / name, info) for name, info in sorted(expected.items())])
    check_files([(HERE / 'run_guarded.py', {'sha256': RUNNER_SHA})])
    need(digest(small(stage / 'JOBS.json')) == JOBS_SHA, 'Jobs changed')
    jobs = json.loads(small(stage / 'JOBS.json'))
    need(list(jobs) == list(JOBS), 'Job schedule changed')
    for name, (lane, _, optimized) in JOBS.items():
        need(jobs[name] == {'lanes': lane, 'finite_only': True, 'optimized': bool(optimized)}, 'Job binding differs')
    return {'stage_sha256': STAGE_SHA, 'stage_files': len(expected), 'runner_sha256': RUNNER_SHA}


def package_check(stage):
    package = stage / 'package'
    spec = trusted_json(package / 'SOURCE-PINS.json', PACKAGE_SHA)
    need(len(spec['package']) == 11 and len(spec['external']) == 36, 'Package source counts differ')
    need({str(path.relative_to(package)) for path in package.rglob('*') if path.is_file()} ==
         set(spec['package']) | {'SOURCE-PINS.json'}, 'Package census differs')
    return check_files([(package / name, info) for name, info in sorted(spec['package'].items())])


def external_check(stage):
    spec = trusted_json(stage / 'package/SOURCE-PINS.json', PACKAGE_SHA)
    entries = []
    for name, info in sorted(spec['external'].items()):
        relative = Path(name)
        need(not relative.is_absolute() and '..' not in relative.parts, 'Unsafe external source')
        entries.append((WORKSPACE / relative, info))
    need(len(entries) == 36, 'External source count differs')
    return check_files(entries)


def runtime_check(stage):
    need(small(stage / 'RUNTIME-PINS.sha256') == (RUNTIME_SHA + '\n').encode('ascii'), 'Runtime anchor differs')
    runtime = trusted_json(stage / 'RUNTIME-PINS.json', RUNTIME_SHA)
    need(runtime['python_version'] == sys.version and str(Path(sys.executable).resolve()) ==
         runtime['executable_realpath'] == '/usr/bin/python3.12', 'Interpreter differs')
    need(len(runtime['files']) == 86 and len(runtime['module_paths']) == 80, 'Runtime counts differ')
    check_files([(Path(name), info) for name, info in sorted(runtime['files'].items())])
    observed = {}
    for name, module in tuple(sys.modules.items()):
        filename = getattr(module, '__file__', None)
        if filename is None:
            continue
        path = str(Path(filename).resolve())
        expected = str(Path(__file__).resolve()) if name == '__main__' else runtime['module_paths'].get(name)
        need(path == expected, 'Envelope module origin differs: ' + name)
        observed[name] = path
    return {'files_checked': 86, 'module_origins': observed}


def guard_check(folder, stage, job, label):
    receipt = json.loads(small(folder / 'receipt.json'))
    need(receipt['status'] == 'PASS' and receipt['exit'] == 0 and receipt['termination'] is None,
         'Guard did not return PASS')
    need(receipt['source_bytes_and_modes_unchanged'] is True and receipt['retained_log_bytes_stable'] is True,
         'Guard source/log custody failed')
    need(receipt['stage_sha256'] == STAGE_SHA and receipt['runner_sha256'] == RUNNER_SHA and
         receipt['job'] == job and receipt['label'] == label, 'Guard operation binding differs')
    lane, _, optimized = JOBS[job]
    command = ['/usr/bin/python3.12', '-B'] + (['-O'] if optimized else []) + [
        str(stage / 'integration/full_driver.py'), '--output', str(folder / 'science'), '--lanes', lane, '--finite-only']
    need(receipt['command'] == command, 'Guard command differs')
    started = json.loads(small(folder / 'START.json'))
    need(all(receipt[key] == value for key, value in started.items()), 'Guard start/receipt differs')
    need(receipt['fractions_sha256'] == pin(Path('/usr/lib/python3.12/fractions.py'))['sha256'], 'Guard fractions drift')
    for name, prefix in (('stdout.txt', 'stdout'), ('stderr.txt', 'stderr')):
        info = pin(folder / name)
        need(info['bytes'] == receipt[prefix + '_bytes'] == receipt[prefix + '_final_bytes'] and
             info['sha256'] == receipt[prefix + '_sha256'], 'Guard retained log differs: ' + name)
    need(receipt['stderr_bytes'] == 0 and receipt['output_cap_observed_at'] is None, 'Guard log rejection')
    usage = json.loads(small(folder / 'usage.json'))
    need(usage == receipt['usage'] and usage['exit'] == 0, 'Guard usage differs')
    need(receipt['sampled_process_group_rss_bytes'] <= 1073741824 and
         receipt['runner_lifetime_max_rss_kib'] * 1024 <= 1073741824, 'Guard memory cap exceeded')
    need(receipt['runner_wall_seconds'] <= 180 and receipt['phase_cap_seconds'] == 600, 'Guard budget mismatch')
    expected_stdout = (json.dumps({'status': 'FINITE_INVENTORY_COMPONENT_RETURNED',
                       'mode': JOBS[job][1], 'optimization': optimized}, sort_keys=True) + '\n').encode()
    need(small(folder / 'stdout.txt') == expected_stdout, 'Exact adapter stdout differs')
    return {'status': receipt['status'], 'exit': receipt['exit'], 'retained_logs_rehashed': True}


def output_check(folder, stage, job):
    mode, optimized = JOBS[job][1:]
    science = folder / 'science'
    component = science / 'component'
    need(not (component / 'scratch').exists(), 'Leftover component scratch')
    need(not any(path.is_symlink() for path in science.rglob('*')), 'Output symlink')
    need({path.name for path in science.iterdir()} == {'component', 'adapter-boundary.json'}, 'Extra science output')
    need({path.name for path in component.iterdir()} == ({'component-receipt.json'} if mode == 'controls'
         else {'component-receipt.json', 'inventory.json'}), 'Extra component output')
    boundary = json.loads(small(science / 'adapter-boundary.json'))
    need(boundary['status'] == 'FINITE_INVENTORY_COMPONENT_RETURNED' and boundary['mode'] == mode and
         boundary['optimization'] == optimized, 'Adapter boundary status/mode differs')
    need(not any(key in boundary for key in ('primary_error_type', 'postcheck_error_type', 'cleanup_error_type')),
         'Adapter retained failure')
    cleanup = boundary['component_cleanup']
    need(cleanup == {'scratch_path': str(component / 'scratch'), 'scratch_exists_after': False,
                     'component_directory_exists': True}, 'Adapter cleanup differs')
    runtime = trusted_json(stage / 'RUNTIME-PINS.json', RUNTIME_SHA)
    for name in ('before', 'after'):
        custody = boundary[name]
        need(custody['runtime_manifest_sha256'] == RUNTIME_SHA and custody['runtime_file_count'] == 86 and
             custody['inventory_manifest_sha256'] == PACKAGE_SHA and custody['inventory_payload_files'] == 11 and
             custody['external_source_files'] == 36 and custody['immutable_workspace'] == str(WORKSPACE) and
             custody['assumptions'] == runtime['assumptions'], 'Adapter custody binding differs')
        for module, actual in custody['module_origins'].items():
            expected = (str(stage / 'integration/full_driver.py') if module == '__main__' else
                        str(stage / 'package' / (module + '.py')) if module in
                        ('component_consumer', 'reference', 'candidate', 'inventory_controls', 'digest_controls')
                        else runtime['module_paths'].get(module))
            need(actual == expected, 'Adapter module origin differs: ' + module)
    receipt = json.loads(small(component / 'component-receipt.json'))
    status = 'INVENTORY_COMPONENT_CONTROLS_RETURNED' if mode == 'controls' else 'INVENTORY_REPRESENTATIVE_COMPONENT_RETURNED'
    need(receipt['status'] == boundary['component_status'] == status and receipt['mode'] == mode and
         receipt['optimization'] == optimized and receipt['cleanup_complete'] is True, 'Component status/cleanup differs')
    pins = trusted_json(stage / 'package/SOURCE-PINS.json', PACKAGE_SHA)
    expected_custody = {'SOURCE-PINS.json': pin(stage / 'package/SOURCE-PINS.json')}
    expected_custody.update({'package/' + name: info for name, info in pins['package'].items()})
    expected_custody.update({'external/' + name: info for name, info in pins['external'].items()})
    need(receipt['source_custody'] == expected_custody, 'Component exact source custody differs')
    if mode == 'controls':
        old, added = receipt['original'], receipt['additional']
        need(receipt['case_count'] == 27 and old['status'] == 'INVENTORY_DIFFERENTIAL_CONTROLS_PASS' and
             old['cases'] == [[name, outcome] for name, outcome in zip(ORIGINAL, ORIGINAL_OUTCOMES)] and
             old['mode_drift_is_returned_for_boundary_comparison'] is True and
             old['publication_wrapper_independent_manifest_controls_still_required'] is True,
             'Original11 ordered controls/flags differ')
        need(added['status'] == 'DIGEST_COUNT_FRESHNESS_TYPED_CONTROLS_PASS' and added['case_count'] == 16 and
             [row['case'] for row in added['cases']] == list(ADDED) and added['production_instrumentation'] is False,
             'Additional16 ordered controls/flags differ')
        for index, row in enumerate(added['cases']):
            reads = ([6] if index in (2, 3, 4, 5) else [] if index == 6 else [7] if index in (10, 13)
                     else [7, 3] if index == 14 else [6, 3])
            for arm in ('reference', 'candidate'):
                counts = row[arm]
                hashes = ([] if index in (3, 6) else reads if len(reads) == 1 or arm == 'candidate'
                          else [value for length in reads for value in (length, length)])
                need(counts['hash_lengths'] == hashes and counts['hash_calls'] == len(hashes) and
                     counts['hash_bytes'] == sum(hashes) and counts['read_calls'] == len(reads) and
                     counts['read_bytes'] == sum(reads) and counts['reads'] ==
                     [[name, length] for name, length in zip(('alpha.txt', 'nested/beta.bin'), reads)],
                     'Independent control counters differ: ' + row['case'])
        return {'status': status, 'ordered_control_rows': 27, 'counter_sequences_checked': True}
    fixture = json.loads(small(stage / 'package/FIXTURE-v1.json'))
    need(fixture['file_count'] == 32 and fixture['total_bytes'] == 453700 and
         fixture['inventory_calls_per_arm'] == 128, 'Fixture dimensions differ')
    expected = {row['name']: {'sha256': row['sha256'], 'bytes': row['bytes'], 'mode': row['mode']}
                for row in fixture['files']}
    need(len(expected) == 32 and sum(row['bytes'] for row in expected.values()) == 453700,
         'Independent expected inventory differs')
    original_pins = trusted_json(WORKSPACE / fixture['manifest_source'], fixture['manifest_sha256'])
    need(sorted(expected) == sorted(original_pins) and all(row['pin'] == original_pins[row['name']] and
         row['sha256'] == original_pins[row['name']][0] for row in fixture['files']), 'Independent pin identity differs')
    raw = small(component / 'inventory.json')
    need(raw == canonical(expected) + b'\n', 'Exact independently derived inventory bytes differ')
    need(receipt['fixture_files'] == 32 and receipt['fixture_bytes'] == 453700 and receipt['inventory_calls'] == 128 and
         receipt['output_sha256'] == digest(raw) and receipt['declared_inventory_file_reads'] == 4096 and
         receipt['declared_inventory_read_bytes'] == 58073600 and
         receipt['declared_inventory_sha_calls'] == (8192 if mode == 'baseline' else 4096) and
         receipt['declared_inventory_sha_bytes'] == (116147200 if mode == 'baseline' else 58073600),
         'Representative operation bill/receipt differs')
    return {'status': status, 'exact_independent_inventory_sha256': digest(raw), 'files': 32, 'bytes': 453700, 'calls': 128}


def main():
    need(HERE == ROOT and len(sys.argv) == 4, 'Exact parent root and three fixed arguments required')
    stage_name, job, label = sys.argv[1:]
    need(stage_name == 'inventory-v1' and job in JOBS and label == job, 'Undeclared stage/job/label')
    stage, folder = HERE / 'stages' / stage_name, HERE / 'runtime/runs' / label
    need(not folder.exists(), 'Refusing earlier operation evidence')
    state = {'schema': 'inventory-parent-validation-v1', 'stage': stage_name, 'job': job, 'label': label,
             'status': 'STARTED', 'checks': {}, 'errors': [], 'interrupted': False}
    child, primary_code = None, None
    own_before = pin(Path(__file__).resolve())

    def interrupted(signum, frame):
        state['interrupted'] = True
        state.setdefault('first_signal', signum)
        if child is not None and child.poll() is None and not state.get('guard_interrupt_forwarded', False):
            state['guard_interrupt_forwarded'] = True
            child.send_signal(signal.SIGINT)

    signal.signal(signal.SIGINT, interrupted)
    signal.signal(signal.SIGTERM, interrupted)

    def check(name, function):
        try:
            state['checks'][name] = function()
        except BaseException as error:
            state['errors'].append({'check': name, 'type': type(error).__name__, 'message': str(error)})

    try:
        for name, function in (('stage_before', lambda: stage_check(stage)),
                ('package_before', lambda: package_check(stage)), ('external_before', lambda: external_check(stage)),
                ('runtime_before', lambda: runtime_check(stage))):
            check(name, function)
        need(not state['errors'] and not state['interrupted'], 'Prelaunch custody/interruption rejected')
        child = subprocess.Popen(['/usr/bin/python3.12', '-B', str(HERE / 'run_guarded.py'), stage_name, job, label], cwd=HERE)
        if state['interrupted']:
            interrupted(signal.SIGINT, None)
        primary_code = child.wait()
        state['guard_exit'] = primary_code
    except BaseException as error:
        state['errors'].append({'check': 'guard_dispatch', 'type': type(error).__name__, 'message': str(error)})
    finally:
        if child is not None and child.poll() is None:
            try:
                interrupted(signal.SIGINT, None)
                primary_code = child.wait()
                state['guard_exit'] = primary_code
            except BaseException as error:
                state['errors'].append({'check': 'guard_reap', 'type': type(error).__name__, 'message': str(error)})
        for name, function in (('stage_after', lambda: stage_check(stage)),
                ('package_after', lambda: package_check(stage)), ('external_after', lambda: external_check(stage)),
                ('runtime_after', lambda: runtime_check(stage)),
                ('guard_receipt_logs', lambda: guard_check(folder, stage, job, label)),
                ('component_outputs', lambda: output_check(folder, stage, job))):
            check(name, function)
        check('envelope_source', lambda: (need(pin(Path(__file__).resolve()) == own_before, 'Envelope source changed') or own_before))
        check('retained_root_census', lambda: (need({path.name for path in folder.iterdir()} ==
              {'START.json', 'stdout.txt', 'stderr.txt', 'usage.json', 'receipt.json', 'science'}, 'Extra/missing run output') or {'exact': True}))
        state['status'] = ('PASS' if primary_code == 0 and not state['errors'] and not state['interrupted'] else 'STOP')
        # A guard/preflight failure can leave no run directory. Preserve additive
        # evidence in a distinct fixed control path without fabricating a run.
        path = (folder / 'parent-validation.json' if folder.is_dir() else
                HERE / 'control' / ('parent-validation-' + label + '.json'))
        need(not path.exists(), 'Refusing earlier parent validation')
        raw = canonical(state) + b'\n'
        path.write_bytes(raw)
        need(path.read_bytes() == raw, 'Parent validation readback differs')
    print(json.dumps({'status': state['status'], 'job': job, 'validation': str(path)}, sort_keys=True))
    if state['interrupted']:
        raise SystemExit(130)
    if primary_code not in (None, 0):
        raise SystemExit(primary_code if primary_code > 0 else 128 - primary_code)
    if state['status'] != 'PASS':
        raise SystemExit(1)


if __name__ == '__main__':
    main()
