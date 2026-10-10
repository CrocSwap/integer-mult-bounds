#!/usr/bin/env python3
"""Reproduce the fixed440 early-restoration word and its exact checks."""
import argparse
import hashlib
from pathlib import Path
import subprocess
import sys
if not __debug__:
    raise SystemExit("Assertions required; refusing -O")
sys.dont_write_bytecode = True

SOURCE_SHA256 = '2d22a9530f0b04a7a794d15077459234ef52183d6e7a70f813cfa849b79f2ebe'
OUTPUT_SHA256 = '8dfff69cc400256746443089817175a3345ac096c924957ef04b32c038964373'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-dir', type=Path, required=True)
    parser.add_argument('--export-dir', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert digest(args.source_dir / 'COHORT249-RECORDS.bin') == SOURCE_SHA256
    code = Path(__file__).resolve().parent
    screen = args.output / 'cleanup-selection'
    common = ['--source-dir', str(args.source_dir),
              '--export-dir', str(args.export_dir)]
    subprocess.run([sys.executable, "-B", str(code / 'cleanup_screen.py'), *common,
                    '--output-dir', str(screen)], check=True)
    subprocess.run([sys.executable, "-B", str(code / 'cleanup_emit.py'), *common,
                    '--screen', str(screen / 'screen.json'),
                    '--output', str(args.output)], check=True)
    assert digest(args.output / 'COHORT249-RECORDS.bin') == OUTPUT_SHA256
    print('PASS fixed440 cleanup word:', OUTPUT_SHA256, flush=True)


if __name__ == '__main__':
    main()
