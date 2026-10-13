"""Three-stage scalar simulation of the complex exchange with auxiliary source frames (PR #7 network).

Network: side.Side(h) with roles.compile_roles, plus h+1 centre wires, under the PR #7 schedule
(fullbatch_hist.invocation): forward L,-J,L^-1,-R,V,G,R,L,J,L^-1,G^-1,V^-1 gives y <- y+x, the inverse
V,G,L,-J,L^-1,-R,G^-1,V^-1,R,L,J,L^-1 gives x <- x-y; stages forward/inverse/forward give the exchange.

All phase frames D_phi = H^(x)m diag(i^phi) H^(x)m are diagonal in the Hadamard basis and every gate is a
scalar combination of wires, so the network is checked pointwise at a random y in F_2^m (m = h^3), exactly
mod p = 2^64-59 with i = sqrt(-1). Each gate gets an independent random common phase, data endpoints get
random phases and scratch is arbitrary. Scratch endpoints:
  stage-1/3 banks (shared between the stages), centre wires, input-pivot and retained slots: source 0, sink wt
  other stage-two side roles: source q_D0, sink wt + q_D0, with D0 = t_A^perp (x) F (x) <t_B>
Pass: every scratch wire leaves as i^wt times its physical input, X -> -Y and Y -> X with the endpoint phases.
Usage: python3 sourceframe_sim.py h [seeds] (run beside side.py and roles.py)."""
import os, sys, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from side import Side
from roles import compile_roles

