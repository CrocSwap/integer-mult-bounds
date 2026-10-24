#!/usr/bin/env python3
"""Exact, explicitly unrealized acceptance budget for kappa = 1/250.

Three complex H8 -> H1 and two BIT H7 -> H1 replacements per BACKWARD
invocation would suffice arithmetically. No such replacement is supplied.
The final admission gate deliberately rejects this hypothetical construction.
Apache-2.0; substantial OpenAI Codex assistance. Retained interval/compiler,
native, controller, delayed-cover and outer authors retain their credit.
"""
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
from hashlib import sha256
import json

from snapshot_probe import load, need

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
KAPPA = Q(1, 250)
COMPLEX_LOCAL = {1: 2201, 2: 412, 3: 510, 4: 127, 5: 40, 8: 8}
BIT_LOCAL = {1: 1323, 2: 1342, 3: 79, 4: 44, 5: 102, 6: 11, 7: 19}


def encode(x):
    if isinstance(x, Q):
        return str(x)
    if isinstance(x, dict):
        return {str(k): encode(v) for k, v in x.items()}
    if isinstance(x, (tuple, list)):
        return [encode(v) for v in x]
    return x


def invoice(kind, replacements):
    ports, block = (112, 8) if kind == 'complex' else (111, 7)
    helpers = {4: 28, 7: 7, 8: 47, 9: 326} if kind == 'complex' else {8: 439}
    local = COMPLEX_LOCAL if kind == 'complex' else BIT_LOCAL
    # Actual p16 call directions: sixteen backward and two forward FULLs.
    target = Counter({r: 18*n for r, n in helpers.items()})
    paid = Counter({r: 18*n for r, n in local.items()})
    paid[1] += 15*ports
    target[1+18*block] += 2*ports
    for length in (7, 8):
        for j in range(1, length+1):
            target[1+block*(j+1)] += 2*ports
            paid[block*(j+1)] += 2*ports
    need(0 <= replacements <= (8 if kind == 'complex' else 9), 'Available centers')
    paid[block] -= 16*replacements
    paid[1] += 16*replacements
    need(all(n >= 0 for n in paid.values()), 'Nonnegative paid inventory')
    return target, +paid


def subtract(a, b):
    return a[0]-b[1], a[1]-b[0]


def moment_margin(E, kind, replacements, saving):
    t, p = invoice(kind, replacements)
    return subtract(E.moment(t, 1-saving), E.moment(p, 1-saving))


def logarithmic_compiler(E, ambient, tested, uniform, cutoff, floor):
    v, theta, exponent = 1024, Q(63, 64), 2000
    # The retained elementary exp kernel has an explicit |argument| < 16
    # contract. Range-reduce here instead of weakening that source guard.
    def wide_power(a):
        reduced = a
        squares = 0
        while abs(reduced)*E.log_bounds(ambient)[1] >= 8:
            reduced /= 2
            squares += 1
        result = E.power(ambient, reduced)
        for _ in range(squares):
            result = E.mul(result, result)
        return result
    eta = E.scale(wide_power(-v*tested), 1-tested)
    need(cutoff**64 < floor**63, 'Strict paid/target rank separation')
    need(2*(cutoff**v)**64 <= (ambient**v)**63, 'Shifted exit bound')
    need(eta[0] > theta**exponent, 'Logarithmic complement capacity')
    need(wide_power(v*tested)[1] < 2**exponent, 'Initial ordinary range')
    gap = tested-uniform
    need(gap.numerator == 1, 'Integer rank grid')
    step = gap.denominator

    def passes(j):
        return (step*j+1)**exponent < 2**j

    lo, hi = 1, 2
    while not passes(hi):
        lo, hi = hi, 2*hi
    while hi-lo > 1:
        mid = (hi+lo)//2
        if passes(mid):
            hi = mid
        else:
            lo = mid
    need(passes(hi) and not passes(hi-1), 'Exact compiler threshold')
    return {'ambient_base': ambient, 'logarithm_power': exponent, 'gap': gap,
            'H': step*hi, 'uniform_N': '2^'+str(step*hi), 'eta': E.display(eta),
            'winning_uniform_word_materialized': False}


