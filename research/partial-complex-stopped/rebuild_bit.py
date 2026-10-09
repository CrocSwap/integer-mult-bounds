"""Bind and reconstruct the whole-projector bit inventory from pinned round seven.

This reconstructs the finite histogram. The source's stated stage-two reversal
and the all-size projector/streaming transfer are separate written premises.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root', type=Path, required=True)
    args = parser.parse_args()
    if sys.flags.optimize:
        raise RuntimeError('Run without -O: assertions must remain enabled')
    here = Path(__file__).resolve().parent
    root = args.source_root.resolve()
    manifest = json.loads((here/'SWAPNIL_SOURCE.json').read_text())
    pin = '741e7aa078392553815df7926ee17ac5e25a8c38'
    assert manifest['commit'] == pin
    assert subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD'],
                                   text=True).strip() == pin
    for name, digest in manifest['tracked_files'].items():
        assert hashlib.sha256((root/name).read_bytes()).hexdigest() == digest, name
    sys.path[:0] = [str(root/'scripts'), str(root/'independent/deferred-readout'),
                   str(root/'independent/two-stage-bit')]
    import certificate_round7 as r7
    import deferred as dr
    S, rk, yl, xd = r7.build()
    old = dr.histogram(S, rk, yl, xd, dr.STAIRCASE_CORNER(S.h))
    h, m, v, N = S.h, old['m'], S.v, old['N']
    hist = Counter()
    for u in range(S.R):
        hist[m-h+S.f[u]] += 2*v
    for rank, count in rk.items():
        if rank:
            hist[rank] += 2*v*count
    hist[h-1] += 2*v*h
    for target in range(v):
        ds = sorted(set([0, *yl[target], h-1]))
        for a, b in zip(ds, ds[1:]):
            if b > a:
                hist[b-a] += 2*v
    for chain in xd:
        for rank in chain:
            if rank:
                hist[rank] += 2*v
    hist[(h-1)**2] += 2*N
    hist[1] += N  # mandatory copied-output correction
    expected = json.loads((here/'inputs/bit.json').read_text())
    assert dict(hist) == {int(r): int(n) for r, n in expected['histogram'].items()}
    assert sum(r*n for r, n in hist.items()) == old['s'] == expected['rank_sum']
    assert (h, m, v, N, S.R, old['W']) == (23, 529, 1771, 3136441, 28866, 108516254)
    assert all(0 < r < m and n > 0 for r, n in hist.items())
    assert max(hist) == 528 and len(hist) == 46
    print(f'PASS {len(manifest["tracked_files"])} pinned files; '
          '46 whole-projector bins, exact rank sum, all paid endpoint copies')


if __name__ == '__main__':
    main()
