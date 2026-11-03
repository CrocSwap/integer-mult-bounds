#!/usr/bin/env python3
"""Shortest six-factor words for the braid endpoint w = 3214.

Standard library only. Checks:
  1. an all-field sufficiency certificate for 16 explicit word families,
     built only from three field-independent operator identities;
  2. an exhaustive census over F_p of every six-factor word equal to [w],
     by tight-peel depth-first search (operator-level final test);
  3. an independent unpruned meet-in-the-middle join at operator level;
  4. that census = union of the families, with 4 n^3 + 12 n^2 words,
     n = p(p+1) the number of rank-one projectors;
  5. that every two-factor suffix allowed by the PR6642 peel table occurs.
Usage: verify.py [p ...]   (default: 2 3; p must be prime)
"""
import itertools
import sys

ID = (0, 1, 2, 3)
LABELS = {"s": (1, 0, 2, 3), "t": (0, 2, 1, 3), "u": (0, 1, 3, 2)}
W = (2, 1, 0, 3)  # one-line 3214, zero-based
PAIRS = [(i, j) for i in range(4) for j in range(4) if i != j]
PIDX = {pr: k for k, pr in enumerate(PAIRS)}
POS = [k for k, (i, j) in enumerate(PAIRS) if i < j]
NEG = [k for k, (i, j) in enumerate(PAIRS) if i > j]
NEGIDX = {k: r for r, k in enumerate(NEG)}

# Families: letter = label, name = projector; X' denotes I - X.
FAMILIES = [
    "s(P) s(P') t(X) t(X') s(Y) s(Y')",
    "t(P) t(P') s(X) s(X') t(Y) t(Y')",
    "s(P) t(X) t(X') s(Y) s(Y') t(P')",
    "t(P) s(X) s(X') t(Y) t(Y') s(P')",
    "s(P) s(P') t(X) s(X) t(X') s(X')",
    "t(P) t(P') s(X) t(X) s(X') t(X')",
    "s(P) t(P) s(X) s(X') t(P') s(P')",
    "t(P) s(P) t(X) t(X') s(P') t(P')",
    "s(P) t(P) s(P') t(P') s(X) s(X')",
    "t(P) s(P) t(P') s(P') t(X) t(X')",
    "s(P) t(X) s(X) t(X') s(X') t(P')",
    "t(P) s(X) t(X) s(X') t(X') s(P')",
    "s(P) t(P') s(P') t(X) t(X') s(P)",
    "t(P) s(P') t(P') s(X) s(X') t(P)",
    "s(P) t(X) t(X') s(P') t(P') s(P)",
    "t(P) s(X) s(X') t(P') s(P') t(P)",
]


def compose(a, b):
    """(ab)(i) = a(b(i)); rightmost acts first."""
    return tuple(a[b[i]] for i in range(4))


def inverse(a):
    out = [0] * 4
    for i, v in enumerate(a):
        out[v] = i
    return tuple(out)


def parse(fam):
    out = []
    for tok in fam.split():
        lab, name = tok[0], tok[2:-1]
        out.append((lab, name.rstrip("'"), name.endswith("'")))
    return out


# ---------------------------------------------------------------- part 1
def reduce_certificate(fam):
    """Rewrite a symbolic word to a pure permutation using only:
    (A) line lemma: a contiguous block whose projectors lie in {Z, I-Z}
        acts by pi_L on im Z and pi_M on ker Z; if pi_L == pi_M it is [pi];
    (B) conjugation: [sigma] D_r(N) = D_{sigma r sigma^-1}(N) [sigma].
    Labels become arbitrary transpositions; both identities hold for every
    transposition, every rank-one projector and every field.
    Returns the resulting permutation and the list of steps."""
    word = [(LABELS[l], z, c) for (l, z, c) in parse(fam)]
    pure = ID  # pure permutation accumulated on the right end
    steps = []
    while word:
        found = None
        for i in range(len(word)):
            for j in range(len(word), i, -1):
                block = word[i:j]
                if len({z for (_, z, _) in block}) != 1:
                    continue
                pl, pm = ID, ID
                for (r, _, c) in block:
                    if c:
                        pm = compose(pm, r)
                    else:
                        pl = compose(pl, r)
                if pl == pm and (j - i) >= 2:
                    found = (i, j, pl)
                    break
            if found:
                break
        if found is None:
            return None, steps
        i, j, pi = found
        steps.append((i, j, pi))
        # push [pi] to the right end through word[j:] by conjugation
        tail = [(compose(compose(pi, r), inverse(pi)), z, c) for (r, z, c) in word[j:]]
        word = word[:i] + tail
        pure = compose(pi, pure)
        # pure permutations already on the right commute past nothing left
    return pure, steps


