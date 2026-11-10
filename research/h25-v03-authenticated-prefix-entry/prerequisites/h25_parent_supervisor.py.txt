"""Parent-only bounded process supervision; imports no candidate implementation.

The runtime caller must establish the trusted clean launcher before calling us.
This source was prepared without loading ctypes or running any control.  The
closed single-threaded child domain is an explicit premise, not a hostile-fork
sandbox.  Numeric process IDs are never used as signal destinations.
"""
import fcntl
import hashlib
import json
import os
from pathlib import Path
import resource
import signal
import stat
import subprocess
import sys
import time

FLAGS = ('-S', '-s', '-P', '-B')
ENV = {'PATH': '/usr/bin:/bin', 'PYTHONHASHSEED': '0', 'LANG': 'C.UTF-8',
       'LC_ALL': 'C.UTF-8', 'TZ': 'UTC', 'PYTHONDONTWRITEBYTECODE': '1'}
RUNNER_SHA = 'bd882e3dadb1b6aeaa63ee824f1a1c58f8ef2546b6840a2bffa46885a184d3eb'
QUEUE_SHA = '1348a7b4d7cc1f9fef556f5e0abdaf04411a998afdcd574d7812c76ab37dcf68'
TCB_SHA = '610492b3fc06baa0560175edc3ba27057de00d00b8fd3d58dbe55e5a371c042a'
LIBC = '/usr/lib/x86_64-linux-gnu/libc.so.6'
NATIVE_PINS = {
    LIBC: '3a15d66867d83762c7f2f1e37359cb8f6c5743edb369c65285cb0b1c4f7498bf',
    '/usr/lib/python3.12/lib-dynload/_ctypes.cpython-312-x86_64-linux-gnu.so': 'aad3e24f186e6c0a1c7efa8f16004f951f527db86f6451d30118657384a456c1',
    '/usr/lib/x86_64-linux-gnu/libffi.so.8.1.4': '00f593fe192f2851b8ce23b25cec2488d769beb5a8f63e8c9e563071e1075153',
    '/usr/lib/python3.12/ctypes/__init__.py': '0782592567ad71097198a3afe985ac3e2ea0b9b5e75452402c9460c89a86318a',
    '/usr/lib/python3.12/ctypes/_endian.py': 'c5d692bdce10dfee242752620061bab684633bc72445a3def484961ef1bdbf3a',
}
CHUNK = 65536
LOG_CAP = 2 * 1024 * 1024
META_CAP = 256 * 1024
CLEANUP_SECONDS = 2.0


def need(condition, message):
    if not condition:
        raise RuntimeError(message)


def launch_contract():
    need(sys.executable == '/usr/bin/python3.12', 'Pinned interpreter required')
    need(sys.flags.no_site == sys.flags.no_user_site == sys.flags.dont_write_bytecode == 1 and
         sys.flags.safe_path and sys.flags.ignore_environment == sys.flags.isolated ==
         sys.flags.hash_randomization == 0, 'Trusted no-site safe-path fixed-seed flags required')
    need(dict(os.environ) == ENV, 'Exact clean environment required')
    need(tuple(sys.path) == ('/usr/lib/python312.zip', '/usr/lib/python3.12',
                            '/usr/lib/python3.12/lib-dynload'), 'Initial system stdlib path changed')
    need(list(Path('/proc/self/task').iterdir()) == [Path('/proc/self/task') / str(os.getpid())],
         'Exactly one parent task required')


def identity(info):
    return (info.st_dev, info.st_ino, info.st_mode, info.st_size, info.st_mtime_ns, info.st_ctime_ns)


