"""Certify the rank floor for one causal nested delivery."""
from fractions import Fraction
from math import gcd, lcm
from pathlib import Path
import importlib.util

HERE = Path(__file__).resolve().parent
BASE = HERE/'retained/research/bit-single-relation-bank-obstruction'


def module(name):
    spec = importlib.util.spec_from_file_location(name, BASE/(name+'.py'))
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def primitive(row):
    divisor = gcd(*row)
    return [x//divisor for x in row] if divisor else row


def integral(row):
    values = [Fraction(x) for x in row]
    scale = lcm(*(x.denominator for x in values))
    return primitive([int(x*scale) for x in values])


def reduce_row(row, basis):
    value = row[:]
    for pivot, donor in basis.items():
        if value[pivot]:
            a, b = donor[pivot], value[pivot]
            value = primitive([a*x-b*y for x,y in zip(value, donor)])
    return value


def geometric_basis(rows):
    basis = {}
    for row in rows:
        value = reduce_row(integral(row), basis)
        if any(value):
            basis[next(i for i,x in enumerate(value) if x)] = value
    return basis


def geometry(word):
    bases = {int(c): geometric_basis(f['B']) for c,f in word['frames'].items()}
    dimensions = {int(c): f['dim'] for c,f in word['frames'].items()}
    pairs = []
    for destination in sorted(bases):
        for donor in sorted(bases):
            small, large = (donor,destination) if dimensions[donor] <= dimensions[destination] else (destination,donor)
            if all(not any(reduce_row(row, bases[large])) for row in bases[small].values()):
                pairs.append([destination, donor, abs(dimensions[donor]-dimensions[destination])])
    return pairs


def remainder(value, basis):
    while value:
        pivot = value.bit_length()-1
        if pivot not in basis:
            return value
        value ^= basis[pivot]
    return 0


def add(value, basis):
    value = remainder(value, basis)
    if value:
        basis[value.bit_length()-1] = value


def dual(value, basis):
    residue = remainder(value, basis)
    if not residue:
        raise ValueError('cheaper source exists')
    result = 1 << (residue.bit_length()-1)
    for pivot, row in sorted(basis.items()):
        if (result & row).bit_count() % 2:
            result ^= 1 << pivot
    return result


def produce():
    engine = module('census')
    word, _ = engine.source()
    pairs = geometry(word)
    dimensions = {int(c): f['dim'] for c,f in word['frames'].items()}
    legal = {c: [(b,r) for d,b,r in pairs if d == c] for c in dimensions}
    orientations = []
    for reverse in (False, True):
        _, _, banks, moves = engine.walk(word, reverse)
        prefix = {c: {} for c in banks}
        for chart, rows in banks.items():
            for key, value in rows.items():
                if key < 0:
                    add(value, prefix[chart])
        cases = []
        for clock, (source,destination) in moves.items():
            old_rank = abs(dimensions[source]-dimensions[destination])
            value = banks[destination][clock]
            for donor, rank in legal[destination]:
                if rank < old_rank:
                    cases.append([clock, donor, rank, hex(dual(value, prefix[donor]))])
            add(value, prefix[destination])
        orientations.append(dict(direction='transpose' if reverse else 'forward', cases=cases))
    return dict(status='PASS_CAUSAL_BIT_DELIVERY_RANK_FLOOR', geometry=pairs, orientations=orientations)


if __name__ == '__main__':
    import json
    print(json.dumps(produce(), indent=2))
