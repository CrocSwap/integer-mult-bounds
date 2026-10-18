"""17-point cover audit engine: pair-representation identity, sharp rows,
coverage primitives and exact small controls.

Object (KB3c, pair-collision object change recorded in TASK.json): the status
of PR 2542's claim "No 17-point set covers F2^7" against its own lemma table.
PR 2542's `lemma_a_table` (vendored byte-exact as vendor/pr2542_engine.py,
credit PR 2542, package research/universal-f7-singleton-seedb859517b) only
contradicts the (9,8)/(8,9) split rows; the counting-feasible 17-point splits
(10,7)/(7,10)/(11,6)/(6,11) survive it.  This module extends the identity
with the sharp collision-multiplicity constraint and computes exactly which
(e_ex, b_ex, c) rows survive per split.

Definitions.  S = A u B with A = S int E (s points, even weight), B = S int O
(t points, odd weight), s + t = 17.  A_x = #unordered pairs of A summing to
x, B_x likewise (x even nonzero).  e_ex = C(s,2) - |supp(A)|, b_ex likewise.
Cross sums a+b (a in A, b in B) hit the odd masks with multiplicities r_o, so

    odd excess       sum_o (r_o - 1) = s*t - 2^(n-1) =: E_o
    colliding pairs  sum_o C(r_o,2)  = 2 * sum_x A_x B_x =: 2c

with C(r,2) >= r-1 per mask.  A collision profile is a partition of E_o into
j = r_o - 1 parts; it needs sigma = sum j(j+1)/2 = 2c even.  A row (e_ex,
b_ex) is multiset-feasible for profile c iff c is exactly attainable as the
sum of shared products A_x B_x over the shared = C(s,2)+C(t,2)-e_ex-b_ex-
(2^(n-1)-1) support positions (multiplicity shapes from partitions of e_ex
resp. b_ex).  This refines PR 2542's closed-form upper bound.
"""

from functools import lru_cache

VENDOR_PIN_PR2542 = (
    "82e4c407b58864c74ffd14d47f00b6b1675005ee0e0173909b7bd092491175e4"
)


# ------------------------------------------------------- counting bounds


def counting_ok(n, s, t):
    odd_masks = 1 << (n - 1)
    even_nonzero = odd_masks - 1
    return (
        s * t >= odd_masks
        and s * (s - 1) // 2 + t * (t - 1) // 2 >= even_nonzero
    )


# ------------------------------------------- collision-multiplicity identity


def _partitions(total):
    """Integer partitions of total as tuples (non-increasing)."""
    if total == 0:
        yield ()
        return
    for part in range(total, 0, -1):
        for rest in _partitions(total - part):
            if not rest or rest[0] <= part:
                yield (part,) + rest


