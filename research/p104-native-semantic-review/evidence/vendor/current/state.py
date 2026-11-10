"""Reuse exact immutable circuit prefixes with a bounded cache.

Gate tables are by Charles Bethin (PR662); production use is by Wentao Li
(PR2329). Prefix reuse is by Ali Romman with OpenAI Codex assistance.
Apache-2.0. No acceptance result is cached.
"""
from functools import lru_cache
from pathlib import Path
import importlib.util

_spec = importlib.util.spec_from_file_location('retained_gate_tables', Path(__file__).parent/'inputs/fast_state.py')
_tables = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_tables)
gate_state = _tables.zero_state


def freeze(value):
    if isinstance(value, (list, tuple)):
        return tuple(map(freeze, value))
    return value


@lru_cache(maxsize=512)
def prefix(n, circuit, basis):
    if not circuit:
        return ((basis, (1, 0)),), 0
    entries, den = prefix(n, circuit[:-1], basis)
    gate = circuit[-1]
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
            if left != (0,0):
                out[x] = left
            if right != (0,0):
                out[y] = right
        den += 1
    else:
        raise ValueError('Unknown Clifford gate')
    while den and all((a & 1) == (b & 1) == 0 for a,b in out.values()):
        out = {x: (a//2,b//2) for x,(a,b) in out.items()}
        den -= 1
    return tuple(out.items()), den


def prefix_state(op, basis=0):
    entries, denominator = prefix(op.n, freeze(op.circuit), basis)
    values = [(0,0)]*(1 << op.n)
    for address, pair in entries:
        values[address] = pair
    return values, denominator


def clear():
    prefix.cache_clear()
    _tables.clear_caches()
