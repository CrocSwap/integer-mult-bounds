"""Bounded wire validation only. The authentic owning parent supplies authority.

This parser cannot mint a complete family/finite pass from counts or a child
terminal. Caller must first join the actual owned child, retain raw streams,
verify exact current source/configuration/runtime custody, and bind a literal
unit from the independently reviewed source manifest. All missing family bodies
remain a hard full-union refusal.
"""
import hashlib
import json


class ControlWireError(RuntimeError):
    pass


def _need(ok, message):
    if ok is not True:
        raise ControlWireError(message)


def _pairs(rows):
    result = {}
    for key, value in rows:
        _need(type(key) is str and key not in result, 'duplicate/nonstring JSON key')
        result[key] = value
    return result


def _noninteger(value):
    raise ControlWireError('noninteger wire number')


def _typed(row, depth=0):
    _need(depth <= 32 and type(row) is list and 1 <= len(row) <= 3 and type(row[0]) is str, 'typed wire shape')
    tag = row[0]
    if tag in ('none', 'opaque-process-local-object-not-authority',
               'original-registered-ParentEpoch-not-serializable', 'original-ErrorOwner-not-serializable'):
        _need(len(row) == 1, 'empty typed wire leaf')
        return None if tag == 'none' else {'opaque_observation_tag': tag}
    _need(len(row) >= 2, 'typed wire value absent')
    value = row[1]
    if tag == 'bool':
        _need(len(row) == 2 and type(value) is bool, 'exact bool wire')
        return value
    if tag == 'int':
        _need(len(row) == 2 and type(value) is int and -(1 << 128) < value < (1 << 128), 'exact int wire')
        return value
    if tag == 'str':
        _need(len(row) == 2 and type(value) is str and len(value) <= 8192, 'exact string wire')
        return value
    if tag == 'bytes':
        _need(len(row) == 3 and type(value) is int and 0 <= value <= 2097152 and
              type(row[2]) is str and len(row[2]) == 64 and all(x in '0123456789abcdef' for x in row[2]), 'bytes observation wire')
        return {'byte_observation_length': value, 'byte_observation_sha256': row[2], 'full_bytes_required_separately': True}
    _need(len(row) == 2 and type(value) is list and len(value) <= 4096, 'typed collection bound')
    if tag in ('list', 'tuple'):
        decoded = [_typed(x, depth + 1) for x in value]
        return decoded if tag == 'list' else tuple(decoded)
    _need(tag == 'dict' and len(value) <= 1024, 'typed mapping tag/bound')
    result = {}
    keys = []
    for item in value:
        _need(type(item) is list and len(item) == 2 and type(item[0]) is str and item[0] not in result, 'typed mapping key')
        keys.append(item[0])
        result[item[0]] = _typed(item[1], depth + 1)
    _need(keys == sorted(keys), 'typed mapping canonical order')
    return result


