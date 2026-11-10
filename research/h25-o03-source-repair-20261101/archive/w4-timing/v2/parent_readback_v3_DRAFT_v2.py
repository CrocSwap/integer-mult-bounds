"""SOURCE-ONLY DRAFT v2. NOT IMPORTED, EXECUTED, ADOPTED OR RUNTIME-QUALIFIED.

No CLI/entry point is provided. Future admission must seal the actual W3 utility,
launcher, this source, schema adapters and independent expected fixture results.
run() is a proposed future interface. It never launches or imports a target.
"""
import hashlib
import json
import os
import re
import stat
import sys
from decimal import (Decimal, Context, localcontext, ROUND_HALF_EVEN,
                     Clamped, DivisionByZero, FloatOperation, Inexact,
                     InvalidOperation, Overflow, Rounded, Subnormal, Underflow)

RAW_CAP = 65536
TAG_CAP = 4096
REPORT_CAP = 65536
META_CAP = 65536
NUMBER_TOKEN_CAP = 32
JSON_DEPTH_CAP = 24
TAG = b'O03_TIME_V3 '
HEX = re.compile(r'[0-9a-f]{64}\Z')
MEASUREMENTS = frozenset(('wall_seconds', 'user_seconds', 'system_seconds',
                          'kernel_individual_maxrss_kib', 'utility_exit'))
ADMISSION_KEYS = frozenset(('schema', 'operation', 'timing_contract_sha256',
    'current_w3_seal_sha256', 'command_contract_sha256', 'timed_subject',
    'prefix_kind', 'rounding_quantum_seconds', 'limits', 'canonical_ledger'))
WAIT_KEYS = frozenset(('schema', 'admission_sha256', 'timing_contract_sha256',
    'command_contract_sha256', 'timed_subject', 'raw_time_sha256',
    'observer_sha256', 'kind', 'exit_code', 'signal_number', 'reaped',
    'tree_complete', 'cpu_complete'))
OBSERVER_REQUIRED = frozenset(('schema', 'admission_sha256', 'operation', 'status',
    'cpu_accounting', 'cpu_seconds', 'inclusive_wall_seconds',
    'inclusive_sampled_simultaneous_tree_rss_bytes', 'inclusive_samples',
    'inclusive_sampler_errors', 'errors', 'outside_tail'))
OBSERVER_OPTIONAL = frozenset(('measurement', 'kernel_individual_maxrss_kib',
    'policy_charge_seconds', 'observer_runtime_before', 'observer_runtime_after',
    'effective_before', 'effective_after', 'execution', 'worker_receipt'))
CPU_KEYS = frozenset(('parent_user', 'parent_system', 'reaped_children_user',
                       'reaped_children_system'))


def isolated_decimal_context():
    """Fresh complete settings; never inherit caller precision/traps/exponents.

    Every admitted token has <=32 chars and |explicit exponent|<=12. A
    conservative common decimal lattice is 10^-44. After the <=10^12 value
    gate, the largest intermediate here is RSS*1024 (<2*10^15); four-term CPU
    sums, wall+.01, and spent+charge are smaller. Aligned coefficients therefore
    need <=60 digits. Precision128 is ample. Full arithmetic/rounding traps fail
    closed if that domain argument is ever violated. See NUMERIC-PROOF-v2.md.
    """
    return Context(prec=128, rounding=ROUND_HALF_EVEN, Emin=-999, Emax=999,
                   capitals=1, clamp=0, flags=[],
                   traps=[Clamped, DivisionByZero, FloatOperation, Inexact,
                          InvalidOperation, Overflow, Rounded, Subnormal, Underflow])


class ReadbackError(RuntimeError):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


def need(ok, code):
    if not ok:
        raise ReadbackError(code)


def same_keys(obj, keys, code):
    need(type(obj) is dict and set(obj) == keys, code)


def sha(value):
    need(type(value) is str and HEX.fullmatch(value) is not None, 'SHA_SCHEMA')
    return value


