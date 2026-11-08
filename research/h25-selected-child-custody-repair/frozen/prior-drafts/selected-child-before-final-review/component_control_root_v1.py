"""Concrete finite component-control bodies; SOURCE ONLY, no execution authority.

The independently admitted fixed bootstrap loads the exact configured images,
installs only enumerated gates BEFORE capture, and calls main(). This module
never supplies a parent completion, substitutes a callback, or resets an owner.
A fresh process is required for each literal unit below. Raw actual returns or
errors are emitted before any oracle. Every intentionally uncertain descriptor
belongs to the enclosing owning parent's final process-domain teardown.
"""
import hashlib
import json
import os
import sys
import types
import epoch_schema_v5 as schema
import epoch_copy_v5 as copying
import epoch_parent_v5 as epoch
import epoch_stop_v5 as stopping
import parent_completion_v1 as parent
import parent_domain_v1 as original_domain
import group01_evidence_v1 as group01
import variant_validation_v1 as variant
import policy_parent_domain_v1 as policy
import policy_receiver_closure_v1 as policy_closure
import persistent_replay_v1 as replay
import component_receiver_closure_v1 as context_closure

CONTEXT_CONFIGURATION = None
CONTEXT_SOURCE_REVIEW = None
CONTEXT_EXECUTION_APPROVAL = None
CONTEXT_FUNDING = None
_STATE = []
_CALLBACKS = [0]
_RETAINED = []
_WRITE = os.write
_MKDIR = os.mkdir
_ARGS_GET = BaseException.__dict__['args'].__get__
_REQUIRED = parent.REQUIRED_MODULES + ('persistent_replay_v1', 'replay_receiver_closure_v1',
    'policy_parent_domain_v1', 'policy_receiver_closure_v1', 'policy_process_domain_v1',
    'component_receiver_closure_v1', 'component_control_root_v1',
    'configured_inverse_v2', 'selected_child_bindings_v1')
MAX_OUTPUT_BYTES = 2 * 1024 * 1024
MAX_EVENTS = 8192
MAX_EVENT_BYTES = 1024 * 1024


class ControlStop(RuntimeError):
    pass


class OpaquePrimary(Exception):
    pass


class ForeignValue:
    def __hash__(self):
        _CALLBACKS[0] += 1
        return 17

    def __eq__(self, other):
        _CALLBACKS[0] += 1
        return False

    def __str__(self):
        _CALLBACKS[0] += 1
        return 'foreign'

    def __len__(self):
        _CALLBACKS[0] += 1
        return 0

    def __iter__(self):
        _CALLBACKS[0] += 1
        return iter(())


class ListSubclass(list):
    pass


class DictSubclass(dict):
    pass


class TupleSubclass(tuple):
    pass


class StringSubclass(str):
    pass


class IntSubclass(int):
    pass


def _foreign_callable():
    _CALLBACKS[0] += 1
    return False


def _need(condition, message):
    if condition is not True:
        raise ControlStop(message)


def _wire(value, depth=0):
    """Bounded type-preserving observation, never executable capability data."""
    _need(depth <= 32, 'raw observer depth bound')
    kind = type(value)
    if value is None:
        return ['none']
    if kind is bool:
        return ['bool', value]
    if kind is int:
        _need(-(1 << 128) < value < (1 << 128), 'raw observer integer bound')
        return ['int', value]
    if kind is str:
        _need(len(value) <= 8192, 'raw observer string bound')
        return ['str', value]
    if kind is bytes:
        _need(len(value) <= 2097152, 'raw observer bytes bound')
        # Full bytes stay in original owned raw files; hash is an observation,
        # never a substitute for the independently retained byte custody.
        return ['bytes', len(value), hashlib.sha256(value).hexdigest()]
    if kind is list or kind is tuple:
        _need(len(value) <= 4096, 'raw observer sequence bound')
        return ['list' if kind is list else 'tuple', [_wire(x, depth + 1) for x in value]]
    if kind is dict:
        _need(len(value) <= 1024 and all(type(k) is str for k in value), 'raw observer mapping domain')
        return ['dict', [[key, _wire(value[key], depth + 1)] for key in sorted(value)]]
    if kind is object:
        return ['opaque-process-local-object-not-authority']
    if kind is epoch.ParentEpoch:
        return ['original-registered-ParentEpoch-not-serializable']
    if kind is schema.ErrorOwner:
        return ['original-ErrorOwner-not-serializable']
    raise ControlStop('foreign outcome cannot be serialized by observer')


def _emit(kind, target, payload):
    state = _STATE[0]
    _need(state['events'] < MAX_EVENTS and _WRITE is os.write, 'raw observer capacity/primitive differs')
    event = {'schema': 'h25-component-control-event-v1', 'unit_id': state['unit'],
             'mode': state['mode'], 'ordinal': state['events'], 'kind': kind,
             'target': target, 'payload': payload}
    raw = (json.dumps(event, sort_keys=True, separators=(',', ':'), ensure_ascii=True) + '\n').encode('ascii')
    _need(len(raw) <= MAX_EVENT_BYTES and state['bytes'] + len(raw) <= MAX_OUTPUT_BYTES,
          'raw observer original stdout bound exceeded')
    # Only inherited stdout. No open, new FD, repair, projection of foreign
    # exceptions, or post-quarantine source acquisition is performed here.
    offset = 0
    calls = 0
    while offset < len(raw):
        calls += 1
        _need(calls <= 4096, 'raw observer write call bound')
        written = _WRITE(1, raw[offset:offset + 65536])
        _need(type(written) is int and 0 < written <= min(65536, len(raw) - offset),
              'raw observer no-progress/foreign write')
        offset += written
    state['digest'].update(raw)
    state['events'] += 1
    state['bytes'] += len(raw)


def _returned(target, value, facts=None):
    _RETAINED.append((target, value, None))
    _STATE[0]['last_raw'] = _STATE[0]['events']
    _emit('RAW_RETURN', target, {'value': _wire(value), 'facts': _wire(facts)})
    return value


def _raised(target, error, facts=None):
    _RETAINED.append((target, None, error))
    _STATE[0]['last_raw'] = _STATE[0]['events']
    kind = type(error)
    label = None
    for typ, name in ((schema.EpochStop, 'epoch_schema_v5.EpochStop'),
                      (RuntimeError, 'builtins.RuntimeError'), (MemoryError, 'builtins.MemoryError'),
                      (OSError, 'builtins.OSError'), (FileExistsError, 'builtins.FileExistsError'),
                      (FileNotFoundError, 'builtins.FileNotFoundError'),
                      (InterruptedError, 'builtins.InterruptedError'),
                      (OpaquePrimary, 'component_control_root_v1.OpaquePrimary')):
        if kind is typ:
            label = name
            break
    _need(label is not None, 'unexpected typed exception retained; no success oracle')
    args = _ARGS_GET(error, BaseException) if kind is not OpaquePrimary else ()
    _emit('RAW_RAISE', target, {'exception_type': label, 'args': _wire(args), 'facts': _wire(facts)})


def _message(error):
    if error is None:
        return None
    args = _ARGS_GET(error, BaseException)
    return args[0] if type(args) is tuple and len(args) == 1 and type(args[0]) is str else None


def _oracle(name, condition, facts):
    # This call always follows the corresponding _returned/_raised emitter.
    _need(condition is True, 'literal control oracle failed: ' + name)
    _need(type(_STATE[0]['last_raw']) is int, 'oracle lacks prior raw observation')
    _emit('ORACLE', name, {'raw_ordinal': _STATE[0]['last_raw'], 'facts': _wire(facts)})


def _context():
    _need(not _STATE, 'one source-fixed component unit per process')
    schema.exact(CONTEXT_CONFIGURATION, ('schema', 'unit_id', 'mode', 'receiver_policy',
        'fixture_directory', 'epoch_export_directory', 'raw_fixture', 'parent_plan'))
    c = CONTEXT_CONFIGURATION
    _need(c['schema'] == 'h25-component-fixed-context-v1', 'context schema')
    schema.text(c['unit_id'], 128)
    schema.choice(c['mode'], ('normal', 'optimized'))
    _need(sys.flags.optimize == (0 if c['mode'] == 'normal' else 1), 'actual child mode differs')
    schema.path(c['fixture_directory'])
    schema.path(c['epoch_export_directory'])
    schema.blob(c['receiver_policy'], schema.RECORD_BYTES)
    schema.blob(c['parent_plan'], schema.RECORD_BYTES)
    schema.blob(c['raw_fixture'], schema.RECORD_BYTES)
    for gate, label in ((CONTEXT_SOURCE_REVIEW, 'CONTEXT_SOURCE_REVIEW'),
                        (CONTEXT_EXECUTION_APPROVAL, 'CONTEXT_EXECUTION_APPROVAL'),
                        (CONTEXT_FUNDING, 'CONTEXT_FUNDING')):
        _need(type(gate) is tuple and len(gate) == 2 and type(gate[0]) is str and gate[0] == label,
              'component context independently admitted gate absent')
        schema.digest(gate[1])
    state = {'unit': c['unit_id'], 'mode': c['mode'], 'events': 0, 'bytes': 0,
             'digest': hashlib.sha256(), 'errors': schema.make_error_owner(),
             'closure': None, 'modules': None, 'parent': None, 'epoch': None,
             'authority': None, 'input_raw': None, 'fault_armed': False, 'last_raw': None}
    _STATE.append(state)
    modules = {name: sys.modules[name] for name in _REQUIRED}
    _need(all(type(x) is types.ModuleType for x in modules.values()), 'actual exact modules required')
    policy_bytes = copying.read_verified(c['receiver_policy'], schema.RECORD_BYTES, error_owner=state['errors'])
    source_policy = schema.decode(policy_bytes)
    schema.exact(source_policy, _REQUIRED)
    _need(modules['component_control_root_v1'] is sys.modules[__name__], 'fixed root module identity')
    state['modules'] = modules
    policy._gate()
    policy_plan_raw = copying.read_verified(policy.CONFIGURATION[state['mode']], schema.RECORD_BYTES, error_owner=state['errors'])
    policy_plan = schema.decode(policy_plan_raw)
    state['closure'] = context_closure.bind_receivers(modules, source_policy, state['errors'], policy_plan['configuration_profile'])
    state['input_raw'] = copying.read_verified(c['raw_fixture'], schema.RECORD_BYTES, error_owner=state['errors'])
    _guard()
    _emit('CONTEXT_BOUND', 'original-source-closure', _wire({'module_count': len(modules),
        'receiver_policy': c['receiver_policy'], 'input_raw': c['raw_fixture']}))
    return state


def _guard():
    state = _STATE[0]
    context_closure.check_receivers(state['closure'])
    copying.verify(CONTEXT_CONFIGURATION['raw_fixture'], schema.RECORD_BYTES, error_owner=state['errors'])


def _make_parent():
    state = _STATE[0]
    _need(state['parent'] is None and state['epoch'] is None, 'parent setup is one-shot')
    _guard()
    c = CONTEXT_CONFIGURATION
    _need(c['parent_plan'] == parent.CONFIGURATION['plans'][state['mode']], 'independent parent plan binding')
    raw = copying.read_verified(c['parent_plan'], schema.RECORD_BYTES, error_owner=state['errors'])
    plan = group01.decode(raw)
    parent._validate_plan(plan)
    _need(plan['mode'] == state['mode'], 'parent fixture actual mode')
    _MKDIR(c['epoch_export_directory'], 0o700)
    authority = object()  # Only the original constructor can register this authority.
    created = epoch.ParentEpoch(authority, plan['epoch_id'], state['mode'], c['epoch_export_directory'],
        [plan['producers'][role]['epoch_plan'] for role in schema.PRODUCERS])
    state['authority'], state['epoch'] = authority, created
    _returned('epoch.ParentEpoch', created, {'original_private_keys': len(epoch._entry_state(created, authority))})
    _oracle('epoch-original21', len(epoch._entry_state(created, authority)) == 21, {'keys': 21})
    owner = parent.make_parent(created, authority, {name: state['modules'][name] for name in parent.REQUIRED_MODULES})
    state['parent'] = owner
    _returned('parent.make_parent', owner)
    _oracle('real-parent-ready', parent._state(owner)['phase'] == 'READY', {'phase': parent._state(owner)['phase']})
    return owner


