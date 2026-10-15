#!/usr/bin/env python3
"""Reproduce the complete concentrated-source-partner/pre-life admission.

Apache-2.0. Marius-Paul Dumitrean with substantial OpenAI Codex assistance.
"""
import argparse
from fractions import Fraction
import json
from pathlib import Path
import subprocess
import sys

import replay_engine

HERE = Path(__file__).resolve().parent


def main():
    if not __debug__:
        raise RuntimeError('Assertions are required; run without optimized Python.')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work', type=Path, required=True,
                        help='Fresh external directory for all generated outputs')
    args = parser.parse_args()
    work = args.work.resolve()
    sources = [HERE.parent/'gmx-t74-borrow43-handoff',
               HERE.parent/'t74-concentrated-source-partners']
    if work.exists() or any(work.is_relative_to(p.resolve()) for p in [HERE, *sources]):
        raise ValueError('Use a new output directory outside all three packages')
    work.mkdir(parents=True)
    subprocess.run([sys.executable, '-B', str(HERE/'verify.py'),
                    '--work', str(work/'construction')], check=True)
    candidate = HERE/'expected'
    sys.argv = [sys.argv[0], '--source', str(sources[0]),
                '--source2696', str(sources[1]), '--candidate', str(candidate),
                '--fill', str(candidate/'FILL.json.gz'),
                '--order', str(candidate/'ORDER.json'),
                '--work', str(work/'cold'), '--jobs', '1']
    replay_engine.main()
    result = json.loads((work/'cold/RESULT.json').read_bytes())
    claim = json.loads((HERE/'CLAIM.json').read_bytes())
    if (Fraction(result['kappa']) != Fraction(claim['kappa']) or
            result['global_profile'] != claim['global_profile']):
        raise ValueError('Complete cold replay differs from the published claim')
    subprocess.run([sys.executable, '-B', str(HERE/'ordinary_witness.py'),
                    '--ledger', str(work/'cold/derivative/outer/LEDGER.json'),
                    '--spec', str(work/'cold/derivative/new/SPEC.json'),
                    '--out', str(work/'MODERN-ORDINARY-WITNESS.json')], check=True)
    (work/'RESULT.json').write_text(json.dumps(result, indent=2)+'\n')
    print('PASS_PUBLISHED_CONCENTRATED_PRELIFE_CLAIM', result['kappa_decimal'])


if __name__ == '__main__':
    main()