def error_name(error):
    # Never call an untrusted exception's __str__/__repr__ for diagnostics.
    try:
        name = type(error).__name__
        return name[:80] if type(name) is str else 'UnknownException'
    except BaseException:
        return 'UnknownException'


def event(state, channel, code, error):
    # Diagnostic allocation/mutation itself is secondary and best effort.
    try:
        if len(state[channel]) < 12:
            state[channel].append({'code': code[:64], 'type': error_name(error)})
    except BaseException:
        pass


def identity(info):
    return tuple(getattr(info, 'st_' + k) for k in
        ('dev', 'ino', 'mode', 'uid', 'gid', 'nlink', 'size', 'mtime_ns', 'ctime_ns'))


def directory_identity(info):
    return tuple(getattr(info, 'st_' + k) for k in
                 ('dev', 'ino', 'mode', 'uid', 'gid', 'nlink'))


def close_all(fds, state, active, code='INPUT_CLOSE_FAILURE'):
    first = None
    for fd in reversed(fds):
        try:
            os.close(fd)
        except BaseException as error:
            event(state, 'secondary_errors', code, error)
            if first is None:
                first = error
    if active is None and first is not None:
        raise first


def path_parts(path):
    need(type(path) is str and len(path) <= 4096 and path.startswith('/'), 'PATH_SCHEMA')
    parts = path[1:].split('/')
    need(bool(parts) and all(p not in ('', '.', '..') and '\x00' not in p for p in parts),
         'PATH_NONCANONICAL')
    return parts


def parent_open(path, fds):
    """Directory-relative no-follow walk. All descriptors are nonblocking."""
    parts = path_parts(path)
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_NONBLOCK
    fd = os.open('/', flags)
    fds.append(fd)
    ancestry = [directory_identity(os.fstat(fd))]
    for part in parts[:-1]:
        fd = os.open(part, flags, dir_fd=fd)
        fds.append(fd)
        ancestry.append(directory_identity(os.fstat(fd)))
    return fd, parts[-1], ancestry


