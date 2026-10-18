#!/usr/bin/env python3
"""Exact finite programs for the phase-accumulator experiment.

Gareth Davidson (bitplane), with substantial OpenAI Codex assistance.
Apache-2.0. This is a classical linear-array model, not a quantum runtime claim.
"""
from dataclasses import dataclass
from hashlib import sha256
import json


def require(condition, message):
    if not condition:
        raise ValueError(message)


@dataclass(frozen=True)
class Op:
    kind: str
    a: tuple = ()
    b: tuple = ()
    power: int = 0

    def record(self):
        return [self.kind, list(self.a), list(self.b), self.power]


def phase(axes, power=1):
    return [Op('phase', tuple(axes), power=power)]


def scale_b(power):
    return [] if power == 0 else [Op('scale_b', power=power)]


def cx(source, target):
    source, target = tuple(source), tuple(target)
    require(len(source) == len(target) and set(source).isdisjoint(target), 'invalid packed XOR')
    return [Op('xor', source, target)]


def c_word(axes, depth=0, inverse=False):
    """C tensor axes; recurse through the explicit C/Q decomposition."""
    axes = tuple(axes)
    require(axes and len(set(axes)) == len(axes) and depth >= 0, 'invalid C call')
    if inverse:
        # C^-1 = -i Z C Z, independently on each active axis.
        return phase(axes, 2) + c_word(axes, depth) + phase(axes, 2) + [Op('global_phase', power=-len(axes))]
    if depth == 0 or len(axes) % 3:
        return [Op('C', axes)]
    f = len(axes) // 3
    p, u, v = axes[:f], axes[f:2*f], axes[2*f:]
    # Physical M = L^-T; Fourier labels become (a+b+c,a+c,b+c).
    chart = cx(v, u) + cx(u, v) + cx(u, p) + cx(p, v)
    return (chart + c_word(p, depth-1) + q_word(u, v, depth-1)
            + [Op('translate', axes)] + list(reversed(chart)))


def h_word(axes, depth=0, inverse=False):
    """Dyadic H0=(1/2)[[1,1],[1,-1]], with its literal priced inverse."""
    axes = tuple(axes)
    if inverse:
        return (scale_b(-len(axes)) + phase(axes, -1)
                + c_word(axes, depth, inverse=True) + phase(axes, -1))
    return phase(axes) + c_word(axes, depth) + phase(axes) + scale_b(len(axes))


def q_word(x, y, depth=0):
    """Fourier multiplier (-1)^(u dot v), using two actual C children."""
    x, y = tuple(x), tuple(y)
    require(len(x) == len(y) and set(x).isdisjoint(y), 'invalid Q call')
    return h_word(x, depth, inverse=True) + cx(x, y) + h_word(x, depth)


def q_walsh_word(x, y):
    """Same Q via one width-2f C call; width is still 2f, not f.

    D(x,y)=(-1)^(x dot y), and Q=D Swap (2^f H0_(2f)) D.
    The scalar 2^f*b^(2f)=(-i)^f is retained exactly.
    """
    x, y = tuple(x), tuple(y)
    require(len(x) == len(y) and set(x).isdisjoint(y), 'invalid Walsh Q')
    diagonal = phase(x)+phase(y)+cx(x,y)+phase(y,-1)+cx(x,y)
    swap = cx(x,y)+cx(y,x)+cx(x,y)
    return (diagonal+phase(x+y)+c_word(x+y)+phase(x+y)+swap+diagonal
            +[Op('global_phase', power=-len(x))])


def accumulator_word(f, aggregate=False, half=False, depth=0):
    """Two open Pauli words close to a phase; all bank lanes are arbitrary.

    The aggregate mutant shares one bank bit across all f columns.
    """
    require(f > 0, 'positive column count required')
    x, y = tuple(range(f)), tuple(range(f, 2*f))
    bank = (2*f,) if aggregate else tuple(range(2*f, 3*f))
    if aggregate:
        a = [Op('xor', bank, (j,)) for j in x]
        b = [Op('xor', bank, (j,)) for j in y]
    else:
        a, b = cx(bank, x), cx(bank, y)
    opened = a + h_word(bank, depth) + b + h_word(bank, depth, inverse=True)
    return opened if half else opened + opened


