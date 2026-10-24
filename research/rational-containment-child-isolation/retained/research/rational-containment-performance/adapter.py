"""Run the unchanged, source-pinned mixed-point benchmark with one substitution."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import sys

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
sys.path.insert(0, str(PACKAGE))
from kernel import Containment


def check_sources(root=ROOT):
    manifest = json.loads((PACKAGE / 'SOURCES.json').read_text())
    for item in manifest['files']:
        if item['usage'] != 'input':
            continue
        path = root / item['path']
        if hashlib.sha256(path.read_bytes()).hexdigest() != item['sha256']:
            raise ValueError('Changed pinned input: ' + item['path'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--engine', choices=('reference', 'annihilator', 'compare'), required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--trace', type=Path)
    parser.add_argument('--cpu', type=int)
    args = parser.parse_args()
    if sys.flags.optimize:
        raise SystemExit('Run without -O: inherited checker assertions must remain enabled')
    if args.output.exists() or (args.trace and args.trace.exists()):
        raise SystemExit('Use fresh output paths')
    check_sources()
    sys.path.insert(0, str(ROOT / 'scripts'))
    import rational_span_frames as frames
    original = frames.contained
    candidate = Containment()
    transcript = hashlib.sha256()
    calls = 0
    targets = set()

    def compare(source, target):
        nonlocal calls
        expected, actual = original(source, target), candidate(source, target)
        if expected != actual:
            raise ValueError('Containment disagreement')
        transcript.update(json.dumps([source, target, actual], separators=(',', ':')).encode() + b'\n')
        calls += 1
        targets.add(target)
        return actual

    if args.engine != 'reference':
        frames.contained = compare if args.engine == 'compare' else candidate
    benchmark = ROOT / 'tests/benchmark_rational_span_frames.py'
    sys.argv = [str(benchmark), str(ROOT), str(args.output)]
    if args.cpu is not None:
        sys.argv.extend(('--cpu', str(args.cpu)))
    try:
        runpy.run_path(str(benchmark), run_name='__main__')
    finally:
        frames.contained = original
    if args.trace:
        record = dict(engine=args.engine, compared_calls=calls, distinct_targets=len(targets),
                      transcript_sha256=transcript.hexdigest() if calls else None,
                      cache=candidate.cache_info()._asdict())
        with args.trace.open('x') as stream:
            stream.write(json.dumps(record, indent=2) + '\n')


if __name__ == '__main__':
    main()
