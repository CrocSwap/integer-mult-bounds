"""Windows Job Object ownership and launch diagnostics for Git blob streams.

Adapted from Mihir Srivastava's PR5463/PR5524 adapters and ywz65's gated
Job Object implementation, with their Apache-2.0 attribution retained.
Shared-reader integration for josecarlosgonzalezroque-design with substantial
OpenAI Codex assistance. This is a binary, context-managed argv subset of Popen.
"""
from contextlib import contextmanager
import ctypes
from ctypes import wintypes
import json
from pathlib import Path
import tempfile
import subprocess
import sys
import threading
import time
import uuid

REAL_POPEN = subprocess.Popen


@contextmanager
def windows_pipe(argv, gate, **kwargs):
    """Yield a gated process and an idempotent, thread-safe whole-job stop.

    Only the job handle owner may release the gate. The requested command's
    stdin/stdout are inherited through the gate without Python-level copying.
    """
    class BasicLimits(ctypes.Structure):
        _fields_ = [("ProcessTime", ctypes.c_int64), ("JobTime", ctypes.c_int64),
                    ("Flags", wintypes.DWORD), ("MinWorkingSet", ctypes.c_size_t),
                    ("MaxWorkingSet", ctypes.c_size_t), ("ActiveProcessLimit", wintypes.DWORD),
                    ("Affinity", ctypes.c_size_t), ("Priority", wintypes.DWORD),
                    ("Scheduling", wintypes.DWORD)]

    class IOCounts(ctypes.Structure):
        _fields_ = [(name, ctypes.c_uint64) for name in
                    ("ReadOps", "WriteOps", "OtherOps", "ReadBytes", "WriteBytes", "OtherBytes")]

    class ExtendedLimits(ctypes.Structure):
        _fields_ = [("Basic", BasicLimits), ("IO", IOCounts),
                    ("ProcessMemory", ctypes.c_size_t), ("JobMemory", ctypes.c_size_t),
                    ("PeakProcessMemory", ctypes.c_size_t), ("PeakJobMemory", ctypes.c_size_t)]

    class Accounting(ctypes.Structure):
        _fields_ = [(name, ctypes.c_int64) for name in
                    ("UserTime", "KernelTime", "PeriodUserTime", "PeriodKernelTime")] + [
                    (name, wintypes.DWORD) for name in
                    ("PageFaults", "TotalProcesses", "ActiveProcesses", "TerminatedProcesses")]

    api = ctypes.WinDLL("kernel32", use_last_error=True)

    def native(name, result, *arguments):
        fn = getattr(api, name)
        fn.restype, fn.argtypes = result, arguments
        return fn

    handle, dword, boolean = wintypes.HANDLE, wintypes.DWORD, wintypes.BOOL
    create_job = native("CreateJobObjectW", handle, ctypes.c_void_p, wintypes.LPCWSTR)
    set_info = native("SetInformationJobObject", boolean, handle, ctypes.c_int, ctypes.c_void_p, dword)
    assign = native("AssignProcessToJobObject", boolean, handle, handle)
    terminate = native("TerminateJobObject", boolean, handle, wintypes.UINT)
    query = native("QueryInformationJobObject", boolean, handle, ctypes.c_int,
                   ctypes.c_void_p, dword, ctypes.c_void_p)
    create_event = native("CreateEventW", handle, ctypes.c_void_p, boolean, boolean, wintypes.LPCWSTR)
    set_event = native("SetEvent", boolean, handle)
    close = native("CloseHandle", boolean, handle)

    def checked(ok):
        if not ok:
            raise ctypes.WinError(ctypes.get_last_error())
        return ok

    job = checked(create_job(None, None))
    event, process, assigned = None, None, False
    stopped = False
    lock = threading.Lock()

    def stop():
        nonlocal stopped
        with lock:
            if stopped:
                return
            checked(terminate(job, 1))
            deadline = time.monotonic() + 10
            while True:
                state = Accounting()
                checked(query(job, 1, ctypes.byref(state), ctypes.sizeof(state), None))
                if not state.ActiveProcesses:
                    break
                if time.monotonic() >= deadline:
                    raise RuntimeError("owned Git process cleanup timed out")
                time.sleep(0.01)
            stopped = True

    try:
        limits = ExtendedLimits()
        limits.Basic.Flags = 0x2000  # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        checked(set_info(job, 9, ctypes.byref(limits), ctypes.sizeof(limits)))
        name = "Local\\research-git-stream-" + uuid.uuid4().hex
        event = checked(create_event(None, True, False, name))
        if ctypes.get_last_error() == 183:
            raise ValueError("Git ownership gate name already exists")
        process = REAL_POPEN([sys.executable, "-I", "-S", "-c", gate, name,
                              json.dumps(argv, ensure_ascii=False)], **kwargs)
        checked(assign(job, int(process._handle)))
        assigned = True
        checked(set_event(event))
        yield process, stop
    finally:
        try:
            if process is not None:
                if assigned:
                    stop()
                elif process.poll() is None:
                    process.kill()
                process.wait(timeout=10)
        finally:
            try:
                if process is not None:
                    # In the actual reader these are already closed. Setup
                    # failure can reach here before the reader owns any streams.
                    for stream in (process.stdin, process.stdout, process.stderr):
                        if stream is not None:
                            stream.close()
            finally:
                try:
                    if event:
                        checked(close(event))
                finally:
                    checked(close(job))