def stable_file(path, limit, keep=False):
    """Complete bounded snapshot; no file read can extend a growing snapshot."""
    path = Path(path)
    before = path.stat(follow_symlinks=False)
    need(stat.S_ISREG(before.st_mode) and before.st_size <= limit, 'File type/size bound: ' + str(path))
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC)
    h, count, blocks = hashlib.sha256(), 0, []
    try:
        opened = os.fstat(fd)
        need(identity(before) == identity(opened), 'File changed while opening')
        while count < opened.st_size:
            block = os.read(fd, min(CHUNK, opened.st_size - count))
            need(bool(block), 'Short retained-file read')
            count += len(block)
            h.update(block)
            if keep:
                blocks.append(block)
        after_fd = os.fstat(fd)
    finally:
        os.close(fd)
    after = path.stat(follow_symlinks=False)
    need(identity(before) == identity(after_fd) == identity(after), 'File drift during retained snapshot')
    row = {'path': str(path), 'sha256': h.hexdigest(), 'bytes': count,
           'identity': list(identity(after)), 'stable': True, 'read_chunk_bytes': CHUNK}
    return (row, b''.join(blocks)) if keep else row


def read_json(path, limit=META_CAP):
    row, raw = stable_file(path, limit, True)
    return json.loads(raw), row


def write_new(path, row):
    raw = json.dumps(row, sort_keys=True, indent=2).encode('ascii') + b'\n'
    need(len(raw) <= META_CAP, 'Bounded metadata record exceeded')
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_CLOEXEC | os.O_NOFOLLOW, 0o600)
    try:
        view = memoryview(raw)
        while view:
            written = os.write(fd, view)
            need(written > 0, 'Metadata write made no progress')
            view = view[written:]
        os.fsync(fd)
    finally:
        os.close(fd)


def proc(pid):
    try:
        with open('/proc/' + str(pid) + '/stat', 'rb') as stream:
            raw = stream.read(8193)
        need(len(raw) <= 8192, 'Unexpected process-stat size')
        end = raw.rfind(b') ')
        need(end >= 0, 'Malformed process stat')
        fields = raw[end + 2:].split()
        return {'pid': int(pid), 'ppid': int(fields[1]), 'pgid': int(fields[2]),
                'sid': int(fields[3]), 'start_ticks': int(fields[19]),
                'state': fields[0].decode('ascii'),
                'rss_bytes': int(fields[21]) * os.sysconf('SC_PAGE_SIZE')}
    except (FileNotFoundError, ProcessLookupError, PermissionError):
        return None


def census():
    found = {}
    with os.scandir('/proc') as entries:
        for entry in entries:
            if entry.name.isdecimal():
                row = proc(int(entry.name))
                if row is not None:
                    found[row['pid']] = row
    return found


def generation(row):
    return row['pid'], row['start_ticks']


def children_now():
    return [row for row in census().values() if row['ppid'] == os.getpid()]