def _variant_seed():
    """Real fresh two-producer launch/accept, no supplied Popen or completion."""
    owner = _make_parent()
    for role in schema.PRODUCERS:
        joined = parent.run_producer(owner, role)
        _returned('parent.run_producer:' + role, joined)
        record = parent.accept_producer(owner, joined)
        _returned('parent.accept_producer:' + role, record)
        _oracle('accepted-owned-producer:' + role,
                parent._state(owner)['runs'][role]['phase'] == 'ACCEPTED', {'role': role})
    state = parent._state(owner)
    run = state['runs']['failure_variants']
    expected = group01.decode(group01.encode(run['plan']['evidence_plan']))
    expected['producer_process_id'] = run['root'][0]
    expected['parent_file_limits'] = list(run['file_limits'])
    files, pins = {}, []
    for relative in parent.VARIANT_FILES:
        limit = 8388608 if relative.endswith('.so') else schema.LOG_BYTES if relative.endswith('.raw') else schema.RECORD_BYTES
        pin = copying.inspect(run['plan']['output'] + '/' + relative, limit, error_owner=state['errors'])
        files[relative] = copying.read_verified(pin, limit, error_owner=state['errors'])
        pins.append(pin)
    result = variant.validate_variant_producer(files, expected)
    _returned('variant.validate_variant_producer:authentic-baseline', result)
    _oracle('variant-authentic26-13-2', len(files) == 26 and
            result['raw_group_relatives'] == list(parent.VARIANT_GROUPS) and len(result['builds']) == 2 and
            result['zero_candidate_loads'] is True and result['not_runtime_authority'] is True,
            {'actual_files': len(files), 'actual_groups': len(result['raw_group_relatives']),
             'actual_builds': len(result['builds']), 'pins': pins})
    return files, expected, pins


def _variant_reject(files, expected, label, message):
    error = None
    try:
        result = variant.validate_variant_producer(files, expected)
    except BaseException as caught:
        error = caught
        _raised('variant.validate_variant_producer:' + label, caught)
    else:
        _returned('variant.validate_variant_producer:' + label, result)
    _oracle(label, type(error) is RuntimeError and _message(error) == message,
            {'expected_first_rejection': message, 'actual_first_rejection': _message(error) if error is not None else None})


def _variant_preserved(pins):
    for pin in pins:
        copying.verify(pin, schema.FILE_BYTES, error_owner=_STATE[0]['errors'])
    _guard()
    _oracle('original-variant-files-retained', True, {'verified_pin_count': len(pins)})


def variant_positive():
    files, expected, pins = _variant_seed()
    # Entire authentic receiver was actually called above, preserving all of
    # its original build/journal/source/ABI/ELF predicates and first failures.
    _variant_preserved(pins)


def variant_helper_types():
    files, expected, pins = _variant_seed()
    _MKDIR(CONTEXT_CONFIGURATION['fixture_directory'], 0o700)
    for role in variant.ROLES:
        key = role + '/helper-return.raw.json'
        actual = variant.decode(files[key])
        changes = [('returncode', False), ('direct_child_reaped', 1), ('single_thread_before_spawn.task_count', True)]
        for field, altered in changes:
            changed = variant.decode(files[key])
            if field == 'single_thread_before_spawn.task_count':
                _need(type(changed['single_thread_before_spawn']['task_count']) is int and
                      changed['single_thread_before_spawn']['task_count'] == 1, 'genuine one-thread baseline absent')
                changed['single_thread_before_spawn']['task_count'] = altered
            else:
                changed[field] = altered
            retained_tag = role + '-' + field.replace('.', '-')
            _variant_probe(files, expected, pins, [(key, variant.canonical(changed))],
                role + '/' + field, 'actual return/attempt/journal differ', retained_tag=retained_tag)
    _variant_preserved(pins)


def variant_float_domain():
    files, expected, pins = _variant_seed()
    values = (0.0, 1.0, -0.0, 1e300, float('nan'), float('inf'), -float('inf'))
    for index, value in enumerate(values):
        same = variant._same(value, value)
        _returned('variant._same:float-' + str(index), same)
        _oracle('float-comparator-' + str(index), same is False, {'native_float_rejected': same is False})
        error = None
        try:
            result = variant.plain({'value': value})
        except BaseException as caught:
            error = caught
            _raised('variant.plain:float-' + str(index), caught)
        else:
            _returned('variant.plain:float-' + str(index), result)
        _oracle('float-plain-' + str(index), type(error) is RuntimeError and _message(error) == 'plain exact container required',
                {'first_rejection': _message(error)})
    for raw in (b'0.0', b'1.0', b'-0.0', b'1e300', b'NaN', b'Infinity', b'-Infinity'):
        error = None
        try:
            result = variant.decode(raw)
        except BaseException as caught:
            error = caught
            _raised('variant.decode:noninteger', caught, {'input': raw})
        else:
            _returned('variant.decode:noninteger', result)
        _oracle('float-json', type(error) is RuntimeError and _message(error) == 'noninteger JSON number is forbidden',
                {'first_rejection': _message(error)})
    _variant_preserved(pins)


def variant_structural_domain():
    files, expected, pins = _variant_seed()
    pairs = (([1, 2], (1, 2)), ({'x': 1}, {}), ({'x': 1}, {'x': 1, 'y': 2}),
             ({'x': 1}, {'y': 1}), ([1, 2], [2, 1]), ((1, 2), (2, 1)),
             (b'a', b'b'), (b'a', b'aa'), ((1 << 64), (1 << 64)),
             (-(1 << 64) - 1, -(1 << 64) - 1), ([None] * 1025, [None] * 1025))
    for index, (left, right) in enumerate(pairs):
        actual = variant._same(left, right)
        _returned('variant._same:structure-' + str(index), actual)
        _oracle('structure-' + str(index), actual is False, {'actual': actual})
    deep = None
    for unused in range(25):
        deep = [deep]
    actual = variant._same(deep, deep)
    _returned('variant._same:depth25', actual)
    _oracle('depth25', actual is False, {'actual': actual})
    for valid in (-(1 << 64), (1 << 64) - 1):
        actual = variant._same(valid, valid)
        _returned('variant._same:integer-edge-valid', actual)
        _oracle('integer-valid-edge', actual is True, {'value': valid})
    _variant_preserved(pins)


def variant_foreign_domain():
    files, expected, pins = _variant_seed()
    foreign = ForeignValue()
    foreign_key = {foreign: 1}
    setup_callbacks = _CALLBACKS[0]
    values = (foreign, ListSubclass([1]), DictSubclass({'x': 1}), TupleSubclass((1,)),
              StringSubclass('x'), IntSubclass(1), _foreign_callable, foreign_key, {'x': foreign})
    for index, value in enumerate(values):
        before = _CALLBACKS[0]
        actual = variant._same(value, value)
        after = _CALLBACKS[0]
        _returned('variant._same:foreign-' + str(index), actual, {'callbacks_before': before, 'callbacks_after': after})
        _oracle('foreign-' + str(index), actual is False and after == before,
                {'actual': actual, 'callback_delta': after - before, 'setup_callbacks': setup_callbacks})
    before = _CALLBACKS[0]
    error = None
    try:
        result = variant.plain(foreign_key)
    except BaseException as caught:
        error = caught
        _raised('variant.plain:foreign-key', caught, {'callback_delta': _CALLBACKS[0] - before})
    else:
        _returned('variant.plain:foreign-key', result)
    _oracle('foreign-key-before-hash', type(error) is RuntimeError and
            _message(error) == 'plain foreign key' and _CALLBACKS[0] == before,
            {'first_rejection': _message(error), 'callback_delta': _CALLBACKS[0] - before})
    _variant_preserved(pins)


def variant_budgets():
    files, expected, pins = _variant_seed()
    # Allocation is real and charged; repeated byte leaves are explicit shared
    # references, while the comparator charges each visited occurrence.
    deep = None
    for unused in range(25):
        deep = [deep]
    values = ([list(range(64)) for unused in range(1024)], ['x' * 8192] * 65,
              [b'x' * 8388608] * 3, deep)
    names = ('paired-node', 'text-total', 'bytes-total', 'depth')
    for name, value in zip(names, values):
        actual = variant._same(value, value)
        _returned('variant._same:budget-' + name, actual)
        _oracle('budget-' + name, actual is False, {'actual': actual})
    _variant_preserved(pins)


def error_overflow():
    owner = schema.make_error_owner()
    errors = []
    for index in range(65):
        try:
            raise RuntimeError('actual delivered secondary ' + str(index))
        except RuntimeError as caught:
            errors.append(caught)
            result = schema.retain_secondary(owner, caught, 'control-overflow', None)
            _returned('schema.retain_secondary:' + str(index), result)
    state = schema.owner_state(owner)
    snapshot = schema.error_snapshot(owner)
    _returned('schema.error_snapshot:overflow', snapshot, {'first64_identity': [state[1][i] is errors[i] for i in range(64)],
        'first_overflow_identity': state[5][0] is errors[64], 'secondary_count': state[4][0]})
    _oracle('exact-overflow-retention', state[4][0] == 64 and all(state[1][i] is errors[i] for i in range(64)) and
            state[5][0] is errors[64] and snapshot['secondary_capture_incomplete'] is True,
            {'retained_first64': True, 'retained_first_overflow': True, 'incomplete': snapshot['secondary_capture_incomplete']})
    _guard()


def unicode_error_projection():
    owner = schema.make_error_owner()
    primary = RuntimeError('\U0001f642' * 256, '\U0001f680' * 256)
    errors = [RuntimeError('secondary-' + str(i)) for i in range(6)]
    schema.retain_primary(owner, primary, 'unicode-control')
    for error in errors:
        schema.retain_secondary(owner, error, 'unicode-secondary', None)
    snapshot = schema.error_snapshot(owner)
    raw = schema.canonical(snapshot)
    _returned('schema.error_snapshot:unicode', snapshot, {'encoded_bytes': len(raw)})
    state = schema.owner_state(owner)
    _oracle('unicode-literal-projection', len(raw) < stopping.STOP_BYTES and state[0][0] is primary and
            all(state[1][i] is errors[i] for i in range(6)) and snapshot['secondary_projection_omitted'] == 0 and
            snapshot['primary']['error']['exact_string_args'] == ['\U0001f642' * 256, '\U0001f680' * 256],
            {'bytes': len(raw), 'omitted': snapshot['secondary_projection_omitted']})
    _guard()


def _arm(expected_rules):
    _guard()
    copying.control_arm()
    _need(copying.CONTROL_CONFIGURATION == {'case_id': _STATE[0]['unit'], 'rules': expected_rules},
          'fault port independently configured rule set differs')
    _STATE[0]['fault_armed'] = True
    _returned('copying.control_arm', None, {'rules': expected_rules})


def _fault_facts(owner, error):
    native = schema.owner_state(owner)
    events = [list(row) for row in copying._CONTROL[4][:copying._CONTROL[5]]]
    return {'first_primary_identity': native[0][0] is error,
        'secondary_identity_indices': [next((i for i, x in enumerate(copying._CONTROL[2]) if x is value), -1)
                                       for value in native[1][:native[4][0]]],
        'error_index': next((i for i, x in enumerate(copying._CONTROL[2]) if x is error), -1),
        'events': events, 'snapshot': schema.error_snapshot(owner),
        'injected_before_native_call': True, 'spontaneous_native_failure_claimed': False}


