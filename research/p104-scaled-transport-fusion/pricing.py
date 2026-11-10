"""Check the complete mixed-projector-root invoice and outer transfer.

The interval and compiler bounds are by zxv and Cao Yifan. The productive
recursion is by Jacob Alan Sussman. The source price adapter is by Ali Romman.
The source lifts and tree invoice are by Ali Romman, with OpenAI Codex
assistance. This adapter keeps the root and changes the native source invoice.
It includes all nine output contractions and their productive target debits.
The original sources retain their credit. Apache-2.0.
"""
from collections import Counter
from fractions import Fraction as Q
from controller import formula_invoice, need

KAPPA = Q('0.003288299')
TESTED = Q('0.003288304')
PREVIOUS = Q('0.003287014')


def encode(value):
    if isinstance(value, Q):
        return str(value)
    if isinstance(value, dict):
        return {str(k): encode(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [encode(v) for v in value]
    return value


def assemble(local, native, word, physical):
    paid, targets = Counter(), Counter()
    counts = Counter(e[0] for e in word['events'])
    need(local['helpers'] == native['helpers'], 'All source helper targets have native maps')
    idle = Counter()
    for event in word['events']:
        if event[0] == 'LOCAL':
            paid.update(local['paid'])
            targets.update(local['helpers'])
        elif event[0] == 'QUERY':
            paid[1] += 104
        elif event[0] in ('IDLE', 'IDLE_ONE'):
            rank = 8*len(event[3] if event[0] == 'IDLE' else event[2])
            count = 208 if event[0] == 'IDLE' else 104
            paid[rank] += count
            idle[rank] += count
    main = Counter()
    for term in word['diagonal']:
        main[1+8*sum(term[1:])] += 104
    targets.update(main)
    need(main == physical['main_targets'], 'All main target phases and ranks')
    need(idle == physical['whole_idle_jobs'], 'All paired and individual whole idle jobs')
    need((targets, paid) == formula_invoice(local), 'Independent tree and emitted-event counts')
    need((counts['LOCAL'], counts['QUERY'], counts['IDLE']) == (18, 17, 14) and counts['IDLE_ONE'] == 2 and counts['LAMBDA'] == 20, 'Complete caller census')
    need((sum(targets.values()), sum(paid.values())) == (13652, 67096), 'All independent fields and paid calls')
    need(sum(r*n for r, n in targets.items())-sum(r*n for r, n in paid.items()) == 760, 'Complete rank-mass surplus')
    need((max(targets), max(paid)) == (145, 56), 'Maximum target and paid ranks')
    return targets, paid, counts


def run(local, native, word, physical, L):
    T, P, counts = assemble(local, native, word, physical)
    E = L.load(L.ROOT/'research/higher-moment-strictification/verify.py', 'balanced_intervals')
    other = L.load(L.ROOT/'research/kappa-rebuild/architecture/mixed_target_probe.py', 'balanced_second_intervals')
    def margin(k):
        a, b = E.moment(T, 1-k), E.moment(P, 1-k)
        return a[0]-b[1], a[1]-b[0]
    low, high, grid = 0, 10**24, 10**26
    while high-low > 1:
        middle = (low+high)//2
        if margin(Q(middle, grid))[0] > 0:
            low = middle
        else:
            high = middle
    lower, upper = Q(low, grid), Q(high, grid)
    signed = Counter(T)
    signed.subtract(P)
    cap, derivative_upper = Q('.0034'), Q(0)
    for rank, count in signed.items():
        logarithm = E.log_bounds(rank)
        a = E.mul(E.power(rank, 1-cap), logarithm)[0]
        b = rank*logarithm[1]
        derivative_upper -= count*(a if count >= 0 else b)
    need(derivative_upper < 0, 'Unique raw crossing below the BIT cap')
    need(margin(lower)[0] > 0 and margin(upper)[1] < 0, 'Strict rational crossing enclosure')
    endpoints = {}
    for label, k in [('lower', lower), ('upper', upper)]:
        tl, th = other.moment(T, k)
        pl, ph = other.moment(P, k)
        second = (tl-ph, th-pl)
        first = margin(k)
        need(max(first[0], second[0]) <= min(first[1], second[1]),
             'Both rational engines agree at the raw endpoint')
        need(second[0] > 0 if label == 'lower' else second[1] < 0,
             'The second engine certifies both raw endpoint signs')
        endpoints[label] = {'first': E.display(first), 'second': E.display(second)}
    need(PREVIOUS < KAPPA < TESTED < lower, 'The claim and tested saving are below the raw crossing')
    t, offset, power, cutoff, floor = 1-TESTED, Q(1, 7), 1920, 12, 13
    target, paid = E.moment(T, t), E.moment(P, t)
    tl, th = other.moment(T, TESTED)
    pl, ph = other.moment(P, TESTED)
    need(tl > ph and max(tl, target[0]) <= min(th, target[1])
         and max(pl, paid[0]) <= min(ph, paid[1]), 'Two independent rational moment engines')
    alpha = E.divide(paid, target)
    gamma = E.divide(E.moment(P, t+offset), E.mul(E.power(cutoff, offset), target))
    delta = E.divide((Q(sum(T.values())*floor),)*2, E.mul(E.power(cutoff, TESTED), target))
    reserve, decay = Q(1, 10**29), Q(31, 32)
    need(alpha[1] < 1-reserve and gamma[1] < decay and delta[1] < decay, 'All charged tail ratios')
    need(power % 128 == 0 and decay**128 < Q(1, 16), 'The previous block estimate applies')
    coarse_tail = 4*Q(1, 16)**(power//128)
    need(1/(1+power*reserve)+coarse_tail > 1, 'The coarse tail bound cannot fund this claim')
    exact_tail = 4*decay**power
    normalized = 1/(1+power*reserve)+exact_tail
    need(normalized < 1 and cutoff**64 < floor**63, 'Completion, splitting and rounding')
    theta, logarithm_power = Q(63, 64), 2100
    # Keep each exponential inside the retained engine's proved domain.
    half = E.power(145, Q(power, 2)*TESTED)
    factor = E.mul(half, half)
    eta = E.scale(E.divide((Q(1), Q(1)), factor), t)
    need(2*(cutoff**power)**64 <= (145**power)**63
         and eta[0] > theta**logarithm_power, 'Shifted exits and complement capacity')
    need(factor[1] < 2**logarithm_power, 'Compiler initial range')
    gap = (TESTED-KAPPA)/7
    need(gap.numerator == 1, 'Exact compiler integer grid')
    step = gap.denominator
    def wins(j):
        return (step*j+1)**logarithm_power < 2**j
    left, right = 1, 2
    while not wins(right):
        left, right = right, 2*right
    while right-left > 1:
        middle = (left+right)//2
        if wins(middle):
            right = middle
        else:
            left = middle
    H = step*right
    need(H > 8*power and wins(right) and not wins(right-1), 'Uniform threshold and adjacent-grid rejection')
    local_routes = (sum(local['paid'].values())+native['helper_normalizers']
                    +native['main_adapters']+4*104+4*local['owned_lifetimes'])*1000
    need(local['real_scalar_allowance']+local_routes < 10**7, 'Every local ordinary operation is funded')
    raw = 18*10**7 + 17*1664 + 32*34*104*len(word['events']) + 34*104*(26+1000)
    need(all(abs(Q(e[-1])) <= 16 for e in word['events'] if e[0] in ('ADD', 'SCALE')),
         'Every emitted scalar coefficient has the declared growth bound')
    need(all(Q(e[-1]).denominator & (Q(e[-1]).denominator-1) == 0
             for e in word['events'] if e[0] in ('ADD', 'SCALE')),
         'Every emitted rational scalar is dyadic')
    need(raw < 10**9, 'Complete ordinary-work budget')
    bit = L.read(L.ROOT/'research/query-thinned-controllers/RESULT.json')['ordinary_BIT']
    atom = Q(bit['atom'])
    ordinary = (1-atom)*Q(bit['after_cover']) + atom*Q('.0000384599')
    admitted = Q(bit['admitted'])
    need(atom > ordinary > admitted > TESTED and atom < 1-ordinary, 'Retained BIT admission and stock')
    outer_module = L.load(L.ROOT/'research/pr4359-p7-padding/dependencies/compiler-refill/endpoint.py', 'balanced_outer')
    params = {'kappa': KAPPA, 'tested_saving': TESTED, 'complex_uniform_saving': KAPPA+6*gap,
              'b': KAPPA+5*gap, 'a': KAPPA+4*gap, 'q': KAPPA+3*gap, 'bit_saving': admitted,
              'epsilon': 1-gap, 'beta': 1-3*gap, 'r0': gap/10, 'stop': gap, 'layout': gap, 'd': gap}
    outer = outer_module.ledger(params)
    outer['functional_checks']['actual_new_BIT_stock_sublinear'] = params['beta']*(1-atom)
    need(len(outer['strict_checks']) == 54 and len(outer['functional_checks']) == 4, 'Full outer predicate inventory')
    need(all(x > 0 for key in ('strict_checks', 'functional_checks') for x in outer[key].values()), 'Every outer inequality is strict')
    old_completion = E.divide((Q(sum(T.values())*17),)*2, E.mul(E.power(16, TESTED), target))
    need(old_completion[0] > 1, 'The old completion cutoff does not fund the new inventory')
    bad = outer_module.ledger(dict(params, bit_saving=Q('.0027')))
    need(any(x <= 0 for x in bad['strict_checks'].values()), 'Insufficient BIT saving rejected')
    return encode({'kappa': KAPPA, 'kappa_decimal': '0.003288299', 'previous_fixed_root': PREVIOUS,
                   'refinement_kind': 'Two scaled transport fusions with an output basis correction; unchanged mixed root.',
                   'gain': KAPPA-PREVIOUS, 'relative_gain_percent': 100*(KAPPA/PREVIOUS-1),
                   'raw_root_interval': [lower, upper], 'raw_headroom': [lower-KAPPA, upper-KAPPA],
                   'raw_endpoint_margins': endpoints,
                   'derivative_upper': derivative_upper, 'margin_at_previous': E.display(margin(PREVIOUS)),
                   'targets': T, 'paid': P, 'productive_fields': sum(T.values()), 'paid_calls': sum(P.values()),
                   'rank_mass_surplus': 760, 'full_forward_calls': 18, 'thin_queries': 17,
                   'whole_idle_jobs': 3120, 'strictification': {
                       'tested': TESTED, 'power': power, 'cutoff': cutoff, 'floor': floor,
                       'tail_offset': offset, 'reserve': reserve, 'tail_decay': decay,
                       'exact_tail_upper': exact_tail, 'coarse_tail_upper': coarse_tail,
                       'alpha': E.display(alpha), 'gamma': E.display(gamma), 'delta': E.display(delta),
                       'normalized_paid_upper': normalized},
                   'compiler': {'theta': theta, 'logarithm_power': logarithm_power, 'eta': E.display(eta),
                                'gap': gap, 'H': H, 'N': '2^'+str(H), 'integer_test_exponent': right,
                                'uniform_saving': params['complex_uniform_saving'], 'word_materialized': False},
                   'nonrecursive': {'local_scalar': local['real_scalar_allowance'], 'local_routes': local_routes,
                                    'raw_scalar_upper': raw, 'raw_budget': 10**9,
                                    'peak_owned_fields': local['peak_owned_fields'],
                                    'scalar_growth_bound': 'At most 2^(10^9 + R*f), where R is the full paid rank mass.',
                                    'paid_rank_mass': sum(r*n for r, n in P.items())},
                   'ordinary_BIT': bit, 'outer': outer,
                   'negative_controls': {'old_completion': 'Cutoff16 and floor17 give a ratio above one.',
                                         'old_BIT': 'An outer inequality fails at BIT saving0.0027.',
                                         'coarse_tail': 'The block tail bound cannot fund this near-limit claim.'}})
