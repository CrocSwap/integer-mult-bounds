"""Exact mirrored two-half HOST tape with four terminal fused phases."""
from collections import Counter
from fractions import Fraction as Q
import hashlib, importlib.util, json, sys
from pathlib import Path
from host34 import N, eye, z, m, tr, add, sc, msum, inv, block_lu
from cut_library import Physical, block_tuple, coupled_bound, canonical

PINS = ('3828d53e80ea97e8b866320f081af20b6b93bfebd58b95b56b85a7afe151af5e',
        '44e6a7983aac450c6f55c87da57d8c975748f32728092c4be6ed966a54854998',
        '60a743d13f668ef86db4b8215b4d5d04430a671ba6f1fe06d9c1c4c3dfe86da5')

def sparse(rows):
    return [{i: x for i, x in enumerate(row) if x} for row in rows]

def masks():
    return [{0, 1, *range(2 + 16 * side, 2 + 16 * side + 2 * min(j + 1, 8))}
            for side, order in enumerate((range(9), range(8, -1, -1))) for j in order]

def tape(signs, blocks=None, ring_audit=None):
    I = eye(2)
    J = [[Q(0), Q(-2)], [Q(1, 2), Q(0)]]
    blocks = blocks or [sc(J, sign) for sign in signs]
    W = [sc(add(I, j, -1), Q(1, 2)) for j in blocks]
    A = I
    phi = []
    for w, j in zip(W, blocks):
        phi.append(m(A, w))
        A = m(A, j)
    assert A == sc(I, -1)
    bridge = tr(eye(N)[:2])
    U = [None] * 18
    seam = add(I, sc(msum(phi[:9], 2, 2), 2), -1)
    for side, ids in enumerate((list(range(9)), list(range(17, 8, -1)))):
        bcoef = inv(add(I, seam, -1) if side == 0 else sc(add(I, seam), -1))
        offset = 2 + 16 * side
        B = [m(bcoef, sc(phi[j], 2)) for j in ids[:-1]]
        P = [sc(b, 2 if side == 0 else -2) for b in B]
        LU = block_lu([[add(b, sc(I, -2)) if i == j else b for j, b in enumerate(P)] for i in range(8)])
        for q, j in enumerate(ids[:-1]):
            U[j] = m(bridge, B[q])
            for i in range(8):
                U[j][offset + 2*i:offset + 2*i + 2] = LU[i][q]
        U[ids[-1]] = add(sc(bridge, 1 - 2 * side), msum((U[j] for j in ids[:-1]), N, 2), -1)
    basis = inv(tr([c for u in U[:-1] for c in tr(u)]))
    Y = []
    for i in range(18):
        cells = [add(sc(p, 2), sc(I, -2)) if i == j else sc(p, 2)
                 for j, p in enumerate(phi)]
        y = m([[q for b in cells[:-1] for q in b[k]] for k in (0, 1)], basis)
        assert all(m(y, u) == b for u, b in zip(U, cells))
        Y.append(y)
    S = z(N, 2)
    F = eye(N)
    domains = {}
    physical = Physical.__new__(Physical)
    physical.cuts = []
    for i, (u, y, w, J_i, mask) in enumerate(zip(U, Y, W, blocks, masks()), 1):
        x = add(u, sc(m(S, w), 2))
        local = m(y, x)
        E = [[Q(a == b and a in mask) for b in range(N)] for a in range(N)]
        assert m(F, x) == u and add(I, local) == sc(J_i, -1)
        assert m(E, x) == x and m(y, E) == y and m(F, E) == m(E, F)
        dual = m(inv(local), y)
        P = m(x, dual)
        if ring_audit is not None:
            vals = [Q(v) for a in (x,dual,F) for row in a for v in row if v]
            assert all(not (v.denominator & (v.denominator-1)) for v in vals)
            ring_audit.append({'stage':i,'max_abs':str(max(map(abs,vals))),
                               'max_denominator':max(v.denominator for v in vals)})
        Fi = inv(F)
        Pplus = add(E, P, -1)
        Pminus = add(E, m(m(F, P), Fi), -1)
        assert m(Pplus, Pplus) == Pplus and m(Pminus, Pminus) == Pminus
        domains[i] = tuple(canonical(sparse(a)) for a in (tr(Pplus), Pplus, tr(Pminus), Pminus))
        physical.cuts.append((i - 1, block_tuple(sparse(F)), block_tuple(sparse(tr(Fi)))))
        F = add(F, m(u, y))
        S = add(S, u)
    assert F == sc(eye(N), -1) and S == z(N, 2)
    physical.cuts.append((18, block_tuple(sparse(F)), block_tuple(sparse(tr(inv(F))))))
    return domains, physical

