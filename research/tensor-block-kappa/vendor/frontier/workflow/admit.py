#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Tekalign (@tekuuu), with substantial OpenAI Codex assistance.
"""Prepare and fully admit a composed-word COMPOSED order/fill derivative.

Research runtime only: native providers must already have passed freshly and
are authenticated by --native-receipt. --prepare-only stops before discovery.
Default complete admission preserves the original verify.py and release stages.
Source inputs and the native cache are read-only; all output uses fresh --work.
"""
import argparse
from fractions import Fraction as Q
import gzip
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import time

SOURCE_COMMIT = 'local-joint12-pr2733'
SOURCE_MANIFEST = '9c72b4301057a6c204c40bb6584eb74b779e06618bcd98d706d726c3e2c92451'   # retired7 derived source: PR2751 overlay + five retired-lender aliases + two hostee moves and two aliases
PARENT_MANIFEST = 'e0eefc96567fbb45e19e6de0ca295381dbe0e686c08ddc783639b065c7c791d4'
PRECISION = dict(endpoint_digits=24, grid_digits=18, margin_digits=28, bootstrap_steps=12)
NATIVE_STAGES = ['native', 'ledgers', 'local-replay', 'wrappers', 'phases']


def need(ok, why):
    if not ok:
        raise RuntimeError(why)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    body = path.read_bytes()
    return json.loads(gzip.decompress(body) if path.suffix == '.gz' else body)


def write(path, value):
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + '\n')


