"""Exact checks of the new allocation, not a replay of a predecessor suite.

Produced by Nick Petalas. Apache-2.0.
"""
import argparse
from dataclasses import replace
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import platform
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from model import allocate, drop_word, exact_run, lift_word, monomial, require

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent


def multiply(left, right):
    a, b = left
    c, d = right
    return a * c - b * d, a * d + b * c


def direct(values, axes):
    """Literal dense tensor entries, independent of butterfly arithmetic."""
    plus = [(1, 0)]
    minus = [(1, 0)]
    for _ in range(axes):
        plus.append(multiply(plus[-1], (1, 1)))
        minus.append(multiply(minus[-1], (1, -1)))
    weights = tuple(multiply(plus[axes - d], minus[d]) for d in range(axes + 1))
    output = []
    for row in range(1 << axes):
        real = imag = 0
        for column in range(1 << axes):
            term = multiply(weights[(row ^ column).bit_count()], values[column])
            real += term[0]
            imag += term[1]
        output.append((real, imag))
    return tuple(output), 1 << axes


def words(axes, mode):
    size = 1 << axes
    if mode == 0:
        identity = (tuple(range(size)), (0,) * size)
        return identity, identity
    entrance = (tuple(i ^ (size - 1) for i in range(size)),
                tuple(i.bit_count() % 4 for i in range(size)))
    exit_word = (tuple((i + 1) % size for i in range(size)),
                 tuple((3 * i + 2) % 4 for i in range(size)))
    return entrance, exit_word


def compare(values, h, axes, mode):
    plan = allocate(h, 1, axes)
    entrance, exit_word = words(axes, mode)
    actual = exact_run(values, plan, entrance, exit_word)
    numerator, denominator = direct(monomial(values, entrance), axes)
    numerator = monomial(numerator, exit_word)
    require(all(a * denominator == n * (1 << plan.lift)
                for pair, ref in zip(actual, numerator, strict=True)
                for a, n in zip(pair, ref, strict=True)), 'exact complete endpoint')
    accepted = overflowed = 0
    for pair, ref in zip(actual, numerator, strict=True):
        for value, target in zip(pair, ref, strict=True):
            expected = (2 * target + denominator) // (2 * denominator)
            cap = 1 << (h - 1)
            if -cap <= expected < cap:
                require(drop_word(value, plan) == expected, 'once-rounded endpoint')
                accepted += 1
            else:
                try:
                    drop_word(value, plan)
                except OverflowError:
                    overflowed += 1
                else:
                    raise ValueError('missing final overflow')
    return accepted, overflowed


def small_census():
    counts = {'vectors': 0, 'fitting_components': 0, 'overflow_components': 0}
    for axes in (1, 2):
        size = 1 << axes
        for flat in product(range(-2, 2), repeat=2 * size):
            values = tuple(zip(flat[::2], flat[1::2], strict=True))
            for mode in (0, 1):
                accepted, overflowed = compare(values, 2, axes, mode)
                counts['vectors'] += 1
                counts['fitting_components'] += accepted
                counts['overflow_components'] += overflowed
    require(counts['vectors'] == 131584, 'complete small domain')
    require(counts['fitting_components'] + counts['overflow_components'] == 1050624,
            'complete component census')
    return counts


def boundary_fixtures():
    count = components = 0
    for axes in range(1, 9):
        size = 1 << axes
        for h in (2, 3, 9, 65, 257):
            cap = 1 << (h - 1)
            fixtures = (
                tuple((-cap, -cap) for _ in range(size)),
                tuple((cap - 1, -cap) for _ in range(size)),
                tuple(((-cap, cap - 1)[i % 2], (-cap, cap - 1)[i.bit_count() % 2])
                      for i in range(size)),
                tuple((1 if i == 0 else 0, 0) for i in range(size)),
            )
            for values in fixtures:
                for mode in (0, 1):
                    accepted, overflowed = compare(values, h, axes, mode)
                    count += 1
                    components += accepted + overflowed
    return {'vectors': count, 'components': components}