def read_regular(path, cap, used, state, expected_sha=None):
    """Size gate before read; <=cap materialized, one sentinel byte not appended.

    Requires retained immutable 0444 regular files with one hard link. No use of
    pathlib.resolve(), ordinary open() on a special file, or a second path read.
    Directory-chain reopening checks an ancestor substitution during this read.
    """
    fds, active = [], None
    try:
        parent, leaf, ancestry = parent_open(path, fds)
        before = os.stat(leaf, dir_fd=parent, follow_symlinks=False)
        need(stat.S_ISREG(before.st_mode), 'FILE_NOT_REGULAR')
        need(before.st_nlink == 1, 'FILE_HARDLINK_ALIAS')
        need(stat.S_IMODE(before.st_mode) == 0o444, 'FILE_NOT_IMMUTABLE')
        need(0 <= before.st_size <= cap, 'INPUT_CAP')
        key = (before.st_dev, before.st_ino)
        need(key not in used, 'FILE_DISALLOWED_ALIAS')
        fd = os.open(leaf, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
        fds.append(fd)
        opened = os.fstat(fd)
        need(identity(before) == identity(opened), 'INPUT_IDENTITY_CHANGED')
        need(stat.S_ISREG(opened.st_mode) and opened.st_size <= cap, 'INPUT_CAP_OR_KIND')
        raw = bytearray()
        digest = hashlib.sha256()
        while len(raw) < cap:
            chunk = os.read(fd, min(4096, cap - len(raw)))
            if not chunk:
                break
            raw.extend(chunk)
            digest.update(chunk)
        # A file growing beyond cap is rejected without appending a cap+1 buffer.
        need(not os.read(fd, 1), 'INPUT_CAP')
        after = os.fstat(fd)
        fresh = os.stat(leaf, dir_fd=parent, follow_symlinks=False)
        fresh_parent, fresh_leaf, fresh_ancestry = parent_open(path, fds)
        fresh_path = os.stat(fresh_leaf, dir_fd=fresh_parent, follow_symlinks=False)
        need(ancestry == fresh_ancestry and identity(before) == identity(after) ==
             identity(fresh) == identity(fresh_path), 'INPUT_IDENTITY_CHANGED')
        need(len(raw) == after.st_size, 'INPUT_SIZE_CHANGED')
        actual_sha = digest.hexdigest()
        if expected_sha is not None:
            need(actual_sha == sha(expected_sha), 'INPUT_HASH_MISMATCH')
        used.add(key)
        return bytes(raw), {'sha256': actual_sha, 'bytes': len(raw),
                            'dev': after.st_dev, 'ino': after.st_ino}
    except BaseException as error:
        active = error
        raise
    finally:
        close_all(fds, state, active)


def lexical_depth(raw):
    # Bound JSON nesting before decoder recursion/object construction. Strings
    # and escaped quotes are skipped; final syntax is still checked by JSON.
    depth, quoted, escape = 0, False, False
    for byte in raw:
        if quoted:
            if escape:
                escape = False
            elif byte == 92:
                escape = True
            elif byte == 34:
                quoted = False
        elif byte == 34:
            quoted = True
        elif byte in (91, 123):
            depth += 1
            need(depth <= JSON_DEPTH_CAP, 'JSON_DEPTH')
        elif byte in (93, 125):
            depth -= 1
            need(depth >= 0, 'JSON_SYNTAX')


def number_token(token):
    need(len(token) <= NUMBER_TOKEN_CAP, 'NUMBER_TOKEN_CAP')
    # Decimal conversion is bounded in lexical length and exponent. This draft
    # stores measurements as exact decimal report strings, never float rounds.
    match = re.search(r'[eE]([+-]?[0-9]+)\Z', token)
    if match:
        exponent = match.group(1)
        need(len(exponent.lstrip('+-')) <= 3, 'NUMBER_EXPONENT_RANGE')
        need(abs(int(exponent)) <= 12, 'NUMBER_EXPONENT_RANGE')
    value = Decimal(token)
    need(value.is_finite(), 'NUMBER_NONFINITE')
    need(abs(value) <= Decimal('1000000000000'), 'NUMBER_RANGE')
    return value


def integer_token(token):
    need(len(token) <= NUMBER_TOKEN_CAP, 'NUMBER_TOKEN_CAP')
    value = int(token)
    need(abs(value) <= 1000000000000, 'NUMBER_RANGE')
    return value


def no_constant(token):
    raise ReadbackError('NUMBER_NONFINITE')


def unique_pairs(pairs):
    obj = {}
    for key, value in pairs:
        need(key not in obj, 'JSON_DUPLICATE_KEY')
        obj[key] = value
    return obj


def strict_json(raw):
    lexical_depth(raw)
    text = raw.decode('utf-8', errors='strict')
    return json.loads(text, object_pairs_hook=unique_pairs, parse_int=integer_token,
                      parse_float=number_token, parse_constant=no_constant)


def nonnegative(value, code):
    need(type(value) in (int, Decimal), code)
    value = Decimal(value)
    need(value.is_finite() and 0 <= value <= Decimal('1000000000000'), code)
    return value


def unsigned_integer(value, maximum, code):
    need(type(value) is int and 0 <= value <= maximum, code)
    return value


def timing(raw, grammar, prefix_kind):
    if grammar == 'historical-two-line-failed-only-v1':
        # An explicitly selected exact historical grammar; never successful.
        prefix = b'Command exited with non-zero status 1\n'
        need(raw.startswith(prefix) and raw.count(b'\n') == 2 and raw.endswith(b'\n'),
             'LEGACY_GRAMMAR')
        need(len(raw) - len(prefix) - 1 <= TAG_CAP, 'TAG_CAP')
        obj = strict_json(raw[len(prefix):-1])
        same_keys(obj, (MEASUREMENTS - {'utility_exit'}) | {'exit'}, 'LEGACY_SCHEMA')
        need(type(obj['exit']) is int and obj['exit'] == 1, 'LEGACY_EXIT')
        obj['utility_exit'] = obj.pop('exit')
        legacy = True
        diagnostics = [0, len(prefix)]
    else:
        need(grammar == 'gnu-time-tagged-v3', 'TIMING_GRAMMAR')
        need(raw.count(TAG) == 1, 'TIMING_TAG_COUNT')
        first, separator, remainder = raw.partition(b'\n')
        if prefix_kind == 'empty':
            prefix = b''
            record_and_suffix = raw
        else:
            need(separator == b'\n', 'PREFIX_GRAMMAR')
            if prefix_kind == 'gnu-nonzero':
                need(re.fullmatch(rb'Command exited with non-zero status ([1-9][0-9]{0,2})', first)
                     is not None, 'PREFIX_GRAMMAR')
                code = int(first.rsplit(b' ', 1)[1])
                need(code <= 255, 'PREFIX_GRAMMAR')
            elif prefix_kind == 'gnu-signal':
                need(re.fullmatch(rb'Command terminated by signal ([1-9][0-9]?)', first)
                     is not None, 'PREFIX_GRAMMAR')
                need(int(first.rsplit(b' ', 1)[1]) <= 64, 'PREFIX_GRAMMAR')
            else:
                raise ReadbackError('PREFIX_GRAMMAR')
            prefix = first + separator
            record_and_suffix = remainder
        record, lf, suffix = record_and_suffix.partition(b'\n')
        need(len(record) <= TAG_CAP, 'TAG_CAP')
        need(record.startswith(TAG), 'TAG_NOT_ANCHORED')
        need(all(c in b' \t\r\n' for c in suffix), 'TIMING_SUFFIX')
        obj = strict_json(record[len(TAG):])
        same_keys(obj, MEASUREMENTS, 'TIMING_SCHEMA')
        legacy = False
        diagnostics = [0, len(prefix)]
    for key in MEASUREMENTS - {'utility_exit'}:
        obj[key] = nonnegative(obj[key], 'MEASUREMENT_INVALID')
    # KiB must be an integer-valued measurement; GNU %M expands as integer.
    need(obj['kernel_individual_maxrss_kib'] ==
         obj['kernel_individual_maxrss_kib'].to_integral_value(), 'RSS_NOT_INTEGER')
    unsigned_integer(obj['utility_exit'], 255, 'UTILITY_EXIT_SCHEMA')
    return obj, diagnostics, legacy


def admission_check(admission, request):
    same_keys(admission, ADMISSION_KEYS, 'ADMISSION_SCHEMA')
    need(admission['schema'] == 'o03-timing-admission-v3' and
         admission['operation'] == 'complete-fixed-o03', 'ADMISSION_SCHEMA')
    for key in ('timing_contract_sha256', 'current_w3_seal_sha256', 'command_contract_sha256'):
        need(sha(admission[key]) == sha(request[key]), 'PROVIDER_ADMISSION_BINDING')
    need(admission['timed_subject'] == 'observer', 'TIMED_SUBJECT_UNREVIEWED')
    need(admission['prefix_kind'] in ('empty', 'gnu-nonzero', 'gnu-signal'), 'PREFIX_GRAMMAR')
    same_keys(admission['limits'], {'outer_seconds', 'rss_bytes'}, 'LIMIT_SCHEMA')
    same_keys(admission['canonical_ledger'], {'current_ledger_sha256', 'cap_seconds',
                                           'spent_seconds'}, 'LEDGER_SCHEMA')
    ledger = admission['canonical_ledger']
    need(sha(ledger['current_ledger_sha256']) == sha(request['current_ledger_sha256']),
         'LEDGER_BINDING')
    need(nonnegative(admission['limits']['outer_seconds'], 'LIMIT_SCHEMA') == Decimal(180)
         and type(admission['limits']['rss_bytes']) is int
         and admission['limits']['rss_bytes'] == 1073741824, 'LIMIT_SCHEMA')
    need(nonnegative(ledger['cap_seconds'], 'LEDGER_SCHEMA') == Decimal(2400), 'LEDGER_SCHEMA')
    spent = nonnegative(ledger['spent_seconds'], 'LEDGER_SCHEMA')
    need(spent < 2400, 'LEDGER_EXHAUSTED')
    need(nonnegative(admission['rounding_quantum_seconds'], 'ROUNDING_SCHEMA') ==
         Decimal('0.01'), 'ROUNDING_SCHEMA')


def observer_check(observer, admission_hash):
    need(type(observer) is dict and OBSERVER_REQUIRED <= set(observer) and
         set(observer) <= OBSERVER_REQUIRED | OBSERVER_OPTIONAL, 'OBSERVER_SCHEMA')
    need(observer['schema'] == 'o03-inclusive-observer-v1' and
         observer['operation'] == 'complete-fixed-o03', 'OBSERVER_SCHEMA')
    need(sha(observer['admission_sha256']) == admission_hash, 'OBSERVER_ADMISSION_BINDING')
    need(observer['status'] in ('PASS', 'STOP'), 'OBSERVER_SCHEMA')
    need(type(observer['errors']) is list and type(observer['inclusive_sampler_errors']) is list,
         'OBSERVER_SCHEMA')
    same_keys(observer['cpu_seconds'], CPU_KEYS, 'OBSERVER_CPU_SCHEMA')
    for value in observer['cpu_seconds'].values():
        nonnegative(value, 'OBSERVER_CPU_INVALID')
    nonnegative(observer['inclusive_wall_seconds'], 'OBSERVER_WALL_INVALID')
    unsigned_integer(observer['inclusive_sampled_simultaneous_tree_rss_bytes'],
                     1000000000000, 'OBSERVER_RSS_INVALID')
    unsigned_integer(observer['inclusive_samples'], 1000000000000, 'OBSERVER_SAMPLES_INVALID')


def corroborate(wait, admission, a_hash, raw_pin, observer_pin, prefix, record):
    same_keys(wait, WAIT_KEYS, 'TERMINATION_SCHEMA')
    need(wait['schema'] == 'o03-launcher-termination-v3', 'TERMINATION_SCHEMA')
    for key, value in (('admission_sha256', a_hash),
        ('timing_contract_sha256', admission['timing_contract_sha256']),
        ('command_contract_sha256', admission['command_contract_sha256']),
        ('raw_time_sha256', raw_pin['sha256']), ('observer_sha256', observer_pin['sha256'])):
        need(sha(wait[key]) == value, 'TERMINATION_BINDING')
    need(wait['timed_subject'] == admission['timed_subject'], 'TIMED_SUBJECT_DISAGREEMENT')
    for key in ('reaped', 'tree_complete', 'cpu_complete'):
        need(type(wait[key]) is bool, 'TERMINATION_SCHEMA')
    need(wait['kind'] in ('exit', 'signal', 'timeout'), 'TERMINATION_SCHEMA')
    if wait['kind'] == 'exit':
        exit_code = unsigned_integer(wait['exit_code'], 255, 'TERMINATION_SCHEMA')
        need(wait['signal_number'] is None and record['utility_exit'] == exit_code,
             'TERMINATION_DISAGREEMENT')
        if exit_code == 0:
            need(prefix == 'empty', 'TERMINATION_DIAGNOSTIC_DISAGREEMENT')
        else:
            need(prefix == 'gnu-nonzero', 'TERMINATION_DIAGNOSTIC_DISAGREEMENT')
        return exit_code == 0
    unsigned_integer(wait['signal_number'], 64, 'TERMINATION_SCHEMA')
    need(wait['signal_number'] > 0 and wait['exit_code'] is None,
         'TERMINATION_SCHEMA')
    need(prefix == 'gnu-signal', 'TERMINATION_DIAGNOSTIC_DISAGREEMENT')
    # Utility exit for signal/timeout remains opaque; never 128+signal inference.
    return False


def report_bytes(state):
    # Only fixed-size fields, <=12 bounded diagnostics, decimal strings <=64 and
    # pins are projected. No raw text, paths, external objects or exception text.
    encoder = json.JSONEncoder(ensure_ascii=True, allow_nan=False, sort_keys=True,
                               separators=(',', ':'))
    out = bytearray()
    for piece in encoder.iterencode(state):
        need(len(piece) <= REPORT_CAP and len(out) + len(piece) + 1 <= REPORT_CAP,
             'REPORT_CAP')
        out.extend(piece.encode('ascii'))
    out.extend(b'\n')
    return bytes(out)


def write_report(path, raw, used, state):
    fds, active = [], None
    try:
        parent, leaf, ancestry = parent_open(path, fds)
        fd = os.open(leaf, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW |
                     os.O_NONBLOCK, 0o600, dir_fd=parent)
        fds.append(fd)
        before = os.fstat(fd)
        need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and
             (before.st_dev, before.st_ino) not in used, 'REPORT_ALIAS_OR_KIND')
        offset = 0
        while offset < len(raw):
            count = os.write(fd, raw[offset:])
            need(type(count) is int and count > 0, 'REPORT_SHORT_WRITE')
            offset += count
        os.fsync(fd)
        after = os.fstat(fd)
        fresh = os.stat(leaf, dir_fd=parent, follow_symlinks=False)
        fresh_parent, fresh_leaf, fresh_ancestry = parent_open(path, fds)
        current = os.stat(fresh_leaf, dir_fd=fresh_parent, follow_symlinks=False)
        need(ancestry == fresh_ancestry and identity(after) == identity(fresh) ==
             identity(current) and after.st_size == len(raw), 'REPORT_IDENTITY_CHANGED')
    except BaseException as error:
        active = error
        raise
    finally:
        close_all(fds, state, active, 'REPORT_CLOSE_FAILURE')


