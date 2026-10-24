"""Run the submitted replay and isolated controls for the rank proof review."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
PACKAGE = (Path(sys.argv[1]).resolve() if len(sys.argv) == 2 else
           HERE.parents[1] / 'early-remainder-audit/packages/boolean-disjointness-repair')


def run(path, optimize=None):
    env = dict(os.environ)
    env.pop('PYTHONOPTIMIZE', None)
    if optimize is not None:
        env['PYTHONOPTIMIZE'] = str(optimize)
    result = subprocess.run([sys.executable, '-B', str(path / 'verify.py')],
                            cwd=path, env=env, capture_output=True, text=True,
                            timeout=120)
    return dict(returncode=result.returncode, stdout=result.stdout,
                stderr=result.stderr)


def change(path, name, old, new, repin):
    source = path / name
    text = source.read_text()
    if text.count(old) != 1:
        raise ValueError('Control needs one matching source string: ' + name)
    source.write_text(text.replace(old, new))
    if repin:
        manifest = path / 'SOURCE-HASHES.json'
        hashes = json.loads(manifest.read_text())
        hashes[name] = hashlib.sha256(source.read_bytes()).hexdigest()
        manifest.write_text(json.dumps(hashes, indent=2) + '\n')


results = {'baseline': run(PACKAGE),
           'baseline_with_pythonoptimize_1': run(PACKAGE, optimize=1),
           'negative_controls': []}
if results['baseline']['returncode'] != 0:
    raise ValueError('Submitted replay failed')
if results['baseline_with_pythonoptimize_1']['returncode'] != 0:
    raise ValueError('Submitted replay failed with PYTHONOPTIMIZE=1')

controls = [
    ('proof_hash', 'PROOF.txt', 'Let h >= 2.', 'Let h >= 1.', False,
     'Source hash mismatch: PROOF.txt'),
    ('wrong_rank_formula', 'check_zeta_corrector.py',
     'formula = (2**(h+1)-2*(-1)**h-3)//3',
     'formula = (2**(h+1)-2*(-1)**h-6)//3', True, 'AssertionError'),
    ('wrong_full_kernel_factor', 'independent/verify.py',
     'len(m_kernel) == 2 * len(b_kernel)',
     'len(m_kernel) == 3 * len(b_kernel)', True, 'AssertionError'),
    ('wrong_preimage_parity', 'independent/verify.py',
     'preimages and all(x.bit_count() % 2 == 1 for x in preimages)',
     'preimages and all(x.bit_count() % 2 == 0 for x in preimages)',
     True, 'AssertionError'),
    ('receipt_mismatch', 'ZETA-CORRECTOR-CHECK.json',
     '"correction_rank": 1,', '"correction_rank": 0,', True,
     'Receipt mismatch: ZETA-CORRECTOR-CHECK.json'),
]
for label, name, old, new, repin, expected in controls:
    with tempfile.TemporaryDirectory(prefix='boolean-repair-review-') as temp:
        copy = Path(temp) / 'package'
        shutil.copytree(PACKAGE, copy)
        change(copy, name, old, new, repin)
        result = run(copy, optimize=1)
        if result['returncode'] == 0 or expected not in result['stderr']:
            raise ValueError('Control was not rejected at its intended check: ' + label)
        results['negative_controls'].append(dict(name=label, repinned=repin,
                                                pythonoptimize='1',
                                                expected_error=expected, **result))

# Construct disjointness by set membership, rather than bit-mask intersection.
# The full matrix must be one rank larger than the proper matrix. For h=1,
# the proper matrix is empty and the stated formula would be false.
def matrix(h, proper):
    masks = range(1, 2**h - 1) if proper else range(2**h)
    subsets = [{j for j in range(h) if (u >> j) & 1} for u in masks]
    return [[int(i == j) ^ int(s.isdisjoint(t))
             for j, t in enumerate(subsets)] for i, s in enumerate(subsets)]


def rank(a):
    a = [row[:] for row in a]
    r = 0
    for c in range(len(a)):
        pivot = next((i for i in range(r, len(a)) if a[i][c]), None)
        if pivot is None:
            continue
        a[r], a[pivot] = a[pivot], a[r]
        for i in range(r + 1, len(a)):
            if a[i][c]:
                a[i] = [x ^ y for x, y in zip(a[i], a[r])]
        r += 1
    return r


results['independent_set_matrix_rows'] = []
for h in range(2, 8):
    b_rank = rank(matrix(h, True))
    m_rank = rank(matrix(h, False))
    expected = (2**(h + 1) - 2 * (-1)**h - 3) // 3
    if b_rank != expected or m_rank != b_rank + 1:
        raise ValueError('Independent set matrix check failed')
    results['independent_set_matrix_rows'].append(dict(h=h, rank_b=b_rank,
                                                     rank_m=m_rank))
results['excluded_boundary_h1'] = dict(rank_b=rank(matrix(1, True)),
                                     invalid_formula_value=(2**2 + 2 - 3)//3)
if results['excluded_boundary_h1'] != {'rank_b': 0, 'invalid_formula_value': 1}:
    raise ValueError('The h=1 scope check failed')
results['checked_file_sha256'] = {
    str(p.relative_to(PACKAGE)): hashlib.sha256(p.read_bytes()).hexdigest()
    for p in sorted(PACKAGE.rglob('*')) if p.is_file()
}
results['python'] = sys.version
results['status'] = 'PASS_INDEPENDENT_BOOLEAN_REPAIR_REVIEW_CHECKS'
(HERE / 'RESULT.json').write_text(json.dumps(results, indent=2) + '\n')
print(results['status'])
print('baseline=PASS pythonoptimize_1=PASS negative_controls=5 independent_set_matrices=h2..7')
print('h1_excluded=CONFIRMED all_h_claim=WRITTEN_PROOF_ONLY no_new_kappa')
