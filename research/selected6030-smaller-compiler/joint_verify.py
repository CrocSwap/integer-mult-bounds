#!/usr/bin/env python3
"""Optional sharp-net example; primary merged-only result is unchanged.
@CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
B supplies the sharp coefficient check; zxv supplies unchanged #4480 routines.
"""
from fractions import Fraction as Q
from pathlib import Path
import argparse, importlib.util, json, sys
from hashlib import sha256
BASE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('published_d', BASE / 'verify.py')
D = importlib.util.module_from_spec(spec)
spec.loader.exec_module(D)
primary = D.main_result()
D.need(primary == D.read(BASE / 'RESULT.json'), 'unchanged primary complete receipt')
source = D.read(BASE / 'JOINT-SOURCE.json')
D.need(source['commit'] == 'a0ef8b7ae2592202247b15da453ce42598863a26', 'fixed pending theorem pin')
D.authenticate_bytes((BASE / 'joint-source/PROOF.md').read_bytes(), source)
E = D.load('intervals', 'net-intervals.py')
K = D.load('compiler', 'net-compiler.py')
cspec = importlib.util.spec_from_file_location('joint_coefficient', BASE / 'joint_coefficient.py')
CM = importlib.util.module_from_spec(cspec)
cspec.loader.exec_module(CM)
coefficient = CM.main_result()
D.need(Q(coefficient['rational_upper']) == Q(1937, 250000), 'same certified coefficient')
r = primary
profile = {k: r['invoice'][k] for k in ('paid', 'targets')}
w = D.read(BASE / 'WITNESS.json')
d = K.tax_data(profile, w)
C = D.C
t = 1 - C

def check(v, p, h, N):
    original = E.mul(N, E.ipow(d['gamma'], v))
    complete = E.sub(E.add(E.ipow(d['delta'], v), E.scale(E.mul(d['concavity_remainder'], E.ipow(d['epsilon'], v)), 2)), E.ipow(d['delta0'], v))
    bound = E.add(E.add(E.ipow(d['alpha'], v), original), complete)
    full = E.divide(E.add(original, E.scale(E.ipow(d['delta'], v), 2)), E.ipow(d['alpha'], v))
    E.need(E.add(original, E.scale(E.ipow(d['delta'], v), 2))[0] > E.add(original, complete)[1], 'full paid charge strictly exceeds net tax')
    E.need(bound[1] < 1, 'complete net budget')
    E.need(full[1] < Q(1, 1000000), 'full paid mass')
    A = Q(h, 4 * v)
    lo = A - Q(1, 10 ** 6)
    hi = A + Q(1, 10 ** 6)
    moments = K.concentrated_moments(p, v, Q(871, 1000), Q(31, 20), Q(1, 1000000))
    ratio, max_j, num, den = K.moment_coefficients(p, moments, hi, lo + Q(1794977, 1000000), Q(204373, 200000))
    eta = E.scale(E.ipow(E.power(145, -C), v), t)
    E.need(ratio < eta[0], 'all polynomial coefficients')
    basecost = E.ipow(E.power(145, C), v)
    log_m = E.scale(E.divide(E.log_bounds(145), E.log_bounds(2)), v)
    basefactor = E.ipow(E.add((Q(1),) * 2, E.scale(log_m, Q(1, h))), p)
    E.need(basecost[1] < basefactor[0], 'ordinary base range')

    def passes(j):
        return (h + 1400000000 * j) ** p < h ** p * 2 ** j
    j = 1
    while not passes(j):
        j += 1
        E.need(j < 10000, 'bounded final grid')
    E.need(Q(1400000000 * j) > log_m[1], 'uniform rank beyond ordinary base')
    E.need(not passes(j - 1), 'previous grid fail')
    E.need(1400000000 * j + h > 2 * p / D.GAP, 'decreasing tail')
    return {'v': v, 'p': p, 'h': h, 'A_lower': str(lo), 'A_upper': str(hi), 'raw_mean_upper': '871/1000', 'raw_log_bound': '31/20', 'paid_excess_upper': '1/1000000', 'ambient_log_lower': '1794977/1000000', 'floor_log_lower': '204373/200000', 'log_moment_upper_bounds': list(map(str, moments)), 'numerator_coefficients': list(map(str, num)), 'denominator_coefficients': list(map(str, den)), 'coefficient': E.display(N), 'net_charge': E.display(bound), 'full_paid_excess': E.display(full), 'max_polynomial_ratio': E.display((ratio, ratio)), 'maximizing_coefficient': max_j, 'eta': E.display(eta), 'ordinary_cost': E.display(basecost), 'ordinary_factor': E.display(basefactor), 'grid_index': j, 'H': 1400000000 * j, 'previous_grid_fails': True}
results = {'old_Q_retuned': check(370, 37, 6700, d['coefficient']), 'sharp_N': check(366, 36, 6400, (Q(1937, 250000),) * 2)}
D.need(results['old_Q_retuned']['H'] == 1433600000000 and results['sharp_N']['H'] == 1397200000000, 'fixed joint heights')
top = (Q(871, 1000) / Q(204373, 200000)) ** 35
D.need(top > E.scale(E.ipow(E.power(145, -C), 366), t)[1], 'p35 top coefficient fails even at zero excess')
no_tail = E.add(E.ipow(d['alpha'], 365), E.sub(E.add(E.ipow(d['delta'], 365), E.scale(E.mul(d['concavity_remainder'], E.ipow(d['epsilon'], 365)), 2)), E.ipow(d['delta0'], 365)))
D.need(no_tail[1] < 1, 'omitting original paid tail makes a false positive')
count = 1
for v in range(1, 366):
    count = 13444 * count + 66834 ** v
D.need(count * (66834 - 13444) == 66834 ** 366 - 13444 ** 366, 'new raw instance recurrence')
output = E.encoded({'status': 'PASS_SELECTED6030_OPTIONAL_SHARP_NET', 'source': source, 'primary_receipt_sha256': sha256((BASE / 'RESULT.json').read_bytes()).hexdigest(), 'sharp_coefficient': coefficient, 'certificates': results, 'outer': primary['outer'], 'kappa': D.KAPPA, 'tested_saving': C, 'uniform_saving': D.KAPPA + 6 * D.GAP, 'height_reduction_relative_to_retuned_old': Q(26, 1024), 'controls': {'p35_zero_excess_top_ratio': str(top), 'omitted_tail_false_positive': E.display(no_tail)}, 'new_counts': {'raw_instances': '(66834^366-13444^366)/(66834-13444)', 'productive_fields': '13444^366', 'paid_call_upper': '240152^366+(13444*17)^366', 'raw_ordinary_upper': '10^9*(66834^366-13444^366)/(66834-13444)'}, 'limitations': primary['limitations'] + ['Optional example depends on a pinned pending fork theorem.', 'These exact certificates only; no globally optimal height or u is claimed.']})
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--write', action='store_true')
args = parser.parse_args()
if args.write:
    (BASE / 'JOINT-RESULT.json').write_text(json.dumps(output, indent=2, sort_keys=True) + '\n')
else:
    D.need(D.read(BASE / 'JOINT-RESULT.json') == output, 'complete joint deterministic receipt')
print(json.dumps({'status': output['status'], 'H': results['sharp_N']['H'], 'retuned_old_H': results['old_Q_retuned']['H']}, sort_keys=True))
