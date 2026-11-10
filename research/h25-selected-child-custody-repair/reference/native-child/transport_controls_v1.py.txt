"""Root-owned isolated fixture registration lifecycle, never production reset."""
import builtins
from types import FunctionType
from native_field_controls_v1 import FIELDS, _hook, empty_sample
from receipt_contract_v1 import need, record, finish

CASE_IDS = ('register-valid', 'register-duplicate', 'register-reordered',
 'register-duplicate-field', 'register-wrong-id', 'register-id-wrapper',
 'register-getter-wrapper', 'register-wrong-descriptor', 'register-wrong-type',
 'bind-before-register', 'bind-duplicate', 'close-before-register',
 'close-before-bind', 'close-twice')
NORMAL_CASE_COUNT = 14
OPTIMIZED_CASE_COUNT = 14


def expectations():
    expected = {}
    for name in CASE_IDS:
        error, phase = None, 'REGISTERED'
        if name == 'register-duplicate': error = 'Fixture primitive registration is once-only'
        elif name in ('register-reordered', 'register-duplicate-field', 'register-getter-wrapper', 'register-wrong-descriptor'):
            error, phase = 'Fixture getter identity differs', 'FAILED'
        elif name in ('register-wrong-id', 'register-id-wrapper', 'register-wrong-type'):
            error, phase = 'Fixture original primitive identity differs', 'FAILED'
        elif name == 'bind-before-register': error, phase = 'Fixture primitive binding is once-only', 'UNBOUND'
        elif name == 'bind-duplicate': error, phase = 'Fixture primitive binding is once-only', 'ACTIVE'
        elif name.startswith('close-'): phase = 'CLOSED'
        expected[name] = {'phase': phase, 'error': None if error is None else ['RuntimeError', error],
                          'field_events': 0, 'same_publication': True}
    need(len(expected) == 14, 'transport literal inventory')
    return expected


def run_transport_controls(new_transport, mode):
    expected = expectations()
    fields = tuple((name, FunctionType.__dict__[name].__get__) for name in FIELDS)
    rows = []
    arm, disarm = _hook()
    for name in CASE_IDS:
        transport = new_transport()
        slot, register0, bind0, close0, receipt0, records, publication = transport
        error = None
        event_log = []
        try:
            arm(empty_sample(), event_log)
            if name == 'bind-before-register':
                bind0()
            elif name == 'close-before-register':
                close0()
            else:
                packet, original_id, original_type = fields, builtins.id, FunctionType
                if name == 'register-reordered': packet = (fields[1], fields[0]) + fields[2:]
                elif name == 'register-duplicate-field': packet = (fields[0], fields[0]) + fields[2:]
                elif name == 'register-wrong-id': original_id = builtins.abs
                elif name == 'register-id-wrapper': original_id = lambda x: builtins.id(x)
                elif name == 'register-getter-wrapper': packet = ((FIELDS[0], lambda *args: None),) + fields[1:]
                elif name == 'register-wrong-descriptor': packet = ((FIELDS[0], FunctionType.__dict__['__defaults__'].__get__),) + fields[1:]
                elif name == 'register-wrong-type': original_type = type
                register0(packet, original_id, original_type)
                if name == 'register-duplicate': register0(fields, builtins.id, FunctionType)
                elif name == 'bind-duplicate':
                    bind0()
                    bind0()
                elif name == 'close-before-bind': close0()
                elif name == 'close-twice':
                    bind0()
                    close0()
                    close0()
        except BaseException as exc:
            error = [type(exc).__name__, str(exc)]
        finally:
            disarm()
        observed = {'phase': receipt0()['phase'], 'error': error,
                    'field_events': len(event_log), 'same_publication': slot[0] == publication[0] and slot[1] is publication[1]}
        rows.append(record(name, observed, expected[name]))
        if publication[0] in ('UNBOUND', 'REGISTERED', 'ACTIVE', 'CLOSED'):
            close0()
        transport = slot = register0 = bind0 = close0 = receipt0 = records = publication = packet = None
    return finish(rows, CASE_IDS, NORMAL_CASE_COUNT if mode == 'normal' else OPTIMIZED_CASE_COUNT, expected, mode)
