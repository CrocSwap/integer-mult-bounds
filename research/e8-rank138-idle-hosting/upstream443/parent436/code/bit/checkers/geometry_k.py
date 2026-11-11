"""PR234's route and idle geometry for the bridged word B_K (DaysSky, assisted with Claude), generalizing PR #370's
geometry_g.py (five stages) to 2K + 1 stages.  Every formula is geometry_g.py's; only the number of blocks and the idle
chronology change.

    H^S with S = 2K + 1 blocks, ambient form G (+) ... (+) G; p* = q* q*^T G / <q*,q*>, k* = I - p*
    route rho(i,t)     [[g p* g^-1, g k*], [k* g^-1, p*]] on blocks (0, i), identity elsewhere; rho(0,t) = I   (i < S)
    stage projector    P (+) K (+) ... (+) K   (K = k* on blocks 1..i)
    data(i,kind)       rho(i,t) * stage_projector(i, frame(kind)) * rho(i,t),  kinds P (port line), K, H, 0
Checks for every port t: rho^2 = I; data(i-1,H) = data(i,P) and data(i-1,K) = data(i,0) for i = 1..S-1; the idle
boundary pairs of B_K (PR #363's bridged.py chronology), each commuting with a*b = a and an idempotent gap whose rank
equals bridged.check(K, h)'s idle climb:
    pair q = 2..K, X: (p, data(2q-3,H)) and (data(2q-2,P), data(2q-1,P));  Y: (0, data(2q-3,K)) and (data(2q-2,0), data(2q-1,0))
    pair 1, final:  (data(2,H), I) and (data(2,K), I - p);   pair q, final: (data(2q,H), I) and (data(2q,K), I - p)
For K = 2 this is geometry_g.py's list of eight pairs, in the same order.  Every gap of rank above floor((m - 1)/2)
gets an explicit intermediate frame Q = b - D, D a sum of mutually orthogonal E8 root projectors r r^T G/<r,r> in a
diagonal block where the gap is block-diagonal (dyadic entries only, so the prime-witness set stays {2}):
a Q = Q a = a, Q b = b Q = Q, Q^2 = Q, ranks (split, rest), so the paid children obey the half-shrink guard
2 max child < m.  Entrance census (every helper starts at frame 0): the S tau-conjugates of
(I_h - P_sigma) (+) 0 are pairwise orthogonal and sum to I - completion(sigma); a duplicated window is rejected.
With the third argument 'unsplit' no climb is split: the idle children are the whole climbs, and the least halving
degree t (m^t > 2 max child^t) is reported instead of the half-shrink guard.
usage: python3 geometry_k.py K WORD.json[.gz] [unsplit]"""
import sys, os, json, gzip, time
import sympy as sp
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'complex', 'code'))
import bridged
def eye(n): return sp.eye(n)
class Geo:
    def __init__(self, h, G, qstar, S):
        self.h = h; self.S = S; self.M = S * h; self.G = G; self.q = qstar
        nq = (qstar.T * G * qstar)[0]; assert nq != 0
        self.pstar = qstar * (qstar.T * G) / nq; self.kstar = eye(h) - self.pstar
        self.GG = sp.diag(*([G] * S))
    def frame_projector(self, B):
        if B.rows == 0: return sp.zeros(self.h)
        return B.T * (B * self.G * B.T).inv() * B * self.G
    def rho(self, stage, g, ginv):
        h, M = self.h, self.M; I = eye(M)
        if stage == 0: return I
        I[:h, :h] = g * self.pstar * ginv; I[stage*h:(stage+1)*h, stage*h:(stage+1)*h] = self.pstar
        I[:h, stage*h:(stage+1)*h] = g * self.kstar; I[stage*h:(stage+1)*h, :h] = self.kstar * ginv
        return I
    def tau(self, stage):
        I = eye(self.M)
        if stage:
            for j in range(self.h): I.row_swap(j, stage * self.h + j)
        return I
    def stage_projector(self, stage, P):
        A = sp.zeros(self.M); A[:self.h, :self.h] = P
        for j in range(1, stage + 1): A[j*self.h:(j+1)*self.h, j*self.h:(j+1)*self.h] = self.kstar
        return A
    def intermediate(self, a, b, split, lines):
        """Q = b - D with D a sum of mutually G-orthogonal root projectors r r^T G/<r,r> (dyadic) inside diagonal blocks
        on which the gap b - a is block-diagonal; rank(Q - a) = split."""
        h, M = self.h, self.M; gap = b - a; need = int(gap.trace()) - split; D = sp.zeros(M); got = 0
        proj = [r * (r.T * self.G) / (r.T * self.G * r)[0] for r in lines]
        for j in range(self.S - 1, 0, -1):
            blk = slice(j * h, (j + 1) * h)
            off = gap.copy(); off[blk, blk] = sp.zeros(h)
            if not (off[blk, :].is_zero_matrix and off[:, blk].is_zero_matrix): continue
            Gj = gap[blk, blk]; chosen = []
            for e in proj:
                if got == need: break
                if Gj * e == e and all(e * f == sp.zeros(h) for f in chosen):
                    chosen.append(e); D[blk, blk] = D[blk, blk] + e; got += 1
            if got == need: break
        assert got == need, ('no dyadic intermediate frame', need, got)
        Q = b - D
        assert D * D == D and D * a == a * D == sp.zeros(M) and b * D == D * b == D and Q * Q == Q
        assert a * Q == Q * a == a and Q * b == b * Q == Q
        assert int((Q - a).trace()) == split and int((b - Q).trace()) == need
        assert all(sp.Rational(x).q & (sp.Rational(x).q - 1) == 0 for x in Q), 'intermediate frame not dyadic'
        return Q
    def check_port(self, K, qt, g, ginv, split, lines):
        h, M, S = self.h, self.M, self.S; I = eye(M); Z = sp.zeros(M)
        assert g * ginv == eye(h) and g.T * self.G * g == self.G, 'port map is not a G-isometry'
        assert g * self.q == qt or g * self.q == -qt, 'port map does not send q* to the port line'
        routes = [self.rho(i, g, ginv) for i in range(S)]
        assert all(r * r == I for r in routes)
        P = self.frame_projector(qt.T); assert P * P == P and P.trace() == 1
        Ph = {'P': P, 'K': eye(h) - P, 'H': eye(h), '0': sp.zeros(h)}
        cache = {}
        def data(i, kind):
            if (i, kind) not in cache: cache[i, kind] = routes[i] * self.stage_projector(i, Ph[kind]) * routes[i]
            return cache[i, kind]
        for i in range(1, S):
            assert data(i-1, 'H') == data(i, 'P'); assert data(i-1, 'K') == data(i, '0')
        p = data(0, 'P'); pairs = []
        for q in range(2, K + 1):
            pairs += [(p, data(2*q-3, 'H')), (Z, data(2*q-3, 'K')), (data(2*q-2, 'P'), data(2*q-1, 'P')), (data(2*q-2, '0'), data(2*q-1, '0'))]
        pairs += [(data(2, 'H'), I), (data(2, 'K'), I - p)]
        for q in range(2, K + 1):
            pairs += [(data(2*q, 'H'), I), (data(2*q, 'K'), I - p)]
        ranks = []; children = []
        for a, b in pairs:
            assert a * b == b * a == a; gap = b - a; assert gap * gap == gap; r = int(gap.trace()); ranks.append(r)
            if r > split:
                Q = self.intermediate(a, b, split, lines); children += [split, r - split]
            else:
                children.append(r)
        assert p * (I - p) == Z and p + (I - p) == I
        return ranks, children
    def check_entrance(self, Psigma):
        h, M, S = self.h, self.M, self.S; Z = sp.zeros(M)
        completion = sp.diag(*([Psigma] * S)); residual = eye(M) - completion
        assert completion * completion == completion and completion.trace() == S * Psigma.trace()
        actual = []
        for i in range(S):
            t = self.tau(i); local = sp.zeros(M); local[:h, :h] = eye(h) - Psigma; actual.append(t * local * t)
        assert sum(actual, Z) == residual
        assert all(a * b == Z for i, a in enumerate(actual) for j, b in enumerate(actual) if i != j)
        assert sum(actual[:S-1] + [actual[S-2]], Z) != residual
        return True