def install_subreaper(root):
    """Called only by the future parent, before any controlled root exists."""
    launch_contract()
    need(not children_now(), 'Parent must own no preexisting child processes')
    tcb, tcb_row = read_json(root / 'control/NATIVE-INITIAL-TCB-v1.json')
    need(tcb_row['sha256'] == TCB_SHA, 'Accepted initial TCB changed')
    need(any(row['path'] == LIBC and row['sha256'] == NATIVE_PINS[LIBC]
             for row in tcb['files']), 'Pinned libc absent from accepted TCB')
    evidence = {path: stable_file(path, 16 * 1024 * 1024) for path in NATIVE_PINS}
    need(all(evidence[path]['sha256'] == expected for path, expected in NATIVE_PINS.items()),
         'Subreaper native/stdlib source supplement changed')
    # This import and native call have NOT been performed during source authoring.
    need(Path('/usr/lib/x86_64-linux-gnu/libffi.so.8').resolve() ==
         Path('/usr/lib/x86_64-linux-gnu/libffi.so.8.1.4'), 'Foreign libffi SONAME resolution')
    import ctypes
    need(sys.modules['_ctypes'].__file__ ==
         '/usr/lib/python3.12/lib-dynload/_ctypes.cpython-312-x86_64-linux-gnu.so', 'Foreign _ctypes owner')
    need(ctypes.__file__ == '/usr/lib/python3.12/ctypes/__init__.py', 'Foreign ctypes owner')
    library = ctypes.CDLL(LIBC, use_errno=True)
    call = library.prctl
    call.argtypes = [ctypes.c_int, ctypes.c_ulong, ctypes.c_ulong, ctypes.c_ulong, ctypes.c_ulong]
    call.restype = ctypes.c_int
    prior, actual = ctypes.c_int(), ctypes.c_int()
    need(call(37, ctypes.addressof(prior), 0, 0, 0) == 0, 'PR_GET_CHILD_SUBREAPER failed')
    need(call(36, 1, 0, 0, 0) == 0, 'PR_SET_CHILD_SUBREAPER failed')
    need(call(37, ctypes.addressof(actual), 0, 0, 0) == 0 and actual.value == 1,
         'Same-process subreaper readback failed')
    for path, expected in NATIVE_PINS.items():
        need(stable_file(path, 16 * 1024 * 1024)['sha256'] == expected, 'TCB bytes changed across load')
    # Retain the CDLL and typed function in the owning parent for its whole queue.
    return {'pid': os.getpid(), 'prior': prior.value, 'actual': actual.value,
            'tcb_sha256': TCB_SHA, 'native_source_evidence': evidence,
            'trust': 'Trusted OS/loader/initial system stdlib; file pins do not authenticate native memory'}, (library, call)


def ledger(root, allow_unclosed=False):
    result = {}
    runs = root / 'runtime/runs'
    for folder in sorted(runs.iterdir()):
        need(folder.is_dir() and not folder.is_symlink(), 'Unexpected round run entry')
        if allow_unclosed and not (folder / 'receipt.json').exists():
            continue
        receipt, _ = read_json(folder / 'receipt.json', 4 * 1024 * 1024)
        amount = receipt.get('runner_wall_seconds', receipt.get('wall_seconds'))
        need(type(amount) in (int, float) and amount >= 0, 'Invalid ledger amount')
        result[folder.name] = float(amount)
    return result


def budget(root):
    phase, _ = read_json(root / 'control/EXECUTION-PHASE.json')
    cap = phase['aggregate_cap_seconds']
    need(type(cap) is int and cap in (600, 2400), 'Unrecognized budget phase')
    current = ledger(root)
    need(sum(current.values()) < cap, 'Round budget consumed')
    return cap, current


def parent_lock(root):
    lock = (root / 'runtime/parent-queue.lock').open('a')
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BaseException:
        lock.close()
        raise
    return lock


class ExecutionDeadline(RuntimeError):
    pass


def deadline_handler(signum, frame):
    raise ExecutionDeadline('Outer execution deadline reached, including Popen/preexec')


