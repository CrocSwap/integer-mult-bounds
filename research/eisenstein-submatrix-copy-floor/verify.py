#!/usr/bin/env python3
"""Eisenstein E8 decoder copy floor C >= 23 by submatrix-minrank certificates.

Standard library only.  Reuses the frozen geometry of
research/eisenstein-clique-copy-bound (PR798) and checks:

1. every 7-clique, and the 540 sets S_uw = N[u] & N[w] (u, w distinct
   nonorthogonal lines; N[x] = x plus its 27 nonorthogonal neighbours);
2. minrank(S_uw) = 10: an exhaustive normalized search rules out every
   fitting rank-<=7 completion of the base pair's 18-line core, an explicit
   fitting rank-8 completion exists, and five pinned automorphisms of the
   nonorthogonality graph (AUTOMORPHISMS.json) are transitive on all 540
   nonorthogonal pairs, so every S_uw has the same minrank;
3. the rational weights 184/6835 (singletons), 13/13670 (7-cliques) and
   7/20505 (S_uw) satisfy sum_S w_S [S meets F][S meets G] <= c(F,G) on all
   296,321 unordered flat pairs with c >= 1 (of 298,378 unordered pairs);
4. objective 30200/1367 > 22, so every fitting decomposition costs >= 23;
5. rejection controls.
"""
import hashlib
import json
import pathlib
import sys
from fractions import Fraction

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
GEOM = ROOT / 'research' / 'eisenstein-clique-copy-bound'
sys.path.insert(0, str(GEOM))
import geometry as g  # noqa: E402  (frozen PR798 geometry, sha-pinned in SOURCES.json)

W_SINGLE = Fraction(184, 6835)
W_CLIQUE7 = Fraction(13, 13670)
W_S20 = Fraction(7, 20505)
CORE_RANK_EXCLUDED = 7


def require(cond, msg):
    if not cond:
        raise SystemExit('FAIL: ' + msg)


def pop(x):
    return bin(x).count('1')


def check_sources():
    spec = json.loads((HERE / 'SOURCES.json').read_text())
    for item in spec['files']:
        data = (ROOT / item['path']).read_bytes()
        require(hashlib.sha256(data).hexdigest() == item['sha256'], 'source pin ' + item['path'])


class Pattern:
    """Fitting pattern on 40 lines: diag 1, nonorthogonal off-diagonal 0, rest free."""

    def __init__(self, adjacent):
        self.adj = adjacent

    def entry(self, p, q):
        if p == q:
            return 1
        if self.adj[p] >> q & 1:
            return 0
        return None


def max_clique(adj, mask):
    best = []

    def ext(chosen, poss):
        nonlocal best
        if not poss:
            if len(chosen) > len(best):
                best = chosen[:]
            return
        if len(chosen) + pop(poss) <= len(best):
            return
        v = (poss & -poss).bit_length() - 1
        ext(chosen + [v], poss & adj[v] & ~((1 << (v + 1)) - 1))
        ext(chosen, poss & ~(1 << v))

    ext([], mask)
    return best


def completion_exists(pat, lines, rank):
    """Is there a fitting B on lines x lines with rank_F2(B) <= rank?

    Normalization (README, Lemma 2): with a clique Q in `lines`, B[Q,Q] = I, so
    any factorization B = U V^T with `rank` columns can be changed to
    U[Q] = V[Q] = [I_|Q| | 0].  Then for v outside Q, U[v] = (B[v,Q], s_v) and
    V[v] = (B[Q,v]^T, t_v) with s_v, t_v in F2^(rank-|Q|), and every entry of
    B between lines outside Q is x_v.y_w + s_v.t_w.  Entries between Q and the
    rest are the chosen x/y bits themselves, so the search enumerates exactly
    the fixed-entry-respecting choices.  Exhaustive backtracking.
    Returns a witness dict or None.
    """
    mask = sum(1 << v for v in lines)
    Q = max_clique(pat.adj, mask)
    q = len(Q)
    if rank < q:
        return None
    extra = rank - q
    rest = [v for v in lines if v not in Q]

    def choices(v, as_row):
        fixed = [pat.entry(v, c) if as_row else pat.entry(c, v) for c in Q]
        free = [i for i, f in enumerate(fixed) if f is None]
        base = sum((f or 0) << i for i, f in enumerate(fixed))
        out = []
        for bits_ in range(1 << len(free)):
            m = base
            for k, i in enumerate(free):
                if bits_ >> k & 1:
                    m |= 1 << i
            out.append(m)
        return out

    dom = {}
    for v in rest:
        opts = []
        for x in choices(v, True):
            for y in choices(v, False):
                for s in range(1 << extra):
                    for t in range(1 << extra):
                        if (pop(x & y) + pop(s & t)) % 2 == 1:  # diagonal = 1
                            opts.append((x, s, y, t))
        dom[v] = opts
    order = sorted(rest, key=lambda v: len(dom[v]))
    asg = {}

    def consistent(v, cand):
        x, s, y, t = cand
        for w, (xw, sw, yw, tw) in asg.items():
            e = pat.entry(v, w)
            if e is not None and (pop(x & yw) + pop(s & tw)) % 2 != e:
                return False
            e = pat.entry(w, v)
            if e is not None and (pop(xw & y) + pop(sw & t)) % 2 != e:
                return False
        return True

    def rec(i):
        if i == len(order):
            return True
        v = order[i]
        for cand in dom[v]:
            if consistent(v, cand):
                asg[v] = cand
                if rec(i + 1):
                    return True
                del asg[v]
        return False

    if not rec(0):
        return None
    return {'Q': Q, 'extra': extra, 'rows': dict(asg)}