def check_families_all_fields():
    for fam in FAMILIES:
        res, steps = reduce_certificate(fam)
        assert res == W, (fam, res, steps)
    pats = [''.join(t[0] for t in parse(f)) for f in FAMILIES]
    assert len(set(pats)) == 16
    return pats


# ---------------------------------------------------------------- engines
def mm(a, b, p):
    return ((a[0]*b[0]+a[1]*b[2]) % p, (a[0]*b[1]+a[1]*b[3]) % p,
            (a[2]*b[0]+a[3]*b[2]) % p, (a[2]*b[1]+a[3]*b[3]) % p)


def gmul(x, y, p):
    """Product of elements sum_sigma M_sigma (x) [sigma] of M_2(F_p)[S_4]."""
    out = {}
    for s1, m1 in x.items():
        for s2, m2 in y.items():
            s = compose(s1, s2)
            m = mm(m1, m2, p)
            o = out.get(s)
            out[s] = m if o is None else tuple((u + v) % p for u, v in zip(o, m))
    return {s: m for s, m in out.items() if any(m)}


def opkey(x, p):
    """Exact 24x24 operator on A (x) U, flattened (the equality notion of PR6642)."""
    mat = [[0] * 24 for _ in range(24)]
    for sig, m in x.items():
        for k, (i, j) in enumerate(PAIRS):
            k2 = PIDX[(sig[i], sig[j])]
            for a in range(2):
                for b in range(2):
                    mat[2*k2+a][2*k+b] = (mat[2*k2+a][2*k+b] + m[2*a+b]) % p
    return tuple(v for row in mat for v in row)


def rank(rows, p):
    rows = [r[:] for r in rows]
    r = 0
    for c in range(len(rows[0])):
        piv = next((i for i in range(r, len(rows)) if rows[i][c]), None)
        if piv is None:
            continue
        rows[r], rows[piv] = rows[piv], rows[r]
        inv = pow(rows[r][c], p - 2, p)
        rows[r] = [v * inv % p for v in rows[r]]
        for i in range(len(rows)):
            if i != r and rows[i][c]:
                f = rows[i][c]
                rows[i] = [(v - f * w) % p for v, w in zip(rows[i], rows[r])]
        r += 1
    return r


def phi(x, p):
    """dim H - dim(H cap M^-1 H) = rank of the negative-row/positive-column block."""
    blk = [[0] * 12 for _ in range(12)]
    for sig, m in x.items():
        for c, k in enumerate(POS):
            i, j = PAIRS[k]
            r = NEGIDX.get(PIDX[(sig[i], sig[j])])
            if r is None:
                continue
            for a in range(2):
                for b in range(2):
                    blk[2*r+a][2*c+b] = (blk[2*r+a][2*c+b] + m[2*a+b]) % p
    return rank(blk, p)


def projectors(p):
    out = []
    for n in itertools.product(range(p), repeat=4):
        if mm(n, n, p) == n and (n[0] + n[3]) % p == 1:
            out.append(n)
    assert len(out) == p * (p + 1)
    return out


def comp(n, p):
    return ((1 - n[0]) % p, (-n[1]) % p, (-n[2]) % p, (1 - n[3]) % p)


