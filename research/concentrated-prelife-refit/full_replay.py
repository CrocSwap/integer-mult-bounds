#!/usr/bin/env python3
"""Complete fresh native/global/outer replay of the single-gate frame refit.
Marius-Paul Dumitrean with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from fractions import Fraction
import json
from pathlib import Path
import subprocess
import sys

import generate
import replay_engine

HERE = Path(__file__).resolve().parent


def main():
    generate.need(__debug__, 'Assertions are required; run without optimized Python')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work', type=Path, required=True)
    args = parser.parse_args()
    work = args.work.resolve()
    packages = [HERE, generate.PARENT, generate.SOURCE,
                HERE.parent/'t74-concentrated-source-partners']
    generate.need(not work.exists() and not any(work.is_relative_to(p.resolve())
                  for p in packages), 'Use fresh output outside all source packages')
    work.mkdir(parents=True)
    manifest = generate.generate(work/'construction')
    expected = HERE/'expected'
    generate.need(set(manifest) == set(generate.read(expected/'MANIFEST.json')),
                  'Complete regenerated file set')
    for name in manifest:
        generate.need(generate.read(work/'construction'/name) == generate.read(expected/name),
                      'Complete regenerated payload '+name)
    sys.argv = [sys.argv[0], '--source', str(generate.SOURCE),
                '--source2696', str(packages[3]), '--candidate', str(expected),
                '--fill', str(expected/'FILL.json.gz'),
                '--order', str(expected/'ORDER.json'), '--work', str(work/'cold'),
                '--jobs', '1']
    replay_engine.main()
    result = generate.read(work/'cold/RESULT.json')
    old = generate.read(generate.PARENT/'CLAIM.json')
    generate.need(Fraction(result['kappa']) > Fraction(old['kappa']), 'Strict gain over PR2733')
    subprocess.run([sys.executable, '-B', str(generate.PARENT/'ordinary_witness.py'),
                    '--ledger', str(work/'cold/derivative/outer/LEDGER.json'),
                    '--spec', str(work/'cold/derivative/new/SPEC.json'),
                    '--out', str(work/'MODERN-ORDINARY-WITNESS.json')], check=True)
    result['public_wrapper_sha256'] = generate.sha(Path(__file__))
    result['ordinary_receipt_sha256'] = generate.sha(work/'MODERN-ORDINARY-WITNESS.json')
    (work/'RESULT.json').write_text(json.dumps(result, indent=2)+'\n')
    print('PASS_PUBLIC_COMPLETE_FRESH_REFIT_REPLAY', result['kappa_decimal'])


if __name__ == '__main__':
    main()
