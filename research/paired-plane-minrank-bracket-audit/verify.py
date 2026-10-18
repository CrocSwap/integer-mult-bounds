#!/usr/bin/env python3
"""Exact minimum scalar fitting rank (49) for PR1825's fixed 56 matched planes.

Independent stdlib re-implementation (no code imported from PR2471 or any
other package).  Default mode recomputes everything from the pinned sources and
compares with CERTIFICATE.json; ``--write-certificate`` regenerates it.

Prepared by thakrarsagar with substantial AI assistance from Claude
(Anthropic, Claude Opus 5.5).  Apache-2.0.
"""
import hashlib
import io
import itertools
import json
import sys
import tarfile
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVE = 'research/community-frontier1094-audit/selected-replay.tar.gz'
ARCHIVE_SHA = 'f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6'
MEMBER = 'candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json'
MEMBER_SHA = 'c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa'
MATCHING = 'research/paired-plane-scalar-mask-obstruction/PR1825-CERTIFICATE.json'
MATCHING_SHA = '4fd648f7b5178bff5441bf364d58234b7bc1a43b924bc6da03013c948f1473b1'
CERT = HERE / 'CERTIFICATE.json'

# PR2471 (ywz65) witnesses, copied verbatim from
# research/paired-plane-scalar-rank-floor/CERTIFICATE.json at PR head
# 5a7c2b681b79d5b5e25fac62aa4bad908525b5ca (git blob
# 1d8a21f3713f2b883ae65d655126732e4f5d54ff); re-checked here, not trusted.
PR2471_CLIQUE = [2, 6, 8, 17, 18, 19, 21, 22, 24, 28, 29, 34, 35, 36, 38, 39,
                 41, 42, 43, 45, 46, 51, 52, 53]
PR2471_CLASSES = [[0, 1, 2], [6, 13], [5, 8, 9], [17, 40], [3, 18, 25],
                  [19, 50], [21, 44], [20, 22], [10, 24, 30], [28, 31],
                  [11, 29], [16, 34, 54], [23, 35], [36], [15, 38],
                  [14, 33, 39], [27, 41], [42, 55], [43, 47], [45],
                  [12, 46, 48], [26, 49, 51], [52], [32, 37, 53], [4, 7]]


class CheckFailure(Exception):
    pass


def need(ok, why):
    if not ok:
        raise CheckFailure(why)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def parity_dot(x, y):
    return bin(x & y).count('1') % 2


# ---------------------------------------------------------------- model
def load_model(archive_bytes, matching_bytes):
    """Return (labels[112], pairs[56], orth[56][56]) from the pinned sources.
    orth[i][j] is True iff i != j and all four basis pairings vanish."""
    need(sha(archive_bytes) == ARCHIVE_SHA, 'archive sha256 mismatch')
    need(sha(matching_bytes) == MATCHING_SHA, 'PR1825 certificate sha256 mismatch')
    with tarfile.open(fileobj=io.BytesIO(archive_bytes), mode='r:gz') as tar:
        handle = tar.extractfile(MEMBER)
        need(handle is not None, 'archive member missing')
        member = handle.read()
    need(sha(member) == MEMBER_SHA, 'DATA-PHASES member sha256 mismatch')
    by_port = {}
    for row in json.loads(member)['recipes']:
        need(row['port'] not in by_port, 'duplicate port')
        by_port[row['port']] = row['q']
    need(sorted(by_port) == list(range(112)), 'ports must be 0..111')
    labels = [by_port[p] for p in range(112)]
    need(all(0 < q < 512 for q in labels) and len(set(labels)) == 112, 'labels: distinct, nonzero, in F2^9')
    pairs = [list(p) for p in json.loads(matching_bytes)['matching']]
    need(len(pairs) == 56 and sorted(x for p in pairs for x in p) == list(range(112)),
         'matching must partition the 112 ports into 56 pairs')
    for a, b in pairs:
        need(parity_dot(labels[a], labels[a]) == 1 and parity_dot(labels[b], labels[b]) == 1
             and parity_dot(labels[a], labels[b]) == 0, 'matched plane must have Gram I2')
    basis = [(labels[a], labels[b]) for a, b in pairs]
    orth = [[i != j and all(parity_dot(x, y) == 0 for x in basis[i] for y in basis[j])
             for j in range(56)] for i in range(56)]
    return labels, pairs, orth


