#!/usr/bin/env python3
"""Exact finite corroboration of the written two-FULL pureword obstruction.

No circuit search or native scientific replay. Apache-2.0; substantial OpenAI
Codex assistance. The all-size theorem is in PROOF.md, not these fixtures.
"""
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import argparse
import json

HERE = Path(__file__).resolve().parent
ZERO, ONE, IMAG = (F(0), F(0)), (F(1), F(0)), (F(0), F(1))


def need(ok, why):
    if not ok:
        raise ValueError(why)


def plus(a, b):
    return a[0]+b[0], a[1]+b[1]


def times(a, b):
    return a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0]


def negative(a):
    return -a[0], -a[1]


def conjugate(a):
    return a[0], -a[1]


def cmul(a, b):
    return tuple(plus(times(a[2*i], b[j]), times(a[2*i+1], b[2+j]))
                 for i in range(2) for j in range(2))


def scalar(a, z):
    return tuple(times(x, z) for x in a)


def group():
    ident = (ONE, ZERO, ZERO, ONE)
    x = (ZERO, ONE, ONE, ZERO)
    s = (ONE, ZERO, ZERO, IMAG)
    u, v = (F(1, 2), F(1, 2)), (F(1, 2), F(-1, 2))
    q = (u, v, v, u)
    rows, lookup, cursor = [ident], {ident: 0}, 0
    while cursor < len(rows):
        need(len(rows) <= 128, 'Explicit finite central group capacity')
        for gen in (q, s):
            item = cmul(rows[cursor], gen)
            if item not in lookup:
                lookup[item] = len(rows); rows.append(item)
        cursor += 1
    table = [[lookup[cmul(a, b)] for b in rows] for a in rows]
    monomial = {i for i, a in enumerate(rows) if
                all(sum(a[2*r+c] != ZERO for c in range(2)) == 1 for r in range(2))
                and all(sum(a[2*r+c] != ZERO for r in range(2)) == 1 for c in range(2))}
    need(len(rows) == 96 and len(monomial) == 32, 'Exact generated group/subgroup sizes')
    need(cmul(q, q) == x, 'Native Gaussian square is translation, not identity')
    return rows, table, monomial, lookup[q], lookup[s], lookup[x]


def algebra(table):
    def add(a, b):
        out = dict(a)
        for g, c in b.items():
            out[g] = plus(out.get(g, ZERO), c)
        return {g: c for g, c in out.items() if c != ZERO}
    def mul(a, b):
        out = {}
        for g, c in a.items():
            for h, d in b.items():
                at = table[g][h]
                out[at] = plus(out.get(at, ZERO), times(c, d))
        return {g: c for g, c in out.items() if c != ZERO}
    def mm(a, b):
        return [[add(mul(a[i][0], b[0][j]), mul(a[i][1], b[1][j]))
                 for j in range(2)] for i in range(2)]
    return add, mul, mm


def finite_projection(rows, table, subgroup, q, s, x):
    add, mul, mm = algebra(table)
    unit = [[{0: ONE}, {}], [{}, {0: ONE}]]
    def shear(i, letter, coefficient=ONE):
        out = [[dict(z) for z in row] for row in unit]
        out[i][1-i] = {letter: coefficient}
        return out
    def diagonal(a, b):
        return [[{a: ONE}, {}], [{}, {b: ONE}]]
    def project(a):
        return {g: c for g, c in a.items() if g in subgroup}
    w = mm(mm(shear(0, 0, (F(1, 2), F(0))), diagonal(s, x)),
           mm(shear(1, 0, IMAG), shear(0, 0, negative(ONE))))
    left = mm(diagonal(x, s), shear(0, 0, IMAG))
    right = mm(shear(1, 0, (F(-2), F(0))), diagonal(s, x))
    qi = next(g for g in range(len(rows)) if table[q][g] == 0)
    si = next(g for g in range(len(rows)) if table[s][g] == 0)
    qb = table[table[s][q]][si]
    letters = [q, qi, qb, next(g for g in range(len(rows)) if table[qb][g] == 0)]
    checks = 0
    for a in letters:
        for b in letters:
            for i in range(2):
                for k in range(2):
                    actual = mm(mm(mm(mm(left, shear(i, b)), w), shear(k, a)), right)
                    projected = [[project(z) for z in row] for row in actual]
                    middle = [[dict(z) for z in row] for row in w]
                    cross = project(mul(mul({b: ONE}, w[1-i][k]), {a: ONE}))
                    middle[i][1-k] = add(middle[i][1-k], cross)
                    need(projected == mm(mm(left, middle), right), 'Exact bimodule cross-term formula')
                    checks += 1
    triple = mm(mm(shear(1, qi), shear(0, q, negative(ONE))), shear(1, qi))
    swap = [[{}, {0: ONE}], [{0: negative(ONE)}, {}]]
    need(mm(swap, triple) == diagonal(qi, q), 'Three-query complete dirty two-owner positive control')
    need(q not in subgroup and qb not in subgroup, 'Both changed central functions remain outside free subgroup')
    need(all(((table[table[h][g]][k] in subgroup) == (g in subgroup))
             for h in subgroup for k in subgroup for g in range(len(rows))), 'Bimodule support law')
    return checks


