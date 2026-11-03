"""Check the new joint closure against literal integer prefixes."""
from array import array
from fractions import Fraction
from hashlib import sha256
from itertools import product
from pathlib import Path
import argparse
import json
import sys

from model import (ACTIVE, INACTIVE, construct, need, produce, forward,
                   reverse, check_rows)

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
SOURCE = ROOT / 'research/g20-sparse-port-construction/RESULT.json'
SOURCE_HASH = '44511d9c7da1c88e265f32ba5d77559b92edb6ca1430180231e84727d939d318'


def bind_source(data: bytes) -> None:
    need(sha256(data).hexdigest() == SOURCE_HASH, 'source hash')
    source = json.loads(data)
    ports = source['scale_free_ports']
    record = next(r for r in ports if r['port'] == 8)
    expressions = [[Fraction(i == j) for j in range(8)] for i in range(8)]
    for event in record['inverse']:
        if event[0] == 'SCALE':
            expressions[event[1]] = [Fraction(event[-1]) * v
                                      for v in expressions[event[1]]]
        else:
            need(event[0] == 'ADD', 'declared source operation')
            source_row = expressions[event[1]]
            target = expressions[event[2]]
            expressions[event[2]] = [a + Fraction(event[-1]) * b
                                      for a, b in zip(target, source_row)]
    expected = tuple(map(Fraction, ('-1/4', '0', '-1', '0', '-1', '0', '0', '-1')))
    need(tuple(expressions[1]) == expected, 'literal port8 inverse column1')


