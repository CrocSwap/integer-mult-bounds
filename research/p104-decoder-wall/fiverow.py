"""P104 decoder wall, part 3: exactly five rows replacing four E8 rows cost >= 28 (FIVEROW). Standard library only.

The theorem (PROOF.md section 3) rests on a finite check over a monotone cover of all codim-5 closures (F, B) (27,423,618 cover closures over both R), run by our C++
enumerator (lane/prop2.cpp, inputs lane/prep.py -> data/fiverow-R*.txt) with the pinned summary data/fiverow-coarse.txt.
That run is too heavy for CI and is NOT repeated here. This checker re-implements the method independently and checks:
  (a) hashes; the vendored labels and Q masks equal those of data/lines120.json; the vendored hyperplane flats of X_R and
      Y_R equal the flats recomputed here from integer normals (exact); every vendored rank-4 start rectangle is genuine
      (I = the 4 ports of a coset of a 2-dim W, J = exactly their common odd partners, rank 2T_R[I,J] = 4);
  (b) seeded random codim-5 closures, both R = (0,1,2,3) and (0,1,3,5), every f = dim F in 0..4: a start block exists,
      propagation outside Dbar x Sbar forces KW, KU, and beta = min over flats hx, hy of rank_F2 Q[KW\\hx, KU\\hy] >= 7;
  (c) teeth: 15 codim-7 closures per R from the enumerator's failure list (f = 0, dim B = 7) reproduce exactly
      (same |KW|, |KU| and beta < 7), so the codim-5 pass is not vacuous;
  (d) the pinned summary: every family of the cover has nostart 0, every coarse failure was refined with refined-fail 0.
Rank tests certify "rank 4" mod p = 2^31 - 1 (a lower bound for the rank over Q, which is what forcing needs).
Usage: fiverow.py [samples per (R, f)] (default 8).  Prints PASS_DECODER_FIVEROW."""
import hashlib, json, random, sys, itertools
from pathlib import Path

HERE = Path(__file__).resolve().parent
SHA = {
    'lines120.json': '4a91033b56fe23feb897b90e6259b33dfbe428ff07ad7ce511a73835074f2708',
    'fiverow-R0123.txt': 'fca962aaafb43e45ab2c5fe45b248a6a73e6de7623882deca17ee4de82598a76', 'fiverow-R0135.txt': 'ca68c3759df549a35eff6c4e619bc0992d018dd8e62ffa08c76ee1441c730d87', 'fiverow-teeth.txt': '8c3e94ef20f5732fb52591963c4e7438c80009a5d40774a6b913b165d206f25d', 'fiverow-coarse.txt': 'dd1e76a3b9f8bc807e0416dde6692ec21ac8ccab53612b00d13614735c856c34',
}
PAIRS = [(117, 107), (114, 106), (111, 108), (104, 110), (115, 109), (112, 119), (105, 118), (116, 113)]
PR = 2147483647
N = 104
P = range(N)


def say(s):
    print(s, flush=True)


def expect(name, got, want):
    if got != want:
        raise SystemExit('FAIL %s: got %r want %r' % (name, got, want))
    say('ok  %s: %r' % (name, got))


def dot(a, b):
    return bin(a & b).count('1') & 1


def basis2(vs):
    b = []
    for v in vs:
        for x in b:
            v = min(v, v ^ x)
        if v:
            b.append(v)
    return b


def prank(rows, cap=4):
    basis = []
    for v in rows:
        v = [x % PR for x in v]
        for c, b in basis:
            if v[c]:
                f = v[c]
                v = [(x - f * y) % PR for x, y in zip(v, b)]
        c = next((i for i, x in enumerate(v) if x), None)
        if c is not None:
            inv = pow(v[c], PR - 2, PR)
            basis.append((c, [x * inv % PR for x in v]))
            if len(basis) == cap:
                break
    return len(basis)


def det3(m):
    return (m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1]) - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
            + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]))


def normal(a, b, c):
    """integer vector orthogonal to a, b, c in Z^4 (generalised cross product); zero iff rank < 3."""
    M = [a, b, c]
    return tuple((-1) ** i * det3([[r[j] for j in range(4) if j != i] for r in M]) for i in range(4))


