"""Exact native observation transport. No capability or semantic PASS decoder.

Only the source-bound live receiver owns the original objects. Encoding retains
native tuple/list, bytes/str, bool/int and None distinctions. Decoding creates
new data objects and must never be used to reconstruct a live owner or compare
in place of the receiver's original observations.
"""
import json
import hashlib

SCHEMA = 'h25-native-observation-wire-v2'
MAX_BYTES = 4 * 1024 * 1024
MAX_NODES = 65536
MAX_DEPTH = 32
MAX_SEQUENCE = 8192
MAX_ATOM_BYTES = 1024 * 1024
MAX_INTEGER_BITS = 128
_TYPE, _LEN = type, len


class WireError(ValueError):
    pass


def _need(value, message):
    if not value:
        raise WireError(message)


def _text(value):
    _need(_TYPE(value) is str and _LEN(value) <= MAX_ATOM_BYTES, 'exact bounded string required')
    _need(_LEN(value.encode('utf-8', 'surrogatepass')) <= MAX_ATOM_BYTES, 'string byte bound')


def _digest(value):
    _need(_TYPE(value) is str and _LEN(value) == 64 and
          all(c in '0123456789abcdef' for c in value), 'exact lowercase digest required')


def _node(value, state, depth):
    state[0] += 1
    _need(state[0] <= MAX_NODES and depth <= MAX_DEPTH, 'observation tree bound')
    kind = _TYPE(value)
    if value is None:
        return ['none']
    if kind is bool:
        return ['bool', value]
    if kind is int:
        _need(value.bit_length() <= MAX_INTEGER_BITS, 'native integer bound')
        return ['int', value]
    if kind is str:
        _text(value)
        return ['str', value]
    if kind is bytes:
        _need(_LEN(value) <= MAX_ATOM_BYTES, 'native bytes bound')
        return ['bytes', value.hex()]
    _need(kind is tuple or kind is list or kind is dict, 'foreign native observation type')
    _need(_LEN(value) <= MAX_SEQUENCE, 'native sequence bound')
    identity = id(value)
    _need(identity not in state[1], 'cyclic observation prohibited')
    state[1].add(identity)
    try:
        if kind is dict:
            for key in value:
                _text(key)
            return ['dict', [[key, _node(item, state, depth + 1)] for key, item in value.items()]]
        return ['tuple' if kind is tuple else 'list', [_node(item, state, depth + 1) for item in value]]
    finally:
        state[1].remove(identity)


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True,
                      allow_nan=False).encode('ascii') + b'\n'


def encode_observation(observation, binding):
    """Serialize actual retained data; native originals stay with the live owner."""
    _need(_TYPE(binding) is dict, 'exact source binding required')
    for key in binding:
        _text(key)
    _need(set(binding) == {'mode', 'epoch_id', 'action_id', 'generation', 'source_role',
          'full_schedule_sha256', 'parent_plan_sha256', 'binding_sha256', 'receiver_sha256'},
          'wire binding keys differ')
    for key in ('mode', 'epoch_id', 'action_id', 'generation', 'source_role'):
        _text(binding[key])
    _need(binding['mode'] in ('normal', 'optimized'), 'wire mode differs')
    for key in ('full_schedule_sha256', 'parent_plan_sha256', 'binding_sha256', 'receiver_sha256'):
        _digest(binding[key])
    _need(_TYPE(observation) is dict, 'exact actual receiver dictionary required')
    value = {'schema': SCHEMA, 'binding': dict(binding), 'tree': _node(observation, [0, set()], 0),
             'runtime_authority': False, 'restorable': False, 'saved_PASS': False}
    raw = _canonical(value)
    _need(_LEN(raw) <= MAX_BYTES, 'wire byte bound')
    return raw


def _pairs(pairs):
    _need(_LEN(pairs) <= MAX_SEQUENCE, 'wire mapping bound')
    result = {}
    for key, value in pairs:
        _text(key)
        _need(key not in result, 'duplicate wire key')
        result[key] = value
    return result


def _reject(value):
    raise WireError('noninteger JSON atom forbidden')


def _restore(node, counter, depth):
    counter[0] += 1
    _need(counter[0] <= MAX_NODES and depth <= MAX_DEPTH and _TYPE(node) is list and
          1 <= _LEN(node) <= 2 and _TYPE(node[0]) is str, 'malformed typed node')
    tag = node[0]
    if tag == 'none':
        _need(_LEN(node) == 1, 'none node arity')
        return None
    _need(_LEN(node) == 2, 'typed node arity')
    data = node[1]
    if tag == 'bool':
        _need(_TYPE(data) is bool, 'bool node type')
        return data
    if tag == 'int':
        _need(_TYPE(data) is int and data.bit_length() <= MAX_INTEGER_BITS, 'int node type')
        return data
    if tag == 'str':
        _text(data)
        return data
    if tag == 'bytes':
        _need(_TYPE(data) is str and _LEN(data) <= 2 * MAX_ATOM_BYTES and _LEN(data) % 2 == 0 and
              all(c in '0123456789abcdef' for c in data), 'noncanonical bytes node')
        return bytes.fromhex(data)
    _need(tag in ('tuple', 'list', 'dict') and _TYPE(data) is list and
          _LEN(data) <= MAX_SEQUENCE, 'container node type')
    if tag == 'dict':
        result = {}
        for pair in data:
            _need(_TYPE(pair) is list and _LEN(pair) == 2, 'dict node pair')
            key, value = pair
            _text(key)
            _need(key not in result, 'duplicate native dictionary key')
            result[key] = _restore(value, counter, depth + 1)
        return result
    result = [_restore(value, counter, depth + 1) for value in data]
    return tuple(result) if tag == 'tuple' else result


def decode_observation(raw):
    """Return fresh audit data only; no process-local identity survives transport."""
    _need(_TYPE(raw) is bytes and 0 < _LEN(raw) <= MAX_BYTES, 'wire byte type/bound')
    value = json.loads(raw.decode('ascii'), object_pairs_hook=_pairs,
                       parse_float=_reject, parse_constant=_reject)
    _need(_TYPE(value) is dict and set(value) == {'schema', 'binding', 'tree',
          'runtime_authority', 'restorable', 'saved_PASS'}, 'wire envelope differs')
    _need(value['schema'] == SCHEMA and value['runtime_authority'] is False and
          value['restorable'] is False and value['saved_PASS'] is False, 'wire authority denied')
    observation = _restore(value['tree'], [0], 0)
    _need(encode_observation(observation, value['binding']) == raw, 'wire bytes not exact canonical form')
    return value['binding'], observation


def observation_sha256(raw):
    _need(_TYPE(raw) is bytes and _LEN(raw) <= MAX_BYTES, 'exact wire bytes required')
    return hashlib.sha256(raw).hexdigest()
