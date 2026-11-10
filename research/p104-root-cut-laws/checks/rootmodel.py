"""The word model of THEOREM.md section 1, in exact rational arithmetic.

A root is: n coordinates; N units u = 0..N-1 in word order, each with vectors x_u, y_u in Q^n; a list of labels k = 0..L-1, each with a set
of LOCAL units and a mask M_k (a set of coordinates); the event sequence (units, and one scalar Delta_k after the last unit of label k).
Units that belong to no label are thin. M(D) is the product, applied in sequence, of the maps  v -> v - 2 x_u (y_u . v)  for a unit and
'multiply the coordinates of M_k by D_k' for a label. Z(D) is the N x N matrix of section 1: Z_uu = 2, and for u != v
Z_uv = 2 sgn(u - v) * sum_c y_u[c] x_v[c] Lam_u[c] / Lam_v[c], where Lam_u[c] is the product of D_k over the labels k with c in M_k whose
Delta comes before unit u in the word."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import random
from fractions import Fraction as Fr
from common import load, fr_matrix, rank_q


class Root:
    def __init__(self, n, N, X, Y, labels, seq, local):
        self.n, self.N, self.X, self.Y = n, N, X, Y
        self.labels = labels            # list of dicts: units (LOCAL, in order), mask (set)
        self.seq = seq                  # ('u', unit) or ('d', label)
        self.local = set(local)
        self.L = len(labels)

    @property
    def rho(self):
        return self.N - self.n

    def before(self):
        """before[u] = labels whose Delta comes before unit u."""
        out, seen = {}, []
        for ev in self.seq:
            if ev[0] == 'd':
                seen.append(ev[1])
            else:
                out[ev[1]] = list(seen)
        return out

    def M(self, D):
        n = self.n
        M = [[Fr(int(i == j)) for j in range(n)] for i in range(n)]
        for ev in self.seq:
            if ev[0] == 'u':
                x, y = self.X[ev[1]], self.Y[ev[1]]
                yM = [sum(y[i] * M[i][j] for i in range(n) if y[i] != 0) for j in range(n)]
                for i in range(n):
                    if x[i] != 0:
                        M[i] = [M[i][j] - 2 * x[i] * yM[j] for j in range(n)]
            else:
                for c in self.labels[ev[1]]['mask']:
                    M[c] = [v * D[ev[1]] for v in M[c]]
        return M

    def contract(self, D):
        """M(D) = -diag(prod D_k^[c in M_k]) exactly."""
        M = self.M(D)
        n = self.n
        for i in range(n):
            e = Fr(1)
            for k, lab in enumerate(self.labels):
                if i in lab['mask']:
                    e *= D[k]
            for j in range(n):
                if M[i][j] != (-e if i == j else 0):
                    return False
        return True

    def hr(self):
        """H-R: x_u, y_u of every LOCAL unit are supported inside its label's mask."""
        for k, lab in enumerate(self.labels):
            for u in lab['units']:
                for c in range(self.n):
                    if (self.X[u][c] != 0 or self.Y[u][c] != 0) and c not in lab['mask']:
                        return False
        return True

    def primed(self, D):
        before = self.before()
        xs, ys = {}, {}
        for u in range(self.N):
            lam = []
            for c in range(self.n):
                v = Fr(1)
                for k in before[u]:
                    if c in self.labels[k]['mask']:
                        v *= D[k]
                lam.append(v)
            ys[u] = [self.Y[u][c] * lam[c] for c in range(self.n)]
            xs[u] = [self.X[u][c] / lam[c] for c in range(self.n)]
        return xs, ys

    def Z(self, D, units=None):
        xs, ys = self.primed(D)
        us = list(range(self.N)) if units is None else units
        Z = []
        for u in us:
            row = []
            for v in us:
                if u == v:
                    row.append(Fr(2))
                else:
                    g = sum(a * b for a, b in zip(ys[u], xs[v]))
                    row.append(2 * (1 if u > v else -1) * g)
            Z.append(row)
        return Z

    def Zpoly_at(self, E, rows, cols):
        """Z restricted to units rows x cols evaluated at E_k = 1 / D_k, with E_k allowed to be 0 (rows before cols in the word only):
        entry = 2 sgn * sum_c y_u[c] x_v[c] prod_{k in [label(u), label(v)), c in M_k} E_k, for label(u) < label(v)."""
        lab_of = {u: k for k, lab in enumerate(self.labels) for u in lab['units']}
        Z = []
        for u in rows:
            row = []
            for v in cols:
                a, b = lab_of[u], lab_of[v]
                assert a < b
                g = Fr(0)
                for c in range(self.n):
                    t = self.Y[u][c] * self.X[v][c]
                    if t == 0:
                        continue
                    for k in range(a, b):
                        if c in self.labels[k]['mask']:
                            t *= E[k]
                    g += t
                row.append(-2 * g)
            Z.append(row)
        return Z


