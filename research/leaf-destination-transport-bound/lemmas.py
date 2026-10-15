"""Finite exact checks of the three lemmas used in the all-size bound E(n) <= ceil(log2 n).

L2 (prefix monomial): every entry of every prefix map Pre_K(t) of a PR628 call is 0 or +-monomial.
LS (dst/src entry):   Pre_K(t)[y, x] in {0, sign*P_K} at every cut t (P_K = full ordered factor product).
L1 (exit):            injecting at the destination of any leaf of K, the column at K's end has every
                      entry 0 or +-monomial, x-entry 0.
These are proved by induction in PROOF.md; the script only checks finite instances (exact free algebra).
"""
import sys
from census import word


def step(col, x, y, j, s):
    cx = col.get(x)
    if not cx:
        return
    cy = col.setdefault(y, {})
    for m, c in cx.items():
        k = (j,) + m
        v = cy.get(k, 0) + s * c
        if v:
            cy[k] = v
        else:
            del cy[k]


def mass(p):
    return sum(abs(c) for c in p.values())


def check(n):
    R = (n - 1).bit_length() + 2
    P = tuple(range(n - 1, -1, -1))
    for sign in (1, -1):
        w = word(n, sign)
        # prefix maps: column v = image of e_v
        cols = {v: {v: {(): 1}} for v in range(R)}
        for (x, y, j, s) in w:
            for v in range(R):
                step(cols[v], x, y, j, s)
            for v in range(R):
                for r, p in cols[v].items():
                    assert mass(p) <= 1, ('L2', n, sign)
            yx = cols[0].get(1, {})
            assert yx == {} or yx == {P: sign}, ('LS', n, sign, yx)
        # exit lemma
        for p in range(len(w)):
            col = {w[p][1]: {(): 1}}
            for (x, y, j, s) in w[p + 1:]:
                step(col, x, y, j, s)
            assert all(mass(q) <= 1 for q in col.values()), ('L1', n, sign)
            assert not col.get(0), ('L1x', n)
    return True


if __name__ == '__main__':
    hi = int(sys.argv[1]) if len(sys.argv) > 1 else 24
    for n in range(1, hi + 1):
        check(n)
    print('PASS_LEMMAS_L1_L2_LS n=1..%d both signs' % hi)
