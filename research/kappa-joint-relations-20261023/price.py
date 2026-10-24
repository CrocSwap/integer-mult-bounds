"""Complete p16 bill and finite compiler for eight joint helper relations.

The interval and compiler proof follows Cao Yifan's PR4610 pricing, Cinna
Davis's PR4470 controller, zxv's completion and logarithmic majorant, and
Jacob Alan Sussman's mixed-target recursion. Apache-2.0.
Ali Romman, with substantial OpenAI Codex assistance.
"""
from collections import Counter
from fractions import Fraction as Q
from native import ROOT, read, load, need, encode, OLD_PAID, OLD_HELPERS, COUNT

KAPPA = Q('.00302666')
TESTED = Q('.00302667')
PREVIOUS = Q('.0030217758')
OLD_ROOT_UPPER = Q('.00302177587078')


def controller():
    """Check the literal p16 word and both rational boundary programs."""
    word = read(ROOT / 'research/joint-helper-lattice/CONTROLLER.json')
    need((word['kind'], word['pairs'], word['prefix_pairs'], word['ambient_rank']) == ('complex', 16, 7, 145), 'Source p16/a7 controller')
    zero = (0,) * 34
    def plus(dst, src, q):
        for k, v in src.items():
            value = dst.get(k, Q(0)) + q * v
            if value: dst[k] = value
            else: dst.pop(k, None)
    def shifted(row, term, sign=1):
        return [{tuple(a + b for a, b in zip(k, term)): sign * v for k, v in cell.items()} for cell in row]
    for side in ('left', 'right'):
        matrix = [[Q(i == j) for j in range(32)] for i in range(32)]
        for e in word['boundaries'][side + '_program']:
            if e[0] == 'SWAP': matrix[e[1]], matrix[e[2]] = matrix[e[2]], matrix[e[1]]
            elif e[0] == 'SCALE': matrix[e[1]] = [Q(e[2]) * x for x in matrix[e[1]]]
            else:
                need(e[0] == 'ADD', 'Boundary scalar opcode')
                matrix[e[1]] = [x + Q(e[3]) * y for x, y in zip(matrix[e[1]], matrix[e[2]])]
        need(matrix == [[Q(x) for x in row] for row in word['boundaries'][side]], 'Exact scalar boundary program')
    rows = [[{zero: Q(x)} if Q(x) else {} for x in row] for row in word['boundaries']['right']]
    for e in word['physical_events']:
        if e[0] in ('LOCAL', 'QUERY_SHEAR'):
            _, stage, pair, back = e
            x, y = 2 * pair, 2 * pair + 1
            if back: x, y = y, x
            term = (1 if back else -1,) + (0,) * 33
            for dst, src in zip(rows[y], shifted(rows[x], term)):
                plus(dst, src, Q(-1 if back else 1))
            if e[0] == 'LOCAL':
                term = (0,) + tuple(int(s == stage) for s in range(33))
                for r in (x, y): rows[r] = shifted(rows[r], term)
        elif e[0] == 'IDLE':
            term = (0,) + tuple(int(s in e[2]) for s in range(33))
            for r in (2 * e[1], 2 * e[1] + 1): rows[r] = shifted(rows[r], term)
        elif e[0] == 'ADD':
            for dst, src in zip(rows[e[1]], rows[e[2]]): plus(dst, src, Q(e[3]))
        else:
            need(e[0] in ('SWAP', 'SIGNED_SWAP'), 'Controller physical opcode')
            rows[e[1]], rows[e[2]] = rows[e[2]], shifted(rows[e[1]], zero, -1 if e[0] == 'SIGNED_SWAP' else 1)
    out = [[{} for _ in range(32)] for _ in range(32)]
    for i, row in enumerate(word['boundaries']['left']):
        for k, q in enumerate(row):
            if Q(q):
                for j in range(32): plus(out[i][j], rows[k][j], Q(q))
    expected = [[{tuple(word['diagonal'][i]): Q(1)} if i == j else {} for j in range(32)] for i in range(32)]
    need(out == expected, 'All p16 Laurent coefficients, central signs and boundary factors')
    return word


