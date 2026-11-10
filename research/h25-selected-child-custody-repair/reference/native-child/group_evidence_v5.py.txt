"""Source-only bounded full-control evidence sink; caller authenticates provenance.

No factory call is authorized by importing this module. The caller must first
admit this source/environment, the original guard and private parent FD identity.
Only completed group boundaries may call the returned captured functions.
"""
import posix
from hashlib import sha256
from types import FunctionType, CellType, BuiltinFunctionType, ModuleType

SCHEMA = 'h25-full-group-evidence-sink-v5'
GROUP_ORDER = ('native', 'transport', 'collector', 'pure_initial', 'pure_extended',
               'pure_combined', 'root_model', 'sink_close_model', 'projection_model', 'aggregate')
MAX_RAW_BYTES = 1048576
MAX_TOTAL_BYTES = 4194304
STOP_RESERVE_BYTES = 65536
FIELDS = ('__code__', '__globals__', '__builtins__', '__defaults__', '__kwdefaults__', '__closure__', '__dict__')
_OPEN, _WRITE, _CLOSE, _FSTAT, _FSYNC, _MKDIR = posix.open, posix.write, posix.close, posix.fstat, posix.fsync, posix.mkdir
_DIR_FLAGS = posix.O_RDONLY | posix.O_DIRECTORY | posix.O_NOFOLLOW | posix.O_CLOEXEC
_FILE_FLAGS = posix.O_WRONLY | posix.O_CREAT | posix.O_EXCL | posix.O_NOFOLLOW | posix.O_CLOEXEC


class EvidenceWriteError(RuntimeError):
    """Retain actual primary/secondary exceptions and confirmed partial output."""
    def __init__(self, primary, secondary, artifact):
        RuntimeError.__init__(self, 'Full-control evidence write failed')
        self.primary, self.secondary, self.artifact = primary, secondary, artifact


def _need(condition, text):
    if not condition:
        raise RuntimeError(text)


def _safe_plain(value, budget, depth=0):
    _need(depth < 32 and budget[0] > 0, 'group evidence JSON node/depth bound')
    budget[0] -= 1
    kind = type(value)
    if value is None or (kind is bool or kind is int or kind is str):
        if kind is str: _need(len(value) <= 65536, 'group evidence JSON string bound')
        if kind is int: _need(value.bit_length() <= 4096, 'group evidence JSON integer bound')
        return
    _need((kind is dict or kind is tuple or kind is list) and len(value) <= 4096, 'group evidence JSON exact value/collection bound')
    if kind is dict:
        for key, item in value.items():
            _need(type(key) is str, 'group evidence JSON key must be exact str')
            _safe_plain(key, budget, depth + 1)
            _safe_plain(item, budget, depth + 1)
    else:
        for item in value:
            _safe_plain(item, budget, depth + 1)


def _quote_ascii(value):
    # Source-owned exact-str escaping. No new JSON/_json/regex dependency.
    _need(type(value) is str, 'group evidence JSON quote requires exact str')
    parts = ['"']
    escapes = {'"': '\\"', '\\': '\\\\', '\b': '\\b', '\f': '\\f',
               '\n': '\\n', '\r': '\\r', '\t': '\\t'}
    for character in value:
        escaped = escapes.get(character)
        if escaped is not None:
            parts.append(escaped)
            continue
        code = ord(character)
        if 0x20 <= code <= 0x7e:
            parts.append(character)
        elif code <= 0xffff:
            parts.append('\\u' + format(code, '04x'))
        else:
            code -= 0x10000
            parts.append('\\u' + format(0xd800 | (code >> 10), '04x') +
                         '\\u' + format(0xdc00 | (code & 0x3ff), '04x'))
    parts.append('"')
    return ''.join(parts)


def _json_tokens(value):
    kind = type(value)
    if value is None:
        yield 'null'
    elif kind is bool:
        yield 'true' if value else 'false'
    elif kind is int:
        yield str(value)
    elif kind is str:
        yield _quote_ascii(value)
    elif kind is list or kind is tuple:
        yield '['
        for index, item in enumerate(value):
            if index: yield ','
            yield from _json_tokens(item)
        yield ']'
    elif kind is dict:  # _safe_plain already checked exact-str keys.
        _need(all(type(key) is str for key in value), 'group evidence JSON token key must be exact str')
        yield '{'
        for index, key in enumerate(sorted(value)):
            if index: yield ','
            yield _quote_ascii(key)
            yield ':'
            yield from _json_tokens(value[key])
        yield '}'
    else:
        raise RuntimeError('group evidence JSON token value is not exact native type')


