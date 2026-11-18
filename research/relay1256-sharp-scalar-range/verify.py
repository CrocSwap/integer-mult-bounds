"""Check sharp scalar ranges on the fixed PR7704 normalized graph."""
from fractions import Fraction
from pathlib import Path
import gzip
import hashlib
import json


ROOT = Path(__file__).resolve().parent
GRID = 921600
GRAPH_HASH = '8e7b755bd2d2d387bc3d3adfe48100985adf74775ca5acbb143170a3d16b5ccf'
ARCHIVE_HASH = '0177c25371181e3b1f2c13325eb8434fbf6384a9ab99a612849efd5d0f6ab2cc'
KINDS = ('snapshot', 'prefix', 'product', 'numerator')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def encode(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def read_graph():
    archive = (ROOT / 'data/CANDIDATE-GRAPH.json.gz').read_bytes()
    require(hashlib.sha256(archive).hexdigest() == ARCHIVE_HASH, 'source archive changed')
    raw = gzip.decompress(archive)
    require(hashlib.sha256(raw).hexdigest() == GRAPH_HASH, 'source graph changed')
    graph = json.loads(raw)
    forms = {key: [(donor, Fraction(q)) for donor, q in row]
             for key, row in graph['forms']}
    moves = {key: (start, end) for key, start, end in graph['moves']}
    n = len(graph['initial'])
    terminals = set(range(graph['first_output'], graph['first_output'] + n))
    require(n == 1501 and len(moves) == 6143 and len(forms) == 7644,
            'source dimensions changed')
    require(set(forms) == set(moves) | terminals and not terminals.intersection(moves),
            'row namespace changed')
    require(len(graph['schedule']) == len(forms) and set(graph['schedule']) == set(forms),
            'schedule is not a permutation')
    charts = {~column: chart for column, chart in enumerate(graph['initial'])}
    for key in graph['schedule']:
        start = moves[key][0] if key in moves else graph['final'][key - graph['first_output']]
        require([d for d, _ in forms[key]] == sorted({d for d, _ in forms[key]}),
                'literal donor order changed')
        require(all(q and d in charts and charts[d] == start for d, q in forms[key]),
                'donor is absent, zero or in a different chart')
        if key in moves:
            charts[key] = moves[key][1]
    return graph, forms, moves


def basis_ranges(graph, forms, moves):
    values = {~column: {column: GRID} for column in range(len(graph['initial']))}
    peaks = {kind: {'mass': GRID, 'row': None, 'term': None, 'vector': {0: GRID}}
             for kind in KINDS}
    triangle = {'mass': GRID, 'row': None}
    trace = hashlib.sha256()
    products = prefixes = 0
    terminal_peak_row = None

    def record(kind, mass, key, term, vector):
        if mass > peaks[kind]['mass']:
            peaks[kind] = {'mass': mass, 'row': key, 'term': term,
                           'vector': dict(vector)}

    for key in graph['schedule']:
        row = {}
        mass = row_triangle = 0
        for term, (donor, q) in enumerate(forms[key], 1):
            product = {}
            for column, value in values[donor].items():
                z, remainder = divmod(q.numerator * value, q.denominator)
                require(remainder == 0, 'literal product is off the declared grid')
                product[column] = z
                old = row.get(column, 0)
                new = old + z
                mass += abs(new) - abs(old)
                if new:
                    row[column] = new
                else:
                    row.pop(column, None)
                products += 1
            product_mass = sum(map(abs, product.values()))
            row_triangle += product_mass
            record('product', product_mass, key, term, product)
            record('numerator', product_mass * q.denominator, key, term,
                   {column: z * q.denominator for column, z in product.items()})
            record('prefix', mass, key, term, row)
            prefixes += 1
        record('snapshot', mass, key, len(forms[key]), row)
        if row_triangle > triangle['mass']:
            triangle = {'mass': row_triangle, 'row': key}
        trace.update(encode([key, sorted(row.items())]) + b'\n')
        if key in moves:
            values[key] = row
        if key == 156140:
            terminal_peak_row = sorted(row.items())
    require(products == 9044092 and prefixes == 172414, 'source coverage changed')
    require(terminal_peak_row == [(1372, GRID)], 'peak row no longer cancels to one input')
    require(Fraction(triangle['mass'], GRID) == Fraction(13819451, 16),
            'source triangle bound changed')
    return peaks, {'rows': len(forms), 'ordered_prefixes': prefixes,
                   'nonzero_basis_products': products,
                   'completed_rows_sha256': trace.hexdigest(),
                   'separate_product_triangle_maximum': str(Fraction(triangle['mass'], GRID)),
                   'triangle_peak_row': triangle['row'],
                   'peak_prefix_row_final_value': 'input 1372'}


def scalar_oracle(graph, forms, moves, inputs, target):
    """Use scalar rational arithmetic, with no basis vectors or range recurrence."""
    values = {~column: Fraction(value) for column, value in enumerate(inputs)}
    maxima = {kind: max(map(abs, inputs)) for kind in KINDS}
    observed = None
    integral = True
    for key in graph['schedule']:
        total = Fraction()
        for term, (donor, q) in enumerate(forms[key], 1):
            numerator = values[donor] * q.numerator
            product = numerator / q.denominator
            total += product
            for kind, value in [('numerator', numerator), ('product', product), ('prefix', total)]:
                maxima[kind] = max(maxima[kind], abs(value))
                integral = integral and value.denominator == 1
                if (kind, key, term) == target:
                    observed = value
        maxima['snapshot'] = max(maxima['snapshot'], abs(total))
        if ('snapshot', key, len(forms[key])) == target:
            observed = total
        if key in moves:
            values[key] = total
    require(observed is not None, 'oracle target was not visited')
    return maxima, observed, integral


def extra_bits(mass):
    bits = 0
    while mass >= GRID << bits:
        bits += 1
    return bits


def check():
    graph, forms, moves = read_graph()
    peaks, coverage = basis_ranges(graph, forms, moves)
    bounds = {kind: Fraction(peak['mass'], GRID) for kind, peak in peaks.items()}
    witnesses = {}
    width = 32
    magnitude = ((1 << (width - 1)) - 1) // GRID * GRID
    for kind, peak in peaks.items():
        signs = [-1 if peak['vector'].get(column, 0) < 0 else 1
                 for column in range(len(graph['initial']))]
        target = (kind, peak['row'], peak['term'])
        maxima, observed, _ = scalar_oracle(graph, forms, moves, signs, target)
        require(observed == bounds[kind], 'corner does not attain its bound')
        require(all(maxima[name] <= bounds[name] for name in KINDS), 'oracle exceeds a bound')
        scaled, integer_value, integral = scalar_oracle(
            graph, forms, moves, [magnitude * x for x in signs], target)
        require(integral, 'integer-lattice witness is not exact')
        require(integer_value == magnitude * bounds[kind], 'scaled corner changed')
        growth = extra_bits(peak['mass'])
        require(all(value < 1 << (width + 21 - 1) for value in scaled.values()),
                'W+21 data range failed')
        require(integer_value >= 1 << (width + growth - 2), 'one-bit-smaller control did not fail')
        donor, q = forms[peak['row']][peak['term'] - 1]
        witnesses[kind] = {
            'maximum_for_unit_inputs': str(bounds[kind]), 'row': peak['row'],
            'one_based_term': peak['term'], 'source_term': [donor, str(q)],
            'support': len(peak['vector']), 'coefficient_vector_sha256':
                hashlib.sha256(encode(sorted(peak['vector'].items()))).hexdigest(),
            'negative_input_columns': [i for i, sign in enumerate(signs) if sign < 0],
            'all_other_input_signs': 1, 'sufficient_uniform_extra_signed_bits': growth,
            'input_signed_width': width, 'input_integer_magnitude': magnitude,
            'attaining_integer_value': int(integer_value),
            'one_bit_smaller_positive_limit': (1 << (width + growth - 2)) - 1,
        }
    require([witnesses[k]['sufficient_uniform_extra_signed_bits'] for k in KINDS]
            == [15, 18, 18, 21], 'bit bounds changed')
    maximum_denominator = max(q.denominator for row in forms.values() for _, q in row)
    require(maximum_denominator == 384, 'division remainder allowance changed')
    return {'status': 'PASS_RELAY1256_SHARP_SCALAR_RANGE',
            'source_graph_sha256': GRAPH_HASH, 'integer_entrance_multiple': GRID,
            'coverage': coverage, 'sharp_ranges': witnesses,
            'scalar_oracle_complete_runs': 8, 'one_bit_smaller_controls': 4,
            'maximum_coefficient_denominator': maximum_denominator,
            'long_division_remainder_strict_upper': 2 * maximum_denominator,
            'source_triangle_to_sharp_prefix_ratio': str(Fraction(13819451, 16) / bounds['prefix']),
            'scope': 'Fixed normalized scalar graph; no physical chart or complete kappa claim.'}


if __name__ == '__main__':
    result = check()
    require(result == json.loads((ROOT / 'RESULT.json').read_text()), 'receipt differs')
    print(result['status'])
    print('7644 rows; 172414 prefixes; 9044092 basis products; 8 scalar oracle runs')
    print('Extra signed bits: snapshots 15; prefixes 18; products 18; numerators 21')
