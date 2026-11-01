"""Fixed G12 two-export consumer, v2 checked identity conversion.

SOURCE ONLY; all selections stay closed.

The selected cold registered-source executor must inject the actual initial
Root/capability/API before candidate exposure, authenticate these exact source
bytes and this entry, and pass those same objects. Python shapes do not prove
that premise. No result registry, setter, caller success flag or new oracle.
"""
import os
import sys
import stat
import json
import hashlib
import math
from types import FunctionType, CodeType, ModuleType

G12_REFERENCE_HANDOFF = None
# Future immutable nine-tuple exactly as accepted DESIGN-v1; never a setter.
# Independent selected consumer identity is injected by the fixed original
# cold loader BEFORE exec. It is not stored inside its own source (no hash cycle).
_BOOTSTRAP = (globals().get('bootstrap_root'), globals().get('bootstrap_capability'),
              globals().get('bootstrap_api'), globals().get('bootstrap_g12_source_identity'))
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
# BEGIN FIXED G12 FILE AND PAIR LEAF

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


def _identity_dict_from_handoff(value):
    """Convert the parent's ordered identity tuple into a FileRecord dictionary.

    Field 4 of the accepted nine-tuple is (dev, ino, full_st_mode, size,
    mtime_ns, ctime_ns). `_file_record` then requires those values under
    string keys. A dictionary is rejected so this boundary stays the only
    conversion and cannot be skipped.
    """
    _need(type(value) is tuple and len(value) == len(_ID_NAMES),
          'G12-N11: handoff identity must be the ordered six-tuple')
    for item in value:
        _need(type(item) is int, 'G12-N11: exact stat value')
    identity = {name: item for name, item in zip(_ID_NAMES, value)}
    _fields(identity, _ID_NAMES)
    _uint(identity['dev'])
    _uint(identity['ino'], True)
    _need(stat.S_ISREG(identity['full_st_mode']), 'G12-N11: file identity type')
    return identity


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


def _root_read(root, api, record, cap):
    _file_record(record)
    _need(api[0]() == _ROOT_PIN, 'G12-N04: actual Root currentness')
    before = root._hash_regular(record['path'], cap, False)
    observed, raw = _read_file(record['path'], cap, 0o444)
    after = root._hash_regular(record['path'], cap, False)
    _need(_exact(observed, record) and before[:2] == after[:2] ==
          (record['sha256'], record['bytes']), 'G12-N17: Root/read/full-identity join')
    _need(api[0]() == _ROOT_PIN, 'G12-N04: actual Root changed after file read')
    return raw


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
# END FIXED G12 FILE AND PAIR LEAF

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


def _authenticate_own_functions(root, api, source, path):
    _need(api[0]() == _ROOT_PIN, 'G12-N04: Root before selected-source compilation')
    code = root._COMPILE(source, path, 'exec', dont_inherit=True, optimize=0)
    declared = {item.co_name: item for item in code.co_consts if type(item) is CodeType}
    for name, function in tuple(globals().items()):
        if type(function) is FunctionType and function.__globals__ is globals():
            _need(name in declared and function.__builtins__ is root.builtins.__dict__ and
                  _source_code_shape(function.__code__) == _source_code_shape(declared[name]),
                  'G12-N04: actual entire own callable differs from selected source: ' + name)
    _need(api[0]() == _ROOT_PIN, 'G12-N04: Root after selected-source compilation')


