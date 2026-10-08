"""Build and audit the 37-declaration standalone current-record math package."""
from pathlib import Path
from fractions import Fraction as Q
import argparse, hashlib, json, os, re, subprocess, time

HERE = Path(__file__).resolve().parent
ap = argparse.ArgumentParser()
ap.add_argument('--lean', default=r'C:\Users\Propietario\.elan\toolchains\leanprover--lean4---v4.31.0\bin\lean.exe')
args = ap.parse_args()
modules = [('DirtyComplementSafety','DirtyComplementSafety'),
    ('FreshKernelReclaim','FreshKernelReclaim'),
    ('FiniteRationalChecks','FrontierRationalCertificate'),
    ('CircuitToggleSafety','CircuitToggleSafety'),
    ('CurrentRecordCertificate','CurrentRecordCertificate')]
names = []; inventory = []
for module, namespace in modules:
    source = HERE/f'{module}.lean'; text = source.read_text(encoding='utf-8')
    assert not re.search(r'\b(?:sorry|admit|native_decide)\b|^axiom\s',text,re.M)
    theorems = re.findall(r'^theorem\s+(\w+)',text,re.M)
    names.extend(f'{namespace}.{name}' for name in theorems)
    inventory.append(dict(module=module,namespace=namespace,theorems=len(theorems),
        source_sha256=hashlib.sha256(source.read_bytes()).hexdigest()))
assert len(names)==37
(HERE/'Audit.lean').write_text(''.join(f'import {m}\n' for m,_ in modules)+'\n'+
    ''.join(f'#print axioms {name}\n' for name in names),encoding='utf-8')
(HERE/'lean-toolchain').write_text('leanprover/lean4:v4.31.0\n',encoding='utf-8')
(HERE/'lakefile.lean').write_text('''import Lake
open Lake DSL
package currentRecordMath
lean_lib CurrentRecordMath where
  roots := #[`DirtyComplementSafety, `FreshKernelReclaim, `FiniteRationalChecks,
    `CircuitToggleSafety, `CurrentRecordCertificate, `Audit]
''',encoding='utf-8')
(HERE/'verify.ps1').write_text('''param([string]$LeanExecutable = "lean")
$ErrorActionPreference = "Stop"
$taskMathRoot = $PSScriptRoot
$env:LEAN_PATH = $taskMathRoot
foreach ($taskModule in @("DirtyComplementSafety", "FreshKernelReclaim", "FiniteRationalChecks", "CircuitToggleSafety", "CurrentRecordCertificate", "Audit")) {
  & $LeanExecutable -o (Join-Path $taskMathRoot ($taskModule + ".olean")) (Join-Path $taskMathRoot ($taskModule + ".lean"))
  if ($LASTEXITCODE -ne 0) { throw "Lean compilation failed: $taskModule" }
}
''',encoding='utf-8')
env = dict(os.environ,LEAN_PATH=str(HERE)); builds = []; permitted={'propext','Classical.choice','Quot.sound'}
for module in [m for m,_ in modules]+['Audit']:
    started=time.monotonic()
    result=subprocess.run([args.lean,'-o',str(HERE/f'{module}.olean'),str(HERE/f'{module}.lean')],
        capture_output=True,text=True,env=env)
    log=result.stdout+result.stderr
    (HERE/f'{module}-compile.log').write_text(log,encoding='utf-8')
    assert result.returncode==0,log
    for axiom_list in re.findall(r'depends on axioms: \[([^]]*)\]',log):
        assert set(a.strip()for a in axiom_list.split(',')if a.strip()) <= permitted
    builds.append(dict(module=module,returncode=result.returncode,elapsed_seconds=round(time.monotonic()-started,3)))
audit=(HERE/'Audit-compile.log').read_text(encoding='utf-8')
assert all(f"'{name}'" in audit for name in names)
d=json.loads((HERE/'weighted-input.json').read_text(encoding='utf-8'))
case=(HERE/'CurrentRecordCertificate.lean').read_text(encoding='utf-8')
pub=re.search(r'def oldPublished : Rat := Rat.divInt \((\d+)\) \((\d+)\)',case)
scope=re.search(r'def oldScoped : Rat := Rat.divInt \((\d+)\) \((\d+)\)',case)
old_public=str(Q(int(pub[1]),int(pub[2]))); old_scope=str(Q(int(scope[1]),int(scope[2])))
package_files=[f'{m}.lean'for m,_ in modules]+['Audit.lean','lean-toolchain','lakefile.lean',
    'verify.ps1','verify_record_math.py','generate_taylor_case.py','weighted-input.json']
receipt=dict(status='PASS complete serial Lean kernel build and all-theorem axiom audit',
    compiler=subprocess.check_output([args.lean,'--version'],text=True).strip(),
    source_commit=d['source_commit'],kappa=d['kappa'],bit_saving=d['bit_saving'],
    prior_published_checked=old_public,prior_scoped_checked=old_scope,
    publication_comparison='PR73 headline and the stronger pinned PR71 scoped limit',
    total_audited_theorems=len(names),reused_theorems=22,new_universal_theorems=4,
    new_concrete_theorems=11,inventory=inventory,builds=builds,
    permitted_axioms=sorted(permitted),proof_escapes=False,
    source_certificate_sha256=d['source_certificate_sha256'],
    candidate_certificate_sha256=d['refined_certificate_sha256'],
    package_files={name:hashlib.sha256((HERE/name).read_bytes()).hexdigest()for name in package_files},
    excluded_baseline_test_cases=True,
    scope='Exact Boolean circuit-toggle/dirty identities and finite Taylor/rounding/moment/47-slack arithmetic. '
      'Analytic log/exp, source-profile binding, assembly formula completeness and global physical/tape multiplication transfer remain explicit contracts.')
(HERE/'record-lean-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(status=receipt['status'],theorems=len(names),receipt=str(HERE/'record-lean-receipt.json'),
    kappa=d['kappa'],prior_published=old_public,prior_scoped=old_scope,builds=builds),indent=2))