def validate_protocol(raw, expected_unit, expected_mode):
    _need(type(raw) is bytes and 0 < len(raw) <= 2097152 and raw.endswith(b'\n'), 'complete original bounded stdout required')
    _need(type(expected_unit) is str and 1 <= len(expected_unit) <= 128 and
          type(expected_mode) is str and expected_mode in ('normal', 'optimized'), 'independent unit/mode required')
    lines = raw.splitlines(keepends=True)
    _need(3 <= len(lines) <= 8192, 'finite event stream size')
    events, outcomes, oracles = [], [], []
    digest = hashlib.sha256()
    for index, line in enumerate(lines):
        _need(line.endswith(b'\n') and len(line) <= 1048576, 'complete bounded event line')
        row = json.loads(line.decode('ascii'), object_pairs_hook=_pairs, parse_float=_noninteger, parse_constant=_noninteger)
        _need(type(row) is dict and set(row) == {'schema', 'unit_id', 'mode', 'ordinal', 'kind', 'target', 'payload'}, 'exact event keys')
        _need(row['schema'] == 'h25-component-control-event-v1' and type(row['unit_id']) is str and
              row['unit_id'] == expected_unit and type(row['mode']) is str and row['mode'] == expected_mode and
              type(row['ordinal']) is int and row['ordinal'] == index and type(row['target']) is str and
              len(row['target']) <= 256, 'event source/unit/mode/order')
        kind = row['kind']
        _need(type(kind) is str and kind in ('CONTEXT_BOUND', 'RAW_RETURN', 'RAW_RAISE', 'ORACLE', 'UNIT_TERMINAL'), 'event kind')
        if index == 0:
            _need(kind == 'CONTEXT_BOUND', 'context must precede target')
        else:
            _need(kind != 'CONTEXT_BOUND', 'context cannot be renewed')
        payload = row['payload']
        if kind == 'CONTEXT_BOUND':
            row['decoded'] = _typed(payload)
        elif kind == 'RAW_RETURN':
            _need(type(payload) is dict and set(payload) == {'value', 'facts'}, 'raw return shape')
            row['decoded'] = {'value': _typed(payload['value']), 'facts': _typed(payload['facts'])}
            outcomes.append(index)
        elif kind == 'RAW_RAISE':
            _need(type(payload) is dict and set(payload) == {'exception_type', 'args', 'facts'} and
                  type(payload['exception_type']) is str and payload['exception_type'] in (
                  'epoch_schema_v5.EpochStop', 'builtins.RuntimeError', 'builtins.MemoryError', 'builtins.OSError',
                  'builtins.FileExistsError', 'builtins.FileNotFoundError', 'builtins.InterruptedError',
                  'component_control_root_v1.OpaquePrimary'), 'raw typed error shape')
            row['decoded'] = {'exception_type': payload['exception_type'], 'args': _typed(payload['args']),
                              'facts': _typed(payload['facts'])}
            outcomes.append(index)
        elif kind == 'ORACLE':
            _need(type(payload) is dict and set(payload) == {'raw_ordinal', 'facts'} and
                  type(payload['raw_ordinal']) is int and outcomes and payload['raw_ordinal'] == outcomes[-1] and
                  payload['raw_ordinal'] < index, 'oracle must follow its actual retained raw observation')
            row['decoded'] = {'raw_ordinal': payload['raw_ordinal'], 'facts': _typed(payload['facts'])}
            oracles.append(index)
        else:
            _need(index == len(lines) - 1 and outcomes and oracles, 'terminal must be last after real raw/oracle records')
            terminal = _typed(payload)
            _need(type(terminal) is dict and set(terminal) == {'status', 'family_completion', 'complete_finite_union',
                  'prior_events', 'prior_wire_sha256', 'actual_runtime_admission', 'gain'}, 'exact limited terminal shape')
            _need(terminal['status'] == 'IMPLEMENTED_UNIT_PASS' and terminal['family_completion'] is False and
                  terminal['complete_finite_union'] is False and terminal['actual_runtime_admission'] is False and
                  terminal['gain'] is False and type(terminal['prior_events']) is int and terminal['prior_events'] == index and
                  terminal['prior_wire_sha256'] == digest.hexdigest(), 'limited terminal/prior complete raw commitment')
            row['decoded'] = terminal
        events.append(row)
        digest.update(line)
    _need(events[-1]['kind'] == 'UNIT_TERMINAL', 'no terminal')
    return {'schema': 'h25-component-control-protocol-observation-v1', 'unit_id': expected_unit,
        'mode': expected_mode, 'stdout_sha256': hashlib.sha256(raw).hexdigest(), 'events': events,
        'raw_ordinals': outcomes, 'oracle_ordinals': oracles, 'wire_protocol_complete': True,
        'actual_child_source_status_custody_required': True, 'protocol_is_case_PASS': False,
        'family_completion': False, 'complete_finite_union': False}