def orthogonal_sets(orth):
    """All nonempty sets of pairwise orthogonal distinct planes (independent sets of G)."""
    n = len(orth)
    out = [(v,) for v in range(n)]
    layer = list(out)
    while layer:
        grown = [s + (j,) for s in layer for j in range(s[-1] + 1, n) if all(orth[t][j] for t in s)]
        out.extend(grown)
        layer = grown
    return out


# ------------------------------------------------- exact path-order DPs
def frontiers(order, nbrs):
    pos = {v: i for i, v in enumerate(order)}
    return [[u for u in order[i:] if any(pos[w] < i for w in nbrs[u])]
            for i in range(len(order) + 1)], pos


def clique_number_dp(orth, order):
    """Exact clique number of G (planes adjacent iff non-orthogonal) = independence
    number of the orthogonality graph, with the count of maximum cliques; DP along
    a vertex order whose state is the set of blocked frontier vertices."""
    n = len(orth)
    nbrs = [set(j for j in range(n) if orth[i][j]) for i in range(n)]
    fr, _ = frontiers(order, nbrs)
    memo = {}

    def rec(i, blocked):
        if i == n:
            return {0: 1}
        key = (i, blocked)
        if key in memo:
            return memo[key]
        v = order[i]
        keep = set(fr[i + 1])
        res = dict(rec(i + 1, frozenset(u for u in blocked if u in keep)))
        if v not in blocked:
            for k, c in rec(i + 1, frozenset(u for u in (blocked | nbrs[v]) if u in keep)).items():
                res[k + 1] = res.get(k + 1, 0) + c
        memo[key] = res
        return res

    counts = rec(0, frozenset())
    top = max(counts)
    return top, counts[top], len(memo)


def b_fold_savings_dp(orth, order, b):
    """Exact b-fold chromatic number of G: choose a multiset of orthogonal sets of
    size >= 2, each plane in at most b of them, maximising sum(|S|-1); then
    chi_b(G) = b*n - max savings (remaining slots are singleton classes)."""
    n = len(orth)
    nbrs = [set(j for j in range(n) if orth[i][j]) for i in range(n)]
    fr, pos = frontiers(order, nbrs)
    own = [[] for _ in range(n)]
    for s in orthogonal_sets(orth):
        if len(s) >= 2:
            ordered = tuple(sorted(s, key=lambda v: pos[v]))
            own[pos[ordered[0]]].append(ordered)
    memo = {}

    def options(i, state):
        caps = dict(zip(fr[i], state))
        nxt = fr[i + 1]
        opts = own[i]
        out = []

        def walk(k, left, cur, gain):
            if k == len(opts):
                out.append((gain, tuple(cur.get(u, b) for u in nxt)))
                return
            s = opts[k]
            for m in range(min([left] + [cur.get(u, b) for u in s[1:]]) + 1):
                cur2 = cur
                if m:
                    cur2 = dict(cur)
                    for u in s[1:]:
                        cur2[u] = cur.get(u, b) - m
                walk(k + 1, left - m, cur2, gain + m * (len(s) - 1))
        walk(0, caps.get(order[i], b), caps, 0)
        return out

    def rec(i, state):
        if i == n:
            return 0
        key = (i, state)
        got = memo.get(key)
        if got is None:
            got = max(g + rec(i + 1, ns) for g, ns in options(i, state))
            memo[key] = got
        return got

    return rec(0, ()), len(memo)


# ------------------------------------------------------------ checks
def owner_map(pairs):
    return {p: k for k, pr in enumerate(pairs) for p in pr}


def check_fitting_supports(supports, pairs, orth):
    """K = sum_S 1_S 1_S^T fits the strict mask iff the supports partition the
    ports and every support joins only ports of distinct pairwise orthogonal planes."""
    owner = owner_map(pairs)
    need(sorted(p for s in supports for p in s) == list(range(112)), 'supports must partition the 112 ports')
    need(all(s for s in supports), 'supports must be nonempty')
    for s in supports:
        for a in s:
            for c in s:
                need(a == c or orth[owner[a]][owner[c]],
                     'support joins ports %d,%d of non-orthogonal or equal planes' % (a, c))
    return len(supports)


