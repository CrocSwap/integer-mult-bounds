#!/usr/bin/env python3
"""Run the unchanged pinned helper-interface checker with either exact evaluator."""
import argparse
import runpy
import sys
from pathlib import Path

from common import ROOT, SOURCE, fixture_runs, load_clifford, verify_sources
import fast_state


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--engine', choices=('reference', 'fast'), required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--runs', nargs=2, type=Path,
                    help='optional fresh ck/jp8 artifacts; defaults to pinned archived fixtures')
    args = ap.parse_args()
    verify_sources()
    if args.out.exists():
        raise ValueError('Use a fresh output file')
    clifford = load_clifford()
    if args.engine == 'fast':
        fast_state.clear_caches()
        clifford.Op.zero_state = fast_state.zero_state
    script = ROOT / SOURCE['checker']
    sys.path.insert(0, str(script.parent))
    sys.argv = [str(script), *map(str, args.runs or fixture_runs()),
                '--entering', '36', '--cold', '22', '--out', str(args.out)]
    runpy.run_path(str(script), run_name='__main__')


if __name__ == '__main__':
    main()
