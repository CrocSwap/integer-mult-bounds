"""UPHASE gadgets.py: exact small runs over Q at the class boundary (N=3, odd labels).
 G1 DEPOSIT HELPER (O3, asc56 shape): helper H loads y_c cold at {0}, rises hot, delivers into X_c, is cleaned by owned U
    (U loaded y_c cold at {0}, rose to the hot chart).                                       expect: class F and class P.
 G2 RENDEZVOUS (REVERSE ctl.py shape, signed): Y_r carries y_c {0}->hot <1>; O1 carries y_r cold up; O2 born at <1>
    takes Y_r - O1 = y_c, delivers into X_c, cleans Y_r.                                       expect: neither (boundary).
 G3 HELPER K-JUMP (O1 via a helper that is never read again): H loads y_c at {0}, rises hot; O2 born hot takes H; the
    token is removed by a cold-carried copy; O2 delivers into X_c and cleans H.               test F and P.
Each also gets the per-port witness for the other ports so all targets are met exactly (X_t = x_t - y_t)."""
from fattr import *
from adjoint import adjoint
N = 3; V = frozenset(range(8))
perpq = lambda q: frozenset(x for x in range(8) if not dot(x, q))
L = lambda q: span([q])

def base(Q):
    init = {}
    for t, q in enumerate(Q):
        init[('X', t)] = (L(q), {('x', t): Fr(1)}); init[('Y', t)] = (frozenset([0]), {('y', t): Fr(1)})
    return init

def witness(Q, t):
    """port t alone: Y_t -> q^perp, owned P born at q^perp loads y_t (cold), rises to V (1), X_t -= P at V."""
    q = Q[t]; o = ('W', t)
    return [('MOVE', ('Y', t), perpq(q)), ('INIT', o, perpq(q), {}, True), ('ADD', o, Fr(1), ('Y', t)), ('MOVE', o, V),
            ('MOVE', ('X', t), V), ('ADD', ('X', t), Fr(-1), o), ('CLEAR', o)]

def report(name, prog, init, Q):
    out = analyze(prog, init, {}, Q)
    fin = out['fin']
    miss = [t for t in range(len(Q)) if fin[('X', t)] != {('x', t): Fr(1), ('y', t): Fr(-1)} or fin[('Y', t)] != {('y', t): Fr(1)}]
    hmiss = [k for k in fin if k[0] == 'H' and fin[k] != init[k][1]]
    R = sum(lf['cost'] for lf in out['L'])
    print('==', name, '| legality', out['bad'][:2], '| target misses', miss, hmiss, '| R =', R, '| identity fails', out['identity_fail'],
          '| inv', out['viol_W'], out['viol_alpha'], '| W_X', out['W_X_nonzero'], 'Yodd', out['Yfinal_odd_terms'])
    rows = decoder_rows(out, Q)
    nb, nc = odd_check(out, rows, Q, range(len(Q)))
    for k, lf in enumerate(out['L']):
        w, v = rows[k]
        print('   F life', lf['reg'], 'cost', lf['cost'], 'GTD', lf['gtd'], 'cold', lf['cold'], 'nox', lf['nox'],
              '| row w', {a: str(b) for a, b in w.items()}, 'v', {a: str(b) for a, b in v.items()}, 'price', price(set(w), set(v), Q) if w and v else 0)
    print('   F decoder identity on odd cells: fails', nb, 'of', nc, ' sum price', sum(price(set(w), set(v), Q) for w, v in rows if w and v))
    ap, ai = adjoint(prog, init, N)
    o2 = analyze(ap, ai, {}, Q)
    for k, lf in enumerate(o2['L']):
        print('   P(adj) life', lf['reg'], 'cost', lf['cost'], 'GTD', lf['gtd'], 'cold', lf['cold'], 'nox', lf['nox'])
    inF = all(lf['gtd'] and lf['cold'] and lf['nox'] for lf in out['L'])
    inP = all(lf['gtd'] and lf['cold'] and lf['nox'] for lf in o2['L'])
    print('   class F:', inF, ' class P:', inP)

