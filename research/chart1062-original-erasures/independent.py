#!/usr/bin/env python3
"""Independent, exact CrocSwap word comparison. Python 3.12, single thread."""
import argparse
from collections import Counter, defaultdict
from decimal import Decimal, Context, ROUND_FLOOR, ROUND_CEILING, ROUND_HALF_EVEN
from difflib import SequenceMatcher
from fractions import Fraction
from functools import cache
import gzip
from hashlib import sha256
from itertools import chain
import json
from math import gcd, isqrt, prod
from pathlib import Path
import sys
from time import monotonic
from datetime import datetime, UTC

PIN = {
    'candidate': '1b0efdc59fe3f8056f3dbfdd618c7f5b4b4f0ed4063689f182ae3dbd1138fede',
    'word': '37358c493d18ebc6be386aebb4c17529b38883674731f7009ef4e96a5313467d',
    'final': 'f24baa73a60d084a6d613dad914f1237a5890a049a183b993af39c75dde99add',
    'invoice': 'b38afd7ca590b5c4c301ee4fbe0e123f0c7220c2bd1f40c66adf208652e3ce15',
    'caller': '255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc',
}
PREMISES = ['native_all_columns', 'owned_erasure', 'compiler', 'precision_tape', 'analytic_recovery']
GRID = 1125 << 25


def need(condition, message):
    if not condition:
        raise ValueError(message)


def stamp():
    return datetime.now(UTC).isoformat(timespec='milliseconds')


