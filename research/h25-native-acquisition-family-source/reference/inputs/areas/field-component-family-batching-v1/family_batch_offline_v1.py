"""Pure byte/data audit of family batch records; never restores live authority.

Only stdlib imports. Caller-acquired pins and an independently retained head,
plan/catalog and complete raw pairs are inputs, not process/native admission.
"""
import hashlib
import json
import math

LIMIT = 4 * 1024 * 1024


class AuditReject(ValueError):
    pass


def need(ok, message):
    if ok is not True:
        raise AuditReject(message)


def exact(value, keys):
    need(type(value) is dict and all(type(k) is str for k in value) and set(value) == set(keys), 'exact native keys differ')


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False).encode('ascii') + b'\n'


def pairs(items):
    need(len(items) <= 8192, 'mapping bound')
    result = {}
    for key, value in items:
        need(type(key) is str and len(key) <= 2097152 and key not in result, 'duplicate or foreign key')
        result[key] = value
    return result


def bounded(value, count, depth=0):
    count[0] += 1
    need(count[0] <= 327693 and depth <= 100, 'complete audit JSON node/depth bound')
    if value is None or type(value) is bool:
        return
    if type(value) is int:
        need(value.bit_length() <= 128, 'integer bound')
        return
    if type(value) is float:
        need(math.isfinite(value), 'nonfinite diagnostic time')
        return
    if type(value) is str:
        need(len(value) <= 2097152, 'string bound')
        return
    need((type(value) is list or type(value) is dict) and len(value) <= 8192, 'collection bound')
    for item in value.values() if type(value) is dict else value:
        bounded(item, count, depth + 1)


def decode(raw):
    need(type(raw) is bytes and 0 < len(raw) <= LIMIT, 'bounded raw audit bytes required')
    value = json.loads(raw.decode('ascii'), object_pairs_hook=pairs)
    bounded(value, [0])
    need(type(value) is dict and canonical(value) == raw, 'exact canonical record required')
    return value


def check_pin(pin, raw):
    exact(pin, ('path', 'sha256', 'bytes', 'identity'))
    need(type(pin['path']) is str and pin['path'].startswith('/') and
         type(pin['bytes']) is int and 0 <= pin['bytes'] <= 67108864 and
         type(raw) is bytes and len(raw) == pin['bytes'] and hashlib.sha256(raw).hexdigest() == pin['sha256'],
         'complete raw artifact or pin hash differs')
    exact(pin['identity'], ('device', 'inode', 'mode', 'links', 'uid', 'gid', 'size', 'mtime_ns', 'ctime_ns'))
    need(all(type(v) is int and v >= 0 for v in pin['identity'].values()) and
         pin['identity']['size'] == pin['bytes'] and pin['identity']['links'] == 1 and
         pin['identity']['mode'] & 0o170000 == 0o100000, 'custody shape differs')


def typed(node, count, depth=0):
    count[0] += 1
    need(count[0] <= 262144 and depth <= 32 and type(node) is list and 1 <= len(node) <= 3, 'typed unit node bound')
    tag = node[0]
    if tag == 'none':
        need(len(node) == 1, 'none arity')
        return None
    if tag in ('opaque-process-local-object-not-authority', 'original-registered-ParentEpoch-not-serializable',
               'original-ErrorOwner-not-serializable'):
        need(len(node) == 1, 'opaque arity')
        return {'opaque_observation_tag': tag}
    need(len(node) >= 2, 'typed atom missing')
    value = node[1]
    if tag == 'bool':
        need(type(value) is bool and len(node) == 2, 'bool type')
        return value
    if tag == 'int':
        need(type(value) is int and value.bit_length() <= 128 and len(node) == 2, 'int type')
        return value
    if tag == 'str':
        need(type(value) is str and len(value) <= 8192 and len(node) == 2, 'string type')
        return value
    if tag == 'bytes':
        need(type(value) is int and len(node) == 3 and 0 <= value <= 2097152, 'byte observation shape')
        return {'byte_observation_length': value, 'byte_observation_sha256': node[2], 'full_bytes_required_separately': True}
    need(type(value) is list and len(value) <= 4096 and len(node) == 2, 'typed container')
    if tag == 'tuple' or tag == 'list':
        values = [typed(x, count, depth + 1) for x in value]
        return tuple(values) if tag == 'tuple' else values
    need(tag == 'dict' and len(value) <= 1024, 'typed dictionary')
    result = {}
    for pair in value:
        need(type(pair) is list and len(pair) == 2 and type(pair[0]) is str and pair[0] not in result, 'typed key shape')
        result[pair[0]] = typed(pair[1], count, depth + 1)
    need(list(result) == sorted(result), 'typed key order')
    return result


