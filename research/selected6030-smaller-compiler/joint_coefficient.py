#!/usr/bin/env python3
"""Exact selected-profile net coefficient certificate for the optional joint application.
@CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
Intervals reused unchanged from zxv #4480; no native admission asserted.
"""
from pathlib import Path
from fractions import Fraction as F
from hashlib import sha256
import json, types

def main_result():
    P = Path(__file__).resolve().parent
    rows = json.loads((P / 'VENDOR.json').read_text())['files']
    row = next((r for r in rows if r['filename'] == 'net-intervals.py'))
    source = (P / 'vendor/net-intervals.py').read_bytes()
    if sha256(source).hexdigest() != row['sha256']:
        raise ValueError('interval source hash')
    E = types.ModuleType('review_intervals')
    exec(compile(source, str(P / 'vendor/net-intervals.py'), 'exec'), E.__dict__)
    C = F(3125809, 10 ** 9)
    t = 1 - C
    u = F(3, 20)
    sigma = t + u
    point = lambda x: (F(x), F(x))

    def ipower(x, p):
        return (E.qpower(x[0], p)[0], E.qpower(x[1], p)[1])

    def need(ok, msg):
        if not ok:
            raise ValueError(msg)
    a = E.qpower(t, 1 / C)

    def D(q):
        return E.sub(E.scale(E.sub(ipower(E.add(point(q), a), t), E.divide(a, point(t))), sigma - t), point((sigma - 1) * q))
    need(D(839)[0] > 0 and D(840)[1] < 0, 'two adjacent quotients')

    def H(q, s):
        return E.add(E.sub(E.scale(E.qpower(s, t), t * q / s + t - sigma), point(sigma * q)), E.scale(E.qpower(q + s, t), sigma - t))

    def ratio(q, s):
        x = E.add(point(q), s)
        num = E.sub(E.add(point(q), ipower(s, t)), ipower(x, t))
        return E.divide(num, ipower(x, sigma))
    root_brackets = {839: (F('0.36735947'), F('0.36735949')), 840: (F('0.36729545'), F('0.36729548'))}
    values = {}
    for q, s in root_brackets.items():
        need(H(q, s[0])[0] > 0 and H(q, s[1])[1] < 0, 'stationary remainder bracket')
        values[q] = ratio(q, s)
    net = (max((v[0] for v in values.values())), max((v[1] for v in values.values())))
    upper = F(1937, 250000)
    need(net[1] < upper, 'rational sharp-coefficient upper')
    need(values[840][0] > values[839][1], 'unique maximizing integer quotient840')
    result = json.loads((P / 'RESULT.json').read_text())
    profile = result['invoice']
    paid = {int(k): v for k, v in profile['paid'].items()}
    targets = {int(k): v for k, v in profile['targets'].items()}
    T = E.moment(targets, t)
    alpha = E.divide(E.moment(paid, t), T)
    gamma = E.divide(E.moment(paid, sigma), E.mul(E.power(16, u), T))
    B = sum(targets.values())
    delta = E.divide(point(B * 17), E.mul(E.power(16, C), T))
    epsilon = E.divide(E.scale(E.power(16, t), B), T)
    delta0 = E.divide(E.scale(E.power(17, t), B), T)
    h0 = E.scale(E.qpower(t, t / C), C)

    def budget(v, coef):
        original = E.mul(coef, E.ipow(gamma, v))
        completion = E.sub(E.add(E.ipow(delta, v), E.scale(E.mul(h0, E.ipow(epsilon, v)), 2)), E.ipow(delta0, v))
        total = E.add(E.ipow(alpha, v), E.add(original, completion))
        full = E.divide(E.add(original, E.scale(E.ipow(delta, v), 2)), E.ipow(alpha, v))
        return (total, full)
    old, unused = budget(365, net)
    new, full = budget(366, point(upper))
    need(old[0] > 1, 'v365 still fails even with exact sharp coefficient')
    need(new[1] < 1 and full[1] < F(1, 10 ** 6), 'complete v366 gate and full paid perturbation')
    report = {'scope': 'Exact coefficient and complete-budget diagnostic only; no native admission or selected change.', 't': str(t), 'sigma': str(sigma), 'u': str(u), 'a': E.display(a), 'turning_signs': {str(q): E.display(D(q)) for q in [839, 840]}, 'remainder_brackets': {str(q): list(map(str, s)) for q, s in root_brackets.items()}, 'candidate_values': {str(q): E.display(v) for q, v in values.items()}, 'sharp_coefficient': E.display(net), 'rational_upper': str(upper), 'v365_bound': E.display(old), 'v366_bound_using_rational_upper': E.display(new), 'v366_full_paid_relative_excess': E.display(full), 'interval_source_sha256': row['sha256'], 'D_receipt_sha256': sha256((P / 'RESULT.json').read_bytes()).hexdigest()}
    lean = E.add(E.ipow(alpha, 365), E.mul(net, E.ipow(gamma, 365)))
    eta = E.scale(E.ipow(E.power(145, -C), 366), t)
    leading35 = (F(871, 1000) / F(204373, 200000)) ** 35
    need(0 < alpha[0] <= alpha[1] < 1 and 0 < gamma[0] <= gamma[1] < 1, 'decreasing raw and original-tail terms')
    need(lean[0] > 1, 'all fixed-bound powers at most365 fail')
    need(leading35 > eta[1], 'fixed mean/floor witness cannot use degree35')
    report.update(v365_raw_plus_original_tax=E.display(lean), v366_capacity=E.display(eta), degree35_minimal_leading_ratio=E.display(point(leading35)))
    return report
