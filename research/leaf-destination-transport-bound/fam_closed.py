"""Theorem 2 closed form: for the explicit family interval of check2.family (top sign +),
row y equals  sum_{l=1}^{H} (-1)^{H-l} f_{n-1}...f_{n-ceil(n/2^l)} * f_{floor(n/2^l)-1}...f_1,
H = floor(log2 n), exactly (monomial = tuple of factor indices, leftmost newest).
Also a mutation control: the same interval in the swapped-split word must not match.
Usage: python3 fam_closed.py LO HI"""
import sys
from check2 import family, fl, gen, step, find_leaf_signed


def lemma_P_exact(k):
    """Lemma P exactly (sign +): cut after the V-chain leaf = first leaf of factor k-1, and
    Pre[y,x] = f_{k-1}..f_0, Pre[y,z_l] = f_{k-1}..f_{k-ceil(k/2^l)} for l = 1..ceil(log2 k)."""
    W = gen(k, 1)
    w = [e for e, _ in W]
    t = find_leaf_signed(W, (), lambda sg: 'V' if sg == 1 else "V'", 1)
    if t != min(i for i, e in enumerate(w) if e[2] == k - 1):
        return False
    d = (k - 1).bit_length()
    cols = {v: {v: {(): 1}} for v in range(d + 2)}
    for e in w[:t + 1]:
        for v in cols:
            step(cols[v], *e)
    if cols[0].get(1) != {tuple(range(k - 1, -1, -1)): 1}:
        return False
    for l in range(1, d + 1):
        a = -(-k // (1 << l))
        if cols[l + 1].get(1) != {tuple(range(k - 1, k - a - 1, -1)): 1}:
            return False
    return True


def closed(n):
    H = fl(n)
    row = {}
    for l in range(1, H + 1):
        c, a = n >> l, -(-n // (1 << l))
        mono = tuple(range(n - 1, n - a - 1, -1)) + tuple(range(c - 1, 0, -1))
        row[mono] = (-1) ** (H - l)
    return row


if __name__ == '__main__':
    lo, hi = int(sys.argv[1]), int(sys.argv[2])
    bad = 0
    for n in range(max(2, lo), hi + 1):
        m, nt, ok, iv, row = family(n)
        good = ok and row == closed(n) and m == fl(n)
        bad += not good
        if not good or n & (n - 1) == 0:
            print(n, 'mass', m, 'interval', iv, 'closed-form', 'match' if good else 'MISMATCH', flush=True)
    pb = [k for k in range(1, min(hi, 128) + 1) if not lemma_P_exact(k)]
    print('LemmaP exact formula k=1..%d failures' % min(hi, 128), pb)
    bad += len(pb)
    ctl = sum(family(n, 'swap')[4] != closed(n) for n in range(4, 40))
    print('CONTROL swap-split mismatches n=4..39:', ctl, '/ 36')
    print('SUMMARY closed form n=%d..%d failures %d' % (max(2, lo), hi, bad))
