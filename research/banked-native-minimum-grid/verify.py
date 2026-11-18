#!/usr/bin/env python3
"""Certify minimum scalar grids of the pinned banked native DAG.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction
from hashlib import sha1, sha256
from math import gcd, lcm
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parent
PRIMES = (2, 3, 5)


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sources():
    record = json.loads((ROOT/'PREDECESSOR.json').read_text())
    for pin in record['files']:
        raw = (ROOT/'predecessor'/pin['path']).read_bytes()
        require(len(raw) == pin['bytes'] and sha256(raw).hexdigest() == pin['sha256'], 'predecessor bytes')
        require(sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest() == pin['git_blob'], 'predecessor Git blob')
    sys.path.insert(0, str(ROOT/'predecessor'))
    import network
    word = network.source_word()
    parent, net, edits = network.networks(word)
    require(len(edits) == 15 and len(parent.moves) == 6157 and len(net.moves) == 6142, 'source graph')
    return word, net


def vprime(value, prime):
    exponent = 0
    while value % prime == 0:
        value //= prime
        exponent += 1
    return exponent


def recursive_bound(net, order):
    bounds = {~r: 1 for r in range(len(net.initial))}
    grid = 1
    for node in order:
        bounds[node] = lcm(*(bounds[donor]*q.denominator for donor, q in net.forms[node].items()))
        grid = lcm(grid, bounds[node])
    return grid


def lower_witnesses(old, new, coefficient, info, grid, witnesses):
    if old == new:
        return
    for prime in PRIMES:
        if vprime(new, prime) < vprime(old, prime):
            q = Fraction(coefficient, grid)
            witnesses[str(prime)] = {**info, 'coefficient': str(q), 'denominator': q.denominator}


def integer_trace(net, order, grid, collect):
    values = {~r: {r: grid} for r in range(len(net.initial))}
    product_gcd = snapshot_gcd = grid
    product_witnesses, snapshot_witnesses = {}, {}
    products = 0
    for node in order:
        row = {}
        for donor, factor in sorted(net.forms[node].items()):
            for owner, value in values[donor].items():
                term, remainder = divmod(factor.numerator*value, factor.denominator)
                require(remainder == 0, 'nonintegral literal scalar product')
                if collect:
                    new = gcd(product_gcd, term)
                    lower_witnesses(product_gcd, new, term,
                                    {'node': node, 'donor': donor, 'input': owner, 'factor': str(factor)},
                                    grid, product_witnesses)
                    product_gcd = new
                total = row.get(owner, 0)+term
                if total:
                    row[owner] = total
                else:
                    row.pop(owner, None)
                products += 1
        if collect:
            for owner, value in row.items():
                new = gcd(snapshot_gcd, value)
                lower_witnesses(snapshot_gcd, new, value, {'node': node, 'input': owner},
                                grid, snapshot_witnesses)
                snapshot_gcd = new
        values[node] = row
    return values, {'products': products, 'snapshot_rows': len(order),
                    'minimum_product_grid': grid//product_gcd,
                    'minimum_snapshot_grid': grid//snapshot_gcd,
                    'product_witnesses': product_witnesses,
                    'snapshot_witnesses': snapshot_witnesses}


def endpoints(word, net, rows, grid):
    expected = [{r: grid} for r in range(word['public'])]
    for port, x in enumerate(word['live']):
        y = x+112
        if port in word['hosted']['Dports']:
            expected[y] = {x: grid, y: grid}
        else:
            expected[x] = {x: grid, y: -grid}
            expected[y] = {x: grid//2, y: grid//2}
    for x, y in zip(word['hosted']['X2'], word['hosted']['Y2'], strict=True):
        expected[x] = {x: grid, y: -grid}
    require([rows[net.first_output+r] for r in range(word['public'])] == expected, 'public endpoint rows')


def fraction_columns(net, order, data):
    # This pass evaluates only the four named basis inputs, without integer scaling.
    witnesses = [('product', v) for v in data['product_witnesses'].values()]
    witnesses += [('snapshot', v) for v in data['snapshot_witnesses'].values()]
    owners = sorted({v['input'] for _, v in witnesses})
    observed = {}
    for owner in owners:
        values = {~r: Fraction(int(r == owner)) for r in range(len(net.initial))}
        for node in order:
            total = Fraction(0)
            for donor, factor in sorted(net.forms[node].items()):
                term = factor*values[donor]
                for kind, w in witnesses:
                    if kind == 'product' and w['input'] == owner and w['node'] == node and w['donor'] == donor:
                        require(str(term) == w['coefficient'] and str(factor) == w['factor'], 'rational product witness')
                        observed[(kind, w['node'], owner)] = term
                total += term
            values[node] = total
            for kind, w in witnesses:
                if kind == 'snapshot' and w['input'] == owner and w['node'] == node:
                    require(str(total) == w['coefficient'], 'rational snapshot witness')
                    observed[(kind, node, owner)] = total
    require(len(observed) == 6, 'rational witness coverage')
    return owners


def first_failure(net, order, owner, grid):
    values = {~r: grid*int(r == owner) for r in range(len(net.initial))}
    for node in order:
        total = 0
        for donor, factor in sorted(net.forms[node].items()):
            numerator = factor.numerator*values[donor]
            term, remainder = divmod(numerator, factor.denominator)
            if remainder:
                return {'node': node, 'donor': donor, 'input': owner, 'grid': grid,
                        'numerator': numerator, 'divisor': factor.denominator, 'remainder': remainder}
            total += term
        values[node] = total
    raise ValueError('understated grid unexpectedly completed')


def sharpness(net, order, data):
    product_grid = data['minimum_product_grid']
    snapshot_grid = data['minimum_snapshot_grid']
    failures = []
    for prime in PRIMES:
        w = data['product_witnesses'][str(prime)]
        require((Fraction(w['coefficient'])*(product_grid//prime)).denominator > 1,
                'product prime-factor sharpness')
        failures.append(first_failure(net, order, w['input'], product_grid//prime))
        w = data['snapshot_witnesses'][str(prime)]
        require((Fraction(w['coefficient'])*(snapshot_grid//prime)).denominator > 1,
                'snapshot prime-factor sharpness')
    for prime in (2, 5):
        w = data['product_witnesses'][str(prime)]
        require((Fraction(w['coefficient'])*snapshot_grid).denominator > 1,
                'snapshot grid cannot hold a product')
        failures.append(first_failure(net, order, w['input'], snapshot_grid))
    return {'prime_factor_product_failures': failures[:3],
            'snapshot_grid_product_failures': failures[3:],
            'snapshot_prime_factor_controls': 3, 'negative_controls': 8}


def verify():
    word, net = sources()
    order = net.schedule()
    upper = recursive_bound(net, order)
    retained = json.loads((ROOT/'predecessor/RESULT.json').read_text())['native']
    require(upper == int(retained['grid']) == 530841600, 'source sufficient grid')
    rows, data = integer_trace(net, order, upper, True)
    endpoints(word, net, rows, upper)
    require(data['products'] == retained['checked_products'] == 8533666, 'complete product coverage')
    require(data['minimum_product_grid'] == 225*2**12 and data['minimum_snapshot_grid'] == 45*2**9,
            'minimum grids')
    smaller, replay = integer_trace(net, order, data['minimum_product_grid'], False)
    require(replay['products'] == data['products'], 'minimum-grid replay coverage')
    scale = upper//data['minimum_product_grid']
    require(all(row == {i: value*scale for i, value in smaller[node].items()}
                for node, row in rows.items()), 'every row agrees under rescaling')
    endpoints(word, net, smaller, data['minimum_product_grid'])
    owners = fraction_columns(net, order, data)
    result = {'status': 'PASS_BANKED_NATIVE_MINIMUM_GRID', 'source_sufficient_grid': upper,
              **data, 'minimum_grid_exact_replay_products': replay['products'],
              'public_rows_checked': len(net.initial), 'fraction_basis_inputs': owners,
              'sharpness': sharpness(net, order, data),
              'scope': 'Normalized rational scalar DAG; physical Clifford and recursive-root precision remain separate.'}
    require(json.loads((ROOT/'RESULT.json').read_text()) == result, 'retained audit receipt')
    return result


if __name__ == '__main__':
    print(json.dumps(verify(), indent=2, sort_keys=True))