def matrix_from_witness(pat, lines, wit):
    """Rebuild B from a normalized witness and check it fits and has the stated rank bound."""
    Q, extra = wit['Q'], wit['extra']
    U, V = {}, {}
    for i, c in enumerate(Q):
        U[c] = (1 << i, 0)
        V[c] = (1 << i, 0)
    for v, (x, s, y, t) in wit['rows'].items():
        U[v] = (x, s)
        V[v] = (y, t)
    B = {}
    for p in lines:
        for r in lines:
            val = (pop(U[p][0] & V[r][0]) + pop(U[p][1] & V[r][1])) % 2
            e = pat.entry(p, r)
            require(e is None or e == val, 'witness does not fit')
            B[(p, r)] = val
    rows = [sum(B[(p, r)] << j for j, r in enumerate(lines)) for p in lines]
    return f2_rank(rows)


def f2_rank(rows):
    rows = list(rows)
    rank = 0
    for bit in range(64):
        piv = next((i for i in range(rank, len(rows)) if rows[i] >> bit & 1), None)
        if piv is None:
            continue
        rows[rank], rows[piv] = rows[piv], rows[rank]
        for i in range(len(rows)):
            if i != rank and rows[i] >> bit & 1:
                rows[i] ^= rows[rank]
        rank += 1
    return rank


def s20_minrank_bound(pat, u, w, nclosed):
    """minrank(S_uw) >= 10: u, w are isolated (block I_2) and the 18-line core has no rank<=7 completion."""
    S = nclosed[u] & nclosed[w]
    lines = [v for v in range(40) if S >> v & 1]
    require(len(lines) == 20, 'S_uw size')
    iso = [v for v in lines if all(pat.entry(v, x) is not None for x in lines)]
    require(sorted(iso) == sorted([u, w]), 'S_uw isolated pair')
    core = [v for v in lines if v not in (u, w)]
    require(completion_exists(pat, core, CORE_RANK_EXCLUDED) is None,
            'core admits a rank-7 completion')
    return S, core


