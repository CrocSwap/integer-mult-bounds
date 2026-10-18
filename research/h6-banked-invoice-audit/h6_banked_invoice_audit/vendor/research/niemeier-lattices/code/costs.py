"""Exact necessary moment screens; no scalar word or exponent claim."""
from fractions import Fraction
from functools import lru_cache
import hashlib
import importlib.util
import json
from math import expm1, floor, log
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT.parent
FRONTIER = Fraction(1612719427075359, 10**18)
FACTORS = (Fraction(1), Fraction(11, 10), Fraction(6, 5), Fraction(3, 2), Fraction(2))
INTERVAL_SCALE = 10**40


def require(value, message):
    if not value:
        raise ValueError(message)


def source_check():
    specification = json.loads((ROOT/'sources/COST-SOURCES.json').read_text())
    for name, digest in specification['inherited_files'].items():
        require(hashlib.sha256((RESEARCH/name).read_bytes()).hexdigest() == digest, f'Cost source hash: {name}')
    for name, digest in specification['repository_files'].items():
        require(hashlib.sha256((RESEARCH.parent/name).read_bytes()).hexdigest() == digest,
                f'Frame lemma source hash: {name}')
    for name, source in specification['bit_source_files'].items():
        require(hashlib.sha256((ROOT/'sources'/name).read_bytes()).hexdigest() == source['sha256'],
                f'Bit comparison source hash: {name}')
    bit_data = (ROOT/'sources/PR543-EXPECTED.json').read_bytes()
    blob = b'blob '+str(len(bit_data)).encode()+b'\0'+bit_data
    require(hashlib.sha1(blob).hexdigest() == specification['bit_citation']['git_blob_sha1'],
            'Original cited bit receipt blob')
    require(FRONTIER == Fraction(specification['frontier']['declared_kappa']), 'Pinned comparison value')
    return specification


def verify_input_links(specification, receipts=None):
    """Bind cost parameters to independently replayed geometry or stated bounds."""
    names = ('E8-CUBED.json', 'E8-SECTIONS.json', 'D24.json')
    if receipts is None:
        receipts = {name: json.loads((ROOT/'evidence'/name).read_text()) for name in names}
    cube, sections, d24 = (receipts[name] for name in names)
    section = {case['blocks']: case for case in sections['cases']}
    expected = {}

    def add(name, ports, h, histogram, source):
        expected[name] = dict(ports=ports, binary_dimension=h,
                             center_width_histogram=histogram, source=source)

    add('E8_cubed_verified_factor', cube['norm_four_lines'], cube['fitting']['dimension'],
        cube['factorization']['center_width_histogram'], 'E8-CUBED.json: factorization')
    add('E8_cubed_all_full_width_fallback', cube['norm_four_lines'], cube['fitting']['dimension'],
        {'25': cube['factorization']['center_count']}, 'E8-CUBED.json: all centers charged at ambient width')
    for blocks, word in ((2, 'squared'), (3, 'cubed')):
        case = section[blocks]
        for suffix, field in (('Fano_factor', 'coordinate_factorization'),
                              ('Pauli_factor', 'operator_factorization')):
            add(f'E8_{word}_{suffix}', case['port_count'], case['fitting']['dimension'],
                case[field]['center_width_histogram'], f'E8-SECTIONS.json: blocks={blocks}, {field}')
    add('D24_verified_factor', d24['port_count'], d24['binary_dimension'],
        d24['center_width_histogram'], 'D24.json: full factor')
    omitted = d24['omitted_axis_variant']
    add('D24_omit_axes', omitted['port_count'], d24['binary_dimension'],
        omitted['center_width_histogram'], 'D24.json: omitted_axis_variant')
    # Restrict the certified unary identity to two blocks. Each block has
    # 56 repeated cubics, 56 distinct cubics and 16 unary centers; each
    # ordered block pair has 8*36 mixed centers. Full ambient width is safe.
    unary_count = 2*(56+56+16)+2*8*36
    add('E8_squared_unary_factor', section[2]['port_count'], section[2]['fitting']['dimension'],
        {'17': unary_count}, 'E8-CUBED.json: two-block restriction, ambient-width upper bound')
    add('E8_squared_pair_only', section[2]['port_count']-2*cube['e8_norm_four_lines'],
        section[2]['fitting']['dimension'], {'17': unary_count},
        'Same two-block factor restricted to pair ports, ambient-width upper bound')
    add('E8_root_reference', cube['e8_root_lines'], 9, {'9': 8},
        'Inherited eight-coordinate E8 root unit, ambient-width bound')
    add('D24_root_coordinate_unit', 24*23, 23, {'23': 24},
        'D_n root-coordinate formula at n=24')
    require(len(specification['cases']) == len(expected), 'Complete cost input coverage')
    require({case['name'] for case in specification['cases']} == set(expected), 'Unique cost case names')
    for case in specification['cases']:
        link = expected[case['name']]
        require(all(case[key] == link[key] for key in
                    ('ports', 'binary_dimension', 'center_width_histogram')),
                f'Cost input disagrees with geometry: {case["name"]}')
    return expected


