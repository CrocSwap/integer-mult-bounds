"""Full rational operator of a gcert/1 program (A, scatter, B) on all registers, every initial value a variable;
compare two programs. usage: cxop.py CERT1 CERT2 [GXDIR]"""
import sys, gzip, json
from fractions import Fraction as Fr
def load(p):
    x = json.load(gzip.open(p)); return x['cert'] if 'cert' in x else x
def op(c):
    v, R = c['v'], c['R']; n = 2 * v + R
    reg = [{r: Fr(1)} for r in range(n)]
    def axpy(t, src, co):
        d = reg[t]
        for k, u in src.items():
            w = d.get(k, 0) + co * u
            if w: d[k] = w
            else: d.pop(k, None)
    def run(G):
        for g in G:
            if g[0] == 'neg': reg[g[2]] = {k: -u for k, u in reg[g[2]].items()}
            elif g[0] == 'out':
                src = dict(reg[g[2]])
                for t, a, b in g[3]: axpy(t, src, Fr(a, b))
            else:
                for s, a, b in g[3]: axpy(g[2], reg[s], Fr(a, b))
    run(c['A']); tot = {k: dict(reg[s]) for k, s, _ in c['ret']}
    for t in range(v):
        for k, a, b in c['scat']['table'][t]: axpy(v + t, tot[k], Fr(a, b))
    run(c['B']); return reg, tot
a, ta = op(load(sys.argv[1])); b, tb = op(load(sys.argv[2]))
assert ta == tb, 'retained totals differ'
diff = [r for r in range(len(a)) if a[r] != b[r]]
print('full rational operator on all %d registers (every initial value a variable) and the retained totals: %s' % (len(a), 'IDENTICAL' if not diff else 'DIFFER at %d registers' % len(diff)))
assert not diff
