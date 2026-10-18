# SPDX-License-Identifier: Apache-2.0
"""Independently check the recorded cutoffs also pay a 1024-bit allowance.

This does not import either inherited moment engine. It checks fourteen
source-pinned rational cutoff obligations, not the multiplication theorem.
Prepared by Tekalign with substantial OpenAI Codex assistance.
"""
import copy
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ASSEMBLY_SHA256 = 'ccd14fa0cb2a3b14d92b0c0d29760fe0d550db836a13ae4ef32499d15ce32727'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def ceil(value):
    return -(-value.numerator // value.denominator)


def check(record):
    checked = []
    for name in ('bootstrap', 'conservative_bootstrap'):
        cuts = record[name]
        require(len(cuts) == 7, 'seven cutoffs per branch')
        for index, item in enumerate(cuts):
            gap, cutoff = Q(item['gap']), int(item['cutoff_log2'])
            require(gap > 0, 'positive gap')
            # 36/gap^2 >= 2*(4+1024)/gap iff gap <= 9/514.
            require(gap <= Q(9, 514), 'quadratic dominance at payload1024')
            quadratic = ceil(36 / gap**2)
            old = max(quadratic, ceil(2 * (4 + 512) / gap))
            enlarged = max(quadratic, ceil(2 * (4 + 1024) / gap))
            require(cutoff == quadratic == old == enlarged, 'unchanged exact cutoff')
            require(cutoff * gap >= 2 * (4 + 1024), 'paid payload1024 reserve')
            require(cutoff * gap**2 >= 36, 'paid quadratic reserve')
            checked.append({'branch': name, 'index': index,
                            'gap': str(gap), 'cutoff_log2': str(cutoff)})
    return checked


def main():
    data = (HERE / 'ASSEMBLY.json').read_bytes()
    require(hashlib.sha256(data).hexdigest() == ASSEMBLY_SHA256, 'pinned assembly')
    record = json.loads(data)
    checked = check(record)
    rejected = []
    for name, expected, mutate in (
        ('missing_native_cutoff', 'seven cutoffs per branch',
         lambda x: x['bootstrap'].pop()),
        ('one_below_quadratic_cutoff', 'unchanged exact cutoff',
         lambda x: x['conservative_bootstrap'][3].__setitem__(
             'cutoff_log2', str(int(x['conservative_bootstrap'][3]['cutoff_log2']) - 1))),
        ('zero_gap', 'positive gap',
         lambda x: x['bootstrap'][0].__setitem__('gap', '0')),
        # A synthetic gap where dominance is false prevents extending the
        # recorded-small-gap argument to an unrestricted cutoff theorem.
        ('outside_dominance_domain', 'quadratic dominance at payload1024',
         lambda x: x['bootstrap'][0].__setitem__('gap', '1/2')),
    ):
        changed = copy.deepcopy(record)
        mutate(changed)
        try:
            check(changed)
        except ValueError as error:
            require(str(error) == expected, 'wrong negative-control failure')
            rejected.append({'name': name, 'reason': str(error)})
        else:
            raise ValueError('accepted negative control: ' + name)
    print(json.dumps({
        'status': 'PASS_FOURTEEN_UNCHANGED_BOOTSTRAP_CUTOFFS_AT_PAYLOAD1024',
        'assembly_sha256': ASSEMBLY_SHA256,
        'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'checked': checked, 'controls_rejected': rejected,
        'scope': 'Recorded exact cutoffs also satisfy the stronger 1024-bit linear reserve. '
                 'No change to the supplier, endpoint, kappa or inherited theorem assumptions.'
    }, indent=2))


if __name__ == '__main__':
    main()
