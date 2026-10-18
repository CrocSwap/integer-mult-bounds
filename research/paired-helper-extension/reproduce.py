#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact Git exports, declared source stages, fresh native chains, full admission.

Mason Hale, with substantial OpenAI Codex assistance. The stage/native/release
mechanisms retain Jeremy Diviney's PR2908 and its credited upstream lineage.
No network fetch is performed. Fresh retained bootstrap is the default;
--retained explicitly reuses a completely authenticated parent/native cache.
"""
import argparse
import hashlib
import io
import json
import os
import subprocess
import sys
import tarfile
import time
from fractions import Fraction as Q
from pathlib import Path, PurePosixPath

P = Path(__file__).resolve().parent
HEAD = '51309592971e3b5be935599eed2a95404dc7781e'
PARENT_MANIFEST = '9dba3fe371602ec023a54e26c0fd66f69eb7a74be86aab89923529083c14b36f'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read(p):
    return json.loads(p.read_bytes())


def save(p, value):
    p.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def tree(p):
    assert not any(f.is_symlink() for f in p.rglob('*'))
    return {f.relative_to(p).as_posix(): sha(f) for f in p.rglob('*')
            if f.is_file() and f != p / 'MANIFEST.json'}


def export(repo, out):
    prefix = PurePosixPath('research/two-sided-helper-extraction')
    raw = subprocess.run(['git', '-C', str(repo), 'archive', '--format=tar',
                          HEAD, str(prefix)], check=True, capture_output=True).stdout
    out.mkdir()
    with tarfile.open(fileobj=io.BytesIO(raw), mode='r:') as archive:
        for member in archive.getmembers():
            path = PurePosixPath(member.name)
            assert not path.is_absolute() and '..' not in path.parts and '\\' not in member.name
            if member.isdir() and (path == prefix or path in prefix.parents):
                continue
            assert path.is_relative_to(prefix) and (member.isfile() or member.isdir())
            dest = out / path.relative_to(prefix)
            if member.isdir():
                dest.mkdir(parents=True, exist_ok=True)
            else:
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(archive.extractfile(member).read())
    assert sha(out / 'MANIFEST.json') == PARENT_MANIFEST
    assert tree(out) == read(out / 'MANIFEST.json')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    for name in ('repo', 'work'):
        ap.add_argument('--' + name, type=Path, required=True)
    ap.add_argument('--retained', type=Path)
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()
    assert __debug__
    work, repo = args.work.resolve(), args.repo.resolve()
    assert not work.exists() and not work.is_relative_to(P) and not P.is_relative_to(work)
    pins = read(P / 'MANIFEST.json')
    assert tree(P) == pins, 'complete public package inventory'
    work.mkdir(parents=True)
    parent = work / 'pr2908'
    export(repo, parent)
    upstream = work / 'parent-export/pr2894'
    core = upstream / 'vendor/pr2857'
    source = work / 'pr2833'
    four, preload, channel, final = [work / n for n in ('source4', 'source-pm', 'source2908', 'source')]
    native, candidate, adapters = [work / n for n in ('native', 'candidate', 'adapters')]
    retained = args.retained.resolve() if args.retained else work / 'retained'
    if args.retained:
        assert not retained.is_relative_to(work) and not work.is_relative_to(retained)
    py = [sys.executable, '-B']
    recipe = [
        ('export-pr2894', py + [parent / 'reproduce.py', '--repo', repo, '--work', work / 'parent-export', '--dry-run']),
        ('export-pr2833', py + [upstream / 'tools/materialize_source.py', '--repo', repo, '--out', source]),
    ]
    if not args.retained:
        recipe.append(('fresh-retained-bootstrap', py + [upstream / 'tools/prepare_retained.py', '--source', source, '--out', retained, '--jobs', '1']))
    recipe += [
        ('four-kernel-stage', py + [core / 'build_overlay.py', '--source', source, '--generator', core / 'shared_kernel.py', '--review', core / 'review_four_groups.py', '--candidate-dir', core / 'words', '--out', four]),
        ('preload-stage', py + [upstream / 'vendor/pm/build_pm_overlay.py', '--overlay', four, '--pm-dir', upstream / 'vendor/pm', '--out', preload]),
        ('parent-paired-stage', py + [parent / 'tools/build_channel_overlay.py', '--source', preload, '--local-package', parent, '--out', channel]),
        ('paired-extension-stage', py + [P / 'tools/build_extension.py', '--source', channel, '--local-package', P, '--out', final]),
        ('derive-closed-adapters', py + [P / 'tools/derive_adapters.py', '--parent-package', parent, '--source', final, '--source-manifest', read(P / 'CLAIM.json')['source_manifest_sha256'], '--retained-receipt', retained / 'NATIVE-RECEIPT.json', '--out', adapters]),
        ('fresh-current-native', py + [adapters / 'prepare_extension_native.py', '--source', final, '--retained-cache', retained / 'native-cache', '--retained-receipt', retained / 'NATIVE-RECEIPT.json', '--out', native, '--jobs', '1']),
        ('complete-admission', py + [adapters / 'admit_extension.py', '--source', final, '--fill', P / 'allocation/FILL.json.gz', '--order', P / 'allocation/ORDER.json', '--dispatch', P / 'allocation/DISPATCH.json', '--native-cache', native / 'native-cache', '--native-receipt', native / 'NATIVE-RECEIPT.json', '--work', candidate, '--replica-helper-dir', core / 'vendor/pr2839', '--reconstructor', core / 'vendor/pr2839/reconstruct_replica.py', '--blocknorm-checker', adapters / 'extension_blocknorm.py', '--comparison-claim', parent / 'CLAIM.json', '--source-profile', 'paired-extension', '--comparison-profile', 'pr2908', '--jobs', '1']),
    ]
    if args.dry_run:
        save(work / 'PREFLIGHT.json', {'status': 'EXACT_PARENT_EXPORT_AND_RECIPE_ONLY_NOT_A_REPLAY', 'commands': [[n, list(map(str, c))] for n, c in recipe]})
        print('PASS_PINNED_PR2908_EXPORT_RECIPE_ONLY')
        return
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONPYCACHEPREFIX=str(work / 'bytecode'),
               OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', PYTHONINTMAXSTRDIGITS='0')
    for name in ('PYTHONOPTIMIZE', 'PYTHONPATH', 'WITNESS_SPEC', 'WITNESS_RECORD', 'WITNESS_DISCOVER'):
        env.pop(name, None)
    stages = []
    for name, command in recipe:
        log, start = work / (name + '.log'), time.monotonic()
        with log.open('w') as stream:
            result = subprocess.run(list(map(str, command)), env=env, cwd=work,
                                    stdin=subprocess.DEVNULL, stdout=stream, stderr=subprocess.STDOUT)
        stages.append({'stage': name, 'exit_code': result.returncode,
                       'seconds': time.monotonic() - start, 'log_sha256': sha(log)})
        save(work / 'STAGES.json', stages)
        assert result.returncode == 0, 'failed ' + name + '; see ' + str(log)
        print('PASS', name, flush=True)
    admission = read(candidate / 'RESULT.json')
    receipt = read(candidate / 'release/RELEASE-RECEIPT.json')
    claim = read(P / 'CLAIM.json')
    assert admission['status'] == 'PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE'
    assert receipt['status'] == 'PASS_RELEASE'
    assert Q(admission['kappa']) == Q(receipt['kappa_decimal']) == Q(claim['kappa'])
    assert admission['release_receipt_sha256'] == sha(candidate / 'release/RELEASE-RECEIPT.json')
    assert admission['package_manifest_sha256'] == receipt['manifest_sha256']
    assert tree(P) == pins and tree(parent) == read(parent / 'MANIFEST.json')
    save(work / 'RESULT.json', {'status': 'PASS_PAIRED_EXTENSION_COMPLETE_REPLAY', 'kappa': admission['kappa'],
                              'source_manifest_sha256': sha(final / 'MANIFEST.json'),
                              'native_receipt_sha256': sha(native / 'NATIVE-RECEIPT.json'),
                              'admission_result_sha256': sha(candidate / 'RESULT.json'),
                              'explicit_retained_reuse': bool(args.retained),
                              'fresh_retained_bootstrap': not bool(args.retained), 'stages': stages,
                              'scope': 'Conditional finite supplier/outer result; inherited all-size theorem obligations remain.'})
    print('PASS_PAIRED_EXTENSION_COMPLETE_REPLAY', admission['kappa'], flush=True)


if __name__ == '__main__':
    main()