def dense_from_supports(supports):
    k = [[0] * 112 for _ in range(112)]
    for s in supports:
        for a in s:
            for c in s:
                k[a][c] += 1
    return k


def check_mask_entries(matrix, pairs, orth):
    owner = owner_map(pairs)
    required = 0
    for i in range(112):
        for j in range(112):
            if i == j or not orth[owner[i]][owner[j]]:
                need(matrix[i][j] == int(i == j), 'mask entry violated at %d,%d' % (i, j))
                required += 1
    return required


def rank_mod_p(matrix, p):
    m = [[x % p for x in row] for row in matrix]
    rank = 0
    for c in range(len(m[0])):
        piv = next((r for r in range(rank, len(m)) if m[r][c]), None)
        if piv is None:
            continue
        m[rank], m[piv] = m[piv], m[rank]
        inv = pow(m[rank][c], p - 2, p)
        m[rank] = [x * inv % p for x in m[rank]]
        for r in range(len(m)):
            if r != rank and m[r][c]:
                f = m[r][c]
                m[r] = [(x - f * z) % p for x, z in zip(m[r], m[rank])]
        rank += 1
    return rank


def check_fractional(sets, y, x, n):
    """y: fractional clique of G (every orthogonal set has y-weight <= 1);
    x: fractional colouring (weights on orthogonal sets covering each plane >= 1)."""
    need(len(y) == n and all(w >= 0 for w in y), 'y must be nonnegative on all planes')
    for s in sets:
        need(sum(y[v] for v in s) <= 1, 'fractional clique violated on %s' % (s,))
    allowed = set(sets)
    cover = [Fraction(0)] * n
    for s, w in x:
        need(tuple(s) in allowed and w > 0, 'x must use orthogonal sets with positive weight')
        for v in s:
            cover[v] += w
    need(all(c >= 1 for c in cover), 'fractional colouring must cover every plane')
    return sum(y), sum(w for _, w in x)


def lower_bound_premises(core, clique22, orth):
    """Premises of the rank lower bound (README, Lemma + Theorem): core = (P0..P4) is
    an induced 5-cycle of the orthogonality graph; clique22 is a set of planes that
    are pairwise non-orthogonal and non-orthogonal to all five core planes."""
    need(len(core) == 5 and len(set(core)) == 5, 'core must be 5 distinct planes')
    for i in range(5):
        for j in range(i + 1, 5):
            need(orth[core[i]][core[j]] == ((j - i) % 5 in (1, 4)),
                 'core is not an induced 5-cycle at %d,%d' % (core[i], core[j]))
    need(len(set(clique22)) == len(clique22) and not set(clique22) & set(core), 'Q distinct, disjoint from core')
    for a in clique22:
        for c in clique22:
            need(a == c or not orth[a][c], 'Q not pairwise non-orthogonal at %d,%d' % (a, c))
        for c in core:
            need(not orth[a][c], 'Q plane %d orthogonal to core plane %d' % (a, c))
    return 2 * len(clique22) + 5


def c5_rank4_search(p, relax_13=False):
    """Finite corroboration of the C5 lemma over GF(p) (not needed by the proof):
    search for a rank-4 factorisation K=UV^T of the 10-port C5 blow-up mask after
    the WLOG normalisation u=v=e1..e4 on the ports of P0 (A) and P2 (C).  Returns
    1 if a completion exists, else 0 (exhaustive).  relax_13 makes P1-P3 entries
    free (control: a completion must then exist)."""
    vecs = list(itertools.product(range(p), repeat=4))
    e = [tuple(int(i == j) for j in range(4)) for i in range(4)]
    plane = {'A1': 0, 'A2': 0, 'C1': 2, 'C2': 2, 'B1': 1, 'B2': 1, 'D1': 3, 'D2': 3, 'E1': 4, 'E2': 4}
    placed = {'A1': (e[0], e[0]), 'A2': (e[1], e[1]), 'C1': (e[2], e[2]), 'C2': (e[3], e[3])}

    def ip(a, c):
        return sum(s * t for s, t in zip(a, c)) % p

    def free(x, z):
        a, c = plane[x], plane[z]
        if a == c:
            return False
        if relax_13 and {a, c} == {1, 3}:
            return True
        return (a - c) % 5 in (1, 4)
    todo = ['D1', 'D2', 'E1', 'E2', 'B1', 'B2']

    def rec(k):
        if k == len(todo):
            return True
        name = todo[k]
        for u in vecs:
            if any(not free(name, o) and ip(u, placed[o][1]) for o in placed):
                continue
            for v in vecs:
                if ip(u, v) != 1 or any(not free(o, name) and ip(placed[o][0], v) for o in placed):
                    continue
                placed[name] = (u, v)
                if rec(k + 1):
                    return True
                del placed[name]
        return False
    return int(rec(0))


