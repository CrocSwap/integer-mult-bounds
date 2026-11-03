"""Full control successor for final Root plus reviewed pure ELF v2 route.

All original 78 authentic fixture observations and 91 initial pure observations
are retained in order. The reviewed 110-case pure extension is additive. The
53 Root, two sink-close and 11 callback-projection models have separate counts.
They cannot qualify real kernel, loader or operating-system cleanup cases.
Importing this module grants no source, stage, command or runtime admission.
"""
from types import FunctionType, CellType
import native_field_controls_v1 as native
import transport_controls_v1 as transport
import collector_controls_v1 as collector
import elf_controls_v1 as elf
import provider_controls_v1 as providers
import run_pure_controls_v2 as pure
import elf_extended_controls_v2 as extension
import loader_model_controls_v3 as models
import group_evidence_v5 as evidence
import close_model_controls_v5 as close_models
import projection_model_controls_v5 as projection_models
from hashlib import sha256
from receipt_contract_v1 import need, validate

SCHEMA = 'h25-indexed-field-additive-controls-v5'
STATUS = 'SOURCE_CONTROL_OBSERVATIONS_COMPLETE_RUNTIME_GATE_OPEN'
DELIVERY_SCHEMA = 'h25-indexed-field-durable-control-delivery-v5'
NORMAL_NONMODEL_COUNT = 279
OPTIMIZED_NONMODEL_COUNT = 279
NORMAL_MODEL_COUNT = 66
OPTIMIZED_MODEL_COUNT = 66
AUTHENTIC_FIXTURE_COUNT = 78
PURE_PREDICATE_COUNT = 201
MAX_CONTEXTS = 41
LEGACY_GROUPS = ('native', 'transport', 'collector', 'elf', 'providers')
GROUPS = LEGACY_GROUPS + ('elf_extended',)
MODULES = (native, transport, collector, elf, providers, extension)

def _admit_control_transport(control_transport):
    need(type(control_transport) is tuple and len(control_transport) == 2, 'control transport exact shape')
    functions, records = control_transport
    need(type(functions) is tuple and len(functions) == 3 and type(records) is tuple and len(records) == 3,
         'control transport function census')
    getters = tuple(FunctionType.__dict__[name].__get__ for name in native.FIELDS)
    cell_get = CellType.__dict__['cell_contents'].__get__
    for target, captured in zip(functions, records):
        need(type(captured) is tuple and len(captured) == 3 and target is captured[0] and
             type(target) is FunctionType and type(captured[1]) is tuple and len(captured[1]) == 7 and
             type(captured[2]) is tuple, 'control transport original target')
        for getter, expected in zip(getters, captured[1]):
            need(id(getter(target, FunctionType)) == id(expected), 'control transport original environment')
        need(captured[1][3] is None and captured[1][4] is None, 'control transport source defaults')
        for cell, expected in captured[2]:
            try: actual_id = id(cell_get(cell, CellType))
            except ValueError: raise RuntimeError('control transport original closure empty') from None
            need(actual_id == id(expected), 'control transport original closure')
    return functions




