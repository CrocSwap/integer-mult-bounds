#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Bounded registered check: package pins; the exact local replay of the four declared stages (verify.py); literal owners,
private stock, controls and exact moment against PR2969 (check_allocation.py); the Fractions-only cap certificates of every
stage, the literal gap and the exact comparisons (check_cap.py); independent review of the four declared edits (edits_review.py);
and binding of the stored receipts to the exact words, overlay, allocation and claim.
"""
import hashlib, json, os, subprocess, sys, tempfile
from fractions import Fraction as Q
from pathlib import Path

P = Path(__file__).resolve().parent
PR2969_HEAD = 'e2ca469b08385d3d5e29a918d66dbefaf889e9f3'
PR2917_DERIVED_SOURCE = '98d57c82a1c7318be3c330c3b66897844d57232f0aaeaea88fb4bebd0a1bedf1'
PR2917_WORDS = {'base': 'fec3c120db1a35022944628d34b56a36f2456248c274c2eaba1a325cdc690ce8',
                'extra': 'e4d0c617df85bf8a824ff68310ca3373dc017c1ebf9ea733056a3ee4a784b36f'}     # the overlay's spec source words
OVERLAY_SOURCE = '751b46364742cbb947f7db07c130ff09085b38b52c520d3b47f2dadc1e21ba80'
STAGE = 'rank7-joint-endframes'

def read(p):
    return json.loads(p.read_bytes())

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def tree():
    assert not any(f.is_symlink() for f in P.rglob('*'))
    return {f.relative_to(P).as_posix(): sha(f) for f in P.rglob('*')
            if f.is_file() and '__pycache__' not in f.parts and f != P / 'MANIFEST.json'}

def main():
    if not __debug__:
        raise SystemExit('refusing python -O: this check relies on assertions')
    pins = read(P / 'MANIFEST.json')
    assert tree() == pins, 'complete package inventory'
    with tempfile.TemporaryDirectory(prefix='rank7-replay-') as tmp:
        out = Path(tmp)
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1')
        for key in ('PYTHONOPTIMIZE', 'PYTHONPATH', 'WITNESS_SPEC', 'WITNESS_RECORD', 'WITNESS_DISCOVER'):
            env.pop(key, None)
        for script, name in [('verify.py', 'local'), ('check_allocation.py', 'owners')]:
            log = out / (name + '.log')
            with log.open('w') as stream:
                r = subprocess.run([sys.executable, '-B', str(P / script), '--work', str(out / name)],
                                   env=env, stdin=subprocess.DEVNULL, stdout=stream, stderr=subprocess.STDOUT)
            if r.returncode:
                print(log.read_text()[-8000:]); raise SystemExit(r.returncode)
            print('PASS', script, log.read_text().strip().splitlines()[-1][:160], flush=True)
        r = subprocess.run([sys.executable, '-B', str(P / 'check_cap.py')], env=env, stdin=subprocess.DEVNULL,
                           capture_output=True, text=True)
        if r.returncode:
            print(r.stdout[-4000:], r.stderr[-4000:]); raise SystemExit(r.returncode)
        cap = json.loads(r.stdout.strip().splitlines()[-1])
        print('PASS check_cap.py', cap['status'], 'gap', cap['gap_float'], flush=True)
        ereview_dir = out / 'edits-review'
        log = out / 'edits-review.log'
        with log.open('w') as stream:
            r = subprocess.run([sys.executable, '-B', str(P / 'edits/edits_review.py'), '--source-dir', str(P / 'vendor'),
                                '--parent-base', str(P / 'data/WORD-base.json.gz'), '--parent-extra', str(P / 'data/WORD-extra.json.gz'),
                                '--candidate-base', str(P / 'edits/FINAL-WORD-base.json.gz'), '--candidate-extra', str(P / 'edits/FINAL-WORD-extra.json.gz'),
                                '--edits', str(P / 'edits/EDITS.json'), '--out-dir', str(ereview_dir)],
                               env=env, stdin=subprocess.DEVNULL, stdout=stream, stderr=subprocess.STDOUT)
        if r.returncode:
            print(log.read_text()[-8000:]); raise SystemExit(r.returncode)
        print('PASS edits_review.py', log.read_text().strip().splitlines()[-1][:160], flush=True)
        ereview = read(ereview_dir / 'REVIEW.json')
        local = read(out / 'local/RESULT.json')
        owner = read(out / 'owners/RESULT.json')
    claim = read(P / 'CLAIM.json')
    admit = read(P / 'evidence/ADMISSION-RESULT.json')
    release = read(P / 'evidence/RELEASE-RECEIPT.json')
    native = read(P / 'evidence/FULL-NATIVE-RECEIPT.json')
    overlay = read(P / 'evidence/OVERLAY-DERIVATION.json')
    edits = read(P / 'evidence/EDITS-DERIVATION.json')
    ereview_stored = read(P / 'evidence/EDITS-REVIEW.json')
    adapters = read(P / 'evidence/ADAPTER-DERIVATION.json')
    replay = read(P / 'evidence/FULL-REPLAY-RESULT.json')
    baseline = read(P / 'allocation/baseline/CLAIM.json')
    assert claim['status'] == 'CONDITIONAL_CANDIDATE_COMPLETE_FINITE_RELEASE'
    assert local['status'] == 'PASS_RANK7_JOINT_ENDFRAMES_THREE_STAGE_REPLAY' and local['control_counts'] == {'stage1': 20, 'stage2': 52, 'stage3': 14, 'stage4': 14}
    assert ereview['status'] == 'PASS_INDEPENDENT_EDIT_REVIEW' == ereview_stored['status'] and ereview == ereview_stored
    assert owner['status'] == 'PASS_RANK7_LITERAL_OWNERS_AND_EXACT_MOMENT' and len(owner['controls']) == 5
    assert cap['status'] == 'PASS_LITERAL_ALLOCATION_BELOW_FIXED_INVENTORY_CAP_WITH_RECORDED_GAP'
    assert admit['status'] == 'PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE'
    assert release['status'] == 'PASS_RELEASE' and replay['status'] == 'PASS_RANK7_EDITS_COMPLETE_REPLAY'
    k = Q(claim['kappa'])
    assert Q(owner['moment']['target']) == k == Q(admit['kappa']) == Q(release['kappa_decimal']) == Q(replay['kappa']) == Q(cap['headline'])
    assert Q(claim['complex_lower']) == Q(admit['complex_lower']) <= Q(cap['literal_lower'])
    assert k == Q(claim['complex_lower']) - Q(1, 10 ** 46) - Q(1, 10 ** 70)
    assert Q(cap['cap_lower']) == Q(claim['fixed_inventory_cap']['cap_lower']) and Q(cap['gap_lower']) > 0
    assert owner['profile'] == claim['profile'] == admit['profile'] == cap['profile']
    assert owner['physical'] == claim['physical_families'] == 66813 and claim['zero_buffers'] == 91
    assert release['manifest_sha256'] == admit['package_manifest_sha256'] == claim['admitted_package_manifest_sha256']
    assert native['status'] == 'PASS_COMPOSED_FRESH_NATIVE_PROVIDERS_AND_AUTHENTICATED_CACHE'
    assert native['fresh_current_provider_count'] == 2 and set(native['providers']) == {'base', 'extra'}
    assert claim['release_receipt_sha256'] == admit['release_receipt_sha256'] == sha(P / 'evidence/RELEASE-RECEIPT.json')
    assert claim['native_receipt_sha256'] == admit['native_receipt_sha256'] == sha(P / 'evidence/FULL-NATIVE-RECEIPT.json')
    assert overlay['stage'] == STAGE and overlay['upstream_manifest_sha256'] == PR2917_DERIVED_SOURCE and overlay['buffers'] == 91
    assert edits['status'] == 'PASS_SOURCE_BOUND_DECLARED_EDIT_OVERLAY' and edits['parent_manifest_sha256'] == overlay['derived_manifest_sha256'] == OVERLAY_SOURCE
    assert claim['declared_edits']['edits_sha256'] == sha(P / 'edits/EDITS.json')
    assert claim['source_manifest_sha256'] == edits['manifest_sha256'] == native['manifest_sha256'] == admit['source_manifest_sha256'] == adapters['source_manifest_sha256']
    assert adapters['buffer_count'] == 91 and 'pr2969' in adapters['comparisons'] and adapters['admission_controls'] == 139
    assert admit['comparison_pr'] == 2969 and admit['comparison_head'] == PR2969_HEAD == claim['baseline_head']
    assert admit['comparison_claim_sha256'] == sha(P / 'allocation/baseline/CLAIM.json')
    assert Q(claim['baseline_kappa']) == Q(admit['comparison_kappa']) == Q(baseline['kappa']) == Q(owner['moment']['previous'])
    assert Q(claim['gain']) == Q(admit['gain']) == k - Q(baseline['kappa']) > 0
    for name, row in claim['previous_claims'].items():
        assert Q(row['gain']) == k - Q(row['kappa']) == Q(cap['comparisons'][name]['gain']) > 0, name
    for tag in ('base', 'extra'):
        word = sha(P / f'data/WORD-{tag}.json.gz')
        final = sha(P / f'edits/FINAL-WORD-{tag}.json.gz')
        assert native['providers'][tag]['word_sha256'] == final == edits['words'][tag]['word_sha256']
        assert edits['words'][tag]['parent_sha256'] == word == overlay['words'][tag]['candidate_word_sha256']
        assert overlay['words'][tag]['source_word_sha256'] == PR2917_WORDS[tag]
    assert admit['fill_sha256'] == sha(P / 'allocation/FILL.json.gz') == claim['fill_sha256']
    assert admit['order_sha256'] == sha(P / 'allocation/ORDER.json')
    assert admit['dispatch_sha256'] == sha(P / 'allocation/DISPATCH.json')
    assert tree() == pins
    print('PASS_RANK7_JOINT_ENDFRAMES_LOCAL_OWNER_MOMENT_CAP_AND_STORED_RELEASE', claim['kappa_decimal'][:40], 'gain over PR2969', float(Q(claim['gain'])))
    print('Native and full integrated admission are authenticated stored evidence here; reproduce.py reruns them.')

if __name__ == '__main__':
    main()