def expected(K, h):
    """idle climbs of bridged.check in the order of check_port's pair list (X and Y of each climb)"""
    idle = bridged.check(K, h)['per_pair_idle']; out = []
    for q in range(2, K + 1):
        a, b, _ = idle[q]; out += [a, a, b, b]
    out += [idle[1][0]] * 2
    for q in range(2, K + 1): out += [idle[q][2]] * 2
    return out
def main(K, word, unsplit=False):
    c = json.load(gzip.open(word, 'rt') if word.endswith('.gz') else open(word))
    assert c['form'] == '<x,y>/2' and c['h'] == 8
    h = 8; S = 2 * K + 1; m = S * h; split = m if unsplit else (m - 1) // 2
    G = eye(h) / 2; L = [sp.Matrix(x) for x in c['lines']]; v = len(L)
    ip = lambda a, b: (a.T * G * b)[0]
    def refl(r): return eye(h) - r * (r.T * G) * 2 / ip(r, r)
    star = 0; geo = Geo(h, G, L[star], S)
    isom = {star: (eye(h), [])}; frontier = [star]
    while frontier:
        nxt = []
        for a in frontier:
            for r in range(v):
                if r == a: continue
                if abs(ip(L[a], L[r])) == 1:
                    d = L[a] - L[r] if ip(L[a], L[r]) == 1 else L[a] + L[r]
                    if r not in isom:
                        isom[r] = (refl(d) * isom[a][0], isom[a][1] + [d]); nxt.append(r)
        frontier = nxt
    assert len(isom) == v
    want = expected(K, h); idle = None; kids = None; t0 = time.time()
    for t in range(v):
        g, w_ = isom[t]
        ranks, children = geo.check_port(K, L[t], g, g.inv(), split, L)
        if idle is None: idle, kids = ranks, children
        assert ranks == idle == want, (ranks, want)
        assert children == kids and (unsplit or 2 * max(children) < m)
        if t % 30 == 0: print('  port %d/%d checked (%d reflections) %.0fs' % (t + 1, v, len(w_), time.time() - t0), flush=True)
    nreg = 2 * v + c['R']; starts = {c['start'][r] for r in range(2 * v, nreg)}
    assert starts == {c['start'][v]} and len(c['frames'][c['start'][v]]) == 0
    geo.check_entrance(sp.zeros(h))
    lay = bridged.check(K, h, split=None if (unsplit or K <= 2) else split)['blocks_per_role_pair']
    t = 1
    while m ** t <= 2 * max(kids) ** t: t += 1
    assert sorted(kids) == sorted(lay * 2), (kids, lay)     # X and Y of every role pair: PR #363's priced idle blocks
    print('PASS E8 geometry in B_%d (%d stages, m = %d): all %d ports (W(E8) reflection words), routes involutive, %d stage boundaries chained,'
          ' idle gap ranks %s (= bridged.py), paid idle children %s (%s); entrance census {0: %d helpers}:'
          ' %d-window completion exact, duplicate window rejected' % (K, S, m, v, S - 1, idle, kids,
          'unsplit, halving degree %d' % t if unsplit else 'explicit dyadic intermediate frames, 2 x %d < %d' % (max(kids), m), c['R'], S))
    if unsplit: print('   unsplit: largest idle child %d of m = %d, least halving degree t = %d (%d^%d > 2 * %d^%d)' % (max(kids), m, t, m, t, max(kids), t))
if __name__ == '__main__':
    main(int(sys.argv[1]), sys.argv[2], len(sys.argv) > 3 and sys.argv[3] == 'unsplit')
