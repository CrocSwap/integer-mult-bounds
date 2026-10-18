#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Disposable on-disk mutation and relocation tests for t37-binomial-endpoint-audit-seed78.

Runs under Python -I -O -B from a temporary directory with spaces in its path,
preserving the original package and checking fail-closed certificate preservation.
"""
import hashlib
import json
from pathlib import Path
import runpy
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent


def run(package, cwd, *arguments):
    return subprocess.run(
        [sys.executable, '-I', '-O', '-B', str(package / 'verify.py'), *arguments],
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=60,
    )


def main():
    completed = 0
    mutations = (
        (
            'inputs/ASSEMBLY.json',
            '416181814685169713943/250000000000000000000000',
            '416181814685169713944/250000000000000000000000',
            'Pinned input changed: inputs/ASSEMBLY.json',
        ),
        (
            'inputs/selected-result.json',
            '1661960547713947',
            '1661960547713948',
            'Pinned input changed: inputs/selected-result.json',
        ),
        (
            'inputs/CLAIM.json',
            '"calls": 333',
            '"calls": 332',
            'Pinned input changed: inputs/CLAIM.json',
        ),
        (
            'inputs/EDITS.json',
            '"delay": 0',
            '"delay": 1',
            'Pinned input changed: inputs/EDITS.json',
        ),
        (
            'inputs/PR589-EXPECTED.json',
            '"decoder_constant": 63',
            '"decoder_constant": 62',
            'Pinned input changed: inputs/PR589-EXPECTED.json',
        ),
        (
            'CERTIFICATE.json',
            'PASS_T37_BINOMIAL_AND_ENDPOINT_AUDIT',
            'UNVERIFIED',
            'Recorded certificate differs from fresh independent computation',
        ),
        (
            'verify.py',
            'Q(su + tail, D)',
            'Q(su, D)',
            'Algebraic enclosure failed',
        ),
        (
            'verify.py',
            'nu = ceil_div(tu * numerator, denominator)',
            'nu = tu * numerator // denominator',
            'Algebraic enclosure failed',
        ),
        (
            'verify.py',
            'Q(32 * m * sum(profile.values()), 10**16 * live)',
            'Q(31 * m * sum(profile.values()), 10**16 * live)',
            'Claimed successor does not have a strict rejection certificate',
        ),
        (
            'verify.py',
            'lam_lo, lam_hi = cost[1][0] / 925, cost[1][1] / 925',
            'lam_lo, lam_hi = cost[1][0] / 300, cost[1][1] / 300',
            'Supporting rank inequality failed at r=2',
        ),
    )
    with tempfile.TemporaryDirectory(prefix='t37 binomial controls ') as temporary:
        root = Path(temporary)
        pristine = root / 'relocated with spaces'
        shutil.copytree(HERE, pristine, ignore=shutil.ignore_patterns('__pycache__'))
        ok = run(pristine, root)
        if ok.returncode != 0 or 'PASS_T37_BINOMIAL_AND_ENDPOINT_AUDIT' not in ok.stdout:
            raise RuntimeError('Relocated optimized positive failed: ' + ok.stderr)
        certificate = (pristine / 'CERTIFICATE.json').read_bytes()
        regenerated = run(pristine, root, '--write-certificate')
        if (
            regenerated.returncode != 0
            or (pristine / 'CERTIFICATE.json').read_bytes() != certificate
        ):
            raise RuntimeError('Exact certificate regeneration failed: ' + regenerated.stderr)

        for number, (name, before, after, expected_error) in enumerate(mutations):
            package = root / ('case ' + str(number))
            shutil.copytree(pristine, package)
            path = package / name
            text = path.read_text()
            if before not in text:
                raise RuntimeError('Mutation target missing: ' + name)
            path.write_text(text.replace(before, after, 1))
            before_certificate = (package / 'CERTIFICATE.json').read_bytes()
            arguments = ('--write-certificate',) if name == 'verify.py' else ()
            bad = run(package, root, *arguments)
            if bad.returncode == 0 or 'ValueError: ' + expected_error not in bad.stderr:
                raise RuntimeError(
                    'Mutation missed its expected rejection: ' + name + '\n' + bad.stderr
                )
            if (package / 'CERTIFICATE.json').read_bytes() != before_certificate:
                raise RuntimeError('Rejected run overwrote the certificate: ' + name)
            completed += 1

        check_repository = runpy.run_path(str(pristine / 'verify.py'))['repository_bindings']
        pins = json.loads((pristine / 'SOURCES.json').read_text())
        repository = root / 'repository fixture'
        for local, remote in pins['provenance'].items():
            destination = repository / remote
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(pristine / local, destination)
        reference = repository / 'reference.txt'
        reference.write_bytes(b'Independent source reference fixture\n')
        pins['references'] = {
            'reference.txt': hashlib.sha256(reference.read_bytes()).hexdigest()
        }
        if check_repository(repository, pins) != 6:
            raise RuntimeError('Repository binding positive failed')
        reference.write_bytes(b'Changed reference\n')
        for remove, expected_error in (
            (False, 'Repository source changed: reference.txt'),
            (True, 'Missing repository source: reference.txt'),
        ):
            if remove:
                reference.unlink()
            try:
                check_repository(repository, pins)
            except ValueError as error:
                if str(error) != expected_error:
                    raise RuntimeError(
                        'Unexpected repository rejection: ' + str(error)
                    ) from error
            else:
                raise RuntimeError('Changed repository reference accepted')
            completed += 1

    print(
        'PASS_T37_BINOMIAL_PACKAGE controls='
        + str(completed)
        + ' relocated_optimized=PASS regeneration=PASS failure_preserves_certificate=PASS'
    )


if __name__ == '__main__':
    main()
