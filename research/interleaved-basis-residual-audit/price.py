"""Count the complete invoice and enclose its prices with rational series.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
No retained pricing engine is used.
"""

from collections import Counter
from fractions import Fraction as F
from functools import cache
from math import factorial
import gzip
import json

import audit


def basis(vectors):
    pivots = {}
    for value in vectors:
        while value:
            bit = value.bit_length() - 1
            if bit not in pivots:
                pivots[bit] = value
                break
            value ^= pivots[bit]
    audit.require(len(pivots) == len(vectors), 'dependent chart basis')
    return pivots


def included(left, right):
    for value in left.values():
        for bit in sorted(right, reverse=True):
            if value >> bit & 1:
                value ^= right[bit]
        if value:
            return False
    return True


def invoice():
    graph, layout, net = audit.construction.build()
    expected = audit.read('results/application.json')
    audit.require(audit.construction.digest(graph) == expected['graph_sha256'], 'complete graph pin')
    interface = audit.read('data/BASE-INTERFACE.json')
    stable_main = {interface['keep'][i] for i in interface['main_roles']}
    mains = {i for i, stable in enumerate(layout['source_labels']) if stable in stable_main}
    audit.require(len(mains) == len(stable_main) == 400 and len(net.initial) == 1260, 'main and helper inventory')
    frames = list(map(basis, graph['frames']))
    def rank(a, b, productive=False):
        forward, reverse = included(frames[a], frames[b]), included(frames[b], frames[a])
        audit.require(forward != reverse, 'non-strict or non-nested transfer')
        audit.require(not productive or forward, 'productive orientation')
        return abs(len(frames[a]) - len(frames[b]))
    native_paid = Counter(rank(a, b) for a, b in net.moves.values())
    native_targets = Counter(rank(a, b, True) for i, (a, b) in enumerate(zip(net.initial, net.final, strict=True)) if i not in mains)
    caller = json.loads(gzip.decompress((audit.SOURCE / 'data/CALLER.json.gz').read_bytes()))
    paid, targets, stages = Counter(), Counter(), []
    for event in caller['events']:
        kind = event[0]
        if kind == 'J':
            stages.append(event[1])
            audit.require(len(set(event[2])) == 4 and event[3][0] != event[3][1], 'joint owner alias')
            continue
        replicas = len(caller['types'][kind]['ports'])
        op = event[1]
        if op == 'QUERY':
            audit.require(event[2] != event[3] and event[4] in (-1, 1), 'query contract')
            paid[1] += replicas
        elif op in ('IDLE_ONE', 'IDLE_ODD'):
            block = event[3]
            audit.require(block and len(block) == len(set(block)) and all(1 <= i <= 16 for i in block), 'idle support')
            odd = op == 'IDLE_ODD'
            audit.require(not odd or len(block) == 1 and event[4] == -1, 'odd idle contract')
            paid[8 * len(block) + odd] += replicas
        else:
            audit.require(op in ('ADD', 'SCALE', 'SWAP', 'LAMBDA'), 'unpriced caller operation')
    audit.require(stages == list(range(1, 17)) and caller['ambient_rank'] == 137, 'complete caller stages')
    for spec in caller['types'].values():
        audit.require(len(spec['diagonal']) == spec['roles'], 'complete root target inventory')
        for phase, coefficient_phase, *powers in spec['diagonal']:
            audit.require(phase in (-1, 0, 1) and coefficient_phase == 0 and len(powers) == 16
                          and set(powers) <= {0, 1} and any(powers), 'root target contract')
            targets[8 * sum(powers) + phase % 2] += len(spec['ports'])
    fixed_paid, fixed_targets = dict(paid), dict(targets)
    paid.update({r: 16 * n for r, n in native_paid.items()})
    targets.update({r: 16 * n for r, n in native_targets.items()})
    result = {name: {str(r): n for r, n in sorted(hist.items())} for name, hist in (('paid', paid), ('targets', targets))}
    for side in ('paid', 'targets'):
        audit.require(result[side] == expected['invoice'][side], 'complete invoice differs')
    surplus = sum(r * n for r, n in targets.items()) - sum(r * n for r, n in paid.items())
    audit.require(surplus == 1328 and sum(paid.values()) == 96512 and sum(targets.values()) == 17296, 'complete caller counts')
    return result, dict(graph_sha256=expected['graph_sha256'], paid=sum(paid.values()), productive=sum(targets.values()),
                        surplus=surplus, stages=16, native_paid=dict(native_paid), native_targets=dict(native_targets),
                        fixed_paid=fixed_paid, fixed_targets=fixed_targets, independent_helpers=len(net.initial) - len(mains))


def round_out(low, high, digits):
    scale = 10 ** digits
    a, b = low * scale, high * scale
    return F(a.numerator // a.denominator, scale), F(-(-b.numerator // b.denominator), scale)


@cache
def log_interval(number):
    exponent = number.bit_length() - 1
    residual = F(number, 1 << exponent)
    def series(value):
        x = (value - 1) / (value + 1)
        audit.require(0 <= x <= F(1, 3), 'log reduction')
        n = 80
        low = 2 * sum(x ** (2 * j + 1) / (2 * j + 1) for j in range(n))
        high = low + 2 * x ** (2 * n + 1) / ((2 * n + 1) * (1 - x * x))
        return low, high
    a, b = series(F(2))
    c, d = series(residual)
    return round_out(exponent * a + c, exponent * b + d, 60)


def rank_price(rank, kappa):
    low, high = log_interval(rank)
    a, b = kappa * low, kappa * high
    audit.require(0 <= a <= b < 1, 'alternating exponential range')
    lower = sum((-b) ** j / factorial(j) for j in range(18))
    upper = sum((-a) ** j / factorial(j) for j in range(17))
    lower, upper = round_out(rank * lower, rank * upper, 40)
    return lower, upper


def margin(invoice, point):
    kappa = F(point)
    low = high = F(0)
    for side, sign in (('targets', 1), ('paid', -1)):
        for rank, count in invoice[side].items():
            a, b = rank_price(int(rank), kappa)
            low += count * (a if sign == 1 else -b)
            high += count * (b if sign == 1 else -a)
    return tuple(map(str, round_out(low, high, 25)))


def verify_prices(invoice):
    price = audit.read('PRICE.json')
    rows = []
    for point, sign in [(price['claim'], 1), (price['bracket'][0], 1), (price['bracket'][1], -1)]:
        low, high = margin(invoice, point)
        audit.require(F(low) > 0 if sign == 1 else F(high) < 0, 'complete margin sign differs')
        rows.append(dict(kappa=point, productive_minus_paid=[low, high]))
    return rows
