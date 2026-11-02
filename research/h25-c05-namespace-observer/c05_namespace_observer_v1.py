"""Linux namespace observations for one bounded canonical ASCII path.

Source proposal only. No compiler, Root, provider, content reader or launcher.
No observation is invoked at module scope; import initialization is unqualified.
All original admission values stay unchanged. The future caller must authenticate this module/native dispatch and
exclude interfering audit hooks, signals, tracing and private-state mutation.
Returned metadata is a trace, not an atomic snapshot or a compilation lease.
"""
import errno
import posix
from types import BuiltinFunctionType

MAX_PATH = 4096
MAX_COMPONENTS = 64
_OPEN, _STAT, _FSTAT, _CLOSE = posix.open, posix.stat, posix.fstat, posix.close
_PATH_FLAGS = posix.O_PATH | posix.O_NOFOLLOW | posix.O_CLOEXEC
_ROOT_FLAGS = _PATH_FLAGS | posix.O_DIRECTORY
_REGULAR, _DIRECTORY, _SYMLINK = 0o100000, 0o040000, 0o120000
# Active owner, first failed owner. No public reset or second acquisition after
# failure. The authenticated caller must preserve this singleton module state.
_PROCESS = [None, None]


class ObservationStop(RuntimeError):
    pass


def _require(condition, message):
    if not condition:
        raise ObservationStop(message)


def _native_bindings():
    for function, name in ((_OPEN, 'open'), (_STAT, 'stat'),
                           (_FSTAT, 'fstat'), (_CLOSE, 'close')):
        _require(type(function) is BuiltinFunctionType and
                 function.__self__ is posix and function.__name__ == name and
                 posix.__dict__.get(name) is function,
                 'native dispatch binding changed')


def _metadata(info):
    # Exact integer projection. No access-time field or float is compared.
    if info is None:
        return None
    values = (info.st_dev, info.st_ino, info.st_mode, info.st_nlink,
              info.st_uid, info.st_gid, info.st_size,
              info.st_mtime_ns, info.st_ctime_ns)
    _require(all(type(value) is int and -(1 << 64) <= value < (1 << 64)
                 for value in values), 'metadata outside original integer domain')
    return values


