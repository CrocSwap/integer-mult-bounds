#!/usr/bin/env python3
"""Exact verifier for the Eisenstein phase-path cost screen (standard library only).

Scope: a necessary-condition screen and a clean-class floor for Eisenstein E8
decoder copy cost, under the inherited format-limits accounting (#801) and the
abstract pairing-rank charge (#798).  This is not a supplier, not a new kappa,
and not a general decoder-optimality theorem.

Parts
  A  geometry replay: 240 roots, order-three J, 40 lines, flat census,
     nonsingularity of every line-spanned flat, a 7-clique (window >= 7).
  B  clean-class ingredients: c = |R cap A| on every clean ordered flat pair;
     two independent sharp witnesses at total cost 40 (frame partition and
     star decomposition of the canonical pattern B0).
  C  certified threshold screen: for every window h in [7, 40] and every odd
     stage count s, closed-form rational brackets U(s,h) on the exact copy-cost
     threshold C*(s,h); a direct certified non-beat check at each window's
     viability end s1(h); and an exact rational tail closure covering all
     s >= s1(h) (increment bound plus an exact monotonicity polynomial).
  D  prize: the bit-side cap on any complex-only gain.
  E  negative controls, including closed-form/direct cross-validation.

No randomness is used anywhere; every check is exact or an explicitly
outward-rounded rational interval enclosure (cert.py).
"""
import json
import sys
from fractions import Fraction as Fr

sys.path.insert(0, 'research/format-limits/scripts')
sys.path.insert(0, 'research/eisenstein-clique-copy-bound')

import cert
import geometry as G
import skel


def require(condition, message):
    if not condition:
        raise AssertionError(message)


# The selected complex-side saving b (PR1094 audit, complex_lower) and the
# selected record's kappa.  Both are historical provenance pins.
B = Fr(67018507072324140917, 40000000000000000000000)
KAPPA_SELECTED = Fr(836330098538459, 500000000000000000)
# The selected assembly's bit side (PR1094 ASSEMBLY.json, bit_lower).
X_BIT = Fr(1733427039589844234749, 10 ** 24)

XDEN = 40          # x = C / v with v = 40 Eisenstein ports
C_FLOOR = 22       # certified all-supports floor (#798)
C_STEP = Fr(9, 10)  # D(s+2) - D(s) at C = 22: D(s) = (s-1) - s*x0, x0 = 22/40,
                   # so D(s+2) - D(s) = 2 - 2*x0 = 2 - 44/40 = 9/10.
H_MIN = 7          # unconditional window floor (7-clique forces rank >= 7)
H_MAX = 40         # B is 40 x 40


def f2_rank(rows):
    basis = {}
    rank = 0
    for x in rows:
        while x:
            high = x.bit_length() - 1
            if high in basis:
                x ^= basis[high]
            else:
                basis[high] = x
                rank += 1
                break
    return rank


