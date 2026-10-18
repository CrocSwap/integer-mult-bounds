#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Full finite 2-role and 3-role quotient censuses for the 15-call five-b UT4 boundary."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location('ut4_fifteen_call_census', HERE / 'census.py')
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)


def verify():
    P, source = C.load()
    algebra = P.fixed_algebra()
    positive = P.positive_and_controls()
    result = C.run(P, progress=True)

    old_2175 = source['predecessor_receipt']['data']
    C.require(algebra == old_2175['algebra'] and positive == old_2175['positive'],
              'predecessor PR2175 algebra/positive control mismatch')

    old_2314 = json.loads((ROOT / 'research/ut4-mixed-weighted-boundary/RESULT.json').read_text(encoding='utf-8'))
    for key in ('4,5,4', '5,5,4', '4,5,5'):
        for field in ('middles', 'a_pass', 'c_pass', 'key_pairs', 'profile_pairs',
                      'words', 'q_pass', 'first_differing_coefficient'):
            C.require(result['domains'][key][field] == old_2314['domains'][key][field],
                      f'predecessor PR2314 domain {key} field {field} mismatch')

    old_2343 = json.loads((ROOT / 'research/register-pairing-compression/RESULT.json').read_text(encoding='utf-8'))
    C.require(old_2343['ut4_consequence']['only_cheaper_count_splits'] == [[4, 5, 6], [5, 5, 5], [6, 5, 4]]
              and old_2343['ut4_consequence']['fifteen_call_existence_decided'] is False,
              'predecessor PR2343 open-splits handoff mismatch')

    C.require(result['outer_catalogues'] == {
        '4': dict(zero_sequences=441, profiles=9721, realizations=55566),
        '5': dict(zero_sequences=3600, profiles=47521, realizations=907200),
        '6': dict(zero_sequences=33489, profiles=174670, realizations=15471918),
    }, 'complete outer inventory mismatch')

    C.require(sum(result['domains'][k]['words'] for k in ('6,5,4', '5,5,5', '4,5,6')) == 20579840,
              'new 15-call two-role word count mismatch')
    C.require(all(result['domains'][k]['q_pass'] == 0 for k in ('6,5,4', '5,5,5', '4,5,6')),
              'unexpected two-role quotient survivor')

    for mode in ('case_I_col_a_row_c', 'case_II_row_a_col_c'):
        st3 = result['three_role_555'][mode]
        C.require(st3['active_profile_pairs'] == 5664 and st3['dirty_profile_pairs'] == 17864
                  and st3['words'] == 42447616 and st3['hh_q_pass'] == 0,
                  f'three-role (5,5,5) {mode} census mismatch')

    result.update(
        status='PASS_UT4_FIFTEEN_CALL_FIVE_B',
        algebra=algebra,
        positive=positive,
        scope=(
            'Formal F2[UT4(F2)] register-model theorem and complete necessary-quotient '
            'rejection for all 15-call five-b splits across arbitrary finite restored '
            'dirty workspaces; no native supplier or new kappa.'
        ),
        theorem=dict(
            target='diag([z],[uz],I_rest)',
            arbitrary_finite_restored_dirty_workspace=True,
            excluded_fifteen_call_five_b_splits=[[6, 5, 4], [5, 5, 5], [4, 5, 6]],
            all_fifteen_call_words_have_b_at_least_six=True,
            five_b_calls_require_at_least_eleven_outer_calls=True,
            five_b_calls_require_at_least_sixteen_total_calls=True,
            weighted_lower_bound='min(4 alpha+6 beta+4 gamma, 4 alpha+5 beta+4 gamma+3 min(alpha,gamma))',
            sharp_price_region='alpha,beta,gamma>=0 and beta<=3 min(alpha,gamma)',
            exact_price_in_region='4 alpha+6 beta+4 gamma',
            price_1_3_1_exact_minimum=26,
            price_1_3_1_cost_25_impossible=True,
            uniform_quantifiers_supplied_by='PROOF.md, not finite role extrapolation',
        ),
    )
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-result', action='store_true')
    args = parser.parse_args()
    result = json.loads(json.dumps(verify()))
    path = HERE / 'RESULT.json'
    if args.write_result:
        path.write_text(json.dumps(result, sort_keys=True, indent=2) + '\n', encoding='utf-8')
    else:
        C.require(result == json.loads(path.read_text(encoding='utf-8')),
                  'recorded result differs from full replay')
    digest = hashlib.sha256(json.dumps(result, sort_keys=True, separators=(',', ':')).encode('utf-8')).hexdigest()
    print(result['status'], 'new_two_role_words=20579840', 'three_role_555_words=84895232', 'receipt=' + digest)


if __name__ == '__main__':
    main()
