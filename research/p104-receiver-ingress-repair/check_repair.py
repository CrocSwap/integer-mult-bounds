"""Build the seventh-ingress realization and check its exact operators and grade bill."""
from fractions import Fraction as F
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from word import check_causality, read_word, require


def add(row, other, factor):
    for k, v in other.items():
        x = row.get(k, 0) + v*factor
        if x:
            row[k] = x
        else:
            row.pop(k, None)


def pullback(schedule, forms, key):
    row = {key: 1}
    for k in reversed(schedule):
        coeff = row.pop(k, 0)
        if coeff:
            add(row, forms[k], coeff)
    require(all(k < 0 for k in row), 'adjoint expands to public coordinates')
    return row


def main():
    w, old, routes, terminals = read_word()
    schedule = w['schedule']
    ing, direct, late = 95914, 88, 94217
    y1, y2 = 155442,155490
    target = {~674: 1, ~780: -1}
    require(pullback(schedule,old,y1) == target, 'original difference terminal')
    require(old[late] == {~674:1, 90590:-1, 90592:-1}, 'public edge input plus core offset')
    require(all(routes[k] == (3,11) for k in (90590,90592)) and w['initial'][780] == 3,
            'new core packet is causal at its sender')

    packet = pullback(schedule,old,late)
    add(packet, target, -1)
    require(len(packet) == 299 and all(w['initial'][~j] == 3 for j in packet),
            'core-only seventh arrival')
    require(max(q.numerator.bit_length() for q in packet.values()) == 30 and
            max(q.denominator.bit_length() for q in packet.values()) == 7,
            'literal coefficient sizes for handoff')

    new = old.copy()
    new_routes = routes | {ing:(3,278), direct:(278,127)}
    new[ing] = packet
    new[direct] = {late:1, ing:-1}
    new[y1] = {direct:1}
    new[y2] = old[y2].copy()
    add(new[y2], old[y1], -1)
    add(new[y2], new[y1], 1)
    check_causality(w,new,new_routes,terminals)
    affected = {ing,direct,y1,y2}
    for k in schedule:
        if affected.intersection(old[k]) or affected.intersection(new[k]):
            affected.add(k)
    require(affected == {ing,direct,y1,y2}, 'complete joint dependency cone')
    require(pullback(schedule,new,direct) == target and
            all(pullback(schedule,new,k) == pullback(schedule,old,k) for k in (y1,y2)),
            'two restored operators on all 1,289 independent inputs')
    broken = new | {direct: {late:1, ing:1}}
    require(pullback(schedule,broken,y1) != target, 'sign error changes a terminal')
    require(sum(pair == (3,278) for pair in new_routes.values()) == 7, 'seven core ingresses')
    require([len(w['frames'][j]) for j in (3,278,288,127)] == [0,2,4,9], 'old and new grades')
    print('PASS full causal reconstruction, all 1,289 terminal rows, seventh core packet has 299 terms.')
    check_tariff()


# Rational log and exponential tail bounds adapted from the #7808 price checker.
def price(d):
    def logarithm(x):
        z = (x-1)/(x+1)
        u, total = z, F(0)
        for j in range(45):
            total += 2*u/(2*j+1)
            u *= z*z
        return total,total + 2*u/(91*(1-z*z))

    def exponential(x):
        require(0 <= x <= F(1,50), 'alternating exponential')
        u = total = F(1)
        for j in range(1,14):
            u *= -x/j
            total += u
        return total,total-u*x/14

    k = d.bit_length()-1
    base, remainder = logarithm(F(2)),logarithm(F(d,1<<k))
    xlo, xhi = (F('0.00387981257853')*(k*base[i]+remainder[i]) for i in (0,1))
    return d*exponential(xhi)[0],d*exponential(xlo)[1]


def check_tariff():
    a,b = price(5),price(7)
    lo,hi = 48*(b[0]-a[1]),48*(b[1]-a[0])
    expected = F('94.966797106425725799489376')
    require(expected < lo <= hi < expected+F(1,10**24), '48-call directed surcharge')
    print('PASS added signed cost lies in 94.966797106425725799489376 + (0, 1e-24).')


if __name__ == '__main__':
    main()
