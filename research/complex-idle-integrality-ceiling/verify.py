#!/usr/bin/env python3
"""Certify the exact integer idle-histogram ceiling for the selected complex local word.

`research/complex-local-word-ceiling` bounds packing with a fractional relaxation (1646/51
rank-51 children per call) and reports a = 0.001690054109089, i.e. under 0.87% of headroom over
the selected kappa. Real packings use integer child counts. This verifier computes the attained
optimum over every feasible integer idle histogram by dynamic programming and certifies the
tighter bracket it implies, so the residual packing headroom is bounded without sampling.

usage: verify.py [--write]
Nick Petalas, with AI assistance. Apache-2.0.
"""
import json
import random
import sys
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[0] / 'complex-local-word-ceiling'))
import ceiling as C  # noqa: E402
import integrality as I  # noqa: E402

M, PAIRS, PORTS, STAGES, CENTRE = 73, 4, 112, 9, 64
FAMILIES = 2 * PAIRS * PORTS
GRID = Q(1, 10 ** 15)


def dec(x, digits=18):
    return f'{float(x):.{digits}g}'


def exact_moment(H, W, a):
    """Certified enclosure of a fully specified histogram's per-call moment."""
    lo = hi = Q(0)
    for r, n in H.items():
        c = C.child_cost(r, M, a)
        lo, hi = lo + n * c[0], hi + n * c[1]
    return lo / W, hi / W