def copy_write_fault(kind):
    directory = CONTEXT_CONFIGURATION['fixture_directory']
    _MKDIR(directory, 0o700)
    owner = schema.make_error_owner()
    rule = lambda site, error: {'site': site, 'occurrence': 1, 'kind': error}
    if kind == 'body-close':
        rules = [rule('write_once.file_fsync', 'OSERROR_EIO'), rule('write_once.close.1', 'OSERROR_EIO')]
    elif kind == 'body-two-closes':
        rules = [rule('write_once.file_fsync', 'MEMORY_ERROR'), rule('write_once.close.1', 'OSERROR_EIO'),
                 rule('write_once.close.2', 'OSERROR_EIO')]
    elif kind == 'two-closes':
        rules = [rule('write_once.close.1', 'OSERROR_EIO'), rule('write_once.close.2', 'OSERROR_EIO')]
    elif kind == 'interrupted-close':
        rules = [rule('write_once.close.1', 'INTERRUPTED_ERROR')]
    elif kind in ('file_fsync', 'directory_fsync', 'readback'):
        rules = [rule('write_once.' + kind, 'OSERROR_EIO')]
    else:
        raise ControlStop('unknown fixed copy fault body')
    _arm(rules)
    error = None
    ambient = RuntimeError('older unrelated handler')
    try:
        raise ambient
    except RuntimeError:
        try:
            result = copying.write_once(directory + '/actual-record.json', b'{"actual":1}\n', error_owner=owner)
        except BaseException as caught:
            error = caught
            facts = _fault_facts(owner, caught)
            _raised('copying.write_once:' + kind, caught, facts)
        else:
            _returned('copying.write_once:' + kind, result)
    native = schema.owner_state(owner)
    reached = [row[3] for row in copying._CONTROL[4][:copying._CONTROL[5]] if row[3] is not None]
    _oracle('copy-fault-exact-first-and-all-sites', error is copying._CONTROL[2][0] and error is not ambient and
            native[0][0] is error and reached == list(range(len(rules))),
            {'reached_rule_indices': reached, 'primary_is_rule0': error is copying._CONTROL[2][0]})
    for i in range(1, len(rules)):
        _oracle('copy-fault-secondary-' + str(i), any(x is copying._CONTROL[2][i] for x in native[1]),
                {'retained_rule': i})
    if 'close' in kind:
        snap = schema.error_snapshot(owner)
        _oracle('copy-close-uncertainty', snap['io_quarantined'] is True and
                snap['parent_kernel_teardown_required'] is True and snap['close_attempts'] > snap['close_confirmed'],
                {'attempts': snap['close_attempts'], 'confirmed': snap['close_confirmed']})
    # No target call, source reread, native acquisition, repair or retry follows.


def census_fault(kind):
    directory = CONTEXT_CONFIGURATION['fixture_directory']
    _MKDIR(directory, 0o700)
    setup_owner = schema.make_error_owner()
    entry_pin = copying.write_once(directory + '/entry', b'x', error_owner=setup_owner)
    owner = schema.make_error_owner()
    if kind == 'historical-memory':
        actual = copying.require_entries(directory, ('entry',), error_owner=owner)
        _returned('copying.require_entries:earlier-success', actual)
        _oracle('historical-release-observation', schema.owner_state(owner)[7][9] is True, {'io9': True})
    if kind == 'after-close-validation':
        error = None
        try:
            result = copying.require_entries(directory, ('wrong',), error_owner=owner)
        except BaseException as caught:
            error = caught
            _raised('copying.require_entries:after-close-validation', caught, schema.error_snapshot(owner))
        else:
            _returned('copying.require_entries:after-close-validation', result)
        snap = schema.error_snapshot(owner)
        _oracle('after-close-conservative-quarantine', type(error) is schema.EpochStop and
                _message(error) == 'copy root entries/custody differ' and snap['io_quarantined'] is True and
                snap['scandir_release_uses_external_premise'] is False,
                {'first_rejection': _message(error), 'snapshot': snap})
        return
    sites = [('require_entries.body', 'MEMORY_ERROR')]
    if kind == 'acquisition':
        sites = [('require_entries.scandir', 'OSERROR_EIO')]
    elif kind == 'body-close-and-fds':
        sites += [('require_entries.scandir_close.2', 'OSERROR_EIO'),
                  ('require_entries.close.1', 'OSERROR_EIO'), ('require_entries.close.2', 'OSERROR_EIO')]
    _arm([{'site': site, 'occurrence': 1, 'kind': code} for site, code in sites])
    error = None
    try:
        result = copying.require_entries(directory, ('entry',), error_owner=owner)
    except BaseException as caught:
        error = caught
        _raised('copying.require_entries:' + kind, caught, _fault_facts(owner, caught))
    else:
        _returned('copying.require_entries:' + kind, result)
    snap = schema.error_snapshot(owner)
    reached = [row[3] for row in copying._CONTROL[4][:copying._CONTROL[5]] if row[3] is not None]
    _oracle('census-first-identity-quarantine', error is copying._CONTROL[2][0] and
            schema.owner_state(owner)[0][0] is error and snap['io_quarantined'] is True and
            snap['parent_kernel_teardown_required'] is True and snap['scandir_release_uses_external_premise'] is False and
            reached == list(range(len(sites))), {'snapshot': snap, 'reached_rule_indices': reached})
    if kind == 'historical-memory':
        _oracle('historical-io9-not-release', snap['scandir_close_returned_result_unobserved'] is True and
                snap['scandir_release_uses_external_premise'] is False, {'snapshot': snap})
    elif kind == 'acquisition':
        _oracle('acquisition-pending-retained', snap['native_acquisition_pending'] is True and
                snap['possible_unreturned_native_fd'] is True, {'snapshot': snap})
    else:
        _oracle('iterator-retained-before-normal-close', snap['uncertain_scandir_owner_retained'] is True,
                {'snapshot': snap})
    # A source-fixed injection does not demonstrate native _iternext closedir.


def _replay_owner():
    modules = {name: _STATE[0]['modules'][name] for name in replay._REQUIRED}
    owner = replay.reserve_batch(modules)
    _returned('replay.reserve_batch', owner)
    _oracle('real-replay-reserved', replay._entry(owner)['phase'] == 'RESERVED', {'phase': 'RESERVED'})
    return owner


def replay_repeat_batch():
    owner = _replay_owner()
    error = None
    try:
        result = replay.reserve_batch({name: _STATE[0]['modules'][name] for name in replay._REQUIRED})
    except BaseException as caught:
        error = caught
        _raised('replay.reserve_batch:duplicate', caught)
    else:
        _returned('replay.reserve_batch:duplicate', result)
    _oracle('same-process-batch-rejected', type(error) is schema.EpochStop and
            _message(error) == 'one replay batch per owning parent; no retry' and
            replay._SHARED['primary'][0] is error and replay._SHARED['quarantine'][0] is True and
            len(replay._BATCHES) == 1, {'first_rejection': _message(error), 'batches': len(replay._BATCHES)})


def replay_duplicate_plan():
    raw = copying.read_verified(replay.CONFIGURATION['plan'], schema.RECORD_BYTES, error_owner=_STATE[0]['errors'])
    original = replay._plan(raw, replay.CONFIGURATION)
    _returned('replay._plan:authentic', original)
    for which in ('epoch', 'generation'):
        value = schema.decode(raw)
        if which == 'epoch':
            value['optimized']['epoch_id'] = value['normal']['epoch_id']
            expected = 'cross-mode epoch reuse'
        else:
            value['optimized']['actions'][0]['generation'] = value['normal']['actions'][0]['generation']
            expected = 'duplicate action or cross-mode generation reuse'
        error = None
        try:
            result = replay._plan(schema.canonical(value), replay.CONFIGURATION)
        except BaseException as caught:
            error = caught
            _raised('replay._plan:duplicate-' + which, caught)
        else:
            _returned('replay._plan:duplicate-' + which, result)
        _oracle('duplicate-plan-' + which, type(error) is schema.EpochStop and _message(error) == expected and
                len(replay._BATCHES) == 0 and len(epoch._PARENT_OWNERS) == 0,
                {'first_rejection': _message(error), 'batches': len(replay._BATCHES), 'epochs': len(epoch._PARENT_OWNERS)})
    _guard()


def replay_foreign_owner():
    for index, bad in enumerate((None, False, 1, {}, {'saved_id': 7}, object(), ForeignValue())):
        for operation in ('burn', 'capture', 'seal', 'stop'):
            before = _CALLBACKS[0]
            error = None
            try:
                if operation == 'burn':
                    result = replay.burn_action(bad, 'normal', 'unused')
                elif operation == 'capture':
                    result = replay.record_captured_return(bad, 'normal', 'unused', None)
                elif operation == 'seal':
                    result = replay.seal_audit(bad)
                else:
                    result = replay.stop_evidence(bad)
            except BaseException as caught:
                error = caught
                _raised('replay.' + operation + ':foreign-' + str(index), caught)
            else:
                _returned('replay.' + operation + ':foreign-' + str(index), result)
            message = ('unknown replay owner; serialized identity is not a capability' if type(bad) is object
                       else 'exact process-local replay owner required')
            _oracle('foreign-replay-' + operation, type(error) is schema.EpochStop and _message(error) == message and
                    _CALLBACKS[0] == before and len(replay._BATCHES) == 0,
                    {'first_rejection': _message(error), 'callback_delta': _CALLBACKS[0] - before})
    _guard()


def replay_duplicate_action(which):
    owner = _replay_owner()
    state = replay._entry(owner)
    mode = _STATE[0]['mode']
    action = state['plan'][mode]['actions'][0]['action_id']
    result = replay.burn_action(owner, mode, action)
    _returned('replay.burn_action:first', result)
    if which == 'capture':
        result = replay.record_captured_return(owner, mode, action, CONTEXT_CONFIGURATION['raw_fixture'])
        _returned('replay.record_captured_return:first', result)
    error = None
    try:
        if which == 'burn':
            result = replay.burn_action(owner, mode, action)
        else:
            result = replay.record_captured_return(owner, mode, action, CONTEXT_CONFIGURATION['raw_fixture'])
    except BaseException as caught:
        error = caught
        _raised('replay.' + which + ':duplicate', caught)
    else:
        _returned('replay.' + which + ':duplicate', result)
    expected = 'same-parent action replay' if which == 'burn' else 'capture replay or closed log'
    slots = replay.stop_evidence(owner)
    _returned('replay.stop_evidence:duplicate', None, {'primary_identity': slots[0][0] is error})
    _oracle('duplicate-action-permanent-stop', type(error) is schema.EpochStop and _message(error) == expected and
            slots[0][0] is error and state['phase'] == 'STOP' and replay._SHARED['quarantine'][0] is True,
            {'first_rejection': _message(error), 'phase': state['phase']})


def replay_bad_raw(which):
    owner = _replay_owner()
    state = replay._entry(owner)
    mode = _STATE[0]['mode']
    action = state['plan'][mode]['actions'][0]['action_id']
    result = replay.burn_action(owner, mode, action)
    _returned('replay.burn_action:raw-test', result)
    if which == 'missing':
        raw_pin = None
        expected = 'exact record type differs'
    elif which == 'foreign':
        raw_pin = ForeignValue()
        expected = 'exact record type differs'
    else:
        raw_pin = dict(CONTEXT_CONFIGURATION['raw_fixture'])
        raw_pin['sha256'] = ('0' if raw_pin['sha256'][0] != '0' else '1') + raw_pin['sha256'][1:]
        expected = 'current source/store custody differs'
    before = _CALLBACKS[0]
    error = None
    try:
        result = replay.record_captured_return(owner, mode, action, raw_pin)
    except BaseException as caught:
        error = caught
        _raised('replay.record_captured_return:' + which, caught,
                {'capture_pending_identity': state['capture_pending'][0] is raw_pin,
                 'phase': state['actions'][(mode, action)]['phase']})
    else:
        _returned('replay.record_captured_return:' + which, result)
    _oracle('raw-reference-rooted-before-rejection', type(error) is schema.EpochStop and _message(error) == expected and
            state['capture_pending'][0] is raw_pin and state['actions'][(mode, action)]['phase'] == 'CAPTURE_ATTEMPT_CONSUMED' and
            state['phase'] == 'STOP' and _CALLBACKS[0] == before,
            {'first_rejection': _message(error), 'callback_delta': _CALLBACKS[0] - before})


