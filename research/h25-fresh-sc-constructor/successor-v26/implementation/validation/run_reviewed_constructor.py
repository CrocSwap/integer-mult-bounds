#!/usr/bin/env python3
"""Adapted PR6588 serial wrapper: NEW controls and inert preparation only.

Parent supplies independently reviewed inventory and oracle hashes. No original
module is imported/extracted/executed. Opaque blobs are copied and hashed only.
External finally preserves partials even when internal postchecks fail.
"""
from pathlib import Path
import hashlib
import json
import os
import resource
import selectors
import shutil
import stat
import subprocess
import sys
import time

SOURCE = Path(__file__).resolve().parents[1]
ROUND = SOURCE.parent
HERE = ROUND / 'validation'
RAW_CAP = 1024 * 1024
FILE_LIMIT = 64 * 1024 * 1024
CLAIMS = {'runtime_admission': False, 'C07': False, 'full_C05': False,
          'full_V03': False, 'original_credit': 0}


def need(value, message):
    if value is not True:
        raise RuntimeError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def raw_json(value):
    return json.dumps(value, indent=2, sort_keys=True, allow_nan=False).encode('ascii') + b'\n'


def retained_write(path, value):
    raw = raw_json(value)
    with path.open('xb') as stream:
        need(stream.write(raw) == len(raw), 'complete retained evidence write')
        stream.flush()
        os.fsync(stream.fileno())
    need(path.read_bytes() == raw, 'retained evidence exact readback')


def inventory(root):
    if not root.exists():
        return {'exists': False, 'files': [], 'directories': []}
    rows, directories = [], []
    for path in sorted(root.rglob('*')):
        info = path.lstat()
        need(not stat.S_ISLNK(info.st_mode), 'inventory symlink')
        if stat.S_ISDIR(info.st_mode):
            directories.append({'path': path.relative_to(root).as_posix(), 'mode': stat.S_IMODE(info.st_mode)})
            continue
        need(stat.S_ISREG(info.st_mode) and info.st_size <= FILE_LIMIT, 'inventory regular/file bound')
        raw = path.read_bytes()
        rows.append({'path': path.relative_to(root).as_posix(), 'bytes': len(raw),
                     'sha256': sha(raw), 'mode': stat.S_IMODE(info.st_mode)})
    return {'exists': True, 'files': rows, 'directories': directories}


def checked_inventory(root, entries, exact_tree=False):
    need(len(entries) == len({r['path'] for r in entries}), 'unique frozen inventory')
    for row in entries:
        path = root / row['path']
        need(not path.is_symlink() and path.is_file(), 'frozen regular file')
        raw = path.read_bytes()
        need(len(raw) == row['bytes'] and sha(raw) == row['sha256'], 'frozen file ' + row['path'])
    if exact_tree or root == SOURCE:
        actual = inventory(root)
        excluded = set() if exact_tree else {'validation/EXECUTION-INVENTORY-v2.json', 'AUTHOR-FREEZE-CONSTRUCTOR-v1.json'}
        need({r['path'] for r in actual['files']} - excluded == {r['path'] for r in entries}, 'exact source/cold tree')
        expected_dirs = {str(parent) for row in entries for parent in Path(row['path']).parents if str(parent) != '.'}
        need({r['path'] for r in actual['directories']} == expected_dirs, 'exact source/cold directories')


def limits():
    resource.setrlimit(resource.RLIMIT_AS, (1024 ** 3, 1024 ** 3))
    resource.setrlimit(resource.RLIMIT_CPU, (15, 15))
    resource.setrlimit(resource.RLIMIT_FSIZE, (FILE_LIMIT, FILE_LIMIT))


