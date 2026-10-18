#!/usr/bin/env python3
"""Certify the packing-independent ceiling of the selected complex local word, and the
local-word budget needed for the a = 1/99 planning target. Writes or checks RESULT.json.

usage: verify.py [--write]
Douglas Colkitt, with Claude (Anthropic) assistance. Apache-2.0.
"""
import json, random, sys
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import ceiling as C  # noqa: E402

M, PAIRS, PORTS, STAGES, CENTRE = 73, 4, 112, 9, 64
FAMILIES = 2 * PAIRS * PORTS                      # live data families per replica (all helpers hosted)
TARGET = Q(1, 99)


def dec(x, digits=18):
    return f'{float(x):.{digits}g}'


def exact_moment(H, W, a):
    lo = hi = Q(0)
    for r, n in H.items():
        c = C.child_cost(r, M, a)
        lo, hi = lo + n * c[0], hi + n * c[1]
    return lo / W, hi / W


def selected():
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


def previous_record(rec, local, N, a_hi):
    """The previous record must split as the same local word plus an admissible idle histogram,
    and its complex endpoint must lie below the same ceiling."""
    prev = json.loads((ROOT / rec['previous_record']).read_text())
    asm = json.loads((ROOT / prev['certificate']).read_text())
    H = {int(r): n for r, n in asm['complex_profile'].items()}
    idle = {r: H.get(r, 0) - N * local.get(r, 0) for r in set(H) | set(local)}
    C.require(all(v >= 0 for v in idle.values()), 'previous record does not contain the local word')
    idle = {r: v for r, v in idle.items() if v}
    q = C.model(local, M, FAMILIES, STAGES, CENTRE)
    C.require(sum(r * v for r, v in idle.items()) == N * q['idle_mass'], 'previous idle mass differs')
    C.require(max(idle) <= q['R'], 'previous idle rank above the guard')
    b = Q(asm['complex_lower'])
    C.require(b < a_hi, 'previous endpoint above the ceiling')
    return dict(record=rec['previous_record'], kappa=prev['kappa'], complex_lower=asm['complex_lower'],
                idle_histogram={str(r): v for r, v in sorted(idle.items())}, below_ceiling=True)


def budget(local, a):
    """Necessary condition relax(a) <= 1 rewritten as sum_r n_r p_r(a) <= B(a), with excess price
    p_r = (r/m)^(1-a) - r (R/m)^(1-a)/R of a local rank-r child over ideal idle mass."""
    q = C.model(local, M, FAMILIES, STAGES, CENTRE)
    R = q['R']
    cR = C.child_cost(R, M, a)
    B = (q['w'] - q['total_mass'] * cR[1] / R, q['w'] - q['total_mass'] * cR[0] / R)
    price = {}
    for r in sorted(set(local) | {1}):
        c = C.child_cost(r, M, a)
        price[r] = (c[0] - r * cR[1] / R, c[1] - r * cR[0] / R)
    spend = (sum(n * price[r][0] for r, n in local.items()), sum(n * price[r][1] for r, n in local.items()))
    others = (spend[0] - local.get(1, 0) * price[1][1], spend[1] - local.get(1, 0) * price[1][0])
    max_rank1 = (B[0] - others[1]) / price[1][1]
    return dict(budget_B=[dec(B[0]), dec(B[1])], local_excess_spend=[dec(spend[0]), dec(spend[1])],
                spend_over_budget_lower=dec(spend[0] / B[1]), rank1_price=dec(price[1][0]),
                max_rank1_per_call_others_fixed=dec(max_rank1, 8),
                excess_price_by_rank={str(r): dec(p[0], 8) for r, p in price.items()})


