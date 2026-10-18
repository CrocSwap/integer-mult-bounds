#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Bounded registered check: package pins, literal owners/controls/exact moment, the Fractions-only cap
certificate, and binding of the stored complete native/admission/release receipts to the exact words,
allocation and claim. It does not rerun the native or integrated outer replay (reproduce.py does).
Structure adapted from Mason Hale's PR2917 run_registered.py. Marius-Paul Dumitrean, with substantial AI
assistance (Claude Code).
"""
import hashlib, json, os, subprocess, sys, tempfile
from fractions import Fraction as Q
from pathlib import Path

P = Path(__file__).resolve().parent
PR2917_HEAD = '224bd5e56041c40078ff6b5fa7393733a215de5c'
DERIVED_SOURCE = '98d57c82a1c7318be3c330c3b66897844d57232f0aaeaea88fb4bebd0a1bedf1'

def read(p):
    return json.loads(p.read_bytes())

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def tree():
    assert not any(f.is_symlink() for f in P.rglob('*'))
    return {f.relative_to(P).as_posix(): sha(f) for f in P.rglob('*') if f.is_file() and f != P / 'MANIFEST.json'}

def main():
    if not __debug__:
        raise SystemExit('refusing python -O: this check relies on assertions')
    pins = read(P / 'MANIFEST.json')
    assert tree() == pins, 'complete package inventory'
    with tempfile.TemporaryDirectory(prefix='cap-fill-replay-') as tmp:
        out = Path(tmp)
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1')
        for key in ('PYTHONOPTIMIZE', 'PYTHONPATH', 'WITNESS_SPEC', 'WITNESS_RECORD', 'WITNESS_DISCOVER'):
            env.pop(key, None)
        log = out / 'owners.log'
        with log.open('w') as stream:
            r = subprocess.run([sys.executable, '-B', str(P / 'check_allocation.py'), '--work', str(out / 'owners')],
                               env=env, stdin=subprocess.DEVNULL, stdout=stream, stderr=subprocess.STDOUT)
        if r.returncode:
            print(log.read_text()[-8000:]); raise SystemExit(r.returncode)
        owner = read(out / 'owners/RESULT.json')
    claim = read(P / 'CLAIM.json')
    admit = read(P / 'evidence/ADMISSION-RESULT.json')
    release = read(P / 'evidence/RELEASE-RECEIPT.json')
    native = read(P / 'evidence/FULL-NATIVE-RECEIPT.json')
    baseline = read(P / 'allocation/baseline/CLAIM.json')
    assert claim['status'] == 'CONDITIONAL_CANDIDATE_COMPLETE_FINITE_RELEASE'
    assert owner['status'] == 'PASS_CAP_FILL_LITERAL_OWNERS_AND_EXACT_MOMENT' and len(owner['controls']) == 5
    assert admit['status'] == 'PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE'
    assert release['status'] == 'PASS_RELEASE'
    k = Q(claim['kappa'])
    assert Q(owner['moment']['target']) == k == Q(admit['kappa']) == Q(release['kappa_decimal'])
    assert Q(claim['complex_lower']) == Q(admit['complex_lower'])
    assert k == Q(claim['complex_lower']) - Q(1, 10 ** 46) - Q(1, 10 ** 70)
    assert owner['profile'] == claim['profile'] == admit['profile']
    assert owner['physical'] == claim['physical_families'] == 66804
    assert release['manifest_sha256'] == admit['package_manifest_sha256'] == claim['admitted_package_manifest_sha256']
    assert native['status'] == 'PASS_COMPOSED_FRESH_NATIVE_PROVIDERS_AND_AUTHENTICATED_CACHE'
    assert native['fresh_current_provider_count'] == 2 and set(native['providers']) == {'base', 'extra'}
    assert claim['release_receipt_sha256'] == admit['release_receipt_sha256'] == sha(P / 'evidence/RELEASE-RECEIPT.json')
    assert claim['native_receipt_sha256'] == admit['native_receipt_sha256'] == sha(P / 'evidence/FULL-NATIVE-RECEIPT.json')
    assert claim['source_manifest_sha256'] == native['manifest_sha256'] == admit['source_manifest_sha256']
    assert admit['comparison_pr'] == 2917 and admit['comparison_head'] == PR2917_HEAD == claim['baseline_head']
    assert Q(claim['baseline_kappa']) == Q(admit['comparison_kappa']) == Q(baseline['kappa']) == Q(owner['moment']['previous'])
    assert Q(claim['gain']) == Q(admit['gain']) == k - Q(baseline['kappa']) > 0
    for tag in ('base', 'extra'):
        assert native['providers'][tag]['word_sha256'] == sha(P / f'rewrite/FINAL-WORD-{tag}.json.gz')
    assert admit['fill_sha256'] == sha(P / 'allocation/FILL.json.gz')
    assert admit['order_sha256'] == sha(P / 'allocation/ORDER.json')
    assert admit['dispatch_sha256'] == sha(P / 'allocation/DISPATCH.json')
    assert tree() == pins
    print('PASS_CAP_FILL_LOCAL_OWNER_MOMENT_CAP_AND_STORED_RELEASE', claim['kappa_decimal'][:40], 'gain', float(Q(claim['gain'])))

if __name__ == '__main__':
    main()
