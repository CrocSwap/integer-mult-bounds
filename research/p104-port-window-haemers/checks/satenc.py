"""CNF encoding of: 'there are F_2 labels W_t, U_t (2 x R each) with B_ST = W_S U_T^T, B_TT = I_2, B_ST = 0 on every orthogonal pair of distinct
ports, for the ports of a given set'. Rank B <= R then holds because B = W U^T has inner dimension R.

Gauge (valid by the argument of THEOREM.md, Section 3, step 0): the orthogonal 8-set K = ports 62, 63, 69, 74, 81, 86, 91, 99 occupies the
coordinates 2i, 2i+1 (i-th element of K) with W = U = unit vectors, so a port t outside K has labels supported on the coordinate pairs of its odd
K-neighbours and on the extra coordinates 16 .. R-1 (forced zeros against K), and B_TT = I_2 for t outside K (row normalisation).

Usage (writes DIMACS):  python3.12 -I -B satenc.py OUT.cnf R full|sub14
 full   = all 104 ports.   sub14 = K and the six ports 57, 67, 68, 95, 100, 101.
Standard library only. Variable and clause order are fixed, so the file is reproducible byte for byte."""
import sys, os, json, itertools, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import PORTS, dot as _dot

KALL = [62, 63, 69, 74, 81, 86, 91, 99]
OALL = [57, 67, 68, 95, 100, 101]
dt = lambda a, b: _dot(PORTS[a], PORTS[b])

class Enc:
    def __init__(self, R, sub):
        self.R, self.sub = R, sub
        use = list(range(len(PORTS))) if sub == 'full' else KALL + OALL
        K = KALL
        oth = [t for t in use if t not in K]
        self.oth, self.nv, self.cl, self.gates = oth, 0, [], []
        TRUE = self.nvar(); self.TRUE = TRUE; self.cl.append([TRUE])
        extra = list(range(16, R))
        Kidx = {c: i for i, c in enumerate(K)}
        self.supp = {t: [2 * Kidx[c] + d for c in K if dt(t, c) for d in (0, 1)] + extra for t in oth}
        self.U, self.W = {}, {}
        for t in oth:
            for D in (self.U, self.W):
                D[t] = [{c: self.nvar() for c in self.supp[t]} for _ in range(2)]
        for t in oth:
            for i in range(2):
                for j in range(2):
                    self.eq(self.ent(t, t, i, j), 1 if i == j else 0)
        self.npairs = 0
        for t, s in itertools.combinations(oth, 2):
            if dt(t, s) == 0:
                self.npairs += 1
                for i in range(2):
                    for j in range(2):
                        self.eq(self.ent(t, s, i, j), 0)
                        self.eq(self.ent(s, t, i, j), 0)
    def nvar(self):
        self.nv += 1
        return self.nv
    def AND(self, a, b):
        v = self.nvar(); self.gates.append((v, 0, a, b))
        self.cl.extend([[-v, a], [-v, b], [v, -a, -b]]); return v
    def xor2(self, a, b):
        v = self.nvar(); self.gates.append((v, 1, a, b))
        self.cl.extend([[-v, a, b], [-v, -a, -b], [v, -a, b], [v, a, -b]]); return v
    def xorlist(self, ls):
        if not ls: return -self.TRUE
        acc = ls[0]
        for l in ls[1:]: acc = self.xor2(acc, l)
        return acc
    def eq(self, ls, val):
        x = self.xorlist(ls); self.cl.append([x] if val else [-x])
    def ent(self, t, s, i, j):   # entry (i, j) of the block W_t U_s^T, as a list of AND gates to be xor-ed
        return [self.AND(self.W[t][i][c], self.U[s][j][c]) for c in self.supp[t] if c in self.U[s][j]]
    def dimacs_chunks(self):
        yield 'p cnf %d %d\n' % (self.nv, len(self.cl))
        buf = []
        for c in self.cl:
            buf.append(' '.join(map(str, c)) + ' 0\n')
            if len(buf) >= 50000:
                yield ''.join(buf); buf = []
        yield ''.join(buf)
    def sha256(self):
        h = hashlib.sha256()
        for ch in self.dimacs_chunks(): h.update(ch.encode())
        return h.hexdigest()
    def evaluate(self, label_values):
        """label_values: {variable: bool} for the W and U variables. Fills in the gate variables and returns the list of falsified clauses
        (empty iff the labelling satisfies the formula)."""
        val = [False] * (self.nv + 1)
        val[self.TRUE] = True
        for v, b in label_values.items(): val[v] = bool(b)
        for v, kind, a, b in self.gates:
            x, y = val[abs(a)] == (a > 0), val[abs(b)] == (b > 0)
            val[v] = (x and y) if kind == 0 else (x != y)
        return [c for c in self.cl if not any(val[abs(l)] == (l > 0) for l in c)]

def main():
    out, R, sub = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    e = Enc(R, sub)
    with open(out, 'w') as f:
        for ch in e.dimacs_chunks(): f.write(ch)
    print(sub, 'R', R, 'free ports', len(e.oth), 'orthogonal pairs', e.npairs, 'vars', e.nv, 'clauses', len(e.cl))
if __name__ == '__main__':
    main()
