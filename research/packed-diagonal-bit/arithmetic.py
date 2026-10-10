"""Exact paid moments, finite ordinary-leaf composition and the balanced assembly.

Adapted from PR197's arithmetic.py (Evan McKinney; PR185/187 finite bootstrap, PR193 balanced bridge inherited):
the bit supplier is PR200's terminal-modified diagonal-circuit word instead of PR187's.
Prepared by Rohan Arun with Anthropic Claude assistance. Apache-2.0.
"""
from fractions import Fraction as Q
from pathlib import Path
import importlib.util, json

BIT_PACKAGE = 'research/paired-cube-diagonal-bit-168'
PR202_KAPPA = Q(6768823, 10 ** 10)       # PR202: v4 source-assisted complex + PR200 bit, theta wrapper
PR199_KAPPA = Q(1693287, 2500000000)      # PR199: PR200 bit priced with PR193 complex, finite leaf composition


def load(name, path):
    s = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
    return m


def build(ROOT, BIT, physical):
    im = load('interval_moment', BIT / BIT_PACKAGE / 'arithmetic/interval_moment.py')
    assembly = load('frontier_assembly', ROOT / 'scripts/paired_cube_assembly.py')
    p = physical
    c191 = json.loads((ROOT / 'research/source-assisted-v4/certificate.json').read_text())
    b200 = json.loads((BIT / BIT_PACKAGE / 'certificate.json').read_text())['bit']

    def profile(m, W, H, delta):
        H = {int(r): int(n) for r, n in H.items()}
        return dict(m=m, W=W, child_multiplicities=H, N=delta, L=0, total_rank=sum(r * n for r, n in H.items()), maxchild=max(H))
    cp = c191['complex_profile']; cp = profile(cp['m'], cp['W_per_vertex'], cp['child_histogram'], cp['deficit_per_vertex'])
    bp = b200['profile']
    unpacked = profile(bp['m'], bp['W_per_vertex'], bp['child_histogram'], bp['deficit_per_vertex'])
    assert unpacked['total_rank'] == bp['rank_per_vertex'] and unpacked['maxchild'] == bp['maxchild'] == 60
    packed = profile(72, p['W'], p['child_histogram'], p['deficit'])

    def paid(row, a, bit):
        result = im.moment(row, a)
        if bit:
            l, u = im.log_interval(Q(row['m'])); e, f = im.exp_interval(a * l, a * u)
            w = Q(1, 10 ** 16) * Q(32 * row['m'] * sum(row['child_multiplicities'].values()), row['W'])
            result.update(lower=result['lower'] + w * e, upper=result['upper'] + w * f)
        return result

    def certify(row, bit):
        den = 10 ** 18; lo = 0; hi = den // 100
        assert paid(row, Q(lo, den), bit)['upper'] < 1 < paid(row, Q(hi, den), bit)['lower']
        while hi - lo > 1:
            mid = (lo + hi) // 2; v = paid(row, Q(mid, den), bit)
            if v['upper'] < 1: lo = mid
            elif v['lower'] > 1: hi = mid
            else: raise AssertionError('Interval inconclusive')
        a = Q(lo, den); b = Q(hi, den)
        return dict(saving=a, accepted=paid(row, a, bit), next_excluded=paid(row, b, bit))

    complex_cert = certify(cp, False)
    original = certify(unpacked, True); new = certify(packed, True)
    assert original['saving'] == Q(b200['coarse']['coarse_saving'])
    assert new['saving'] > original['saving']
    assert paid(packed, original['saving'], True)['upper'] < paid(unpacked, original['saving'], True)['lower']
    # Finite-depth ordinary supplier composition, as in PR185/187/197, from PR200's completed ordinary supplier.
    old = Q(b200['coarse']['ordinary_saving']); coarse = new['saving']; chain = [old]
    for _ in range(3):
        a = (1 - coarse) * coarse + coarse * chain[-1]
        assert chain[-1] < a < coarse < 1 - a
        chain.append(a)
    assert 0 < p['conservative_selector_calls'] < 2 ** 40
    # Additional chart/router calls use the inherited completed ordinary selector; their exponent is at most the
    # atom exponent coarse, which is below 1 - ordinary.
    assert coarse < 1 - chain[-1]
    bridge = c191['assembly']['finite_bridge']; bridge['rows']['degree_gap'] = Q(bridge['rows']['degree_gap'])
    beta = eta = Q(1, 10 ** 24); weak = Q(1, 10 ** 30); den = 10 ** 18

    def assemble(bit_saving):
        b = complex_cert['saving']; a = min(bit_saving, (1 - beta) * b - weak)
        q = a * (1 - 2 * eta); bound = (1 - eta) * q / (1 + q); z = bound * den
        k = Q((z.numerator - 1) // z.denominator, den)
        out = assembly.assembly(a, b, bridge, k, eta=eta, beta=beta)
        assert len(out['strict_constraints']) == 47 and len(out['margins']) == 7
        try: assembly.assembly(a, b, bridge, k + Q(1, den), eta=eta, beta=beta)
        except AssertionError: pass
        else: raise AssertionError('Next final grid accepted')
        constraints = out.pop('strict_constraints')
        out['strict_constraint_count'] = len(constraints)
        out['minimum_constraint'] = min(constraints.values())
        return dict(kappa=k, assembly=out, binding='complex' if a == (1 - beta) * b - weak else 'bit')
    before = assemble(old); after = assemble(chain[-1])
    del before['assembly']
    assert before['kappa'] < after['kappa'] and after['binding'] == 'bit'
    assert after['kappa'] > PR202_KAPPA and after['kappa'] > PR199_KAPPA
    controls = []
    bad = dict(packed, total_rank=packed['total_rank'] + 1)
    try: paid(bad, coarse, True)
    except ValueError: controls.append('changed rank mass')
    else: raise AssertionError('Corrupt mass accepted')

    return dict(scope='Conditional composition; physical and finite bridge proof dependencies are separate',
                source_commits=dict(complex='187e1010ac8b259af8e9b5166f68b64bc27b4b47', bit='a1175449f34d39ff933d9d8ab23ced1f32b290ec'),
                complex_profile=cp, unpacked_profile=unpacked, packed_profile=packed, complex=complex_cert,
                bit_before=original, bit_after=new, bit_coarse_relative_gain=new['saving'] / original['saving'] - 1,
                stock_relative_reduction=1 - Q(p['W'], 3 * unpacked['W']), ordinary_chain=chain,
                extra_selector_calls=p['conservative_selector_calls'], selector_toll_gap=1 - chain[-1] - coarse,
                comparison_pr202_kappa=PR202_KAPPA, comparison_pr199_kappa=PR199_KAPPA,
                before_packing=before, after_packing=after,
                kappa_gain_from_packing=after['kappa'] - before['kappa'],
                relative_gain_over_pr202=after['kappa'] / PR202_KAPPA - 1, controls=controls)
