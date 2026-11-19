"""Exact port responses and a modular certificate for rational transversality."""
from fractions import Fraction
from functools import cache
from math import isqrt
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from word import check_causality, read_word, require


A, B, PRIVATE = 95887, 100336, 95914
PRIME = 1_000_003


def add(row, other, factor):
    for j, value in other.items():
        total = row.get(j, 0) + factor * value
        if total:
            row[j] = total
        else:
            row.pop(j, None)


def rational_rank(rows):
    pivots = {}
    for source in rows:
        row = dict(source)
        while row:
            lead = min(row)
            if lead not in pivots:
                pivots[lead] = {j: Fraction(q) / row[lead] for j, q in row.items()}
                break
            add(row, pivots[lead], -row[lead])
    return len(pivots)


@cache
def residue(q):
    return q.numerator * pow(q.denominator, -1, PRIME) % PRIME


def add_mod(row, other, factor):
    for j, value in other.items():
        total = (row.get(j, 0) + factor * value) % PRIME
        if total:
            row[j] = total
        else:
            row.pop(j, None)


def modular_rank(rows):
    pivots = {}
    for source in rows:
        row = dict(source)
        while row:
            lead = min(row)
            if lead not in pivots:
                inverse = pow(row[lead], -1, PRIME)
                pivots[lead] = {j: q * inverse % PRIME for j, q in row.items()}
                break
            add_mod(row, pivots[lead], -row[lead])
    return len(pivots)


def main():
    w, forms, routes, ends = read_word()
    check_causality(w, forms, routes, ends)
    order = w['schedule']
    ins = {k for k, (_, v) in routes.items() if v == 278}
    outs = {k for k, (u, _) in routes.items() if u == 278}
    arrivals = {k for k, (_, v) in routes.items() if v == 127}
    interior = {k for k, v in ends.items() if v == 127}
    exterior = ends.keys() - interior
    require((len(ins), len(outs), len(interior), len(arrivals), len(exterior)) ==
            (10, 10, 902, 902, 387), 'word dimensions')
    require(278 not in w['initial'] and 127 not in w['initial'] and
            not any(u == 127 for u, _ in routes.values()), 'source and receiver stock')
    require(max(map(order.index, ins)) < min(map(order.index, outs)) and
            all(forms[k].keys() <= ins for k in outs), 'all ten ingresses available')
    require(all(forms[k].keys() <= arrivals for k in interior), 'native receiver decoder')

    # Overwrite outgoing definitions with ten independent tags. Every other
    # operation is the literal word, with public input set to zero.
    pulse = {}
    for k in order:
        row = {}
        if k in outs:
            row[k] = 1
        else:
            for j, q in forms[k].items():
                add(row, pulse.get(j, {}), q)
        pulse[k] = row
    require(rational_rank(pulse[k] for k in exterior) == 8, 'exterior pulse rank')
    shifts = {k: (row.get(A, 0) - row.get(B, 0), row.get(PRIVATE, 0))
              for k, row in pulse.items()}
    require(all(shifts[k] == (0, 0) for k in exterior), 'two exterior kernel vectors')
    require({k: shifts[k] for k in arrivals if any(shifts[k])} ==
            {103472: (1, 0), 104080: (Fraction(-1, 2), 0), 88: (0, 1)},
            'receiver image of the two exterior-invisible directions')
    half = Fraction(1, 2)
    require({k: shifts[k] for k in ends if any(shifts[k])} ==
            {155442: (half, 1), 155490: (-half, 1)}, 'terminal image of both free shifts')
    require(max(map(order.index, ins)) < min(order.index(k) for k in (155442, 155490)),
            'basis of either shift can be sent before all affected reads')

    require(all(PRIME % d for d in range(2, isqrt(PRIME) + 1)), 'prime field')
    symbolic = {~j: {j: 1} for j in range(len(w['initial']))}
    for k in order:
        row = {}
        for j, q in forms[k].items():
            add_mod(row, symbolic[j], residue(q))
        symbolic[k] = row
    # Full row ranks over this prime give full row ranks over the rationals.
    # Ten source rows and 902 demanded rows suffice because each demanded row
    # is already a linear combination of exactly 902 received rows.
    targets = sorted((symbolic[k] for k in interior), key=len)
    require(modular_rank(targets + [symbolic[k] for k in sorted(ins)]) == 912,
            'joint full row rank on 1,289 independent public inputs')
    print('PASS exterior rank 8/10, exact two-dimensional receiver response, joint rank 912/912.')


if __name__ == '__main__':
    main()
