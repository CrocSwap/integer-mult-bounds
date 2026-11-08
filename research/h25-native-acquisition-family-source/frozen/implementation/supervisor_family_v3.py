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


# Additive V2 before-target guard. The admitted single-writer/no-mutator startup
# premise is inherited; these files are not a hostile-child authentication claim.
GUARD_CAP = 1048576
MARKER_CAP = 1048576
_GUARD_ATTEMPTS = []


def _guard_exact(value, keys):
    need(type(value) is dict and all(type(k) is str for k in value) and
         set(value) == set(keys), 'Guard exact native keys differ')


def _guard_bytes(value):
    raw = json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True, allow_nan=False).encode('ascii') + b'\n'
    need(len(raw) <= GUARD_CAP, 'Guard complete packet exceeds bounded channel')
    return raw


def _guard_digest(value):
    need(type(value) is str and len(value) == 64 and
         all(c in '0123456789abcdef' for c in value), 'Guard exact digest differs')


def _guard_path(value):
    need(type(value) is str and value.startswith('/') and len(value) <= 4096 and
         all(c not in ('', '.', '..') for c in value.split('/')[1:]), 'Guard absolute path differs')
    cursor = Path('/')
    for component in Path(value).parts[1:-1]:
        cursor = cursor / component
        info = cursor.stat(follow_symlinks=False)
        need(stat.S_ISDIR(info.st_mode), 'Guard parent path is not a genuine directory')


def _guard_generation(row):
    _guard_exact(row, ('pid', 'start_ticks'))
    need(all(type(row[k]) is int and 0 < row[k] and row[k].bit_length() <= 128 for k in row), 'Guard generation exact integers required')


def _guard_leaf(row):
    _guard_exact(row, ('pid', 'ppid', 'pgid', 'sid', 'start_ticks'))
    need(all(type(row[k]) is int and 0 < row[k] and row[k].bit_length() <= 128 for k in row), 'Guard leaf exact integers required')


def _guard_source(pin):
    _guard_exact(pin, ('path', 'sha256', 'bytes'))
    _guard_path(pin['path']); _guard_digest(pin['sha256'])
    need(type(pin['bytes']) is int and 0 <= pin['bytes'] <= 8388608, 'Guard complete source bound')
    row = stable_file(pin['path'], 8388608)
    need(row['sha256'] == pin['sha256'] and row['bytes'] == pin['bytes'] and
         not row['identity'][2] & 0o222, 'Guard immutable exact source changed')


def _guard_binding(binding):
    _guard_exact(binding, ('case_id', 'context_id', 'unit_id', 'mode', 'action_id', 'generation',
        'nonce', 'parent_generation', 'component_source', 'entry_source', 'supervisor_source',
        'context_sha256', 'marker_path', 'request_path', 'ack_path', 'consume_path', 'timeout_milliseconds'))
    for key in ('case_id', 'context_id', 'unit_id', 'action_id', 'generation'):
        need(type(binding[key]) is str and 0 < len(binding[key]) <= 256, 'Guard declared identity differs')
    need(type(binding['mode']) is str and binding['mode'] in ('normal', 'optimized'), 'Guard declared mode differs')
    for key in ('nonce', 'context_sha256'):
        _guard_digest(binding[key])
    _guard_generation(binding['parent_generation'])
    need(type(binding['timeout_milliseconds']) is int and 1 <= binding['timeout_milliseconds'] <= 180000,
         'Guard deadline allocation differs')
    for key in ('marker_path', 'request_path', 'ack_path', 'consume_path'):
        _guard_path(binding[key])
    paths = [binding[k] for k in ('marker_path','request_path','ack_path','consume_path')]
    paths += [binding[k] + '.pending' for k in ('request_path','ack_path','consume_path')]
    need(len(set(paths)) == len(paths), 'Guard channel/marker path reused')
    for key in ('component_source','entry_source','supervisor_source'):
        _guard_source(binding[key])
    need(binding['supervisor_source']['path'] == __file__, 'Actual guard supervisor source origin differs')
    _guard_bytes(binding)


