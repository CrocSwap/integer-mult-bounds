"""Inclusive observer/serialized admission. Final one-write tail remains OPEN_NOT_ZERO.

The first Python instruction starts the operation timer before other imports,
source authentication, staging, controls or target imports. Interpreter startup
before this instruction is additionally visible to an enclosing canonical guard;
never report it as zero or as a measured portion of this timer.
"""
import time
START = time.monotonic()
import resource
SELF_START = resource.getrusage(resource.RUSAGE_SELF)
CHILD_START = resource.getrusage(resource.RUSAGE_CHILDREN)
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import threading
sys.path.insert(0, str(Path(__file__).resolve().parent))
from custody import need, pin, read_json, safe, same, write_json

RSS_CAP = 1073741824
TIME_CAP = 180.0
INTERVAL = 0.01
LOG_CAP = 4 * 1024 * 1024


def process_table():
    result = {}
    for path in Path('/proc').iterdir():
        if not path.name.isdecimal():
            continue
        try:
            raw = (path / 'stat').read_text()
            row = raw[raw.rfind(')') + 2:].split()
            result[int(path.name)] = {'state': row[0], 'ppid': int(row[1]), 'pgrp': int(row[2]),
                                     'start_ticks': int(row[19]), 'rss_bytes': max(0, int(row[21])) * os.sysconf('SC_PAGE_SIZE')}
        except (OSError, ValueError, IndexError):
            continue
    return result


def sample_tree(root, known):
    table = process_table()
    members = {root} if root in table else set()
    changed = True
    while changed:
        added = {pid for pid, info in table.items() if info['ppid'] in members} - members
        changed = bool(added)
        members |= added
    # Keep previously seen identities even after reparenting; PID reuse is rejected.
    for pid, start in tuple(known.items()):
        if pid in table and table[pid]['start_ticks'] == start:
            members.add(pid)
    for pid in members:
        known[pid] = table[pid]['start_ticks']
    return sum(table[pid]['rss_bytes'] for pid in members), table, members


def terminate(process, known):
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    table = process_table()
    for pid, start in known.items():
        if pid != os.getpid() and pid in table and table[pid]['start_ticks'] == start:
            try:
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
    process.wait()