def load_root(name):
    R = load(name)
    n, N = R['n'], R['N']
    X, Y = fr_matrix(R['X']), fr_matrix(R['Y'])
    if len(X) == n and len(X[0]) == N:
        X = [list(c) for c in zip(*X)]
        Y = [list(c) for c in zip(*Y)]
    labels, seq, local = [], [], []
    last = {max(s['units']): k for k, s in enumerate(R['stages'])}
    for s in R['stages']:
        labels.append({'units': list(s['units']), 'mask': set(s['mask'])})
        local += s['units']
    for u in range(N):
        seq.append(('u', u))
        if u in last:
            seq.append(('d', last[u]))
    return Root(n, N, X, Y, labels, seq, local)


def merged_word(base, J):
    """Two-chain root base (a direct sum of two chain roots, coordinates 0..19 and 20..39) with an interior Whitehead stage:
    on chain A the LOCAL units of stages J and J+1 are put at one label (specialise D_J = 1), and chain B does the same at its last two
    stages. Labels of chain B skip the label J. Units outside the original stages stay thin."""
    n, N = base.n, base.N
    chainA = [u for u in range(N) if all(base.X[u][c] == 0 and base.Y[u][c] == 0 for c in range(20, 40))]
    A = set(chainA)
    st = base.labels
    stage_of = {u: k for k, lab in enumerate(st) for u in lab['units']}
    # per chain: list of (units before and including the stage's LOCAL unit, restricted mask); thin units ride with the next stage
    def chain_word(chain):
        out, cur = [], []
        for u in chain:
            cur.append(u)
            if u in stage_of:
                k = stage_of[u]
                out.append((cur, [c for c in st[k]['mask'] if (c < 20) == (chain is chainA_list)], [u]))
                cur = []
        return out, cur
    chainA_list = chainA
    chainB_list = [u for u in range(N) if u not in A]
    wa, ta = chain_word(chainA_list)
    wb, tb = chain_word(chainB_list)
    assert not ta and not tb and len(wa) == 18 and len(wb) == 18
    assert len(wa[J][0]) == 1 and len(wa[J + 1][0]) == 1
    la = []
    for k, (us, m, loc) in enumerate(wa):
        if k == J:
            continue
        la.append(((wa[J][0] + us) if k == J + 1 else us, m, (wa[J][2] + loc) if k == J + 1 else loc))
    lb = wb[:J] + [None] + wb[J:-2] + [(wb[-2][0] + wb[-1][0], wb[-2][1], wb[-2][2] + wb[-1][2])]
    assert len(la) == 17 and len(lb) == 18
    seq, labels, local = [], [], []
    for k in range(18):
        units, mask, loc = [], [], []
        if k < len(la):
            units += la[k][0]; mask += la[k][1]; loc += la[k][2]
        if lb[k] is not None:
            units += lb[k][0]; mask += lb[k][1]; loc += lb[k][2]
        seq += [('u', u) for u in units]
        seq.append(('d', k))
        labels.append({'units': loc, 'mask': set(mask)})
        local += loc
    # the word order of units is the merged order; renumber so that unit index = position
    order = [ev[1] for ev in seq if ev[0] == 'u']
    ren = {u: i for i, u in enumerate(order)}
    X = [base.X[u] for u in order]
    Y = [base.Y[u] for u in order]
    seq2 = [('u', ren[ev[1]]) if ev[0] == 'u' else ev for ev in seq]
    labels2 = [{'units': [ren[u] for u in lab['units']], 'mask': lab['mask']} for lab in labels]
    return Root(n, N, X, Y, labels2, seq2, [ren[u] for u in local])


def rand_D(L, seed):
    rnd = random.Random(seed)
    return [Fr(rnd.randint(2, 9), rnd.randint(1, 5)) * rnd.choice((1, -1)) for _ in range(L)]