def replay(controls=True):
    check_sources()
    reps, images, adjacent, _pairs, _orbits = g.geometry()
    pat = Pattern(adjacent)
    nclosed = [adjacent[u] | (1 << u) for u in range(40)]
    flats = g.flats(reps, images)
    require(len(flats) == 772, 'flat count')
    masks = [m for m, _, _ in flats]
    bases = [b for _, b, _ in flats]

    cliques = g.all_cliques(adjacent)
    require(len(cliques) == 40054, 'clique count')
    c7 = [c for c in cliques if pop(c) == 7]
    require(len(c7) == 2880, '7-clique count')
    for c in c7:
        for v in range(40):
            if c >> v & 1:
                require(c & ~nclosed[v] == 0, '7-clique is a clique')

    pairs = [(u, w) for u in range(40) for w in range(u + 1, 40) if adjacent[u] >> w & 1]
    require(len(pairs) == 540, 'nonorthogonal pair count')
    aut = json.loads((HERE / 'AUTOMORPHISMS.json').read_text())
    base = tuple(aut['base_pair'])
    gens = aut['generators']
    for gperm in gens:
        require(is_automorphism(adjacent, gperm), 'generator is an automorphism')
    require(pair_orbit(gens, base) == set(pairs), 'generators are transitive on nonorthogonal pairs')
    # Exhaustive core search for the base pair only; automorphisms preserve the
    # fitting pattern, map N[x] to N[g x] and hence S_uw to S_(gu)(gw), so all
    # 540 sets have the same minrank (README, Lemma 3).
    _S, core = s20_minrank_bound(pat, base[0], base[1], nclosed)
    wit = completion_exists(pat, core, 8)
    require(wit is not None, 'rank-8 core completion exists')
    witness_rank = matrix_from_witness(pat, core, wit)
    require(witness_rank == 8, 'rank-8 witness has F2 rank 8')
    s20 = [nclosed[u] & nclosed[w] for u, w in pairs]
    require(len(set(s20)) == 540 and all(pop(x) == 20 for x in s20), 'distinct 20-line S_uw')

    costs = {}
    for i in range(len(masks)):
        for j in range(i, len(masks)):
            c = g.pairing_rank(bases[i], bases[j]) if bases[i] and bases[j] else 0
            if c:
                costs[(i, j)] = c

    # hit bitsets per flat
    def meet_bits(sets):
        return [sum(1 << k for k, s in enumerate(sets) if s & f) for f in masks]

    m7 = meet_bits(c7)
    m20 = meet_bits(s20)
    checked = tight = 0
    min_slack = None
    for (i, j), c in costs.items():
        lhs = (W_SINGLE * pop(masks[i] & masks[j]) + W_CLIQUE7 * pop(m7[i] & m7[j])
               + W_S20 * pop(m20[i] & m20[j]))
        slack = c - lhs
        require(slack >= 0, 'primal inequality at flats %d,%d' % (i, j))
        checked += 1
        tight += slack == 0
        min_slack = slack if min_slack is None else min(min_slack, slack)
    objective = W_SINGLE * 40 + W_CLIQUE7 * 7 * len(c7) + W_S20 * 10 * len(s20)
    require(objective == Fraction(30200, 1367), 'objective value')
    require(objective > 22, 'objective exceeds 22')
    floor = -(-objective.numerator // objective.denominator)
    require(floor == 23, 'integer floor')

    ncontrols = 0
    if controls:
        ncontrols = run_controls(pat, adjacent, nclosed, base, gens, c7, masks, costs, m7, m20)
    return {
        'flat_pairs_with_positive_cost': checked,
        'tight': tight,
        'cliques7': len(c7),
        's20_sets': len(s20),
        'core_rank8_witness_rank': witness_rank,
        'objective': str(objective),
        'copy_floor': floor,
        'controls': ncontrols,
    }


def run_controls(pat, adjacent, nclosed, base, gens, c7, masks, costs, m7, m20):
    n = 0
    # 1. The completion search is not vacuous: a 7-clique has no rank-6 completion
    #    and has a rank-7 one.
    clique = [v for v in range(40) if c7[0] >> v & 1]
    require(completion_exists(pat, clique, 6) is None, 'control: clique rank 6')
    require(completion_exists(pat, clique, 7) is not None, 'control: clique rank 7')
    n += 1
    # 2. A transposition of the two base lines composed with a generator is still checked:
    #    swapping two lines of different neighbourhoods is rejected as an automorphism.
    u, w = base
    x = next(v for v in range(40) if nclosed[v] != nclosed[u] and v != u)
    swap = list(range(40))
    swap[u], swap[x] = x, u
    require(not is_automorphism(adjacent, swap), 'control: non-automorphism rejected')
    n += 1
    # 3. Too few generators fail transitivity (the orbit check is not vacuous).
    require(pair_orbit(gens[:1], base) != pair_orbit(gens, base), 'control: one generator not transitive')
    n += 1
    # 4. Raising the S_uw weight by 1/20505 violates a primal inequality.
    bad = W_S20 + Fraction(1, 20505)
    require(any(W_SINGLE * pop(masks[i] & masks[j]) + W_CLIQUE7 * pop(m7[i] & m7[j])
                + bad * pop(m20[i] & m20[j]) > c for (i, j), c in costs.items()),
            'control: inflated S_uw weight is rejected')
    n += 1
    # 5. Without the S_uw sets the same singleton/clique weights total less than 22.
    require(W_SINGLE * 40 + W_CLIQUE7 * 7 * len(c7) < 22, 'control: cliques alone below 22')
    n += 1
    return n


def is_automorphism(adj, perm):
    if sorted(perm) != list(range(40)):
        return False
    return all((adj[perm[a]] >> perm[b] & 1) == (adj[a] >> b & 1)
               for a in range(40) for b in range(40))


def pair_orbit(gens, base):
    seen = {tuple(sorted(base))}
    stack = list(seen)
    while stack:
        a, b = stack.pop()
        for gp in gens:
            img = tuple(sorted((gp[a], gp[b])))
            if img not in seen:
                seen.add(img)
                stack.append(img)
    return seen


def main():
    result = replay(controls='--no-controls' not in sys.argv)
    expected = json.loads((HERE / 'RESULT.json').read_text()) if (HERE / 'RESULT.json').exists() else None
    if '--write' in sys.argv:
        (HERE / 'RESULT.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    elif expected is not None:
        require(expected == result, 'RESULT.json mismatch')
    print('PASS_EISENSTEIN_SUBMATRIX_COPY_FLOOR: C >= %d; objective %s; %d flat pairs; '
          '%d S_uw sets minrank 10; %d controls; no new kappa'
          % (result['copy_floor'], result['objective'], result['flat_pairs_with_positive_cost'],
             result['s20_sets'], result['controls']))


if __name__ == '__main__':
    main()
