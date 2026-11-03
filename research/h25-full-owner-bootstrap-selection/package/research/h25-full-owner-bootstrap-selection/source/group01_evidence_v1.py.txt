"""Parent data replay of the exact unchanged Group01 finite producer route.

All arguments come from the owning parent registry and independently frozen
prelaunch plan.  A parsed status never establishes process ownership, native
correctness or historical source continuity.  Those are separate original
source/runtime and owned-domain obligations.  No function was executed here.
"""
import json
import math
import epoch_schema_v5 as schema
import epoch_copy_v5 as copying
import original_build_provenance_v5 as original_build
import parent_closure_v1 as closure
import group01_original_predicates_v1 as original_predicates

_TYPE, _LEN = type, len
GROUP_ORDER = ('native', 'transport', 'collector', 'pure_initial', 'pure_extended',
               'pure_combined', 'root_model', 'sink_close_model', 'projection_model', 'aggregate')
GROUP_KEYS = ('native', 'transport', 'collector', 'elf', 'providers', 'elf_extended')
MAX_JSON_NODES = 200000
MAX_JSON_BYTES = 4 * 1024 * 1024
FINITE_KEYS = ('status', 'lanes', 'data_handling', 'data_source_custody', 'optimized',
    'original_controls', 'new_controls', 'new_source_custody', 'driver_sha256',
    'initial_native_tcb', 'initial_native_tcb_restoration', 'native_packet',
    'reference_driver_sha256', 'phases')


def _pairs(pairs):
    schema.need(_TYPE(pairs) is list and _LEN(pairs) <= 8192, 'receipt JSON object bound')
    result = {}
    for key, value in pairs:
        schema.need(_TYPE(key) is str and _LEN(key) <= 65536 and key not in result,
                    'receipt duplicate/foreign/oversize key')
        result[key] = value
    return result


def _reject(value):
    raise schema.EpochStop('nonfinite receipt JSON constant')


def _plain(value, budget, depth=0):
    schema.need(depth <= 40 and budget[0] > 0, 'receipt JSON node/depth bound')
    budget[0] -= 1
    kind = _TYPE(value)
    if value is None or kind is bool:
        return
    if kind is int:
        schema.need(value.bit_length() <= 4096, 'receipt integer bound')
        return
    if kind is float:
        schema.need(math.isfinite(value), 'nonfinite receipt number')
        return
    if kind is str:
        schema.need(_LEN(value) <= 65536, 'receipt string bound')
        budget[1] += _LEN(value)
        schema.need(budget[1] <= MAX_JSON_BYTES, 'receipt text budget')
        return
    schema.need(kind in (list, dict) and _LEN(value) <= 8192, 'receipt exact collection bound')
    if kind is dict:
        for key, item in value.items():
            schema.need(_TYPE(key) is str, 'receipt exact key required')
            _plain(key, budget, depth + 1)
            _plain(item, budget, depth + 1)
    else:
        for item in value:
            _plain(item, budget, depth + 1)


def decode(raw):
    schema.need(_TYPE(raw) is bytes and 0 < _LEN(raw) <= MAX_JSON_BYTES, 'receipt raw byte bound')
    value = json.loads(raw.decode('ascii'), object_pairs_hook=_pairs, parse_constant=_reject)
    schema.need(_TYPE(value) is dict, 'receipt top-level exact object required')
    _plain(value, [MAX_JSON_NODES, 0])
    return value


def encode(value):
    _plain(value, [MAX_JSON_NODES, 0])
    raw = json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True,
                     allow_nan=False).encode('ascii') + b'\n'
    schema.need(_LEN(raw) <= MAX_JSON_BYTES, 'receipt canonical byte bound')
    return raw


def same_json(left, right):
    # Both operands are exact bounded JSON-native data. Canonical bytes retain
    # bool/int/float distinctions that Python nested equality otherwise loses.
    return encode(left) == encode(right)


def _read(path, bound, error_owner):
    pin = copying.inspect(path, bound, error_owner=error_owner)
    raw = copying.read_verified(pin, bound, error_owner=error_owner)
    return pin, raw


def _captured_call(receiver_capability, module, name, *args):
    # Exact module/function names below are source literals, not caller-selected
    # callbacks.  Current source/identity checks surround every receiving call.
    closure.check_receivers(receiver_capability)
    function = closure.receiver(receiver_capability, module, name)
    result = function(*args)
    closure.check_receivers(receiver_capability)
    return result