p = (1 << 64) - 59
g = next(a for a in range(2, 100) if pow(a, (p - 1) // 2, p) == p - 1)
IU = pow(g, (p - 1) // 4, p); assert IU * IU % p == p - 1
IP = [pow(IU, k, p) for k in range(4)]
HALF = pow(2, p - 2, p)


def par(x): return bin(x).count('1') & 1


def qD0(h, y, tA, tB):
    """wt(P_D0 y) mod 4 for D0 = t_A^perp (x) F (x) <t_B>; y[i][j] is an h-bit int over the third index."""
    tot = 0
    for j in range(h):
        z = sum(par(y[i][j] & tB) << i for i in range(h))
        if par(z & tA): z ^= tA                      # project along the first index onto t_A^perp
        tot += 3 * bin(z).count('1')                 # each surviving (i,j) carries t_B, of weight 3
    return tot % 4


class Invocation:
    """Framed scalar operations on one bank: side slots 0..R-1, centre wires R..R+h (index R+h is '*')."""

    def __init__(s, c, k, rnd):
        s.c, s.k, s.rnd, s.h, s.R = c, k, rnd, c.h, k['size']
        s.pieces = {t: [] for t in c.triples}
        for i, sl in k['pout'].items():
            S, _, cf = c.pieces[i]; s.pieces[S].append((sl, cf * HALF % p))   # side map weights are +-1/2
        s.cent = {i: [t for t in c.triples if i in t] for i in range(s.h)}

    def gate(s, cells):
        """Bring every (values, key, frames) cell to one fresh random common phase."""
        ph = s.rnd.randrange(4)
        for val, key, fr in cells:
            d = (ph - fr[key]) % 4
            if d: val[key] = val[key] * IP[d] % p
            fr[key] = ph

    def L(s, b, sign):
        r, rf = b
        for n, ins, outs in (s.k['gates'] if sign > 0 else reversed(s.k['gates'])):
            s.gate([(r, q, rf) for q in set(ins + outs)])
            if sign > 0:
                if len(ins) == 2: r[ins[0]] = (r[ins[0]] + r[ins[1]]) % p
                for o in outs[1:]: r[o] = (r[o] + r[outs[0]]) % p
            else:
                for o in outs[1:]: r[o] = (r[o] - r[outs[0]]) % p
                if len(ins) == 2: r[ins[0]] = (r[ins[0]] - r[ins[1]]) % p

    def J(s, b, tgt, sg):                            # one injection gate per target
        r, rf = b; tv, tf = tgt
        for S, terms in s.pieces.items():
            if not terms: continue
            s.gate([(r, sl, rf) for sl, _ in terms] + [(tv, S, tf)])
            tv[S] = (tv[S] + sg * sum(cf * r[sl] for sl, cf in terms)) % p

    def V(s, b, src, sg):                            # copy gates
        r, rf = b; xv, xf = src
        for t, sl in s.k['src'].items():
            s.gate([(r, sl, rf), (xv, t, xf)]); r[sl] = (r[sl] + sg * xv[t]) % p

    def central(s, b, d):                            # one central gate: all of one data bank and every centre wire
        r, rf = b; dv, df = d
        s.gate([(dv, t, df) for t in s.c.triples] + [(r, s.R + i, rf) for i in range(s.h + 1)])

    def G(s, b, src, sg):
        r = b[0]; xv = src[0]; s.central(b, src)
        for i in range(s.h): r[s.R + i] = (r[s.R + i] + sg * sum(xv[t] for t in s.cent[i])) % p
        r[s.R + s.h] = (r[s.R + s.h] + sg * sum(xv.values())) % p

    def Rc(s, b, tgt, sg):
        r = b[0]; tv = tgt[0]; s.central(b, tgt)
        for t in s.c.triples:
            tv[t] = (tv[t] + sg * (sum(r[s.R + i] for i in t) - r[s.R + s.h]) * HALF) % p

    def forward(s, b, x, y):
        s.L(b, 1); s.J(b, y, -1); s.L(b, -1); s.Rc(b, y, -1); s.V(b, x, 1); s.G(b, x, 1)
        s.Rc(b, y, 1); s.L(b, 1); s.J(b, y, 1); s.L(b, -1); s.G(b, x, -1); s.V(b, x, -1)

    def inverse(s, b, y, x):
        s.V(b, y, 1); s.G(b, y, 1); s.L(b, 1); s.J(b, x, -1); s.L(b, -1); s.Rc(b, x, -1)
        s.G(b, y, -1); s.V(b, y, -1); s.Rc(b, x, 1); s.L(b, 1); s.J(b, x, 1); s.L(b, -1)


def run(c, k, seed, src_frame=True, sink_ok=True):
    """Returns (data ok, scratch ok, invocations with nonzero q_D0, stage-two invocations)."""
    rnd = random.Random(seed); h = c.h; T = c.triples; tm = {t: sum(1 << q for q in t) for t in T}
    y = [[rnd.getrandbits(h) for _ in range(h)] for _ in range(h)]
    wt = sum(bin(y[i][j]).count('1') for i in range(h) for j in range(h)) % 4
    I = Invocation(c, k, rnd); W = k['size'] + h + 1
    keep = set(k['src'].values()) | set(k['rout'].values()) | set(range(k['size'], W))
    keys = [(a, b, d) for a in T for b in T for d in T]
    X = {a: rnd.randrange(p) for a in keys}; Y = {a: rnd.randrange(p) for a in keys}
    Xf = {a: rnd.randrange(4) for a in keys}; Yf = {a: rnd.randrange(4) for a in keys}
    X0, Y0, Xf0, Yf0 = dict(X), dict(Y), dict(Xf), dict(Yf)
    psiX = {a: rnd.randrange(4) for a in keys}; psiY = {a: rnd.randrange(4) for a in keys}

    def bank(ph):
        v = [rnd.randrange(p) for _ in range(W)]; return [v, list(ph), list(v)]
    b1 = {(A, B): bank([0] * W) for A in T for B in T}
    q0 = {(A, B): qD0(h, y, tm[A], tm[B]) for A in T for B in T}
    b2 = {AB: bank([0 if (sl in keep or not src_frame) else q for sl in range(W)]) for AB, q in q0.items()}

    def stage(st, fixed, bk, inv):
        key = [lambda t: (t,) + fixed, lambda t: (fixed[0], t, fixed[1]), lambda t: fixed + (t,)][st]
        xv = {t: X[key(t)] for t in T}; xf = {t: Xf[key(t)] for t in T}
        yv = {t: Y[key(t)] for t in T}; yf = {t: Yf[key(t)] for t in T}
        if inv: I.inverse(bk[:2], (yv, yf), (xv, xf))
        else: I.forward(bk[:2], (xv, xf), (yv, yf))
        for t in T: X[key(t)], Xf[key(t)], Y[key(t)], Yf[key(t)] = xv[t], xf[t], yv[t], yf[t]

    partner = lambda t: tuple(sorted((q + 1) % h for q in t))   # stage-three reuse of the stage-one banks
    for A in T:
        for B in T: stage(0, (A, B), b1[A, B], False)
    for A in T:
        for B in T: stage(1, (A, B), b2[A, B], True)
    for A in T:
        for B in T: stage(2, (B, partner(A)), b1[A, B], False)

    def sink(val, fr, i, target): return val[i] * IP[(target - fr[i]) % 4] % p
    ok_s = all(sink(v, f, i, wt) == v0[i] * IP[wt] % p for v, f, v0 in b1.values() for i in range(W))
    for AB, (v, f, v0) in b2.items():
        framed = lambda i: src_frame and sink_ok and i not in keep
        ok_s &= all(sink(v, f, i, (wt + q0[AB]) % 4 if framed(i) else wt) == v0[i] * IP[wt] % p for i in range(W))
    ok_d = all(sink(X, Xf, a, psiX[a]) == (-Y0[a] * IP[(psiX[a] - Yf0[a]) % 4]) % p and
               sink(Y, Yf, a, psiY[a]) == X0[a] * IP[(psiY[a] - Xf0[a]) % 4] % p for a in keys)
    return ok_d, ok_s, sum(1 for q in q0.values() if q), len(q0)


if __name__ == '__main__':
    h = int(sys.argv[1]); seeds = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    c = Side(h); k = compile_roles(c)
    print('h', h, 'side roles', k['size'], 'centre wires', h + 1, 'source-framed per invocation',
          k['size'] - len(set(k['src'].values()) | set(k['rout'].values())), flush=True)
    for seed in range(seeds):
        print('seed', seed, 'source frames: (data ok, scratch ok, nonzero q_D0, invocations)', run(c, k, seed), flush=True)
    print('negative control, sink wt only (scratch must fail):', run(c, k, 100, sink_ok=False), flush=True)
    print('baseline, no source frames (must pass):', run(c, k, 101, src_frame=False), flush=True)