def integer_state(values: tuple, modulus: int, scale: int) -> tuple:
    numerator = -values[0] - 4 * sum(values[1:])
    cuts = tuple((numerator - j * modulus) // scale for j in range(-12, 1))
    comparison = sum(int(v >= modulus) << i for i, v in enumerate(values))
    return cuts, comparison


def extend(prefix: tuple, letter: int) -> tuple:
    values, modulus, scale = prefix
    mask, bit = divmod(letter, 2)
    return (tuple(v + scale * ((mask >> i) & 1) for i, v in enumerate(values)),
            modulus + scale * bit, 2 * scale)


def check_edge(tables, prefixes: list, source: int, letter: int, target: int) -> None:
    child = extend(prefixes[source], letter)
    need(integer_state(*child) == tables.states[target], 'integer-prefix edge')


def check_closure(tables) -> tuple:
    count = len(tables.states)
    need(count == 23789 and len(set(tables.states)) == count, 'exact joint state count')
    prefixes = [((0, 0, 0, 0), 0, 1)]
    for state in range(1, count):
        parent, letter = tables.parents[state], tables.incoming[state]
        need(0 <= parent < state and 0 <= letter < 32, 'finite reachability tree')
        child = extend(prefixes[parent], letter)
        need(child[2].bit_length() <= 129, 'bounded prefix witness size')
        prefixes.append(child)
    digest = sha256()
    for source, prefix in enumerate(prefixes):
        need(integer_state(*prefix) == tables.states[source], 'reachable state witness')
        digest.update(json.dumps(tables.states[source], separators=(',', ':')).encode())
        for letter in range(32):
            target = tables.edges[32 * source + letter]
            need(0 <= target < count, 'closure label range')
            check_edge(tables, prefixes, source, letter, target)
    return prefixes, digest.hexdigest()


def check_fibers(tables) -> dict:
    checked, largest = 0, 0
    maxima = []
    for letter in range(32):
        fibers = tables.inverse[letter]
        maximum = max(map(len, fibers.values()))
        maxima.append(maximum)
        need(maximum == tables.maxima[letter], 'declared active maximum')
        for target, fiber in fibers.items():
            need(tuple(sorted(set(fiber))) == fiber, 'distinct ordered predecessors')
            for rank, source in enumerate(fiber):
                need(tables.edges[32 * source + letter] == target, 'inverse edge')
                need(tables.ranks[32 * source + letter] == rank, 'literal inverse rank')
                checked += 1
        largest = max(largest, maximum)
    need(checked == 761248 and largest == 203, 'complete inverse census')
    return dict(inverse_edges=checked, active_maximum=largest,
                row_history_values=16 * largest, maxima=maxima)


def encode_rows(inputs: tuple, modulus: int, length: int) -> tuple:
    return tuple(tuple((v >> i) & 1 for v in inputs) + ((modulus >> i) & 1,)
                 for i in range(length))


def oracle(inputs: tuple, modulus: int) -> int:
    numerator = -inputs[0] - 4 * (inputs[2] + inputs[4] + inputs[7])
    low = (numerator * pow(4, -1, modulus)) % modulus
    carry, remainder = divmod(numerator - 4 * low, modulus)
    need(remainder == 0 and -16 <= carry <= 12, 'direct carry envelope')
    return ((carry + 16) & 31) | 32


def letter_row(letter: int) -> tuple:
    mask, bit = divmod(letter, 2)
    row = [0] * 9
    row[8] = bit
    for i, j in enumerate(ACTIVE):
        row[j] = (mask >> i) & 1
    for i, j in enumerate(INACTIVE):
        row[j] = ((mask ^ 10) >> i) & 1
    return tuple(row)


def check_packets(tables) -> dict:
    canonical, dirty_cases, invalid = 0, 0, 0
    for modulus in (1, 3, 5):
        for active in product(range(modulus), repeat=4):
            inputs = [0] * 8
            for j, value in zip(ACTIVE, active):
                inputs[j] = value
            for i, j in enumerate(INACTIVE):
                inputs[j] = i % modulus
            rows = encode_rows(tuple(inputs), modulus, modulus.bit_length())
            result, bits = produce(tables, rows)
            need(result == oracle(tuple(inputs), modulus), 'independent carry oracle')
            need(bits <= (3248 ** len(rows) - 1).bit_length(), 'history capacity')
            canonical += 1
    for active in product(range(3), repeat=4):
        inputs = [0] * 8
        for j, value in zip(ACTIVE, active):
            inputs[j] = value
        rows = encode_rows(tuple(inputs), 3, 2)
        expected = oracle(tuple(inputs), 3)
        for dirty in range(64):
            need(produce(tables, rows, dirty)[0] == dirty ^ expected, 'dirty output')
            dirty_cases += 1
    for letters in product(range(32), repeat=3):
        rows = tuple(letter_row(letter) for letter in letters)
        inputs = tuple(sum(row[j] << i for i, row in enumerate(rows)) for j in range(8))
        modulus = sum(row[8] << i for i, row in enumerate(rows))
        valid = rows[0][8] == rows[-1][8] == 1 and all(v < modulus for v in inputs)
        result, _ = produce(tables, rows)
        need(bool(result & 32) == valid, 'canonical validity from literal integers')
        invalid += int(not valid)
    return dict(canonical_packets=canonical, dirty_outputs=dirty_cases,
                arbitrary_three_row_streams=32768, invalid_streams=invalid)


def check_long(tables) -> dict:
    lengths = (1, 2, 3, 8, 31, 127, 4097)
    cases, maximum_bits = 0, 0
    for length in lengths:
        modulus = (1 << length) - 1
        inputs = tuple((modulus * (j + 1)) // 9 for j in range(8))
        rows = encode_rows(inputs, modulus, length)
        for dirty in (0, 23, 63):
            result, bits = produce(tables, rows, dirty)
            need(result == dirty ^ oracle(inputs, modulus), 'long integer oracle')
            need(bits <= (3248 ** length - 1).bit_length(), 'long history capacity')
            maximum_bits = max(maximum_bits, bits)
            cases += 1
    need(produce(tables, ())[0] & 32 == 0, 'empty stream invalid and restored')
    return dict(long_cases=cases, longest_rows=max(lengths),
                largest_observed_history_bits=maximum_bits)


def rejecting_controls(tables, prefixes: list, data: bytes) -> list:
    controls = []
    try:
        bind_source(data + b' ')
    except ValueError:
        controls.append('bad_source_hash')
    else:
        raise ValueError('changed source did not reject')
    try:
        check_edge(tables, prefixes, 0, 0, 1)
    except ValueError:
        controls.append('bad_prefix_edge')
    else:
        raise ValueError('changed edge did not reject')
    bad_rows = [('nonbinary_row', ((0,) * 8 + (2,),)),
                ('boolean_row', ((False,) * 9,)),
                ('short_row', ((0,) * 8,)), ('mutable_rows', []),
                ('row_limit', ((0,) * 9,) * 4098)]
    for name, rows in bad_rows:
        try:
            check_rows(rows)
        except ValueError:
            controls.append(name)
        else:
            raise ValueError('bad rows did not reject: ' + name)
    for name, dirty in [('negative_dirty', -1), ('oversize_dirty', 64)]:
        try:
            produce(tables, (), dirty)
        except ValueError:
            controls.append(name)
        else:
            raise ValueError('bad dirty output did not reject: ' + name)
    rows = ((0,) * 8 + (1,),)
    work = forward(tables, rows)
    bad = work[:-1] + (work[-1] + 3248,)
    try:
        reverse(tables, rows, bad)
    except ValueError:
        controls.append('unpaid_history_capacity')
    else:
        raise ValueError('nonzero incoming history did not reject')
    return controls


def edge_hash(edges: array) -> str:
    canonical = array('H', edges)
    need(canonical.itemsize == 2, '16-bit table export cells')
    if sys.byteorder == 'little':
        canonical.byteswap()
    return sha256(canonical.tobytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--emit', action='store_true', help='generate a new receipt on stdout')
    args = parser.parse_args()
    need(SOURCE.stat().st_size == 212442, 'bounded source size')
    data = SOURCE.read_bytes()
    bind_source(data)
    tables = construct()
    prefixes, state_hash = check_closure(tables)
    report = dict(status='PASS_G20_INITIALIZED_JOINT_STATE',
                  claim_type='finite construction certificate with scoped all-width proof',
                  joint_active_states=len(tables.states),
                  main_state_bits=(len(tables.states) - 1).bit_length() + 4,
                  active_letters=32, forward_edges=len(tables.edges),
                  state_sha256=state_hash, edge_sha256=edge_hash(tables.edges),
                  source_sha256=sha256(data).hexdigest(),
                  model_sha256=sha256((PACKAGE / 'model.py').read_bytes()).hexdigest(),
                  verifier_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
    report.update(check_fibers(tables))
    report.update(check_packets(tables))
    report.update(check_long(tables))
    report['rejecting_controls'] = rejecting_controls(tables, prefixes, data)
    report['ideal_packed_static_table_bits'] = 53 * len(tables.edges) + 480 + 8 * len(tables.states)
    if not args.emit:
        need(report == json.loads((PACKAGE / 'RESULT.json').read_text()), 'stored receipt equality')
    print(json.dumps(report, sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
