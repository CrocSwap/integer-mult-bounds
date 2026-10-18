"""KB3d engine: the Fourier/Parseval obstruction for the (11,6)/(6,11) rows.

Object: the two remaining rows (5,1),(6,0) of PR 2542's "No 17-point set
covers F2^7" question, the recorded remainder of PR 2773 (package
research/f7-17point-cover-audit-seedcfa215c2, Aaron Wang).  This module
proves them structurally impossible; no enumeration is needed.

Lemma (odd-coverage Fourier obstruction).  Let n >= 1 and let A be a subset
of the even-weight coset E of F2^n and B a subset of the odd-weight coset O,
with |A| = s and |B| = t of opposite parity.  If every odd mask is a cross
sum a + b (a in A, b in B) -- the odd half of (A u B) + (A u B) = F2^n --
then, with r = 1_A * 1_B the cross-sum multiplicity and rho = r - 1_O:

  * sum rho = s*t - |O| =: E_o, rho >= 0 on O;
  * for the all-ones vector 1, r_hat(s) = f_hat(s) g_hat(s) equals
    FT(1_O)(s) + rho_hat(s), and FT(1_O) is supported on {0, 1};
  * so for s not in {0, 1}: |f_hat(s) g_hat(s)| = |rho_hat(s)| <= E_o;
  * f_hat(u) == s (mod 2) and g_hat(u) == t (mod 2) for every u, so the
    odd-cardinality side's character is nonzero and the even-cardinality
    side's character c_hat(u) obeys |c_hat(u)| <= E_o and c_hat(u) == 0
    (mod 2);
  * Parseval on that side: sum_{u not in {0,1}} c_hat(u)^2
    = 2^n * card - card^2 - card^2 (its character is +/- card at 0 and 1).

If the Parseval remainder exceeds (2^n - 2) * (largest even <= E_o)^2 the
hypothesis is contradictory.

For (s, t) = (11, 6) (and its odd-translation mirror (6, 11)) at n = 7:
E_o = 2 forces c_hat(u) in {0, +2, -2} off {0, 1}, but the remainder is
128*6 - 36 - 36 = 696 > 126*4 = 504.  Exact obstruction: deficit 192.
Hence no 17-point set of split (11,6)/(6,11) covers F2^7; the remainder
rows (5,1),(6,0) are impossible.

All arithmetic here is exact Python integers; no floats are used.
"""

# Vendored byte-exact from PR 2773's package (credit: Aaron Wang (navinor),
# PR 2773, head 6739c799799621878a9249c93e2b12cc799c1482, extracted with
# agent_tools.py pr-tree-extract).  The pins are enforced by test_engine.py.
VENDOR_PIN_COVER17 = (
    "082bc838134cba9754368cff894d53c729467a689b4cafee8374423688d93654"
)
VENDOR_PIN_SEARCH17 = (
    "9eb1bf79ffb99b0efcdaF57916c493bc781abd4a0096d584dc6bc6ca294bf674".lower()
)


# ------------------------------------------------------------ characters


def dot(s, x):
    """Parity of the bitwise dot product over F2."""
    return (s & x).bit_count() & 1


def chi(s, x):
    """Character (-1)^(s.x)."""
    return -1 if dot(s, x) else 1


def ft(pts, n):
    """Characters of a set of points: ft[s] = sum_{p in pts} (-1)^(s.p)."""
    N = 1 << n
    return tuple(sum(chi(s, p) for p in pts) for s in range(N))


def rho_hat_values(rho, n):
    """Characters of a multiplicity map {x: count} of small support."""
    N = 1 << n
    out = []
    for s in range(N):
        out.append(sum(c * chi(s, x) for x, c in rho.items()))
    return tuple(out)


# ------------------------------------------------- cross sums and identity


def cross_multiplicity(A, B, n):
    """r = 1_A * 1_B on F2^n: r[x] = #{(a,b): a + b = x}."""
    N = 1 << n
    r = [0] * N
    for a in A:
        for b in B:
            r[a ^ b] += 1
    return r


def ft_convolution_ok(A, B, n):
    """Exact identity check: r_hat(s) = f_hat(s) * g_hat(s) for all s."""
    r = cross_multiplicity(A, B, n)
    f = ft(A, n)
    g = ft(B, n)
    N = 1 << n
    for s in range(N):
        r_hat = sum(r[x] * chi(s, x) for x in range(N))
        if r_hat != f[s] * g[s]:
            return False
    return True


