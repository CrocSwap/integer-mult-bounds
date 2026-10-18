#!/usr/bin/env python3
"""Unregistered evidence for the README's (G)/(D) observation, standard library only: for every P105 unit, run
verify.criterion on each live frame that precedes its pivot in frame order and tally the failure reasons.

    python3 -I -B research/complex-rank8-rigidity-p105/tally_earlier.py [--jobs N]

Expected (a few seconds): first live frame passes 230560; at most 20 failures before a pivot;
reasons W 17210, nonempty-blocks 219. No frame preceding a pivot fails (G) or (D), so in every unit the first live
frame passing (W) and nonempty blocks also passes (G) and (D).
"""
import argparse
import collections
import gzip
import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify as V  # noqa: E402


def earlier(u):
    X, p = u[:7], u[7]
    xm = V.F0MASK | sum(1 << i for i in X)
    return [V.criterion(X, V.FRAMES[n])[0] for n in range(p) if not V.FMASK[n] & xm]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--jobs', type=int, default=os.cpu_count() or 1)
    args = ap.parse_args()
    units = json.loads(gzip.decompress(V.UNITS_FILE.read_bytes()))['p105']
    tally, first, most = collections.Counter(), 0, 0
    with ProcessPoolExecutor(args.jobs) as ex:
        for r in ex.map(earlier, units, chunksize=512):
            tally.update(r)
            first += not r
            most = max(most, len(r))
    print(f'units {len(units)}; first live frame passes {first}; at most {most} failures before a pivot; '
          f'reasons {dict(sorted(tally.items(), key=lambda kv: str(kv[0])))}')


if __name__ == '__main__':
    main()
