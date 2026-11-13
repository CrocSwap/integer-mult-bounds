"""Helper-layer lower bounds on the #7334 word.  Standard library only.

Fixed registers: the mains (live X/Y, hosted X2/Y2) and the owned registers, with their whole
schedule.  Helpers: every other public register.  Contents are compared after projecting out
the helper coordinates (pi).  Pricing of a public helper climbing a = p_0 < ... < p_{k+1} = b
(dims): D0 = f(b - a) - sum f(p_{i+1} - p_i), f(r) = r ln r.

Part 1  Per-frame need.  For each frame G (identified by its span):
          R_G = rank pi(contents of fixed registers at every fixed event at G),
          n_G = fixed arrivals (initial residents + every fixed MOVE in),
          m_G = fixed departures (MOVEs out, CLEARs, final residents),
          B_G = max(0, R_G - n_G, R_G - m_G)  <=  pass-through helpers at G.
        Expected: sum B_G = 681; #7334 itself satisfies stops_G >= B_G on every frame.
Part 2  Chain cover, free endpoints: exhaustively over all chains in dims 0..9,
        D0(chain) >= k * f(2) for k interior stops (minimum slack exactly 0), so the
        sound floor is f(2) * 681 = 944.07; #7334's helper D0 = 9,983.73.
Part 3  Conditional floor with #7334's (start dim, end dim) census fixed: a 22-class flow LP;
        the vendored dual certificate (data/lp-dual-c2.json) is checked by weak duality
        here (the bound holds for ANY multipliers, so no solver is trusted): >= 1,367.08.
Controls: tampered certificate multipliers lower the bound; f(2) replaced by f(3) in Part 2
        is violated; dropping the fixed-arrival credit n_G inflates sum B_G.
Prints PASS_HELPER_LAYER_FLOOR.
"""
import collections
import gzip
import hashlib
import itertools
import json
import math
import sys
from fractions import Fraction as Fr
from pathlib import Path

HERE = Path(__file__).resolve().parent
WORD = HERE / 'data' / 'word-7334.json.gz'
WORD_SHA256 = '4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a'
CERT = HERE / 'data' / 'lp-dual-c2.json'
P = 2147483647


def require(ok, label):
    if not ok:
        print('FAIL ' + label)
        sys.exit(1)
    print('ok   ' + label)


def f(r):
    return r * math.log(r) if r > 0 else 0.0


def span(b):
    s = {0}
    for v in b:
        s |= {x ^ v for x in s}
    return frozenset(s)


def canon(S):
    """Canonical name of a subspace: its first independent elements in increasing order."""
    out, sp = [], {0}
    for v in sorted(S):
        if v not in sp:
            out.append(v)
            sp |= {x ^ v for x in sp}
    return ','.join(map(str, out))


def modq(s):
    x = Fr(s)
    return x.numerator % P * pow(x.denominator % P, P - 2, P) % P


def rank(vs):
    piv = {}
    r = 0
    for v in vs:
        v = dict(v)
        while v:
            k = min(v)
            b = piv.get(k)
            if b is None:
                inv = pow(v[k], P - 2, P)
                piv[k] = {c: x * inv % P for c, x in v.items()}
                r += 1
                break
            g = v[k]
            for c, x in b.items():
                nv = (v.get(c, 0) - g * x) % P
                if nv:
                    v[c] = nv
                else:
                    v.pop(c, None)
    return r


def load():
    raw = WORD.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == WORD_SHA256, '#7334 WORD.json.gz SHA256 ' + WORD_SHA256[:16] + '...')
    return json.loads(gzip.decompress(raw))


