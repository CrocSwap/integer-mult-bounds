"""Direct charged geometric tails for the frozen eight-relation p16 bill.

The interval and compiler proof follows Cao Yifan's PR4610 pricing, Cinna
Davis's PR4470 controller, zxv's completion and logarithmic majorant, and
Jacob Alan Sussman's mixed-target recursion. Apache-2.0.
Derived from Ali Romman PR5377; eight-relation assembly by Dugongue,
with substantial OpenAI Codex assistance.
"""
from collections import Counter
from fractions import Fraction as Q
from strictify import completed_upper, tensor_power, logarithm_power, finite_threshold
from native import ROOT, read, load, need, encode, OLD_PAID, OLD_HELPERS

KAPPA = Q('.0030266747680744')
TESTED = Q('.0030266747680745')
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
    # This second census uses the source invoice and the directional profile deltas.
    check_T = Counter({int(r): n for r, n in word['invoice']['main'].items()})
    check_T.update({r: 18 * n for r, n in OLD_HELPERS.items()}); check_T[9] -= 128
    check_P = Counter({int(r): n for r, n in word['invoice']['whole_idle'].items()})
    check_P.update({r: 18 * n for r, n in OLD_PAID.items()}); check_P[1] += 1680 - 128; check_P[8] -= 128
    need(T == check_T and P == check_P, 'Independent full invoice substitution')
    need(sum(T.values()) == 10800 and sum(P.values()) == 64148, 'Complete productive and paid counts')
    need(sum(r * n for r, n in T.items()) - sum(r * n for r, n in P.items()) == 752, 'Unchanged complete rank surplus')
    return T, P


