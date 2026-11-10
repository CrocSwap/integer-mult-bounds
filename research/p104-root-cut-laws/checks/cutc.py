"""Theorem C (THEOREM.md section 5): crossing bounds for flat words, the nullity step, the (f, r) corollary, the non-flat form n_down + a_down,
and the non-flat toy that is the scope limit of the flat statement. Exact arithmetic over F_p, p = 2^61 - 1; standard library only.
Prints 'ok   ' lines and the marker PASS_CUTC."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import random
from common import req, finish, rank_p

P = 2 ** 61 - 1


def inv_p(A):
    k = len(A)
    M = [[x % P for x in A[i]] + [int(i == j) for j in range(k)] for i in range(k)]
    for j in range(k):
        q = next((i for i in range(j, k) if M[i][j]), None)
        if q is None:
            return None
        M[j], M[q] = M[q], M[j]
        iv = pow(M[j][j], -1, P)
        M[j] = [x * iv % P for x in M[j]]
        for i in range(k):
            if i != j and M[i][j]:
                g = M[i][j]
                M[i] = [(a - g * b) % P for a, b in zip(M[i], M[j])]
    return [r[k:] for r in M]


def sub(M, rows, cols):
    return [[M[i][j] for j in cols] for i in rows]


def rk(M):
    return rank_p(M, P) if M and M[0] else 0


def run_word(n, o, label0, events):
    """Registers 0..n-1 are public, n..n+o-1 owned (start at zero). label0 = start labels of all registers. Events:
    ('H', r, h): register r moves to frame label h.   ('A', d, s, c): register d += c * register s (any labels).
    Returns T (public rows over public inputs), the final labels, and per-event data for the counts."""
    R = [[int(i == j) for j in range(n)] for i in range(n)] + [[0] * n for _ in range(o)]
    lab = list(label0)
    log = []
    for e in events:
        if e[0] == 'H':
            log.append(('H', e[1], lab[e[1]], e[2]))
            lab[e[1]] = e[2]
        else:
            _, d, s, c = e
            log.append(('A', d, s, lab[d], lab[s]))
            R[d] = [(a + c * b) % P for a, b in zip(R[d], R[s])]
    return [r[:] for r in R[:n]], lab, log


def counts(n, label0, final, log, U):
    """n_down, n_up (all hops leaving / entering U), pub/owned split, a_down (ADD with destination outside U and source inside U), flat flag."""
    inU = lambda x: x in U
    nd = nu = pd = pu = od = ou = ad = 0
    flat = True
    for e in log:
        if e[0] == 'H':
            _, r, a, b = e
            if inU(a) and not inU(b):
                nd += 1
                if r < n:
                    pd += 1
                else:
                    od += 1
            if (not inU(a)) and inU(b):
                nu += 1
                if r < n: pu += 1
                else: ou += 1
        else:
            _, d, s, ld, ls = e
            if ld != ls:
                flat = False
            if (not inU(ld)) and inU(ls):
                ad += 1
    return dict(nd=nd, nu=nu, pd=pd, pu=pu, od=od, ou=ou, ad=ad, flat=flat)


def classes(n, label0, final, U):
    A = [r for r in range(n) if label0[r] in U and final[r] in U]
    D = [r for r in range(n) if label0[r] in U and final[r] not in U]
    C = [r for r in range(n) if label0[r] not in U and final[r] in U]
    E = [r for r in range(n) if label0[r] not in U and final[r] not in U]
    return A, D, C, E


def random_word(rnd, flat, passthrough=0):
    n = rnd.randint(3, 6)
    o = rnd.randint(0, 2)
    F = rnd.randint(3, 6)
    label0 = [rnd.randrange(F) for _ in range(n + o)]
    lab = list(label0)
    frozen = set(range(passthrough))                        # public registers that are only ever hopped
    events = []
    for _ in range(rnd.randint(5, 25)):
        if rnd.random() < .3:
            r = rnd.randrange(n + o)
            g = rnd.randrange(F)
            if g != lab[r]:
                events.append(('H', r, g)); lab[r] = g
        else:
            d = rnd.choice([r for r in range(n + o) if r not in frozen])
            cand = [s for s in range(n + o) if s != d and s not in frozen and (not flat or lab[s] == lab[d])]
            if not cand:
                continue
            events.append(('A', d, rnd.choice(cand), rnd.choice([-2, -1, 1, 2])))
    return n, o, F, label0, events


def nullity_theorem(rnd):
    bad = tot = 0
    for _ in range(400):
        n = rnd.randint(2, 6)
        T = [[rnd.randrange(-3, 4) for _ in range(n)] for _ in range(n)]
        Ti = inv_p(T)
        if Ti is None:
            continue
        I = [i for i in range(n) if rnd.random() < .5]
        J = [j for j in range(n) if rnd.random() < .5]
        Ic = [i for i in range(n) if i not in I]
        Jc = [j for j in range(n) if j not in J]
        if not (I and J):
            continue
        nul1 = len(J) - rk(sub(T, I, J))
        nul2 = (len(Ic) - rk(sub(Ti, Jc, Ic))) if (Jc and Ic) else len(Ic)
        tot += 1
        bad += nul1 != nul2
    return tot, bad


def main():
    rnd = random.Random(53)
    # ---- nullity theorem (the step from the up-count to the inverse block)
    tot, bad = nullity_theorem(rnd)
    req(tot > 300 and bad == 0, 'nullity theorem, nullity T[I,J] = nullity T^-1[J^c, I^c], on %d random invertible matrices: 0 failures' % tot)
    # ---- flat words, any U: (a) and (b), planted bounds
    va = vb = ta = tb = ca = cb = cuts = 0
    for _ in range(1500):
        n, o, F, label0, events = random_word(rnd, flat=True)
        T, final, log = run_word(n, o, label0, events)
        Ti = inv_p(T)
        for _ in range(6):
            U = {f for f in range(F) if rnd.random() < .5}
            A, D, C, E = classes(n, label0, final, U)
            c = counts(n, label0, final, log, U)
            assert c['flat']
            cuts += 1
            ra = rk(sub(T, D + E, A + D))
            va += ra > c['nd']; ta += (ra == c['nd'] and c['nd'] > 0); ca += ra > c['nd'] - 1
            if Ti is not None:
                rb = rk(sub(Ti, A + D, D + E))
                lim = c['nu'] - len(C) + len(D)
                vb += rb > lim; tb += (rb == lim and c['nu'] > 0); cb += rb > lim - 1
    req(cuts == 9000 and va == 0, '(a) rank T[D+E, A+D] <= n_down on %d random flat cuts (1,500 words, any U): 0 violations, %d tight' % (cuts, ta))
    req(vb == 0, '(b) rank T^-1[A+D, D+E] <= n_up - |C| + |D| on the invertible cases: 0 violations, %d tight' % tb)
    req(ca > 500 and cb > 500, 'control: the planted bounds n_down - 1 and n_up - |C| + |D| - 1 fail (%d and %d times), so the test can fire' % (ca, cb))
    # ---- corollary: T identity on D (D registers are only hopped); f <= e + o_down, r <= e + o_up; excess >= f + r, >= 2 max(f, r) without owned
    inst = viol1 = viol2 = viol3 = ownedfree = tightfr = 0
    for _ in range(4000):
        n, o, F, label0, events = random_word(rnd, flat=True, passthrough=2)
        T, final, log = run_word(n, o, label0, events)
        Ti = inv_p(T)
        if Ti is None:
            continue
        for _ in range(4):
            U = {f for f in range(F) if rnd.random() < .5}
            A, D, C, E = classes(n, label0, final, U)
            c = counts(n, label0, final, log, U)
            if not (D and A and E):
                continue
            # T is the identity on D when the D registers (all among the first two public registers) are frozen except for hops
            if not all(d < 2 for d in D):
                continue
            f = rk(sub(T, E, A))
            r = rk(sub(Ti, A, E))
            e = c['pd'] - len(D)
            inst += 1
            assert e == c['pu'] - len(C)
            viol1 += f > e + c['od']
            viol2 += r > e + c['ou']
            excess = c['nd'] + c['nu'] - len(C) - len(D)
            viol3 += excess < f + r
            if c['od'] + c['ou'] == 0:
                ownedfree += 1
                viol3 += excess < 2 * max(f, r)
            tightfr += (excess == f + r)
    req(inst > 300 and viol1 == 0 and viol2 == 0, 'corollary: f <= e + o_down and r <= e + o_up on %d cuts with T the identity on D (e = pub_down - |D| = pub_up - |C|): 0 violations' % inst)
    req(viol3 == 0 and ownedfree > 30, 'corollary: crossings beyond |C|+|D| are >= f + r, and >= 2 max(f, r) on the %d owned-free cuts: 0 violations (%d tight at f + r)' % (ownedfree, tightfr))
    # ---- the minimisation behind "f + r with owned, 2 max(f, r) without owned"
    best_owned = {}
    best_pub = {}
    for f in range(0, 9):
        for r in range(0, 9):
            best_owned[f, r] = min(2 * e + od + ou for e in range(0, 20) for od in range(0, 20) for ou in range(0, 20) if e + od >= f and e + ou >= r)
            best_pub[f, r] = min(2 * e for e in range(0, 20) if e >= f and e >= r)
    req(all(best_owned[k] == k[0] + k[1] for k in best_owned) and all(best_pub[k] == 2 * max(k) for k in best_pub), 'minimisation over (e, o_down, o_up): f + r with owned allowed, 2 max(f, r) without, for all 0 <= f, r <= 8')
    req(any(best_pub[k] != k[0] + k[1] for k in best_pub), 'control: without owned the price f + r is not attainable (2 max(f, r) > f + r when f != r); the discount is |f - r|')
    # ---- non-flat words: n_down + a_down, and the toy
    vn = vold = cnt = 0
    for _ in range(1000):
        n, o, F, label0, events = random_word(rnd, flat=False)
        T, final, log = run_word(n, o, label0, events)
        for _ in range(4):
            U = {f for f in range(F) if rnd.random() < .5}
            A, D, C, E = classes(n, label0, final, U)
            c = counts(n, label0, final, log, U)
            ra = rk(sub(T, D + E, A + D))
            cnt += 1
            vn += ra > c['nd'] + c['ad']
            vold += ra > c['nd']
    req(vn == 0, 'non-flat words: rank T[D+E, A+D] <= n_down + a_down on %d random cuts: 0 violations' % cnt)
    req(vold > 0, 'control: the flat bound n_down alone fails on %d of those non-flat cuts' % vold)
    # the toy: frames are elements of F_2^4 (ints, hops are XOR), Delta = 1, m = 2, a = 4, b = 8
    Dl, m, a, b = 1, 2, 4, 8
    X1, X2, Y1, Y2, W, Z1, Z2 = range(7)
    label0 = [0, Dl, m, m ^ Dl, 0, Dl, 0]
    ev = [('A', W, X1, 1), ('A', W, X2, 1), ('A', Z1, X2, 1), ('A', Z2, X1, 1),
          ('H', W, m), ('H', Z1, Dl ^ m ^ a), ('H', Z2, m ^ b),
          ('A', Y1, W, 1), ('A', Y2, W, 1),
          ('H', Y1, m ^ a), ('H', Y2, m ^ Dl ^ b),
          ('A', Y1, Z1, -1), ('A', Y2, Z2, -1)]
    T, final, log = run_word(4, 3, label0, ev)
    want = [[1, 0, 0, 0], [0, 1, 0, 0], [1, 0, 1, 0], [0, 1, 0, 1]]
    req([[x % P for x in r] for r in T] == want, 'toy: y1 += x1 and y2 += x2 exactly (T[E, A] = identity, joint junk w, z1, z2 cancelled)')
    U = {0, Dl, m ^ Dl ^ a, m ^ b}
    A, D, C, E = classes(4, label0, final, U)
    c = counts(4, label0, final, log, U)
    req((A, D, C, E) == ([0, 1], [], [], [2, 3]) and rk(sub(T, D + E, A + D)) == 2, 'toy: U = {0, Delta, m+Delta+a, m+b}: x1, x2 in U at both ends, y1, y2 outside at both ends, rank T[E, A] = 2')
    req(c['nd'] == 1 and c['nu'] == 0 and c['ad'] == 2 and not c['flat'], 'toy: only one hop (w, mass 1) leaves U, so n_down = 1 < 2; a_down = 2 non-flat ADDs (y1 -= z1, y2 -= z2) across U, n_down + a_down = 3 >= 2')
    nonflat_adds = sum(1 for e in log if e[0] == 'A' and e[3] != e[4])
    req(nonflat_adds == 4, 'toy: 4 of the 8 ADDs join registers at different frames (the word is not flat); the flat bound is the one that fails')
    finish('PASS_CUTC')


if __name__ == '__main__':
    main()
