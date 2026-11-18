"""Own physical checks for a banked circuit (no upstream code):
 (a) symplectic rank of every transfer T_b T_a^-1 (canonical chart Cliffords, GF(2) tableau) equals |dim b - dim a| > 0;
 (b) bank-cost stock: local terms, homes, reset/transfer service bounds (#7682 formulas), coefficient bits, row-denominator lcm."""
import sys, os, gzip, json
from math import lcm
from fractions import Fraction as Q
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bank import load, Net, schedule
N = 9
def par(x): return bin(x).count('1') & 1
def gf2_rank(rows):
    piv = {}
    for x in rows:
        while x:
            b = x.bit_length() - 1
            if b not in piv: piv[b] = x; break
            x ^= piv[b]
    return len(piv)
def gf2_inv(rows, n):
    a = [r | (1 << (n + i)) for i, r in enumerate(rows)]
    for j in range(n):
        k = next(i for i in range(j, n) if a[i] >> j & 1); a[j], a[k] = a[k], a[j]
        for i in range(n):
            if i != j and a[i] >> j & 1: a[i] ^= a[j]
    return [r >> n for r in a]
def tr(rows, n): return [sum(((rows[j] >> i) & 1) << j for j in range(n)) for i in range(n)]
# Clifford as tableau: images of X_0..X_{n-1}, Z_0..Z_{n-1} as (x, z) bitmasks (phases dropped: rank is phase-free)
def img(T, x, z):
    u = v = 0
    for i in range(N):
        if x >> i & 1: u ^= T[i][0]; v ^= T[i][1]
        if z >> i & 1: u ^= T[N + i][0]; v ^= T[N + i][1]
    return (u, v)
def then(A, B): return [img(B, *p) for p in A]            # first A, then B
def ident(): return [(1 << i, 0) for i in range(N)] + [(0, 1 << i) for i in range(N)]
def inverse(T):
    cols = [x | (z << N) for x, z in T]; M = tr(cols, 2 * N); Mi = gf2_inv(M, 2 * N); ci = tr(Mi, 2 * N)
    return [(w & ((1 << N) - 1), w >> N) for w in ci]
def perm(G):
    cols = tr(G, N); gi = gf2_inv(G, N)
    return [(c, 0) for c in cols] + [(0, g) for g in gi]
def diag(Qr): return [(1 << i, Qr[i]) for i in range(N)] + [(0, 1 << i) for i in range(N)]
def fourier(axes):
    T = ident()
    for i in axes: T[N + i] = (1 << i, 1 << i)
    return T
def extend(U):
    out = []
    for x in list(U) + [1 << i for i in range(N)]:
        if gf2_rank(out + [x]) > len(out): out.append(x)
    return out
def chart(U):
    r = len(U)
    if r == 0: return ident()
    if r == N: return fourier(range(N))
    G = tr(extend(U), N); gi = gf2_inv(G, N); git = tr(gi, N)
    Qr = [(1 << i) ^ sum(par(git[i] & gj) << j for j, gj in enumerate(git)) for i in range(N)]
    K = then(perm(G), diag(Qr))
    return then(then(inverse(K), fourier(range(r))), K)
def trank(U, V):
    op = then(inverse(chart(U)), chart(V))
    return gf2_rank([x for x, z in op[N:]])
if __name__ == '__main__':
    W = load(sys.argv[1]); fr = W['frames']; dim = [len(f) for f in fr]
    C = json.load(gzip.open(sys.argv[2], 'rt'))
    moves = {int(k): tuple(v) for k, v in C['moves'].items()}
    forms = {int(k): {int(t): Q(c) for t, c in row.items()} for k, row in C['forms'].items()}
    pairs = sorted(set(moves.values()))
    bad = [(a, b) for a, b in pairs if trank(fr[a], fr[b]) != abs(dim[a] - dim[b]) or a == b]
    # control: a deliberately non-nested pair must not pass
    print('distinct transfer pairs', len(pairs), 'symplectic rank == |dim diff| > 0 failures:', len(bad), bad[:5])
    print('control 912->913 (non-nested): rank', trank(fr[912], fr[913]), 'dim diff', abs(dim[912] - dim[913]))
    if len(sys.argv) > 3:
        old = {tuple(v) for v in json.load(gzip.open(sys.argv[3], 'rt'))['moves'].values()}
        print('new pairs vs reference circuit:', sorted(set(pairs) - old))
    n = len(C.get('initial', W['initial'])); k = len(moves); t = sum(len(r) for r in forms.values())
    bits = max(max(abs(c.numerator).bit_length(), c.denominator.bit_length()) for r in forms.values() for c in r.values())
    net = Net(C['first'], C.get('initial', W['initial']), C.get('final', W['final']), moves, forms); order = schedule(net); den = {}
    for x in order:
        d = 1
        for y, c in forms[x].items():
            d = lcm(d, c.denominator * (den[y] if y >= 0 else 1))
        den[x] = d
    L = 1
    for d in den.values(): L = lcm(L, d)
    odd = L
    while odd % 2 == 0: odd //= 2
    b = 2 * n + 2 * k + 4
    print('terms', t, 'paid rows', k, 'homes/native', b, 'reset R', 2 * b + 8 * (t + k + n) + 4 * n,
          'transfer legs X', 2 * t + 2 * (k + n) + 6 * k + 4 * n, 'coef bits', bits,
          'row-denominator lcm', L, '= odd', odd, 'x 2^%d' % (L // odd).bit_length() if L != odd else '')
    mass = {}
    for x in order:
        mass[x] = sum(abs(c) * (mass[y] if y >= 0 else 1) for y, c in forms[x].items())
    print('max row absolute mass', max(mass.values()), '; x grid 2025', max(mass.values()) * 2025)