def _encode(value, limit):
    _safe_plain(value, [100000])
    chunks, size = [], 0
    for chunk in _json_tokens(value):
        raw = chunk.encode('ascii')
        size += len(raw)
        _need(size + 1 <= limit, 'group evidence encoded byte bound')
        chunks.append(raw)
    return b''.join(chunks) + b'\n'


def _admission(function):
    values = tuple(FunctionType.__dict__[name].__get__(function, FunctionType) for name in FIELDS)
    getter = CellType.__dict__['cell_contents'].__get__
    cells = () if values[5] is None else tuple((cell, getter(cell, CellType)) for cell in values[5])
    return function, values, cells


def _admission_graph(functions):
    """All direct/immutable-tuple Python closure dependencies, no target calls.

    Mutable state dictionaries/lists are data, never callable dispatch tables in
    the sink. Module-global helpers/classes are authenticated by the caller's
    original complete source guard. Row4 is an explicit delegated boundary:
    its own fields/cells are pinned, then its source must inline-admit the
    original authority dispatcher before EVERY unchanged op6 check. We never
    walk that authority registry or recapture its expected values.
    """
    queue, records, seen, tuple_nodes, tuple_seen = list(functions), [], [], 0, set()
    while queue:
        function = queue.pop(0)
        if any(function is prior for prior in seen):
            continue
        _need(type(function) is FunctionType and len(seen) < 512, 'group evidence function graph bound')
        seen.append(function)
        row = _admission(function)
        records.append(row)
        if function is functions[4]:
            continue  # delegated original authority guard; direct fields/cells still pinned
        pending = [value for _, value in row[2]]
        pending.extend(value for value in (row[1][3], row[1][4]) if value is not None)
        while pending:
            value = pending.pop()
            if type(value) is FunctionType:
                queue.append(value)
            elif type(value) is tuple:
                identity = id(value)
                if identity in tuple_seen:
                    continue
                tuple_seen.add(identity)
                tuple_nodes += 1
                _need(tuple_nodes <= 8192, 'group evidence immutable tuple graph bound')
                pending.extend(value)
    _need(tuple(row[0] for row in records[:5]) == functions, 'group evidence original root graph order')
    return tuple(records)


def _make_close_sink(holder, closed, state, schema, expected_group_count):
    """Capture one consume-once closer and its original outcome.

    Production supplies its authenticated native close; models supply an explicit
    fake. The returned closure never calls a guard or Python formatting helper.
    An exception means closure is unconfirmed, not proof the FD is still open.
    """
    close_state, base_error = [False, False, None], BaseException
    def close_sink():
        # Clear ownership BEFORE native close. Neither an exception nor a repeated
        # call may reuse this descriptor number; it could already be recycled.
        fd, holder[0] = holder[0], None
        if fd is not None:
            close_state[0] = True
            try:
                closed(fd)
            except base_error as failure:
                close_state[2] = failure
                raise
            else:
                close_state[1] = True
        summary = {'schema': schema, 'completed_groups': state['index'],
            'expected_groups': expected_group_count,
            'raw_pins': [[group, pin] for group, pin in state['raw_pins']],
            'validation_pins': [[group, pin] for group, pin in state['validation_pins']],
            'stop_pin': state['stop_pin'], 'reserved_bytes': state['reserved_bytes'],
            'directory_closed': close_state[1], 'directory_close_attempted': close_state[0],
            'directory_close_outcome': ('CONFIRMED' if close_state[1] else
                ('UNCONFIRMED_AFTER_EXCEPTION' if close_state[2] is not None else 'NOT_ATTEMPTED')),
            'directory_close_error_present': close_state[2] is not None}
        return summary, close_state[2]
    return close_sink