def _guard_read(path):
    before=os.stat(path,follow_symlinks=False)
    need(before.st_nlink==1,'Guard final custody requires one link')
    pin, raw = stable_file(path, GUARD_CAP, True)
    after=os.stat(path,follow_symlinks=False)
    need(after.st_nlink==1 and identity(before)==identity(after),'Guard single-link custody changed during read')
    value = json.loads(raw)
    need(_guard_bytes(value) == raw and not pin['identity'][2] & 0o222,
         'Guard complete canonical immutable packet required')
    return value, pin


_PUBLICATION_BINDING = [None]


def prepare_atomic_publication(root, admission):
    """Before-capture initialization by the externally authenticated caller.

    Input digests do not create authority. The actual caller must bind this
    exact source/ABI/native profile and grant the operation before invoking it.
    No native call or import occurred while authoring this source.
    """
    need(_PUBLICATION_BINDING[0] is None, 'Atomic publication initializer already consumed')
    state={'phase':'PREPARING','primary':[None],'secondary':[],'pid':os.getpid(),
           'library':None,'library_entered':False,'library_returned':False,
           'call':None,'call_binding_entered':False,'call_binding_returned':False}
    _PUBLICATION_BINDING[0]=state  # no retry after any partial load/binding
    try:
        launch_contract()
        need(not _GUARD_ATTEMPTS,'Publication binding must precede every guard attempt')
        _guard_exact(admission, ('schema','source_sha256','source_review_sha256','primitive_review_sha256',
            'kernel_profile_sha256','runtime_premise_sha256','command_approval_sha256','funding_sha256'))
        need(admission['schema']=='h25-exclusive-single-link-publication-admission-v1', 'Publication admission shape differs')
        for name in admission:
            if name!='schema':
                _guard_digest(admission[name])
        need(stable_file(__file__,8388608)['sha256']==admission['source_sha256'], 'Actual publication source differs')
        tcb,tcb_pin=read_json(Path(root)/'control/NATIVE-INITIAL-TCB-v1.json')
        need(tcb_pin['sha256']==TCB_SHA and any(r['path']==LIBC and r['sha256']==NATIVE_PINS[LIBC]
             for r in tcb['files']), 'Publication original native premise differs')
        source_evidence={name:stable_file(name,16*1024*1024) for name in NATIVE_PINS}
        need(all(source_evidence[name]['sha256']==expected for name,expected in NATIVE_PINS.items()),
             'Publication libc/ctypes/libffi source supplement differs')
        need(Path('/usr/lib/x86_64-linux-gnu/libffi.so.8').resolve()==
             Path('/usr/lib/x86_64-linux-gnu/libffi.so.8.1.4'), 'Publication libffi SONAME differs')
        import ctypes
        need(ctypes.__file__=='/usr/lib/python3.12/ctypes/__init__.py' and
             sys.modules['_ctypes'].__file__=='/usr/lib/python3.12/lib-dynload/_ctypes.cpython-312-x86_64-linux-gnu.so',
             'Publication ctypes owners differ')
        state['module']=ctypes;state['source_evidence']=source_evidence;state['admission']=admission
        state['library_entered']=True
        library=ctypes.CDLL(LIBC,use_errno=True)
        state['library']=library;state['library_returned']=True
        state['call_binding_entered']=True
        call=library.renameat2  # existing glibc symbol; absence stops, no fallback
        state['call']=call;state['call_binding_returned']=True
        signature=(ctypes.c_int,ctypes.c_char_p,ctypes.c_int,ctypes.c_char_p,ctypes.c_uint)
        call.argtypes=list(signature);call.restype=ctypes.c_int
        state.update({'module':ctypes,'library':library,'library_type':type(library),'call':call,
            'call_type':type(call),'call_flags':call._flags_,'library_handle':library._handle,
            'signature':signature,'get_errno':ctypes.get_errno,
            'set_errno':ctypes.set_errno,'source_evidence':source_evidence,'admission':admission,
            'admission_raw':_guard_bytes(admission),'source_path':__file__})
        for name,expected in NATIVE_PINS.items():
            need(stable_file(name,16*1024*1024)['sha256']==expected, 'Publication TCB drift across binding')
        state['phase']='SEALED'
        _publication_binding()
        return None
    except BaseException as error:
        state['primary'][0]=error;state['phase']='STOP'
        raise