def tree(root, exclude=()):
    result = {}
    for path in sorted(root.rglob('*')):
        need(not path.is_symlink(), 'unbound symlink: ' + str(path))
        name = path.relative_to(root).as_posix()
        if path.is_file() and name not in exclude:
            result[name] = sha(path)
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    for name in ('source', 'fill', 'order', 'native-cache', 'native-receipt', 'work'):
        ap.add_argument('--' + name, type=Path, required=True)
    ap.add_argument('--jobs', type=int, default=4)
    ap.add_argument('--prepare-only', action='store_true')
    a = ap.parse_args()
    need(not sys.flags.optimize and a.jobs > 0, 'enabled assertions and positive jobs required')
    source, cache, work = a.source.resolve(), a.native_cache.resolve(), a.work.resolve()
    need(not work.exists() and not work.is_relative_to(source) and not work.is_relative_to(cache),
         'fresh external work required')
    need(sha(source / 'MANIFEST.json') == SOURCE_MANIFEST, 'COMPOSED manifest pin')
    source_files = read(source / 'MANIFEST.json')
    need(len(source_files) == 506 and tree(source, ('MANIFEST.json',)) == source_files,
         'complete COMPOSED source inventory and hashes')
    native_receipt = read(a.native_receipt)
    need(native_receipt['status'] == 'PASS_COMPOSED_FRESH_NATIVE_PROVIDERS_AND_AUTHENTICATED_CACHE'
         and native_receipt['source_commit'] == SOURCE_COMMIT
         and native_receipt['manifest_sha256'] == SOURCE_MANIFEST, 'native receipt source binding')
    need(tree(cache) == native_receipt['cache_files'], 'complete native/parent cache hashes')
    old = source / 'vendor/pr1297'
    need(sha(old / 'MANIFEST.json') == PARENT_MANIFEST, 'retained parent pin')
    parent_receipt = cache / '_receipts' / PARENT_MANIFEST / 'RECEIPT.json'
    need(sha(parent_receipt) == native_receipt['retained_parent_receipt_sha256'], 'parent receipt pin')
    pr = read(parent_receipt)
    need(pr['vendor_manifest_sha256'] == PARENT_MANIFEST and pr['claim_sha256'] == sha(old / 'CLAIM.json'),
         'parent receipt claim binding')
    for name, digest in pr['files'].items():
        need(sha(parent_receipt.parent / name) == digest, 'parent receipt file')
    parent_result = read(parent_receipt.parent / 'RESULT.json')
    need(parent_result['status'] == 'PASS_GLOBAL_MIXED_X54_FUSIONS_NATIVE_AND_STRICT_ADMISSION'
         and parent_result['kappa'] == read(old / 'CLAIM.json')['kappa'], 'retained parent completed admission')
    natives = {}
    for tag in ('base', 'extra'):
        word = source / ('new/borrow/words/BORROW-WORD-43' + tag + '.json.gz')
        entry = cache / sha(word)
        binding = native_receipt['providers'][tag]
        need(binding['word_sha256'] == sha(word)
             and tree(entry, ('CACHE.json',)) == binding['complete_native_files'], 'native full-tree binding')
        need(read(entry / 'local/FULL-WORD.json.gz') == read(word), 'native complete word')
        stages = read(entry / 'STEPS.json')
        need([s['step'] for s in stages] == NATIVE_STAGES and all(s['exit_code'] == 0 for s in stages),
             'native five-stage coverage')
        checks = read(entry / 'local/LOCAL-CHECKS.json')
        need(all(checks[o]['paid_profile'] == read(word)['report']['local_profile'] for o in ('forward', 'backward')),
             'native actual paid profiles')
        natives[tag] = entry
    work.mkdir(parents=True)
    package = work / 'package'
    shutil.copytree(source, package)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1', PYTHONINTMAXSTRDIGITS='0',
               OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', AUDIT_FAST_SHARDS=str(a.jobs))
    for name in ('PYTHONOPTIMIZE', 'WITNESS_SPEC', 'WITNESS_DISCOVER', 'WITNESS_RECORD'):
        env.pop(name, None)
    stages, patches = [], []

    def run(name, script, *args):
        start = time.monotonic()
        command = [sys.executable, '-B', str(script), *map(str, args)]
        log = work / (name + '.log')
        with log.open('w') as output:
            result = subprocess.run(command, env=env, cwd=work, stdin=subprocess.DEVNULL,
                                    stdout=output, stderr=subprocess.STDOUT)
        stages.append(dict(name=name, exit_code=result.returncode, seconds=time.monotonic() - start,
                           script_sha256=sha(script), log_sha256=sha(log), command=command))
        write(work / 'STAGES.json', stages)
        need(result.returncode == 0, 'failed ' + name + '; see ' + str(log))
        print('PASS', name, flush=True)

    def patch(name, replacements):
        path = package / name
        before = sha(path)
        body = path.read_text()
        for old_text, new_text in replacements:
            need(body.count(old_text) == 1, 'exact patch preimage: ' + name + ': ' + old_text[:80])
            body = body.replace(old_text, new_text)
        path.write_text(body)
        patches.append(dict(path=name, before_sha256=before, after_sha256=sha(path), replacements=replacements))

    # PR2530's already checked correction: restored zero buffers occupy physical
    # rows. COMPOSED's shipped SPEC includes them; its rebound SPEC omitted them.
    patch('new/rebind.py', [
        ("physical=spec['expected']['live'] + 8 + R + 2)",
         "physical=spec['expected']['live'] + 8 + R + 2 + max(len(rd(d / 'CANONICAL-WORD.json.gz').get('zero_buffers', [])) for d in locs.values()))")])
    # Preserve the exact fixed-grid-maximum equality while deriving precision
    # from the same SPEC read by both independent outer arithmetic checkers.
    patch('verify_release.py', [
        ('Fraction(1, 10 ** 3046) - Fraction(1, 10 ** 3022)',
         "Fraction(1, 10 ** (spec['outer_refinement']['endpoint_digits'] + 46)) - Fraction(1, 10 ** (spec['outer_refinement']['endpoint_digits'] + 22))"),
        ('epsilon=1-(1025/1024)e-3080', "epsilon=1-(1025/1024)e-{spec['outer_refinement']['endpoint_digits']+80}"),
        ('at the one 3000-digit rejection call', "at the one {spec['outer_refinement']['endpoint_digits']}-digit rejection call")])
    write(work / 'RUNTIME-PATCHES.json', patches)
    shutil.copy2(a.fill, package / 'new/borrow-fill/FILL.json.gz')
    shutil.copy2(a.order, package / 'new/borrow-fill/ORDER.json')
    run('owners', package / 'reconstruct.py', '--out', work / 'owners')
    run('parent-lift', package / 'lift_parent.py', '--owners', work / 'owners', '--out', work / 'parent-data')
    for name in ('PLAN.json', 'OWNERS.json.gz', 'DISPATCH.json', 'PROFILE.json', 'CONSTRUCTION.json',
                 'GLOBAL-TEMPLATE.json.gz', 'SPEC.json'):
        shutil.copy2(work / 'parent-data' / name, package / name)
    shutil.copy2(work / 'owners/ORDER.json', package / 'ORDER.json')
    spec = read(package / 'SPEC.json')
    spec['outer_refinement'] = PRECISION
    spec['expected']['live'] = 66304
    # COMPOSED's pre-life mechanism changes which helper labels retain width8.
    # Preserve its declared spot set; rebind and the original strict verifier
    # still check the actual native widths, including every other helper.
    source_spots = read(source / 'new/SPEC.json')['width_spot_helpers']
    need(source_spots == [278, 281, 284, 289], 'COMPOSED source spot-width pins')
    spec['width_spot_helpers'] = source_spots
    write(package / 'new/SPEC.json', spec)
    run('rebind', package / 'new/rebind.py', package, natives['base'] / 'local',
        natives['extra'] / 'local', work / 'rebound')
    spec = read(work / 'rebound/SPEC.json')
    need(spec['expected']['physical'] == 66794, 'complete physical cost including 72 buffers (R 408)')
    layout = work / 'layout'
    layout.mkdir()
    with tarfile.open(old / 'upstream-layout.tar.gz') as archive:
        need(all(m.isfile() and not Path(m.name).is_absolute() and '..' not in Path(m.name).parts
                 for m in archive.getmembers()), 'retained archive paths')
        archive.extractall(layout, filter='data')
    runtime = layout / 'packing74'
    runtime.mkdir()
    for name in ('replay.py', 'freeze_spec.py', 'audit_mixed.py', 'independent_core.py', 'geometry_controls.py', 'audit_fast.py'):
        shutil.copy2(package / name, runtime / name)
    for name in ('code', 'construction', 'inputs'):
        shutil.copytree(package / name, runtime / name)
    shutil.copytree(work / 'rebound', runtime / 'candidate')
    shutil.copytree(natives['extra'], runtime / 'native-extra')
    data = runtime / 'candidate'
    result = dict(status='PREPARED_COMPOSED_SAME_WORD_DERIVATIVE_NOT_ADMITTED', source_commit=SOURCE_COMMIT,
                  source_manifest_sha256=SOURCE_MANIFEST, native_receipt_sha256=sha(a.native_receipt),
                  fill_sha256=sha(package / 'new/borrow-fill/FILL.json.gz'),
                  order_sha256=sha(package / 'new/borrow-fill/ORDER.json'), profile=read(work / 'rebound/PROFILE.json'),
                  patches=patches, scope='Prepared only; source/native/parent inputs authenticated and literal owner fill reconstructed.')
    write(work / 'RESULT.json', result)
    if a.prepare_only:
        print(result['status'], flush=True)
        return
    run('discovery', runtime / 'replay.py', '--data', data, '--work', work / 'discovery',
        '--local', natives['base'] / 'local', '--discover')
    supplier = read(work / 'discovery/RESULT.json')
    for name in ('PLAN.json', 'PROFILE.json', 'SPEC.json'):
        shutil.copy2(data / name, package / 'new' / name)
    spec = read(package / 'new/SPEC.json')
    original_claim = read(source / 'CLAIM.json')
    claim = dict(status='CONDITIONAL_CANDIDATE_EXPECTED_BY_REPLAY', kappa=supplier['kappa'],
                 kappa_decimal=supplier['kappa_decimal'], baseline_pr=2679, baseline_head=SOURCE_COMMIT,
                 baseline_kappa=read(source / 'outer/OUTER-CLAIM.json')['kappa'], outer_refinement=PRECISION,
                 scope=original_claim['scope'], kappa_layers=original_claim['kappa_layers'],
                 headline_kappa_source='outer/OUTER-CLAIM.json',
                 verification='Candidate discovered from literal fill; full original verification must pass separately.')
    write(package / 'CLAIM.json', claim)
    C = Q(spec['expected']['complex_lower'])
    write(package / 'outer/B.json', dict(b=str(C-Q(1,10**104)), b_above_endpoint=str(C+Q(1,10**24)),
                                        profile=spec['expected']['global_profile'], live=spec['expected']['live']))
    for name in ('check_ledger.py', 'independent_check.py'):
        run('outer-' + name, package / 'outer' / name)
    ledger = read(package / 'outer/LEDGER.json')
    row = ledger['rows']['struct_boundary_radix_union']['kappa']
    kappa = Q(row['rational'])
    previous = Q('0.0017161404259974415161889999999999999999999998999999999999999999999999')
    need(kappa == C-Q(1,10**70)-Q(1,10**46) and kappa > previous and kappa > Q('17171415863484263381089999999999999999999998999999999999999999999999/10000000000000000000000000000000000000000000000000000000000000000000000'),   # retired5: also strictly above PR2751
         'candidate must strictly improve pinned COMPOSED before full release')
    outer_claim = read(source / 'outer/OUTER-CLAIM.json')
    outer_claim.update(kappa=row['decimal'], kappa_rational=row['rational'],
                       baseline_head=SOURCE_COMMIT, baseline_kappa=str(previous), gain=str(kappa-previous),
                       b='certified complex_lower - 1e-104 (outer/B.json)',
                       retuned_slacks='Endpoint precision24; free gaps follow outer/check_ledger.py from the frozen SPEC.',
                       fixed_grid_maximum='kappa=C-10^-70-10^-46 exactly; same fixed-grid-maximum proof at precision24.')
    write(package / 'outer/OUTER-CLAIM.json', outer_claim)
    write(package / 'MANIFEST.json', tree(package, ('MANIFEST.json',)))
    run('release', package / 'verify_release.py', '--main', source.parents[1], '--work', work / 'release',
        '--native-cache', cache, '--jobs', a.jobs)
    receipt = read(work / 'release/RELEASE-RECEIPT.json')
    need(receipt['status'] == 'PASS_RELEASE' and Q(receipt['kappa_decimal']) == kappa
         and receipt['manifest_sha256'] == sha(package / 'MANIFEST.json'), 'complete release binding')
    need(sha(source / 'MANIFEST.json') == SOURCE_MANIFEST
         and tree(source, ('MANIFEST.json',)) == source_files and tree(cache) == native_receipt['cache_files'],
         'read-only source/cache inputs changed')
    result.update(status='PASS_COMPOSED_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE',
                  complex_lower=str(C), kappa=str(kappa), kappa_decimal=row['decimal'],
                  gain=str(kappa-previous), release_receipt_sha256=sha(work / 'release/RELEASE-RECEIPT.json'),
                  package_manifest_sha256=sha(package / 'MANIFEST.json'), stages=stages,
                  scope='Conditional finite construction and modern outer arithmetic. Exact inherited theorem obligations remain. Both native providers explicitly reused from authenticated fresh five-stage runs.')
    write(work / 'RESULT.json', result)
    print(result['status'], row['decimal'], flush=True)


if __name__ == '__main__':
    main()
