from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
import packet325 as contract
contract.require_assertions()
contract.verify_inputs()
contract.verify_frame_binding()
contract.verify_bank()
"""Bind the independently checked finite PR325 components and scope."""
from pathlib import Path
from fractions import Fraction
import hashlib, json

if not __debug__:
    raise RuntimeError('Assertions must be enabled')
HERE = contract.AUDIT
SOURCE = contract.SOURCE
LOCAL = contract.FRAME
BANK = contract.BANK
GLOBAL = contract.GLOBAL
HEAD = '0eca9340a3df6141b8e71a41638c3937b3522888'
def read(path): return json.loads(Path(path).read_text())
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def bind(receipt, key, path): assert receipt[key] == sha(path), (key, str(path))
def verify_manifest(folder, flat=False):
    manifest = read(folder/'MANIFEST.json')
    if flat:
        entries = manifest.items()
    else:
        assert manifest['head'] == HEAD
        files = manifest['files']
        entries = files.items() if isinstance(files, dict) else ((x['path'],x['sha256']) for x in files)
    for name, expected in entries:
        assert sha(folder/name) == expected, (str(folder), name)
for folder in (SOURCE, LOCAL, BANK): verify_manifest(folder)
verify_manifest(GLOBAL, True)
checks = {
    'GEOMETRY-RESULT.json': 'check_geometry.py',
    'EVENT-AUDIT.json': 'check_events.py',
    'FULL-FRAME-AUDIT.json': 'check_full_frames.py',
    'BANK-PRICE-AUDIT.json': 'check_bank_price.py',
    'GLOBAL-AUDIT.json': 'check_global.py',
    'GLOBAL-CHART-BOUNDS.json': 'check_chart_units.py',
}
receipts = {name: read(HERE/name) for name in checks}
controls = read(HERE/'ASSERTION-CONTROLS.json')
assert controls['status'].startswith('PASS') and set(controls['controls']) == set(checks.values())
for name, checker in checks.items():
    receipt = receipts[name]
    assert receipt['status'].startswith('PASS')
    bind(receipt, 'checker_sha256', contract.HERE/'audit'/checker)
    bind(controls['controls'][checker], 'checker_sha256', contract.HERE/'audit'/checker)
    assert controls['controls'][checker]['return_code'] != 0
geometry, events, frames, banks, global_ir, units = (receipts[name] for name in checks)
assert geometry['source_head'] == events['head'] == HEAD
bind(geometry, 'source_manifest_sha256', SOURCE/'SOURCES.json')
bind(geometry, 'word_sha256', SOURCE/'inputs/bitword__selected__bit__word_p10.json.gz')
for name, expected in events['inputs'].items(): assert sha(SOURCE/name) == expected
for key, file in [('source_result_sha256',SOURCE/'RESULT.json'),
                  ('full_frame_result_sha256',LOCAL/'RESULT.json'),
                  ('full_frame_validation_sha256',LOCAL/'VALIDATION.json'),
                  ('proof_sha256',HERE/'FRAME-CONTRACT.md')]: bind(frames,key,file)
for name, expected in frames['pinned_theorems'].items():
    assert sha(HERE/'inert'/name.replace('/','__')) == expected
for key, file in [('bank_result_sha256',BANK/'BANK-RESULT.json'),
                  ('price_result_sha256',BANK/'PRICE-RESULT.json'),
                  ('local_frame_result_sha256',LOCAL/'RESULT.json')]: bind(banks,key,file)
for key, file in [('global_result_sha256',GLOBAL/'RESULT.json'),
                  ('global_manifest_sha256',GLOBAL/'MANIFEST.json'),
                  ('local_result_sha256',LOCAL/'RESULT.json'),
                  ('copy_override_sha256',GLOBAL/'copied-work-projector-overrides.json')]: bind(global_ir,key,file)
