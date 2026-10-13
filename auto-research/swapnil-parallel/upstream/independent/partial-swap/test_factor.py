"""Task 1: exact checks of the partial-swap batching factorization.
For idempotent p (rank a, m/2<a<m, k=m-a) with invertible first-k-rows/last-k-cols corner, the
lower-lower Bruhat permutation of S_p is exactly: H_l<->D_sigma(l) (sigma = corner's own Bruhat
permutation), H_i<->D_i for i in M=[k, m-k), fixed elsewhere; and S_p = L1 (w D) L2 exactly.
Also implements the batched schedule mod a prime and compares with S_p x."""
import random, sys
from fractions import Fraction as Q
from factor import bruhat, swapmat, predicted, mul, inv, rank, ident

def rand_idem(m, a, rng, lo=-3, hi=3, kind='generic'):
    while True:
        S = [[Q(rng.randint(lo, hi)) for _ in range(m)] for _ in range(m)]
        if kind == 'sparse':
            S = [[x if rng.random() < .3 or i == j else Q(0) for j, x in enumerate(r)] for i, r in enumerate(S)]
        if rank(S) == m: break
    D = [[Q(int(i == j and i < a)) for j in range(m)] for i in range(m)]
    return mul(mul(S, D), inv(S))

def corner(p, k): m = len(p); return [r[m-k:] for r in p[:k]]

def check(p, sim_prime=None, rng=None):
    """Return ('skip'|'ok'|'FAIL', info)."""
    m = len(p); a = rank(p); k = m-a
    assert mul(p, p) == p
    C = corner(p, k)
    S = swapmat(p)
    piv, L1, Mon, L2 = bruhat(S)
    assert mul(mul(L1, Mon), L2) == S, 'factorization identity'
    assert all(L1[i][j] == 0 for i in range(2*m) for j in range(i+1, 2*m))
    assert all(L2[i][j] == 0 for i in range(2*m) for j in range(i+1, 2*m))
    nontriv = sum(1 for i, c in enumerate(piv) if c > i)
    invol = all(piv[piv[i]] == i for i in range(2*m))
    if rank(C) < k:
        return 'singular', dict(nontriv=nontriv, a=a, invol=invol,
                                aligned_mid=all(piv[i] == m+i for i in range(k, m-k)))
    cp, *_ = bruhat(C, track=False)
    sigma = {l: m-k+cp[l] for l in range(k)}
    ok = piv == predicted(sigma, m, k)
    if ok and sim_prime:                      # run the batched schedule over Z/q (field width b=1)
        q = sim_prime
        def md(x):
            return x.numerator*pow(x.denominator, -1, q) % q
        x = [rng.randrange(q) for _ in range(2*m)]
        y = [sum(md(L2[i][j])*x[j] for j in range(i+1)) % q for i in range(2*m)]   # lower: earlier controls
        # monomial: out_i = Mon[i][piv[i]] * y[piv[i]]; done as: scale, k corner swaps, ONE block swap
        sc = [0]*(2*m)
        for i in range(2*m): sc[piv[i]] = md(Mon[i][piv[i]])
        y = [sc[j]*y[j] % q for j in range(2*m)]                 # unit diagonal scaling (column side)
        for l in range(k): y[l], y[sigma[l]+m] = y[sigma[l]+m], y[l]          # k width-b corner swaps
        y[k:m-k], y[m+k:2*m-k] = y[m+k:2*m-k], y[k:m-k]          # one contiguous width-(t b) interchange
        out = [sum(md(L1[i][j])*y[j] for j in range(i+1)) % q for i in range(2*m)]
        want = [sum(md(S[i][j])*x[j] for j in range(2*m)) % q for i in range(2*m)]
        assert out == want, 'mod-q schedule mismatch'
    return ('ok' if ok else 'FAIL'), dict(nontriv=nontriv, a=a)

def denoms(M):
    d = 1
    for r in M:
        for x in r: d = d*x.denominator//__import__('math').gcd(d, x.denominator)
    return d

if __name__ == '__main__':
    tally = {}
    rng = random.Random(2026)
    cases = []
    # all (m, a) with m in 3..12 and every a in (m/2, m), including a = floor(m/2)+1 (t = 1 or 2)
    for m in range(3, 13):
        for a in range(m//2+1, m):
            for rep in range(6): cases.append((m, a, 'generic'))
            for rep in range(3): cases.append((m, a, 'sparse'))
    for m, a, kind in cases:
        p = rand_idem(m, a, rng, kind=kind)
        st, info = check(p, sim_prime=1000003, rng=rng)
        tally[st] = tally.get(st, 0)+1
        if st == 'FAIL': print('FAIL', m, a, kind, info); sys.exit(1)
        if st == 'singular':
            tally.setdefault('singular_profiles', set()).add((info['nontriv'] == info['a'], info['invol'], info['aligned_mid']))
    print('random idempotents:', {k: v for k, v in tally.items()})
    # adversarial: corner singular by construction
    adv = {}
    for m in range(4, 11):
        for a in range(m//2+1, m):
            k = m-a
            # p = diag-type: coordinate projector onto first a coords (corner is zero)
            p = [[Q(int(i == j and i < a)) for j in range(m)] for i in range(m)]
            st, info = check(p); adv.setdefault('coordinate', []).append((m, a, st, info['nontriv'], info['aligned_mid']))
            # projector whose kernel misses the last k coordinates (U_L singular): q = UV with U_L rank-deficient
            while True:
                U = [[Q(rng.randint(-2, 2)) for _ in range(k)] for _ in range(m)]
                U[0] = [Q(0)]*k                          # first row of U zero -> U_L singular
                V = [[Q(rng.randint(-2, 2)) for _ in range(m)] for _ in range(k)]
                VU = mul(V, U)
                if rank(U) == k and rank(VU) == k: break

            qq = mul(mul(U, inv(VU)), V)
            p = [[Q(int(i == j))-qq[i][j] for j in range(m)] for i in range(m)]
            st, info = check(p); adv.setdefault('U_L singular', []).append((m, a, st, info['nontriv'], info['aligned_mid']))
    for k_, v in adv.items():
        bad_aligned = [x for x in v if not x[4]]
        print('adversarial', k_, ': all singular corners =', all(x[2] == 'singular' for x in v),
              '| nontriv==a in', sum(x[3] == x[1] for x in v), '/', len(v),
              '| middle NOT aligned in', len(bad_aligned), '/', len(v), 'e.g.', bad_aligned[:2])
