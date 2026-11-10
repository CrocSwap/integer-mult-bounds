"""Fixed G12 parent custody source, v2 identity and preflight-close repair.

No execution or publication authority.

Only a later independently reviewed literal may select the launch. All actual
authorization, phase, resource-fit, custody and final-cost gates remain closed.
Unknown final tails remain unknown in the complete original symbolic invoice.
No manifest, receipt dictionary or success flag is accepted from a caller.
"""
import time
import resource
import signal
import subprocess
import fcntl
G12_REFERENCE_LAUNCH_SELECTION = None
_INITIAL_PARENT_SOURCE_PIN = globals().get('bootstrap_g12_parent_source_pin')
# Actual initial parent source identity comes only from the trusted external
# selected launcher; its future literal parent slot is None (no own-hash cycle).
import os


import sys


import stat


import json


import hashlib


import math


from types import FunctionType, CodeType, ModuleType


_ROOT_PIN = 'f5a2d33f2b4d3651f214156a0e7094c2bb516ce2d5ab7698d18c11f98f35dee0'


_PROVIDER_PIN = '9cbb7368f89e71d1e6cc46db5dc77efed3e03ed2a801c98c88fe316e4d9f3ef2'


_PRODUCER_PIN = 'a346025d5b6e2b26246521c6af6292643a4c2c3286b33ff3996dcf051cd6be26'


_GUARD_PIN = 'bd882e3dadb1b6aeaa63ee824f1a1c58f8ef2546b6840a2bffa46885a184d3eb'


_AUTHORITY_PIN = 'f279ab86fc17c6a517b035f19d56863919cbd8304de4e7d5332457c6159aec10'


_META_CAP = 262144


_PAIR_CAP = 268435456


_CHUNK = 65536


_LOG_CAP = 2097152


_MISSING = object()


_ID_NAMES = ('dev', 'ino', 'full_st_mode', 'size', 'mtime_ns', 'ctime_ns')


class _RawG12Errors:
    """Fixed error-retention slots; storing raw failures precedes formatting/IO."""
    __slots__ = ('slots', 'count')
    def __init__(self):
        self.slots = [None] * 4096
        self.count = 0
    def append(self, value):
        # All fixed directory/process/stream paths together have fewer than 4096
        # close sites under the 256-component/128-generation source ceilings.
        if self.count >= len(self.slots):
            raise RuntimeError('G12-N09: fixed raw secondary retention exhausted')
        self.slots[self.count] = value
        self.count += 1
    def __bool__(self):
        return self.count != 0
    def __len__(self):
        return self.count
    def __getitem__(self, index):
        if type(index) is not int or not 0 <= index < self.count:
            raise IndexError(index)
        return self.slots[index]
    def __iter__(self):
        for index in range(self.count):
            yield self.slots[index]
    def __repr__(self):
        return repr(tuple(self))


def _need(condition, message):
    if not condition:
        raise RuntimeError(message)


def _exact(value, expected):
    if type(value) is not type(expected):
        return False
    if type(value) in (list, tuple):
        return len(value) == len(expected) and all(_exact(a, b) for a, b in zip(value, expected))
    if type(value) is dict:
        return set(value) == set(expected) and all(_exact(value[k], expected[k]) for k in expected)
    return value == expected


def _fields(value, fields):
    _need(type(value) is dict and all(type(k) is str for k in value) and
          set(value) == set(fields), 'G12-N12: exact field domain differs')


def _digest(value):
    return type(value) is str and len(value) == 64 and all(c in '0123456789abcdef' for c in value)


def _uint(value, positive=False):
    _need(type(value) is int and value >= (1 if positive else 0), 'G12-N12: exact integer domain')


def _number(value):
    _need(type(value) in (int, float) and math.isfinite(value) and value >= 0,
          'G12-N12: finite nonnegative exact number required')


def _path(path):
    _need(type(path) is str and path.startswith('/') and
          all(p not in ('', '.', '..') for p in path.split('/')[1:]), 'G12-N11: absolute canonical path')
    return path


def _identity(info):
    return dict(zip(_ID_NAMES, (info.st_dev, info.st_ino, info.st_mode, info.st_size,
                                info.st_mtime_ns, info.st_ctime_ns)))


def _directory_key(info):
    return info.st_dev, info.st_ino, info.st_mode


def _directory_chain(path):
    """Held no-follow chain; no later absolute path silently changes its owner."""
    _path(path)
    _need(len(path.split('/')) <= 257, 'G12-N11: finite directory-component bound')
    fds, rows = [], []
    primary = None
    try:
        fd = os.open('/', os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC)
        fds.append(fd)
        for part in path.split('/')[1:]:
            before = os.stat(part, dir_fd=fd, follow_symlinks=False)
            _need(stat.S_ISDIR(before.st_mode), 'G12-N11: directory component type')
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC,
                            dir_fd=fd)
            fds.append(child)
            opened = os.fstat(child)
            _need(_directory_key(before) == _directory_key(opened), 'G12-N11: directory replaced')
            rows.append((fd, part, child, _directory_key(opened)))
            fd = child
        return fds, rows
    except BaseException as error:
        primary = (error, error.__traceback__)
    secondary = _RawG12Errors()
    for descriptor in reversed(fds):
        try:
            os.close(descriptor)
        except BaseException as error:
            secondary.append((error, error.__traceback__))
    _raise_preserved(primary, secondary)


def _check_chain(rows):
    for parent, name, descriptor, key in rows:
        _need(_directory_key(os.fstat(descriptor)) == key ==
              _directory_key(os.stat(name, dir_fd=parent, follow_symlinks=False)),
              'G12-N11: directory binding changed')


def _raise_preserved(primary, secondaries):
    """Never replace first raw failure if evidence formatting or retention fails."""
    if primary is not None:
        error, traceback = primary
        try:
            error.add_note('G12 ordered secondary failures: ' + repr(secondaries))
        except BaseException:
            pass
        raise error.with_traceback(traceback)
    if secondaries:
        error, traceback = secondaries[0][:2]
        raise error.with_traceback(traceback)


def _handoff_identity_tuple(record):
    """Pack a FileRecord identity as the immutable six-tuple handoff field.

    The accepted nine-tuple keeps this field positional. The cold consumer
    converts it back to a string-keyed dictionary; this parent does not emit
    a second, dictionary representation.
    """
    _fields(record['identity'], _ID_NAMES)
    return tuple(record['identity'][key] for key in _ID_NAMES)


def _close_known_descriptors(descriptors):
    """Attempt every close. Ordered failures never stop the remaining closes."""
    failures = _RawG12Errors()
    for descriptor in reversed(tuple(descriptors)):
        try:
            os.close(descriptor)
        except BaseException as error:
            failures.append((error, error.__traceback__))
    return failures


def _finally_close_known(descriptors, secondaries):
    """Preflight finally: close all, keep a pending primary, fail if the body succeeded.

    A pending body error stays the propagating primary. Every close failure is
    then an ordered secondary. If the body succeeded, the first close failure
    propagates and only the later close failures are secondaries.
    """
    failures = _close_known_descriptors(descriptors)
    if sys.exc_info()[1] is None and failures:
        error, traceback = failures[0]
        for item in list(failures)[1:]:
            secondaries.append(item)
        raise error.with_traceback(traceback)
    for item in failures:
        secondaries.append(item)




def _read_file(path, cap, mode=None):
    _path(path)
    parent, name = path.rsplit('/', 1)
    fds, rows = _directory_chain(parent)
    descriptor, primary, secondary, result = None, None, _RawG12Errors(), None
    try:
        before = os.stat(name, dir_fd=fds[-1], follow_symlinks=False)
        _need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and
              0 <= before.st_size <= cap and (mode is None or before.st_mode == stat.S_IFREG | mode),
              'G12-N11: regular-file size/mode/link domain')
        descriptor = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC,
                             dir_fd=fds[-1])
        opened = os.fstat(descriptor)
        _need(_identity(before) == _identity(opened) and opened.st_nlink == 1,
              'G12-N11: file changed on open')
        count, blocks, hasher = 0, [], hashlib.sha256()
        while count < opened.st_size:
            block = os.read(descriptor, min(_CHUNK, opened.st_size - count))
            _need(bool(block), 'G12-N11: short file read')
            count += len(block)
            hasher.update(block)
            blocks.append(block)
        _need(os.read(descriptor, 1) == b'', 'G12-N11: file grew')
        after = os.fstat(descriptor)
        ending = os.stat(name, dir_fd=fds[-1], follow_symlinks=False)
        _need(_identity(before) == _identity(after) == _identity(ending) and
              after.st_nlink == ending.st_nlink == 1, 'G12-N11: full file identity changed')
        _check_chain(rows)
        result = ({'path': path, 'sha256': hasher.hexdigest(), 'bytes': count,
                   'identity': _identity(after), 'nlink': 1}, b''.join(blocks))
    except BaseException as error:
        primary = (error, error.__traceback__)
    for fd in ([descriptor] if descriptor is not None else []) + list(reversed(fds)):
        try:
            os.close(fd)
        except BaseException as error:
            secondary.append((error, error.__traceback__))
    _raise_preserved(primary, secondary)
    return result


def _file_record(value):
    _fields(value, ('path', 'sha256', 'bytes', 'identity', 'nlink'))
    _path(value['path'])
    _need(_digest(value['sha256']) and type(value['nlink']) is int and value['nlink'] == 1,
          'G12-N11: file digest/link record')
    _uint(value['bytes'])
    _fields(value['identity'], _ID_NAMES)
    for key in _ID_NAMES:
        _need(type(value['identity'][key]) is int, 'G12-N11: exact stat value')
    _uint(value['identity']['dev'])
    _uint(value['identity']['ino'], True)
    _need(stat.S_ISREG(value['identity']['full_st_mode']) and
          value['identity']['size'] == value['bytes'], 'G12-N11: file identity size/type')


def _pairs(items):
    result = {}
    for key, value in items:
        _need(type(key) is str and key not in result, 'G12-N12: duplicate JSON key')
        result[key] = value
    return result


def _nonfinite(value):
    raise ValueError('G12-N12: nonfinite JSON token: ' + value)


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True,
                      allow_nan=False).encode('ascii')


def _json(raw, cap, canonical=False, newline=False):
    _need(type(raw) is bytes and len(raw) <= cap, 'G12-N12: raw JSON bound')
    # Scan lexical nesting before json.loads recursion or object materialization.
    depth, quoted, escaped = 0, False, False
    for char in raw:
        if quoted:
            if escaped:
                escaped = False
            elif char == 92:
                escaped = True
            elif char == 34:
                quoted = False
        elif char == 34:
            quoted = True
        elif char in (91, 123):
            depth += 1
            _need(depth <= 256, 'G12-N12: JSON depth limit')
        elif char in (93, 125):
            depth -= 1
            _need(depth >= 0, 'G12-N12: JSON nesting')
    _need(depth == 0 and not quoted, 'G12-N12: incomplete JSON')
    value = json.loads(raw.decode('utf-8'), object_pairs_hook=_pairs, parse_constant=_nonfinite)
    pending, count = [(value, 0)], 0
    while pending:
        item, depth = pending.pop()
        count += 1
        _need(count <= cap and depth <= 256, 'G12-N12: JSON node/depth limit')
        if type(item) is dict:
            pending.extend((x, depth + 1) for pair in item.items() for x in pair)
        elif type(item) is list:
            pending.extend((x, depth + 1) for x in item)
        elif type(item) is str:
            _need(len(item) <= cap, 'G12-N12: JSON string limit')
        elif type(item) is float:
            _need(math.isfinite(item), 'G12-N12: overflowed JSON number')
        else:
            _need(item is None or type(item) in (bool, int), 'G12-N12: JSON primitive')
    if canonical:
        _need(raw == _canonical(value) + (b'\n' if newline else b''), 'G12-N12: canonical JSON bytes')
    return value


