"""Proved packing ceiling for the T16 owner bins of the selected PR1094 supplier (PROOF.md, "A proved packing ceiling").

Standard library only; every decisive comparison is exact (integers and Fractions). Logarithms enter only through
E = sum over bins of g(free), g(f) = f ln f (0 for f <= 1), and every comparison of sums of g values is done on
exp(.) = products of f**f, i.e. on integers. Decimal (correctly rounded ln) is used only to print values.

Inputs, derived from the package data (no hard-coded instance beyond cross-check assertions):
  bins     = every (owner, child) key of data/PLAN.json "windows" times 112 ports, capacity = the window's rank;
  helpers  = the widths of the 69,120 rows of data/OWNERS.json.gz (the same multiset as the selected map).

Theorem 1 (integer weights a(w) = floor(7w/9), A(c) = floor(7c/9)): every multiset of widths with sum <= c has
  sum a <= A(c) (sum a <= 7 sum w / 9 <= 7c/9 and sum a is an integer; also checked over all 1,163 patterns). Summing over bins: 37 * (#empty cap-48 bins) <= sum_bins A - sum_helpers a = 180,832,
  so at most 4,887 cap-48 bins are empty in ANY legal map (windows and the family rule are ignored: relaxation).
Theorem 2 (LP dual): lambda = (36/37) ln 48, v_w and mu_c below are dual-feasible for every pattern, so
  E <= sum_c B_c mu_c - sum_w N_w v_w (exact multiple of ln 48).
Theorem 3 (sharp surrogate bound): with the slack s = A(c) - sum a of each bin, g(free) <= H(s) := max g over
  patterns with slack s, and the slacks sum to 180,832; an exact knapsack argument gives
  E <= 4887 g(48) + g(17).
This bounds the surrogate E and the number of empty cap-48 bins, not kappa."""
from collections import Counter
from decimal import Decimal, getcontext
from fractions import Fraction as Q
from pathlib import Path
import argparse
import gzip
import json

if not __debug__:
    raise RuntimeError('Assertions must remain enabled')