def replay_incomplete_audit():
    owner = _replay_owner()
    state = replay._entry(owner)
    result = replay.seal_audit(owner)
    _returned('replay.seal_audit:incomplete', result)
    _oracle('audit-denies-completion-and-resume', result['full_completion'] is False and
            result['runtime_authority'] is False and result['resume_allowed'] is False and
            all(row['phase'] == 'RESERVED' for row in state['actions'].values()),
            {'full_completion': result['full_completion'], 'runtime_authority': result['runtime_authority'],
             'resume_allowed': result['resume_allowed'], 'action_phases': [x['phase'] for x in state['actions'].values()]})
    raw = copying.read_verified(result['head'], schema.RECORD_BYTES, error_owner=_STATE[0]['errors'])
    event = schema.decode(raw)
    _returned('replay.audit-current-file', event)
    _oracle('actual-audit-record-denies-completion', event['payload']['full_completion'] is False and
            event['payload']['resume_allowed'] is False and event['runtime_authority'] is False,
            {'payload': event['payload']})
    _guard()


def policy_nominal():
    owner = _make_parent()
    modules = {name: _STATE[0]['modules'][name] for name in policy.REQUIRED_POLICY_MODULES}
    policy_owner = policy.make_policy_parent(owner, modules)
    _returned('policy.make_policy_parent', policy_owner)
    for role in policy.ROLES:
        joined = policy.run_policy(policy_owner, role)
        _returned('policy.run_policy:' + role, joined)
        observed = policy.take_policy_observation(policy_owner, joined)
        _returned('policy.take_policy_observation:' + role, observed)
        # take_policy_observation already enforces the original exact native
        # result/status/owned-domain/FD/profile/raw grammar. These explicit
        # observations retain the H/R/EOF and no-authority boundary separately.
        _oracle('policy-genuine-phases:' + role, observed['role'] == role and
                observed['release_attempted'] == (True, True) and observed['release_returned'] == (True, True) and
                observed['barrier_eof'] is True and observed['epoch_completion_minted'] is False and
                observed['full_case_or_full_caller_admission'] is False,
                {'terminal': observed['terminal'], 'helper_census': observed['helper_census'],
                 'root_census': observed['root_census'], 'release_attempted': observed['release_attempted'],
                 'release_returned': observed['release_returned'], 'barrier_eof': observed['barrier_eof']})
    _guard()


def _group01_seed():
    owner = _make_parent()
    joined = parent.run_producer(owner, 'group01')
    _returned('parent.run_producer:group01', joined)
    record = parent.accept_producer(owner, joined)
    _returned('parent.accept_producer:group01', record)
    state = parent._state(owner)
    run = state['runs']['group01']
    raw = copying.read_verified(record['raw_result'], schema.RAW_RESULT_BYTES, error_owner=state['errors'])
    return owner, state, run, group01.decode(raw), raw


def parent_unknown_owners():
    for index, bad in enumerate((None, False, 1, {}, {'status': 'PASS'}, object(), ForeignValue(), _foreign_callable)):
        for name in ('run', 'accept', 'commit', 'stop'):
            before = _CALLBACKS[0]
            error = None
            try:
                if name == 'run':
                    result = parent.run_producer(bad, 'group01')
                elif name == 'accept':
                    result = parent.accept_producer(bad, object())
                elif name == 'commit':
                    result = parent.commit_exports(bad)
                else:
                    result = parent.stop_evidence(bad)
            except BaseException as caught:
                error = caught
                _raised('parent.' + name + ':unknown-' + str(index), caught)
            else:
                _returned('parent.' + name + ':unknown-' + str(index), result)
            expected = 'unregistered parent completion owner' if type(bad) is object else 'exact parent capability required'
            _oracle('unknown-parent-' + name, type(error) is schema.EpochStop and _message(error) == expected and
                    _CALLBACKS[0] == before and not parent._PARENTS,
                    {'first_rejection': _message(error), 'callbacks': _CALLBACKS[0] - before})
    _guard()


def parent_bad_run(which):
    owner = _make_parent()
    joined = parent.run_producer(owner, 'group01')
    _returned('parent.run_producer:real-group01', joined)
    state = parent._state(owner)
    if which == 'foreign-process':
        bad = state['runs']['group01']['process']
        expected = 'joined original producer capability required'
    elif which == 'unknown':
        bad = object()
        expected = 'unknown or replayed producer completion'
    else:
        record = parent.accept_producer(owner, joined)
        _returned('parent.accept_producer:first', record)
        bad = joined
        expected = 'joined original producer capability required'
    error = None
    try:
        result = parent.accept_producer(owner, bad)
    except BaseException as caught:
        error = caught
        _raised('parent.accept_producer:' + which, caught)
    else:
        _returned('parent.accept_producer:' + which, result)
    evidence = parent.stop_evidence(owner)
    _returned('parent.stop_evidence:' + which, None, {'primary_identity': evidence[0][0] is error,
        'summary': evidence[3], 'actual_stop_write_attempted': state['stop_write_attempted']})
    _oracle('parent-invalid-run-stops', type(error) is schema.EpochStop and _message(error) == expected and
            evidence[0][0] is error and state['phase'] == 'STOP',
            {'first_rejection': _message(error), 'phase': state['phase']})


def parent_premature_commit():
    owner = _make_parent()
    error = None
    try:
        result = parent.commit_exports(owner)
    except BaseException as caught:
        error = caught
        _raised('parent.commit_exports:premature', caught)
    else:
        _returned('parent.commit_exports:premature', result)
    evidence = parent.stop_evidence(owner)
    _returned('parent.stop_evidence:premature', None, {'primary_identity': evidence[0][0] is error})
    _oracle('only-actual-accepted-producers-export', type(error) is schema.EpochStop and
            _message(error) == 'only two genuinely accepted producer records may export' and
            evidence[0][0] is error and parent._state(owner)['next'] == 0,
            {'first_rejection': _message(error), 'accepted_producers': parent._state(owner)['next']})


def parent_repeated_stop():
    owner = _make_parent()
    state = parent._state(owner)
    first = OpaquePrimary('original primary')
    later = OpaquePrimary('later primary')
    result = parent._stop(state, 'first-delivered-control', first)
    _returned('parent._stop:first', result, {'first_identity': state['stop'][0] is first,
        'write_attempted': state['stop_write_attempted'], 'stop_pin': state['stop_file']})
    pin = state['stop_file']
    _need(pin is not None and state['stop_write_attempted'] is True, 'first real STOP writer did not complete')
    result = parent._stop(state, 'later-delivered-control', later)
    _returned('parent._stop:repeat', result, {'first_identity': state['stop'][0] is first,
        'secondary_identity': state['fallback'][4] is later, 'same_stop_pin_identity': state['stop_file'] is pin})
    evidence = parent.stop_evidence(owner)
    _returned('parent.stop_evidence:repeat', None, {'first_identity': evidence[0][0] is first,
        'secondary_identity': evidence[2][4] is later})
    _oracle('STOP-writer-at-most-once', evidence[0][0] is first and evidence[2][4] is later and
            state['stop_file'] is pin and state['stop_write_attempted'] is True,
            {'retained_original_pin': pin, 'first_identity': evidence[0][0] is first})
    # The original function's consumed attempt precedes write_once. No second
    # native writer is possible; exact retained pin is re-read by outer parent.


def parent_scalar_envelope(which):
    owner, state, run, original, original_raw = _group01_seed()
    directory = CONTEXT_CONFIGURATION['fixture_directory']
    _MKDIR(directory, 0o700)
    fields = ('original_controls', 'v2_controls', 'modified_helper_invocations') if which == 'helper' else (
        'original_controls', 'micro_repetitions')
    values = (False, 0.0) if which == 'helper' else (128.0, True)
    first = ('original runtime/ordered-complement independent projection differs' if which == 'helper' else
             'original native independent outcome projection differs')
    for index, value in enumerate(values):
        changed = group01.decode(original_raw)
        row = changed
        for key in fields[:-1]:
            row = row[key]
        row[fields[-1]] = value
        altered_stdout = group01.encode(changed)
        target_dir = directory + '/altered-' + str(index)
        _MKDIR(target_dir, 0o700)
        receipt_pin = copying.write_once(target_dir + '/receipt.json', altered_stdout, error_owner=state['errors'])
        finite_pin = copying.write_once(target_dir + '/finite-controls.json',
            group01.encode(changed['original_controls']), error_owner=state['errors'])
        _returned('actual-three-consistent-projections', None, {'receipt': receipt_pin, 'finite': finite_pin,
            'stdout_sha256': schema.sha(altered_stdout), 'altered_native_type': 'bool' if type(value) is bool else 'float'})
        error = None
        try:
            result = group01.authenticate_group01(target_dir, run['plan']['evidence_plan'], run['root'][0],
                run['file_limits'], state['receivers'], state['errors'], altered_stdout)
        except BaseException as caught:
            error = caught
            _raised('group01.authenticate_group01:' + which + '-' + str(index), caught)
        else:
            _returned('group01.authenticate_group01:' + which + '-' + str(index), result)
        _oracle('new-scalar-envelope-' + str(index), type(error) is schema.EpochStop and _message(error) == first,
                {'expected_first_rejection': first, 'actual_first_rejection': _message(error)})
    changed = group01.decode(original_raw)
    row = changed
    for key in fields[:-1]:
        row = row[key]
    row[fields[-1]] = ForeignValue()
    before = _CALLBACKS[0]
    error = None
    try:
        result = group01._legacy_controls(changed, run['plan']['evidence_plan']['legacy_outcomes'])
    except BaseException as caught:
        error = caught
        _raised('group01._legacy_controls:foreign-native-value', caught)
    else:
        _returned('group01._legacy_controls:foreign-native-value', result)
    _oracle('foreign-native-scalar-before-callback', type(error) is schema.EpochStop and _message(error) == first and
            _CALLBACKS[0] == before, {'first_rejection': _message(error), 'callback_delta': _CALLBACKS[0] - before})
    _guard()


def parent_expected_types():
    owner, state, run, original, original_raw = _group01_seed()
    base = run['plan']['evidence_plan']
    paths = (('stage_sha256',), ('root_sha256',), ('driver_sha256',), ('reference_driver_sha256',),
             ('generation',), ('hashlib_origin',), ('legacy_outcomes', 'original_fixture_sha256'))
    for path in paths:
        for kind in ('bool', 'float', 'foreign'):
            expected = group01.decode(group01.encode(base))
            row = expected
            for key in path[:-1]:
                row = row[key]
            row[path[-1]] = False if kind == 'bool' else 0.0 if kind == 'float' else ForeignValue()
            before = _CALLBACKS[0]
            error = None
            try:
                result = group01.authenticate_group01(run['plan']['output'], expected, run['root'][0],
                    run['file_limits'], state['receivers'], state['errors'], original_raw)
            except BaseException as caught:
                error = caught
                _raised('group01.authenticate_group01:expected-' + '/'.join(path) + '-' + kind, caught)
            else:
                _returned('group01.authenticate_group01:expected-' + '/'.join(path) + '-' + kind, result)
            _oracle('independent-expected-native-type', type(error) is schema.EpochStop and
                    _message(error) == 'exact text/limit type differs' and _CALLBACKS[0] == before,
                    {'field': list(path), 'first_rejection': _message(error), 'callback_delta': _CALLBACKS[0] - before})
    _guard()


