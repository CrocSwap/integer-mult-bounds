#!/usr/bin/env python3
"""Independent source and new-carrier boundary checks for the joint review.

No contributor scientific module is imported. The arithmetic addresses the
specific risk of retaining old carrier/stock/grid constants after substitution.
It is not a replay of the astronomical compiled word or a proof of tariffs.
"""

import argparse
from fractions import Fraction
from hashlib import sha1, sha256
import json
from pathlib import Path


EXPECTED_PROOF = '814c514717592ef64bf4afd1bc5dff8284cf534790287fc8b2d1a0408c6caee5'


def require(value, message):
    if not value:
        raise ValueError(message)


def blob(data):
    return sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root', type=Path,
                        default=Path(__file__).resolve().parent,
                        help='Directory containing the retained refs/ tree; reviewed PROOF.md is its parent')
    ROOT = parser.parse_args().source_root.resolve()
    proof = (ROOT.parent / 'PROOF.md').read_bytes()
    require(sha256(proof).hexdigest() == EXPECTED_PROOF, 'Reviewed proof drift')
    sources = []
    pinned = json.loads((ROOT / 'refs/CANONICAL-INTERFACE-PINS.json').read_text())
    for row in pinned['files']:
        data = (ROOT / 'refs/canonical' / row['path']).read_bytes()
        require(blob(data) == row['git_blob'], 'Canonical Git blob drift')
        require(sha256(data).hexdigest() == row['sha256'], 'Canonical SHA drift')
        sources.append({'path': 'refs/canonical/' + row['path'],
                        'sha256': sha256(data).hexdigest()})
    origins = json.loads((ROOT / 'refs/ORIGIN-METADATA.json').read_text())
    relevant = {'pr7828/PROOF.md', 'pr7828/APPLICATION.md',
                'pr7828/schedule.py', 'pr7828/product.py', 'pr7828/RESULT.json',
                'pr7840/PROOF.md'}
    for row in origins:
        if row['local'] in relevant:
            data = (ROOT / 'refs' / row['local']).read_bytes()
            require(blob(data) == row['git_blob'], 'Predecessor Git blob drift')
            sources.append({'path': 'refs/' + row['local'],
                            'sha256': sha256(data).hexdigest(),
                            'commit': row['commit']})

    witnesses = json.loads((ROOT / 'refs/pr7828/RESULT.json').read_text())
    rows = []
    for name, ambient, public in [('selected_BIT', 134, (8, 18, 7)),
                                  ('selected_complex', 153, (9, 18, 8))]:
        witness = witnesses[name]
        v, h = witness['v'], witness['H']
        require(public[0] + public[1]*public[2] == ambient == witness['source_ambient'],
                'Actual caller ambient')
        require(h >= 1 + v*(ambient-1).bit_length(), 'Whole root contains product window')
        c, u = Fraction(witness['raw_saving']), Fraction(witness['uniform_saving'])
        threshold = 1 + c*(2+v*(ambient-1).bit_length())
        require(h*(c-u) > threshold, 'New carrier moment threshold')
        context_bound = 2*(h+v)
        grid = 356*context_bound
        require(grid.bit_length() <= h, 'New common-grid unfinished depth')
        # New independent row-stock bound: with W_N <= N^15 and q >= 2,
        # ell_F <= N^2+15H <= 2N^2, so C_row <= 64N^2 for H >= 3.
        # A sufficient dyadic log2(e) is j0=4H+100. Its comparison uses only
        # short integers, never N=2^H or e=2^j0.
        require(h >= 3, 'Row bound domain')
        j0 = 4*h+100
        log_row_upper = (j0+1).bit_length()  # ceil(log2(j0+2))
        require(249*j0 > 500*h+2251+250*log_row_upper,
                'Simultaneous three-stage productive-cover reserve')
        rows.append({'source': name, 'H': h, 'v': v,
                     'context_bound': context_bound,
                     'grid_factor_bit_length': grid.bit_length(),
                     'productive_row_log2_cutoff': j0,
                     'carrier_funding_margin': str(h*(c-u)-threshold)})

    rho = Fraction(1, 250)
    uniform = Fraction(witnesses['selected_BIT']['uniform_saving'])
    cover_loss = Fraction(1, 10**10)
    b = uniform-cover_loss
    require(b == Fraction('0.0038525298'), 'Covered saving')
    require(Fraction(64, 2**45) < cover_loss/4, 'Fresh-cover fallback debit')
    stages = [Fraction(0), Fraction('.0034'), Fraction('.0038507'), Fraction('.00385248')]
    gaps = []
    for previous, following in zip(stages, stages[1:]):
        gap = (1-rho)*b+rho*previous-following
        require(gap > 0 and following < rho and following < 1-rho, 'Cold stage exponent')
        gaps.append(str(gap))
    require(stages[-1] > Fraction('.00376669'), 'Selected movement interface')
    require(Fraction(witnesses['selected_complex']['uniform_saving'])
            - Fraction(363005817, 100000000000) == Fraction(6, 10**14),
            'Unchanged complete outer price')
    # These exact comparisons justify the universal dyadic monotonicity
    # argument used in the review's reserve lemma.
    require(15*3 <= 2**6 and Fraction(4, 3)**2 < 2, 'Row-reserve base comparisons')
    print(json.dumps({'status': 'PASS_JOINT_BOUNDARY_CROSS_REVIEW',
                      'proof_sha256': EXPECTED_PROOF, 'sources': sources,
                      'carriers': rows, 'cold_stage_gaps': gaps,
                      'scope': 'Pinned-source equality and new-carrier boundary arithmetic only; universal argument is in CROSS-REVIEW.md.'}, indent=2))


if __name__ == '__main__':
    main()