def validate_aggregate(receipt, mode):
    need(type(mode) is str and mode in ('normal', 'optimized'), 'aggregate exact mode')
    need(type(receipt) is dict and set(receipt) == {'schema', 'status', 'mode',
        'nonmodel_observed_count', 'authentic_fixture_observed_count', 'pure_predicate_observed_count',
        'model_observed_count', 'root_model_observed_count', 'sink_close_model_observed_count', 'projection_model_observed_count',
        'native_fixture_contexts', 'groups', 'pure_v2', 'root_model', 'sink_close_model', 'projection_model',
        'kernel_capability_qualified', 'full_finite_union_qualified', 'all_202_obligations_covered',
        'required_guarded_cases_status', 'old_group_order_preserved', 'model_provenance_separately_reported'},
        'aggregate v5 exact receipt keys')
    need(receipt['schema'] == SCHEMA and receipt['status'] == STATUS and receipt['mode'] == mode,
         'aggregate v5 status/mode')
    for key in ('kernel_capability_qualified', 'full_finite_union_qualified', 'all_202_obligations_covered'):
        need(receipt[key] is False, 'aggregate v5 cannot qualify open runtime/ELF obligations')
    need(receipt['required_guarded_cases_status'] == 'REQUIRED_NOT_EXECUTED_BY_THIS_ENTRY' and
         receipt['old_group_order_preserved'] is True and receipt['model_provenance_separately_reported'] is True,
         'aggregate v5 retained scope and ordering')
    need(type(receipt['groups']) is dict and tuple(receipt['groups']) == GROUPS, 'aggregate v5 exact group order')
    for name, module in zip(LEGACY_GROUPS, MODULES[:5]):
        literal = module.NORMAL_CASE_COUNT if mode == 'normal' else module.OPTIMIZED_CASE_COUNT
        validate(receipt['groups'][name], module.CASE_IDS, literal, module.expectations(), mode)
    extension.validate_extended(receipt['groups']['elf_extended'], mode)
    pure.validate_pure(receipt['pure_v2'], mode)
    need(receipt['pure_v2']['initial']['elf'] == receipt['groups']['elf'] and
         receipt['pure_v2']['initial']['providers'] == receipt['groups']['providers'] and
         receipt['pure_v2']['extended'] == receipt['groups']['elf_extended'],
         'aggregate v5 pure group projections differ')
    models.validate_model_receipt(receipt['root_model'], mode)
    close_models.validate_model_receipt(receipt['sink_close_model'], mode)
    projection_models.validate_model_receipt(receipt['projection_model'], mode)
    for key, literal in (('nonmodel_observed_count', 279), ('authentic_fixture_observed_count', 78),
                         ('pure_predicate_observed_count', 201), ('model_observed_count', 66),
                         ('root_model_observed_count', 53), ('sink_close_model_observed_count', 2), ('projection_model_observed_count', 11),
                         ('native_fixture_contexts', 41)):
        need(type(receipt[key]) is int and receipt[key] == literal, 'aggregate v5 independent literal census')
    need(sum(receipt['groups'][key]['case_count'] for key in GROUPS[:3]) == 78 and
         sum(receipt['groups'][key]['case_count'] for key in GROUPS) == 279 and
         receipt['root_model']['observations']['case_count'] == 53 and
         receipt['sink_close_model']['observations']['case_count'] == 2 and
         receipt['projection_model']['observations']['case_count'] == 11 and
         receipt['root_model_observed_count'] + receipt['sink_close_model_observed_count'] +
             receipt['projection_model_observed_count'] == 66,
         'aggregate v5 observed census consistency')
    return receipt


class GroupControlError(RuntimeError):
    """Explicit error carrier; original exceptions and raw returned object survive."""
    def __init__(self, failure, primary, secondary=None, raw_result=None, teardown=None):
        RuntimeError.__init__(self, 'Full-control group failed: ' + failure['group'])
        self.failure = failure
        self.primary_exception = primary
        self.secondary_capture_exception = secondary
        self.raw_result = raw_result
        self.teardown_exception = teardown
        self.cleanup_receipt = None


def _error_record(exc):
    """Bounded explicit projection; foreign exception/type/args stay opaque.

    No exception name lookup, str/repr, foreign attribute lookup, hashing or
    equality occurs. Type labels are source literals selected by identity only.
    Only exact native exceptions reach the original BaseException args getter;
    only one exact str argument can become message text. The caller retains the
    actual exception object/cause independently of this intentionally partial view.
    """
    kind, label = type(exc), None
    for native_type, native_label in (
        (BaseException, 'BaseException'), (Exception, 'Exception'),
        (RuntimeError, 'RuntimeError'), (TypeError, 'TypeError'),
        (ValueError, 'ValueError'), (LookupError, 'LookupError'),
        (IndexError, 'IndexError'), (KeyError, 'KeyError'),
        (OSError, 'OSError'), (MemoryError, 'MemoryError'),
        (OverflowError, 'OverflowError'), (AssertionError, 'AssertionError'),
        (SystemExit, 'SystemExit'), (KeyboardInterrupt, 'KeyboardInterrupt'),
        (StopIteration, 'StopIteration'), (BrokenPipeError, 'BrokenPipeError'),
        (FileNotFoundError, 'FileNotFoundError'), (PermissionError, 'PermissionError'),
        (IsADirectoryError, 'IsADirectoryError'), (NotADirectoryError, 'NotADirectoryError'),
        (FileExistsError, 'FileExistsError'), (TimeoutError, 'TimeoutError'),
        (InterruptedError, 'InterruptedError')):
        if kind is native_type:
            label = native_label
            break
    if label is None:
        return {'schema': 'h25-safe-error-projection-v5', 'type': 'OPAQUE_FOREIGN_EXCEPTION',
                'type_provenance': 'OPAQUE_FOREIGN_TYPE', 'message': None,
                'message_provenance': 'OMITTED_FOREIGN_TYPE', 'message_truncated': False,
                'opaque_exception_retained_separately': True}
    arguments = BaseException.__dict__['args'].__get__(exc, BaseException)
    message, provenance, truncated = None, 'OMITTED_NON_SINGLE_STR_ARGUMENTS', False
    if type(arguments) is tuple:
        if len(arguments) == 0:
            message, provenance = '', 'EMPTY_EXACT_ARGS'
        elif len(arguments) == 1 and type(arguments[0]) is str:
            message, provenance = arguments[0][:4096], 'EXACT_STR_ARGUMENT'
            truncated = len(arguments[0]) > 4096
    return {'schema': 'h25-safe-error-projection-v5', 'type': label,
            'type_provenance': 'EXACT_NATIVE_TYPE', 'message': message,
            'message_provenance': provenance, 'message_truncated': truncated,
            'opaque_exception_retained_separately': True}


