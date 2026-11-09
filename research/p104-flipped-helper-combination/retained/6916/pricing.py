"""Recount the complete unchanged-caller invoice and conditional outer price.

Adapted from the pinned #6902 pricing check. @CubeJerry with substantial OpenAI
assistance; predecessor credits and inherited assumptions are in README.md.
No floating-point result is used as a mathematical acceptance condition.
"""
from collections import Counter
from fractions import Fraction as Q
from linear import HERE, load, main_roles, need, read

PIN = Q('.00376669')


def native_census(word):
    dimensions = list(map(len, word['frames']))
    main = main_roles(word)
    targets = Counter(dimensions[b] - dimensions[a]
                      for r, (a, b) in enumerate(zip(word['initial'], word['final']))
                      if r not in main)
    paid = Counter(abs(dimensions[e[3]] - dimensions[e[2]])
                   for e in word['program'] if e[0] == 'MOVE')
    return targets, paid


def caller_invoice(word, caller):
    """Charge actual caller opcodes; no inherited invoice is treated as output."""
    local_targets, local_paid = native_census(word)
    targets, paid = Counter(), Counter()
    hosts = 0
    for e in caller['events']:
        if e[0] == 'HOST2':
            targets.update(local_targets)
            paid.update(local_paid)
            hosts += 1
        elif e[0] == 'QUERY':
            paid[1] += 104
        elif e[0] == 'IDLE_ONE':
            need(e[2], 'Nonempty one-field idle')
            paid[8 * len(e[2])] += 104
        else:
            need(e[0] in ('LAMBDA', 'ADD', 'SCALE', 'SWAP'), 'Known ordinary caller opcode')
    for exponent, zero, *stage_mask in caller['diagonal']:
        rank = int(exponent % 2) + 8 * sum(stage_mask)
        need(rank > 0, 'Positive whole caller target')
        targets[rank] += 104
    need(hosts == 18, 'Eighteen unchanged native calls')
    return targets, paid


def root_invoice(word, root):
    """Independent root/mask derivation of the wrapper jobs, as in #6902."""
    local_targets, local_paid = native_census(word)
    targets, paid, hosted = Counter(), Counter(), Counter()
    for role in range(root['n']):
        mask_stages = [k for k, stage in enumerate(root['stages']) if role in stage['mask']]
        active = [k for k in mask_stages
                  if any(Q(root['Y'][unit][role]) for unit in root['stages'][k]['units'])]
        targets[8 * len(mask_stages) + 1] += 104
        for k in active:
            hosted[k] += 1
        run, previous = 0, None
        for k in mask_stages:
            if k in active:
                if run:
                    paid[8 * run] += 104
                run, previous = 0, None
                continue
            if previous is not None and k == previous + 1:
                run += 1
            else:
                if run:
                    paid[8 * run] += 104
                run = 1
            previous = k
        if run:
            paid[8 * run] += 104
    for k in range(len(root['stages'])):
        if hosted[k] > 4:
            paid[8] += 104 * (hosted[k] - 4)
    thin = root['N'] - sum(len(stage['units']) for stage in root['stages'])
    paid[1] += 104 * thin
    for r, count in local_targets.items():
        targets[r] += 18 * count
    for r, count in local_paid.items():
        paid[r] += 18 * count
    return targets, paid


