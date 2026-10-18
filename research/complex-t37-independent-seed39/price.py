# SPDX-License-Identifier: Apache-2.0
"""Two unchanged exact moment engines and all 47 outer inequalities for T37.

T37 adaptation by Tekalign (@tekuuu) with substantial OpenAI Codex assistance;
predecessor arithmetic driver by icekylinx. The complex
1024-bit prefix is paid in its finite row invoice; the bootstrap's 512-bit
coefficient remains the unchanged PR589 bit supplier's allowance.

The normalized comparison checks one exact finite vector majorization; the
analytic implication uses strict concavity of r^(1-b) for 0<b<1. This finite
check is not a formal proof of the supplier or its all-size interfaces.
"""
import sys
sys.dont_write_bytecode = True
import argparse
from collections import Counter
import hashlib
from fractions import Fraction
from pathlib import Path
from common import HERE, ROOT, read, require, sha, dump, load


def main():
    require(__debug__, 'Do not use python -O: retained arithmetic engines require assertions')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    old = load(HERE/'vendor/pr870/independent/price_profile_t16.py', 'unchanged_price_helpers')
    pins = read(HERE/'vendor/pr870/data/UPSTREAM-PINS.json')
    for name in ('moment', 'base_two_moment', 'outer'):
        relative = old.SOURCE/'engines'/(name+'.py')
        require(sha(ROOT/relative) == pins[relative.as_posix()], 'Exact arithmetic source pin')
    M, B, A = [old.load(ROOT/old.SOURCE/'engines', name) for name in ('moment', 'base_two_moment', 'outer')]
    supplied, claim = read(args.profile), read(HERE/'data/CLAIM.json')
    require(supplied['status'] == 'PASS_INDEPENDENT_VARIABLE_T_LITERAL_WINDOWS_CHARTS_PREFIX_ROW',
            'Independent owner/profile receipt status')
    require((supplied['live'], supplied['deficit']) == (33152, 11840), 'T37 profile stock and deficit')
    require((supplied['calls'], supplied['physical']) == (333, 33666), 'T37 calls and physical stock')
    require(supplied['explicit_order_input'] and supplied['declared_order_role_times_bound'], 'Explicit order admission')
    require((supplied['prefix_bits'], supplied['charged_prefix_bits'], supplied['physical_row_coefficient']) ==
            (779, 1024, 17495), 'T37 complex prefix and row reserve')
    profile = {int(rank): count for rank, count in supplied['profile'].items()}
    expected = Counter({int(rank):333*count for rank,count in claim['local_profile'].items()})
    expected.update({int(rank):count for rank,count in claim['idle'].items()})
    require(profile == dict(expected), 'Independently recounted profile/claim binding')
    bit_bytes = old.BIT_PATH.read_bytes()
    require(hashlib.sha1(b'blob '+str(len(bit_bytes)).encode()+b'\0'+bit_bytes).hexdigest() == old.BIT_BLOB, 'PR589 bit supplier blob')
    bit = read(old.BIT_PATH)
    deficit = old.pr589_deficit(bit['word'], bit['nine']['bit']['live'])
    c = Fraction(bit['nine']['bit_lower'])
    require(c == Fraction(claim['bit_lower']), 'Unchanged bit supplier/claim binding')
    require(claim['charged_complex_payload'] == 1024, 'Claimed complex prefix allowance')
    bit_checks = old.moment_checks(M, B, {int(r): n for r, n in bit['nine']['profile'].items()},
                                  64, bit['nine']['bit']['live'], c, deficit, True)
    prices = {}
    for mode, surcharge in (('native', False), ('conservative', True)):
        root = M.certify(profile, 73, 33152, surcharge)
        b = Fraction(root['lower'])
        prices[mode] = dict(root=root, moments=old.moment_checks(M, B, profile, 73, 33152, b, 11840, surcharge),
                            outer=old.outer47(c, b, A))
    require(prices['native']['outer']['kappa'] == str(Fraction(claim['kappa'])), 'Claimed T37 exponent')
    require(Fraction(prices['native']['root']['lower']) == Fraction(claim['complex_lower']), 'Claimed complex endpoint')
    # This exact normalized comparison also explains the direction of the
    # gain independently of either root solver. Shared local terms cancel.
    require(supplied['local_profile'] == claim['local_profile'], 'Recounted local profile binding')
    baseline_profile = Counter({int(rank):189*count for rank,count in supplied['local_profile'].items()})
    baseline_profile.update({48:6292, 1:3, 3:1})
    difference = Counter({rank:21*count for rank,count in profile.items()})
    difference.subtract({rank:37*count for rank,count in baseline_profile.items()})
    difference = {rank:count for rank,count in difference.items() if count}
    require(dict(difference) == {48:2, 1:15, 3:-37}, 'T37/T21 normalized difference')
    concentrated = [48,48]+[1]*15+[0]*20
    uniform = [3]*37
    partial_gaps = [sum(concentrated[:i])-sum(uniform[:i]) for i in range(1,38)]
    require(sum(concentrated) == sum(uniform) == 111 and
            all(gap > 0 for gap in partial_gaps[:-1]) and partial_gaps[-1] == 0,
            'Strict rank-mass majorization')
    result = dict(status='PASS_T37_TWO_EXACT_ENGINES_AND_OUTER47', prices=prices, bit_checks=bit_checks,
                  profile_sha256=sha(args.profile), gain_over_pr890=str(Fraction(claim['kappa'])-Fraction(claim['baseline890_kappa'])),
                  normalized_profile_comparison=dict(t37_multiplier=21, t21_multiplier=37,
                      rank_count_difference=difference, zero_padded_majorization_gaps=partial_gaps,
                      pr890_idle_profile={48:6292, 1:3, 3:1},
                      canceled_local_calls=6993, fewer_children=20,
                      consequence='For every 0<b<1, strict concavity of r^(1-b) lowers the normalized native moment; fewer children also lower the retained surcharge.'),
                  bootstrap_coefficient_bits=512, complex_prefix_charge_bits=1024,
                  input_sha256={'claim':sha(HERE/'data/CLAIM.json'),
                      'unchanged_price_helpers':sha(HERE/'vendor/pr870/independent/price_profile_t16.py'),
                      'bit_supplier':sha(old.BIT_PATH),
                      **{name:sha(ROOT/old.SOURCE/'engines'/(name+'.py'))
                         for name in ('moment','base_two_moment','outer')}},
                  scope='Exact arithmetic for the independently recounted T37 profile; full controller and invoice admission are separate mandatory stages.')
    dump(args.out, result)
    print(result['status'], prices['native']['outer']['kappa_decimal'])


if __name__ == '__main__':
    main()