def odd_profiles(excess):
    """Collision profiles for odd excess `excess`: partitions j of it with
    sigma = sum j(j+1)/2 even (= 2c for integer c).  Each j is one odd mask
    with r = j + 1 cross representations."""
    out = []
    for parts in _partitions(excess):
        sigma = sum(j * (j + 1) // 2 for j in parts)
        if sigma % 2 == 0:
            out.append(sorted(parts))
    return sorted(out)


def profile_c_values(n, s, t):
    """c = sum_x A_x B_x forced by each integer collision profile."""
    excess = s * t - (1 << (n - 1))
    if excess < 0:
        return []
    return sorted(
        {sum(j * (j + 1) // 2 for j in parts) // 2 for parts in odd_profiles(excess)}
    )


def _shapes(total_pairs, excess):
    """Multiplicity shapes: A_x values summing to total_pairs with support
    size total_pairs - excess (the excess parts carry the collisions)."""
    if excess > total_pairs:
        return
    for parts in _partitions(excess):
        yield tuple(sorted((1 + p for p in parts), reverse=True)) + (
            1,
        ) * (total_pairs - excess - len(parts))


def _draws(shape, shared):
    """All multisets of `shared` values drawn from a multiplicity shape."""
    if shared == 0:
        yield ()
        return
    counts = {}
    for v in shape:
        counts[v] = counts.get(v, 0) + 1
    vals = sorted(counts)
    limits = [counts[v] for v in vals]

    def rec(i, remaining, acc):
        if i == len(vals):
            if remaining == 0:
                yield tuple(acc)
            return
        for take in range(min(limits[i], remaining) + 1):
            yield from rec(i + 1, remaining - take, acc + [vals[i]] * take)

    yield from rec(0, shared, [])


def _pairing_sums(a_draw, b_draw):
    """All dot products sum a_i b_pi(i) over pairings of two draws."""
    if len(a_draw) <= 1:
        yield sum(x * y for x, y in zip(a_draw, b_draw))
        return
    a0 = a_draw[0]
    for i in range(len(b_draw)):
        rest = b_draw[:i] + b_draw[i + 1 :]
        for tail in _pairing_sums(a_draw[1:], rest):
            yield a0 * b_draw[i] + tail


def attainable_c(n, s, t, e_ex, b_ex):
    """Exact attainable values of sum_x A_x B_x on the shared support
    positions for one (e_ex, b_ex) row."""
    odd_masks = 1 << (n - 1)
    even_nonzero = odd_masks - 1
    A = s * (s - 1) // 2
    B = t * (t - 1) // 2
    shared = A + B - e_ex - b_ex - even_nonzero
    if shared < 0:
        return set()
    out = set()
    for sa in _shapes(A, e_ex):
        for sb in _shapes(B, b_ex):
            for da in _draws(sa, shared):
                for db in _draws(sb, shared):
                    out.update(_pairing_sums(da, db))
    return out


def sharp_rows(n, s, t):
    """Sharp pair-representation rows for one parity split.

    Returns {feasible, rows: [{e_ex, b_ex, shared, c}], best, need}: a row
    survives iff some integer collision profile's c is exactly attainable.
    `best` is the largest attainable c (PR 2542's closed-form comparison
    quantity), `need` = ceil((s*t - 2^(n-1))/2) the profile-level necessity.
    """
    odd_masks = 1 << (n - 1)
    even_nonzero = odd_masks - 1
    A = s * (s - 1) // 2
    B = t * (t - 1) // 2
    excess = s * t - odd_masks
    need = (excess + 1) // 2 if excess > 0 else 0
    rows = []
    best = -1
    if excess < 0 or A + B < even_nonzero:
        return dict(feasible=False, rows=[], best=best, need=need)
    c_vals = set(profile_c_values(n, s, t))
    for e_ex in range(A + 1):
        for b_ex in range(B + 1):
            shared = A + B - e_ex - b_ex - even_nonzero
            if shared < 0:
                continue
            attain = attainable_c(n, s, t, e_ex, b_ex)
            if not attain:
                continue
            best = max(best, max(attain))
            for c in sorted(attain & c_vals):
                rows.append(dict(e_ex=e_ex, b_ex=b_ex, shared=shared, c=c))
    return dict(feasible=bool(rows), rows=rows, best=best, need=need)


def surviving_rows(n, s, t, min_e_ex=0, min_b_ex=0):
    """Sharp rows filtered by census-implied minimum excesses (min excess of
    s-point sets resp. t-point sets in F2^(n-1))."""
    sharp = sharp_rows(n, s, t)
    rows = [
        r
        for r in sharp["rows"]
        if r["e_ex"] >= min_e_ex and r["b_ex"] >= min_b_ex
    ]
    return dict(
        feasible=bool(rows),
        rows=rows,
        best=sharp["best"],
        need=sharp["need"],
    )


# ------------------------------------------------------ coverage primitives


def coverage_mask(pts):
    """Bitmask of {a ^ b : a, b in pts} (self-pairs give mask 0)."""
    mask = 1  # zero via a = b
    for i in range(len(pts)):
        pi = pts[i]
        for j in range(i):
            mask |= 1 << (pi ^ pts[j])
    return mask


def coverage_mask_dual(pts):
    """Dual predicate (PR 2542's independent check): mask m is covered iff
    (pts xor m) meets pts."""
    pset = set(pts)
    limit = 1 << max(pts).bit_length() if pts else 1
    mask = 0
    for m in range(limit):
        if any((p ^ m) in pset for p in pts):
            mask |= 1 << m
    return mask


# --------------------------------------------------- exact small controls


@lru_cache(maxsize=None)
def brute_force_set_census(n, k):
    """Exact census of k-point sets S (0 in S, translation WLOG) over F2^n:
    returns (number of covering sets, max |S+S|).  Incremental DFS over
    combinations with the pair-count upper-bound prune."""
    N = 1 << n
    full_mask = (1 << N) - 1
    pairs_total = k * (k - 1) // 2
    state = {"covers": 0, "best": 0}

    sums = [0]
    masks = [1]  # stack of coverage masks

    def rec(next_pt, depth):
        size = depth + 1
        if size == k:
            mask = masks[-1]
            covered = mask.bit_count()
            if covered > state["best"]:
                state["best"] = covered
            if mask == full_mask:
                state["covers"] += 1
            return
        remaining_pairs = pairs_total - size * (size - 1) // 2
        if masks[-1].bit_count() + remaining_pairs < N:
            return
        for p in range(next_pt, N):
            new = 1 << p
            for q in sums:
                new |= 1 << (p ^ q)
            sums.append(p)
            masks.append(masks[-1] | new)
            rec(p + 1, depth + 1)
            masks.pop()
            sums.pop()

    rec(1, 0)
    return state["covers"], state["best"]