def raw_events(raw, unit, mode):
    need(type(raw) is bytes and len(raw) <= 2097152 and raw.endswith(b'\n'), 'whole original unit stdout required')
    lines = raw.splitlines(keepends=True)
    need(3 <= len(lines) <= 8192, 'event count')
    events, latest, digest = [], None, hashlib.sha256()
    for index, line in enumerate(lines):
        need(len(line) <= 1048576, 'event byte bound')
        event = json.loads(line.decode('ascii'), object_pairs_hook=pairs)
        exact(event, ('schema', 'unit_id', 'mode', 'ordinal', 'kind', 'target', 'payload'))
        need(event['schema'] == 'h25-component-control-event-v1' and event['unit_id'] == unit and
            event['mode'] == mode and type(event['ordinal']) is int and event['ordinal'] == index, 'unit/mode/order')
        kind, value = event['kind'], event['payload']
        need((index == 0) is (kind == 'CONTEXT_BOUND'), 'complete original context event omitted or renewed')
        if kind == 'CONTEXT_BOUND':
            need(index == 0, 'context renewed')
            decoded = typed(value, [0])
        elif kind == 'RAW_RETURN':
            exact(value, ('value', 'facts'))
            decoded = {'value': typed(value['value'], [0]), 'facts': typed(value['facts'], [0])}; latest = index
        elif kind == 'RAW_RAISE':
            exact(value, ('exception_type', 'args', 'facts'))
            decoded = {'exception_type': value['exception_type'], 'args': typed(value['args'], [0]),
                       'facts': typed(value['facts'], [0])}; latest = index
        elif kind == 'ORACLE':
            exact(value, ('raw_ordinal', 'facts'))
            need(type(value['raw_ordinal']) is int and value['raw_ordinal'] == latest and latest < index,
                 'oracle did not follow its actual raw observation')
            decoded = {'raw_ordinal': latest, 'facts': typed(value['facts'], [0])}
        else:
            need(kind == 'UNIT_TERMINAL' and index == len(lines)-1, 'terminal omitted or misplaced')
            decoded = typed(value, [0])
            need(decoded['family_completion'] is False and decoded['complete_finite_union'] is False and
                decoded['prior_events'] == index and decoded['prior_wire_sha256'] == digest.hexdigest(),
                'child terminal scope or complete raw prefix differs')
        events.append(dict(event, decoded=decoded)); digest.update(line)
    need(events[-1]['kind'] == 'UNIT_TERMINAL', 'terminal missing')
    return events


