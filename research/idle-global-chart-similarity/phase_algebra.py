"""Exact quadratic Z/4 phases on binary addresses and their complete sums.

Ross Richardson with substantial OpenAI Codex assistance. Apache-2.0.
No floating point, sampling, or inference from a hash is used.
"""
from __future__ import annotations

from functools import lru_cache

N = 73
ALL = (1 << N) - 1
PAIR = {}
_next = 0
for _i in range(N):
    for _j in range(_i + 1, N):
        PAIR[_i, _j] = 1 << _next
        _next += 1
INCIDENT = [sum(PAIR[min(i, j), max(i, j)] for j in range(N) if i != j) for i in range(N)]
ZERO = (0, 0, 0)


def bits(mask):
    while mask:
        low = mask & -mask
        yield low.bit_length() - 1
        mask ^= low


@lru_cache(maxsize=None)
def clique(mask):
    out = 0
    values = list(bits(mask))
    for at, i in enumerate(values):
        for j in values[at + 1:]:
            out ^= PAIR[i, j]
    return out


def qadd(a, b):
    a0, a1, aq = a
    b0, b1, bq = b
    return a0 ^ b0, a1 ^ b1 ^ (a0 & b0), aq ^ bq


def qneg(q):
    low, high, edges = q
    return low, high ^ low, edges


@lru_cache(maxsize=None)
def parity(mask, coefficient=1):
    coefficient %= 4
    return (mask if coefficient & 1 else 0,
            mask if coefficient & 2 else 0,
            clique(mask) if coefficient & 1 else 0)


def qsum(axes, coefficient=1):
    q = ZERO
    for axis in axes:
        q = qadd(q, parity(axis, coefficient))
    return q


def value(q, address):
    low, high, edges = q
    exponent = (low & address).bit_count() + 2 * (high & address).bit_count()
    active = list(bits(address))
    for at, i in enumerate(active):
        for j in active[at + 1:]:
            exponent += 2 * bool(edges & PAIR[i, j])
    return exponent % 4


def neighbors(edges, i, active):
    return sum(1 << j for j in bits(active & ~(1 << i))
               if edges & PAIR[min(i, j), max(i, j)])


def cmul(a, b):
    return a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]


@lru_cache(maxsize=None)
def gauss(q, n=N):
    """Sum i**q(x) over every n-bit x, by exact one/pair elimination."""
    active = (1 << n) - 1
    low, high, edges = q
    if (low | high) & ~active:
        raise ValueError('phase outside declared variables')
    if edges & ~clique(active):
        raise ValueError('quadratic phase outside declared variables')
    factor = (1, 0)
    while active:
        if low:
            bit = low & -low
            i = bit.bit_length() - 1
            alpha = 1 + 2 * bool(high & bit)
            adjacent = neighbors(edges, i, active)
            low &= ~bit
            high &= ~bit
            edges &= ~INCIDENT[i]
            active ^= bit
            low, high, edges = qadd((low, high, edges), parity(adjacent, -alpha))
            factor = cmul(factor, (1, 1 if alpha == 1 else -1))
            continue
        if edges:
            edge = edges & -edges
            i, j = next(pair for pair, flag in PAIR.items() if flag == edge)
            bi, bj = 1 << i, 1 << j
            left = neighbors(edges, i, active) & ~bj
            right = neighbors(edges, j, active) & ~bi
            ai, aj = bool(high & bi), bool(high & bj)
            active &= ~(bi | bj)
            high &= ~(bi | bj)
            edges &= ~(INCIDENT[i] | INCIDENT[j])
            if ai:
                high ^= right
            if aj:
                high ^= left
            high ^= left & right
            for a in bits(left):
                for b in bits(right):
                    if a != b:
                        edges ^= PAIR[min(a, b), max(a, b)]
            factor = (factor[0] * (-2 if ai and aj else 2),
                      factor[1] * (-2 if ai and aj else 2))
            continue
        if high:
            return 0, 0
        return factor[0] << active.bit_count(), factor[1] << active.bit_count()
    return factor


def p_add(a, b, scale=1):
    out = dict(a)
    for q, c in b.items():
        v = out.get(q, 0) + scale * c
        if v:
            out[q] = v
        else:
            out.pop(q, None)
    return out


def p_phase(a, q):
    return {qadd(key, q): c for key, c in a.items()}


def p_mul(a, b):
    out = {}
    for qa, ca in a.items():
        for qb, cb in b.items():
            q = qadd(qa, qb)
            c = out.get(q, 0) + ca * cb
            if c:
                out[q] = c
            else:
                out.pop(q, None)
    return out


def p_sum(a, n=N):
    real = imag = 0
    for q, c in a.items():
        u, v = gauss(q, n)
        real += c * u
        imag += c * v
    return real, imag


def identity(phase=ZERO):
    return [[{phase: 1} if i == j else {} for j in range(8)] for i in range(8)]


def copy_matrix(matrix):
    return [[dict(v) for v in row] for row in matrix]


