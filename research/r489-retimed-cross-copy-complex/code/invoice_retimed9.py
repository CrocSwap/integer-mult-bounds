"""Fresh finite invoice of the hosted nine-stage template of PR #495's retimed kernel complex word, in the form of PR #433's
complex_integrate.py as extended for entering helpers by PR #484's integrate_gk.py (paid entrance monomials, 144 factors
at entry and exit), with PR #495's wrapper-group charge (two wrappers of eight monomial compiler groups for every helper)
added to the local adapter bill, the hosted live stock (no banks) and physical stock, and a second route charge for every
helper (the second piece of a PR #448 split residual).  Overcharging is deliberate; every inequality is PR #442's.
usage: invoice_retimed9.py HOSTED_DIR LOCAL_DIR PARENT_SPLIT_CENTRES OUT_DIR   (writes OUT_DIR/INTEGRATION.json)"""
import gzip, hashlib, json, math, sys
from pathlib import Path
cd, local, psc, od = map(Path, sys.argv[1:5]); od.mkdir(parents=True)
t = json.loads(gzip.decompress((cd / 'GLOBAL-TEMPLATE.json.gz').read_bytes())); hosted = json.loads((cd / 'HOSTED.json').read_text())
assert hashlib.sha256(gzip.decompress((cd / 'GLOBAL-TEMPLATE.json.gz').read_bytes())).hexdigest() == hosted['template_sha256']
review = json.loads((local / 'LOCAL-REVIEW.json').read_text()); parent = json.loads((psc / 'INTEGRATION.json').read_text())
checks = review['checks']; assert hosted['source_local_checks'] == checks
m, T, L, k, v, R = 73, 8, 9, 4, 120, 560; n = 2 * v + R
W, physical = t['live'], t['physical']; private_centres = hosted['private_centers']
assert (W, physical) == (hosted['live'], hosted['physical']) == (7680, 7680 + R + private_centres + 2)
paid = {int(r): z for r, z in hosted['global_profile'].items()}; mass = sum(r * z for r, z in paid.items()); assert m * W - mass == 2496
compiler = 64 * (m + 1) ** 3
macros = max(z['scalar_macros'] for z in checks.values()); children = sum(checks['forward']['paid_profile'].values())
adapters = 16 * (macros + children + n + private_centres) + 64 * m + 2 * R * 8
local_bound = max(z['real_component_primitive_bound'] for z in checks.values()) + adapters * compiler
bridges = [e for e in t['recipe'] if e['kind'] == 'bridge']; bridge_adds = 2 * v * T * len(bridges)
terminal_shifts = k * v * T; terminal_moves = 2 * k * v * T
widths = hosted['entering_residuals'] // (L * T); assert widths == 79
scalar_primitives = sum(checks[c['orientation']]['real_component_primitive_bound'] for c in t['calls']); assert len(t['calls']) == L * T
idle_items = sum(e['replicas'] for e in t['idle_children'])
nonlocal_items = (4 * v * T * L + 2 * v * T * L + 2 * L * T * R + idle_items + bridge_adds + terminal_shifts + terminal_moves + W + physical
                  + 2 * L * T * widths * 144 + 2 * L * T * R)
outside = 8 * nonlocal_items + 64 * m
pervertex = scalar_primitives + bridge_adds + terminal_shifts + terminal_moves + W + (72 * adapters + outside) * compiler + 64 * physical
r = m // 2; group = 2 ** (r * r) * math.prod(2 ** (2 * i) - 1 for i in range(1, r + 1)); stock = group * physical
smass = group * mass; logical = group * pervertex + 64; router = compiler * (logical + 1) * (stock + 1) ** 2
GG, EE, C0 = 1 << 30000, 1 << 100000, 1 << 210000; BB = smass + EE
literal = 2 * GG * stock ** 2 + 8 * smass + 4 * stock + 4 + 32 * m
maxchild = max(paid); depth = 2; assert m ** depth > 2 * maxchild ** depth
assert local_bound < 1 << 48 and logical < 1 << 6050 and router < GG and literal < EE and BB < 1 << 100001
assert 32 * m * BB * BB < C0 and 2 * BB + 18 < C0
row = depth * stock.bit_length() + 9909 + 252; assert row < 20161
assert pervertex > parent['finite_invoice']['pervertex'], 'the new word is charged at least the parent invoice'
res = dict(status='PASS_RETIMED_KERNEL_HOSTED_FINITE_INVOICE', template_sha256=hosted['template_sha256'], live=W, physical=physical,
           rank_mass=mass, deficit=2496, maxchild=maxchild,
           finite_invoice=dict(local_primitive_bound=local_bound, local_adapters=adapters, scalar_primitives=scalar_primitives,
                               nonlocal_items=nonlocal_items, pervertex=pervertex, physical_stock_bits=stock.bit_length(),
                               router_bits=router.bit_length(), literal_bits=literal.bit_length(), physical_row_coefficient=row,
                               retained_row_coefficient=20161, compiler=compiler, G_exponent=30000, E_exponent=100000, C0_exponent=210000,
                               required_C0_bits=(32 * m * BB * BB).bit_length(), halving_degree=depth,
                               halving_integer_inequality=[m ** depth, 2 * maxchild ** depth]),
           parent_pervertex=parent['finite_invoice']['pervertex'])
(od / 'INTEGRATION.json').write_text(json.dumps(res, indent=2) + '\n')
print(json.dumps({k_: res[k_] for k_ in ('status', 'live', 'physical', 'maxchild')} | {'pervertex_bits': pervertex.bit_length(), 'router_bits': router.bit_length(), 'row': row}))