def ordinary_bound(word, caller, ledger):
    def swaps(axes):
        return len(set(axes) - set(range(len(axes))))
    main_maps = 0
    for exponent, zero, *selection in caller['diagonal']:
        axes = ([0] if exponent else []) + [axis
                for stage, selected in enumerate(selection, 1) if selected
                for axis in range(9 + 8 * (stage - 1), 9 + 8 * stage)]
        main_maps += 104 * (2 * swaps(axes) + 2 * bool(exponent) + int(exponent == -1))
    idle_maps = query_maps = 0
    for e in caller['events']:
        if e[0] == 'IDLE_ONE':
            axes = [axis for stage in e[2]
                    for axis in range(9 + 8 * (stage - 1), 9 + 8 * stage)]
            idle_maps += 104 * 2 * swaps(axes)
        elif e[0] == 'QUERY':
            query_maps += 104 * (2 + int(e[3] == -1))
    roles, events = caller['roles'], caller['events']
    rest = (32 * roles * 104 * len(events)
            + sum(e[0] == 'QUERY' for e in events) * 16 * 104
            + roles * 104 * 26 + 1000 * (main_maps + idle_maps + query_maps))
    routes = (sum(ledger['paid'].values()) + 2 * sum(ledger['helpers'].values())
              + 416 + 8 * 104 + 4 * ledger['owned_lifetimes']) * 1000
    per_allowance = ledger['scalar_allowance'] + routes
    per_upper = ledger['scalar_upper'] + routes
    need(per_upper >= per_allowance, 'Reviewed scalar upper covers total allowance')
    raw_allowance, raw_upper = 18 * per_allowance + rest, 18 * per_upper + rest
    need(raw_upper < 10 ** 9, 'Complete ordinary raw budget below 10^9')
    return dict(routes_per_call=routes, caller_rest=rest,
                per_call_allowance=per_allowance, per_call_reviewed_upper=per_upper,
                raw_allowance=raw_allowance, raw_reviewed_upper=raw_upper,
                margin_under_billion=10 ** 9 - raw_upper)


