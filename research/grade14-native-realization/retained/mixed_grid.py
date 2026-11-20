"""Check signed Laurent rows and bound physical products on each caller template. Apache-2.0."""
from collections import Counter
from fractions import Fraction
from functools import cache
from math import gcd, lcm

from mixed_caller import need


@cache
def gaussian(real, imag):
    a, b = Fraction(real), Fraction(imag)
    d = lcm(a.denominator, b.denominator)
    return int(a*d), int(b*d), d


def exact(events, targets, grid):
    rows = [{(i, 0, 0): (grid, 0)} for i in range(len(targets))]
    stages = [0]*16
    for op, *args in events:
        if op.startswith('HOST_'):
            stages[args[0]] += 1
        elif op.startswith('IDLE_'):
            for j in args[1]:
                stages[j] += 1
    # A formal path traverses an event at most once. Each D exponent fits in its own digit.
    bits = max(stages).bit_length()
    unit = [1 << (bits*j) for j in range(16)]
    divisions = components = 0
    common = grid
    peak = entrance = grid

    def observe(row):
        nonlocal common, peak
        mass = 0
        for x, y in row.values():
            common = gcd(common, gcd(x, y))
            mass += abs(x) + abs(y)
        peak = max(peak, mass)
        return row

    def term(row, a=1, b=0, d=1, phase=0, body=0, real_parts=False):
        nonlocal common, divisions, components
        out = {}
        for (r, q, degree), (x, y) in row.items():
            if real_parts and b and d > 1:
                for product, coefficient in ((a*x, a), (b*y, b), (a*y, a), (b*x, b)):
                    if coefficient:
                        value, rem = divmod(product, d)
                        need(rem == 0, 'inexact separate Gaussian component')
                        common = gcd(common, value)
                        components += 1
            xx, yy = a*x-b*y, b*x+a*y
            if d != 1:
                xx, rx = divmod(xx, d)
                yy, ry = divmod(yy, d)
                need(rx == ry == 0, 'inexact caller pre-product')
                divisions += 1
            if xx or yy:
                out[r, (q+phase) % 4, degree+body] = (xx, yy)
        return observe(out)

    def add(left, right):
        out = left.copy()
        for key, (x, y) in right.items():
            a, b = out.get(key, (0, 0))
            if a+x or b+y:
                out[key] = a+x, b+y
            else:
                out.pop(key, None)
        return observe(out)

    for op, *args in events:
        if op.startswith('HOST_'):
            stage, *regs = args
            entrance = max(entrance, *(sum(abs(x)+abs(y) for x, y in rows[r].values()) for r in regs))
            if op == 'HOST_A':
                x, y, u, v = regs
                rows[y] = add(rows[y], term(rows[x], phase=-1))
                rows[u] = add(rows[u], term(rows[v], a=-1, phase=1))
            else:
                x, y = regs
                a, b = rows[x], rows[y]
                rows[x] = add(a, term(b, a=-1, phase=1))
                rows[y] = add(term(b, d=2), term(a, d=2, phase=-1))
            for i in regs:
                rows[i] = term(rows[i], body=unit[stage])
            continue
        target, *v = args
        if op == 'SWAP':
            donor, = v
            rows[target], rows[donor] = rows[donor], rows[target]
        elif op in ('ADD', 'SCALE'):
            donor = v[0] if op == 'ADD' else target
            part = term(rows[donor], *gaussian(*v[-1]), real_parts=True)
            rows[target] = add(rows[target], part) if op == 'ADD' else part
        elif op == 'QUERY':
            donor, sign = v
            rows[target] = add(rows[target], term(rows[donor], phase=sign))
        elif op == 'LAMBDA':
            sign, = v
            old = rows[target]
            rows[target] = add(term(old, 1, sign, 2, real_parts=True),
                               term(old, 1, -sign, 2, phase=2, real_parts=True))
        else:
            need(op in ('IDLE_ONE', 'IDLE_ODD') and len(v[0]) == len(set(v[0])), 'whole idle')
            rows[target] = term(rows[target], phase=v[1] if op == 'IDLE_ODD' else 0,
                                body=sum(unit[j] for j in v[0]))
    for i, (q, mask) in enumerate(targets):
        need(rows[i] == {(i, q % 4, sum(unit[j] for j in mask)): (grid, 0)}, 'signed diagonal endpoint')
    return dict(minimum_grid=grid//common, preproduct_divisions=divisions,
                separate_component_divisions=components, exponent_bits=bits,
                maximum_stage_occurrences=max(stages), peak_mass=str(Fraction(peak, grid)),
                peak_native_entrance_mass=str(Fraction(entrance, grid)))


def envelope(events, count):
    """Bound every component before summing. Do not use signed cancellation."""
    rows = [(0, Fraction(1))]*count
    max_height = pre_height = 0
    max_mass = pre_mass = Fraction(1)

    def observe(height, mass):
        nonlocal max_height, max_mass
        max_height = max(max_height, height)
        max_mass = max(max_mass, mass)
        return height, mass

    def scale(row, a, b, d):
        return observe(row[0] + (d & -d).bit_length()-1, row[1]*Fraction(abs(a)+abs(b), d))

    def add(u, v):
        return observe(max(u[0], v[0]), u[1]+v[1])

    for op, *args in events:
        if op.startswith('HOST_'):
            _, *indices = args
            pre_height = max(pre_height, *(rows[j][0] for j in indices))
            pre_mass = max(pre_mass, *(rows[j][1] for j in indices))
            if op == 'HOST_A':
                x, y, u, v = indices
                rows[y], rows[u] = add(rows[y], rows[x]), add(rows[u], rows[v])
            else:
                x, y = indices
                a, b = rows[x], rows[y]
                rows[x] = add(a, b)
                rows[y] = add(scale(a, 1, 0, 2), scale(b, 1, 0, 2))
            continue
        target, *v = args
        if op == 'SWAP':
            donor, = v
            rows[target], rows[donor] = rows[donor], rows[target]
        elif op in ('ADD', 'SCALE'):
            donor = v[0] if op == 'ADD' else target
            part = scale(rows[donor], *gaussian(*v[-1]))
            rows[target] = add(rows[target], part) if op == 'ADD' else part
        elif op == 'QUERY':
            rows[target] = add(rows[target], rows[v[0]])
        elif op == 'LAMBDA':
            part = scale(rows[target], 1, 1, 2)
            rows[target] = add(part, part)
        else:
            need(op in ('IDLE_ONE', 'IDLE_ODD'), 'known envelope event')
    return dict(height=max_height, entrance_height=pre_height,
                mass=str(max_mass), entrance_mass=str(pre_mass))


def census(events, targets):
    paid, uses = Counter(), Counter()
    productive = Counter(q % 2 + 8*len(m) for q, m in targets)
    rotations = 0
    for op, *args in events:
        if op.startswith('HOST_'):
            continue
        uses[op] += 1
        if op in ('ADD', 'SCALE'):
            rotations += int(bool(Fraction(args[-1][1])))
        elif op == 'QUERY':
            paid[1] += 1
        elif op in ('IDLE_ONE', 'IDLE_ODD'):
            paid[8*len(args[1]) + int(op == 'IDLE_ODD')] += 1
    return productive, paid, uses, rotations
