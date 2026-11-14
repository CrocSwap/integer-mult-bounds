"""P104 decoder wall, part 1: the row price and the exact 8-row decoder with rank-8 rigidity. Standard library only.

Data (SHA256 pinned below): data/lines120.json = {"labels": 120 F2^9 labels, "gram": 120x120 integer Gram} of the 120
E8 lines, the first 104 being the P104 ports (our derived data; reflection closure of the port Gram, labels solved over F2);
data/iso968.json maps the PR968 decoder's Gram onto the vendored 104-port block. The PR968 decoder file is read from the
repository (pinned in SOURCES.json).
Checked:
  (a) hashes; the 120-line Gram is an E8 line Gram (symmetric, diagonal 2, entries in {0,+-1} off the diagonal, rank 8,
      G^2 = 30 G); the 104-port block equals the PR968 Gram D T^T/2 under the vendored permutation and signs (every entry);
      labels: dot(u_i,u_j) = G_ij + 1 mod 2 on all 120^2 pairs, all labels odd and distinct;
  (b) Lemma 1 identity: dim B - dim(B cap A^perp) = F2 rank of [q_t.q_s] (t in D, s in S) on 400 seeded random supports;
  (c) the decoder: 8 rows w_j = G[.,d_j], u_j = G[.,d'_j]/(2 G[d_j,d'_j]) on the 16 virtual lines; sum_j w_j u_j^T = G/2
      exactly on all 104^2 cells, so M_pp = 1 and M = 0 on every odd-label cell; each row |D| = |S| = 52, pairing rank 7
      (= dim B + dim A - 9 = 8 + 8 - 9), total 56 = 7/13 per port; control: the form rank of a row on A+B is 9, not 7;
  (d) zero freedom: with the 8 gather vectors fixed and all 8 coordinates free, each port's deposit vector is the unique
      solution of its odd + diagonal equations (nullity 1 at all 104 ports) and equals the E8 one;
  (e) rank-8 flats: a real vector v != 0 has support {t : r_t.v != 0} whose labels span <= 9 - c dims only if the ports
      outside some codim-c label subspace have real rank <= 7. Exactly 16 hyperplanes do (52 ports outside each; exact
      rank 7), and no codim-2 subspace does (all 43,435), even after deleting any one port (no coloops). Hence every
      E8-world row (Xa)(Yb)^T has dim B, dim A >= 8 and pairing rank >= 7, also with one port free.
Real ranks use the integer matrix G[S, basis] (rank = rank of the root set); rank mod p = 2^31-1 is a lower bound and is
used only to certify rank 8; every "rank <= 7" is re-checked exactly over Q.  Prints PASS_DECODER_ROWS."""
import hashlib, json, random, itertools
from pathlib import Path
from fractions import Fraction as Fr

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PR968 = 'research/complex-frame-pair-decoders/inputs/pr717/P104_HIT_flip_3a.txt'
PR968_SHA256 = '8e0178db02c14e1b29058cdbdbd50aac22f2b55a1ba21dc82f417610c9932526'
SHA = {
    'lines120.json': '4a91033b56fe23feb897b90e6259b33dfbe428ff07ad7ce511a73835074f2708',
    'iso968.json': 'fd3fb6b90918d6802c7b22b7fe2efdf3a3979e4bc50bb610437957a84b702e1f',
}
PAIRS = [(117, 107), (114, 106), (111, 108), (104, 110), (115, 109), (112, 119), (105, 118), (116, 113)]  # (d_j, d'_j)
PR = 2147483647
N = 104


def say(s):
    print(s, flush=True)


def expect(name, got, want):
    if got != want:
        raise SystemExit('FAIL %s: got %r want %r' % (name, got, want))
    say('ok  %s: %r' % (name, got))


def dot(a, b):
    return bin(a & b).count('1') & 1


def rank2(vs):
    basis = []
    for v in vs:
        for b in basis:
            v = min(v, v ^ b)
        if v:
            basis.append(v)
    return len(basis)


def span(vs):
    s = {0}
    for v in vs:
        if v not in s:
            s |= {x ^ v for x in s}
    return s


def fdim(s):
    return len(s).bit_length() - 1


def pairing_rank(Dl, Sl):
    Sl = sorted(set(Sl))
    return rank2([sum(dot(t, s) << i for i, s in enumerate(Sl)) for t in set(Dl)])