def verify_price(targets, paid, claim):
    interval_root = HERE / 'retained/retained/runtime'
    first = load(interval_root / 'intervals.py', 'split_intervals')
    second = load(interval_root / 'second_intervals.py', 'split_second_intervals')
    outer = load(interval_root / 'endpoint.py', 'split_endpoint')
    kappa, tested, low, high = (Q(claim[k]) for k in ('kappa', 'tested', 'raw_lower', 'raw_upper'))
    bit = read(HERE / 'retained/retained/bit/FRAGMENT-BIT-ADMISSION.json')
    need(bit['status'] == 'PASS_TWO_FRAGMENTS_BIT_ORDINARY_00376669'
         and Q(bit['ordinary_admitted']) == PIN, 'Explicit inherited open BIT admission pin')
    need(kappa < tested < low < high < PIN, 'Headline, tested price, and raw interval order')
    need(Q(bit['raw_crossing'][0]) > Q(bit['raw_tested']) > PIN,
         'Inherited BIT admission margins')
    for label, saving, sign in (('lower', low, 1), ('upper', high, -1), ('tested', tested, 1)):
        tl, th = first.moment(targets, 1 - saving)
        pl, ph = first.moment(paid, 1 - saving)
        al, ah = second.moment(targets, saving)
        bl, bh = second.moment(paid, saving)
        need((tl > ph and al > bh) if sign > 0 else (th < pl and ah < bl),
             ('Two rational interval engines certify the signed margin', label))
    signed = Counter(targets)
    signed.subtract(paid)
    derivative_upper = Q(0)
    for rank, coefficient in signed.items():
        logarithm = first.log_bounds(rank)
        bound = (first.mul(first.power(rank, 1 - PIN), logarithm)[0]
                 if coefficient >= 0 else rank * logarithm[1])
        derivative_upper -= coefficient * bound
    need(derivative_upper < 0, 'Unique raw crossing below the BIT pin')

    cutoff, floor, power, offset = 11, 12, 1920, Q(1, 7)
    logarithm_power = claim['logarithm_power']
    exponent = 1 - tested
    target_moment = first.moment(targets, exponent)
    alpha = first.divide(first.moment(paid, exponent), target_moment)
    gamma = first.divide(first.moment(paid, exponent + offset),
                         first.mul(first.power(cutoff, offset), target_moment))
    delta = first.divide((Q(sum(targets.values()) * floor),) * 2,
                         first.mul(first.power(cutoff, tested), target_moment))
    reserve, decay = Q(1, 10 ** 27), Q(31, 32)
    need(alpha[1] < 1 - reserve and gamma[1] < decay and delta[1] < decay,
         'All three tail ratios with every added target field counted')
    need(1 / (1 + power * reserve) + 4 * decay ** power < 1,
         'Power-1920 composite contraction')
    max_rank = max(targets)
    # A native contact has nine axes; each of the eighteen caller stages
    # introduces eight more.  The largest productive rank (145) is smaller
    # than this physical ambient cap (153).  They are different quantities.
    ambient = claim['physical_ambient_cap']
    need(ambient == 153 and max_rank == 145 and max_rank <= ambient,
         'Actual caller ambient cap separately bounds every productive rank')
    quarter = first.power(ambient, Q(power, 4) * tested)
    factor = first.mul(first.mul(quarter, quarter), first.mul(quarter, quarter))
    eta = first.scale(first.divide((Q(1), Q(1)), factor), exponent)
    need(eta[0] > Q(63, 64) ** logarithm_power and factor[1] < 2 ** logarithm_power,
         'Compiler complement capacity at the explicitly enlarged logarithm power')
    need(cutoff ** 64 < floor ** 63
         and 2 * (cutoff ** power) ** 64 <= (ambient ** power) ** 63,
         'Shifted integer exits')
    gap = (tested - kappa) / 7
    need(gap.numerator == 1, 'Exact reciprocal compiler grid')
    step = gap.denominator
    def wins(j):
        return (step * j + 1) ** logarithm_power < 2 ** j
    lo, hi = 1, 2
    while not wins(hi):
        lo, hi = hi, 2 * hi
    while hi - lo > 1:
        middle = (lo + hi) // 2
        if wins(middle):
            hi = middle
        else:
            lo = middle
    need(step * hi > 8 * power and wins(hi) and not wins(hi - 1),
         'Exact uniform threshold and failed predecessor grid point')
    parameters = dict(kappa=kappa, tested_saving=tested,
                      complex_uniform_saving=kappa + 6 * gap,
                      b=kappa + 5 * gap, a=kappa + 4 * gap, q=kappa + 3 * gap,
                      bit_saving=PIN, epsilon=1 - gap, beta=1 - 3 * gap,
                      r0=gap / 10, stop=gap, layout=gap, d=gap)
    ledger = outer.ledger(parameters)
    ledger['functional_checks']['actual_new_BIT_stock_sublinear'] = parameters['beta'] * (1 - Q(1, 250))
    need(len(ledger['strict_checks']) == 54 and len(ledger['functional_checks']) == 4
         and all(value > 0 for group in ('strict_checks', 'functional_checks')
                 for value in ledger[group].values()), 'Complete outer 54 strict and 4 functional checks')
    bad = outer.ledger(dict(parameters, bit_saving=parameters['a'] - Q(1, 10 ** 12)))
    need(any(value <= 0 for group in ('strict_checks', 'functional_checks')
             for value in bad[group].values()), 'Insufficient BIT pin control fails')
    plus, minus = [(7, 1), (3, 1), (5, 1)], [(9, 1), (4, 1), (1, 2)]
    def log_derivative(terms):
        lo = hi = Q(0)
        for rank, count in terms:
            a, b = first.mul((Q(rank), Q(rank)), first.log_bounds(rank))
            lo += count * a
            hi += count * b
        return lo, hi
    second_bound = sum(count * first.mul(first.mul((Q(rank), Q(rank)), first.log_bounds(rank)),
                                         first.log_bounds(rank))[1] for rank, count in plus + minus)
    positive, negative = log_derivative(plus), log_derivative(minus)
    derivative = (positive[0] - negative[1], positive[1] - negative[0])
    need(derivative[1] + PIN * second_bound < 0, 'Inherited input-lift saving lemma through the BIT pin')
    for saving in (kappa, tested):
        margin = (sum(count * first.power(rank, 1 - saving)[0] for rank, count in plus)
                  - sum(count * first.power(rank, 1 - saving)[1] for rank, count in minus))
        need(margin > 0 and saving * (-derivative[1]) - saving * saving * second_bound / 2 > 0,
             'Input-lift saving at headline and tested price')
    return dict(kappa=str(kappa), tested=str(tested), bit_pin=str(PIN),
                threshold=str(step * hi), logarithm_power=logarithm_power,
                maximum_productive_rank=max_rank, physical_ambient_cap=ambient,
                strict_checks=54, functional_checks=4,
                alpha_upper_diagnostic=float(alpha[1]), gamma_upper_diagnostic=float(gamma[1]),
                delta_upper_diagnostic=float(delta[1]))