class OwnedPopen:
    """The Popen subset used by the blob reader, with job-aware kill/exit.

    This is a reader adapter, not a general subprocess replacement.
    The caller must use the context manager, as the actual reader does.
    """
    def __init__(self, argv, gate, **kwargs):
        self.context = windows_pipe(argv, gate, **kwargs)
        self.process, self.stop = self.context.__enter__()

    def __getattr__(self, name):
        return getattr(self.process, name)

    def kill(self):
        self.stop()

    def __enter__(self):
        return self

    def __exit__(self, *exception):
        return self.context.__exit__(*exception)


STARTUP_TIMEOUT = 10
MAX_REPORT_BYTES = 65536

# REPORT is inserted as a Python string literal by make_gate. The requested
# command receives its original argv/env/cwd/standard handles, not this channel.
GATE = r'''
import ctypes
from ctypes import wintypes
import json
import os
import subprocess
import sys
api = ctypes.WinDLL('kernel32', use_last_error=True)
api.OpenEventW.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.LPCWSTR]
api.OpenEventW.restype = wintypes.HANDLE
api.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
api.WaitForSingleObject.restype = wintypes.DWORD
api.CloseHandle.argtypes = [wintypes.HANDLE]
api.CloseHandle.restype = wintypes.BOOL
event = api.OpenEventW(0x00100000, False, sys.argv[1])
if not event:
    raise ctypes.WinError(ctypes.get_last_error())
try:
    if api.WaitForSingleObject(event, 30000) != 0:
        raise RuntimeError('Git launch ownership gate was not released')
finally:
    api.CloseHandle(event)

def report(value):
    with open(REPORT + '.pending', 'x', encoding='utf-8') as stream:
        json.dump(value, stream, ensure_ascii=True)
    os.replace(REPORT + '.pending', REPORT)

# Only this OSError is reported as a requested-executable launch error. Failure
# of the gate/reporting mechanism fails closed via the parent's bounded wait.
try:
    child = subprocess.Popen(json.loads(sys.argv[2]))
except OSError as error:
    report({'status': 'oserror', 'errno': error.errno,
            'winerror': error.winerror, 'strerror': error.strerror,
            'filename': error.filename, 'filename2': error.filename2})
    raise SystemExit(1)
report({'status': 'started'})
raise SystemExit(child.wait())
'''


def make_gate(report):
    return 'REPORT = ' + repr(str(report)) + '\n' + GATE


def read_payload(path):
    with path.open('rb') as stream:
        return stream.read(MAX_REPORT_BYTES + 1)


def interpret_report(payload):
    # Truncated, oversized, malformed or unknown reports never become success,
    # and never trigger the reader's legacy retry.
    if len(payload) > MAX_REPORT_BYTES:
        raise ValueError('oversized Git launch report')
    value = json.loads(payload)
    if value == {'status': 'started'}:
        return
    fields = {'status', 'errno', 'winerror', 'strerror', 'filename', 'filename2'}
    if (not isinstance(value, dict) or set(value) != fields
            or value['status'] != 'oserror'
            or type(value['errno']) is not int or type(value['winerror']) is not int
            or not isinstance(value['strerror'], str)
            or any(value[k] is not None and not isinstance(value[k], str)
                   for k in ('filename', 'filename2'))):
        raise ValueError('invalid Git launch report')
    # Windows OSError maps the original native code to the appropriate subclass
    # and errno, just as direct CreateProcess/Popen did in the gate.
    raise OSError(value['errno'], value['strerror'], value['filename'],
                  value['winerror'], value['filename2'])


def read_report(path):
    interpret_report(read_payload(path))


def await_launch(process, report, argv, timeout):
    deadline = time.monotonic() + timeout
    while True:
        if report.exists():
            try:
                payload = read_payload(report)
            except PermissionError:
                # Windows can briefly deny opening a newly renamed report.
                # Retry only channel I/O, within the original startup bound.
                # A requested executable's PermissionError is reconstructed
                # below, outside this handler, and must propagate immediately.
                pass
            else:
                interpret_report(payload)
                return
        elif process.poll() is not None:
            # A fast process may publish between the existence check and poll.
            if not report.exists():
                raise RuntimeError('Git ownership gate exited without a launch report')
        if time.monotonic() >= deadline:
            raise subprocess.TimeoutExpired(argv, timeout)
        time.sleep(0.01)


@contextmanager
def checked_pipe(argv, **kwargs):
    """Report launch before returning streams; stop the owned job on any failure.

    The owner retains the PR5463 gated Job Object protocol. Startup has its own
    bound; the existing per-response watchdog still excludes consumer pauses.
    """
    if not isinstance(argv, list) or not argv or any(type(a) is not str for a in argv):
        raise TypeError('Git launch wrapper requires a nonempty list of strings')
    with tempfile.TemporaryDirectory(prefix='git launch status ') as temporary:
        report = Path(temporary) / 'status.json'
        with OwnedPopen(argv, make_gate(report), **kwargs) as process:
            await_launch(process, report, argv, STARTUP_TIMEOUT)
            yield process


class LaunchCheckedPopen:
    """Only the Popen subset consumed by the blob reader, used with with."""
    def __init__(self, argv, **kwargs):
        self.context = checked_pipe(argv, **kwargs)
        self.process = self.context.__enter__()

    def __getattr__(self, name):
        return getattr(self.process, name)

    def __enter__(self):
        return self

    def __exit__(self, *exception):
        return self.context.__exit__(*exception)
