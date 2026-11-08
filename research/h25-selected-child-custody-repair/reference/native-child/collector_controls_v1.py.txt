"""Actual authority collector controls on isolated source-authenticated owners.

UNEXECUTED. Parent supplies exact final bytes/pin and original Root primitives.
No replacement collector, production private-cell change, expected recapture,
second native image, module-registry replacement, or original-control waiver.
"""
import builtins
from hashlib import sha256
from types import FunctionType, ModuleType, CellType, CodeType, BuiltinFunctionType
from native_field_controls_v1 import FIELDS, _hook, empty_sample
from receipt_contract_v1 import need, record, finish

CASE_IDS = ('collector-seven-matches', 'collector-first-mismatch',
 'collector-middle-mismatch', 'collector-last-mismatch', 'collector-vector-hit',
 'collector-legitimate-close-before-events', 'collector-active-close-getter',
 'collector-active-close-id', 'collector-native-only-close',
 'collector-publication-drift', 'collector-wrapper-before-first-use',
 'collector-wrong-owner-before-first-use')
NORMAL_CASE_COUNT = 12
OPTIMIZED_CASE_COUNT = 12
# id(function), seven current-getter/id + independent expected-id comparisons.
PREFIX = ('id', 'get:__code__', 'id', 'id', 'id', 'id', 'id', 'id',
          'get:__defaults__', 'id', 'id', 'get:__kwdefaults__', 'id', 'id',
          'id', 'id', 'id', 'id')
ACTIVE = (0, 1, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1, 0)


def expectations():
    all_events = PREFIX + ('id',) * 4
    all_active = ACTIVE + (0,) * 4
    def row(events, active, value=True, error=None, phase='ACTIVE', vectors=1):
        return {'events': list(events), 'active': list(active), 'result': value,
                'error': error, 'phase': phase, 'field_vectors': vectors}
    expected = {
      'collector-seven-matches': row(all_events, all_active),
      'collector-first-mismatch': row(PREFIX[:4], ACTIVE[:4], False, vectors=0),
      'collector-middle-mismatch': row(PREFIX[:11], ACTIVE[:11], False, vectors=0),
      'collector-last-mismatch': row(PREFIX, ACTIVE, False, vectors=0),
      'collector-vector-hit': row(('id',) * 12, (0,) * 12),
      'collector-legitimate-close-before-events': row(all_events, (0,) * 22, phase='CLOSED'),
      'collector-active-close-getter': row(all_events, (0, 1, 1) + (0,) * 19, phase='CLOSED'),
      'collector-active-close-id': row(all_events, (0, 1, 1) + (0,) * 19, phase='CLOSED'),
      'collector-native-only-close': row(('id',), (0,), None,
        ['RuntimeError', 'Runtime drift: native-only close is not Root close'], vectors=0),
      'collector-publication-drift': row(('id',), (0,), None,
        ['RuntimeError', 'Runtime drift: native field publication differs'], phase='ACTIVE', vectors=0),
      'collector-wrapper-before-first-use': row(('id',), (0,), None,
        ['RuntimeError', 'Runtime drift: native field publication differs'], vectors=0),
      'collector-wrong-owner-before-first-use': row(('id',), (0,), None,
        ['RuntimeError', 'Runtime drift: native field publication differs'], vectors=0)}
    need(len(expected) == 12 and tuple(expected) == CASE_IDS, 'collector literal inventory')
    return expected


def admit_descriptor(descriptor):
    """Original Python caller admission, never a new native self-validator."""
    need(type(descriptor) is tuple and len(descriptor) == 6 and
         descriptor[0] == 'h25-cold-authority-caller-v1', 'fixture caller descriptor')
    getters = tuple(FunctionType.__dict__[name].__get__ for name in FIELDS[:6])
    cell_get = CellType.__dict__['cell_contents'].__get__
    missing = object()
    records = (descriptor[3],) + descriptor[4]
    need(type(descriptor[4]) is tuple and 1 <= len(records) <= 8193, 'fixture helper census')
    for item in records:
        need(type(item) is tuple and len(item) == 9 and type(item[0]) is FunctionType,
             'fixture target exact function')
        fn = item[0]
        for getter, expected in zip(getters, item[1:7]):
            need(builtins.id(getter(fn, FunctionType)) == builtins.id(expected),
                 'fixture target function environment')
        keywords = item[5]
        if keywords is not None:
            need(type(keywords) is dict and len(keywords) == len(item[7]), 'fixture target keyword census')
            iterator = current = None
            valid = True
            try:
                iterator = dict.__iter__(keywords)
                while True:
                    current = next(iterator, missing)
                    if current is missing:
                        break
                    if type(current) is not str:
                        valid = False
                        break
                    current = None
            finally:
                iterator = current = None
            need(valid, 'fixture target keyword key domain')
            for name, expected in item[7]:
                need(builtins.id(dict.get(keywords, name, missing)) == builtins.id(expected),
                     'fixture target keyword value')
        for cell, expected in item[8]:
            try:
                actual_id = builtins.id(cell_get(cell, CellType))
            except ValueError:
                raise RuntimeError('fixture target closure became empty') from None
            need(actual_id == builtins.id(expected), 'fixture target closure value')
    need(descriptor[3][0] is descriptor[2] and descriptor[3][4] is None and
         descriptor[3][5] is None and not descriptor[3][7], 'fixture dispatcher contract')


