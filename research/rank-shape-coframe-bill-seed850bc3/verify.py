#!/usr/bin/env python3
"""Fully charged block-climb gate screen over all rank-one payload reblockings.

Aaron Wang, with help from opencode (substantial AI assistance). Apache-2.0.
The interval engine is Douglas Colkitt's retained PR1240 source, unchanged.

Scope: cost-alphabet implication audit for the drawn `complex-rank-shape-decoder`
card (method 2). In the frozen PR1240/PR1429/PR1605 cost alphabet (width 73,
stock 896/9, centre charge 64, old idle mass 1646 at rank 51) we price every
partition of the selected word's 2,412 rank-one payloads into block children of
rank at most the declared cap, with copies (rank-k frame transports), frames and
dirty-slot restoration charged at the PR1605/PR3039 proved minimum, and screen
the complete per-call profiles at the card's acceptance target
a* = 21/20 * 1690054109089/10^15. No physical decoder, word-level co-frame
census, supplier admission or new kappa is claimed.
"""
import argparse
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}
PAYLOAD = 2412
TARGET = Q(21, 20) * Q(1690054109089, 10 ** 15)
PLANNING = Q(1, 99)
BASE_CEILING = Q(1690054109089, 10 ** 15)
WIDTH, STOCK, IDLE, CAP, TOTAL = 73, Q(896, 9), 1646, 51, Q(7232)
INPUTS = {
    'research/complex-local-word-ceiling/ceiling.py',
    'research/complex-rank-one-block-budget/README.md',
    'research/complex-rank-one-block-budget/RESULT.json',
}


def require(ok, why):
    if not ok:
        raise ValueError(why)


def load_engine():
    pins = json.loads((HERE / 'SOURCES.json').read_text(encoding='utf-8'))
    live = [v for v in pins['files'] if v['usage'] == 'input']
    require(len(live) == len(INPUTS) and {v['path'] for v in live} == INPUTS,
            'incomplete source inventory')
    authenticated = {}
    for v in live:
        data = (ROOT / v['path']).read_bytes()
        require(hashlib.sha256(data).hexdigest() == v['sha256'],
                'source drift: ' + v['path'])
        authenticated[v['path']] = data
    prior = json.loads(authenticated['research/complex-rank-one-block-budget/RESULT.json'])
    require(prior['local_profile'] == {str(r): n for r, n in BASE.items()} and
            Q(prior['target']) == TARGET and prior['idle_mass'] == IDLE and
            prior['rank16_complete_max_extra_integer_rank_mass'] == 10,
            'predecessor model binding')
    frozen = pins['frozen_sources'][0]
    data = (HERE / frozen['local_path']).read_bytes()
    require(hashlib.sha256(data).hexdigest() == frozen['sha256'], 'PR3066 source drift')
    # Execute precisely the authenticated source bytes, without consulting pyc.
    path = ROOT / 'research/complex-local-word-ceiling/ceiling.py'
    namespace = {'__name__': 'retained_ceiling', '__file__': str(path)}
    exec(compile(authenticated['research/complex-local-word-ceiling/ceiling.py'],
                 str(path), 'exec'), namespace)
    return namespace


def iv_add(*terms):
    lo = sum((t[0] for t in terms), Q(0))
    hi = sum((t[1] for t in terms), Q(0))
    return lo, hi


def iv_scale(term, count):
    require(count >= 0, 'nonnegative count')
    return count * term[0], count * term[1]


def moment_strict(hist, cost, a, idle=IDLE):
    """PR1605 strict contract: added work is paid on top of the old idle bill."""
    out = [Q(0), Q(0)]
    for rank, count in list(hist.items()) + [(CAP, Q(idle, CAP))]:
        require(type(rank) is int and 1 <= rank <= CAP and count >= 0, 'histogram domain')
        lo, hi = cost(rank, WIDTH, a)
        out[0] += count * lo
        out[1] += count * hi
    return out[0] / STOCK, out[1] / STOCK