def _hex(value, cap):
    _need(type(value) is str and len(value) <= cap and len(value) % 2 == 0 and
          all(c in '0123456789abcdef' for c in value), 'G12-N12: complete lowercase hex')
    return bytes.fromhex(value)


def _decimal(value, positive=False):
    _need(type(value) is str and bool(value), 'G12-N12: integer tag text')
    digits = value[1:] if value.startswith('-') else value
    _need(bool(digits) and all(c in '0123456789' for c in digits) and
          (digits == '0' or digits[0] != '0') and value != '-0' and
          (not positive or (not value.startswith('-') and value != '0')), 'G12-N12: canonical integer')


def _tagged(raw, cap):
    value = _json(raw, cap, True)
    pending = [(value, 0)]
    count = 0
    while pending:
        node, depth = pending.pop()
        count += 1
        _need(count <= cap and depth <= 256 and type(node) is list and len(node) >= 1 and
              type(node[0]) is str, 'G12-N12: tagged primitive bound/shape')
        tag = node[0]
        if tag == 'None':
            _need(len(node) == 1, 'G12-N12: None arity')
            continue
        _need(len(node) == (3 if tag == 'Fraction' else 2), 'G12-N12: primitive arity')
        arg = node[1]
        if tag == 'bool':
            _need(type(arg) is bool, 'G12-N12: bool tag')
        elif tag == 'int':
            _decimal(arg)
        elif tag == 'Fraction':
            _decimal(arg)
            _decimal(node[2], True)
        elif tag == 'str':
            _need(type(arg) is str, 'G12-N12: string tag')
        elif tag == 'bytes':
            _hex(arg, cap)
        elif tag == 'float':
            _need(type(arg) is str and float.fromhex(arg).hex() == arg, 'G12-N12: float.hex domain')
        elif tag in ('tuple', 'list'):
            _need(type(arg) is list, 'G12-N12: sequence tag')
            pending.extend((item, depth + 1) for item in arg)
        elif tag == 'dict':
            _need(type(arg) is list, 'G12-N12: ordered dict tag')
            for pair in arg:
                _need(type(pair) is list and len(pair) == 2, 'G12-N12: dict pair')
                pending.extend((item, depth + 1) for item in pair)
        else:
            raise ValueError('G12-N12: unknown primitive tag')
    return value


def _rank_events(encoded):
    value = _tagged(_hex(encoded, _PAIR_CAP), _PAIR_CAP)
    _need(value[0] == 'tuple', 'G12-N12: rank tuple')
    for event in value[1]:
        _need(event[0] == 'tuple' and len(event[1]) == 2 and event[1][0][0] == 'tuple' and
              all(x[0] == 'int' for x in event[1][0][1]) and event[1][1][0] == 'int',
              'G12-N12: rank-event grammar')
    return len(value[1])


def _validate_pair(common_raw, diagnostic_raw):
    common = _json(common_raw, _PAIR_CAP, True, True)
    diagnostic = _json(diagnostic_raw, _PAIR_CAP, True, True)
    spec = _PAIR_SCHEMA
    _fields(common, spec['common_exact_fields'])
    _fields(diagnostic, spec['diagnostic_exact_fields'])
    for key, expected in spec['common_constants'].items():
        _need(_exact(common[key], expected), 'G12-N13: original common source/workload binding')
    for key, expected in spec['diagnostic_constants'].items():
        _need(_exact(diagnostic[key], expected), 'G12-N13: diagnostic source/role binding')
    _need(type(common['literal_original_value']) is bool, 'G12-N12: observed literal exact bool')
    _uint(common['remaining_original_case_count'], True)
    payload = _hex(common['common_payload_hex'], _PAIR_CAP)
    _need(_digest(common['common_payload_sha256']) and
          hashlib.sha256(payload).hexdigest() == common['common_payload_sha256'] ==
          diagnostic['common_payload_sha256'], 'G12-N13: complete common digest join')
    tagged = _tagged(payload, _PAIR_CAP)
    _need(tagged[0] == 'tuple' and len(tagged[1]) == 10, 'G12-N13: common tuple arity')
    prefix = [['str', 'g12-original-remainder-common-v1'],
              ['tuple', [['str', p] for p in spec['common_constants']['original_scientific_pins']]],
              ['int', '25'], ['tuple', [['int', '0'], ['int', '2'], ['int', '1']]]]
    _need(_exact(tagged[1][:4], prefix), 'G12-N13: common inner source/workload prefix')
    suffix = ['tuple', [['str', name] for name in ('verify_role_frames', 'full_log_integer_bounds',
              'original_upstream_verify_sources', 'original_serializable', 'complete_original_cli')]]
    _need(_exact(tagged[1][-1], suffix), 'G12-N13: original suffix phase order')
    for key in ('prefix_end', 'suffix_start', 'cli_end'):
        row = diagnostic[key]
        _fields(row, spec['diagnostic_snapshot_exact_fields'])
        _uint(row['rank_event_count'])
        _need(_rank_events(row['ordered_rank_events_hex']) == row['rank_event_count'] and
              row['native_binding'] is None and row['cache_binding'] is None,
              'G12-N12: original diagnostic rank/binding domain')
        receipt = row['complement_receipt']
        _fields(receipt, spec['complement_receipt_exact_fields'])
        _uint(receipt['calls'])
        _uint(receipt['canonical_stream_bytes'])
        _need(_digest(receipt['sha256']) and receipt['schema'] ==
              'v2-jsonl:call,us,vs,result(type=list+values or type=None); ordered exact integer vectors', 'G12-N12: complement receipt')
    _rank_events(diagnostic['ordered_rank_suffix_hex'])
    _fields(diagnostic['phases'], spec['phase_exact_names'])
    for row in diagnostic['phases'].values():
        _fields(row, ('calls', 'wall_seconds', 'cpu_seconds_with_children'))
        _need(type(row['calls']) is int and row['calls'] == 1, 'G12-N12: phase calls')
        _number(row['wall_seconds'])
        _number(row['cpu_seconds_with_children'])
    return common, diagnostic, payload


def _source_pin(value):
    _fields(value, ('path', 'sha256', 'bytes', 'mode'))
    _path(value['path'])
    _uint(value['bytes'])
    _need(_digest(value['sha256']) and type(value['mode']) is str and len(value['mode']) == 4 and
          all(c in '01234567' for c in value['mode']), 'G12-N02: exact source pin')


def _validate_guard(start, receipt, usage, stdout, stderr, root_argv, invocation, source_pins, phase_sha):
    _fields(start, _GUARD_SCHEMA['START_exact_fields'])
    _fields(receipt, _GUARD_SCHEMA['receipt_exact_fields'])
    _fields(usage, ('user_seconds', 'system_seconds', 'kernel_max_rss_kib', 'exit'))
    for key in start:
        _need(_exact(start[key], receipt[key]), 'G12-N07: original START/receipt field join')
    for key, expected in _GUARD_SCHEMA['required_values'].items():
        _need(_exact(receipt[key], expected), 'G12-N07: original guard success predicate')
    for key in ('job', 'label', 'stage_sha256'):
        _need(_exact(start[key], invocation[key]), 'G12-N07: selected invocation mismatch')
    expected_launch = {'contract': 'trusted-clean-nosite-safe-path-fixedseed-v1',
        'no_site': 1, 'no_user_site': 1, 'safe_path': True, 'ignore_environment': 0,
        'isolated': 0, 'hash_seed_environment': '0', 'hash_randomization': 0,
        'initial_sys_path': ['/usr/lib/python312.zip', '/usr/lib/python3.12', '/usr/lib/python3.12/lib-dynload'],
        'environment': dict(_ENV),
        'trust_boundary': 'Authenticated parent launcher, OS, interpreter and system stdlib before this module; no Python self-authentication claim'}
    _need(_exact(start['parent_launch'], expected_launch), 'G12-N07: exact original clean parent launch')
    _need(_exact(start['command'], root_argv) and start['runner_sha256'] == _GUARD_PIN and
          start['budget_phase_sha256'] == phase_sha and _digest(start['fractions_sha256']),
          'G12-N07: selected command/source/phase binding')
    _need(type(start['phase_cap_seconds']) is int and start['phase_cap_seconds'] in (600, 2400),
          'G12-N05: original aggregate cap')
    _number(start['spent_before_seconds'])
    _need(start['spent_before_seconds'] < start['phase_cap_seconds'], 'G12-N05: consumed budget')
    for key in ('wall_seconds', 'runner_wall_seconds', 'runner_user_seconds', 'runner_system_seconds',
                'runner_lifetime_max_rss_kib', 'sampled_process_group_rss_bytes'):
        _number(receipt[key])
    limit = min(180, start['phase_cap_seconds'] - start['spent_before_seconds'])
    _need(receipt['wall_seconds'] <= limit and receipt['runner_wall_seconds'] <= limit and
          receipt['runner_lifetime_max_rss_kib'] * 1024 <= 1073741824 and
          receipt['sampled_process_group_rss_bytes'] <= 1073741824,
          'G12-N07: original guard resource caps')
    for key in ('user_seconds', 'system_seconds', 'kernel_max_rss_kib'):
        _number(usage[key])
    _need(type(usage['exit']) is int and usage['exit'] == 0 and _exact(usage, receipt['usage']),
          'G12-N07: complete original usage join')
    for name, raw in (('stdout', stdout), ('stderr', stderr)):
        _need(len(raw) <= _LOG_CAP and receipt[name + '_bytes'] == len(raw) and
              type(receipt[name + '_bytes']) is int and receipt[name + '_final_bytes'] == len(raw) and
              type(receipt[name + '_final_bytes']) is int and
              receipt[name + '_sha256'] == hashlib.sha256(raw).hexdigest(), 'G12-N07: complete raw log join')
    _need(stderr == b'' and type(receipt['python']) is str and type(receipt['platform']) is str,
          'G12-N07: original stderr/platform fields')