def qrank(M):
    A = [[Fr(x) for x in r] for r in M]
    if not A:
        return 0
    r = 0
    for c in range(len(A[0])):
        p = next((i for i in range(r, len(A)) if A[i][c] != 0), None)
        if p is None:
            continue
        A[r], A[p] = A[p], A[r]
        for i in range(len(A)):
            if i != r and A[i][c] != 0:
                f = A[i][c] / A[r][c]
                A[i] = [x - f * y for x, y in zip(A[i], A[r])]
        r += 1
    return r


def prank(rows):
    """rank mod PR of integer vectors (a lower bound for the rank over Q); returns (rank, pivot row indices)."""
    basis = []  # (pivot col, normalised vector)
    piv_rows = []
    for idx, v in enumerate(rows):
        v = [x % PR for x in v]
        for c, b in basis:
            if v[c]:
                f = v[c]
                v = [(x - f * y) % PR for x, y in zip(v, b)]
        c = next((i for i, x in enumerate(v) if x), None)
        if c is not None:
            inv = pow(v[c], PR - 2, PR)
            basis.append((c, [x * inv % PR for x in v]))
            piv_rows.append(idx)
            if len(basis) == 8:
                break
    return len(basis), piv_rows


def nullspace(M):
    """exact nullspace basis of a Fraction matrix."""
    A = [list(r) for r in M]
    m = len(A[0])
    piv = []
    r = 0
    for c in range(m):
        p = next((i for i in range(r, len(A)) if A[i][c] != 0), None)
        if p is None:
            continue
        A[r], A[p] = A[p], A[r]
        A[r] = [x / A[r][c] for x in A[r]]
        for i in range(len(A)):
            if i != r and A[i][c] != 0:
                f = A[i][c]
                A[i] = [x - f * y for x, y in zip(A[i], A[r])]
        piv.append(c)
        r += 1
    free = [c for c in range(m) if c not in piv]
    out = []
    for fc in free:
        v = [Fr(0)] * m
        v[fc] = Fr(1)
        for i, pc in enumerate(piv):
            v[pc] = -A[i][fc]
        out.append(v)
    return out


