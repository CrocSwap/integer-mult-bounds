#!/usr/bin/env python3
"""Rebuild PR56 and certify its enlarged-frame profiles with enough primes.

RaD's exact profiler supplies integer minor bounds, unlike the diagnostic
three-prime profiler. Requires C++17 and Boost multiprecision headers.
"""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import shlex
import subprocess

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT/'research/positive-skip'


def run(work):
    work.mkdir(parents=True,exist_ok=True)
    spec = importlib.util.spec_from_file_location('positive_skip_rebuild',HERE/'build.py')
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    rebuilt = module.run(work)
    exe = work/'exact-profiles'
    subprocess.run([*shlex.split(os.environ.get('CXX','c++')),'-O3','-std=c++17','-I',str(ROOT/'scripts/partial_swap'),str(HERE/'pr51/positive_frame_profiles.cpp'),'-o',str(exe)],check=True)
    for h in (23,25):
        final = work/f'h{h}-clone-{len(rebuilt[str(h)]["rounds"])}/dag.bin'
        output = work/f'exact-{h}.json'
        subprocess.run([str(exe),str(final),str(HERE/f'links-{h}.uses'),'fixed',str(output)],check=True)
        actual = json.loads(output.read_text())
        expected = json.loads((HERE/f'profiles-{h}.json').read_text())
        if actual['blocks'] != expected['blocks'] or actual['R'] != expected['R']:
            raise ValueError('Exact positive-frame profile differs from certificate')
        if actual['prime_product_bits'] <= actual['maximum_minor_bound_bits']:
            raise ValueError('Insufficient prime product')
        print(f'PASS h={h}: exact enlarged-frame profile, {len(actual["primes"])} primes',flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work-dir',type=Path,default=ROOT/'build/positive-skip-exact')
    run(parser.parse_args().work_dir.resolve())
