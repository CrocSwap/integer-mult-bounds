"""Signed scalar/C arithmetic and a complete local numerical source witness."""
from collections import Counter
from fractions import Fraction
from functools import lru_cache

from common import digest, integer, require


def widths(p, h, f):
    require(all(type(x) is int for x in (p, h, f)) and p >= 0 and h >= 0 and f >= 1,
            'nonnegative input widths and positive column count')
    return p+(145*f+1)//2+4, p+h+145*f+20


def nearest(numerator, denominator):
    require(type(numerator) is int and type(denominator) is int and denominator > 0, 'quantizer integer domain')
    return (2*numerator+denominator)//(2*denominator)


def toward_zero(numerator, denominator):
    require(type(numerator) is int and type(denominator) is int and denominator > 0, 'quantizer integer domain')
    return (1 if numerator >= 0 else -1)*(abs(numerator)//denominator)


def turn(value, phase):
    a, b = value
    return ((a, b), (-b, a), (-a, -b), (b, -a))[phase % 4]


def invert(rows):
    require(len(rows) == 9 and all(type(r) is int and 0 <= r < 512 for r in rows), 'binary map domain')
    a = [r | (1 << (9+i)) for i, r in enumerate(rows)]
    for j in range(9):
        pivot = next((i for i in range(j, 9) if a[i] >> j & 1), None)
        require(pivot is not None, 'bijective binary map')
        a[j], a[pivot] = a[pivot], a[j]
        for i in range(9):
            if i != j and a[i] >> j & 1:
                a[i] ^= a[j]
    return tuple(r >> 9 for r in a)


def mv(rows, x):
    return sum(((r & x).bit_count() % 2) << i for i, r in enumerate(rows))


def qvalue(quadratic, linear, x):
    return (sum(linear[i] for i in range(9) if x >> i & 1)
            +2*sum(((quadratic[i] >> (i+1)) & (x >> (i+1))).bit_count()
                   for i in range(9) if x >> i & 1)) % 4


def record_key(record):
    require(type(record) is dict and set(record) == {'matrix_rows', 'offset', 'quadratic_rows', 'linear_Z4', 'phase'},
            'complete native monomial')
    matrix, quadratic, linear = (tuple(record[k]) for k in ('matrix_rows', 'quadratic_rows', 'linear_Z4'))
    invert(matrix)
    require(len(quadratic) == len(linear) == 9, 'native phase dimension')
    require(all(type(q) is int and 0 <= q < 512 for q in quadratic)
            and all(type(a) is int and 0 <= a < 4 for a in linear), 'native phase domain')
    require(all((quadratic[i] >> j & 1) == (quadratic[j] >> i & 1) for i in range(9) for j in range(9)),
            'symmetric phase quadratic')
    require(all((linear[i] & 1) == (quadratic[i] >> i & 1) for i in range(9)), 'phase diagonal parity')
    return matrix, integer(record['offset'], 0, 511, 'native translation'), quadratic, linear, integer(record['phase'], 0, 3, 'native phase')


@lru_cache(maxsize=128)
def monomial_plan(key):
    matrix, offset, quadratic, linear, phase = key
    return tuple((mv(matrix, x) ^ offset, (qvalue(quadratic, linear, x)+phase) % 4) for x in range(512))


def apply_plan(vector, plan):
    require(len(vector) == len(plan) == 512, 'complete512-coordinate plan')
    out = [None]*512
    for value, (destination, phase) in zip(vector, plan):
        require(out[destination] is None, 'one-to-one monomial plan')
        out[destination] = turn(value, phase)
    require(all(value is not None for value in out), 'complete monomial return')
    return out


class Arithmetic:
    def __init__(self, width):
        integer(width, 2, 1_000_000, 'finite fixture signed width')
        self.width = width
        self.limit = 1 << (width-1)
        self.temporary_limit = 1 << (width+5)
        self.counts = Counter()

    def stored(self, value):
        require(type(value) is int and -self.limit < value < self.limit, 'strict signed component headroom')
        self.counts['stored_components'] += 1
        return value

    def divide(self, numerator, denominator, name):
        require(type(numerator) is int and -self.temporary_limit < numerator < self.temporary_limit,
                'signed numerator temporary width')
        require(type(denominator) is int and denominator > 0 and numerator % denominator == 0,
                'exact division before quantization: '+name)
        answer = numerator//denominator
        require(nearest(numerator, denominator) == toward_zero(numerator, denominator) == answer,
                'both deterministic quantizers are identity')
        self.counts[name] += 1
        return self.stored(answer)

    def product(self, value, coefficient):
        return self.divide(value*coefficient.numerator, coefficient.denominator, 'scalar_products')

    def cstage(self, vector, mask, sign=1):
        require(type(vector) is list and len(vector) == 512, 'complete native stage field')
        integer(mask, 1, 511, 'C direction')
        require(type(sign) is int and sign in (-1, 1), 'C sign')
        for x in range(512):
            y = x ^ mask
            if x > y:
                continue
            a, b = vector[x]
            c, d = vector[y]
            numerators = (a-sign*b+c+sign*d, b+sign*a+d-sign*c,
                          a+sign*b+c-sign*d, b-sign*a+d+sign*c)
            values = tuple(self.divide(n, 2, 'C_components') for n in numerators)
            vector[x], vector[y] = values[:2], values[2:]
        self.counts['C_stages'] += 1
        return vector

    def native(self, vector, record):
        require(type(record) is dict and set(record) == {'rank', 'left', 'right'}, 'native complete record')
        rank = integer(record['rank'], 0, 9, 'native rank')
        if rank:
            vector = apply_plan(vector, monomial_plan(record_key(record['right'])))
            for j in range(rank):
                self.cstage(vector, 1 << j)
        else:
            require(record['right'] is None, 'rank-zero normalization convention')
        return apply_plan(vector, monomial_plan(record_key(record['left'])))


@lru_cache(maxsize=128)
def chart_data(vectors):
    rank = len(vectors)
    if rank in (0, 9):
        return rank, None, None
    columns = []
    reached = {0}
    for value in vectors+tuple(1 << j for j in range(9)):
        if value not in reached:
            columns.append(value)
            reached |= {x ^ value for x in tuple(reached)}
    require(len(columns) == 9, 'canonical frame extension')
    matrix = tuple(sum(((columns[j] >> i) & 1) << j for j in range(9)) for i in range(9))
    inverse = invert(matrix)
    inverse_columns = tuple(sum(((inverse[j] >> i) & 1) << j for j in range(9)) for i in range(9))
    quadratic = tuple((1 << i) ^ sum(((a & b).bit_count() % 2) << j for j, b in enumerate(inverse_columns))
                      for i, a in enumerate(inverse_columns))
    linear = tuple((q >> i) & 1 for i, q in enumerate(quadratic))
    before = tuple((mv(inverse, x), -qvalue(quadratic, linear, x) % 4) for x in range(512))
    after = tuple((mv(matrix, x), qvalue(quadratic, linear, mv(matrix, x))) for x in range(512))
    return rank, before, after


def chart(vector, vectors, arithmetic, sign=1):
    rank, before, after = chart_data(tuple(vectors))
    vector = apply_plan(vector, before) if before is not None else list(vector)
    for j in range(rank):
        arithmetic.cstage(vector, 1 << j, sign)
    return apply_plan(vector, after) if after is not None else vector


def native_records(word, native, source_result):
    records = {(a, b): rec for a, b, rec in native['pairs']}
    require(len(records) == len(native['pairs']), 'unique native source pairs')
    wanted = {(e[2], e[3]) for e in word['program'] if e[0] == 'MOVE'}
    main = set(word['live']) | {r+112 for r in word['live']}
    wanted |= {(word['initial'][r], word['final'][r]) for r in range(770) if r not in main}
    require(wanted == records.keys(), 'exact MOVE and helper recipe coverage')
    payload = native['pairs']+[r['recipe'] for r in native['adapters']]
    require(digest(payload) == native['recipe_payload_sha256'] == source_result['native']['recipe_payload_sha256'],
            'actual selected compiled native payload, with phases')
    for (a, b), record in records.items():
        rank = integer(record['rank'], 0, 9, 'native rank')
        require(rank == abs(len(word['frames'][a])-len(word['frames'][b])), 'source normalized native rank')
        record_key(record['left'])
        if rank:
            record_key(record['right'])
        else:
            require(record['right'] is None, 'rank-zero source right side')
    expected_adapters = [(kind, r, q) for r, q in zip(word['live'], word['ports']) for kind in ('input', 'output')]
    require([(r['kind'], r['role'], r['port']) for r in native['adapters']] == expected_adapters, 'all208 intrinsic adapters')
    for adapter in native['adapters']:
        require(adapter['recipe']['rank'] == 0 and adapter['recipe']['right'] is None, 'ordinary intrinsic adapter')
        record_key(adapter['recipe']['left'])
    return records


def complete_local_fixture(word, native, source_result, progress=False):
    records = native_records(word, native, source_result)
    p, h, f = 3, 2, 1
    fractional, width = widths(p, h, f)
    lift = 1 << (fractional-p)
    initial = [[((((37*r+19*x+7*x*x+0x6030) % 63)-31)*lift,
                 (((11*r+23*x+3*x*x+17) % 63)-31)*lift) for x in range(512)] for r in range(770)]
    fields = [list(v) for v in initial]+[None]*29
    arithmetic = Arithmetic(width)
    for vector in initial:
        for value in vector:
            require(all(abs(c) < 1 << (fractional+h) for c in value), 'actual input amplitude admission')
    initial_hash = digest(initial)
    counts = Counter()
    for index, event in enumerate(word['program']):
        kind, target = event[:2]
        counts[kind] += 1
        if kind == 'INIT':
            require(fields[target] is None, 'fixture fresh owned storage')
            fields[target] = [(0, 0)]*512
        elif kind == 'CLEAR':
            require(fields[target] is not None, 'fixture current owned reset')
            fields[target] = None
        elif kind == 'MOVE':
            fields[target] = arithmetic.native(fields[target], records[event[2], event[3]])
        else:
            require(kind in ('ADD', 'COPY', 'SCALE'), 'fixture source opcode')
            coefficient = Fraction(event[-2])
            source = target if kind == 'SCALE' else event[2]
            product = [(arithmetic.product(a, coefficient), arithmetic.product(b, coefficient))
                       for a, b in fields[source]]
            if kind == 'ADD':
                fields[target] = [(arithmetic.stored(a+c), arithmetic.stored(b+d))
                                  for (a, b), (c, d) in zip(fields[target], product)]
            else:
                if kind == 'COPY':
                    require(all(v == (0, 0) for v in fields[target]), 'fixture COPY into zero')
                fields[target] = product
        if progress and index % 6000 == 0:
            print('local_quantizer_event', index, flush=True)
    reference = Arithmetic(width)
    logical = [chart(v, word['frames'][word['initial'][r]], reference, -1) for r, v in enumerate(initial)]
    for r in range(770):
        expected = list(logical[r])
        if r-112 in word['live']:
            expected = [(a+c, b+d) for (a, b), (c, d) in zip(expected, logical[r-112])]
        expected = chart(expected, word['frames'][word['final'][r]], reference)
        require(fields[r] == expected, 'complete direct-native integer endpoint '+str(r))
    require(fields[770:] == [None]*29, 'all owned fixture lifetimes reset')
    require(digest(initial) == initial_hash, 'immutable original fixture inputs')
    return {'scope': 'complete22803-event local numerical fixture, not global2^145 replay',
            'p': p, 'h': h, 'f': f, 'physical_coordinates': 512, 'fractional_bits': fractional,
            'signed_component_bits': width, 'temporary_component_bits': width+6,
            'events': dict(sorted(counts.items())), 'arithmetic': dict(sorted(arithmetic.counts.items())),
            'reference_arithmetic': dict(sorted(reference.counts.items())),
            'public_complex_outputs': 770*512, 'endpoint_sha256': digest(fields[:770]),
            'original_components_sha256': initial_hash, 'owned_labels_returned': 29,
            'quantizers': ['nearest with upward ties', 'toward zero'], 'all_checked_divisions_exact': True}
