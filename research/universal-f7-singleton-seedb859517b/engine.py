#!/usr/bin/env python3
"""Exact engine for the singleton universal source path problem (PR943 model).

A restored source word w over n labels has even label counts >= 2; its prefix
parity states are the vertices of a closed walk on the n-cube starting at 0;
paired readouts realize D(w) = {q_s xor q_t} = P + P for the prefix vertex set
P.  A word is universal iff P + P = F2^n.  f(n) is the minimum word length.

This module is standard library only and computes coverage with exact integer
bitmasks (one bit per element of F2^n; no floating point anywhere).
"""
from collections import Counter
from hashlib import sha256
from itertools import combinations

# ------------------------------------------------------------------ coverage


def prefixes(word):
    """Prefix parity states q_0..q_L of a word (list of label indices)."""
    out, q = [0], 0
    for j in word:
        q ^= 1 << j
        out.append(q)
    return out


def coverage_mask(points, n=None):
    """Bitmask of P + P = {a xor b : a, b in P} over F2^n."""
    if n is None:
        n = max(p.bit_length() for p in points) if points else 0
    size = 1 << n
    mask = 0
    pts = list(points)
    for i, a in enumerate(pts):
        for b in pts[i:]:
            mask |= 1 << (a ^ b)
    return mask & ((1 << size) - 1)


def coverage_size(word):
    """|D(w)| for a source word: pairwise XORs of its prefix states."""
    return word_coverage(word)


def word_coverage(word):
    return coverage_mask(prefixes(word)).bit_count()


def word_is_restored(word, n):
    counts = [0] * n
    for j in word:
        if not 0 <= j < n:
            return False
        counts[j] += 1
    return all(c > 0 and c % 2 == 0 for c in counts)


def word_is_universal(word, n):
    return word_is_restored(word, n) and word_coverage(word) == 1 << n


# --------------------------------------------------------------- construction


def gray_word(n):
    """Reflected-Gray construction: 2^ceil(n/2) + 2^floor(n/2) calls."""
    k = (n + 1) // 2

    def block(m, offset):
        if m == 0:
            return []
        g = [t ^ (t >> 1) for t in range(1 << m)]
        steps = []
        for t in range(1 << m):
            diff = g[t] ^ g[(t + 1) % (1 << m)]
            steps.append(offset + diff.bit_length() - 1)
        return steps

    return block(k, 0) + block(n - k, k)


# ------------------------------------------------------------------ word census


def restricted_growth_words(n, length):
    """Canonical restored words: labels in first-occurrence order.

    Every label used, every count even and at least two (forced by the
    parity/room feasibility test at the leaves).
    """
    word = [0] * length
    count = [0] * n

    def rec(i, used):
        odd = 0
        for j in range(used):
            odd += count[j] & 1
        if odd + 2 * (n - used) > length - i:
            return
        if i == length:
            yield tuple(word)
            return
        for j in range(min(used + 1, n)):
            word[i] = j
            count[j] += 1
            yield from rec(i + 1, used + 1 if j == used else used)
            count[j] -= 1

    yield from rec(0, 0)


def census_words(n, length):
    """Histogram, records SHA-256 and word count for all canonical words.

    Records are 'word:size' lines sorted and joined with newlines, matching
    the pinned research/universal-connector-six-source/EXPECTED.json format.
    """
    hist = Counter()
    records = []
    words = 0
    for word in restricted_growth_words(n, length):
        size = word_coverage(word)
        hist[size] += 1
        records.append("".join(map(str, word)) + ":" + str(size))
        words += 1
    digest = sha256("\n".join(sorted(records)).encode()).hexdigest()
    return hist, digest, words


# ------------------------------------------------------------ counting bounds


def counting_least_even_L(n):
    """Least even L with feasible prefix-parity split sizes at length L.

    Split sizes s = |E|, t = |O| obey s, t <= L/2, s*t >= 2^(n-1) (odd masks)
    and C(s,2) + C(t,2) >= 2^(n-1) - 1 (even nonzero masks).
    """
    odd_masks = 1 << (n - 1)
    even_nonzero = odd_masks - 1
    L = 2
    while True:
        half = L // 2
        for s in range(1, half + 1):
            for t in range(1, half + 1):
                if s * t >= odd_masks and s * (s - 1) // 2 + t * (t - 1) // 2 >= even_nonzero:
                    return L
        L += 2


