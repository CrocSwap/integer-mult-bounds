#!/usr/bin/env python3
"""Price kernel quotients of the BIT local word by dimension. Apache-2.0.

`build.build(kernels)` rebuilds the word for a kernel subspace and `verify.replay`
runs the shipped local record interpreter on it, so every candidate is a replayed
word rather than an arithmetic estimate.  One dimension reaches 0.0124, two 0.0218,
three 0.0322; four falls back to 0.0175.  Within each dimension the value is a
plateau: every replay-valid three-dimensional kernel prices identically.

    python3 -B scan_kernels.py
"""
import importlib.util
import itertools
import random
import sys
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent


def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE/(name+'.py'))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


B = load('build')
VV = load('verify')


def price(kernels):
    try:
        artifact = B.build(kernels)
    except Exception as exc:
        return kernels, type(exc).__name__, 0, 0.0, 0
    dims = {int(k): v for k, v in artifact['frame_dims'].items()}
    start, final = artifact['start'], artifact['final']
    records = [tuple(r) for r in artifact['records']]
    try:
        profiles = {}
        for reverse in (False, True):
            profile, _, _ = VV.replay(records, start, final, dims, reverse)
            profiles[reverse] = profile
        if profiles[False] != profiles[True]:
            return kernels, 'directions-disagree', 0, 0.0, 0
        helpers = Counter({8: 439})
        targets, paid, surplus, _ = VV.invoice(dict(helpers), dict(profiles[False]))
        kappa = VV.admissible_kappa(targets, paid)
        return kernels, 'ok', surplus, kappa or 0.0, artifact['frames']
    except Exception as exc:
        return kernels, type(exc).__name__, 0, 0.0, 0


def main():
    axes = [150, 102, 255, 153, 15, 240, 105, 1, 7, 9, 165, 170, 204, 90, 60]
    candidates = []
    for k in (1, 2, 3, 4):
        candidates += [list(c) for c in itertools.combinations(axes, k)]
    random.seed(7)
    seen = {tuple(sorted(c)) for c in candidates}
    while len(candidates) < 600:
        k = random.choice((2, 3))
        c = sorted(random.sample(range(1, 256), k))
        if tuple(c) not in seen:
            seen.add(tuple(c))
            candidates.append(c)
    print('pricing %d kernel subspaces across 8 workers ...' % len(candidates), flush=True)
    best = {}
    valid = 0
    with Pool(8) as pool:
        for done, (kb, status, surplus, kappa, frames) in enumerate(
                pool.imap_unordered(price, candidates), 1):
            if status == 'ok':
                valid += 1
                cur = best.get(len(kb))
                if cur is None or kappa > cur[0]:
                    best[len(kb)] = (kappa, kb, surplus, frames)
            if done % 100 == 0:
                print('  %d/%d valid %d' % (done, len(candidates), valid), flush=True)
    print()
    print('replay-valid: %d of %d' % (valid, len(candidates)))
    print('best by kernel dimension:')
    for k in sorted(best):
        kappa, kb, surplus, frames = best[k]
        print('   dim %d  kernel %-18s frames %3d  surplus %5d  kappa %.12f'
              % (k, str(kb), frames, surplus, kappa))


if __name__ == '__main__':
    main()
