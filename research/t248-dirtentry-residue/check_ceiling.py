# SPDX-License-Identifier: Apache-2.0
"""Apply the retained local-word packing envelope to the actual PR2833 profile.

The historical alpha/(1+alpha) conversion is not used: this contribution uses
the source-bound PR2839 modern outer contract. The complex exponent itself is
bounded by this normalized-moment relaxation.
"""
from fractions import Fraction as Q
from pathlib import Path
import json
import sys
import types

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate import HERE, authenticate, need, read


def main():
    authenticate()
    tool = HERE / 'vendor/ceiling.py'
    ceiling = types.ModuleType('retained_ceiling')
    exec(compile(tool.read_bytes(), str(tool), 'exec'), ceiling.__dict__)
    providers = read(HERE / 'sources/PR2833-PROVIDERS.json')
    local = {int(r): n for r, n in providers['gauge44']['actual_paid_profile'].items()}
    need(local == {1: 2382, 2: 650, 3: 266, 4: 128, 5: 26, 8: 8},
         'actual unchanged source profile')
    need(local == {int(r): n for r, n in providers['extra']['actual_paid_profile'].items()},
         'both provider inventories agree')
    lower, upper = ceiling.ceiling(local, 73, 896, 9, 64)
    need(upper == Q(1758437153251, 10**15), 'retained exact alpha cap')
    candidate = Q(1718658508304930004819, 10**24)
    need(candidate < lower, 'candidate inside fixed-word envelope')
    print(json.dumps({
        'status': 'PASS_ACTUAL_LOCAL_WORD_PACKING_CEILING',
        'local_profile': local, 'complex_ceiling_lower': str(lower),
        'complex_ceiling_upper': str(upper),
        'candidate_fraction_of_upper': str(candidate / upper),
        'scope': 'Fractional rank-51 idle relaxation with nine-stage hosted coverage; '
                 'complex saving cap, not an attainable allocation or a changed outer contract.'
    }, sort_keys=True))


if __name__ == '__main__':
    main()
