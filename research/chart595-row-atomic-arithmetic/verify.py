#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Check exact row accumulation on the fixed chart-595 graph."""

from fractions import Fraction
from hashlib import sha256
import gzip
import importlib.util
import json
from math import gcd, lcm
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCALE = 161280
spec = importlib.util.spec_from_file_location('row_kernel', HERE / 'kernel.py')
kernel = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kernel)


def require(test, message):
    if not test:
        raise ValueError(message)


def load():
    for name, pin in json.loads((HERE / 'ORIGINS.json').read_text()).items():
        require(sha256((HERE / name).read_bytes()).hexdigest() == pin['sha256'], name)
    raw = gzip.decompress((HERE / 'inputs/CANDIDATE-GRAPH.json.gz').read_bytes())
    require(sha256(raw).hexdigest() == 'd5dab11bb773bf5beb8ae2998be1282b243e2d1606c5257896a037c9b52c5c3b', 'graph')
    graph = json.loads(raw)
    rows = {}
    for key, terms in graph['forms']:
        factors = [Fraction(q) for _, q in terms]
        denominator = lcm(*(q.denominator for q in factors))
        coefficients = [q.numerator * (denominator // q.denominator) for q in factors]
        rows[key] = ([d for d, _ in terms], coefficients, denominator)
    return graph, rows


def statistics(rows):
    details = []
    for key, (donors, coefficients, denominator) in rows.items():
        mass = sum(map(abs, coefficients))
        details.append({'row': key, 'terms': len(donors), 'denominator': denominator,
                        'l1': mass, 'max_coefficient': max(map(abs, coefficients)),
                        'bits': max(mass.bit_length(), denominator.bit_length()),
                        'shift_add_iterations': sum(abs(c).bit_length() for c in coefficients),
                        'signed_adds': sum(abs(c).bit_count() for c in coefficients)})
    result = {'rows': len(rows), 'terms': sum(x['terms'] for x in details),
              'max_denominator': max(details, key=lambda x: x['denominator']),
              'max_l1': max(details, key=lambda x: x['l1']),
              'max_coefficient': max(details, key=lambda x: x['max_coefficient']),
              'max_bits': max(x['bits'] for x in details),
              'shift_add_iterations': sum(x['shift_add_iterations'] for x in details),
              'signed_adds': sum(x['signed_adds'] for x in details),
              'nontrivial_divisions': sum(x['denominator'] != 1 for x in details)}
    require(result['rows'] == 7644 and result['terms'] == 170652, 'full row count')
    require(result['max_l1']['l1'] == 683350 and result['max_denominator']['denominator'] == 6720,
            'all-row width constants')
    return result


def basis_trace(graph, rows):
    values = {~i: {i: SCALE} for i in range(1502)}
    trace = sha256()
    stored_gcd = SCALE
    products = 0
    quotients = 0
    for key in graph['schedule']:
        donors, coefficients, denominator = rows[key]
        total = {}
        for donor, coefficient in zip(donors, coefficients, strict=True):
            for column, value in values[donor].items():
                products += 1
                total[column] = total.get(column, 0) + coefficient * value
        output = {}
        for column, value in total.items():
            quotient, remainder = divmod(value, denominator)
            require(remainder == 0, 'row-final basis division')
            quotients += 1
            if quotient:
                output[column] = quotient
                stored_gcd = gcd(stored_gcd, quotient)
        values[key] = output
        trace.update(json.dumps([key, sorted((i, v * 280) for i, v in output.items())],
                                separators=(',', ':')).encode())
    prior = json.loads((HERE / 'inputs/GRID-RESULT.json').read_text())
    require(trace.hexdigest() == prior['row_trace_sha256'], 'complete literal-product reference')
    require(stored_gcd == 1 and products == 8738317, 'minimal stored grid')
    return {'basis_products': products, 'row_final_basis_divisions': quotients,
            'minimum_snapshot_grid': SCALE, 'reference_row_trace_sha256': trace.hexdigest()}


def complete_execution(graph, rows, seed):
    source = {~i: SCALE * (((i * (719 + seed) + 29) % 127) - 63) for i in range(1502)}
    actual = dict(source)
    oracle = dict(source)
    maximum = 0
    trace = sha256()
    for key in graph['schedule']:
        donors, coefficients, denominator = rows[key]
        before = tuple(actual[d] for d in donors)
        value = kernel.row(before, coefficients, denominator, 64)
        reference = sum((Fraction(c, denominator) * oracle[d]
                         for d, c in zip(donors, coefficients, strict=True)), Fraction())
        require(reference.denominator == 1 and value == reference, 'full scalar execution')
        require(before == tuple(actual[d] for d in donors), 'immutable donor values')
        kernel.check(value, 64)
        actual[key] = value
        oracle[key] = reference
        maximum = max(maximum, abs(value))
        trace.update(f'{key}:{value};'.encode())
    return {'seed': seed, 'rows': len(graph['schedule']), 'maximum_stored_magnitude': maximum,
            'trace_sha256': trace.hexdigest()}


def expect_failure(action, token):
    try:
        action()
    except ValueError as error:
        require(token in str(error), 'wrong rejection')
        return
    raise ValueError('negative control passed')


def kernel_controls(rows):
    cases = 0
    for donors, coefficients, denominator in rows.values():
        for width in (16, 32):
            for sign in (-1, 1):
                # Multiples of D give exact rows for all donor signs.
                value = sign * denominator * (((1 << (width - 1)) - 1) // denominator)
                inputs = [value if c > 0 else -value for c in coefficients]
                actual = kernel.row(inputs, coefficients, denominator, width)
                expected = sum(c * x for c, x in zip(coefficients, inputs, strict=True)) // denominator
                require(actual == expected, 'row boundary fixture')
                cases += 1
    _, coefficients, denominator = rows[151738]
    large = []
    for width in (32, 128, 2048, 4096):
        value = denominator * (((1 << (width - 1)) - 1) // denominator)
        inputs = [value if c > 0 else -value for c in coefficients]
        expected = sum(c * x for c, x in zip(coefficients, inputs, strict=True)) // denominator
        require(kernel.row(inputs, coefficients, denominator, width) == expected, 'large exact row')
        large.append({'data_width': width, 'output_bits': abs(expected).bit_length() + 1})
    value = denominator * (((1 << 31) - 1) // denominator)
    numerator = 683350 * value
    expect_failure(lambda: kernel.check(numerator, 32 + 19), 'signed arithmetic width')
    require(numerator % denominator == 0, 'accepted-domain narrow-word control')
    expect_failure(lambda: kernel.row([1], [1], 7, 2), 'nonzero exact-division remainder')
    expect_failure(lambda: kernel.row([2], [1], 1, 2), 'signed arithmetic width')
    expect_failure(lambda: kernel.row([True], [1], 1, 2), 'signed arithmetic width')
    expect_failure(lambda: kernel.row([1], [683351], 1, 2), 'row coefficient mass')
    return {'all_row_boundary_cases': cases, 'large_rows': large,
            'narrow_word_control': {'row': 151738, 'data_width': 32,
                                    'numerator': numerator, 'needed_signed_bits': numerator.bit_length() + 1},
            'rejection_controls': 5}


def result():
    graph, rows = load()
    return {'statistics': statistics(rows), 'basis': basis_trace(graph, rows),
            'full_scalar_runs': [complete_execution(graph, rows, seed) for seed in (0, 4)],
            'kernel': kernel_controls(rows),
            'scope': 'Exact normalized row arithmetic; no physical tape, root or supplier substitution.'}


def main():
    receipt = result()
    require(receipt == json.loads((HERE / 'RESULT.json').read_text()), 'receipt mismatch')
    print('PASS_CHART595_ROW_ATOMIC_ARITHMETIC')


if __name__ == '__main__':
    main()
