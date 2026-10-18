#!/usr/bin/env python3
"""Read-only source-bound replay. No generation occurs by default.

Ross Richardson with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import gzip
import json
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
_loader_path = HERE / 'source_exec.py'
_loader = {'__file__': str(_loader_path)}
exec(compile(_loader_path.read_bytes(), str(_loader_path), 'exec'), _loader)


def need(ok, why):
    if not ok:
        raise ValueError(why)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path)
    parser.add_argument('--regenerate', action='store_true')
    parser.add_argument('--emit-initial-result', action='store_true',
                        help='authoring only: requires --out; does not read RESULT.json')
    args = parser.parse_args()
    need(not args.emit_initial_result or args.out is not None, 'authoring requires --out')
    need(args.out is None or not args.out.exists(), 'output already exists')
    expected = None if args.emit_initial_result else json.loads((HERE / 'RESULT.json').read_text())
    check = _loader['load_source']('independent_native_binding', HERE / 'check.py')
    result = json.loads(json.dumps(check.replay(controls=True)))
    if not args.emit_initial_result:
        need(result == expected,
             'exact replay receipt differs from fixed RESULT.json')
    if args.regenerate:
        with tempfile.TemporaryDirectory(prefix='p104-two-target-native-') as tmp:
            output = Path(tmp) / 'NATIVE.json.gz'
            subprocess.run([sys.executable, '-I', '-O', '-B', str(HERE / 'compile.py'),
                            '--out', str(output)], check=True, timeout=240)
            need(json.loads(gzip.decompress(output.read_bytes())) ==
                 json.loads(gzip.decompress((HERE / 'NATIVE.json.gz').read_bytes())),
                 'complete regenerated native payload differs')
    data = json.dumps(result, sort_keys=True, indent=2) + '\n'
    if args.out:
        with args.out.open('x') as out:
            out.write(data)
    print(data, end='')
    print('PASS_P104_TWO_TARGET_NATIVE no_new_kappa')


if __name__ == '__main__':
    main()