def policy_gate_values(which):
    raw = copying.read_verified(policy.CONFIGURATION[_STATE[0]['mode']], schema.RECORD_BYTES,
        error_owner=_STATE[0]['errors'])
    profile = schema.decode(raw)['configuration_profile']
    for key in policy_closure._CONFIGURED_GATE_NAMES:
        expected_digest = profile['gate_digests'][key]
        value = (key, expected_digest)
        actual = policy_closure._configured_gate(value, key, expected_digest)
        _returned('policy_closure._configured_gate:valid-' + key, actual)
        _oracle('configured-valid-' + key, actual == value and type(actual) is tuple, {'actual': list(actual)})
        if which == 'content':
            variants = [(('wrong-label', expected_digest), 'configured receiver gate label differs'),
                ((key, 'A' * 64), 'sha256 differs'), ((key, 'a' * 63), 'sha256 differs'),
                ((key, 'a' * 65), 'text bound exceeded'),
                ((key, ('0' if expected_digest[0] != '0' else '1') + expected_digest[1:]),
                 'configured receiver gate admission differs')]
        else:
            variants = [(None, 'configured receiver gate tuple shape differs'),
                ([key, expected_digest], 'configured receiver gate tuple shape differs'),
                ((), 'configured receiver gate tuple shape differs'),
                ((key,), 'configured receiver gate tuple shape differs'),
                ((key, expected_digest, 'extra'), 'configured receiver gate tuple shape differs'),
                (TupleSubclass((key, expected_digest)), 'configured receiver gate tuple shape differs'),
                ((StringSubclass(key), expected_digest), 'exact text/limit type differs'),
                ((ForeignValue(), expected_digest), 'exact text/limit type differs'),
                ((key, ForeignValue()), 'exact text/limit type differs')]
        for index, (bad, expected) in enumerate(variants):
            before = _CALLBACKS[0]
            error = None
            try:
                result = policy_closure._configured_gate(bad, key, expected_digest)
            except BaseException as caught:
                error = caught
                _raised('policy_closure._configured_gate:' + key + '-' + str(index), caught)
            else:
                _returned('policy_closure._configured_gate:' + key + '-' + str(index), result)
            _oracle('configured-exact-rejection', type(error) is schema.EpochStop and _message(error) == expected and
                    _CALLBACKS[0] == before, {'first_rejection': _message(error), 'callback_delta': _CALLBACKS[0] - before})
    if which == 'shape':
        bad_key = {ForeignValue(): None}
        candidates = [(DictSubclass(profile), 'exact record type differs'),
            (bad_key, 'foreign record key rejected'),
            ({'schema': profile['schema'], 'gate_digests': profile['gate_digests'], 'extra': 1}, 'exact record keys differ'),
            ({'schema': profile['schema']}, 'exact record keys differ'),
            ({'schema': 'unsupported', 'gate_digests': profile['gate_digests']}, 'configured receiver profile schema differs')]
        for index, (bad, expected) in enumerate(candidates):
            before = _CALLBACKS[0]
            error = None
            try:
                result = policy_closure._configuration_profile(bad)
            except BaseException as caught:
                error = caught
                _raised('policy_closure._configuration_profile:' + str(index), caught)
            else:
                _returned('policy_closure._configuration_profile:' + str(index), result)
            _oracle('profile-native-domain', type(error) is schema.EpochStop and _message(error) == expected and
                    _CALLBACKS[0] == before, {'first_rejection': _message(error), 'callback_delta': _CALLBACKS[0] - before})
    _guard()


def epoch_existing_stop():
    owner = _make_parent()
    state = _STATE[0]
    original_epoch = state['epoch']
    authority = state['authority']
    native_owner = epoch._entry_state(original_epoch, authority)['_error_owner']
    path = CONTEXT_CONFIGURATION['epoch_export_directory'] + '/STOP.json'
    initial = copying.write_once(path, b'original existing STOP bytes\n', error_owner=native_owner)
    primary = OpaquePrimary('actual target primary')
    outward = None
    try:
        try:
            raise primary
        except OpaquePrimary:
            original_epoch._failed('control-existing-stop', primary)
            raise
    except OpaquePrimary as caught:
        outward = caught
        _raised('ParentEpoch._failed:existing-STOP', caught)
    unused, original_state = epoch._registered_parent(original_epoch)
    fallback = original_state['_failure_fallback'][1]
    _returned('ParentEpoch.stop_evidence:retained', None, {'primary_identity': original_state['_stop'][1] is primary,
        'writer_failure_is_FileExistsError': type(fallback) is FileExistsError, 'original_stop_pin': initial})
    _oracle('existing-STOP-primary-and-writer-separated', outward is primary and original_state['_stop'][1] is primary and
            type(fallback) is FileExistsError, {'primary_identity': outward is primary,
            'writer_failure_type': 'FileExistsError' if type(fallback) is FileExistsError else 'different'})
    # Original acquire failure latches uncertainty. Outer owner re-reads the
    # pre-existing STOP after this child exits; this child does not reacquire.


def parent_stage_fault(which):
    owner = _make_parent()
    state = parent._state(owner)
    if which == 'acquire-memory':
        pairs = [('parent.stage.acquire', 'MEMORY_ERROR')]
    elif which == 'acquire-absent':
        pairs = [('parent.stage.acquire', 'FILE_NOT_FOUND')]
    elif which == 'close-only':
        pairs = [('parent.stage.close', 'OSERROR_EIO')]
    elif which == 'body-and-close':
        pairs = [('parent.stage.stat', 'MEMORY_ERROR'), ('parent.stage.close', 'OSERROR_EIO')]
    else:
        _need(which in ('count', 'name', 'path', 'stat', 'files_append'), 'unknown stage body site')
        pairs = [('parent.stage.' + which, 'MEMORY_ERROR')]
    _arm([{'site': site, 'occurrence': 1, 'kind': kind} for site, kind in pairs])
    error = None
    try:
        result = parent.run_producer(owner, 'group01')
    except BaseException as caught:
        error = caught
        selected = [list(row) for row in copying._CONTROL[4][:copying._CONTROL[5]] if row[3] is not None]
        _raised('parent.run_producer:stage-' + which, caught, {'selected_fault_events': selected,
            'first_primary_identity': state['unknown_owner']['primary'][0] is caught,
            'quarantine': state['unknown_owner']['quarantine'][0],
            'pending': state['unknown_owner']['pending'][0],
            'iterator_uncertain': state['unknown_owner']['iterator_uncertain'][0],
            'all_instrumented_site_visits': copying._CONTROL[5]})
    else:
        _returned('parent.run_producer:stage-' + which, result)
    stop = parent.stop_evidence(owner)
    _returned('parent.stop_evidence:stage-' + which, None, {'primary_identity': stop[0][0] is error,
        'summary': stop[3], 'stop_write_attempted': state['stop_write_attempted']})
    reached = [row[3] for row in copying._CONTROL[4][:copying._CONTROL[5]] if row[3] is not None]
    _oracle('parent-stage-fault-reached-and-retained', error is copying._CONTROL[2][0] and
            stop[0][0] is error and state['unknown_owner']['primary'][0] is error and
            state['unknown_owner']['quarantine'][0] is True and state['stop_write_attempted'] is False and
            reached == list(range(len(pairs))) and not any(row['spawn_entered'] for row in stop[3]),
            {'reached_rule_indices': reached, 'spawn_entered': [x['spawn_entered'] for x in stop[3]],
             'stop_write_attempted': state['stop_write_attempted']})
    if which in ('acquire-memory', 'acquire-absent'):
        _oracle('constructor-stage-pending-not-cleared', state['unknown_owner']['pending'][0] is True,
                {'pending': state['unknown_owner']['pending'][0]})
    else:
        _oracle('stage-iterator-uncertainty-kept', state['unknown_owner']['iterator_uncertain'][0] is True,
                {'iterator_uncertain': state['unknown_owner']['iterator_uncertain'][0]})
    if len(pairs) == 2:
        _oracle('stage-close-secondary-exact', state['fallback'][3] is copying._CONTROL[2][1],
                {'close_secondary_identity': state['fallback'][3] is copying._CONTROL[2][1]})


def parent_early_constructor_fault():
    state = _STATE[0]
    c = CONTEXT_CONFIGURATION
    _need(c['parent_plan'] == parent.CONFIGURATION['plans'][state['mode']], 'independent parent plan binding')
    raw = copying.read_verified(c['parent_plan'], schema.RECORD_BYTES, error_owner=state['errors'])
    plan = group01.decode(raw)
    parent._validate_plan(plan)
    _MKDIR(c['epoch_export_directory'], 0o700)
    authority = object()
    original_epoch = epoch.ParentEpoch(authority, plan['epoch_id'], state['mode'], c['epoch_export_directory'],
        [plan['producers'][role]['epoch_plan'] for role in schema.PRODUCERS])
    state['epoch'], state['authority'] = original_epoch, authority
    _returned('epoch.ParentEpoch:before-constructor-fault', original_epoch)
    _arm([{'site': 'parent.constructor.before_plan_read', 'occurrence': 1, 'kind': 'MEMORY_ERROR'}])
    modules = {name: state['modules'][name] for name in parent.REQUIRED_MODULES}
    first = None
    try:
        result = parent.make_parent(original_epoch, authority, modules)
    except BaseException as caught:
        first = caught
        _raised('parent.make_parent:before-publication', caught, {'published_owners': len(parent._PARENTS),
            'shared_primary_identity': parent._UNKNOWN_OWNER['primary'][0] is caught,
            'quarantine': parent._UNKNOWN_OWNER['quarantine'][0]})
    else:
        _returned('parent.make_parent:before-publication', result)
    _oracle('constructor-owner-preexists-failure', first is copying._CONTROL[2][0] and not parent._PARENTS and
            parent._UNKNOWN_OWNER['primary'][0] is first and parent._UNKNOWN_OWNER['quarantine'][0] is True,
            {'published_owners': len(parent._PARENTS), 'exact_primary_identity': first is copying._CONTROL[2][0]})
    visits = copying._CONTROL[5]
    later = None
    try:
        result = parent.make_parent(original_epoch, authority, modules)
    except BaseException as caught:
        later = caught
        _raised('parent.make_parent:after-unpublished-failure', caught)
    else:
        _returned('parent.make_parent:after-unpublished-failure', result)
    _oracle('no-second-constructor-configuration-read', type(later) is schema.EpochStop and
            _message(later) == 'earlier constructor failure prohibits configuration reads' and
            parent._UNKNOWN_OWNER['primary'][0] is first and copying._CONTROL[5] == visits,
            {'first_rejection': _message(later), 'new_instrumented_sites': copying._CONTROL[5] - visits})


def parent_owned_native_flag(which):
    owner = _make_parent()
    state = parent._state(owner)
    original = epoch._entry_state(state['epoch'], state['authority'])
    native = schema.owner_state(original['_error_owner'])
    _need(any(row is native for row in state['unknown_owner']['native_errors']), 'genuine native owner was not attached')
    # This is a finite explicit state fault on a genuinely constructed owner,
    # not a replacement object, fabricated capability or native-failure claim.
    if which in ('0', '1', '2', '4', '6', '10', '11'):
        native[7][int(which)] = True
    elif which == 'overflow':
        native[5][1] = True
    elif which == 'close-overflow':
        native[7][7][:] = [0, 0, 0, 0, 1]
    elif which == 'iterator':
        directory = CONTEXT_CONFIGURATION['fixture_directory']
        _MKDIR(directory, 0o700)
        iterator = os.scandir(directory)
        native[7][5] = iterator
    else:
        raise ControlStop('undeclared original-owner state fault')
    native[7][9] = True  # Historical normal-close indication must not override.
    error = None
    try:
        result = parent.run_producer(owner, 'group01')
    except BaseException as caught:
        error = caught
        _raised('parent.run_producer:owned-native-flag-' + which, caught, {
            'original_native_owner_attached': any(row is native for row in state['unknown_owner']['native_errors']),
            'quarantine': state['unknown_owner']['quarantine'][0], 'historical_io9': native[7][9]})
    else:
        _returned('parent.run_producer:owned-native-flag-' + which, result)
    stop = parent.stop_evidence(owner)
    _returned('parent.stop_evidence:owned-native-flag-' + which, None, {
        'primary_identity': stop[0][0] is error, 'run_count': len(state['runs']),
        'stop_write_attempted': state['stop_write_attempted']})
    _oracle('original-native-flags-block-acquisition', type(error) is schema.EpochStop and
            _message(error) == 'parent I/O ownership requires kernel teardown' and
            state['unknown_owner']['quarantine'][0] is True and stop[0][0] is error and
            not state['runs'] and state['stop_write_attempted'] is False and native[7][9] is True,
            {'first_rejection': _message(error), 'run_count': len(state['runs']), 'stop_writer': state['stop_write_attempted']})