def varied_tape(mode):
    J = [[Q(0), Q(-2)], [Q(1, 2), Q(0)]]
    def changed(t):
        S = [[Q(1), Q(t)], [Q(0), Q(1)]]
        return sc(m(m(S, J), inv(S)), -1)
    def closed(ts):
        a = [changed(t) for t in ts]
        return a + [inv(v) for v in reversed(a)]
    if mode.startswith('unit-lu-'):
        ts = [4 if x == 'p' else -4 if x == 'm' else 0 for x in mode.removeprefix('unit-lu-')]
        assert len(ts) == 8
        left = [v for t in ts[:4] for v in closed([t])]
        right = [v for t in ts[4:7] for v in closed([t])]
        return left + [J, inv(J)] + right + [changed(ts[7]),changed(ts[7])]
    if mode == 'local-pairs':
        left = [v for t in (1, -2, 3, -1) for v in closed([t])]
        right = [v for t in (2, -1, 3) for v in closed([t])]
    elif mode == 'palindrome':
        left, right = closed([1, -2, 3, -1]), closed([2, -1, 3])
    else:
        left, right = closed([1, 2, 3, 4]), closed([-2, -3, -4])
    return left + [J, inv(J)] + right + [changed(1), changed(1)]

def main(caller, result, engine, price=True, mode='commuting'):
    assert tuple(hashlib.sha256(p.read_bytes()).hexdigest() for p in (caller, result, engine)) == PINS
    C = json.loads(caller.read_bytes())
    R = json.loads(result.read_bytes())
    sp = importlib.util.spec_from_file_location('gate', engine)
    g = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(g)
    claim, cap = map(Q, (R['gate']['claim'], R['gate']['BIT_pin']))
    powers = [0, 3, 0, 3, 0, 3, 0, 3, 0, 1, 0, 3, 0, 3, 0, 3, 0, 3, 2]
    signs = [1 if (b-a) % 4 == 1 else -1 for a, b in zip(powers, powers[1:])]
    audit = [] if mode.startswith('unit-lu-') else None
    D, P = tape(signs, None if mode == 'commuting' else varied_tape(mode), audit)
    stage_masks = masks()
    old = C['types']['B']['diagonal']
    expected = [sum(d[2+i] for d in old) for i in range(18)]
    assert [len(mask) + 2 * (j in (8, 9)) for j, mask in enumerate(stage_masks)] == expected
    productive = Counter(1 + 8 * sum(j in mask for mask in stage_masks) for j in range(N))
    productive[9] += 4
    assert productive == Counter(1 + 8 * sum(d[2:]) for d in old)
    out = {'status':'PASS_MIRRORED_HOST34_TERMINAL_PHASE_SUPPORT',
           'tape':mode, 'rank_9_phase_stages':[9,9,10,10],
           'old_target_cardinalities':expected, 'core_cardinalities':list(map(len, stage_masks))}
    if audit is not None:
        out['dyadic_active_HOST_frames'] = audit
    if price:
        order = tuple(range(1,10))+tuple(range(18,9,-1))
        bill, cuts = coupled_bound(order, D, P)
        assert sum(r*n for r,n in bill.items()) == 176*8
        invoice = Counter({int(r):n for r,n in R['invoice']['T'].items()})
        invoice.subtract({int(r):n for r,n in R['invoice']['P'].items()})
        delta = Counter(8*len(e[3]) for e in C['events'] if e[:2]==['B','IDLE_ONE'])
        delta[1] += 4
        delta[9] -= 4
        delta.subtract(bill)
        invoice.update({r:8*n for r,n in delta.items()})
        value = g.moment(invoice,claim)
        deriv = (0,0)
        for r,n in invoice.items():
            deriv = g.add(deriv,g.smul(g.mul(g.power(r,cap if n>=0 else claim),g.log(r)),-n))
        assert deriv[1] < 0
        out.update({'directed_complete_margin':g.value(value),
                    'directed_complete_margin_exact':[str(Q(v,g.B)) for v in value],
                    'directed_derivative_upper':str(Q(deriv[1],g.B)),
                    'optimistic_core_paid':dict(bill),'cut_price':cuts})
        if value[0]>0:
            floor = Q('0.003635202569271')
            ceil = Q('0.003635202569272')
            assert g.moment(invoice,floor)[0] > 0 and g.moment(invoice,ceil)[1] < 0
            out['formal_candidate_crossing_bracket'] = [str(floor),str(ceil)]
    print(json.dumps(out, indent=2))

if __name__ == '__main__':
    main(*(Path(x) for x in sys.argv[1:4]), price='--support-only' not in sys.argv,
         mode=next((a.removeprefix('--tape=') for a in sys.argv[4:] if a.startswith('--tape=')), 'commuting'))