class ReadbackOutcome:
    def __init__(self, state):
        self.state = state
        self.primary = None
        self.traceback = None

    def raise_primary(self):
        if self.primary is not None:
            raise self.primary.with_traceback(self.traceback)


def run(request):
    """Future readback only. All external work lives inside primary boundary.

    Trusted request hashes MUST come from separately authenticated independent
    admission/custody; illustrative fixture hashes are never current authority.
    Return a structured outcome preserving the exact primary exception object.
    The caller may invoke outcome.raise_primary(); report failure never substitutes
    that object. A controller completion receipt must attest report write/close.
    """
    state = {'schema': 'o03-parent-readback-v3-draft', 'status': 'STOP',
        'execution_success': None, 'measurement_valid': None,
        'termination_corroborated': None, 'cap_validation': 'UNKNOWN',
        'ledger_validation': 'UNKNOWN', 'accounting_complete': None,
        'primary_errors': [], 'secondary_errors': [], 'measurements': None,
        'policy_charge_seconds': None, 'raw_time': None, 'diagnostic_byte_range': None,
        'admission_record': None, 'observer_record': None, 'termination_record': None,
        'observer_status': None, 'observer_error_count': None,
        'legacy_derived_failure_only': False, 'report_write': 'NOT_ATTEMPTED',
        'provider_status': 'EXTERNAL_CURRENT_W3_SEAL_REQUIRED_NOT_VERIFIED_HERE',
        'qualification': 'READBACK_ONLY_NO_O03_OR_W5_ADMISSION',
        'outside_tail_cost': 'OPEN_NOT_ZERO', 'publication_cost': 'OPEN_NOT_ZERO',
        'canonical_ledger_written_here': False}
    outcome = ReadbackOutcome(state)
    primary, traceback, used, stage = None, None, set(), 'REQUEST'
    numeric_manager, numeric_entered = None, False
    try:
        numeric_manager = localcontext(isolated_decimal_context())
        numeric_manager.__enter__()
        numeric_entered = True
        need(type(request) is dict, 'REQUEST_SCHEMA')
        grammar = request['grammar']
        need(grammar in ('gnu-time-tagged-v3', 'historical-two-line-failed-only-v1'),
             'TIMING_GRAMMAR')
        names = ('raw_time', 'report') if grammar == 'historical-two-line-failed-only-v1' else (
            'admission', 'observer', 'termination', 'raw_time', 'report')
        paths = [request[k] for k in names]
        for path in paths:
            path_parts(path)
        need(len(set(paths)) == len(paths), 'PATH_DISALLOWED_ALIAS')
        if grammar == 'historical-two-line-failed-only-v1':
            stage = 'TIMING_READ'
            raw, raw_pin = read_regular(request['raw_time'], RAW_CAP, used, state,
                                        request['raw_time_sha256'])
            state['raw_time'] = raw_pin
            stage = 'TIMING_PARSE'
            record, diagnostic_range, legacy = timing(raw, grammar, None)
            state['measurement_valid'] = True
            state['measurements'] = {k: str(record[k]) for k in sorted(MEASUREMENTS)}
            state['diagnostic_byte_range'] = diagnostic_range
            state['legacy_derived_failure_only'] = True
            state['execution_success'] = False
            state['accounting_complete'] = False
            raise ReadbackError('LEGACY_FAILED_ACCOUNTING_ONLY')
        stage = 'ADMISSION_READ'
        a_raw, a_pin = read_regular(request['admission'], META_CAP, used, state,
                                    request['admission_sha256'])
        state['admission_record'] = a_pin
        admission = strict_json(a_raw)
        admission_check(admission, request)
        stage = 'OBSERVER_READ'
        o_raw, o_pin = read_regular(request['observer'], META_CAP, used, state,
                                    request['observer_sha256'])
        state['observer_record'] = o_pin
        observer = strict_json(o_raw)
        observer_check(observer, a_pin['sha256'])
        state['observer_status'] = observer['status']
        state['observer_error_count'] = len(observer['errors'])
        stage = 'TERMINATION_READ'
        w_raw, w_pin = read_regular(request['termination'], META_CAP, used, state,
                                    request['termination_sha256'])
        state['termination_record'] = w_pin
        wait = strict_json(w_raw)
        stage = 'TIMING_READ'
        raw, raw_pin = read_regular(request['raw_time'], RAW_CAP, used, state,
                                    request['raw_time_sha256'])
        state['raw_time'] = raw_pin
        stage = 'TIMING_PARSE'
        record, diagnostic_range, legacy = timing(raw, grammar, admission['prefix_kind'])
        state['measurement_valid'] = True
        state['measurements'] = {k: str(record[k]) for k in sorted(MEASUREMENTS)}
        state['diagnostic_byte_range'] = diagnostic_range
        state['legacy_derived_failure_only'] = legacy
        if legacy:
            state['execution_success'] = False
            state['accounting_complete'] = False
            # Historical facts are preserved. No implicit legacy termination,
            # successful readback, current grant or repaired runtime is invented.
            raise ReadbackError('LEGACY_FAILED_ACCOUNTING_ONLY')
        stage = 'TERMINATION_VALIDATE'
        success = corroborate(wait, admission, a_pin['sha256'], raw_pin, o_pin,
                              admission['prefix_kind'], record)
        # Prefix numeric content is independently matched to wait facts.
        if admission['prefix_kind'] != 'empty':
            diagnostic = raw[:diagnostic_range[1]].rstrip(b'\n')
            number = int(diagnostic.rsplit(b' ', 1)[1])
            expected = wait['exit_code'] if wait['kind'] == 'exit' else wait['signal_number']
            need(number == expected, 'TERMINATION_DIAGNOSTIC_DISAGREEMENT')
        need(wait['reaped'] is True, 'TERMINATION_NOT_REAPED')
        state['termination_corroborated'] = True
        state['execution_success'] = success
        charge = record['wall_seconds'] + Decimal('0.01')
        state['policy_charge_seconds'] = str(charge)
        stage = 'CAP_VALIDATE'
        state['cap_validation'] = 'FAIL'
        need(record['kernel_individual_maxrss_kib'] * 1024 <= 1073741824,
             'INDIVIDUAL_RSS_CAP')
        need(observer['inclusive_sampled_simultaneous_tree_rss_bytes'] <= 1073741824 and
             observer['inclusive_samples'] > 0 and not observer['inclusive_sampler_errors'],
             'INCLUSIVE_SAMPLER_INVALID')
        need(charge <= 180 and nonnegative(observer['inclusive_wall_seconds'],
             'OBSERVER_WALL_INVALID') <= charge, 'WALL_CAP_OR_COVERAGE')
        observed_cpu = sum((nonnegative(v, 'OBSERVER_CPU_INVALID') for v in
                            observer['cpu_seconds'].values()), Decimal(0))
        need(record['user_seconds'] + record['system_seconds'] + Decimal('0.03') >=
             observed_cpu, 'CPU_COVERAGE')
        state['cap_validation'] = 'PASS'
        stage = 'LEDGER_VALIDATE'
        state['ledger_validation'] = 'FAIL'
        need(nonnegative(admission['canonical_ledger']['spent_seconds'], 'LEDGER_SCHEMA') +
             charge <= 2400, 'LEDGER_CAP')
        state['ledger_validation'] = 'PASS'
        stage = 'ACCOUNTING_VALIDATE'
        complete = (wait['tree_complete'] is True and wait['cpu_complete'] is True and
            observer['cpu_accounting'] == 'COMPLETE_FOR_SOURCE_FIXED_REAPED_SUCCESS_TREE')
        state['accounting_complete'] = complete
        need(complete, 'ACCOUNTING_INCOMPLETE')
        need(success and observer['status'] == 'PASS' and not observer['errors'], 'WORKLOAD_STOP')
        state['status'] = 'PASS_READBACK_CONDITIONAL_ONLY'
    except BaseException as error:
        primary, traceback = error, error.__traceback__
        if stage == 'TIMING_PARSE' and state['measurement_valid'] is None:
            state['measurement_valid'] = False
        if stage == 'TERMINATION_VALIDATE':
            state['termination_corroborated'] = False
        code = error.code if type(error) is ReadbackError else stage
        event(state, 'primary_errors', code, error)
    finally:
        # Capture the primary before restoration; even a restoration failure
        # cannot replace a read/parse/execution/cap/ledger exception object.
        if numeric_entered:
            try:
                numeric_manager.__exit__(None, None, None)
            except BaseException as error:
                event(state, 'secondary_errors', 'DECIMAL_CONTEXT_RESTORE_FAILURE', error)
                if primary is None:
                    primary, traceback = error, error.__traceback__
                    state['status'] = 'STOP'
                    event(state, 'primary_errors', 'DECIMAL_CONTEXT_RESTORE_FAILURE', error)
    # A reporting failure cannot replace an already saved read/parse/workload
    # failure. In-memory failure evidence and bounded stderr are best effort.
    try:
        state['report_write'] = 'ATTEMPTED'
        payload = report_bytes(state)
        write_report(request['report'], payload, used, state)
        state['report_write'] = 'COMPLETE'
    except BaseException as error:
        event(state, 'secondary_errors', 'REPORT_WRITE_OR_CLOSE_FAILURE', error)
        try:
            state['report_write'] = 'FAILED'
            state['status'] = 'STOP'
        except BaseException:
            pass
        if primary is None:
            primary, traceback = error, error.__traceback__
            event(state, 'primary_errors', 'REPORT_WRITE_OR_CLOSE_FAILURE', error)
        try:
            # No raw diagnostics or exception strings are regenerated here.
            sys.stderr.write('O03_READBACK_REPORT_FAILURE primary=' + error_name(primary) +
                             ' reporting=' + error_name(error) + '\n')
        except BaseException as diagnostic_error:
            event(state, 'secondary_errors', 'FALLBACK_DIAGNOSTIC_FAILURE', diagnostic_error)
    outcome.primary, outcome.traceback = primary, traceback
    return outcome
