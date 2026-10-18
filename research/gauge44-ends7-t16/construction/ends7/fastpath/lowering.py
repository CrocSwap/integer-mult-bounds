"""Retain the exact lowering checks with an explicit state evaluator.

The algebra and algorithm are from the pinned clifford_exact.py.
This module passes the evaluator as an argument. It does not change that module.
Apache-2.0. See NOTICE.md for source credit.
"""


def monomial(op, algebra, evaluate):
    n, tab = op.n, op.tab
    assert all(x == 0 and p % 2 == 0 for x, z, p in tab[n:])
    G = algebra.transpose([x for x, z, p in tab[:n]], n)
    b = algebra.mv(G, sum((p // 2) << i for i, (x, z, p) in enumerate(tab[n:])))
    gt = algebra.transpose(G, n)
    cols = [algebra.mv(gt, z) for x, z, p in tab[:n]]
    Q = algebra.transpose(cols, n)
    alpha = [(p - 2*algebra.parity(b & z)) % 4 for x, z, p in tab[:n]]
    out = algebra.diag(n, Q, alpha).then(algebra.perm(n, G)).then(algebra.xgate(n, b))
    assert out.tab == tab
    vec, den = evaluate(op)
    assert den == 0 and all(a == (0, 0) for i, a in enumerate(vec) if i != b)
    phase = [(1, 0), (0, 1), (-1, 0), (0, -1)].index(vec[b])
    out = out.then(algebra.Op(n, algebra.identity(n), [('phase', phase)]))
    assert evaluate(out) == evaluate(op)
    return out, dict(matrix_rows=G, offset=b, quadratic_rows=Q,
                     linear_Z4=alpha, phase=phase)


def lower_child(op, algebra, evaluate):
    n = op.n
    Bcols = [x for x, z, p in op.tab[n:]]
    r = algebra.rank(Bcols)
    if not r:
        mon, rec = monomial(op, algebra, evaluate)
        return dict(rank=0, left=rec, right=None), mon
    G = algebra.transpose(algebra.basis_extend(Bcols, n), n)
    A = algebra.inv(G, n)
    PA = algebra.perm(n, A)
    part = op.then(PA)
    Bcols = [x for x, z, p in part.tab[n:]]
    Dcols = [z for x, z, p in part.tab[n:]]
    picks, selected = [], []
    for j, x in enumerate(Bcols):
        if algebra.rank(selected + [x]) > len(selected):
            picks.append(j)
            selected.append(x)
    assert len(picks) == r and all(x >> r == 0 for x in Bcols)
    Br = algebra.transpose(selected, r)
    Bi = algebra.inv(Br, r)
    Dr = algebra.transpose([Dcols[j] & ((1 << r) - 1) for j in picks], r)
    Qsmall = tuple(sum(algebra.parity(row & col) << j
                       for j, col in enumerate(algebra.transpose(Bi, r))) for row in Dr)
    Q = Qsmall + (0,) * (n-r)
    DQ = algebra.diag(n, Q)
    V = part.then(DQ).then(algebra.hadamard(n, range(r)))
    assert all(x == 0 for x, z, p in V.tab[n:])
    Vmon, _ = monomial(V, algebra, evaluate)
    S = algebra.diag(n, tuple(1 << i if i < r else 0 for i in range(n)))
    left = S.adjoint().then(DQ.adjoint()).then(PA.adjoint())
    right = Vmon.then(S.adjoint()).then(algebra.xgate(n, (1 << r)-1))
    lmon, lrec = monomial(left, algebra, evaluate)
    rmon, rrec = monomial(right, algebra, evaluate)
    compiled = rmon.then(algebra.fourier(n, range(r))).then(lmon)
    assert compiled.tab == op.tab and evaluate(compiled) == evaluate(op)
    return dict(rank=r, left=lrec, right=rrec), compiled
