"""Portable isolated-replay and evidence-admission controls; Apache-2.0.

Arham-Tahir64 with substantial OpenAI Codex assistance.
"""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def digest_tree(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file()}


def main():
    inputs = json.loads((HERE/'VERIFY.json').read_text(encoding='utf-8'))['inputs']
    checks = []
    # A checkout-local scratch directory also works in restricted Windows
    # hosts whose redirected system temp directory denies child writes.
    with tempfile.TemporaryDirectory(prefix='diagonal-mask-controls-', dir=ROOT) as directory:
        root = Path(directory)
        need(root.parent == ROOT, 'scratch directory must remain inside the checkout')
        package = root/'research/complex-diagonal-mask-rigidity'
        package.mkdir(parents=True)
        for name in ('verify.py', 'SOURCES.json', 'RESULTS.json'):
            shutil.copyfile(HERE/name, package/name)
        for name in inputs:
            target = root/name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT/name, target)

        def replay(extra=()):
            return subprocess.run([sys.executable, '-I', '-O', '-B', str(package/'verify.py'), *extra],
                                  cwd=root, text=True, capture_output=True, timeout=30)

        before = digest_tree(root)
        result = replay()
        need(result.returncode == 0 and 'PASS_COMPLEX_DIAGONAL_MASK_RIGIDITY' in result.stdout,
             'isolated optimized positive replay: '+result.stderr)
        need(digest_tree(root) == before, 'positive replay writes files')
        checks.append('isolated optimized positive replay and read-only tree')

        # Each mutation is restored before the next case. Diagnostics must
        # identify the intended rejection, not merely crash for another reason.
        def reject(path, mutated, expected):
            original = path.read_bytes()
            path.write_bytes(mutated)
            result = replay()
            need(result.returncode != 0 and expected in result.stderr, 'missing rejection: '+expected)
            path.write_bytes(original)
            checks.append(expected)

        source = root/'research/p112-single-lift/reference-geometry.json'
        reject(source, source.read_bytes()+b' ', 'source drift:')
        pins = json.loads((package/'SOURCES.json').read_text(encoding='utf-8'))
        pins['files'] = [r for r in pins['files'] if r.get('usage') != 'input']
        reject(package/'SOURCES.json', json.dumps(pins).encode(), 'source inventory')
        receipt = json.loads((package/'RESULTS.json').read_text(encoding='utf-8'))
        receipt['singleton_minors'][0]['imaginary_rank'] = 8
        reject(package/'RESULTS.json', json.dumps(receipt).encode(), 'receipt mismatch')
        receipt = json.loads((package/'RESULTS.json').read_text(encoding='utf-8'))
        receipt['singleton_minors'].pop()
        reject(package/'RESULTS.json', json.dumps(receipt).encode(), 'receipt mismatch')

        output = root/'existing-output.json'
        output.write_bytes(b'preserve this existing output\n')
        digest = output.read_bytes()
        result = replay(['--write', str(output)])
        need(result.returncode != 0 and 'FileExistsError' in result.stderr,
             'existing output must be rejected')
        need(output.read_bytes() == digest, 'existing output changed')
        checks.append('existing output rejected and preserved')
        need(digest_tree(root) == {**before, 'existing-output.json': hashlib.sha256(digest).hexdigest()},
             'controls leave altered input files')
    need(len(checks) == 6, 'control coverage')
    print('PASS_DIAGONAL_MASK_PACKAGE_CONTROLS checks=6 isolated_optimized_read_only=1')


if __name__ == '__main__':
    main()
