#!/usr/bin/env python3
"""Derive the ordinary BIT admission constants and the controller rank-surplus
identity used by research/query-thinned-controllers and inherited by #4470.

1. atom/ordinary/admitted: the literals are bound from source; the admissible
   atom set is an exact open interval, 0.004 lies in it, 0.003 does not, and the
   supremum of the ordinary saving is its left endpoint.
2. controller.py's check surplus == 48*|thick| - 112 (complex) / - 111 (BIT)
   is the case s_loc = 48 of surplus = (p+2)*(H - C + sum_ports(2 b + 1)) - P,
   for every p and prefix length a, and for per-port block widths.

Exact rationals only; runs in a few seconds. No new kappa.
Mark (Matarener), with substantial Claude Code assistance. Apache-2.0.
"""
import ast
import json
import random
import re
import sys
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
QTC = ROOT/'research/query-thinned-controllers'
JHL = ROOT/'research/joint-helper-lattice/verify.py'
THREE = ROOT/'research/kappa-rebuild/complex/full-identity-certificates/RESULT.json'


def need(ok, label):
    if not ok:
        raise SystemExit('FAIL: '+label)
    print('PASS', label)


# ------------------------------------------------------------ source binding
def bind_sources():
    text = (QTC/'verify.py').read_text(encoding='utf-8')
    m = re.search(r"before, after, atom, old = Q\('([.\d]+)'\), Q\('([.\d]+)'\), Q\('([.\d]+)'\), Q\('([.\d]+)'\)", text)
    need(m is not None, 'Bind before/after/atom/old literals in query-thinned verify.py')
    C0, C1, atom, old = (Q(x) for x in m.groups())
    m = re.search(r"ordinary, admitted = \(1-atom\)\*after\+atom\*old, Q\('([.\d]+)'\)", text)
    need(m is not None, 'Bind ordinary formula and admitted literal')
    admitted = Q(m.group(1))
    need('atom > ordinary > admitted and atom < 1-ordinary' in text and "2**26 > 256/(before-after)" in text,
         'Bind admission predicates and prime allowance')
    jhl = JHL.read_text(encoding='utf-8')
    m = re.search(r"KAPPA, TESTED = Q\('([.\d]+)'\), Q\('([.\d]+)'\)", jhl)
    need(m is not None and "atom==Q('.004')" in jhl and "atom>ordinary>admitted>TESTED" in jhl,
         'Bind #4470 reuse: atom 0.004 and admitted > TESTED')
    kappa, tested = (Q(x) for x in m.groups())
    ctrl = (QTC/'controller.py').read_text(encoding='utf-8')
    tree = ast.parse(ctrl)
    bit = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name) \
                and node.targets[0].id in ('helpers', 'children') and isinstance(node.value, ast.Dict):
            bit[node.targets[0].id] = ast.literal_eval(node.value)
    need(set(bit) == {'helpers', 'children'}, 'Bind BIT helper/child literals in controller.py')
    need("48*len(thick)-112 if kind == 'complex' else 48*len(thick)-111" in ctrl, 'Bind the hard-coded surplus check')
    three = json.loads(THREE.read_text(encoding='utf-8'))['providers']['THREE-base']
    cx = ({int(k): v for k, v in three['helper_boundary']['widths'].items()},
          {int(k): v for k, v in three['unsplit_replays']['forward']['paid_profile'].items()})
    return dict(C0=C0, C1=C1, atom=atom, old=old, admitted=admitted, kappa=kappa, tested=tested,
                sides={'complex': (cx[0], cx[1], 112, 8), 'bit': (bit['helpers'], bit['children'], 111, 7)})


# ------------------------------------------------------------ part 1: atom
def ordinary(C1, old, d):
    return (1-d)*C1+d*old


def admissible(C1, old, d):
    o = ordinary(C1, old, d)
    return o < d < 1-o


def atom_interval(C1, old):
    """ordinary decreases in d, so o(d) < d iff d > lo and d < 1-o(d) iff d < hi."""
    return C1/(1+C1-old), (1-C1)/(1-C1+old)