def flats(Z):
    dirs = sorted({tuple(Z[t]) for t in P if any(Z[t])})
    out = set()
    for a, b, c in itertools.combinations(dirs, 3):
        n = normal(a, b, c)
        if any(n):
            out.add(sum(1 << t for t in P if sum(x * y for x, y in zip(Z[t], n)) == 0))
    return out


def load(raw):
    L = raw.decode().split()
    i = 0
    n = int(L[i]); i += 1
    lab = [int(x) for x in L[i:i + n]]; i += n
    Qm = [int(x, 16) for x in L[i:i + n]]; i += n
    k = int(L[i]); i += 1
    HX = [int(x, 16) for x in L[i:i + k]]; i += k
    k = int(L[i]); i += 1
    HY = [int(x, 16) for x in L[i:i + k]]; i += k
    k = int(L[i]); i += 1
    B = [(int(L[i + 2 * j], 16), int(L[i + 2 * j + 1], 16)) for j in range(k)]
    return lab, Qm, HX, HY, B


def ports(m):
    return [t for t in P if m >> t & 1]


class Inst:
    def __init__(self, R, raw, U, G):
        self.R = R
        lab, Qm, HX, HY, BIC = load(raw)
        expect('%r: vendored labels = lines120 port labels' % (R,), lab == U[:N], True)
        Q = [sum(dot(U[t], U[s]) << s for s in P) for t in P]
        expect('%r: vendored Q masks = recomputed' % (R,), Qm == Q, True)
        self.Q, self.U, self.HX, self.HY, self.BIC = Q, U, HX, HY, BIC
        self.X = [[G[t][PAIRS[j][0]] for j in R] for t in P]
        self.Y = [[G[PAIRS[j][0]][PAIRS[j][1]] * G[s][PAIRS[j][1]] for j in R] for s in P]
        expect('%r: vendored X-flats = recomputed (count %d)' % (R, len(HX)), set(HX) == flats(self.X), True)
        expect('%r: vendored Y-flats = recomputed (count %d)' % (R, len(HY)), set(HY) == flats(self.Y), True)
        good = 0
        for I, J in BIC:
            Ip, Jp = ports(I), ports(J)
            labs = [U[t] for t in Ip]
            W = {a ^ labs[0] for a in labs}
            iscos = len(Ip) == 4 and len(W) == 4 and all(a ^ b in W for a in W for b in W)
            common = sum(1 << s for s in P if all(Q[t] >> s & 1 for t in Ip))
            T = [[sum(x * y for x, y in zip(self.X[t], self.Y[s])) for s in Jp] for t in Ip]
            good += iscos and common == J and prank(T) == 4
        expect('%r: vendored rank-4 start rectangles genuine' % (R,), (good, len(BIC)), (len(BIC), len(BIC)))

    def prop(self, D, S, I, J):
        KW, KU = set(ports(I)), set(ports(J))
        ch = True
        while ch:
            ch = False
            for t in P:
                if t not in KW:
                    part = [self.Y[s] for s in KU if self.Q[t] >> s & 1 and not (D >> t & 1 and S >> s & 1)]
                    if len(part) >= 4 and prank(part) == 4:
                        KW.add(t); ch = True
                if t not in KU:
                    part = [self.X[s] for s in KW if self.Q[s] >> t & 1 and not (D >> s & 1 and S >> t & 1)]
                    if len(part) >= 4 and prank(part) == 4:
                        KU.add(t); ch = True
        return KW, KU

    def evalc(self, Fb, Bb):
        U = self.U
        sp = {0}
        for v in Bb:
            sp |= {x ^ v for x in sp}
        D = sum(1 << t for t in P if U[t] in sp)
        S = sum(1 << t for t in P if all(dot(U[t], x) == 0 for x in Fb))
        best = None
        tries = 0
        done = False
        for pas in range(3):
            if done:
                break
            for I, J in self.BIC:
                if pas == 0:
                    if I & D:
                        continue
                    sI, sJ = I, J
                elif pas == 1:
                    if not I & D:
                        continue
                    sJ, sI = J & ~S, I
                    if prank([self.Y[s] for s in ports(sJ)]) < 4:
                        continue
                else:
                    if I & S:
                        continue
                    sI, sJ = J & ~D, I
                    if prank([self.X[t] for t in ports(sI)]) < 4 or prank([self.Y[s] for s in ports(I)]) < 4:
                        continue
                if best and all(t in best[0] for t in ports(sI)) and all(t in best[1] for t in ports(sJ)):
                    continue
                KW, KU = self.prop(D, S, sI, sJ)
                if best is None or len(KW) + len(KU) > len(best[0]) + len(best[1]):
                    best = (KW, KU)
                tries += 1
                if len(best[0]) + len(best[1]) == 2 * N or tries >= 6:
                    done = True
                    break
        if best is None:
            return 0, set(), set()
        KW, KU = best
        As = [basis2([U[t] for t in KW if not hx >> t & 1]) for hx in self.HX]
        Cs = [basis2([U[t] for t in KU if not hy >> t & 1]) for hy in self.HY]
        beta = 99
        for A in As:
            for C in Cs:
                r = len(basis2([sum(dot(a, c) << j for j, c in enumerate(C)) for a in A]))
                beta = min(beta, r)
        return beta, KW, KU


