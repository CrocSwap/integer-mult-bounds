"""Independent positive-binomial moment signs and 1024-bit outer witness.

The binomial engine is the merged PR960 audit (following PR678's distinct
binomial-series arithmetic). The outer theorem inequalities are inherited.
Prepared with OpenAI Codex assistance; Apache-2.0.
"""
import argparse
from fractions import Fraction as Q
from pathlib import Path
from support import P, ROOT, SOURCE, T37, dump, load, read, require, sha


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work', type=Path, required=True)
    args = parser.parse_args()
    claim = read(P / 'CLAIM.json')
    counted = read(args.work / 'INDEPENDENT-OWNERS.json')
    require(counted['profile'] == claim['profile'], 'Price actual independently recounted profile')
    engine_path = ROOT / 'research/t21-binomial-audit/verify.py'
    engine = load(engine_path, 'e4_positive_binomial')
    outer_path = SOURCE / 'engines/outer.py'
    outer = load(outer_path, 'e4_retained_outer')
    profile = {int(k): v for k, v in counted['profile'].items()}
    b, c = Q(claim['complex_lower']), Q(claim['bit_lower'])
    bracket = engine.brackets(profile, 73, counted['live'], b, False)
    old = read(T37 / 'CLAIM.json')
    before = {int(k): v for k, v in old['profile'].items()}
    difference = {r: profile.get(r, 0) - before.get(r, 0) for r in set(profile) | set(before)}
    require({r: n for r, n in difference.items() if n} == {1: -12, 2: 8, 3: 4, 4: -4}, 'Exact global profile change')
    require(sum(r*n for r, n in difference.items()) == 0, 'Conserved rank mass')
    gain_upper = Q(0)
    for r, n in difference.items():
        lo, hi, _ = engine.power_interval(r, 73, b)
        gain_upper += r*n*(hi if n >= 0 else lo)
    require(gain_upper < 0, 'Strict moment improvement at nominated exponent')
    eta = beta = Q(1, 10**24)
    s = min(c, (1-beta)*b) - Q(1, 10**27)
    require(0 < s < c and s < (1-beta)*b, 'Strict inner exponent')
    chain = [Q(384599, 10**10)]
    cuts = []
    payload = counted['charged_prefix_bits']
    require(payload == 1024 and counted['prefix_bits'] < payload, 'Actual prefix payload')
    for _ in range(7):
        previous = chain[-1]
        exponent = (1-s)*s + s*previous
        gap = min(s-exponent, 1-exponent-s, 1-exponent-s*(1-previous), 1-s)
        require(previous < exponent < s < 1-exponent and gap > 0, 'Bootstrap gap')
        ceil = lambda value: -(-value.numerator // value.denominator)
        cutoff = max(ceil(36/gap**2), ceil(2*(4+payload)/gap))
        require(cutoff*gap**2 >= 36 and cutoff*gap >= 2*(4+payload), 'Full-payload cutoff')
        cuts.append(dict(exponent=str(exponent), gap=str(gap), cutoff_log2=str(cutoff)))
        chain.append(exponent)
    bridge = {'semantic': {'C0': {'base': 2, 'exponent': 210000}, 'strict_literal_gap': 1},
              'rows': {'degree_gap': Q(10**6)-Q(51*20161, 25)}}
    kappa = Q(claim['kappa'])
    admitted = outer.assembly(chain[-1], b, bridge, kappa, eta=eta, beta=beta)
    constraints = admitted['strict_constraints']
    require(len(constraints) == 47 and all(v > 0 for v in constraints.values()), 'All outer inequalities')
    rejected = []
    for name, kk, ee, bb in [('next_grid', kappa+Q(1, 10**18), eta, beta),
                              ('zero_eta', kappa, Q(0), beta), ('zero_beta', kappa, eta, Q(0)),
                              ('unit_beta', kappa, eta, Q(1))]:
        try:
            outer.assembly(chain[-1], b, bridge, kk, eta=ee, beta=bb)
        except AssertionError:
            rejected.append(name)
        else:
            raise ValueError('Outer control accepted: ' + name)
    require(kappa > Q(old['kappa']), 'Strict selected-baseline improvement')
    dump(args.work / 'INDEPENDENT-PRICE.json', dict(
        status='PASS_BINOMIAL_MOMENTS_AND_1024_BIT_OUTER', root=bracket,
        kappa=str(kappa), baseline_kappa=old['kappa'], gain=str(kappa-Q(old['kappa'])),
        signed_profile_change=difference, signed_moment_change_upper=str(gain_upper),
        charged_prefix_bits=payload, bootstrap=cuts,
        outer={k: str(v) for k, v in constraints.items()}, controls_rejected=rejected,
        sources={str(p.relative_to(ROOT)): sha(p) for p in (engine_path, outer_path)},
        owner_receipt_sha256=sha(args.work / 'INDEPENDENT-OWNERS.json')))
    print('PASS_BINOMIAL_MOMENTS_AND_1024_BIT_OUTER', claim['kappa_decimal'])


if __name__ == '__main__':
    main()
