"""Serial Lean build and complete theorem/axiom receipt for frozen-62 research."""
from pathlib import Path
import argparse, hashlib, json, os, re, subprocess, time

HERE = Path(__file__).resolve().parent
ap = argparse.ArgumentParser()
ap.add_argument('--lean', default=r'C:\Users\Propietario\.elan\toolchains\leanprover--lean4---v4.31.0\bin\lean.exe')
args = ap.parse_args()
modules = [
    ('DirtyComplementSafety', 'DirtyComplementSafety'),
    ('FreshKernelReclaim', 'FreshKernelReclaim'),
    ('CoordinateConjugacy', 'CoordinateConjugacy'),
    ('FiniteRationalChecks', 'FrontierRationalCertificate'),
    ('RankFlowPrice', 'RankFlowPrice'),
    ('ProfileSearchCertificate', 'RefinedFrontierCertificate'),
]
names = []
inventory = []
for module, namespace in modules:
    source = HERE/f'{module}.lean'
    text = source.read_text(encoding='utf-8')
    if re.search(r'\b(?:sorry|admit|native_decide)\b', text):
        raise ValueError(f'Forbidden proof escape in {source.name}')
    theorems = re.findall(r'^theorem\s+(\w+)', text, flags=re.M)
    names.extend(f'{namespace}.{name}' for name in theorems)
    inventory.append(dict(module=module, namespace=namespace, theorem_count=len(theorems),
        source_sha256=hashlib.sha256(source.read_bytes()).hexdigest()))
audit = ''.join(f'import {module}\n' for module, _ in modules)
audit += '\n/- Every theorem in this packet is included in the kernel axiom audit. -/\n'
audit += ''.join(f'#print axioms {name}\n' for name in names)
(HERE/'Audit.lean').write_text(audit, encoding='utf-8')
(HERE/'lean-toolchain').write_text('leanprover/lean4:v4.31.0\n', encoding='utf-8')
(HERE/'lakefile.lean').write_text('''import Lake
open Lake DSL
package frozen62Research
lean_lib Frozen62Research where
  roots := #[`DirtyComplementSafety, `FreshKernelReclaim, `CoordinateConjugacy,
    `FiniteRationalChecks, `RankFlowPrice, `ProfileSearchCertificate, `Audit]
''', encoding='utf-8')
(HERE/'verify.ps1').write_text('''param([string]$LeanExecutable = "lean")
$ErrorActionPreference = "Stop"
$taskMathRoot = $PSScriptRoot
$env:LEAN_PATH = $taskMathRoot
$taskModules = @("DirtyComplementSafety", "FreshKernelReclaim", "CoordinateConjugacy", "FiniteRationalChecks", "RankFlowPrice", "ProfileSearchCertificate", "Audit")
foreach ($taskModule in $taskModules) {
  & $LeanExecutable -o (Join-Path $taskMathRoot ($taskModule + ".olean")) (Join-Path $taskMathRoot ($taskModule + ".lean"))
  if ($LASTEXITCODE -ne 0) { throw "Lean compilation failed: $taskModule" }
}
''', encoding='utf-8')
env = dict(os.environ, LEAN_PATH=str(HERE))
builds = []
for module in [m for m, _ in modules]+['Audit']:
    started = time.monotonic()
    result = subprocess.run([args.lean, '-o', str(HERE/f'{module}.olean'),
        str(HERE/f'{module}.lean')], env=env, capture_output=True, text=True)
    (HERE/f'{module}-compile.log').write_text(result.stdout+result.stderr, encoding='utf-8')
    assert result.returncode == 0, result.stdout+result.stderr
    assert 'sorryAx' not in result.stdout+result.stderr
    builds.append(dict(module=module, returncode=result.returncode,
        elapsed_seconds=round(time.monotonic()-started,3)))
data = json.loads((HERE/'weighted-input.json').read_text(encoding='utf-8'))
lower = json.loads((HERE/'old-profile-lower-data.json').read_text(encoding='utf-8'))
version = subprocess.run([args.lean,'--version'],capture_output=True,text=True,check=True).stdout.strip()
receipt = dict(status='PASS serial Lean kernel compilation and all-theorem axiom audit',
    compiler=version, compiler_executable=args.lean, source_commit=data['source_commit'],
    kappa=data['kappa'], bit_saving=data['bit_saving'],
    frozen_old_scoped=data['comparison']['old_formal_scoped_limit'],
    frozen_old_published=data['comparison']['old_published_kappa'],
    fresh_universal_theorems=34, concrete_instance_theorems=15,
    reused_helper_theorems=4, total_audited_theorems=len(names),
    namespaces=[n for _,n in modules], inventory=inventory, builds=builds,
    permitted_axioms=['propext','Classical.choice','Quot.sound'],
    proof_escapes={'sorry':False,'admit':False,'native_decide':False,'new_axioms':False},
    weighted_input_sha256=hashlib.sha256((HERE/'weighted-input.json').read_bytes()).hexdigest(),
    old_profile_lower_data_sha256=hashlib.sha256((HERE/'old-profile-lower-data.json').read_bytes()).hexdigest(),
    old_rounded_lower_strict_gap=lower['lower_strict_gap'],
    auxiliary_files={name:hashlib.sha256((HERE/name).read_bytes()).hexdigest() for name in
        ['Audit.lean','generate_profile_case.py','verify_math.py','verify.ps1','lakefile.lean','lean-toolchain']},
    scope='Finite Boolean encoder/reclaim/conjugacy identities and exact rational moment/assembly gates. '
        'Source-profile binding, analytic log/exp enclosure, physical frame/tape/routing contracts and '
        'global integer multiplication theorem remain explicit external contracts.')
(HERE/'lean-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(status=receipt['status'], audited_theorems=len(names),
    receipt=str(HERE/'lean-receipt.json'), kappa=data['kappa'], builds=builds),indent=2))