def inverse_word(word):
    result = []
    for op in reversed(word):
        if op.kind == 'C':
            result += c_word(op.a, inverse=True)
        elif op.kind in ('phase', 'global_phase', 'scale_b'):
            result.append(Op(op.kind, op.a, op.b, -op.power))
        else:
            require(op.kind in ('xor', 'translate'), 'unknown inverse operation')
            result.append(op)
    return result


def denominator_budget(word):
    return sum(len(op.a) if op.kind == 'C' else max(op.power, 0) if op.kind == 'scale_b' else 0
               for op in word)


def word_digest(word):
    return sha256(json.dumps([op.record() for op in word], separators=(',', ':')).encode()).hexdigest()


def rotate(re, im, power):
    p = power % 4
    if p == 0:
        return re, im
    if p == 1:
        return -im, re
    if p == 2:
        return -re, -im
    return im, -re


def permutation(op, address):
    if op.kind == 'translate':
        return address ^ sum(1 << bit for bit in op.a)
    require(op.kind == 'xor', 'not a permutation')
    return address ^ sum(((address >> source) & 1) << target for source, target in zip(op.a, op.b))


def apply(word, real, imag, trace=None):
    """Mutate Gaussian-integer grid data. Every halving must be exact."""
    require(len(real) == len(imag) and len(real) > 0 and len(real) & (len(real)-1) == 0,
            'power-of-two full array required')
    n = len(real)
    for step, op in enumerate(word):
        if op.kind == 'C':
            for axis in op.a:
                bit = 1 << axis
                for left in range(n):
                    if left & bit:
                        continue
                    right = left | bit
                    ar, ai, br, bi = real[left], imag[left], real[right], imag[right]
                    values = (ar-ai+br+bi, ar+ai-br+bi, ar+ai+br-bi, -ar+ai+br+bi)
                    require(all(v % 2 == 0 for v in values), 'C lost exact grid divisibility')
                    real[left], imag[left], real[right], imag[right] = (v//2 for v in values)
        elif op.kind in ('xor', 'translate'):
            for left in range(n):
                right = permutation(op, left)
                if left < right:
                    real[left], real[right] = real[right], real[left]
                    imag[left], imag[right] = imag[right], imag[left]
        elif op.kind == 'phase':
            mask = sum(1 << bit for bit in op.a)
            for j in range(n):
                real[j], imag[j] = rotate(real[j], imag[j], (j & mask).bit_count()*op.power)
        elif op.kind == 'global_phase':
            for j in range(n):
                real[j], imag[j] = rotate(real[j], imag[j], op.power)
        elif op.kind == 'scale_b':
            for _ in range(abs(op.power)):
                for j in range(n):
                    re, im = real[j], imag[j]
                    if op.power > 0:
                        require((re+im) % 2 == 0 and (im-re) % 2 == 0, 'scale lost exact divisibility')
                        real[j], imag[j] = (re+im)//2, (im-re)//2
                    else:
                        real[j], imag[j] = re-im, re+im
        else:
            raise ValueError('unknown operation '+op.kind)
        if trace is not None:
            trace(step, op, real, imag)
    return real, imag


def gaussian_product(a, b):
    return a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0]


def reference_c_column(bits, axes, column, grid):
    """Closed tensor-kernel formula; no emitted-program execution."""
    n = 1 << bits
    mask = sum(1 << bit for bit in axes)
    real, imag = [0]*n, [0]*n
    require(grid % (1 << len(axes)) == 0, 'reference grid too coarse')
    for row in range(n):
        if (row ^ column) & ~mask:
            continue
        value = (1, 0)
        for axis in axes:
            value = gaussian_product(value, (1, -1 if ((row ^ column) >> axis) & 1 else 1))
        real[row], imag[row] = (v*(grid >> len(axes)) for v in value)
    return real, imag