def selected():
    """Re-derive the selected complex local word from the pinned certificate and audit file."""
    rec = json.loads((ROOT / 'certificates/selected-result.json').read_text())
    asm = json.loads((ROOT / rec['certificate']).read_text())
    ind = json.loads((ROOT / 'research/community-frontier1094-audit/INDEPENDENT1094.json').read_text())
    H = {int(r): n for r, n in asm['complex_profile'].items()}
    idle = {int(r): n for r, n in ind['owner']['idle'].items()}
    N, W = ind['price']['calls'], ind['price']['live']
    C.require(H == {int(r): n for r, n in ind['owner']['profile'].items()}, 'profile mismatch')
    C.require(N % STAGES == 0 and W == FAMILIES * (N // STAGES), 'live stock is not 2*pairs*V per replica')
    mass = sum(r * n for r, n in H.items())
    C.require(mass == (M - 1) * W + CENTRE * N, 'coverage identity mass = 72W + 64N fails')
    local = {}
    for r, n in H.items():
        k = n - idle.get(r, 0)
        C.require(k >= 0 and k % N == 0, f'local rank {r} not uniform per call')
        if k:
            local[r] = k // N
    return rec, asm, H, idle, N, W, local


def exhaustive_idle(mass, R, m, a):
    """Independent min-cost enumeration over every integer histogram, for small domains.

    Plain descending recursion over counts; no dynamic program and no shared code path with
    `best_idle`. Exponential, so only used as a control on small (mass, R). Costs are held in
    the same scaled integer currency as `best_idle`, so the comparison is exact equality.
    """
    cost = [0] + [I.scaled(C.child_cost(r, m, a)[0]) for r in range(1, R + 1)]

    def rec(rank, left):
        if left == 0:
            return 0
        if rank == 0:
            return None
        out, k = None, 0
        while k * rank <= left:
            sub = rec(rank - 1, left - k * rank)
            if sub is not None:
                v = sub + k * cost[rank]
                out = v if out is None or v < out else out
            k += 1
        return out

    return rec(R, mass)


def controls(local, a_int, a_relax, q):
    """Thirteen recorded control results: fixtures for the dynamic program, the two-sided
    bracket certificate, monotonicity, and the parent's own controls re-run on the optimum."""
    out = {}
    a = a_relax[1]

    # 1. The dynamic program agrees with an independent exhaustive enumeration on three small
    #    domains, so the optimum it reports for mass 1646 is not a dynamic-program artefact.
    agree = []
    for mass, cap in ((30, 7), (36, 8), (45, 9)):
        dp_lo, _ = I.best_idle(mass, cap, M, a)
        brute = exhaustive_idle(mass, cap, M, a)
        agree.append({'idle_mass': mass, 'rank_cap': cap, 'agrees': dp_lo == brute})
    out['dp_matches_exhaustive_enumeration'] = agree
    C.require(all(row['agrees'] for row in agree), 'dynamic program disagrees with exhaustive enumeration')

    # 2. Failure control: a deliberately incomplete search must be caught. Restricting the DP to
    #    a smaller rank cap cannot match the true optimum, so a cap-48 run is strictly worse.
    _, hist48 = I.best_idle(int(q['idle_mass']), 48, M, a)
    lo48, _ = I.idle_bounds(hist48, M, a)
    _, hist51 = I.best_idle(int(q['idle_mass']), q['R'], M, a)
    lo51, _ = I.idle_bounds(hist51, M, a)
    out['truncated_rank_cap_is_strictly_worse'] = 'yes' if lo48 > lo51 else 'NO'
    C.require(lo48 > lo51, 'rank cap 48 unexpectedly matched the cap-51 optimum')

    # 3. The integrality gap is certified, not asserted: for every 0 < a <= relaxation ceiling the
    #    certified lower bound on the integer optimum exceeds the certified upper bound on the
    #    fractional relaxation, so the integer optimum is strictly larger than the fractional one.
    #    At a = 0 the two coincide exactly (both equal total_mass/w = 1), so the grid starts above 0.
    slack = None
    for k in range(1, 21):
        aa = Q(k, 20) * a
        r_hi = C.relax(local, M, FAMILIES, STAGES, CENTRE, aa)[1]
        i_lo = I.moment(local, M, FAMILIES, STAGES, CENTRE, aa)[0]
        slack = (i_lo - r_hi) if slack is None else min(slack, i_lo - r_hi)
    out['integer_optimum_strictly_above_fractional_relaxation'] = dec(slack) if slack is not None else 'NO'
    C.require(slack is not None and slack > 0, 'no certified integrality gap above a = 0')

    # 4. The integer moment is strictly increasing in a, as the parent's relaxation is.
    grid = [Q(k, 20) * a for k in range(0, 11)]
    vals = [I.moment(local, M, FAMILIES, STAGES, CENTRE, aa)[0] for aa in grid]
    out['integer_moment_strictly_increasing_in_a'] = 'yes' if all(
        x < y for x, y in zip(vals, vals[1:])) else 'NO'
    C.require(all(x < y for x, y in zip(vals, vals[1:])), 'integer moment not monotone in a')

    # 5. The optimum histogram is a feasible integer packing: exact mass, ranks inside the guard.
    lo_w, hi_w, hist, _ = I.moment(local, M, FAMILIES, STAGES, CENTRE, a_int[1])
    out['optimal_histogram_mass_conserved'] = sum(r * n for r, n in hist.items()) == int(q['idle_mass'])
    out['optimal_histogram_ranks_within_guard'] = max(hist) <= q['R']
    C.require(sum(r * n for r, n in hist.items()) == int(q['idle_mass']), 'optimum does not conserve idle mass')
    C.require(max(hist) <= q['R'], 'optimum uses a rank above the halving guard')

    # 6. Non-vacuity: the witness at the lower end is genuinely below one, and the certified
    #    lower bound at the upper end is genuinely above one. A bound that rejected every a
    #    would satisfy the upper half alone.
    wit_lo, wit_hi, _, _ = I.moment(local, M, FAMILIES, STAGES, CENTRE, a_int[0])
    rej_lo, _, _, _ = I.moment(local, M, FAMILIES, STAGES, CENTRE, a_int[1])
    out['bracket_is_witnessed_on_both_sides'] = 'yes' if wit_hi < 1 < rej_lo else 'NO'
    C.require(wit_hi < 1 < rej_lo, 'integer bracket is not witnessed on both sides')

    # 7. Strict tightening: the integer ceiling is strictly below the fractional relaxation.
    out['integer_ceiling_strictly_below_relaxation'] = 'yes' if a_int[1] < a_relax[1] else 'NO'
    C.require(a_int[1] < a_relax[1], 'integrality did not tighten the ceiling')

    # 8. A tighter guard cannot raise the ceiling, and one extra rank-1 local child cannot
    #    raise it either. Both are the parent's controls, now on the attained optimum.
    tight = I.ceiling_int(local, M, FAMILIES, STAGES, CENTRE, grid=GRID, R=q['R'] - 1)[1]
    worse = dict(local)
    worse[1] += 1
    extra = I.ceiling_int(worse, M, FAMILIES, STAGES, CENTRE, grid=GRID)[1]
    out['one_lower_guard_lowers_ceiling'] = 'yes' if tight < a_int[1] else 'NO'
    out['one_more_rank1_child_lowers_ceiling'] = 'yes' if extra < a_int[1] else 'NO'
    C.require(tight < a_int[1], 'tightening the guard did not lower the ceiling')
    C.require(extra < a_int[1], 'an extra rank-1 child did not lower the ceiling')

    # 9. The parent's sampling control, kept as a weaker statement: 25 random integer idle
    #    histograms are never better than the dynamic-program optimum.
    rng = random.Random(1094)
    worst_gap = None
    for _ in range(25):
        left, idle = int(q['idle_mass']), {}
        while left:
            r = min(left, rng.choice([1, 2, 3, 7, 13, 24, 40, 48, 51]))
            idle[r] = idle.get(r, 0) + 1
            left -= r
        v = I.scaled(sum((n * C.child_cost(r, M, a)[0] for r, n in idle.items()), Q(0)))
        gap = v - lo51
        worst_gap = gap if worst_gap is None else min(worst_gap, gap)
    out['sampled_idle_histograms_never_beat_optimum'] = 'yes' if worst_gap >= 0 else 'NO'
    C.require(worst_gap >= 0, 'a sampled histogram beat the dynamic-program optimum')

    # 10. The reported witness is the natural largest-first histogram, and the dynamic program is
    #     never beaten by it. The greedy rule is *not* assumed optimal; only the weaker statement
    #     is certified, so the DP remains the proof and greedy is a cross-check of the witness.
    left, greedy = int(q['idle_mass']), {}
    while left:
        r = min(left, q['R'])
        greedy[r] = greedy.get(r, 0) + 1
        left -= r
    greedy_lo, greedy_hi = I.idle_bounds(greedy, M, a)
    out['largest_first_greedy_matches_dynamic_program'] = 'yes' if greedy == hist51 else 'NO'
    out['dynamic_program_never_worse_than_greedy'] = 'yes' if lo51 <= greedy_lo else 'NO'
    C.require(lo51 <= greedy_lo, 'greedy beat the dynamic-program optimum')
    return out


def lever_rows(local, kappa_sel):
    """Integer versus fractional ceiling for the lever rows whose premises admit integer counts.

    Only rows with an integral per-call idle mass are listed. A row whose per-call paid mass is
    non-integral has no integer packing at all under this model and is reported separately.
    """
    rows = []
    cases = [('selected word (baseline)', local, CENTRE, 1),
             ('centre path free: no rank-8 copies, centre charge 0',
              {r: n for r, n in local.items() if r != 8}, 0, 1)]
    for name, word, centre, unpaid in cases:
        qc = I.model(word, M, FAMILIES, STAGES, centre, unpaid=unpaid)
        if qc['idle_mass'].denominator != 1:
            continue
        rel = C.ceiling(word, M, FAMILIES, STAGES, centre, grid=GRID, unpaid=unpaid)[1]
        lo, hi = I.ceiling_int(word, M, FAMILIES, STAGES, centre, grid=GRID, unpaid=unpaid)
        _, _, h, _ = I.moment(word, M, FAMILIES, STAGES, centre, hi, unpaid=unpaid)
        rows.append(dict(lever=name, idle_mass_per_call=str(qc['idle_mass']),
                         a_ceiling_fractional=dec(rel), a_ceiling_integer=dec(hi),
                         integer_ceiling_multiplier=dec(hi / rel),
                         kappa_upper_bound_fractional=dec(rel / (1 + rel)),
                         kappa_upper_bound_integer=dec(hi / (1 + hi)),
                         max_kappa_gain_percent_fractional=dec(100 * (rel / (1 + rel) / kappa_sel - 1), 6),
                         max_kappa_gain_percent_integer=dec(100 * (hi / (1 + hi) / kappa_sel - 1), 6),
                         optimal_idle_histogram={str(r): n for r, n in sorted(h.items())}))
    return rows


def main():
    rec, asm, H, idle, N, W, local = selected()
    a_relax = C.ceiling(local, M, FAMILIES, STAGES, CENTRE)
    a_int = I.ceiling_int(local, M, FAMILIES, STAGES, CENTRE, grid=GRID)
    q = I.model(local, M, FAMILIES, STAGES, CENTRE)

    # The bracket must be certified on both sides by the integer bounds, not by the relaxation.
    # At the low end the DP argmin's certified upper moment is below one (a witness exists); at
    # the high end the certified lower moment of *every* integer histogram is above one.
    wit_lo, wit_hi, hist, _ = I.moment(local, M, FAMILIES, STAGES, CENTRE, a_int[0])
    rej_lo, rej_hi, _, _ = I.moment(local, M, FAMILIES, STAGES, CENTRE, a_int[1])
    C.require(wit_hi < 1, 'no integer packing witnesses the lower bracket end')
    C.require(rej_lo > 1, 'upper bracket end not certified: some integer packing may still fit')

    kappa_sel = Q(rec['kappa'])
    kappa_relax = a_relax[1] / (1 + a_relax[1])
    kappa_int = a_int[1] / (1 + a_int[1])

    # The selected record's own packing must sit below the attained ceiling, not above it.
    actual = exact_moment(H, W, a_int[1])
    C.require(actual[0] > 1, 'selected profile not above one at the integer ceiling')

    # Integrality of the idle remainder under the two-unpaid lever: the per-call paid mass is
    # 71 * (896/9) + 64, which is not an integer, so that premise has no integer packing at all.
    q2 = I.model(local, M, FAMILIES, STAGES, CENTRE, unpaid=2)
    two_unpaid_integral = q2['total_mass'].denominator == 1

    out = dict(
        status='PASS_COMPLEX_IDLE_INTEGRALITY_CEILING',
        model=dict(m=M, pairs=PAIRS, ports=PORTS, stages=STAGES, centre_per_call=CENTRE,
                   live_families_per_call=str(q['w']), idle_rank_cap=q['R'],
                   idle_mass_per_call=str(q['idle_mass']),
                   coverage_identity='mass = 72 W + 64 N (re-checked on the selected profile)',
                   added_constraint='idle child counts are non-negative integers summing to '
                                    f'{int(q["idle_mass"])} rank units per call'),
        selected=dict(calls=N, live=W, local_profile_per_call={str(r): n for r, n in sorted(local.items())},
                      selected_idle_histogram={str(r): n for r, n in sorted(idle.items())},
                      complex_lower=asm['complex_lower'], kappa=rec['kappa']),
        fractional_relaxation_ceiling=dict(
            a_ceiling=str(a_relax[1]), a_ceiling_decimal=dec(a_relax[1]),
            kappa_upper_bound=dec(kappa_relax),
            max_kappa_gain_percent=dec(100 * (kappa_relax / kappa_sel - 1), 6),
            optimal_idle_histogram='fractional: ' + dec(q['idle_mass'] / q['R'], 12) + ' children of rank '
                                   + str(q['R'])),
        integer_ceiling=dict(
            a_witnessed_below=str(a_int[0]), a_ceiling=str(a_int[1]), a_ceiling_decimal=dec(a_int[1]),
            kappa_upper_bound=dec(kappa_int),
            max_kappa_gain_percent=dec(100 * (kappa_int / kappa_sel - 1), 6),
            optimal_idle_histogram={str(r): n for r, n in sorted(hist.items())},
            integrality_cost_in_a=dec(a_relax[1] - a_int[1]),
            integrality_cost_percent_of_ceiling=dec(100 * (1 - a_int[1] / a_relax[1]), 6),
            witness_moment_at_lower_end=[dec(wit_lo), dec(wit_hi)],
            certified_bounds_at_upper_end=[dec(rej_lo), dec(rej_hi)]),
        comparison=dict(
            relaxation_minus_integer_a=dec(a_relax[1] - a_int[1]),
            relaxation_headroom_percent=dec(100 * (kappa_relax / kappa_sel - 1), 6),
            integer_headroom_percent=dec(100 * (kappa_int / kappa_sel - 1), 6),
            headroom_removed_percent_points=dec(100 * ((kappa_relax - kappa_int) / kappa_sel), 6),
            selected_profile_moment_at_integer_ceiling=dec(actual[0], 12),
            two_unpaid_coordinate_idle_mass=str(q2['idle_mass']),
            two_unpaid_coordinate_idle_mass_is_integer=two_unpaid_integral),
        controls=controls(local, a_int, a_relax, q),
        lever_rows_with_integer_premises=lever_rows(local, kappa_sel),
        scope='Attained-optimum bound for the selected complex local word: one fixed paid local '
              'profile per call, m = 73, 2*4*112 live data families per nine-stage replica, centre '
              'charge 64, the coverage law and the outer halving guard R = 51. The only addition to '
              'research/complex-local-word-ceiling is that idle child counts are integers. It is not '
              'a bound for other local words, port counts, templates, coverage laws or outer recipes, '
              'and it still allows every repacking without checking physical realizability. No new '
              'kappa: the selected record is unchanged.')
    text = json.dumps(out, indent=1, sort_keys=True) + '\n'
    if sys.argv[1:] == ['--write']:
        (HERE / 'RESULT.json').write_text(text)
    else:
        C.require((HERE / 'RESULT.json').read_text() == text, 'RESULT.json differs')
    print(out['status'],
          'a_ceiling', out['integer_ceiling']['a_ceiling_decimal'],
          'kappa<=', out['integer_ceiling']['kappa_upper_bound'],
          'headroom', out['comparison']['integer_headroom_percent'] + '%')


if __name__ == '__main__':
    try:
        main()
    except ValueError as e:
        print('FAIL:', e)
        sys.exit(1)