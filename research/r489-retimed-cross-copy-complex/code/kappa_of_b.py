"""Exact kappa for a complex supplier composed with #493's R489 bit supplier, as #494's assemble_489.py computes it.
usage:
  kappa_of_b.py PR494_ROOT PR493_OUT --b 718766148669433/500000000000000000
  kappa_of_b.py PR494_ROOT PR493_OUT --profile HOSTED.json [--m 73]     (b from a complex global profile, then kappa)
PR494_ROOT is research/ on #494's branch; PR493_OUT is the pr493/ directory of a completed #494 verify output.
The bit side is #493's exact root (asserted equal to its receipt) and its charged three-level coefficient width is
recomputed exactly as in assemble_489.py. Prints b, binding component and kappa; asserts the 47 strict inequalities
and rejects the next kappa grid point. A screen and a cross-check, not a substitute for the package's assembly."""
import argparse, importlib.util, json, sys
from fractions import Fraction as Q
from pathlib import Path
ap = argparse.ArgumentParser(); ap.add_argument('research', type=Path); ap.add_argument('pr493_out', type=Path)
ap.add_argument('--b'); ap.add_argument('--profile', type=Path); ap.add_argument('--m', type=int, default=73)
a = ap.parse_args()
pkg = a.research / 'e8-bit-carrier-skeleton'; eng = pkg / 'code/hub/e8-r740-replica32/code/engines'
def load(name):
    sp = importlib.util.spec_from_file_location('k_' + name, eng / (name + '.py'))
    mod = importlib.util.module_from_spec(sp); sp.loader.exec_module(mod); return mod
M, Other, Outer = load('moment'), load('base_two_moment'), load('outer')
bd = a.pr493_out / 'bit'; audit = json.loads((bd / 'AUDIT.json').read_text()); pg = json.loads((bd / 'GLOBAL.json').read_text())
geo = json.loads((bd / 'GEOMETRY.json').read_text()); r493 = json.loads((a.pr493_out / 'RESULT.json').read_text())
# bit half, verbatim from #494's assemble_489.py
P = {int(r): n for r, n in audit['profile'].items()}; m, W = 78, audit['live']; E = sum(P.values())
T, L, R, V, K = 8, 11, 489, 120, 5
physical = W + 9; d = m * m; N = 2 * m
unit = L * T * pg['local_additions'] + pg['bridge_additions']
J = 8 * T * L * (2 * V + R) + 8 * (2 * K * V * T) + 2 * L * T * R + 2 * pg['copy_erase_episodes']
high = 16 * (d + 1) ** 2; good = 8 * m * m + 8; compiler = 128 * N ** 3
selectors = 2 * L * T * ((W - 1) + R * m * (geo['max_route_factors'] + 144 + 2 + (m - 1) + m))
prefix = int(pg['global_prefix_bound'])
coefficient = unit + J * high + J * physical + E * (good + compiler) + 16 * m ** 3 + pg['copy_erase_episodes'] + selectors + prefix + 1
two = (coefficient + 1) ** 3 * (E + 1) ** 3; charged_two = 64 * ((two.bit_length() + 63) // 64)
root = M.certify(P, m, W, True); c = Q(root['lower']); assert c == Q(r493['bit_lower'])
# complex b
if a.profile:
    h = json.loads(a.profile.read_text()); PC = {int(r): n for r, n in (h.get('global_profile') or h['complex_profile']).items()}
    WC = h.get('live') or h['complex_live']; mc = a.m; EC = sum(PC.values())
    rc = M.certify(PC, mc, WC, True); b = Q(int(Q(rc['lower']) * 10 ** 18), 10 ** 18)
    fbc = 32 * mc * mc * EC
    l3, h3 = Other.moment(mc, WC, list(PC.items()), b); b3, bh3 = Other.moment(mc, WC, [(1, fbc)], b); assert h3 + bh3 / 10 ** 16 < 1
    print('complex deficit', mc * WC - sum(r * z for r, z in PC.items()), 'live', WC)
else:
    b = Q(a.b)
# outer assembly, verbatim from #494's assemble_489.py
eta = beta = Q(1, 10 ** 18); grid = Q(1, 10 ** 18); s = min(c, (1 - beta) * b) - Q(1, 10 ** 24)
assert 0 < s < c and s < (1 - beta) * b
chain = [Q(384599, 10 ** 10)]
def ceil(x): return -((-x.numerator) // x.denominator)
for j in range(6):
    old = chain[-1]; z = (1 - s) * s + s * old
    gap = min(s - z, 1 - z - s, 1 - z - s * (1 - old), 1 - s); assert old < z < s < 1 - z and gap > 0
    cutoff = max(ceil(36 / gap ** 2), ceil(2 * (4 + charged_two) / gap)); assert cutoff * gap ** 2 >= 36 and cutoff * gap >= 2 * (4 + charged_two)
    chain.append(z)
q = chain[-1] * (1 - 2 * eta); margin = (1 - eta) * q / (1 + q); ticks = margin / grid; k = grid * ((ticks.numerator - 1) // ticks.denominator)
bridge = {'semantic': {'C0': {'base': 2, 'exponent': 210000}, 'strict_literal_gap': 1}, 'rows': {'degree_gap': Q(10 ** 6) - Q(51 * 20161, 25)}}
res = Outer.assembly(chain[-1], b, bridge, k, eta=eta, beta=beta)
assert len(res['strict_constraints']) == 47 and all(x > 0 for x in res['strict_constraints'].values())
try: Outer.assembly(chain[-1], b, bridge, k + grid, eta=eta, beta=beta)
except AssertionError: pass
else: raise AssertionError('next kappa grid point accepted')
ref = Q(358867191156973, 250000000000000000)
print(json.dumps(dict(complex_b=str(b), complex_b_decimal=format(float(b), '.18f'), bit_c=str(c),
                      binding='bit' if c < (1 - beta) * b else 'complex', kappa=str(k), kappa_decimal=format(float(k), '.18f'),
                      above_pr494=k > ref, gain_over_pr494_percent=float(100 * (k / ref - 1))), indent=2))
