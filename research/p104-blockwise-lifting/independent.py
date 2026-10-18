#!/usr/bin/env python3
"""Independent blocked integer-lifting identity checks (stdlib only).

Source semantics were read from pinned b12bbaeb5ca2e83f15433fc2dd0ba3b766595281,
but no predecessor or proposed implementation is imported. Apache-2.0.
Prepared with OpenAI Codex assistance; finite evidence, not a kernel proof.
The ideal backend below is a direct exact numerator oracle, not a cheap child.
"""

import hashlib
import itertools
import json
import random
from fractions import Fraction
from pathlib import Path


def need(ok, message):
    if not ok:
        raise ValueError(message)


def plus(a, b):
    return tuple((x + u, y + v) for (x, y), (u, v) in zip(a, b))


def scale(a, m):
    return tuple((m*x, m*y) for x, y in a)


def magnitude(a):
    return max((abs(t) for z in a for t in z), default=0)


def pair(a, b, inverse=False):
    """Independent closed output formula: average floor, difference ceil/floor."""
    sx, sy = (a[0] + b[0]) // 2, (a[1] + b[1]) // 2
    dx, dy = a[0] - b[0], a[1] - b[1]
    dx, dy = (dy, -dx) if inverse else (-dy, dx)
    return ((sx - ((-dx)//2), sy - ((-dy)//2)),
            (sx - dx//2, sy - dy//2))


def lift(value, axes, inverse=False):
    out = list(value)
    initial = magnitude(out)
    for j, bit in enumerate(reversed(axes) if inverse else axes, 1):
        for x in range(len(out)):
            if not (x >> bit) & 1:
                y = x ^ (1 << bit)
                a, b = out[x], out[y]
                # Literal temporary magnitudes also obey this same stage bound.
                need(max(abs(a[0]-b[0]), abs(a[1]-b[1]))
                     <= 2*magnitude((a, b)), 'difference width')
                out[x], out[y] = pair(a, b, inverse)
        need(magnitude(out) <= (1 << j)*initial, 'literal stage width')
    return tuple(out)


def ideal(value, axes, inverse=False, require_integral=True):
    """Raw rational butterfly numerators / 2**len(axes), no lifting calls."""
    out = list(value)
    sign = -1 if inverse else 1
    for bit in reversed(axes) if inverse else axes:
        for x in range(len(out)):
            if not (x >> bit) & 1:
                y = x ^ (1 << bit)
                ar, ai = out[x]
                br, bi = out[y]
                out[x] = (ar+br-sign*(ai-bi), ai+bi+sign*(ar-br))
                out[y] = (ar+br+sign*(ai-bi), ai+bi-sign*(ar-br))
    d = 1 << len(axes)
    if require_integral:
        need(all(t % d == 0 for z in out for t in z), 'ideal integrality')
        return tuple((a//d, b//d) for a, b in out)
    return tuple((Fraction(a, d), Fraction(b, d)) for a, b in out)


def split_block(value, axes, inverse=False, guard_delta=0):
    g = len(axes)//2 + 1 + guard_delta
    modulus = 1 << g
    low = tuple((a % modulus, b % modulus) for a, b in value)
    high = plus(value, scale(low, -1))
    wide = ideal(high, axes, inverse, require_integral=(guard_delta == 0))
    narrow = lift(low, axes, inverse)
    need(magnitude(narrow) < (1 << (g+len(axes))), 'narrow width')
    return plus(wide, narrow)


def compositions(rank):
    for cuts in range(1 << (rank-1)):
        parts, start = [], 0
        for end in range(1, rank):
            if cuts >> (end-1) & 1:
                parts.append(end-start)
                start = end
        yield tuple(parts + [rank-start])


def blocks(parts):
    out, start = [], 0
    for size in parts:
        out.append(tuple(range(start, start+size)))
        start += size
    return tuple(out)


def blocked(value, parts, inverse=False, wrong_block_order=False):
    schedule = blocks(parts)
    if inverse and not wrong_block_order:
        schedule = tuple(reversed(schedule))
    for axes in schedule:
        value = split_block(value, axes, inverse)
    return value


def clean_add(value, target, axes, inverse=False, sign=1):
    """Model the clean additive interface with an exact clean ideal oracle.

    The oracle call's implementation/space/child bill is NOT supplied here.
    Both extraction copies use XOR and are undone; narrow lift is reversed.
    """
    g = len(axes)//2 + 1
    modulus = 1 << g
    q = [(0, 0) for _ in value]
    t = [(0, 0) for _ in value]
    for j, (a, b) in enumerate(value):
        q[j] = (q[j][0] ^ (a//modulus), q[j][1] ^ (b//modulus))
        t[j] = (t[j][0] ^ (a % modulus), t[j][1] ^ (b % modulus))
    # Clean, additive A(q)=2**g U(q) is an explicit conditional interface.
    out = plus(target, scale(ideal(scale(q, modulus), axes, inverse), sign))
    t = list(lift(t, axes, inverse))
    out = plus(out, scale(t, sign))
    t = list(lift(t, axes, not inverse))
    for j, (a, b) in enumerate(value):
        t[j] = (t[j][0] ^ (a % modulus), t[j][1] ^ (b % modulus))
        q[j] = (q[j][0] ^ (a//modulus), q[j][1] ^ (b//modulus))
    need(all(a == b == 0 for a, b in q+t), 'clean interface restoration')
    return out


def clean_inplace(value, axes, inverse=False):
    """Compute F, swap, subtract its literal inverse; all work returns zero."""
    zero = tuple((0, 0) for _ in value)
    y = clean_add(value, zero, axes, inverse)
    # The swap leaves x=F(value), y=value.
    x, y = y, value
    y = clean_add(x, y, axes, not inverse, -1)
    need(y == zero, 'in-place clean target')
    return x


def fixtures(rank, inactive=0):
    n = 1 << (rank+inactive)
    rng = random.Random(45316 + 97*rank + inactive)
    yield tuple((0, 0) for _ in range(n))
    yield tuple((1 if j == 0 else 0, -1 if j == n-1 else 0) for j in range(n))
    yield tuple(((17*j+3) % 31 - 15, (23*j+7) % 29 - 14) for j in range(n))
    for width in (1, 31, 257, 4096):
        yield tuple(((1 if rng.getrandbits(1) else -1)*rng.getrandbits(width),
                     (1 if rng.getrandbits(1) else -1)*rng.getrandbits(width))
                    for _ in range(n))


def trunc_half(x):
    return x//2 if x >= 0 else -((-x)//2)


def wrong_floor_pair(a, b, inverse=False):
    dx, dy = a[0]-b[0], a[1]-b[1]
    sx, sy = b[0]+trunc_half(dx), b[1]+trunc_half(dy)
    dx, dy = (dy, -dx) if inverse else (-dy, dx)
    br, bi = sx-trunc_half(dx), sy-trunc_half(dy)
    return ((br+dx, bi+dy), (br, bi))


def control_witnesses():
    floor_witness = None
    for flat in itertools.product(range(-2, 3), repeat=4):
        v = (flat[:2], flat[2:])
        low = tuple((a % 2, b % 2) for a, b in v)
        high = plus(v, scale(low, -1))
        mutant = plus(ideal(high, (0,)), wrong_floor_pair(*low))
        if mutant != lift(v, (0,)):
            floor_witness = dict(input=v, expected=lift(v, (0,)), mutant=mutant)
            break
    need(floor_witness is not None, 'wrong floor control did not fail')
    v = ((3, 0), (0, 0), (0, 0), (0, 0))
    expected, mutant = lift(v, (0, 1)), split_block(v, (0, 1), guard_delta=-1)
    need(expected != mutant, 'insufficient guard control did not fail')
    guard_witness = dict(input=v, expected=expected,
                         mutant=tuple((int(a), int(b)) for a, b in mutant))
    reverse_witness = None
    for j in range(4):
        v = tuple((int(j == k), 0) for k in range(4))
        sent = blocked(v, (1, 1))
        mutant = blocked(sent, (1, 1), inverse=True, wrong_block_order=True)
        if mutant != v:
            reverse_witness = dict(input=v, sent=sent, expected=v, mutant=mutant)
            break
    need(reverse_witness is not None, 'block reverse control did not fail')
    return dict(wrong_floor=floor_witness, insufficient_guard=guard_witness,
                wrong_inverse_block_order=reverse_witness)


def main():
    counters = dict(compositions=0, partition_fixture_directions=0,
                    exhaustive_vectors_rank1=0, exhaustive_vectors_rank2=0,
                    exhaustive_partition_directions=0, equivariance_directions=0,
                    clean_add_directions=0, clean_inplace_directions=0,
                    inactive_axis_partition_directions=0,
                    uniform_guard_sharpness_directions=0)
    for rank in range(1, 8):
        axes = tuple(range(rank))
        parts_all = tuple(compositions(rank))
        counters['compositions'] += len(parts_all)
        # Exact independent witnesses for failure at one fewer guard bit.
        impulse = tuple((int(j == 0), 0) for j in range(1 << rank))
        x = impulse if rank % 2 == 0 else scale(impulse, 0)
        delta = scale(impulse, 1 << (rank//2))
        for inverse in (False, True):
            actual_delta = plus(lift(plus(x, delta), axes, inverse),
                                scale(lift(x, axes, inverse), -1))
            ideal_delta = ideal(delta, axes, inverse, require_integral=False)
            need(actual_delta != ideal_delta, 'guard sharpness witness')
            counters['uniform_guard_sharpness_directions'] += 1
        for v in fixtures(rank):
            for inverse in (False, True):
                expected = lift(v, axes, inverse)
                need(lift(expected, axes, not inverse) == v, 'literal inverse')
                for parts in parts_all:
                    need(blocked(v, parts, inverse) == expected, 'blocked identity')
                    counters['partition_fixture_directions'] += 1
                # Test clean target with arbitrary signed incoming accumulation.
                target = tuple((11*j-7, -13*j+2) for j in range(len(v)))
                need(clean_add(v, target, axes, inverse) == plus(target, expected),
                     'arbitrary additive target')
                counters['clean_add_directions'] += 1
                need(clean_inplace(v, axes, inverse) == expected, 'clean in-place')
                counters['clean_inplace_directions'] += 1
                z = tuple((3*j-5, 7-2*j) for j in range(len(v)))
                delta = scale(z, 1 << (rank//2+1))
                need(lift(plus(v, delta), axes, inverse)
                     == plus(expected, ideal(delta, axes, inverse)), 'equivariance')
                counters['equivariance_directions'] += 1
        for v in fixtures(rank, inactive=1):
            for inverse in (False, True):
                expected = lift(v, axes, inverse)
                for parts in parts_all:
                    need(blocked(v, parts, inverse) == expected, 'inactive axis')
                    counters['inactive_axis_partition_directions'] += 1
    for rank, radius in ((1, 3), (2, 1)):
        axes = tuple(range(rank))
        for flat in itertools.product(range(-radius, radius+1), repeat=2*(1 << rank)):
            v = tuple(zip(flat[::2], flat[1::2]))
            counters['exhaustive_vectors_rank'+str(rank)] += 1
            for inverse in (False, True):
                expected = lift(v, axes, inverse)
                need(lift(expected, axes, not inverse) == v, 'exhaustive inverse')
                for parts in compositions(rank):
                    need(blocked(v, parts, inverse) == expected, 'exhaustive block')
                    counters['exhaustive_partition_directions'] += 1
    receipt = dict(status='PASS_INDEPENDENT_BLOCK_LIFTING', source_commit=
                   'b12bbaeb5ca2e83f15433fc2dd0ba3b766595281',
                   checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                   coverage=counters, controls=control_witnesses(),
                   limits=['finite rank/fixture checks only; proof is separate',
                           'direct exact ideal oracle; no fast recursive backend',
                           'clean owned work only; no arbitrary dirty-helper admission',
                           'no physical tape, recursive-child, or kappa claim'])
    print(json.dumps(receipt, sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
