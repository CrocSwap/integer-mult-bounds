#!/usr/bin/env python3
"""Run relocated optimized CLIs and mathematical corruption controls."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


def need(condition, message):
    if not condition:
        raise ValueError(message)


def run(root):
    return subprocess.run(
        [sys.executable, '-I', '-O', '-Werror', '-B',
         str(root/'research/qutrit-mub-stability/verify.py')],
        cwd=root, env={**os.environ, 'PATH': ''},
        capture_output=True, text=True, timeout=30, check=False)


def digest_tree(root):
    files = sorted(p for p in root.rglob('*') if p.is_file())
    need(len(files) <= 16, 'export capacity')
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}


def exported_success(root, package):
    root.mkdir()
    target = root/'research/qutrit-mub-stability'
    shutil.copytree(package, target, copy_function=shutil.copyfile)
    target.chmod(0o700)  # The private mutation copy must be writable even from read-only input.
    source = 'research/pure-math-atlas-400/volumes/02-geometry.md'
    destination = root/source
    destination.parent.mkdir(parents=True)
    shutil.copyfile(package.parents[1]/source, destination)
    before = digest_tree(root)
    result = run(root)
    need(result.returncode == 0 and 'PASS_QUTRIT_MUB_STABILITY' in result.stdout, result.stderr)
    need(digest_tree(root) == before, 'replay changed exported bytes')
    return target, destination


def reject(root, expected):
    result = run(root)
    need(result.returncode != 0 and expected in result.stderr,
         'wrong corruption outcome: '+result.stdout+result.stderr)


def controls(root, package):
    target, source = exported_success(root, package)
    original = source.read_bytes()
    source.write_bytes(original+b'\nchanged\n')
    reject(root, 'source pin mismatch')
    source.write_bytes(original)
    receipt = target/'RESULT.json'
    original = receipt.read_bytes()
    data = json.loads(original)
    data['jacobian_rank'] = True
    receipt.write_text(json.dumps(data))
    reject(root, 'receipt mismatch')
    receipt.write_bytes(original)
    script = target/'verify.py'
    code = script.read_text()
    old = 'row[9*a+k], row[9*b+k] = -value, value'
    need(code.count(old) == 1, 'differential mutation anchor')
    script.write_text(code.replace(old, 'row[9*a+k], row[9*b+k] = value, value'))
    data = json.loads(original)
    data['file_sha256']['verify.py'] = hashlib.sha256(script.read_bytes()).hexdigest()
    receipt.write_text(json.dumps(data))
    reject(root, 'Jacobian rank is not sixteen')
    script.write_text(code)
    receipt.write_bytes(original)
    proof = target/'PROOF.md'
    original_proof = proof.read_bytes()
    proof.write_bytes(original_proof+b'\nchanged\n')
    reject(root, 'receipt mismatch')
    proof.write_bytes(original_proof)
    receipt.unlink()
    reject(root, 'FileNotFoundError')
    receipt.write_bytes(original)
    need(run(root).returncode == 0, 'restored export fails')


def mathematical_controls(package):
    # Execute the source with a different module name; no bytecode file or module cache.
    namespace = {'__name__': 'qutrit_controls', '__file__': str(package/'verify.py')}
    exec(compile((package/'verify.py').read_text(), str(package/'verify.py'), 'exec'), namespace)
    rows = namespace['linearization']()
    gauges = namespace['gauge_vectors']()
    controls = [([row[:] for row in rows], gauges), (rows, gauges[:9])]
    controls[0][0][0][0] += 1
    for bad_rows, bad_gauges in controls:
        try:
            namespace['analyze'](bad_rows, bad_gauges)
        except ValueError:
            continue
        raise ValueError('invalid mathematical certificate accepted')


def main():
    package = Path(__file__).resolve().parent
    mathematical_controls(package)
    with tempfile.TemporaryDirectory(prefix='qutrit-controls-', dir=os.environ.get('TMPDIR')) as temporary:
        controls(Path(temporary)/'export', package)
    print('PASS_QUTRIT_MUB_CONTROLS rejected=7 optimized_export=PASS immutable=PASS')


if __name__ == '__main__':
    main()