def tail(E, kind, replacements, tested, uniform, cutoff, floor):
    t, p = invoice(kind, replacements)
    target = E.moment(t, 1-tested)
    alpha = E.divide(E.moment(p, 1-tested), target)
    gamma = E.divide(E.moment(p, 1-tested+Q(1, 5)), E.mul(E.power(cutoff, Q(1, 5)), target))
    delta = E.divide((Q(sum(t.values())*floor),)*2, E.mul(E.power(cutoff, tested), target))
    need(alpha[1] < 1-Q(1, 1000000), 'Strict raw moment gap')
    need(gamma[1] < Q(97, 100) and delta[1] < Q(97, 100), 'Both charged tails')
    need(Q(97, 100)**128 < Q(1, 16), 'Tail decay block')
    complete = 1/(1+1024*Q(1, 1000000))+Q(4, 2**32)
    need(complete < 1, 'Original and completion tails both included')
    return {'tested': tested, 'uniform': uniform, 'targets': t, 'paid': p,
            'alpha': E.display(alpha), 'gamma': E.display(gamma), 'delta': E.display(delta),
            'tensor_power': 1024, 'cutoff': cutoff, 'floor': floor,
            'complete_normalized_paid_upper': complete,
            'compiler': logarithmic_compiler(E, 145 if kind == 'complex' else 127,
                                             tested, uniform, cutoff, floor)}


def main():
    E = load('k004_exact_intervals', ROOT/'research/higher-moment-strictification/verify.py')
    O = load('k004_outer_ledger', ROOT/'research/pr4359-p7-padding/dependencies/compiler-refill/endpoint.py')
    tested, d = Q('0.00405'), Q(1, 140000)
    complex_uniform = KAPPA+6*d
    rows = {}
    for kind, min_count in (('complex', 3), ('bit', 2)):
        margins = {str(n): E.display(moment_margin(E, kind, n, KAPPA)) for n in range(5)}
        need(moment_margin(E, kind, min_count-1, KAPPA)[1] < 0, 'One fewer center fails: '+kind)
        need(moment_margin(E, kind, min_count, KAPPA)[0] > 0, 'Sufficient center budget: '+kind)
        rows[kind] = {'hypothetical_centers_per_backward_call': min_count,
                      'raw_margins_at_kappa_004': margins}
    c = tail(E, 'complex', 3, tested, complex_uniform, 20, 21)
    b = tail(E, 'bit', 2, Q('.0041'), Q('.00409'), 17, 18)
    before, after, atom, old = Q('.00409'), Q('.00408'), Q('.005'), Q('.0000384599')
    ordinary, admitted = (1-atom)*after+atom*old, Q('.00405')
    need(before > after and atom > ordinary > admitted and atom < 1-ordinary, 'Ordinary BIT admission')
    need(2**26 > 256/(before-after), 'Delayed-cover prime coefficient')
    params = {'kappa': KAPPA, 'tested_saving': tested, 'complex_uniform_saving': complex_uniform,
              'b': KAPPA+5*d, 'a': KAPPA+4*d, 'q': KAPPA+3*d, 'bit_saving': admitted,
              'epsilon': 1-d, 'beta': 1-3*d, 'r0': d/10, 'stop': d, 'layout': d, 'd': d}
    outer = O.ledger(params)
    outer['functional_checks']['actual_new_BIT_stock_sublinear'] = params['beta']*(1-atom)
    failures = [k for part in ('strict_checks', 'functional_checks')
                for k, v in outer[part].items() if v <= 0]
    need(not failures, 'Strict nine-row outer ledger')
    # These are real gates: favorable arithmetic never substitutes for a word.
    obligations = {'complex_replacement_word': False, 'bit_replacement_word': False,
                   'arbitrary_input_endpoint_replay': False, 'phase_and_all_width_binding': False,
                   'ordinary_precision_tape_tariff': False}
    admitted_construction = not failures and all(obligations.values())
    need(not admitted_construction, 'Unrealized construction is rejected')
    out = {'status': 'PASS_CONDITIONAL_BUDGET_ONLY_PHYSICAL_CONSTRUCTION_MISSING',
           'target_kappa': KAPPA, 'new_kappa_claimed': False,
           'cost_model': 'Exact native endpoint and every independent helper preserved; remove selected centers only in the sixteen backward FULLs, and replace each by one H1. Ordinary work is a separate unresolved contract.',
           'minimum_replacements_in_this_model': rows, 'complex': c, 'bit': b,
           'ordinary_BIT': {'before_cover': before, 'after_cover': after, 'atom': atom,
                            'ordinary_saving': ordinary, 'admitted': admitted},
           'outer_parameters': params, 'outer': outer, 'missing_obligations': obligations,
           'admitted_construction': admitted_construction,
           'exact_engine_sha256': sha256((ROOT/'research/higher-moment-strictification/verify.py').read_bytes()).hexdigest()}
    (HERE/'evidence/acceptance-budget.json').write_text(json.dumps(encode(out), indent=2)+'\n')
    print(json.dumps({'status': out['status'], 'target_kappa': str(KAPPA),
                     'ordinary_BIT': str(ordinary), 'outer_failures': failures,
                     'admitted_construction': admitted_construction}))


if __name__ == '__main__':
    main()
