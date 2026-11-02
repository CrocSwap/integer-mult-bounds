"""Finite negative-only data records. No import/load/compile/runtime authority.

Source draft: no target execution has been authorized. These functions are not
run during source checks. Every caller must be a separately reviewed fixed
parent/child source; JSON never creates a parent capability.
"""
import hashlib
import json

SCHEMA = 'h25-negative-build-epoch-v3'
CLAIM_SCHEMA = 'h25-negative-import-claim-v3'
ROLES = ('production', 'watcher', 'bounds', 'pyinit_failure', 'exec_failure')
PRODUCERS = ('group01', 'failure_variants')
GROUPS = ('02', '03', '04', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16')
PROFILE_KEYS = ('source_manifest_sha256', 'project_headers_sha256', 'system_headers_sha256',
                'compiler_link_sha256', 'link_profile_sha256')
LAUNCH_KEYS = ('configuration_sha256', 'root_sha256', 'stage_sha256', 'command_sha256',
               'startup_tcb_sha256', 'expected_history_sha256')
FILE_BYTES = 64 * 1024 * 1024
RECORD_BYTES = 1024 * 1024
RAW_RESULT_BYTES = 4 * 1024 * 1024
LOG_BYTES = 2 * 1024 * 1024
JOURNAL_BYTES = 3 * 65536
CHUNK_BYTES = 65536
PATH_BYTES = 4096
MAX_PATH_COMPONENTS = 64
MAX_READ_CALLS = 8192
MAX_WRITE_CALLS = 8192
MAX_RECORD_WRITE_CALLS = 4096
MAX_PRIVATE_COPIES = 41
MAX_EXPORTS = 5
MAX_EPOCH_FILE_BYTES = 46 * FILE_BYTES
IDENTITY_KEYS = ('device', 'inode', 'mode', 'links', 'uid', 'gid', 'size', 'mtime_ns', 'ctime_ns')


# Captured before any adverse input. Actual startup primitive/source admission
# is still required by the future caller; no module is imported in source work.
_TYPE, _LEN = type, len
_DICT, _LIST, _TUPLE, _STR, _INT, _BOOL, _BYTES = dict, list, tuple, str, int, bool, bytes
MAX_RECORD_KEYS = 256
MAX_SEQUENCE = 256
MAX_WIRE_NODES = 8192
MAX_WIRE_DEPTH = 24
MAX_WIRE_TEXT = 8192
MAX_WIRE_TEXT_TOTAL = 512 * 1024


class EpochStop(RuntimeError):
    """Literal bounded source error; original foreign failures remain opaque."""


def need(condition: bool, message: str) -> None:
    # No truth testing or formatting of an unknown object.
    if _TYPE(message) is not _STR or _LEN(message) > 256:
        raise EpochStop('invalid internal error literal')
    if condition is not True:
        raise EpochStop(message)


def exact(value: dict, keys: tuple[str, ...]) -> None:
    need(_TYPE(value) is _DICT, 'exact record type differs')
    need(_LEN(value) <= MAX_RECORD_KEYS, 'record cardinality bound exceeded')
    need(_TYPE(keys) is _TUPLE, 'exact expected key tuple differs')
    need(_LEN(keys) <= MAX_RECORD_KEYS, 'expected key cardinality bound exceeded')
    # Iteration over an exact dict does not hash its keys. Complete this walk
    # before membership, set creation, or any value lookup in that dictionary.
    for key in value:
        need(_TYPE(key) is _STR, 'foreign record key rejected')
        need(_LEN(key) <= MAX_WIRE_TEXT, 'record key length bound exceeded')
    for key in keys:
        need(_TYPE(key) is _STR, 'foreign expected key rejected')
        need(_LEN(key) <= MAX_WIRE_TEXT, 'expected key length bound exceeded')
    need(_LEN(value) == _LEN(keys), 'exact record keys differ')
    seen = set()
    for key in keys:
        need(key not in seen, 'duplicate expected key')
        seen.add(key)
    for key in value:
        need(key in seen, 'exact record keys differ')


def integer(value: int, lower: int, upper: int) -> None:
    need(_TYPE(value) is _INT and _TYPE(lower) is _INT and _TYPE(upper) is _INT,
         'exact integer type differs')
    need(lower <= value <= upper, 'bounded exact integer differs')


def boolean(value: bool) -> None:
    need(_TYPE(value) is _BOOL, 'exact boolean type differs')


def text(value: str, limit: int = MAX_WIRE_TEXT) -> None:
    need(_TYPE(value) is _STR and _TYPE(limit) is _INT, 'exact text/limit type differs')
    need(0 <= limit <= MAX_WIRE_TEXT and _LEN(value) <= limit, 'text bound exceeded')


def choice(value: str, choices: tuple[str, ...]) -> None:
    text(value)
    need(_TYPE(choices) is _TUPLE and _LEN(choices) <= MAX_SEQUENCE, 'choice tuple differs')
    for item in choices:
        text(item)
    need(value in choices, 'literal choice differs')


def sequence(value: list, count: int) -> None:
    need(_TYPE(value) is _LIST and _TYPE(count) is _INT, 'exact sequence type differs')
    need(0 <= count <= MAX_SEQUENCE and _LEN(value) == count, 'exact sequence count differs')


def digest(value: str) -> None:
    text(value, 64)
    need(_LEN(value) == 64 and all(c in '0123456789abcdef' for c in value), 'sha256 differs')


def label(value: str) -> None:
    text(value, 96)
    need(1 <= _LEN(value) <= 96 and
         all(c in 'abcdefghijklmnopqrstuvwxyz0123456789-' for c in value), 'label differs')


def path(value: str) -> None:
    text(value, PATH_BYTES)
    need(1 < _LEN(value) <= PATH_BYTES and value.isascii() and value.startswith('/'),
         'canonical absolute path differs')
    parts = value.split('/')[1:]
    need(_LEN(parts) <= MAX_PATH_COMPONENTS and
         all(p not in ('', '.', '..') for p in parts) and
         all(32 <= ord(c) <= 126 for c in value), 'canonical absolute path differs')


def _plain(value, depth: int, budget: list):
    # depth and budget are newly created private native values, never inputs.
    budget[0] += 1
    need(budget[0] <= MAX_WIRE_NODES and depth <= MAX_WIRE_DEPTH, 'plain record node/depth bound')
    kind = _TYPE(value)
    if value is None or kind is _BOOL:
        return value
    if kind is _STR:
        need(_LEN(value) <= MAX_WIRE_TEXT, 'plain text bound')
        budget[1] += _LEN(value)
        need(budget[1] <= MAX_WIRE_TEXT_TOTAL, 'plain total text bound')
        return value
    if kind is _INT:
        need(-(1 << 127) <= value < (1 << 127), 'plain integer bound')
        return value
    if kind is _DICT:
        need(_LEN(value) <= MAX_RECORD_KEYS, 'plain dictionary bound')
        for key in value:
            need(_TYPE(key) is _STR, 'plain foreign dictionary key')
            need(_LEN(key) <= MAX_WIRE_TEXT, 'plain dictionary key bound')
        result = {}
        for key, item in value.items():
            budget[1] += _LEN(key)
            need(budget[1] <= MAX_WIRE_TEXT_TOTAL, 'plain total key text bound')
            result[key] = _plain(item, depth + 1, budget)
        return result
    if kind is _LIST or kind is _TUPLE:
        need(_LEN(value) <= MAX_SEQUENCE, 'plain sequence bound')
        return [_plain(item, depth + 1, budget) for item in value]
    raise EpochStop('foreign plain-record value rejected')


def plain_copy(value):
    """Bounded callback-free native copy before any codec/equality use."""
    return _plain(value, 0, [0, 0])


def required_roles(group: str) -> tuple[str, ...]:
    text(group, 2)
    need(group in GROUPS, 'positive/non-native/unknown group cannot import')
    return ROLES[:3] + (('pyinit_failure',) if group == '13' else
                        ('exec_failure',) if group == '14' else ())


def profile(value: dict) -> None:
    exact(value, PROFILE_KEYS)
    for key in PROFILE_KEYS:
        digest(value[key])


def launch(value: dict) -> None:
    exact(value, LAUNCH_KEYS)
    for key in LAUNCH_KEYS:
        digest(value[key])


def blob(value: dict, limit: int = FILE_BYTES) -> None:
    integer(limit, 0, FILE_BYTES)
    exact(value, ('path', 'sha256', 'bytes', 'identity'))
    path(value['path'])
    digest(value['sha256'])
    integer(value['bytes'], 0, limit)
    identity = value['identity']
    exact(identity, IDENTITY_KEYS)
    for key in IDENTITY_KEYS:
        integer(identity[key], 0, (1 << 127) - 1)
    need(identity['inode'] > 0 and identity['size'] == value['bytes'] and
         identity['mode'] & 0o170000 == 0o100000 and identity['links'] == 1,
         'regular single-link file custody differs')


def inode(value: dict) -> tuple[int, int]:
    blob(value)
    return value['identity']['device'], value['identity']['inode']


def canonical(value: dict) -> bytes:
    need(_TYPE(value) is _DICT, 'canonical top-level exact dictionary required')
    safe = plain_copy(value)
    raw = json.dumps(safe, sort_keys=True, separators=(',', ':'), ensure_ascii=True,
                     allow_nan=False).encode('ascii') + b'\n'
    need(_LEN(raw) <= RECORD_BYTES, 'record byte bound exceeded')
    return raw


def sha(raw: bytes) -> str:
    need(_TYPE(raw) is _BYTES, 'exact byte buffer required')
    return hashlib.sha256(raw).hexdigest()


def _pairs(pairs: list) -> dict:
    need(_TYPE(pairs) is _LIST and _LEN(pairs) <= MAX_RECORD_KEYS, 'decoded key count differs')
    result = {}
    for pair in pairs:
        need(_TYPE(pair) is _TUPLE and _LEN(pair) == 2, 'decoded pair differs')
        key, value = pair
        text(key)
        need(key not in result, 'duplicate JSON key')
        result[key] = value
    return result


def _reject_constant(value):
    raise EpochStop('nonfinite JSON constant rejected')


def decode(raw: bytes) -> dict:
    need(_TYPE(raw) is _BYTES, 'exact raw bytes required')
    need(0 < _LEN(raw) <= RECORD_BYTES, 'raw record bound differs')
    result = json.loads(raw.decode('ascii'), object_pairs_hook=_pairs, parse_constant=_reject_constant)
    need(_TYPE(result) is _DICT, 'decoded top-level record differs')
    safe = plain_copy(result)
    need(canonical(safe) == raw, 'noncanonical record bytes')
    return safe


def build(value: dict) -> None:
    exact(value, ('role', 'producer_role', 'producer_generation', 'producer_stage_sha256',
                  'command_sha256', 'profile', 'original_output', 'original_receipt',
                  'attempt', 'journal', 'stdout', 'stderr'))
    choice(value['role'], ROLES)
    choice(value['producer_role'], PRODUCERS)
    need((value['role'] in ROLES[:3]) == (value['producer_role'] == 'group01'), 'producer role swap')
    label(value['producer_generation'])
    digest(value['producer_stage_sha256'])
    digest(value['command_sha256'])
    profile(value['profile'])
    blob(value['original_output'])
    need(value['original_output']['bytes'] > 0, 'empty compiled artifact')
    for key, bound in (('original_receipt', 65536), ('attempt', 65536),
                       ('journal', JOURNAL_BYTES), ('stdout', LOG_BYTES), ('stderr', LOG_BYTES)):
        blob(value[key], bound)


def producer(value: dict) -> None:
    exact(value, ('role', 'generation', 'stage_sha256', 'command_sha256', 'root_sha256',
                  'terminal', 'raw_result', 'raw_groups', 'final_source_custody',
                  'parent_observation', 'completion_checker_sha256', 'builds'))
    choice(value['role'], PRODUCERS)
    label(value['generation'])
    for key in ('stage_sha256', 'command_sha256', 'root_sha256', 'completion_checker_sha256'):
        digest(value[key])
    for key in ('terminal', 'raw_result', 'raw_groups', 'final_source_custody', 'parent_observation'):
        blob(value[key], RAW_RESULT_BYTES)
    roles = ROLES[:3] if value['role'] == 'group01' else ROLES[3:]
    sequence(value['builds'], len(roles))
    for role, row in zip(roles, value['builds']):
        build(row)
        need(row['role'] == role and row['producer_role'] == value['role'] and
             row['producer_generation'] == value['generation'] and
             row['producer_stage_sha256'] == value['stage_sha256'], 'producer build binding differs')


def epoch(value: dict) -> None:
    exact(value, ('schema', 'epoch_id', 'mode', 'publication_state', 'intent', 'producers', 'exports',
                  'not_runtime_authority'))
    text(value['schema'])
    text(value['publication_state'])
    boolean(value['not_runtime_authority'])
    need(value['schema'] == SCHEMA and value['publication_state'] == 'COMMITTED' and
         value['not_runtime_authority'] is True, 'epoch publication/schema/authority differs')
    label(value['epoch_id'])
    blob(value['intent'], RECORD_BYTES)
    choice(value['mode'], ('normal', 'optimized'))
    sequence(value['producers'], 2)
    builds = []
    for role, row in zip(PRODUCERS, value['producers']):
        producer(row)
        need(row['role'] == role, 'producer order differs')
        builds.extend(row['builds'])
    need(value['producers'][0]['generation'] != value['producers'][1]['generation'], 'producer generation reused')
    sequence(value['exports'], MAX_EXPORTS)
    seen_paths, seen_inodes = set(), set()
    for role, source, row in zip(ROLES, builds, value['exports']):
        exact(row, ('role', 'build_sha256', 'file'))
        digest(row['build_sha256'])
        choice(row['role'], ROLES)
        need(row['role'] == role and row['build_sha256'] == sha(canonical(source)), 'export build binding differs')
        blob(row['file'])
        need((row['file']['sha256'], row['file']['bytes']) ==
             (source['original_output']['sha256'], source['original_output']['bytes']), 'export bytes differ')
        for record in (source['original_output'], row['file']):
            need(record['path'] not in seen_paths and inode(record) not in seen_inodes, 'artifact/link alias')
            seen_paths.add(record['path'])
            seen_inodes.add(inode(record))


def claim(value: dict, manifest: dict, expected_launch: dict,
          expected_group: str, expected_generation: str, expected_private_directory: str) -> None:
    epoch(manifest)
    launch(expected_launch)
    label(expected_generation)
    path(expected_private_directory)
    roles = required_roles(expected_group)
    exact(value, ('schema', 'epoch_id', 'mode', 'group', 'generation', 'manifest_sha256',
                  'launch', 'copies', 'local_compilations', 'not_runtime_authority', 'admission'))
    text(value['schema'])
    label(value['epoch_id'])
    choice(value['mode'], ('normal', 'optimized'))
    text(value['group'], 2)
    label(value['generation'])
    digest(value['manifest_sha256'])
    integer(value['local_compilations'], 0, 0)
    boolean(value['not_runtime_authority'])
    text(value['admission'])
    need(value['schema'] == CLAIM_SCHEMA and value['epoch_id'] == manifest['epoch_id'] and
         value['mode'] == manifest['mode'] and value['group'] == expected_group and
         value['generation'] == expected_generation and value['manifest_sha256'] == sha(canonical(manifest)),
         'claim independent epoch/mode/group/generation/manifest differs')
    launch(value['launch'])
    need(value['launch'] == expected_launch and type(value['local_compilations']) is int and
         value['local_compilations'] == 0 and value['not_runtime_authority'] is True and
         value['admission'] == 'CURRENT_CHILD_CHECKS_REQUIRED', 'claim authority/launch differs')
    sequence(value['copies'], len(roles))
    export_by_role = {row['role']: row for row in manifest['exports']}
    builds = [row for parent in manifest['producers'] for row in parent['builds']]
    occupied_paths = {row['original_output']['path'] for row in builds}
    occupied_inodes = {inode(row['original_output']) for row in builds}
    occupied_paths.update(row['file']['path'] for row in manifest['exports'])
    occupied_inodes.update(inode(row['file']) for row in manifest['exports'])
    for role, row in zip(roles, value['copies']):
        exact(row, ('role', 'build_sha256', 'source', 'destination'))
        choice(row['role'], ROLES)
        digest(row['build_sha256'])
        blob(row['source'])
        blob(row['destination'])
        expected = export_by_role[role]
        need(row['role'] == role and row['build_sha256'] == expected['build_sha256'] and
             row['source'] == expected['file'], 'copy original source provenance differs')
        dest = row['destination']
        need(dest['path'] == expected_private_directory + '/' + role + '.artifact',
             'private origin differs from independent launch')
        need((dest['sha256'], dest['bytes']) == (row['source']['sha256'], row['source']['bytes']),
             'private copy bytes differ')
        need(dest['path'] not in occupied_paths and inode(dest) not in occupied_inodes, 'private copy alias')
        occupied_paths.add(dest['path'])
        occupied_inodes.add(inode(dest))


def imported_inputs(raw_manifest: bytes, raw_claim: bytes, expected_manifest_sha256: str,
                    expected_launch: dict, expected_group: str, expected_generation: str,
                    expected_private_directory: str) -> tuple:
    """Validate data binding only. Child must still perform all original checks.

    Expected values must be supplied by independently pinned fresh launch source,
    never from either JSON argument. This helper has no runtime admission state.
    The negative Root must consume its one-attempt guard BEFORE invoking it.
    """
    digest(expected_manifest_sha256)
    need(sha(raw_manifest) == expected_manifest_sha256, 'independent parent manifest pin differs')
    manifest, receipt = decode(raw_manifest), decode(raw_claim)
    claim(receipt, manifest, expected_launch, expected_group, expected_generation, expected_private_directory)
    return manifest, receipt

# Opaque error/result custody. The owner never invokes a foreign object's
# string, equality, hash, attribute, metaclass, or formatting protocol.
ERROR_SLOTS = 64
CASE_SLOTS = 64
MAX_ERROR_ARGS = 2
MAX_ERROR_ARG_CHARS = 256
MAX_SECONDARY_PROJECTIONS = 6
_BASE_ARGS_GET = BaseException.args.__get__
_NATIVE_ERROR_LABELS = (
    (EpochStop, 'EPOCH_STOP'), (RuntimeError, 'RUNTIME_ERROR'),
    (ValueError, 'VALUE_ERROR'), (TypeError, 'TYPE_ERROR'),
    (OSError, 'OS_ERROR'), (FileNotFoundError, 'FILE_NOT_FOUND'),
    (PermissionError, 'PERMISSION_ERROR'), (InterruptedError, 'INTERRUPTED_ERROR'),
    (BlockingIOError, 'BLOCKING_IO_ERROR'), (MemoryError, 'MEMORY_ERROR'),
    (KeyboardInterrupt, 'KEYBOARD_INTERRUPT'), (SystemExit, 'SYSTEM_EXIT'),
    (OverflowError, 'OVERFLOW_ERROR'), (RecursionError, 'RECURSION_ERROR'),
    (UnicodeDecodeError, 'UNICODE_DECODE_ERROR'))


CUSTODY_SUCCESSORS = tuple(range(1, 257))
IO_QUARANTINE_ERROR = EpochStop('epoch IO quarantined; parent teardown required')


class ErrorOwner:
    __slots__ = ('_state',)


_OWNER_GET = ErrorOwner._state.__get__
_OWNER_SET = ErrorOwner._state.__set__
_OBJECT_NEW = object.__new__


def make_error_owner() -> ErrorOwner:
    owner = _OBJECT_NEW(ErrorOwner)
    # 0 primary [opaque,phase]; 1 errors; 2 phases; 3 uncertain FD;
    # 4 counts [secondary,close_attempts,close_confirmed,cases];
    # 5 overflow [first opaque, incomplete flag];
    # 6 cases [name,opaque,is_error,capture_state,raw_sink_return,validated].
    state = [[None, None, None], [None] * ERROR_SLOTS, [None] * ERROR_SLOTS,
             [None] * ERROR_SLOTS, [0, 0, 0, 0], [None, False],
             [[None, None, False, 'NOT_RETURNED', None, False, None, None] for _ in range(CASE_SLOTS)],
             [False, False, False, None, False, None, False, [0] * 5, [0] * 5, False, False, False, None],
             [[None, False, 'NOT_RETURNED', None] for _ in range(CASE_SLOTS)]]
    _OWNER_SET(owner, state)
    return owner


def owner_state(owner: ErrorOwner) -> list:
    need(_TYPE(owner) is ErrorOwner, 'exact trusted error owner required')
    state = _OWNER_GET(owner, ErrorOwner)
    need(_TYPE(state) is _LIST and _LEN(state) == 9, 'trusted owner state shape differs')
    for index, count in ((0, 3), (1, ERROR_SLOTS), (2, ERROR_SLOTS), (3, ERROR_SLOTS),
                         (4, 4), (5, 2), (6, CASE_SLOTS), (7, 13), (8, CASE_SLOTS)):
        need(_TYPE(state[index]) is _LIST and _LEN(state[index]) == count, 'trusted owner slot shape differs')
    integer(state[4][0], 0, ERROR_SLOTS)
    integer(state[4][1], 0, 1 << 32)
    integer(state[4][2], 0, state[4][1])
    integer(state[4][3], 0, CASE_SLOTS)
    boolean(state[5][1])
    io = state[7]
    for index in (0, 1, 2, 4, 6, 9, 10, 11):
        boolean(io[index])
    for index in (7, 8):
        need(_TYPE(io[index]) is _LIST and _LEN(io[index]) == 5, 'close counter digits differ')
        for digit in io[index][:4]:
            integer(digit, 0, 255)
        integer(io[index][4], 0, 1)
        need(io[index][4] == 0 or io[index][:4] == [0, 0, 0, 0], 'close counter exceeds inherited bound')
    # Fallible scalar projection occurs only at API entry/snapshot, never in
    # the inline cleanup path. The five native digits are authoritative.
    attempts = io[7][0] + (io[7][1] << 8) + (io[7][2] << 16) + (io[7][3] << 24) + (io[7][4] << 32)
    confirmed = io[8][0] + (io[8][1] << 8) + (io[8][2] << 16) + (io[8][3] << 24) + (io[8][4] << 32)
    need(confirmed <= attempts, 'native close confirmation exceeds attempt')
    state[4][1], state[4][2] = attempts, confirmed
    return state


def retain_primary(owner: ErrorOwner, opaque, phase: str, uncertain_fd=None) -> None:
    state = owner_state(owner)
    text(phase, 96)
    if uncertain_fd is not None:
        integer(uncertain_fd, 0, (1 << 31) - 1)
    if state[0][0] is None:
        state[0][0], state[0][1], state[0][2] = opaque, phase, uncertain_fd
    elif state[0][0] is not opaque:
        retain_secondary(owner, opaque, phase, uncertain_fd)


def retain_secondary(owner: ErrorOwner, opaque, phase: str, uncertain_fd) -> None:
    state = owner_state(owner)
    text(phase, 96)
    if uncertain_fd is not None:
        integer(uncertain_fd, 0, (1 << 31) - 1)
    index = state[4][0]
    if index < ERROR_SLOTS:
        # Preallocated native slots: no error formatting/attributes, no append.
        state[1][index], state[2][index], state[3][index] = opaque, phase, uncertain_fd
        state[4][0] = index + 1
    else:
        state[5][1] = True
        if state[5][0] is None:
            state[5][0] = opaque


def close_attempt(owner: ErrorOwner) -> None:
    state = owner_state(owner)
    need(state[4][1] < 1 << 32, 'close attempt counter bound')
    digits = state[7][7]
    index = 0
    while index < 4 and digits[index] == 255:
        digits[index] = 0
        index = CUSTODY_SUCCESSORS[index]
    digits[index] = CUSTODY_SUCCESSORS[digits[index]]


def close_confirmed(owner: ErrorOwner) -> None:
    state = owner_state(owner)
    need(state[4][2] < state[4][1], 'close confirmation lacks attempt')
    digits = state[7][8]
    index = 0
    while index < 4 and digits[index] == 255:
        digits[index] = 0
        index = CUSTODY_SUCCESSORS[index]
    digits[index] = CUSTODY_SUCCESSORS[digits[index]]


def project_error(opaque) -> dict:
    kind = _TYPE(opaque)
    label_value, admitted = 'FOREIGN_OPAQUE_EXCEPTION', False
    for expected_kind, literal_label in _NATIVE_ERROR_LABELS:
        if kind is expected_kind:
            label_value, admitted = literal_label, True
            break
    strings, omitted = [], False
    if admitted:
        # Native BaseException descriptor, only after exact whitelisted type.
        # No normal error.args/__dict__/cause/context/name/str access exists.
        arguments = _BASE_ARGS_GET(opaque, BaseException)
        if _TYPE(arguments) is _TUPLE:
            omitted = _LEN(arguments) > MAX_ERROR_ARGS
            for argument in arguments[:MAX_ERROR_ARGS]:
                if _TYPE(argument) is _STR:
                    if _LEN(argument) <= MAX_ERROR_ARG_CHARS:
                        strings.append(argument)
                    else:
                        strings.append(argument[:MAX_ERROR_ARG_CHARS])
                        omitted = True
                else:
                    omitted = True
        else:
            omitted = True
    return {'literal_type_label': label_value, 'exact_string_args': strings,
            'foreign_or_excess_args_omitted': omitted or not admitted,
            'original_object_retained_opaquely': True}


def error_snapshot(owner: ErrorOwner) -> dict:
    state = owner_state(owner)
    secondary = []
    for index in range(min(state[4][0], MAX_SECONDARY_PROJECTIONS)):
        text(state[2][index], 96)
        if state[3][index] is not None:
            integer(state[3][index], 0, (1 << 31) - 1)
        secondary.append({'slot': index, 'phase': state[2][index],
                          'uncertain_close_fd': state[3][index],
                          'error': project_error(state[1][index])})
    primary = None
    if state[0][0] is not None:
        text(state[0][1], 96)
        if state[0][2] is not None:
            integer(state[0][2], 0, (1 << 31) - 1)
        primary = {'phase': state[0][1], 'uncertain_close_fd': state[0][2],
                   'error': project_error(state[0][0])}
    # Projection happens only after operation cleanup. At most six recorder
    # errors are projected; a scan of all 64 slots counts omitted projections.
    recording_failures = []
    recording_failure_count = 0
    for index, row in enumerate(state[8]):
        if row[3] is not None:
            recording_failure_count += 1
            if len(recording_failures) < MAX_SECONDARY_PROJECTIONS:
                recording_failures.append({'slot': index, 'state': row[2],
                    'target_is_error': row[1], 'recording_error': project_error(row[3]),
                    'target_retained_opaquely': row[2] != 'NOT_RETURNED'})
    return {'primary': primary, 'secondary': secondary,
            'secondary_capture_incomplete': state[5][1],
            'secondary_projection_omitted': max(0, state[4][0] - MAX_SECONDARY_PROJECTIONS),
            'close_attempts': state[4][1], 'close_confirmed': state[4][2],
            'close_counter_incomplete': state[7][6],
            'io_quarantined': state[7][0], 'native_acquisition_pending': state[7][1],
            'possible_unreturned_native_fd': state[7][2],
            'parent_kernel_teardown_required': state[7][4],
            'uncertain_scandir_owner_retained': state[7][5] is not None,
            'scandir_close_returned_result_unobserved': state[7][9],
            # An earlier normal close observation never overrides a later
            # delivered failure or retained stream uncertainty.
            'scandir_release_uses_external_premise': (state[7][9] and not state[7][0]
                                                     and state[7][5] is None),
            'external_guard_acquisition_pending': state[7][10],
            'external_guard_fd_count_unavailable': state[7][11],
            'native_acquisition_error': None if state[7][3] is None else project_error(state[7][3]),
            'external_guard_error': None if state[7][12] is None else project_error(state[7][12]),
            'recording_failures': recording_failures,
            'recording_projection_omitted': max(0, recording_failure_count - MAX_SECONDARY_PROJECTIONS)}



def record_case(owner: ErrorOwner, name: str, opaque, is_error: bool) -> int:
    state = owner_state(owner)
    text(name, 16)
    boolean(is_error)
    count = state[4][3]
    need(count < CASE_SLOTS, 'case capacity exceeded')
    for index in range(count):
        row = state[6][index]
        need(_TYPE(row) is _LIST and _LEN(row) == 8, 'case slot shape differs')
        text(row[0], 16)
        need(row[0] != name, 'case identity replay')
    row = state[6][count]
    need(_TYPE(row) is _LIST and _LEN(row) == 8, 'case slot shape differs')
    text(row[3], 32)
    need(row[3] == 'NOT_RETURNED', 'case slot already used')
    row[0], row[1], row[2] = name, opaque, is_error
    row[3] = 'RETURNED_NOT_CAPTURED'
    state[4][3] = count + 1
    return count


def case_slot(owner: ErrorOwner, index: int) -> list:
    state = owner_state(owner)
    integer(index, 0, CASE_SLOTS - 1)
    need(index < state[4][3], 'case not recorded')
    row = state[6][index]
    need(_TYPE(row) is _LIST and _LEN(row) == 8, 'case slot shape differs')
    text(row[0], 16)
    boolean(row[2])
    choice(row[3], ('NOT_RETURNED', 'RETURNED_NOT_CAPTURED', 'RAW_CAPTURED', 'VALIDATED'))
    boolean(row[5])
    return row

# Original-function record checks use native descriptors only after exact
# FunctionType/CellType gates. Provenance must come from the authenticated Root
# factory call, never a record recaptured after adverse input.
from types import FunctionType as _FUNCTION_TYPE, CellType as _CELL_TYPE
_FUNCTION_GETTERS = tuple(_FUNCTION_TYPE.__dict__[name].__get__ for name in
    ('__code__', '__globals__', '__defaults__', '__kwdefaults__', '__closure__', '__annotations__', '__dict__'))
_CELL_GET = _CELL_TYPE.cell_contents.__get__


def capture_original_function(function) -> tuple:
    need(_TYPE(function) is _FUNCTION_TYPE, 'exact original function required')
    values = tuple(getter(function, _FUNCTION_TYPE) for getter in _FUNCTION_GETTERS)
    need(values[2] is None and values[3] is None, 'original callback defaults differ')
    closure = values[4]
    cells = []
    if closure is not None:
        need(_TYPE(closure) is _TUPLE and _LEN(closure) <= 64, 'original closure bound differs')
        for cell in closure:
            need(_TYPE(cell) is _CELL_TYPE, 'original closure cell differs')
            cells.append((cell, _CELL_GET(cell, _CELL_TYPE)))
    return function, values, tuple(cells)


def check_original_function(function, record) -> None:
    need(_TYPE(function) is _FUNCTION_TYPE, 'foreign callable rejected')
    need(_TYPE(record) is _TUPLE and _LEN(record) == 3, 'original callback record differs')
    need(function is record[0], 'original callback identity differs')
    values, cells = record[1], record[2]
    need(_TYPE(values) is _TUPLE and _LEN(values) == 7, 'original callback value record differs')
    need(_TYPE(cells) is _TUPLE and _LEN(cells) <= 64, 'original callback cell record differs')
    for getter, expected in zip(_FUNCTION_GETTERS, values):
        need(getter(function, _FUNCTION_TYPE) is expected, 'original callback environment differs')
    need(values[2] is None and values[3] is None, 'original callback defaults differ')
    closure = values[4]
    if closure is None:
        need(_LEN(cells) == 0, 'unexpected original closure records')
        return
    need(_TYPE(closure) is _TUPLE and _LEN(closure) == _LEN(cells), 'original closure record count differs')
    for actual_cell, pair in zip(closure, cells):
        need(_TYPE(pair) is _TUPLE and _LEN(pair) == 2, 'original cell pair differs')
        need(_TYPE(actual_cell) is _CELL_TYPE and actual_cell is pair[0], 'original cell identity differs')
        need(_CELL_GET(actual_cell, _CELL_TYPE) is pair[1], 'original closure content identity differs')


def prepare_case_shadow(owner: ErrorOwner) -> tuple:
    state = owner_state(owner)
    count = state[4][3]
    need(count < CASE_SLOTS, 'case shadow capacity exceeded')
    row = state[8][count]
    need(_TYPE(row) is _LIST and _LEN(row) == 4 and row[0] is None and row[3] is None and row[2] == 'NOT_RETURNED',
         'case shadow was already consumed')
    return state, count, row
