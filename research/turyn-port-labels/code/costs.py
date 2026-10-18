"""Exact pressure comparisons for explicitly scoped Turyn accounting models."""
from fractions import Fraction
from functools import lru_cache
from math import expm1, floor, isqrt, log
from geometry import require, source_check
from screen import ln_bounds, exp_bounds

FRONTIER = Fraction(1612719427075359, 10**18)
STAGES = tuple(range(3, 102, 2))
CASES = [('full_h27', 23040, 27, 27), ('punctured_h27', 21504, 27, 24),
         ('hypothetical_full_h25', 23040, 25, 25),
         ('hypothetical_h27_width25', 23040, 27, 25)]
MODELS = ('literal_twolevel', 'hosting_aware_slots', 'no_bridge_split', 'idle_free')


@lru_cache(maxsize=None)
def logarithm(base):
    return ln_bounds(base, terms=24)


def idle_slots(pairs, d, split=True):
    slots = [2*(pairs-1)*d] if pairs > 1 else []
    for pair in range(1, pairs):
        slots.extend([2*pair*d, d] if split else [(2*pair+1)*d])
        if pairs-pair-1:
            slots.append(2*(pairs-pair-1)*d)
    return slots


def instance(n, h, width, stages, model):
    require(model in MODELS and stages >= 3 and stages % 2 == 1, 'Cost model parameters')
    pairs, d = (stages-1)//2, h-1
    m, center_bill = d*stages+1, 512*width
    stock, cap = (stages-1)*n, isqrt((d*stages+1)**2//2)
    deficit = stock-stages*center_bill
    terms = [(2*n*stages*d, Fraction(m, d)),
             (stages*center_bill, Fraction(m, width if model == 'literal_twolevel' else h))]
    if model != 'idle_free':
        for rank in idle_slots(pairs, d, model != 'no_bridge_split'):
            if model == 'literal_twolevel':
                full, remainder = divmod(rank, cap)
                if full:
                    terms.append((2*n*full*cap, Fraction(m, cap)))
                if remainder:
                    terms.append((2*n*remainder, Fraction(m, remainder)))
            else:
                terms.append((2*n*rank, Fraction(m, max(rank, h))))
    if model != 'idle_free':
        require(sum(mass for mass, _ in terms) == m*stock-deficit, 'Forced-slot mass identity')
    return dict(n=n, h=h, center_width=width, center_bill=center_bill, stages=stages,
                m=m, stock=stock, deficit=deficit, twolevel_cap=cap,
                terms=terms, logarithms=[logarithm(base) for _, base in terms])


def pressure_bounds(row, alpha):
    lower = upper = Fraction(0)
    for (mass, _), (low, high) in zip(row['terms'], row['logarithms']):
        a, b = exp_bounds(alpha*low, alpha*high, terms=12)
        lower += mass*(a-1)
        upper += mass*(b-1)
    return lower, upper


def nominate(row):
    if row['deficit'] <= 0:
        return 0.
    low, high = 0., .01
    for _ in range(60):
        mid = (low+high)/2
        pressure = sum(mass*expm1(mid*log(float(base))) for mass, base in row['terms'])
        if pressure < row['deficit']:
            low = mid
        else:
            high = mid
    return low


def scaled_interval(low, high, scale):
    return [low.numerator*scale//low.denominator,
            -((-high.numerator*scale)//high.denominator)]


def exact_root_bracket(row, alpha):
    scale = 10**15
    start = floor(alpha*scale)
    low, high = Fraction(start-2, scale), Fraction(start+3, scale)
    ll, lu = pressure_bounds(row, low)
    hl, hu = pressure_bounds(row, high)
    require(lu < row['deficit'] < hl, 'Certified nominal root bracket')
    return low, high


def comparison(row, target):
    alpha = target/(1-target)
    lower, upper = pressure_bounds(row, alpha)
    slack_low, slack_high = row['deficit']-upper, row['deficit']-lower
    return dict(target_kappa=str(target), pressure_slack_interval_scaled_1e12=
                scaled_interval(slack_low, slack_high, 10**12),
                verdict='HEADROOM_IN_THIS_RELAXATION' if slack_low > 0 else
                        'TARGET_FAILS_THIS_MODEL' if slack_high < 0 else 'UNDECIDED')


def above_deficit(row, alpha):
    # exp(x)-1 >= x often certifies nonwinning stages without evaluating
    # their exponential intervals. Close cases still use the full series.
    linear_lower = alpha*sum(mass*low for (mass, _), (low, _) in
                             zip(row['terms'], row['logarithms']))
    return linear_lower > row['deficit'] or pressure_bounds(row, alpha)[0] > row['deficit']


def run():
    sources = source_check()
    require(FRONTIER == Fraction(sources['frontier']['declared_kappa']), 'Frontier cost target')
    cases = []
    for name, n, h, width in CASES:
        models = []
        for model in MODELS:
            rows = [instance(n, h, width, stages, model) for stages in STAGES]
            positive = [row for row in rows if row['deficit'] > 0]
            best = max(positive, key=nominate)
            low, high = exact_root_bracket(best, nominate(best))
            # Certify the numerical nomination dominates every other stage in
            # the explicitly searched range. This is not a theorem outside it.
            require(all(row is best or above_deficit(row, low) for row in positive),
                    'Certified maximum over the recorded stage range')
            k_low, k_high = low/(1+low), high/(1+high)
            entry = {key: value for key, value in best.items() if key not in ('terms', 'logarithms')}
            entry.update(model=model, nominal_kappa_interval_scaled_1e18=
                         scaled_interval(k_low, k_high, 10**18),
                         best_in_searched_range_certified=True,
                         target_comparisons=[comparison(best, FRONTIER*factor)
                                             for factor in (1, Fraction(11, 10), Fraction(6, 5))])
            models.append(entry)
        cases.append(dict(name=name, models=models))
    full25 = [instance(23040, 25, 25, stages, 'literal_twolevel') for stages in (3, 5, 7, 9)]
    budget = [dict(stages=row['stages'], m=row['m'], stock=row['stock'],
        deficit=row['deficit'], idle_rank_mass=sum(2*row['n']*r for r in idle_slots((row['stages']-1)//2, 24)),
        target_comparisons=[comparison(row, FRONTIER*factor) for factor in (1, Fraction(11, 10), Fraction(6, 5))])
        for row in full25]
    return dict(status='PASS_SCOPED_TURYN_COST_COMPARISONS', frontier=sources['frontier'],
        accounting_source=sources['accounting_source'], searched_odd_stages=[3, 101],
        numerical_engine='Exact Fraction log/exponential intervals with 24/12 terms and tail bounds; floating arithmetic only nominates the certified maximum',
        cases=cases, fullport25_helper_pressure_budget=budget,
        scope='Conditional accounting models, not full-cost words. These calculations neither prohibit dimension 27 in general nor establish a new kappa.')
