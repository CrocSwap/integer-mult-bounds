"""(493-helper copy) Exact paid moments, three finite ordinary levels and PR234's outer-47 assembly for the banked five-stage bit
supplier. Uses PR234's own pinned moment, bootstrap and assembly code unchanged.
Prepared by Rohan Arun with Anthropic Claude assistance. Apache-2.0.
"""
from fractions import Fraction as Q
from pathlib import Path
import importlib.util

PKG = 'research/five-stage-source-bound-v8'
PR234_KAPPA = Q(703701743496697, 10 ** 18)
PR230_KAPPA = Q(694787513005285, 10 ** 18)
PR237_KAPPA = Q(177145602695277, 250000000000000000)   # PR237: banks on PR234's 471-source five-stage helper


def load(name, path):
    s = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
    return m


def build(P234, pr234_math, physical):
    """pr234_math: PR234's freshly computed mathematics (bit_profile, complex_profile, assembly parameters)."""
    math = load('pr234_moments', P234 / PKG / 'code/five_stage_bit_cost_20261009.py')
    outer = load('pr234_outer47', P234 / PKG / 'code/paired_cube_assembly.py')
    bp = pr234_math['bit_profile']; cp = pr234_math['complex_profile']
    assert (bp['m'], bp['deficit'], bp['maxchild']) == (120, 4400, 100)
    H = {int(k): n for k, n in bp['histogram'].items()}
    removed = {int(k): n for k, n in physical['removed_exteriors'].items()}
    for r, n in removed.items():
        assert H[r] >= n; H[r] -= n
    c = physical['copies']; m = 120
    H = {r: c * n for r, n in H.items() if n}
    W = physical['W']; mass = sum(r * n for r, n in H.items()); deficit = m * W - mass
    assert deficit == c * bp['deficit'], 'banking preserves the telescoping deficit'
    assert max(H) < m // 2
    # Coarse paid saving on the 10^-18 grid, PR234's interval engine with the inherited bad-class envelope.
    root = Q(math.certify(H, m, W, True)['lower']); den = 10 ** 18
    lo = Q(int(root * den), den)
    while math.moment(H, m, W, lo, True)[1] >= 1: lo -= Q(1, den)
    hi = lo + Q(1, den)
    while math.moment(H, m, W, hi, True)[0] <= 1: lo = hi; hi = lo + Q(1, den)
    assert math.moment(H, m, W, lo, True)[1] < 1 < math.moment(H, m, W, hi, True)[0]
    coarse = lo
    unbanked = {int(k): n for k, n in bp['histogram'].items()}
    old_coarse = Q(pr234_math['contract']['assembly']['bit_coarse']) if 'contract' in pr234_math else None
    if old_coarse is not None:
        assert math.moment(H, m, W, old_coarse, True)[1] < math.moment(unbanked, m, bp['W'], old_coarse, True)[0], \
            'banking strictly improves the paid moment at PR234 coarse saving'
    chain = [Q(384599, 10 ** 10)]
    for _ in range(3):
        a = (1 - coarse) * coarse + coarse * chain[-1]
        assert chain[-1] < a < coarse < 1 - a
        chain.append(a)
    bit = chain[-1]
    b = Q(pr234_math['assembly']['parameters']['a_complex'])
    cm = math.moment({int(k): n for k, n in cp['histogram'].items()}, 110, cp['W'], b, False)
    assert cm[1] < 1
    eta = Q(1, 10 ** 12); beta = Q(1, 10 ** 9)
    assert bit < (1 - beta) * b
    bridge = dict(proof='PROOF.md', representation='Exact powers with source-bound finite overcharges',
                  semantic=dict(G=dict(base=2, exponent=30000), E=dict(base=2, exponent=100000),
                                B_upper=dict(base=2, exponent=100001), C0=dict(base=2, exponent=210000), C1=1,
                                strict_literal_gap=1, induction_gap_lower=1),
                  rows=dict(coefficient=20161, degree=10 ** 6, suffix_slope=4 * 10 ** 6,
                            degree_gap=Q(10 ** 6) - Q(51 * 20161, 25)))
    q = bit * (1 - 2 * eta); minimum = (1 - eta) * q / (1 + q); ticks = minimum * den
    kappa = Q(ticks.numerator // ticks.denominator, den)
    if kappa == minimum: kappa -= Q(1, den)
    result = outer.assembly(bit, b, bridge, kappa, eta=eta, beta=beta)
    assert len(result['strict_constraints']) == 47 and len(result['margins']) == 7
    assert all(x > 0 for x in result['strict_constraints'].values())
    try: outer.assembly(bit, b, bridge, kappa + Q(1, den), eta=eta, beta=beta)
    except AssertionError: pass
    else: raise AssertionError('adjacent kappa grid point admitted')
    assert kappa > PR237_KAPPA > PR234_KAPPA > PR230_KAPPA
    controls = []
    try: profile_check({**H, 1: H[1] + 1}, m, W, c * bp['deficit'])
    except AssertionError: controls.append('changed rank mass rejected')
    else: raise AssertionError('corrupt rank mass accepted')
    try: math.moment({**H, m: 1}, m, W, coarse, True)
    except AssertionError: controls.append('full-width child rejected')
    else: raise AssertionError('full-width child accepted')
    return dict(scope='Conditional finite supplier composition; PR234 physical, scalar, prime and analytic dependencies inherited',
                bit_profile=dict(m=m, W=W, copies=c, histogram={str(r): n for r, n in sorted(H.items())},
                                 calls=sum(H.values()), rank_mass=mass, deficit=deficit, maxchild=max(H)),
                bit_coarse_saving=coarse, pr234_bit_coarse_saving=old_coarse, ordinary_chain=chain, bit=bit,
                complex_saving=b, complex_moment_interval=cm, assembly=result, kappa=kappa,
                comparison_pr234_kappa=PR234_KAPPA, relative_gain_over_pr234=kappa / PR234_KAPPA - 1,
                comparison_pr230_kappa=PR230_KAPPA, comparison_pr237_kappa=PR237_KAPPA,
                relative_gain_over_pr237=kappa / PR237_KAPPA - 1, controls=controls)


def profile_check(H, m, W, deficit):
    assert m * W - sum(r * n for r, n in H.items()) == deficit
    return True