def observe(command, cwd, folder, deadline, rss_cap=RSS_CAP, interval=INTERVAL):
    """Observe current parent plus all discoverable descendants, including cleanup."""
    folder = Path(folder)
    folder.mkdir(mode=0o700)
    known, peak, samples, termination = {}, 0, 0, None
    start = time.monotonic()
    out_path, err_path = folder / 'stdout.txt', folder / 'stderr.txt'
    child = None
    old_handlers = {}
    signals = []
    def interrupted(signum, frame):
        signals.append(signum)
    for signum in (signal.SIGINT, signal.SIGTERM):
        old_handlers[signum] = signal.signal(signum, interrupted)
    try:
        with out_path.open('xb') as out, err_path.open('xb') as err:
            child = subprocess.Popen(command, cwd=cwd, stdin=subprocess.DEVNULL, stdout=out,
                                     stderr=err, start_new_session=True,
                                     env={'PATH': '/usr/bin:/bin', 'LC_ALL': 'C.UTF-8', 'TZ': 'UTC',
                                          'PYTHONDONTWRITEBYTECODE': '1'})
            while True:
                rss, table, members = sample_tree(os.getpid(), known)
                peak, samples = max(peak, rss), samples + 1
                if rss > rss_cap:
                    termination = 'sampled_tree_rss_cap'
                elif time.monotonic() > deadline:
                    termination = 'wall_or_aggregate_cap'
                elif signals:
                    termination = 'signal_' + str(signals[0])
                elif max(out_path.stat().st_size, err_path.stat().st_size) > LOG_CAP:
                    termination = 'retained_log_cap'
                code = child.poll()
                if termination is not None:
                    terminate(child, known)
                    code = child.returncode
                    break
                if code is not None:
                    break
                time.sleep(interval)
            # All known living descendants make this command fail, even if main returned0.
            rss, table, members = sample_tree(os.getpid(), known)
            peak, samples = max(peak, rss), samples + 1
            survivors = sorted(pid for pid in members if pid != os.getpid() and pid in table and table[pid]['state'] != 'Z')
            if survivors:
                termination = termination or 'surviving_descendants'
                terminate(child, known)
        logs = {'stdout': pin(out_path), 'stderr': pin(err_path)}
        need(all(v['size'] <= LOG_CAP for v in logs.values()), 'log cap on closing readback')
        return {'command': command, 'exit': code, 'termination': termination,
                'wall_seconds': time.monotonic() - start, 'sampled_simultaneous_tree_rss_bytes': peak,
                'samples': samples, 'interval_seconds': interval,
                'tracked_identities': {str(k): v for k, v in sorted(known.items())},
                'survivors_before_cleanup': survivors, 'logs': logs,
                'limits': {'rss_bytes': rss_cap, 'deadline_monotonic': deadline}}
    finally:
        if child is not None and child.poll() is None:
            terminate(child, known)
        for signum, handler in old_handlers.items():
            signal.signal(signum, handler)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--admission', required=True)
    parser.add_argument('--admission-sha256', required=True)
    args = parser.parse_args()
    # Observe parent authentication and closing checks too; target work is also
    # continuously sampled by this thread, independently of the foreground guard.
    stop_sampling, inclusive_known = threading.Event(), {}
    inclusive = {'peak': 0, 'samples': 0, 'errors': []}
    def sampler():
        while not stop_sampling.is_set():
            try:
                rss, _, _ = sample_tree(os.getpid(), inclusive_known)
                inclusive['peak'] = max(inclusive['peak'], rss)
                inclusive['samples'] += 1
            except BaseException as error:
                inclusive['errors'].append(type(error).__name__ + ': ' + str(error))
            stop_sampling.wait(INTERVAL)
    sampling_thread = threading.Thread(target=sampler, name='inclusive-rss-observer', daemon=True)
    sampling_thread.start()
    admission = read_json(Path(args.admission), args.admission_sha256)
    need(admission['schema'] == 'o03-envelope-admission-v1', 'admission schema')
    need(admission['independent_source_accepted'] is True and admission['parent_execution_admitted'] is True,
         'explicit independent source and parent admission required')
    need(admission['maximum_command_seconds'] == TIME_CAP and admission['sampled_group_cap_bytes'] == RSS_CAP,
         'caps differ')
    ledger = admission['canonical_ledger']
    need(ledger['cap_seconds'] == 2400 and 0 <= ledger['spent_seconds'] < 2400, 'canonical budget invalid')
    lock_path = safe(Path(ledger['lock_path']))
    with lock_path.open('a+b') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        for filename, expected in ledger['fresh_files'].items():
            same(Path(filename), expected)
        # Consume before source checks/staging so failures cannot reroll this fixed operation.
        consumed = Path(admission['consumed_marker'])
        with consumed.open('xb') as marker:
            marker.write((args.admission_sha256 + '\n').encode('ascii'))
            marker.flush()
            os.fsync(marker.fileno())
        folder = safe(Path(admission['operation_root']))
        folder.mkdir(mode=0o700)
        record = {'schema': 'o03-inclusive-observer-v1', 'status': 'STARTED',
                  'admission_sha256': args.admission_sha256, 'errors': [],
                  'outside_tail': {'final_observer_record_writes': 1, 'parent_readbacks': 1,
                                   'cost': 'OPEN_NOT_ZERO', 'publication': 'OPEN_NOT_ZERO'},
                  'measurement': {'sampled_rss': 'simultaneous observer parent plus discoverable descendants',
                    'limitations': '10ms sampling can miss short peaks/processes; PID start ticks prevent reuse conflation; an unseen reparented/escaped process can be missed; proc RSS includes shared pages per process; no exact true peak claim',
                    'cpu': 'entire fresh observer lifetime SELF plus reaped-children rusage; child usage includes descendants reaped by their parents; no summing sampled CPU',
                    'individual_maxrss': 'kernel SELF and CHILDREN maxima are separate individual process high water marks; never summed as concurrent peak',
                    'interpreter_startup': 'before first Python instruction is measured only by enclosing canonical guard; OPEN_NOT_ZERO otherwise',
                    'cgroup_peak': 'NOT_COLLECTED; no cgroup isolation/peak claim'}}
        try:
            need(admission['operation'] in admission['fixed_order'], 'undeclared operation')
            index = admission['fixed_order'].index(admission['operation'])
            need(len(set(admission['fixed_order'])) == len(admission['fixed_order']), 'duplicate operation labels')
            if index:
                previous = read_json(Path(admission['previous_observer_receipt']), admission['previous_observer_sha256'])
                need(previous['status'] == 'PASS' and previous['operation'] == admission['fixed_order'][index - 1], 'fixed predecessor missing/failed')
            for filename, expected in admission['envelope_source_files'].items():
                same(Path(filename), expected)
            from bootstrap import closure
            from effective import capture, unchanged
            runtime = read_json(Path(admission['runtime_manifest']), admission['runtime_sha256'])
            import importlib
            for filename, expected in runtime['files'].items():
                same(Path(filename), expected)
            for name in runtime['preload_modules']:
                importlib.import_module(name)
            record['observer_runtime_before'], observer_objects = closure(runtime, Path(__file__).resolve().parent.parent,
                Path(__file__).resolve(), main_path=Path(__file__).resolve())
            effective_before = capture(dict(sys.modules))
            record['effective_before'] = effective_before
            worker = Path(admission['worker'])
            need(str(worker) in admission['envelope_source_files'], 'worker source unsealed')
            command = [admission['interpreter'], '-B', '-I', '-S', str(worker), '--admission',
                       str(Path(args.admission)), '--admission-sha256', args.admission_sha256]
            remaining = ledger['cap_seconds'] - ledger['spent_seconds']
            record['execution'] = observe(command, str(folder), folder / 'guard',
                                           START + min(TIME_CAP, remaining))
            need(record['execution']['exit'] == 0 and record['execution']['termination'] is None,
                 'worker/guard failure')
            need(record['execution']['logs']['stderr']['size'] == 0, 'worker stderr')
            worker_receipt = read_json(folder / 'worker-receipt.json')
            need(worker_receipt['status'] == 'PASS', 'worker receipt failure')
            record['worker_receipt'] = pin(folder / 'worker-receipt.json')
            for filename, expected in admission['envelope_source_files'].items():
                same(Path(filename), expected)
            for filename, expected in ledger['fresh_files'].items():
                same(Path(filename), expected)
        except BaseException as error:
            record['errors'].append({'type': type(error).__name__, 'message': str(error)})
        try:
            record['observer_runtime_after'], after_objects = closure(runtime, Path(__file__).resolve().parent.parent,
                Path(__file__).resolve(), main_path=Path(__file__).resolve())
            need(all(after_objects[k] is v for k, v in observer_objects.items()), 'observer callable drift')
            record['effective_after'] = capture(dict(sys.modules))
            unchanged(effective_before, record['effective_after'])
        except BaseException as error:
            record['errors'].append({'check': 'observer-runtime-after', 'type': type(error).__name__, 'message': str(error)})
        try:
            for filename, expected in admission['envelope_source_files'].items():
                same(Path(filename), expected)
            for filename, expected in ledger['fresh_files'].items():
                same(Path(filename), expected)
        except BaseException as error:
            record['errors'].append({'check': 'closing-source-ledger', 'type': type(error).__name__, 'message': str(error)})
        stop_sampling.set()
        sampling_thread.join()
        record['inclusive_sampled_simultaneous_tree_rss_bytes'] = inclusive['peak']
        record['inclusive_samples'] = inclusive['samples']
        record['inclusive_sampler_errors'] = inclusive['errors']
        if inclusive['peak'] > RSS_CAP or inclusive['errors']:
            record['errors'].append({'type': 'SamplerFailure', 'message': 'inclusive cap/sampler failure'})
        record['cpu_accounting'] = ('COMPLETE_FOR_SOURCE_FIXED_REAPED_SUCCESS_TREE' if not record['errors'] else
                                    'FAILED_ATTEMPT_REAPING_OR_KILL_GAPS_OPEN_NOT_ZERO')
        record['operation'] = admission['operation']
        self_end, child_end = resource.getrusage(resource.RUSAGE_SELF), resource.getrusage(resource.RUSAGE_CHILDREN)
        record['cpu_seconds'] = {'parent_user': self_end.ru_utime,
            'parent_system': self_end.ru_stime,
            'reaped_children_user': child_end.ru_utime,
            'reaped_children_system': child_end.ru_stime}
        record['kernel_individual_maxrss_kib'] = {'observer_self_lifetime': self_end.ru_maxrss,
                                                 'reaped_children_individual_maximum': child_end.ru_maxrss}
        record['inclusive_wall_seconds'] = time.monotonic() - START
        record['policy_charge_seconds'] = record['inclusive_wall_seconds']
        if record['inclusive_wall_seconds'] > min(TIME_CAP, 2400 - ledger['spent_seconds']):
            record['errors'].append({'type': 'CapFailure', 'message': 'closing checks exceeded cap'})
        record['status'] = 'PASS' if not record['errors'] else 'STOP'
        # The finite final write and exactly one parent readback are outside above endpoint.
        write_json(folder / 'observer-receipt.json', record)
    if record['status'] != 'PASS':
        raise SystemExit(1)


if __name__ == '__main__':
    main()
