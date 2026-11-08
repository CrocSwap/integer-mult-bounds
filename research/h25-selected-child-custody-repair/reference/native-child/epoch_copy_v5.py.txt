"""Bounded exclusive copy source with opaque error ownership; never executed here."""
import hashlib
import os
import stat
import epoch_schema_v5 as schema

COPY_CONFIGURATION = None
COPY_EXECUTION_APPROVAL = None
COPY_FUNDING = None
_TYPE, _LEN = type, len
_OPEN, _CLOSE, _READ, _WRITE = os.open, os.close, os.read, os.write
_FSTAT, _STAT, _LSEEK, _FSYNC = os.fstat, os.stat, os.lseek, os.fsync
_SCANDIR, _STAT_RESULT = os.scandir, os.stat_result


def _gate() -> None:
    schema.exact(COPY_CONFIGURATION, ('leaf_policy_sha256', 'configuration_sha256', 'scandir_release_premise_sha256'))
    schema.exact(COPY_EXECUTION_APPROVAL, ('external_launch_policy_sha256',))
    schema.exact(COPY_FUNDING, ('reservation_sha256',))
    for values in (COPY_CONFIGURATION, COPY_EXECUTION_APPROVAL, COPY_FUNDING):
        for value in values.values():
            schema.digest(value)


def _fd(value) -> None:
    schema.integer(value, 0, (1 << 31) - 1)


def _identity(info) -> dict:
    schema.need(_TYPE(info) is _STAT_RESULT, 'exact native stat result required')
    row = dict(zip(schema.IDENTITY_KEYS, (info.st_dev, info.st_ino, info.st_mode, info.st_nlink,
               info.st_uid, info.st_gid, info.st_size, info.st_mtime_ns, info.st_ctime_ns)))
    for value in row.values():
        schema.integer(value, 0, (1 << 127) - 1)
    return row





def _parent(path: str, owner, fd_slots: list, destination: int) -> str:
    """Fill the caller-owned slot; caller's finally owns all five slots.

    No descriptor tuple crosses the helper return boundary. The fifth slot
    owns the next ancestor until its transfer; any helper-entry/body failure
    leaves all known descriptors reachable to the caller's inline cleanup.
    """
    schema.path(path)
    _state = schema.owner_state(owner)
    _primary, _secondary, _phases, _uncertain = _state[0], _state[1], _state[2], _state[3]
    _counts, _overflow, _io = _state[4], _state[5], _state[7]
    _attempt_digits, _confirmed_digits = _io[7], _io[8]
    _successors = schema.CUSTODY_SUCCESSORS
    _quarantine_error = schema.IO_QUARANTINE_ERROR
    _base_error, _close_native = BaseException, _CLOSE
    _error_index = _digit = 0
    _owned_fd = _close_error = _acquisition_error = None
    cleanup_primary = operation_primary = None
    schema.need(_TYPE(fd_slots) is list and _LEN(fd_slots) == 5, 'internal FD slots differ')
    schema.integer(destination, 0, 3)
    schema.need(fd_slots[destination] is None and fd_slots[4] is None, 'parent slots already owned')
    parts = path.split('/')
    name = parts[-1]
    flags = os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW | os.O_DIRECTORY
    if _io[0] or _io[1] or _io[10] or _overflow[1] or _attempt_digits[4] == 1:
        raise _quarantine_error
    _io[1] = True
    try:
        fd_slots[destination] = _OPEN('/', flags)
    except _base_error as _acquisition_error:
        if _io[3] is None:
            _io[3] = _acquisition_error
        _io[0] = True
        _io[2] = True
        _io[4] = True
        raise
    _io[1] = False
    _fd(fd_slots[destination])
    for part in parts[1:-1]:
        if _io[0] or _io[1] or _io[10] or _overflow[1] or _attempt_digits[4] == 1:
            raise _quarantine_error
        _io[1] = True
        try:
            fd_slots[4] = _OPEN(part, flags, dir_fd=fd_slots[destination])
        except _base_error as _acquisition_error:
            if _io[3] is None:
                _io[3] = _acquisition_error
            _io[0] = True
            _io[2] = True
            _io[4] = True
            raise
        _io[1] = False
        _fd(fd_slots[4])
        previous = fd_slots[destination]
        fd_slots[destination] = fd_slots[4]
        fd_slots[4] = None
        _owned_fd = previous
        previous = None
        if _owned_fd is not None:
            if _attempt_digits[4] == 1:
                _io[6] = True
                _io[0] = True
                _io[4] = True
            else:
                _digit = 0
                while _digit < 4 and _attempt_digits[_digit] == 255:
                    _attempt_digits[_digit] = 0
                    _digit = _successors[_digit]
                _attempt_digits[_digit] = _successors[_attempt_digits[_digit]]
            try:
                _close_native(_owned_fd)
            except _base_error as _close_error:
                _io[0] = True
                _io[4] = True
                if cleanup_primary is None:
                    cleanup_primary = _close_error
                if _primary[0] is None:
                    _primary[0] = _close_error
                    _primary[1] = 'close'
                    _primary[2] = _owned_fd
                elif _primary[0] is not _close_error:
                    _error_index = _counts[0]
                    if _error_index < 64:
                        _secondary[_error_index] = _close_error
                        _phases[_error_index] = 'close'
                        _uncertain[_error_index] = _owned_fd
                        _counts[0] = _successors[_error_index]
                    else:
                        _overflow[1] = True
                        _io[0] = True
                        _io[4] = True
                        if _overflow[0] is None:
                            _overflow[0] = _close_error
            else:
                if _confirmed_digits[4] == 1:
                    _io[6] = True
                    _io[0] = True
                    _io[4] = True
                else:
                    _digit = 0
                    while _digit < 4 and _confirmed_digits[_digit] == 255:
                        _confirmed_digits[_digit] = 0
                        _digit = _successors[_digit]
                    _confirmed_digits[_digit] = _successors[_confirmed_digits[_digit]]
            if cleanup_primary is not None:
                raise cleanup_primary
    return name

def _hash_fd(descriptor: int, limit: int) -> tuple[str, int]:
    _fd(descriptor)
    schema.integer(limit, 0, schema.FILE_BYTES)
    digest, total, read_calls = hashlib.sha256(), 0, 0
    position = _LSEEK(descriptor, 0, os.SEEK_SET)
    schema.integer(position, 0, 0)
    while True:
        read_calls += 1
        schema.need(read_calls <= schema.MAX_READ_CALLS, 'hash read-call bound exceeded')
        raw = _READ(descriptor, min(schema.CHUNK_BYTES, limit + 1 - total))
        schema.need(_TYPE(raw) is bytes, 'native read returned foreign data')
        if _LEN(raw) == 0:
            break
        total += _LEN(raw)
        schema.need(total <= limit, 'file exceeds copy/hash bound')
        digest.update(raw)
    return digest.hexdigest(), total


