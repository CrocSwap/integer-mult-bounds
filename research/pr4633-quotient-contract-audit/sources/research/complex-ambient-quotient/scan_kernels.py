#!/usr/bin/env python3
"""Price every one-dimensional quotient kernel of the complex supplier.

`phi` in `build.py` quotients the nine-axis ambient by span{KERNEL}.  Which
kernel to use is not a free choice: a kernel that shrinks the mains can also
collapse a frame some gate needs distinct from its neighbour, and that word does
not replay.  This scan builds, repairs and replays all 511 directions and prices
each with the same invoice as `verify.py`.

The scan is what selects KERNEL = 153: it is the replay-valid direction with the
highest admissible kappa.

    python3 -B scan_kernels.py

Apache-2.0; substantial AI assistance.
"""
import importlib.util
import sys
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROLES = 632
MAINS = 224

_state = {}


def setup():
    spec = importlib.util.spec_from_file_location('build', HERE/'build.py')
    build = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(build)
    patch = build.F.read(build.JOINT/'PATCH.json')
    word, programs, _, _, _ = build.construct(patch, return_raw=True)
    vspec = importlib.util.spec_from_file_location('verify', HERE/'verify.py')
    verify = importlib.util.module_from_spec(vspec)
    vspec.loader.exec_module(verify)
    _state.update(build=build, verify=verify, word=word, programs=programs)


def phi_for(kernel):
    pivot = (kernel & -kernel).bit_length()-1

    def phi(v):
        if (v >> pivot) & 1:
            v ^= kernel
        low = v & ((1 << pivot) - 1)
        return low | ((v >> (pivot + 1)) << pivot)
    return phi


def price(kernel):
    build, verify = _state['build'], _state['verify']
    word, programs = _state['word'], _state['programs']
    try:
        build.phi = phi_for(kernel)
        quot, moves, _ = build.quotient(word, programs)
        _, full_frame = build.repad_helpers(quot)
        moves = build.renumber_full_ambient(quot, moves, full_frame)
        ext = verify.load(verify.ROOT/'research/kappa-rebuild/complex/native_extensions.py',
                          'scan_ext_%d' % kernel)
        ext.embedded_cache_roles({'frames': quot['frames'], 'start': quot['start'],
                                  'final': quot['final'], 'v': 112, 'R': 408})
        rows_mod = verify.load(verify.ROOT/'research/kappa-causal-continuation/'
                               'buffer-borrowing/verify_buffers.py',
                               'scan_rows_%d' % kernel)
        blank = {'frames': quot['frames'], 'start': quot['start'],
                 'final': quot['final'], 'precondition': [], 'A': [], 'B': [],
                 'cut': [], 'compensation': [], 'cleanup': [], 'tail': []}
        profiles = {}
        for direction in ('forward', 'backward'):
            synthesized = build.F.synthesize(blank, [list(e) for e in moves[direction]])
            rows, rec = ext.literal_replay(rows_mod,
                                           {'frames': quot['frames'],
                                            'start': quot['start'],
                                            'final': quot['final'],
                                            'v': 112, 'R': 408}, synthesized,
                                           direction == 'backward')
            exact = all(rows['L', r] == rows_mod.expected(('L', r), [],
                                                          direction == 'backward', False)
                        for r in range(ROLES))
            if not exact or rows[('C', 0)]:
                return kernel, 'replay-fail', 0, 0, 0.0
            profiles[direction] = Counter({int(k): v for k, v in
                                           rec['paid_profile'].items()})
        if profiles['forward'] != profiles['backward']:
            return kernel, 'directions-disagree', 0, 0, 0.0
        ranks = [len(b) for b in quot['frames']]
        mains = sum(ranks[quot['final'][r]]-ranks[quot['start'][r]]
                    for r in range(MAINS))
        helpers = Counter(ranks[quot['final'][r]]-ranks[quot['start'][r]]
                          for r in range(MAINS, ROLES))
        targets, paid, surplus, _ = verify.invoice(dict(helpers),
                                                   dict(profiles['forward']))
        kappa = verify.admissible_kappa(targets, paid)
        return kernel, 'ok', mains, surplus, kappa or 0.0
    except Exception as exc:
        return kernel, type(exc).__name__, 0, 0, 0.0


def main():
    setup()
    build = _state['build']
    word = _state['word']
    frames = word['frames']

    def mass(kernel):
        phi = phi_for(kernel)
        dim = {i: len(build.span_of(build.dedupe([phi(x) for x in b]))).bit_length()-1
               for i, b in enumerate(frames)}
        return sum(dim[word['final'][r]]-dim[word['start'][r]] for r in range(MAINS))

    kernels = list(range(1, 512))
    print('pricing %d kernels across 8 workers ...' % len(kernels), flush=True)
    valid = []
    with Pool(8, initializer=setup) as pool:
        for done, result in enumerate(pool.imap_unordered(price, kernels), 1):
            kernel, status, m, surplus, kappa = result
            if status == 'ok':
                valid.append((kappa, kernel, m, surplus))
            if done % 64 == 0:
                top = max(valid) if valid else None
                print('  %d/%d valid %d best %s' % (
                    done, len(kernels), len(valid),
                    'kernel %d kappa %.12f' % (top[1], top[0]) if top else '-'),
                    flush=True)
    valid.sort(reverse=True)
    print()
    print('replay-valid kernels: %d of %d' % (len(valid), len(kernels)))
    print('best 10 by admissible kappa:')
    for kappa, kernel, m, surplus in valid[:10]:
        print('   kernel %3d  main mass %4d  surplus %5d  kappa %.12f'
              % (kernel, m, surplus, kappa))


if __name__ == '__main__':
    main()
