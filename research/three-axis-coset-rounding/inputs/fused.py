"""Fuse two Gaussian axes with an exact inverse on the integer grid.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
import importlib.util
from pathlib import Path


def need(ok, why):
    if not ok:
        raise ValueError(why)


def retained(name):
    spec = importlib.util.spec_from_file_location('retained_'+name, Path(__file__).parent/'inputs'/(name+'.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


baseline = retained('baseline')


def parity(values):
    return ((values[0][0] ^ values[1][1] ^ values[2][1] ^ values[3][0]) & 1,
            (values[0][1] ^ values[1][0] ^ values[2][0] ^ values[3][1]) & 1)


def block(values, width, sign=1, trace=None):
    need(type(width) is int and width >= 2 and type(sign) is int and sign in (-1, 1), 'Block format')
    need(len(values) == 4 and all(len(z) == 2 for z in values), 'Four Gaussian words')
    trace = trace if trace is not None else {}
    def word(value):
        need(type(value) is int and -(1 << (width-1)) <= value < (1 << (width-1)), 'Signed word overflow')
        trace['checked_values'] = trace.get('checked_values', 0)+1
        trace['peak_integer'] = max(trace.get('peak_integer', 0), abs(value))
        return value
    def add(x, y, direction=1):
        return word(x[0]+direction*y[0]), word(x[1]+direction*y[1])
    def phase(z, q):
        a, b = z
        if q == 0:
            return a, b
        if q == 1:
            return word(-b), a
        if q == 2:
            return word(-a), word(-b)
        return b, word(-a)
    x = [tuple(map(word, z)) for z in values]
    a, b = parity(x)
    x[0] = word(x[0][0]-a), x[0][1]
    x[1] = word(x[1][0]-b), x[1][1]
    x = [phase(z, q % 4) for z, q in zip(x, (0, -sign, -sign, 2))]
    u, v = add(x[0], x[1]), add(x[0], x[1], -1)
    w, z = add(x[2], x[3]), add(x[2], x[3], -1)
    x = [add(u, w), add(v, z), add(u, w, -1), add(v, z, -1)]
    need(all(n & 1 == 0 for z in x for n in z), 'Exact block halves')
    x = [tuple(word(n >> 1) for n in z) for z in x]
    x = [phase(z, q % 4) for z, q in zip(x, (sign, 0, 0, -sign))]
    x[0] = word(x[0][0]+b), x[0][1]
    x[1] = word(x[1][0]+a), x[1][1]
    for key, count in dict(fused_blocks=1, data_additions=20, data_negations=6,
                           component_swaps=4, data_half_shifts=8, parity_xors=6,
                           parity_bit_reads=8, block_value_reads=8, block_value_writes=8).items():
        trace[key] = trace.get(key, 0)+count
    trace['nonzero_blocks'] = trace.get('nonzero_blocks', 0)+int(bool(a or b))
    return tuple(x)


def group(values, first, second, width, sign=1, trace=None):
    need(type(first) is type(second) is int and 0 <= first < second
         and len(values) > (1 << second) and len(values) & (len(values)-1) == 0, 'Two-axis dimensions')
    mask = (1 << first) | (1 << second)
    for index in range(len(values)):
        if index & mask == 0:
            indices = (index, index | (1 << first), index | (1 << second), index | mask)
            out = block([values[j] for j in indices], width, sign, trace)
            for j, value in zip(indices, out):
                values[j] = value
    return values


def call(values, f, axis, width, adjoint=False, trace=None):
    need(type(f) is int and f >= 1 and type(axis) is int and axis in (0, 2)
         and len(values) == 8**f and type(adjoint) is bool, 'Literal Gaussian call dimensions')
    stages = list(range(0, f, 2))
    if adjoint:
        stages.reverse()
    for stage in stages:
        if stage+1 < f:
            group(values, 3*stage+axis, 3*(stage+1)+axis, width, -1 if adjoint else 1, trace)
        else:
            baseline.layer(values, 3*stage+axis, width, -1 if adjoint else 1, trace)
    return values
