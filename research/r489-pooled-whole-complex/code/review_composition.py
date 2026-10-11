"""Independent fresh-supplier composition gate. OpenAI Codex. Apache-2.0.

Usage: review_composition.py AUDIT_OUT PARENT_CHANGED FRESH_SPLIT_CENTRES
       FRESH_BASE_HOSTED NEW_HOSTED BIT_RESULT REPORT.json

The enclosing verifier must execute both pinned supplier verifiers and the
changed-host owner/controller audits in a newly created output directory.
This script binds their outputs and independently checks finite assembly;
it does not infer all-size realization from finite checks.
"""
from copy import deepcopy
from fractions import Fraction as Q
from pathlib import Path
import gzip
import hashlib
import importlib.util
import json
import math
import sys

if not __debug__:
    raise RuntimeError('assertions must remain enabled')
assert len(sys.argv) == 8, __doc__
audit_dir, changed, split, base_hosted, hosted, bit_path, report_path = map(
    lambda p: Path(p).resolve(), sys.argv[1:])


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def object_sha(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def template_sha(directory):
    return hashlib.sha256(gzip.decompress((directory / 'GLOBAL-TEMPLATE.json.gz').read_bytes())).hexdigest()


owner_path = audit_dir / 'OWNERS-AND-PROFILE.json'
invoice_path = audit_dir / 'PREFIX-AND-INVOICE.json'
assembly_path = audit_dir / 'EXACT-ASSEMBLY.json'
owner, invoice, assembly = map(read, [owner_path, invoice_path, assembly_path])
bit, host, base, integration = map(read, [bit_path, hosted / 'HOSTED.json', base_hosted / 'HOSTED.json', split / 'INTEGRATION.json'])
new_template, base_template, split_template = map(
    lambda d: read(d / 'GLOBAL-TEMPLATE.json.gz'), [hosted, base_hosted, split])
assert owner['status'].startswith('PASS_') and invoice['status'].startswith('PASS_')
assert assembly['status'] == 'PASS_REHOSTED_COMPLEX_AND_FRESH_BIT_EXACT_ASSEMBLY'
assert bit['status'] == 'PASS_ELEVEN_STAGE_WHOLE_HOSTED_BIT_PRICE_AND_CITED_ASSEMBLY'
assert bit['R'] == 489 and bit['bit']['halving_depth'] == 3

# Keep the changed hosting attached to the freshly reconstructed local word.
assert host['template_sha256'] == template_sha(hosted) == assembly['complex_template_sha256']
assert base['template_sha256'] == template_sha(base_hosted)
assert host['parent_template_sha256'] == base['parent_template_sha256'] == integration['global_template_sha256'] == template_sha(split)
preserved_fields = [
    'local_programs', 'm', 'recipe', 'adapter_policy', 'cover',
    'loop_order', 'expanded_scalar_interface',
    'exact_data_phase_recipe_sha256', 'exact_local_clifford_recipe_sha256',
    'residual_adapter_sha256',
]
for field in preserved_fields:
    assert new_template[field] == base_template[field] == split_template[field], field
assert len(new_template['calls']) == len(base_template['calls']) == len(split_template['calls']) == 72
for new_call, base_call, split_call in zip(new_template['calls'], base_template['calls'], split_template['calls']):
    for field in ['orientation', 'stage', 'replica', 'pair', 'window', 'local_program_sha256']:
        assert new_call[field] == base_call[field] == split_call[field], field
    assert new_call['local_program_sha256'] == object_sha(new_template['local_programs'][new_call['orientation']])

# Bind the profile admission, retaining a dynamic width and physical stock.
m, live, physical = new_template['m'], new_template['live'], new_template['physical']
profile = {int(r): count for r, count in owner['paid_profile'].items()}
assert m == 73 and all(type(r) is int and r > 0 and type(n) is int and n > 0 for r, n in profile.items())
assert live == host['live'] == owner['live'] and physical == host['physical'] == owner['physical']
assert profile == {int(r): count for r, count in host['global_profile'].items()}
mass = sum(r * n for r, n in profile.items())
assert mass == owner['rank_mass'] == host['rank_mass'] and m * live - mass == owner['deficit'] == host['deficit'] == 2496
assert max(profile) == host['maxchild'] and owner['hosted_residuals'] == host['hosted_residuals']
assert assembly['owner_audit_sha256'] == sha(owner_path) and assembly['invoice_sha256'] == sha(invoice_path)
assert assembly['bit_result_sha256'] == sha(bit_path) and assembly['bit_template_sha256'] == bit['bit_template_sha256']

# Independently rebuild the stock-sensitive finite invoice. The scalar audit
# separately reconstructs the complete local primitive and wrapper charge.
old_inv = integration['finite_invoice']
pervertex = old_inv['pervertex']
rebased = pervertex - 65 * integration['physical'] + 65 * physical - integration['live'] + live
used = max(pervertex, rebased)
compiler = 64 * (m + 1) ** 3
assert invoice['unhosted_pervertex'] == pervertex
assert invoice['hosted_rebased_pervertex'] == rebased
assert invoice['conservative_pervertex_used'] == used
assert invoice['compiler'] == old_inv['compiler'] == compiler
for field in ['local_adapters', 'local_primitive_bound']:
    assert invoice[field] == old_inv[field], field
group = 2 ** ((m // 2) ** 2) * math.prod(2 ** (2 * i) - 1 for i in range(1, m // 2 + 1))
stock, paid_mass = group * physical, group * mass
logical = group * used + 64
router = compiler * (logical + 1) * (stock + 1) ** 2
G, E, C0 = 1 << 30000, 1 << 100000, 1 << 210000
B = paid_mass + E
literal = 2 * G * stock ** 2 + 8 * paid_mass + 4 * stock + 4 + 32 * m
complex_row = 2 * stock.bit_length() + 9909 + 252
finite = dict(
    physical_stock_bits=stock.bit_length(), router_bits=router.bit_length(),
    literal_bits=literal.bit_length(), physical_row_coefficient=complex_row,
    retained_row_coefficient=20161, required_C0_bits=(32 * m * B * B).bit_length(),
    halving_integer_inequality=[m * m, 2 * max(profile) ** 2],
    G_exponent=30000, E_exponent=100000, C0_exponent=210000,
)
assert invoice['finite'] == finite
strict = dict(
    local_primitive_bound=invoice['local_primitive_bound'] < 1 << 48,
    logical=logical < 1 << 6050, router=router < G, literal=literal < E,
    mass=B < 1 << 100001, precision=32 * m * B * B < C0,
    tape=2 * B + 18 < C0, row=complex_row < 20161,
    halving=m * m > 2 * max(profile) ** 2,
)
assert all(strict.values()) and invoice['strict_checks'] == strict


def load_engine(name):
    path = changed / 'work/pr361/code/engines' / (name + '.py')
    spec = importlib.util.spec_from_file_location('composition_review_' + name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


M, Other, Outer = map(load_engine, ['moment', 'base_two_moment', 'outer'])
b = Q(assembly['complex_lower'])
step = Q(1, 10 ** 24)
assert b > 0 and (b / step).denominator == 1
assert Q(assembly['complex_decimal']) == b and Q(assembly['next_b_rejected']) == b + step
fallback = 32 * m * m * sum(profile.values())
moments = []
for endpoint, accept in [(b, True), (b + step, False)]:
    ml, mh = M.moment(profile, m, live, endpoint, True)
    bl, bh = Other.moment(m, live, list(profile.items()), endpoint)
    fl, fh = Other.moment(m, live, [(1, fallback)], endpoint)
    bl, bh = bl + fl / 10 ** 16, bh + fh / 10 ** 16
    assert (mh < 1 and bh < 1) if accept else (ml > 1 and bl > 1)
    moments.append(dict(endpoint=str(endpoint), mercator=[str(ml - 1), str(mh - 1)], base_two=[str(bl - 1), str(bh - 1)], accept=accept))
assert assembly['exact_moment_receipts'] == moments

# The historical two-level field is deliberately absent: use fresh depth-three
# invoice fields directly, even though the complex supplier binds numerically.
c = Q(bit['bit_lower'])
charge = bit['bit']['charged_three_level_coefficient_bits']
row = max(20161, bit['bit']['row_coefficient'], complex_row)
assert charge == 6464 and bit['bit']['row_coefficient'] == 19431


def check_bit_binding(candidate):
    assert Q(candidate['bit_lower']) == c
    assert candidate['bit_charged_three_level_coefficient_bits'] == charge
    assert candidate['bit_prefix_bits'] == bit['bit']['charged_prefix_bits']
    assert candidate['external_row_allowance'] == row


check_bit_binding(assembly)
binding_controls = []
for field, value in [
    ('bit_charged_three_level_coefficient_bits', bit['bit']['charged_prefix_bits']),
    ('bit_charged_three_level_coefficient_bits', charge - 64),
    ('external_row_allowance', row - 1),
    ('bit_lower', str(c + step)),
]:
    bad = deepcopy(assembly)
    bad[field] = value
    try:
        check_bit_binding(bad)
    except AssertionError:
        binding_controls.append(dict(field=field, rejected_value=value))
    else:
        raise AssertionError('binding mutation accepted: ' + field)

eta = beta = grid = Q(1, 10 ** 18)
saving = min(c, (1 - beta) * b) - step
assert 0 < saving < c and saving < (1 - beta) * b
chain, cutoffs = [Q(384599, 10 ** 10)], []
for _ in range(6):
    old = chain[-1]
    new = (1 - saving) * saving + saving * old
    gap = min(saving - new, 1 - new - saving, 1 - new - saving * (1 - old), 1 - saving)
    assert old < new < saving < 1 - new and gap > 0
    cutoff = max(math.ceil(36 / gap ** 2), math.ceil(2 * (4 + charge) / gap))
    assert cutoff * gap ** 2 >= 36 and cutoff * gap >= 2 * (4 + charge)
    cutoffs.append(dict(gap=str(gap), cutoff_log2=str(cutoff)))
    chain.append(new)
q = chain[-1] * (1 - 2 * eta)
ticks = ((1 - eta) * q / (1 + q)) / grid
kappa = grid * ((ticks.numerator - 1) // ticks.denominator)
assert assembly['kappa'] == str(kappa) and assembly['bootstrap'] == cutoffs
assert assembly['binding_component'] == ('bit' if c < (1 - beta) * b else 'complex')
bridge = {'semantic': {'C0': {'base': 2, 'exponent': 210000}, 'strict_literal_gap': 1}, 'rows': {'degree_gap': Q(10 ** 6) - Q(51 * row, 25)}}
outer = Outer.assembly(chain[-1], b, bridge, kappa, eta=eta, beta=beta)
slacks = outer['strict_constraints']
assert len(slacks) == 47 and all(value > 0 for value in slacks.values())
assert assembly['strict_outer_constraints'] == {name: str(value) for name, value in slacks.items()}
controls = []
for name, k, e, be in [
    ('next_grid', kappa + grid, eta, beta), ('zero_eta', kappa, Q(0), beta),
    ('zero_beta', kappa, eta, Q(0)), ('unit_beta', kappa, eta, Q(1)),
]:
    try:
        Outer.assembly(chain[-1], b, bridge, k, eta=e, beta=be)
    except AssertionError:
        controls.append(name)
    else:
        raise AssertionError(name)
assert assembly['outer_controls'] == controls

report = dict(
    status='PASS_INDEPENDENT_FRESH_SUPPLIER_COMPOSITION_GATE',
    bit_result_sha256=sha(bit_path), assembly_sha256=sha(assembly_path),
    owner_audit_sha256=sha(owner_path), invoice_sha256=sha(invoice_path),
    fresh_complex_integration_sha256=sha(split / 'INTEGRATION.json'),
    fresh_base_template_sha256=base['template_sha256'],
    changed_template_sha256=host['template_sha256'],
    preserved_local_program_sha256=object_sha(new_template['local_programs']),
    preserved_fields=preserved_fields, live=live, physical=physical,
    profile=profile, rank_mass=mass, finite=finite,
    bit_lower=str(c), complex_lower=str(b), kappa=str(kappa),
    bit_charged_three_level_coefficient_bits=charge,
    bit_row_coefficient=bit['bit']['row_coefficient'], external_row_allowance=row,
    strict_outer_constraints=47, outer_controls=controls,
    binding_mutations_rejected=binding_controls,
    scope='Arithmetic and fresh-output binding gate. Enclosing fresh root execution must bind both complete pinned supplier replays, physical owner/controller admission, scalar invoice and compiler provenance. Inherited Lemma A spectator borrowing, all-size compiler/common-label/restored-row/precision/tape and analytic-transfer contracts remain conditional.',
)
report_path.write_text(json.dumps(report, indent=2) + '\n')
print(report['status'], 'live', live, 'kappa', str(kappa), flush=True)