def _capture_graph(namespace):
    """Capture the fixed own/JSON function graph before candidate exposure."""
    modules = (json, json.decoder, json.encoder, json.scanner, hashlib, os, stat, math) + tuple(
        namespace[name] for name in ('subprocess', 'fcntl', 'signal', 'resource', 'time') if name in namespace)
    namespaces = [namespace] + [module.__dict__ for module in modules]
    namespaces.extend((json._default_decoder.__dict__, json._default_encoder.__dict__))
    records, members, seen = [], [], set()
    for mapping in namespaces:
        members.append((mapping, tuple(mapping.items())))
        for value in mapping.values():
            candidates = [value]
            if type(value) is type:
                candidates.extend(value.__dict__.values())
                if value.__module__ in (__name__, 'json.decoder', 'json.encoder', 'subprocess'):
                    members.append((value.__dict__, tuple(value.__dict__.items())))
            for function in candidates:
                if type(function) is not FunctionType or id(function) in seen:
                    continue
                seen.add(id(function))
                records.append((function, function.__code__, function.__globals__, function.__builtins__,
                    function.__defaults__, function.__kwdefaults__, function.__closure__,
                    tuple(function.__dict__.items()),
                    () if function.__kwdefaults__ is None else tuple(function.__kwdefaults__.items()),
                    () if function.__closure__ is None else tuple((c, c.cell_contents) for c in function.__closure__)))
    data = tuple((name, _canonical(namespace[name])) for name in
                 ('_PAIR_SCHEMA', '_MANIFEST_SCHEMA', '_GUARD_SCHEMA', '_PUBLICATION_SCHEMA',
                  '_ENGINE_PINS', '_OTHER_SOURCE_PINS', '_ENV', '_EVIDENCE_NAMES') if name in namespace)
    return tuple(records), tuple(members), data



def _current_graph(graph):
    records, members, data = graph
    for mapping, rows in members:
        # The capture itself is assigned once after this snapshot.
        expected = dict(rows)
        for name, value in rows:
            _need(mapping.get(name, _MISSING) is value, 'G12-N04: captured namespace member changed: ' + name)
        extra = set(mapping) - set(expected)
        _need(not extra or mapping is globals() and extra == {'_INITIAL_GRAPH'},
              'G12-N04: captured namespace census changed')
    for name, expected in data:
        _need(_canonical(globals()[name]) == expected, 'G12-N04: source-owned schema constant changed')
    for f, code, namespace, builtin, defaults, kw, cells, attrs, kws, contents in records:
        _need(f.__code__ is code and f.__globals__ is namespace and f.__builtins__ is builtin and
              f.__defaults__ is defaults and f.__kwdefaults__ is kw and f.__closure__ is cells and
              len(f.__dict__) == len(attrs), 'G12-N04: captured function graph changed')
        for name, value in attrs:
            _need(f.__dict__.get(name, _MISSING) is value, 'G12-N04: function attributes changed')
        if kw is not None:
            _need(len(kw) == len(kws), 'G12-N04: keyword-default census changed')
            for name, value in kws:
                _need(kw.get(name, _MISSING) is value, 'G12-N04: keyword defaults changed')
        for cell, value in contents:
            _need(cell.cell_contents is value, 'G12-N04: captured closure changed')



_PAIR_SCHEMA = {'common_constants': {'authority_source_sha256': 'f279ab86fc17c6a517b035f19d56863919cbd8304de4e7d5332457c6159aec10',
                      'extra_target': [0, 2, 1],
                      'h': 25,
                      'literal_original_type': 'bool',
                      'original_driver_sha256': '0d976d2eb6b845f20d4a3396591a806f966688b88693cd6a5f8a0c9e48925e36',
                      'original_scientific_pins': ['d623617f7c5cb3189580883a8ab30c0bd3832688ae3f1f0c1f881bbbbff8e0c1',
                                                   '0da395e67ac04fa213494e71012c1b19b544596d34cdce5a3b172b1fb6af5f1b',
                                                   '88bba3caf5975f30fa7abceaea9454110cf3b069233e8241a2ca13d1dff171a7',
                                                   'adc7f1241b42e322a6451854ab7e4b4c146bf78a'],
                      'producer_role': 'independent-original-uncached',
                      'schema': 'g12-independent-original-reference-envelope-v1',
                      'scope': 'Actual original N22 literal and P07 common remainder observations only; '
                               'no original PROFILE_ANCHOR_PASS, FULL_PASS, native qualification or G12 '
                               'approval.',
                      'selected_driver_sha256': 'a346025d5b6e2b26246521c6af6292643a4c2c3286b33ff3996dcf051cd6be26'},
 'common_exact_fields': ['schema',
                         'producer_role',
                         'selected_driver_sha256',
                         'original_driver_sha256',
                         'authority_source_sha256',
                         'original_scientific_pins',
                         'h',
                         'extra_target',
                         'literal_original_type',
                         'literal_original_value',
                         'remaining_original_case_count',
                         'common_payload_sha256',
                         'common_payload_hex',
                         'scope'],
 'complement_receipt_exact_fields': ['calls', 'canonical_stream_bytes', 'sha256', 'schema'],
 'diagnostic_constants': {'complement_suffix_limit': 'Only cumulative original start/end receipts; no '
                                                     'digest subtraction or suffix-stream claim.',
                          'completion': 'Exact source-owned intentional marker followed by original '
                                        'finally, exact observer restoration, both cold2 checks and '
                                        'original source/output custody.',
                          'producer_role': 'independent-original-uncached',
                          'schema': 'g12-independent-original-reference-diagnostics-v1',
                          'selected_driver_sha256': 'a346025d5b6e2b26246521c6af6292643a4c2c3286b33ff3996dcf051cd6be26'},
 'diagnostic_exact_fields': ['schema',
                             'producer_role',
                             'selected_driver_sha256',
                             'common_payload_sha256',
                             'prefix_end',
                             'suffix_start',
                             'cli_end',
                             'ordered_rank_suffix_hex',
                             'complement_suffix_limit',
                             'phases',
                             'completion'],
 'diagnostic_snapshot_exact_fields': ['rank_event_count',
                                      'ordered_rank_events_hex',
                                      'complement_receipt',
                                      'native_binding',
                                      'cache_binding'],
 'phase_exact_names': ['input_custody',
                       'engine_custody',
                       'fresh_root_copy',
                       'fresh_engine_copy',
                       'cold_engine_import',
                       'cold_complex_module_load',
                       'cold_certify_import',
                       'cold_prepare_import',
                       'side_construction',
                       'checks_initialization',
                       'compile_roles',
                       'verify_map',
                       'verify_labels',
                       'verify_role_frames',
                       'original_upstream_verify_sources',
                       'full_log_integer_bounds',
                       'original_serializable',
                       'complete_original_cli']}


_MANIFEST_SCHEMA = {'accounting_exact_fields': ['clock',
                             'parent_entry_ns',
                             'preseal_end_ns',
                             'parent_preseal_wall_ns',
                             'parent_self_user_seconds',
                             'parent_self_system_seconds',
                             'parent_children_user_seconds',
                             'parent_children_system_seconds',
                             'parent_lifetime_max_rss_kib',
                             'guard_usage',
                             'guard_runner_wall_seconds',
                             'categories',
                             'complete_tail_accounting_required',
                             'unmeasured_final_tail'],
 'cleanup_exact_fields': ['operating_premises',
                          'owned_generations',
                          'observed_groups',
                          'remaining',
                          'current_children',
                          'known_streams_closed',
                          'known_pidfds_closed',
                          'io_unknown',
                          'lease_identity',
                          'science_directory_identity',
                          'observations_record'],
 'custody_exact_fields': ['retained_directory',
                          'retained_directory_identity',
                          'retained_file_mode',
                          'created_after_known_cleanup',
                          'source_selection_required',
                          'known_close_policy'],
 'exact_top_level_fields': ['schema',
                            'invocation',
                            'selected_sources',
                            'workload',
                            'launch',
                            'terminal',
                            'guard',
                            'cleanup',
                            'pair',
                            'retained_evidence',
                            'custody',
                            'accounting',
                            'scope'],
 'guard_exact_fields': ['start',
                        'receipt',
                        'start_fields',
                        'receipt_fields',
                        'stdout',
                        'stderr',
                        'usage'],
 'invocation_exact_fields': ['stage',
                             'job',
                             'label',
                             'stage_sha256',
                             'jobs_sha256',
                             'launch_selection_sha256'],
 'launch_exact_fields': ['parent_pid',
                         'parent_start_ticks',
                         'guard_pid',
                         'guard_start_ticks',
                         'guard_pgid',
                         'guard_sid',
                         'parent_guard_argv',
                         'guard_root_argv',
                         'adapter_producer_argv',
                         'cwd',
                         'environment',
                         'flags',
                         'launch_record'],
 'pair_exact_fields': ['common', 'diagnostics', 'common_payload_sha256'],
 'retained_evidence_exact_keys': ['guard_START',
                                  'guard_receipt',
                                  'guard_stdout',
                                  'guard_stderr',
                                  'guard_usage',
                                  'parent_launch',
                                  'parent_outer_stdout',
                                  'parent_outer_stderr',
                                  'parent_owned_observations',
                                  'parent_preseal_accounting'],
 'schema_literal': 'g12-parent-two-export-custody-v2',
 'selected_sources_exact_fields': ['parent',
                                   'guard',
                                   'root',
                                   'provider',
                                   'adapter',
                                   'producer',
                                   'authority',
                                   'source_pins',
                                   'reference',
                                   'engine',
                                   'runtime_profile',
                                   'cleanup_leaf_origin'],
 'terminal_exact_fields': ['actual_popen_returncode',
                           'wait_completed',
                           'parent_stop',
                           'primary_error',
                           'secondary_errors',
                           'guard_receipt_missing'],
 'workload_exact_fields': ['role',
                           'h',
                           'extra_target',
                           'mode',
                           'anchor',
                           'optimize',
                           'original_scientific_pins'],
 'workload_values': {'anchor': None,
                     'extra_target': [0, 2, 1],
                     'h': 25,
                     'mode': 'profile',
                     'optimize': 0,
                     'original_scientific_pins': ['d623617f7c5cb3189580883a8ab30c0bd3832688ae3f1f0c1f881bbbbff8e0c1',
                                                  '0da395e67ac04fa213494e71012c1b19b544596d34cdce5a3b172b1fb6af5f1b',
                                                  '88bba3caf5975f30fa7abceaea9454110cf3b069233e8241a2ca13d1dff171a7',
                                                  'adc7f1241b42e322a6451854ab7e4b4c146bf78a'],
                     'role': 'independent-original-uncached'}}


_GUARD_SCHEMA = {'START_exact_fields': ['command',
                        'parent_launch',
                        'stage_sha256',
                        'runner_sha256',
                        'fractions_sha256',
                        'budget_phase_sha256',
                        'spent_before_seconds',
                        'phase_cap_seconds',
                        'job',
                        'label'],
 'receipt_exact_fields': ['command',
                          'parent_launch',
                          'stage_sha256',
                          'runner_sha256',
                          'fractions_sha256',
                          'budget_phase_sha256',
                          'spent_before_seconds',
                          'phase_cap_seconds',
                          'job',
                          'label',
                          'exit',
                          'wall_seconds',
                          'usage',
                          'termination',
                          'sampled_process_group_rss_bytes',
                          'source_bytes_and_modes_unchanged',
                          'stdout_sha256',
                          'stdout_bytes',
                          'stderr_sha256',
                          'stderr_bytes',
                          'stdout_final_bytes',
                          'stderr_final_bytes',
                          'retained_log_bytes_stable',
                          'output_cap_observed_at',
                          'log_read_chunk_bytes',
                          'runner_wall_seconds',
                          'runner_user_seconds',
                          'runner_system_seconds',
                          'runner_lifetime_max_rss_kib',
                          'python',
                          'platform',
                          'status'],
 'required_values': {'exit': 0,
                     'log_read_chunk_bytes': 65536,
                     'output_cap_observed_at': None,
                     'retained_log_bytes_stable': True,
                     'source_bytes_and_modes_unchanged': True,
                     'status': 'PASS',
                     'stderr_bytes': 0,
                     'stderr_final_bytes': 0,
                     'termination': None}}