def _publication_binding():
    state=_PUBLICATION_BINDING[0]
    need(state is not None and state['phase']=='SEALED' and state['pid']==os.getpid() and
         state['primary'][0] is None, 'Actual before-capture publication binding required')
    module=state['module'];call=state['call']
    need(sys.modules.get('ctypes') is module and type(state['library']) is state['library_type'] and
         state['library_type'] is module.CDLL and type(call) is state['call_type'] and
         state['library'].renameat2 is call and module.get_errno is state['get_errno'] and
         module.set_errno is state['set_errno'], 'Publication native function/owner binding changed')
    actual=(module.c_int,module.c_char_p,module.c_int,module.c_char_p,module.c_uint)
    need(all(a is z for a,z in zip(actual,state['signature'])) and
         type(call.argtypes) is list and len(call.argtypes)==5 and
         all(a is z for a,z in zip(call.argtypes,state['signature'])) and call.restype is module.c_int,
         'Publication exact renameat2 ABI changed')
    need(type(state['library']._name) is str and state['library']._name==LIBC and
         type(state['library']._handle) is int and state['library']._handle>0 and
         state['library']._handle==state['library_handle'] and
         type(call._flags_) is int and call._flags_==state['call_flags'] and call.errcheck is None,
         'Publication library handle/flags or hidden native callback changed')
    need(_guard_bytes(state['admission'])==state['admission_raw'] and
         stable_file(state['source_path'],8388608)['sha256']==state['admission']['source_sha256'],
         'Publication source/admission drifted')
    for name,expected in NATIVE_PINS.items():
        need(stable_file(name,16*1024*1024)['sha256']==expected, 'Publication TCB current source drifted')
    return state


def _publication_stat(path):
    try:
        info=os.stat(path,follow_symlinks=False)
    except FileNotFoundError:
        return {'path':str(path),'exists':False}
    return {'path':str(path),'exists':True,'device':info.st_dev,'inode':info.st_ino,'mode':info.st_mode,
            'links':info.st_nlink,'bytes':info.st_size,'uid':info.st_uid,'gid':info.st_gid,
            'mtime_ns':info.st_mtime_ns,'ctime_ns':info.st_ctime_ns}


def _publication_close(token,custody):
    if token['fd'] is None or token['closed']:
        return
    token['closed']=True  # close entered once; ambiguity never causes retry
    try:
        os.close(token['fd'])
    except BaseException as error:
        if token['primary'][0] is None:
            token['primary'][0]=error
        else:
            token['secondary'].append(error);custody['secondary'].append(error)