def load_original_g12_reference(root, capability, api):
    """Return only original literal/count/opaque common/provenance, after joint custody."""
    config = G12_REFERENCE_HANDOFF
    selected = _BOOTSTRAP[3]
    _need(type(config) is tuple and len(config) == 9 and type(selected) is tuple and len(selected) == 3,
          'G12-N01: actual parent handoff and cold source remain unselected')
    _need(root is _BOOTSTRAP[0] and capability is _BOOTSTRAP[1] and api is _BOOTSTRAP[2] and
          type(root) is ModuleType and type(api) is tuple and len(api) == 4 and
          all(type(f) is FunctionType and f.__globals__ is root.__dict__ for f in api),
          'G12-N04: initial actual cold Root/capability/API identities differ')
    _need(api[0]() == _ROOT_PIN and sys.flags.optimize == 0, 'G12-N04: authentic Root/assertions')
    api[1](capability, _PROVIDER_PIN)
    _current_graph(_INITIAL_GRAPH)
    source_path, source_sha, source_size = selected
    source_record, source_raw = _read_file(source_path, 1048576, 0o444)
    _need(source_path == __file__ and source_record['sha256'] == source_sha and
          source_record['bytes'] == source_size, 'G12-N04: exact independently selected consumer source')
    _authenticate_own_functions(root, api, source_raw, source_path)
    path, sha, size, identity_tuple, parent_path, parent_sha, publication_path, publication_sha, publication_size = config
    _need(_digest(sha) and _digest(parent_sha) and _digest(publication_sha), 'G12-N16: source selection digest domain')
    identity = _identity_dict_from_handoff(identity_tuple)
    manifest_record = {'path': path, 'sha256': sha, 'bytes': size, 'identity': identity, 'nlink': 1}
    manifest_raw = _root_read(root, api, manifest_record, _META_CAP)
    manifest = _json(manifest_raw, _META_CAP, True, True)
    _validate_manifest(manifest, parent_path, parent_sha)
    retained = manifest['custody']['retained_directory']
    _need(path == retained + '/manifest.json' and publication_path == retained + '/publication.json',
          'G12-N16: exact fixed publication/manifest paths')
    dirs, rows = _directory_chain(retained)
    primary, secondaries, result = None, _RawG12Errors(), None
    try:
        _need(_exact(_identity(os.fstat(dirs[-1])), manifest['custody']['retained_directory_identity']),
              'G12-N17: final retained directory identity')
        publication_record, _ = _read_file(publication_path, _META_CAP, 0o444)
        _need(publication_record['sha256'] == publication_sha and publication_record['bytes'] == publication_size,
              'G12-N15: source-selected final publication bytes')
        publication_raw = _root_read(root, api, publication_record, _META_CAP)
        publication = _json(publication_raw, _META_CAP, True, True)
        _validate_publication(publication, manifest, manifest_record)
        evidence = {}
        for name, record in manifest['retained_evidence'].items():
            cap = _LOG_CAP if name in ('guard_stdout', 'guard_stderr', 'parent_outer_stdout', 'parent_outer_stderr') else _META_CAP
            evidence[name] = _root_read(root, api, record, cap)
        launch_data = _json(evidence['parent_launch'], _META_CAP, True, True)
        _fields(launch_data, ('schema', 'selection_sha256', 'source_selection', 'launch'))
        _need(launch_data['schema'] == 'g12-parent-actual-launch-v1' and
              launch_data['selection_sha256'] == manifest['invocation']['launch_selection_sha256'] ==
              hashlib.sha256(_canonical(launch_data['source_selection'])).hexdigest() and
              _exact(launch_data['source_selection']['source_pins'], manifest['selected_sources']) and
              _exact(launch_data['launch'], {k: v for k, v in manifest['launch'].items() if k != 'launch_record'}),
              'G12-N07: actual source-selected launch/raw evidence binding')
        start = _json(evidence['guard_START'], _META_CAP)
        receipt = _json(evidence['guard_receipt'], _META_CAP)
        usage = _json(evidence['guard_usage'], 16384)
        _need(_exact(start, manifest['guard']['start_fields']) and
              _exact(receipt, manifest['guard']['receipt_fields']), 'G12-N07: original raw evidence joins')
        _validate_guard(start, receipt, usage, evidence['guard_stdout'], evidence['guard_stderr'],
                        manifest['launch']['guard_root_argv'], manifest['invocation'], manifest['selected_sources'],
                        launch_data['source_selection']['phase_pin']['sha256'])
        _need(_exact(_json(evidence['parent_outer_stdout'], _LOG_CAP), receipt) and
              evidence['parent_outer_stderr'] == b'', 'G12-N07: actual outer raw log join')
        common_record = manifest['pair']['common']['retained']
        diagnostic_record = manifest['pair']['diagnostics']['retained']
        common_raw = _root_read(root, api, common_record, _PAIR_CAP)
        diagnostic_raw = _root_read(root, api, diagnostic_record, _PAIR_CAP)
        common, diagnostics, payload = _validate_pair(common_raw, diagnostic_raw)
        _need(common['common_payload_sha256'] == manifest['pair']['common_payload_sha256'], 'G12-N13: pair/manifest payload')
        # Joint final reread includes diagnostics even after common decoding.
        for record, raw, cap in ((manifest_record, manifest_raw, _META_CAP),
                                 (common_record, common_raw, _PAIR_CAP),
                                 (diagnostic_record, diagnostic_raw, _PAIR_CAP),
                                 (publication_record, publication_raw, _META_CAP)):
            _need(_root_read(root, api, record, cap) == raw, 'G12-N17: final full custody set changed')
        for name, record in manifest['retained_evidence'].items():
            cap = _LOG_CAP if name in ('guard_stdout', 'guard_stderr', 'parent_outer_stdout', 'parent_outer_stderr') else _META_CAP
            _need(_root_read(root, api, record, cap) == evidence[name], 'G12-N17: raw retained evidence drift')
        _check_chain(rows)
        _need(_exact(_identity(os.fstat(dirs[-1])), manifest['custody']['retained_directory_identity']),
              'G12-N17: final namespace changed after decode')
        _need(_read_file(source_path, 1048576, 0o444) == (source_record, source_raw), 'G12-N04: consumer source drift')
        _current_graph(_INITIAL_GRAPH)
        api[1](capability, _PROVIDER_PIN)
        _need(api[0]() == _ROOT_PIN, 'G12-N17: final actual Root currentness')
        # Full diagnostic raw bytes stay retained; their hash is part of immutable
        # provenance, and no diagnostic counter becomes an equality oracle.
        provenance = (path, sha, size, tuple(identity[k] for k in _ID_NAMES), parent_path, parent_sha,
                      publication_path, publication_sha, publication_size, common_record['sha256'],
                      diagnostic_record['sha256'], common['common_payload_sha256'],
                      tuple(common['original_scientific_pins']), _PRODUCER_PIN, _AUTHORITY_PIN)
        result = common['literal_original_value'], common['remaining_original_case_count'], payload, provenance
    except BaseException as error:
        primary = error, error.__traceback__
    for descriptor in reversed(dirs):
        try:
            os.close(descriptor)
        except BaseException as error:
            secondaries.append((error, error.__traceback__))
    _raise_preserved(primary, secondaries)
    return result

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

_INITIAL_GRAPH = _capture_graph(globals())