def run_child(command, cold, tag):
    """Separate exact bounded raw captures; overflow/timeouts retain failure."""
    prior = resource.getrusage(resource.RUSAGE_CHILDREN)
    start = time.monotonic()
    record = {'tag': tag, 'command': command, 'status': 'INCOMPLETE', 'raw_limit': RAW_CAP}
    env = {'PATH': '/usr/bin:/bin', 'LANG': 'C.UTF-8', 'LC_ALL': 'C.UTF-8',
           'PYTHONDONTWRITEBYTECODE': '1', 'PYTHONHASHSEED': '0', 'TZ': 'UTC'}
    output = {}
    with (HERE / (tag + '.stdout')).open('xb') as out, (HERE / (tag + '.stderr')).open('xb') as err:
        process = subprocess.Popen(command, cwd=cold, env=env, stdin=subprocess.DEVNULL,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=limits)
        selector = selectors.DefaultSelector()
        sizes = {'stdout': 0, 'stderr': 0}
        sinks = {'stdout': out, 'stderr': err}
        overflow, timeout = False, False
        for pipe, name in ((process.stdout, 'stdout'), (process.stderr, 'stderr')):
            os.set_blocking(pipe.fileno(), False)
            selector.register(pipe, selectors.EVENT_READ, name)
        code, capture_error = None, None
        try:
            while selector.get_map():
                remaining = 15 - (time.monotonic() - start)
                if remaining <= 0:
                    timeout = True
                    process.kill()
                    break
                for key, unused in selector.select(min(remaining, 0.1)):
                    name = key.data
                    block = os.read(key.fileobj.fileno(), min(65536, RAW_CAP - sizes[name] + 1))
                    if not block:
                        selector.unregister(key.fileobj)
                        continue
                    allowed = min(len(block), RAW_CAP - sizes[name])
                    sinks[name].write(block[:allowed])
                    sizes[name] += allowed
                    if allowed < len(block):
                        overflow = True
                        process.kill()
                        break
                if overflow:
                    break
            code = process.wait(timeout=max(0.05, 15 - (time.monotonic() - start)))
        except BaseException as error:
            capture_error = error
            if process.poll() is None:
                process.kill()
            code = process.wait()
        finally:
            selector.close()
            process.stdout.close()
            process.stderr.close()
            out.flush()
            err.flush()
            record.update({'returncode': process.poll(), 'timeout': timeout, 'overflow': overflow,
                           'wall_seconds': time.monotonic() - start, 'raw_sizes': sizes})
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    for name in ('stdout', 'stderr'):
        output[name] = (HERE / (tag + '.' + name)).read_bytes()
        record[name + '_sha256'] = sha(output[name])
    record['cpu_seconds'] = after.ru_utime + after.ru_stime - prior.ru_utime - prior.ru_stime
    record['cumulative_child_peak_rss_kib'] = after.ru_maxrss
    if capture_error is not None:
        record['capture_error'] = {'type': type(capture_error).__name__, 'message': str(capture_error)}
    retained_write(HERE / (tag + '.attempt.json'), record)
    if capture_error is not None:
        raise capture_error
    need(code == 0 and not timeout and not overflow and output['stderr'] == b'', 'failed child retained; no next launch')
    return json.loads(output['stdout']), record


def finalize_attempt(prepared, finish, capture, ledger):
    """Public tiny-fixture seams for final-close/capture/ledger failure controls.

    Intermediate preparation never produces terminal acceptance. Every finally
    stage is attempted, preserving the first raw error and later stage errors.
    """
    state = {'status': 'INCOMPLETE', 'prepared': prepared, 'finish': False,
             'external_inventory': False, 'ledger': False, 'errors': []}
    for name, operation in (('finish', finish), ('external_inventory', capture), ('ledger', ledger)):
        try:
            operation(state)
            state[name] = True
        except BaseException as error:
            state['errors'].append({'stage': name, 'type': type(error).__name__, 'message': str(error)})
    if not state['errors'] and prepared is True:
        state['status'] = 'COMPLETE_INERT_INSTALLATION_ONLY'
    return state


def verify_stage(stage, rows):
    actual = inventory(stage)
    expected = {r['installed_relative_path']: r for r in rows if r['installed_relative_path'] is not None}
    need(actual['exists'] and {r['path'] for r in actual['files']} == set(expected), 'external exact259 stage inventory')
    dirs = {str(parent) for path in expected for parent in Path(path).parents if str(parent) != '.'}
    need({r['path'] for r in actual['directories']} == dirs
         and all(r['mode'] == 0o700 for r in actual['directories']), 'external exact38 directories/modes')
    for row in actual['files']:
        want = expected[row['path']]
        need(row['bytes'] == want['bytes'] and row['sha256'] == want['sha256']
             and row['mode'] == want['mode'], 'external exact installed bytes/mode')
    return actual


