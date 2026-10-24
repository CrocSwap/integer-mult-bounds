#!/usr/bin/env python3
"""Independent verifier for the BIT ambient quotient. Apache-2.0.

Loads the artifact written by `build.py` and the pinned source word, replays both
with the shipped local-word semantics (`mixed_productive_bit.audit_local`'s
record interpreter), and prices the emitted and quotient invoices with the
two-constraint screen.

It does not import `build.py`.

    python3 -B verify.py
"""
import gzip
import json
import struct
import sys
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT/'research/kappa-rebuild/bit/sources/pr589-regenerated'

PAIRS, HELPERS, AMBIENT = 111, 439, 8
STAGES = 16
ROLES = 2*PAIRS+HELPERS
CALLS, SPLIT = 18, 7
PORTS, BLOCK = 111, 7
TAIL_OFFSET, CUTOFF, TARGET_GAMMA = 0.2, 20.0, 0.97
LOCAL = Counter({1: 1323, 2: 1342, 3: 79, 4: 44, 5: 102, 6: 11, 7: 19})
ADDS, COPIES = 24305, 9


def need(ok, message):
    if not ok:
        raise ValueError(message)


def _rank(rows):
    piv = {}
    for r in [x for x in rows if x]:
        y = r
        for p in sorted(piv, reverse=True):
            if y >> p & 1:
                y ^= piv[p]
        if y:
            piv[y.bit_length()-1] = y
    return len(piv)


def moment(profile, exponent):
    return sum(n*(r**exponent) for r, n in profile.items() if n and r > 0)


def dual_ok(T, P, kappa, u=TAIL_OFFSET, c=CUTOFF, gamma=TARGET_GAMMA):
    t = 1.0-kappa
    return moment(P, t) < moment(T, t) and moment(P, t+u) < gamma*(c**u)*moment(T, t)


def admissible_kappa(T, P, lo=1e-7, hi=0.25, steps=2400):
    best = None
    prev = None
    for i in range(steps+1):
        k = lo+(hi-lo)*i/steps
        if dual_ok(T, P, k):
            best, prev = k, k
        elif prev is not None and best == prev:
            a, b = prev, k
            for _ in range(90):
                mid = (a+b)/2
                if dual_ok(T, P, mid):
                    a = mid
                else:
                    b = mid
            return a
    return best


def rank_mass(profile):
    return sum(r*n for r, n in profile.items())


def invoice(helper_widths, paid_profile):
    targets = Counter({r: CALLS*n for r, n in helper_widths.items()})
    paid = Counter({r: CALLS*n for r, n in paid_profile.items()})
    thin = PORTS*(2*STAGES+1-CALLS)
    paid[1] += thin
    targets[1+BLOCK*(STAGES+2)] += 2*PORTS
    for length in (SPLIT, STAGES-1-SPLIT):
        for j in range(1, length+1):
            targets[1+BLOCK*(j+1)] += 2*PORTS
            paid[BLOCK*(j+1)] += 2*PORTS
    return targets, paid, rank_mass(targets)-rank_mass(paid), thin


def replay(records, start, final, dims, reverse):
    """The shipped record interpreter, minus the emitted-profile assertion."""
    current = list(final if reverse else start)+[-1]
    values = [1 << i for i in range(ROLES)]+[0]
    owned = None
    profile = Counter()
    adds = copies = 0
    for op, x, y, c, f, z in (reversed(records) if reverse else records):
        if op == 0:
            old, new = (c, y) if reverse else (y, c)
            need(current[x] == old, 'MOVE entrance: role %d at frame %d, expected %d'
                 % (x, current[x], old))
            current[x] = new
            if f:
                profile[f] += 1
        elif op == 1:
            need(current[x] == current[y] == f, 'ADD common frame at role %d' % x)
            need(owned is None or x != owned, 'owned source mutated')
            values[x] ^= values[y] if c & 1 else 0
            adds += 1
        elif op == (3 if reverse else 2):
            need(owned is None and y == ROLES and values[ROLES] == 0
                 and current[x] == c, 'COPY entrance')
            owned = x
            current[ROLES] = f
            values[ROLES] = values[x]
            profile[abs(dims[c]-dims[f])] += 1
            copies += 1
        else:
            need(op == (2 if reverse else 3) and owned == x and y == ROLES,
                 'COPY close')
            need(values[ROLES] == values[x], 'copied field exact cleanup')
            values[ROLES], owned = 0, None
    expected = [(1 << i) ^ ((1 << (i-PAIRS)) if PAIRS <= i < 2*PAIRS else 0)
                for i in range(ROLES)]
    need(values == expected+[0], 'arbitrary input columns are not exact')
    need(current[:ROLES] == (start if reverse else final), 'endpoints are not exact')
    need(adds == ADDS and copies == COPIES, 'complete local word')
    return profile, adds, copies