class OwnedDomain:
    """Only our new children and their observed descendants enter this domain."""
    def __init__(self):
        need(not children_now(), 'Owned child domain was not initially empty')
        self.rows, self.fds, self.groups, self.reaped = {}, {}, set(), []
        self.root = None
        self.parent_group = os.getpgrp()
        self.parent_session = os.getsid(0)

    def add(self, row):
        key = generation(row)
        if key in self.rows:
            if row['pgid'] != self.parent_group:
                self.groups.add((row['pgid'], row['sid']))
            return
        need(len(self.rows) < 128, 'Owned process observation limit exceeded')
        need(row['pid'] != os.getpid(), 'Parent cannot enter its own child domain')
        try:
            fd = os.pidfd_open(row['pid'], 0)
        except ProcessLookupError:
            return
        current = proc(row['pid'])
        if current is None or generation(current) != key:
            os.close(fd)
            return
        self.rows[key], self.fds[key] = dict(current), fd
        # During interrupted Popen a child can briefly precede setsid. Its
        # individual pidfd is owned; the queue parent group never is.
        if current['pgid'] != self.parent_group:
            self.groups.add((current['pgid'], current['sid']))

    def observe(self):
        all_rows = census()
        known = {pid for pid, start in self.rows if pid in all_rows and
                 all_rows[pid]['start_ticks'] == start}
        for pid in known:
            self.add(all_rows[pid])
        changed = True
        while changed:
            changed = False
            for pid, row in all_rows.items():
                if pid not in known and (row['ppid'] == os.getpid() or row['ppid'] in known):
                    self.add(row)
                    if generation(row) in self.rows:
                        known.add(pid)
                        changed = True
        return all_rows, [all_rows[pid] for pid in known]

    def kill_owned(self):
        self.observe()
        for key, fd in self.fds.items():
            current = proc(key[0])
            if current is not None and generation(current) == key and current['state'] != 'Z':
                try:
                    signal.pidfd_send_signal(fd, signal.SIGKILL, None, 0)
                except ProcessLookupError:
                    pass

    def cleanup(self, process):
        start = time.monotonic()
        seen_after_root = []
        completed = False
        while True:
            _, current = self.observe()
            if process is not None and process.returncode is not None:
                seen_after_root.extend(generation(row) for row in current if row['pid'] != process.pid)
            self.kill_owned()
            if process is not None:
                process.poll()
            for key in list(self.rows):
                row = proc(key[0])
                if row is None or generation(row) != key or row['ppid'] != os.getpid():
                    continue
                if process is not None and row['pid'] == process.pid:
                    continue
                try:
                    pid, status = os.waitpid(row['pid'], os.WNOHANG)
                except ChildProcessError:
                    continue
                if pid:
                    self.reaped.append({'pid': pid, 'start_ticks': key[1], 'wait_status': status})
            all_rows, current = self.observe()
            occupied = [row for row in all_rows.values() if (row['pgid'], row['sid']) in self.groups]
            if not current and not occupied and not children_now():
                completed = True
                break
            if time.monotonic() - start >= CLEANUP_SECONDS:
                break
            time.sleep(0.01)
        final_rows = census()
        remaining = [row for row in final_rows.values() if
                     generation(row) in self.rows or (row['pgid'], row['sid']) in self.groups or
                     row['ppid'] == os.getpid()]
        for fd in self.fds.values():
            os.close(fd)
        self.fds.clear()
        return {'complete': completed and not remaining,
                'owned_generations': list(self.rows.values()),
                'groups': [{'pgid': g, 'sid': s} for g, s in sorted(self.groups)],
                'reaped_adopted': self.reaped,
                'observed_after_root_exit': [list(key) for key in sorted(set(seen_after_root))],
                'remaining': remaining, 'cleanup_seconds': time.monotonic() - start,
                'cleanup_tail_limit_seconds': CLEANUP_SECONDS,
                'group_empty_proved': completed and not remaining,
                'signal_method': 'SIGKILL via generation-checked pidfd only; never killpg'}


def reconcile_missing_receipt(root, label, began, cause, cleanup):
    folder = root / 'runtime/runs' / label
    folder.mkdir(exist_ok=True)
    if not cleanup['complete'] and not (folder / 'receipt.json').exists():
        # A surviving root must never race a replacement canonical receipt.
        # Leave its attempt unclosed, blocking the unchanged runner, and add a
        # distinct charged STOP record for the parent to reconcile manually.
        folder = root / 'runtime/runs' / (label + '-outer-unclosed-stop')
        folder.mkdir()
    path = folder / 'receipt.json'
    if path.exists():
        return None
    start = {}
    if (folder / 'START.json').exists():
        start, _ = read_json(folder / 'START.json')
    row = dict(start, schema='h25-outer-reconciled-stop-v1', status='STOP', label=label,
               kind='outer_reconciled_incomplete_root', termination=cause, attempt_label=label,
               wall_seconds=time.monotonic() - began, original_root_receipt_absent=True,
               original_root_completion_claimed=False, cleanup_complete=cleanup['complete'],
               all_prior_files_preserved=True)
    row['label'] = folder.name
    row['runner_wall_seconds'] = row['wall_seconds']
    if not (folder / 'START.json').exists():
        write_new(folder / 'START.json', {'kind': row['kind'], 'label': label})
    write_new(path, row)
    return row