def run(native):
    word = controller(); T, P = assemble(native, word)
    from native import HERE
    predecessor = read(HERE / 'PREDECESSOR-5383.json')
    old = predecessor['arithmetic']
    need(Q(old['kappa']) == Q('.00302666'), 'Pinned concurrent eight-relation bound')
    need(T == Counter({int(r):n for r,n in old['targets'].items()}) and P == Counter({int(r):n for r,n in old['paid'].items()}), 'Same complete bill as PR5383')
    need(KAPPA > Q(old['kappa']), 'Strict compiler-margin improvement over PR5383')
    prior = read(ROOT / 'research/kappa-round6-compiler-tightening-20261022/ARITHMETIC.json')
    need(Q(prior['kappa']) == PREVIOUS and Q(prior['raw_root_interval'][1]) == OLD_ROOT_UPPER, 'Pinned prior conditional bound and raw crossing')
    prior_T = Counter({int(r): n for r, n in prior['targets'].items()})
    prior_P = Counter({int(r): n for r, n in prior['paid'].items()})
    prior_T[9] -= 128; prior_P[1] -= 128; prior_P[8] -= 128
    need(T == prior_T and P == prior_P, 'Complete delta from the final PR4610 bill')
    E = load('research/higher-moment-strictification/verify.py', 'owned_relation_intervals')
    other = load('research/kappa-rebuild/architecture/mixed_target_probe.py', 'owned_relation_second_intervals')
    def margin(c):
        t, p = E.moment(T, 1 - c), E.moment(P, 1 - c)
        return t[0] - p[1], t[1] - p[0]
    need(margin(OLD_ROOT_UPPER)[0] > 0, 'Changed invoice beats the prior raw root upper endpoint')
    lo, hi, grid = 302667476807000000, 302667476808000000, 10**20
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
    t, u, c, b = 1 - TESTED, Q(1, 5), 20, 21
    target, paid = E.moment(T, t), E.moment(P, t)
    tl, th = other.moment(T, TESTED); pl, ph = other.moment(P, TESTED)
    need(tl > ph and max(tl, target[0]) <= min(th, target[1]) and max(pl, paid[0]) <= min(ph, paid[1]), 'Two exact interval engines agree')
    alpha = E.divide(paid, target)
    gamma = E.divide(E.moment(P, t + u), E.mul(E.power(c, u), target))
    delta = E.divide((Q(sum(T.values()) * b),) * 2, E.mul(E.power(c, TESTED), target))
    reserve = Q(1, 10**17); g, d = Q(957,1000), Q(952,1000)
    v = tensor_power(reserve,g,d)
    need(alpha[1] < 1 - reserve and gamma[1] < g and delta[1] < d, 'Original and completion tails charged')
    normalized = completed_upper(v,reserve,g,d)
    need(normalized<1 and c**64<b**63, 'Complete geometric tails and rank separation')
    need(1/(1+v*reserve)+Q(4,2**32)>=1, 'Coarse predecessor tail bound fails at this power and reserve')
    theta=Q(63,64)
    eta=E.scale(E.power(145,-v*TESTED),t)
    initial=E.power(145,v*TESTED)
    power=logarithm_power(theta,eta[0],initial[1])
    need(2*(20**v)**64 <= (145**v)**63 and eta[0]>theta**power and initial[1]<2**power, 'Complete logarithmic compiler capacity')
    gap=(TESTED-KAPPA)/7
    threshold=finite_threshold(gap,power);height=threshold['H'];right=threshold['j']
    need(height>8*v, 'Finite uniform-rank threshold exceeds template scale')
    # Matched comparison: retain exactly PR5387's tested and claimed savings.
    prev=read(HERE/'RESULT.json')['arithmetic']
    prevC=Q(prev['strictification']['tested']);prevK=Q(prev['kappa']);prevRho=Q(prev['strictification']['reserve'])
    prevT=E.moment(T,1-prevC);prevP=E.moment(P,1-prevC)
    need(E.divide(prevP,prevT)[1]<1-prevRho, 'Matched comparison paid contraction')
    need(E.divide(E.moment(P,1-prevC+u),E.mul(E.power(c,u),prevT))[1]<g, 'Matched gamma')
    need(E.divide((Q(sum(T.values())*b),)*2,E.mul(E.power(c,prevC),prevT))[1]<d, 'Matched delta')
    cv=tensor_power(prevRho,g,d)
    ce=E.scale(E.power(145,-cv*prevC),1-prevC);ci=E.power(145,cv*prevC)
    cp=logarithm_power(theta,ce[0],ci[1]);ct=finite_threshold((prevC-prevK)/7,cp)
    need(c**64<b**63 and 2*(20**cv)**64 <= (145**cv)**63, 'Matched shifted exits and rank separation')
    need(ct['H']>8*cv and cv<prev['strictification']['power'] and ct['H']<prev['compiler']['H'], 'Strictly smaller matched product and uniform threshold')
    comparison={'kappa':prevK,'tested':prevC,'old_power':prev['strictification']['power'],'new_power':cv,'old_logarithm_power':prev['compiler']['logarithm_power'],'new_logarithm_power':cp,'old_H':prev['compiler']['H'],'new_H':ct['H'],'j':ct['j'],'complete_normalized_upper':completed_upper(cv,prevRho,g,d)}
    local_scalar = max(x['real_scalar_allowance'] for x in native.values())
    # The old route allowance is retained. Charge sixteen additional owned field
    # lifetimes at two routes each; the eight L pivots reuse existing slots.
    routes = (max(sum(x['paid'].values()) for x in native.values()) + 2 * 408 + 688 + 32) * 1000
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
    return encode({'matched_PR5387': comparison, 'gain_over_PR5387':KAPPA-Q('.003026674765'), 'gain_over_PR5383': KAPPA-Q('.00302666'), 'completion_reserve': reserve, 'kappa': KAPPA, 'kappa_decimal': '.0030266747680744', 'gain_over_PR4610': KAPPA - PREVIOUS,
                   'raw_root_interval': [root_low, root_high], 'raw_headroom': [root_low - KAPPA, root_high - KAPPA],
                   'margin_at_previous_kappa': E.display(margin(PREVIOUS)),
                   'margin_at_previous_root_upper': E.display(margin(OLD_ROOT_UPPER)),
                   'fixed_profile_ceiling': {'decreasing_through': Q(1, 20), 'derivative_upper': E.display((-derivative,) * 2), 'remaining_interval_moment_upper': E.display((upper,) * 2)},
                   'targets': T, 'paid': P, 'productive_fields': sum(T.values()), 'paid_calls': sum(P.values()), 'rank_mass_surplus': 752,
                   'full_backward': 16, 'full_forward': 2, 'query_shears': 15,
                   'strictification': {'tested': TESTED, 'power': v, 'cutoff': c, 'floor': b, 'tail_offset': u, 'gamma_envelope':g,'delta_envelope':d,'reserve': reserve, 'alpha': E.display(alpha), 'gamma': E.display(gamma), 'delta': E.display(delta), 'normalized_paid_upper': normalized},
                   'compiler': {'theta': theta, 'logarithm_power': power, 'eta': E.display(eta), 'gap': gap, 'uniform_saving': params['complex_uniform_saving'], 'H': height, 'N': '2^' + str(height), 'integer_test_exponent': right, 'word_materialized': False},
                   'nonrecursive': {'local_scalar': local_scalar, 'local_routes': routes, 'raw_scalar_upper': scalar_upper, 'raw_budget': 10**9, 'additional_private_slots': 8, 'owned_slots_backward': 17},
                   'ordinary_BIT': bit, 'outer': outer, 'negative_controls': controls})