_PUBLICATION_SCHEMA = {'exact_fields': ['schema',
                  'parent_source_sha256',
                  'launch_selection_sha256',
                  'manifest_path',
                  'manifest_sha256',
                  'manifest_bytes',
                  'manifest_identity',
                  'retained_pair_sha256',
                  'final_pair_recheck_complete',
                  'known_lease_close_completed',
                  'primary_error',
                  'secondary_errors',
                  'measured_through_ns',
                  'actual_costs_through_ns',
                  'unmeasured_final_tail',
                  'complete_cost_qualification'],
 'schema_literal': 'g12-parent-custody-publication-v2'}


_COST_CATEGORIES = ('source/stage/plan/authentication and dependency preflight', 'parent invocation setup and known lease operations', 'adapter bootstrap source read/hash/compile/exec and argv/module alias custody/restoration', 'entire independent uncached reference including fresh copies/engine imports/original CLI/trace capture/original checks/finally/restoration/cold2', 'guard launch/time/monitoring/STOP/final original source inventory/usage/raw-log hashing/receipt', 'actual parent wait and known descendant/group/FD cleanup', 'canonical receipt and START joins plus all complete raw evidence retention', 'both exports full reads/hashes/JSON/schema/payload decode/crosslinks and repeated pair checks', 'new parent copies/write/fsync/chmod/close/directory sync/readback', 'manifest schema/write/hash/fsync/close/readback and source-selection publication tail', 'parent failure/secondary-error retention and necessary cleanup after deadline', 'cold consumer complete manifest/pair/publication read/hash/parse/decode/recheck and all retained alias lifetimes')


