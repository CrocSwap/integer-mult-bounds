#!/usr/bin/env python3
"""Independent exact check of the optional sharp-tax compiler application.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
Uses the lead's binomial/Newton implementation, never the author compiler.
The coefficient theorem and interval certificate remain separate dependencies.
"""
import argparse
from fractions import Fraction as F
import importlib.util
import json
from pathlib import Path


def need(ok, message):
    if not ok:
        raise ValueError(message)


def check_row(name, row, oracle):
    v, p, h = row['v'], row['p'], row['h']
    wanted = {'old_Q_retuned': (370, 37, 6700, 1024),
              'sharp_N': (366, 36, 6400, 998)}[name]
    need((v, p, h, row['grid_index']) == wanted, 'parameter tuple')
    mu = oracle.binomial_moments(v, p, F(row['raw_log_bound']),
                                F(row['raw_mean_upper']), F(row['paid_excess_upper']))
    need(mu == list(map(F, row['log_moment_upper_bounds'])), 'binomial mixture moments')
    num = oracle.convolution_polynomial(mu, F(row['A_upper']))
    intercept = F(row['A_lower']) + F(row['ambient_log_lower'])
    slope = F(row['floor_log_lower'])
    den = oracle.newton([(intercept+slope*g)**p for g in range(p+1)])
    need(num == list(map(F, row['numerator_coefficients'])), 'Newton numerators')
    need(den == list(map(F, row['denominator_coefficients'])), 'Newton denominators')
    need(all(x > 0 for x in den), 'positive denominators')
    ratios = [a/b for a, b in zip(num, den)]
    need(max(ratios) < F(row['eta']['lower']), 'exact capacity comparisons')
    need(ratios.index(max(ratios)) == row['maximizing_coefficient'], 'maximizing index')
    j, H = row['grid_index'], row['H']
    need(H == 1400000000*j, 'height grid')
    need((h+H)**p < h**p*2**j, 'integer height bound')
    need((h+H-1400000000)**p >= h**p*2**(j-1), 'previous grid fails')
    need(H+h > 2*p*1400000000, 'decreasing-tail guard')
    bad = num.copy()
    bad[-1] += 1
    need(bad != list(map(F, row['numerator_coefficients'])), 'changed coefficient detected')
    need(oracle.convolution_polynomial(mu, F(row['A_lower'])) != num,
         'reversed shift differs from certificate')
    return {'v': v, 'p': p, 'h': h, 'moments': len(mu), 'numerators': len(num),
            'denominators': len(den), 'grid_index': j, 'H': H}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('package', nargs='?', type=Path, default=Path(__file__).resolve().parent)
    package = parser.parse_args().package
    spec = importlib.util.spec_from_file_location('lead_binomial_newton', package/'independent_oracle.py')
    oracle = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(oracle)
    joint = json.loads((package/'JOINT-RESULT.json').read_bytes())
    rows = {name: check_row(name, joint['certificates'][name], oracle)
            for name in ('old_Q_retuned', 'sharp_N')}
    need(F(rows['sharp_N']['H'], rows['old_Q_retuned']['H']) == F(499, 512),
         'fair fixed-certificate ratio')
    print(json.dumps({'marker': 'PASS_INDEPENDENT_JOINT_COMPILER_ORACLE',
                      'certificates': rows, 'relative_height_reduction': '13/512',
                      'scope': 'Exact binomial/Newton and integer corroboration. The sharp coefficient theorem and interval certificate are separate dependencies.'}, sort_keys=True))


if __name__ == '__main__':
    main()