def assemble(native, word):
    T, P = Counter(), Counter()
    orientations = Counter(); thin = 0
    for e in word['physical_events']:
        if e[0] == 'LOCAL':
            direction = 'backward' if e[3] else 'forward'
            orientations[direction] += 1
            T.update(native[direction]['helpers']); P.update(native[direction]['paid'])
        elif e[0] == 'QUERY_SHEAR': thin += 1; P[1] += 112
        elif e[0] == 'IDLE': P[8 * len(e[2])] += 224
    main = Counter()
    for term in word['diagonal']:
        need(term[0] in (-1, 1) and all(x in (0, 1) for x in term[1:]), 'Whole Gaussian main target')
        main[1 + 8 * sum(term[1:])] += 112
    T.update(main)
    need(orientations == {'backward': 16, 'forward': 2} and thin == 15, 'Every actual call orientation')
    # This second census uses the source invoice and the complete local deltas.
    check_T = Counter({int(r): n for r, n in word['invoice']['main'].items()})
    check_T.update({r: 18 * n for r, n in OLD_HELPERS.items()}); check_T[9] -= 16 * COUNT
    check_P = Counter({int(r): n for r, n in word['invoice']['whole_idle'].items()})
    check_P.update({r: 18 * n for r, n in OLD_PAID.items()}); check_P[1] += 1680 - 16 * COUNT; check_P[8] -= 16 * COUNT
    need(T == check_T and P == check_P, 'Independent full invoice substitution')
    need(sum(T.values()) == 10800 and sum(P.values()) == 64148, 'Complete productive and paid counts')
    need(sum(r * n for r, n in T.items()) - sum(r * n for r, n in P.items()) == 752, 'Unchanged complete rank surplus')
    return T, P