def part_atom(s):
    C0, C1, old, atom, admitted = s['C0'], s['C1'], s['old'], s['atom'], s['admitted']
    lo, hi = atom_interval(C1, old)
    need(ordinary(C1, old, lo) == lo and 1-ordinary(C1, old, hi) == hi, 'Interval endpoints are the two fixed points')
    eps = Q(1, 10**12)
    need(all(admissible(C1, old, d) for d in (lo+eps, (lo+hi)/2, hi-eps)) and
         not any(admissible(C1, old, d) for d in (lo, hi, lo-eps, hi+eps)), 'Admissible atoms = open interval (lo, hi)')
    need(lo < atom < hi and ordinary(C1, old, atom) == Q('0.0034363538396'), 'Atom 0.004 admissible; ordinary 0.0034363538396')
    need(not admissible(C1, old, Q('.003')), 'Old atom 0.003 rejected')
    need(admitted < ordinary(C1, old, atom) and admitted > s['tested'], 'admitted 0.0034 < ordinary and > #4470 tested 0.003020155')
    need(C0-C1 > Q(256, 2**26), 'Delayed-cover gap exceeds 256/2^26')
    c1max = C0-Q(256, 2**26)
    return {'atom_interval_open': [str(lo), str(hi)], 'atom_interval_float': [float(lo), float(hi)],
            'ordinary_at_atom': str(ordinary(C1, old, atom)), 'sup_ordinary': str(lo), 'sup_ordinary_float': float(lo),
            'admitted': str(admitted), 'admitted_relative_loss': float(1-admitted/lo),
            'sup_ordinary_at_C1_limit_float': float(c1max/(1+c1max-old)),
            'binding_side_margin': str(admitted-s['tested'])}


# ------------------------------------------------------------ part 2: surplus
def literal_surplus(helpers, children, widths, p, a):
    """Same counting as controller.inventories, with one block width per port."""
    thick = {0, 2*p, *range(1, 2*p, 2)}
    targets = Counter({r: len(thick)*n for r, n in helpers.items()})
    paid = Counter({r: len(thick)*n for r, n in children.items()})
    paid[1] += len(widths)*(2*p+1-len(thick))
    for b in widths:
        targets[1+b*(p+2)] += 2
        for length in (a, p-1-a):
            for j in range(1, length+1):
                targets[1+b*(j+1)] += 2
                paid[b*(j+1)] += 2
    return sum(r*n for r, n in targets.items())-sum(r*n for r, n in paid.items()), targets, paid


def closed_surplus(helpers, children, widths, p):
    H = sum(r*n for r, n in helpers.items()); C = sum(r*n for r, n in children.items())
    return (p+2)*(H-C+sum(2*b+1 for b in widths))-len(widths)


def part_surplus(s):
    out = {}
    for kind, (helpers, children, ports, block) in s['sides'].items():
        H = sum(r*n for r, n in helpers.items()); C = sum(r*n for r, n in children.items())
        s_loc = H-C+(2*block+1)*ports
        need(s_loc == 48, '%s: s_loc = H - C + (2b+1)P = %d - %d + %d = 48' % (kind, H, C, (2*block+1)*ports))
        widths = [block]*ports
        for p in range(2, 41):
            for a in range(p):
                lit = literal_surplus(helpers, children, widths, p, a)[0]
                if lit != closed_surplus(helpers, children, widths, p) or lit != 48*(p+2)-ports:
                    need(False, '%s literal count p=%d a=%d' % (kind, p, a))
        need(True, '%s: literal counting = closed form = 48(p+2) - %d for p = 2..40, every a' % (kind, ports))
        ctrl = json.loads((QTC/('%s-CONTROLLER.json' % kind.upper())).read_text(encoding='utf-8'))['invoice']
        T = ctrl['thick_calls']; p = T-2
        mass = lambda d: sum(int(r)*n for r, n in d.items())
        need(mass(ctrl['targets'])-mass(ctrl['paid']) == ctrl['rank_surplus'] == closed_surplus(helpers, children, widths, p),
             '%s: committed p=%d invoice surplus %d matches the closed form' % (kind, p, ctrl['rank_surplus']))
        out[kind] = {'H': H, 'C': C, 'ports': ports, 'block': block, 's_loc': s_loc, 'committed_p': p,
                     'committed_surplus': ctrl['rank_surplus']}
    rng = random.Random(4470)
    helpers, children = s['sides']['complex'][:2]
    for _ in range(200):
        widths = [rng.randint(1, 12) for _ in range(rng.randint(1, 20))]
        p = rng.randint(2, 30); a = rng.randrange(p)
        if literal_surplus(helpers, children, widths, p, a)[0] != closed_surplus(helpers, children, widths, p):
            need(False, 'mixed widths %s p=%d a=%d' % (widths, p, a))
    need(True, 'Mixed per-port widths: 200 random instances match (p+2)(H - C + sum(2b+1)) - P')
    out['formula'] = 'surplus = (p+2)*(H - C + sum_ports(2*b_port + 1)) - P'
    return out


def run():
    s = bind_sources()
    return {'schema': 'admission-constant-derivation/1', 'status': 'PASS_DERIVED_NO_NEW_KAPPA',
            'atom': part_atom(s), 'surplus': part_surplus(s),
            'kappa_effect': 'none: complex tested %s binds; BIT admitted only needs to exceed it' % s['tested']}


if __name__ == '__main__':
    result = run()
    out = HERE/'RESULT.json'
    if '--write' in sys.argv:
        out.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n', encoding='utf-8', newline='\n')
    else:
        need(result == json.loads(out.read_text(encoding='utf-8')), 'Receipt matches exact replay')
    print(json.dumps({k: result[k] for k in ('status', 'kappa_effect')}))