def run_root(root, case, evidence, seconds, shared_deadline, as_bytes=201326592,
             rss_bytes=201326592):
    """One root. Cleanup and stable custody finish before returning to a queue."""
    launch_contract()
    need(stable_file(root / 'run_guarded_v3.py', META_CAP)['sha256'] == RUNNER_SHA,
         'Actual root runner changed')
    need(time.monotonic() + CLEANUP_SECONDS < shared_deadline, 'No reserved cleanup tail remains')
    command = ['/usr/bin/python3.12', *FLAGS, str(root / 'run_guarded_v3.py'),
               case['stage'], case['job'], case['label']]
    for value in (case['stage'], case['job'], case['label']):
        need(type(value) is str and value and all(c in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_' for c in value),
             'Unsafe case identity')
    evidence.mkdir()
    need(type(seconds) in (int, float) and 0 < seconds <= 190, 'Unadmitted root deadline')
    need(type(as_bytes) is int and 0 < as_bytes <= 1024 ** 3, 'Unadmitted root address-space bound')
    need(type(rss_bytes) is int and 0 < rss_bytes <= 1024 ** 3, 'Unadmitted aggregate RSS bound')
    began = time.monotonic()
    deadline = min(began + seconds, shared_deadline - CLEANUP_SECONDS)
    domain = OwnedDomain()
    process, failure, cleanup = None, None, None
    peak, spawn_entered, captured = 0, False, None
    setter, limit_kind, limits = resource.setrlimit, resource.RLIMIT_AS, (as_bytes, as_bytes)
    need(list(Path('/proc/self/task').iterdir()) == [Path('/proc/self/task') / str(os.getpid())],
         'Root preexec requires exactly one task')
    def child_limit():
        setter(limit_kind, limits)
    old_handler = signal.getsignal(signal.SIGALRM)
    need(signal.getitimer(signal.ITIMER_REAL) == (0.0, 0.0), 'Parent already has an execution alarm')
    write_new(evidence / 'LAUNCH.json', {'command': command, 'parent_pid': os.getpid(),
              'parent_pgid': os.getpgrp(), 'parent_sid': os.getsid(0),
              'root_execution_seconds': seconds, 'address_space_bytes': as_bytes,
              'rss_sum_bytes': rss_bytes, 'new_session': True, 'cleanup_reserved_seconds': CLEANUP_SECONDS})
    try:
        with (evidence / 'root.stdout.raw').open('xb') as out, (evidence / 'root.stderr.raw').open('xb') as err:
            signal.signal(signal.SIGALRM, deadline_handler)
            signal.setitimer(signal.ITIMER_REAL, max(0.000001, deadline - time.monotonic()))
            try:
                spawn_entered = True
                process = subprocess.Popen(command, cwd=root, env=dict(ENV), stdout=out,
                                           stderr=err, start_new_session=True, preexec_fn=child_limit)
                # Popen leaves an exited root waitable; capture its generation BEFORE poll.
                captured = proc(process.pid)
                need(captured is not None and captured['pgid'] == captured['sid'] == process.pid,
                     'New root process/session identity missing')
                domain.root = generation(captured)
                domain.add(captured)
                write_new(evidence / 'ROOT-PROCESS.json', captured)
                while True:
                    _, current = domain.observe()
                    peak = max(peak, sum(row['rss_bytes'] for row in current))
                    need(peak <= rss_bytes, 'Owned process RSS sum exceeded')
                    need(max((evidence / name).stat().st_size for name in
                             ('root.stdout.raw', 'root.stderr.raw')) <= LOG_CAP, 'Outer raw log cap exceeded')
                    if process.poll() is not None:
                        break
                    time.sleep(0.01)
            finally:
                signal.setitimer(signal.ITIMER_REAL, 0)
                signal.signal(signal.SIGALRM, old_handler)
    except BaseException as error:
        failure = {'type': type(error).__name__, 'message': str(error)[:2048]}
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, old_handler)
        # This is also required when Popen raised before returning an object.
        try:
            cleanup = domain.cleanup(process)
        except BaseException as cleanup_error:
            cleanup = {'complete': False, 'group_empty_proved': False,
                       'owned_generations': list(domain.rows.values()),
                       'groups': [{'pgid': g, 'sid': sid} for g, sid in sorted(domain.groups)],
                       'reaped_adopted': domain.reaped, 'observed_after_root_exit': [],
                       'remaining': 'UNKNOWN_AFTER_CLEANUP_ERROR',
                       'error': {'type': type(cleanup_error).__name__, 'message': str(cleanup_error)[:2048]}}
            for fd in domain.fds.values():
                os.close(fd)
            domain.fds.clear()
    if not cleanup['complete']:
        failure = failure or {'type': 'CleanupIncomplete', 'message': 'Owned descendants/group remain after bounded cleanup tail'}
    if time.monotonic() > shared_deadline:
        failure = failure or {'type': 'SharedDeadline', 'message': 'Shared cap crossed; necessary cleanup charged'}
    reconciled = reconcile_missing_receipt(root, case['label'], began,
                  failure or {'type': 'MissingRootReceipt', 'message': 'Root exited without receipt'}, cleanup)
    if reconciled is not None:
        failure = failure or {'type': 'MissingRootReceipt', 'message': 'New reconciled STOP receipt; no retry'}
    logs = {}
    for name in ('root.stdout.raw', 'root.stderr.raw'):
        try:
            logs[name] = stable_file(evidence / name, LOG_CAP)
        except BaseException as error:
            failure = failure or {'type': type(error).__name__, 'message': str(error)[:2048]}
            logs[name] = {'path': str(evidence / name), 'complete_hash': None, 'stable': False}
    result = {'schema': 'h25-parent-root-supervision-v1', 'label': case['label'],
              'status': 'STOP' if failure else 'ROOT_COMPLETED_AND_OWNED_DOMAIN_EMPTY',
              'failure': failure, 'spawn_entered': spawn_entered,
              'spawn_returned': process is not None, 'captured_root': captured,
              'returncode': None if process is None else process.returncode,
              'cleanup': cleanup, 'outer_logs': logs, 'sampled_owned_rss_bytes': peak,
              'execution_and_cleanup_seconds': time.monotonic() - began,
              'root_receipt_reconciled': reconciled is not None,
              'no_hostile_fork_or_concurrent_children_claim': True}
    write_new(evidence / 'SUPERVISION.json', result)
    return result


def stop_supplement(root, label, reason):
    folder = root / 'runtime/runs' / (label + '-supervision-stop')
    folder.mkdir()
    row = {'status': 'STOP', 'label': folder.name, 'kind': 'supervision_failure_marker',
           'failure': reason, 'wall_seconds': 0.0, 'runner_wall_seconds': 0.0,
           'cost_accounted_by_enclosing_queue_overhead': True, 'original_receipts_preserved': True}
    write_new(folder / 'START.json', {'kind': row['kind']})
    write_new(folder / 'receipt.json', row)


def packet_unchanged(directory, manifest):
    for name, expected in manifest['files'].items():
        row = stable_file(directory / name, META_CAP)
        need(row['sha256'] == expected['sha256'] and row['bytes'] == expected['bytes'],
             'Parent source packet changed: ' + name)
        need(not (directory / name).stat().st_mode & 0o222, 'Parent source packet became writable')
    return True