def main():
    with gzip.open(HERE/'QUOTIENT-BIT-WORD.json.gz', 'rt') as handle:
        artifact = json.load(handle)
    kernels = [int(v) for v in artifact['kernel_basis']]
    dims = {int(k): v for k, v in artifact['frame_dims'].items()}
    start, final = artifact['start'], artifact['final']
    records = [tuple(r) for r in artifact['records']]

    need(artifact['ambient_dim'] == AMBIENT, 'ambient is not eight')
    need(len(start) == len(final) == ROLES, 'role count')
    need(1 <= len(kernels) < AMBIENT, 'kernel dimension out of range')
    need(all(0 < k < (1 << AMBIENT) for k in kernels), 'kernel vector out of range')
    need(_rank(kernels) == len(kernels), 'kernel basis is not independent')
    need(artifact['quotient_width'] == AMBIENT - len(kernels),
         'quotient width does not match the kernel dimension')
    need(max(dims.values()) == AMBIENT, 'no frame reaches the full ambient')
    need(all(dims[final[r]] == AMBIENT for r in range(2*PAIRS, ROLES)),
         'a helper final is not D_I8')
    need(all(dims[start[r]] == 0 for r in range(2*PAIRS, ROLES)),
         'a helper start is not ground')

    mains = Counter(dims[final[r]]-dims[start[r]] for r in range(2*PAIRS))
    helpers = Counter(dims[final[r]]-dims[start[r]] for r in range(2*PAIRS, ROLES))
    print('artifact: kernel %s (dim %d), %d frames, %d roles, ambient %d'
          % (kernels, len(kernels), len(dims), ROLES, AMBIENT))
    print('main widths %s ; helper widths %s'
          % (dict(sorted(mains.items())), dict(sorted(helpers.items()))))

    profiles = {}
    for reverse in (False, True):
        profile, adds, copies = replay(records, start, final, dims, reverse)
        profiles[reverse] = profile
        print('%-7s adds %d copies %d paid %s (mass %d)'
              % ('reverse' if reverse else 'forward', adds, copies,
                 dict(sorted(profile.items())), rank_mass(profile)))
    need(profiles[False] == profiles[True], 'directions disagree')

    # Anchor: replaying the pinned source word must reproduce the declared bill.
    source_word = json.load(gzip.open(SOURCE/'WORD.json.gz'))
    source_frames = json.loads((SOURCE/'records/frames.json').read_text())['frames']
    source_dims = {int(k): v['dim'] for k, v in source_frames.items()}
    source_records = list(struct.iter_unpack('<6i', (SOURCE/'records/249-records.bin').read_bytes()))
    emitted = Counter()
    for reverse in (False, True):
        profile, _, _ = replay(list(source_records), source_word['start'],
                               source_word['final'], source_dims, reverse)
        need(profile == LOCAL, 'source word does not reproduce the declared bill')
        emitted = profile
    print('source  paid %s (mass %d)  matches the declared local bill'
          % (dict(sorted(emitted.items())), rank_mass(emitted)))

    quotient = profiles[False]
    t0, p0, s0, thin0 = invoice(dict(helpers), dict(emitted))
    t1, p1, s1, thin1 = invoice(dict(helpers), dict(quotient))
    k0, k1 = admissible_kappa(t0, p0), admissible_kappa(t1, p1)
    need(k0 is not None, 'emitted invoice is not admissible')
    need(k1 is not None and k1 > k0, 'quotient does not improve the screen')
    need(s0 == 48*CALLS-111, 'emitted surplus identity 48*thick-111')
    print()
    print('emitted  surplus %d (thin %d)  BIT kappa %.15f' % (s0, thin0, k0))
    print('quotient surplus %d (thin %d)  BIT kappa %.15f' % (s1, thin1, k1))
    print('gain %+.15f  %+.2f%%' % (k1-k0, 100*(k1/k0-1)))

    result = {
        'package': 'bit-ambient-quotient',
        'status': 'PASS_BIT_AMBIENT_QUOTIENT',
        'kernel_basis': kernels,
        'kernel_dimension': len(kernels),
        'frames': len(dims),
        'roles': ROLES,
        'ambient_dim': AMBIENT,
        'helper_widths': {str(r): n for r, n in sorted(helpers.items())},
        'main_widths': {str(r): n for r, n in sorted(mains.items())},
        'main_rank_mass': rank_mass(mains),
        'emitted_paid': {str(r): n for r, n in sorted(emitted.items())},
        'quotient_paid': {str(r): n for r, n in sorted(quotient.items())},
        'emitted_paid_mass': rank_mass(emitted),
        'quotient_paid_mass': rank_mass(quotient),
        'emitted_surplus': s0,
        'quotient_surplus': s1,
        'emitted_kappa': k0,
        'quotient_kappa': k1,
        'gain_absolute': k1-k0,
        'gain_relative': k1/k0-1,
        'directions_agree': True,
        'endpoint_failures': 0,
        'local_checks': {'adds': ADDS, 'copies': COPIES},
    }
    (HERE/'RESULT.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print('wrote RESULT.json')


if __name__ == '__main__':
    main()
