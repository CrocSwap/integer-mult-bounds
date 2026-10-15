#!/usr/bin/env python3
"""Bounded portable checks; complete cold native/global/outer replay is separate.
Marius-Paul Dumitrean with substantial OpenAI Codex assistance. Apache-2.0.
"""
import importlib.util
import subprocess
import sys
import tempfile
from pathlib import Path

import generate


def main():
    generate.need(__debug__, 'Assertions are required; run without optimized Python')
    here = Path(__file__).resolve().parent
    with tempfile.TemporaryDirectory(prefix='concentrated-prelife-refit-') as folder:
        work = Path(folder)
        manifest = generate.generate(work/'construction')
        generate.need(set(manifest) == set(generate.read(here/'expected/MANIFEST.json')),
                      'Complete regenerated artifact set')
        for name in manifest:
            generate.need(generate.read(work/'construction'/name) ==
                          generate.read(here/'expected'/name), 'Complete generated payload '+name)
        subprocess.run([sys.executable, '-B', str(here/'verify_refit.py'),
                        '--out', str(work/'WORDS.json')], check=True)
        spec = importlib.util.spec_from_file_location('refit_exact_price', generate.PARENT/'vendor/price.py')
        price = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(price)
        result = price.price(generate.read(here/'expected/PROFILE.json'))
        generate.need(result == generate.read(here/'evidence/EXACT-PRICE.json'),
                      'Exact endpoint and outward moment certificates')
        subprocess.run([sys.executable, '-B', str(here/'ceiling/check.py'),
                        '--work', str(work/'ceiling')], check=True)
        subprocess.run([sys.executable, '-B', str(here/'check_admission.py')], check=True)
    print('PASS_REGISTERED_REFIT_CONSTRUCTION_INDEPENDENT_WORDS_PRICE_CEILING_AND_ADMISSION_BINDINGS')


if __name__ == '__main__':
    main()