def parent_metadata_absence():
    owner = _make_parent()
    state = parent._state(owner)
    domain_owner = original_domain.create_domain(state['unknown_owner'])
    _returned('original_domain.create_domain', domain_owner)
    domain_state = original_domain._state(domain_owner)
    absent = original_domain._proc((1 << 31) - 1, domain_state)
    _returned('original_domain._proc:metadata-absence', absent,
        {'acquisition_in_flight': domain_state['acquisition_in_flight'],
         'pending': state['unknown_owner']['pending'][0], 'quarantine': state['unknown_owner']['quarantine'][0]})
    _oracle('metadata-only-absence-before-open', absent is None and domain_state['acquisition_in_flight'] is False and
            state['unknown_owner']['pending'][0] is False and state['unknown_owner']['quarantine'][0] is False,
            {'observed_none': absent is None, 'acquisition_in_flight': domain_state['acquisition_in_flight']})
    result = original_domain.finish_domain(domain_owner)
    _returned('original_domain.finish_domain:empty-owned-domain', result)
    _guard()


def _original_build_copy(row, independent, destination, scenario):
    """Copy authentic owned packet; original files stay immutable and pinned.

    Relocation changes only path references required by the original parser.
    A separate unaltered relocated packet is accepted before each negative.
    No compiler/process/source mutation or new native fault port is introduced.
    """
    errors = _STATE[0]['errors']
    parser = group01.original_build
    receipt = parser._decode_original(copying.read_verified(row['original_receipt'], 65536, error_owner=errors), 65536)
    attempt = parser._decode_original(copying.read_verified(row['attempt'], 65536, error_owner=errors), 65536)
    journal_raw = copying.read_verified(row['journal'], schema.JOURNAL_BYTES, error_owner=errors)
    _need(journal_raw.endswith(b'\n') and len(journal_raw.splitlines()) == 3, 'authentic journal triple required')
    events = [parser._decode_original(line, 65536) for line in journal_raw.splitlines()]
    stdout = copying.read_verified(row['stdout'], schema.LOG_BYTES, error_owner=errors)
    stderr = copying.read_verified(row['stderr'], schema.LOG_BYTES, error_owner=errors)
    _MKDIR(destination, 0o700)
    paths = {name: destination + '/' + name for name in ('attempt', 'journal', 'receipt')}
    # Keep genuine stdout/stderr pins and origins, including empty logs: the
    # original write_once API deliberately refuses zero-length records.
    paths.update(stdout=row['stdout']['path'], stderr=row['stderr']['path'])
    receipt['attempt_path'], receipt['attempt_journal_path'] = paths['attempt'], paths['journal']
    for name in ('stdout', 'stderr'):
        receipt[name]['path'] = paths[name]
    for event in events + [attempt]:
        for name in ('stdout', 'stderr', 'attempt', 'journal'):
            event[name + '_path'] = paths[name]
        if 'logs' in event:
            for name in ('stdout', 'stderr'):
                event['logs'][name]['path'] = paths[name]
    if scenario == 'J01':
        events[0]['extra'] = None
    elif scenario == 'J02':
        events[1]['extra'] = None
    elif scenario in ('J03', 'J04', 'J05'):
        for event in events[1:] + [attempt]:
            census = event['single_thread_before_spawn']
            if scenario == 'J03':
                census['task_count'] = True
            elif scenario == 'J04':
                census['task_ids'] = [independent['producer_process_id']] * 2
            else:
                wrong = 1 if independent['producer_process_id'] != 1 else 2
                census['process_id'], census['task_ids'] = wrong, [wrong]
    elif scenario in ('J06', 'J07'):
        limits = [1, 1] if scenario == 'J06' else [33554432, 33554432]
        if limits == independent['parent_file_limits']:
            limits = [67108864, 67108864]
        for event in events[1:] + [attempt]:
            event['parent_file_limits_before'] = list(limits)
            if 'parent_file_limits_after' in event:
                event['parent_file_limits_after'] = list(limits)
    elif scenario == 'J08':
        wrong = '0' * 64 if independent['preexec_code_sha256'] != '0' * 64 else '1' * 64
        for event in events[1:] + [attempt]:
            event['preexec_code_sha256'] = wrong
    elif scenario == 'J09':
        _need(type(receipt['stdout']['bytes_before']) is int and receipt['stdout']['bytes_before'] == 0,
              'J09 requires genuinely empty original compiler stdout')
        receipt['stdout']['bytes_before'] = False
    elif scenario == 'J10':
        _need(type(events[-1]['logs']['stdout']['bytes_before']) is int and
              events[-1]['logs']['stdout']['bytes_before'] == 0,
              'J10 requires genuinely empty original compiler stdout')
        events[-1]['logs']['stdout']['bytes_before'] = False
    else:
        _need(scenario == 'baseline', 'unknown original journal scenario')
    copied = schema.plain_copy(row)
    for name, raw in (('attempt', schema.canonical(attempt)),
                      ('journal', b''.join(schema.canonical(event) + b'\n' for event in events)),
                      ('original_receipt', schema.canonical(receipt))):
        path_name = 'receipt' if name == 'original_receipt' else name
        copied[name] = copying.write_once(paths[path_name], raw, error_owner=errors)
        _returned('original-build-input-custody:' + scenario + ':' + name, None,
                  {'input_pin': copied[name], 'original_pin': row[name]})
    return copied


def original_journal_fault(scenario):
    owner, state, run, original, original_raw = _group01_seed()
    directory = CONTEXT_CONFIGURATION['fixture_directory']
    _MKDIR(directory, 0o700)
    parser = group01.original_build
    expected_errors = {'J01': 'exact record keys differ', 'J02': 'exact record keys differ',
        'J03': 'exact integer type differs', 'J04': 'exact sequence count differs',
        'J05': 'original producer thread identity differs', 'J06': 'inherited file limit below original cap',
        'J07': 'independent inherited limits differ', 'J08': 'independent preexec bytecode pin differs',
        'J09': 'complete original raw log/preview differs', 'J10': 'original final journal/attempt differs'}
    for index, (row, build_plan) in enumerate(zip(run['record']['builds'], run['plan']['evidence_plan']['builds'])):
        _need(row['role'] == build_plan['role'], 'authentic original role order differs')
        independent = schema.plain_copy(build_plan['expected_original'])
        independent['producer_process_id'] = run['root'][0]
        independent['parent_file_limits'] = list(run['file_limits'])
        baseline = _original_build_copy(row, independent, directory + '/baseline-' + str(index), 'baseline')
        actual = parser.authenticate_original_build(baseline, independent, error_owner=state['errors'])
        _returned('original_build.authenticate_original_build:relocated-positive', actual)
        _oracle('relocation-preserves-original-parser', actual['role'] == row['role'] and
                actual['not_runtime_authority'] is True, {'role': row['role'], 'scenario': scenario})
        changed = _original_build_copy(row, independent, directory + '/negative-' + str(index), scenario)
        error = None
        try:
            actual = parser.authenticate_original_build(changed, independent, error_owner=state['errors'])
        except BaseException as caught:
            error = caught
            _raised('original_build.authenticate_original_build:' + scenario + ':' + row['role'], caught,
                    {'altered_row': changed, 'expected_from_parent_plan': independent})
        else:
            _returned('original_build.authenticate_original_build:' + scenario + ':' + row['role'], actual)
        _oracle('original-journal-exact-reached-predicate', type(error) is schema.EpochStop and
                _message(error) == expected_errors[scenario], {'scenario': scenario, 'role': row['role'],
                'expected_first_rejection': expected_errors[scenario], 'actual_first_rejection': _message(error)})
        for key in ('original_output', 'original_receipt', 'attempt', 'journal', 'stdout', 'stderr'):
            copying.verify(row[key], schema.FILE_BYTES, error_owner=state['errors'])
        _guard()


def _variant_probe(files, expected, pins, changes, label, message, retained_tag=None):
    """Persist complete changed byte witnesses before actual receiver call."""
    root = CONTEXT_CONFIGURATION['fixture_directory']
    tag = label
    if retained_tag is not None:
        _need(type(retained_tag) is str and 1 <= len(retained_tag) <= 128 and
              all(c in 'abcdefghijklmnopqrstuvwxyz0123456789_-' for c in retained_tag),
              'source-fixed retained input tag differs')
        tag = retained_tag
    destination = root + '/' + tag
    _MKDIR(destination, 0o700)
    changed_files = dict(files)
    witnesses = []
    for index, (relative, raw) in enumerate(changes):
        _need(type(relative) is str and type(raw) is bytes, 'fixed native mutation domain')
        pin = copying.write_once(destination + '/input-' + str(index), raw, error_owner=_STATE[0]['errors'])
        changed_files[relative] = raw
        witnesses.append({'relative': relative, 'pin': pin})
    _returned('variant-input-custody:' + label, None, {'changed_bytes': witnesses,
        'original_pin_count': len(pins), 'originals_unchanged': True})
    _variant_reject(changed_files, expected, label, message)
    _variant_preserved(pins)


def variant_inventory_domain():
    files, expected, pins = _variant_seed()
    _MKDIR(CONTEXT_CONFIGURATION['fixture_directory'], 0o700)
    key = 'root-before.raw.json'
    # Exact JSON duplicate handling precedes the original counter predicates.
    _variant_probe(files, expected, pins, [(key, b'{"load_calls":0,"load_calls":0}')],
                   'duplicate-key', 'duplicate JSON key')
    for relative, raw, label in ((key, b'[]', 'wrong-top-type'),
                                (key, b'{"x":1.0}', 'noninteger-json')):
        _variant_probe(files, expected, pins, [(relative, raw)], label,
                       'exact record required' if label == 'wrong-top-type' else 'noninteger JSON number is forbidden')
    for relative in variant.RAW_INVENTORY:
        altered = dict(files)
        del altered[relative]
        _returned('variant-input-inventory:missing', None, {'missing': relative, 'original_pin_count': len(pins)})
        _variant_reject(altered, expected, 'missing-' + relative, 'record key census differs')
    _variant_probe(files, expected, pins, [('extra-unaccepted.raw.json', b'{}')],
                   'extra-file', 'record key census differs')
    _variant_preserved(pins)


def variant_journal_fields():
    files, expected, pins = _variant_seed()
    _MKDIR(CONTEXT_CONFIGURATION['fixture_directory'], 0o700)
    for role in variant.ROLES:
        key = role + '/control.attempt.jsonl'
        original = [variant.decode(line) for line in files[key].splitlines()]
        _need(len(original) == 3, 'authentic original triple required')
        variants = ('extra-prelaunch', 'extra-started', 'bool-task-count', 'wrong-task-list',
                    'wrong-census-pid', 'wrong-limits', 'wrong-preexec', 'wrong-final-logs',
                    'missing-tail', 'missing-event', 'wrong-order')
        for label in variants:
            events = [variant.decode(line) for line in files[key].splitlines()]
            message = 'record key census differs'
            if label == 'extra-prelaunch':
                events[0]['extra'] = None
            elif label == 'extra-started':
                events[1]['extra'] = None
            elif label == 'bool-task-count':
                events[1]['single_thread_before_spawn']['task_count'] = True
                message = 'producer census differs'
            elif label == 'wrong-task-list':
                events[1]['single_thread_before_spawn']['task_ids'] *= 2
                message = 'producer census differs'
            elif label == 'wrong-census-pid':
                pid = expected['producer_process_id']
                events[1]['single_thread_before_spawn']['process_id'] = 1 if pid != 1 else 2
                message = 'producer census differs'
            elif label == 'wrong-limits':
                events[1]['parent_file_limits_before'] = [1, 1]
                message = 'inherited limits or preexec source differ'
            elif label == 'wrong-preexec':
                events[1]['preexec_code_sha256'] = '0' * 64 if expected['preexec_code_sha256'] != '0' * 64 else '1' * 64
                message = 'inherited limits or preexec source differ'
            elif label == 'wrong-final-logs':
                events[-1]['logs']['stdout']['preview_utf8'] += 'changed'
                message = 'actual return/attempt/journal differ'
            elif label == 'missing-event':
                events.pop()
                message = 'original successful journal must contain exactly three events'
            elif label == 'wrong-order':
                events[0], events[1] = events[1], events[0]
            else:
                message = 'original journal bound or tail differs'
            raw = b''.join(variant.canonical(event) + b'\n' for event in events)
            if label == 'missing-tail':
                raw = raw[:-1]
            _variant_probe(files, expected, pins, [(key, raw)], role + '-' + label, message)


