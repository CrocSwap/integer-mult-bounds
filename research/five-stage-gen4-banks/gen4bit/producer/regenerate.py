#!/usr/bin/env python3
"""Rebuild gen4bit/selected/bit from the generator and the two physical-layer producers, and compare.

    python3 -B gen4bit/producer/regenerate.py --work /new/scratch/dir      (about 2 minutes)

1. paired_cube_bit_word.py --p 12 (frozen arcs data/arcs_p12.json) writes the virtual word;
2. make_physical.py adds the compensated reuse pairs and late recipient reads;
3. descent.py moves operation frames (PR200 physical-layer rules) and writes the physical word.
The five pinned files must be reproduced exactly (gzip members compared after decompression).
This is provenance only: verify.py admits the pinned files themselves and never runs a producer.
Prepared by DreamingOfClouds with Anthropic Claude assistance; Apache-2.0.
"""
import argparse, gzip, shutil, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BIT = HERE.parent

def main():
    ap = argparse.ArgumentParser(description=__doc__); ap.add_argument('--work', type=Path, required=True)
    a = ap.parse_args(); work = a.work.resolve(); assert not work.exists(), 'work dir must be new'
    raw, phys, pkg, final = work/'raw', work/'phys', work/'pkg', work/'final'
    py = [sys.executable, '-B']
    subprocess.run(py + [str(HERE/'paired_cube_bit_word.py'), '--p', '12', '--out', str(raw)], check=True)
    subprocess.run(py + [str(HERE/'make_physical.py'), '--src', str(raw), '--out', str(phys)], check=True)
    (pkg/'selected').mkdir(parents=True)
    shutil.copytree(BIT/'bit', pkg/'bit'); shutil.copytree(BIT/'references', pkg/'references')
    shutil.copytree(phys, pkg/'selected/bit')
    subprocess.run(py + [str(HERE/'descent.py'), str(pkg), str(final)], check=True)
    pinned = BIT/'selected/bit'
    for name in ('graph_p12.json', 'kchron_p12.json', 'profile_p12.json'):
        assert (final/name).read_bytes() == (pinned/name).read_bytes(), name
    for name in ('word_p12.json.gz', 'frames_p12.json.gz'):
        assert gzip.decompress((final/name).read_bytes()) == gzip.decompress((pinned/name).read_bytes()), name
    print('PASS gen4 regeneration: all five pinned bit-word files reproduced exactly')

if __name__ == '__main__':
    main()