def _validate_manifest(manifest, parent_path, parent_sha):
    spec = _MANIFEST_SCHEMA
    _fields(manifest, spec['exact_top_level_fields'])
    _need(manifest['schema'] == spec['schema_literal'], 'G12-N12: custody schema')
    for name in ('invocation', 'selected_sources', 'workload', 'launch', 'terminal', 'guard',
                 'cleanup', 'pair', 'custody', 'accounting'):
        _fields(manifest[name], spec[name + '_exact_fields'])
    _fields(manifest['retained_evidence'], spec['retained_evidence_exact_keys'])
    _need(_exact(manifest['workload'], spec['workload_values']), 'G12-N13: fixed workload')
    invocation = manifest['invocation']
    _need(invocation['stage'] == 'g12-reference-custody-v1' and invocation['job'] == 'g12-reference' and
          type(invocation['label']) is str and bool(invocation['label']) and
          all(c in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_' for c in invocation['label']),
          'G12-N13: fixed invocation role')
    for name in ('stage_sha256', 'jobs_sha256', 'launch_selection_sha256'):
        _need(_digest(invocation[name]), 'G12-N12: invocation digest')
    sources = manifest['selected_sources']
    for name, pin in sources.items():
        if name != 'engine':
            _source_pin(pin)
    for name, expected in (('guard', _GUARD_PIN), ('root', _ROOT_PIN), ('provider', _PROVIDER_PIN),
                           ('producer', _PRODUCER_PIN), ('authority', _AUTHORITY_PIN)):
        _need(sources[name]['sha256'] == expected and sources[name]['mode'] == '0444',
              'G12-N02: selected original source mismatch')
    _need(sources['producer']['bytes'] == 70246 and sources['parent']['path'] == parent_path and
          sources['parent']['sha256'] == parent_sha, 'G12-N02: selected producer/parent identity')
    _need(_exact(sources['engine'], _ENGINE_PINS), 'G12-N02: exact original engine source pins')
    for name, expected in _OTHER_SOURCE_PINS.items():
        _need(sources[name]['sha256'] == expected, 'G12-N02: selected original dependency mismatch')
    terminal = {'actual_popen_returncode': 0, 'wait_completed': True, 'parent_stop': None,
                'primary_error': None, 'secondary_errors': [], 'guard_receipt_missing': False}
    _need(_exact(manifest['terminal'], terminal), 'G12-N06: authenticated terminal data rejects')
    cleanup = manifest['cleanup']
    _need(_exact(cleanup['remaining'], []) and _exact(cleanup['current_children'], []) and
          cleanup['known_streams_closed'] is True and cleanup['known_pidfds_closed'] is True and
          cleanup['io_unknown'] is False and type(cleanup['owned_generations']) is list and
          bool(cleanup['owned_generations']) and _exact(cleanup['operating_premises'], _OPERATING_PREMISES),
          'G12-N08: known selected chain custody rejects')
    for name in ('parent_pid', 'parent_start_ticks', 'guard_pid', 'guard_start_ticks', 'guard_pgid', 'guard_sid'):
        _uint(manifest['launch'][name], True)
    label = invocation['label']
    stage = _R + '/stages/g12-reference-custody-v1'
    science = _R + '/runtime/runs/' + label + '/science'
    parent_argv, root_argv, producer_argv = _fixed_argv(label, sources)
    launch = manifest['launch']
    _need(_exact(launch['parent_guard_argv'], parent_argv) and _exact(launch['guard_root_argv'], root_argv) and
          _exact(launch['adapter_producer_argv'], producer_argv) and launch['cwd'] == _R and
          _exact(launch['environment'], _ENV) and _exact(launch['flags'], list(_FLAGS)),
          'G12-N03: exact fixed launch/adapter argv')
    retained = _R + '/runtime/g12-reference-parent-custody-v1/' + label
    custody = manifest['custody']
    _need(custody['retained_directory'] == retained and custody['retained_file_mode'] == '0444' and
          custody['created_after_known_cleanup'] is True and custody['source_selection_required'] is True and
          custody['known_close_policy'] == 'Any unknown close rejects publication', 'G12-N14: custody ownership')
    _fields(custody['retained_directory_identity'], _ID_NAMES)
    _need(custody['retained_directory_identity']['full_st_mode'] == stat.S_IFDIR | 0o500,
          'G12-N14: final retained directory mode')
    for name in ('common', 'diagnostics'):
        pair = manifest['pair'][name]
        _fields(pair, ('original', 'retained'))
        _file_record(pair['original'])
        _file_record(pair['retained'])
        filename = 'g12-reference.' + name + '.json'
        _need(pair['original']['path'] == science + '/' + filename and
              pair['retained']['path'] == retained + '/' + filename and
              pair['original']['sha256'] == pair['retained']['sha256'] and
              pair['original']['bytes'] == pair['retained']['bytes'] and
              pair['retained']['identity']['full_st_mode'] == stat.S_IFREG | 0o444,
              'G12-N13: original/retained complete pair join')
    _need(_digest(manifest['pair']['common_payload_sha256']), 'G12-N13: payload pin')
    for name, record in manifest['retained_evidence'].items():
        _file_record(record)
        _need(record['path'] == retained + '/' + _EVIDENCE_NAMES[name] and
              record['identity']['full_st_mode'] == stat.S_IFREG | 0o444,
              'G12-N14: retained raw evidence path/mode')
    for name, evidence_name in (('start', 'guard_START'), ('receipt', 'guard_receipt'),
                               ('stdout', 'guard_stdout'), ('stderr', 'guard_stderr'), ('usage', 'guard_usage')):
        _need(_exact(manifest['guard'][name], manifest['retained_evidence'][evidence_name]),
              'G12-N07: guard retained record join')
    _need(_exact(launch['launch_record'], manifest['retained_evidence']['parent_launch']) and
          _exact(cleanup['observations_record'], manifest['retained_evidence']['parent_owned_observations']),
          'G12-N08: parent observation record join')
    account = manifest['accounting']
    _need(account['clock'] == 'monotonic_ns' and account['complete_tail_accounting_required'] is True and
          _exact(account['categories'], list(_COST_CATEGORIES)), 'G12-N15: full cost categories/tail')
    for name in ('parent_entry_ns', 'preseal_end_ns', 'parent_preseal_wall_ns'):
        _uint(account[name])
    _need(account['preseal_end_ns'] >= account['parent_entry_ns'] and
          account['parent_preseal_wall_ns'] == account['preseal_end_ns'] - account['parent_entry_ns'],
          'G12-N15: actual parent clock endpoints')
    for name in ('parent_self_user_seconds', 'parent_self_system_seconds', 'parent_children_user_seconds',
                 'parent_children_system_seconds', 'parent_lifetime_max_rss_kib', 'guard_runner_wall_seconds'):
        _number(account[name])
    _need(account['unmeasured_final_tail'] is None, 'G12-N15: unmeasured tail must stay explicitly unknown')
    _need(_exact(account['guard_usage'], manifest['guard']['receipt_fields']['usage']) and
          _exact(account['guard_runner_wall_seconds'], manifest['guard']['receipt_fields']['runner_wall_seconds']),
          'G12-N15: actual guard cost join')
    _need(manifest['scope'] == _SCOPE, 'G12-N18: custody scope cannot become scientific approval')


def _fixed_argv(label, sources):
    stage = _R + '/stages/g12-reference-custody-v1'
    science = _R + '/runtime/runs/' + label + '/science'
    parent = ['/usr/bin/python3.12', *_FLAGS, _R + '/run_guarded_v3.py',
              'g12-reference-custody-v1', 'g12-reference', label]
    root = ['/usr/bin/python3.12', *_FLAGS, stage + '/integration/full_driver.py',
            '--root-sha256', _ROOT_PIN, '--provider', stage + '/integration/probe_binding_v3.py',
            _PROVIDER_PIN, '--driver', stage + '/integration/g12_reference_adapter_v1.py',
            sources['adapter']['sha256'], '--integration', stage + '/integration', '--',
            '--output', science, '--lanes', 'g12-reference']
    producer = [stage + '/baseline/full_driver.py', '--frozen-root', stage + '/baseline/frozen',
                '--reference', stage + '/baseline/reference/certificates/complex-network.json',
                '--mode', 'profile', '--output', science]
    return parent, root, producer


def _validate_publication(publication, manifest, manifest_record):
    _fields(publication, _PUBLICATION_SCHEMA['exact_fields'])
    _need(publication['schema'] == _PUBLICATION_SCHEMA['schema_literal'] and
          publication['parent_source_sha256'] == manifest['selected_sources']['parent']['sha256'] and
          publication['launch_selection_sha256'] == manifest['invocation']['launch_selection_sha256'] and
          publication['manifest_path'] == manifest_record['path'] and
          publication['manifest_sha256'] == manifest_record['sha256'] and
          publication['manifest_bytes'] == manifest_record['bytes'] and
          _exact(publication['manifest_identity'], manifest_record['identity']) and
          _exact(publication['retained_pair_sha256'], {name: manifest['pair'][name]['retained']['sha256']
                                                     for name in ('common', 'diagnostics')}) and
          publication['final_pair_recheck_complete'] is True and publication['known_lease_close_completed'] is True and
          publication['primary_error'] is None and _exact(publication['secondary_errors'], []) and
          publication['complete_cost_qualification'] is False and
          _exact(publication['unmeasured_final_tail'], manifest['accounting']['unmeasured_final_tail']),
          'G12-N15: exact publication/manifest/final-tail join')
    _uint(publication['measured_through_ns'])
    _need(publication['measured_through_ns'] >= manifest['accounting']['preseal_end_ns'],
          'G12-N15: publication clock precedes preseal')
    costs = publication['actual_costs_through_ns']
    _fields(costs, ('entry_ns', 'through_ns', 'wall_ns', 'self_user_seconds', 'self_system_seconds',
                    'children_user_seconds', 'children_system_seconds', 'lifetime_max_rss_kib'))
    for name in ('entry_ns', 'through_ns', 'wall_ns'):
        _uint(costs[name])
    _need(costs['entry_ns'] == manifest['accounting']['parent_entry_ns'] and
          costs['through_ns'] == publication['measured_through_ns'] and
          costs['wall_ns'] == costs['through_ns'] - costs['entry_ns'], 'G12-N15: publication actual clock join')
    for name in ('self_user_seconds', 'self_system_seconds', 'children_user_seconds',
                 'children_system_seconds', 'lifetime_max_rss_kib'):
        _number(costs[name])


def _source_code_shape(code):
    _need(type(code) is CodeType, 'G12-N04: exact code type')
    def constant(value):
        kind = type(value)
        if value is None or value is Ellipsis:
            return ('singleton', value is Ellipsis)
        if kind in (int, bool, str, bytes):
            return (kind.__name__, value)
        if kind is float:
            return ('float', value.hex())
        if kind is tuple:
            return ('tuple', tuple(constant(item) for item in value))
        if kind is frozenset:
            return ('frozenset', tuple(sorted(constant(item) for item in value)))
        if kind is CodeType:
            return ('code', _source_code_shape(value))
        raise RuntimeError('G12-N04: unsupported source code constant')
    return tuple(constant(value) for value in (
        code.co_argcount, code.co_posonlyargcount, code.co_kwonlyargcount,
        code.co_nlocals, code.co_stacksize, code.co_flags, code.co_code,
        code.co_names, code.co_varnames, code.co_freevars, code.co_cellvars,
        code.co_exceptiontable, code.co_linetable, code.co_firstlineno,
        code.co_filename, code.co_name, code.co_qualname, code.co_consts))


_R = '/home/d3lerium/.codex/.chatgpt-projects/g-p-6ad5817fd84881918865926b6fd51453/outputs/h25-data-handling-20261028'


_ENGINE_PINS = {'compare_side_verifier.py': '6e507bb0c7e00d090a60289fddb6c55e90c946d0850c42c3c5e3e15c27604a68',
 'finite_controls.py': 'df989a831aac43cc1af95169dad8c64a7548760e6e1f96976da996703f2c8f7a',
 'native_backend.py': 'e473c38245c3668715b5a78dfe980b2fe3ed0d0c9b8c97c666fbae6ecf1fffd5',
 'native_gf2.c': 'e9c3c9194a08718bd1575c1cf08c6c6772d3b644c2e274c25a84a1f9249d06cc',
 'profile_side_verifier.py': '9c994378171c20a91539418d93cb8387e1daa93465d6862beefea90e12999c2a',
 'source/complex_circuit.py': 'd623617f7c5cb3189580883a8ab30c0bd3832688ae3f1f0c1f881bbbbff8e0c1',
 'source/complex_network.py': '0da395e67ac04fa213494e71012c1b19b544596d34cdce5a3b172b1fb6af5f1b'}


_OTHER_SOURCE_PINS = {'cleanup_leaf_origin': '7b3304eaf4884e3029df5095e2b0950c18d1544ad21431a07c033b85e53bd4f7',
 'reference': '1f763d95c7ff163aa71d13cd82784f16665be8afb21f75e76941e2119562098f',
 'runtime_profile': 'ad0ec2aea01b83f97bdeafd9e9208360127fee870d024d353879b5ed99237109',
 'source_pins': '88bba3caf5975f30fa7abceaea9454110cf3b069233e8241a2ca13d1dff171a7'}


_OPERATING_PREMISES = ('Selected fixed scientific sources, adapter and ordinary profile branch do not fork/spawn threads, '
 'daemonize, pass writable descriptors to outsiders, or enlist external writers. Trusted '
 'OS/loader/interpreter/stdlib and cooperating same-user parent launch domain exclude unrelated writer '
 'interference. This is an explicit finite source/operating premise, not established merely by a clean /proc '
 'snapshot.')


_SCOPE = ('Fixed source-data custody only. No G12/P02/full-positive/native/performance/scientific admission; no '
 'universal writers theorem.')


_FLAGS = ('-S', '-s', '-P', '-B')


_ENV = {'LANG': 'C.UTF-8',
 'LC_ALL': 'C.UTF-8',
 'PATH': '/usr/bin:/bin',
 'PYTHONDONTWRITEBYTECODE': '1',
 'PYTHONHASHSEED': '0',
 'TZ': 'UTC'}


_EVIDENCE_NAMES = {'guard_START': 'guard-START.json',
 'guard_receipt': 'guard-receipt.json',
 'guard_stderr': 'guard-stderr.txt',
 'guard_stdout': 'guard-stdout.txt',
 'guard_usage': 'guard-usage.json',
 'parent_launch': 'parent-LAUNCH.json',
 'parent_outer_stderr': 'parent-outer-stderr.txt',
 'parent_outer_stdout': 'parent-outer-stdout.txt',
 'parent_owned_observations': 'parent-owned-observations.json',
 'parent_preseal_accounting': 'parent-preseal-accounting.json'}



def _proc(pid):
    # Derived from original supervisor proc; PermissionError is never absence.
    descriptor, primary, secondaries, result = None, None, _RawG12Errors(), None
    try:
        descriptor = os.open('/proc/' + str(pid) + '/stat', os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
        raw = os.read(descriptor, 8193)
        _need(len(raw) <= 8192 and os.read(descriptor, 1) == b'', 'G12-N08: process-stat finite bound')
        end = raw.rfind(b') ')
        _need(end >= 0 and raw.split(b' ', 1)[0] == str(pid).encode('ascii'), 'G12-N08: process-stat PID')
        fields = raw[end + 2:].split()
        _need(len(fields) >= 22 and fields[0] in (b'R', b'S', b'D', b'Z', b'T', b't', b'X', b'x', b'I', b'K', b'W', b'P'),
              'G12-N08: process-stat shape/state')
        result = {'pid': pid, 'ppid': int(fields[1]), 'pgid': int(fields[2]), 'sid': int(fields[3]),
                  'start_ticks': int(fields[19]), 'state': fields[0].decode('ascii'),
                  'rss_bytes': int(fields[21]) * os.sysconf('SC_PAGE_SIZE')}
        for key in ('pid', 'ppid', 'pgid', 'sid', 'start_ticks', 'rss_bytes'):
            _uint(result[key], key in ('pid', 'start_ticks'))
    except (FileNotFoundError, ProcessLookupError):
        result = None
    except BaseException as error:
        primary = error, error.__traceback__
    if descriptor is not None:
        try:
            os.close(descriptor)
        except BaseException as error:
            secondaries.append((error, error.__traceback__))
    _raise_preserved(primary, secondaries)
    return result


def _census():
    rows = {}
    with os.scandir('/proc') as entries:
        for entry in entries:
            if entry.name.isdecimal():
                _need(len(rows) < 65536, 'G12-N08: finite process census bound')
                row = _proc(int(entry.name))
                if row is not None:
                    rows[row['pid']] = row
    return rows


def _children():
    return [row for row in _census().values() if row['ppid'] == os.getpid()]


class _KnownG12Chain:
    """Scoped generation/pidfd observation only; never universal writer proof."""
    def __init__(self):
        _need(not _children(), 'G12-N08: initial parent child domain must be empty')
        _need(os.listdir('/proc/self/task') == [str(os.getpid())], 'G12-N08: single initial parent task')
        self.rows, self.fds, self.groups, self.observations = {}, {}, set(), []
        self.parent_pid = os.getpid()
        self.parent_group = os.getpgrp()
        self.closed = False
        self.unknown = False

    def add(self, row):
        key = row['pid'], row['start_ticks']
        if key in self.rows:
            _need(self.rows[key]['pid'] == row['pid'], 'G12-N08: owned generation identity')
            if row['pgid'] != self.parent_group:
                self.groups.add((row['pgid'], row['sid']))
            return
        _need(row['pid'] != self.parent_pid and len(self.rows) < 128, 'G12-N08: fixed owned process bound')
        descriptor = os.pidfd_open(row['pid'], 0)
        # A failed/ambiguous adoption rejects; never treat it as known closure.
        self.fds[key] = descriptor
        current = _proc(row['pid'])
        _need(current is not None and (current['pid'], current['start_ticks']) == key,
              'G12-N08: process generation changed during pidfd adoption')
        self.rows[key] = dict(current)
        if current['pgid'] != self.parent_group:
            self.groups.add((current['pgid'], current['sid']))

    def observe(self):
        _need(not self.closed, 'G12-N08: closed observation domain')
        rows = _census()
        known = {pid for pid, start in self.rows if pid in rows and rows[pid]['start_ticks'] == start}
        for pid in known:
            self.add(rows[pid])
        changed = True
        while changed:
            changed = False
            for pid, row in rows.items():
                if pid not in known and (row['ppid'] == self.parent_pid or row['ppid'] in known):
                    self.add(row)
                    known.add(pid)
                    changed = True
        occupied = [row for row in rows.values() if (row['pgid'], row['sid']) in self.groups]
        current = [rows[pid] for pid in known]
        _need(len(self.observations) < 4096, 'G12-N08: finite observation retention')
        self.observations.append({'monotonic_ns': time.monotonic_ns(), 'current': current, 'occupied_groups': occupied})
        return rows, current, occupied

    def stop_known(self):
        self.observe()
        for key, descriptor in self.fds.items():
            current = _proc(key[0])
            if current is not None:
                _need((current['pid'], current['start_ticks']) == key, 'G12-N08: generation ambiguity before signal')
                if current['state'] != 'Z':
                    try:
                        signal.pidfd_send_signal(descriptor, signal.SIGKILL, None, 0)
                    except ProcessLookupError:
                        pass

    def finish(self, process, deadline, failed):
        _need(type(deadline) is int, 'G12-N08: selected paid cleanup deadline')
        current, occupied = [], []
        while True:
            if failed:
                self.stop_known()
            if process is not None:
                process.poll()
            _, current, occupied = self.observe()
            if not current and not occupied and not _children():
                break
            if not failed or time.monotonic_ns() >= deadline:
                raise RuntimeError('G12-N08: selected-chain cleanup UNKNOWN')
            time.sleep(0.01)
        primary, secondaries = None, _RawG12Errors()
        for key, descriptor in tuple(self.fds.items()):
            try:
                os.close(descriptor)
                del self.fds[key]
            except BaseException as error:
                self.unknown = True
                secondaries.append((error, error.__traceback__))
        self.closed = not self.fds and not self.unknown
        _raise_preserved(primary, secondaries)
        return {'operating_premises': _OPERATING_PREMISES,
                'owned_generations': list(self.rows.values()),
                'observed_groups': [{'pgid': g, 'sid': s} for g, s in sorted(self.groups)],
                'remaining': [], 'current_children': [], 'known_streams_closed': False,
                'known_pidfds_closed': self.closed, 'io_unknown': self.unknown,
                'lease_identity': None, 'science_directory_identity': None,
                'observations_record': None}


def _trusted_parent_launch():
    _need(sys.executable == '/usr/bin/python3.12' and sys.flags.optimize == 0 and
          sys.flags.no_site == sys.flags.no_user_site == sys.flags.dont_write_bytecode == 1 and
          sys.flags.safe_path and sys.flags.ignore_environment == sys.flags.isolated == sys.flags.hash_randomization == 0,
          'G12-N02: original clean parent interpreter flags')
    _need(dict(os.environ) == _ENV and tuple(sys.path) ==
          ('/usr/lib/python312.zip', '/usr/lib/python3.12', '/usr/lib/python3.12/lib-dynload'),
          'G12-N02: original clean environment/search path')
    _need(sys.gettrace() is None and sys.getprofile() is None, 'G12-N04: no parent tracing callbacks')


def _exclusive_directory(path):
    parent, name = _path(path).rsplit('/', 1)
    fds, rows = _directory_chain(parent)
    primary, secondaries, result = None, _RawG12Errors(), None
    try:
        os.mkdir(name, 0o700, dir_fd=fds[-1])
        descriptor = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=fds[-1])
        fds.append(descriptor)
        current = os.fstat(descriptor)
        _need(current.st_mode == stat.S_IFDIR | 0o700, 'G12-N14: new parent directory mode')
        rows.append((fds[-2], name, descriptor, _directory_key(current)))
        _check_chain(rows)
        result = fds, rows
    except BaseException as error:
        primary = error, error.__traceback__
    if primary is not None:
        for descriptor in reversed(fds):
            try:
                os.close(descriptor)
            except BaseException as error:
                secondaries.append((error, error.__traceback__))
        _raise_preserved(primary, secondaries)
    return result


def _write_fd(descriptor, raw):
    _need(type(raw) is bytes, 'G12-N14: exact retained byte copy')
    offset, hasher = 0, hashlib.sha256()
    while offset < len(raw):
        block = raw[offset:offset + _CHUNK]
        written = os.write(descriptor, block)
        _need(type(written) is int and 0 < written <= len(block), 'G12-N14: complete copy write progress')
        hasher.update(block[:written])
        offset += written
    _need(offset == len(raw) and hasher.hexdigest() == hashlib.sha256(raw).hexdigest(),
          'G12-N14: complete copied byte digest')
    os.fsync(descriptor)
    os.fchmod(descriptor, 0o444)
    os.fsync(descriptor)


def _copy_file(directory, name, raw):
    fds, rows = directory
    descriptor = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC,
                         0o600, dir_fd=fds[-1])
    primary, secondaries = None, _RawG12Errors()
    try:
        _write_fd(descriptor, raw)
        _check_chain(rows)
    except BaseException as error:
        primary = error, error.__traceback__
    try:
        os.close(descriptor)
    except BaseException as error:
        secondaries.append((error, error.__traceback__))
    _raise_preserved(primary, secondaries)
    os.fsync(fds[-1])