def _admit_group_sink(packet, mode, run_guard=True):
    # Records were captured by the source-admitted caller/factory before any
    # adverse group. This is an identity check, not self-authenticated provenance.
    need(type(packet) is tuple and len(packet) == 4 and packet[0] == evidence.SCHEMA,
         'full route requires original group evidence packet')
    _, functions, records, contract = packet
    need(type(functions) is tuple and len(functions) == 5 and type(records) is tuple and 5 <= len(records) <= 512 and
         tuple(row[0] for row in records[:5] if type(row) is tuple and len(row) == 3) == functions,
         'group evidence exact function packet')
    getters = tuple(FunctionType.__dict__[name].__get__ for name in native.FIELDS)
    cell_get = CellType.__dict__['cell_contents'].__get__
    seen = []
    for row in records:
        need(type(row) is tuple and len(row) == 3, 'group evidence graph row')
        function = row[0]
        need(not any(function is previous for previous in seen), 'group evidence duplicate graph function')
        seen.append(function)
        need(type(function) is FunctionType and
             type(row[1]) is tuple and len(row[1]) == 7 and type(row[2]) is tuple,
             'group evidence original function record')
        for getter, expected in zip(getters, row[1]):
            need(getter(function, FunctionType) is expected, 'group evidence original function field changed')
        for cell, expected in row[2]:
            try: actual = cell_get(cell, CellType)
            except ValueError: raise RuntimeError('group evidence original closure emptied') from None
            need(actual is expected, 'group evidence original closure changed')
    need(type(contract) is dict and set(contract) == {'schema', 'mode', 'group_order', 'raw_byte_limit',
        'total_byte_limit', 'stop_reserve_bytes', 'directory', 'directory_identity', 'parent_identity', 'function_graph_count',
        'graph_traversal', 'delegated_guard_boundary', 'cleanup_record_index',
        'exclusive_outputs', 'raw_before_outer_validation', 'caller_source_admission_required'},
        'group evidence contract exact keys')
    need(contract['schema'] == evidence.SCHEMA and contract['mode'] == mode and
         contract['group_order'] == ('native', 'transport', 'collector', 'pure_initial', 'pure_extended',
                                     'pure_combined', 'root_model', 'sink_close_model', 'projection_model', 'aggregate') and
         contract['directory'] == 'field-groups-v5' and contract['exclusive_outputs'] is True and
         contract['raw_before_outer_validation'] is True and contract['caller_source_admission_required'] is True and
         contract['graph_traversal'] == 'DIRECT_AND_IMMUTABLE_TUPLE_FUNCTION_CLOSURES' and
         contract['delegated_guard_boundary'] == 'ROW4_ORIGINAL_DISPATCH_ADMISSION_BEFORE_EVERY_OP6' and
         type(contract['cleanup_record_index']) is int and contract['cleanup_record_index'] == 3,
         'group evidence literal policy')
    for key, literal in (('raw_byte_limit', 1048576), ('total_byte_limit', 4194304), ('stop_reserve_bytes', 65536)):
        need(type(contract[key]) is int and contract[key] == literal, 'group evidence exact resource bound')
    for key in ('directory_identity', 'parent_identity'):
        need(type(contract[key]) is tuple and len(contract[key]) == 4 and all(type(value) is int for value in contract[key]),
             'group evidence exact original directory identity')
    need(type(contract['function_graph_count']) is int and contract['function_graph_count'] == len(records),
         'group evidence exact graph census')
    if run_guard:
        functions[4]()  # caller-authenticated original complete source/environment guard
    return functions


