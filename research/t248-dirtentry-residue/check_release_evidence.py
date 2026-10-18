# SPDX-License-Identifier: Apache-2.0
"""Authenticate retained execution evidence; this does not rerun the full proof.

The separate reproduce.py entry point performs a new complete release.
"""
from pathlib import Path
from fractions import Fraction as Q
import hashlib
import json
import sys
import tarfile

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from generate import authenticate, need, read


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    authenticate()
    evidence = HERE / 'evidence/full'
    pins = read(evidence / 'MANIFEST.json')
    actual = {}
    for path in evidence.rglob('*'):
        need(not path.is_symlink(), 'evidence symlink')
        if path.is_file() and path != evidence / 'MANIFEST.json':
            actual[path.relative_to(evidence).as_posix()] = sha(path)
    need(actual == pins, 'complete retained evidence inventory')
    claim = read(HERE / 'CLAIM.json')
    result = read(evidence / 'candidate/RESULT.json')
    release = read(evidence / 'candidate/release/RELEASE-RECEIPT.json')
    native = read(evidence / 'native/NATIVE-RECEIPT.json')
    native_result = read(evidence / 'native/RESULT.json')
    need(result['status'] == 'PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE'
         and release['status'] == 'PASS_RELEASE', 'successful complete candidate release')
    kappa = Q('0.001718658508304930004819') - Q(1, 10**46) - Q(1, 10**70)
    need(Q(claim['kappa']) == Q(result['kappa']) == Q(release['kappa_decimal']) == kappa,
         'exact headline across release layers')
    previous = read(HERE / 'sources/PR2843-CLAIM.json')
    need(kappa - Q(previous['kappa']) == Q(230463210106193, 10**24), 'exact comparator gain')
    need(result['comparison_claim_sha256'] == sha(HERE / 'sources/PR2843-CLAIM.json'),
         'full exact pinned comparator')
    for field, path in [('fill', 'FILL.json.gz'), ('order', 'ORDER.json'),
                        ('dispatch', 'DISPATCH.json')]:
        need(result[field + '_sha256'] == sha(HERE / path), 'released ' + field + ' identity')
    need(result['profile'] == read(HERE / 'PROFILE.json') == claim['paid_profile'],
         'complete released paid profile')
    need(claim['admission_result_sha256'] == sha(evidence / 'candidate/RESULT.json'),
         'published claim result binding')
    need(claim['release_receipt_sha256'] == result['release_receipt_sha256']
         == sha(evidence / 'candidate/release/RELEASE-RECEIPT.json'), 'release receipt binding')
    need(result['package_manifest_sha256'] == release['manifest_sha256']
         == sha(evidence / 'candidate/admitted-package/MANIFEST.json'), 'admitted package binding')
    need(result['native_receipt_sha256'] == native_result['native_receipt_sha256']
         == sha(evidence / 'native/NATIVE-RECEIPT.json'), 'native receipt binding')
    need(native_result['preparer_sha256'] == sha(HERE / 'prepare_dirtentry_native.py'),
         'actually executed native producer identity')
    need(native['fresh_current_provider_count'] == native['fresh_retained_native_count'] == 2
         and native['fresh_retained_parent'] is True and not native['reused_retained_parent'],
         'four fresh chains and fresh retained parent')
    cached = {}
    with tarfile.open(evidence / 'native/NATIVE-CACHE.tar.gz', 'r:gz') as archive:
        for member in archive.getmembers():
            need(member.isfile(), 'regular cache archive entries only')
            name = member.name
            need(not Path(name).is_absolute() and '..' not in Path(name).parts,
                 'safe cache member path')
            if name.startswith('native-cache/'):
                name = name[len('native-cache/'):]
            need(name not in cached, 'unique cache member')
            cached[name] = hashlib.sha256(archive.extractfile(member).read()).hexdigest()
    need(cached == native['cache_files'], 'complete authenticated native cache payload')
    stages = read(evidence / 'candidate/STAGES.json')
    need([x['name'] for x in stages] == ['owners', 'parent-lift', 'rebind', 'discovery',
         'outer-check_ledger.py', 'outer-independent_check.py', 'release']
         and all(x['exit_code'] == 0 for x in stages), 'all complete admission stages')
    print(json.dumps({'status': 'PASS_RETAINED_RELEASE_EVIDENCE_BINDINGS',
                      'kappa': str(kappa), 'retained_evidence_files': len(pins),
                      'native_cache_files': len(cached),
                      'scope': 'Read-only source, artifact, exact-layer and successful-execution '
                               'receipt authentication; not a fresh native or outer replay.'}, sort_keys=True))


if __name__ == '__main__':
    main()
