#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Check the fixed chart-595 scalar grid and its factor-seven witnesses."""

from collections import Counter
from fractions import Fraction
from hashlib import sha256
import gzip
import json
from math import gcd
from pathlib import Path

HERE = Path(__file__).resolve().parent
GRAPH_HASH = 'd5dab11bb773bf5beb8ae2998be1282b243e2d1606c5257896a037c9b52c5c3b'
GRID = 45158400


def require(test, message):
    if not test:
        raise ValueError(message)


def load():
    for name, pin in json.loads((HERE / 'ORIGINS.json').read_text()).items():
        require(sha256((HERE / name).read_bytes()).hexdigest() == pin['sha256'], name)
    raw = gzip.decompress((HERE / 'inputs/CANDIDATE-GRAPH.json.gz').read_bytes())
    require(sha256(raw).hexdigest() == GRAPH_HASH, 'decoded graph')
    graph = json.loads(raw)
    rows = {k: [(d, Fraction(q)) for d, q in terms] for k, terms in graph['forms']}
    require(len(rows) == len(graph['forms']) == len(graph['schedule']) == 7644,
            'complete row inventory')
    require(set(rows) == set(graph['schedule']), 'unique schedule')
    require(len(graph['initial']) == len(graph['final']) == 1502, 'public owners')
    require(len(graph['moves']) == 6142, 'paid moves')
    return graph, rows


def valuation(number, prime):
    power = 0
    while number % prime == 0:
        number //= prime
        power += 1
    return power


def basis_replay(graph, rows):
    values = {~i: {i: GRID} for i in range(1502)}
    product_gcd = row_gcd = GRID
    products = 0
    prime_witnesses = {}
    seven_columns = Counter()
    seven_rows = Counter()
    seven_witnesses = {}
    trace = sha256()
    for key in graph['schedule']:
        total = {}
        for donor, q in rows[key]:
            require(donor in values, 'future read')
            for column, value in values[donor].items():
                product, remainder = divmod(value * q.numerator, q.denominator)
                require(remainder == 0, 'nonintegral literal product')
                products += 1
                product_gcd = gcd(product_gcd, product)
                denominator = GRID // gcd(GRID, product)
                witness = None
                for prime in (2, 3, 5, 7):
                    exponent = valuation(denominator, prime)
                    if exponent > prime_witnesses.get(prime, {}).get('exponent', 0):
                        witness = {'row': key, 'donor': donor, 'column': column,
                                   'scalar': str(q), 'donor_value': str(Fraction(value, GRID)),
                                   'product': str(Fraction(product, GRID))}
                        prime_witnesses[prime] = dict(witness, exponent=exponent)
                    if prime == 7 and exponent == 2:
                        seven_columns[column] += 1
                        seven_rows[key] += 1
                        if column not in seven_witnesses:
                            seven_witnesses[column] = witness or {
                                'row': key, 'donor': donor, 'column': column,
                                'scalar': str(q), 'donor_value': str(Fraction(value, GRID)),
                                'product': str(Fraction(product, GRID))}
                total[column] = total.get(column, 0) + product
        total = {i: v for i, v in total.items() if v}
        for value in total.values():
            row_gcd = gcd(row_gcd, value)
        values[key] = total
        trace.update(json.dumps([key, sorted(total.items())], separators=(',', ':')).encode())
    require(products == 8738317, 'complete nonzero product count')
    require(GRID // product_gcd == GRID and GRID // row_gcd == 161280, 'grid minima')
    require(seven_columns == {281: 60, 1501: 570} and len(seven_rows) == 40,
            'factor-seven support')
    return {'products': products, 'minimum_product_grid': GRID,
            'minimum_snapshot_grid': GRID // row_gcd,
            'prime_witnesses': prime_witnesses,
            'seven_squared_columns': sorted(seven_columns.items()),
            'seven_squared_rows': sorted(seven_rows.items()),
            'seven_witnesses': seven_witnesses, 'row_trace_sha256': trace.hexdigest()}


def rational_column(graph, rows, witness):
    """Use rational arithmetic on one input, without the integer basis trace."""
    values = {~i: Fraction(i == witness['column']) for i in range(1502)}
    for key in graph['schedule']:
        total = Fraction()
        for donor, q in rows[key]:
            product = values[donor] * q
            if (key, donor) == (witness['row'], witness['donor']):
                require(str(q) == witness['scalar'], 'witness scalar')
                require(str(values[donor]) == witness['donor_value'], 'rational donor')
                require(str(product) == witness['product'], 'rational product')
                return product
            total += product
        values[key] = total
    raise ValueError('missing witness')


def first_failure(graph, rows, column, grid):
    values = {~i: grid * (i == column) for i in range(1502)}
    for key in graph['schedule']:
        total = 0
        for donor, q in rows[key]:
            product, remainder = divmod(values[donor] * q.numerator, q.denominator)
            if remainder:
                return {'row': key, 'donor': donor, 'column': column, 'grid': grid,
                        'scalar': str(q), 'divisor': q.denominator, 'remainder': remainder}
            total += product
        values[key] = total
    raise ValueError('under-grid control did not fail')


def main():
    graph, rows = load()
    result = basis_replay(graph, rows)
    controls = []
    for prime, witness in result['prime_witnesses'].items():
        product = rational_column(graph, rows, witness)
        require(valuation(product.denominator, prime) == witness['exponent'], 'prime sharpness')
        controls.append(first_failure(graph, rows, witness['column'], GRID // prime))
    for column, witness in result['seven_witnesses'].items():
        product = rational_column(graph, rows, witness)
        require(product.denominator % 49 == 0, 'two independent input witnesses')
        controls.append(first_failure(graph, rows, column, 161280))
    result['under_grid_controls'] = controls
    result['scope'] = 'Normalized scalar products and complete snapshots of the fixed graph only.'
    result = json.loads(json.dumps(result))
    require(result == json.loads((HERE / 'RESULT.json').read_text()), 'receipt mismatch')
    print('PASS_CHART595_FACTOR_SEVEN_AUDIT')


if __name__ == '__main__':
    main()
