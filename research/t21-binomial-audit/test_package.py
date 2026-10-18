#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Disposable on-disk mutation tests, preserving the original package."""
from pathlib import Path
import hashlib
import json
import runpy
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent


def run(package, cwd, *arguments):
    return subprocess.run(
        [sys.executable, '-I', '-O', '-B', str(package/'verify.py'), *arguments],
        cwd=cwd, capture_output=True, text=True, timeout=60)


def main():
    completed = 0
    mutations = (
        ('inputs/ASSEMBLY.json', '1664724476433282815289', '1664724476433282815290',
         'Pinned input changed: inputs/ASSEMBLY.json'),
        ('inputs/selected-result.json', '1661957774647029', '1661957774647030',
         'Pinned input changed: inputs/selected-result.json'),
        ('inputs/CLAIM.json', '"calls": 189', '"calls": 188',
         'Pinned input changed: inputs/CLAIM.json'),
        ('inputs/PROOF.md', '1366848', '1366849',
         'Pinned input changed: inputs/PROOF.md'),
        ('CERTIFICATE.json', 'PASS_T21_BINOMIAL_MOMENT', 'UNVERIFIED',
         'Recorded certificate differs from fresh independent computation'),
        ('verify.py', 'Q(su + tail, D)', 'Q(su, D)', 'Algebraic enclosure failed'),
        ('verify.py', 'nu = ceil_div(tu * numerator, denominator)',
         'nu = tu * numerator // denominator', 'Algebraic enclosure failed'),
        ('verify.py', 'Q(32*m*sum(profile.values()), 10**16*live)',
         'Q(31*m*sum(profile.values()), 10**16*live)',
         'Claimed successor does not have a strict rejection certificate'),
    )
    with tempfile.TemporaryDirectory(prefix='t21-binomial-controls-') as temporary:
        root = Path(temporary)
        pristine = root/'relocated'
        shutil.copytree(HERE, pristine, ignore=shutil.ignore_patterns('__pycache__'))
        ok = run(pristine, root)
        if ok.returncode != 0 or 'PASS_T21_BINOMIAL_MOMENT' not in ok.stdout:
            raise RuntimeError('Relocated optimized positive failed: '+ok.stderr)
        certificate = (pristine/'CERTIFICATE.json').read_bytes()
        regenerated = run(pristine, root, '--write-certificate')
        if regenerated.returncode != 0 or (pristine/'CERTIFICATE.json').read_bytes() != certificate:
            raise RuntimeError('Exact certificate regeneration failed: '+regenerated.stderr)
        for number, (name, before, after, expected_error) in enumerate(mutations):
            package = root/str(number)
            shutil.copytree(pristine, package)
            path = package/name
            text = path.read_text()
            if before not in text:
                raise RuntimeError('Mutation target missing: '+name)
            path.write_text(text.replace(before, after, 1))
            before_certificate = (package/'CERTIFICATE.json').read_bytes()
            # Code defects must fail their mathematical checks even when allowed
            # to regenerate the receipt; a stale-certificate mismatch is insufficient.
            arguments = ('--write-certificate',) if name == 'verify.py' else ()
            bad = run(package, root, *arguments)
            if bad.returncode == 0 or 'ValueError: '+expected_error not in bad.stderr:
                raise RuntimeError('Mutation missed its expected rejection: '+name+'\n'+bad.stderr)
            if (package/'CERTIFICATE.json').read_bytes() != before_certificate:
                raise RuntimeError('Rejected run overwrote the certificate: '+name)
            completed += 1
        # Exercise optional repository comparisons offline. The four input
        # copies are real; the separately pinned reference is a synthetic fixture.
        check_repository = runpy.run_path(str(pristine/'verify.py'))['repository_bindings']
        pins = json.loads((pristine/'SOURCES.json').read_text())
        repository = root/'repository-fixture'
        for local, remote in pins['provenance'].items():
            destination = repository/remote
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(pristine/local, destination)
        reference = repository/'reference.txt'
        reference.write_bytes(b'Independent source reference fixture\n')
        pins['references'] = {'reference.txt':hashlib.sha256(reference.read_bytes()).hexdigest()}
        if check_repository(repository, pins) != 5:
            raise RuntimeError('Repository binding positive failed')
        reference.write_bytes(b'Changed reference\n')
        for remove, expected_error in (
                (False, 'Repository source changed: reference.txt'),
                (True, 'Missing repository source: reference.txt')):
            if remove:
                reference.unlink()
            try:
                check_repository(repository, pins)
            except ValueError as error:
                if str(error) != expected_error:
                    raise RuntimeError('Unexpected repository rejection: '+str(error)) from error
            else:
                raise RuntimeError('Changed repository reference accepted')
            completed += 1
    print('PASS_T21_BINOMIAL_PACKAGE controls='+str(completed)+
          ' relocated_optimized=PASS regeneration=PASS failure_preserves_certificate=PASS')


if __name__ == '__main__':
    main()
