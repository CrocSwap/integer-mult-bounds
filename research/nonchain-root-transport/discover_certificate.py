"""Optional LP certificate generation; replay needs only the Python standard library.

CubeJerry with substantial OpenAI GPT-6 Astra Pro assistance. Apache-2.0.
"""
from decimal import Decimal, ROUND_FLOOR
import json
import numpy as np
from scipy.optimize import linprog
from model import C, HERE, capacities

SCALE = 100_000_000

def down(x):
    return int((Decimal(str(float(x)))*SCALE).to_integral_value(rounding=ROUND_FLOOR))


def generate(p, q):
    intervals, caps, demands, targets = capacities(p, q)
    matrix = np.array([[int(c <= a and d >= b) for c, d in intervals]
                       for a, b in intervals], dtype=float)
    rows = [i for i, (a, b) in enumerate(intervals) if a == b]
    costs = np.array([(8*(b-a+1))**float(1-C) for a, b in intervals])
    result = linprog(costs, A_ub=matrix, b_ub=caps, A_eq=matrix[rows],
                     b_eq=demands, bounds=(0, None), method='highs')
    if not result.success:
        raise RuntimeError(result.message)
    alpha = [min(0, down(v)) for v in result.ineqlin.marginals]
    beta = [down(v)-2 for v in result.eqlin.marginals]
    return {'p': p, 'q': q, 'scale': SCALE,
            'alpha': {str(i): v for i, v in enumerate(alpha) if v}, 'beta': beta,
            'discovery_only': {'solver': 'scipy.optimize.linprog/HiGHS',
                'paid_objective': float(result.fun),
                'primal_intervals': [[a, b, float(result.x[i])] for i, (a, b) in enumerate(intervals)
                                     if result.x[i] > 1e-8]}}

if __name__ == '__main__':
    certificate = {'schema': 'mixed-mask-interval-dual/1', 'C': str(C),
                   'cases': [generate(4, 4), generate(1, 2)]}
    (HERE/'certificate.json').write_text(json.dumps(certificate, indent=2)+'\n')
    print('Wrote certificate.json; run verify.py independently.')