def reference_q_column(bits, x, y, column, grid):
    """The exact Fourier sum is 2^-f (-1)^(delta_x dot delta_y)."""
    require(len(x) == len(y), 'unequal Q blocks')
    n, f = 1 << bits, len(x)
    mask = sum(1 << bit for bit in (*x, *y))
    real, imag = [0]*n, [0]*n
    require(grid % (1 << f) == 0, 'reference grid too coarse')
    for row in range(n):
        diff = row ^ column
        if diff & ~mask:
            continue
        exponent = sum(((diff >> a) & 1)*((diff >> b) & 1) for a, b in zip(x, y)) % 2
        real[row] = (-1 if exponent else 1)*(grid >> f)
    return real, imag


def reference_open_column(f, column, grid):
    """P=X(v)Z(u): x'=x+c, coefficient 2^-f (-1)^((c'+c).(y'+y))."""
    mask = (1 << f)-1
    x, y, c = column & mask, (column >> f) & mask, column >> (2*f)
    n = 1 << (3*f)
    real, imag = [0]*n, [0]*n
    require(grid % (1 << f) == 0, 'open-state grid too coarse')
    for out_c in range(1 << f):
        for out_y in range(1 << f):
            row = (x ^ c) | (out_y << f) | (out_c << (2*f))
            sign = -1 if ((out_c ^ c) & (out_y ^ y)).bit_count() % 2 else 1
            real[row] = sign*(grid >> f)
    return real, imag


def relabel_word(word, mapping):
    return [Op(op.kind, tuple(mapping[j] for j in op.a), tuple(mapping[j] for j in op.b), op.power)
            for op in word]


def columnwise_bank_word(f, shared=False, close_each=False, reverse_consumer=False):
    """Recursively substitute scalar-column producer/consumer contracts."""
    half = accumulator_word(1, half=True)
    words = [relabel_word(half, {0:j, 1:f+j, 2:2*f if shared else 2*f+j}) for j in range(f)]
    if close_each:
        return [op for word in words for op in word+word]
    opened = [op for word in words for op in word]
    consumers = reversed(words) if reverse_consumer else words
    return opened+[op for word in consumers for op in word]


def check_columns(word, bits, reference, columns=None, checkpoints=None):
    n = 1 << bits
    grid_bits = denominator_budget(word) + bits + 2
    grid = 1 << grid_bits
    selected = range(n) if columns is None else columns
    digest = sha256()
    count = 0
    supports = []
    for column in selected:
        real, imag = [0]*n, [0]*n
        real[column] = grid
        def at_boundary(step, op, real, imag):
            if step in checkpoints:
                require((real, imag) == checkpoints[step](column, grid),
                        f'wrong open-state column {column} at step {step}')
        apply(word, real, imag, trace=at_boundary if checkpoints else None)
        expected = reference(column, grid)
        require((real, imag) == expected, f'wrong complete column {column}')
        supports.append(sum(re != 0 or im != 0 for re, im in zip(real, imag)))
        # Keep the exact integer-grid convention in the digest and receipt.
        for re, im in zip(real, imag):
            digest.update(f'{re}/{grid},{im}/{grid};'.encode())
        count += 1
    result = {'columns': count, 'coefficients': count*n, 'grid_bits': grid_bits,
            'column_support_minmax': [min(supports), max(supports)],
            'matrix_grid_sha256': digest.hexdigest(), 'word_sha256': word_digest(word)}
    if checkpoints:
        result['checkpoint_steps'] = sorted(checkpoints)
        result['checkpoint_columns'] = count*len(checkpoints)
    return result


def rank_binary(rows):
    basis = {}
    for row in rows:
        while row:
            bit = row.bit_length()-1
            if bit not in basis:
                basis[bit] = row
                break
            row ^= basis[bit]
    return len(basis)


def v2(n):
    require(isinstance(n, int) and n > 0, 'positive bank dimension required')
    return (n & -n).bit_length()-1
