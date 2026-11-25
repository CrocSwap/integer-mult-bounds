# SPDX-License-Identifier: Apache-2.0
"""Exact finite profile comparison; no native or outer admission inferred."""
import hashlib
import json
from fractions import Fraction as Q
from pathlib import Path
from price import interval, compact, need

HERE = Path(__file__).resolve().parent


def check(profile):
    expected = json.loads((HERE / 'EXPECTED.json').read_text())
    raw = (HERE / 'FRONTIER.json').read_bytes()
    need(hashlib.sha256(raw).hexdigest() == expected['frontier_sha256'],
         'exact predecessor claim')
    predecessor = json.loads(raw)
    profile = {int(r): n for r, n in profile.items()}
    need(profile == {int(r): n for r, n in expected['profile'].items()},
         'actual reconstructed profile')
    need(all(type(n) is int and n >= 0 for n in profile.values()),
         'nonnegative integer profile')
    old = {int(r): n for r, n in predecessor['profile'].items()}
    need(type(expected['replicas']) is int and expected['replicas'] > 0 and
         type(predecessor['replicas']) is int and predecessor['replicas'] > 0,
         'positive integer replica normalization')
    delta = {r: predecessor['replicas'] * profile.get(r, 0) - expected['replicas'] * old.get(r, 0)
             for r in set(profile) | set(old)}
    need(sum(r*n for r, n in delta.items()) == 0, 'equal rank mass')
    difference = interval(delta, Q(predecessor['root_interval'][1]))
    need(difference[1] < 0, 'strict cost decrease')
    signed = dict(profile)
    signed[73] = signed.get(73, 0) - 896 * expected['replicas']
    lo, hi = map(Q, expected['root_interval'])
    lower, upper = interval(signed, lo), interval(signed, hi)
    need(lower[1] < 0 and upper[0] > 0, 'exact root bracket')
    endpoint = lo - Q(1, 10**46) - Q(1, 10**70)
    need(endpoint == Q(expected['candidate_endpoint']) and
         endpoint > Q(predecessor['kappa']), 'strict candidate endpoint')
    return {'status': 'PASS_EXACT_FINITE_PROFILE_COMPARISON',
            'cross_multiplied_delta_vs_predecessor': delta,
            'cost_difference': compact(difference),
            'root_interval': list(map(str, (lo, hi))),
            'lower_check': compact(lower), 'upper_check': compact(upper),
            'scope': 'Finite profile only; complete release is separate.'}


if __name__ == '__main__':
    # This convenience command prices the pinned expectation. The aggregate
    # verifier must call check() on its independently reconstructed profile.
    data = json.loads((HERE / 'EXPECTED.json').read_text())
    print(json.dumps(check(data['profile']), indent=2))