def _make_cleanup_admitter(packet):
    """Capture native admission operations before controls; no source-guard retry.

    The close closure has no Python helper call. Its native closer and holder
    are pinned by row3, so an unrelated writer/guard defect need not leak its FD.
    The caller retains this same original subset for pre-entry/outer failures.
    """
    type0, len0, tuple0, error, zip0 = type, len, tuple, RuntimeError, zip
    function_type, cell_type = FunctionType, CellType
    getters = tuple(FunctionType.__dict__[name].__get__ for name in native.FIELDS)
    cell_get = CellType.__dict__['cell_contents'].__get__
    if type0(packet) is not tuple or len0(packet) != 4:
        raise error('group evidence cleanup packet')
    functions, graph = packet[1], packet[2]
    if type0(functions) is not tuple or len0(functions) != 5 or type0(graph) is not tuple or len0(graph) < 5:
        raise error('group evidence cleanup inventory')
    original, record0 = functions[3], graph[3]
    def close_original():
        if (type0(record0) is not tuple0 or len0(record0) != 3 or original is not record0[0] or
                type0(original) is not function_type or type0(record0[1]) is not tuple0 or len0(record0[1]) != 7 or
                type0(record0[2]) is not tuple0):
            raise error('group evidence cleanup original record')
        for getter, expected in zip0(getters, record0[1]):
            if getter(original, function_type) is not expected:
                raise error('group evidence cleanup function changed')
        for cell, expected in record0[2]:
            if cell_get(cell, cell_type) is not expected:
                raise error('group evidence cleanup closure changed')
        return original()
    return close_original


def _observe_group(packet, mode, group, operation, validator):
    raw = None
    state, raw_pin = 'NOT_RETURNED', None
    try:
        raw = operation()
        state = 'RETURNED_CAPTURE_FAILED'
        sink = _admit_group_sink(packet, mode)
        raw_pin = sink[0](group, raw)  # RAW BEFORE OUTER VALIDATION
        state = 'RETURNED_CAPTURE_FAILED'
        _admit_group_sink(packet, mode)  # freshness after native-I/O/audit boundary
        state = 'RETURNED_MALFORMED'
        validator(raw)
        state = 'RETURNED_VALIDATION_EVIDENCE_FAILED'
        sink = _admit_group_sink(packet, mode)
        sink[1](group)
        return raw
    except BaseException as primary:
        failure = {'group': group, 'return_state': state, 'primary_error': _error_record(primary),
                   'raw_pin': raw_pin, 'next_group_started': False,
                   'raw_return_available_in_memory': state != 'NOT_RETURNED'}
        if type(primary) is evidence.EvidenceWriteError:
            failure['partial_output'] = primary.artifact
            failure['write_primary_error'] = _error_record(primary.primary)
            failure['write_secondary_error'] = None if primary.secondary is None else _error_record(primary.secondary)
        # Serialization/guard/IO errors cannot convert a returned malformed
        # object into NOT_RETURNED. Inner group validation failures that raise
        # before the public group returns correctly remain NOT_RETURNED.
        secondary = None
        try:
            sink = _admit_group_sink(packet, mode)
            sink[2](group, failure)
        except BaseException as capture_failure:
            secondary = capture_failure
            failure['secondary_capture_error'] = _error_record(capture_failure)
            if type(capture_failure) is evidence.EvidenceWriteError:
                failure['secondary_capture_artifact'] = capture_failure.artifact
                failure['secondary_write_primary_error'] = _error_record(capture_failure.primary)
                failure['secondary_write_cleanup_error'] = None if capture_failure.secondary is None else _error_record(capture_failure.secondary)
        raise GroupControlError(failure, primary, secondary, raw) from primary


