#!/usr/bin/env python3
"""Exact negative control: PR73 does not dominate PR68 at every power."""
from fractions import Fraction
from hashlib import sha256
from math import isqrt
from pathlib import Path
import argparse
import json

def main():
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--new', type=Path, default=here.parent / 'latest-analytic/pr73-candidate.json')
    parser.add_argument('--old', type=Path, default=here.parents[1] / 'transfer-proof/latest-analytic/pr68-candidate.json')
    parser.add_argument('--output', type=Path, default=here / 'normalized-dominance-control.json')
    args = parser.parse_args()
    rawnew, rawold = args.new.read_bytes(), args.old.read_bytes()
    new, old = json.loads(rawnew)['bit'], json.loads(rawold)['bit']
    assert new['m'] == old['m'] == 575
    cn = {int(t): int(c) for t, c in new['child_multiplicities'].items()}
    co = {int(t): int(c) for t, c in old['child_multiplicities'].items()}
    d = {t: cn.get(t, 0) * old['W'] - co.get(t, 0) * new['W'] for t in cn.keys() | co.keys()}
    caps = [sum(v * min(t, k) for t, v in d.items()) for k in range(1, max(d) + 1)]
    scale = 10 ** 18
    lower, upper, bounds = Fraction(), Fraction(), []
    for t, delta in sorted(d.items()):
        k = isqrt(t * scale * scale)
        assert k * k <= t * scale * scale < (k + 1) * (k + 1)
        lo, hi = Fraction(k, scale), Fraction(k + 1, scale)
        lower += delta * (lo if delta >= 0 else hi)
        upper += delta * (hi if delta >= 0 else lo)
        bounds.append({'width': t, 'signed_count_cross_product': delta, 'sqrt_lower': str(lo), 'sqrt_upper': str(hi)})
    denom = new['W'] * old['W']
    lower, upper = lower / denom, upper / denom
    assert lower > 0 and caps[-1] < 0
    report = {
        'status': 'PASS: exact counterexample to universal power dominance',
        'new_candidate_sha256': sha256(rawnew).hexdigest(),
        'old_candidate_sha256': sha256(rawold).hexdigest(),
        'normalization': 'd_t = n_new(t)*W_old - n_old(t)*W_new; denominators are positive.',
        'positive_capped_sums': sum(c > 0 for c in caps), 'total_caps': len(caps),
        'rank_mass_difference_numerator': caps[-1],
        'witness_power': '1/2', 'equivalent_saving': '1/2',
        'sqrt_weighted_difference_interval': [str(lower), str(upper)],
        'relation_to_characteristic': 'This positive interval bounds sqrt(575)*(Psi_new(1/2)-Psi_old(1/2)). Thus the normalized new characteristic is strictly larger at power1/2.',
        'rows': bounds,
        'scope': 'This refutes all-power dominance, not the newer certified saving near power1. Both original certificates and their small-saving inequalities remain valid.'
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(report['status'])
    print('positive difference lower bound:', lower)

if __name__ == '__main__':
    main()