def lemma_a_table(n, s, t):
    """Exact pair-representation rows for one parity split.

    A_x = #{e<e' in E : e+e' = x}, B_x similarly on the odd side.  Full
    coverage forces |S| = C(s,2) + C(t,2) - e_ex - b_ex - (2^(n-1) - 1) shared
    nonzero even values with S = supp(A) int supp(B), and the odd-side excess
    forces sum_x A_x B_x >= ceil((s*t - 2^(n-1))/2).  Since sum A_x B_x over S
    is at most |S| + e_ex + b_ex + e_ex*b_ex, every row that misses the bound
    is a contradiction.
    """
    odd_masks = 1 << (n - 1)
    even_nonzero = odd_masks - 1
    A = s * (s - 1) // 2
    B = t * (t - 1) // 2
    need = (s * t - odd_masks + 1) // 2  # ceil((st - odd)/2)
    rows = []
    if s * t < odd_masks or A + B < even_nonzero:
        rows.append(dict(e_ex=None, b_ex=None, shared=None, upper=None,
                         need=need, feasible=False, reason="counting"))
        return rows
    for e_ex in range(A + 1):
        for b_ex in range(B + 1):
            shared = A + B - e_ex - b_ex - even_nonzero
            if shared < 0:
                continue
            upper = shared + e_ex + b_ex + e_ex * b_ex
            rows.append(dict(e_ex=e_ex, b_ex=b_ex, shared=shared, upper=upper,
                             need=need, feasible=upper >= need, reason="identity"))
    return rows


def split_identity_feasible(n, s, t):
    return any(r["feasible"] for r in lemma_a_table(n, s, t))


def admissible_splits(n, length):
    """Parity splits that survive counting and the pair-representation identity."""
    half = length // 2
    out = []
    for s in range(1, half + 1):
        for t in range(1, half + 1):
            if split_identity_feasible(n, s, t) and _counting_ok(n, s, t):
                out.append((s, t))
    return sorted(set(out))