# ------------------------------------------------------------- build
def exact_lp(orth):
    """Exact Bland-rule simplex for max sum y s.t. y(S) <= 1 for every orthogonal set S.
    The primal is the fractional clique y; the returned x is the dual (fractional
    colouring) read from reduced costs."""
    sets = orthogonal_sets(orth)
    n, m = len(orth), len(sets)
    rows = []
    for r, s in enumerate(sets):
        row = [Fraction(0)] * (n + m + 1)
        for v in s:
            row[v] = Fraction(1)
        row[n + r] = row[-1] = Fraction(1)
        rows.append(row)
    obj = [Fraction(-1)] * n + [Fraction(0)] * (m + 1)
    basis = [n + r for r in range(m)]
    while True:
        col = next((j for j in range(n + m) if obj[j] < 0), None)
        if col is None:
            break
        best = None
        for r in range(m):
            if rows[r][col] > 0:
                ratio = rows[r][-1] / rows[r][col]
                if best is None or ratio < best[0] or (ratio == best[0] and basis[r] < basis[best[1]]):
                    best = (ratio, r)
        r = best[1]
        a = rows[r][col]
        rows[r] = [z / a for z in rows[r]]
        nz = [j for j, z in enumerate(rows[r]) if z]
        for rr in range(m):
            if rr != r and rows[rr][col]:
                f = rows[rr][col]
                for j in nz:
                    rows[rr][j] -= f * rows[r][j]
        f = obj[col]
        for j in nz:
            obj[j] -= f * rows[r][j]
        basis[r] = col
    y = [Fraction(0)] * n
    for r, bcol in enumerate(basis):
        if bcol < n:
            y[bcol] = rows[r][-1]
    x = [(list(s), obj[n + r]) for r, s in enumerate(sets) if obj[n + r]]
    return y, x


def supports_from_half_integral(x, pairs):
    classes = []
    for s, w in x:
        need((2 * w).denominator == 1, 'fractional colouring (LP dual) not half-integral')
        classes.extend([list(s)] * int(2 * w))
    used = [0] * len(pairs)
    supports = []
    for s in classes:
        sup = []
        for v in s:
            if used[v] < 2:
                sup.append(pairs[v][used[v]])
                used[v] += 1
        if sup:
            supports.append(sorted(sup))
    return supports


def max_clique_simple(cands, orth):
    best = []

    def rec(chosen, pool):
        nonlocal best
        if len(chosen) + len(pool) <= len(best):
            return
        if not pool:
            best = chosen[:]
            return
        v = pool[0]
        rec(chosen + [v], [u for u in pool[1:] if not orth[v][u]])
        rec(chosen, pool[1:])
    rec([], sorted(cands))
    return best


def find_core(orth):
    """Induced 5-cycles of the orthogonality graph, each with a maximum clique of G
    inside the common non-orthogonal neighbourhood; return the best."""
    n = len(orth)
    nb = [set(j for j in range(n) if orth[i][j]) for i in range(n)]
    best = None
    for a in range(n):
        for b in sorted(nb[a]):
            for c in sorted(nb[b] - nb[a] - {a}):
                for d in sorted(nb[c] - nb[a] - nb[b] - {a, b}):
                    for e in sorted(nb[d] - nb[b] - nb[c] - {a, b, c}):
                        if a not in nb[e] or a != min(a, b, c, d, e) or b > e:
                            continue
                        cyc = (a, b, c, d, e)
                        common = [v for v in range(n) if v not in cyc and all(not orth[v][z] for z in cyc)]
                        q = max_clique_simple(common, orth)
                        if best is None or len(q) > len(best[1]):
                            best = (list(cyc), sorted(q))
    return best


