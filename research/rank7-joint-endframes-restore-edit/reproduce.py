#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact Git exports, PR2917's declared source stages, the rank7-joint-endframes overlay, fresh native chains and complete
admission of this package's three-stage words (PR2942's words + joint rank-7 end frames + five paired extractions +
PR2957's fourteen declared rewrites) with a new literal T74 allocation, against Dugongue's PR2969 headline.

The recipe is our PR2942 reproduce.py (itself PR2917's reproduce.py by Mason Hale, with PR2908's stage/native/release
mechanisms by Jeremy Diviney and the credited upstream lineage, as generalized by PR2930), with these changes:
(1) after PR2917's paired-extension stage, tools/build_overlay.py appends the stage 'rank7-joint-endframes' to PR2917's
derived source: the exact edit spec PR2917 word -> this package's word (tools/wordedit.py, cleanup re-derived), replayed
by the source's own rebuild chain with guards for lowered endpoints and moved warp positions, so every previous state
stays in the audit chain; (2) the closed adapters are derived for 91 private buffers and six width classes with the PR2917,
PR2966 and PR2969 headlines as pinned comparators (tools/derive_adapters.py); (3) the admission uses this package's
allocation/ and compares against PR2969. PR2942 (parent words), PR2957 (rewrite applier), PR2966 and PR2969 (comparators)
are exported from their exact commits and checked byte for byte. No network fetch is performed: the commits below must be
present in --repo (see README). Fresh retained bootstrap is the default; --retained explicitly reuses a completely
authenticated cache. Marius-Paul Dumitrean, with substantial AI assistance (Claude Code).
"""
import argparse, hashlib, io, json, os, shutil, subprocess, sys, tarfile, time
from fractions import Fraction as Q
from pathlib import Path, PurePosixPath

P = Path(__file__).resolve().parent
PR2908 = ('51309592971e3b5be935599eed2a95404dc7781e', 'research/two-sided-helper-extraction',
          '9dba3fe371602ec023a54e26c0fd66f69eb7a74be86aab89923529083c14b36f')
PR2917 = ('224bd5e56041c40078ff6b5fa7393733a215de5c', 'research/paired-helper-extension',
          '55c46ddf2e3edc87dfe1ba3320947466d36980d457eb37f6cd6fba341dae0192')
PR2942 = ('a027b0f6fdb0ab2b42ba10fc31b53960166bf2bf', 'research/paired-extension-normal45',
          '23bd270f440c4c7ad0d106990ae391e1af799a61ef3601d00e27f1824ae8ba69')
PR2957 = ('b74b25f3ccc84c16e1a801d73b2f47e5ea764c78', 'research/paired-extension-cap-fill-swaps',
          '9cd226a2bf7391e7fbf4a23741bb1934afafbd596aef06f2999a935cd6e44e28')
PR2966 = ('e62d3eb9005117d82a9babcfa937ecc53237c490', 'research/paired-extension-normal45-rewrites',
          '9e410c244efb370e20a5f9dc366550e11bcb14ebcecf8f2cb850512e82573914')
PR2969 = ('e2ca469b08385d3d5e29a918d66dbefaf889e9f3', 'research/paired-swap-normal45',
          '797c55c560dec5b5a657296f49d918fc5db708b7bed3eba046b3358b1666e55b')
PR2917_SOURCE = '98d57c82a1c7318be3c330c3b66897844d57232f0aaeaea88fb4bebd0a1bedf1'     # PR2917 derived source, 632 files
# PR2917's derived source plus the stage rank7-joint-endframes (637 files), deterministic from this package
OVERLAY_SOURCE = '751b46364742cbb947f7db07c130ff09085b38b52c520d3b47f2dadc1e21ba80'
# PR2979's overlay plus the stage declared-edit-list (tools/build_edits.py), deterministic from this package
EDIT_SOURCE = '9215312229c431078ba61daf106edb8caf20b33f48317d46438a341552cf153f'
STAGE, PROFILE, COMMIT = 'rank7-joint-endframes', 'rank7-joint-endframes', 'rank7-joint-endframes-pr2917'

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def read(p):
    return json.loads(p.read_bytes())

def save(p, value):
    p.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')

def tree(p):
    assert not any(f.is_symlink() for f in p.rglob('*'))
    return {f.relative_to(p).as_posix(): sha(f) for f in p.rglob('*') if f.is_file() and f != p / 'MANIFEST.json'}

def export(repo, head, package, manifest, out):
    prefix = PurePosixPath(package)
    raw = subprocess.run(['git', '-C', str(repo), 'archive', '--format=tar', head, str(prefix)],
                         check=True, capture_output=True).stdout
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
    assert sha(out / 'MANIFEST.json') == manifest, 'exact exported package manifest ' + package
    assert tree(out) == read(out / 'MANIFEST.json'), 'complete exported inventory ' + package

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    for name in ('repo', 'work'):
        ap.add_argument('--' + name, type=Path, required=True)
    ap.add_argument('--retained', type=Path)
    ap.add_argument('--jobs', type=int, default=1, choices=(1, 2, 3))
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()
    if not __debug__:
        raise SystemExit('refusing python -O: the inherited validators rely on assertions')
    work, repo = args.work.resolve(), args.repo.resolve()
    assert not work.exists() and not work.is_relative_to(P) and not P.is_relative_to(work)
    pins = read(P / 'MANIFEST.json')
    assert tree(P) == pins, 'complete public package inventory'
    work.mkdir(parents=True)
    parent, extension, normal45, swaps, rewrites, frontier = [work / n for n in ('pr2908', 'pr2917', 'pr2942', 'pr2957', 'pr2966', 'pr2969')]
    for spec, out in ((PR2908, parent), (PR2917, extension), (PR2942, normal45), (PR2957, swaps), (PR2966, rewrites), (PR2969, frontier)):
        export(repo, *spec, out)
    for tag in ('base', 'extra'):
        assert sha(P / f'data/PARENT-{tag}.json.gz') == sha(normal45 / f'data/WORD-{tag}.json.gz'), 'parents are PR2942s words'
    for name in ('structure.py', 'vendor/audit_local.py', 'vendor/preload_move.py'):
        assert sha(P / name) == sha(extension / name), 'vendored byte-identical from PR2917: ' + name
    assert sha(P / 'vendor/declared_rewrites.py') == sha(swaps / 'rewrite/declared_rewrites.py'), 'PR2957 applier byte-identical'
    assert sha(P / 'allocation/baseline/CLAIM.json') == sha(frontier / 'CLAIM.json'), 'moment baseline is PR2969s headline'
    for name in ('ORDER.json', 'PROFILE.json'):
        assert sha(P / 'allocation/baseline' / name) == sha(frontier / 'allocation' / name), 'PR2969 baseline ' + name
    for name, src in (('PR2942', normal45), ('PR2957', swaps), ('PR2966', rewrites)):
        assert sha(P / f'comparators/{name}-CLAIM.json') == sha(src / 'CLAIM.json'), 'comparator ' + name
    words = work / 'candidate-words'
    words.mkdir()
    for tag in ('base', 'extra'):
        shutil.copy2(P / f'data/WORD-{tag}.json.gz', words / f'WORD-{tag}.json.gz')
    upstream = work / 'parent-export/pr2894'
    core = upstream / 'vendor/pr2857'
    source = work / 'pr2833'
    four, preload, channel, final, overlay, edited = [work / n for n in ('source4', 'source-pm', 'source2908', 'source', 'source-rank7', 'source-edits')]
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
        ('paired-extension-stage', py + [extension / 'tools/build_extension.py', '--source', channel, '--local-package', extension, '--out', final]),
        ('rank7-overlay-stage', py + [P / 'tools/build_overlay.py', '--source', final, '--candidate-dir', words, '--out', overlay, '--stage-name', STAGE]),
        ('declared-edit-stage', py + [P / 'tools/build_edits.py', '--source', overlay, '--local-package', P, '--out', edited]),
        ('derive-closed-adapters', py + [P / 'tools/derive_adapters.py', '--parent-package', parent, '--source', edited, '--retained-receipt', retained / 'NATIVE-RECEIPT.json', '--out', adapters,
                                         '--buffers', '91', '--source-commit', COMMIT, '--source-profile', PROFILE, '--upstream-head', PR2917[0],
                                         '--comparison', 'pr2917=' + str(extension / 'CLAIM.json'), '--comparison', 'pr2966=' + str(rewrites / 'CLAIM.json'),
                                         '--comparison', 'pr2969=' + str(frontier / 'CLAIM.json')]),
        ('fresh-current-native', py + [adapters / 'prepare_extension_native.py', '--source', edited, '--retained-cache', retained / 'native-cache', '--retained-receipt', retained / 'NATIVE-RECEIPT.json', '--out', native, '--jobs', str(min(2, args.jobs))]),
        ('complete-admission', py + [adapters / 'admit_extension.py', '--source', edited, '--fill', P / 'allocation/FILL.json.gz', '--order', P / 'allocation/ORDER.json', '--dispatch', P / 'allocation/DISPATCH.json',
                                     '--native-cache', native / 'native-cache', '--native-receipt', native / 'NATIVE-RECEIPT.json', '--work', candidate, '--replica-helper-dir', core / 'vendor/pr2839',
                                     '--reconstructor', core / 'vendor/pr2839/reconstruct_replica.py', '--blocknorm-checker', adapters / 'extension_blocknorm.py',
                                     '--comparison-claim', frontier / 'CLAIM.json', '--source-profile', PROFILE, '--comparison-profile', 'pr2969', '--jobs', str(args.jobs)]),
    ]
    if args.dry_run:
        save(work / 'PREFLIGHT.json', {'status': 'EXACT_EXPORTS_AND_RECIPE_ONLY_NOT_A_REPLAY', 'commands': [[n, list(map(str, c))] for n, c in recipe]})
        print('PASS_PINNED_PR2908_PR2917_PR2942_PR2957_PR2966_PR2969_EXPORT_RECIPE_ONLY')
        return
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONPYCACHEPREFIX=str(work / 'bytecode'),
               OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', PYTHONINTMAXSTRDIGITS='0')
    for name in ('PYTHONOPTIMIZE', 'PYTHONPATH', 'WITNESS_SPEC', 'WITNESS_RECORD', 'WITNESS_DISCOVER'):
        env.pop(name, None)
    # Windows: text-mode writes would turn the overlay's LF files into CRLF; the stage builders must write LF.
    adapter = work / 'process-lf-adapter'
    adapter.mkdir()
    (adapter / 'sitecustomize.py').write_text("from pathlib import Path\n_w = Path.write_text\ndef _t(self, data, encoding=None, errors=None, newline=None):\n    return _w(self, data, encoding=encoding, errors=errors, newline='\\n' if newline is None else newline)\nPath.write_text = _t\n", encoding='utf-8', newline='\n')
    env['PYTHONPATH'] = str(adapter)
    stages = []
    for name, command in recipe:
        if name == 'rank7-overlay-stage':
            assert sha(final / 'MANIFEST.json') == PR2917_SOURCE, 'derived source equals PR2917s'
        log, start = work / (name + '.log'), time.monotonic()
        with log.open('w') as stream:
            result = subprocess.run(list(map(str, command)), env=env, cwd=work, stdin=subprocess.DEVNULL,
                                    stdout=stream, stderr=subprocess.STDOUT)
        stages.append({'stage': name, 'exit_code': result.returncode, 'seconds': time.monotonic() - start, 'log_sha256': sha(log)})
        save(work / 'STAGES.json', stages)
        assert result.returncode == 0, 'failed ' + name + '; see ' + str(log)
        if name == 'rank7-overlay-stage':
            derivation = read(work / 'source-rank7-DERIVATION.json')
            assert derivation['stage'] == STAGE and derivation['buffers'] == 91 and derivation['upstream_manifest_sha256'] == PR2917_SOURCE
            assert sha(overlay / 'MANIFEST.json') == derivation['derived_manifest_sha256'] == OVERLAY_SOURCE, 'derived rank-7 overlay'
        if name == 'declared-edit-stage':
            derivation = read(work / 'source-edits-DERIVATION.json')
            assert derivation['parent_manifest_sha256'] == OVERLAY_SOURCE
            assert sha(edited / 'MANIFEST.json') == derivation['manifest_sha256'] == EDIT_SOURCE, 'derived declared-edit source'
        print('PASS', name, flush=True)
    admission = read(candidate / 'RESULT.json')
    receipt = read(candidate / 'release/RELEASE-RECEIPT.json')
    claim = read(P / 'CLAIM.json')
    assert admission['status'] == 'PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE'
    assert receipt['status'] == 'PASS_RELEASE'
    assert Q(admission['kappa']) == Q(receipt['kappa_decimal']) == Q(claim['kappa'])
    assert Q(admission['comparison_kappa']) == Q(read(frontier / 'CLAIM.json')['kappa']) == Q(claim['baseline_kappa']) < Q(admission['kappa'])
    assert admission['release_receipt_sha256'] == sha(candidate / 'release/RELEASE-RECEIPT.json')
    assert admission['package_manifest_sha256'] == receipt['manifest_sha256']
    assert admission['source_manifest_sha256'] == EDIT_SOURCE
    assert admission['fill_sha256'] == sha(P / 'allocation/FILL.json.gz')
    assert tree(P) == pins and all(tree(x) == read(x / 'MANIFEST.json') for x in (parent, extension, normal45, swaps, rewrites, frontier))
    save(work / 'RESULT.json', {'status': 'PASS_RANK7_EDITS_COMPLETE_REPLAY', 'kappa': admission['kappa'], 'gain': admission['gain'],
                              'comparison_pr': 2969, 'pr2917_source_manifest_sha256': sha(final / 'MANIFEST.json'),
                              'rank7_source_manifest_sha256': sha(overlay / 'MANIFEST.json'),
                              'source_manifest_sha256': sha(edited / 'MANIFEST.json'),
                              'native_receipt_sha256': sha(native / 'NATIVE-RECEIPT.json'),
                              'admission_result_sha256': sha(candidate / 'RESULT.json'),
                              'explicit_retained_reuse': bool(args.retained), 'fresh_retained_bootstrap': not bool(args.retained),
                              'stages': stages, 'scope': 'Conditional finite supplier/outer result; inherited all-size theorem obligations remain.'})
    print('PASS_RANK7_EDITS_COMPLETE_REPLAY', admission['kappa'], flush=True)

if __name__ == '__main__':
    main()