def main():
    need(len(sys.argv) == 3, 'reviewed inventory and independent oracle SHA arguments required')
    inventory_sha, oracle_sha = sys.argv[1:]
    cold = HERE / 'cold-exact-v2'
    final = {'status': 'INCOMPLETE', 'runs': [], 'errors': [], 'claims': CLAIMS,
             'original_definitions_executed': False, 'costs': 'OPEN_NOT_ZERO'}
    terminal = False
    try:
        HERE.mkdir(mode=0o700, parents=False, exist_ok=True)
        need(HERE.is_dir() and not HERE.is_symlink(), 'ordinary reviewed output root')
        frozen_raw = (SOURCE / 'validation/EXECUTION-INVENTORY-v2.json').read_bytes()
        need(sha(frozen_raw) == inventory_sha, 'independently frozen inventory identity')
        frozen = json.loads(frozen_raw)
        entries = frozen['files']
        oracle_raw = (ROUND / 'review/INDEPENDENT-EXPECTED-OUTCOMES-v26-v1.json').read_bytes()
        need(sha(oracle_raw) == oracle_sha, 'independent oracle identity')
        oracle = json.loads(oracle_raw)
        need(oracle['case_count'] == 22, 'independent22 cases')
        checked_inventory(SOURCE, entries)
        plan = json.loads((SOURCE / 'controls/CONTROL-PLAN-v2.json').read_bytes())
        expected = [{'id': r['id'], 'outcome': r['expected']} for r in oracle['cases']]
        need(plan['cases'] == expected, 'independent ordered plan oracle')
        request = json.loads((SOURCE / 'payload/REQUEST-v2.json').read_bytes())['constructor_request']
        selection_raw = (SOURCE / 'payload/SELECTION-v2.json').read_bytes()
        compatibility_raw = (SOURCE / 'caller/CALLER-COMPATIBILITY-v2.json').read_bytes()
        need(sha(selection_raw) == request['selection_sha256']
             and sha(compatibility_raw) == request['compatibility_sha256'], 'actual compatibility and selection files')
        selection = json.loads(selection_raw)
        need(not cold.exists(), 'fresh cold destination no retry')
        cold.mkdir(mode=0o700)
        for row in entries:
            target = cold / row['path']
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(SOURCE / row['path'], target)
        checked_inventory(cold, entries, True)
        need(not (ROUND / 'proposed-runtime').exists(), 'runtime-owned paths remain absent')
        for mode in ('normal', 'optimized'):
            checked_inventory(SOURCE, entries)
            checked_inventory(cold, entries, True)
            parent = Path(selection['approved_preparation']['parents'][mode])
            need(parent == HERE / ('preparation-' + mode), 'reviewed concrete parent')
            parent.mkdir(mode=0o700, parents=False, exist_ok=False)
            fixtures = HERE / ('new-controls-' + mode)
            command = [sys.executable, '-B'] + (['-O'] if mode == 'optimized' else [])
            controls, observation = run_child(command + [str(cold / 'controls/full_proposal_controls.py'), str(fixtures), mode], cold, mode + '-controls')
            final['runs'].append(observation)
            need(controls == {'status': 'NEW_CONTROL_OBSERVATIONS_ONLY', 'controls': expected[1:],
                              'claims': CLAIMS, 'original_definitions_executed': False}, 'exact independent new-control oracle')
            child, observation = run_child(command + [str(cold / 'validation/full_prepare_child.py'), mode], cold, mode + '-prepare')
            final['runs'].append(observation)
            need(child == {'status': 'CHILD_FINISHED_INERT_PREPARATION_ONLY', 'mode': mode,
                          'installed_occurrences': 259, 'finish_succeeded': True,
                          'manifest_sha256': request['manifest_sha256'], 'claims': CLAIMS,
                          'original_definitions_executed': False}, 'exact full child finished oracle')
            def capture(state):
                checked_inventory(SOURCE, entries)
                checked_inventory(cold, entries, True)
                state['stage_inventory'] = verify_stage(parent / request['stage_name'], request['manifest'])
                need(not (ROUND / 'proposed-runtime').exists(), 'no runtime paths created')
            state = finalize_attempt(True, lambda state: None, capture,
                                     lambda state: retained_write(HERE / (mode + '.finalization-ledger.json'), state))
            final[mode + '_finalization'] = state
            need(state['status'] == 'COMPLETE_INERT_INSTALLATION_ONLY', 'external finalization incomplete')
        terminal = True
    except BaseException as error:
        final['errors'].append({'stage': 'internal', 'type': type(error).__name__, 'message': str(error)})
    finally:
        # This external layer runs even when internal postchecks are bypassed.
        for name, root in (('source', SOURCE), ('cold_copy', cold), ('outputs', HERE)):
            try:
                if name == 'source' and 'entries' in locals():
                    checked_inventory(root, entries)
                if name == 'cold_copy' and 'entries' in locals() and root.exists():
                    checked_inventory(root, entries, True)
                if name == 'outputs' and terminal:
                    for final_mode in ('normal', 'optimized'):
                        verify_stage(Path(selection['approved_preparation']['destinations'][final_mode]), request['manifest'])
                    need(not (ROUND / 'proposed-runtime').exists(), 'external runtime paths absent')
                final[name + '_final_inventory'] = inventory(root)
            except BaseException as error:
                terminal = False
                final['errors'].append({'stage': name + '_final_inventory', 'type': type(error).__name__, 'message': str(error)})
        final['status'] = 'COMPLETE_INERT_INSTALLATION_ONLY' if terminal and not final['errors'] else 'INCOMPLETE'
        try:
            retained_write(HERE / 'EXTERNAL-FINAL-v2.json', final)
            final['external_ledger_verified'] = True
        except BaseException as error:
            terminal = False
            final['status'] = 'INCOMPLETE'
            final['errors'].append({'stage': 'external_final_ledger', 'type': type(error).__name__, 'message': str(error)})
            try:
                retained_write(HERE / 'EXTERNAL-FINAL-FAILURE-v2.json', final)
            except BaseException as salvage_error:
                final['errors'].append({'stage': 'failure_ledger', 'type': type(salvage_error).__name__, 'message': str(salvage_error)})
    if terminal and not final['errors']:
        print(json.dumps({'status': 'COMPLETE_INERT_INSTALLATION_ONLY', 'unique_cases': 22,
                          'mode_observations': 44, 'claims': CLAIMS,
                          'original_definitions_executed': False}, sort_keys=True))
        return 0
    print(json.dumps({'status': 'INCOMPLETE', 'claims': CLAIMS,
                      'errors': final['errors'], 'original_definitions_executed': False}, sort_keys=True))
    return 1


if __name__ == '__main__':
    sys.exit(main())
