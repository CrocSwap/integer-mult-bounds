#!/usr/bin/env python3
"""Portable evidence and finite-support replay; the theorem remains written proof."""
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent

def need(ok, message):
    if not ok:
        raise ValueError(message)

def encoded(value):
    return (json.dumps(value, indent=2, sort_keys=True) + '\n').encode()

def authenticate():
    manifest = json.loads((ROOT / 'EVIDENCE.json').read_text())
    actual = {str(p.relative_to(ROOT)) for p in (ROOT / 'evidence').rglob('*') if p.is_file()}
    need(actual == set(manifest['files']), 'evidence file inventory changed')
    for name, digest in manifest['files'].items():
        path = ROOT / name
        need(not path.is_symlink() and sha256(path.read_bytes()).hexdigest() == digest,
             'immutable evidence mismatch: ' + name)
    # The author's original nested manifests remain byte-exact and independently bind their files.
    for directory in ['inventory', 'budget', 'independent-review', 'supplements']:
        base = ROOT / 'evidence' / directory
        original = json.loads((base / 'FILES.json').read_text())
        files = original.get('files', original)
        for name, digest in files.items():
            need(sha256((base / name).read_bytes()).hexdigest() == digest,
                 'original author manifest mismatch: ' + directory + '/' + name)
    need((ROOT / 'evidence/proof/PROOF.md').read_bytes() ==
         (ROOT / 'evidence/independent-review/frozen/REVIEWED-PROOF.md').read_bytes(),
         'reviewed proof differs from the author freeze')
    return manifest

def run():
    manifest = authenticate()
    proof = ROOT / 'evidence/proof'
    # Execute unchanged source checker in this interpreter's optimization mode.
    cmd = [sys.executable, '-I']
    if sys.flags.optimize:
        cmd.append('-O')
    cmd += ['-W', 'error', '-B', str(proof / 'check_source_and_flag.py')]
    source = subprocess.run(cmd, check=True, capture_output=True, timeout=90).stdout
    need(source == (proof / 'SOURCE-FLAG-CHECK.json').read_bytes(),
         'source/flag receipt did not regenerate byte-exactly')
    check = ROOT / 'evidence/budget/check_budget.py'
    spec = importlib.util.spec_from_file_location('frozen_conditional_budget', check)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    # Only private loader paths move. __file__ remains the original unchanged checker,
    # retaining its exact self digest; all scientific functions and JSON fields are unchanged.
    with tempfile.TemporaryDirectory(prefix='released-ceiling-') as temporary:
        temp = Path(temporary)
        stock = temp / 'coded-port-adapter-ceiling-20261023/outputs/released-operator-inventory-20261023'
        shutil.copytree(ROOT / 'evidence/inventory', stock)
        module.HERE = temp / 'outputs/released-operator-optimistic-budget-20261023'
        module.STOCK = stock
        value = module.run()
        budget = encoded(value)
        # Price support for the separate written paid-shear screen, not its theorem.
        need(21 * 2 < module.margin(module.B)[0], 'seven explicit shears fit raw allowance')
        need(24 * module.power(2, module.B)[0] > 45, 'eight explicit shears fail at B')
        need(3 * 112 > module.margin(module.A)[1], '112-shear bill exceeds entire raw allowance')
    for name in ['RESULT.json', 'RESULT-OPTIMIZED.json']:
        need(budget == (ROOT / 'evidence/budget' / name).read_bytes(),
             'full conditional budget receipt differs: ' + name)
    print(json.dumps({
        'status': 'PASS_SCOPED_SUPPORT_AND_CONDITIONAL_ARITHMETIC',
        'immutable_evidence_files': len(manifest['files']),
        'reviewed_proof_sha256': sha256((proof / 'PROOF.md').read_bytes()).hexdigest(),
        'source_flag_receipt_sha256': sha256(source).hexdigest(),
        'budget_receipt_sha256': sha256(budget).hexdigest(),
        'source_flag_controls': 5,
        'separate_paid_screen_proof_sha256': sha256((ROOT / 'evidence/supplements/frozen/PAID-SHEAR-SCREEN.md').read_bytes()).hexdigest(),
        'separate_paid_screen_review_sha256': sha256((ROOT / 'evidence/supplements/PAID-SHEAR-ADDENDUM.md').read_bytes()).hexdigest(),
        'explicit_rank_two_shear_execution_max_raw_count': 7,
        'conditional_invoice_controls': 5,
        'max_uniform_integer_extra_H1': value['max_uniform_integer_extra_H1'],
        'scope': 'Written independently reviewed sufficiently-large-width fixed columnwise Clifford obstruction; finite source/flag support and conditional invoice arithmetic only. No absolute-phase/native/compiler/caller replay, physical FREE classification or kappa.'
    }, indent=2, sort_keys=True))

if __name__ == '__main__':
    run()