def rand_sub(rnd, k, containing=()):
    b = basis2(list(containing))
    while len(b) < k:
        b = basis2(b + [rnd.randrange(1, 512)])
    return b


def main():
    nsamp = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    raws = {f: (HERE / 'data' / f).read_bytes() for f in SHA}
    for f, h in SHA.items():
        expect('SHA256 data/' + f, hashlib.sha256(raws[f]).hexdigest(), h)
    d = json.loads(raws['lines120.json'])
    U, G = d['labels'], d['gram']
    insts = {'R0123': Inst((0, 1, 2, 3), raws['fiverow-R0123.txt'], U, G),
             'R0135': Inst((0, 1, 3, 5), raws['fiverow-R0135.txt'], U, G)}

    say('== (b) random codim-5 closures (%d per R and f)' % nsamp)
    for name, seed in (('R0123', 1), ('R0135', 2)):
        rnd = random.Random(seed)
        hist = {}
        for f in range(5):
            for _ in range(nsamp):
                Fb = rand_sub(rnd, f) if f else []
                Bb = rand_sub(rnd, f + 5, containing=Fb)
                beta, KW, KU = insts[name].evalc(Fb, Bb)
                if beta < 7:
                    raise SystemExit('FAIL %s closure F=%r B=%r beta %d' % (name, Fb, Bb, beta))
                hist[(f, beta)] = hist.get((f, beta), 0) + 1
        expect('%s: (f, beta) histogram, all beta >= 7' % name, sorted(hist.items()), [((f, 7), nsamp) for f in range(5)])

    say('== (c) teeth: codim-7 failures reproduce')
    agree = 0
    tot = 0
    for line in raws['fiverow-teeth.txt'].decode().splitlines():
        name, rest = line.split(' ', 1)
        hd, cl = rest.split('|')
        w = hd.split()
        cb, kw, ku = int(w[1]), int(w[3]), int(w[5])
        t = cl.split()
        i = t.index('B')
        Fb = [int(x) for x in t[1:i]]
        Bb = [int(x) for x in t[i + 1:]]
        beta, KW, KU = insts[name].evalc(Fb, Bb)
        tot += 1
        agree += (beta == cb and beta < 7 and len(KW) == kw and len(KU) == ku)
    expect('teeth closures reproduced (beta < 7, same |KW|, |KU|)', (agree, tot), (30, 30))

    say('== (d) pinned summary of the full enumeration (lane/prop2.cpp, not re-run here)')
    fams = [l for l in raws['fiverow-coarse.txt'].decode().splitlines() if l.startswith('refine-to')]
    expect('families (2 R x 5 covers)', len(fams), 10)
    expect('every family: nostart 0 and refined-fail 0',
           all(' nostart 0 ' in l and 'refined-fail 0' in l for l in fams), True)
    tot = sum(int(l.split(' closures ')[1].split()[0]) for l in fams)
    expect('cover closures enumerated (both R)', tot, 2 * (3309747 * 2 + 788035 * 2 + 5516245))
    say('PASS_DECODER_FIVEROW')


if __name__ == '__main__':
    main()
