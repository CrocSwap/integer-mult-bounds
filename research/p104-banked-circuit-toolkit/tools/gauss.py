"""Own exact Gaussian-dyadic state simulation of chart transfers T_b T_a^-1 (canonical chart Cliffords on 9 axes).
Checks, for every column |x>, that the transfer spreads it over exactly 2^r basis states with equal modulus, r = |dim b - dim a|
(the physical rank of the job), using exact integer Gaussian numerators over a power-of-two denominator."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from phys import gf2_inv, gf2_rank, tr, extend, par, N
def mv(rows, x): return sum(par(r & x) << i for i, r in enumerate(rows))
def qval(Q, al, x):
    return (sum(al[i] for i in range(N) if x >> i & 1) + 2 * sum(par((Q[i] >> (i + 1)) & (x >> (i + 1))) for i in range(N) if x >> i & 1)) % 4
def mul_i(a, k):
    x, y = a
    return [(x, y), (-y, x), (-x, -y), (y, -x)][k % 4]
def chart_circuit(U):
    r = len(U)
    if r == 0: return []
    if r == N: return [('C', 1 << i, 1) for i in range(N)]
    G = tr(extend(U), N); gi = gf2_inv(G, N); git = tr(gi, N)
    Q = [(1 << i) ^ sum(par(git[i] & gj) << j for j, gj in enumerate(git)) for i in range(N)]
    al = [(Q[i] >> i) & 1 for i in range(N)]
    K = [('P', G), ('D', Q, al)]
    Kd = [('D', Q, [(-a) % 4 for a in al]), ('P', gi)]
    return Kd + [('C', 1 << i, 1) for i in range(r)] + K
def adjoint(circ):
    out = []
    for e in reversed(circ):
        if e[0] == 'P': out.append(('P', gf2_inv(e[1], N)))
        elif e[0] == 'D': out.append(('D', e[1], [(-a) % 4 for a in e[2]]))
        elif e[0] == 'C': out.append(('C', e[1], -e[2]))
    return out
def run(circ, x):
    M = 1 << N; v = [(0, 0)] * M; v[x] = (1, 0); den = 0
    for e in circ:
        if e[0] == 'P':
            w = [(0, 0)] * M
            for y, a in enumerate(v): w[mv(e[1], y)] = a
            v = w
        elif e[0] == 'D': v = [mul_i(a, qval(e[1], e[2], y)) for y, a in enumerate(v)]
        elif e[0] == 'C':
            q, s = e[1], e[2]; w = []
            for y, (a, b) in enumerate(v):
                c, d = v[y ^ q]; w.append((a - s * b + c + s * d, b + s * a + d - s * c))
            v = w; den += 1
        while den and all((a & 1) == 0 and (b & 1) == 0 for a, b in v): v = [(a // 2, b // 2) for a, b in v]; den -= 1
    return v, den
def column_rank(Ua, Ub, cols=range(1 << N)):
    circ = adjoint(chart_circuit(Ua)) + chart_circuit(Ub); out = set()
    for x in cols:
        v, den = run(circ, x)
        nz = [a * a + b * b for a, b in v if a or b]
        if len(set(nz)) != 1: return None
        k = len(nz).bit_length() - 1
        if len(nz) != 1 << k: return None
        out.add(k)
    return out.pop() if len(out) == 1 else None
if __name__ == '__main__':
    import json, gzip
    from bank import load
    W = load(sys.argv[1]); fr = W['frames']
    pairs = json.loads(sys.argv[2])
    for a, b in pairs:
        r = column_rank(fr[a], fr[b]); print(a, b, 'column rank', r, 'dim diff', abs(len(fr[a]) - len(fr[b])), 'OK' if r == abs(len(fr[a]) - len(fr[b])) else 'FAIL', flush=True)