def left(matrix, event, inverse=False):
    kind = event[0]
    if kind == 'phase':
        _, row, q = event
        if inverse:
            q = qneg(q)
        matrix[row] = [p_phase(v, q) for v in matrix[row]]
    elif kind == 'shear':
        _, dst, src, coefficient = event
        if inverse:
            coefficient = -coefficient
        matrix[dst] = [p_add(a, b, coefficient) for a, b in zip(matrix[dst], matrix[src], strict=True)]
    elif kind == 'turn':
        _, a, b = event
        old_a, old_b = matrix[a], matrix[b]
        sign = -1 if inverse else 1
        matrix[a] = [{q: sign * c for q, c in v.items()} for v in old_b]
        matrix[b] = [{q: -sign * c for q, c in v.items()} for v in old_a]
    else:
        raise ValueError('unknown elementary event')


def right_inverse(matrix, event):
    kind = event[0]
    if kind == 'phase':
        _, col, q = event
        q = qneg(q)
        for row in matrix:
            row[col] = p_phase(row[col], q)
    elif kind == 'shear':
        _, dst, src, coefficient = event
        for row in matrix:
            row[src] = p_add(row[src], row[dst], -coefficient)
    elif kind == 'turn':
        _, a, b = event
        for row in matrix:
            old_a, old_b = row[a], row[b]
            row[a] = old_b
            row[b] = {q: -c for q, c in old_a.items()}
    else:
        raise ValueError('unknown inverse event')


def trace_square(matrix):
    out = {}
    for i in range(8):
        for j in range(8):
            out = p_add(out, p_mul(matrix[i][j], matrix[j][i]))
    return out


def evaluate(matrix, address):
    powers = [(1, 0), (0, 1), (-1, 0), (0, -1)]
    out = []
    for row in matrix:
        result = []
        for p in row:
            a = b = 0
            for q, c in p.items():
                u, v = powers[value(q, address)]
                a += c * u
                b += c * v
            result.append((a, b))
        out.append(result)
    return out


def events(context, residual):
    """Transcribe the pinned eight-stream physical projection into elementary gates."""
    out, sites = [], {}
    blocks, stage = {}, None
    for event in context['template']['execution_schedule']:
        kind = event['kind']
        if kind in ('bank_padding_cover_sweep', 'translate_every_live_family'):
            continue
        if kind == 'local_cover_sweep':
            stage = event['stage']
            blocks[stage] = []
        if stage is None:
            raise ValueError('event before first stage')
        blocks[stage].append(event)
    recipe = context['recipe']
    for time, (stage, replica) in enumerate(context['order']):
        for stream, axes in context['hosts'].get(time, ()):
            out.append(('phase', stream, qsum(axes)))
        if replica != 0:
            continue
        for event in blocks[stage]:
            kind = event['kind']
            if kind == 'local_cover_sweep':
                local = next(v for v in context['template']['recipe']
                             if v['kind'] == 'local' and v['stage'] == stage)
                x, y = 2 * local['pair'], 2 * local['pair'] + 1
                for side, stream in enumerate((x, y)):
                    before = parity(recipe['q'], 1 - side) if stage == 0 else qadd(
                        qsum(1 << i for i in range(9 + 8 * (stage - 1))), parity(recipe['q'], -side))
                    out.append(('phase', stream, qneg(before)))
                out.append(('shear', x, y, -1) if local['reverse'] else ('shear', y, x, 1))
                for side, stream in enumerate((x, y)):
                    after = qadd(qsum(1 << i for i in range(9 + 8 * stage)), parity(recipe['q'], -side))
                    out.append(('phase', stream, after))
            elif kind == 'idle_cover_sweep':
                for side, child in enumerate(event['child_indices']):
                    stream = 2 * event['pair'] + side
                    if child in sites:
                        raise ValueError('duplicate child')
                    sites[child] = len(out)
                    out.append(('phase', stream, qsum(residual[child])))
                    out.append(('phase', stream, parity(recipe['idle_children'][child]['translation_after'], 2)))
            elif kind == 'bridge':
                dst, src, coefficient = event['dst'], event['src'], event['coefficient']
                out.extend([('shear', 2 * dst, 2 * src, coefficient),
                            ('shear', 2 * src + 1, 2 * dst + 1, -coefficient)])
            elif kind == 'terminal_Y_translations':
                out.extend(('phase', 2 * pair + 1, parity(recipe['q'], 2)) for pair in event['pairs'])
            elif kind == 'terminal':
                out.extend(('turn', 2 * pair, 2 * pair + 1) for pair in range(event['pairs']))
            else:
                raise ValueError('unknown physical event ' + kind)
    if set(sites) != set(range(20)):
        raise ValueError('incomplete residual sites')
    return out, sites


def required_matrices(operations, sites):
    """At cut k, return g_k A_k W^-1 T A_k^-1 = B_k^-1 T A_k^-1."""
    matrix = identity(qsum(1 << i for i in range(N)))
    for event in reversed(operations):
        left(matrix, event, inverse=True)
    at = {index: child for child, index in sites.items()}
    for k, event in enumerate(operations):
        if k in at:
            required = copy_matrix(matrix)
            left(required, event)
            yield at[k], required
        left(matrix, event)
        right_inverse(matrix, event)