def _actual_costs(entry_ns, own_start, children_start):
    through = time.monotonic_ns()
    own, children = resource.getrusage(resource.RUSAGE_SELF), resource.getrusage(resource.RUSAGE_CHILDREN)
    return {'entry_ns': entry_ns, 'through_ns': through, 'wall_ns': through - entry_ns,
            'self_user_seconds': own.ru_utime - own_start.ru_utime,
            'self_system_seconds': own.ru_stime - own_start.ru_stime,
            'children_user_seconds': children.ru_utime - children_start.ru_utime,
            'children_system_seconds': children.ru_stime - children_start.ru_stime,
            'lifetime_max_rss_kib': own.ru_maxrss}


def run_g12_reference():
    """P01: one source-private invocation; accepts no caller completion data."""
    configured = G12_REFERENCE_LAUNCH_SELECTION
    _need(type(configured) is dict, 'G12-N01: exact immutable launch source literal remains None')
    _need(type(_INITIAL_PARENT_SOURCE_PIN) is dict and configured['source_pins']['parent'] is None,
          'G12-N02: independent initial external parent source pin; no self-hash literal')
    _source_pin(_INITIAL_PARENT_SOURCE_PIN)
    configured_bytes = _canonical(configured)
    selection = dict(configured)
    selection['source_pins'] = dict(configured['source_pins'])
    selection['source_pins']['parent'] = dict(_INITIAL_PARENT_SOURCE_PIN)
    # Actual launch remains closed. The independently reviewed source scope
    # correction requires the complete symbolic bill, not a new financial API.
    entry_ns = time.monotonic_ns()
    own_start, children_start = resource.getrusage(resource.RUSAGE_SELF), resource.getrusage(resource.RUSAGE_CHILDREN)
    selection_bytes = _canonical(selection)
    selection_sha = hashlib.sha256(selection_bytes).hexdigest()
    parent_graph = _capture_graph(globals())
    phase, stage_data, stage_record, jobs_record, phase_record = None, None, None, None, None
    source_records, originals, evidence, retained_records = {}, {}, {}, {}
    parent_identity = _proc(os.getpid())
    process, chain, lease, lease_identity = None, None, None, None
    lease_closed, attempted, wait_completed = False, False, False
    outer = {}
    observation, retained, science_directory, run_directory = None, None, None, None
    primary, secondaries, parent_stop = None, _RawG12Errors(), None
    cleanup, common, diagnostic, common_payload = None, None, None, None
    start, receipt, usage, launch = None, None, None, None
    manifest, manifest_record, publication_record = None, None, None
    reserved = {}
    candidate_pin = None

    def current():
        _need(G12_REFERENCE_LAUNCH_SELECTION is configured and _canonical(configured) == configured_bytes and
              _canonical(selection) == selection_bytes and _exact(selection['source_pins']['parent'], _INITIAL_PARENT_SOURCE_PIN),
              'G12-N16: selected launch source changed')
        _current_graph(parent_graph)
        _need(_proc(os.getpid())['start_ticks'] == parent_identity['start_ticks'], 'G12-N08: parent generation')
        _need(os.listdir('/proc/self/task') == [str(os.getpid())], 'G12-N08: parent thread domain changed')
        if lease is not None and not lease_closed:
            _need(_identity(os.fstat(lease)) == lease_identity and os.fstat(lease).st_nlink == 1,
                  'G12-N08: actual parent lease identity changed')
        for domain in (observation, retained, science_directory, run_directory):
            if domain is not None:
                _check_chain(domain[1])

    def _g12_preflight_and_claim():
        """P02: exact source/phase/namespace gate; separate parent-queue lease."""
        nonlocal phase, stage_data, stage_record, jobs_record, phase_record, chain
        nonlocal lease, lease_identity, observation
        _fields(selection, ('schema', 'stage', 'job', 'label', 'stage_sha256', 'jobs_sha256', 'source_pins',
                            'phase_pin', 'body_deadline_ns', 'retention_tail_allowance_ns',
                            'parent_observation_directory', 'parent_retained_directory'))
        _need(selection['schema'] == 'g12-one-reference-launch-selection-v1' and
              selection['stage'] == 'g12-reference-custody-v1' and selection['job'] == 'g12-reference',
              'G12-N02: fixed G12 launch role')
        label = selection['label']
        _need(type(label) is str and bool(label) and
              all(c in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_' for c in label),
              'G12-N03: fixed selected guard label')
        _need(selection['parent_observation_directory'] == _R + '/runtime/g12-reference-parent-observation-v1/' + label and
              selection['parent_retained_directory'] == _R + '/runtime/g12-reference-parent-custody-v1/' + label,
              'G12-N02: fixed parent namespace')
        _uint(selection['body_deadline_ns'], True)
        _uint(selection['retention_tail_allowance_ns'], True)
        _need(selection['body_deadline_ns'] > entry_ns, 'G12-N05: no remaining complete body allowance')
        _trusted_parent_launch()
        sources = selection['source_pins']
        _fields(sources, _MANIFEST_SCHEMA['selected_sources_exact_fields'])
        _need(_exact(sources['engine'], _ENGINE_PINS), 'G12-N02: exact seven original engine pins')
        for name, pin in sources.items():
            if name == 'engine':
                continue
            _source_pin(pin)
            observed, raw = _read_file(pin['path'], max(pin['bytes'], 1), int(pin['mode'], 8))
            _need(observed['sha256'] == pin['sha256'] and observed['bytes'] == pin['bytes'],
                  'G12-N02: selected source bytes/modes')
            source_records[name] = observed, raw
        _need(sources['parent']['path'] == __file__, 'G12-N04: external parent source selection')
        for name, expected in (('guard', _GUARD_PIN), ('root', _ROOT_PIN), ('provider', _PROVIDER_PIN),
                              ('producer', _PRODUCER_PIN), ('authority', _AUTHORITY_PIN)):
            _need(sources[name]['sha256'] == expected and sources[name]['mode'] == '0444', 'G12-N02: original source pin')
        for name, expected in _OTHER_SOURCE_PINS.items():
            _need(sources[name]['sha256'] == expected, 'G12-N02: original dependency pin')
        _source_pin(selection['phase_pin'])
        phase_record, phase_raw = _read_file(selection['phase_pin']['path'], _META_CAP,
                                             int(selection['phase_pin']['mode'], 8))
        _need(selection['phase_pin']['path'] == _R + '/control/EXECUTION-PHASE.json' and
              phase_record['sha256'] == selection['phase_pin']['sha256'] and
              phase_record['bytes'] == selection['phase_pin']['bytes'], 'G12-N05: original phase identity')
        phase = _json(phase_raw, _META_CAP)
        _need(type(phase['aggregate_cap_seconds']) is int and phase['aggregate_cap_seconds'] in (600, 2400),
              'G12-N05: original unchanged aggregate cap')
        stage = _R + '/stages/g12-reference-custody-v1'
        stage_record, stage_raw = _read_file(stage + '/STAGE.json', _META_CAP, 0o444)
        jobs_record, jobs_raw = _read_file(stage + '/JOBS.json', _META_CAP, 0o444)
        _need(stage_record['sha256'] == selection['stage_sha256'] and
              jobs_record['sha256'] == selection['jobs_sha256'], 'G12-N02: independently selected stage/jobs')
        stage_data = _json(stage_raw, _META_CAP)
        jobs = _json(jobs_raw, _META_CAP)
        _need(_exact(jobs, {'g12-reference': {'bootstrap': {'driver': 'integration/g12_reference_adapter_v1.py',
                     'provider': 'integration/probe_binding_v3.py'}, 'lanes': 'g12-reference', 'optimized': False}}),
              'G12-N03: exact only-job bootstrap/lanes/no-finite/no-optimization')
        _need(stage_data['runner_sha256'] == _GUARD_PIN, 'G12-N02: original runner source')
        for relative, row in stage_data['files'].items():
            _need(type(relative) is str and all(x not in ('', '.', '..') for x in relative.split('/')) and
                  not relative.startswith('/'), 'G12-N02: stage closure relative path')
            _fields(row, ('sha256', 'mode'))
            _need(type(row['mode']) is int, 'G12-N02: original source mode')
            observed, _ = _read_file(stage + '/' + relative, 16777216, row['mode'])
            _need(observed['sha256'] == row['sha256'], 'G12-N02: complete staged source closure')
        # Exact census rejects undeclared files/directories/symlinks, including an
        # alternate staged authority. Walk source paths only; no runtime payloads.
        actual = set()
        for path, dirs, files in os.walk(stage, followlinks=False):
            for name in dirs:
                _need(stat.S_ISDIR(os.lstat(path + '/' + name).st_mode), 'G12-N02: stage directory symlink')
            for name in files:
                full = path + '/' + name
                _need(stat.S_ISREG(os.lstat(full).st_mode), 'G12-N02: stage nonregular source')
                relative = full[len(stage) + 1:]
                if relative != 'STAGE.json':
                    actual.add(relative)
        _need(actual == set(stage_data['files']), 'G12-N02: exact staged closure census')
        for name, pin in sources.items():
            if name not in ('engine', 'parent', 'guard', 'cleanup_leaf_origin'):
                _need(pin['path'].startswith(stage + '/'), 'G12-N02: selected source outside new stage')
                relative = pin['path'][len(stage) + 1:]
                _need(stage_data['files'][relative] == {'sha256': pin['sha256'], 'mode': int(pin['mode'], 8)},
                      'G12-N02: selected source/stage binding')
        chain = _KnownG12Chain()
        for path in (_R + '/runtime/runs/' + label, selection['parent_observation_directory'],
                     selection['parent_retained_directory']):
            parent, name = path.rsplit('/', 1)
            fds, rows = _directory_chain(parent)
            try:
                try:
                    os.stat(name, dir_fd=fds[-1], follow_symlinks=False)
                except FileNotFoundError:
                    pass
                else:
                    raise RuntimeError('G12-N05: prior output/evidence/custody path exists')
                _check_chain(rows)
            finally:
                _finally_close_known(fds, secondaries)
        # Separate from the original guard's science.lock. No contention wait.
        lock_path = _R + '/runtime/parent-queue.lock'
        parent_fds, parent_rows = _directory_chain(_R + '/runtime')
        try:
            lease = os.open('parent-queue.lock', os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW | os.O_CLOEXEC,
                            0o600, dir_fd=parent_fds[-1])
            info = os.fstat(lease)
            _need(stat.S_ISREG(info.st_mode) and info.st_nlink == 1, 'G12-N08: parent lease type/link')
            lease_identity = _identity(info)
            fcntl.flock(lease, fcntl.LOCK_EX | fcntl.LOCK_NB)
            _check_chain(parent_rows)
            _need(_identity(os.stat('parent-queue.lock', dir_fd=parent_fds[-1], follow_symlinks=False)) == lease_identity,
                  'G12-N08: parent lease name identity')
        finally:
            _finally_close_known(parent_fds, secondaries)
        observation = _exclusive_directory(selection['parent_observation_directory'])
        current()

    def _g12_launch_once():
        """P03: retain the actual Popen, actual descriptors and generation."""
        nonlocal process, attempted, launch
        _need(not attempted and process is None, 'G12-N06: no second launch attempt')
        current()
        parent_argv, root_argv, producer_argv = _fixed_argv(selection['label'], selection['source_pins'])
        for name in ('stdout', 'stderr'):
            outer[name] = os.open('outer-' + name + '.txt',
                os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC,
                0o600, dir_fd=observation[0][-1])
        attempted = True
        process = subprocess.Popen(parent_argv, cwd=_R, env=dict(_ENV), stdout=outer['stdout'],
                                   stderr=outer['stderr'], close_fds=True, start_new_session=True)
        _need(type(process) is subprocess.Popen and type(process.pid) is int and process.pid > 0,
              'G12-N06: actual Popen object/PID')
        row = _proc(process.pid)
        _need(row is not None and row['ppid'] == os.getpid() and
              row['pgid'] == process.pid and row['sid'] == process.pid, 'G12-N06: actual new guard generation/session')
        chain.add(row)
        launch = {'parent_pid': parent_identity['pid'], 'parent_start_ticks': parent_identity['start_ticks'],
                  'guard_pid': row['pid'], 'guard_start_ticks': row['start_ticks'],
                  'guard_pgid': row['pgid'], 'guard_sid': row['sid'], 'parent_guard_argv': parent_argv,
                  'guard_root_argv': root_argv, 'adapter_producer_argv': producer_argv,
                  'cwd': _R, 'environment': dict(_ENV), 'flags': list(_FLAGS), 'launch_record': None}
        raw = _canonical({'schema': 'g12-parent-actual-launch-v1', 'selection_sha256': selection_sha, 'source_selection': selection,
                          'launch': {k: v for k, v in launch.items() if k != 'launch_record'}}) + b'\n'
        _copy_file(observation, 'LAUNCH.json', raw)
        evidence['parent_launch'] = _read_file(selection['parent_observation_directory'] + '/LAUNCH.json', _META_CAP, 0o444)

    def _g12_observe_wait_and_close():
        """P04: actual wait and scoped known-chain closure; no status substitute."""
        nonlocal wait_completed, cleanup, parent_stop
        _need(process is not None and type(process) is subprocess.Popen, 'G12-N06: missing retained actual Popen')
        while process.poll() is None:
            _, children, occupied = chain.observe()
            if time.monotonic_ns() >= selection['body_deadline_ns']:
                parent_stop = 'selected_complete_body_deadline'
            elif sum(row['rss_bytes'] for row in children) > 1073741824:
                parent_stop = 'selected_known_chain_rss_cap'
            elif resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024 > 1073741824:
                parent_stop = 'parent_lifetime_rss_cap'
            elif any(os.fstat(descriptor).st_size > _LOG_CAP for descriptor in outer.values()):
                parent_stop = 'parent_outer_log_cap'
            if parent_stop:
                raise RuntimeError('G12-N06: parent STOP: ' + parent_stop)
            current()
            time.sleep(0.05)
        code = process.wait()
        wait_completed = True
        _need(type(code) is int and code == 0 and type(process.returncode) is int and process.returncode == 0,
              'G12-N06: actual guard wait returncode')
        cleanup = chain.finish(process, selection['body_deadline_ns'] + selection['retention_tail_allowance_ns'], False)
        for name, descriptor in tuple(outer.items()):
            os.fsync(descriptor)
            os.close(descriptor)
            del outer[name]
        cleanup['known_streams_closed'] = not outer
        cleanup['lease_identity'] = lease_identity
        _need(parent_stop is None and cleanup['known_pidfds_closed'] and not cleanup['io_unknown'],
              'G12-N08: complete known closes')
        current()

    def _g12_join_original_guard_evidence():
        """P05: retain complete canonical originals; never reconstruct receipt."""
        nonlocal start, receipt, usage, science_directory, run_directory
        run = _R + '/runtime/runs/' + selection['label']
        run_directory = _directory_chain(run)
        science_directory = _directory_chain(run + '/science')
        cleanup['science_directory_identity'] = _identity(os.fstat(science_directory[0][-1]))
        fixed = {'guard_START': ('START.json', _META_CAP), 'guard_receipt': ('receipt.json', _META_CAP),
                 'guard_stdout': ('stdout.txt', _LOG_CAP), 'guard_stderr': ('stderr.txt', _LOG_CAP),
                 'guard_usage': ('usage.json', 16384)}
        for name, (filename, cap) in fixed.items():
            evidence[name] = _read_file(run + '/' + filename, cap)
        for name in ('stdout', 'stderr'):
            evidence['parent_outer_' + name] = _read_file(selection['parent_observation_directory'] + '/outer-' + name + '.txt', _LOG_CAP)
        start = _json(evidence['guard_START'][1], _META_CAP)
        receipt = _json(evidence['guard_receipt'][1], _META_CAP)
        usage = _json(evidence['guard_usage'][1], 16384)
        invocation = {'job': selection['job'], 'label': selection['label'], 'stage_sha256': selection['stage_sha256']}
        _validate_guard(start, receipt, usage, evidence['guard_stdout'][1], evidence['guard_stderr'][1],
                        launch['guard_root_argv'], invocation, selection['source_pins'], selection['phase_pin']['sha256'])
        fraction, _ = _read_file('/usr/lib/python3.12/fractions.py', 1048576)
        _need(start['fractions_sha256'] == fraction['sha256'], 'G12-N07: original fractions source join')
        _need(_exact(_json(evidence['parent_outer_stdout'][1], _LOG_CAP), receipt) and
              evidence['parent_outer_stderr'][1] == b'', 'G12-N07: actual outer stdout/empty stderr')
        current()

    def _g12_collect_complete_pair():
        """P06: complete original common AND diagnostics, followed by joint recheck."""
        nonlocal common, diagnostic, common_payload
        _need(wait_completed and process.returncode == 0 and cleanup is not None and receipt is not None,
              'G12-N10: original successful owner/receipt join must precede pair')
        science = _R + '/runtime/runs/' + selection['label'] + '/science'
        for name in ('common', 'diagnostics'):
            originals[name] = _read_file(science + '/g12-reference.' + name + '.json', _PAIR_CAP)
        common, diagnostic, common_payload = _validate_pair(originals['common'][1], originals['diagnostics'][1])
        for name in ('common', 'diagnostics'):
            _need(_read_file(originals[name][0]['path'], _PAIR_CAP) == originals[name], 'G12-N11: original joint pair changed')
        current()

    def _g12_retain_parent_pair_and_evidence():
        """P07: fresh parent directory only after all selected writers are known closed."""
        nonlocal retained
        _need(not _children() and cleanup['known_pidfds_closed'] and cleanup['known_streams_closed'],
              'G12-N08: no retained directory until known selected cleanup')
        current()
        retained = _exclusive_directory(selection['parent_retained_directory'])
        for name in ('common', 'diagnostics'):
            filename = 'g12-reference.' + name + '.json'
            _copy_file(retained, filename, originals[name][1])
            record, raw = _read_file(selection['parent_retained_directory'] + '/' + filename, _PAIR_CAP, 0o444)
            _need(raw == originals[name][1] and record['sha256'] == originals[name][0]['sha256'], 'G12-N14: complete retained pair readback')
            retained_records[name] = record
        observation_raw = _canonical({'schema': 'g12-known-chain-observations-v1', 'cleanup': cleanup,
                                       'observations': chain.observations}) + b'\n'
        _copy_file(observation, 'owned-observations.json', observation_raw)
        evidence['parent_owned_observations'] = _read_file(selection['parent_observation_directory'] + '/owned-observations.json', _META_CAP, 0o444)
        costs = _actual_costs(entry_ns, own_start, children_start)
        accounting_raw = _canonical(costs) + b'\n'
        _copy_file(observation, 'preseal-accounting.json', accounting_raw)
        evidence['parent_preseal_accounting'] = _read_file(selection['parent_observation_directory'] + '/preseal-accounting.json', _META_CAP, 0o444)
        for name in _MANIFEST_SCHEMA['retained_evidence_exact_keys']:
            _copy_file(retained, _EVIDENCE_NAMES[name], evidence[name][1])
            record, raw = _read_file(selection['parent_retained_directory'] + '/' + _EVIDENCE_NAMES[name],
                                      max(len(evidence[name][1]), 1), 0o444)
            _need(raw == evidence[name][1], 'G12-N14: raw evidence copy differs')
            retained_records[name] = record
        # Reserve BOTH metadata names before recording final directory identity.
        # Existing FD writes/file chmod do not change parent directory entries.
        for name in ('manifest.json', 'publication.json'):
            reserved[name] = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC,
                                     0o600, dir_fd=retained[0][-1])
        os.fsync(retained[0][-1])
        current()

    def _g12_seal_once():
        """P08: private actual owner seal; returns only a candidate for later adoption."""
        nonlocal manifest, manifest_record, publication_record, candidate_pin, lease_closed
        _need(process is not None and type(process) is subprocess.Popen and process.returncode == 0 and
              wait_completed and primary is None and not secondaries and parent_stop is None and not _children() and
              not outer and not chain.fds and not chain.unknown, 'G12-N08: actual owner final conjunction')
        current()
        for name, original in originals.items():
            _need(_read_file(original[0]['path'], _PAIR_CAP) == original, 'G12-N11: original pair final drift')
            _need(_read_file(retained_records[name]['path'], _PAIR_CAP, 0o444)[0] == retained_records[name],
                  'G12-N14: retained pair final drift')
        for name, (record, raw) in source_records.items():
            _need(_read_file(record['path'], max(record['bytes'], 1), record['identity']['full_st_mode'] & 0o7777) == (record, raw),
                  'G12-N02: complete selected source drift')
        for record, raw in evidence.values():
            _need(_read_file(record['path'], max(record['bytes'], 1), record['identity']['full_st_mode'] & 0o7777) == (record, raw),
                  'G12-N07: final complete original raw evidence drift')
        for record in (stage_record, jobs_record, phase_record):
            _need(_read_file(record['path'], _META_CAP, record['identity']['full_st_mode'] & 0o7777)[0] == record,
                  'G12-N02: stage/jobs/phase final identity drift')
        os.fchmod(retained[0][-1], 0o500)
        # Update exactly our owned mode transition, retaining dev/inode binding.
        parent, name, descriptor, old = retained[1][-1]
        final_dir_info = os.fstat(descriptor)
        _need((final_dir_info.st_dev, final_dir_info.st_ino) == old[:2], 'G12-N14: retained directory owner transition')
        retained[1][-1] = (parent, name, descriptor, _directory_key(final_dir_info))
        os.fsync(descriptor)
        directory_identity = _identity(final_dir_info)
        costs = _actual_costs(entry_ns, own_start, children_start)
        account = {'clock': 'monotonic_ns', 'parent_entry_ns': entry_ns,
            'preseal_end_ns': costs['through_ns'], 'parent_preseal_wall_ns': costs['wall_ns'],
            'parent_self_user_seconds': costs['self_user_seconds'], 'parent_self_system_seconds': costs['self_system_seconds'],
            'parent_children_user_seconds': costs['children_user_seconds'], 'parent_children_system_seconds': costs['children_system_seconds'],
            'parent_lifetime_max_rss_kib': costs['lifetime_max_rss_kib'], 'guard_usage': usage,
            'guard_runner_wall_seconds': receipt['runner_wall_seconds'], 'categories': list(_COST_CATEGORIES),
            'complete_tail_accounting_required': True, 'unmeasured_final_tail': None}
        launch['launch_record'] = retained_records['parent_launch']
        cleanup['observations_record'] = retained_records['parent_owned_observations']
        manifest = {'schema': 'g12-parent-two-export-custody-v2',
            'invocation': {'stage': selection['stage'], 'job': selection['job'], 'label': selection['label'],
                          'stage_sha256': selection['stage_sha256'], 'jobs_sha256': selection['jobs_sha256'],
                          'launch_selection_sha256': selection_sha},
            'selected_sources': selection['source_pins'], 'workload': _MANIFEST_SCHEMA['workload_values'],
            'launch': launch, 'terminal': {'actual_popen_returncode': process.returncode, 'wait_completed': wait_completed,
                'parent_stop': parent_stop, 'primary_error': None, 'secondary_errors': [], 'guard_receipt_missing': False},
            'guard': {'start': retained_records['guard_START'], 'receipt': retained_records['guard_receipt'],
                'start_fields': start, 'receipt_fields': receipt, 'stdout': retained_records['guard_stdout'],
                'stderr': retained_records['guard_stderr'], 'usage': retained_records['guard_usage']},
            'cleanup': cleanup,
            'pair': {name: {'original': originals[name][0], 'retained': retained_records[name]} for name in ('common', 'diagnostics')},
            'retained_evidence': {name: retained_records[name] for name in _MANIFEST_SCHEMA['retained_evidence_exact_keys']},
            'custody': {'retained_directory': selection['parent_retained_directory'], 'retained_directory_identity': directory_identity,
                'retained_file_mode': '0444', 'created_after_known_cleanup': True, 'source_selection_required': True,
                'known_close_policy': 'Any unknown close rejects publication'}, 'accounting': account, 'scope': _SCOPE}
        manifest['pair']['common_payload_sha256'] = common['common_payload_sha256']
        _validate_manifest(manifest, selection['source_pins']['parent']['path'], selection['source_pins']['parent']['sha256'])
        raw = _canonical(manifest) + b'\n'
        _need(len(raw) <= _META_CAP, 'G12-N14: manifest finite metadata cap')
        _write_fd(reserved['manifest.json'], raw)
        os.close(reserved['manifest.json'])
        del reserved['manifest.json']
        os.fsync(retained[0][-1])
        manifest_record, reread = _read_file(selection['parent_retained_directory'] + '/manifest.json', _META_CAP, 0o444)
        _need(reread == raw, 'G12-N14: complete manifest readback')
        current()
        _need(not _children(), 'G12-N08: unexpected child at final lease close')
        fcntl.flock(lease, fcntl.LOCK_UN)
        os.close(lease)
        lease_closed = True
        costs = _actual_costs(entry_ns, own_start, children_start)
        publication = {'schema': 'g12-parent-custody-publication-v2',
            'parent_source_sha256': selection['source_pins']['parent']['sha256'], 'launch_selection_sha256': selection_sha,
            'manifest_path': manifest_record['path'], 'manifest_sha256': manifest_record['sha256'],
            'manifest_bytes': manifest_record['bytes'], 'manifest_identity': manifest_record['identity'],
            'retained_pair_sha256': {name: retained_records[name]['sha256'] for name in ('common', 'diagnostics')},
            'final_pair_recheck_complete': True, 'known_lease_close_completed': lease_closed,
            'primary_error': None, 'secondary_errors': [], 'measured_through_ns': costs['through_ns'],
            'actual_costs_through_ns': costs, 'unmeasured_final_tail': None,
            'complete_cost_qualification': False}
        _validate_publication(publication, manifest, manifest_record)
        publication_raw = _canonical(publication) + b'\n'
        _need(len(publication_raw) <= _META_CAP, 'G12-N15: publication metadata cap')
        _write_fd(reserved['publication.json'], publication_raw)
        os.close(reserved['publication.json'])
        del reserved['publication.json']
        os.fsync(retained[0][-1])
        publication_record, observed = _read_file(selection['parent_retained_directory'] + '/publication.json', _META_CAP, 0o444)
        _need(observed == publication_raw and _identity(os.fstat(retained[0][-1])) == directory_identity,
              'G12-N15: final publication readback/directory identity')
        current()
        # This candidate is not a source selection or completed enclosing invoice.
        candidate_pin = (manifest_record['path'], manifest_record['sha256'], manifest_record['bytes'],
            _handoff_identity_tuple(manifest_record), selection['source_pins']['parent']['path'],
            selection['source_pins']['parent']['sha256'], publication_record['path'],
            publication_record['sha256'], publication_record['bytes'])

    def _g12_finish_failure():
        """P09: always preserve actual first failure, known cleanup and partial originals."""
        nonlocal lease_closed
        # Every later error is retained separately; no receipt or PASS replacement.
        if chain is not None and not chain.closed:
            try:
                chain.finish(process, selection['body_deadline_ns'] + selection['retention_tail_allowance_ns'], True)
            except BaseException as error:
                secondaries.append((error, error.__traceback__))
        for name, descriptor in tuple(outer.items()):
            try:
                os.close(descriptor)
                del outer[name]
            except BaseException as error:
                secondaries.append((error, error.__traceback__))
        for name, descriptor in tuple(reserved.items()):
            try:
                os.close(descriptor)
                del reserved[name]
            except BaseException as error:
                secondaries.append((error, error.__traceback__))
        if lease is not None and not lease_closed:
            try:
                os.close(lease)
                lease_closed = True
            except BaseException as error:
                secondaries.append((error, error.__traceback__))
        # Failure-tail raw records are never advertised as canonical guard data.
        if observation is not None and (primary is not None or secondaries):
            try:
                failures = {'schema': 'g12-parent-failed-attempt-v1', 'attempted': attempted,
                    'actual_returncode': None if process is None else process.returncode,
                    'primary': None if primary is None else repr(primary[0]),
                    'ordered_secondaries': [repr(item[0]) for item in secondaries],
                    'known_cleanup': 'UNKNOWN' if chain is None or not chain.closed else 'KNOWN_SELECTED_CHAIN_ONLY',
                    'actual_costs_through_prewrite': _actual_costs(entry_ns, own_start, children_start),
                    'enclosing_full_failure_tail_required': True}
                _copy_file(observation, 'FAILED-ATTEMPT.json', _canonical(failures) + b'\n')
            except BaseException as error:
                secondaries.append((error, error.__traceback__))
        for domain in (science_directory, run_directory, retained, observation):
            if domain is not None:
                for descriptor in reversed(domain[0]):
                    try:
                        os.close(descriptor)
                    except BaseException as error:
                        secondaries.append((error, error.__traceback__))

    try:
        _g12_preflight_and_claim()
        _g12_launch_once()
        _g12_observe_wait_and_close()
        _g12_join_original_guard_evidence()
        _g12_collect_complete_pair()
        _g12_retain_parent_pair_and_evidence()
        _g12_seal_once()
    except BaseException as error:
        primary = error, error.__traceback__
    try:
        _g12_finish_failure()
    except BaseException as error:
        # Preserve primary even if a secondary bookkeeping append itself failed.
        if primary is None:
            primary = error, error.__traceback__
        else:
            try:
                primary[0].add_note('P09 bookkeeping failure: ' + repr(error))
            except BaseException:
                pass
    _raise_preserved(primary, secondaries)
    _need(candidate_pin is not None and lease_closed and not outer and not reserved,
          'G12-N15: final tail incomplete; manifest remains unselected')
    return candidate_pin