def greedy_order(orth):
    n = len(orth)
    nbrs = [set(j for j in range(n) if orth[i][j]) for i in range(n)]
    best = None
    for start in range(n):
        order, placed, rest = [start], {start}, set(range(n)) - {start}
        while rest:
            def key(u):
                fr = set(w for z in placed | {u} for w in nbrs[z] if w not in placed and w != u)
                return (len(fr), -len(nbrs[u] & placed), u)
            u = min(rest, key=key)
            order.append(u)
            placed.add(u)
            rest.remove(u)
        width = max(len(f) for f in frontiers(order, nbrs)[0])
        if best is None or width < best[0]:
            best = (width, order)
    return best[1]


# ------------------------------------------------------------- main
def run_checks(cert, pairs, orth):
    n = 56
    sets = orthogonal_sets(orth)
    sizes = {}
    for s in sets:
        sizes[str(len(s))] = sizes.get(str(len(s)), 0) + 1
    out = {'orthogonal_set_counts_by_size': sizes,
           'nonorthogonal_plane_pairs': sum(1 for i in range(n) for j in range(i + 1, n) if not orth[i][j])}
    # PR2471 witnesses, re-checked against the independent reconstruction
    need(len(set(PR2471_CLIQUE)) == 24 and all(not orth[a][c] for a in PR2471_CLIQUE
                                               for c in PR2471_CLIQUE if a != c), 'PR2471 clique')
    need(len(PR2471_CLASSES) == 25 and sorted(v for c in PR2471_CLASSES for v in c) == list(range(n)),
         'PR2471 classes must partition the planes')
    pr_supports = [[pairs[v][slot] for v in cl] for cl in PR2471_CLASSES for slot in (0, 1)]
    check_fitting_supports(pr_supports, pairs, orth)
    out['pr2471_witnesses_rechecked'] = {'plane_clique_24_pairwise_nonorthogonal': True,
                                         'orthogonal_classes_25_rank50_fit': True}
    order = cert['dp_vertex_order']
    need(sorted(order) == list(range(n)), 'order must be a permutation')
    omega, count, states = clique_number_dp(orth, order)
    out['omega'] = {'value': omega, 'maximum_clique_count': count, 'dp_states': states}
    save1, states1 = b_fold_savings_dp(orth, order, 1)
    out['chi'] = {'value': n - save1, 'max_savings_b1': save1, 'dp_states': states1}
    y = [Fraction(w) for w in cert['fractional_clique_y']]
    x = [(s, Fraction(w)) for s, w in cert['fractional_colouring_x']]
    ysum, xsum = check_fractional(sets, y, x, n)
    need(ysum == xsum, 'LP certificates must meet')
    out['chi_f'] = str(ysum)
    supports = cert['rank49_supports']
    count49 = check_fitting_supports(supports, pairs, orth)
    dense = dense_from_supports(supports)
    required = check_mask_entries(dense, pairs, orth)
    reps = [s[0] for s in supports]
    need(all(dense[a][c] == int(a == c) for a in reps for c in reps), 'representatives must give identity')
    out['rank49_fit'] = {'supports': count49, 'required_entries_checked': required,
                         'rank_mod_2': rank_mod_p(dense, 2), 'rank_mod_3': rank_mod_p(dense, 3),
                         'rank_mod_101': rank_mod_p(dense, 101)}
    out['rank_lower_bound'] = lower_bound_premises(cert['c5_core'], cert['clique22'], orth)
    y_alt = [Fraction(1) if v in cert['clique22'] else Fraction(1, 2) if v in cert['c5_core'] else Fraction(0)
             for v in range(n)]
    out['lower_bound_fractional_clique_sum'] = str(check_fractional(sets, y_alt, x, n)[0])
    out['solver_controls'] = solver_controls()
    out['c5_lemma_finite_corroboration'] = {
        'gf2_rank4_completion_exists': c5_rank4_search(2),
        'gf3_rank4_completion_exists': c5_rank4_search(3),
        'gf2_control_P1P3_freed_completion_exists': c5_rank4_search(2, relax_13=True)}
    return out


