#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Isolated CLI controls. Writes only to an automatically removed temporary copy."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent


def require(ok, label):
    if not ok:
        raise ValueError(label)


def snapshot(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file()}


def main():
    original = snapshot(HERE)
    names = ('MODEL.json', 'CERTIFICATE.json', 'EXPECTED.json')
    with tempfile.TemporaryDirectory(prefix='crown publication with spaces ') as td:
        sandbox = Path(td)
        package = sandbox/'standalone package'
        work = sandbox/'empty working directory'
        work.mkdir()
        shutil.copytree(HERE, package)
        require(not (sandbox/'.git').exists() and not (package/'.git').exists(), 'no checkout in copied test root')
        pristine = {n: (package/n).read_bytes() for n in names}

        def reset():
            for n, raw in pristine.items():
                (package/n).write_bytes(raw)

        def run(expect_success, flags=()):
            before = snapshot(package)
            result = subprocess.run([sys.executable, '-I', '-O', '-B', str(package/'verify.py'), *flags],
                                    cwd=work, capture_output=True, text=True, timeout=10)
            require(snapshot(package) == before, 'default verifier wrote or changed package files')
            if expect_success:
                require(result.returncode == 0 and not result.stderr, 'standalone replay failed: ' + result.stderr)
                require('PASS_P112_COSTAR_CROWN_PREMISES' in result.stdout, 'missing success result')
            else:
                require(result.returncode == 1 and not result.stdout and result.stderr.startswith('FAIL_P112_COSTAR_CROWN:'),
                        'bad input was not cleanly rejected: ' + repr(result))
            return result.stdout

        baseline = run(True)
        require(run(True) == baseline, 'default output is nondeterministic')
        require(run(True, ('--json',)) == run(True, ('--json',)), 'JSON output is nondeterministic')
        controls = ['copied-package-no-checkout-path-with-spaces', 'read-only-default', 'deterministic-default-and-json']
        for name in names:
            reset()
            (package/name).unlink()
            run(False)
            controls.append('missing-' + name)
        for label, raw in [('malformed', b'{'), ('duplicate-key', b'{"x":1,"x":2}'), ('nonfinite', b'{"x":NaN}')]:
            reset()
            (package/'CERTIFICATE.json').write_bytes(raw)
            run(False)
            controls.append(label + '-certificate')
        mutations = [
            ('MODEL.json', 'normal_source_indices', [0, 1, 56, 86]),
            ('MODEL.json', 'term_capacities', [3, 3, 2, 2]),
            ('MODEL.json', 'zero_coefficients_allowed', False),
            ('MODEL.json', 'asymmetric_factors_allowed', False),
            ('MODEL.json', 'ordered_mask', 'diagonal only'),
            ('MODEL.json', 'co_star', 'orthogonal lines, excluding the self-line'),
            ('CERTIFICATE.json', 'remaining_group_capacity', 3),
            ('CERTIFICATE.json', 'residual_target_rank', 2),
            ('CERTIFICATE.json', 'ordered_mask_count', 112),
            ('CERTIFICATE.json', 'ordered_proof_equations', []),
            ('CERTIFICATE.json', 'normal_source_indices', [False, 1, 56, 87]),
            ('CERTIFICATE.json', 'verdict', 'accepted'),
            ('EXPECTED.json', 'status', 'ACCEPTED_BY_CALLER'),
        ]
        for name, key, value in mutations:
            reset()
            obj = json.loads(pristine[name])
            obj[key] = value
            (package/name).write_text(json.dumps(obj))
            run(False)
            controls.append('tampered-' + name + '-' + key)
        reset()
        cert = json.loads(pristine['CERTIFICATE.json'])
        cert['nine_root_coordinates']['87'][2] = 1
        (package/'CERTIFICATE.json').write_text(json.dumps(cert))
        run(False)
        controls.append('tampered-root-coordinate')
        reset()
        # JSON formatting is not mathematical evidence and is deliberately unpinned.
        for name in names:
            (package/name).write_text(json.dumps(json.loads(pristine[name]), sort_keys=True))
        require(run(True) == baseline, 'semantic-equivalent JSON formatting rejected')
        controls.append('formatting-only-changes-accepted')
    require(snapshot(HERE) == original, 'original publication package changed')
    print('PASS_CROWN_PORTABILITY controls=' + str(len(controls)) + ' no_checkout read_only deterministic')


if __name__ == '__main__':
    main()
