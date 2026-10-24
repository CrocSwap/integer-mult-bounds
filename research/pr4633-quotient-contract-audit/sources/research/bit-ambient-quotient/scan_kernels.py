#!/usr/bin/env python3
"""Price every one-dimensional ambient quotient of the BIT local word. Apache-2.0.

`build.build(kernel)` rebuilds the word for a kernel and `verify.replay` runs the
shipped local record interpreter on it, so every candidate here is a replayed
word rather than an arithmetic estimate.  The scan selects `255`.

    python3 -B scan_kernels.py
"""
import importlib.util
import sys
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent


def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE/(name+'.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


B = load('build')
VV = load('verify')


def price(kernel):
    try:
        artifact = B.build(kernel)
        dims = {int(k): v for k, v in artifact['frame_dims'].items()}
        start, final = artifact['start'], artifact['final']
        records = [tuple(r) for r in artifact['records']]
        profiles = {}
        for reverse in (False, True):
            profile, _, _ = VV.replay(records, start, final, dims, reverse)
            profiles[reverse] = profile
        if profiles[False] != profiles[True]:
            return kernel, 'directions-disagree', 0, 0.0
        helpers = Counter({8: 439})
        targets, paid, surplus, _ = VV.invoice(dict(helpers), dict(profiles[False]))
        kappa = VV.admissible_kappa(targets, paid)
        return kernel, 'ok', surplus, kappa or 0.0
    except Exception as exc:
        return kernel, type(exc).__name__, 0, 0.0


def main():
    kernels = list(range(1, 256))
    print('pricing %d kernels across 8 workers ...' % len(kernels), flush=True)
    rows = []
    with Pool(8) as pool:
        for done, (kernel, status, surplus, kappa) in enumerate(
                pool.imap_unordered(price, kernels), 1):
            if status == 'ok':
                rows.append((kappa, kernel, surplus))
            if done % 32 == 0:
                top = max(rows) if rows else None
                print('  %d/%d valid %d best %s' % (
                    done, len(kernels), len(rows),
                    'kernel %d kappa %.12f' % (top[1], top[0]) if top else '-'),
                    flush=True)
    rows.sort(reverse=True)
    print()
    print('replay-valid kernels: %d of %d' % (len(rows), len(kernels)))
    print('best 10 by admissible kappa:')
    for kappa, kernel, surplus in rows[:10]:
        print('   kernel %3d  surplus %5d  kappa %.12f' % (kernel, surplus, kappa))


if __name__ == '__main__':
    main()