def run_all(field_control_transport, authority_source, authority_digest, root, capability,
            api, compile0, exec0, elf_module, mode, *, group_sink):
    need(type(mode) is str and mode in ('normal', 'optimized'), 'control exact mode')
    close_original_sink = _make_cleanup_admitter(group_sink)
    made = [0]
    def new_fixture():
        _admit_control_transport(field_control_transport)
        made[0] += 1
        need(made[0] <= MAX_CONTEXTS, 'aggregate native fixture bound')
        return original_new()
    def new_transport():
        _admit_control_transport(field_control_transport)
        made[0] += 1
        need(made[0] <= MAX_CONTEXTS, 'aggregate native fixture bound')
        return original_transport()
    def check(module, receipt):
        literal = module.NORMAL_CASE_COUNT if mode == 'normal' else module.OPTIMIZED_CASE_COUNT
        return validate(receipt, module.CASE_IDS, literal, module.expectations(), mode)
    def group(name, operation, validator):
        return _observe_group(group_sink, mode, name, operation, validator)
    try:
        _admit_group_sink(group_sink, mode)  # required; no fallback or expected recapture
        original_new, original_transport, original_models = _admit_control_transport(field_control_transport)
        receipts = {}
        receipts['native'] = group('native', lambda: native.run_native_field_controls(new_fixture, mode),
                                   lambda raw: check(native, raw))
        receipts['transport'] = group('transport', lambda: transport.run_transport_controls(new_transport, mode),
                                      lambda raw: check(transport, raw))
        receipts['collector'] = group('collector', lambda: collector.run_collector_controls(new_transport, authority_source,
            authority_digest, root, capability, api, compile0, exec0, mode), lambda raw: check(collector, raw))
        initial = group('pure_initial', lambda: pure.run_initial(elf_module, mode),
                         lambda raw: pure.initial.validate_pure(raw, mode))
        receipts['elf'], receipts['providers'] = initial['elf'], initial['providers']
        extended = group('pure_extended', lambda: pure.run_extended(elf_module, mode),
                          lambda raw: extension.validate_extended(raw, mode))
        receipts['elf_extended'] = extended
        pure_receipt = group('pure_combined', lambda: pure.combine_groups(initial, extended, mode),
                              lambda raw: pure.validate_pure(raw, mode))
        def run_models():
            _admit_control_transport(field_control_transport)
            return models.run_loader_model_controls(original_models(), mode)
        model = group('root_model', run_models,
                       lambda raw: models.validate_model_receipt(raw, mode))
        close_model = group('sink_close_model', lambda: close_models.run_close_model_controls(mode),
                            lambda raw: close_models.validate_model_receipt(raw, mode))
        projection_model = group('projection_model',
            lambda: projection_models.run_projection_model_controls(evidence, _error_record, GroupControlError, mode),
            lambda raw: projection_models.validate_model_receipt(raw, mode))
        result = {'schema': SCHEMA, 'status': STATUS, 'mode': mode,
            'nonmodel_observed_count': sum(r['case_count'] for r in receipts.values()),
            'authentic_fixture_observed_count': sum(receipts[key]['case_count'] for key in GROUPS[:3]),
            'pure_predicate_observed_count': pure_receipt['observation_count'],
            'model_observed_count': model['observations']['case_count'] + close_model['observations']['case_count'] +
                projection_model['observations']['case_count'],
            'root_model_observed_count': model['observations']['case_count'],
            'sink_close_model_observed_count': close_model['observations']['case_count'],
            'projection_model_observed_count': projection_model['observations']['case_count'],
            'native_fixture_contexts': made[0], 'groups': receipts, 'pure_v2': pure_receipt,
            'root_model': model, 'sink_close_model': close_model, 'projection_model': projection_model,
            'kernel_capability_qualified': False, 'full_finite_union_qualified': False,
            'all_202_obligations_covered': False,
            'required_guarded_cases_status': 'REQUIRED_NOT_EXECUTED_BY_THIS_ENTRY',
            'old_group_order_preserved': True, 'model_provenance_separately_reported': True}
        group('aggregate', lambda: result, lambda raw: validate_aggregate(raw, mode))
    except BaseException as primary:
        cleanup_receipt, teardown = None, None
        try:
            cleanup_receipt, teardown = close_original_sink()
        except BaseException as close_failure:
            # The close closure has consumed the FD and latched this original
            # exception. The admitted outer caller may read back once without
            # another native operation; no tuple enters cleanup_receipt.
            teardown = close_failure
        if type(primary) is GroupControlError:
            primary.cleanup_receipt = cleanup_receipt
            if teardown is not None:
                primary.teardown_exception = teardown
        elif teardown is not None:
            failure = {'group': 'full-route-setup-or-between-groups', 'return_state': 'NOT_RETURNED',
                       'primary_error': _error_record(primary), 'next_group_started': False}
            wrapped = GroupControlError(failure, primary, teardown=teardown)
            wrapped.cleanup_receipt = cleanup_receipt
            raise wrapped from primary
        raise
    try:
        delivery, teardown = close_original_sink()
    except BaseException as primary:
        failure = {'group': 'sink-teardown', 'return_state': 'RETURNED_DELIVERY_TEARDOWN_FAILED',
                   'primary_error': _error_record(primary), 'next_group_started': False}
        raise GroupControlError(failure, primary, raw_result=result, teardown=primary) from primary
    if teardown is not None:
        failure = {'group': 'sink-teardown', 'return_state': 'RETURNED_DELIVERY_TEARDOWN_FAILED',
                   'primary_error': _error_record(teardown), 'next_group_started': False}
        wrapped = GroupControlError(failure, teardown, raw_result=result, teardown=teardown)
        wrapped.cleanup_receipt = delivery
        raise wrapped from teardown
    receipt = {'schema': DELIVERY_SCHEMA, 'mode': mode, 'aggregate': result, 'group_evidence': delivery}
    return validate_all(receipt, mode)