def main():
    raws = {f: (HERE / 'data' / f).read_bytes() for f in SHA}
    for f in SHA:
        expect('SHA256 data/' + f, hashlib.sha256(raws[f]).hexdigest(), SHA[f])
    d = json.loads(raws['lines120.json'])
    U, G = d['labels'], d['gram']
    P = list(range(N))

    say('== (a) geometry')
    expect('120 lines, distinct odd labels', (len(U), len(set(U)), all(dot(u, u) for u in U)), (120, 120, True))
    expect('Gram symmetric, diag 2, off-diagonal in {0,+-1}',
           all(G[i][j] == G[j][i] for i in range(120) for j in range(120)) and all(G[i][i] == 2 for i in range(120))
           and all(G[i][j] in (0, 1, -1) for i in range(120) for j in range(120) if i != j), True)
    expect('rank G120', qrank(G), 8)
    expect('G120^2 = 30 G120', all(sum(G[i][k] * G[k][j] for k in range(120)) == 30 * G[i][j]
                                   for i in range(120) for j in range(120)), True)
    expect('dot(u_i,u_j) = G_ij + 1 mod 2 on all 120^2 pairs',
           all(dot(U[i], U[j]) == (G[i][j] + 1) % 2 for i in range(120) for j in range(120)), True)
    raw = (ROOT / PR968).read_bytes()
    expect('SHA256 of PR968 decoder file', hashlib.sha256(raw).hexdigest(), PR968_SHA256)
    ls = raw.decode().split('\n')
    Dr = [[int(x) for x in l[3:].split()] for l in ls if l.startswith(' d:')]
    Tr = [[int(x) for x in l[3:].split()] for l in ls if l.startswith(' t:')]
    GP = [[sum(Dr[k][i] * Tr[k][j] for k in range(8)) // 2 for j in range(N)] for i in range(N)]
    iso = json.loads(raws['iso968.json'])
    perm, eps = iso['perm'], iso['eps']
    expect('PR968 Gram = eps eps G104(perm) on all 104^2 entries',
           all(GP[u][v] == eps[u] * eps[v] * G[perm[u]][perm[v]] for u in P for v in P), True)

    say('== (b) Lemma 1 identity (pairing rank = dim B - dim(B cap A^perp))')
    rnd = random.Random(7)
    good = 0
    for _ in range(400):
        Dl = rnd.sample(U, rnd.randint(1, 12))
        Sl = rnd.sample(U, rnd.randint(1, 12))
        B, A = span(Dl), span(Sl)
        Bp = [x for x in B if all(not dot(x, a) for a in Sl)]
        good += pairing_rank(Dl, Sl) == fdim(B) - fdim(set(Bp))
    expect('identity on 400 random (D,S)', good, 400)

    say('== (c) the 8-row decoder')
    rows = []
    for dd, dp in PAIRS:
        c = G[dd][dp]
        assert dd >= N and dp >= N and c in (1, -1)
        w = [G[p][dd] for p in P]
        u = [Fr(G[s][dp], 2 * c) for s in P]
        rows.append((w, u))
    M = [[sum(w[t] * u[s] for w, u in rows) for s in P] for t in P]
    expect('M = G/2 on all 104^2 cells', all(M[t][s] == Fr(G[t][s], 2) for t in P for s in P), True)
    expect('M_pp = 1 and M = 0 on every odd-label cell',
           all(M[p][p] == 1 for p in P) and all(M[t][s] == 0 for t in P for s in P if t != s and dot(U[t], U[s])), True)
    expect('odd cells per port (excluding diagonal)', sorted({sum(1 for s in P if s != t and dot(U[t], U[s])) for t in P}), [55])
    tot = 0
    prof = []
    for w, u in rows:
        Dl = [U[t] for t in P if w[t]]
        Sl = [U[s] for s in P if u[s]]
        r = pairing_rank(Dl, Sl)
        tot += r
        prof.append((len(Dl), len(Sl), fdim(span(Dl)), fdim(span(Sl)), r, pairing_rank(Dl + Sl, Dl + Sl)))
    expect('rows (|D|,|S|,dim B,dim A,pairing rank,control form rank on A+B)', sorted(set(prof)), [(52, 52, 8, 8, 7, 9)])
    expect('total climb floor', (tot, Fr(tot, N)), (56, Fr(7, 13)))

    say('== (d) zero freedom per port')
    hist = {}
    same = True
    for p in P:
        odd = [s for s in P if s != p and dot(U[p], U[s])]
        ns = nullspace([[rows[j][1][s] for j in range(8)] for s in odd])
        hist[len(ns)] = hist.get(len(ns), 0) + 1
        if len(ns) != 1:
            same = False
            continue
        v = ns[0]
        sc = sum(v[j] * rows[j][1][p] for j in range(8))
        if sc == 0 or any(v[j] / sc != rows[j][0][p] for j in range(8)):
            same = False
    expect('nullity histogram (all 8 coordinates free)', hist, {1: 104})
    expect('unique solution = E8 deposit vector at every port', same, True)

    say('== (e) rank-8 flats')
    bas = prank([G[p] for p in P])[1]
    expect('a real basis among the ports', len(bas), 8)
    V = [[G[p][b] for b in bas] for p in P]
    expect('basis coordinates have real rank 8', qrank(V), 8)
    hyp = []
    for y in range(1, 512):
        out = [p for p in P if dot(U[p], y)]
        if prank([V[p] for p in out])[0] < 8 and qrank([V[p] for p in out]) <= 7:
            hyp.append((y, len(out), qrank([V[p] for p in out])))
    expect('hyperplanes y^perp whose outside ports have real rank <= 7', len(hyp), 16)
    expect('their outside sizes and ranks', sorted({(o, r) for _, o, r in hyp}), [(52, 7)])
    expect('they are the kernel hyperplanes of odd y', sorted({dot(y, y) for y, _, _ in hyp}), [1])
    seen = set()
    nY = 0
    bad = []
    for y1 in range(1, 512):
        for y2 in range(y1 + 1, 512):
            key = frozenset((y1, y2, y1 ^ y2))
            if key in seen:
                continue
            seen.add(key)
            nY += 1
            out = [p for p in P if dot(U[p], y1) or dot(U[p], y2)]
            vecs = [V[p] for p in out]
            r, piv = prank(vecs)
            ok = r == 8
            if ok:
                for i in piv:  # only basis members can be coloops
                    if prank(vecs[:i] + vecs[i + 1:])[0] < 8:
                        ok = False
                        break
            if not ok:
                bad.append((y1, y2))
    expect('codim-2 label subspaces checked', nY, 43435)
    expect('codim-2 subspaces whose outside ports (minus any one port) have rank <= 7', bad, [])
    # control: the check bites -- a kernel hyperplane's outside set fails it
    y0 = hyp[0][0]
    out0 = [V[p] for p in P if dot(U[p], y0)]
    expect('control: kernel hyperplane outside set certified rank 8?', prank(out0)[0] == 8, False)
    say('PASS_DECODER_ROWS')


if __name__ == '__main__':
    main()