P = Path(__file__).resolve().parent
W = (4, 5, 7, 8, 9)
a = {w: 7*w//9 for w in W}


def A(c):
    return 7*c//9


def patterns(c):
    out = []
    def rec(i, rem, cur):
        if i == len(W):
            out.append(tuple(cur))
            return
        for k in range(rem//W[i]+1):
            rec(i+1, rem-k*W[i], cur+[k])
    rec(0, c, [])
    return out


def expg(f):
    """exp(g(f)) as an integer: f**f for f > 1, else 1."""
    return f**f if f > 1 else 1


def run(data, out_path):
    plan = json.loads((data/'PLAN.json').read_text())
    roles = json.loads(gzip.decompress((data/'OWNERS.json.gz').read_bytes()))
    ports = 112
    B = Counter()
    for key, (cap, _) in plan['windows'].items():
        B[cap] += ports
    N = Counter(r['width'] for r in roles)
    # Cross-check the derived instance against the numbers stated in PROOF.md.
    assert dict(B) == {8: 10752, 16: 7168, 32: 7168, 48: 7168}, B
    assert dict(N) == {w: 144*k for w, k in zip(W, (56, 32, 30, 122, 240))}, N
    caps = sorted(B)
    idle_total = sum(c*n for c, n in B.items()) - sum(w*n for w, n in N.items())
    assert idle_total == 237024

    # Theorem 1.
    assert a == {4: 3, 5: 3, 7: 5, 8: 6, 9: 7} and [A(c) for c in caps] == [6, 12, 24, 37]
    pats = {c: patterns(c) for c in caps}
    npat = sum(len(p) for p in pats.values())
    assert npat == 1163, npat
    for c in caps:
        for p in pats[c]:
            assert sum(a[w]*k for w, k in zip(W, p)) <= A(c), (c, p)
    T = sum(A(c)*n for c, n in B.items()) - sum(a[w]*n for w, n in N.items())
    weight_bins, weight_helpers = sum(A(c)*n for c, n in B.items()), sum(a[w]*n for w, n in N.items())
    assert (weight_bins, weight_helpers, T) == (587776, 406944, 180832)
    nmax = T//37
    assert nmax == 4887

    # Theorem 2: LP dual, all values exact multiples of ln 48 (Fractions); the pattern check compares
    # q*f*ln f <= p*ln 48 as f**(q*f) <= 48**p on integers.
    lam = Q(36, 37)   # lambda / ln 48
    v = {4: 4*lam, 5: 4*lam, 7: Q(20, 3)*lam, 8: 8*lam, 9: Q(28, 3)*lam}
    mu = {8: 8*lam, 16: 16*lam, 32: 32*lam, 48: Q(48)}
    tight = []
    for c in caps:
        for p in pats[c]:
            f = c - sum(w*k for w, k in zip(W, p))
            alpha = mu[c] - sum(v[w]*k for w, k in zip(W, p))   # reduced cost = alpha ln 48 - g(f)
            assert alpha >= 0
            if f > 1:
                lhs, rhs = f**(alpha.denominator*f), 48**alpha.numerator
                assert lhs <= rhs, (c, p)
                if lhs == rhs:
                    tight.append((c, p, f))
            elif alpha == 0:
                tight.append((c, p, f))
    beta = sum(B[c]*mu[c] for c in caps) - sum(N[w]*v[w] for w in W)   # E <= beta ln 48

    # Theorem 3: H(s) = max g over (cap, pattern) with slack s (compared as integers f**f).
    best = {}
    for c in caps:
        for p in pats[c]:
            f = c - sum(w*k for w, k in zip(W, p))
            s = A(c) - sum(a[w]*k for w, k in zip(W, p))
            if s == 0:
                assert f <= 1, (c, p)   # zero-slack bins have g = 0, e.g. cap 32 with (9, 9, 9, 4)
                continue
            if s not in best or expg(f) > expg(best[s][0]):
                best[s] = (f, c, p)
    assert best[37][0] == 48 and best[37][1] == 48   # only the empty cap-48 bin has slack 37 and g(48)
    # rho = max H(s)/s over all items except the empty cap-48 bin; compare f**(f*s') vs f'**(f'*s) on integers.
    other = []   # (slack, free) items available to bins that are not empty cap-48 bins
    for c in caps:
        for p in pats[c]:
            if c == 48 and sum(p) == 0:
                continue
            f = c - sum(w*k for w, k in zip(W, p))
            s = A(c) - sum(a[w]*k for w, k in zip(W, p))
            if s:
                other.append((s, f))
    Hn = {}
    for s, f in other:
        if s not in Hn or expg(f) > expg(Hn[s]):
            Hn[s] = f
    rs, rf = next(iter(Hn.items()))
    for s, f in Hn.items():   # exact argmax of g(f)/s: g(f)/s > g(rf)/rs  <=>  f**(f*rs) > rf**(rf*s)
        if expg(f)**rs > expg(rf)**s:
            rs, rf = s, f
    # rho < g(48)/37 strictly: rf**(rf*37) < 48**(48*rs)
    assert expg(rf)**37 < expg(48)**rs
    # Exact knapsack on the small range: Pk[S] = max over multisets of `other` items with slack sum exactly S of
    # prod f**f (= exp of the best sum of g), None if S is not attainable.
    K = 12
    SM = T - 37*(nmax-K)
    Pk = [1] + [None]*SM
    for S in range(1, SM+1):
        cand = None
        for s, f in Hn.items():
            if s <= S and Pk[S-s] is not None:
                x = Pk[S-s]*expg(f)
                if cand is None or x > cand:
                    cand = x
        Pk[S] = cand
    # For n = nmax-K .. nmax empty cap-48 bins, E <= n g(48) + log Pk[T-37n]; compare relative to n0 = nmax-K.
    n0 = nmax-K
    scores = {}
    for n in range(n0, nmax+1):
        S = T-37*n
        if Pk[S] is not None:
            scores[n] = expg(48)**(n-n0)*Pk[S]
    nbest = max(scores, key=lambda n: scores[n])
    assert nbest == nmax and Pk[T-37*nmax] == expg(17), (nbest, Pk[T-37*nmax])
    # For n < n0: E <= n g(48) + rho (T - 37 n) <= (n0-1) g(48) + rho (T - 37 (n0-1)) (increasing in n, as
    # g(48) > 37 rho). Show that this is below nmax g(48) + g(17):
    #   rho * R < (nmax-n0+1) g(48) + g(17), R = T - 37 (n0-1)
    #   <=> rf**(rf*R) < (48**(48*(K+1)) * 17**17)**rs.
    R = T-37*(n0-1)
    assert expg(rf)**R < (expg(48)**(K+1)*expg(17))**rs
    # The (float) full knapsack over all T as a cross-check of the structure (not part of the proof).
    import math
    gf = lambda f: f*math.log(f) if f > 1 else 0.0
    items = [(s, gf(f)) for s, (f, _, _) in best.items()]
    dp = [0.0]+[-1e300]*T
    for t in range(1, T+1):
        m = -1e300
        for s, x in items:
            if s <= t:
                y = dp[t-s]+x
                if y > m:
                    m = y
        dp[t] = m
    getcontext().prec = 40
    ln = lambda n: Decimal(n).ln()
    g48 = 48*ln(48)
    E3 = nmax*g48 + 17*ln(17)
    E2 = Decimal(beta.numerator)/Decimal(beta.denominator)*ln(48)
    assert abs(Decimal(dp[T]) - E3) < Decimal('1e-6')*E3

    # The package's own map, for reference: its empty cap-48 bins, slack distribution and E.
    used = Counter()
    content = {}
    for r in roles:
        k = (r['owner_replica'], r['child'], r['port'])
        used[k] += r['width']
        content.setdefault(k, Counter())[r['width']] += 1
    cap_of = {}
    for key, (cap, _) in plan['windows'].items():
        o, c = map(int, key.split(','))
        for p in range(ports):
            cap_of[o, c, p] = cap
    n48 = sum(1 for k, c in cap_of.items() if c == 48 and used[k] == 0)
    E = sum(gf(c-used[k]) for k, c in cap_of.items())
    slack = Counter()
    for k, c in cap_of.items():
        s = A(c) - sum(a[w]*n for w, n in content.get(k, Counter()).items())
        assert s >= 0
        slack[c, c-used[k], s] += 1
    assert sum(s*n for (_, _, s), n in slack.items()) == T and n48 <= nmax
    one_free = Counter()
    for (c, f, s), n in slack.items():
        if f == 1:
            one_free[c, s] += n
    out = dict(
        bins=dict(sorted(B.items())), helpers=dict(sorted(N.items())), idle_total=idle_total, patterns=npat,
        theorem1=dict(a=a, A={c: A(c) for c in caps}, bin_weight=weight_bins, helper_weight=weight_helpers,
                      slack_total=T, max_empty_cap48=nmax),
        theorem2=dict(lambda_over_ln48=str(lam), bound_over_ln48=str(beta), bound_decimal=str(E2.quantize(Decimal('0.001'))),
                      tight_patterns=[[c, list(p), f] for c, p, f in tight]),
        theorem3=dict(rho_item=dict(slack=rs, free=rf), bound='4887 g(48) + g(17)', bound_decimal=str(E3.quantize(Decimal('0.001'))),
                      float_full_knapsack=round(dp[T], 3)),
        this_map=dict(empty_cap48=n48, E=round(E, 3), surrogate_gap=round(float(E3)-E, 3),
                      one_free_bins_by_cap_and_slack={f'{c},{s}': n for (c, s), n in sorted(one_free.items())}),
    )
    assert E < float(E3)
    if out_path:
        out_path.write_text(json.dumps(out, indent=1)+'\n')
    print('PASS_PACKING_CEILING', 'empty_cap48<=', nmax, 'E<=', out['theorem3']['bound_decimal'],
          'LP', out['theorem2']['bound_decimal'], 'map', n48, out['this_map']['E'])
    return out


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--data', type=Path, default=P/'data')
    ap.add_argument('--out', type=Path)
    args = ap.parse_args()
    run(args.data, args.out)