def _counting_ok(n, s, t):
    odd_masks = 1 << (n - 1)
    even_nonzero = odd_masks - 1
    return (s * t >= odd_masks
            and s * (s - 1) // 2 + t * (t - 1) // 2 >= even_nonzero)


def set_level_splits(n, size):
    """Parity splits of a size-point set that survive counting and identity."""
    out = []
    for s in range(1, size):
        t = size - s
        if _counting_ok(n, s, t) and split_identity_feasible(n, s, t):
            out.append((s, t))
    return sorted(set(out))


# --------------------------------------------------------------- set census


def normalized_set_census(n, k):
    """All k-point subsets of F2^n containing 0 (translation-normalized).

    Reports the number of sets, the maximum |P+P| and the number of full
    covers.  Exact integer computation; recursive growth with a running
    pair-sum mask.
    """
    total = (1 << n) - 1  # nonzero points to choose from
    max_cov = 0
    covers = 0
    sets = 0
    full = (1 << (1 << n)) - 1

    chosen = []

    def rec(start, support):
        nonlocal max_cov, covers, sets
        if len(chosen) == k - 1:
            sets += 1
            cov = support | 1  # zero mask always covered
            c = cov.bit_count()
            if c > max_cov:
                max_cov = c
            if cov == full:
                covers += 1
            return
        need = (k - 1) - len(chosen)
        for v in range(start, total + 2 - need):
            add = 1 << v  # 0 + v
            for u in chosen:
                add |= 1 << (u ^ v)
            chosen.append(v)
            rec(v + 1, support | add)
            chosen.pop()

    rec(1, 0)
    return dict(sets=sets, max_coverage=max_cov, covers=covers)


# ------------------------------------------------------------------ cycle


def hamiltonian_cycle(points, n):
    """A closed walk word through every point of P exactly once, or None.

    The word's step labels are the hypercube coordinates, so the result is a
    restored source word iff every label is used an even number of times (a
    closed walk forces even use automatically).
    """
    P = sorted(set(points))
    if len(P) != len(points) or 0 not in P:
        return None
    index = {v: i for i, v in enumerate(P)}
    size = len(P)
    neigh = []
    for v in P:
        ns = []
        for bit in range(n):
            w = v ^ (1 << bit)
            if w in index:
                ns.append((index[w], bit))
        neigh.append(ns)

    target = (1 << size) - 1
    path = [0]
    used = 1 << 0
    steps = []

    def dfs(cur):
        nonlocal used
        if used == target:
            for nb, bit in neigh[cur]:
                if nb == 0:
                    steps.append(bit)
                    return True
            return False
        for nb, bit in neigh[cur]:
            if nb == 0 or (used >> nb) & 1:
                continue
            used |= 1 << nb
            path.append(nb)
            steps.append(bit)
            if dfs(nb):
                return True
            steps.pop()
            path.pop()
            used ^= 1 << nb
        return False

    if dfs(0):
        return steps
    return None


def closed_walk_word(points, word):
    """Vertex sequence of the walk defined by word (sanity helper)."""
    return prefixes(word)


# --------------------------------------------------------------- joint search


def joint_covers(n, splits, require_min_degree=False, max_nodes=None, stats=None):
    """Exhaustive (E, O) covers of F2^n with the given parity split sizes.

    E subset even-weight vectors with 0 in E, O subset odd-weight vectors,
    increasing global order (each pair enumerated once); E + O must cover all
    odd masks and (E+E) u (O+O) all even nonzero masks.  Collision budgets and
    coverage-capacity bounds prune the tree.  If require_min_degree, sets whose
    induced hypercube graph has a vertex of degree < 2 are skipped (every word
    of minimal length walks a Hamiltonian cycle through its prefix set, so this
    preserves completeness for word exclusion).
    """
    odd_masks = 1 << (n - 1)
    even_nonzero = odd_masks - 1
    ALL_ODD = 0
    ALL_EVEN = 0
    for v in range(1 << n):
        if v & 1:
            ALL_ODD |= 1 << v
        elif v:
            ALL_EVEN |= 1 << v
    results = []
    nodes = [0]

    for (s, t) in splits:
        A = s * (s - 1) // 2
        B = t * (t - 1) // 2
        budget = A + B - even_nonzero  # e_ex + b_ex <= budget
        if budget < 0:
            continue
        E = [0]
        O = []
        state = dict(e_supp=0, o_supp=0, coll=0, c_odd=0, c_even=0)

        def rec(last):
            nodes[0] += 1
            if max_nodes is not None and nodes[0] > max_nodes:
                raise OverflowError("node cap reached")
            e, o = len(E), len(O)
            if e == s and o == t:
                st = state
                if (st["c_odd"] & ALL_ODD) == ALL_ODD and (st["c_even"] & ALL_EVEN) == ALL_EVEN:
                    if require_min_degree and not _min_degree_two(E + O, n):
                        return
                    results.append((tuple(E), tuple(O)))
                return
            st = state
            unc_odd = ALL_ODD & ~st["c_odd"]
            if unc_odd.bit_count() > s * t - e * o:
                return
            unc_even = ALL_EVEN & ~st["c_even"]
            rem_e = A - e * (e - 1) // 2
            rem_o = B - o * (o - 1) // 2
            if unc_even.bit_count() > rem_e + rem_o:
                return
            if e < s:
                for v in range(last + 1, (1 << n)):
                    if v & 1:
                        continue
                    add = 0
                    for u in E:
                        add |= 1 << (v ^ u)
                    nc = (add & st["e_supp"]).bit_count()
                    if st["coll"] + nc > budget:
                        continue
                    saved = (st["e_supp"], st["coll"], st["c_odd"], st["c_even"])
                    st["e_supp"] |= add
                    st["coll"] += nc
                    m = 0
                    for w in O:
                        m |= 1 << (v ^ w)
                    st["c_odd"] |= m
                    st["c_even"] |= add
                    E.append(v)
                    rec(v)
                    E.pop()
                    st["e_supp"], st["coll"], st["c_odd"], st["c_even"] = saved
            if o < t:
                for v in range(last + 1, (1 << n)):
                    if not (v & 1):
                        continue
                    add = 0
                    for u in O:
                        add |= 1 << (v ^ u)
                    nc = (add & st["o_supp"]).bit_count()
                    if st["coll"] + nc > budget:
                        continue
                    saved = (st["o_supp"], st["coll"], st["c_odd"], st["c_even"])
                    st["o_supp"] |= add
                    st["coll"] += nc
                    m = 0
                    for w in E:
                        m |= 1 << (v ^ w)
                    st["c_odd"] |= m
                    st["c_even"] |= add
                    O.append(v)
                    rec(v)
                    O.pop()
                    st["o_supp"], st["coll"], st["c_odd"], st["c_even"] = saved

        rec(0)
    if stats is not None:
        stats["nodes"] = nodes[0]
    return results


def _min_degree_two(P, n):
    S = set(P)
    for v in P:
        deg = 0
        for bit in range(n):
            if (v ^ (1 << bit)) in S:
                deg += 1
        if deg < 2:
            return False
    return True


# ------------------------------------------------------- cyclic word census


def rg_prefixes(n, depth):
    """Every restricted-growth prefix of given length over n labels.

    Shards of cyclic_census: every canonical word has exactly one of these as
    its length-`depth` prefix, so the subtrees partition the search space.
    """
    out = []

    def rec(i, used, acc):
        if i == depth:
            out.append(tuple(acc))
            return
        for j in range(min(used + 1, n)):
            acc.append(j)
            rec(i + 1, used + 1 if j == used else used, acc)
            acc.pop()

    rec(0, 0, [])
    return out


def cyclic_census(n, length, budget=None, simple=False, stop_on_first=False,
                  prefix=(), stats=None, max_nodes=None, collect_all=False):
    """Exhaustive canonical word census of length `length` at n sources.

    Restricted-growth words (complete under coordinate relabeling, which is a
    hypercube automorphism), labels in first-occurrence order, every label
    used with an even count >= 2.  Prunes: multiplicity room, self-avoidance
    when `simple` (the caller must justify |P| = length), and the
    pair-representation collision budget `budget` (e_ex + b_ex <= budget; the
    caller must justify it from the split identity).  `prefix` restricts the
    search to one shard subtree.  Returns dict(nodes, leaves, hits, words)
    where words lists universal witnesses (up to stop_on_first).
    """
    cap = max_nodes
    out = dict(nodes=0, leaves=0, hits=0, words=[])
    word = [0] * length
    count = [0] * n
    st = dict(q=0, seen=1, e_supp=0, o_supp=0, coll=0, used=0, odd=0)
    E = [0]
    O = []

    def rec(i):
        out["nodes"] += 1
        if cap is not None and out["nodes"] > cap:
            raise OverflowError("node cap reached")
        if i == length:
            if st["q"] != 0:
                return
            out["leaves"] += 1
            if collect_all:
                out.setdefault("all_words", []).append(tuple(word))
            pts = E + O
            cov = 0
            for a_i in range(len(pts)):
                a = pts[a_i]
                for b in pts[a_i:]:
                    cov |= 1 << (a ^ b)
            if cov.bit_count() == 1 << n:
                out["hits"] += 1
                out["words"].append(tuple(word))
            return
        if st["odd"] + 2 * (n - st["used"]) > length - i:
            return
        room = length - 2 * (n - 1)
        limit = min(st["used"] + 1, n)
        for j in range(limit):
            if count[j] >= room:
                continue
            if i < len(prefix) and j != prefix[i]:
                continue
            nq = st["q"] ^ (1 << j)
            closing = (i == length - 1 and nq == 0)
            if simple and not closing and (st["seen"] >> nq) & 1:
                continue
            if closing:
                newcoll = 0
                add = 0
            elif nq & 1:
                add = 0
                for u in O:
                    add |= 1 << (nq ^ u)
                newcoll = (add & st["o_supp"]).bit_count()
                if budget is not None and st["coll"] + newcoll > budget:
                    continue
            else:
                add = 0
                for u in E:
                    add |= 1 << (nq ^ u)
                newcoll = (add & st["e_supp"]).bit_count()
                if budget is not None and st["coll"] + newcoll > budget:
                    continue
            saved = (st["q"], st["seen"], st["e_supp"], st["o_supp"],
                     st["coll"], st["used"], st["odd"])
            word[i] = j
            count[j] += 1
            st["odd"] += 1 if (count[j] & 1) else -1
            st["q"] = nq
            if not closing:
                st["seen"] |= 1 << nq
                if nq & 1:
                    st["o_supp"] |= add
                    O.append(nq)
                else:
                    st["e_supp"] |= add
                    E.append(nq)
            st["coll"] += newcoll
            if j == st["used"]:
                st["used"] += 1
            rec(i + 1)
            if stop_on_first and out["hits"]:
                return
            (st["q"], st["seen"], st["e_supp"], st["o_supp"],
             st["coll"], st["used"], st["odd"]) = saved
            count[j] -= 1
            if not closing:
                (O if (nq & 1) else E).pop()

    rec(0)
    if stats is not None:
        stats.update(out)
    return out