def needs(W):
    NP, NO = W['public'], W['owned_fields']
    live, H = W['live'], W['hosted']
    mains = set(live) | {r + 112 for r in live} | set(H['X2']) | set(H['Y2'])
    fixed = lambda r: r >= NP or r in mains
    hel = [r for r in range(NP) if not fixed(r)]
    hset = set(hel)
    FS = [span(b) for b in W['frames']]
    FK, KEYS = {}, []
    for s in FS:
        if s not in FK:
            FK[s] = len(KEYS)
            KEYS.append(s)
    fid = [FK[s] for s in FS]
    dimk = [len(s).bit_length() - 1 for s in KEYS]
    N = NP + NO
    row = [{r: 1} if r < NP else {} for r in range(N)]
    cur = list(W['initial']) + [None] * NO
    vec = lambda r: {k: c for k, c in row[r].items() if k not in hset}
    V = collections.defaultdict(list)
    n = collections.Counter()
    m = collections.Counter()
    for r in range(NP):
        if fixed(r):
            V[fid[cur[r]]].append(vec(r))
            n[fid[cur[r]]] += 1
    for e in W['program']:
        op, r = e[0], e[1]
        if op == 'MOVE':
            if fixed(r):
                a, b = fid[e[2]], fid[e[3]]
                v = vec(r)
                V[a].append(v)
                V[b].append(v)
                m[a] += 1
                n[b] += 1
            cur[r] = e[3]
        elif op == 'INIT':
            row[r] = {}
            cur[r] = e[2]
        elif op == 'CLEAR':
            V[fid[e[2]]].append(vec(r))
            m[fid[e[2]]] += 1
            row[r] = {}
            cur[r] = None
        elif op == 'SCALE':
            q = modq(e[2])
            row[r] = {k: v * q % P for k, v in row[r].items()}
        else:
            s, c, g = e[2], modq(e[3]), fid[e[4]]
            both = fixed(s) and fixed(r)
            if both:
                V[g].append(vec(s))
                V[g].append(vec(r))
            if op == 'COPY':
                row[r] = {}
            R = row[r]
            for k, v in row[s].items():
                nv = (R.get(k, 0) + c * v) % P
                if nv:
                    R[k] = nv
                else:
                    R.pop(k, None)
            if both:
                V[g].append(vec(r))
    for r in range(NP):
        if fixed(r):
            V[fid[cur[r]]].append(vec(r))
            m[fid[cur[r]]] += 1
    chain = {h: [fid[W['initial'][h]]] for h in hel}
    for e in W['program']:
        if e[0] == 'MOVE' and e[1] in chain:
            chain[e[1]].append(fid[e[3]])
    stops = collections.Counter()
    for ch in chain.values():
        for x in ch[1:-1]:
            stops[x] += 1
    out = {}
    for G in set(V) | set(stops):
        R = rank(V[G])
        out[G] = dict(dim=dimk[G], R=R, n=n[G], m=m[G], B=max(0, R - n[G], R - m[G]), stops=stops[G],
                      noarr=max(0, R - m[G], R))
    return out, KEYS, dimk, chain


def chain_cost(p):
    return f(p[-1] - p[0]) - sum(f(p[i + 1] - p[i]) for i in range(len(p) - 1))


def part2():
    worst, worst3 = 1e9, 1e9
    for a in range(10):
        for b in range(a + 2, 10):
            for k in range(1, b - a):
                for S in itertools.combinations(range(a + 1, b), k):
                    c = chain_cost([a, *S, b])
                    worst = min(worst, c - k * f(2))
                    worst3 = min(worst3, c - k * f(3))
    require(abs(worst) < 1e-12, 'every chain in dims 0..9 with k interior stops costs >= k f(2); minimum slack %.1e' % worst)
    require(worst3 < -0.1, 'control: the same with f(3) per stop is violated (minimum slack %.3f)' % worst3)