def validate_all(receipt, mode):
    need(type(receipt) is dict and set(receipt) == {'schema', 'mode', 'aggregate', 'group_evidence'} and
         receipt['schema'] == DELIVERY_SCHEMA and receipt['mode'] == mode, 'full v5 delivery envelope')
    validate_aggregate(receipt['aggregate'], mode)
    delivery = receipt['group_evidence']
    need(type(delivery) is dict and set(delivery) == {'schema', 'completed_groups', 'expected_groups', 'raw_pins',
        'validation_pins', 'stop_pin', 'reserved_bytes', 'directory_closed', 'directory_close_attempted',
        'directory_close_outcome', 'directory_close_error_present'}, 'full v5 group evidence keys')
    need(delivery['schema'] == evidence.SCHEMA and delivery['completed_groups'] == delivery['expected_groups'] == 10 and
         type(delivery['completed_groups']) is int and type(delivery['expected_groups']) is int and
         delivery['directory_closed'] is True and delivery['directory_close_attempted'] is True and
         delivery['directory_close_outcome'] == 'CONFIRMED' and delivery['directory_close_error_present'] is False and
         delivery['stop_pin'] is None and
         type(delivery['reserved_bytes']) is int and 0 < delivery['reserved_bytes'] <= 4194304 - 65536,
         'full v5 complete durable group census')
    for key in ('raw_pins', 'validation_pins'):
        rows = delivery[key]
        need(type(rows) is list and len(rows) == 10 and all(type(row) is list and len(row) == 2 for row in rows) and
             tuple(row[0] for row in rows) == evidence.GROUP_ORDER,
             'full v5 exact durable group order')
        for index, (group, pin) in enumerate(rows):
            suffix = '-raw.json' if key == 'raw_pins' else '-validation.json'
            need(type(pin) is dict and set(pin) == {'file', 'bytes', 'sha256', 'durable'} and
                 pin['file'] == 'field-groups-v5/' + str(index).zfill(2) + '-' + group + suffix and
                 type(pin['bytes']) is int and 0 < pin['bytes'] <= (1048576 if key == 'raw_pins' else 8192) and
                 type(pin['sha256']) is str and len(pin['sha256']) == 64 and
                 all(character in '0123456789abcdef' for character in pin['sha256']) and pin['durable'] is True,
                 'full v5 durable evidence pin shape')
    raw_aggregate = evidence._encode(receipt['aggregate'], 1048576)
    final_pin = delivery['raw_pins'][-1][1]
    need(final_pin['sha256'] == sha256(raw_aggregate).hexdigest() and final_pin['bytes'] == len(raw_aggregate),
         'full v5 aggregate raw bytes binding')
    need(sum(pin['bytes'] for _, pin in delivery['raw_pins']) +
         sum(pin['bytes'] for _, pin in delivery['validation_pins']) == delivery['reserved_bytes'],
         'full v5 complete evidence byte invoice')
    return receipt
