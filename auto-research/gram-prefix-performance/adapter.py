#!/usr/bin/env python3
"""Run the pinned Gram checker with an optional exact determinant adapter."""
import argparse
import contextlib
import gzip
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CHECKER = 'research/e8-bit-carrier-skeleton/code/bit/checkers/gram_frames.py'
ANCHOR = 's.loader.exec_module(pw)'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def source_check(root=ROOT):
    pins = json.loads((HERE / 'SOURCE.json').read_text())
    for name, expected in pins['source_sha256'].items():
        require(hashlib.sha256((root / name).read_bytes()).hexdigest() == expected,
                'source pin mismatch: ' + name)
    payload = gzip.decompress((HERE / 'frames.json.gz').read_bytes())
    require(hashlib.sha256(payload).hexdigest() == pins['frames_payload_sha256'],
            'frame payload mismatch')
    return pins, payload


def execute(engine, frames, gram='e8ham', h=8, positive=True, trace=False, old=None, requests=None):
    require(not sys.flags.optimize, 'enabled assertions required by the pinned checker')
    require(engine in ('reference', 'prefix', 'compare'), 'unknown determinant engine')
    source_check()
    from kernel import PrefixDeterminant
    code = (ROOT / CHECKER).read_text()
    require(code.count(ANCHOR) == 1, 'unique pinned insertion point')
    digester = hashlib.sha256()
    calls = 0
    kernel = None

    def install(original):
        nonlocal kernel
        kernel = PrefixDeterminant(original) if engine != 'reference' else None
        target = original if kernel is None else kernel
        if not trace and engine != 'compare' and requests is None:
            return target

        def checked(matrix):
            nonlocal calls
            value = target(matrix)
            if engine == 'compare':
                require(value == original(matrix), 'determinant differs from reference')
            calls += 1
            if requests is not None:
                requests.append([row[:] for row in matrix])
            digester.update(json.dumps([matrix, value], separators=(',', ':')).encode() + b'\n')
            return value
        return checked

    # The only source alteration installs the chosen determinant implementation.
    # All checker loops, assertions, rank and witness code execute unchanged.
    code = code.replace(ANCHOR, ANCHOR + '\npw.det = __install(pw.det)', 1)
    argv = [str(ROOT / CHECKER), str(frames), '--gram', gram, '--h', str(h)]
    if positive:
        argv.append('--positive')
    if old is not None:
        argv.extend(['--new', str(old)])
    saved_argv = sys.argv
    output = io.StringIO()
    try:
        sys.argv = argv
        with contextlib.redirect_stdout(output):
            exec(compile(code, str(ROOT / CHECKER), 'exec'),
                 {'__name__': '__main__', '__file__': str(ROOT / CHECKER), '__install': install})
    finally:
        sys.argv = saved_argv
    return dict(stdout=output.getvalue(), determinant_calls=calls if trace or engine == 'compare' else None,
                determinant_trace_sha256=digester.hexdigest() if trace or engine == 'compare' else None,
                kernel_stats=dict(kernel.stats) if kernel is not None else None)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--engine', choices=['reference', 'prefix', 'compare'], default='prefix')
    ap.add_argument('--frames', type=Path, help='directory with frames.json; defaults to the pinned R420 fixture')
    ap.add_argument('--gram', choices=['e8ham', 'triple9'], default='e8ham')
    ap.add_argument('--h', type=int, default=8)
    ap.add_argument('--no-positive', action='store_true')
    ap.add_argument('--new', type=Path)
    ap.add_argument('--trace', action='store_true')
    ap.add_argument('--out', type=Path)
    args = ap.parse_args()
    require(not sys.flags.optimize, 'enabled assertions required by the pinned checker')
    if args.out:
        require(not args.out.exists(), 'output already exists')
    _, payload = source_check()
    with tempfile.TemporaryDirectory(prefix='gram-prefix-') as temp:
        frames = args.frames or Path(temp)
        if args.frames is None:
            (frames / 'frames.json').write_bytes(payload)
        result = execute(args.engine, frames, args.gram, args.h, not args.no_positive, args.trace, args.new)
    if args.out:
        with args.out.open('x') as stream:
            json.dump(result, stream, indent=2)
            stream.write('\n')
    print(result['stdout'], end='')


if __name__ == '__main__':
    main()
