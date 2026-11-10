#!/usr/bin/env python3
"""Normalized-Fraction compiler oracle with a reused signed-pair flow model.

Source-aware independent expected model, not source execution or a fresh blind
implementation. Historical B12S9 factorial/pair mathematics is adapted inline.
"""
import argparse
from fractions import Fraction
from functools import lru_cache
import hashlib
from itertools import combinations_with_replacement, product
import json
from math import factorial, prod
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
CAP = 16 * 1024 * 1024
PINS = {
    'CASES.json': 'ce0152497423d200f0e2c8b83b9efce992c95c92743e238cd5a060306bf329a0',
    'SOURCE-PINS.json': 'f2031ec3b25d187bd924037b63e46943c4d19ece39175e2c58327d7a4f0e59ed',
}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def positive(value, message):
    need(type(value) is int and value > 0, message)
    return value


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'),
                       ensure_ascii=True) + '\n').encode('ascii')


def unique(pairs):
    value = {}
    for key, item in pairs:
        need(key not in value, 'duplicate JSON key')
        value[key] = item
    return value


def no_real(token):
    raise ValueError('float/nonfinite JSON token: ' + token)


def decode(raw):
    need(len(raw) <= CAP, 'JSON byte cap')
    return json.loads(raw, object_pairs_hook=unique,
                      parse_float=no_real, parse_constant=no_real)


def read_raw(path, cap=CAP):
    with path.open('rb') as handle:
        raw = handle.read(cap + 1)
    need(len(raw) <= cap, 'input byte cap: ' + str(path))
    return raw


def authenticate():
    metadata = {}
    for name, expected in PINS.items():
        raw = read_raw(HERE / name)
        need(hashlib.sha256(raw).hexdigest() == expected, 'metadata drift: ' + name)
        metadata[name] = decode(raw)
    sources = {}
    for row in metadata['SOURCE-PINS.json']['objects']:
        name = row['local_path']
        need(type(name) is str and not Path(name).is_absolute()
             and '..' not in Path(name).parts and name not in sources,
             'safe unique source path')
        size = positive(row['bytes'], 'source byte length')
        raw = read_raw(HERE / name, size)
        blob = b'blob ' + str(len(raw)).encode('ascii') + b'\0' + raw
        need(len(raw) == size and hashlib.sha256(raw).hexdigest() == row['sha256']
             and hashlib.sha1(blob).hexdigest() == row['git_blob'],
             'source byte/Git drift: ' + name)
        sources[name] = raw
    need(len(sources) == 6, 'six source objects')
    return metadata['CASES.json'], sources


def inventory(rows, minimum):
    need(type(rows) is list and rows, 'nonempty inventory list')
    result = []
    for pair in rows:
        need(type(pair) is list and len(pair) == 2, 'rank/count pair')
        rank = positive(pair[0], 'positive integer rank')
        count = positive(pair[1], 'positive integer multiplicity')
        need(rank >= minimum, 'inventory rank bound')
        result.append((rank, count))
    need(len({rank for rank, count in result}) == len(result), 'distinct ranks')
    return tuple(sorted(result))


@lru_cache(None)
def multisets(targets, degree):
    result = []
    for letters in combinations_with_replacement(range(len(targets)), degree):
        powers = tuple(letters.count(i) for i in range(len(targets)))
        weight = factorial(degree) // prod(factorial(a) for a in powers)
        weight *= prod(count ** a for (rank, count), a in zip(targets, powers))
        column = prod(rank ** a for (rank, count), a in zip(targets, powers))
        result.append((column, weight))
    return tuple(result)


def paid_words(paid, depth):
    for word in product(paid, repeat=depth):
        yield prod(r for r, count in word), prod(count for r, count in word)


def add(histogram, rank, count):
    need(type(rank) is int and rank > 0 and type(count) is int and count > 0,
         'positive whole flow contribution')
    histogram[rank] = histogram.get(rank, 0) + count


def pair_edges(targets, paid, degree, rho, paths, cap, sources, exits):
    for column, coefficient in multisets(targets, degree):
        z = rho * column
        for target, target_count in targets:
            parent = target * z <= cap
            for rank, paid_count in paid:
                child = rank * z <= cap
                count = paths * coefficient * target_count * paid_count
                if parent and not child:
                    add(exits, target * rank * z, count)
                elif child and not parent:
                    add(sources, target * rank * z, count)


def flow_recipe(targets, paid, cap):
    height, least = 0, 1
    while least * targets[0][0] <= cap:
        height += 1
        least *= targets[0][0]
    sources, exits = {}, {}
    for column, weight in multisets(targets, height):
        if column <= cap:
            for rank, count in targets:
                add(sources, rank * column, weight * count)
    units = columns = 0
    for depth in range(height + 1):
        for rho, paths in paid_words(paid, depth):
            for column, weight in multisets(targets, height - depth):
                if rho * column <= cap:
                    units += paths * weight
                    columns += paths * weight * rho * column
            if depth == height:
                if rho <= cap:
                    for rank, count in paid:
                        add(exits, rank * rho, paths * count)
            else:
                pair_edges(targets, paid, height - depth - 1,
                           rho, paths, cap, sources, exits)
    need(sources, 'nonempty complete flow')
    return height, tuple(sorted(sources.items())), tuple(sorted(exits.items())), units, columns


def exact_integer(value, label):
    need(value.denominator == 1 and value.numerator >= 0,
         'nonintegral/negative recovered ' + label)
    return value.numerator


def child_weights(n, sources, exits):
    result = {}
    for rank, count in sources:
        child = n - rank
        need(0 <= child < n, 'source complement descent')
        result[child] = result.get(child, 0) + count
    for child, count in exits:
        need(0 < child < n, 'exit descent')
        result[child] = result.get(child, 0) + count
    return result