def variant_initial_fields():
    files, expected, pins = _variant_seed()
    _MKDIR(CONTEXT_CONFIGURATION['fixture_directory'], 0o700)
    key = 'initial-controls.raw.json'
    for label in ('wrong-order', 'missing-record', 'wrong-rejection', 'side-effect'):
        data = variant.decode(files[key])
        if label == 'wrong-order':
            data['records'][1], data['records'][2] = data['records'][2], data['records'][1]
            message = 'initial five order differs'
        elif label == 'missing-record':
            data['records'].pop()
            message = 'initial five count differs'
        elif label == 'wrong-rejection':
            data['records'][1]['rejection'] = 'wrong rejection witness'
            message = 'original rejection differs'
        else:
            data['records'][3]['corrupt_function_executed'] = True
            message = 'initial control side effect boundary differs'
        _variant_probe(files, expected, pins, [(key, variant.canonical(data))], label, message)
    data = variant.decode(files['initial-restoration.raw.json'])
    data['hash_function_id'] = data['hash_function_id'] + 1
    _variant_probe(files, expected, pins, [('initial-restoration.raw.json', variant.canonical(data))],
                   'restoration-function-identity', 'fresh restoration continuity differs')


def variant_root_fields():
    files, expected, pins = _variant_seed()
    _MKDIR(CONTEXT_CONFIGURATION['fixture_directory'], 0o700)
    for role in ('before', 'after'):
        key = 'root-' + role + '.raw.json'
        for counter in variant.COUNTERS:
            for label in ('nonzero', 'missing', 'bool'):
                data = variant.decode(files[key])
                if label == 'missing':
                    del data[counter]
                else:
                    data[counter] = False if label == 'bool' else 1
                _variant_probe(files, expected, pins, [(key, variant.canonical(data))],
                    role + '-' + counter + '-' + label,
                    'record key census differs' if label == 'missing' else 'Root native event occurred')


def variant_forged_authority():
    files, expected, pins = _variant_seed()
    _MKDIR(CONTEXT_CONFIGURATION['fixture_directory'], 0o700)
    for field in ('parent_completion', 'domain_closed', 'failure_helper_qualification'):
        for value, label in ((True, 'bool'), ({'status': 'PASS'}, 'mapping')):
            data = variant.decode(files['receipt.json'])
            data[field] = value
            _variant_probe(files, expected, pins, [('receipt.json', variant.canonical(data))],
                field + '-' + label, 'final producer binding differs')


def variant_duplicate_types():
    files, expected, pins = _variant_seed()
    _MKDIR(CONTEXT_CONFIGURATION['fixture_directory'], 0o700)
    # Real duplicate observations: mutate only their duplicate in receipt.json.
    # The original independently validated counterpart remains byte-identical.
    for phase in ('before', 'after'):
        for counter in variant.COUNTERS:
            data = variant.decode(files['receipt.json'])
            _need(type(data['root_' + phase][counter]) is int and data['root_' + phase][counter] == 0,
                  'genuine zero-counter duplicate absent')
            data['root_' + phase][counter] = False
            _variant_probe(files, expected, pins, [('receipt.json', variant.canonical(data))],
                phase + '-' + counter, 'final Root counters differ')
    data = variant.decode(files['receipt.json'])
    _need(type(data['candidate_loads']) is int and data['candidate_loads'] == 0, 'genuine zero-load duplicate absent')
    data['candidate_loads'] = False
    _variant_probe(files, expected, pins, [('receipt.json', variant.canonical(data))],
                   'candidate-loads-bool', 'final producer binding differs')


def component_close_fault(operation):
    """Existing Python close ports around real files; no native delivery claim."""
    directory = CONTEXT_CONFIGURATION['fixture_directory']
    _MKDIR(directory, 0o700)
    setup = schema.make_error_owner()
    source = copying.write_once(directory + '/source', b'actual original bytes\n', error_owner=setup)
    _returned('copying.write_once:source-setup', source)
    owner = schema.make_error_owner()
    rules = [{'site': operation + '.close.1', 'occurrence': 1, 'kind': 'OSERROR_EIO'},
             {'site': operation + '.close.2', 'occurrence': 1, 'kind': 'INTERRUPTED_ERROR'}]
    _arm(rules)
    error = None
    ambient = RuntimeError('older unrelated target handler')
    try:
        raise ambient
    except RuntimeError:
        try:
            if operation == 'inspect':
                actual = copying.inspect(source['path'], error_owner=owner)
            elif operation == 'read_verified':
                actual = copying.read_verified(source, error_owner=owner)
            else:
                actual = copying.copy_once(source, directory + '/destination', (), error_owner=owner)
        except BaseException as caught:
            error = caught
            _raised('copying.' + operation + ':known-closes', caught, _fault_facts(owner, caught))
        else:
            _returned('copying.' + operation + ':known-closes', actual)
    native = schema.owner_state(owner)
    close_events = [row for row in copying._CONTROL[4][:copying._CONTROL[5]]
                    if row[0].startswith(operation + '.close.')]
    expected_close_sites = [operation + '.close.' + str(i)
                            for i in range(1, 5 if operation == 'copy_once' else 3)]
    descriptors = [row[2] for row in close_events]
    reached = [row[3] for row in copying._CONTROL[4][:copying._CONTROL[5]] if row[3] is not None]
    snapshot = schema.error_snapshot(owner)
    _oracle('known-close-first-is-local-not-ambient', error is copying._CONTROL[2][0] and error is not ambient and
            native[0][0] is error and any(x is copying._CONTROL[2][1] for x in native[1]) and
            reached == [0, 1] and [row[0] for row in close_events] == expected_close_sites and
            all(type(fd) is int and fd >= 0 for fd in descriptors) and
            len(descriptors) == len(set(descriptors)) and
            snapshot['close_attempts'] == snapshot['close_confirmed'] + 2 and
            snapshot['io_quarantined'] is True and
            snapshot['parent_kernel_teardown_required'] is True,
            {'operation': operation, 'reached_rules': reached, 'snapshot': snapshot,
             'known_close_sites': expected_close_sites, 'known_descriptor_tokens': descriptors,
             'native_failure_claimed': False, 'full_target_capture_context': False})
    # Uncertain FDs remain for authentic outer process teardown. No source read,
    # verification, new acquisition, retry or repair follows this oracle.


def _native_before(owner, mode, case):
    """Register actual original slots before the fixed native operation.

    This function belongs to the same source-authenticated fixed root as the
    delivery body. The actual _native_prepare call constructs owner through
    schema.make_error_owner; a copied dictionary is not an input to this API.
    The opaque token never crosses the process boundary or becomes a receipt.
    """
    state = _STATE[0]
    record = state['native_case']
    _need(record['phase'] == 'PREPARED' and record['setup_status'] == ['SETUP_SUCCEEDED'] and
          record['setup_pending'] == [False] and record['setup_error'] == [None] and
          record['owner'] is owner and
          record['mode'] == mode == state['mode'] and record['case'] == case == state['unit'],
          'native observer original construction/context differs')
    _need(case in ('epoch-v4/C03/native-enoent', 'epoch-v4/C03/native-eexist',
                   'epoch-v4/C03/native-eloop'), 'unimplemented native observer case')
    _need(sys.flags.optimize == (0 if mode == 'normal' else 1),
          'native observer actual Python mode differs')
    original = schema.owner_state(owner)
    _need(original[0] == [None, None, None] and original[4] == [0, 0, 0, 0] and
          original[5] == [None, False] and all(x is None for x in original[1]) and
          all(x is None for x in original[2]) and all(x is None for x in original[3]),
          'native observer requires the fresh original owner')
    io = original[7]
    _need(all(io[i] is False for i in (0, 1, 2, 4, 6, 9, 10, 11)) and
          io[3] is None and io[5] is None and io[12] is None and
          io[7] == [0, 0, 0, 0, 0] and io[8] == [0, 0, 0, 0, 0],
          'native observer owner already has custody history')
    _need(type(record['caught']) is list and record['caught'] == [None] and
          type(record['returned']) is list and record['returned'] == [None],
          'native observer outcome slots already occupied')
    # Capture the actual original native descriptors before any target I/O.
    # They are used only after an exact whitelisted native exception type test.
    errno_get = OSError.__dict__['errno'].__get__
    filename_get = OSError.__dict__['filename'].__get__
    token = object()
    record['observer'] = [token, False, original, original[0], original[1],
                          original[2], original[3], original[4], original[5], io,
                          record['caught'], record['returned'], errno_get, filename_get]
    record['phase'] = 'REGISTERED'
    return token


def _native_observe(token, caught_slot):
    """Read actual held operands; return observations without a PASS marker.

    Original operation cleanup has completed before this function is entered.
    Its possibly allocating work cannot precede or replace known-FD cleanup.
    No source reread, native acquisition, retry, target call, or error protocol
    of an arbitrary object occurs here. All opaque objects stay strongly held.
    """
    state = _STATE[0]
    record = state['native_case']
    saved = record['observer']
    _need(record['phase'] == 'RETURNED' and saved[0] is token and saved[1] is False and
          caught_slot is saved[10] is record['caught'],
          'native observation stale/foreign/replayed/early token')
    saved[1] = True  # Consume before fallible observation; never restore.
    original = schema._OWNER_GET(record['owner'], schema.ErrorOwner)
    _need(original is saved[2] and all(original[i] is saved[j] for i, j in
          ((0, 3), (1, 4), (2, 5), (3, 6), (4, 7), (5, 8), (7, 9))),
          'actual original owner slots were replaced')
    error = caught_slot[0]
    io = saved[9]
    primary, secondary, phases, uncertain = saved[3], saved[4], saved[5], saved[6]
    counts, overflow = saved[7], saved[8]
    kind = type(error)
    label = 'UNSUPPORTED_OR_NO_NATIVE_ERROR'
    actual_errno = actual_filename = None
    if kind is FileNotFoundError:
        label = 'builtins.FileNotFoundError'
    elif kind is FileExistsError:
        label = 'builtins.FileExistsError'
    elif kind is OSError:
        label = 'builtins.OSError'
    if label != 'UNSUPPORTED_OR_NO_NATIVE_ERROR':
        actual_errno = saved[12](error, OSError)
        actual_filename = saved[13](error, OSError)
    attempts = io[7][0] + (io[7][1] << 8) + (io[7][2] << 16) + (io[7][3] << 24) + (io[7][4] << 32)
    confirmed = io[8][0] + (io[8][1] << 8) + (io[8][2] << 16) + (io[8][3] << 24) + (io[8][4] << 32)
    # Each field below is a read from an actual retained object or source-owned
    # control transition. No expected value is copied into an observed slot.
    facts = {
        'schema': 'h25-native-acquisition-observation-v1',
        'case_id': record['case'], 'mode': record['mode'], 'path': record['path'],
        'site': 'epoch_copy_v5.final_native_open', 'occurrence': 1, 'role': 'NO_ROLE',
        'native_error_type': label, 'native_errno': actual_errno,
        'native_filename': actual_filename, 'primary_phase': primary[1],
        'first_primary_is_outward': primary[0] is error and error is not None,
        'first_acquisition_is_outward': io[3] is error and error is not None,
        'outward_is_older_ambient': error is record['ambient'],
        'secondary_count': counts[0],
        'secondary_occupied': [x is not None for x in secondary],
        'secondary_phases': list(phases), 'uncertain_fd_slots': list(uncertain),
        'primary_uncertain_fd': primary[2],
        'close_attempts': attempts, 'close_confirmed_returns': confirmed,
        'quarantine': io[0], 'pending_acquisition': io[1],
        'possible_unreturned_fd': io[2], 'parent_kernel_teardown_required': io[4],
        'retained_iterator_present': io[5] is not None,
        'close_counter_overflow': io[6], 'historical_release_premise': io[9],
        'external_guard_acquisition_pending': io[10], 'external_guard_fd_count_unavailable': io[11],
        'error_overflow': overflow[1], 'overflow_error_present': overflow[0] is not None,
        'operation_returned_value': record['returned'][0] is not None,
        'delivery_phase': record['phase'],
        'observer_token_consumed': saved[1],
        'injected_before_native_call': False,
        'kernel_release_observed': False,
        'post_acquisition_boxing_covered': False,
        'full_family_completion': False,
    }
    record['observation'] = facts
    record['phase'] = 'OBSERVED'
    return facts

