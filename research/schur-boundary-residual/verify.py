#!/usr/bin/env python3
"""Scoped exact boundary evidence; source authentication precedes all imports."""
import argparse
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(condition, message):
    if not condition:
        raise ValueError(message)


def source_bytes():
    manifest = json.loads((HERE / 'SOURCES.json').read_text())
    rows = [r for r in manifest['files'] if r['usage'] == 'input']
    for row in rows:
        path = ROOT / row['path']
        need(path.is_file() and not path.is_symlink(), 'regular input: ' + row['path'])
        need(sha256(path.read_bytes()).hexdigest() == row['sha256'], 'exact input: ' + row['path'])
    return len(rows)


def algebra():
    # Check the constants/base steps of the written induction, not an all-p census.
    # p <= 2^p follows at p=1 and p+1 <= 2p. The bounds below then
    # decrease geometrically at every integer p >= 1.
    need(1 <= 2 and 1 + 1 <= 2 * 1, 'elementary induction base')
    for coefficient, degree, ceiling_bits in ((40, 2, 6), (3200, 4, 12)):
        need(coefficient < 1 << ceiling_bits, 'strict power-of-two coefficient envelope')
        need(ceiling_bits - (32768 - degree) < -1, 'Neumann envelope below one half at p=1')
        need(32768 - degree > 0, 'Neumann envelope decreases for every p increment')
    eta_cap = Q(1, 1 << 16)
    need(32768 > 16, 'uniform coarse eta cap')
    need(195 + 4 + 6 * eta_cap < 200, 'factor product coefficient')
    need(65 + 2 * eta_cap < 66, 'rounded lower growth')
    need(2 + 8 * 66 == 530, 'combined residual coefficient')
    need(200 + 5 == 205, 'both setup perturbations')
    need(32 * 530 == 16960 and 32 * 205 * 8 == 52480, 'solution error constants')
    need(16960 + 52480 == 69440 < 1 << 17, 'final constant')
    need(2 * 101 + 8 <= 3 * 101, 'effective diagonal within stated p domain')

    # An exact zero-online-residual example isolates the initial Schur rounding.
    unit = 1 << 8
    S = 1 + Q(1, 3 * unit)
    Sbar = Q(int(S * unit), unit)
    x = r = Q(1)
    rho = Sbar * x - r
    error = x - r / S
    need(Sbar == 1 and rho == 0 and error == Q(1, 3 * unit + 1),
         'omitting initial Schur rounding falsely predicts zero error')
    need(error == (rho - (Sbar - S) * r / S) / Sbar, 'complete scalar error identity')

    # A two-row P=3 model separates the actual one-round upper program from
    # rounding its dot-product residual before multiplication by the reciprocal.
    def tau(v):
        return Q(int(v * 8), 8)
    qhat = tau(Q(8, 3))
    y = [Q(1, 8), Q(1, 8)]
    last = tau(qhat * y[1])
    residual = y[0] - Q(1, 8) * last
    first = tau(qhat * residual)
    wrong = tau(qhat * tau(residual))
    need([first, last] == [Q(1, 8), Q(1, 4)] and wrong == 0,
         'premature upper residual rounding distinguished')
    need(1 / qhat != tau(Q(3, 8)), 'effective diagonal is not rounded U diagonal')
    return {
        'uniform_domain': 'integer p >= 101, P=32768p; explicit source premises in PROOF.md',
        'neumann_envelopes': ['40 p^2 eta < 2^(6-32766p) < 1/2',
                              '3200 p^4 eta < 2^(12-32764p) < 1/2'],
        'original_S_error_constant': 69440,
        'reported_allowance': '2^17 p^5 eta max(1,||r||_infinity)',
        'scalar_omission_control': {'P': 8, 'online_residual': '0', 'original_error': str(error)},
        'early_round_control': {'P': 3, 'actual': [str(first), str(last)], 'mutant': [str(wrong), str(last)]},
        'scope': 'Exact scalar controls and arithmetic of the written proof; no finite test establishes the analytic premises.'
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true', help='write the complete deterministic finite receipt')
    args = parser.parse_args()
    count = source_bytes()
    # -B prevents writes, not reads: isolate cached bytecode before importing
    # any authenticated predecessor module or the local fixture.
    with tempfile.TemporaryDirectory(prefix='schur-boundary-pycache-') as cache:
        old = sys.pycache_prefix
        sys.pycache_prefix = cache
        try:
            sys.path.insert(0, str(HERE))
            sys.path.insert(0, str(ROOT / 'research/physical-gaussian-core'))
            from gaussian_sources import opened
            from fixture import run_fixture
            with opened():
                physical = run_fixture()
        finally:
            sys.pycache_prefix = old
    result = {'status': 'PASS_SCHUR_BOUNDARY_RESIDUAL', 'source_inputs': count,
              'algebra': algebra(), 'physical': physical}
    path = HERE / 'RESULT.json'
    if args.write:
        path.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    else:
        need(result == json.loads(path.read_text()), 'complete typed finite receipt')
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