def verify_chain(mode, expected_plan_sha256, expected_cases, expected_families, registry_directory,
                 retained_head, record_pairs, artifact_pairs, *, expected_envelopes, require_terminal=True):
    need(mode in ('normal', 'optimized') and type(record_pairs) is tuple and len(record_pairs) <= 4096,
         'bounded exact mode/record pairs required')
    artifacts = {}
    for pin, raw in artifact_pairs:
        check_pin(pin, raw); need(pin['path'] not in artifacts, 'artifact path repeated')
        artifacts[pin['path']] = (pin, raw)
    previous, reserved, consumed, judged, families = None, {}, set(), {}, []
    envelope_active, complete = None, False
    dispatch_started, envelope_index, active_children = False, 0, []
    for sequence, pair in enumerate(record_pairs):
        need(type(pair) is tuple and len(pair) == 2, 'record pair shape')
        pin, raw = pair; check_pin(pin, raw); row = decode(raw)
        exact(row, ('schema', 'plan_sha256', 'mode', 'kind', 'identity', 'sequence', 'previous', 'payload',
                    'runtime_authority', 'saved_PASS'))
        need(row['schema'] == 'h25-family-batch-chain-v1' and row['mode'] == mode and
            row['plan_sha256'] == expected_plan_sha256 and type(row['sequence']) is int and row['sequence'] == sequence and
            canonical(row['previous']) == canonical(previous) and row['runtime_authority'] is False and
            row['saved_PASS'] is False, 'record source/order/predecessor/authority differs')
        kind, identity, payload = row['kind'], row['identity'], row['payload']
        key = hashlib.sha256(canonical({'mode': mode, 'identity': identity, 'kind': kind})).hexdigest()
        need(pin['path'] == registry_directory + '/family-batch-' + key + '.json', 'semantic burn filename differs')
        if kind == 'BATCH_PLAN_RESERVED':
            need(sequence == 0 and payload['cases'] == list(expected_cases), 'complete case reservation differs')
        elif kind == 'CHILD_RESERVED':
            need(not dispatch_started and envelope_active is None and identity not in reserved and payload['case_id'] in expected_cases,
                 'child reservation reused/substituted')
            reserved[identity] = payload['case_id']
        elif kind == 'ENVELOPE_CONSUMED':
            need(envelope_active is None and identity == list(expected_envelopes)[envelope_index] and
                payload['children'] == expected_envelopes[identity] and
                list(reserved.values()) == list(expected_cases), 'envelope order/reservation/grouping differs')
            dispatch_started = True
            envelope_active = identity
            active_children = payload['children']
        elif kind == 'CHILD_CONSUMED':
            need(envelope_active is not None and identity in active_children and identity in reserved and identity not in consumed and
                payload['case_id'] == reserved[identity], 'child consumed before reserve or replayed')
            consumed.add(identity)
        elif kind == 'CHILD_JUDGED':
            need(identity in consumed and payload['case_id'] == reserved[identity] and identity not in judged and
                payload['case_id'] == list(expected_cases)[len(judged)] and
                payload['family_completion'] is False and payload['complete_finite_union'] is False,
                'unit judgment omitted/replayed or invented completion')
            for raw_pin in payload['raw_pins']:
                need(raw_pin['path'] in artifacts and canonical(raw_pin) == canonical(artifacts[raw_pin['path']][0]),
                     'complete acquired original raw artifact absent')
            stdout_pin = payload['raw_pins'][0]
            raw_events(artifacts[stdout_pin['path']][1], expected_cases[payload['case_id']]['unit_id'], mode)
            judged[identity] = payload['case_id']
        elif kind == 'ENVELOPE_COMPLETE':
            need(identity == envelope_active and all(c in judged for c in active_children) and
                 payload['children'] == len(active_children) and payload['whole_family_or_union'] is False, 'envelope completion invented scope')
            envelope_active = None
            envelope_index += 1
        elif kind == 'FAMILY_COMPLETE':
            need(identity in expected_families and identity not in families and
                payload['cases'] == expected_families[identity] and all(c in judged.values() for c in payload['cases']),
                'family missing original cases or substituted scenario')
            families.append(identity)
        else:
            need(kind == 'COMPONENT_UNION_COMPLETE' and sequence == len(record_pairs)-1 and envelope_active is None and
                families == list(expected_families) and len(families) == 212 and
                set(judged.values()) == set(expected_cases) and payload['families'] == families and
                payload['full_six_area_finite'] is False and payload['restorable'] is False,
                'complete212 terminal or full child tail missing')
            complete = True
        previous = pin
    need(canonical(previous) == canonical(retained_head), 'independently retained head differs')
    need(not require_terminal or complete, 'complete terminal missing; partial prefix never resumes')
    return {'schema': 'h25-family-batch-offline-data-audit-v1', 'records': len(record_pairs),
        'complete_212_chain_data': complete, 'families': len(families), 'raw_artifacts': len(artifacts),
        'current_kernel_ownership_verified': False, 'full_original_semantic_oracles_recomputed': False,
        'runtime_authority': False, 'restorable': False, 'saved_PASS': False, 'full_finite_union': False}
