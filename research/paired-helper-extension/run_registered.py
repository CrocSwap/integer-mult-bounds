#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact local/owner/moment replay and binding of recorded complete release.

This bounded command does not rerun the native or integrated outer replay;
reproduce.py executes that separately from exact Git sources.
"""
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from fractions import Fraction as Q
from pathlib import Path

P = Path(__file__).resolve().parent


def read(p):
    return json.loads(p.read_bytes())


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def tree():
    assert not any(f.is_symlink() for f in P.rglob('*'))
    return {f.relative_to(P).as_posix(): sha(f) for f in P.rglob('*')
            if f.is_file() and f != P / 'MANIFEST.json'}


def main():
    assert __debug__
    pins = read(P / 'MANIFEST.json')
    assert tree() == pins
    with tempfile.TemporaryDirectory(prefix='paired-extension-replay-') as tmp:
        out = Path(tmp)
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1')
        for key in ('PYTHONOPTIMIZE', 'PYTHONPATH', 'WITNESS_SPEC', 'WITNESS_RECORD', 'WITNESS_DISCOVER'):
            env.pop(key, None)
        for script, name in [('verify.py', 'local'), ('check_allocation.py', 'owners')]:
            log = out / (name + '.log')
            with log.open('w') as stream:
                result = subprocess.run([sys.executable, '-B', str(P / script), '--work', str(out / name)],
                                        env=env, stdin=subprocess.DEVNULL, stdout=stream, stderr=subprocess.STDOUT)
            if result.returncode:
                print(log.read_text()[-8000:])
                raise SystemExit(result.returncode)
        local = read(out / 'local/RESULT.json')
        owner = read(out / 'owners/RESULT.json')
        claim = read(P / 'CLAIM.json')
        admit = read(P / 'evidence/ADMISSION-RESULT.json')
        release = read(P / 'evidence/RELEASE-RECEIPT.json')
        native = read(P / 'evidence/FULL-NATIVE-RECEIPT.json')
        assert local['status'] == 'PASS_NINE_ADDITIONAL_PAIRED_EXTRACTIONS'
        assert len(local['semantic_controls']) == 36
        assert claim['status'] == 'CONDITIONAL_CANDIDATE_COMPLETE_FINITE_RELEASE'
        assert owner['status'] == 'PASS_PAIRED_EXTENSION_LITERAL_OWNERS_AND_EXACT_MOMENT'
        assert admit['status'] == 'PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE'
        assert release['status'] == 'PASS_RELEASE'
        assert Q(owner['moment']['target']) == Q(claim['kappa']) == Q(admit['kappa']) == Q(release['kappa_decimal'])
        assert owner['profile'] == claim['profile'] == admit['profile']
        assert owner['physical'] == claim['physical_families'] == 66804
        assert release['manifest_sha256'] == admit['package_manifest_sha256']
        assert native['status'] == 'PASS_COMPOSED_FRESH_NATIVE_PROVIDERS_AND_AUTHENTICATED_CACHE'
        assert native['fresh_current_provider_count'] == 2 and set(native['providers']) == {'base', 'extra'}
        assert native['reused_retained_native_count'] == 2 and native['reused_retained_parent']
        assert claim['release_receipt_sha256'] == admit['release_receipt_sha256'] == sha(P / 'evidence/RELEASE-RECEIPT.json')
        assert claim['native_receipt_sha256'] == admit['native_receipt_sha256'] == sha(P / 'evidence/FULL-NATIVE-RECEIPT.json')
        assert claim['source_manifest_sha256'] == native['manifest_sha256'] == admit['source_manifest_sha256']
        assert Q(claim['baseline_kappa']) == Q(admit['comparison_kappa']) == Q(owner['moment']['previous'])
        for tag in ('base', 'extra'):
            assert native['providers'][tag]['word_sha256'] == sha(P / f'data/WORD-{tag}.json.gz')
        assert admit['fill_sha256'] == sha(P / 'allocation/FILL.json.gz')
        assert admit['order_sha256'] == sha(P / 'allocation/ORDER.json')
        assert admit['dispatch_sha256'] == sha(P / 'allocation/DISPATCH.json')
        assert tree() == pins
        print('PASS_PAIRED_EXTENSION_LOCAL_OWNER_MOMENT_AND_STORED_RELEASE', claim['kappa'])
        print('Native and full integrated admission are authenticated stored evidence here; reproduce.py reruns them.')


if __name__ == '__main__':
    main()