def run(native):
    word = controller(); T, P = assemble(native, word)
    prior = read(ROOT / 'research/kappa-round6-compiler-tightening-20261022/ARITHMETIC.json')
    need(Q(prior['kappa']) == PREVIOUS and Q(prior['raw_root_interval'][1]) == OLD_ROOT_UPPER, 'Pinned prior conditional bound and raw crossing')
    prior_T = Counter({int(r): n for r, n in prior['targets'].items()})
    prior_P = Counter({int(r): n for r, n in prior['paid'].items()})
    prior_T[9] -= 16 * COUNT; prior_P[1] -= 16 * COUNT; prior_P[8] -= 16 * COUNT
    need(T == prior_T and P == prior_P, 'Complete delta from the final PR4610 bill')
    E = load('research/higher-moment-strictification/verify.py', 'owned_relation_intervals')
    other = load('research/kappa-rebuild/architecture/mixed_target_probe.py', 'owned_relation_second_intervals')
    def margin(c):
        t, p = E.moment(T, 1 - c), E.moment(P, 1 - c)
        return t[0] - p[1], t[1] - p[0]
    need(margin(Q('.00302238736348'))[0] > 0, 'Changed invoice beats the PR5377 raw crossing')
    need(margin(OLD_ROOT_UPPER)[0] > 0, 'Changed invoice beats the prior raw root upper endpoint')
    lo, hi, grid = 0, 10**12, 10**14
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if margin(Q(mid, grid))[0] > 0: lo = mid
        else: hi = mid
    root_low, root_high = Q(lo, grid), Q(hi, grid)
    need(margin(root_low)[0] > 0 and margin(root_high)[1] < 0, 'Strict rational root enclosure')
    need(PREVIOUS < KAPPA < TESTED < root_low, 'New bound and explicit compiler headroom')
    # The complete signed profile decreases on [0, .05], and stays negative
    # on [.05, 1]. This proves a fixed-profile ceiling, not a circuit ceiling.
    signed = {r: T[r] - P[r] for r in T.keys() | P.keys()}
    derivative, upper = None, None
    for i in range(16):
        l, r = Q(i, 320), Q(i + 1, 320); low = Q(0)
        for rank, n in signed.items():
            term = E.mul(E.power(rank, 1 - r if n > 0 else 1 - l), E.log_bounds(rank))
            low += n * term[0 if n > 0 else 1]
        derivative = low if derivative is None else min(derivative, low)
    for i in range(128):
        l, r = Q(1, 20) + Q(19 * i, 2560), Q(1, 20) + Q(19 * (i + 1), 2560)
        value = sum(n * E.power(rank, 1 - l if n > 0 else 1 - r)[1 if n > 0 else 0] for rank, n in signed.items())
        upper = value if upper is None else max(upper, value)
    need(derivative > 0 and upper < 0, 'Fixed-profile ceiling on all 0 < kappa < 1')
    t, u, v, c, b = 1 - TESTED, Q(1, 5), 1024, 20, 21
    target, paid = E.moment(T, t), E.moment(P, t)
    tl, th = other.moment(T, TESTED); pl, ph = other.moment(P, TESTED)
    need(tl > ph and max(tl, target[0]) <= min(th, target[1]) and max(pl, paid[0]) <= min(ph, paid[1]), 'Two exact interval engines agree')
    alpha = E.divide(paid, target)
    gamma = E.divide(E.moment(P, t + u), E.mul(E.power(c, u), target))
    delta = E.divide((Q(sum(T.values()) * b),) * 2, E.mul(E.power(c, TESTED), target))
    reserve = Q(1, 10**9); g = d = Q(97, 100)
    need(alpha[1] < 1 - reserve and gamma[1] < g and delta[1] < d, 'Original and completion tails charged')
    need(g**128 < Q(1, 16) and d**128 < Q(1, 16), 'Two strict tail decay blocks')
    normalized = 1 / (1 + v * reserve) + Q(4, 2**32)
    need(normalized < 1 and c**64 < b**63, 'Paid completion, splitting and rounding')
    theta, power = Q(63, 64), 1000
    eta = E.scale(E.power(145, -v * TESTED), t)
    need(2 * (20**v)**64 <= (145**v)**63 and eta[0] > theta**power, 'Shifted exits and complement capacity')
    need(E.power(145, v * TESTED)[1] < 2**power, 'Compiler initial range')
    gap = (TESTED - KAPPA) / 7; need(gap.numerator == 1, 'Finite integer grid')
    step = gap.denominator
    def wins(j): return (step * j + 1)**power < 2**j
    left, right = 1, 2
    while not wins(right): left, right = right, 2 * right
    while right - left > 1:
        mid = (left + right) // 2
        if wins(mid): right = mid
        else: left = mid
    height = step * right
    need(height > 8 * v and wins(right) and not wins(right - 1), 'Finite uniform-rank threshold')
    local_scalar = max(x['real_scalar_allowance'] for x in native.values())
    # Charge both routes for each of eight snapshots and eight owned helpers.
    # The eight owned helpers use existing physical slots.
    routes = (max(sum(x['paid'].values()) for x in native.values()) + 2 * 408 + 688 + 4 * COUNT) * 1000
    need(local_scalar + routes < 10**7, 'All new preparation, COPY, CLEAR and fixed routes fit')
    scalar_upper = 18 * 10**7 + 15 * 1792 + 32 * 112 * (len(word['physical_events']) + sum(len(word['boundaries'][k + '_program']) for k in ('left', 'right')))
    need(scalar_upper < 10**9, 'Complete raw nonrecursive bound')
    bit = read(ROOT / 'research/query-thinned-controllers/RESULT.json')['ordinary_BIT']
    atom = Q(bit['atom']); ordinary = (1 - atom) * Q(bit['after_cover']) + atom * Q('.0000384599'); admitted = Q(bit['admitted'])
    need(atom == Q('.004') and atom > ordinary > admitted > TESTED and atom < 1 - ordinary, 'Retained stronger BIT admission and stock')
    L = load('research/pr4359-p7-padding/dependencies/compiler-refill/endpoint.py', 'owned_relation_outer')
    params = {'kappa': KAPPA, 'tested_saving': TESTED, 'complex_uniform_saving': KAPPA + 6 * gap,
              'b': KAPPA + 5 * gap, 'a': KAPPA + 4 * gap, 'q': KAPPA + 3 * gap, 'bit_saving': admitted,
              'epsilon': 1 - gap, 'beta': 1 - 3 * gap, 'r0': gap / 10, 'stop': gap, 'layout': gap, 'd': gap}
    outer = L.ledger(params); outer['functional_checks']['actual_new_BIT_stock_sublinear'] = params['beta'] * (1 - atom)
    need(len(outer['strict_checks']) == 54 and len(outer['functional_checks']) == 4, 'Complete outer predicate inventory')
    need(all(x > 0 for key in ('strict_checks', 'functional_checks') for x in outer[key].values()), 'Every outer inequality is strict')
    controls = {}
    for name, patch in [('old_BIT', {'bit_saving': Q('.0027')}), ('closed_uniform', {'complex_uniform_saving': params['b']}), ('unfunded_endpoint', {'kappa': TESTED}), ('closed_epsilon', {'epsilon': Q(1)})]:
        bad = L.ledger(dict(params, **patch)); failed = [k for k, x in bad['strict_checks'].items() if x <= 0]
        need(failed, 'Reject outer patch ' + name); controls[name] = failed
    bad_native = {d: dict(x) for d, x in native.items()}
    bad_native['backward']['helpers'] = OLD_HELPERS
    try: assemble(bad_native, word)
    except ValueError: controls['unearned_helper_credit'] = 'Rejected by the independent complete census'
    else: raise ValueError('Unowned helper credit was accepted')
    return encode({'kappa': KAPPA, 'kappa_decimal': '.00302666', 'gain_over_PR4610': KAPPA - PREVIOUS,
                   'gain_over_PR5377': KAPPA - Q('.00302235'), 'PR5377_raw_root_upper': Q('.00302238736348'),
                   'raw_root_interval': [root_low, root_high], 'raw_headroom': [root_low - KAPPA, root_high - KAPPA],
                   'margin_at_previous_kappa': E.display(margin(PREVIOUS)),
                   'margin_at_previous_root_upper': E.display(margin(OLD_ROOT_UPPER)),
                   'fixed_profile_ceiling': {'decreasing_through': Q(1, 20), 'derivative_upper': E.display((-derivative,) * 2), 'remaining_interval_moment_upper': E.display((upper,) * 2)},
                   'targets': T, 'paid': P, 'productive_fields': sum(T.values()), 'paid_calls': sum(P.values()), 'rank_mass_surplus': 752,
                   'full_backward': 16, 'full_forward': 2, 'query_shears': 15,
                   'strictification': {'tested': TESTED, 'power': v, 'cutoff': c, 'floor': b, 'tail_offset': u, 'reserve': reserve, 'alpha': E.display(alpha), 'gamma': E.display(gamma), 'delta': E.display(delta), 'normalized_paid_upper': normalized},
                   'compiler': {'theta': theta, 'logarithm_power': power, 'eta': E.display(eta), 'gap': gap, 'uniform_saving': params['complex_uniform_saving'], 'H': height, 'N': '2^' + str(height), 'integer_test_exponent': right, 'word_materialized': False},
                   'nonrecursive': {'local_scalar': local_scalar, 'local_routes': routes, 'raw_scalar_upper': scalar_upper, 'raw_budget': 10**9, 'additional_private_slots': COUNT, 'owned_slots_backward': 2 * COUNT + 1},
                   'ordinary_BIT': bit, 'outer': outer, 'negative_controls': controls})
