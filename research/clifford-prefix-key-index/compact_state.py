"""Iterative compact keys for exact immutable Clifford prefix states.

Produced by Nick Petalas. Apache-2.0.
Gate application and sparse states retain Ali Romman, Charles Bethin and
Wentao Li credit from PR6479. The new step is the bounded iterative key index.
"""
from collections import OrderedDict
from functools import lru_cache
from pathlib import Path
import importlib.util

_HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location('compact_gate_tables', _HERE/'vendor/inputs/fast_state.py')
_tables = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_tables)
_nodes = OrderedDict()
_states = OrderedDict()
_next = 0
NODE_CAP = 8192
STATE_CAP = 512
MAX_GATES = 512


def freeze_gate(gate):
    return tuple(tuple(x) if isinstance(x, (tuple, list)) else x for x in gate)


def node(parent, gate):
    global _next
    key = parent, gate
    found = _nodes.get(key)
    if found is not None:
        _nodes.move_to_end(key)
        return found
    _next += 1
    _nodes[key] = _next
    if len(_nodes) > NODE_CAP:
        _nodes.popitem(last=False)
    return _next


@lru_cache(maxsize=512)
def route(n, gates):
    keys = [node(0, ('root',n))]
    for gate in gates:
        keys.append(node(keys[-1],gate))
    return tuple(keys)


def remember(key, value):
    _states[key] = value
    _states.move_to_end(key)
    if len(_states) > STATE_CAP:
        _states.popitem(last=False)


def step(n, gate, entries, den):
    tag = gate[0]
    if tag == 'P':
        mapping = _tables.permutation_table(n, gate[1])
        out = {mapping[x]: pair for x, pair in entries}
    elif tag == 'X':
        out = {x ^ gate[1]: pair for x, pair in entries}
    elif tag in ('D', 'phase'):
        phases = _tables.phase_table(n, gate[1], gate[2]) if tag == 'D' else None
        out = {}
        for x, (a, b) in entries:
            phase = phases[x] if phases is not None else gate[1] % 4
            out[x] = ((a,b),(-b,a),(-a,-b),(b,-a))[phase]
    elif tag == 'C':
        direction, sign = gate[1:]
        values = dict(entries)
        pairs = {min(x, x ^ direction) for x in values}
        out = {}
        for x in pairs:
            y = x ^ direction
            a, b = values.get(x, (0,0))
            c, d = values.get(y, (0,0))
            left = (a-sign*b+c+sign*d, b+sign*a+d-sign*c)
            right = (c-sign*d+a+sign*b, d+sign*c+b-sign*a)
            if left != (0,0): out[x] = left
            if right != (0,0): out[y] = right
        den += 1
    else:
        raise ValueError('Unknown Clifford gate')
    for _ in range(den):
        if not all((a & 1) == (b & 1) == 0 for a,b in out.values()): break
        out = {x: (a//2,b//2) for x,(a,b) in out.items()}
        den -= 1
    return tuple(out.items()), den


def prefix_state(op, basis=0):
    if not (type(op.n) is int and 1 <= op.n <= 9 and type(basis) is int
            and 0 <= basis < 1 << op.n and len(op.circuit) <= MAX_GATES):
        raise ValueError('Bounded Clifford state domain')
    if _next + MAX_GATES + 1 >= 2**63: clear()
    gates = tuple(freeze_gate(g) for g in op.circuit)
    keys = route(op.n,gates)
    entries, denominator = ((basis,(1,0)),), 0
    start = 0
    for i in range(len(keys)-1,-1,-1):
        key = keys[i], basis
        if key in _states:
            entries, denominator = _states[key]
            _states.move_to_end(key)
            start = i
            break
    else:
        remember((keys[0],basis),(entries,denominator))
    for i in range(start,len(gates)):
        entries, denominator = step(op.n,gates[i],entries,denominator)
        remember((keys[i+1],basis),(entries,denominator))
    values = [(0,0)]*(1 << op.n)
    for address, pair in entries: values[address] = pair
    return values, denominator


def clear():
    global _next
    _states.clear()
    _nodes.clear()
    route.cache_clear()
    _next = 0
    _tables.clear_caches()
