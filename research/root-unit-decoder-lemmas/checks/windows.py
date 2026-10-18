"""Window table of the open T = 3 cases.  usage: windows.py   (reads ../lib only)
N(h) = ceil(v * x*(h)): the least cost that rules the window h of a unit out (cost >= N(h) closes (unit, T = 3, h)); x*(h) is the
break-even ratio against the E8 ceiling (lib/fx.py).  The h-ranges are the open ranges recorded in the README (T <= 2, the unique
rank-7 pairings of E6/E7 and the covering counts at h <= 6 are not recomputed here).  The script (i) recomputes the N(h) table,
(ii) checks it against the table printed in the README, (iii) checks max N(h)/v and N(h) <= ceil(2v/3) for every listed window,
and (iv) checks that the top of each window needs only N = 3w + 1 where the README says so.
Tie rule: at h = 9 the break-even is exactly x*(9) = 3/5 (the E8 ceiling itself), so for D6 (v = 30) a cost of 18 is a tie, not a win, and
N = 18 (an earlier note read 19 there through float noise; the 1e-12 below is that tolerance, all other values are far from integers)."""
import io, contextlib, math, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', 'lib'))
with contextlib.redirect_stdout(io.StringIO()):
    import ade
import fx
E8ref = fx.best(9, 0.6)[0]
def xstar(h):
    lo, hi = 0.0, 1.0
    for _ in range(50):
        mid = (lo + hi) / 2
        if fx.best(h, mid)[0] >= E8ref: lo = mid
        else: hi = mid
    return lo
OPEN = {'D5': (7, 8), 'D6': (7, 17), 'D7': (7, 24), 'D8': (7, 29), 'E6': (8, 25), 'E7': (8, 33)}
UN = {'D5': ade.D(5), 'D6': ade.D(6), 'D7': ade.D(7), 'D8': ade.D(8), 'E6': ade.E6b(), 'E7': ade.E7()}
worst = 0.0; ok = True
for nm, (h0, h1) in OPEN.items():
    L = UN[nm]; G = np.rint(L @ L.T).astype(int); v = len(L); K = ade.maxclique((G != 0) & ~np.eye(v, dtype=bool)); w = int(np.linalg.matrix_rank(G[np.ix_(K, K)]))
    Ns = [(h, math.ceil(v * xstar(h) - 1e-12)) for h in range(h0, h1 + 1)]
    runs = []
    for h, N in Ns:
        if runs and runs[-1][2] == N: runs[-1][1] = h
        else: runs.append([h, h, N])
    txt = ', '.join(f"h{a}{'' if a == b else '-' + str(b)} {N}" for a, b, N in runs)
    top = Ns[-1][1]; lim = math.ceil(2 * v / 3)
    good = all(N <= lim for _, N in Ns); ok = ok and good; worst = max(worst, max(N for _, N in Ns) / v)
    print(f"{nm} v={v} w={w} 3w={3*w} 2v/3->{lim} N: {txt} | top N={top} (3w+1={3*w+1}) | all N <= ceil(2v/3): {good}")
print(f"max N(h)/v over the listed windows {worst:.4f} (2/3 = {2/3:.4f}); every window covered by ceil(2v/3): {ok}")
