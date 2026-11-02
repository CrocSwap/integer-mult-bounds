"""Bounded exact conformance and failure checks for the new evaluator."""

from hashlib import sha256
from itertools import product
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from adapter import authenticate, require
from sparse_product import raw_product


def literal(a, b):
    """Independent, unpruned dot products on Gaussian integer numerators."""
    ea, ar, ai = a
    eb, br, bi = b
    real, imag = [], []
    for i, j in product(range(8), repeat=2):
        real.append(sum(ar[8*i+k]*br[8*k+j]-ai[8*i+k]*bi[8*k+j] for k in range(8)))
        imag.append(sum(ar[8*i+k]*bi[8*k+j]+ai[8*i+k]*br[8*k+j] for k in range(8)))
    return ea+eb, real, imag


def kernel_checks():
    matrices = []
    for values in product(((0, 0), (1, 0), (0, 1)), repeat=4):
        real, imag = [0]*64, [0]*64
        for index, pair in zip((0, 1, 8, 9), values):
            real[index], imag[index] = pair
        matrices.append((0, tuple(real), tuple(imag)))
    checked = 0
    for a, b in product(matrices, repeat=2):
        require(raw_product(a, b) == literal(a, b), 'Small exact kernel mismatch')
        checked += 1
    for case in range(64):
        real = tuple(((j*37+case*19) % 41-20)*(2**65+1) for j in range(64))
        imag = tuple(((j*13+case*7) % 29-14) for j in range(64))
        a = case % 10, real, imag
        b = (case+3) % 10, tuple(reversed(imag)), tuple(reversed(real))
        require(raw_product(a, b) == literal(a, b), 'Large signed kernel mismatch')
        checked += 1
    return checked


def invoke(script, args=(), optimized=False, cwd=None, success=True):
    command = [sys.executable, '-I', '-W', 'error', '-B']
    if optimized:
        command.append('-O')
    environment = os.environ.copy()
    environment.pop('PYTHONOPTIMIZE', None)
    # Fresh namespace also blocks reads of preexisting bytecode.
    with tempfile.TemporaryDirectory(prefix='sparse-pyc-') as cache:
        command += ['-X', 'pycache_prefix='+cache, str(script), *args]
        result = subprocess.run(command, cwd=cwd, env=environment,
                                capture_output=True, timeout=30, check=False)
    require((result.returncode == 0) == success,
            'Unexpected command status: '+result.stderr.decode(errors='replace')[-1500:])
    if success:
        require(not result.stderr, 'Unexpected command diagnostics')
    return result


def export_fixture(destination):
    """Copy exactly the package and its seventeen live inputs, never Git state."""
    root = HERE.parents[1]
    sources = json.loads((HERE/'SOURCES.json').read_text())
    paths = [row['path'] for row in sources['files'] if row['usage'] == 'input']
    paths += [str(p.relative_to(root)) for p in HERE.iterdir() if p.is_file()]
    require(len(paths) <= 32, 'Export file bound')
    for relative in paths:
        target = destination/relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((root/relative).read_bytes())
    return paths


def rejection_checks(source, expected):
    rejected = 0
    with tempfile.TemporaryDirectory(prefix='sparse-export-') as folder:
        destination = Path(folder)
        paths = export_fixture(destination)
        exported = destination/'research/sparse-gaussian-path-replay/adapter.py'
        environment_path = os.environ.get('PATH')
        os.environ['PATH'] = ''
        try:
            result = invoke(exported, cwd=destination)
            require(result.stdout == expected, 'Git-free complete replay differs')
        finally:
            if environment_path is None:
                os.environ.pop('PATH', None)
            else:
                os.environ['PATH'] = environment_path
        for name in paths:
            if not name.startswith('research/weighted-path-valuations/'):
                continue
            target = destination/name
            original = target.read_bytes()
            target.write_bytes(original+b'\ncorrupt\n')
            failed = invoke(exported, cwd=destination, success=False)
            require(b'Source integrity mismatch' in failed.stderr, 'Wrong pin rejection')
            target.write_bytes(original)
            rejected += 1
        target = exported.parent/'sparse_product.py'
        original = target.read_bytes()
        require(original.count(b'x*u-y*v') == 1, 'Mutation marker mismatch')
        target.write_bytes(original.replace(b'x*u-y*v', b'x*u+y*v'))
        failed = invoke(exported, ('--engine', 'compare'), success=False)
        require(b'Gaussian product conformance mismatch' in failed.stderr,
                'Incorrect Gaussian sign was accepted')
        rejected += 1
    for script in (source/'verify.py', HERE/'adapter.py'):
        failed = invoke(script, optimized=True, success=False)
        require(b'without -O' in failed.stderr, 'Missing optimized-mode rejection')
        rejected += 1
    return rejected


def main():
    source = authenticate()
    kernels = kernel_checks()
    reference = invoke(source/'verify.py')
    sparse = invoke(HERE/'adapter.py')
    require(reference.stdout == sparse.stdout, 'Complete scientific stdout mismatch')
    comparison = json.loads(invoke(HERE/'adapter.py', ('--engine', 'compare')).stdout)
    require(comparison['scientific'] == json.loads(reference.stdout), 'Full compare mismatch')
    stats = comparison['conformance']
    require(stats == {'calls': 30343, 'baseline_products': 2275392,
                      'sparse_products': 1038376,
                      'cache': {'currsize': 8164, 'hits': 22179,
                                'maxsize': 40000, 'misses': 8164},
                      'transcript_sha256':
                      'd1e74f64ea043c5cd5e7028cdf729488401ff111bf58392bb21e9ed137c1819d'},
            'Reached-call transcript or work inventory changed')
    rejected = rejection_checks(source, reference.stdout)
    require(kernels == 6625 and rejected == 20, 'Check inventory changed')
    hashes = {p.name: sha256(p.read_bytes()).hexdigest()
              for p in sorted(HERE.iterdir()) if p.is_file()}
    print(json.dumps({'status': 'PASS_SPARSE_GAUSSIAN_PATH_REPLAY',
                      'kernel_cases': kernels, 'rejections': rejected,
                      'scientific_stdout_sha256': sha256(reference.stdout).hexdigest(),
                      'conformance': stats, 'package_sha256': hashes}, sort_keys=True))


if __name__ == '__main__':
    main()
