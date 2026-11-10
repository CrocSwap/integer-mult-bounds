"""Bound the seven rank-four extensions of the classified mixed root.

All arithmetic is rational or integer. Integer table entries are outward
bounds, not rounded observations. The interval engine is by zxv.
Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as Q
from functools import reduce
from itertools import combinations, product

TAIL = 100
GRID = 2**40


def need(ok, message):
    if not ok:
        raise ValueError(message)


def admissible(masks):
    if any(not a & b for a, b in combinations(masks, 2)):
        return False
    for a, b, c in combinations(masks, 3):
        if (a | b | c).bit_count() < 4:
            return False
        if a & b == a & c == b & c and (a & b).bit_count() == 1:
            return False
    return all(reduce(int.__or__, group).bit_count() >= 6
               for group in combinations(masks, 5))


def run(local, E, saving):
    t = 1-saving
    paid = {int(r): c for r, c in local['paid'].items()}
    helpers = {int(r): c for r, c in local['helpers'].items()}
    native = (E.moment(paid, t)[0]-E.moment(helpers, t)[1])/104
    # Floor lower bounds and ceil upper bounds. Python integers do not overflow.
    def down(x):
        return (x*GRID).__floor__()
    def up(x):
        return -(-x*GRID).__floor__()
    powers = {r: E.power(r, t) for r in range(1, 8*TAIL+2)}
    h = [GRID]+[up(powers[8*n+1][1]) for n in range(1, TAIL)]
    idle = [0]+[down(powers[8*n][0]) for n in range(1, TAIL)]
    deficit = down(native)
    costs = [0]*TAIL
    for n in range(2, TAIL):
        node = 2*idle[n]+GRID-2*h[n]
        costs[n] = min(costs[a]+costs[n-a]+node for a in range(1, n))
    masks = [extra for extra in range(64) if extra.bit_count() == 4
             and admissible([3, 5, 11, 21, extra])]
    need(masks == [39, 43, 45, 46, 51, 53, 54], 'Complete support inventory')
    records = []
    for mask in masks:
        best, witness, checks, small_best = None, None, 0, None
        for e in range(1, TAIL-4):
            pairs = []
            for pair_bit, single_bit in ((1, 3), (2, 4)):
                table = {}
                for size in range(2, TAIL-e-1):
                    candidates = [(h[c+((mask >> single_bit) & 1)*e]-idle[c]
                                   -costs[c]-costs[size-c], c) for c in range(1, size)]
                    value, child = max(candidates)
                    table[size] = (h[size+((mask >> pair_bit) & 1)*e]+value, child)
                pairs.append(table)
            for left in range(2, TAIL-e-1):
                for right in range(2, TAIL-e-left):
                    total = left+right+e
                    value = (h[left+right+(mask & 1)*e]+pairs[0][left][0]+pairs[1][right][0]
                             +h[e]-2*idle[e]-costs[e]-total*deficit-2*GRID)
                    checks += 1
                    if total <= 10:
                        small_best = value if small_best is None else max(small_best, value)
                    if best is None or value > best:
                        c, d = pairs[0][left][1], pairs[1][right][1]
                        best, witness = value, [left-c, right-d, c, d, e]
        need(best < 0, 'Every positive child tuple below the tail loses')
        brute = []
        for sizes in product(range(1, 7), repeat=5):
            if sum(sizes) > 10:
                continue
            degrees = [sum(size*((support >> j) & 1)
                           for size, support in zip(sizes, (3, 5, 11, 21, mask)))
                       for j in range(6)]
            a, b, c, d, e = sizes
            brute.append(sum(h[q] for q in degrees)-sum(sizes)*deficit
                         -sum(costs[q] for q in sizes)-idle[c]-idle[d]-2*idle[e]-2*GRID)
        need(small_best == max(brute), 'The pair recurrence equals direct five-child enumeration')
        records.append({'mask': mask, 'finite_margin_upper': str(Q(best, GRID)),
                        'maximizing_upper_bound_children': witness, 'pair_total_checks': checks,
                        'direct_small_tuple_controls': len(brute)})

    # Each binary node is at least -1. Concavity gives the three tail
    # bounds in EXTENSIONS.md; each has a negative and decreasing derivative.
    H = lambda r: E.power(r, t)
    inc = H(9)[1]-H(8)[0]
    single = H(17)[1]-2*H(8)[0]+2*inc
    n = TAIL
    tail39 = H(8*n+1)[1]+2*H(4*n+5)[1]-H(8)[0]+3*inc-n*(native-1)-7
    tail43 = H(8*n+1)[1]+2*H(4*n+1)[1]+single-n*(native-1)-7
    rational_h = E.divide(H(16*n+3), H(3))[1]
    tail46 = 3*rational_h+single-n*(native-1)-7
    slope39 = 8*t*(H(8*n+1)[1]/(8*n+1)+H(4*n+5)[1]/(4*n+5))-(native-1)
    slope43 = 8*t*(H(8*n+1)[1]/(8*n+1)+H(4*n+1)[1]/(4*n+1))-(native-1)
    slope46 = 16*t*rational_h/Q(16*n+3, 3)-(native-1)
    need(max(tail39, tail43, tail46, slope39, slope43, slope46) < 0,
         'The three concave tails are negative and decreasing')
    return {'saving': str(saving), 'integer_grid': GRID, 'tail_start': TAIL,
            'finite': records, 'tail_upper': list(map(str, (tail39, tail43, tail46))),
            'tail_derivative_upper': list(map(str, (slope39, slope43, slope46))),
            'scope': 'All positive binary child sizes and all binary tree shapes for the seven rank-four extensions of the fixed two-endpoint, two-rank-three stage support pattern. No other support family is excluded.'}
