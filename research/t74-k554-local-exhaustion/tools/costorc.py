import bisect
from word import span
from fc3 import Oracle
V = 112
INF = 1 << 60
def dim(Fr): return len(Fr).bit_length() - 1
class CostOracle(Oracle):
    def __init__(self, w, c):
        super().__init__(w); self.c = c
        full = frozenset(range(512)); R = w['report']['R']
        ends = [full] * V + [frozenset(x for x in range(512) if (x & p).bit_count() % 2 == 0) for p in w['ports']] + [full] * R
        for r, vecs in w['helper_final'].items(): ends[int(r)] = span(tuple(vecs))
        self.ends = ends
    def info(self, y, p):
        gl = self.g.get(y, []); ps = self.pos.get(y, [])
        k = bisect.bisect_left(ps, p)
        Fr = gl[k - 1][2] if k > 0 else self.start[y]
        N = gl[k][2] if k < len(gl) else self.ends[y]
        return Fr, N
    def zcost(self, F0, N, T):
        if T == F0: return 0
        if not (F0 <= T) or not (T <= N): return INF
        if T == N: return 0
        a = dim(T) - dim(F0); k = dim(N) - dim(F0)
        return self.c[a] + self.c[k - a] - self.c[k]
    def cost(self, x, y, p):
        Fx, Nx = self.info(x, p); Fy, Ny = self.info(y, p)
        U = span(tuple(Fx | Fy))
        best = INF
        for T in {Fx, Fy, Nx, Ny, U}:
            if not (Fx <= T and Fy <= T): continue
            cst = self.zcost(Fx, Nx, T) + self.zcost(Fy, Ny, T)
            if cst < best: best = cst
        return best
