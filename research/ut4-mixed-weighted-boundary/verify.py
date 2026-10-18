#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Full finite census supporting the written all-workspace weighted theorem."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('ut4_boundary_census', HERE / 'census.py')
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)


def verify():
    P, source = C.load()
    algebra = P.fixed_algebra()
    positive = P.positive_and_controls()
    result = C.run(P, progress=True)
    old = source['predecessor_receipt']['data']
    control = dict(result['domains']['4,5,4'], outer_zero_sequences=441, profiles=9721)
    C.require(control == old['census'] and algebra == old['algebra'] and positive == old['positive'],
              'predecessor thirteen-call control did not reproduce')
    C.require(result['outer_catalogues'] == {
        '4': dict(zero_sequences=441, profiles=9721, realizations=55566),
        '5': dict(zero_sequences=3600, profiles=47521, realizations=907200)}, 'complete outer inventory')
    C.require(sum(result['domains'][key]['words'] for key in ('5,5,4', '4,5,5')) == 421888,
              'new expanded-domain coverage')
    result.update(status='PASS_UT4_MIXED_WEIGHTED_BOUNDARY', algebra=algebra, positive=positive,
                  scope='Formal group-algebra theorem supported by complete necessary-quotient rejection; no native supplier or new kappa.',
                  theorem=dict(target='diag([z],[uz],I_rest)', arbitrary_finite_restored_dirty_workspace=True,
                               all_fourteen_call_words_have_counts=[4, 6, 4],
                               five_b_calls_require_at_least_ten_outer_calls=True,
                               weighted_lower_bound='min(4 alpha+6 beta+4 gamma, 4 alpha+5 beta+4 gamma+2 min(alpha,gamma))',
                               sharp_price_region='alpha,beta,gamma>=0 and beta<=2 min(alpha,gamma)',
                               exact_price_in_region='4 alpha+6 beta+4 gamma',
                               uniform_quantifiers_supplied_by='PROOF.md, not finite role extrapolation'))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-result', action='store_true')
    args = parser.parse_args()
    result = json.loads(json.dumps(verify()))
    path = HERE / 'RESULT.json'
    if args.write_result:
        path.write_text(json.dumps(result, sort_keys=True, indent=2) + '\n')
    else:
        C.require(result == json.loads(path.read_text()), 'recorded result differs from full replay')
    digest = hashlib.sha256(json.dumps(result, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    print(result['status'], 'new_expanded_words=421888', 'receipt=' + digest)


if __name__ == '__main__':
    main()