def make_group_sink(parent_fd, expected_parent_identity, original_source_guard, mode, *, original_native_io):
    """Create one fresh private child under an already owned/admitted parent FD.

    Parent identity is the caller's original tuple(dev, ino, uid, mode), never
    recaptured by this factory as authority. The caller separately authenticates
    original_source_guard and captures/adopts the returned five-function packet.
    Factory, writes, fsyncs, guards, serialization and teardown all remain paid.
    """
    _need(type(parent_fd) is int and parent_fd >= 0 and type(expected_parent_identity) is tuple and
          len(expected_parent_identity) == 4 and all(type(x) is int for x in expected_parent_identity),
          'group evidence original parent identity')
    _need(type(original_source_guard) is FunctionType and type(mode) is str and mode in ('normal', 'optimized'),
          'group evidence original guard/mode')
    original_source_guard()
    _need(type(original_native_io) is tuple and len(original_native_io) == 5 and
          original_native_io[0] == 'h25-original-group-native-io-v1', 'group evidence early native IO packet')
    _, original_functions, original_dir_flags, original_file_flags, original_posix = original_native_io
    _need(type(original_functions) is tuple and len(original_functions) == 6 and
          type(original_posix) is ModuleType and original_posix is posix and
          type(original_dir_flags) is int and original_dir_flags == _DIR_FLAGS and
          type(original_file_flags) is int and original_file_flags == _FILE_FLAGS,
          'group evidence original native owner/flag profile')
    for current, original, name in zip((_OPEN, _WRITE, _CLOSE, _FSTAT, _FSYNC, _MKDIR),
                                       original_functions, ('open', 'write', 'close', 'fstat', 'fsync', 'mkdir')):
        _need(current is original and type(original) is BuiltinFunctionType and
              original.__self__ is original_posix and original.__name__ == name,
              'group evidence primitive differs from early native capture')
    opened, wrote, closed, stated, synced, mkdir = original_functions
    guard, error, base_error, need0 = original_source_guard, RuntimeError, BaseException, _need
    encode0, sha0, write_error = _encode, sha256, EvidenceWriteError
    parent_info = stated(parent_fd)
    need0((parent_info.st_dev, parent_info.st_ino, parent_info.st_uid, parent_info.st_mode) == expected_parent_identity and
          parent_info.st_mode & 0o177777 == 0o040700, 'group evidence parent is not original private directory')
    directory_name = 'field-groups-v5'
    mkdir(directory_name, 0o700, dir_fd=parent_fd)
    directory_fd = opened(directory_name, _DIR_FLAGS, dir_fd=parent_fd)
    # Ownership transfers to this local holder immediately; close is never retried.
    holder = [directory_fd]
    try:
        info = stated(directory_fd)
        need0(info.st_mode & 0o177777 == 0o040700 and info.st_uid == parent_info.st_uid and info.st_dev == parent_info.st_dev,
              'group evidence child directory identity/mode')
        identity = (info.st_dev, info.st_ino, info.st_uid, info.st_mode)
        synced(directory_fd)
        synced(parent_fd)
        guard()
        state = {'index': 0, 'pending': None, 'terminal': False, 'reserved_bytes': 0,
                 'raw_pins': [], 'validation_pins': [], 'stop_pin': None}
        file_flags, schema, groups = _FILE_FLAGS, SCHEMA, GROUP_ORDER
        raw_limit, total_limit, stop_reserve = MAX_RAW_BYTES, MAX_TOTAL_BYTES, STOP_RESERVE_BYTES
        expected_group_count = len(groups)
        def owned_directory():
            need0(holder[0] is not None, 'group evidence sink is closed')
            current = stated(holder[0])
            need0((current.st_dev, current.st_ino, current.st_uid, current.st_mode) == identity,
                  'group evidence original child identity changed')
            return holder[0]
        def write_record(filename, value, limit, stop=False):
            guard()
            directory = owned_directory()
            raw = encode0(value, limit)
            ceiling = total_limit if stop else total_limit - stop_reserve
            need0(state['reserved_bytes'] + len(raw) <= ceiling, 'group evidence total byte bound')
            state['reserved_bytes'] += len(raw)  # attempted bytes remain charged after any failure
            fd, written, primary, secondary = None, 0, None, None
            artifact = {'file': directory_name + '/' + filename, 'bytes_expected': len(raw),
                        'sha256_expected': sha0(raw).hexdigest(), 'bytes_confirmed': 0, 'durable': False}
            try:
                fd = opened(filename, file_flags, 0o600, dir_fd=directory)
                while written < len(raw):
                    count = wrote(fd, raw[written:])
                    need0(type(count) is int and 0 < count <= len(raw) - written, 'group evidence short/invalid write')
                    written += count
                    artifact['bytes_confirmed'] = written
                actual = stated(fd)
                need0(actual.st_mode & 0o177777 == 0o100600 and actual.st_uid == identity[2] and
                      actual.st_nlink == 1 and actual.st_size == len(raw), 'group evidence file identity/size')
                synced(fd)
                synced(directory)
                artifact['durable'] = True
            except base_error as failure:
                primary = failure
            finally:
                if fd is not None:
                    consumed, fd = fd, None
                    try: closed(consumed)
                    except base_error as failure:
                        if primary is None: primary = failure
                        else: secondary = failure
            if primary is not None:
                raise write_error(primary, secondary, artifact) from primary
            return {'file': artifact['file'], 'bytes': len(raw), 'sha256': artifact['sha256_expected'], 'durable': True}
        def expected(group):
            need0(not state['terminal'] and state['index'] < len(groups) and
                  type(group) is str and group == groups[state['index']], 'group evidence exact next boundary')
        def capture_return(group, raw):
            guard()
            expected(group)
            need0(state['pending'] is None, 'group evidence duplicate raw return')
            # Mark returned before serialization so capture failure is never NOT_RETURNED.
            state['pending'] = (group, None)
            pin = write_record(str(state['index']).zfill(2) + '-' + group + '-raw.json', raw, raw_limit)
            state['pending'] = (group, pin)
            state['raw_pins'].append((group, pin))
            guard()  # retain unchanged original freshness checks across callback-bearing I/O
            return pin
        def capture_validation(group):
            guard()
            expected(group)
            pending = state['pending']
            need0(pending is not None and pending[0] == group and pending[1] is not None,
                  'group evidence validation requires a durable raw return')
            note = {'schema': schema, 'mode': mode, 'group': group, 'state': 'RETURNED_RAW_OUTER_VALIDATED', 'raw': pending[1]}
            pin = write_record(str(state['index']).zfill(2) + '-' + group + '-validation.json', note, 8192)
            state['validation_pins'].append((group, pin))
            guard()  # no next group until post-I/O original freshness succeeds
            state['pending'] = None
            state['index'] += 1
            return pin
        def capture_failure(group, failure):
            guard()
            expected(group)
            need0(type(failure) is dict and failure.get('group') == group and
                  failure.get('return_state') in ('NOT_RETURNED', 'RETURNED_CAPTURE_FAILED', 'RETURNED_MALFORMED',
                                                   'RETURNED_VALIDATION_EVIDENCE_FAILED'), 'group evidence failure state')
            need0(failure['return_state'] == 'RETURNED_CAPTURE_FAILED' or
                  (failure['return_state'] == 'NOT_RETURNED') == (state['pending'] is None),
                  'group evidence returned/nonreturned census differs')
            state['terminal'] = True  # consume even if STOP I/O fails; never retry/continue
            note = {'schema': schema, 'mode': mode, 'failure': failure,
                    'raw_pins': [[group, pin] for group, pin in state['raw_pins']],
                    'validation_pins': [[group, pin] for group, pin in state['validation_pins']],
                    'reserved_bytes_before_stop': state['reserved_bytes']}
            pin = write_record(str(state['index']).zfill(2) + '-' + group + '-STOP.json', note, stop_reserve, True)
            state['stop_pin'] = pin
            return pin
        close_sink = _make_close_sink(holder, closed, state, schema, expected_group_count)
        functions = (capture_return, capture_validation, capture_failure, close_sink, guard)
        graph = _admission_graph(functions)
        contract = {'schema': schema, 'mode': mode, 'group_order': groups, 'raw_byte_limit': raw_limit,
                    'total_byte_limit': total_limit, 'stop_reserve_bytes': stop_reserve,
                    'directory': directory_name, 'directory_identity': identity,
                    'parent_identity': expected_parent_identity, 'function_graph_count': len(graph),
                    'graph_traversal': 'DIRECT_AND_IMMUTABLE_TUPLE_FUNCTION_CLOSURES',
                    'delegated_guard_boundary': 'ROW4_ORIGINAL_DISPATCH_ADMISSION_BEFORE_EVERY_OP6',
                    'cleanup_record_index': 3, 'exclusive_outputs': True,
                    'raw_before_outer_validation': True, 'caller_source_admission_required': True}
        return (schema, functions, graph, contract)
    except base_error as primary:
        fd, holder[0] = holder[0], None
        secondary = None
        if fd is not None:
            try: closed(fd)
            except base_error as failure: secondary = failure
        raise write_error(primary, secondary, {'file': directory_name, 'state': 'FACTORY_FAILED_DIRECTORY_RETAINED'}) from primary