def factor(lab, n, p):
    return {ID: comp(n, p), LABELS[lab]: n}


def alphabet(p):
    return [((lab, n), factor(lab, n, p)) for lab in "stu" for n in projectors(p)]


def word_op(word, p):
    x = {ID: (1, 0, 0, 1)}
    for lab, n in word:
        x = gmul(x, factor(lab, n, p), p)
    return opkey(x, p)


# ---------------------------------------------------------------- part 2
def census_dfs(p):
    fs = alphabet(p)
    target = {W: (1, 0, 0, 1)}
    assert phi(target, p) == 6
    for _, f in fs:
        assert phi(f, p) == 1
    ident = opkey({ID: (1, 0, 0, 1)}, p)
    words = set()

    def rec(rem, depth, suffix):
        if depth == 6:
            if opkey(rem, p) == ident:
                words.add(tuple(reversed(suffix)))
            return
        for name, f in fs:
            nxt = gmul(rem, f, p)
            if phi(nxt, p) == 5 - depth:
                rec(nxt, depth + 1, suffix + [name])

    rec(target, 0, [])
    return words


# ---------------------------------------------------------------- part 3
def census_mitm(p):
    """No defect pruning. word = L R with |L| = |R| = 3; factors are
    involutions, so L = T R^{-1} = T * reversed(R)."""
    fs = alphabet(p)
    left = {}
    for trip in itertools.product(fs, repeat=3):
        x = gmul(gmul(trip[0][1], trip[1][1], p), trip[2][1], p)
        left.setdefault(opkey(x, p), []).append(tuple(t[0] for t in trip))
    words = set()
    target = {W: (1, 0, 0, 1)}
    for trip in itertools.product(fs, repeat=3):
        x = gmul(gmul(gmul(target, trip[2][1], p), trip[1][1], p), trip[0][1], p)
        for lw in left.get(opkey(x, p), ()):
            words.add(lw + tuple(t[0] for t in trip))
    return words


# ---------------------------------------------------------------- part 4
def family_words(p):
    projs = projectors(p)
    out = set()
    count = 0
    for fam in FAMILIES:
        toks = parse(fam)
        names = sorted({z for (_, z, _) in toks})
        for vals in itertools.product(projs, repeat=len(names)):
            env = dict(zip(names, vals))
            w = tuple((l, comp(env[z], p) if c else env[z]) for (l, z, c) in toks)
            out.add(w)
            count += 1
    assert count == len(out), "family parametrizations overlap"
    return out


def main(primes):
    pats = check_families_all_fields()
    print("PASS all-field sufficiency certificate for 16 families:", " ".join(pats))
    for p in primes:
        n = p * (p + 1)
        fam = family_words(p)
        target = opkey({W: (1, 0, 0, 1)}, p)
        bad = [w for w in fam if word_op(w, p) != target]
        assert not bad, bad[:1]
        dfs = census_dfs(p)
        assert dfs == fam, (len(dfs), len(fam))
        assert len(dfs) == 4 * n**3 + 12 * n**2
        projs = projectors(p)
        suffixes = {w[4:] for w in dfs}
        allowed = set()
        for r, r2 in (("s", "t"), ("t", "s")):
            for P in projs:
                allowed.add(((r, comp(P, p)), (r, P)))
                for N in projs:
                    allowed.add(((r2, N), (r, P)))
        assert suffixes == allowed and len(allowed) == 2 * (n + n * n)
        msg = f"PASS F{p}: n={n} census={len(dfs)} = 4n^3+12n^2, equal to the 16 families; every tight two-peel suffix extends"
        if p <= 3:
            mitm = census_mitm(p)
            assert mitm == dfs
            msg += "; unpruned meet-in-the-middle agrees"
        print(msg)
    print("PASS_BRAID_3214_SHORTEST_WORDS")


if __name__ == "__main__":
    args = [int(a) for a in sys.argv[1:]] or [2, 3]
    main(args)