def _fixture(new_transport, source, digest, root, capability, api, compile0, exec0, serial):
    # These original Root entries/primitives are caller-authenticated before the
    # suite is entered. Fresh root identity check precedes each raw source exec.
    api[0]()
    need(type(source) is bytes and len(source) <= 1048576 and type(digest) is str and
         sha256(source).hexdigest() == digest, 'fixture final authority source pin')
    transport = new_transport()
    module = ModuleType('_h25_field_authority_fixture_' + str(serial))
    namespace = ModuleType.__dict__['__dict__'].__get__(module, ModuleType)
    namespace.update({'__builtins__': builtins.__dict__, '__file__': '<pinned-authority-fixture>',
                      '_H25_FIELD_TRANSPORT': transport})
    code = compile0(source, '<pinned-authority-fixture>', 'exec', dont_inherit=True)
    exec0(code, namespace)
    operations = namespace['capture_authority'](root, capability, api)
    first_dict = FunctionType.__dict__['__dict__'].__get__(operations[0], FunctionType)
    descriptor = dict.__getitem__(first_dict, '_h25_caller_descriptor')
    admit_descriptor(descriptor)
    helpers = {}
    for item in descriptor[4]:
        need(type(item[1]) is CodeType, 'fixture helper original code type')
        name = item[1].co_name
        if name in ('raw_function_record', 'fresh_function', 'indexed_field_id'):
            need(name not in helpers, 'fixture helper ambiguous')
            helpers[name] = item[0]
    need(set(helpers) == {'raw_function_record', 'fresh_function', 'indexed_field_id'}, 'fixture helper closure missing')
    # Same sealed native image; transport registration was original raw capture.
    transport[2]()
    owner = transport[0][1][1]
    status = owner._field_status
    need(type(status) is BuiltinFunctionType and status.__self__ is owner, 'fixture status owner')
    return module, transport, descriptor, helpers, status


def run_collector_controls(new_transport, source, digest, root, capability, api, compile0, exec0, mode):
    expected = expectations()
    rows = []
    arm, disarm = _hook()
    for serial, case_id in enumerate(CASE_IDS):
        module = transport = descriptor = helpers = status = fn = current = None
        try:
            module, transport, descriptor, helpers, status = _fixture(
                new_transport, source, digest, root, capability, api, compile0, exec0, serial)
            fn = empty_sample()
            admit_descriptor(descriptor)
            current = helpers['raw_function_record'](fn)
            # Only this standalone fixture record is modified. Production pinned
            # expected refs and the authority's own helper records stay intact.
            if case_id.endswith('first-mismatch') or case_id.endswith('middle-mismatch') or case_id.endswith('last-mismatch'):
                index = {'collector-first-mismatch': 0, 'collector-middle-mismatch': 3,
                         'collector-last-mismatch': 6}[case_id]
                values = list(current[1])
                values[index] = object()
                current = (current[0], tuple(values)) + current[2:]
            domains = {}
            admit_descriptor(descriptor)
            if case_id == 'collector-vector-hit':
                need(helpers['fresh_function'](current, domains, False, native_fields=True) is True,
                     'fixture vector setup')
            if case_id == 'collector-legitimate-close-before-events':
                transport[3]()
            elif case_id == 'collector-native-only-close':
                close_record = transport[5][2]
                code0, closure0 = close_record[1][0], close_record[1][5]
                token_candidates = [value for name, cell in zip(code0.co_freevars, closure0)
                                    for saved_cell, value in close_record[2]
                                    if name == 'token' and cell is saved_cell]
                need(len(token_candidates) == 1, 'fixture private token source locator')
                owner = transport[0][1][1]
                closer = owner._close_fields
                need(type(closer) is BuiltinFunctionType and closer.__self__ is owner, 'fixture closer owner')
                closer(token_candidates[0])
                token_candidates = closer = owner = None
            elif case_id == 'collector-publication-drift':
                transport[0][0] = 'CLOSED'
            elif case_id in ('collector-wrapper-before-first-use', 'collector-wrong-owner-before-first-use'):
                payload = transport[0][1]
                transport[0][1] = ((lambda *args: 0),) + payload[1:] if case_id == 'collector-wrapper-before-first-use' else (payload[0], object()) + payload[2:]
                payload = None
            # This admission occurs before test audit events; fixture source-owned
            # actions below change no helper function/closure binding.
            admit_descriptor(descriptor)
            log, active = [], []
            result = error = None
            def action(label):
                active.append(status()[2])
                if case_id == 'collector-active-close-getter' and label == 'get:__code__':
                    transport[3]()
                elif case_id == 'collector-active-close-id' and label == 'id' and status()[2] == 1:
                    transport[3]()
            try:
                arm(fn, log, action)
                result = helpers['fresh_function'](current, domains, False, native_fields=True)
            except BaseException as exc:
                error = [type(exc).__name__, str(exc)]
            finally:
                disarm()
            observed = {'events': log, 'active': active, 'result': result, 'error': error,
                        'phase': transport[6][0],
                        'field_vectors': sum(type(key) is tuple and key[0] == 'function-fields' for key in domains)}
            rows.append(record(case_id, observed, expected[case_id]))
        finally:
            disarm()
            if transport is not None:
                # Restore only our controlled public fixture slot before close.
                transport[0][:] = transport[6][:]
                transport[3]()
            module = transport = descriptor = helpers = status = fn = current = action = None
    count = NORMAL_CASE_COUNT if mode == 'normal' else OPTIMIZED_CASE_COUNT
    return finish(rows, CASE_IDS, count, expected, mode)