def _legacy_controls(result, expected):
    schema.exact(expected, ('original_counts', 'original_fixture_sha256',
        'original_v2_counts', 'original_v2_stream', 'new_controls'))
    schema.digest(expected['original_fixture_sha256'])
    native = result['original_controls']
    schema.need(_TYPE(native) is dict and native.get('status') == 'FINITE_NATIVE_GF2_CONTROLS_PASS' and
        same_json(native.get('counts'), expected['original_counts']) and
        native.get('fixture_sha256') == expected['original_fixture_sha256'] and
        _TYPE(native.get('micro_repetitions')) is int and native['micro_repetitions'] == 128 and
        native.get('independent_oracle') ==
        'Dense binary lists, descending pivots, addition modulo 2; no packed/source/native helpers',
        'original native independent outcome projection differs')
    schema.need(_TYPE(native.get('micro_fixtures')) is int and native['micro_fixtures'] > 0 and
        _TYPE(native.get('native_and_fallback_calls')) is dict and
        all(_TYPE(value) is int and value > 0 for value in native['native_and_fallback_calls'].values()),
        'original native and fallback paths not represented')
    v2 = native.get('v2_controls')
    schema.need(_TYPE(v2) is dict and v2.get('status') == 'V2_RUNTIME_AND_COMPLEMENT_STREAM_PASS' and
        same_json(v2.get('counts'), expected['original_v2_counts']) and
        same_json(v2.get('complement_fixture_stream'), expected['original_v2_stream']) and
        _TYPE(v2.get('modified_helper_invocations')) is int and v2['modified_helper_invocations'] == 0,
        'original runtime/ordered-complement independent projection differs')
    # The expected complete new-control tree is an independently approved input
    # before launch.  It is never learned from this result or an earlier PASS.
    schema.need(same_json(result['new_controls'], expected['new_controls']),
                'complete original bookkeeping control return differs')


