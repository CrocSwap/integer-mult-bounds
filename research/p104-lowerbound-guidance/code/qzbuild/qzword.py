# QZBUILD: assemble a caller word (C1-json schema) from model data (v_e, w_e, a_t, b_t), generic over a field
# (floats or Fractions).  Prefix construction: P with P v_i = e_{r_i}, rows r_i = w_i, other rows = basis of ann{v_i}.
from fractions import Fraction as Fr
import json

def mat_inv(A, Z, O):
    n = len(A); M = [list(r) + [O if i == j else Z for j in range(n)] for i, r in enumerate(A)]
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(M[r][c]))
        if M[p][c] == Z: raise ZeroDivisionError('singular')
        M[c], M[p] = M[p], M[c]
        piv = M[c][c]; M[c] = [x/piv for x in M[c]]
        for r in range(n):
            if r != c and M[r][c] != Z:
                f = M[r][c]; M[r] = [x - f*y for x, y in zip(M[r], M[c])]
    return [r[n:] for r in M]
def mm(A, B, Z):
    return [[sum((A[i][l]*B[l][j] for l in range(len(B))), Z) for j in range(len(B[0]))] for i in range(len(A))]
def NZ(x): return abs(x) > 1e-10 if isinstance(x, float) else x != 0
def nullspace_rows(vs, n, Z, O):
    """basis of {p : p.v = 0 for v in vs} (row vectors)."""
    # rows of matrix = vs ; nullspace of vs (as m x n)
    M = [list(v) for v in vs]; piv = []; r = 0
    for c in range(n):
        p = None
        for i in range(r, len(M)):
            if NZ(M[i][c]) and (p is None or abs(M[i][c]) > abs(M[p][c])): p = i
        if p is None: continue
        M[r], M[p] = M[p], M[r]; pv = M[r][c]; M[r] = [x/pv for x in M[r]]
        for i in range(len(M)):
            if i != r and M[i][c] != Z:
                f = M[i][c]; M[i] = [x - f*y for x, y in zip(M[i], M[r])]
        piv.append(c); r += 1
        if r == len(M): break
    free = [c for c in range(n) if c not in piv]; out = []
    for f in free:
        x = [Z]*n; x[f] = O
        for i, c in enumerate(piv): x[c] = -M[i][f]
        out.append(x)
    return out
def prefix(pairs, n, Z, O):
    """pairs: list of (row, v, w). returns P with P v = e_row, row(P,row) = w."""
    rows = {r for r, _, _ in pairs}
    ann = nullspace_rows([v for _, v, _ in pairs], n, Z, O)
    P = [None]*n
    for r, v, w in pairs: P[r] = list(w)
    others = [i for i in range(n) if i not in rows]
    assert len(ann) == len(others)
    for i, a in zip(others, ann): P[i] = a
    return P
def elem_ops(C, Z, O):
    """ops (ADD r c val)/(SCALE r val) whose left-product (first op applied first) equals C."""
    n = len(C); M = [list(r) for r in C]; ops = []  # reduce M to I; record E's; C = E1^-1 ... Ep^-1
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(M[r][c]))
        if M[c][c] == Z or (isinstance(M[c][c], float) and abs(M[c][c]) < 0.5*abs(M[p][c])):
            ops.append(('ADD', c, p, O)); M[c] = [x + y for x, y in zip(M[c], M[p])]
        piv = M[c][c]
        if piv != O:
            ops.append(('SCALE', c, O/piv)); M[c] = [x/piv for x in M[c]]
        for r in range(n):
            if r != c and M[r][c] != Z:
                f = M[r][c]; ops.append(('ADD', r, c, -f)); M[r] = [x - f*y for x, y in zip(M[r], M[c])]
    # E_p...E_1 C = I  => C = E_1^-1 ... E_p^-1 ; left-applying C to X = apply E_p^-1 first
    inv = []
    for op in reversed(ops):
        if op[0] == 'ADD': inv.append(('ADD', op[1], op[2], -op[3]))
        else: inv.append(('SCALE', op[1], O/op[2]))
    return inv
def host_mat(n, s, t, a, b, Z, O):
    H = [[O if i == j else Z for j in range(n)] for i in range(n)]
    H[s][t] = a; H[t][s] = b; H[t][t] = O + a*b
    return H
def assemble(d, V, W, ab, Z=Fr(0), O=Fr(1), conv=str):
    """V, W: per incidence vectors; ab per host.  Returns event list in C1-json schema (stages 1-based)."""
    n = d.n; cur = [[O if i == j else Z for j in range(n)] for i in range(n)]
    out = []; inc = 0; h = 0
    def apply_C(target):
        nonlocal cur
        C = mm(target, mat_inv(cur, Z, O), Z)
        for op in elem_ops(C, Z, O):
            if op[0] == 'ADD': out.append(['ADD', op[1], op[2], conv(op[3])])
            else: out.append(['SCALE', op[1], conv(op[2])])
        cur = target
    for ev in d.events:
        if ev[0] == 'H':
            t = ev[1]; a, b = ab[h]; s_, t_ = 0, 1
            P1 = prefix([(s_, V[inc], W[inc]), (t_, V[inc+1], W[inc+1])], n, Z, O)
            H = host_mat(n, s_, t_, a, b, Z, O)
            Hi = mat_inv(H, Z, O)
            apply_C(mm(Hi, P1, Z))
            out.append(['LAMBDA', t_, -1]); out.append(['HOST', t+1, s_, t_, conv(a), conv(b)]); out.append(['LAMBDA', t_, 1])
            cur = P1; inc += 2; h += 1
        else:
            S = sorted(ev[1]); P1 = prefix([(0, V[inc], W[inc])], n, Z, O)
            apply_C(P1)
            out.append(['IDLE_ONE', 0, [x+1 for x in S]]); inc += 1
    apply_C([[O if i == j else Z for j in range(n)] for i in range(n)])
    for r in range(n): out.append(['LAMBDA', r, 1])
    diag = [[1, 0] + [1 if t in M else 0 for t in range(d.k)] for M in d.masks]
    return {'schema': 'qzbuild/1 (C1 schema: HOST [stage1, s, t, a, b], dst wrapped by LAMBDA; IDLE_ONE row stages1)',
            'roles': n, 'stages': d.k, 'events': out, 'diagonal': diag}
