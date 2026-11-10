"""Price two boundary extensions with every helper and idle charged.

The helper module and the directly corrected border lose for all binary
child sizes. The uncorrected border price is not a kappa result.
Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from fractions import Fraction as Q


def run(local, E, saving):
    def need(ok, message):
        if not ok:
            raise ValueError(message)
    tail, grid, t = 100, 2**40, 1-saving
    paid = {int(r): c for r, c in local['paid'].items()}
    helpers = {int(r): c for r, c in local['helpers'].items()}
    native = (E.moment(paid, t)[0]-E.moment(helpers, t)[1])/104
    down = lambda x: (x*grid).__floor__()
    up = lambda x: -(-x*grid).__floor__()
    H = lambda r: E.power(r, t)
    high = [grid]+[up(H(8*n+1)[1]) for n in range(1, tail)]
    low = [grid]+[down(H(8*n+1)[0]) for n in range(1, tail)]
    idle = [0]+[down(H(8*n)[0]) for n in range(1, tail)]
    costs = [0]*tail
    for n in range(2, tail):
        node = 2*idle[n]+grid-2*high[n]
        costs[n] = min(costs[a]+costs[n-a]+node for a in range(1, n))
    deficit = down(native)
    helper_best = corrected_best = None
    helper_count = corrected_count = 0
    for n in range(3, tail):
        for b in range(1, n-1):
            for a in range(1, (n-b)//2+1):
                c = n-a-b
                value = high[n]+high[a+b]+high[b+c]-low[b]-n*deficit-costs[a]-costs[b]-costs[c]
                helper_count += 1
                if helper_best is None or value > helper_best:
                    helper_best, helper_children = value, [a, b, c]
        for a in range(1, n//3+1):
            for b in range(a, (n-a)//2+1):
                c = n-a-b
                value = high[n]+high[a]+high[b]+high[c]-n*deficit-costs[a]-costs[b]-costs[c]-4*grid
                corrected_count += 1
                if corrected_best is None or value > corrected_best:
                    corrected_best, corrected_children = value, [a, b, c]
    need(helper_best < 0 and corrected_best < 0, 'Every finite triple loses with all required charges')
    n = tail
    helper_tail = H(8*n+1)[1]+2*H(4*n+5)[1]-H(9)[0]-n*(native-1)-3
    helper_slope = 8*t*(H(8*n+1)[1]/(8*n+1)+H(4*n+5)[1]/(4*n+5))-(native-1)
    third = E.divide(H(8*n+3), H(3))[1]
    corrected_tail = H(8*n+1)[1]+3*third-n*(native-1)-7
    corrected_slope = 8*t*(H(8*n+1)[1]/(8*n+1)+third/Q(8*n+3, 3))-(native-1)
    need(max(helper_tail, helper_slope, corrected_tail, corrected_slope) < 0,
         'Both all-size tails are negative and decreasing')

    # This is the diagonal limit of a fixed [6,6,6] border, not its finite word.
    targets = Counter({r: 18*c for r, c in helpers.items()})
    invoice = Counter({r: 18*c for r, c in paid.items()})
    targets.update({145: 104, 49: 936, 33: 624, 17: 1872})
    invoice.update({1: 1768, 16: 1872, 32: 624, 48: 624})
    def margin(k):
        a, b = E.moment(targets, 1-k), E.moment(invoice, 1-k)
        return a[0]-b[1], a[1]-b[0]
    lower, upper, denominator = 0, 10**12, 10**14
    while upper-lower > 1:
        mid = (lower+upper)//2
        if margin(Q(mid, denominator))[0] > 0:
            lower = mid
        else:
            upper = mid
    bracket = [Q(lower, denominator), Q(upper, denominator)]
    need(margin(bracket[0])[0] > 0 and margin(bracket[1])[1] < 0, 'Strict formal invoice crossing enclosure')
    goal = Q(101, 100)*saving
    need(margin(goal)[0] > 0, 'The uncorrected formal price exceeds the one-percent goal')
    return {'saving': str(saving), 'integer_grid': grid, 'tail_start': tail,
            'helper_module': {'finite_triples': helper_count, 'children': helper_children,
                              'finite_margin_upper': str(Q(helper_best, grid)),
                              'tail_upper': str(helper_tail), 'tail_derivative_upper': str(helper_slope),
                              'scope': 'All positive binary child sizes and shapes for the three-field module, with its consumed middle helper debited.'},
            'corrected_border': {'finite_triples': corrected_count, 'children': corrected_children,
                                 'finite_margin_upper': str(Q(corrected_best, grid)),
                                 'tail_upper': str(corrected_tail), 'tail_derivative_upper': str(corrected_slope),
                                 'scope': 'All positive binary child sizes and shapes for the star border with both direct rank-one corrections paid. Other recovery methods are not excluded.'},
            'formal_border': {'children': [6, 6, 6], 'raw_crossing': list(map(str, bracket)),
                              'one_percent_goal': str(goal), 'margin_at_goal': list(map(str, margin(goal))),
                              'paid_jobs': sum(invoice.values()), 'productive_fields': sum(targets.values()),
                              'paid': {str(r): c for r, c in invoice.items()},
                              'targets': {str(r): c for r, c in targets.items()},
                              'recovery_charges_included': False, 'is_kappa_result': False}}