def moment_law(hist, cost, a):
    """Coverage-law convention: every added rank unit is refunded from old idle."""
    paid = sum(Q(r) * Q(n) for r, n in hist.items())
    idle = TOTAL - paid
    require(idle >= 0, 'local word pays more mass than the coverage law allows')
    return moment_strict(hist, cost, a, idle=Q(idle))


def decision(bounds):
    if bounds[1] < 1:
        return 'pass'
    if bounds[0] > 1:
        return 'fail'
    raise ValueError('interval does not decide strict moment sign')


def decimal_bounds(bounds, digits=15):
    scale = 10 ** digits
    lo = (bounds[0] * scale).__floor__()
    hi = (bounds[1] * scale).__ceil__()
    return [str(Q(lo, scale)), str(Q(hi, scale))]


def exact_bounds(bounds):
    return [str(bounds[0]), str(bounds[1])]


def pr3066_profile(charged_pairs):
    hist = dict(BASE)
    del hist[1]
    hist[16] = hist.get(16, 0) + 150
    hist[2] = hist.get(2, 0) + 2 * charged_pairs
    remainder = 12 - 2 * charged_pairs
    if remainder:
        hist[remainder] = hist.get(remainder, 0) + 1
    return dict(sorted(hist.items()))


def greedy_blocks(payload, cap):
    blocks = []
    left = payload
    while left > 0:
        take = min(cap, left)
        blocks.append(take)
        left -= take
    return blocks


def reblocked(cap, payload=PAYLOAD, saves=0, transports=0):
    """BASE with `payload` rank-one children replaced by greedy blocks.

    saves and transports are charged at rank 1 and at the block rank (PR1429),
    one per block unless count overridden by per-block arrays (int here)."""
    blocks = greedy_blocks(payload, cap)
    hist = dict(BASE)
    hist[1] = hist.get(1, 0) - payload + saves
    for k in blocks:
        hist[k] = hist.get(k, 0) + 1
        if transports:
            hist[k] = hist.get(k, 0) + transports
    if hist[1] == 0:
        del hist[1]
    require(all(n >= 0 for n in hist.values()), 'negative count')
    return dict(sorted(hist.items()))


def with_rank1(hist, units):
    out = dict(hist)
    out[1] = out.get(1, 0) + units
    return dict(sorted(out.items()))


def strict_ceiling(hist, cost, grid=Q(1, 10 ** 13)):
    lo, hi = Q(0), Q(1, 20)
    require(decision(moment_strict(hist, cost, hi)) == 'fail', 'search window too small')
    require(decision(moment_strict(hist, cost, lo)) == 'pass', 'no positive saving')
    while hi - lo > grid:
        mid = Q(int((lo + hi) / 2 / grid)) * grid
        if mid <= lo:
            mid = lo + grid
        v = moment_strict(hist, cost, mid)
        if v[1] < 1:
            lo = mid
        elif v[0] > 1:
            hi = mid
        else:
            raise ValueError('enclosure too wide to separate the grid point')
    return lo, hi


def law_ceiling(engine, hist, grid=Q(1, 10 ** 13)):
    return engine['ceiling'](hist, WIDTH, 896, 9, 64, grid=grid)


def max_units(hist, cost, a, convention):
    """Largest number of added rank-one units still passing at a (strict sign).

    Returns (units, law_capped): law_capped says the coverage law, not the
    moment, stopped the budget search."""
    def dec(units):
        h = with_rank1(hist, units)
        try:
            return decision(convention(h, cost, a))
        except ValueError as exc:
            if 'coverage law' in str(exc):
                return 'law_exhausted'
            raise
    units = 0
    while dec(units) == 'pass':
        units += 1
        require(units <= 4000, 'budget search runaway')
    return units - 1, dec(units) == 'law_exhausted'