def _guard_publish(path, value, custody):
    # The only publication operation moves a complete immutable staging inode
    # with renameat2(RENAME_NOREPLACE). No hardlink alias ever becomes visible.
    _guard_path(path)
    native=_publication_binding()  # authenticated before any packet acquisition
    raw=_guard_bytes(value);pending=Path(path+'.pending')
    record={'stage':str(pending),'final':path,'raw':raw,'before_stage':None,'before_final':None,
            'after_stage':None,'after_final':None,'directory_identity':None,'entered':False,'returned':False,'result':None,
            'errno':None,'committed':False,'uncertain':True,'primary':[None],'secondary':[],'tokens':[]}
    custody.setdefault('publications',[]).append(record)
    token={'fd':None,'entered':True,'closed':False,'primary':[None],'secondary':[]}
    directory={'fd':None,'entered':True,'closed':False,'primary':[None],'secondary':[]}
    custody.setdefault('io',[]).extend((token,directory));record['tokens']=[token,directory]
    try:
        token['fd']=os.open(pending,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_CLOEXEC|os.O_NOFOLLOW,0o600)
        view=memoryview(raw)
        while view:
            count=os.write(token['fd'],view);need(count>0,'Guard complete write made no progress')
            view=view[count:]
        os.fsync(token['fd'])
        os.fchmod(token['fd'],0o400)
        os.fsync(token['fd'])
        _publication_close(token,custody)
        if token['primary'][0] is not None:
            raise token['primary'][0]
        before,retained=stable_file(pending,GUARD_CAP,True)
        record['before_stage']=_publication_stat(pending);record['before_final']=_publication_stat(path)
        need(retained==raw and record['before_stage']['links']==1 and
             not record['before_stage']['mode'] & 0o222 and
             before['identity']==[record['before_stage'][k] for k in
                 ('device','inode','mode','bytes','mtime_ns','ctime_ns')],
             'Complete immutable single-link staging custody differs')
        directory['fd']=os.open(str(Path(path).parent),os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
        source_parent=Path(pending).parent;final_parent=Path(path).parent
        held=os.fstat(directory['fd']);named=os.stat(final_parent,follow_symlinks=False)
        record['directory_identity']={'device':held.st_dev,'inode':held.st_ino,'mode':held.st_mode}
        relative_stage=os.stat(pending.name,dir_fd=directory['fd'],follow_symlinks=False)
        need(source_parent==final_parent and stat.S_ISDIR(held.st_mode) and
             (held.st_dev,held.st_ino)==(named.st_dev,named.st_ino) and
             (relative_stage.st_dev,relative_stage.st_ino)==
             (record['before_stage']['device'],record['before_stage']['inode']),
             'Publication source and target do not share the authenticated held parent')
        # Both names are relative to the same held directory. No pre-check is
        # trusted for destination exclusivity: the primitive enforces it atomically.
        native['set_errno'](0)
        record['entered']=True;record['uncertain']=True
        result=native['call'](directory['fd'],os.fsencode(pending.name),
                              directory['fd'],os.fsencode(Path(path).name),1)
        record['returned']=True;record['result']=result
        need(type(result) is int and result in (0,-1),'Publication native return outside exact ABI')
        if result!=0:
            record['errno']=native['get_errno']()
            need(type(record['errno']) is int and record['errno']>0,'Publication failure errno unavailable')
            raise OSError(record['errno'],'Exclusive atomic single-link publication failed',path)
        record['committed']=True
        os.fsync(directory['fd'])
        record['after_stage']=_publication_stat(pending);record['after_final']=_publication_stat(path)
        need(record['after_stage']['exists'] is False and record['after_final']['exists'] is True and
             record['after_final']['links']==1 and
             all(record['after_final'][k]==record['before_stage'][k] for k in
                 ('device','inode','mode','bytes','uid','gid','mtime_ns')),
             'Atomic single-link move custody differs')
        observed,pin=_guard_read(path)
        need(_guard_bytes(observed)==raw,'Guard atomic publication complete readback differs')
        _publication_close(directory,custody)
        if directory['primary'][0] is not None:
            raise directory['primary'][0]
        record['uncertain']=False
        return pin
    except BaseException as error:
        record['primary'][0]=error
        if custody['primary'][0] is None:
            custody['primary'][0]=error
        elif custody['primary'][0] is not error:
            custody['secondary'].append(error)
        # Metadata only; never remove, overwrite, finish, or retry an uncertain
        # stage/final. Exact raw and all known tokens remain in same-process custody.
        for key,name in [('after_stage',pending),('after_final',path)]:
            try:
                record[key]=_publication_stat(name)
            except BaseException as secondary:
                record['secondary'].append(secondary);custody['secondary'].append(secondary)
        raise
    finally:
        _publication_close(token,custody);_publication_close(directory,custody)
        if record['primary'][0] is not None:
            for item in (token,directory):
                if item['primary'][0] is not None and item['primary'][0] is not record['primary'][0]:
                    record['secondary'].append(item['primary'][0]);custody['secondary'].append(item['primary'][0])


def _guard_fail(guard, error):
    if guard['primary'][0] is None:
        guard['primary'][0] = error
    elif guard['primary'][0] is not error:
        guard['secondary'].append(error)
    guard['phase'] = 'STOP'


def _guard_begin(case, deadline):
    need(len(_GUARD_ATTEMPTS) < 1024, 'Two-mode finite guard attempt registry exhausted')
    guard = {'phase': 'CONSUMED', 'primary': [None], 'secondary': [], 'binding': None,
             'request': None, 'request_pin': None, 'ack': None, 'ack_pin': None,
             'consume_pin': None, 'live': None, 'root': None, 'deadline': deadline,
             'checkpoint':'BEFORE_SOURCE_BINDING','supervision_result':None}
    _GUARD_ATTEMPTS.append(guard)  # consume before acquisition, never reset
    try:
        binding = case['family_guard']
        _guard_binding(binding)
        need(binding['action_id'] == case['family_action_id'] and binding['generation'] == case['family_generation'],
             'Guard original action/generation source binding differs')
        current = proc(os.getpid())
        need(current is not None and binding['parent_generation'] ==
             {'pid': current['pid'], 'start_ticks': current['start_ticks']}, 'Guard actual owning parent differs')
        for old in _GUARD_ATTEMPTS[:-1]:
            prior = old['binding']
            if prior is not None:
                need(prior['nonce'] != binding['nonce'] and prior['generation'] != binding['generation'],
                     'Guard release generation/nonce already consumed')
        guard['binding'] = binding
        for key in ('marker_path','request_path','ack_path','consume_path'):
            path = Path(binding[key])
            need(not path.exists() and not path.is_symlink(), 'Stale/reused guard channel or marker')
            if key != 'marker_path':
                need(not Path(str(path) + '.pending').exists() and not Path(str(path) + '.pending').is_symlink(),
                     'Stale/reused guard publication')
        guard['deadline'] = min(deadline, time.monotonic() + binding['timeout_milliseconds'] / 1000)
        guard['checkpoint'] = 'WAITING_REQUEST'
        guard['phase'] = 'WAITING_REQUEST'
        return guard
    except BaseException as error:
        _guard_fail(guard, error)
        raise


def _guard_step(guard, domain, all_rows, current, captured):
    try:
        binding = guard['binding']
        if guard['phase'] == 'CONSUMED_RELEASE':
            # The published request/release/consumption remain immutable through
            # the entire child lifetime; final outer validation repeats this.
            for key,pin in [('request_path',guard['request_pin']),('ack_path',guard['ack_pin']),
                            ('consume_path',guard['consume_pin'])]:
                _, actual = _guard_read(binding[key])
                need(actual == pin, 'Guard retained packet drifted after release')
            return
        need(time.monotonic() <= guard['deadline'], 'Before-target parent guard deadline expired')
        if guard['phase'] == 'WAITING_REQUEST':
            request_path = Path(binding['request_path'])
            if not request_path.exists():
                return
            request, request_pin = _guard_read(request_path)
            _guard_exact(request, ('schema','binding','process','marker'))
            need(type(request['schema']) is str and request['schema'] == 'h25-family-guard-request-v2' and
                 _guard_bytes(request['binding']) == _guard_bytes(binding), 'Guard request expected source/context differs')
            leaf = request['process']; _guard_leaf(leaf)
            marker = request['marker']; _guard_exact(marker, ('path','sha256','bytes'))
            need(type(marker['path']) is str and marker['path'] == binding['marker_path'] and
                 type(marker['bytes']) is int and 0 <= marker['bytes'] <= MARKER_CAP, 'Guard marker bound differs')
            _guard_digest(marker['sha256'])
            marker_pin, marker_raw = stable_file(marker['path'], MARKER_CAP, True)
            need(marker_pin['sha256'] == marker['sha256'] and marker_pin['bytes'] == marker['bytes'],
                 'Guard complete source/context marker changed')
            marked = json.loads(marker_raw)
            need(type(marked) is dict and type(marked.get('actual_context')) is dict and
                 marked.get('schema') == 'h25-component-pretarget-identity-v1' and
                 all(type(marked.get(k)) is str and marked[k] == binding[k] for k in
                     ('case_id','context_id','unit_id','mode')) and
                 marked.get('component_source_path') == binding['component_source']['path'],
                 'Guard actual case/context/unit/mode/source marker differs')
            context_raw = json.dumps(marked['actual_context'], sort_keys=True, separators=(',', ':'),
                                     ensure_ascii=True, allow_nan=False).encode('ascii') + b'\n'
            need(hashlib.sha256(context_raw).hexdigest() == binding['context_sha256'] and
                 all(type(marked['process'][k]) is int and marked['process'][k] == leaf[k] for k in leaf),
                 'Guard actual context or process differs')
            _guard_binding(binding)  # complete immutable sources again before ACK
            key = generation(leaf)
            live = proc(leaf['pid']); root_live = proc(captured['pid'])
            need(live is not None and root_live is not None and live['state'] != 'Z' and root_live['state'] != 'Z' and
                 generation(root_live) == domain.root and key in domain.rows and key in domain.fds and
                 all(type(live[k]) is int and live[k] == leaf[k] for k in leaf) and
                 any(generation(r) == key for r in current), 'Guard leaf is not a live generation-owned child')
            cursor = leaf['pid']; seen = set()
            while cursor != captured['pid']:
                need(cursor not in seen and len(seen) < 128 and cursor in all_rows,
                     'Guard live ancestor chain to captured Root absent')
                seen.add(cursor); cursor = all_rows[cursor]['ppid']
            need(generation(all_rows[captured['pid']]) == domain.root,
                 'Guard captured Root generation no longer current')
            guard['checkpoint'] = 'LIVE_GENERATION_SOURCE_CONTEXT_VALIDATED'
            guard['request'], guard['request_pin'], guard['live'], guard['root'] = request, request_pin, dict(live), dict(root_live)
            ack = {'schema':'h25-family-guard-release-v2','binding':binding,
                   'request_sha256':request_pin['sha256'],'process':leaf,
                   'parent_generation':binding['parent_generation'],
                   'root_generation':{'pid':captured['pid'],'start_ticks':captured['start_ticks']},
                   'expires_monotonic':guard['deadline']}
            guard['phase'] = 'RELEASE_CONSUMED'  # once before publication, even if it fails
            guard['ack'], guard['ack_pin'] = ack, _guard_publish(binding['ack_path'], ack, guard)
            guard['checkpoint'] = 'ACK_DURABLY_PUBLISHED'
            guard['phase'] = 'WAITING_CONSUME'
        if guard['phase'] == 'WAITING_CONSUME' and Path(binding['consume_path']).exists():
            consumed, consumed_pin = _guard_read(binding['consume_path'])
            _guard_exact(consumed, ('schema','request_sha256','ack_sha256','process'))
            need(consumed['schema'] == 'h25-family-guard-consumed-v2' and
                 type(consumed['request_sha256']) is str and consumed['request_sha256'] == guard['request_pin']['sha256'] and
                 type(consumed['ack_sha256']) is str and consumed['ack_sha256'] == guard['ack_pin']['sha256'] and
                 _guard_bytes(consumed['process']) == _guard_bytes(guard['request']['process']),
                 'Guard release consumption differs')
            guard['consume_pin'] = consumed_pin; guard['phase'] = 'CONSUMED_RELEASE'
            guard['checkpoint'] = 'CHILD_CONSUMED_RELEASE'
    except BaseException as error:
        _guard_fail(guard, error)
        raise


def child_guard_wait(binding, marker_pin, process, state):
    """Fixed child wait; no target callback until matching one-shot ACK consumed."""
    need(type(state) is dict and state['phase'] == 'PRETARGET' and state['primary'][0] is None,
         'Before-target child guard already consumed/stopped')
    state['phase'] = 'WAITING_RELEASE'  # burn before any acquisition
    try:
        _guard_binding(binding)
        leaf = {k:process[k] for k in ('pid','ppid','pgid','sid','start_ticks')}; _guard_leaf(leaf)
        need(leaf['pid'] == os.getpid(), 'Guard child process identity differs')
        request = {'schema':'h25-family-guard-request-v2','binding':binding,'process':leaf,
                   'marker':{k:marker_pin[k] for k in ('path','sha256','bytes')}}
        request_pin = _guard_publish(binding['request_path'], request, state)
        state['request'],state['request_pin'] = request,request_pin
        deadline = time.monotonic() + binding['timeout_milliseconds'] / 1000
        while not Path(binding['ack_path']).exists():
            need(time.monotonic() < deadline, 'Before-target child ACK wait expired')
            owner = proc(binding['parent_generation']['pid'])
            need(owner is not None and owner['state'] != 'Z' and
                 generation(owner) == (binding['parent_generation']['pid'],binding['parent_generation']['start_ticks']),
                 'Before-target owning parent is no longer live')
            time.sleep(min(0.01,max(0.0,deadline-time.monotonic())))
        ack, ack_pin = _guard_read(binding['ack_path'])
        _guard_exact(ack, ('schema','binding','request_sha256','process','parent_generation','root_generation','expires_monotonic'))
        need(type(ack['schema']) is str and ack['schema'] == 'h25-family-guard-release-v2' and
             _guard_bytes(ack['binding']) == _guard_bytes(binding) and
             type(ack['request_sha256']) is str and ack['request_sha256'] == request_pin['sha256'] and
             _guard_bytes(ack['process']) == _guard_bytes(leaf) and
             _guard_bytes(ack['parent_generation']) == _guard_bytes(binding['parent_generation']) and
             type(ack['expires_monotonic']) is float and
             time.monotonic() <= min(deadline,ack['expires_monotonic']), 'Missing/wrong/stale/timedout parent ACK')
        _guard_generation(ack['root_generation'])
        owner = proc(binding['parent_generation']['pid']); own = proc(os.getpid())
        need(owner is not None and owner['state'] != 'Z' and own is not None and own['state'] != 'Z' and
             generation(owner) == (binding['parent_generation']['pid'],binding['parent_generation']['start_ticks']) and
             all(type(own[k]) is int and own[k] == leaf[k] for k in leaf), 'ACK owner/child generation no longer live')
        need(_guard_read(binding['request_path'])[1] == request_pin, 'Own request changed before ACK consumption')
        state['ack'],state['ack_pin'] = ack,ack_pin
        state['phase'] = 'RELEASE_CONSUMED'  # never retry even if publication fails
        consumed = {'schema':'h25-family-guard-consumed-v2','request_sha256':request_pin['sha256'],
                    'ack_sha256':ack_pin['sha256'],'process':leaf}
        state['consume_pin'] = _guard_publish(binding['consume_path'],consumed,state)
        need(time.monotonic() <= min(deadline,ack['expires_monotonic']), 'ACK expired during complete consume publication')
        state['phase'] = 'TARGET_RELEASED'
        return None
    except BaseException as error:
        _guard_fail(state,error)
        raise


def guard_evidence(guard):
    return {'schema':'h25-family-live-parent-guard-v2','phase':guard['phase'],
            'request':guard['request_pin'],'ack':guard['ack_pin'],'consume':guard['consume_pin'],
            'live_generation_before_release':guard['live'],'captured_root_before_release':guard['root'],
            'parent_generation':None if guard['binding'] is None else guard['binding']['parent_generation'],
            'actual_error_retained':guard['primary'][0] is not None,
            'no_post_exit_substitute':True,'no_retry':True}

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
    guard = _guard_begin(case, deadline)
    domain = OwnedDomain()
    # Raw slots and actual custodians precede every timer/spawn operation.
    root_errors = [None] * 5
    guard['root_errors'] = root_errors
    guard['owned_domain'] = domain
    guard['actual_process'] = None
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
                guard['actual_process'] = process
                # Popen leaves an exited root waitable; capture its generation BEFORE poll.
                captured = proc(process.pid)
                need(captured is not None and captured['pgid'] == captured['sid'] == process.pid,
                     'New root process/session identity missing')
                domain.root = generation(captured)
                domain.add(captured)
                write_new(evidence / 'ROOT-PROCESS.json', captured)
                while True:
                    all_rows, current = domain.observe()
                    _guard_step(guard, domain, all_rows, current, captured)
                    peak = max(peak, sum(row['rss_bytes'] for row in current))
                    need(peak <= rss_bytes, 'Owned process RSS sum exceeded')
                    need(max((evidence / name).stat().st_size for name in
                             ('root.stdout.raw', 'root.stderr.raw')) <= LOG_CAP, 'Outer raw log cap exceeded')
                    if process.poll() is not None:
                        need(guard['phase'] == 'CONSUMED_RELEASE', 'Root exited without actual before-target release consumption')
                        break
                    time.sleep(0.01)
            except BaseException as error:
                root_errors[0] = error
                if guard['primary'][0] is None:
                    guard['primary'][0] = error
                raise
    except BaseException as error:
        # Includes outer log-close failure. Never format before raw retention.
        root_errors[1] = error
        if guard['primary'][0] is None:
            guard['primary'][0] = error
        if guard['phase'] != 'CONSUMED_RELEASE':
            guard['phase'] = 'STOP'
    finally:
        timer_retired = False
        try:
            signal.setitimer(signal.ITIMER_REAL, 0)
            timer_retired = True
        except BaseException as timer_error:
            root_errors[2] = timer_error
            if guard['primary'][0] is None:
                guard['primary'][0] = timer_error
        # An uncertain active alarm must not be assigned its old default action.
        # Keep the known handler while the actual enclosing owner retires it.
        if timer_retired:
            try:
                signal.signal(signal.SIGALRM, old_handler)
            except BaseException as handler_error:
                root_errors[3] = handler_error
                if guard['primary'][0] is None:
                    guard['primary'][0] = handler_error
        # This attempt is independent of both timer errors and pending Popen.
        try:
            cleanup = domain.cleanup(process)
        except BaseException as cleanup_error:
            root_errors[4] = cleanup_error
            if guard['primary'][0] is None:
                guard['primary'][0] = cleanup_error
            cleanup = {'complete': False, 'group_empty_proved': False,
                       'owned_generations': list(domain.rows.values()),
                       'groups': [{'pgid': g, 'sid': sid} for g, sid in sorted(domain.groups)],
                       'reaped_adopted': domain.reaped, 'observed_after_root_exit': [],
                       'remaining': 'UNKNOWN_AFTER_CLEANUP_ERROR'}
            # Do not retry possibly attempted closes. The real domain, process,
            # handles and raw errors remain strongly held in the original guard.
    try:
        if guard['primary'][0] is not None:
            primary = guard['primary'][0]
            failure = {'type': type(primary).__name__, 'message': str(primary)[:2048]}
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
                  'no_hostile_fork_or_concurrent_children_claim': True,
                  'before_target_guard': guard_evidence(guard)}
        guard['supervision_result'] = result
        write_new(evidence / 'SUPERVISION.json', result)
        if guard['primary'][0] is not None:
            raise guard['primary'][0]
        return result
    except BaseException as error:
        if guard['primary'][0] is not None:
            if error is not guard['primary'][0]:
                guard['secondary'].append(error)
            raise guard['primary'][0]
        raise



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
