#!/usr/bin/env python3
"""Independent Decimal cross-check; not an acceptance certificate.

Prepared for @alephnan with substantial OpenAI Codex assistance. Apache-2.0.
Uses only the standard library and literal historical inventories, with no
imports from repository numerical sources. Decimal results are rounded, not
outward interval enclosures. The exact verifier remains the acceptance gate.
"""

from decimal import Decimal as D, localcontext
import json


P = {1: 37305, 2: 10695, 3: 3360, 4: 1530, 5: 300,
     8: 1464, 16: 448, 32: 448, 48: 448}
T = {5: 420, 6: 270, 7: 840, 8: 1395, 9: 3195,
     25: 448, 41: 448, 57: 448, 121: 224}
WIDTH = 121
PRECISION = 90
BISECTIONS = 200
BINOMIAL_TERMS = 512


def calculate():
    with localcontext() as context:
        context.prec = PRECISION
        logs = {r: D(r).ln() for r in set(P) | set(T) | {WIDTH}}
        centre = logs[5]
        s = D(99739) / 100000

        def tilted(alpha):
            powers = {r: (alpha * logs[r]).exp() for r in logs}
            mass = sum(D(count) * powers[r] for r, count in P.items())
            residual = sum(D(count) * powers[r] * (logs[r] - centre)
                           for r, count in P.items())
            return powers, mass, residual

        lo, hi = D('0.98981438244597'), D('0.98981438244599')
        endpoint_residuals = [tilted(lo)[2], tilted(hi)[2]]
        if not endpoint_residuals[0] < 0 < endpoint_residuals[1]:
            raise ArithmeticError('Diagnostic bisection endpoints do not straddle zero')
        for _ in range(BISECTIONS):
            mid = (lo + hi) / 2
            if tilted(mid)[2] > 0:
                hi = mid
            else:
                lo = mid
        alpha = (lo + hi) / 2
        pa, mass, residual = tilted(alpha)
        probabilities = {r: D(count) * pa[r] / mass for r, count in P.items()}
        variance = sum(probabilities[r] * (logs[r] - centre) ** 2 for r in P)
        third = sum(probabilities[r] * abs(logs[r] - centre) ** 3 for r in P)
        support = max(abs(logs[r] - centre) for r in P)
        target_mass = sum(D(count) * pa[k] for k, count in T.items())
        gap, ratio, tau = mass - target_mass, target_mass / mass, s - alpha
        ps = {r: (s * logs[r]).exp() for r in logs}
        terminal = sum(D(count) * ps[r] for r, count in P.items()) / ps[WIDTH]

        # Evaluate every paid/target pair directly. This deliberately does not
        # use the exact verifier's aggregation of coefficients by rank.
        boundary = sum(D(pr * tk) * (pa[k] * ps[r] - pa[r] * ps[k])
                       for r, pr in P.items() for k, tk in T.items() if r > k)
        capacity, coefficient = D(0), s
        for j in range(1, BINOMIAL_TERMS + 1):
            integrated_term = sum(
                D(pr * tk) * (pa[r] * (D(k) / WIDTH) ** j
                              - pa[k] * (D(r) / WIDTH) ** j)
                for r, pr in P.items() for k, tk in T.items() if k > r
            ) / (D(j) - alpha)
            capacity += coefficient * integrated_term
            coefficient *= (D(j) - s) / (j + 1)
        exit_value = (gap * terminal + boundary / ps[WIDTH]) / tau

        # Supplementary rounded check of the proof's conservative error budget.
        multiplier = WIDTH * sum(P.values()) * sum(T.values())
        retained = D(3 * multiplier) / 10**8
        middle = D(17 * multiplier) * (D(247) / 250) ** 3001
        high = D(8 * multiplier) / ((D(3) / 500) ** 2 * 10**18)
        error_total = retained + middle + high + D(1) / 5 + D(2) / 10**7

        return {
            'status': 'DIAGNOSTIC_NOT_ACCEPTANCE',
            'scope': ('Rounded supplementary cross-check only; no outward interval '
                      'enclosures or scientific acceptance decisions. Run verify.py '
                      'for the exact acceptance gate.'),
            'method': {'engine': 'Python standard-library decimal',
                       'precision': PRECISION, 'mean_bisections': BISECTIONS,
                       'binomial_terms': BINOMIAL_TERMS,
                       'repository_numerical_imports': False,
                       'capacity_evaluation': 'direct paid/target pair sum'},
            'literal_inputs': {'P': P, 'T': T, 'width': WIDTH},
            'alpha': str(alpha),
            'mean_endpoint_residuals': [str(x) for x in endpoint_residuals],
            'mean_residual_at_computed_alpha': str(residual),
            'probabilities': {str(r): str(probabilities[r]) for r in (1, 2, 3)},
            'variance': str(variance),
            'third_absolute_moment': str(third),
            'max_absolute_centered_support': str(support),
            'tilted_paid_mass': str(mass),
            'tilted_gap': str(gap),
            'tilted_target_ratio': str(ratio),
            'tau': str(tau),
            'terminal_coefficient': str(terminal),
            'capacity_512_direct_pair_sum': str(capacity),
            'boundary_plus_leaf': str(exit_value),
            'margin_512': str(capacity - exit_value),
            'error_budget': {'retained': str(retained), 'middle': str(middle),
                             'high': str(high), 'complete': str(error_total)},
        }


if __name__ == '__main__':
    print(json.dumps(calculate(), indent=2))
