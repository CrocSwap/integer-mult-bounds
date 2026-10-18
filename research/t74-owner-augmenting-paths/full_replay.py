#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Generate the complete changed data and run the pinned admission chain.

Immutable predecessor sources remain unchanged; a staged driver adds the four
pinned pricing files. Optional reuse must pass the predecessor's complete
source-bound baseline and native evidence validators.
"""
import argparse
import gzip
import hashlib
import json
import os
import shutil
import subprocess
import sys
from fractions import Fraction as Q
from pathlib import Path
from verify import P, canonical, read, require, verify


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_source(root, pin):
    package = root / pin['package']
    manifest = package / pin['manifest']
    require(sha(manifest) == pin['manifest_sha256'], 'Wrong immutable manifest')
    inventory = read(manifest)
    actual = {p.relative_to(package).as_posix() for p in package.rglob('*')
              if p.is_file() and p != manifest and '__pycache__' not in p.parts}
    require(actual == set(inventory), 'Changed immutable source inventory')
    for name, wanted in inventory.items():
        require(sha(package / name) == wanted, 'Changed predecessor file: ' + name)
    return package


def prepare(predecessor, output):
    receipt, owners = verify()
    output.mkdir(parents=True, exist_ok=False)
    for name in ('PLAN.json', 'SPEC.json', 'PROFILE.json', 'OWNERS.json.gz',
                 'DISPATCH.json', 'CONSTRUCTION.json', 'GLOBAL-TEMPLATE.json.gz'):
        shutil.copy2(predecessor / 'data' / name, output / name)
    owner_file = output / 'OWNERS.json.gz'
    owner_file.write_bytes(gzip.compress(canonical(owners), mtime=0))
    plan = read(output / 'PLAN.json')
    plan['source_plan_sha256'] = sha(predecessor / 'data/PLAN.json')
    plan['source_owners_sha256'] = sha(predecessor / 'data/OWNERS.json.gz')
    plan['assignment_sha256'] = sha(owner_file)
    plan['assignment_content_sha256'] = receipt['owners_content_sha256']
    plan['profile'] = receipt['global_profile']
    plan['replica_lift']['owners_file_sha256'] = sha(owner_file)
    plan['solver_status'] = 'Explicit complete augmenting-path witness; unchanged call order'
    (output / 'PLAN.json').write_text(json.dumps(plan, indent=2) + '\n')
    (output / 'PROFILE.json').write_text(json.dumps(receipt['global_profile'], indent=2) + '\n')
    construction = read(output / 'CONSTRUCTION.json')
    construction['idle'] = receipt['idle_profile']
    construction['scope'] = ('Whole-role alternating paths on the pinned PR2322 words. '
                             'Complete chronology, families, widths and prefixes checked.')
    (output / 'CONSTRUCTION.json').write_text(json.dumps(construction, indent=2) + '\n')
    spec = read(output / 'SPEC.json')
    spec['data'] = dict(plan_sha256=sha(output / 'PLAN.json'), owners_sha256=sha(owner_file))
    (output / 'SPEC.json').write_text(json.dumps(spec, indent=2) + '\n')
    return receipt


def stage_priced_driver(predecessor, destination):
    """Keep the native source pin while adopting four exact PR2349 price files."""
    shutil.copytree(predecessor, destination, ignore=shutil.ignore_patterns('__pycache__'))
    overlay = destination / 'PRIVATE-STOCK-OVERLAY'
    overlay.mkdir()
    names = read(P / 'PREDECESSORS.json')['private_stock_overlay']['files']
    for name in names:
        shutil.copy2(P / 'vendor/private-stock' / name, overlay / name)
    driver = destination / 'delta_replay.py'
    text = driver.read_text()
    marker = "    runtime_hashes = {p.relative_to(runtime).as_posix():sha(p)"
    require(text.count(marker) == 1, 'Changed predecessor runtime-copy boundary')
    injection = (
        "    private_stock_overlay = Path(__file__).resolve().parent/'PRIVATE-STOCK-OVERLAY'\n"
        "    overlay_files = {p.name:sha(p) for p in private_stock_overlay.iterdir()}\n"
        "    for name in overlay_files:\n"
        "        shutil.copy2(private_stock_overlay/name,runtime/'code'/name)\n"
    )
    text = text.replace(marker, injection + marker)
    original = "        assert (PACKAGE/relative).is_file() and sha(PACKAGE/relative)==digest, ("
    require(text.count(original) == 1, 'Changed predecessor runtime-binding boundary')
    replacement = (
        "        expected_source = (private_stock_overlay/Path(relative).name\n"
        "                           if relative in {'code/'+n for n in overlay_files}\n"
        "                           else PACKAGE/relative)\n"
        "        assert expected_source.is_file() and sha(expected_source)==digest, ("
    )
    driver.write_text(text.replace(original, replacement))
    return dict(predecessor_driver_sha256=sha(predecessor / 'delta_replay.py'),
                staged_driver_sha256=sha(driver),
                overlay_sha256={name: sha(overlay / name) for name in names})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ancestor-root', type=Path, required=True)
    parser.add_argument('--supplier-root', type=Path, required=True)
    parser.add_argument('--predecessor-root', type=Path, required=True)
    parser.add_argument('--baseline', type=Path)
    parser.add_argument('--base-native', type=Path)
    parser.add_argument('--extra-native', type=Path)
    parser.add_argument('--work', type=Path, required=True)
    args = parser.parse_args()
    require(__debug__, 'The inherited full chain requires assertions enabled')
    pins = read(P / 'PREDECESSORS.json')['sources']
    roots = {'2288': args.ancestor_root.resolve(), '2312': args.supplier_root.resolve(),
             '2322': args.predecessor_root.resolve()}
    packages = {pr: check_source(root, pins[pr]) for pr, root in roots.items()}
    work = args.work.resolve()
    work.mkdir(parents=True, exist_ok=False)
    bounded = prepare(packages['2322'], work / 'data')
    driver_binding = stage_priced_driver(packages['2322'], work / 'driver')
    command = [sys.executable, '-B', str(work / 'driver/cold_replay.py'),
               '--source-root', str(roots['2288']), '--candidate-source-root', str(roots['2312']),
               '--data', str(work / 'data'), '--work', str(work / 'admission')]
    for option in ('baseline', 'base_native', 'extra_native'):
        if getattr(args, option):
            command += ['--' + option.replace('_', '-'), str(getattr(args, option).resolve())]
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONINTMAXSTRDIGITS='0',
               OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1')
    env.pop('PYTHONOPTIMIZE', None)
    with (work / 'admission.log').open('w') as log:
        result = subprocess.run(command, env=env, stdout=log, stderr=subprocess.STDOUT)
    require(result.returncode == 0, 'Admission failed: ' + (work / 'admission.log').read_text()[-3500:])
    admitted = read(work / 'admission/REPLAY.json')
    strict = read(work / 'admission/delta/strict/ASSEMBLY.json')
    invoice = read(work / 'admission/delta/strict/global/audit/PREFIX-AND-INVOICE.json')
    claim = read(P / 'CLAIM.json')
    require(admitted['status'] == 'PASS_SOURCE_BOUND_CHANGED_OWNER_REPLAY', 'Missing full admission')
    require({int(k): v for k, v in strict['complex_profile'].items()}
            == bounded['global_profile'], 'Full invoice differs from the bounded certificate')
    require(Q(claim['comparison_kappa']) < Q(claim['kappa']) < Q(admitted['final_kappa']),
            'Published kappa is not below the full admitted outer point')
    require(Q(strict['bit_lower']) == Q('.001733427039589844234749'), 'Changed bit supplier')
    require(invoice['physical'] == 66826 and invoice['private_zero_buffers'] == 78,
            'Dedicated cleanup-buffer stock was not charged')
    ledger = read(work / 'admission/delta/fine-padding/outer/LEDGER.json')
    receipt = dict(status='PASS_T74_AUGMENTING_PATHS_FULL_CONDITIONAL_ADMISSION',
                   published_kappa=claim['kappa'], admitted_kappa=admitted['final_kappa'],
                   comparison_kappa=claim['comparison_kappa'],
                   global_profile=bounded['global_profile'],
                   owners_content_sha256=bounded['owners_content_sha256'],
                   native_words='Unchanged, source-bound PR2322 base and extra providers',
                   driver_binding=driver_binding,
                   physical_stock=66826, private_zero_buffers=78,
                   invoice_sha256=sha(work / 'admission/delta/strict/global/audit/PREFIX-AND-INVOICE.json'),
                   inherited_replay_sha256=sha(work / 'admission/REPLAY.json'),
                   strict_assembly_sha256=sha(work / 'admission/delta/strict/ASSEMBLY.json'),
                   outer_ledger_sha256=sha(work / 'admission/delta/fine-padding/outer/LEDGER.json'),
                   command=command, explicit_reuse={k: bool(getattr(args, k)) for k in
                                                   ('baseline', 'base_native', 'extra_native')},
                   scope='Finite conditional construction; inherited all-size and analytic premises remain.')
    (work / 'RESULT.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], claim['kappa'], flush=True)


if __name__ == '__main__':
    main()
