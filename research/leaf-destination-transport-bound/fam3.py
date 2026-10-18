"""PROOF3 Task 1: explicit attaining families for the three census-only source-dirty LCA cases
   (top sign +, (U,V')), (top sign +, (U',V')), (top sign -, (U,V')).
Family: inject at the leaf reached by the y-keeping chain inside phase alpha
        (y-keeping rule: sign + call -> U', sign - call -> U);
        read row z_{V'} (scratch level 2 = register 3) at the cut after the V-chain leaf of V'.U
        (Lemma Q).  Expect: mass == #terms == fl(n), row equals the closed form, and Lemma Q's
        readout formula holds exactly.  Also re-checks the (U,V)+ family of PROOF.md section 4.
Usage: python3 fam3.py LO HI"""
import sys
from check2 import gen, step, mass, fl, find_leaf_signed

UKEEP = lambda sg: "U'" if sg == 1 else 'U'
VRULE = lambda sg: 'V' if sg == 1 else "V'"
CASES = [(1, ('U',), "V'"), (1, ("U'",), "V'"), (-1, ('U',), "V'")]


def seg(hi, length):
    """f_hi f_{hi-1} ... f_{hi-length+1} (leftmost newest)."""
    return tuple(range(hi, hi - length, -1))


def exit_chain(n, s, alpha):
    """Exit column of phase alpha (top sign s) for the y-keeping-chain injection."""
    W = gen(n, s); w = [e for e, _ in W]
    p = find_leaf_signed(W, alpha, UKEEP, s)
    end = max(i for i, (_, q) in enumerate(W) if q[:1] == alpha)
    col = {w[p][1]: {(): 1}}
    for e in w[p + 1:end + 1]:
        step(col, *e)
    return p, end, {r: v for r, v in col.items() if v}


def exit_closed(n, sigma):
    """Claimed exit of a U-type phase (size b = n//2) along the y-keeping chain:
    level l (register l+1), l = 1..H:  sigma * (-1)^(H-l) * f_{floor(n/2^l)-1} ... f_1."""
    H = fl(n)
    return {l + 1: {seg((n >> l) - 1, (n >> l) - 1): sigma * (-1) ** (H - l)} for l in range(1, H + 1)}


def readout_cut(W):
    """Cut after the V-chain leaf of phase V'.U (a sign + call of size c = floor(a/2))."""
    return find_leaf_signed(W, ("V'", 'U'), VRULE, 1)


def lemma_Q(n, s):
    """Lemma Q: row z_{V'} (register 3) of the map from V'-start to the readout cut."""
    W = gen(n, s); w = [e for e, _ in W]
    st = min(i for i, (_, q) in enumerate(W) if q[:1] == ("V'",))
    t = readout_cut(W)
    b, a = n // 2, n - n // 2
    c = a // 2
    R = max(fl(n) + 4, (n - 1).bit_length() + 3)
    got = {}
    for v in range(R):
        col = {v: {(): 1}}
        for e in w[st:t + 1]:
            step(col, *e)
        if col.get(3):
            got[v] = col[3]
    want = {3: {(): 1}, 2: {seg(b + c - 1, c): 1}}
    for l in range(1, (c - 1).bit_length() + 1):       # Lemma P on V'.U, its level l = register l+3
        want[l + 3] = {seg(b + c - 1, -(-c // (1 << l))): 1}
    return got == want


def family(n, s, alpha):
    W = gen(n, s); w = [e for e, _ in W]
    p, end, ex = exit_chain(n, s, alpha)
    t = readout_cut(W)
    col = {w[p][1]: {(): 1}}
    for e in w[p + 1:t + 1]:
        step(col, *e)
    return ex, col.get(3, {}), (p + 1, t + 1)


def row_closed(n, sigma):
    """sum over levels l=1..H of the exit entry times Lemma Q's readout coefficient."""
    b, a = n // 2, n - n // 2
    c = a // 2
    H = fl(n)
    row = {}
    for l in range(1, H + 1):
        left = () if l == 2 else seg(b + c - 1, c) if l == 1 else seg(b + c - 1, -(-c // (1 << (l - 2))))
        row[left + seg((n >> l) - 1, (n >> l) - 1)] = sigma * (-1) ** (H - l)
    return row


SIGMA = {(1, ("U",)): 1, (1, ("U'",)): 1, (-1, ("U",)): 1}   # exit is sign-independent (Lemma X chain)

if __name__ == '__main__':
    lo, hi = int(sys.argv[1]), int(sys.argv[2])
    bad = 0
    for n in range(max(4, lo), hi + 1):
        res = []
        for s, alpha, _ in CASES:
            ex, row, iv = family(n, s, alpha)
            sig = SIGMA[(s, alpha)]
            exok = {r: v for r, v in ex.items() if r != 1} == exit_closed(n, sig)
            q = lemma_Q(n, s)
            good = exok and q and mass(row) == len(row) == fl(n) and row == row_closed(n, sig)
            bad += not good
            res.append('%s%s:%s' % ('+' if s == 1 else '-', alpha[0], 'ok' if good else
                                    'FAIL(exit=%s,Q=%s,mass=%d)' % (exok, q, mass(row))))
        print(n, 'H', fl(n), ' '.join(res), flush=True)
    print('SUMMARY fam3 n=%d..%d failures %d' % (max(4, lo), hi, bad))