def lp_bound(cert, out, KEYS, dimk, classes, tamper=None):
    """Weak-duality bound for the C2 flow LP from arbitrary multipliers (y free, z <= 0)."""
    need = sorted(G for G, o in out.items() if o['B'] > 0)
    key = lambda G: canon(KEYS[G])
    gid = {key(G): G for G in need}
    y = {}
    for c, node, val in cert['y']:
        cc = tuple(c)
        y[(cc, node if node == 's' else gid[node])] = val
    z = {gid[k]: min(0.0, v) for k, v in cert['z'].items()}
    if tamper:
        tamper(y, z)
    mask = {G: KEYS[G] for G in need}
    inc = [(G, H) for G in need for H in need if dimk[G] < dimk[H] and mask[G] < mask[H]]
    LB = sum(z.get(G, 0.0) * (-out[G]['B']) for G in need)
    for (a, b), N in classes.items():
        cl = (a, b)
        g = lambda p, q: f(q - a) - f(p - a) - f(q - p)
        nodes = [G for G in need if a < dimk[G] < b]
        ns = set(nodes)
        ys = y.get((cl, 's'), 0.0)
        LB += N * ys
        arcs = [('s', 't', 0.0)]
        arcs += [('s', G, g(a, dimk[G])) for G in nodes]
        arcs += [(G, 't', g(dimk[G], b)) for G in nodes]
        arcs += [(G, H, g(dimk[G], dimk[H])) for G, H in inc if G in ns and H in ns]
        for u, v, cost in arcs:
            red = cost
            red -= ys if u == 's' else -y.get((cl, u), 0.0)
            if v != 't':
                red -= y.get((cl, v), 0.0)
                red -= -z.get(v, 0.0)
            if red < 0:
                LB += red * N
    return LB, len(need), len(inc)


def main():
    W = load()
    out, KEYS, dimk, chain = needs(W)
    sumB = sum(o['B'] for o in out.values())
    byd = {d: sum(o['B'] for o in out.values() if o['dim'] == d) for d in range(10)}
    print('     frames %d; sum B_G %d; by dim %s' % (len(out), sumB, byd))
    require(sumB == 681, 'per-frame pass-through need sum B_G = 681')
    require(all(o['stops'] >= o['B'] for o in out.values()), '#7334 satisfies helper stops >= B_G on every frame')
    noarr = sum(o['noarr'] for o in out.values())
    require(noarr > sumB, 'control: dropping the fixed-arrival credit n_G inflates the need to %d' % noarr)
    part2()
    floor = f(2) * sumB
    hel_d0 = sum(chain_cost([dimk[x] for x in ch]) for ch in chain.values())
    require(abs(floor - 944.0665) < 1e-3, 'sound floor f(2) * 681 = %.4f D0' % floor)
    require(abs(hel_d0 - 9983.7252) < 1e-3, '#7334 helper-layer D0 = %.4f (%d helpers)' % (hel_d0, len(chain)))
    ends = collections.Counter((dimk[ch[0]], dimk[ch[-1]]) for ch in chain.values())
    require(len(ends) == 22 and sum(ends.values()) == 1101, '#7334 helper (start dim, end dim) census: 22 classes, 1,101 helpers')
    cert = json.loads(CERT.read_text())
    LB, nneed, ninc = lp_bound(cert, out, KEYS, dimk, dict(ends))
    print('     need frames %d, strict inclusions %d' % (nneed, ninc))
    require(LB >= 1367.08, 'C2 conditional floor (endpoint census fixed): weak-duality bound %.4f >= 1367.08' % LB)

    def tam(y, z):
        for k in list(z):
            z[k] *= 1.5
    LBt, _, _ = lp_bound(cert, out, KEYS, dimk, dict(ends), tam)
    require(LBt < LB - 1, 'control: perturbed multipliers give a weaker bound (%.2f)' % LBt)
    own = 0.0
    needset = {G for G, o in out.items() if o['B'] > 0}
    for ch in chain.values():
        own += chain_cost([dimk[ch[0]]] + [dimk[x] for x in ch[1:-1] if x in needset] + [dimk[ch[-1]]])
    print('     #7334 chains restricted to need stops: %.2f D0' % own)
    require(own >= LB, "#7334's own need-stop pattern is feasible for C2 and costs %.2f >= the bound" % own)
    print('PASS_HELPER_LAYER_FLOOR')


if __name__ == '__main__':
    main()
