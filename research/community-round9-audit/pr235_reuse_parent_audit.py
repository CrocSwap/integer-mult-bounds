"""Maintainer PR235 audit: reuse this round's complete, unchanged PR234 replay.

Runs every PR235 arithmetic/certificate check against freshly computed parent
outputs. Does not claim to execute the original PR235 full driver, or rebuild Lean.
"""
from pathlib import Path
import hashlib, importlib.util, json, subprocess, sys
sys.dont_write_bytecode=True
base=Path('/tmp/integer-mult-export235/research/fixed-prime-bootstrap')
parent_root=Path('/tmp/integer-mult-export234')
parent=parent_root/'research/five-stage-source-bound-v8'
banks=Path('/tmp/integer-mult-export237')
fresh=Path('/tmp/integer-mult-pr234-fresh')
spec=importlib.util.spec_from_file_location('pr235_audit_target',base/'verify.py')
mod=importlib.util.module_from_spec(spec);sys.modules[spec.name]=mod;spec.loader.exec_module(mod)
own=mod.inventory(base,'SOURCE.json'); before=mod.inventory(parent,'MANIFEST.json')
pre=json.loads((base/'prerequisite.json').read_text())
for root,expected in [(parent_root,pre['commit']),(banks,pre['banks_commit'])]:
    assert subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip()==expected
assert mod.digest(parent/'MANIFEST.json')==pre['manifest_sha256']
bankpkg=banks/'research/five-stage-banks'
assert {p.relative_to(bankpkg).as_posix():mod.digest(p) for p in bankpkg.rglob('*') if p.is_file()}==pre['banks_files']
receipt=json.loads((fresh/'verification.json').read_text())
assert receipt['status']=='PASS_FRESH_SOURCE_FINITE_CANDIDATE',receipt['status']
expected=json.loads((parent/'expected-math.json').read_text())['mathematics']
computed=json.loads((fresh/'certificate.json').read_text())
assert computed.pop('schema')=='five-stage-v8-reproduced-mathematics/1'
assert computed==expected, 'Fresh parent differs from expected mathematics'
result=mod.arithmetic(parent,fresh,banks);result['prerequisite']=pre
assert result==json.loads((base/'certificate.json').read_text())
assert mod.inventory(base,'SOURCE.json')==own
assert mod.inventory(parent,'MANIFEST.json')==before
assert {p.relative_to(bankpkg).as_posix():mod.digest(p) for p in bankpkg.rglob('*') if p.is_file()}==pre['banks_files']
print(json.dumps(dict(status='PASS_PR235_CHANGED_WORK_WITH_FRESH_PINNED_PARENT',
    kappa=result['kappa'], parent_receipt_sha256=mod.digest(fresh/'verification.json'),
    parent_certificate_sha256=mod.digest(fresh/'certificate.json'),
    parent_replayed_separately=True, full_original_driver_executed=False,
    lean_rebuilt=False, address='Exact prime residues, paid fallback, independent moments, banks, seven finite levels and all 47 constraints; inherited interfaces conditional',
    result=result),indent=2))