def allocations():
    count = strictly_smaller = 0
    for h in range(2, 130):
        for rank in range(1, 9):
            for columns in range(1, 33):
                plan = allocate(h, rank, columns)
                g = rank * columns
                old = h + g + (g + 2) // 2 + 1
                saving = g // 2 + (1 if g % 2 == 0 else 0)
                require(old - plan.width == saving, 'exact width saving')
                require(plan.width == h + plan.lift + plan.extension, 'codec extent')
                require(saving >= 0 and (saving > 0) == (g > 1), 'strict gain domain')
                count += 1
                strictly_smaller += int(saving > 0)
    plan = allocate(2, 8, 1)
    old_volume = 4096 * 6 * (16 + 1)
    new_volume = 4096 * 6 * (plan.width + 1)
    require((old_volume, new_volume, old_volume - new_volume) == (417792, 294912, 122880),
            'complete minimum-geometry record count')
    return {'cases': count, 'strictly_smaller': strictly_smaller,
            'g8_h2_volumes': [old_volume, new_volume], 'bits_saved': old_volume - new_volume}


def codecs():
    lifts = drops = overflows = 0
    for h in range(2, 9):
        for axes in range(1, 9):
            plan = allocate(h, 1, axes)
            cap = 1 << (h - 1)
            for value in range(-cap, cap):
                encoded = lift_word(value, plan)
                integer = int(encoded, 2) - (int(encoded[0]) << plan.width)
                require(integer == value * (1 << plan.lift), 'physical low zeros and sign extension')
                require(drop_word(integer, plan) == value, 'exact codec round trip')
                lifts += 1
            for value in range(-(cap + 1) << plan.lift, (cap + 1) << plan.lift):
                expected = (2 * value + (1 << plan.lift)) // (2 << plan.lift)
                try:
                    actual = drop_word(value, plan)
                except OverflowError:
                    require(not -cap <= expected < cap, 'true overflow only')
                    overflows += 1
                else:
                    require(actual == expected and -cap <= actual < cap, 'all signed half ties')
                    drops += 1
    return {'lift_round_trips': lifts, 'drop_values': drops, 'overflow_values': overflows}


def controls():
    rejected = 0
    for args in ((1, 1, 1), (2, 0, 1), (2, 9, 1), (2, 1, 0),
                 (True, 1, 1), (2, True, 1), (2, 1, True), (4097, 1, 1)):
        try:
            allocate(*args)
        except ValueError:
            rejected += 1
        else:
            raise ValueError('accepted invalid allocation')
    insufficient = 0
    for axes in range(1, 9):
        plan = allocate(2, 1, axes)
        values = ((1, 0),) + ((0, 0),) * ((1 << axes) - 1)
        entrance, exit_word = words(axes, 0)
        try:
            exact_run(values, replace(plan, lift=plan.lift - 1), entrance, exit_word)
        except ValueError as error:
            require(str(error) == 'nonintegral Gaussian half', 'insufficient lift discriminator')
            insufficient += 1
        else:
            raise ValueError('accepted insufficient lift')
    plan = allocate(2, 1, 1)
    identity, _ = words(1, 0)
    exact = exact_run(((1, 0), (0, 0)), plan, identity, ((0, 1), (2, 2)))
    final = tuple(tuple(drop_word(v, plan) for v in pair) for pair in exact)
    early = ((-1, -1), (-1, 0))
    require(final == ((0, 0), (0, 1)) and final != early, 'round after negative exit')
    return {'invalid_allocations': rejected, 'insufficient_lift_rejections': insufficient,
            'rounding_order_discriminators': 1}


def source_hashes():
    data = json.loads((HERE / 'SOURCES.json').read_text())
    result = {}
    require(len(data['files']) <= 16, 'bounded source inventory')
    for row in data['files']:
        if row['usage'] == 'input':
            digest = sha256((ROOT / row['path']).read_bytes()).hexdigest()
            require(digest == row['sha256'], 'unchanged cited source: ' + row['path'])
            result[row['path']] = digest
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--emit', action='store_true', help='print computed hash-bound receipt')
    args = parser.parse_args()
    require(sys.version_info >= (3, 12), 'CPython 3.12 or newer')
    sources = source_hashes()
    result = {'claim_type': 'scoped proof with exact finite corroboration',
              'python': platform.python_version(), 'allocations': allocations(),
              'small_census': small_census(), 'boundary_fixtures': boundary_fixtures(),
              'codecs': codecs(), 'controls': controls(), 'source_sha256': sources}
    files = sorted(path for path in HERE.iterdir() if path.is_file())
    require(len(files) <= 16, 'bounded package inventory')
    result['package_sha256'] = {path.name: sha256(path.read_bytes()).hexdigest() for path in files}
    if args.emit:
        print(json.dumps(result, sort_keys=True, indent=2))
    print('PASS_SHARP_ROUNDED_MOVE_ALLOCATION')


if __name__ == '__main__':
    main()