def cross_info(A, B, n):
    """Coverage facts about the cross sums of A x B."""
    r = cross_multiplicity(A, B, n)
    half = 1 << (n - 1)
    all_ones = (1 << n) - 1
    odd = [x for x in range(1 << n) if dot(all_ones, x)]
    covers_odd = all(r[o] >= 1 for o in odd)
    info = {
        "covers_odd": covers_odd,
        "cross_pairs": len(A) * len(B),
        "odd_masks": half,
        "odd_excess": len(A) * len(B) - half,
        "odd_profile": sorted(r[o] - 1 for o in odd if r[o] > 1),
    }
    if covers_odd:
        rho = {o: r[o] - 1 for o in odd if r[o] > 1}
        info["rho_total"] = sum(rho.values())
        info["rho_hat_max"] = max(abs(v) for v in rho_hat_values(rho, n)) if rho else 0
    return info


# ------------------------------------------------------- profile bookkeeping


def _partitions(total):
    """Integer partitions of total as non-increasing tuples."""
    if total == 0:
        yield ()
        return
    for part in range(total, 0, -1):
        for rest in _partitions(total - part):
            if not rest or rest[0] <= part:
                yield (part,) + rest


def odd_profiles(excess):
    """Collision profiles of rho for odd excess: partitions j of the excess
    with sigma = sum j(j+1)/2 even (= 2c for integer c = sum A_x B_x)."""
    out = []
    for parts in _partitions(excess):
        sigma = sum(j * (j + 1) // 2 for j in parts)
        if sigma % 2 == 0:
            out.append(sorted(parts))
    return sorted(out)


def all_rho_shapes(total):
    """All rho: {x: count} over x in [0, 64) with counts summing to total
    (small totals only; used as an exhaustive control on |rho_hat|)."""
    if total == 0:
        yield {}
        return
    for first in range(64):
        for rest in _multisets(total - 1, first, 64):
            rho = {first: 1}
            for x in rest:
                rho[x] = rho.get(x, 0) + 1
            yield rho


def _multisets(remaining, low, high):
    """Multisets of size `remaining` from range(low, high), non-decreasing."""
    if remaining == 0:
        yield ()
        return
    for x in range(low, high):
        for rest in _multisets(remaining - 1, x, high):
            yield (x,) + rest


# ------------------------------------------------------------- the obstruction


def obstruction(n, s_count, t_count):
    """Exact arithmetic of the odd-coverage hypothesis for one parity split.

    Hypothesis: A subset of the even coset of F2^n of size s_count, B subset
    of the odd coset of size t_count, and every odd mask of F2^n is a cross
    sum a + b (a in A, b in B).  Returns a dict; `contradiction` is True when
    that hypothesis is impossible.
    """
    N = 1 << n
    half = 1 << (n - 1)
    odd_excess = s_count * t_count - half
    res = {
        "n": n,
        "split": (s_count, t_count),
        "hypothesis": (
            "A in the even coset, B in the odd coset of F2^%d, |A| = %d, "
            "|B| = %d, and the cross sums A + B cover every odd mask" % (n, s_count, t_count)
        ),
        "odd_excess": odd_excess,
    }
    if odd_excess < 0:
        res["contradiction"] = True
        res["reason"] = "counting: fewer cross pairs than odd masks"
        res["bounded_side"] = None
        res["parseval_remainder"] = None
        res["max_allowed"] = None
        res["deficit"] = None
        res["character_values"] = None
        return res
    if s_count % 2 == t_count % 2:
        res["contradiction"] = False
        res["reason"] = (
            "equal character parities: no side is squeezed by |f_hat g_hat| <= E_o"
        )
        res["bounded_side"] = None
        res["parseval_remainder"] = None
        res["max_allowed"] = None
        res["deficit"] = None
        res["character_values"] = None
        return res
    if s_count % 2 == 0:
        bounded, card = "A", s_count
    else:
        bounded, card = "B", t_count
    max_char = 2 * (odd_excess // 2)  # largest even <= odd_excess
    allowed = list(range(-max_char, max_char + 1, 2))
    # Parseval on the bounded side: sum_u c_hat(u)^2 = 2^n * card, and
    # c_hat(0) = card, c_hat(1) = -card (its points all sit in one coset).
    parseval_remainder = N * card - card * card - card * card
    max_allowed = (N - 2) * max_char * max_char
    res.update(
        bounded_side=bounded,
        bounded_cardinality=card,
        character_values=allowed,
        parseval_remainder=parseval_remainder,
        max_allowed=max_allowed,
        deficit=parseval_remainder - max_allowed,
        contradiction=parseval_remainder > max_allowed,
        reason=(
            "Parseval remainder %d exceeds %d allowed character squares"
            % (parseval_remainder, max_allowed)
        ),
    )
    return res


# ------------------------------------------------------------- set utilities


def sumset_mask(pts, n):
    """Bitmask of {a + b : a, b in pts} (self pairs give mask 0)."""
    mask = 1
    for i in range(len(pts)):
        for j in range(i):
            mask |= 1 << (pts[i] ^ pts[j])
    return mask


def split_of(pts, n):
    """(even-count, odd-count) parity split of a point set."""
    all_ones = (1 << n) - 1
    e = sum(1 for p in pts if not dot(all_ones, p))
    return (e, len(pts) - e)