def digest(obj):
    return sha256(json.dumps(obj, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def load(path, pin):
    data = path.read_bytes()
    need(sha256(data).hexdigest() == PIN[pin], f'{pin} packed SHA-256')
    return json.loads(gzip.decompress(data) if data.startswith(b'\x1f\x8b') else data)


def program_diff(a, b):
    def encode(p):
        return [tuple(e) for e in p]
    matching = SequenceMatcher(None, encode(a), encode(b), autojunk=True)
    changes, aligned = [], {}
    for tag, i, j, k, l in matching.get_opcodes():
        if tag == 'equal':
            aligned.update(zip(range(i, j), range(k, l)))
        else:
            changes.append(dict(old_start=i, new_start=k, old=a[i:j], new=b[k:l]))
    return changes, aligned


def span(basis):
    support = {0}
    for v in basis:
        need(0 < v < 512 and v not in support, 'independence of chart basis')
        support |= {v ^ x for x in support}
    return support


@cache
def ratio(value):
    q = Fraction(value)
    return q.numerator, q.denominator


def replay(word, watch, observe_grid=True, fault=None):
    n = word['public']
    count = n + word['owned_fields']
    charts = word['initial'] + [None] * word['owned_fields']
    spans = [span(b) for b in word['frames']]
    dim = list(map(len, word['frames']))
    rows = [{i: GRID} for i in range(n)] + [{} for _ in range(n, count)]
    active = {}
    lifetimes, erasures, owned_events, copies = [], [], [], []
    routes, readings = defaultdict(list), {}
    paid, targets, odd, ops = Counter(), Counter(), Counter(), Counter()
    peak = rises = 0
    mass_max, mass_at, common_divisor = GRID, None, GRID

    def observe(row, index, kind):
        nonlocal mass_max, mass_at, common_divisor
        if observe_grid:
            denominator_factor = gcd(common_divisor, *row.values())
            mass = sum(map(abs, row.values()))
            if mass > mass_max:
                mass_max, mass_at = mass, [index, kind]
            common_divisor = denominator_factor

    def multiply(row, a, b, index):
        if b == 1:
            return {j: a * v for j, v in row.items()}
        product = {}
        for j, v in row.items():
            quotient, remainder = divmod(v * a, b)
            need(not remainder, f'nonintegral grid product at {index} input {j}')
            product[j] = quotient
        return product

    for index, event in enumerate(word['program']):
        effect = fault[1] if fault and index == fault[0] else event
        op, dest, *args = effect
        need(0 <= dest < count, f'destination {index}')
        ops[op] += 1
        operands = [dest] + ([args[0]] if op in ('ADD', 'COPY') else [])
        if any(r >= n for r in operands):
            owned_events.append(tuple(effect))
        if index in watch:
            readings[index] = [tuple(sorted(rows[r].items())) for r in operands]
        if op == 'INIT':
            chart, = args
            need(0 <= chart < len(spans) and dest >= n and dest not in active
                 and charts[dest] is None and not rows[dest], f'INIT {index}')
            charts[dest] = active[dest] = chart
            peak = max(peak, len(active))
            continue
        need(charts[dest] is not None, f'dead destination {index}')
        if op == 'CLEAR':
            chart, = args
            need(dest in active and charts[dest] == chart, f'CLEAR {index}')
            erasures.append((dest, chart, sorted(rows[dest].items())))
            lifetimes.append((dest, active.pop(dest), chart))
            charts[dest], rows[dest] = None, {}
        elif op == 'MOVE':
            before, after, owned = args
            need(charts[dest] == before and type(owned) is bool and owned == (dest >= n),
                 f'MOVE interface {index}')
            need(0 <= after < len(spans) and (spans[before] < spans[after]
                 or (owned and spans[after] < spans[before])), f'MOVE nesting {index}')
            rank = abs(dim[after] - dim[before])
            paid[rank] += 1
            if owned and dim[after] > dim[before]:
                rises += rank
            routes[dest].append((before, after))
            charts[dest] = after
        elif op == 'SCALE':
            scalar, chart = args
            a, b = ratio(scalar)
            need(a and charts[dest] == chart, f'SCALE chart/scalar {index}')
            odd[op] += (b & -b) != b
            rows[dest] = multiply(rows[dest], a, b, index)
            observe(rows[dest], index, 'scale')
        else:
            need(op in ('ADD', 'COPY'), f'opcode {index}')
            src, scalar, chart = args
            a, b = ratio(scalar)
            need(0 <= src < count and src != dest and a and charts[dest] == charts[src] == chart,
                 f'{op} interface {index}')
            if op == 'COPY':
                need(not rows[dest], f'COPY requires actual zero at {index}')
                copies.append((dest, src, chart, scalar))
            odd[op] += (b & -b) != b
            product = multiply(rows[src], a, b, index)
            observe(product, index, 'product')
            row = rows[dest]
            for j, v in product.items():
                value = row.get(j, 0) + v
                if value:
                    row[j] = value
                else:
                    row.pop(j, None)
            observe(row, index, 'stored')
    need(not active and charts == word['final'] + [None] * (count - n), 'endpoint charts and owned closure')
    mains = set(word['live']) | {r + 112 for r in word['live']} | set(word['hosted']['X2'] + word['hosted']['Y2'])
    bad_helpers = [i for i in range(n) if i not in mains and rows[i] != {i: GRID}]
    for i in range(n):
        if i not in mains:
            targets[dim[charts[i]] - dim[word['initial'][i]]] += 1
    need(all(not row for row in rows[n:]), 'owned zero returns')
    common = GRID // common_divisor
    return dict(rows=rows, erased=erasures, lifetime=lifetimes, peak=peak, rises=rises,
                owned_events=owned_events, copies=copies, routes=routes, paid=paid,
                targets=targets, odd=odd, ops=ops, grid=common,
                mass=mass_max, mass_at=mass_at, readings=readings, bad_helpers=bad_helpers)


def compare_rows(a, b):
    return [i for i, (x, y) in enumerate(zip(a, b)) if x != y]


def signed_delta(a, b):
    return {k: b[k] - a[k] for k in sorted(a.keys() | b.keys()) if b[k] != a[k]}

# Gaussian numerators below have denominator 2**exponent.
COMPILER_SHA = '2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962'


def normalize(row, exponent):
    row = {i: (a, b) for i, (a, b) in row.items() if a or b}
    while exponent and all((a | b) & 1 == 0 for a, b in row.values()):
        row = {i: (a // 2, b // 2) for i, (a, b) in row.items()}
        exponent -= 1
    return row, exponent


def lut(columns):
    result = [0]
    for col in columns:
        result += [x ^ col for x in result]
    return result


def phases(q, linear):
    result = [0]
    for i, row in enumerate(q):
        result += [(p + linear[i] + 2 * ((row & x).bit_count() & 1)) % 4
                   for x, p in enumerate(result)]
    return result


def rotated(a, b, power):
    return ((a, b), (-b, a), (-a, -b), (b, -a))[power % 4]


def half_fourier(rank, bits):
    # Product of (1+i) for unmoved bits and (1-i) for flipped bits.
    pop = bits.bit_count()
    return rotated(1, rank % 2, rank // 2 - pop)


def frame_columns(basis, adjoint=False):
    rank = len(basis)
    columns = list(basis if 0 < rank < 9 else ())
    support = span(columns)
    for i in range(9):
        axis = 1 << i
        if axis not in support:
            columns.append(axis)
            support |= {x ^ axis for x in support}
    permutation = lut(columns)
    inverse = {y: x for x, y in enumerate(permutation)}
    dual = [inverse[1 << i] for i in range(9)]
    q = [(1 << i) ^ sum(((a & b).bit_count() % 2) << j for j, b in enumerate(dual))
         for i, a in enumerate(dual)]
    chart_phase = phases(q, [row >> i & 1 for i, row in enumerate(q)])
    if rank == 9:
        chart_phase = [0] * 512
    rot = []
    for bits in range(1 << rank):
        a, b = half_fourier(rank, bits)
        magnitude = 1 << (rank // 2)
        rot.append((a * magnitude, (-b if adjoint else b) * magnitude))
    return [
        normalize({x ^ shift: rotated(a, b, chart_phase[x ^ shift] - chart_phase[x])
                   for shift, (a, b) in zip(permutation, rot)}, rank)
        for x in range(512)
    ]


def monomial_table(rec):
    rows = rec['matrix_rows']
    permutation = lut([sum((row >> j & 1) << i for i, row in enumerate(rows))
                       for j in range(9)])
    phase = phases(rec['quadratic_rows'], rec['linear_Z4'])
    return [(y ^ rec['offset'], (p + rec['phase']) % 4) for y, p in zip(permutation, phase)]


def recipe_columns(recipe):
    rank = recipe['rank']
    left = monomial_table(recipe['left'])
    right = monomial_table(recipe['right'])
    columns = []
    for x in range(512):
        y, p = right[x]
        row = {}
        for i in range(1 << rank):
            z, q = left[y ^ i]
            a, b = half_fourier(rank, i)
            row[z] = rotated(a, b, p + q)
        columns.append(normalize(row, (rank + 1) // 2))
    return columns


def compose(first, second):
    columns = []
    for row, de in first:
        max_other = max(second[y][1] for y in row)
        values = {}
        for y, (a, b) in row.items():
            col, df = second[y]
            for z, (c, d) in col.items():
                olda, oldb = values.get(z, (0, 0))
                values[z] = (olda + ((a*c - b*d) << (max_other - df)),
                             oldb + ((a*d + b*c) << (max_other - df)))
        columns.append(normalize(values, de + max_other))
    return columns


def conjugate_transpose(matrix):
    transposed = [{} for _ in matrix]
    for x, (col, exponent) in enumerate(matrix):
        for y, (a, b) in col.items():
            transposed[y][x] = (a, -b, exponent)
    result = []
    for col in transposed:
        exponent = max(e for _, _, e in col.values())
        result.append(normalize({x: (a << (exponent - e), b << (exponent - e))
                                 for x, (a, b, e) in col.items()}, exponent))
    return result


def physical(frames, edits, source):
    import runpy

    raw = source.read_bytes()
    need(sha256(raw).hexdigest() == COMPILER_SHA, 'original compiler source hash')
    compiler = runpy.run_path(str(source))
    changed_routes = [
        [[tuple(e[2:4]) for patch in edits for e in patch[label]
          if e[0] == 'MOVE' and e[1] == field] for label in ('old', 'new')]
        for field in sorted({e[1] for patch in edits for label in ('old', 'new')
                             for e in patch[label] if e[0] == 'MOVE'})
    ]
    pairs = sorted({p for routes in changed_routes for route in routes for p in route})

    @cache
    def frame(i, adj=False):
        return frame_columns(frames[i], adj)

    @cache
    def chart(i):
        return compiler['canonical_frame'](9, tuple(frames[i]))

    receipts, operators = [], {}
    for a, b in pairs:
        rec, _ = compiler['lower_child'](chart(a).adjoint().then(chart(b)))
        rank = len(frames[b]) - len(frames[a])
        need(rec['rank'] == rank > 0, f'lowered child rank {a},{b}')
        expected = compose(frame(a, True), frame(b))
        actual = recipe_columns(rec)
        need(actual == expected, f'physical forward mismatch {a},{b}')
        expect_adjoint = compose(frame(b, True), frame(a))
        actual_adjoint = conjugate_transpose(actual)
        need(actual_adjoint == expect_adjoint, f'physical adjoint mismatch {a},{b}')
        need(all(len(row) == 1 << rank and
                 all((a*a + b*b) * (1 << rank) == 1 << (2 * e) for a, b in row.values())
                 for row, e in actual), f'physical support and squared modulus {a},{b}')
        mutated = dict(rec, left=dict(rec['left'], phase=(rec['left']['phase'] + 1) % 4))
        bad = recipe_columns(mutated)
        need(bad != expected and all(l.keys() == r.keys() for (l, _), (r, _) in zip(bad, actual)),
             'absolute phase control keeps support and changes amplitudes')
        operators[(a, b)] = (actual, actual_adjoint)
        receipts.append(dict(pair=[a, b], rank=rank, forward_columns=len(actual),
                             adjoint_columns=len(actual_adjoint), forward_sha256=digest(actual),
                             adjoint_sha256=digest(actual_adjoint), phase_control_column=0))
    for old, new in changed_routes:
        (a, b), (middle, c) = old
        need(b == middle and new == [(a, c)], 'route contraction endpoints')
        x, xadj = operators[a, b]
        y, yadj = operators[b, c]
        f, fadj = operators[a, c]
        need(compose(x, y) == f and compose(yadj, xadj) == fadj,
             f'absolute-phase physical route equality {a},{b},{c}')
    return dict(changed_pairs=receipts, contracted_routes=changed_routes, compiler_sha256=COMPILER_SHA)

OUTER_SHA = '60a743d13f668ef86db4b8215b4d5d04430a671ba6f1fe06d9c1c4c3dfe86da5'
CAP = Fraction('.00376669')
PREC = 78
NEAR = Context(prec=PREC, rounding=ROUND_HALF_EVEN)
DOWN = Context(prec=PREC, rounding=ROUND_FLOOR)
UP = Context(prec=PREC, rounding=ROUND_CEILING)
BINARY = 1 << 256


def scalar_service(text, addition):
    a, d = ratio(text)
    a = abs(a)
    return 4 * (a.bit_length() + d.bit_length() + 1 + (a.bit_count() if addition else 0))


def bill(word, caller, replayed, caller_odd_scale):
    specifications = caller['types']
    stages = caller['stages']
    port_counts = Counter({typ: len(t['ports']) for typ, t in specifications.items()})
    need(specifications['A']['ports'] == word['hosted']['Dports'], 'Type A D ports')
    need(sorted(chain.from_iterable(t['ports'] for t in specifications.values())) == list(range(104)),
         'Type A/B port partition')
    owners = {ty: set(range(t['offset'], t['offset'] + t['roles'])) for ty, t in specifications.items()}
    need(not (owners['A'] & owners['B']) and len(owners['A'] | owners['B']) == caller['roles'],
         'disjoint type owners')
    stages_seen, wrap, productive = [], Counter(), Counter()
    events_by_type = defaultdict(list)
    for e in caller['events']:
        if e[0] == 'J':
            _, stage, a, b = e
            need(len(set(a)) == 4 and set(a) <= owners['A'] and
                 len(set(b[:2])) == 2 and set(b[:2]) <= owners['B'] and b[2:] == ['-1', '1/2'],
                 'exclusive and signed joint bindings')
            stages_seen.append(stage)
            continue
        ty, op, r, *args = e
        need(r in owners[ty], 'caller local owner')
        if op in ('ADD', 'SWAP', 'QUERY'):
            need(args[0] in owners[ty] and args[0] != r, 'caller source owner')
        events_by_type[ty].append(e)
        if op == 'QUERY':
            wrap[1] += port_counts[ty]
        if op in ('IDLE_ONE', 'IDLE_ODD'):
            chosen = args[0]
            need(len(set(chosen)) == len(chosen) and 1 <= min(chosen) <= max(chosen) <= stages,
                 'caller idle stages')
            need(op != 'IDLE_ODD' or (ty == 'B' and len(chosen) == 1 and args[1:] == [-1]),
                 'signed idle controls')
            wrap[8 * len(chosen) + (op == 'IDLE_ODD')] += port_counts[ty]
    need(stages_seen == list(range(1, stages + 1)) and caller['ambient_rank'] == 9 + 8 * stages,
         'fixed chronological native invocations and ambient rank')
    route = {
        'moves': replayed['ops']['MOVE'],
        'helper_boundary': 2 * sum(replayed['targets'].values()),
        'main_boundaries': 2 * (sum(port_counts.values()) + port_counts['A']),
        'main_adapters': 4 * (sum(port_counts.values()) + port_counts['A']),
        'lifetime': 4 * len(replayed['lifetime']),
    }

    def swaps(axes):
        return sum(x >= len(axes) for x in axes)

    rest = {}
    caller_scalars = caller_macros = queries = idles = lambdas = signed_idle = 0
    max_num_bits = max(1125, caller_odd_scale).bit_length()
    for ty, table in specifications.items():
        p = port_counts[ty]
        output = 0
        for phase, zero, *bits in table['diagonal']:
            need(zero == 0 and len(bits) == stages and all(x in (0, 1) for x in bits),
                 'caller productive diagonal')
            needed = 8 * sum(bits) + phase % 2
            need(needed > 0 and any(bits), 'productive field without empty-root credit')
            productive[needed] += p
            axes = ([0] if phase else []) + [i for k, bit in enumerate(bits) if bit
                                             for i in range(9 + 8*k, 17 + 8*k)]
            output += p * 1000 * (2 * swaps(axes) + 2 * bool(phase) + (phase == -1))
        local = events_by_type[ty]
        rest[ty] = dict(envelope=32 * table['roles'] * p * (len(local) + stages),
                        field_boundary=26 * table['roles'] * p, output=output,
                        query=0, idle=0, fused=0, thin=0)
        caller_macros += len(local) * p
        for _, op, _, *args in local:
            if op == 'QUERY':
                rest[ty]['query'] += p * 1000 * (2 + (args[1] == -1))
                rest[ty]['thin'] += 16 * p
                queries += p
            elif op == 'IDLE_ONE':
                axes = [i for k in args[0] for i in range(1 + 8*k, 9 + 8*k)]
                rest[ty]['idle'] += 2 * p * 1000 * swaps(axes)
                idles += p
            elif op == 'IDLE_ODD':
                rest[ty]['fused'] += 36500 * p
                idles += p
                signed_idle += p
            elif op == 'LAMBDA':
                lambdas += p
            elif op in ('ADD', 'SCALE'):
                caller_scalars += p * scalar_service(args[-1], op == 'ADD')
                max_num_bits = max(max_num_bits, abs(ratio(args[-1])[0]).bit_length())
    native_scalars = 0
    for e in word['program']:
        if e[0] in ('ADD', 'COPY', 'SCALE'):
            coefficient = e[-2]
            native_scalars += scalar_service(coefficient, e[0] != 'SCALE')
            max_num_bits = max(max_num_bits, abs(ratio(coefficient)[0]).bit_length())
    paid, targets = wrap.copy(), productive.copy()
    for rank, count in replayed['paid'].items():
        paid[rank] += stages * count
    for rank, count in replayed['targets'].items():
        targets[rank] += stages * count
    surplus = sum(rank * count for rank, count in targets.items()) - sum(rank * count for rank, count in paid.items())
    caller_total = sum(sum(items.values()) for items in rest.values())
    native_routing = 1000 * sum(route.values())
    conversion = stages * word['public'] * sum(port_counts.values())
    caller_fields = sum(table['roles'] * port_counts[ty] for ty, table in specifications.items())
    odd_charge = 2 * caller_fields * 4 * (caller_odd_scale.bit_length() + 1 + caller_odd_scale.bit_count())
    ordinary = stages * (native_routing + native_scalars) + caller_total + conversion + 1000 * lambdas + caller_scalars + odd_charge
    need(ordinary < 10**9 and max_num_bits <= 24, 'ordinary and scalar numerator caps')
    # J contacts comprise four on each hosted A half and two paired contacts per B side.
    contacts = 4 * stages * (2 * port_counts['A'] + port_counts['B'])
    slots = 2 * sum(paid.values()) + 2 * sum(targets.values()) + contacts + 2 * idles + 3 * queries + lambdas + signed_idle
    per_map = 4 * (caller['ambient_rank'] + 1)**2
    native_macro = stages * (len(word['program']) - replayed['ops']['MOVE'])
    conversions = 2 * (stages * word['public'] + caller_fields)
    tape = dict(native_invocations=stages, monomial_map_slots=slots, elementary_records_upper=slots * per_map,
                scalar_services_upper=32 * (native_macro + caller_macros + conversions))
    return dict(paid=paid, targets=targets, surplus=surplus, caller_paid=wrap, caller_productive=productive,
                ordinary=ordinary, ordinary_native_scalar=native_scalars, ordinary_native_routes=native_routing,
                ordinary_route_counts=route, ordinary_caller_routes=rest, ordinary_caller_total=caller_total,
                ordinary_conversion=conversion, ordinary_caller_scalar=caller_scalars,
                ordinary_odd_caller_conversion=odd_charge, ordinary_lambda_surcharge=1000*lambdas,
                native_contacts=contacts, signed_idle_uses=signed_idle, idle_uses=idles, queries=queries, lambdas=lambdas,
                reserved_owned_banks=stages * word['owned_fields'], max_scalar_numerator_bits=max_num_bits,
                tape=tape, tape_macro_inputs=dict(native=native_macro, caller=caller_macros, conversions=conversions))


@cache
def log_decimal(rank):
    z = NEAR.ln(Decimal(rank))
    return NEAR.next_minus(z), NEAR.next_plus(z)


def as_decimal(q, cx):
    return cx.divide(Decimal(q.numerator), Decimal(q.denominator))


def decimal_power(rank, k):
    if rank == 1 or not k:
        return Decimal(rank), Decimal(rank)
    l, u = log_decimal(rank)
    x = DOWN.multiply(as_decimal(-k, DOWN), u)
    y = UP.multiply(as_decimal(-k, UP), l)
    return (DOWN.multiply(Decimal(rank), NEAR.next_minus(NEAR.exp(x))),
            UP.multiply(Decimal(rank), NEAR.next_plus(NEAR.exp(y))))


@cache
def sqrt_powers(rank):
    l = u = BINARY * rank
    dyadic = []
    for _ in range(176):
        l = isqrt(l * BINARY)
        r = isqrt(u * BINARY)
        u = r + (r*r < u*BINARY)
        dyadic.append((l, u))
    return dyadic


def dyadic_power(rank, k):
    # Evaluate rank ** (1-k) by rationally comparing the remaining
    # binary expansion to the next full dyadic exponent.
    need(0 <= k <= 1, 'exponent range')
    e = 1 - k
    whole, remainder = divmod(e.numerator, e.denominator)
    lower = upper = BINARY * rank**whole
    roots = sqrt_powers(rank)
    for a, b in roots:
        bit, remainder = divmod(2 * remainder, e.denominator)
        if bit:
            lower = (lower * a) // BINARY
            upper = -((-upper * b) // BINARY)
    if remainder:
        upper = -((-upper * roots[-1][1]) // BINARY)
    return lower, upper


def moments(hist, k, power, down, up):
    lo = hi = 0
    for rank, coefficient in hist.items():
        if coefficient:
            a, b = power(rank, k)
            if coefficient < 0:
                a, b = b, a
            lo, hi = down(lo, a, coefficient), up(hi, b, coefficient)
    return lo, hi


def decimal_moment(hist, k):
    def term(cx, acc, value, coefficient):
        return cx.add(acc, cx.multiply(value, Decimal(coefficient)))
    return moments(hist, k, decimal_power, lambda *xs: term(DOWN, *xs), lambda *xs: term(UP, *xs))


def dyadic_moment(hist, k):
    weighted = lambda acc, val, coeff: acc + val * coeff
    return moments(hist, k, dyadic_power, weighted, weighted)


def crossing(hist):
    unit = 10**35
    lo, hi = 0, int(CAP * unit)
    need(decimal_moment(hist, Fraction(lo, unit))[0] > 0 and
         decimal_moment(hist, Fraction(hi, unit))[1] < 0, 'starting directed price bracket')
    while hi - lo > 1:
        mid = (lo + hi) // 2
        a, b = decimal_moment(hist, Fraction(mid, unit))
        if a > 0:
            lo = mid
        elif b < 0:
            hi = mid
        else:
            raise ValueError('ambiguous decimal bisection')
    low, high = Fraction(lo, unit), Fraction(hi, unit)
    need(dyadic_moment(hist, low)[0] > 0 > dyadic_moment(hist, high)[1],
         'independent integer-root crossing signs')
    return low, high


def price(old, new, final, interval_source):
    import runpy

    need(sha256(interval_source.read_bytes()).hexdigest() == OUTER_SHA, 'original M-model gate hash')
    outer = runpy.run_path(str(interval_source))
    hist = lambda bill: {r: bill['targets'][r] - bill['paid'][r]
                         for r in bill['targets'].keys() | bill['paid'].keys()}
    old_hist, new_hist = hist(old), hist(new)
    old_bracket = crossing(old_hist)
    new_bracket = crossing(new_hist)
    # Use the original effective deltas and publication decimal granularity.
    invoices = {label: {'P': dict(b['paid']), 'T': dict(b['targets'])}
                for label, b in [('original', old), ('candidate', new)]}
    gates = {}
    for label, precinct, slack in [('framework', 10**15, Fraction(7, 10**17)),
                                   ('public', 10**13, Fraction(7, 10**14))]:
        if label == 'framework':
            old_claim = Fraction(final['framework_claim'])
        else:
            old_claim = Fraction(final['claim'])
        scaled = (new_bracket[0] - slack) * precinct
        claim = Fraction((scaled.numerator - 1) // scaled.denominator, precinct)
        need(claim > old_bracket[1], f'{label} exceeds original directed ceiling')
        for invoice_label, h, point, sign in [
            ('original', old_hist, old_claim + slack, 1),
            ('candidate', new_hist, claim + slack, 1),
            ('restored', old_hist, claim, -1),
        ]:
            l, u = decimal_moment(h, point)
            a, b = dyadic_moment(h, point)
            need((l > 0 and a > 0) if sign > 0 else (u < 0 and b < 0),
                 f'{invoice_label} {label} two independent directed signs')
        old_gate = outer['gate'](invoices['original'], old_claim, old_claim + slack, *old_bracket, CAP)
        new_gate = outer['gate'](invoices['candidate'], claim, claim + slack, *new_bracket, CAP)
        gates[label] = dict(original=old_gate, candidate=new_gate)
    show = lambda bracket: [str(NEAR.divide(Decimal(x.numerator), Decimal(x.denominator))) for x in bracket]
    return dict(original_crossing=show(old_bracket), candidate_crossing=show(new_bracket),
                raw_gain_bounds=show((new_bracket[0] - old_bracket[1], new_bracket[1] - old_bracket[0])),
                restored_invoice_negative=True, interval_source_sha256=OUTER_SHA, gates=gates)

CALLER_ARCHIVE_SHA = '617341e053d7d4bc971ff3690ab2db01b1da8b3847ac4a71cc68f044b532efb5'
ARCHIVE_MEMBER = 'research/p104-cohort-short-caller/inputs/pr7113.tar'
CALLER_SOURCE_PREFIX = 'research/signed-caller-8x9/replay/supplier7112/short-caller/'


def caller_source(source_root):
    from io import BytesIO
    import tarfile

    base = source_root / 'retained/role902'
    route = json.loads((base / 'bench/TARIFF-SOURCE.json').read_bytes())['chain']
    raw = (base / 'upstream/inputs/pr7480/inputs/pr7334.tar.gz').read_bytes()
    for item in route:
        need(sha256(raw).hexdigest() == item['archive_sha256'], 'original archive chain hash')
        with tarfile.open(fileobj=BytesIO(raw)) as package:
            if ARCHIVE_MEMBER in package.getnames():
                raw = package.extractfile(ARCHIVE_MEMBER).read()
                break
            raw = package.extractfile(item['member']).read()
    need(sha256(raw).hexdigest() == CALLER_ARCHIVE_SHA, 'literal #7113 archive hash')
    return tarfile.open(fileobj=BytesIO(raw))


def original_caller_grid(archive, caller, original_caller_path):
    path = CALLER_SOURCE_PREFIX + 'check_odd_caller_exact_grid.py'
    source = archive.extractfile(path).read().decode()
    start, end = source.index('primes='), source.index('with (root/')
    scope = dict(C=caller, Q=Fraction, prod=prod, sha256=sha256, cpath=original_caller_path)
    exec(compile(source[start:end], path, 'exec'), scope)
    return scope['rec']


def exact_precision(archive, caller, word, stats, caller_grid):
    from types import ModuleType

    prefix = CALLER_SOURCE_PREFIX + 'admission-source/retained/query-only-precision-envelope/'
    paths = [prefix + name for name in ('source_binding.py', 'envelopes.py')]
    source_binding, text = [archive.extractfile(p).read() for p in paths]
    source = text.decode()
    helper_count = sum(stats['targets'].values())
    replacements = [
        ('(54, 43, 51)', repr((len(stats['lifetime']), stats['peak'], word['owned_fields'])), 1),
        ('elif op in ("LAMBDA", "IDLE_ONE"):', 'elif op in ("LAMBDA", "IDLE_ONE", "IDLE_ODD"):', 2),
        ('all(0 <= r < 38 for r in ar) and all(38 <= r < 76 for r in br[:2])',
         'all(r in local_owners(caller, "A") for r in ar) and all(r in local_owners(caller, "B") for r in br[:2])', 1),
        ('all(1 <= k <= 18 for k in e[3])', 'all(1 <= k <= caller["stages"] for k in e[3])', 1),
        ('list(range(1, 19))', 'list(range(1, caller["stages"] + 1))', 1),
        ('word["public"] - len(mains) == 1061', f'word["public"] - len(mains) == {helper_count}', 1),
        ('physical_main_inputs=3952, fresh_arbitrary_helpers=18 * 1061,',
         f'physical_main_inputs=caller["roles"] * 52, fresh_arbitrary_helpers=caller["stages"] * {helper_count},', 1),
    ]
    for before, after, count in replacements:
        need(source.count(before) == count, 'audited original envelope source substitution')
        source = source.replace(before, after)
    # The signed IDLE_ODD signature and actual COPY zero were verified separately.
    binding = ModuleType('source_binding')
    binding.__file__ = paths[0]
    old_binding = sys.modules.get(binding.__name__)
    sys.modules[binding.__name__] = binding

    def owners(c, ty):
        spec = c['types'][ty]
        return range(spec['offset'], spec['offset'] + spec['roles'])

    try:
        exec(compile(source_binding, paths[0], 'exec'), binding.__dict__)
        scope = dict(__name__='verified_original_envelope', local_owners=owners)
        exec(compile(source, paths[1], 'exec'), scope)
        native_peaks, native = scope['native_envelope'](word)
        caller_peaks, caller_receipt = scope['caller_envelope'](caller, native_peaks, word)
    finally:
        if old_binding is None:
            del sys.modules[binding.__name__]
        else:
            sys.modules[binding.__name__] = old_binding
    odd = stats['grid']
    dyadic = (odd & -odd).bit_length() - 1
    odd >>= dyadic
    height = caller_grid['grid_exponents'][0] + dyadic
    mass = binding.strict_power(caller_peaks['M_context'][0]) + caller_grid['caller_odd_scale_bits'] + odd.bit_length()
    c = 2 * max(height, mass)
    return dict(context_c=c, context_height=height, context_mass_bits=mass,
                source_sha256=sha256(text).hexdigest(), executed_code_sha256=sha256(source.encode()).hexdigest(),
                native=native, caller=caller_receipt)


def h_check(precision, gate):
    h = int(gate['H'])
    kstar = 1920 * 153**1920 * (h + 1)**2
    c = precision['context_c']
    bound = max(v['strict_power_of_two'] for v in precision['caller']['bounds'].values())
    need(c <= 4096 and (4096*kstar).bit_length() < h and bound < h, 'tape H and precision inequalities')
    return dict(H=h, Kstar_bits=kstar.bit_length(), context_c=c, context_bound_bits=(c*kstar).bit_length(),
                conservative_context_bound_bits=(4096*kstar).bit_length(), rounded_caller_bound_exponent=bound)


def word_audit(old, new, changes, aligned):
    n = old['public']
    fields = {e[1] for ed in changes for t in ('old', 'new') for e in ed[t]}

    def operands(e):
        return e[1:3] if e[0] in ('ADD', 'COPY') else e[1:2]

    selected = {i: j for i, j in aligned.items()
                if fields.intersection(operands(old['program'][i]))
                or max(operands(old['program'][i])) >= n}
    a_watch = set(selected) | {i for ed in changes for i in range(ed['old_start'], ed['old_start'] + len(ed['old']))}
    b_watch = set(selected.values()) | {i for ed in changes for i in range(ed['new_start'], ed['new_start'] + len(ed['new']))}
    a = replay(old, a_watch)
    b = replay(new, b_watch)
    for key in ('erased', 'lifetime', 'peak', 'rises', 'owned_events', 'copies', 'targets', 'grid', 'mass'):
        need(a[key] == b[key], 'baseline/candidate ' + key)
    need(not a['bad_helpers'] and not b['bad_helpers'], 'all arbitrary helper identities')
    need(a['rows'] == b['rows'], 'all exact output and returned rows')
    private_reads = {i: j for i, j in selected.items() if max(operands(old['program'][i])) >= n}
    private_diffs = []
    for i, j in private_reads.items():
        for r, u, v in zip(operands(old['program'][i]), a['readings'][i], b['readings'][j]):
            if u != v:
                private_diffs.append([i, j, r])
    need(not private_diffs, 'all paired private-contact entrance values: ' + str(private_diffs[:6]))
    changed_reads = [[i, j, list(operands(old['program'][i])), [r for r, u, v in
                      zip(operands(old['program'][i]), a['readings'][i], b['readings'][j]) if u != v]]
                     for i, j in selected.items() if a['readings'][i] != b['readings'][j]]
    recovered = {}
    # Identify each affected register's last changed action, then inspect the
    # actual preserved reads downstream, including contacts before the other
    # helper has finished its route.
    for r in sorted(fields):
        related = [ed for ed in changes if any(e[1] == r for label in ('old', 'new') for e in ed[label])]
        if not any(ed['old_start'] for ed in related):
            related = changes
        last_change = max(ed['old_start'] + max(len(ed['old']) - 1, 0) for ed in related)
        readbacks = []
        for i, j in selected.items():
            event = old['program'][i]
            if i > last_change and event[0] in ('ADD', 'COPY') and event[2] == r:
                left, right = a['readings'][i][1], b['readings'][j][1]
                need(left == right, f'retained source observation {r} at {i}/{j}')
                readbacks.append(dict(original_index=i, candidate_index=j, event=event, row_sha256=digest(left)))
        recovered[r] = readbacks

    # Alter an actual encoding coefficient while preserving legality and the MOVE itinerary.
    index = next(i for i, e in enumerate(new['program']) if e[0] == 'ADD' and e[1:4] == [185, 779, '-1/4'])
    event = new['program'][index].copy()
    event[3] = '-1/2'
    mutant = replay(new, set(), False, (index, event))
    output_diffs = compare_rows(a['rows'], mutant['rows'])
    erasure_diffs = compare_rows(a['erased'], mutant['erased'])
    need(output_diffs or erasure_diffs, 'legal coefficient fault must change an observable consequence')
    if output_diffs:
        output = output_diffs[0]
        normal, changed = a['rows'][output], mutant['rows'][output]
        column = next(i for i in sorted(normal.keys() | changed.keys()) if normal.get(i, 0) != changed.get(i, 0))
        witness = dict(output=output, public_basis_input=column,
                       original=str(Fraction(normal.get(column, 0), GRID)),
                       mutated=str(Fraction(changed.get(column, 0), GRID)))
    else:
        witness = dict(first_changed_ordered_erasure=erasure_diffs[0])
    rows = [sorted(row.items()) for row in a['rows']]
    # Matrix columns of the transpose are the original rows. Each entry is
    # rational and exact, so real conjugate-transpose equivalence follows for
    # the linear map with retirement rows exposed as separate outputs.
    result = dict(public_input_columns=n, final_rows=len(rows), final_rows_sha256=digest(rows),
                  ordered_erasures=len(a['erased']), ordered_erasure_sha256=digest(a['erased']),
                  nonzero_erasure_rows=sum(bool(e[2]) for e in a['erased']),
                  arbitrary_helper_returns=sum(a['targets'].values()), owned_fields=old['owned_fields'],
                  owned_lifetimes=len(a['lifetime']), owned_active_peak=a['peak'], owned_ascent_rank_mass=a['rises'],
                  owned_interface_events=len(a['owned_events']), owned_interface_inputs_checked=len(private_reads),
                  owned_contacts_sha256=digest(a['owned_events']), copy_zero_guards=a['copies'],
                  total_common_grid=a['grid'], native_scaled_mass=str(Fraction(a['mass'], 1 << 25)),
                  peak_mass_cuts=dict(original=a['mass_at'], candidate=b['mass_at']),
                  new_native_paid=b['paid'], old_native_paid=a['paid'], native_delta=signed_delta(a['paid'], b['paid']),
                  op_delta=signed_delta(a['ops'], b['ops']), odd_divisions=b['odd'],
                  changed_full_routes={r: [a['routes'].get(r, []), b['routes'].get(r, [])]
                                       for r in sorted(a['routes'].keys() | b['routes'].keys())
                                       if a['routes'].get(r) != b['routes'].get(r)},
                  internal_changed_contact_values=changed_reads,
                  retained_downstream_source_observations=recovered,
                  coefficient_control=dict(index=index, actual=new['program'][index], altered=event, witness=witness,
                                           changed_outputs=output_diffs, changed_erasures=erasure_diffs))
    return a, b, result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for arg in ('candidate', 'original-word', 'original-invoice', 'original-final', 'signed-caller',
                'original-source', 'out'):
        parser.add_argument('--' + arg, required=True, type=Path)
    args = parser.parse_args()
    need(__debug__, 'run without Python -O')
    start = monotonic()
    report = dict(schema='croc-sprint-verifier/1', started_utc=stamp(),
                  source_heads={'native': 'e1d2756eecf03e146338239fee81772a99ba8d4c',
                                'caller': '07a76c5e2738882c0cb322278e56f6cae3c9885d'},
                  plan_frozen_utc='2026-11-17T19:03:09Z', hashes=PIN, stages=[])
    stage = 'input authentication'

    def checkpoint(name):
        receipt = dict(stage=name, elapsed_seconds=round(monotonic()-start, 3), utc=stamp())
        report['stages'].append(receipt)
        print(json.dumps(receipt), flush=True)

    try:
        old = load(args.original_word, 'word')
        new = load(args.candidate, 'candidate')
        bill_pin = load(args.original_invoice, 'invoice')
        final = load(args.original_final, 'final')
        caller = load(args.signed_caller, 'caller')
        old_digest, new_digest = digest(old), digest(new)
        need(final['candidate_canonical_sha256'] == old_digest and
             final['caller_sha256'] == PIN['caller'] and final['assumptions'] == PREMISES,
             'original FINAL source binding and five assumptions')
        need(all(old.get(k) == new.get(k) for k in (old.keys() | new.keys()) - {'program'}),
             'only program changed')
        report['canonical_sha256'] = dict(original=old_digest, candidate=new_digest)
        report['premises'] = PREMISES
        changes, aligned = program_diff(old['program'], new['program'])
        report['program_edits'] = changes
        checkpoint(stage)
        stage = 'full exact rational word and control'
        a, b, audit = word_audit(old, new, changes, aligned)
        report['word'] = audit
        checkpoint(stage)
        stage = 'physical route columns and absolute phase controls'
        base = args.original_source / 'retained/role902'
        report['physical'] = physical(old['frames'], changes, base / 'independent/engines/clifford_exact.py')
        checkpoint(stage)
        with caller_source(args.original_source) as archive:
            stage = 'fixed signed caller exact grid and charge census'
            caller_bytes = archive.extractfile('research/signed-caller-8x9/expected/ODD-TYPE-AB-CALLER.json').read()
            need(sha256(caller_bytes).hexdigest() == PIN['caller'], 'same supplied #7113 caller as source archive')
            cg = original_caller_grid(archive, caller, args.signed_caller)
            report['caller_exact_grid'] = cg
            old_bill, new_bill = [bill(word, caller, stats, int(cg['caller_odd_scale']))
                                  for word, stats in ((old, a), (new, b))]
            for key in ('paid', 'targets'):
                need(old_bill[key] == {int(r): count for r, count in bill_pin[key].items()}, 'original literal invoice ' + key)
            need(old_bill['ordinary'] == final['ordinary_bound'] and old_bill['tape'] == final['tape'] and
                 old_bill['surplus'] == final['surplus'], 'original ordinary, tape and surplus reproduce')
            need(old_bill['targets'] == new_bill['targets'] and old_bill['surplus'] == new_bill['surplus'],
                 'productive invoice and rank surplus preserved')
            report['bill'] = dict(original=old_bill, candidate=new_bill,
                                  paid_delta=signed_delta(old_bill['paid'], new_bill['paid']),
                                  ordinary_delta=new_bill['ordinary']-old_bill['ordinary'],
                                  tape_delta=signed_delta(Counter(old_bill['tape']), Counter(new_bill['tape'])))
            checkpoint(stage)
            stage = 'two directed prices and retained M-model numeric gates'
            prices = price(old_bill, new_bill, final, base / 'engines/interval_gate.py')
            report['price'] = prices
            checkpoint(stage)
            stage = 'precision majorants, adjoint witnesses, and H checks'
            precisions = {label: exact_precision(archive, caller, word, stats, cg)
                          for label, word, stats in [('original', old, a), ('candidate', new, b)]}
            need(precisions['original']['context_c'] == final['precision_c'], 'original precision factor reproduces')
            report['precision'] = precisions
            report['tape_H_checks'] = {kind: {label: h_check(precisions[label], gate)
                                             for label, gate in gates.items()}
                                      for kind, gates in prices['gates'].items()}
            need(report['tape_H_checks']['public']['original']['H'] == final['public_H'],
                 'original public H reproduces')
            checkpoint(stage)
        report['status'] = 'VERIFIED_LOCAL_EXACT_AND_NUMERIC; FULL_SIGNED_ENGINE_OUTSTANDING'
        report['outstanding'] = [
            'Complete candidate-hash signed physical binding, 17-call child/caller application, contact phase-polynomial checks and global catalogue replay.',
            'Complete original-engine candidate native all-columns catalogue and whole signed/final assembly. Changed native paid pairs have exact forward and adjoint coverage here.',
            'Separate 18-stage native ingredient M-model price/admission gate. The 17-stage signed framework and public M-model numeric gates were evaluated.',
        ]
    except Exception as exc:
        report['status'] = 'CHECK_DISCREPANCY_OR_FAILURE'
        report['failure'] = dict(stage=stage, type=type(exc).__name__, message=str(exc))
        raise
    finally:
        report['finished_utc'] = stamp()
        report['elapsed_seconds'] = round(monotonic()-start, 3)
        report['command'] = ['python3.12', 'verify.py', '--candidate', 'frozen.json.gz',
                             '--original-word', 'originals/word.json.gz',
                             '--original-invoice', 'originals/invoice-new.json',
                             '--original-final', 'originals/FINAL.json',
                             '--signed-caller', 'originals/7113-CALLER.json',
                             '--original-source', '<pinned-original-source-directory>',
                             '--out', args.out.name]
        report['checker_sha256'] = sha256(Path(__file__).read_bytes()).hexdigest()
        temporary = args.out.with_name(args.out.name + '.tmp')
        temporary.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
        temporary.replace(args.out)


if __name__ == '__main__':
    main()