def _native_prepare(case):
    """Prepare a real private filesystem cause before original protected IO.

    The actual setup owner and a preallocated first-error slot are published
    before fallible fixture creation. Failed setup retains pending custody and
    cannot register or invoke the observed operation. No retry follows it.
    """
    state = _STATE[0]
    _need(case in ('epoch-v4/C03/native-enoent',
                   'epoch-v4/C03/native-eexist',
                   'epoch-v4/C03/native-eloop') and state['unit'] == case,
          'fixed native acquisition unit differs')
    _need('native_case' not in state and not state['fault_armed'],
          'native case replay or pre-call injection')
    _guard()
    copying._gate()
    fixture = CONTEXT_CONFIGURATION['fixture_directory']
    path = fixture + '/native-target'
    schema.path(path)
    _need(_MKDIR is os.mkdir, 'native fixture primitive differs')
    setup_owner = schema.make_error_owner()
    owner = schema.make_error_owner()
    caught = [None]
    returned = [None]
    setup_error = [None]
    setup_pending = [False]
    setup_status = [None]
    ambient = RuntimeError('older-native-case-caller-exception')
    record = {'case': case, 'mode': state['mode'], 'path': path,
              'owner': owner, 'caught': caught, 'returned': returned,
              'ambient': ambient, 'phase': 'PREPARING',
              'setup_owner': setup_owner, 'setup_blob': None,
              'setup_error': setup_error, 'setup_pending': setup_pending,
              'setup_status': setup_status}
    state['native_case'] = record
    # Pending publication precedes every fallible fixture operation. No
    # traceback or allocating failure handler is needed to root its owner.
    setup_pending[0] = True
    try:
        _MKDIR(fixture, 0o700)
        if case == 'epoch-v4/C03/native-eexist':
            # Original exclusive writer, full reread, and known-token cleanup.
            # Mode0600 plus private custody is not a read-only-file assertion.
            record['setup_blob'] = copying.write_once(
                path, b'h25-native-existing-file-v1\n', error_owner=setup_owner)
        elif case == 'epoch-v4/C03/native-eloop':
            # This actual original primitive joins the successor native profile.
            # It installs no filter, tracer, callback, or replacement.
            os.symlink(CONTEXT_CONFIGURATION['raw_fixture']['path'], path)
        # ENOENT leaves the final name absent in the exclusive private directory.
        # This last guard is still setup, before any observed acquisition.
        _guard()
    except BaseException as error:
        setup_error[0] = error
        setup_status[0] = 'SETUP_FAILED'
        # Leave pending true and phase PREPARING. No helper, source guard,
        # close retry, observer, or target operation follows this failure.
        raise
    setup_status[0] = 'SETUP_SUCCEEDED'
    setup_pending[0] = False
    record['phase'] = 'PREPARED'
    return record


def _native_invoke(record):
    """Run one unchanged original operation, then retain its actual outcome.

    The first statement in the delivered handler stores the exact outward
    exception in a preallocated None slot. There is no helper call, formatting,
    protocol conversion, new acquisition, or independent observer before it.
    Original operation cleanup has already attempted each known token once.
    """
    state = _STATE[0]
    _need(record is state['native_case'] and record['phase'] == 'REGISTERED',
          'native operation lacks one-use independent registration')
    owner = record['owner']
    path = record['path']
    case = record['case']
    caught = record['caught']
    returned = record['returned']
    ambient = record['ambient']
    record['phase'] = 'INVOKING'
    try:
        raise ambient
    except RuntimeError:
        try:
            if case == 'epoch-v4/C03/native-eexist':
                returned[0] = copying.write_once(path, b'never-overwrite-existing\n',
                                                 error_owner=owner)
            else:
                returned[0] = copying.inspect(path, schema.RECORD_BYTES,
                                              error_owner=owner)
        except BaseException as error:
            caught[0] = error
    # Known cleanup is already over. The strong root above precedes these
    # fallible bookkeeping operations. No acquisition/retry follows a failure.
    record['phase'] = 'RETURNED'


def native_acquisition_case(case):
    record = _native_prepare(case)
    ticket = _native_before(record['owner'], record['mode'], case)
    _native_invoke(record)
    facts = _native_observe(ticket, record['caught'])
    _raised('epoch_copy_v5.native_acquisition', record['caught'][0], facts)
    _oracle('native-acquisition-local-delivery',
            record['caught'][0] is not None and record['returned'][0] is None,
            {'source_owned_observer_completed': True, 'subcase_only': True,
             'family_completion': False})


def main():
    state = _context()
    unit = state['unit']
    if unit in ('epoch-v4/C03/native-enoent', 'epoch-v4/C03/native-eexist',
                'epoch-v4/C03/native-eloop'):
        native_acquisition_case(unit)
    elif unit in ('epoch-journal/J01/actual-triple', 'epoch-journal/J02/actual-triple',
                'epoch-journal/J03/actual-triple', 'epoch-journal/J04/actual-triple',
                'epoch-journal/J05/actual-triple', 'epoch-journal/J06/actual-triple',
                'epoch-journal/J07/actual-triple', 'epoch-journal/J08/actual-triple',
                'epoch-journal/J09/actual-triple', 'epoch-journal/J10/actual-triple'):
        original_journal_fault(unit.split('/')[1])
    elif unit == 'variant/V15/raw-inventory':
        variant_inventory_domain()
    elif unit == 'variant/V16/actual-journal':
        variant_journal_fields()
    elif unit == 'variant/V17/initial-five':
        variant_initial_fields()
    elif unit == 'variant/V18/root-counters':
        variant_root_fields()
    elif unit == 'variant/V22/forged-authority':
        variant_forged_authority()
    elif unit == 'variant/V27/duplicate-types':
        variant_duplicate_types()
    elif unit in ('parent-old/P13/inspect', 'parent-old/P13/read_verified', 'parent-old/P13/copy_once'):
        component_close_fault(unit.rsplit('/', 1)[1])
    elif unit in ('parent-v2/B01-01/acquire-memory', 'parent-v2/B01-01/acquire-absent',
                'parent-v2/B01-03/count', 'parent-v2/B01-03/name', 'parent-v2/B01-03/path',
                'parent-v2/B01-03/stat', 'parent-v2/B01-03/files_append',
                'parent-v2/B01-04/close-only', 'parent-v2/B01-04/body-and-close'):
        parent_stage_fault(unit.rsplit('/', 1)[1])
    elif unit == 'parent-v2/B01-11/early-constructor':
        parent_early_constructor_fault()
    elif unit in ('parent-v2/B01-10/0', 'parent-v2/B01-10/1', 'parent-v2/B01-10/2',
                  'parent-v2/B01-10/4', 'parent-v2/B01-10/6', 'parent-v2/B01-10/10',
                  'parent-v2/B01-10/11', 'parent-v2/B01-10/overflow',
                  'parent-v2/B01-10/close-overflow', 'parent-v2/B01-10/iterator'):
        parent_owned_native_flag(unit.rsplit('/', 1)[1])
    elif unit == 'parent-v2/B01-07/metadata-absence':
        parent_metadata_absence()
    elif unit == 'parent-old/P02/unknown-owners':
        parent_unknown_owners()
    elif unit in ('parent-old/P02/foreign-process', 'parent-old/P02/unknown', 'parent-old/P02/replayed'):
        parent_bad_run(unit.rsplit('/', 1)[1])
    elif unit == 'parent-old/P05/premature-commit':
        parent_premature_commit()
    elif unit == 'parent-v2/B01-14/repeated-stop':
        parent_repeated_stop()
    elif unit == 'parent-v2/B02-01/consistent-scalars':
        parent_scalar_envelope('helper')
    elif unit == 'parent-v2/B02-02/consistent-scalars':
        parent_scalar_envelope('micro')
    elif unit == 'parent-v2/B02-05/independent-types':
        parent_expected_types()
    elif unit == 'policy-b01/B01-N02/content-api':
        policy_gate_values('content')
    elif unit == 'policy-b01/B01-N03/shape-api':
        policy_gate_values('shape')
    elif unit == 'epoch-writer/W01/existing-stop':
        epoch_existing_stop()
    elif unit in ('variant/V01/nominal', 'variant/V32/authentic'):
        variant_positive()
    elif unit == 'variant/V26/helper-types':
        variant_helper_types()
    elif unit == 'variant/V28/float-domain':
        variant_float_domain()
    elif unit == 'variant/V29/structural-domain':
        variant_structural_domain()
    elif unit == 'variant/V30/foreign-domain':
        variant_foreign_domain()
    elif unit == 'variant/V33/budgets':
        variant_budgets()
    elif unit == 'epoch-old/O07/overflow':
        error_overflow()
    elif unit == 'epoch-writer/W11/unicode':
        unicode_error_projection()
    elif unit in ('epoch-old/O03/body-close', 'epoch-writer/W04/body-close'):
        copy_write_fault('body-close')
    elif unit == 'epoch-old/O04/body-two-closes':
        copy_write_fault('body-two-closes')
    elif unit in ('epoch-old/O05/two-closes', 'epoch-writer/W05/two-closes'):
        copy_write_fault('two-closes')
    elif unit == 'epoch-old/O06/interrupted-close':
        copy_write_fault('interrupted-close')
    elif unit.startswith('epoch-writer/W03/') and unit.rsplit('/', 1)[1] in ('file_fsync', 'directory_fsync', 'readback'):
        copy_write_fault(unit.rsplit('/', 1)[1])
    elif unit == 'epoch-v5/V5-C02/body-memory':
        census_fault('body-memory')
    elif unit == 'epoch-v5/V5-C04/history-memory':
        census_fault('historical-memory')
    elif unit == 'epoch-v5/V5-C05/after-close-validation':
        census_fault('after-close-validation')
    elif unit == 'epoch-v4/C03/scandir-acquisition':
        census_fault('acquisition')
    elif unit == 'epoch-v4/C04/body-close-and-fds':
        census_fault('body-close-and-fds')
    elif unit == 'replay/RP01/repeat-batch':
        replay_repeat_batch()
    elif unit == 'replay/RP05/duplicate-plan':
        replay_duplicate_plan()
    elif unit == 'replay/RP21/foreign-owner':
        replay_foreign_owner()
    elif unit in ('replay/RP22/burn', 'replay/RP22/capture'):
        replay_duplicate_action(unit.rsplit('/', 1)[1])
    elif unit in ('replay/RP23/missing', 'replay/RP23/foreign', 'replay/RP23/altered'):
        replay_bad_raw(unit.rsplit('/', 1)[1])
    elif unit == 'replay/RP29/incomplete-audit':
        replay_incomplete_audit()
    elif unit in ('policy-v2/P36/nominal', 'policy-domain/D01/nominal'):
        policy_nominal()
    else:
        raise ControlStop('unit has no implemented body; full finite union cannot pass')
    _emit('UNIT_TERMINAL', 'component-control', _wire({'status': 'IMPLEMENTED_UNIT_PASS',
        'family_completion': False, 'complete_finite_union': False,
        'prior_events': state['events'], 'prior_wire_sha256': state['digest'].hexdigest(),
        'actual_runtime_admission': False, 'gain': False}))
    return 0