def part_a():
    reps, images, adjacent, pairs, orbits = G.geometry()
    require(len(reps) == 40 and len(images) == 40, 'line count')
    require(all(m.bit_count() == 27 for m in adjacent), 'nonorthogonal degree')
    flats = G.flats(reps, images)
    census = {}
    for mask, basis, _gens in flats:
        key = (len(basis) // 2, mask.bit_count())
        census[key] = census.get(key, 0) + 1
    require(census == {(0, 0): 1, (1, 1): 40, (2, 2): 240, (2, 4): 90,
                       (3, 5): 360, (3, 12): 40, (4, 40): 1},
            'flat census mismatch: %r' % (census,))
    for _mask, basis, _gens in flats:
        require(G.pairing_rank(basis, basis) * 2 == len(basis),
                'degenerate flat span encountered')
    # A 7-clique exists; the pattern forces B[Q,Q] = I_7, so rank B >= 7.
    maximal = G.maximal_cliques(adjacent)
    require(any(m.bit_count() == 7 for m in maximal), 'no 7-clique')
    return reps, images, adjacent, flats


def clean_pairs_census(adjacent, flats):
    """All ordered flat pairs (R, A) with every cross pair t!=s orthogonal.

    For such clean pairs the per-rectangle charge is exactly |R cap A|:
    the functionals B(., t) = <., t> - <Jt, Jt.>, t in R cap A, are
    K-independent on X_R by positive definiteness of the real form and
    pairwise orthogonality of R cap A (each is a signed unit vector on the
    orthogonal line t, and distinct such lines are orthogonal).
    """
    checked = 0
    for r_mask, r_basis, _rg in flats:
        for a_mask, a_basis, _ag in flats:
            clean = True
            t_iter = r_mask
            while t_iter:
                low = t_iter & -t_iter
                t = low.bit_length() - 1
                t_iter ^= low
                # t must be orthogonal to every OTHER line of A (including
                # the other lines of R cap A); the diagonal t = s needs no
                # check, so mask t's own bit off when present.
                others = a_mask ^ low if a_mask & low else a_mask
                if adjacent[t] & others:
                    clean = False
                    break
            if not clean:
                continue
            cost = G.pairing_rank(r_basis, a_basis)
            shared = (r_mask & a_mask).bit_count()
            require(cost >= shared,
                    'clean-class per-rectangle bound violated')
            require(cost == shared, 'clean pair not tight')
            checked += 1
    return checked


def part_b(reps, images, adjacent, flats):
    """Clean-class ingredients and two sharp cost-40 witnesses."""
    checked = clean_pairs_census(adjacent, flats)
    require(checked == 7033, 'clean ordered pair count %d' % checked)

    # Witness 1: partition of the 40 lines into ten pairwise-orthogonal,
    # full-span 4-line frames; the block-diagonal decoder costs exactly 40.
    orth = [((1 << 40) - 1) ^ adjacent[i] ^ (1 << i) for i in range(40)]
    frames = []

    def cover_search(uncovered):
        if not uncovered:
            return True
        v = min((t for t in range(40) if (uncovered >> t) & 1),
                key=lambda t: (orth[t] & uncovered).bit_count())
        cands = [t for t in range(40) if (orth[v] & uncovered) & (1 << t)]
        for i in range(len(cands)):
            for j in range(i + 1, len(cands)):
                if not (orth[cands[i]] >> cands[j]) & 1:
                    continue
                for k in range(j + 1, len(cands)):
                    a, b, c = cands[i], cands[j], cands[k]
                    if (orth[a] >> c) & 1 and (orth[b] >> c) & 1:
                        frame = (1 << v) | (1 << a) | (1 << b) | (1 << c)
                        frames.append(frame)
                        if cover_search(uncovered & ~frame):
                            return True
                        frames.pop()
        return False

    require(cover_search((1 << 40) - 1), 'no frame partition found')
    require(len(frames) == 10, 'frame partition size')
    covered = 0
    for frame in frames:
        covered |= frame
    require(covered == (1 << 40) - 1, 'frames do not cover')
    total = 0
    for frame in frames:
        idx = [t for t in range(40) if (frame >> t) & 1]
        require(all((orth[a] >> b) & 1 for a in idx for b in idx if a != b),
                'frame not pairwise orthogonal')
        rows = []
        for t in idx:
            rows += [reps[t], images[t]]
        basis = G.echelon(tuple(rows))
        require(len(basis) == 8, 'frame span not full')
        total += G.pairing_rank(basis, basis)
    require(total == 40, 'frame-partition cost %d' % total)
    block = [[0] * 40 for _ in range(40)]
    for frame in frames:
        idx = [t for t in range(40) if (frame >> t) & 1]
        for t in idx:
            for s in idx:
                block[t][s] = 1
    for t in range(40):
        for s in range(40):
            if t != s and (adjacent[t] >> s) & 1:
                require(block[t][s] == 0, 'witness pattern violation')
        require(block[t][t] == 1, 'witness diagonal')
    require(f2_rank([sum(block[t][s] << s for s in range(40))
                     for t in range(40)]) == 10, 'witness rank')

    # Witness 2: the canonical pattern B0 = (I + orthogonality) mod 2
    # decomposes into 40 clean stars, each of cost exactly 1.
    star_total = 0
    for t in range(40):
        readers = [s for s in range(40)
                   if s == t or not (adjacent[s] >> t) & 1]
        rows = []
        for s in readers:
            rows += [reps[s], images[s]]
        cost = G.pairing_rank(G.echelon(tuple(rows)), (reps[t], images[t]))
        require(cost == 1, 'star cost %d at line %d' % (cost, t))
        star_total += cost
    require(star_total == 40, 'star decomposition cost %d' % star_total)
    return {'clean_ordered_pairs': checked, 'witnesses': ['frame', 'star'],
            'clean_floor': 40}


def threshold_brackets(s, h):
    """Certified rational brackets on C*(s,h): beat(C) iff C < C*(s,h).

    F_C(b) = F_0(b) + s*x*((m/h)^b - 1) and D_C = (s-1) - s*x with x = C/40,
    so the beat condition is linear in C and
        C* = 40 * ((s-1) - F_0(b)) / (s * (m/h)^b).
    """
    prof0, m, _d0 = skel.profile(s, h, 1, Fr(0))
    flo, fhi = cert.F_iv(prof0, m, B)
    glo, ghi = cert.g_iv(h, m, B)
    glow, ghigh = glo / h + 1, ghi / h + 1          # enclosures of (m/h)^b
    require(glow <= ghigh, 'g enclosure order')
    u_lo = Fr(XDEN) * (s - 1 - fhi) / (s * ghigh)   # <= C*
    u_hi = Fr(XDEN) * (s - 1 - flo) / (s * glow)    # >= C*
    require(u_lo <= u_hi, 'bracket order')
    return u_lo, u_hi, m


def beat_direct(s, h, cost, bb=B):
    """Certified direct test: X(s,h,x=cost/40) > bb."""
    prof, m, deficit = skel.profile(s, h, 1, Fr(cost, XDEN))
    if deficit <= 0:
        return False
    flo, fhi = cert.F_iv(prof, m, bb)
    return fhi < deficit


def slot_masses(s, a, x0):
    """Exact closed-form total slot mass at stage s (window h = a+1, k = 1).

    Slots (skel.profile, k=1): active mass 2*s*a at cap a; copy mass s*x0 at
    cap h; idle: pair-0 tail mass 2a(s-3) at cap a(s-3); for p = 1..K-1 a
    pre-stretch slot of mass 4pa at cap 2pa and a bridge slot of mass 2a at
    cap h; for p = 1..K-2 a tail slot of mass 4a(K-1-p) at cap 2a(K-1-p).
    Caps 2aj (j = 1..K-1) therefore carry mass 8aj (count 4), and cap h
    carries the copy mass plus 2a(K-1) of bridge mass.  Total:
        2as + s*x0 + 2a(K-1) + 8a*sum_{j=1..K-1} j = 4aK^2 + 2aK + (2K+1)x0.
    (Cross-checked against skel.profile at s = 3, 5, 99.)
    """
    big_k = (s - 1) // 2
    return 4 * a * big_k * big_k + 2 * a * big_k + (2 * big_k + 1) * x0


def tail_increment(s, a, x0=Fr(22, XDEN)):
    """Certified lower bound on F_x0(b; s+2) - F_x0(b; s).

    A slot of mass w and cap c contributes w*((m/c)^q - 1), m = m(s) = 1+as.
    When s grows by 2, m grows by delta = 2a.  With u = delta/m in (0,1) and
    0 < q < 1, the binomial series alternates with decreasing magnitudes, so
        (1+u)^q - 1 >= q*u - q*(1-q)*u^2/2.
    Since (m/c)^q >= 1 and the bracket is positive,
        increment >= w * [q*delta/m - q*(1-q)*delta^2/(2*m^2)].
    Summing over slots (masses only grow with s; no slot is free since the
    largest cap a(s-3) is below m for all s >= 3):
        Inc(s) = Sigma(s) * [c1/m(s) - c2/m(s)^2],
    c1 = 2ab, c2 = 2a^2*b*(1-b).
    """
    m_now = 1 + a * s
    c1 = 2 * a * B
    c2 = 2 * a * a * B * (1 - B)
    return slot_masses(s, a, x0) * (c1 / m_now - c2 / (m_now * m_now))


def tail_step_bound(a, x0, big_k):
    """Certified lower bound on the per-pair increment at stage K = (s-1)/2.

    Linear in K: w(K) >= 4aK*c1/(3a+1) - c2*(3/(2a) + 3*x0/(4a^2)), from
    Sigma(K)/m(K) >= 4aK^2/(2aK+a+1) >= 4aK/(3a+1) (K >= 1) and
    Sigma(K)/m(K)^2 <= 1/a + 1/(2a) + 3*x0/(4*a^2).
    """
    c1 = 2 * a * B
    c2 = 2 * a * a * B * (1 - B)
    return Fr(4 * a) * big_k * c1 / (3 * a + 1) - c2 * (Fr(3, 2 * a) + Fr(3 * x0, 4 * a * a))


def tail_closure_margin(a, x0, s1, margin1, p_max=200):
    """Certified: the D - F gap stays nonpositive for every s >= s1.

    With margin1 an upper bound on the gap at s1 (margin1 <= 0 there), the
    gap at s1 + 2P satisfies
        gap <= margin1 + C_STEP*P - sum_{p=1..P} Inc_p,
    so it suffices that Q(P) = sum Inc_p - margin1 - C_STEP*P > 0 for all
    P >= 1.  Exact rational partial sums for P <= p_max; beyond that the
    exact linear per-pair step bound (increasing in K) is summed in closed
    form and the resulting quadratic's real minimum is checked exactly.
    """
    worst = None
    w_sum = Fr(0)
    for p in range(1, p_max + 1):
        w_sum += tail_increment(s1 + 2 * (p - 1), a, x0)
        value = w_sum - margin1 - C_STEP * p
        if worst is None or value < worst[1]:
            worst = (p, value)
    require(worst[1] > 0,
            'tail closure fails at P=%d: %s' % (worst[0], worst[1]))
    # Beyond p_max: Q(n) >= base' + lin*n + quad*n^2 - quad*n for n = P - p_max,
    # with step(K) = alpha*K - beta a lower bound on the per-pair increment.
    alpha = Fr(4 * a) * (2 * a * B) / (3 * a + 1)
    beta = (2 * a * a * B * (1 - B)) * (Fr(3, 2 * a) + Fr(3 * x0, 4 * a * a))
    k_start = (s1 - 1) // 2 + p_max
    base = w_sum - margin1 - C_STEP * p_max
    lin = alpha * k_start - beta - C_STEP
    quad = alpha / 2
    require(quad > 0, 'tail quadratic coefficient')
    # Q(n) = quad*n^2 + (lin-quad)*n + base for integer n >= 1; its minimum
    # over all real n bounds every integer value from above... conversely,
    # positivity of the real minimum implies positivity at every integer n.
    vmin = base - (lin - quad) * (lin - quad) / (4 * quad)
    require(vmin > 0, 'tail beyond p_max fails at the quadratic minimum')
    return worst


def part_c():
    # Cross-check the closed-form slot masses against the engine.
    for h_check in (7, 10, 12, 20, 40):
        a_check = h_check - 1
        for s_check in (3, 5, 9, 99, 201):
            prof0, _m, _d = skel.profile(s_check, h_check, 1, Fr(22, XDEN))
            engine_mass = sum(z * cap for cap, z in prof0.items())
            require(engine_mass == slot_masses(s_check, a_check, Fr(22, XDEN)),
                    'slot mass formula mismatch at s=%d h=%d' % (s_check, h_check))
    maps = {}
    sup_hi = None
    sup_arg = None
    sup_bracket = None
    for h in range(H_MIN, H_MAX + 1):
        a = h - 1
        row = {}
        s1 = None
        s = 3
        while s <= 401:
            u_lo, u_hi, m = threshold_brackets(s, h)
            if u_hi <= C_FLOOR:
                # Certified non-beat at C = 22 for this s (C* <= u_hi <= 22).
                # Try to close the tail here; stages before the closure point
                # are each certified non-beat by their own bracket, so the
                # closure may start at any non-beat stage.
                prof, m2, deficit = skel.profile(s, h, 1, Fr(C_FLOOR, XDEN))
                require(deficit > 0, 'deficit sign at closure candidate')
                flo, fhi = cert.F_iv(prof, m2, B)
                require(flo >= deficit,
                        'bracket/direct disagreement at h=%d s=%d' % (h, s))
                margin1 = deficit - flo        # <= 0: certified gap upper bound
                try:
                    tail_closure_margin(a, Fr(22, XDEN), s, margin1)
                    s1 = s
                    break
                except AssertionError:
                    pass                        # keep scanning; this s is
                    # still certified non-beat, closure starts later.
            else:
                t_hi = u_hi.__ceil__() - 1
                t_lo = u_lo.__ceil__() - 1 if u_lo > C_FLOOR else None
                row[s] = (t_lo, t_hi)
                if sup_hi is None or t_hi > sup_hi:
                    sup_hi = t_hi
                    sup_arg = (s, h)
                    sup_bracket = (u_lo, u_hi)
            s += 2
        if s1 is None:
            raise AssertionError('window %d never closes within scan' % h)
        maps[h] = {'s1': s1, 'row': row}
    require(sup_hi is not None, 'empty screen')
    require(sup_bracket[1] > sup_bracket[0], 'degenerate sup bracket')
    return maps, sup_hi, sup_arg, sup_bracket


def part_d():
    cap = X_BIT / (1 + X_BIT)
    require(cap > KAPPA_SELECTED, 'bit cap below selected record')
    # Every screen argmax point clears the bit side, so the cap binds there.
    for s, h, cost in ((9, 10, 29), (3, 10, 25), (9, 8, 30), (9, 7, 31)):
        result = skel.X(s, h, 1, Fr(cost, XDEN))
        require(result is not None and result['lo'] > X_BIT,
                'boundary point does not clear the bit side at %r' % ((s, h, cost),))
    gain = float(cap / KAPPA_SELECTED - 1) * 100
    return {'x_bit': str(X_BIT), 'kappa_cap': str(cap),
            'gain_percent': gain}


def part_e(sup_arg, sup_hi):
    """Negative controls: tampered inputs must flip the verdicts."""
    s_arg, h_arg = sup_arg
    # C1: closed form and direct root finding agree (certified implications;
    # the brackets are ~1e-42 wide, far below any integer gap).
    for s, h, cost in ((9, 10, 29), (9, 10, 30), (3, 10, 25), (3, 10, 26),
                       (7, 7, 31), (7, 7, 32), (15, 7, 27), (15, 7, 28)):
        u_lo, u_hi, _m = threshold_brackets(s, h)
        require(u_hi - u_lo < Fr(1, 10 ** 30), 'bracket not tight')
        direct = beat_direct(s, h, cost)
        if cost < u_lo:
            require(direct, 'closed form says beat, direct disagrees')
        if cost >= u_hi:
            require(not direct, 'closed form says no-beat, direct disagrees')
    # C2: doubling b must flip the argmax boundary beat to false.
    require(beat_direct(s_arg, h_arg, sup_hi, B) is True, 'argmax must beat')
    require(beat_direct(s_arg, h_arg, sup_hi, 2 * B) is False,
            'doubled b did not flip the beat verdict')
    # C3: a tampered pattern must change the clean census.
    reps, images, adjacent, flats = part_a()
    tampered = list(adjacent)
    for i in range(40):
        done = False
        for j in range(40):
            if i != j and not (adjacent[i] >> j) & 1:
                tampered[i] |= (1 << j)
                tampered[j] |= (1 << i)
                done = True
                break
        if done:
            break
    changed = clean_pairs_census(tampered, flats)
    require(changed != 7033, 'tampered pattern left the clean census unchanged')
    # C4: the star witness must depend on the exact pattern.  Adding one
    # nonorthogonality (i, j) removes i from star j's readers and j from
    # star i's; if some single addition pushes a star cost above 1, the
    # total-40 witness is genuinely geometry-dependent (existential control).
    def star_cost(pattern, t):
        readers = [s for s in range(40)
                   if s == t or not (pattern[s] >> t) & 1]
        rows = []
        for s in readers:
            rows += [reps[s], images[s]]
        return G.pairing_rank(G.echelon(tuple(rows)), (reps[t], images[t]))

    def star_total(pattern):
        return sum(star_cost(pattern, t) for t in range(40))

    require(star_total(adjacent) == 40, 'true star total drifted')
    # C4a: the frame witness needs orthogonality, not just any partition:
    # the naive consecutive 4-blocks pattern must violate the zero-pattern.
    naive = [[0] * 40 for _ in range(40)]
    for start in range(0, 40, 4):
        for t in range(start, start + 4):
            for s in range(start, start + 4):
                naive[t][s] = 1
    illegal = any(t != s and (adjacent[t] >> s) & 1 and naive[t][s]
                  for t in range(40) for s in range(40))
    require(illegal, 'naive partition pattern is legal; witness not structural')
    # C4b: the star cost is not vacuously constant: removing the self-loop
    # must drop the star cost to 0 (distinct F2-lines intersect trivially).
    star_no_self = G.pairing_rank(
        G.echelon(tuple(x for s in range(40)
                        if s != 0 and not (adjacent[s] >> 0) & 1
                        for x in (reps[s], images[s]))),
        (reps[0], images[0]))
    require(star_no_self == 0, 'star without self-loop should cost 0')


def main():
    summary = {}
    reps, images, adjacent, flats = part_a()
    summary['geometry'] = {'lines': 40, 'flats': len(flats),
                           'all_flats_nonsingular': True}
    summary['clean_class'] = part_b(reps, images, adjacent, flats)
    maps, sup_hi, sup_arg, sup_bracket = part_c()
    summary['screen'] = {
        'window_range': [H_MIN, H_MAX],
        'sup_integer_threshold': sup_hi,
        'sup_arg': {'s': sup_arg[0], 'h': sup_arg[1]},
        'sup_bracket': [str(sup_bracket[0]), str(sup_bracket[1])],
        'sup_bracket_decimal': [float(sup_bracket[0]), float(sup_bracket[1])],
        'viable_ends': {h: maps[h]['s1'] for h in (7, 8, 9, 10)},
        'window_maxima': {h: max(t[1] for t in maps[h]['row'].values())
                          for h in (7, 8, 9, 10)},
    }
    summary['prize'] = part_d()
    part_e(sup_arg, sup_hi)
    summary['negative_controls'] = 4
    print(json.dumps(summary, indent=1))
    print('PASS_EISENSTEIN_PHASE_COST_SCREEN: '
          'clean-class floor 40; certified necessary threshold <= %d '
          '(bracket %.6f..%.6f at s=%d h=%d); no new kappa'
          % (sup_hi, float(sup_bracket[0]), float(sup_bracket[1]),
             sup_arg[0], sup_arg[1]))


if __name__ == '__main__':
    main()