def inspect(path: str, limit: int = schema.FILE_BYTES, *, error_owner) -> dict:
    schema.owner_state(error_owner)
    schema.path(path)
    schema.integer(limit, 0, schema.FILE_BYTES)
    _gate()
    _state = schema.owner_state(error_owner)
    _primary, _secondary, _phases, _uncertain = _state[0], _state[1], _state[2], _state[3]
    _counts, _overflow, _io = _state[4], _state[5], _state[7]
    _attempt_digits, _confirmed_digits = _io[7], _io[8]
    _successors = schema.CUSTODY_SUCCESSORS
    _quarantine_error = schema.IO_QUARANTINE_ERROR
    _base_error, _close_native = BaseException, _CLOSE
    _error_index = _digit = 0
    _owned_fd = _close_error = _acquisition_error = None
    cleanup_primary = operation_primary = None
    _fd_slots = [None] * 5
    _iterator = _owned_iterator = None
    try:
        name = _parent(path, error_owner, _fd_slots, 1)
        parent = _fd_slots[1]
        if _io[0] or _io[1] or _io[10] or _overflow[1] or _attempt_digits[4] == 1:
            raise _quarantine_error
        _io[1] = True
        try:
            _fd_slots[0] = _OPEN(name, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
        except _base_error as _acquisition_error:
            if _io[3] is None:
                _io[3] = _acquisition_error
            _io[0] = True
            _io[2] = True
            _io[4] = True
            raise
        _io[1] = False
        descriptor = _fd_slots[0]
        _fd(descriptor)
        before = _identity(_FSTAT(descriptor))
        schema.need(stat.S_ISREG(before['mode']) and before['links'] == 1 and before['size'] <= limit,
                    'file kind/link/size differs')
        digest, count = _hash_fd(descriptor, limit)
        after = _identity(_FSTAT(descriptor))
        named = _identity(_STAT(name, dir_fd=parent, follow_symlinks=False))
        schema.need(before == after == named and count == before['size'], 'file changed during bounded snapshot')
        result = {'path': path, 'sha256': digest, 'bytes': count, 'identity': after}
        schema.blob(result, limit)
        return result
    except _base_error as operation_error:
        operation_primary = operation_error
        if _primary[0] is None:
            _primary[0] = operation_error
            _primary[1] = 'inspect'
            _primary[2] = None
        elif _primary[0] is not operation_error:
            _error_index = _counts[0]
            if _error_index < 64:
                _secondary[_error_index] = operation_error
                _phases[_error_index] = 'inspect'
                _uncertain[_error_index] = None
                _counts[0] = _successors[_error_index]
            else:
                _overflow[1] = True
                _io[0] = True
                _io[4] = True
                if _overflow[0] is None:
                    _overflow[0] = operation_error
        raise
    finally:
        _owned_fd = _fd_slots[0]
        _fd_slots[0] = None
        if _owned_fd is not None:
            if _attempt_digits[4] == 1:
                _io[6] = True
                _io[0] = True
                _io[4] = True
            else:
                _digit = 0
                while _digit < 4 and _attempt_digits[_digit] == 255:
                    _attempt_digits[_digit] = 0
                    _digit = _successors[_digit]
                _attempt_digits[_digit] = _successors[_attempt_digits[_digit]]
            try:
                _close_native(_owned_fd)
            except _base_error as _close_error:
                _io[0] = True
                _io[4] = True
                if cleanup_primary is None:
                    cleanup_primary = _close_error
                if _primary[0] is None:
                    _primary[0] = _close_error
                    _primary[1] = 'close'
                    _primary[2] = _owned_fd
                elif _primary[0] is not _close_error:
                    _error_index = _counts[0]
                    if _error_index < 64:
                        _secondary[_error_index] = _close_error
                        _phases[_error_index] = 'close'
                        _uncertain[_error_index] = _owned_fd
                        _counts[0] = _successors[_error_index]
                    else:
                        _overflow[1] = True
                        _io[0] = True
                        _io[4] = True
                        if _overflow[0] is None:
                            _overflow[0] = _close_error
            else:
                if _confirmed_digits[4] == 1:
                    _io[6] = True
                    _io[0] = True
                    _io[4] = True
                else:
                    _digit = 0
                    while _digit < 4 and _confirmed_digits[_digit] == 255:
                        _confirmed_digits[_digit] = 0
                        _digit = _successors[_digit]
                    _confirmed_digits[_digit] = _successors[_confirmed_digits[_digit]]
        _owned_fd = _fd_slots[1]
        _fd_slots[1] = None
        if _owned_fd is not None:
            if _attempt_digits[4] == 1:
                _io[6] = True
                _io[0] = True
                _io[4] = True
            else:
                _digit = 0
                while _digit < 4 and _attempt_digits[_digit] == 255:
                    _attempt_digits[_digit] = 0
                    _digit = _successors[_digit]
                _attempt_digits[_digit] = _successors[_attempt_digits[_digit]]
            try:
                _close_native(_owned_fd)
            except _base_error as _close_error:
                _io[0] = True
                _io[4] = True
                if cleanup_primary is None:
                    cleanup_primary = _close_error
                if _primary[0] is None:
                    _primary[0] = _close_error
                    _primary[1] = 'close'
                    _primary[2] = _owned_fd
                elif _primary[0] is not _close_error:
                    _error_index = _counts[0]
                    if _error_index < 64:
                        _secondary[_error_index] = _close_error
                        _phases[_error_index] = 'close'
                        _uncertain[_error_index] = _owned_fd
                        _counts[0] = _successors[_error_index]
                    else:
                        _overflow[1] = True
                        _io[0] = True
                        _io[4] = True
                        if _overflow[0] is None:
                            _overflow[0] = _close_error
            else:
                if _confirmed_digits[4] == 1:
                    _io[6] = True
                    _io[0] = True
                    _io[4] = True
                else:
                    _digit = 0
                    while _digit < 4 and _confirmed_digits[_digit] == 255:
                        _confirmed_digits[_digit] = 0
                        _digit = _successors[_digit]
                    _confirmed_digits[_digit] = _successors[_confirmed_digits[_digit]]
        _owned_fd = _fd_slots[2]
        _fd_slots[2] = None
        if _owned_fd is not None:
            if _attempt_digits[4] == 1:
                _io[6] = True
                _io[0] = True
                _io[4] = True
            else:
                _digit = 0
                while _digit < 4 and _attempt_digits[_digit] == 255:
                    _attempt_digits[_digit] = 0
                    _digit = _successors[_digit]
                _attempt_digits[_digit] = _successors[_attempt_digits[_digit]]
            try:
                _close_native(_owned_fd)
            except _base_error as _close_error:
                _io[0] = True
                _io[4] = True
                if cleanup_primary is None:
                    cleanup_primary = _close_error
                if _primary[0] is None:
                    _primary[0] = _close_error
                    _primary[1] = 'close'
                    _primary[2] = _owned_fd
                elif _primary[0] is not _close_error:
                    _error_index = _counts[0]
                    if _error_index < 64:
                        _secondary[_error_index] = _close_error
                        _phases[_error_index] = 'close'
                        _uncertain[_error_index] = _owned_fd
                        _counts[0] = _successors[_error_index]
                    else:
                        _overflow[1] = True
                        _io[0] = True
                        _io[4] = True
                        if _overflow[0] is None:
                            _overflow[0] = _close_error
            else:
                if _confirmed_digits[4] == 1:
                    _io[6] = True
                    _io[0] = True
                    _io[4] = True
                else:
                    _digit = 0
                    while _digit < 4 and _confirmed_digits[_digit] == 255:
                        _confirmed_digits[_digit] = 0
                        _digit = _successors[_digit]
                    _confirmed_digits[_digit] = _successors[_confirmed_digits[_digit]]
        _owned_fd = _fd_slots[3]
        _fd_slots[3] = None
        if _owned_fd is not None:
            if _attempt_digits[4] == 1:
                _io[6] = True
                _io[0] = True
                _io[4] = True
            else:
                _digit = 0
                while _digit < 4 and _attempt_digits[_digit] == 255:
                    _attempt_digits[_digit] = 0
                    _digit = _successors[_digit]
                _attempt_digits[_digit] = _successors[_attempt_digits[_digit]]
            try:
                _close_native(_owned_fd)
            except _base_error as _close_error:
                _io[0] = True
                _io[4] = True
                if cleanup_primary is None:
                    cleanup_primary = _close_error
                if _primary[0] is None:
                    _primary[0] = _close_error
                    _primary[1] = 'close'
                    _primary[2] = _owned_fd
                elif _primary[0] is not _close_error:
                    _error_index = _counts[0]
                    if _error_index < 64:
                        _secondary[_error_index] = _close_error
                        _phases[_error_index] = 'close'
                        _uncertain[_error_index] = _owned_fd
                        _counts[0] = _successors[_error_index]
                    else:
                        _overflow[1] = True
                        _io[0] = True
                        _io[4] = True
                        if _overflow[0] is None:
                            _overflow[0] = _close_error
            else:
                if _confirmed_digits[4] == 1:
                    _io[6] = True
                    _io[0] = True
                    _io[4] = True
                else:
                    _digit = 0
                    while _digit < 4 and _confirmed_digits[_digit] == 255:
                        _confirmed_digits[_digit] = 0
                        _digit = _successors[_digit]
                    _confirmed_digits[_digit] = _successors[_confirmed_digits[_digit]]
        _owned_fd = _fd_slots[4]
        _fd_slots[4] = None
        if _owned_fd is not None:
            if _attempt_digits[4] == 1:
                _io[6] = True
                _io[0] = True
                _io[4] = True
            else:
                _digit = 0
                while _digit < 4 and _attempt_digits[_digit] == 255:
                    _attempt_digits[_digit] = 0
                    _digit = _successors[_digit]
                _attempt_digits[_digit] = _successors[_attempt_digits[_digit]]
            try:
                _close_native(_owned_fd)
            except _base_error as _close_error:
                _io[0] = True
                _io[4] = True
                if cleanup_primary is None:
                    cleanup_primary = _close_error
                if _primary[0] is None:
                    _primary[0] = _close_error
                    _primary[1] = 'close'
                    _primary[2] = _owned_fd
                elif _primary[0] is not _close_error:
                    _error_index = _counts[0]
                    if _error_index < 64:
                        _secondary[_error_index] = _close_error
                        _phases[_error_index] = 'close'
                        _uncertain[_error_index] = _owned_fd
                        _counts[0] = _successors[_error_index]
                    else:
                        _overflow[1] = True
                        _io[0] = True
                        _io[4] = True
                        if _overflow[0] is None:
                            _overflow[0] = _close_error
            else:
                if _confirmed_digits[4] == 1:
                    _io[6] = True
                    _io[0] = True
                    _io[4] = True
                else:
                    _digit = 0
                    while _digit < 4 and _confirmed_digits[_digit] == 255:
                        _confirmed_digits[_digit] = 0
                        _digit = _successors[_digit]
                    _confirmed_digits[_digit] = _successors[_confirmed_digits[_digit]]
        if operation_primary is None and cleanup_primary is not None:
            raise cleanup_primary

def verify(expected: dict, limit: int = schema.FILE_BYTES, *, error_owner) -> None:
    schema.owner_state(error_owner)
    schema.blob(expected, limit)
    schema.need(inspect(expected['path'], limit, error_owner=error_owner) == expected,
                'current source/store custody differs')


def copy_once(source: dict, destination: str, occupied_inodes: tuple, *, error_owner) -> dict:
    schema.owner_state(error_owner)
    schema.blob(source)
    schema.path(destination)
    schema.need(_TYPE(occupied_inodes) is tuple and _LEN(occupied_inodes) <= 51, 'inode collection differs')
    for pair in occupied_inodes:
        schema.need(_TYPE(pair) is tuple and _LEN(pair) == 2, 'inode pair differs')
        schema.integer(pair[0], 0, (1 << 127) - 1)
        schema.integer(pair[1], 1, (1 << 127) - 1)
    schema.need(source['path'] != destination, 'copy path aliases source')
    _gate()
    verify(source, error_owner=error_owner)
    _state = schema.owner_state(error_owner)
    _primary, _secondary, _phases, _uncertain = _state[0], _state[1], _state[2], _state[3]
    _counts, _overflow, _io = _state[4], _state[5], _state[7]
    _attempt_digits, _confirmed_digits = _io[7], _io[8]
    _successors = schema.CUSTODY_SUCCESSORS
    _quarantine_error = schema.IO_QUARANTINE_ERROR
    _base_error, _close_native = BaseException, _CLOSE
    _error_index = _digit = 0
    _owned_fd = _close_error = _acquisition_error = None
    cleanup_primary = operation_primary = None
    _fd_slots = [None] * 5
    _iterator = _owned_iterator = None
    try:
        source_name = _parent(source['path'], error_owner, _fd_slots, 3)
        source_parent = _fd_slots[3]
        target_name = _parent(destination, error_owner, _fd_slots, 2)
        target_parent = _fd_slots[2]
        if _io[0] or _io[1] or _io[10] or _overflow[1] or _attempt_digits[4] == 1:
            raise _quarantine_error
        _io[1] = True
        try:
            _fd_slots[1] = _OPEN(source_name, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=source_parent)
        except _base_error as _acquisition_error:
            if _io[3] is None:
                _io[3] = _acquisition_error
            _io[0] = True
            _io[2] = True
            _io[4] = True
            raise
        _io[1] = False
        source_fd = _fd_slots[1]
        _fd(source_fd)
        before = _identity(_FSTAT(source_fd))
        schema.need(before == source['identity'], 'source changed before copy')
        if _io[0] or _io[1] or _io[10] or _overflow[1] or _attempt_digits[4] == 1:
            raise _quarantine_error
        _io[1] = True
        try:
            _fd_slots[0] = _OPEN(target_name, os.O_RDWR | os.O_CREAT | os.O_EXCL | os.O_CLOEXEC | os.O_NOFOLLOW, 0o600, dir_fd=target_parent)
        except _base_error as _acquisition_error:
            if _io[3] is None:
                _io[3] = _acquisition_error
            _io[0] = True
            _io[2] = True
            _io[4] = True
            raise
        _io[1] = False
        target_fd = _fd_slots[0]
        _fd(target_fd)
        initial = _identity(_FSTAT(target_fd))
        schema.need(stat.S_ISREG(initial['mode']) and initial['links'] == 1 and initial['size'] == 0 and
                    stat.S_IMODE(initial['mode']) == 0o600 and
                    (initial['device'], initial['inode']) not in occupied_inodes and
                    (initial['device'], initial['inode']) != schema.inode(source), 'exclusive destination alias')
        digest, count, write_calls, read_calls = hashlib.sha256(), 0, 0, 0
        while True:
            read_calls += 1
            schema.need(read_calls <= schema.MAX_READ_CALLS, 'copy read-call bound exceeded')
            raw = _READ(source_fd, min(schema.CHUNK_BYTES, source['bytes'] + 1 - count))
            schema.need(_TYPE(raw) is bytes, 'native copy read returned foreign data')
            if _LEN(raw) == 0:
                break
            count += _LEN(raw)
            schema.need(count <= source['bytes'], 'source grew during copy')
            digest.update(raw)
            offset = 0
            while offset < _LEN(raw):
                write_calls += 1
                schema.need(write_calls <= schema.MAX_WRITE_CALLS, 'copy write-call bound exceeded')
                written = _WRITE(target_fd, raw[offset:])
                schema.integer(written, 1, _LEN(raw) - offset)
                offset += written
        schema.need(count == source['bytes'] and digest.hexdigest() == source['sha256'] and
                    _identity(_FSTAT(source_fd)) == source['identity'] and
                    _identity(_STAT(source_name, dir_fd=source_parent, follow_symlinks=False)) == source['identity'],
                    'copy source custody/bytes differ')
        _FSYNC(target_fd)
        _FSYNC(target_parent)
        before_readback = _identity(_FSTAT(target_fd))
        read_sha, read_size = _hash_fd(target_fd, schema.FILE_BYTES)
        after = _identity(_FSTAT(target_fd))
        named = _identity(_STAT(target_name, dir_fd=target_parent, follow_symlinks=False))
        schema.need(read_sha == source['sha256'] and read_size == source['bytes'] and after['links'] == 1 and
                    (after['device'], after['inode']) == (initial['device'], initial['inode']) and
                    before_readback == after == named, 'destination readback/custody differs')
        result = {'path': destination, 'sha256': read_sha, 'bytes': read_size, 'identity': after}
        schema.blob(result)
        verify(source, error_owner=error_owner)
        schema.need(inspect(destination, error_owner=error_owner) == result, 'destination path changed after copy')
        return result
    except _base_error as operation_error:
        operation_primary = operation_error
        if _primary[0] is None:
            _primary[0] = operation_error
            _primary[1] = 'copy_once'
            _primary[2] = None
        elif _primary[0] is not operation_error:
            _error_index = _counts[0]
            if _error_index < 64:
                _secondary[_error_index] = operation_error
                _phases[_error_index] = 'copy_once'
                _uncertain[_error_index] = None
                _counts[0] = _successors[_error_index]
            else:
                _overflow[1] = True
                _io[0] = True
                _io[4] = True
                if _overflow[0] is None:
                    _overflow[0] = operation_error
        raise
    finally:
        _owned_fd = _fd_slots[0]
        _fd_slots[0] = None
        if _owned_fd is not None:
            if _attempt_digits[4] == 1:
                _io[6] = True
                _io[0] = True
                _io[4] = True
            else:
                _digit = 0
                while _digit < 4 and _attempt_digits[_digit] == 255:
                    _attempt_digits[_digit] = 0
                    _digit = _successors[_digit]
                _attempt_digits[_digit] = _successors[_attempt_digits[_digit]]
            try:
                _close_native(_owned_fd)
            except _base_error as _close_error:
                _io[0] = True
                _io[4] = True
                if cleanup_primary is None:
                    cleanup_primary = _close_error
                if _primary[0] is None:
                    _primary[0] = _close_error
                    _primary[1] = 'close'
                    _primary[2] = _owned_fd
                elif _primary[0] is not _close_error:
                    _error_index = _counts[0]
                    if _error_index < 64:
                        _secondary[_error_index] = _close_error
                        _phases[_error_index] = 'close'
                        _uncertain[_error_index] = _owned_fd
                        _counts[0] = _successors[_error_index]
                    else:
                        _overflow[1] = True
                        _io[0] = True
                        _io[4] = True
                        if _overflow[0] is None:
                            _overflow[0] = _close_error
            else:
                if _confirmed_digits[4] == 1:
                    _io[6] = True
                    _io[0] = True
                    _io[4] = True
                else:
                    _digit = 0
                    while _digit < 4 and _confirmed_digits[_digit] == 255:
                        _confirmed_digits[_digit] = 0
                        _digit = _successors[_digit]
                    _confirmed_digits[_digit] = _successors[_confirmed_digits[_digit]]
        _owned_fd = _fd_slots[1]
        _fd_slots[1] = None
        if _owned_fd is not None:
            if _attempt_digits[4] == 1:
                _io[6] = True
                _io[0] = True
                _io[4] = True
            else:
                _digit = 0
                while _digit < 4 and _attempt_digits[_digit] == 255:
                    _attempt_digits[_digit] = 0
                    _digit = _successors[_digit]
                _attempt_digits[_digit] = _successors[_attempt_digits[_digit]]
            try:
                _close_native(_owned_fd)
            except _base_error as _close_error:
                _io[0] = True
                _io[4] = True
                if cleanup_primary is None:
                    cleanup_primary = _close_error
                if _primary[0] is None:
                    _primary[0] = _close_error
                    _primary[1] = 'close'
                    _primary[2] = _owned_fd
                elif _primary[0] is not _close_error:
                    _error_index = _counts[0]
                    if _error_index < 64:
                        _secondary[_error_index] = _close_error
                        _phases[_error_index] = 'close'
                        _uncertain[_error_index] = _owned_fd
                        _counts[0] = _successors[_error_index]
                    else:
                        _overflow[1] = True
                        _io[0] = True
                        _io[4] = True
                        if _overflow[0] is None:
                            _overflow[0] = _close_error
            else:
                if _confirmed_digits[4] == 1:
                    _io[6] = True
                    _io[0] = True
                    _io[4] = True
                else:
                    _digit = 0
                    while _digit < 4 and _confirmed_digits[_digit] == 255:
                        _confirmed_digits[_digit] = 0
                        _digit = _successors[_digit]
                    _confirmed_digits[_digit] = _successors[_confirmed_digits[_digit]]
        _owned_fd = _fd_slots[2]
        _fd_slots[2] = None
        if _owned_fd is not None:
            if _attempt_digits[4] == 1:
                _io[6] = True
                _io[0] = True
                _io[4] = True
            else:
                _digit = 0
                while _digit < 4 and _attempt_digits[_digit] == 255:
                    _attempt_digits[_digit] = 0
                    _digit = _successors[_digit]
                _attempt_digits[_digit] = _successors[_attempt_digits[_digit]]
            try:
                _close_native(_owned_fd)
            except _base_error as _close_error:
                _io[0] = True
                _io[4] = True
                if cleanup_primary is None:
                    cleanup_primary = _close_error
                if _primary[0] is None:
                    _primary[0] = _close_error
                    _primary[1] = 'close'
                    _primary[2] = _owned_fd
                elif _primary[0] is not _close_error:
                    _error_index = _counts[0]
                    if _error_index < 64:
                        _secondary[_error_index] = _close_error
                        _phases[_error_index] = 'close'
                        _uncertain[_error_index] = _owned_fd
                        _counts[0] = _successors[_error_index]
                    else:
                        _overflow[1] = True
                        _io[0] = True
                        _io[4] = True
                        if _overflow[0] is None:
                            _overflow[0] = _close_error
            else:
                if _confirmed_digits[4] == 1:
                    _io[6] = True
                    _io[0] = True
                    _io[4] = True
                else:
                    _digit = 0
                    while _digit < 4 and _confirmed_digits[_digit] == 255:
                        _confirmed_digits[_digit] = 0
                        _digit = _successors[_digit]
                    _confirmed_digits[_digit] = _successors[_confirmed_digits[_digit]]
        _owned_fd = _fd_slots[3]
        _fd_slots[3] = None
        if _owned_fd is not None:
            if _attempt_digits[4] == 1:
                _io[6] = True
                _io[0] = True
                _io[4] = True
            else:
                _digit = 0
                while _digit < 4 and _attempt_digits[_digit] == 255:
                    _attempt_digits[_digit] = 0
                    _digit = _successors[_digit]
                _attempt_digits[_digit] = _successors[_attempt_digits[_digit]]
            try:
                _close_native(_owned_fd)
            except _base_error as _close_error:
                _io[0] = True
                _io[4] = True
                if cleanup_primary is None:
                    cleanup_primary = _close_error
                if _primary[0] is None:
                    _primary[0] = _close_error
                    _primary[1] = 'close'
                    _primary[2] = _owned_fd
                elif _primary[0] is not _close_error:
                    _error_index = _counts[0]
                    if _error_index < 64:
                        _secondary[_error_index] = _close_error
                        _phases[_error_index] = 'close'
                        _uncertain[_error_index] = _owned_fd
                        _counts[0] = _successors[_error_index]
                    else:
                        _overflow[1] = True
                        _io[0] = True
                        _io[4] = True
                        if _overflow[0] is None:
                            _overflow[0] = _close_error
            else:
                if _confirmed_digits[4] == 1:
                    _io[6] = True
                    _io[0] = True
                    _io[4] = True
                else:
                    _digit = 0
                    while _digit < 4 and _confirmed_digits[_digit] == 255:
                        _confirmed_digits[_digit] = 0
                        _digit = _successors[_digit]
                    _confirmed_digits[_digit] = _successors[_confirmed_digits[_digit]]
        _owned_fd = _fd_slots[4]
        _fd_slots[4] = None
        if _owned_fd is not None:
            if _attempt_digits[4] == 1:
                _io[6] = True
                _io[0] = True
                _io[4] = True
            else:
                _digit = 0
                while _digit < 4 and _attempt_digits[_digit] == 255:
                    _attempt_digits[_digit] = 0
                    _digit = _successors[_digit]
                _attempt_digits[_digit] = _successors[_attempt_digits[_digit]]
            try:
                _close_native(_owned_fd)
            except _base_error as _close_error:
                _io[0] = True
                _io[4] = True
                if cleanup_primary is None:
                    cleanup_primary = _close_error
                if _primary[0] is None:
                    _primary[0] = _close_error
                    _primary[1] = 'close'
                    _primary[2] = _owned_fd
                elif _primary[0] is not _close_error:
                    _error_index = _counts[0]
                    if _error_index < 64:
                        _secondary[_error_index] = _close_error
                        _phases[_error_index] = 'close'
                        _uncertain[_error_index] = _owned_fd
                        _counts[0] = _successors[_error_index]
                    else:
                        _overflow[1] = True
                        _io[0] = True
                        _io[4] = True
                        if _overflow[0] is None:
                            _overflow[0] = _close_error
            else:
                if _confirmed_digits[4] == 1:
                    _io[6] = True
                    _io[0] = True
                    _io[4] = True
                else:
                    _digit = 0
                    while _digit < 4 and _confirmed_digits[_digit] == 255:
                        _confirmed_digits[_digit] = 0
                        _digit = _successors[_digit]
                    _confirmed_digits[_digit] = _successors[_confirmed_digits[_digit]]
        if operation_primary is None and cleanup_primary is not None:
            raise cleanup_primary

def write_once(path: str, raw: bytes, *, error_owner) -> dict:
    schema.owner_state(error_owner)
    schema.path(path)
    schema.need(_TYPE(raw) is bytes, 'exact record bytes required')
    schema.need(0 < _LEN(raw) <= schema.RECORD_BYTES, 'record bound differs')
    _gate()
    _state = schema.owner_state(error_owner)
    _primary, _secondary, _phases, _uncertain = _state[0], _state[1], _state[2], _state[3]
    _counts, _overflow, _io = _state[4], _state[5], _state[7]
    _attempt_digits, _confirmed_digits = _io[7], _io[8]
    _successors = schema.CUSTODY_SUCCESSORS
    _quarantine_error = schema.IO_QUARANTINE_ERROR
    _base_error, _close_native = BaseException, _CLOSE
    _error_index = _digit = 0
    _owned_fd = _close_error = _acquisition_error = None
    cleanup_primary = operation_primary = None
    _fd_slots = [None] * 5
    _iterator = _owned_iterator = None
    try:
        name = _parent(path, error_owner, _fd_slots, 1)
        parent = _fd_slots[1]
        if _io[0] or _io[1] or _io[10] or _overflow[1] or _attempt_digits[4] == 1:
            raise _quarantine_error
        _io[1] = True
        try:
            _fd_slots[0] = _OPEN(name, os.O_RDWR | os.O_CREAT | os.O_EXCL | os.O_CLOEXEC | os.O_NOFOLLOW, 0o600, dir_fd=parent)
        except _base_error as _acquisition_error:
            if _io[3] is None:
                _io[3] = _acquisition_error
            _io[0] = True
            _io[2] = True
            _io[4] = True
            raise
        _io[1] = False
        descriptor = _fd_slots[0]
        _fd(descriptor)
        initial = _identity(_FSTAT(descriptor))
        schema.need(stat.S_ISREG(initial['mode']) and initial['links'] == 1 and initial['size'] == 0 and
                    stat.S_IMODE(initial['mode']) == 0o600, 'exclusive record file differs')
        offset, calls = 0, 0
        while offset < _LEN(raw):
            calls += 1
            schema.need(calls <= schema.MAX_RECORD_WRITE_CALLS, 'record write-call bound exceeded')
            written = _WRITE(descriptor, raw[offset:offset + schema.CHUNK_BYTES])
            schema.integer(written, 1, min(schema.CHUNK_BYTES, _LEN(raw) - offset))
            offset += written
        _FSYNC(descriptor)
        _FSYNC(parent)
        owned = _identity(_FSTAT(descriptor))
        result = inspect(path, schema.RECORD_BYTES, error_owner=error_owner)
        schema.need(result['identity'] == owned and
                    (owned['device'], owned['inode']) == (initial['device'], initial['inode']) and
                    result['sha256'] == schema.sha(raw) and result['bytes'] == _LEN(raw), 'record readback differs')
        return result
    except _base_error as operation_error:
        operation_primary = operation_error
        if _primary[0] is None:
            _primary[0] = operation_error
            _primary[1] = 'write_once'
            _primary[2] = None
        elif _primary[0] is not operation_error:
            _error_index = _counts[0]
            if _error_index < 64:
                _secondary[_error_index] = operation_error
                _phases[_error_index] = 'write_once'
                _uncertain[_error_index] = None
                _counts[0] = _successors[_error_index]
            else:
                _overflow[1] = True
                _io[0] = True
                _io[4] = True
                if _overflow[0] is None:
                    _overflow[0] = operation_error
        raise
    finally:
        _owned_fd = _fd_slots[0]
        _fd_slots[0] = None
        if _owned_fd is not None:
            if _attempt_digits[4] == 1:
                _io[6] = True
                _io[0] = True
                _io[4] = True
            else:
                _digit = 0
                while _digit < 4 and _attempt_digits[_digit] == 255:
                    _attempt_digits[_digit] = 0
                    _digit = _successors[_digit]
                _attempt_digits[_digit] = _successors[_attempt_digits[_digit]]
            try:
                _close_native(_owned_fd)
            except _base_error as _close_error:
                _io[0] = True
                _io[4] = True
                if cleanup_primary is None:
                    cleanup_primary = _close_error
                if _primary[0] is None:
                    _primary[0] = _close_error
                    _primary[1] = 'close'
                    _primary[2] = _owned_fd
                elif _primary[0] is not _close_error:
                    _error_index = _counts[0]
                    if _error_index < 64:
                        _secondary[_error_index] = _close_error
                        _phases[_error_index] = 'close'
                        _uncertain[_error_index] = _owned_fd
                        _counts[0] = _successors[_error_index]
                    else:
                        _overflow[1] = True
                        _io[0] = True
                        _io[4] = True
                        if _overflow[0] is None:
                            _overflow[0] = _close_error
            else:
                if _confirmed_digits[4] == 1:
                    _io[6] = True
                    _io[0] = True
                    _io[4] = True
                else:
                    _digit = 0
                    while _digit < 4 and _confirmed_digits[_digit] == 255:
                        _confirmed_digits[_digit] = 0
                        _digit = _successors[_digit]
                    _confirmed_digits[_digit] = _successors[_confirmed_digits[_digit]]
        _owned_fd = _fd_slots[1]
        _fd_slots[1] = None
        if _owned_fd is not None:
            if _attempt_digits[4] == 1:
                _io[6] = True
                _io[0] = True
                _io[4] = True
            else:
                _digit = 0
                while _digit < 4 and _attempt_digits[_digit] == 255:
                    _attempt_digits[_digit] = 0
                    _digit = _successors[_digit]
                _attempt_digits[_digit] = _successors[_attempt_digits[_digit]]
            try:
                _close_native(_owned_fd)
            except _base_error as _close_error:
                _io[0] = True
                _io[4] = True
                if cleanup_primary is None:
                    cleanup_primary = _close_error
                if _primary[0] is None:
                    _primary[0] = _close_error
                    _primary[1] = 'close'
                    _primary[2] = _owned_fd
                elif _primary[0] is not _close_error:
                    _error_index = _counts[0]
                    if _error_index < 64:
                        _secondary[_error_index] = _close_error
                        _phases[_error_index] = 'close'
                        _uncertain[_error_index] = _owned_fd
                        _counts[0] = _successors[_error_index]
                    else:
                        _overflow[1] = True
                        _io[0] = True
                        _io[4] = True
                        if _overflow[0] is None:
                            _overflow[0] = _close_error
            else:
                if _confirmed_digits[4] == 1:
                    _io[6] = True
                    _io[0] = True
                    _io[4] = True
                else:
                    _digit = 0
                    while _digit < 4 and _confirmed_digits[_digit] == 255:
                        _confirmed_digits[_digit] = 0
                        _digit = _successors[_digit]
                    _confirmed_digits[_digit] = _successors[_confirmed_digits[_digit]]
        _owned_fd = _fd_slots[2]
        _fd_slots[2] = None
        if _owned_fd is not None:
            if _attempt_digits[4] == 1:
                _io[6] = True
                _io[0] = True
                _io[4] = True
            else:
                _digit = 0
                while _digit < 4 and _attempt_digits[_digit] == 255:
                    _attempt_digits[_digit] = 0
                    _digit = _successors[_digit]
                _attempt_digits[_digit] = _successors[_attempt_digits[_digit]]
            try:
                _close_native(_owned_fd)
            except _base_error as _close_error:
                _io[0] = True
                _io[4] = True
                if cleanup_primary is None:
                    cleanup_primary = _close_error
                if _primary[0] is None:
                    _primary[0] = _close_error
                    _primary[1] = 'close'
                    _primary[2] = _owned_fd
                elif _primary[0] is not _close_error:
                    _error_index = _counts[0]
                    if _error_index < 64:
                        _secondary[_error_index] = _close_error
                        _phases[_error_index] = 'close'
                        _uncertain[_error_index] = _owned_fd
                        _counts[0] = _successors[_error_index]
                    else:
                        _overflow[1] = True
                        _io[0] = True
                        _io[4] = True
                        if _overflow[0] is None:
                            _overflow[0] = _close_error
            else:
                if _confirmed_digits[4] == 1:
                    _io[6] = True
                    _io[0] = True
                    _io[4] = True
                else:
                    _digit = 0
                    while _digit < 4 and _confirmed_digits[_digit] == 255:
                        _confirmed_digits[_digit] = 0
                        _digit = _successors[_digit]
                    _confirmed_digits[_digit] = _successors[_confirmed_digits[_digit]]
        _owned_fd = _fd_slots[3]
        _fd_slots[3] = None
        if _owned_fd is not None:
            if _attempt_digits[4] == 1:
                _io[6] = True
                _io[0] = True
                _io[4] = True
            else:
                _digit = 0
                while _digit < 4 and _attempt_digits[_digit] == 255:
                    _attempt_digits[_digit] = 0
                    _digit = _successors[_digit]
                _attempt_digits[_digit] = _successors[_attempt_digits[_digit]]
            try:
                _close_native(_owned_fd)
            except _base_error as _close_error:
                _io[0] = True
                _io[4] = True
                if cleanup_primary is None:
                    cleanup_primary = _close_error
                if _primary[0] is None:
                    _primary[0] = _close_error
                    _primary[1] = 'close'
                    _primary[2] = _owned_fd
                elif _primary[0] is not _close_error:
                    _error_index = _counts[0]
                    if _error_index < 64:
                        _secondary[_error_index] = _close_error
                        _phases[_error_index] = 'close'
                        _uncertain[_error_index] = _owned_fd
                        _counts[0] = _successors[_error_index]
                    else:
                        _overflow[1] = True
                        _io[0] = True
                        _io[4] = True
                        if _overflow[0] is None:
                            _overflow[0] = _close_error
            else:
                if _confirmed_digits[4] == 1:
                    _io[6] = True
                    _io[0] = True
                    _io[4] = True
                else:
                    _digit = 0
                    while _digit < 4 and _confirmed_digits[_digit] == 255:
                        _confirmed_digits[_digit] = 0
                        _digit = _successors[_digit]
                    _confirmed_digits[_digit] = _successors[_confirmed_digits[_digit]]
        _owned_fd = _fd_slots[4]
        _fd_slots[4] = None
        if _owned_fd is not None:
            if _attempt_digits[4] == 1:
                _io[6] = True
                _io[0] = True
                _io[4] = True
            else:
                _digit = 0
                while _digit < 4 and _attempt_digits[_digit] == 255:
                    _attempt_digits[_digit] = 0
                    _digit = _successors[_digit]
                _attempt_digits[_digit] = _successors[_attempt_digits[_digit]]
            try:
                _close_native(_owned_fd)
            except _base_error as _close_error:
                _io[0] = True
                _io[4] = True
                if cleanup_primary is None:
                    cleanup_primary = _close_error
                if _primary[0] is None:
                    _primary[0] = _close_error
                    _primary[1] = 'close'
                    _primary[2] = _owned_fd
                elif _primary[0] is not _close_error:
                    _error_index = _counts[0]
                    if _error_index < 64:
                        _secondary[_error_index] = _close_error
                        _phases[_error_index] = 'close'
                        _uncertain[_error_index] = _owned_fd
                        _counts[0] = _successors[_error_index]
                    else:
                        _overflow[1] = True
                        _io[0] = True
                        _io[4] = True
                        if _overflow[0] is None:
                            _overflow[0] = _close_error
            else:
                if _confirmed_digits[4] == 1:
                    _io[6] = True
                    _io[0] = True
                    _io[4] = True
                else:
                    _digit = 0
                    while _digit < 4 and _confirmed_digits[_digit] == 255:
                        _confirmed_digits[_digit] = 0
                        _digit = _successors[_digit]
                    _confirmed_digits[_digit] = _successors[_confirmed_digits[_digit]]
        if operation_primary is None and cleanup_primary is not None:
            raise cleanup_primary

def read_verified(expected: dict, limit: int = schema.RECORD_BYTES, *, error_owner) -> bytes:
    schema.owner_state(error_owner)
    schema.integer(limit, 1, schema.RAW_RESULT_BYTES)
    schema.blob(expected, limit)
    _gate()
    verify(expected, limit, error_owner=error_owner)
    _state = schema.owner_state(error_owner)
    _primary, _secondary, _phases, _uncertain = _state[0], _state[1], _state[2], _state[3]
    _counts, _overflow, _io = _state[4], _state[5], _state[7]
    _attempt_digits, _confirmed_digits = _io[7], _io[8]
    _successors = schema.CUSTODY_SUCCESSORS
    _quarantine_error = schema.IO_QUARANTINE_ERROR
    _base_error, _close_native = BaseException, _CLOSE
    _error_index = _digit = 0
    _owned_fd = _close_error = _acquisition_error = None
    cleanup_primary = operation_primary = None
    _fd_slots = [None] * 5
    _iterator = _owned_iterator = None
    try:
        name = _parent(expected['path'], error_owner, _fd_slots, 1)
        parent = _fd_slots[1]
        if _io[0] or _io[1] or _io[10] or _overflow[1] or _attempt_digits[4] == 1:
            raise _quarantine_error
        _io[1] = True
        try:
            _fd_slots[0] = _OPEN(name, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
        except _base_error as _acquisition_error:
            if _io[3] is None:
                _io[3] = _acquisition_error
            _io[0] = True
            _io[2] = True
            _io[4] = True
            raise
        _io[1] = False
        descriptor = _fd_slots[0]
        _fd(descriptor)
        schema.need(_identity(_FSTAT(descriptor)) == expected['identity'], 'evidence changed before read')
        chunks, count, calls = [], 0, 0
        while True:
            calls += 1
            schema.need(calls <= schema.MAX_READ_CALLS, 'evidence read-call bound exceeded')
            raw = _READ(descriptor, min(schema.CHUNK_BYTES, limit + 1 - count))
            schema.need(_TYPE(raw) is bytes, 'native evidence read returned foreign data')
            if _LEN(raw) == 0:
                break
            count += _LEN(raw)
            schema.need(count <= limit, 'evidence byte bound exceeded')
            chunks.append(raw)
        result = b''.join(chunks)
        schema.need(count == expected['bytes'] and schema.sha(result) == expected['sha256'] and
                    _identity(_FSTAT(descriptor)) == expected['identity'] and
                    _identity(_STAT(name, dir_fd=parent, follow_symlinks=False)) == expected['identity'],
                    'retained evidence bytes/custody differ')
        verify(expected, limit, error_owner=error_owner)
        return result
    except _base_error as operation_error:
        operation_primary = operation_error
        if _primary[0] is None:
            _primary[0] = operation_error
            _primary[1] = 'read_verified'
            _primary[2] = None
        elif _primary[0] is not operation_error:
            _error_index = _counts[0]
            if _error_index < 64:
                _secondary[_error_index] = operation_error
                _phases[_error_index] = 'read_verified'
                _uncertain[_error_index] = None
                _counts[0] = _successors[_error_index]
            else:
                _overflow[1] = True
                _io[0] = True
                _io[4] = True
                if _overflow[0] is None:
                    _overflow[0] = operation_error
        raise
    finally:
        _owned_fd = _fd_slots[0]
        _fd_slots[0] = None
        if _owned_fd is not None:
            if _attempt_digits[4] == 1:
                _io[6] = True
                _io[0] = True
                _io[4] = True
            else:
                _digit = 0
                while _digit < 4 and _attempt_digits[_digit] == 255:
                    _attempt_digits[_digit] = 0
                    _digit = _successors[_digit]
                _attempt_digits[_digit] = _successors[_attempt_digits[_digit]]
            try:
                _close_native(_owned_fd)
            except _base_error as _close_error:
                _io[0] = True
                _io[4] = True
                if cleanup_primary is None:
                    cleanup_primary = _close_error
                if _primary[0] is None:
                    _primary[0] = _close_error
                    _primary[1] = 'close'
                    _primary[2] = _owned_fd
                elif _primary[0] is not _close_error:
                    _error_index = _counts[0]
                    if _error_index < 64:
                        _secondary[_error_index] = _close_error
                        _phases[_error_index] = 'close'
                        _uncertain[_error_index] = _owned_fd
                        _counts[0] = _successors[_error_index]
                    else:
                        _overflow[1] = True
                        _io[0] = True
                        _io[4] = True
                        if _overflow[0] is None:
                            _overflow[0] = _close_error
            else:
                if _confirmed_digits[4] == 1:
                    _io[6] = True
                    _io[0] = True
                    _io[4] = True
                else:
                    _digit = 0
                    while _digit < 4 and _confirmed_digits[_digit] == 255:
                        _confirmed_digits[_digit] = 0
                        _digit = _successors[_digit]
                    _confirmed_digits[_digit] = _successors[_confirmed_digits[_digit]]
        _owned_fd = _fd_slots[1]
        _fd_slots[1] = None
        if _owned_fd is not None:
            if _attempt_digits[4] == 1:
                _io[6] = True
                _io[0] = True
                _io[4] = True
            else:
                _digit = 0
                while _digit < 4 and _attempt_digits[_digit] == 255:
                    _attempt_digits[_digit] = 0
                    _digit = _successors[_digit]
                _attempt_digits[_digit] = _successors[_attempt_digits[_digit]]
            try:
                _close_native(_owned_fd)
            except _base_error as _close_error:
                _io[0] = True
                _io[4] = True
                if cleanup_primary is None:
                    cleanup_primary = _close_error
                if _primary[0] is None:
                    _primary[0] = _close_error
                    _primary[1] = 'close'
                    _primary[2] = _owned_fd
                elif _primary[0] is not _close_error:
                    _error_index = _counts[0]
                    if _error_index < 64:
                        _secondary[_error_index] = _close_error
                        _phases[_error_index] = 'close'
                        _uncertain[_error_index] = _owned_fd
                        _counts[0] = _successors[_error_index]
                    else:
                        _overflow[1] = True
                        _io[0] = True
                        _io[4] = True
                        if _overflow[0] is None:
                            _overflow[0] = _close_error
            else:
                if _confirmed_digits[4] == 1:
                    _io[6] = True
                    _io[0] = True
                    _io[4] = True
                else:
                    _digit = 0
                    while _digit < 4 and _confirmed_digits[_digit] == 255:
                        _confirmed_digits[_digit] = 0
                        _digit = _successors[_digit]
                    _confirmed_digits[_digit] = _successors[_confirmed_digits[_digit]]
        _owned_fd = _fd_slots[2]
        _fd_slots[2] = None
        if _owned_fd is not None:
            if _attempt_digits[4] == 1:
                _io[6] = True
                _io[0] = True
                _io[4] = True
            else:
                _digit = 0
                while _digit < 4 and _attempt_digits[_digit] == 255:
                    _attempt_digits[_digit] = 0
                    _digit = _successors[_digit]
                _attempt_digits[_digit] = _successors[_attempt_digits[_digit]]
            try:
                _close_native(_owned_fd)
            except _base_error as _close_error:
                _io[0] = True
                _io[4] = True
                if cleanup_primary is None:
                    cleanup_primary = _close_error
                if _primary[0] is None:
                    _primary[0] = _close_error
                    _primary[1] = 'close'
                    _primary[2] = _owned_fd
                elif _primary[0] is not _close_error:
                    _error_index = _counts[0]
                    if _error_index < 64:
                        _secondary[_error_index] = _close_error
                        _phases[_error_index] = 'close'
                        _uncertain[_error_index] = _owned_fd
                        _counts[0] = _successors[_error_index]
                    else:
                        _overflow[1] = True
                        _io[0] = True
                        _io[4] = True
                        if _overflow[0] is None:
                            _overflow[0] = _close_error
            else:
                if _confirmed_digits[4] == 1:
                    _io[6] = True
                    _io[0] = True
                    _io[4] = True
                else:
                    _digit = 0
                    while _digit < 4 and _confirmed_digits[_digit] == 255:
                        _confirmed_digits[_digit] = 0
                        _digit = _successors[_digit]
                    _confirmed_digits[_digit] = _successors[_confirmed_digits[_digit]]
        _owned_fd = _fd_slots[3]
        _fd_slots[3] = None
        if _owned_fd is not None:
            if _attempt_digits[4] == 1:
                _io[6] = True
                _io[0] = True
                _io[4] = True
            else:
                _digit = 0
                while _digit < 4 and _attempt_digits[_digit] == 255:
                    _attempt_digits[_digit] = 0
                    _digit = _successors[_digit]
                _attempt_digits[_digit] = _successors[_attempt_digits[_digit]]
            try:
                _close_native(_owned_fd)
            except _base_error as _close_error:
                _io[0] = True
                _io[4] = True
                if cleanup_primary is None:
                    cleanup_primary = _close_error
                if _primary[0] is None:
                    _primary[0] = _close_error
                    _primary[1] = 'close'
                    _primary[2] = _owned_fd
                elif _primary[0] is not _close_error:
                    _error_index = _counts[0]
                    if _error_index < 64:
                        _secondary[_error_index] = _close_error
                        _phases[_error_index] = 'close'
                        _uncertain[_error_index] = _owned_fd
                        _counts[0] = _successors[_error_index]
                    else:
                        _overflow[1] = True
                        _io[0] = True
                        _io[4] = True
                        if _overflow[0] is None:
                            _overflow[0] = _close_error
            else:
                if _confirmed_digits[4] == 1:
                    _io[6] = True
                    _io[0] = True
                    _io[4] = True
                else:
                    _digit = 0
                    while _digit < 4 and _confirmed_digits[_digit] == 255:
                        _confirmed_digits[_digit] = 0
                        _digit = _successors[_digit]
                    _confirmed_digits[_digit] = _successors[_confirmed_digits[_digit]]
        _owned_fd = _fd_slots[4]
        _fd_slots[4] = None
        if _owned_fd is not None:
            if _attempt_digits[4] == 1:
                _io[6] = True
                _io[0] = True
                _io[4] = True
            else:
                _digit = 0
                while _digit < 4 and _attempt_digits[_digit] == 255:
                    _attempt_digits[_digit] = 0
                    _digit = _successors[_digit]
                _attempt_digits[_digit] = _successors[_attempt_digits[_digit]]
            try:
                _close_native(_owned_fd)
            except _base_error as _close_error:
                _io[0] = True
                _io[4] = True
                if cleanup_primary is None:
                    cleanup_primary = _close_error
                if _primary[0] is None:
                    _primary[0] = _close_error
                    _primary[1] = 'close'
                    _primary[2] = _owned_fd
                elif _primary[0] is not _close_error:
                    _error_index = _counts[0]
                    if _error_index < 64:
                        _secondary[_error_index] = _close_error
                        _phases[_error_index] = 'close'
                        _uncertain[_error_index] = _owned_fd
                        _counts[0] = _successors[_error_index]
                    else:
                        _overflow[1] = True
                        _io[0] = True
                        _io[4] = True
                        if _overflow[0] is None:
                            _overflow[0] = _close_error
            else:
                if _confirmed_digits[4] == 1:
                    _io[6] = True
                    _io[0] = True
                    _io[4] = True
                else:
                    _digit = 0
                    while _digit < 4 and _confirmed_digits[_digit] == 255:
                        _confirmed_digits[_digit] = 0
                        _digit = _successors[_digit]
                    _confirmed_digits[_digit] = _successors[_confirmed_digits[_digit]]
        if operation_primary is None and cleanup_primary is not None:
            raise cleanup_primary

def require_entries(directory: str, expected_names: tuple[str, ...], *, error_owner) -> None:
    schema.owner_state(error_owner)
    schema.path(directory)
    schema.need(_TYPE(expected_names) is tuple and _LEN(expected_names) <= 7, 'census tuple differs')
    # Validate all names before hashing, equality, membership, or set creation.
    for name in expected_names:
        schema.text(name, 256)
        schema.need(0 < _LEN(name) and '/' not in name and name not in ('.', '..'), 'census name differs')
    schema.need(_LEN(set(expected_names)) == _LEN(expected_names), 'duplicate census name')
    _gate()
    _state = schema.owner_state(error_owner)
    _primary, _secondary, _phases, _uncertain = _state[0], _state[1], _state[2], _state[3]
    _counts, _overflow, _io = _state[4], _state[5], _state[7]
    _attempt_digits, _confirmed_digits = _io[7], _io[8]
    _successors = schema.CUSTODY_SUCCESSORS
    _quarantine_error = schema.IO_QUARANTINE_ERROR
    _base_error, _close_native = BaseException, _CLOSE
    _error_index = _digit = 0
    _owned_fd = _close_error = _acquisition_error = None
    cleanup_primary = operation_primary = None
    _fd_slots = [None] * 5
    _iterator = _owned_iterator = None
    try:
        name = _parent(directory, error_owner, _fd_slots, 1)
        parent = _fd_slots[1]
        if _io[0] or _io[1] or _io[10] or _overflow[1] or _attempt_digits[4] == 1:
            raise _quarantine_error
        _io[1] = True
        try:
            _fd_slots[0] = _OPEN(name, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW | os.O_DIRECTORY, dir_fd=parent)
        except _base_error as _acquisition_error:
            if _io[3] is None:
                _io[3] = _acquisition_error
            _io[0] = True
            _io[2] = True
            _io[4] = True
            raise
        _io[1] = False
        descriptor = _fd_slots[0]
        _fd(descriptor)
        before = _identity(_FSTAT(descriptor))
        schema.need(stat.S_ISDIR(before['mode']), 'copy root is not a directory')
        names = []
        if _io[0] or _io[1] or _io[10] or _overflow[1] or _attempt_digits[4] == 1:
            raise _quarantine_error
        _io[1] = True
        try:
            _iterator = _SCANDIR(descriptor)
        except _base_error as _acquisition_error:
            if _io[3] is None:
                _io[3] = _acquisition_error
            _io[0] = True
            _io[2] = True
            _io[4] = True
            raise
        _io[1] = False
        for entry in _iterator:
            # Exact native entry guard remains before its attribute access.
            schema.need(_TYPE(entry) is os.DirEntry, 'native directory entry type differs')
            entry_name = entry.name
            schema.text(entry_name, 256)
            names.append(entry_name)
            schema.need(_LEN(names) <= 7, 'copy root entry bound exceeded')
        _owned_iterator = _iterator
        _iterator = None
        if _owned_iterator is not None:
            try:
                _owned_iterator.close()
            except _base_error as _close_error:
                if _io[5] is None:
                    _io[5] = _owned_iterator
                _io[0] = True
                _io[4] = True
                if cleanup_primary is None:
                    cleanup_primary = _close_error
                if _primary[0] is None:
                    _primary[0] = _close_error
                    _primary[1] = 'scandir-close'
                    _primary[2] = None
                elif _primary[0] is not _close_error:
                    _error_index = _counts[0]
                    if _error_index < 64:
                        _secondary[_error_index] = _close_error
                        _phases[_error_index] = 'scandir-close'
                        _uncertain[_error_index] = None
                        _counts[0] = _successors[_error_index]
                    else:
                        _overflow[1] = True
                        _io[0] = True
                        _io[4] = True
                        if _overflow[0] is None:
                            _overflow[0] = _close_error
            else:
                # A normal/no-op return after a delivered body error cannot
                # invoke the selected release premise or clear uncertainty.
                if operation_primary is None and not _io[0] and _io[5] is None:
                    _io[9] = True
                _io[4] = True
        if cleanup_primary is not None:
            raise cleanup_primary
        schema.need(set(names) == set(expected_names) and before == _identity(_FSTAT(descriptor)) ==
                    _identity(_STAT(name, dir_fd=parent, follow_symlinks=False)), 'copy root entries/custody differ')
    except _base_error as operation_error:
        operation_primary = operation_error
        # Any body failure may follow an ignored closedir result, including
        # iterator OSError/MemoryError before an explicit close becomes a no-op.
        # Root the exact error first; quarantine and retain stream uncertainty
        # before cleanup or any optional helper/reporting can run.
        _io[0] = True
        _io[4] = True
        if _io[5] is None:
            if _iterator is not None:
                _io[5] = _iterator
            elif _owned_iterator is not None:
                _io[5] = _owned_iterator
        if _primary[0] is None:
            _primary[0] = operation_error
            _primary[1] = 'require_entries'
            _primary[2] = None
        elif _primary[0] is not operation_error:
            _error_index = _counts[0]
            if _error_index < 64:
                _secondary[_error_index] = operation_error
                _phases[_error_index] = 'require_entries'
                _uncertain[_error_index] = None
                _counts[0] = _successors[_error_index]
            else:
                _overflow[1] = True
                _io[0] = True
                _io[4] = True
                if _overflow[0] is None:
                    _overflow[0] = operation_error
        raise
    finally:
        _owned_iterator = _iterator
        _iterator = None
        if _owned_iterator is not None:
            try:
                _owned_iterator.close()
            except _base_error as _close_error:
                if _io[5] is None:
                    _io[5] = _owned_iterator
                _io[0] = True
                _io[4] = True
                if cleanup_primary is None:
                    cleanup_primary = _close_error
                if _primary[0] is None:
                    _primary[0] = _close_error
                    _primary[1] = 'scandir-close'
                    _primary[2] = None
                elif _primary[0] is not _close_error:
                    _error_index = _counts[0]
                    if _error_index < 64:
                        _secondary[_error_index] = _close_error
                        _phases[_error_index] = 'scandir-close'
                        _uncertain[_error_index] = None
                        _counts[0] = _successors[_error_index]
                    else:
                        _overflow[1] = True
                        _io[0] = True
                        _io[4] = True
                        if _overflow[0] is None:
                            _overflow[0] = _close_error
            else:
                # A normal/no-op return after a delivered body error cannot
                # invoke the selected release premise or clear uncertainty.
                if operation_primary is None and not _io[0] and _io[5] is None:
                    _io[9] = True
                _io[4] = True
        _owned_fd = _fd_slots[0]
        _fd_slots[0] = None
        if _owned_fd is not None:
            if _attempt_digits[4] == 1:
                _io[6] = True
                _io[0] = True
                _io[4] = True
            else:
                _digit = 0
                while _digit < 4 and _attempt_digits[_digit] == 255:
                    _attempt_digits[_digit] = 0
                    _digit = _successors[_digit]
                _attempt_digits[_digit] = _successors[_attempt_digits[_digit]]
            try:
                _close_native(_owned_fd)
            except _base_error as _close_error:
                _io[0] = True
                _io[4] = True
                if cleanup_primary is None:
                    cleanup_primary = _close_error
                if _primary[0] is None:
                    _primary[0] = _close_error
                    _primary[1] = 'close'
                    _primary[2] = _owned_fd
                elif _primary[0] is not _close_error:
                    _error_index = _counts[0]
                    if _error_index < 64:
                        _secondary[_error_index] = _close_error
                        _phases[_error_index] = 'close'
                        _uncertain[_error_index] = _owned_fd
                        _counts[0] = _successors[_error_index]
                    else:
                        _overflow[1] = True
                        _io[0] = True
                        _io[4] = True
                        if _overflow[0] is None:
                            _overflow[0] = _close_error
            else:
                if _confirmed_digits[4] == 1:
                    _io[6] = True
                    _io[0] = True
                    _io[4] = True
                else:
                    _digit = 0
                    while _digit < 4 and _confirmed_digits[_digit] == 255:
                        _confirmed_digits[_digit] = 0
                        _digit = _successors[_digit]
                    _confirmed_digits[_digit] = _successors[_confirmed_digits[_digit]]
        _owned_fd = _fd_slots[1]
        _fd_slots[1] = None
        if _owned_fd is not None:
            if _attempt_digits[4] == 1:
                _io[6] = True
                _io[0] = True
                _io[4] = True
            else:
                _digit = 0
                while _digit < 4 and _attempt_digits[_digit] == 255:
                    _attempt_digits[_digit] = 0
                    _digit = _successors[_digit]
                _attempt_digits[_digit] = _successors[_attempt_digits[_digit]]
            try:
                _close_native(_owned_fd)
            except _base_error as _close_error:
                _io[0] = True
                _io[4] = True
                if cleanup_primary is None:
                    cleanup_primary = _close_error
                if _primary[0] is None:
                    _primary[0] = _close_error
                    _primary[1] = 'close'
                    _primary[2] = _owned_fd
                elif _primary[0] is not _close_error:
                    _error_index = _counts[0]
                    if _error_index < 64:
                        _secondary[_error_index] = _close_error
                        _phases[_error_index] = 'close'
                        _uncertain[_error_index] = _owned_fd
                        _counts[0] = _successors[_error_index]
                    else:
                        _overflow[1] = True
                        _io[0] = True
                        _io[4] = True
                        if _overflow[0] is None:
                            _overflow[0] = _close_error
            else:
                if _confirmed_digits[4] == 1:
                    _io[6] = True
                    _io[0] = True
                    _io[4] = True
                else:
                    _digit = 0
                    while _digit < 4 and _confirmed_digits[_digit] == 255:
                        _confirmed_digits[_digit] = 0
                        _digit = _successors[_digit]
                    _confirmed_digits[_digit] = _successors[_confirmed_digits[_digit]]
        _owned_fd = _fd_slots[2]
        _fd_slots[2] = None
        if _owned_fd is not None:
            if _attempt_digits[4] == 1:
                _io[6] = True
                _io[0] = True
                _io[4] = True
            else:
                _digit = 0
                while _digit < 4 and _attempt_digits[_digit] == 255:
                    _attempt_digits[_digit] = 0
                    _digit = _successors[_digit]
                _attempt_digits[_digit] = _successors[_attempt_digits[_digit]]
            try:
                _close_native(_owned_fd)
            except _base_error as _close_error:
                _io[0] = True
                _io[4] = True
                if cleanup_primary is None:
                    cleanup_primary = _close_error
                if _primary[0] is None:
                    _primary[0] = _close_error
                    _primary[1] = 'close'
                    _primary[2] = _owned_fd
                elif _primary[0] is not _close_error:
                    _error_index = _counts[0]
                    if _error_index < 64:
                        _secondary[_error_index] = _close_error
                        _phases[_error_index] = 'close'
                        _uncertain[_error_index] = _owned_fd
                        _counts[0] = _successors[_error_index]
                    else:
                        _overflow[1] = True
                        _io[0] = True
                        _io[4] = True
                        if _overflow[0] is None:
                            _overflow[0] = _close_error
            else:
                if _confirmed_digits[4] == 1:
                    _io[6] = True
                    _io[0] = True
                    _io[4] = True
                else:
                    _digit = 0
                    while _digit < 4 and _confirmed_digits[_digit] == 255:
                        _confirmed_digits[_digit] = 0
                        _digit = _successors[_digit]
                    _confirmed_digits[_digit] = _successors[_confirmed_digits[_digit]]
        _owned_fd = _fd_slots[3]
        _fd_slots[3] = None
        if _owned_fd is not None:
            if _attempt_digits[4] == 1:
                _io[6] = True
                _io[0] = True
                _io[4] = True
            else:
                _digit = 0
                while _digit < 4 and _attempt_digits[_digit] == 255:
                    _attempt_digits[_digit] = 0
                    _digit = _successors[_digit]
                _attempt_digits[_digit] = _successors[_attempt_digits[_digit]]
            try:
                _close_native(_owned_fd)
            except _base_error as _close_error:
                _io[0] = True
                _io[4] = True
                if cleanup_primary is None:
                    cleanup_primary = _close_error
                if _primary[0] is None:
                    _primary[0] = _close_error
                    _primary[1] = 'close'
                    _primary[2] = _owned_fd
                elif _primary[0] is not _close_error:
                    _error_index = _counts[0]
                    if _error_index < 64:
                        _secondary[_error_index] = _close_error
                        _phases[_error_index] = 'close'
                        _uncertain[_error_index] = _owned_fd
                        _counts[0] = _successors[_error_index]
                    else:
                        _overflow[1] = True
                        _io[0] = True
                        _io[4] = True
                        if _overflow[0] is None:
                            _overflow[0] = _close_error
            else:
                if _confirmed_digits[4] == 1:
                    _io[6] = True
                    _io[0] = True
                    _io[4] = True
                else:
                    _digit = 0
                    while _digit < 4 and _confirmed_digits[_digit] == 255:
                        _confirmed_digits[_digit] = 0
                        _digit = _successors[_digit]
                    _confirmed_digits[_digit] = _successors[_confirmed_digits[_digit]]
        _owned_fd = _fd_slots[4]
        _fd_slots[4] = None
        if _owned_fd is not None:
            if _attempt_digits[4] == 1:
                _io[6] = True
                _io[0] = True
                _io[4] = True
            else:
                _digit = 0
                while _digit < 4 and _attempt_digits[_digit] == 255:
                    _attempt_digits[_digit] = 0
                    _digit = _successors[_digit]
                _attempt_digits[_digit] = _successors[_attempt_digits[_digit]]
            try:
                _close_native(_owned_fd)
            except _base_error as _close_error:
                _io[0] = True
                _io[4] = True
                if cleanup_primary is None:
                    cleanup_primary = _close_error
                if _primary[0] is None:
                    _primary[0] = _close_error
                    _primary[1] = 'close'
                    _primary[2] = _owned_fd
                elif _primary[0] is not _close_error:
                    _error_index = _counts[0]
                    if _error_index < 64:
                        _secondary[_error_index] = _close_error
                        _phases[_error_index] = 'close'
                        _uncertain[_error_index] = _owned_fd
                        _counts[0] = _successors[_error_index]
                    else:
                        _overflow[1] = True
                        _io[0] = True
                        _io[4] = True
                        if _overflow[0] is None:
                            _overflow[0] = _close_error
            else:
                if _confirmed_digits[4] == 1:
                    _io[6] = True
                    _io[0] = True
                    _io[4] = True
                else:
                    _digit = 0
                    while _digit < 4 and _confirmed_digits[_digit] == 255:
                        _confirmed_digits[_digit] = 0
                        _digit = _successors[_digit]
                    _confirmed_digits[_digit] = _successors[_confirmed_digits[_digit]]
        if operation_primary is None and cleanup_primary is not None:
            raise cleanup_primary

# Separately versioned successor APIs. Original APIs above keep their exact bytes.
COMPLETE_IO_CONFIGURATION = None
COMPLETE_IO_VERSION_V3 = 'h25-complete-custody-io-v3'
COMPLETE_READ_BYTES_V3 = 64 * 1024 * 1024
OBSERVATION_WRITE_BYTES_V3 = 4 * 1024 * 1024

def _complete_io_gate_v3():
    schema.exact(COMPLETE_IO_CONFIGURATION, ('schema', 'source_review_sha256', 'domain_review_sha256'))
    schema.text(COMPLETE_IO_CONFIGURATION['schema'], 64)
    schema.need(COMPLETE_IO_CONFIGURATION['schema'] == COMPLETE_IO_VERSION_V3, 'complete IO version gate absent')
    schema.digest(COMPLETE_IO_CONFIGURATION['source_review_sha256'])
    schema.digest(COMPLETE_IO_CONFIGURATION['domain_review_sha256'])

def read_verified_complete_v3(expected: dict, limit: int = schema.RECORD_BYTES, *, error_owner) -> bytes:
    schema.owner_state(error_owner)
    schema.integer(limit, 1, COMPLETE_READ_BYTES_V3)
    _complete_io_gate_v3()
    schema.blob(expected, limit)
    _gate()
    verify(expected, limit, error_owner=error_owner)
    _state = schema.owner_state(error_owner)
    _primary, _secondary, _phases, _uncertain = _state[0], _state[1], _state[2], _state[3]
    _counts, _overflow, _io = _state[4], _state[5], _state[7]
    _attempt_digits, _confirmed_digits = _io[7], _io[8]
    _successors = schema.CUSTODY_SUCCESSORS
    _quarantine_error = schema.IO_QUARANTINE_ERROR
    _base_error, _close_native = BaseException, _CLOSE
    _error_index = _digit = 0
    _owned_fd = _close_error = _acquisition_error = None
    cleanup_primary = operation_primary = None
    _fd_slots = [None] * 5
    _iterator = _owned_iterator = None
    try:
        name = _parent(expected['path'], error_owner, _fd_slots, 1)
        parent = _fd_slots[1]
        if _io[0] or _io[1] or _io[10] or _overflow[1] or _attempt_digits[4] == 1:
            raise _quarantine_error
        _io[1] = True
        try:
            _fd_slots[0] = _OPEN(name, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
        except _base_error as _acquisition_error:
            if _io[3] is None:
                _io[3] = _acquisition_error
            _io[0] = True
            _io[2] = True
            _io[4] = True
            raise
        _io[1] = False
        descriptor = _fd_slots[0]
        _fd(descriptor)
        schema.need(_identity(_FSTAT(descriptor)) == expected['identity'], 'evidence changed before read')
        chunks, count, calls = [], 0, 0
        while True:
            calls += 1
            schema.need(calls <= schema.MAX_READ_CALLS, 'evidence read-call bound exceeded')
            raw = _READ(descriptor, min(schema.CHUNK_BYTES, limit + 1 - count))
            schema.need(_TYPE(raw) is bytes, 'native evidence read returned foreign data')
            if _LEN(raw) == 0:
                break
            count += _LEN(raw)
            schema.need(count <= limit, 'evidence byte bound exceeded')
            chunks.append(raw)
        result = b''.join(chunks)
        schema.need(count == expected['bytes'] and schema.sha(result) == expected['sha256'] and
                    _identity(_FSTAT(descriptor)) == expected['identity'] and
                    _identity(_STAT(name, dir_fd=parent, follow_symlinks=False)) == expected['identity'],
                    'retained evidence bytes/custody differ')
        verify(expected, limit, error_owner=error_owner)
        return result
    except _base_error as operation_error:
        operation_primary = operation_error
        if _primary[0] is None:
            _primary[0] = operation_error
            _primary[1] = 'read_verified'
            _primary[2] = None
        elif _primary[0] is not operation_error:
            _error_index = _counts[0]
            if _error_index < 64:
                _secondary[_error_index] = operation_error
                _phases[_error_index] = 'read_verified'
                _uncertain[_error_index] = None
                _counts[0] = _successors[_error_index]
            else:
                _overflow[1] = True
                _io[0] = True
                _io[4] = True
                if _overflow[0] is None:
                    _overflow[0] = operation_error
        raise
    finally:
        _owned_fd = _fd_slots[0]
        _fd_slots[0] = None
        if _owned_fd is not None:
            if _attempt_digits[4] == 1:
                _io[6] = True
                _io[0] = True
                _io[4] = True
            else:
                _digit = 0
                while _digit < 4 and _attempt_digits[_digit] == 255:
                    _attempt_digits[_digit] = 0
                    _digit = _successors[_digit]
                _attempt_digits[_digit] = _successors[_attempt_digits[_digit]]
            try:
                _close_native(_owned_fd)
            except _base_error as _close_error:
                _io[0] = True
                _io[4] = True
                if cleanup_primary is None:
                    cleanup_primary = _close_error
                if _primary[0] is None:
                    _primary[0] = _close_error
                    _primary[1] = 'close'
                    _primary[2] = _owned_fd
                elif _primary[0] is not _close_error:
                    _error_index = _counts[0]
                    if _error_index < 64:
                        _secondary[_error_index] = _close_error
                        _phases[_error_index] = 'close'
                        _uncertain[_error_index] = _owned_fd
                        _counts[0] = _successors[_error_index]
                    else:
                        _overflow[1] = True
                        _io[0] = True
                        _io[4] = True
                        if _overflow[0] is None:
                            _overflow[0] = _close_error
            else:
                if _confirmed_digits[4] == 1:
                    _io[6] = True
                    _io[0] = True
                    _io[4] = True
                else:
                    _digit = 0
                    while _digit < 4 and _confirmed_digits[_digit] == 255:
                        _confirmed_digits[_digit] = 0
                        _digit = _successors[_digit]
                    _confirmed_digits[_digit] = _successors[_confirmed_digits[_digit]]
        _owned_fd = _fd_slots[1]
        _fd_slots[1] = None
        if _owned_fd is not None:
            if _attempt_digits[4] == 1:
                _io[6] = True
                _io[0] = True
                _io[4] = True
            else:
                _digit = 0
                while _digit < 4 and _attempt_digits[_digit] == 255:
                    _attempt_digits[_digit] = 0
                    _digit = _successors[_digit]
                _attempt_digits[_digit] = _successors[_attempt_digits[_digit]]
            try:
                _close_native(_owned_fd)
            except _base_error as _close_error:
                _io[0] = True
                _io[4] = True
                if cleanup_primary is None:
                    cleanup_primary = _close_error
                if _primary[0] is None:
                    _primary[0] = _close_error
                    _primary[1] = 'close'
                    _primary[2] = _owned_fd
                elif _primary[0] is not _close_error:
                    _error_index = _counts[0]
                    if _error_index < 64:
                        _secondary[_error_index] = _close_error
                        _phases[_error_index] = 'close'
                        _uncertain[_error_index] = _owned_fd
                        _counts[0] = _successors[_error_index]
                    else:
                        _overflow[1] = True
                        _io[0] = True
                        _io[4] = True
                        if _overflow[0] is None:
                            _overflow[0] = _close_error
            else:
                if _confirmed_digits[4] == 1:
                    _io[6] = True
                    _io[0] = True
                    _io[4] = True
                else:
                    _digit = 0
                    while _digit < 4 and _confirmed_digits[_digit] == 255:
                        _confirmed_digits[_digit] = 0
                        _digit = _successors[_digit]
                    _confirmed_digits[_digit] = _successors[_confirmed_digits[_digit]]
        _owned_fd = _fd_slots[2]
        _fd_slots[2] = None
        if _owned_fd is not None:
            if _attempt_digits[4] == 1:
                _io[6] = True
                _io[0] = True
                _io[4] = True
            else:
                _digit = 0
                while _digit < 4 and _attempt_digits[_digit] == 255:
                    _attempt_digits[_digit] = 0
                    _digit = _successors[_digit]
                _attempt_digits[_digit] = _successors[_attempt_digits[_digit]]
            try:
                _close_native(_owned_fd)
            except _base_error as _close_error:
                _io[0] = True
                _io[4] = True
                if cleanup_primary is None:
                    cleanup_primary = _close_error
                if _primary[0] is None:
                    _primary[0] = _close_error
                    _primary[1] = 'close'
                    _primary[2] = _owned_fd
                elif _primary[0] is not _close_error:
                    _error_index = _counts[0]
                    if _error_index < 64:
                        _secondary[_error_index] = _close_error
                        _phases[_error_index] = 'close'
                        _uncertain[_error_index] = _owned_fd
                        _counts[0] = _successors[_error_index]
                    else:
                        _overflow[1] = True
                        _io[0] = True
                        _io[4] = True
                        if _overflow[0] is None:
                            _overflow[0] = _close_error
            else:
                if _confirmed_digits[4] == 1:
                    _io[6] = True
                    _io[0] = True
                    _io[4] = True
                else:
                    _digit = 0
                    while _digit < 4 and _confirmed_digits[_digit] == 255:
                        _confirmed_digits[_digit] = 0
                        _digit = _successors[_digit]
                    _confirmed_digits[_digit] = _successors[_confirmed_digits[_digit]]
        _owned_fd = _fd_slots[3]
        _fd_slots[3] = None
        if _owned_fd is not None:
            if _attempt_digits[4] == 1:
                _io[6] = True
                _io[0] = True
                _io[4] = True
            else:
                _digit = 0
                while _digit < 4 and _attempt_digits[_digit] == 255:
                    _attempt_digits[_digit] = 0
                    _digit = _successors[_digit]
                _attempt_digits[_digit] = _successors[_attempt_digits[_digit]]
            try:
                _close_native(_owned_fd)
            except _base_error as _close_error:
                _io[0] = True
                _io[4] = True
                if cleanup_primary is None:
                    cleanup_primary = _close_error
                if _primary[0] is None:
                    _primary[0] = _close_error
                    _primary[1] = 'close'
                    _primary[2] = _owned_fd
                elif _primary[0] is not _close_error:
                    _error_index = _counts[0]
                    if _error_index < 64:
                        _secondary[_error_index] = _close_error
                        _phases[_error_index] = 'close'
                        _uncertain[_error_index] = _owned_fd
                        _counts[0] = _successors[_error_index]
                    else:
                        _overflow[1] = True
                        _io[0] = True
                        _io[4] = True
                        if _overflow[0] is None:
                            _overflow[0] = _close_error
            else:
                if _confirmed_digits[4] == 1:
                    _io[6] = True
                    _io[0] = True
                    _io[4] = True
                else:
                    _digit = 0
                    while _digit < 4 and _confirmed_digits[_digit] == 255:
                        _confirmed_digits[_digit] = 0
                        _digit = _successors[_digit]
                    _confirmed_digits[_digit] = _successors[_confirmed_digits[_digit]]
        _owned_fd = _fd_slots[4]
        _fd_slots[4] = None
        if _owned_fd is not None:
            if _attempt_digits[4] == 1:
                _io[6] = True
                _io[0] = True
                _io[4] = True
            else:
                _digit = 0
                while _digit < 4 and _attempt_digits[_digit] == 255:
                    _attempt_digits[_digit] = 0
                    _digit = _successors[_digit]
                _attempt_digits[_digit] = _successors[_attempt_digits[_digit]]
            try:
                _close_native(_owned_fd)
            except _base_error as _close_error:
                _io[0] = True
                _io[4] = True
                if cleanup_primary is None:
                    cleanup_primary = _close_error
                if _primary[0] is None:
                    _primary[0] = _close_error
                    _primary[1] = 'close'
                    _primary[2] = _owned_fd
                elif _primary[0] is not _close_error:
                    _error_index = _counts[0]
                    if _error_index < 64:
                        _secondary[_error_index] = _close_error
                        _phases[_error_index] = 'close'
                        _uncertain[_error_index] = _owned_fd
                        _counts[0] = _successors[_error_index]
                    else:
                        _overflow[1] = True
                        _io[0] = True
                        _io[4] = True
                        if _overflow[0] is None:
                            _overflow[0] = _close_error
            else:
                if _confirmed_digits[4] == 1:
                    _io[6] = True
                    _io[0] = True
                    _io[4] = True
                else:
                    _digit = 0
                    while _digit < 4 and _confirmed_digits[_digit] == 255:
                        _confirmed_digits[_digit] = 0
                        _digit = _successors[_digit]
                    _confirmed_digits[_digit] = _successors[_confirmed_digits[_digit]]
        if operation_primary is None and cleanup_primary is not None:
            raise cleanup_primary


def write_observation_once_v3(path: str, raw: bytes, *, error_owner) -> dict:
    schema.owner_state(error_owner)
    schema.path(path)
    schema.need(_TYPE(raw) is bytes, 'exact record bytes required')
    schema.need(0 < _LEN(raw) <= OBSERVATION_WRITE_BYTES_V3, 'record bound differs')
    _complete_io_gate_v3()
    _gate()
    _state = schema.owner_state(error_owner)
    _primary, _secondary, _phases, _uncertain = _state[0], _state[1], _state[2], _state[3]
    _counts, _overflow, _io = _state[4], _state[5], _state[7]
    _attempt_digits, _confirmed_digits = _io[7], _io[8]
    _successors = schema.CUSTODY_SUCCESSORS
    _quarantine_error = schema.IO_QUARANTINE_ERROR
    _base_error, _close_native = BaseException, _CLOSE
    _error_index = _digit = 0
    _owned_fd = _close_error = _acquisition_error = None
    cleanup_primary = operation_primary = None
    _fd_slots = [None] * 5
    _iterator = _owned_iterator = None
    try:
        name = _parent(path, error_owner, _fd_slots, 1)
        parent = _fd_slots[1]
        if _io[0] or _io[1] or _io[10] or _overflow[1] or _attempt_digits[4] == 1:
            raise _quarantine_error
        _io[1] = True
        try:
            _fd_slots[0] = _OPEN(name, os.O_RDWR | os.O_CREAT | os.O_EXCL | os.O_CLOEXEC | os.O_NOFOLLOW, 0o600, dir_fd=parent)
        except _base_error as _acquisition_error:
            if _io[3] is None:
                _io[3] = _acquisition_error
            _io[0] = True
            _io[2] = True
            _io[4] = True
            raise
        _io[1] = False
        descriptor = _fd_slots[0]
        _fd(descriptor)
        initial = _identity(_FSTAT(descriptor))
        schema.need(stat.S_ISREG(initial['mode']) and initial['links'] == 1 and initial['size'] == 0 and
                    stat.S_IMODE(initial['mode']) == 0o600, 'exclusive record file differs')
        offset, calls = 0, 0
        while offset < _LEN(raw):
            calls += 1
            schema.need(calls <= schema.MAX_RECORD_WRITE_CALLS, 'record write-call bound exceeded')
            written = _WRITE(descriptor, raw[offset:offset + schema.CHUNK_BYTES])
            schema.integer(written, 1, min(schema.CHUNK_BYTES, _LEN(raw) - offset))
            offset += written
        _FSYNC(descriptor)
        _FSYNC(parent)
        owned = _identity(_FSTAT(descriptor))
        result = inspect(path, OBSERVATION_WRITE_BYTES_V3, error_owner=error_owner)
        schema.need(result['identity'] == owned and
                    (owned['device'], owned['inode']) == (initial['device'], initial['inode']) and
                    result['sha256'] == schema.sha(raw) and result['bytes'] == _LEN(raw), 'record readback differs')
        return result
    except _base_error as operation_error:
        operation_primary = operation_error
        if _primary[0] is None:
            _primary[0] = operation_error
            _primary[1] = 'write_once'
            _primary[2] = None
        elif _primary[0] is not operation_error:
            _error_index = _counts[0]
            if _error_index < 64:
                _secondary[_error_index] = operation_error
                _phases[_error_index] = 'write_once'
                _uncertain[_error_index] = None
                _counts[0] = _successors[_error_index]
            else:
                _overflow[1] = True
                _io[0] = True
                _io[4] = True
                if _overflow[0] is None:
                    _overflow[0] = operation_error
        raise
    finally:
        _owned_fd = _fd_slots[0]
        _fd_slots[0] = None
        if _owned_fd is not None:
            if _attempt_digits[4] == 1:
                _io[6] = True
                _io[0] = True
                _io[4] = True
            else:
                _digit = 0
                while _digit < 4 and _attempt_digits[_digit] == 255:
                    _attempt_digits[_digit] = 0
                    _digit = _successors[_digit]
                _attempt_digits[_digit] = _successors[_attempt_digits[_digit]]
            try:
                _close_native(_owned_fd)
            except _base_error as _close_error:
                _io[0] = True
                _io[4] = True
                if cleanup_primary is None:
                    cleanup_primary = _close_error
                if _primary[0] is None:
                    _primary[0] = _close_error
                    _primary[1] = 'close'
                    _primary[2] = _owned_fd
                elif _primary[0] is not _close_error:
                    _error_index = _counts[0]
                    if _error_index < 64:
                        _secondary[_error_index] = _close_error
                        _phases[_error_index] = 'close'
                        _uncertain[_error_index] = _owned_fd
                        _counts[0] = _successors[_error_index]
                    else:
                        _overflow[1] = True
                        _io[0] = True
                        _io[4] = True
                        if _overflow[0] is None:
                            _overflow[0] = _close_error
            else:
                if _confirmed_digits[4] == 1:
                    _io[6] = True
                    _io[0] = True
                    _io[4] = True
                else:
                    _digit = 0
                    while _digit < 4 and _confirmed_digits[_digit] == 255:
                        _confirmed_digits[_digit] = 0
                        _digit = _successors[_digit]
                    _confirmed_digits[_digit] = _successors[_confirmed_digits[_digit]]
        _owned_fd = _fd_slots[1]
        _fd_slots[1] = None
        if _owned_fd is not None:
            if _attempt_digits[4] == 1:
                _io[6] = True
                _io[0] = True
                _io[4] = True
            else:
                _digit = 0
                while _digit < 4 and _attempt_digits[_digit] == 255:
                    _attempt_digits[_digit] = 0
                    _digit = _successors[_digit]
                _attempt_digits[_digit] = _successors[_attempt_digits[_digit]]
            try:
                _close_native(_owned_fd)
            except _base_error as _close_error:
                _io[0] = True
                _io[4] = True
                if cleanup_primary is None:
                    cleanup_primary = _close_error
                if _primary[0] is None:
                    _primary[0] = _close_error
                    _primary[1] = 'close'
                    _primary[2] = _owned_fd
                elif _primary[0] is not _close_error:
                    _error_index = _counts[0]
                    if _error_index < 64:
                        _secondary[_error_index] = _close_error
                        _phases[_error_index] = 'close'
                        _uncertain[_error_index] = _owned_fd
                        _counts[0] = _successors[_error_index]
                    else:
                        _overflow[1] = True
                        _io[0] = True
                        _io[4] = True
                        if _overflow[0] is None:
                            _overflow[0] = _close_error
            else:
                if _confirmed_digits[4] == 1:
                    _io[6] = True
                    _io[0] = True
                    _io[4] = True
                else:
                    _digit = 0
                    while _digit < 4 and _confirmed_digits[_digit] == 255:
                        _confirmed_digits[_digit] = 0
                        _digit = _successors[_digit]
                    _confirmed_digits[_digit] = _successors[_confirmed_digits[_digit]]
        _owned_fd = _fd_slots[2]
        _fd_slots[2] = None
        if _owned_fd is not None:
            if _attempt_digits[4] == 1:
                _io[6] = True
                _io[0] = True
                _io[4] = True
            else:
                _digit = 0
                while _digit < 4 and _attempt_digits[_digit] == 255:
                    _attempt_digits[_digit] = 0
                    _digit = _successors[_digit]
                _attempt_digits[_digit] = _successors[_attempt_digits[_digit]]
            try:
                _close_native(_owned_fd)
            except _base_error as _close_error:
                _io[0] = True
                _io[4] = True
                if cleanup_primary is None:
                    cleanup_primary = _close_error
                if _primary[0] is None:
                    _primary[0] = _close_error
                    _primary[1] = 'close'
                    _primary[2] = _owned_fd
                elif _primary[0] is not _close_error:
                    _error_index = _counts[0]
                    if _error_index < 64:
                        _secondary[_error_index] = _close_error
                        _phases[_error_index] = 'close'
                        _uncertain[_error_index] = _owned_fd
                        _counts[0] = _successors[_error_index]
                    else:
                        _overflow[1] = True
                        _io[0] = True
                        _io[4] = True
                        if _overflow[0] is None:
                            _overflow[0] = _close_error
            else:
                if _confirmed_digits[4] == 1:
                    _io[6] = True
                    _io[0] = True
                    _io[4] = True
                else:
                    _digit = 0
                    while _digit < 4 and _confirmed_digits[_digit] == 255:
                        _confirmed_digits[_digit] = 0
                        _digit = _successors[_digit]
                    _confirmed_digits[_digit] = _successors[_confirmed_digits[_digit]]
        _owned_fd = _fd_slots[3]
        _fd_slots[3] = None
        if _owned_fd is not None:
            if _attempt_digits[4] == 1:
                _io[6] = True
                _io[0] = True
                _io[4] = True
            else:
                _digit = 0
                while _digit < 4 and _attempt_digits[_digit] == 255:
                    _attempt_digits[_digit] = 0
                    _digit = _successors[_digit]
                _attempt_digits[_digit] = _successors[_attempt_digits[_digit]]
            try:
                _close_native(_owned_fd)
            except _base_error as _close_error:
                _io[0] = True
                _io[4] = True
                if cleanup_primary is None:
                    cleanup_primary = _close_error
                if _primary[0] is None:
                    _primary[0] = _close_error
                    _primary[1] = 'close'
                    _primary[2] = _owned_fd
                elif _primary[0] is not _close_error:
                    _error_index = _counts[0]
                    if _error_index < 64:
                        _secondary[_error_index] = _close_error
                        _phases[_error_index] = 'close'
                        _uncertain[_error_index] = _owned_fd
                        _counts[0] = _successors[_error_index]
                    else:
                        _overflow[1] = True
                        _io[0] = True
                        _io[4] = True
                        if _overflow[0] is None:
                            _overflow[0] = _close_error
            else:
                if _confirmed_digits[4] == 1:
                    _io[6] = True
                    _io[0] = True
                    _io[4] = True
                else:
                    _digit = 0
                    while _digit < 4 and _confirmed_digits[_digit] == 255:
                        _confirmed_digits[_digit] = 0
                        _digit = _successors[_digit]
                    _confirmed_digits[_digit] = _successors[_confirmed_digits[_digit]]
        _owned_fd = _fd_slots[4]
        _fd_slots[4] = None
        if _owned_fd is not None:
            if _attempt_digits[4] == 1:
                _io[6] = True
                _io[0] = True
                _io[4] = True
            else:
                _digit = 0
                while _digit < 4 and _attempt_digits[_digit] == 255:
                    _attempt_digits[_digit] = 0
                    _digit = _successors[_digit]
                _attempt_digits[_digit] = _successors[_attempt_digits[_digit]]
            try:
                _close_native(_owned_fd)
            except _base_error as _close_error:
                _io[0] = True
                _io[4] = True
                if cleanup_primary is None:
                    cleanup_primary = _close_error
                if _primary[0] is None:
                    _primary[0] = _close_error
                    _primary[1] = 'close'
                    _primary[2] = _owned_fd
                elif _primary[0] is not _close_error:
                    _error_index = _counts[0]
                    if _error_index < 64:
                        _secondary[_error_index] = _close_error
                        _phases[_error_index] = 'close'
                        _uncertain[_error_index] = _owned_fd
                        _counts[0] = _successors[_error_index]
                    else:
                        _overflow[1] = True
                        _io[0] = True
                        _io[4] = True
                        if _overflow[0] is None:
                            _overflow[0] = _close_error
            else:
                if _confirmed_digits[4] == 1:
                    _io[6] = True
                    _io[0] = True
                    _io[4] = True
                else:
                    _digit = 0
                    while _digit < 4 and _confirmed_digits[_digit] == 255:
                        _confirmed_digits[_digit] = 0
                        _digit = _successors[_digit]
                    _confirmed_digits[_digit] = _successors[_confirmed_digits[_digit]]
        if operation_primary is None and cleanup_primary is not None:
            raise cleanup_primary

