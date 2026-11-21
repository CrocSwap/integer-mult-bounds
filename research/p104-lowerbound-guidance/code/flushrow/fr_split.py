"""FLUSHROW fr_split.py (own code): the SPLIT reduction  (a) => (b).
Every owned intake that comes after an output of the same lifetime is preceded by a hand-over through a fresh RESTORED helper
G (token g, born {0}, ascends to the current chart C of the register d):
    MOVE G -> C;  G += d;  INIT d'@C;  d' += G;  G -= d;  d' -= G;  CLEAR d;   (then d is renamed d')
d' = content(d) exactly, G ends = g exactly (pinned), no owned move is added or removed, so R and every original final are unchanged.
After the pass every lifetime is GTD (all intakes before all outputs).  Checked exactly with the G2C global-FA engine on
UP-generator fuzz runs, the G2C descend-then-reintake walk, and the asc56 U run."""
import sys, random, pickle
sys.path.insert(0, 'code/g2cluster')
sys.path.insert(0, 'code/uphase')
from gfa import *
from fuzz import gen

def split(prog, init):
    init = dict(init); out = []
    owned = set(); outed = set(); ch = {k: f for k, (f, c) in init.items()}
    alias = {}; ng = 0
    A = lambda r: alias.get(r, r)
    for op in prog:
        t = op[0]
        if t == 'INIT':
            r = op[1]; alias.pop(r, None); owned.add(r); ch[r] = op[2]; out.append(op)
        elif t == 'MOVE':
            r = A(op[1]); ch[r] = op[2]; out.append(('MOVE', r, op[2]))
        elif t == 'CLEAR':
            r = A(op[1]); owned.discard(r); outed.discard(r); out.append(('CLEAR', r)); alias.pop(op[1], None)
        else:
            d, lam, s = A(op[1]), op[2], A(op[3])
            if d in owned and d in outed:              # intake after output -> hand over first
                C = ch[d]; G = ('G', ng); dn = ('S', ng); ng += 1
                init[G] = (frozenset([0]), {('g', G[1]): Fr(1)})
                if C != frozenset([0]): out.append(('MOVE', G, C))
                out += [('ADD', G, Fr(1), d), ('INIT', dn, C, {}, True), ('ADD', dn, Fr(1), G), ('ADD', G, Fr(-1), d),
                        ('ADD', dn, Fr(-1), G), ('CLEAR', d)]
                owned.discard(d); outed.discard(d); owned.add(dn); ch[dn] = C
                for k, v in list(alias.items()):
                    if v == d: alias[k] = dn
                alias[op[1]] = dn; d = dn
            if s in owned: outed.add(s)
            out.append(('ADD', d, lam, s))
    return out, init

def gtd_all(res):
    for lf in res['L']:
        ev = [e[0] for e in lf['events'] if e[0] in 'IO']
        if 'O' in ev and 'I' in ev[ev.index('O'):]: return False
    return True

def finals_cold(res, P, prog, init):
    """precondition of the odd-cell identity: every non-X public final has y-part cold at its final chart
    (X finals: y-part on even cells apart from the diagonal is not required here; x-balance handles X)"""
    CH = Charts(P)
    for k, f in res['fin'].items():
        if isinstance(k, tuple) and k[0] == 'X':
            if {kk: v for kk, v in f.items() if kk[0] == 'x'} != {('x', k[1]): Fr(1)}: return False   # x-balance precondition
            continue
        if k not in res['W']: continue
        cold = CH.info(regchart(prog, init)[k])[1]
        if any(kk[0] == 'y' and kk[1] not in cold for kk in f): return False
        if any(kk[0] == 'x' for kk in f): return False                                             # x only in X finals
    return True

def regchart(prog, init):
    ch = {k: f for k, (f, c) in init.items()}
    for op in prog:
        if op[0] in ('MOVE', 'INIT'): ch[op[1]] = op[2]
    return ch

def compare(prog, init, P, label=None):
    r0 = gfa(prog, init, P)
    p2, i2 = split(prog, init)
    r1 = gfa(p2, i2, P)
    R0 = sum(lf['cost'] for lf in r0['L']); R1 = sum(lf['cost'] for lf in r1['L'])
    same = all(r1['fin'][k] == r0['fin'][k] for k in r0['fin'])
    pinned = all(r1['fin'][k] == c for k, (f, c) in i2.items() if k[0] == 'G')
    fc = finals_cold(r0, P, prog, init)
    nb0, _ = odd_check(r0, P, len(P)); nb1, _ = odd_check(r1, P, len(P))
    ng = sum(1 for k in i2 if k[0] == 'G')
    return dict(legal=not r1['bad'], R_equal=R0 == R1, finals_equal=same, helpers_restored=pinned, gtd_before=gtd_all(r0),
                gtd_after=gtd_all(r1), id_fail=r1['identity_fail'], odd_fail=int(fc and nb1 > 0), odd_ok_before=int(fc and nb0 == 0), cold_runs=int(fc), inv=r1['viol_pub'] + r1['viol_row'], handovers=ng, R=R0)

if __name__ == '__main__':
    # (1) the G2C descend-then-reintake walk  <e3> -> <e1,e2,e3> -> <e1,e2> -> <e1,e2,e4,e5>
    exec(open('code/g2cluster/epoch2.py').read().split('out = analyze')[0])
    from gfa import odd_check as _oc; globals()['odd_check'] = _oc
    print('epoch2 walk:', compare(prog, init, P))
    # (2) fuzz (UP generator, same distribution as fuzz20k)
    rng = random.Random(int(sys.argv[1]) if len(sys.argv) > 1 else 23); n = int(sys.argv[2]) if len(sys.argv) > 2 else 5000
    T = dict(runs=0, illegal=0, R_neq=0, fin_neq=0, unrestored=0, not_gtd_after=0, id_fail=0, odd_fail=0, odd_ok_before=0, cold_runs=0, inv=0, had_multi=0, handovers=0)
    for it in range(n):
        N = rng.choice([3, 4]); nports = rng.randint(2, 5 if N == 4 else 4)
        prog, init, P = gen(rng, N, nports, rng.randint(1, 3), rng.randint(40, 120))
        if gfa(prog, init, P)['bad']: continue
        c = compare(prog, init, P); T['runs'] += 1
        T['illegal'] += not c['legal']; T['R_neq'] += not c['R_equal']; T['fin_neq'] += not c['finals_equal']
        T['unrestored'] += not c['helpers_restored']; T['not_gtd_after'] += not c['gtd_after']; T['id_fail'] += c['id_fail'] > 0
        T['odd_fail'] += c['odd_fail']; T['odd_ok_before'] += c['odd_ok_before']; T['cold_runs'] += c['cold_runs']; T['inv'] += c['inv'] > 0; T['had_multi'] += not c['gtd_before']; T['handovers'] += c['handovers']
    print('FUZZ', T)
    print('  (cold_runs = runs whose public finals are y-cold (precondition of the identity); odd_ok_before/odd_fail = among those, odd-cell identity holds before / fails after the split)')
    # (3) asc56 U run (no-mix): already GTD -> expect 0 hand-overs, identical
    d = pickle.load(open('code/halvpay/f56run_nomix.pkl', 'rb'))
    print('asc56 nomix:', compare(d['prog'], d['init'], d['P']))
