#!/usr/bin/env python3
"""Repin four malformed public summaries and require semantic rejection.

These controls exercise recorded-summary coherence only, not any fresh scientific
replay. Originals and their historical original-hash declarations are untouched.
"""
from pathlib import Path
import hashlib
import importlib.util
import json
import shutil
import tempfile

H = Path(__file__).resolve().parent

def read(path):
    return json.loads(path.read_text())

def write(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def edit(root, name, transform):
    path = root / name
    value = read(path)
    transform(value)
    write(path, value)
    provenance = read(root / 'PUBLIC-PROVENANCE.json')
    if name in provenance['files']:
        # Deliberately preserve the asserted original hash. Public normalization
        # metadata can be forged; exact gate contents must still be checked.
        provenance['files'][name]['public_sha256'] = sha(path)
        provenance['files'][name]['normalization'] = 'workspace-prefix-to-token'
        write(root / 'PUBLIC-PROVENANCE.json', provenance)

def repin(root):
    pins = read(root / 'PUBLIC-PINS.json')
    pins['sha256'] = {name: sha(root / name) for name in pins['sha256']}
    write(root / 'PUBLIC-PINS.json', pins)

def check_controls():
    spec = importlib.util.spec_from_file_location('recorded_summary', H / 'check_recorded_summary.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.check(H)
    cases = [
        ('missing-fresh-stages', 'exact two fresh native stages', [
            ('evidence/NATIVE-RESULT.json', lambda x: x.__setitem__('stages', [])),
            ('evidence/NATIVE-STAGES.json', lambda x: x.clear()),
        ]),
        ('missing-provider-set', 'exact current invoice providers', [
            ('evidence/PREFIX-AND-INVOICE.json', lambda x: x.__setitem__('providers', {})),
        ]),
        ('empty-invoice-predicates', 'complete finite invoice gate set', [
            ('evidence/PREFIX-AND-INVOICE.json', lambda x: x.__setitem__('strict_checks', {})),
        ]),
        ('changed-certified-endpoint', 'exact certified endpoint', [
            ('evidence/ADMISSION-RESULT.json', lambda x: x.__setitem__('kappa', '1/500')),
        ]),
    ]
    results = []
    with tempfile.TemporaryDirectory(prefix='retiming-summary-controls-') as scratch:
        for name, expected, changes in cases:
            root = Path(scratch) / name
            shutil.copytree(H, root)
            for path, transform in changes:
                edit(root, path, transform)
            repin(root)
            try:
                module.check(root)
            except ValueError as error:
                if str(error) != expected:
                    raise RuntimeError(f'{name}: unexpected rejection: {error}') from error
                results.append({'name': name, 'rejected_at': str(error)})
            else:
                raise RuntimeError(f'{name}: malformed summary was accepted')
    return {'status': 'PASS_PUBLIC_SUMMARY_SEMANTIC_CONTROLS', 'controls': results,
            'scope': 'Four repinned malformed normalized summaries rejected at content predicates; no fresh scientific replay.'}

if __name__ == '__main__':
    print(json.dumps(check_controls(), indent=2, sort_keys=True))