def compile_expected(targets, paid, maximum):
    m, W, P = targets[-1][0], sum(c for k, c in targets), sum(c for k, c in paid)
    delta = sum(k * c for k, c in targets) - sum(r * c for r, c in paid)
    need(paid[-1][0] < m <= maximum and delta > 0, 'compiler rank/surplus domain')
    widths = [1] * (maximum + 1)
    normal = {'leaves': [Fraction(e) for e in range(maximum + 1)]}
    normal.update({key: [Fraction(0) for e in range(maximum + 1)]
                   for key in ('units', 'columns', 'slots')})
    vectors = {'widths': widths, 'leaves': list(range(maximum + 1))}
    vectors.update({key: [0] * (maximum + 1) for key in ('units', 'columns', 'slots')})
    recipes = {}
    for n in range(m, maximum + 1):
        cap = n // m
        if cap not in recipes:
            recipes[cap] = flow_recipe(targets, paid, cap)
        height, sources, exits, local_units, local_columns = recipes[cap]
        count = sum(c for rank, c in sources)
        widths[n] = widths[n - 1] * count
        children = child_weights(n, sources, exits)
        need(all(widths[n - 1] % widths[e] == 0 for e in children),
             'nested whole-batch divisibility')
        local = {'leaves': 0, 'units': local_units, 'columns': local_columns,
                 'slots': count + sum(c for rank, c in exits) + (W + P) * local_units}
        for key in normal:
            total = Fraction(local[key]) + sum((weight * normal[key][e]
                    for e, weight in children.items()), Fraction(0))
            normal[key][n] = total / count
            vectors[key][n] = exact_integer(widths[n] * normal[key][n], key)
        need(widths[n] * n - vectors['leaves'][n] == delta * vectors['columns'][n],
             'expanded rank-mass identity')
        need(vectors['units'][n] <= vectors['columns'][n]
             <= widths[n] * n // delta, 'unit/column envelope')
        need(vectors['slots'][n] <= 2 * (W + P) * vectors['units'][n],
             'complete routing envelope')
    summary = finish_summary(vectors, normal['leaves'][maximum], targets, paid,
                             maximum, recipes[maximum // m][0], delta)
    return vectors, summary


def bigint(value):
    need(type(value) is int and value >= 0, 'nonnegative summary integer')
    bits = value.bit_length()
    raw = value.to_bytes((bits + 7) // 8, 'big')
    return {'bits': bits, 'unsigned_big_endian_sha256': hashlib.sha256(raw).hexdigest()}


def finish_summary(vectors, normalized_leaves, targets, paid, n, height, delta):
    W, P = sum(c for k, c in targets), sum(c for k, c in paid)
    ceiling = W * (W + P + 1) ** (height + 1)
    scale = 10 ** 18
    low = normalized_leaves.numerator * scale // normalized_leaves.denominator
    return {
        'n': n, 'productive_width': bigint(vectors['widths'][n]),
        'paid_rank_one_leaves': bigint(vectors['leaves'][n]),
        'raw_instances': bigint(vectors['units'][n]),
        'column_mass': bigint(vectors['columns'][n]),
        'routing_slots': bigint(vectors['slots'][n]),
        'leaves_per_array': {'lower': str(Fraction(low, scale)),
                             'upper': str(Fraction(low + 1, scale))},
        'width_exponent_envelope': ceiling.bit_length() * n,
        'source_count_upper': ceiling, 'rank_one_surplus': delta,
        'paid_above_99_percent_linear': normalized_leaves > Fraction(99 * n, 100),
        'nested_batch_checks': n - targets[-1][0] + 1,
    }


def build_packet(specification, sources):
    need(specification['schema'] == 'direct-compiler-counts-cases/1', 'case schema')
    names, cases = set(), []
    for row in specification['cases']:
        name = row['name']
        need(type(name) is str and name not in names, 'unique case name')
        names.add(name)
        targets, paid = inventory(row['targets'], 2), inventory(row['paid'], 1)
        maximum = positive(row['maximum'], 'positive maximum')
        if name == 'raw-p7':
            raw = decode(sources['inputs/p7-RESULT.json.txt'])['strictification']
            expected_t = tuple(sorted((int(k), v) for k, v in raw['targets'].items()))
            expected_p = tuple(sorted((int(k), v) for k, v in raw['paid'].items()))
            need((targets, paid) == (expected_t, expected_p), 'raw inventory binding')
        vectors, summary = compile_expected(targets, paid, maximum)
        encoded = {key: [format(value, 'x') for value in values]
                   for key, values in vectors.items()}
        cases.append({'name': name, 'maximum': maximum,
                      'vectors': encoded, 'summary': summary})
    return {'schema': 'direct-compiler-counts-audit/1', 'cases': cases}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--emit', action='store_true')
    mode.add_argument('--reference', type=Path)
    args = parser.parse_args()
    specification, sources = authenticate()
    encoded = canonical(build_packet(specification, sources))
    need(len(encoded) <= CAP, 'packet byte cap')
    if args.emit:
        sys.stdout.buffer.write(encoded)
    else:
        reference = args.reference or HERE / 'CERTIFICATE.json'
        need(read_raw(reference) == encoded, 'complete canonical packet mismatch')
        print('PASS_DIRECT_COMPILER_FRACTION_ORACLE', hashlib.sha256(encoded).hexdigest())


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError, OverflowError) as error:
        print('FAIL_DIRECT_COMPILER_FRACTION_ORACLE', error, file=sys.stderr)
        raise SystemExit(1)
