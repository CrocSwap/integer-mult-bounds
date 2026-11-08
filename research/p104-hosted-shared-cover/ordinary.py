#!/usr/bin/env python3
"""Ordinary (non-recursive) raw bound, own recount. python3 -I -B ordinary.py WORD.json.gz CALLER.json
Definitions read from the predecessor review (ordinary()), its adapter inventory and pricing.py:93,102-113."""
import gzip, json, sys
from fractions import Fraction as Q
from collections import Counter
W = json.load(gzip.open(sys.argv[1], 'rt')); C = json.load(open(sys.argv[2]))
def swaps(sel, dim):
    wanted = set(range(len(sel)))
    return len(list(zip(sorted(set(sel) - wanted), sorted(wanted - set(sel)))))
n = len(W['initial']); live = set(W['live']); main = live | {r + 112 for r in live}
fr = W['frames']; dim = [len(b) for b in fr]
paid = Counter(abs(dim[e[3]] - dim[e[2]]) for e in W['program'] if e[0] == 'MOVE')
hel = Counter(dim[W['final'][r]] - dim[W['initial'][r]] for r in range(n) if r not in main)
life = sum(e[0] == 'INIT' for e in W['program'])
allow = upper = 0
for e in W['program']:
    if e[0] in ('INIT', 'CLEAR'): allow += 2
    elif e[0] == 'SCALE':
        q = Q(e[2]); a, d = abs(q.numerator), q.denominator
        allow += 2 * (abs(a.bit_length() - d.bit_length()) + int(q < 0)); upper += 4 * (a.bit_length() + d.bit_length() + 1)
    elif e[0] in ('ADD', 'COPY'):
        q = Q(e[3]); a, d = abs(q.numerator), q.denominator
        allow += 2 * (3 + a.bit_length() - 1 + a.bit_count() + d.bit_length() - 1); upper += 4 * (a.bit_length() + a.bit_count() + d.bit_length() + 1)
norm = 2 * sum(hel.values())
routes = (sum(paid.values()) + norm + 208 + 4 * 104 + 4 * life) * 1000
print('native: allowance %d, reviewed scalar upper %d, routes %d' % (allow, upper, routes))
print('per call, funded display (pricing.py:93): allowance+routes = %d ; reviewed upper+routes = %d ; bound 10^7' % (allow + routes, upper + routes))
roles = C['roles']; ev = C['events']; amb = C['ambient_rank']
main_ex = main_nine = main_ph = 0
for role, (qp, zero, *sel) in enumerate(C['diagonal']):
    axes = ([0] if qp else []) + [a for st, y in enumerate(sel, 1) if y for a in range(9 + 8 * (st - 1), 9 + 8 * st)]
    k = swaps(axes, amb); main_ex += 2 * k * 104; main_nine += 2 * bool(qp) * 104; main_ph += int(qp == -1) * 104
idle_ex = 0; qn = qph = 0
for e in ev:
    if e[0] == 'IDLE_ONE':
        axes = [a for st in e[2] for a in range(9 + 8 * (st - 1), 9 + 8 * st)]
        idle_ex += 2 * swaps(axes, amb) * 104
    elif e[0] == 'QUERY':
        qn += 2 * 104; qph += int(e[3] == -1) * 104
main_maps = main_ex + main_nine + main_ph
caller = 32 * roles * 104 * len(ev); thin = sum(e[0] == 'QUERY' for e in ev) * 16 * 104
out = roles * 104 * 26 + main_maps * 1000
rest = caller + thin + out + idle_ex * 1000 + (qn + qph) * 1000
print('caller envelope %d, thin %d, outputs %d (main maps %d), idle adapters %d, query adapters %d' % (caller, thin, out, main_maps, idle_ex * 1000, (qn + qph) * 1000))
print('RAW literal definition (18 calls x 10^7): %d  < 10^9: %s' % (18 * 10 ** 7 + rest, 18 * 10 ** 7 + rest < 10 ** 9))
for name, per in (('actual allowance+routes', allow + routes), ('reviewed upper+routes', upper + routes)):
    print('RAW with %s per call (18 x %d): %d  < 10^9: %s' % (name, per, 18 * per + rest, 18 * per + rest < 10 ** 9))
