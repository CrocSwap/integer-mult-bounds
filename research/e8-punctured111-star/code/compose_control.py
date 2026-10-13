# Outer composition of a bit c with a cited complex b, and the control that reproduces PR #535's published kappa.
# The outer half is PR #472's / #493's assemble.py verbatim (six bootstrap levels, 47 strict inequalities, next-grid and
# invalid-parameter controls), here as a function of (c, b) so that the SAME code is run on
#   control : PR #535's inputs (the live bit c of PR #510, #535's complex b)  -> must give #535's published kappa exactly
#   star    : this package's c and the same b                                   -> must equal the kappa that assemble.py wrote
# No bit port count enters: the bit unit has v = 111 ports, #535's complex word has its own; the outer assembly sees only
# the two real numbers c and b, the bit's charged coefficient bits (bootstrap cutoffs only) and the row bound.
# Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code; engines are PR #315's / #361's (pinned in the parent). Apache-2.0.
"""usage: compose_control.py PARENT_PACKAGE RESULT.json PR535_EXPECTED.json OUT.json"""
import importlib.util
import json
import sys
from fractions import Fraction as Q
from pathlib import Path

parent, resp, e535p, outp = map(Path, sys.argv[1:5])
eng = parent / 'code/hub/e8-r740-replica32/code/engines'


def load(name):
    sp = importlib.util.spec_from_file_location('comp_' + name, eng / (name + '.py'))
    mod = importlib.util.module_from_spec(sp); sp.loader.exec_module(mod); return mod


Outer = load('outer')


def ceil(x): return -((-x.numerator) // x.denominator)


def compose(c, b, coeff_bits, row=20161):
    eta = beta = grid = Q(1, 10 ** 18)
    s = min(c, (1 - beta) * b) - Q(1, 10 ** 24)
    assert 0 < s < c and s < (1 - beta) * b
    chain, cuts = [Q(384599, 10 ** 10)], []
    for _ in range(6):
        old = chain[-1]; a = (1 - s) * s + s * old
        gap = min(s - a, 1 - a - s, 1 - a - s * (1 - old), 1 - s); assert old < a < s < 1 - a and gap > 0
        cut = max(ceil(36 / gap ** 2), ceil(2 * (4 + coeff_bits) / gap))
        assert cut * gap ** 2 >= 36 and cut * gap >= 2 * (4 + coeff_bits)
        cuts.append(str(cut)); chain.append(a)
    q = chain[-1] * (1 - 2 * eta); margin = (1 - eta) * q / (1 + q); ticks = margin / grid
    k = grid * ((ticks.numerator - 1) // ticks.denominator)
    bridge = {'semantic': {'C0': {'base': 2, 'exponent': 210000}, 'strict_literal_gap': 1},
              'rows': {'degree_gap': Q(10 ** 6) - Q(51 * row, 25)}}
    a = Outer.assembly(chain[-1], b, bridge, k, eta=eta, beta=beta)
    assert len(a['strict_constraints']) == 47 and all(x > 0 for x in a['strict_constraints'].values())
    ctl = []
    for name, kk, ee, bb in [('next_grid', k + grid, eta, beta), ('zero_eta', k, Q(0), beta), ('zero_beta', k, eta, Q(0)), ('unit_beta', k, eta, Q(1))]:
        try: Outer.assembly(chain[-1], b, bridge, kk, eta=ee, beta=bb)
        except AssertionError: ctl.append(name)
        else: raise AssertionError(name)
    return dict(kappa=k, binding='bit' if c < (1 - beta) * b else 'complex', controls=ctl, strict=47)


e535 = json.loads(e535p.read_text()); res = json.loads(resp.read_text())
b = Q(e535['complex_lower']); c510 = Q(e535['bit_lower']); k535 = Q(e535['kappa'])
ctl = compose(c510, b, 512)                   # #535 adds the PR #510 nine-stage bit (charged two-level coefficient 512 bits)
assert ctl['kappa'] == k535 and ctl['binding'] == e535['binding_component'] == 'bit', (ctl, e535['kappa'])
c = Q(res['bit_lower'])
star = compose(c, b, res['bit']['charged_three_level_coefficient_bits'])
assert str(b) == res['kappa']['pr535']['complex_lower'] and star['kappa'] == Q(res['kappa']['pr535']['kappa'])
assert star['binding'] == res['kappa']['pr535']['binding_component']
out = dict(complex_lower=str(b), pr535_published_kappa=str(k535), pr535_published_kappa_decimal=e535['kappa_decimal'],
           control_bit_lower=str(c510), control_kappa=str(ctl['kappa']), control_binding=ctl['binding'],
           control_reproduces_pr535_kappa=True, control_outer_controls=ctl['controls'],
           star_bit_lower=str(c), kappa_star_vs_pr535=str(star['kappa']), star_binding=star['binding'],
           star_outer_controls=star['controls'], star_strict_constraints=star['strict'],
           kappa_gain_over_pr535=str(star['kappa'] / k535 - 1), bit_headroom_over_complex_b=str(c / ((1 - Q(1, 10 ** 18)) * b) - 1))
outp.write_text(json.dumps(out, indent=1) + '\n')
print('   control: #510 bit c %s + #535 b -> kappa %s == #535 published %s (bit-bound), 47/47 strict, controls %s'
      % (e535['bit_decimal'], ctl['kappa'], k535, ','.join(ctl['controls'])))
print('   star   : bit c %s + #535 b -> kappa %s (%s-bound), 47/47 strict; %+.4f%% over #535; bit c exceeds (1-1e-18)b by %+.4f%%'
      % (res['bit_lower_decimal'], star['kappa'], star['binding'], 100 * float(star['kappa'] / k535 - 1),
         100 * float(c / ((1 - Q(1, 10 ** 18)) * b) - 1)))