def controls(local):
    out = {}
    def rejects(name, f):
        try:
            f(); out[name] = 'ACCEPTED'
        except ValueError as e:
            out[name] = 'rejected: ' + str(e)
    rejects('idle_rank_52_violates_halving_guard', lambda: C.model(local, M, FAMILIES, STAGES, CENTRE, R=52))
    rejects('local_mass_exceeds_coverage', lambda: C.model({1: 7300}, M, FAMILIES, STAGES, CENTRE))
    lo0, hi0 = C.ceiling(local, M, FAMILIES, STAGES, CENTRE)
    worse = dict(local); worse[1] += 1
    lo1, hi1 = C.ceiling(worse, M, FAMILIES, STAGES, CENTRE)
    out['one_more_rank1_child_lowers_ceiling'] = 'yes' if hi1 < hi0 else 'NO'
    # dominance: integer idle histograms with ranks <= 51 and the exact idle mass never beat the relaxation
    q = C.model(local, M, FAMILIES, STAGES, CENTRE)
    rng = random.Random(1094)
    worst = None
    for _ in range(25):
        left, idle = int(q['idle_mass']), {}
        while left:
            r = min(left, rng.choice([1, 2, 3, 7, 13, 24, 40, 48, 51]))
            idle[r] = idle.get(r, 0) + 1
            left -= r
        Hc = dict(local)
        for r, n in idle.items():
            Hc[r] = Hc.get(r, 0) + n
        val = exact_moment(Hc, q['w'], hi0)[0]
        worst = val if worst is None else min(worst, val)
    out['sampled_idle_histograms_above_one_at_ceiling'] = 'yes' if worst > 1 else 'NO'
    C.require(all(v.startswith('rejected') or v == 'yes' for v in out.values()), f'control failed: {out}')
    return out


def main():
    rec, asm, H, idle, N, W, local = selected()
    b = Q(asm['complex_lower'])
    lo, hi = C.ceiling(local, M, FAMILIES, STAGES, CENTRE)
    C.require(b < lo, 'selected endpoint above the relaxation')
    act = exact_moment(H, W, hi)
    C.require(act[0] > 1, 'selected profile not above one at the ceiling')
    rel_b = C.relax(local, M, FAMILIES, STAGES, CENTRE, b)
    C.require(rel_b[1] < exact_moment(H, W, b)[0], 'relaxation must not exceed the actual moment')
    prev = previous_record(rec, local, N, hi)
    kappa_cap = hi / (1 + hi)
    q = C.model(local, M, FAMILIES, STAGES, CENTRE)
    out = dict(
        status='PASS_COMPLEX_LOCAL_WORD_CEILING',
        model=dict(m=M, pairs=PAIRS, ports=PORTS, stages=STAGES, centre_per_call=CENTRE,
                   live_families_per_call=str(q['w']), idle_rank_cap=q['R'],
                   coverage_identity='mass = 72 W + 64 N (checked on the selected profile)'),
        selected=dict(calls=N, live=W, rank_mass=sum(r * n for r, n in H.items()),
                      local_profile_per_call={str(r): n for r, n in sorted(local.items())},
                      idle_histogram={str(r): n for r, n in sorted(idle.items())},
                      local_mass_per_call=str(q['local_mass']), idle_mass_per_call=str(q['idle_mass']),
                      complex_lower=asm['complex_lower'], kappa=rec['kappa']),
        ceiling=dict(a_relaxation_achievable=str(lo), a_ceiling=str(hi), a_ceiling_decimal=dec(hi),
                     kappa_upper_bound=dec(kappa_cap),
                     max_kappa_gain_percent=dec(100 * (kappa_cap / Q(rec['kappa']) - 1), 6),
                     selected_moment_at_ceiling_lower=dec(act[0])),
        previous_record_same_local_word=prev,
        target=dict(a=str(TARGET), **budget(local, TARGET)),
        at_selected_endpoint=budget(local, b),
        controls=controls(local),
        scope='Bound for the selected local word (paid profile per call), 2*4*112 live data families per '
              'nine-stage replica, the coverage law and the outer halving guard. It is not a bound for other '
              'local words, port counts, templates, coverage laws or outer recipes, and allows fractional idle '
              'counts and every repacking without checking physical realizability.')
    text = json.dumps(out, indent=1, sort_keys=True) + '\n'
    if sys.argv[1:] == ['--write']:
        (HERE / 'RESULT.json').write_text(text)
    else:
        C.require((HERE / 'RESULT.json').read_text() == text, 'RESULT.json differs')
    print(out['status'], 'a_ceiling', out['ceiling']['a_ceiling_decimal'], 'kappa<=', out['ceiling']['kappa_upper_bound'])


if __name__ == '__main__':
    try:
        main()
    except ValueError as e:
        print('FAIL:', e); sys.exit(1)