def min_coverage(cap, cost, a, convention):
    """Least payload coverage by zero-charge blocks whose profile passes at a."""
    for blocks in range(1, PAYLOAD // 2 + 2):
        payload = min(blocks * cap, PAYLOAD)
        hist = reblocked(cap, payload=payload)
        if decision(convention(hist, cost, a)) == 'pass':
            lo_b, hi_b = (blocks - 1) * cap + 1, payload
            best = payload
            while lo_b <= hi_b:
                mid = (lo_b + hi_b) // 2
                if decision(convention(reblocked(cap, payload=mid), cost, a)) == 'pass':
                    best = mid
                    hi_b = mid - 1
                else:
                    lo_b = mid + 1
            return best, len(greedy_blocks(best, cap))
    raise ValueError('no passing coverage found')


def enumerate_partitions(total, cap):
    out = []

    def rec(left, ceiling, acc):
        if left == 0:
            out.append(list(acc))
            return
        for k in range(min(ceiling, left), 0, -1):
            acc.append(k)
            rec(left - k, k, acc)
            acc.pop()

    rec(total, cap, [])
    return out


def small_instance_check(cost, a):
    """Independent exhaustive check: greedy is strictly minimal at payloads=24, cap=8."""
    total, cap = 24, 8
    greedy = greedy_blocks(total, cap)
    g_cost = iv_add(*[iv_scale(cost(k, WIDTH, a), 1) for k in greedy])
    others = 0
    for part in enumerate_partitions(total, cap):
        if part == greedy:
            continue
        p_cost = iv_add(*[iv_scale(cost(k, WIDTH, a), 1) for k in part])
        require(g_cost[1] < p_cost[0], 'greedy not strictly minimal on small instance')
        others += 1
    return others


def merge_certificate(cost, a, cap):
    """Strict subadditivity on the full merge grid: merging two blocks strictly helps."""
    checks = 0
    for p in range(2, cap + 1):
        for q in range(p, cap + 1):
            if p + q > cap:
                continue
            left = iv_add(cost(p, WIDTH, a), cost(q, WIDTH, a))
            right = cost(p + q, WIDTH, a)
            require(left[0] > right[1], 'merge certificate failed at %d+%d' % (p, q))
            checks += 1
    return checks


def monotone_certificate(cost, a, cap):
    """c(k)/k strictly decreasing: larger blocks deliver payloads cheapest."""
    checks = 0
    for p in range(2, cap):
        for q in range(p + 1, cap + 1):
            lp, hp = cost(p, WIDTH, a)
            lq, hq = cost(q, WIDTH, a)
            require(lp / p > hq / q, 'payload monotonicity failed at %d,%d' % (p, q))
            checks += 1
    return checks


def tax_dominance_certificate(cost, a, cap):
    """A restoration-taxed block is dearer than its payload singles at this a."""
    c1 = cost(1, WIDTH, a)
    checks = 0
    for k in range(2, cap + 1):
        taxed = iv_add(cost(k, WIDTH, a), c1)
        singles = iv_scale(c1, k)
        require(singles[1] < taxed[0], 'tax dominance failed at k=%d' % k)
        checks += 1
    return checks


def transport_dominance_certificate(cost, a, cap):
    """One paid transport per block is dearer than the payload singles at this a."""
    checks = 0
    for k in range(2, cap + 1):
        charged = iv_scale(cost(k, WIDTH, a), 2)
        singles = iv_scale(cost(1, WIDTH, a), k)
        require(singles[1] < charged[0], 'transport dominance failed at k=%d' % k)
        checks += 1
    return checks


def result(engine):
    cost = engine['child_cost']
    checks = []

    # --- predecessor replay: PR3066's seven published rows, exactly ---
    frozen = json.loads((HERE / json.loads((HERE / 'SOURCES.json').read_text(
        encoding='utf-8'))['frozen_sources'][0]['local_path']).read_text(encoding='utf-8'))
    rows = []
    for published in frozen['rows']:
        q = published['charged_pairs']
        hist = pr3066_profile(q)
        require({str(r): n for r, n in hist.items()} == published['profile'],
                'PR3066 profile drift at q=%d' % q)
        require(sum(r * n for r, n in hist.items()) == 5586 + 2 * q, 'paid mass')
        bounds = moment_strict(hist, cost, TARGET)
        require(decimal_bounds(bounds) == published['moment'],
                'PR3066 moment drift at q=%d' % q)
        require(decision(bounds) == published['decision'] ==
                ('pass' if q <= 5 else 'fail'), 'PR3066 decision drift at q=%d' % q)
        rows.append({'charged_pairs': q, 'moment': decimal_bounds(bounds),
                     'moment_exact': exact_bounds(bounds),
                     'decision': decision(bounds)})
    checks.append('pr3066_seven_rows_reproduced')

    # --- certificates at the acceptance target ---
    merges = merge_certificate(cost, TARGET, CAP)
    mono = monotone_certificate(cost, TARGET, CAP)
    tax = tax_dominance_certificate(cost, TARGET, CAP)
    trans = transport_dominance_certificate(cost, TARGET, CAP)
    checks += ['merge_grid_strict', 'payload_monotone_strict',
               'tax_dominance_strict', 'transport_dominance_strict']

    # --- control: baseline and planning target ---
    require(decision(moment_strict(BASE, cost, TARGET)) == 'fail', 'baseline control')
    require(decision(moment_strict(BASE, cost, PLANNING)) == 'fail', 'planning control')
    checks += ['unchanged_baseline_fails', 'one_over_99_still_fails']

    # --- shapes ---
    g16 = reblocked(16)
    g51 = reblocked(51)
    require(g16 == pr3066_profile(0), 'greedy cap-16 shape must be PR3066 q=0 row')

    # --- contract lattice, strict contract (added work paid on top) ---
    contracts = []
    shapes = {'greedy16': (16, g16, 151), 'greedy51': (51, g51, 48)}
    for name, (capk, hist, block_count) in shapes.items():
        free_bounds = moment_strict(hist, cost, TARGET)
        contracts.append({'shape': name, 'contract': 'zero_charge',
                          'profile': {str(r): n for r, n in hist.items()},
                          'rank_mass': sum(r * n for r, n in hist.items()),
                          'moment': decimal_bounds(free_bounds),
                          'moment_exact': exact_bounds(free_bounds),
                          'decision': decision(free_bounds)})
        saved = with_rank1(hist, block_count)
        taxed_bounds = moment_strict(saved, cost, TARGET)
        contracts.append({'shape': name, 'contract': 'restoration_tax_one_save_per_block',
                          'profile': {str(r): n for r, n in saved.items()},
                          'rank_mass': sum(r * n for r, n in saved.items()),
                          'moment': decimal_bounds(taxed_bounds),
                          'moment_exact': exact_bounds(taxed_bounds),
                          'decision': decision(taxed_bounds)})
        over = dict(hist)
        for k in greedy_blocks(PAYLOAD, capk):
            over[k] = over.get(k, 0) + 1
        over = dict(sorted(over.items()))
        over_bounds = moment_strict(over, cost, TARGET)
        contracts.append({'shape': name, 'contract': 'one_paid_transport_per_block',
                          'profile': {str(r): n for r, n in over.items()},
                          'rank_mass': sum(r * n for r, n in over.items()),
                          'moment': decimal_bounds(over_bounds),
                          'moment_exact': exact_bounds(over_bounds),
                          'decision': decision(over_bounds)})
        both = with_rank1(over, block_count)
        both_bounds = moment_strict(both, cost, TARGET)
        contracts.append({'shape': name, 'contract': 'transport_plus_restoration',
                          'profile': {str(r): n for r, n in both.items()},
                          'rank_mass': sum(r * n for r, n in both.items()),
                          'moment': decimal_bounds(both_bounds),
                          'moment_exact': exact_bounds(both_bounds),
                          'decision': decision(both_bounds)})
    checks.append('contract_lattice_screened')

    # --- uniform-tax optimum: taxed blocks are counterproductive, so the best
    # uniformly taxed realization is the unchanged selected word ---
    uniform = {'optimal_profile': {str(r): n for r, n in BASE.items()},
               'reason': ('for every 2<=k<=51 at a*, k rank-one singles are strictly '
                          'cheaper than one rank-k block plus one rank-one save '
                          '(tax_dominance certificate); blocking without owned gather '
                          'slots is counterproductive at every block size'),
               'moment': decimal_bounds(moment_strict(BASE, cost, TARGET)),
               'moment_exact': exact_bounds(moment_strict(BASE, cost, TARGET)),
               'decision': decision(moment_strict(BASE, cost, TARGET))}
    require(uniform['decision'] == 'fail', 'uniform tax must be excluded at a*')
    checks.append('uniform_restoration_tax_excluded')

    # --- mutation control: dropping the saves from a taxed profile must flip it ---
    g51_taxed = with_rank1(g51, 48)
    require(decision(moment_strict(g51_taxed, cost, TARGET)) == 'fail',
            'taxed greedy-51 must fail')
    require(decision(moment_strict(g51, cost, TARGET)) == 'pass',
            'omitted-save false pass must be observable')
    checks.append('omitted_save_false_pass_control')

    # --- coverage-law rejection of over-law transport masses ---
    over_law = reblocked(51, transports=1)
    require(sum(r * n for r, n in over_law.items()) > TOTAL, 'transport mass accounting')
    try:
        moment_law(over_law, cost, TARGET)
    except ValueError as exc:
        require('coverage law' in str(exc), 'wrong rejection reason')
    else:
        raise ValueError('over-law transport profile not rejected')
    checks.append('over_law_transport_rejected')

    # --- budgets: exact slack in added rank-one units at a* ---
    budgets = {}
    for name, (capk, hist, block_count) in shapes.items():
        strict_units, strict_capped = max_units(hist, cost, TARGET, moment_strict)
        law_units, law_capped = max_units(hist, cost, TARGET, moment_law)
        budgets[name] = {
            'blocks': block_count,
            'slack_rank1_units_strict_contract': strict_units,
            'slack_strict_contract_law_capped': strict_capped,
            'slack_rank1_units_coverage_law': law_units,
            'slack_coverage_law_law_capped': law_capped,
            'max_taxed_blocks_strict_contract': strict_units,
            'min_zero_charge_blocks_strict_contract': block_count - strict_units,
        }
        require(decision(moment_strict(with_rank1(hist, strict_units), cost, TARGET))
                == 'pass', 'budget boundary pass side')
        require(decision(moment_strict(with_rank1(hist, strict_units + 1), cost, TARGET))
                == 'fail', 'budget boundary fail side')
    checks.append('budget_boundaries_signed')

    # --- minimal zero-charge coverage of the payloads ---
    coverage = {}
    for capk in (16, 51):
        payload_strict, blocks_strict = min_coverage(capk, cost, TARGET, moment_strict)
        payload_law, blocks_law = min_coverage(capk, cost, TARGET, moment_law)
        coverage['cap%d' % capk] = {
            'min_payloads_covered_strict_contract': payload_strict,
            'blocks_strict_contract': blocks_strict,
            'min_payloads_covered_coverage_law': payload_law,
            'blocks_coverage_law': blocks_law,
        }
    checks.append('min_coverage_computed')

    # --- coverage/charged-work tradeoff at the strict contract ---
    tradeoff = []
    for capk, payload in ((16, coverage['cap16']['min_payloads_covered_strict_contract']),
                          (16, 768), (16, PAYLOAD), (51, coverage['cap51']['min_payloads_covered_strict_contract']),
                          (51, 1530), (51, PAYLOAD)):
        hist = reblocked(capk, payload=payload)
        units, capped = max_units(hist, cost, TARGET, moment_strict)
        tradeoff.append({'cap': capk, 'covered_payloads': payload,
                         'slack_rank1_units_strict_contract': units,
                         'slack_strict_contract_law_capped': capped})

    # --- ceilings (coverage law, the card's ceiling definition) ---
    ceilings = []
    law_profiles = [('baseline', BASE), ('greedy16', g16), ('greedy51', g51),
                    ('greedy51_restoration_taxed', g51_taxed)]
    for name, hist in law_profiles:
        lo, hi = law_ceiling(engine, hist)
        ratio_lo = lo / BASE_CEILING
        ceilings.append({'profile': name,
                         'ceiling': [str(lo), str(hi)],
                         'ratio_to_selected_ceiling': [str(ratio_lo), str(hi / BASE_CEILING)],
                         'gate_five_percent': 'pass' if lo >= Q(21, 20) * BASE_CEILING
                         else ('fail' if hi < Q(21, 20) * BASE_CEILING else 'undecided')})
    base_lo, base_hi = law_ceiling(engine, BASE)
    require(base_lo <= BASE_CEILING <= base_hi, 'selected ceiling bracket control')
    checks.append('selected_ceiling_bracket_control')

    # --- strict-convention ceilings ---
    strict_ceilings = []
    for name, hist in [('baseline', BASE), ('greedy16', g16), ('greedy51', g51),
                       ('greedy51_restoration_taxed', g51_taxed)]:
        at_zero = moment_strict(hist, cost, Q(0))
        if decision(at_zero) == 'fail':
            strict_ceilings.append({
                'profile': name, 'ceiling': None,
                'reason': 'moment above one for every a >= 0 under the strict contract',
                'moment_at_zero': exact_bounds(at_zero)})
            continue
        lo, hi = strict_ceiling(hist, cost)
        strict_ceilings.append({'profile': name, 'ceiling': [str(lo), str(hi)],
                                'ratio_to_selected_ceiling': [str(lo / BASE_CEILING),
                                                             str(hi / BASE_CEILING)]})

    # --- independent small-instance check ---
    others = small_instance_check(cost, TARGET)
    checks.append('small_instance_greedy_strictly_minimal')

    return {
        'scope': ('cost-alphabet implication audit for complex-rank-shape-decoder '
                  'method 2; no physical decoder, word-level co-frame census, '
                  'supplier admission or new kappa'),
        'target': str(TARGET), 'stock': str(STOCK), 'width': WIDTH,
        'idle_mass': IDLE, 'idle_rank': CAP, 'coverage_law_total_mass': str(TOTAL),
        'baseline_profile': {str(r): n for r, n in BASE.items()},
        'payload_units': PAYLOAD,
        'predecessor_rows': rows,
        'certificates': {'merge_grid_checks': merges, 'payload_monotone_checks': mono,
                         'tax_dominance_checks': tax,
                         'transport_dominance_checks': trans},
        'shapes': {name: {'cap': capk,
                          'profile': {str(r): n for r, n in hist.items()},
                          'blocks': block_count}
                   for name, (capk, hist, block_count) in shapes.items()},
        'contracts': contracts,
        'uniform_restoration_tax': uniform,
        'budgets': budgets,
        'min_zero_charge_coverage': coverage,
        'tradeoff': tradeoff,
        'ceilings_coverage_law': ceilings,
        'ceilings_strict_contract': strict_ceilings,
        'small_instance_other_partitions': others,
        'checks': checks,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    engine = load_engine()
    expected = result(engine)
    if args.write:
        with open(HERE / 'RESULT.json', 'w', encoding='utf-8', newline='\n') as fh:
            fh.write(json.dumps(expected, indent=2, sort_keys=True) + '\n')
    else:
        actual = json.loads((HERE / 'RESULT.json').read_text(encoding='utf-8'))
        require(json.dumps(actual, sort_keys=True) == json.dumps(expected, sort_keys=True),
                'result receipt drift')
    b16 = expected['budgets']['greedy16']
    b51 = expected['budgets']['greedy51']
    c16 = expected['min_zero_charge_coverage']['cap16']
    print('PASS_RANK_SHAPE_COFRAME_BILL '
          'min_cover_cap16=%d slack_units_cap16=%d min_free_blocks_cap16=%d '
          'slack_units_cap51=%d min_cover_cap51=%d uniform_tax_excluded=1 no_new_kappa'
          % (c16['min_payloads_covered_strict_contract'],
             b16['slack_rank1_units_strict_contract'],
             b16['min_zero_charge_blocks_strict_contract'],
             b51['slack_rank1_units_strict_contract'],
             expected['min_zero_charge_coverage']['cap51']['min_payloads_covered_strict_contract']))


if __name__ == '__main__':
    main()
