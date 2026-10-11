#!/usr/bin/env python3
"""Rebuild bitword/selected/bit from the generator and the two physical-layer producers, and compare.

    python3 -B bitword/producer/regenerate.py --work /new/scratch/dir                 (about 2 minutes)
    python3 -B bitword/producer/regenerate.py --work /new/dir --solve-matching --emit /new/out/dir

1. paired_cube_bit_word.py --p 10 (frozen arcs data/arcs_p10.json) writes the virtual word;
2. make_physical.py --bank-parity adds the compensated reuse pairs and late recipient reads (recipients are
   rank h - 3 = 17 gauges; trailing pairs are dropped until the 60-replica bank width is a multiple of m = 100);
3. descent.py moves operation frames (PR200 physical-layer rules, cost r*ln(100/r)) and writes the physical word.
The five pinned files must be reproduced exactly (gzip members compared after decompression).
This is provenance only: verify.py admits the pinned files themselves and never runs a producer.

Re-pinning (new module data): --solve-matching runs the generator on a scratch copy of this producer directory,
first to recompute and freeze the carrier matching, then on the frozen arcs (the package is never written), and
--emit writes the five new selected files and the new frozen arcs_p10.json to a new directory instead of
comparing. See discovery/REPIN.md.
Prepared by DreamingOfClouds with Anthropic Claude assistance; Apache-2.0.
"""
import argparse, gzip, shutil, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BIT = HERE.parent
P = 10
NAMES = ['graph_p%d.json' % P, 'kchron_p%d.json' % P, 'profile_p%d.json' % P]
GZ = ['word_p%d.json.gz' % P, 'frames_p%d.json.gz' % P]


def main():
    ap = argparse.ArgumentParser(description=__doc__); ap.add_argument('--work', type=Path, required=True)
    ap.add_argument('--solve-matching', action='store_true', help='recompute the carrier matching on a scratch copy')
    ap.add_argument('--emit', type=Path, help='write the new selected files and arcs here instead of comparing')
    a = ap.parse_args(); work = a.work.resolve(); assert not work.exists(), 'work dir must be new'
    assert a.emit is None or not a.emit.exists(), 'emit dir must be new'
    assert a.emit is not None or not a.solve_matching, '--solve-matching is for re-pinning; use it with --emit'
    raw, phys, pkg, final = work/'raw', work/'phys', work/'pkg', work/'final'
    py = [sys.executable, '-B']
    producer = HERE   # only the generator runs from a scratch copy when the matching is re-solved
    if a.solve_matching:
        producer = work/'producer'; shutil.copytree(HERE, producer)
        (producer/'data'/('arcs_p%d.json' % P)).unlink(missing_ok=True)
        # first run: solve the carrier matching and freeze it in the scratch copy's data/arcs_pP.json
        subprocess.run(py + [str(producer/'paired_cube_bit_word.py'), '--p', str(P), '--out', str(work/'solve')], check=True)
    # the pinned word is always the frozen-arc compile (frame ids follow the frozen arc order)
    subprocess.run(py + [str(producer/'paired_cube_bit_word.py'), '--p', str(P), '--out', str(raw)], check=True)
    subprocess.run(py + [str(HERE/'make_physical.py'), '--src', str(raw), '--out', str(phys), '--bank-parity'], check=True)
    (pkg/'selected').mkdir(parents=True)
    shutil.copytree(BIT/'bit', pkg/'bit'); shutil.copytree(BIT/'references', pkg/'references')
    shutil.copytree(phys, pkg/'selected/bit')
    subprocess.run(py + [str(HERE/'descent.py'), str(pkg), str(final)], check=True)
    if a.emit is not None:
        out = a.emit.resolve(); (out/'selected').mkdir(parents=True)
        for name in NAMES + GZ:
            shutil.copyfile(final/name, out/'selected'/name)
        shutil.copyfile(producer/'data'/('arcs_p%d.json' % P), out/('arcs_p%d.json' % P))
        print('EMITTED new p=%d bit word to %s (selected/ and arcs_p%d.json); nothing compared' % (P, out, P))
        return
    pinned = BIT/'selected/bit'
    assert sorted(x.name for x in pinned.iterdir()) == sorted(NAMES + GZ), 'pinned file set'
    for name in NAMES:
        assert (final/name).read_bytes() == (pinned/name).read_bytes(), name
    for name in GZ:
        assert gzip.decompress((final/name).read_bytes()) == gzip.decompress((pinned/name).read_bytes()), name
    print('PASS p=%d regeneration: all five pinned bit-word files reproduced exactly' % P)

if __name__ == '__main__':
    main()
