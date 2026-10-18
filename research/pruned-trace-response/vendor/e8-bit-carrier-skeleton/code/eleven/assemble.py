"""Exact eleven-stage bit pricing and outer assembly against cited complex suppliers.
The bit half is PR #472's code/assemble.py (chafreaky, with OpenAI Codex assistance; DaysSky's PR #442 hosting
assembly before it) with R as a parameter: the two PR #315 moment engines (DreamingOfClouds) with the inherited
10^-16 bad-branch allowance on the audited profile (m = 78, W = 9600), the finite invoice with the hosted stock
(physical prefix charged to the next 64-bit block, three-level coefficient likewise), three-level halving and PR #445's
elementary orthogonal-cover row bound.  The outer half is the same file's assembly (#434/#315: six bootstrap levels,
47 strict inequalities, next-grid and invalid-parameter controls), run once per cited complex b; the complex b values
are cited from their PRs' receipts (code/cited.py), not rebuilt.
usage: assemble.py BIT_DIR R PACKAGE_DIR OUT.json SUPPLIER[,SUPPLIER...]
Prepared by eumemic with substantial Anthropic Claude assistance; Apache-2.0."""
import importlib.util
import json
import sys
from fractions import Fraction as Q
from pathlib import Path

bd = Path(sys.argv[1]); R = int(sys.argv[2]); root = Path(sys.argv[3]); outp = Path(sys.argv[4])
names = sys.argv[5].split(",")
eng = root / "code/hub/e8-r740-replica32/code/engines"
sys.path.insert(0, str(root / "code/hub/r740-hosted-eleven/code"))
from row_bound import bound as row_bound, controls as row_controls  # noqa: E402


def load(name):
    sp = importlib.util.spec_from_file_location('hosted_' + name, eng / (name + '.py'))
    mod = importlib.util.module_from_spec(sp); sp.loader.exec_module(mod); return mod


M, Other, Outer = load('moment'), load('base_two_moment'), load('outer')
cited = {s["name"]: s for s in json.loads((root / "data/complex-b.json").read_text())["suppliers"]}
# ---------------- bit: PR #472's arithmetic, verbatim apart from R
audit = json.loads((bd / "AUDIT.json").read_text()); bg = json.loads((bd / 'GLOBAL.json').read_text())
assert audit['template_sha256'] == bg['template_sha256'] and audit['status'] == 'PASS_INDEPENDENT_ELEVEN_STAGE_HOSTING_AUDIT'
P = {int(r): n for r, n in audit['profile'].items()}; m, W = 78, audit['live']; E = sum(P.values())
geo = json.loads((bd / 'GEOMETRY.json').read_text()); pg = bg
T, L, V, K = 8, 11, 120, 5
assert pg["replicas"] == T and pg["R"] == R
mass = sum(r * z for r, z in P.items()); assert m * W - mass == (2 * K * V - L * 72) * T
physical = W + 9; d = m * m; N = 2 * m
unit = L * T * pg['local_additions'] + pg['bridge_additions']
J = 8 * T * L * (2 * V + R) + 8 * (2 * K * V * T) + 2 * L * T * R + 2 * pg['copy_erase_episodes']   # every helper route charged
high = 16 * (d + 1) ** 2; good = 8 * m * m + 8; compiler = 128 * N ** 3
selectors = 2 * L * T * ((W - 1) + R * m * (geo['max_route_factors'] + 144 + 2 + (m - 1) + m))
prefix = int(pg['global_prefix_bound']); charged_prefix = 64 * ((prefix.bit_length() + 63) // 64)
assert prefix < 1 << charged_prefix and charged_prefix == pg['charged_prefix_bits']
assert audit['physical_prefix_bits'] == prefix.bit_length()
coefficient = unit + J * high + J * physical + E * (good + compiler) + 16 * m ** 3 + pg['copy_erase_episodes'] + selectors + prefix + 1
two = (coefficient + 1) ** 3 * (E + 1) ** 3; charged_two = 64 * ((two.bit_length() + 63) // 64)
assert two < 1 << charged_two and 2 * max(P) ** 3 < m ** 3
assert coefficient < 1 << 100000 and 32 * m * (coefficient + 1) ** 2 < 1 << 210000
rows = row_bound(m, physical, max(P), 3); row = rows["complete_row_coefficient"]
assert row == 19431 < 20161
row_rejected = row_controls()
root_ = M.certify(P, m, W, True); c = Q(root_['lower']); chi = Q(root_['upper'])
fb = 32 * m * m * E
lo, hi = Other.moment(m, W, list(P.items()), c); bl, bh = Other.moment(m, W, [(1, fb)], c); assert hi + bh / 10 ** 16 < 1
lo2, hi2 = Other.moment(m, W, list(P.items()), chi); bl2, bh2 = Other.moment(m, W, [(1, fb)], chi); assert lo2 + bl2 / 10 ** 16 > 1
res = dict(status='PASS_ELEVEN_STAGE_WHOLE_HOSTED_BIT_PRICE_AND_CITED_ASSEMBLY', R=R, bit_lower=str(c),
           bit_lower_decimal=root_['lower'], next_grid_point_rejected=str(chi),
           bit=dict(live=W, physical=physical, maxchild=max(P), rank_mass=mass, hosted_residuals=audit['hosted_residuals'],
                    prefix_bits=prefix.bit_length(), charged_prefix_bits=charged_prefix, coefficient_bits=coefficient.bit_length(),
                    three_level_coefficient_bits=two.bit_length(), charged_three_level_coefficient_bits=charged_two,
                    row_coefficient=row, halving_depth=3),
           bit_profile={str(r): n for r, n in sorted(P.items())}, row_bound=rows, row_controls=row_rejected,
           bit_template_sha256=bg['template_sha256'], emitted_program_sha256=bg['emitted_program_sha256'],
           audit_mutations_rejected=len(audit['mutations_rejected']), kappa={})


def ceil(x): return -((-x.numerator) // x.denominator)


# ---------------- outer assembly exactly as PR #472 (#434's combined.py), once per cited complex b
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
                              binding_component='bit' if c < (1 - beta) * b else 'complex', strict_outer_constraints=47,
                              outer_controls=controls, bootstrap=cutoffs, complex_status=cited[name]["status"],
                              complex_role=cited[name]["role"])
outp.write_text(json.dumps(res, indent=1) + '\n')
print("   bit c = %s = %s (10^-24 grid; next point rejected); profile %s; prefix %d bits (charged %d), three-level %d bits"
      " (charged %d), row %d" % (c, root_['lower'], res['bit_profile'], prefix.bit_length(), charged_prefix, two.bit_length(),
                                 charged_two, row))
for name, x in res['kappa'].items():
    print("   with PR #%s's complex b = %s: kappa = %s = %s (%s-bound), 47/47 strict, controls %s" %
          (name[2:], x['complex_lower'], x['kappa'], x['kappa_decimal'], x['binding_component'], ",".join(x['outer_controls'])))
