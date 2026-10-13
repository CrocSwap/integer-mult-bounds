"""Exact paid-profile objective on the flat elementary-op state of a bitE8 word, without rebuilding
the word dictionary, plus the objective decomposition used by the pair search.

The paid profile of a word is the sum over registers of the weights of that register's frame ascents
through D, A, B, the retained-total snapshot, C (the reverse of the z-destination gates of A then B,
all at the full frame) and final.  A register's contribution therefore depends only on the operations
that touch it, so

    * the objective delta of one transported operation is the sum of the deltas of the two registers
      it touches, and
    * a k-operation improvement requires the k operations to share registers.

Minimising G(a0) = sum_r n_r r^(1-a0) for any fixed a0 > 0 maximises the certified saving c, because
the certified c is the root of Psi(a) = m^a G(a) - M = D and both m^a and G are increasing in a.
"""
from collections import Counter


class StateProf:
    """paid profile / objective of the flat op list held in a tune.Tuner"""

    def __init__(self, T, a0=0.001733):
        self.T = T
        self.V = T.V
        self.N = T.N
        self.wt = [r ** (1.0 - a0) for r in range(0, 64)]
        self.start = list(T.w['start'])
        self.final = list(T.w['final'])
        self.ret = list(T.w['ret'])
        self.dims = T.cat.dim                       # live list: Cat.closure may append frames
        self.full = next(i for i, m in enumerate(T.cat.masks) if bin(m).count('1') == T.V)
        self.rebuild_z()

    def rebuild_z(self):
        V = self.T.V
        self.z = [g for g in self.T.secs['A'] + self.T.secs['B'] if not (V <= g[1] < 2 * V)]

    def profile(self):
        T = self.T
        dim = self.dims
        cur = list(self.start)
        P = Counter()

        def climb(r, f):
            a = cur[r]
            if a == f:
                return
            d = dim[f] - dim[a]
            if d > 0:
                P[d] += 1
            cur[r] = f

        for f, t, ss in T.w['D']:
            for r in [t, *ss]:
                climb(r, f)
        for f, t, s in T.secs['A']:
            climb(t, f); climb(s, f)
        tops = [dim[cur[q]] for q in self.ret]
        for f, t, s in T.secs['B']:
            climb(t, f); climb(s, f)
        fu = self.full
        for f, t, s in reversed(self.z):
            climb(t, fu); climb(s, fu)
        for r, f in enumerate(self.final):
            climb(r, f)
        P.update(tops)
        return dict(sorted(P.items()))

    def objective(self):
        return sum(n * self.wt[r] for r, n in self.profile().items())


def apply_move(V, i, q, frame):
    """transport op i of view V to slot q at `frame`; returns a token for undo_move"""
    op = V.ops.pop(i)
    old = (i, op[0])
    op[0] = frame
    V.ops.insert(q, op)
    V.reindex()
    return old


def undo_move(V, q, old):
    i, f0 = old
    op = V.ops.pop(q)
    op[0] = f0
    V.ops.insert(i, op)
    V.reindex()
