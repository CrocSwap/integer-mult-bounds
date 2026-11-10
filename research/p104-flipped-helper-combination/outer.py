"""Source-bound #6916 interval and outer-ledger application to the new invoice."""
from collections import Counter
from fractions import Fraction as Q
from linear import HERE,load,need,read
PIN=Q(".00376669")

def verify_price(targets, paid, claim):
    interval_root = HERE / 'retained/6917/retained/runtime'
    first = load(interval_root / 'intervals.py', 'split_intervals')
    second = load(interval_root / 'second_intervals.py', 'split_second_intervals')
    outer = load(interval_root / 'endpoint.py', 'split_endpoint')
    kappa, tested, low, high = (Q(claim[k]) for k in ('kappa', 'tested', 'raw_lower', 'raw_upper'))
    bit = read(HERE / 'retained/6917/retained/bit/FRAGMENT-BIT-ADMISSION.json')
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