# ---- G1
Q = [1, 2, 4]; c = 0; init = base(Q); init[('H', 0)] = (frozenset([0]), {('h', 0): Fr(1)})
g = [('ADD', ('H', 0), Fr(1, 2), ('Y', c)),                          # halving load at {0}
     ('INIT', ('U', 0), frozenset([0]), {}, True), ('ADD', ('U', 0), Fr(1, 2), ('Y', c)),
     ('MOVE', ('H', 0), L(1)), ('ADD', ('X', c), Fr(-2), ('H', 0)),  # hot public delivery into X_c (O3)
     ('MOVE', ('U', 0), L(1)), ('ADD', ('H', 0), Fr(-1), ('U', 0)), ('CLEAR', ('U', 0)),   # cleaning by owned
     ('MOVE', ('H', 0), V), ('MOVE', ('Y', c), perpq(1)), ('MOVE', ('X', c), V), ('ADD', ('X', c), Fr(2), ('H', 0))]
for t in (1, 2): g += witness(Q, t)
report('G1 deposit helper', g, init, Q)

# ---- G2
Q = [1, 2, 4]; c, r = 0, 1; init = base(Q); H1 = L(1)
g = [('INIT', ('O', 1), frozenset([0]), {}, True), ('ADD', ('O', 1), Fr(1), ('Y', r)), ('ADD', ('Y', r), Fr(1), ('Y', c)),
     ('MOVE', ('Y', r), H1), ('MOVE', ('O', 1), H1),
     ('INIT', ('O', 2), H1, {}, True), ('ADD', ('O', 2), Fr(1), ('Y', r)), ('ADD', ('O', 2), Fr(-1), ('O', 1)),
     ('ADD', ('Y', r), Fr(-1), ('O', 2)), ('ADD', ('X', c), Fr(-1), ('O', 2)), ('CLEAR', ('O', 1)), ('CLEAR', ('O', 2)),
     ('MOVE', ('Y', r), perpq(2)), ('MOVE', ('X', c), V), ('MOVE', ('Y', c), perpq(1))]
g += witness(Q, 2)
g = [op if not (op[0] == 'MOVE' and op[1] == ('Y', 2) and False) else op for op in g]
# port r witness without moving Y_r again (it is already at q_r^perp)
q = Q[r]; o = ('W', r)
g += [('INIT', o, perpq(q), {}, True), ('ADD', o, Fr(1), ('Y', r)), ('MOVE', o, V), ('MOVE', ('X', r), V), ('ADD', ('X', r), Fr(-1), o), ('CLEAR', o)]
report('G2 rendezvous', g, init, Q)

# ---- G3
Q = [1, 2, 4]; c = 0; init = base(Q); init[('H', 0)] = (frozenset([0]), {('h', 0): Fr(1)}); H1 = L(1)
g = [('INIT', ('O', 1), frozenset([0]), {}, True), ('ADD', ('O', 1), Fr(1), ('H', 0)),     # O1 = h (token copy, cold)
     ('ADD', ('H', 0), Fr(1), ('Y', c)), ('MOVE', ('H', 0), H1), ('MOVE', ('O', 1), H1),     # H = h + y_c, hot at <1>
     ('INIT', ('O', 2), H1, {}, True), ('ADD', ('O', 2), Fr(1), ('H', 0)), ('ADD', ('O', 2), Fr(-1), ('O', 1)),   # O2 = y_c (hot intake)
     ('ADD', ('H', 0), Fr(-1), ('O', 2)), ('ADD', ('X', c), Fr(-1), ('O', 2)), ('CLEAR', ('O', 1)), ('CLEAR', ('O', 2)),
     ('MOVE', ('H', 0), V), ('MOVE', ('X', c), V), ('MOVE', ('Y', c), perpq(1))]
for t in (1, 2): g += witness(Q, t)
report('G3 helper K-jump', g, init, Q)