def cycle_orth(k):
    return [[(i - j) % k in (1, k - 1) for j in range(k)] for i in range(k)]


def solver_controls():
    """Known answers for the two DPs: if the orthogonality graph is the cycle C_k
    (k odd), G is its complement, omega(G)=alpha(C_k)=(k-1)/2, chi(G)=(k+1)/2 and
    chi_2(G)=k.  A DP that ignored constraints or capacities would miss these."""
    out = {}
    for k in (5, 7):
        orth = cycle_orth(k)
        order = list(range(k))
        omega = clique_number_dp(orth, order)[0]
        chi = k - b_fold_savings_dp(orth, order, 1)[0]
        chi2 = 2 * k - b_fold_savings_dp(orth, order, 2)[0]
        need((omega, chi, chi2) == ((k - 1) // 2, (k + 1) // 2, k), 'DP control failed on C%d' % k)
        out['C%d' % k] = [omega, chi, chi2]
    return out


def negative_controls(cert, pairs, orth, archive_bytes, matching_bytes):
    results = {}

    def expect_fail(name, fn):
        try:
            fn()
        except CheckFailure as exc:
            results[name] = 'rejected: ' + str(exc)
            return
        raise SystemExit('NEGATIVE CONTROL ACCEPTED: ' + name)
    bad = bytearray(matching_bytes)
    bad[len(bad) // 2] ^= 1
    expect_fail('tampered_PR1825_certificate_byte', lambda: load_model(archive_bytes, bytes(bad)))
    merged = [c[:] for c in PR2471_CLASSES]
    merged[13] = merged[13] + merged.pop(19)  # [36] + [45]: a 24-class plane partition
    expect_fail('pr2471_classes_merged_to_24', lambda: check_fitting_supports(
        [[pairs[v][s] for v in cl] for cl in merged for s in (0, 1)], pairs, orth))
    sup = [s[:] for s in cert['rank49_supports']]
    owner = owner_map(pairs)
    port = sup[0][0]
    partner = [q for q in pairs[owner[port]] if q != port][0]
    src = next(k for k, s in enumerate(sup) if partner in s)
    sup[src].remove(partner)
    sup[0].append(partner)
    sup = [s for s in sup if s]
    expect_fail('rank_fit_both_ports_of_one_plane_in_one_support',
                lambda: check_fitting_supports(sup, pairs, orth))
    sets = orthogonal_sets(orth)
    y = [Fraction(w) for w in cert['fractional_clique_y']]
    k = next(i for i, w in enumerate(y) if w == Fraction(1, 2))
    y2 = y[:]
    y2[k] = Fraction(1)
    x = [(s, Fraction(w)) for s, w in cert['fractional_colouring_x']]
    expect_fail('fractional_clique_half_weight_raised_to_1', lambda: check_fractional(sets, y2, x, 56))
    x2 = x[:-1]
    expect_fail('fractional_colouring_set_dropped', lambda: check_fractional(sets, y, x2, 56))
    swap = next(v for v in range(56) if v not in cert['clique22'] and v not in cert['c5_core']
                and any(orth[v][c] for c in cert['c5_core']))
    # This substitution breaks Q's pairwise non-orthogonality (it is rejected by the Q-clique check).
    expect_fail('Q_plane_replaced_breaks_Q_clique',
                lambda: lower_bound_premises(cert['c5_core'], cert['clique22'][:-1] + [swap], orth))
    # Isolate the Q x core branch: drop one Q plane and add a plane that keeps Q pairwise
    # non-orthogonal but is orthogonal to some core plane.
    q, core = cert['clique22'], cert['c5_core']
    drop, add = next((d, v) for d in q for v in range(56)
                     if v not in q and v not in core
                     and all(not orth[v][u] for u in q if u != d)
                     and any(orth[v][c] for c in core))
    expect_fail('Q_plane_swapped_keeps_clique_but_orthogonal_to_core',
                lambda: lower_bound_premises(core, [u for u in q if u != drop] + [add], orth))
    core = cert['c5_core']
    expect_fail('core_reordered_not_a_cycle',
                lambda: lower_bound_premises([core[0], core[2], core[1], core[3], core[4]], cert['clique22'], orth))
    return results


def result_block(checks):
    need(checks['omega']['value'] == 24 and checks['chi']['value'] == 25, 'omega/chi')
    need(checks['chi_f'] == '49/2', 'chi_f')
    need(checks['rank49_fit']['supports'] == 49 and checks['rank49_fit']['rank_mod_2'] == 49
         and checks['rank49_fit']['rank_mod_3'] == 49, 'rank-49 fit')
    need(checks['rank_lower_bound'] == 49 and checks['lower_bound_fractional_clique_sum'] == '49/2', 'lower bound')
    c5 = checks['c5_lemma_finite_corroboration']
    need(c5['gf2_rank4_completion_exists'] == 0 and c5['gf3_rank4_completion_exists'] == 0
         and c5['gf2_control_P1P3_freed_completion_exists'] == 1, 'C5 corroboration')
    return {'omega_G': 24, 'chi_G': 25, 'fractional_chi_G': '49/2', 'two_fold_chi_G': 49,
            'min_scalar_fitting_rank': 49,
            'field_scope': 'every field: lower bound by the C5 lemma proof in README, upper bound by an explicit 0/1 '
                           'disjoint-support matrix; finite corroboration of the lemma over GF(2) and GF(3) only'}


def main(argv):
    archive_bytes = (ROOT / ARCHIVE).read_bytes()
    matching_bytes = (ROOT / MATCHING).read_bytes()
    _, pairs, orth = load_model(archive_bytes, matching_bytes)
    if '--two-fold-dp' in argv:
        # Optional supplementary cross-check (about 72-81 s, about 0.8 GB peak RSS):
        # exact chi_2 by the capacity-2 DP, independent of the LP certificate.
        cert = json.loads(CERT.read_text(encoding='utf-8'))
        save2, states2 = b_fold_savings_dp(orth, cert['dp_vertex_order'], 2)
        print(json.dumps({'max_savings_b2': save2, 'chi_2': 112 - save2, 'dp_states': states2}))
        need(112 - save2 == 49, 'two-fold DP disagrees with chi_2 = 49')
        print('PASS_TWO_FOLD_DP_CHI2_49')
        return 0
    if '--write-certificate' in argv:
        order = greedy_order(orth)
        y, x = exact_lp(orth)
        core, clique22 = find_core(orth)
        cert = {
            'schema_version': 1,
            'object': 'PR1825 fixed 56 matched planes, strict PR1889 scalar mask (as stated in PR2471)',
            'sources': {ARCHIVE: ARCHIVE_SHA, ARCHIVE + '#' + MEMBER: MEMBER_SHA, MATCHING: MATCHING_SHA},
            'dp_vertex_order': order,
            'fractional_clique_y': [str(w) for w in y],
            'fractional_colouring_x': [[s, str(w)] for s, w in x],
            'rank49_supports': supports_from_half_integral(x, pairs),
            'c5_core': core,
            'clique22': clique22,
        }
        cert['checks'] = run_checks(cert, pairs, orth)
        cert['negative_controls'] = negative_controls(cert, pairs, orth, archive_bytes, matching_bytes)
        cert['result'] = result_block(cert['checks'])
        CERT.write_text(json.dumps(cert, indent=1, sort_keys=True) + '\n', encoding='utf-8')
        print('wrote', CERT)
        return 0
    cert = json.loads(CERT.read_text(encoding='utf-8'))
    checks = run_checks(cert, pairs, orth)
    need(checks == cert['checks'], 'recomputed checks differ from CERTIFICATE.json')
    controls = negative_controls(cert, pairs, orth, archive_bytes, matching_bytes)
    need(controls == cert['negative_controls'], 'negative-control record differs from CERTIFICATE.json')
    need(result_block(checks) == cert['result'], 'result block differs')
    print(json.dumps(cert['result'], sort_keys=True))
    print('PASS_PAIRED_PLANE_MINRANK_EXACT_49')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except CheckFailure as exc:
        print('FAIL:', exc)
        sys.exit(1)