def authenticate_group01(output, expected, process_id, parent_file_limits,
                         receiver_capability, error_owner, stdout_raw):
    """Return actual evidence data; only the owning launcher can mint authority."""
    schema.path(output)
    schema.integer(process_id, 1, (1 << 31) - 1)
    schema.exact(expected, ('mode', 'generation', 'stage_sha256', 'root_sha256',
        'driver_sha256', 'reference_driver_sha256', 'builds', 'legacy_outcomes',
        'source_receipts', 'tcb_files', 'hashlib_origin'))
    schema.choice(expected['mode'], ('normal', 'optimized'))
    schema.label(expected['generation'])
    for key in ('stage_sha256', 'root_sha256', 'driver_sha256', 'reference_driver_sha256'):
        schema.digest(expected[key])
    schema.path(expected['hashlib_origin'])
    optimize = 0 if expected['mode'] == 'normal' else 1
    result_pin, result_raw = _read(output + '/receipt.json', MAX_JSON_BYTES, error_owner)
    result = decode(result_raw)
    schema.exact(result, FINITE_KEYS)
    schema.need(result['status'] == 'H25_DATA_HANDLING_FINITE_PASS' and
                result['lanes'] == 'all' and _TYPE(result['optimized']) is int and
                result['optimized'] == optimize and
                result['driver_sha256'] == expected['driver_sha256'] and
                result['reference_driver_sha256'] == expected['reference_driver_sha256'],
                'original finite producer route/mode/source differs')
    schema.need(same_json(decode(stdout_raw), result), 'original stdout and terminal finite receipt differ')
    _legacy_controls(result, expected['legacy_outcomes'])
    finite_pin, finite_raw = _read(output + '/finite-controls.json', MAX_JSON_BYTES, error_owner)
    schema.need(same_json(decode(finite_raw), result['original_controls']), 'original finite raw result differs')
    data, packet = result['data_handling'], result['native_packet']
    schema.need(_TYPE(data) is dict and data.get('schema') == 'h25-data-handling-v2' and
        data.get('full_caller_run') is False and data.get('full_candidate_admission') is False and
        data.get('cache_teardown_stops') == [] and same_json(data.get('native_packet'), packet),
        'original finite data or cleanup boundary differs')
    original_predicates.check_original_control_union(
        {'controls': data['controls'], 'native_packet': packet}, optimize, include_late=True)
    schema.need(packet['late_started'] is True and packet['late_completed'] is True and
        packet['field_service_closed'] is True and packet['direct_close_stop'] is None and
        packet['field_group_stop'] is None and packet['field_restoration_receipt_checked'] is True and
        packet['field_runtime_qualification'] is False,
        'original late/group/field cleanup or qualification boundary differs')
    schema.exact(expected['source_receipts'], ('data_source_custody', 'new_source_custody',
                                              'compiler_dependencies'))
    for key in ('data_source_custody', 'new_source_custody'):
        schema.need(same_json(result[key], expected['source_receipts'][key]), 'source-derived receipt custody differs')
    schema.need(same_json(packet['compiler_dependencies'], expected['source_receipts']['compiler_dependencies']),
                'original compiler/link/header receipt closure differs')
    # Original placement is authenticated by exact launched source.  This call
    # replays its fixed data contract; it does not rerun initial native checks.
    tcb_files = tuple(tuple(row) for row in expected['tcb_files'])
    _captured_call(receiver_capability, 'restoration_contract_v1', 'validate_restoration',
        result['initial_native_tcb'], data['controls']['native_initial_tcb'],
        result['initial_native_tcb_restoration'], tcb_files, expected['hashlib_origin'],
        expected['root_sha256'], len(tcb_files))
    schema.integer(result['initial_native_tcb']['pid'], 1, (1 << 31) - 1)
    schema.integer(result['initial_native_tcb_restoration']['pid'], 1, (1 << 31) - 1)
    schema.need(result['initial_native_tcb']['pid'] == process_id and
                result['initial_native_tcb_restoration']['pid'] == process_id,
                'initial/restoration receipt belongs to another process')
    initial_pin, initial_raw = _read(output + '/initial-native-tcb.json', MAX_JSON_BYTES, error_owner)
    restored_pin, restored_raw = _read(output + '/initial-native-tcb-restoration.json', MAX_JSON_BYTES, error_owner)
    schema.need(same_json(decode(initial_raw), result['initial_native_tcb']) and
                same_json(decode(restored_raw), result['initial_native_tcb_restoration']),
                'initial/restoration retained raw differs')
    controls_pin, controls_raw = _read(output + '/initial-tcb-controls/receipt.json', MAX_JSON_BYTES, error_owner)
    schema.need(same_json(decode(controls_raw), data['controls']['native_initial_tcb']), 'original initial five-control raw differs')
    delivery = packet['field_group_delivery']
    aggregate = delivery['aggregate']
    schema.need(same_json(data['controls']['native_fields'], aggregate), 'field aggregate projections differ')
    # JSON object order is not the original insertion-order observation.  Restore
    # only this explicit source-fixed mapping order for the existing validator;
    # no value/case/sequence/order or unknown-key repair is permitted.
    schema.exact(aggregate['groups'], GROUP_KEYS)
    aggregate['groups'] = {key: aggregate['groups'][key] for key in GROUP_KEYS}
    _captured_call(receiver_capability, 'run_controls_v5', 'validate_all', delivery, expected['mode'])
    values = (aggregate['groups']['native'], aggregate['groups']['transport'],
        aggregate['groups']['collector'], aggregate['pure_v2']['initial'],
        aggregate['pure_v2']['extended'], aggregate['pure_v2'], aggregate['root_model'],
        aggregate['sink_close_model'], aggregate['projection_model'], aggregate)
    group_rows = []
    for index, (group, value) in enumerate(zip(GROUP_ORDER, values)):
        raw_ref = delivery['group_evidence']['raw_pins'][index][1]
        validation_ref = delivery['group_evidence']['validation_pins'][index][1]
        raw_pin, raw = _read(output + '/' + raw_ref['file'], 1048576, error_owner)
        validation_pin, validation_raw = _read(output + '/' + validation_ref['file'], 8192, error_owner)
        schema.need(raw_pin['sha256'] == raw_ref['sha256'] and raw_pin['bytes'] == raw_ref['bytes'] and
            validation_pin['sha256'] == validation_ref['sha256'] and validation_pin['bytes'] == validation_ref['bytes'],
            'durable group pin differs from actual retained bytes')
        schema.need(raw == encode(value), 'complete raw group differs from original aggregate projection')
        note = {'schema': 'h25-full-group-evidence-sink-v5', 'mode': expected['mode'], 'group': group,
                'state': 'RETURNED_RAW_OUTER_VALIDATED', 'raw': raw_ref}
        schema.need(validation_raw == encode(note), 'complete validation note differs')
        group_rows.append({'group': group, 'raw': raw_pin, 'validation': validation_pin})
    builds = []
    schema.sequence(expected['builds'], 3)
    for role, build_plan in zip(schema.ROLES[:3], expected['builds']):
        schema.exact(build_plan, ('role', 'profile', 'command_sha256', 'original_output_path', 'expected_original'))
        schema.need(build_plan['role'] == role, 'original build role order differs')
        base = output + '/cold-native-metadata/' + role
        original_record_pin, raw_receipt = _read(base + '-build.json', 65536, error_owner)
        original_record = decode(raw_receipt)
        schema.need(same_json(original_record, packet['builds'][role]), 'original build raw/terminal projection differs')
        row = {'role': role, 'producer_role': 'group01', 'producer_generation': expected['generation'],
            'producer_stage_sha256': expected['stage_sha256'], 'command_sha256': build_plan['command_sha256'],
            'profile': build_plan['profile'],
            'original_output': copying.inspect(build_plan['original_output_path'], error_owner=error_owner),
            'original_receipt': original_record_pin,
            'attempt': copying.inspect(base + '.attempt.json', 65536, error_owner=error_owner),
            'journal': copying.inspect(base + '.attempt.jsonl', schema.JOURNAL_BYTES, error_owner=error_owner),
            'stdout': copying.inspect(base + '.stdout.raw', schema.LOG_BYTES, error_owner=error_owner),
            'stderr': copying.inspect(base + '.stderr.raw', schema.LOG_BYTES, error_owner=error_owner)}
        independent = schema.plain_copy(build_plan['expected_original'])
        independent['producer_process_id'] = process_id
        independent['parent_file_limits'] = list(parent_file_limits)
        closure.check_receivers(receiver_capability)
        original_build.authenticate_original_build(row, independent, error_owner=error_owner)
        closure.check_receivers(receiver_capability)
        builds.append(row)
    return {'raw_result': result_pin, 'group_rows': group_rows, 'builds': builds,
            'additional_raw': [finite_pin, initial_pin, restored_pin, controls_pin],
            'own_group01_source_and_result_contract_checked': True,
            'later_cross_root_aggregate_required_before_export': False,
            'native_runtime_or_full_union_qualified': False}
