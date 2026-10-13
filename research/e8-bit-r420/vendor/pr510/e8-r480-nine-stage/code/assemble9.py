# Nine-stage bit price and cited outer assembly. Bit half: the nine-stage invoice of PR #463 code/assemble_k.py (verbatim apart from
# dropping its complex half); outer half: PR #493 code/eleven/assemble.py's per-supplier loop (verbatim). Prepared by DreamingOfClouds
# with Claude Opus 5.5 (Anthropic), via Claude Code. Apache-2.0.
# usage: assemble9.py BASE BIT_DIR AUDIT.json PR493_PACKAGE OUT.json SUPPLIER[,SUPPLIER...]
import importlib.util, json, sys, math
from fractions import Fraction as Q
from pathlib import Path
base, bd, ap, root, outp = map(Path, sys.argv[1:6]); names = sys.argv[6].split(',')
eng = root / 'code/hub/e8-r740-replica32/code/engines'
def load(name):
    sp = importlib.util.spec_from_file_location('e_' + name, eng / (name + '.py')); mod = importlib.util.module_from_spec(sp); sp.loader.exec_module(mod); return mod
M, Other, Outer = load('moment'), load('base_two_moment'), load('outer')
cited = {s["name"]: s for s in json.loads((root / "data/complex-b.json").read_text())["suppliers"]}
audit = json.loads(ap.read_text()); bg = json.loads((bd / 'GLOBAL.json').read_text())
assert audit['template_sha256'] == bg['template_sha256'] and audit['status'] == 'PASS_INDEPENDENT_REPLICATED_HOSTING_AUDIT'
P = {int(r): n for r, n in audit['profile'].items()}; m, W = bg['m'], audit['live']; E = sum(P.values())
geo = json.loads((base / 'nine/GEOMETRY.json').read_text()); pg = json.loads((base / 'nine/GLOBAL.json').read_text())
T, R, V = pg['replicas'], pg['R'], 120; L = (m - 1) // 7; K = (L - 1) // 2; assert L % 2 == 1 and m == 1 + 7 * L
DEPTH = bg['halving_depth']; DEFICIT = T * (2 * K * V - 9 * 8 * L)
assert bg['m'] == m and bg['replicas'] == T and bg['R'] == R and bg['deficit'] == DEFICIT
mass = sum(r * z for r, z in P.items()); assert m * W - mass == DEFICIT
physical = W + 9; d = m * m; N = 2 * m
unit = L * T * pg['local_additions'] + pg['bridge_additions']
J = 8 * T * L * (2 * V + R) + 8 * (2 * K * V * T) + 2 * L * T * R + 2 * pg['copy_erase_episodes']
high = 16 * (d + 1) ** 2; good = 8 * m * m + 8; compiler = 128 * N ** 3
selectors = 2 * L * T * ((W - 1) + R * m * (geo['max_route_factors'] + 144 + 2 + (m - 1) + m))
prefix = int(pg['global_prefix_bound']); charged_prefix = 64 * ((prefix.bit_length() + 63) // 64)
coefficient = unit + J * high + J * physical + E * (good + compiler) + 16 * m ** 3 + pg['copy_erase_episodes'] + selectors + prefix + 1
two = (coefficient + 1) ** DEPTH * (E + 1) ** DEPTH; charged_two = 512 if two.bit_length() <= 512 else 64 * ((two.bit_length() + 63) // 64)
assert two < 1 << charged_two and 2 * max(P) ** DEPTH < m ** DEPTH
row = DEPTH * (m * m + 1) + 9909 + 252; assert row == 18355 and row < 20161
root_ = M.certify(P, m, W, True); c = Q(root_['lower']); chi = Q(root_['upper'])
fb = 32 * m * m * E
lo, hi = Other.moment(m, W, list(P.items()), c); bl, bh = Other.moment(m, W, [(1, fb)], c); assert hi + bh / 10 ** 16 < 1
lo2, hi2 = Other.moment(m, W, list(P.items()), chi); bl2, bh2 = Other.moment(m, W, [(1, fb)], chi); assert lo2 + bl2 / 10 ** 16 > 1
res = dict(status='PASS_NINE_STAGE_WHOLE_HOSTED_BIT_PRICE_AND_CITED_ASSEMBLY', R=R, stages=L, replicas=T, bit_lower=str(c), bit_lower_decimal=root_['lower'],
           next_grid_point_rejected=str(chi), bit=dict(live=W, physical=physical, maxchild=max(P), rank_mass=mass, hosted_residuals=audit['hosted_residuals'],
           bank_assignments=audit.get('bank_assignments'), prefix_bits=prefix.bit_length(), charged_prefix_bits=charged_prefix, coefficient_bits=coefficient.bit_length(),
           two_level_coefficient_bits=two.bit_length(), charged_two_level_coefficient_bits=charged_two, row_coefficient=row, halving_depth=DEPTH),
           bit_profile={str(r): n for r, n in sorted(P.items())}, emitted_program_sha256=bg.get('emitted_program_sha256'), kappa={})
def ceil(x): return -((-x.numerator) // x.denominator)
for name in names:
    b = Q(cited[name]["b"])
    eta = beta = Q(1, 10 ** 18); grid = Q(1, 10 ** 18); s = min(c, (1 - beta) * b) - Q(1, 10 ** 24)
    assert 0 < s < c and s < (1 - beta) * b
    chain = [Q(384599, 10 ** 10)]; cutoffs = []
    for j in range(6):
        old = chain[-1]; a = (1 - s) * s + s * old
        gap = min(s - a, 1 - a - s, 1 - a - s * (1 - old), 1 - s); assert old < a < s < 1 - a and gap > 0
        cutoff = max(ceil(36 / gap ** 2), ceil(2 * (4 + charged_two) / gap)); assert cutoff * gap ** 2 >= 36 and cutoff * gap >= 2 * (4 + charged_two)
        cutoffs.append(dict(gap=str(gap), cutoff_log2=str(cutoff))); chain.append(a)
    q = chain[-1] * (1 - 2 * eta); margin = (1 - eta) * q / (1 + q); ticks = margin / grid; k = grid * ((ticks.numerator - 1) // ticks.denominator)
    bridge = {'semantic': {'C0': {'base': 2, 'exponent': 210000}, 'strict_literal_gap': 1}, 'rows': {'degree_gap': Q(10 ** 6) - Q(51 * 20161, 25)}}
    a = Outer.assembly(chain[-1], b, bridge, k, eta=eta, beta=beta)
    assert len(a['strict_constraints']) == 47 and all(x > 0 for x in a['strict_constraints'].values())
    controls = []
    for cname, kk, ee, bb in [('next_grid', k + grid, eta, beta), ('zero_eta', k, Q(0), beta), ('zero_beta', k, eta, Q(0)), ('unit_beta', k, eta, Q(1))]:
        try: Outer.assembly(chain[-1], b, bridge, kk, eta=ee, beta=bb)
        except AssertionError: controls.append(cname)
        else: raise AssertionError(cname)
    res['kappa'][name] = dict(complex_lower=str(b), kappa=str(k), kappa_decimal=format(float(k), '.18f'),
                              binding_component='bit' if c < (1 - beta) * b else 'complex', strict_outer_constraints=47, outer_controls=controls)
outp.write_text(json.dumps(res, indent=1) + '\n')
print('   nine-stage bit c = %s = %s; profile %s; prefix %d bits, two-level %d bits (charged %d), row %d, depth %d'
      % (c, root_['lower'], res['bit_profile'], prefix.bit_length(), two.bit_length(), charged_two, row, DEPTH))
for name, x in res['kappa'].items(): print('   %s: b %s kappa %s (%s-bound) 47/47, controls %s' % (name, x['complex_lower'], x['kappa_decimal'], x['binding_component'], ','.join(x['outer_controls'])))
