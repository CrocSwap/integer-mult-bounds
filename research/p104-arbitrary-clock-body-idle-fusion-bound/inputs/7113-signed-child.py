"""Exact nine-slot signed child on the retained 153-coordinate field layout."""

from collections import Counter
from hashlib import sha256
from pathlib import Path
from random import Random
import argparse
import json

LAYOUT = 153
EXPECTED_PORTS = (15, 17, 27, 34, 35, 42, 47, 55)
NOTE_SHA = '64c70926a8705874f1c9b42a2f703e42cad4e90f927f544458cfdf729540236c'
# Integer numerators over 2 in the exact C gate.
C = (((1, 1), (1, -1)), ((1, -1), (1, 1)))
PHASE = ((1, 0), (0, -1), (-1, 0), (0, 1))


def multiply(x, y):
    a, b = x
    c, d = y
    return a*c - b*d, a*d + b*c


def conjugate(z):
    a, b = z
    return a, -b


def matrix_product(a, b):
    return tuple(tuple(tuple(sum(multiply(a[i][k], b[k][j])[c] for k in range(2))
                             for c in range(2)) for j in range(2)) for i in range(2))


def swap_blocks(label, a, b, width):
    mask = (1 << width)-1
    delta = ((label >> (a*width)) ^ (label >> (b*width))) & mask
    return label ^ (delta << (a*width)) ^ (delta << (b*width))


def permute(label, swaps, width):
    for a, b in swaps:
        label = swap_blocks(label, a, b, width)
    return label


def masks(stage, width):
    return ((1 << width)-1, ((1 << (8*width))-1) << ((9+8*(stage-1))*width))


def descriptor(stage):
    assert 1 <= stage <= 18
    return tuple((j, 8*stage+j) for j in range(1, 9))


def packed_kernel(row, col, width, mutate=None):
    if (row ^ col) >> (9*width):
        return (0, 0)
    result = (1, 0)
    for j in range(9*width):
        result = multiply(result, C[(row >> j) & 1][(col >> j) & 1])
    q = (1 << width)-1
    if (row ^ col) & q and ((row ^ col) & q).bit_count() % 2:
        result = -result[0], -result[1]
    exponent = width if mutate != 'missing multiplicity' else 1
    return multiply(PHASE[exponent % 4] if mutate != 'missing global phase' else (1,0), result)


def separate_kernel(row, col, stage, width):
    q, body = masks(stage, width)
    if (row ^ col) & ~(q | body):
        return (0,0)
    result = (1,0)
    for bit in range(width):
        result = multiply(result, conjugate(C[(row >> bit) & 1][(col >> bit) & 1]))
    start = (9+8*(stage-1))*width
    for bit in range(start, start+8*width):
        result = multiply(result, C[(row >> bit) & 1][(col >> bit) & 1])
    return result


def verify_route(stage, width):
    swaps = descriptor(stage)
    q, body = masks(stage, width)
    front = (1 << (9*width))-1
    assert permute(q | body, swaps, width) == front
    assert permute(q, swaps, width) == q
    for i in range(LAYOUT*width):
        x = 1 << i
        assert permute(permute(x, swaps, width), reversed(swaps), width) == x
    return swaps


def check_finite(stage, width, rng):
    swaps = verify_route(stage, width)
    q, body = masks(stage, width)
    prefix = 9*width
    active = q | body
    parked = rng.getrandbits(LAYOUT*width) & ~active
    if width == 1:
        pairs = ((r,c) for r in range(1<<prefix) for c in range(1<<prefix))
    else:
        pairs = ((rng.getrandbits(prefix), rng.getrandbits(prefix)) for _ in range(1024))
    tests, mutant = 0, Counter()
    for r,c in pairs:
        outer_r = parked | permute(r, reversed(swaps), width)
        outer_c = parked | permute(c, reversed(swaps), width)
        expected = separate_kernel(outer_r, outer_c, stage, width)
        assert packed_kernel(r,c,width) == expected
        if tests < 8:
            for mutation in ('missing global phase','missing multiplicity'):
                mutant[mutation] += packed_kernel(r,c,width,mutation) != expected
        tests += 1
    other = (1 << (LAYOUT*width))-1 & ~active
    spectator = other & -other
    assert spectator and separate_kernel(0,spectator,stage,width) == (0,0)
    assert packed_kernel(0,permute(spectator,swaps,width),width) == (0,0)
    assert mutant['missing global phase']
    assert bool(mutant['missing multiplicity']) == (width != 1)
    return dict(stage=stage, width=width, tested_entries=tests, denominator=2**prefix,
                mutated_entries=dict(mutant), spectators=LAYOUT*width-prefix, swaps=swaps,
                child_rank=9, exponent=width % 4)


def main(note, caller):
    assert sha256(note.read_bytes()).hexdigest() == NOTE_SHA
    text = note.read_text()
    assert r'C^{-1}=-iZCZ' in text and r'C^{\otimes af}' in text
    data = json.loads(caller.read_text())
    ports = tuple(data['types']['B']['ports'])
    assert ports == EXPECTED_PORTS and data['stages'] == 18
    cc = tuple(tuple(conjugate(x) for x in row) for row in C)
    assert matrix_product(C, cc) == (((4,0),(0,0)),((0,0),(4,0)))
    assert matrix_product(C, C) == (((0,0),(4,0)),((4,0),(0,0)))
    rng = Random(0)
    records = [check_finite(stage, width, rng) for stage in (9,10) for width in (1,2,3)]
    print(json.dumps(dict(status='PASS_SIGNED_RANK9_FIELD_OPERATOR', caller_sha=sha256(caller.read_bytes()).hexdigest(),
                          note_sha=NOTE_SHA, logical_layout=LAYOUT, logical_ports=ports,
                          stages=(9,10), field_requests_per_port=4, checks=records), sort_keys=True))


if __name__ == '__main__':
    assert __debug__
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('note', type=Path)
    parser.add_argument('caller', type=Path)
    main(**vars(parser.parse_args()))