def fp_ops(prime=1000003):
    need(prime % 4 == 3 and all(prime % d for d in range(2, 1001)),
         'Fixed prime and irreducible quadratic for exact modular rank')
    def add(a, b):
        return ((a[0]+b[0]) % prime, (a[1]+b[1]) % prime)
    def mul(a, b):
        return ((a[0]*b[0]-a[1]*b[1]) % prime, (a[0]*b[1]+a[1]*b[0]) % prime)
    def inv(a):
        d = pow((a[0]*a[0]+a[1]*a[1]) % prime, -1, prime)
        return (a[0]*d % prime, -a[1]*d % prime)
    def power(a, n):
        out = (1, 0)
        while n:
            if n & 1:
                out = mul(out, a)
            a = mul(a, a); n //= 2
        return out
    def reduce(a):
        return tuple(z.numerator * pow(z.denominator, -1, prime) % prime for z in a)
    return add, mul, inv, power, reduce


def tensor_rank_controls(rows, subgroup):
    phases = (ONE, IMAG, negative(ONE), negative(IMAG))
    representatives = sorted({min(scalar(a, z) for z in phases) for a in rows})
    need(len(representatives) == 24, 'Exact projective group has 24 classes')
    add, mul, inv, power, reduce = fp_ops()
    base = [[reduce(sum_gaussian(times(conjugate(x), y) for x, y in zip(a, b)))
             for b in representatives] for a in representatives]
    ranks = {}
    for width in range(23, 27):
        matrix = [[power(z, width) for z in row] for row in base]
        rank = 0
        for col in range(24):
            pivot = next((r for r in range(rank, 24) if matrix[r][col] != (0, 0)), None)
            if pivot is None:
                continue
            matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
            scale = inv(matrix[rank][col]); matrix[rank] = [mul(z, scale) for z in matrix[rank]]
            for r in range(rank+1, 24):
                factor = matrix[r][col]
                matrix[r] = [add(a, tuple(-v for v in mul(factor, b)))
                             for a, b in zip(matrix[r], matrix[rank])]
            rank += 1
        need(rank == 24, 'Projective tensor Gram full rank at a sufficient width')
        ranks[str(width)] = rank
    return ranks


def sum_gaussian(items):
    out = ZERO
    for x in items:
        out = plus(out, x)
    return out


def semantic_controls(rows, table, subgroup, q, x):
    u, v = (F(1, 2), F(1, 2)), (F(1, 2), F(-1, 2))
    reconstructed = tuple(plus(times(u, a), times(v, b)) for a, b in zip(rows[0], rows[x]))
    need(reconstructed == rows[q], 'Width-one Gaussian matrix relation exists')
    delta = plus(times(rows[q][0], rows[q][0]), negative(times(u, ONE)))
    need(delta != ZERO, 'Same scalar sum does not tensorize at width two')
    iphase = tuple(times(IMAG, z) for z in rows[0])
    need(iphase in rows, 'Absolute i word phase retained as a group element')
    need(times(IMAG, IMAG) != IMAG, 'Width-two word phase cannot become width-independent scalar i')
    need({q: ONE} != {0: u, x: v}, 'Group-algebra Gaussian is not its accidental width-one sum')
    # Existing transformed helper state or a nonmonomial free address gate is
    # outside the theorem, rather than an identity-scratch counterexample.
    need(q not in subgroup, 'Adding Q to the free subgroup invalidates the hypothesis')
    return ['width1_sum_not_tensorized', 'wordphase_not_scalar_i',
            'nonmonomial_free_gate_invalidates_model', 'three_query_positive_control']


def authenticate():
    path = HERE/'ORIGINS.json'
    manifest = json.loads(path.read_text())
    for row in manifest['files']:
        target = HERE/row['local_path']
        need(sha256(target.read_bytes()).hexdigest() == row['sha256'], 'Frozen source bytes: '+row['local_path'])
    return {row['local_path']: row['sha256'] for row in manifest['files']}


def run():
    source_hashes = authenticate()
    rows, table, subgroup, q, s, x = group()
    checks = finite_projection(rows, table, subgroup, q, s, x)
    return {'status': 'PASS_TWO_FULL_CENTRAL_OBSTRUCTION_MODEL', 'group_order': len(rows),
            'monomial_subgroup_order': len(subgroup), 'projective_group_order': 24,
            'projective_monomial_order': 8, 'projection_formula_fixtures': checks,
            'bimodule_support_checks': len(rows)*len(subgroup)**2,
            'tensor_gram_ranks_mod_1000003_i_squared_minus1': tensor_rank_controls(rows, subgroup),
            'semantic_controls': semantic_controls(rows, table, subgroup, q, x),
            'sources': source_hashes, 'no_new_kappa': True,
            'own_files': {p.relative_to(HERE).as_posix(): sha256(p.read_bytes()).hexdigest()
                          for p in sorted(HERE.rglob('*')) if p.is_file()
                          and p.name != 'RESULT.json' and '__pycache__' not in p.parts},
            'limits': 'Written theorem supplies universal quantifiers; central finite model only, no native/outer replay.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--write-receipt', type=Path)
    args = parser.parse_args(); result = run()
    encoded = json.dumps(result, sort_keys=True, indent=2)+'\n'
    if args.write_receipt:
        with args.write_receipt.open('x') as handle:
            handle.write(encoded)
    else:
        receipt = HERE/'RESULT.json'
        need(receipt.is_file(), 'Committed scientific receipt is required')
        need(json.loads(receipt.read_text()) == result, 'Source-bound scientific receipt equality')
        print(encoded, end='')
