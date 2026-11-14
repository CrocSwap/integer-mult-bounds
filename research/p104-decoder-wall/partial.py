"""P104 decoder wall, part 2: partial replacement of E8 rows. Standard library only, exact.

Setting: keep the E8 rows outside R (R a set of row indices), replace the rows in R by rank-1 rows w_k u_k^T that must give
2T_R := sum_{j in R} w_j (2u_j)^T on every Q-cell (odd-label pair or diagonal); even cells are free (junk).
Checked:
  (a) for each of the 70 four-subsets R: a 4 x 15 all-Q rectangle I x J (I = the 4 ports on a coset a + W, dim W = 2;
      J = their common odd partners) with rank 2T_R[I,J] = 4. By the rectangle-rank lemma any replacement needs >= 4
      rank-1 rows: 3 or fewer rows (any climbs, any field of characteristic 0) are impossible;
  (b) for each R, exactly 4 replacement rows: propagation from that rectangle (a port whose forced partners on allowed
      cells have rank 4 is forced) reaches forced sets KW = KU = all 104 ports for 62 R, and all but one common port t0 for
      8 R. So the 4 rows are E8-world rows (X a_k)(Y b_k)^T on the forced ports; with rows.py (e) each has dim B, dim A >= 8
      even with one port free, so pairing rank >= 7 and the replacement costs >= 28 (the original rows: exactly 28);
  (c) cross-pair identity: for every nonempty R (255 subsets), (2T_R o Q) mod 2 = sum_{j in R, i not in R}
      (x_i x_j)(y_i y_j)^T mod 2 (x_j = 2u_j mod 2, y_j = w_j mod 2), and its F2 rank is exactly |R|(8 - |R|);
      hence a half-integer replacement of R costs >= |R|(8-|R|) (7, 12, 15, 16, ... for |R| = 1, 2, 3, 4).
Ranks: rank mod p (p = 2^31 - 1) only to certify "rank 4" (a lower bound for the rank over Q, all that (a) and (b) need).
Prints PASS_DECODER_PARTIAL."""
import hashlib, json, itertools
from pathlib import Path

HERE = Path(__file__).resolve().parent
SHA_LINES = '4a91033b56fe23feb897b90e6259b33dfbe428ff07ad7ce511a73835074f2708'
PAIRS = [(117, 107), (114, 106), (111, 108), (104, 110), (115, 109), (112, 119), (105, 118), (116, 113)]
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


def setup():
    raw = (HERE / 'data' / 'lines120.json').read_bytes()
    expect('SHA256 data/lines120.json', hashlib.sha256(raw).hexdigest(), SHA_LINES)
    d = json.loads(raw)
    U, G = d['labels'], d['gram']
    W, U2 = [], []
    for dd, dp in PAIRS:
        c = G[dd][dp]
        W.append([G[p][dd] for p in range(N)])
        U2.append([c * G[s][dp] for s in range(N)])
    Q = [[dot(U[t], U[s]) for s in range(N)] for t in range(N)]
    return U, G, W, U2, Q


def start_rect(R, U, W, U2, Q):
    """all rank-4 all-Q rectangles, in order (4-port coset I, J = common Q-partners) for target 2T_R."""
    seen = set()
    for w1 in range(1, 512):
        for w2 in range(w1 + 1, 512):
            Wsp = frozenset((0, w1, w2, w1 ^ w2))
            if Wsp in seen:
                continue
            seen.add(Wsp)
            cos_seen = set()
            for a in U[:N]:
                cos = frozenset(a ^ x for x in Wsp)
                if cos in cos_seen:
                    continue
                cos_seen.add(cos)
                I = [p for p in range(N) if U[p] in cos]
                if len(I) < 4:
                    continue
                J = [s for s in range(N) if all(Q[t][s] for t in I)]
                M = [[sum(W[j][t] * U2[j][s] for j in R) for s in J] for t in I]
                if prank(M) == 4:
                    yield I, J


def propagate(R, I, J, W, U2, Q):
    X = [[W[j][t] for j in R] for t in range(N)]
    Y = [[U2[j][s] for j in R] for s in range(N)]
    KW, KU = set(I), set(J)
    ch = True
    while ch:
        ch = False
        for t in range(N):
            if t not in KW and prank([Y[s] for s in KU if Q[t][s]]) == 4:
                KW.add(t)
                ch = True
            if t not in KU and prank([X[s] for s in KW if Q[s][t]]) == 4:
                KU.add(t)
                ch = True
    return KW, KU


def main():
    U, G, W, U2, Q = setup()
    G104 = [[sum(W[j][t] * U2[j][s] for j in range(8)) for s in range(N)] for t in range(N)]
    expect('positive control: sum_j w_j (2u_j)^T = G on all cells', all(G104[t][s] == G[t][s] for t in range(N) for s in range(N)), True)

    say('== (a)+(b) four-row targets, all 70 R')
    hist = {}
    rect = {}
    for R in itertools.combinations(range(8), 4):
        best = None
        tries = 0
        for I, J in start_rect(R, U, W, U2, Q):
            tries += 1
            KW, KU = propagate(R, I, J, W, U2, Q)
            if best is None or len(KW) + len(KU) > len(best[0]) + len(best[1]):
                best = (KW, KU)
            if len(KW) + len(KU) >= 206 or tries >= 20:
                break
        if best is None:
            raise SystemExit('FAIL no rank-4 rectangle for R=%r' % (R,))
        rect[tries] = rect.get(tries, 0) + 1
        KW, KU = best
        free = tuple(sorted(set(range(N)) - KW)), tuple(sorted(set(range(N)) - KU))
        key = (len(KW), len(KU), free[0] == free[1])
        hist[key] = hist.get(key, 0) + 1
    expect('rank-4 start rectangles found for all 70 R', sum(rect.values()), 70)
    say('    starts tried per R (histogram): %r' % dict(sorted(rect.items())))
    expect('forced sets (|KW|, |KU|, same free port) over the 70 R', hist, {(104, 104, True): 62, (103, 103, True): 8})
    # control: a rectangle on non-Q cells is not admissible -- the start search must reject an even pair
    t0 = 0
    s0 = next(s for s in range(N) if s != t0 and not Q[t0][s])
    expect('control: even cell exists in row 0 (not prescribed)', Q[t0][s0], 0)

    say('== (c) cross-pair identity and the k(8-k) bound')
    xb = [sum((U2[j][s] % 2) << s for s in range(N)) for j in range(8)]
    y = [[W[j][t] % 2 for t in range(N)] for j in range(8)]
    Qb = [sum(Q[t][s] << s for s in range(N)) for t in range(N)]
    ranks = {}
    allid = True
    for k in range(1, 9):
        for R in itertools.combinations(range(8), k):
            Rs = set(R)
            rows = []
            for t in range(N):
                bits = 0
                for j in R:
                    if y[j][t]:
                        bits ^= xb[j] & Qb[t]
                bits2 = 0
                for j in R:
                    for i in range(8):
                        if i not in Rs and y[i][t] and y[j][t]:
                            bits2 ^= xb[i] & xb[j]
                if bits != bits2:
                    allid = False
                rows.append(bits)
            ranks.setdefault(k, set()).add(rank2(rows))
    expect('identity (2T_R o Q) mod 2 = cross pairs, all 255 R', allid, True)
    expect('F2 rank by |R|', {k: sorted(v) for k, v in ranks.items()}, {k: [k * (8 - k)] for k in range(1, 9)})
    say('PASS_DECODER_PARTIAL')


if __name__ == '__main__':
    main()