bind(units, 'normalizer_sha256',GLOBAL/'normalizers.json.gz')
assert geometry['pairs'] == events['changed_setup_frames'] == 480
assert frames['all_records_reconstructed'] == global_ir['all_local_records'] == 398660
assert global_ir['all_global_stage_records'] == 119604000
assert global_ir['global_paid_calls'] == banks['calls'] == 14514000
assert global_ir['global_rank_mass'] == banks['rank_mass'] == 65757600
assert global_ir['max_rank'] == banks['max_rank'] == 42
assert global_ir['completion_children'] == banks['completion_children'] == 0
assert banks['stock'] == 658800 and banks['selector_calls'] == 170009279400
assert banks['finite_coefficient'] == 24857617667871401
assert banks['all47exact_slacks_reproduced'] and banks['adjacent_kappa_rejected']
assert Fraction(banks['kappa']) == Fraction(770612425424136,10**18)
assert frames['arbitrary_dirty_operator_retained_by_common_array_frame_identity']
assert frames['address_geometry_distinguished_from_F2_payload_values']
source_bindings = {
    'source_manifest': sha(SOURCE/'MANIFEST.json'),
    'local_manifest': sha(LOCAL/'MANIFEST.json'),
    'local_arbitrary_dirty_binding': sha(LOCAL/'ARBITRARY-DIRTY-AUDIT-BINDING.json'),
    'bank_manifest': sha(BANK/'MANIFEST.json'),
    'global_manifest': sha(GLOBAL/'MANIFEST.json'),
    'global_result': sha(GLOBAL/'RESULT.json'),
}
result = {
    'status': 'PASS_INDEPENDENT_FINITE_PR325_480_RETIMING_COMPOSITION',
    'head': HEAD,
    'checker_sha256': sha(__file__),
    'documentation_sha256': {n:sha(HERE/n) for n in ('AUDIT.md','FRAME-CONTRACT.md')},
    'receipt_sha256': {n:sha(HERE/n) for n in [*checks,'ASSERTION-CONTROLS.json']},
    'source_bindings_sha256': source_bindings,
    'global_program_sha256': global_ir['program_binding'],
    'retimings': 480,
    'full_local_records': 398660,
    'mapped_global_records': 119604000,
    'literal_stock': 658800,
    'literal_children': 14514000,
    'literal_rank_mass': 65757600,
    'maximum_rank': 42,
    'completion_children': 0,
    'selector_calls': 170009279400,
    'finite_coefficient': 24857617667871401,
    'kappa': '770612425424136/1000000000000000000',
    'kappa_decimal': '0.000770612425424136',
    'all_47_strict_assembly_checks': True,
    'finite_gate_closed': True,
    'theorem_contract': 'Pinned 03-motifs common F2 array-frame lifting, exact nested address projectors and complete COPY contract, instantiated on every actual finite gate/edge.',
    'retained_conditions': ['production primitive/compiler implementation', 'uniform eligible-prime interfaces beyond the checked new endpoint charts', 'weighted routing/compiler interfaces', 'restored-row and ordinary-leaf interfaces', 'complex/full-C interface', 'analytic all-size theorem'],
    'scope': 'Exact finite construction, arbitrary-dirty array-frame composition, emitted global IR, bank invoice and rational price. This is not an unconditional all-size theorem or an optimality claim.'
}
(HERE/'FINAL-AUDIT.json').write_text(json.dumps(contract.portable(result),indent=2)+'\n')
files = [*checks, *checks.values(), 'ASSERTION-CONTROLS.json','AUDIT.md','FRAME-CONTRACT.md','FINAL-AUDIT.json','finalize_audit.py']
files += [str(p.relative_to(HERE)) for p in sorted((HERE/'inert').iterdir()) if p.is_file()]
manifest = {'status':'FROZEN_INDEPENDENT_FINITE_PR325_AUDIT','head':HEAD,'code_root':'$PACKAGE/audit','files':{n:sha((contract.HERE/'audit'/n)if n.endswith('.py')else HERE/n) for n in sorted(set(files))}}
(HERE/'MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'status':result['status'],'final_audit_sha256':sha(HERE/'FINAL-AUDIT.json'),'manifest_sha256':sha(HERE/'MANIFEST.json')},indent=2))