path = RESEARCH/'leech-lattice/code/screen.py'
spec = importlib.util.spec_from_file_location('frozen_niemeier_moment_bounds', path)
engine = importlib.util.module_from_spec(spec)
spec.loader.exec_module(engine)


@lru_cache(maxsize=None)
def logarithm(base):
    low, high = engine.ln_bounds(base, terms=24)
    return rounded_bounds(low, high)


def rounded_bounds(low, high):
    # Outward rounding keeps all later sums on one rational denominator.
    # This preserves the proof intervals and avoids enormous denominator lcms.
    return (Fraction(low.numerator*INTERVAL_SCALE//low.denominator, INTERVAL_SCALE),
            Fraction(-((-high.numerator*INTERVAL_SCALE)//high.denominator), INTERVAL_SCALE))


@lru_cache(maxsize=None)
def power_bounds(base, alpha):
    low, high = logarithm(base)
    lower, upper = engine.exp_bounds(alpha*low, alpha*high, terms=12)
    return rounded_bounds(lower, upper)


def idle_slots(stages, d):
    pairs = (stages-1)//2
    slots = [2*(pairs-1)*d] if pairs > 1 else []
    for pair in range(1, pairs):
        slots.extend((2*pair*d, d))
        if pairs-pair-1:
            slots.append(2*(pairs-pair-1)*d)
    return slots


def instance(n, h, histogram, stages, relaxed=False):
    require(n > 0 and h >= 2 and stages >= 3 and stages % 2 == 1, 'Moment parameters')
    require(all(1 <= width <= h and count >= 0 for width, count in histogram.items()), 'Center widths')
    d, m = h-1, (h-1)*stages+1
    bill = sum(width*count for width, count in histogram.items())
    deficit = (stages-1)*n-stages*bill
    terms = [(2*n*stages*d, Fraction(m, d))]
    terms.extend((stages*width*count, Fraction(m, h if relaxed else width))
                 for width, count in sorted(histogram.items()) if count)
    terms.extend((2*n*rank, Fraction(m, max(rank, h))) for rank in idle_slots(stages, d))
    require(sum(mass for mass, _ in terms) == m*(stages-1)*n-deficit, 'Exact forced rank-mass identity')
    return dict(ports=n, binary_dimension=h, center_bill=bill, stages=stages, m=m,
                stock=(stages-1)*n, deficit=deficit, terms=terms)


def pressure_bounds(row, alpha):
    low = high = Fraction(0)
    for mass, base in row['terms']:
        lower, upper = power_bounds(base, alpha)
        low += mass*(lower-1)
        high += mass*(upper-1)
    return low, high


def nominate(row):
    if row['deficit'] <= 0:
        return 0.
    lo, hi = 0., .02
    for _ in range(60):
        a = (lo+hi)/2
        p = sum(mass*expm1(a*log(float(base))) for mass, base in row['terms'])
        if p < row['deficit']:
            lo = a
        else:
            hi = a
    return lo


def scaled(low, high, scale=10**18):
    return [low.numerator*scale//low.denominator, -((-high.numerator*scale)//high.denominator)]


def bracket(row):
    integer = floor(nominate(row)*10**15)
    lo, hi = Fraction(integer-2, 10**15), Fraction(integer+3, 10**15)
    require(pressure_bounds(row, lo)[1] < row['deficit'] < pressure_bounds(row, hi)[0], 'Certified root bracket')
    return lo, hi


def tail_bound(n, h, bill, alpha, start):
    # Active climbs and the (L-3)/2 bridge slots alone suffice. Each term
    # of this divided-by-L bound increases for real L >= start >= 3.
    d = h-1
    log_l = logarithm(Fraction(start))[0]
    log_bridge = logarithm(Fraction(d*start+1, h))[0]
    lower = d*alpha*(2*log_l+(1-Fraction(3, start))*log_bridge)
    return lower, Fraction(n-bill, n)


def dominates(row, alpha):
    linear = alpha*sum(mass*logarithm(base)[0] for mass, base in row['terms'])
    return linear > row['deficit'] or pressure_bounds(row, alpha)[0] > row['deficit']


def compare(row, target):
    alpha = target/(1-target)
    low, high = pressure_bounds(row, alpha)
    slack = row['deficit']-high, row['deficit']-low
    return dict(target_kappa=str(target), slack_interval_scaled_1e12=scaled(*slack, 10**12),
                verdict='NOMINAL_HEADROOM' if slack[0] > 0 else 'FAILS_NECESSARY_SCREEN' if slack[1] < 0 else 'UNDECIDED')


def optimize(n, h, histogram, relaxed=False):
    bill = sum(width*count for width, count in histogram.items())
    if bill >= n:
        return dict(status='NO_POSITIVE_DEFICIT', center_bill=bill,
                    proof='D=L*(N-C)-N is negative for every positive stage count')
    limit = 101
    while True:
        rows = [instance(n, h, histogram, stages, relaxed) for stages in range(3, limit+1, 2)]
        best = max(rows, key=nominate)
        low, high = bracket(best)
        tail_low, tail_right = tail_bound(n, h, bill, low, limit)
        if tail_low > tail_right:
            break
        limit = 2*limit-1
        require(limit <= 3201, 'Finite tail search resource bound')
    require(all(row is best or row['deficit'] <= 0 or dominates(row, low) for row in rows),
            'Selected stage strictly dominates every other finite candidate')
    return dict(status='CERTIFIED_GLOBAL_ODD_STAGE_MAXIMUM', best_stages=best['stages'], m=best['m'],
        center_bill=bill, stock=best['stock'], deficit=best['deficit'],
        kappa_interval_scaled_1e18=scaled(low/(1+low), high/(1+high)),
        finite_odd_stage_range=[3, limit], tail_start=limit,
        tail_pressure_lower_bound=str(tail_low), tail_deficit_upper_bound=str(tail_right),
        comparisons=[compare(best, FRONTIER*factor) for factor in FACTORS])


def extra_children_budget(row, target, child_rank, copies_per_call=1):
    alpha = target/(1-target)
    low, high = pressure_bounds(row, alpha)
    slack = row['deficit']-high, row['deficit']-low
    power_low, power_high = power_bounds(Fraction(row['m'], child_rank), alpha)
    cost_low = row['stages']*copies_per_call*child_rank*power_low
    cost_high = row['stages']*copies_per_call*child_rank*power_high
    if slack[0] < 0:
        return dict(child_rank=child_rank, copies_per_call=copies_per_call, admissible_count=0)
    lower, upper = slack[0]/cost_high, slack[1]/cost_low
    lo, hi = lower.numerator//lower.denominator, upper.numerator//upper.denominator
    require(lo == hi, 'Exact integer additional-child budget')
    require(lo*cost_high < slack[0] and (lo+1)*cost_low > slack[1],
            'Strict admissibility and rejection of the next child count')
    return dict(child_rank=child_rank, copies_per_call=copies_per_call, admissible_count=lo,
                scope='Additional paid children in every local call, no stock change and no hosting credit')


def center_threshold(h, target):
    alpha = target/(1-target)
    candidates = []
    for stages in range(3, 102, 2):
        row = instance(1, h, {}, stages, True)
        low, high = pressure_bounds(row, alpha)
        pl, ph = power_bounds(Fraction(row['m'], h), alpha)
        numerator_low, numerator_high = stages-1-high, stages-1-low
        # Once the numerator is negative, C >= 0 cannot pass at this stage.
        if numerator_high <= 0:
            continue
        require(numerator_low > 0, 'Resolved center-threshold numerator sign')
        candidates.append((numerator_low/(stages*ph), numerator_high/(stages*pl), stages))
    best = max(candidates, key=lambda item: item[0])
    require(all(item is best or item[1] < best[0] for item in candidates), 'Exact optimal center threshold stage')
    tl, tr = tail_bound(1, h, best[0], alpha, 101)
    require(tl > tr, 'All later stages have smaller center threshold')
    return dict(binary_dimension=h, target_kappa=str(target), best_stages=best[2],
                maximum_center_bill_per_port_interval_scaled_1e12=scaled(best[0], best[1], 10**12),
                scope='Relaxed center cap h and inherited hosting-aware slots; a necessary threshold')


def run():
    sources = source_check()
    specification = json.loads((ROOT/'evidence/COST-INPUTS.json').read_text())
    links = verify_input_links(specification)
    results = []
    for case in specification['cases']:
        histogram = {int(width): count for width, count in case['center_width_histogram'].items()}
        results.append(dict(name=case['name'], input_scope=case['scope'],
            fixed_center_widths=optimize(case['ports'], case['binary_dimension'], histogram),
            relaxed_center_cap=optimize(case['ports'], case['binary_dimension'], histogram, True)))
    budgets = []
    for name in specification['budget_cases']:
        candidate = next(case for case in specification['cases'] if case['name'] == name)
        histogram = {int(width): count for width, count in candidate['center_width_histogram'].items()}
        h = candidate['binary_dimension']
        for stages in (3, 5, 7, 9):
            row = instance(candidate['ports'], h, histogram, stages)
            entries = []
            for factor in FACTORS:
                target = FRONTIER*factor
                entries.append(dict(**compare(row, target), additional_children=[
                    extra_children_budget(row, target, rank, copies)
                    for rank, copies in ((1, 1), (h-1, 2))]))
            budgets.append(dict(candidate=name, stages=stages, m=row['m'], stock=row['stock'], deficit=row['deficit'],
                idle_rank_mass=sum(2*candidate['ports']*rank for rank in idle_slots(stages, h-1)), targets=entries))
    catalog = json.loads((ROOT/'catalog.json').read_text())
    uniform = []
    cap = center_threshold(25, FRONTIER)
    cap_upper = Fraction(cap['maximum_center_bill_per_port_interval_scaled_1e12'][1], 10**12)
    for lattice in catalog['lattices']:
        ratio = Fraction(65000, lattice['norm4_lines'])
        require(ratio > cap_upper, 'Uniform catalog baseline fails for all odd stages')
        uniform.append(dict(root_system=lattice['root_system'], ports=lattice['norm4_lines'],
            hypothetical_center_bill_per_port=str(ratio),
            result='FAILS_FRONTIER_FOR_EVERY_ODD_STAGE'))
    bit = json.loads((ROOT/'sources/PR543-EXPECTED.json').read_text())['nine']
    bit_low = Fraction(bit['bit_lower'])
    bit_high = bit_low+Fraction(1, 10**24)
    return dict(status='PASS_SCOPED_NIEMEIER_MOMENT_SCREENS', sources=sources,
        geometry_input_links=links, cases=results,
        additional_child_budgets=budgets,
        cited_bit_limitation=dict(moment_lower=str(bit_low), claimed_rejected_next_endpoint=str(bit_high),
            nominal_outer_cap_interval_scaled_1e18=scaled(bit_low/(1+bit_low), bit_high/(1+bit_high)),
            maximum_gain_over_frontier_percent_interval_scaled_1e12=scaled(
                100*(bit_low/(1+bit_low)/FRONTIER-1), 100*(bit_high/(1+bit_high)/FRONTIER-1), 10**12),
            scope='Retained PR543 bit supplier as cited and repriced by PR592. These upstream moment endpoints were read, not freshly replayed here. Larger overall gains require improving the bit supplier as well.'),
        necessary_center_thresholds=[center_threshold(h, FRONTIER*factor)
                                     for h in (23, 25) for factor in (1, Fraction(6, 5))],
        uniform_catalog_baseline=uniform,
        uniform_catalog_scope='Hypothetical h=25 and 2600 centers of width 25 for each norm-four shell; no rank, labeling, support or factorization claim for the other lattices',
        scope='Necessary one-supplier moment screens only. No native scalar word, helper inventory, physical hosting, bit supplier or outer transfer is supplied; no overall kappa improvement is claimed.')