class NamespaceObservation:
    """One use; construct and retain the owner BEFORE calling observe().

    No caller supplies stat facts, expected kinds, a resolver or an I/O callback.
    No capability or authenticity claim is conferred on caller-supplied paths.
    Raw stat/error objects remain on this owner, including after failure.
    This class is ordinary protected local state, not an original Root owner.
    """
    __slots__ = ('path', 'parts', 'phase', 'outcome', 'terminal_index',
                 'primary', 'secondary', 'quarantined', 'pending_open', 'operation',
                 'lookup', 'pinned', 'late', 'lookup_errors', 'open_errors',
                 'close_errors', 'close_attempted', 'close_confirmed',
                 'fd_numbers', '_fds', 'projected')

    def __init__(self, path):
        _require(type(path) is str and 1 < len(path) <= MAX_PATH,
                 'bounded exact string path required')
        _require(path.startswith('/') and
                 all(32 <= ord(c) < 127 for c in path),
                 'canonical absolute ASCII path required')
        parts = tuple(path.split('/')[1:])
        _require(1 <= len(parts) <= MAX_COMPONENTS and
                 all(part not in ('', '.', '..') for part in parts),
                 'unsupported path spelling or component bound')
        count = len(parts) + 1
        self.path, self.parts = path, parts
        self.phase, self.outcome = 'NEW', None
        self.terminal_index = None
        self.primary = None
        self.secondary = None
        self.quarantined = False
        self.pending_open = False
        self.operation = None
        # Every ownership/error/raw-result slot exists before acquisition.
        self.lookup = [None] * count
        self.pinned = [None] * count
        self.late = [None] * count
        self.lookup_errors = [None] * count
        self.open_errors = [None] * count
        self.close_errors = [None] * count
        self.close_attempted = [False] * count
        self.close_confirmed = [False] * count
        self.fd_numbers = [None] * count
        self._fds = [None] * count
        self.projected = None

    def _acquire(self, index, name, parent, flags):
        self.operation = 'open'
        self.pending_open = True
        try:
            # First destination of a delivered FD is its preallocated slot.
            self._fds[index] = _OPEN(name, flags, dir_fd=parent)
        except BaseException as error:
            if self.primary is None:
                self.primary = error
            self.open_errors[index] = error
            # No open error is reinterpreted as absence or successful release.
            raise
        self.pending_open = False
        self.fd_numbers[index] = self._fds[index]
        self.operation = 'fstat'
        self.pinned[index] = _FSTAT(self._fds[index])

    def _walk(self):
        _native_bindings()
        NamespaceObservation._acquire(self, 0, '/', None, _ROOT_FLAGS)
        _require(self.pinned[0].st_mode & 0o170000 == _DIRECTORY,
                 'process root descriptor is not a directory')
        index = 1
        while index <= len(self.parts):
            name = self.parts[index - 1]
            parent = self._fds[index - 1]
            self.operation = 'stat-nofollow'
            try:
                # A single basename: there is no hidden intermediate symlink.
                self.lookup[index] = _STAT(name, dir_fd=parent,
                                           follow_symlinks=False)
            except BaseException as error:
                self.lookup_errors[index] = error
                if (type(error) is FileNotFoundError and
                        type(error.errno) is int and error.errno == errno.ENOENT):
                    self.outcome = 'ABSENT_AT_PINNED_PARENT'
                    self.terminal_index = index
                    break
                if self.primary is None:
                    self.primary = error
                raise
            NamespaceObservation._acquire(self, index, name, parent, _PATH_FLAGS)
            # Raw lookup and pinned metadata were both retained first.
            _require(_metadata(self.lookup[index]) == _metadata(self.pinned[index]),
                     'lookup and pinned object metadata differ')
            kind = self.pinned[index].st_mode & 0o170000
            self.terminal_index = index
            if kind == _SYMLINK:
                self.outcome = 'SYMLINK_UNRESOLVED'
                break
            if kind not in (_REGULAR, _DIRECTORY):
                self.outcome = 'SPECIAL_FILE_UNSUPPORTED'
                break
            if index == len(self.parts):
                self.outcome = ('REGULAR_CONTENT_UNREAD' if kind == _REGULAR
                                else 'DIRECTORY_CONTENTS_UNENUMERATED')
                break
            if kind != _DIRECTORY:
                self.outcome = 'NON_DIRECTORY_PREFIX'
                break
            index += 1
        # These observations concern the same held objects, not new path walks.
        # Equality of endpoints is not asserted to imply interval stability.
        self.operation = 'late-fstat'
        index = 0
        while index < len(self._fds):
            if self._fds[index] is not None:
                self.late[index] = _FSTAT(self._fds[index])
            index += 1

    def observe(self):
        """Return None. Evidence stays on the pre-existing owner in every case."""
        _require(type(self) is NamespaceObservation, 'exact observation owner required')
        if _PROCESS[1] is not None:
            raise _PROCESS[1].primary
        _require(_PROCESS[0] is None, 'another observation is active')
        _require(self.phase == 'NEW', 'observation owner is single-use')
        _PROCESS[0] = self
        self.phase = 'RUNNING'
        try:
            NamespaceObservation._walk(self)
        except BaseException as error:
            # No diagnostic formatting or cleanup call precedes this root.
            if self.primary is None:
                self.primary = error
            elif self.primary is not error:
                self.secondary = error
            self.quarantined = True
            if _PROCESS[1] is None:
                _PROCESS[1] = self
        finally:
            index = len(self._fds) - 1
            while index >= 0:
                descriptor = self._fds[index]
                if descriptor is not None:
                    # Consume ownership before exactly one close attempt.
                    self._fds[index] = None
                    self.close_attempted[index] = True
                    try:
                        _CLOSE(descriptor)
                    except BaseException as error:
                        if self.primary is None:
                            self.primary = error
                        self.close_errors[index] = error
                        self.quarantined = True
                        if _PROCESS[1] is None:
                            _PROCESS[1] = self
                    else:
                        self.close_confirmed[index] = True
                index -= 1
            _PROCESS[0] = None
        if self.primary is not None:
            self.phase = 'FAILED'
            raise self.primary
        self.phase = 'DONE'

    def project(self):
        """Pure diagnostic projection; it writes nothing and creates no pin.

        Failed observations retain raw state only. A failure here also roots
        its error, poisons this module's future acquisitions and forbids retry.
        """
        _require(type(self) is NamespaceObservation, 'exact observation owner required')
        if _PROCESS[1] is not None:
            raise _PROCESS[1].primary
        _require(self.phase == 'DONE', 'successful observation required')
        try:
            return NamespaceObservation._project(self)
        except BaseException as error:
            self.primary = error
            self.quarantined = True
            self.phase = 'FAILED'
            if _PROCESS[1] is None:
                _PROCESS[1] = self
            raise

    def _project(self):
        rows = []
        index = 0
        while index < len(self._fds):
            rows.append({
                'index': index,
                'name': '/' if index == 0 else self.parts[index - 1],
                'parent_index': None if index == 0 else index - 1,
                'lookup': _metadata(self.lookup[index]),
                'pinned': _metadata(self.pinned[index]),
                'late': _metadata(self.late[index]),
                'lookup_exception_retained': self.lookup_errors[index] is not None,
                'open_exception_retained': self.open_errors[index] is not None,
                'close_exception_retained': self.close_errors[index] is not None,
                'close_attempted': self.close_attempted[index],
                'close_confirmed': self.close_confirmed[index],
            })
            index += 1
        self.projected = {
            'schema': 'h25-c05-namespace-observation-v1',
            'requested_path': self.path,
            'phase': self.phase,
            'outcome': self.outcome,
            'terminal_index': self.terminal_index,
            'rows': rows,
            'primary_retained': self.primary is not None,
            'pending_open': self.pending_open,
            'quarantined': self.quarantined,
            'metadata_fields': ('device', 'inode', 'mode', 'links', 'uid', 'gid',
                                'size', 'mtime_ns', 'ctime_ns'),
            'regular_content_read': False,
            'directory_members_enumerated': False,
            'absolute_namespace_snapshot': False,
            'interval_stability_established': False,
            'durable_capture_established': False,
            'full_c05': False,
            'runtime_qualified': False,
        }
        return self.projected