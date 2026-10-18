"""Group G2: the Levi graph of the Fano plane realised over Q, and its EXACT minimum F2 cost at T = 4 and T = 5 (exhaustive over all admissible B, C program kgap ex)."""
import sys, os, json, subprocess, itertools
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
from units import rank
H = os.path.dirname(os.path.abspath(__file__)); DATA = os.path.join(H, '..', 'data'); BIN = os.environ['C2T_BIN']
fl = [set((i, (i + 1) % 7, (i + 3) % 7)) for i in range(7)]
for T in (4, 5):
    d = json.load(open(os.path.join(DATA, 'fano_T%d.json' % T))); P, Q = d['P'], d['Q']
    dg = all(sum(a * b for a, b in zip(P[t], Q[t])) != 0 for t in range(7))
    inc = {(t, s) for t in range(7) for s in range(7) if t != s and sum(a * b for a, b in zip(P[t], Q[s])) == 0}
    inp = "%d 7\n" % T + "\n".join(" ".join(map(str, P[t] + Q[t])) for t in range(7)) + "\n"
    out = subprocess.run([os.path.join(BIN, 'kgap'), 'ex'], input=inp, capture_output=True, text=True).stdout.split('\n')
    b = [l for l in out if l.startswith('best')][0].split()
    # the zero pattern of P_i . Q_s contains a Fano plane: one triple of points per line Q_s, any two triples meeting in exactly one point
    tri = [[set(c) for c in itertools.combinations([i for i in range(7) if sum(a * b for a, b in zip(P[i], Q[s])) == 0], 3)] for s in range(7)]
    def fano(k, chosen):
        if k == 7: return True
        return any(all(len(c & d) == 1 for d in chosen) and fano(k + 1, chosen + [c]) for c in tri[k])
    contains = fano(0, [])
    M = [[sum(a * b for a, b in zip(P[t], Q[s])) for s in range(7)] for t in range(7)]
    rk = rank(M); blocks = all(any(P[t][j] for t in range(7)) and any(Q[t][j] for t in range(7)) for j in range(T))
    pts_ok = len({tuple(p) for p in P}) == 7
    print("FL T=%d: rank(P Q^T) = %d with all %d blocks nonempty: %s; zero pattern contains a Fano plane (7 point-triples, one per line, pairwise meeting in one point) %s; 7 distinct points %s, diagonals nonzero %s, %d orthogonal pairs (p_t.q_s = 0, t != s; the Fano ones plus accidental ones), free entries f = %s; exact minimum F2 cost over all 2^f admissible B = %s, v = 7, cost - v = %d" % (
        T, rk, T, blocks, contains, pts_ok, dg, len(inc), b[3], b[1], int(b[1]) - 7))
