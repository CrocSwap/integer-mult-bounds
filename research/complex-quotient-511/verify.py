#!/usr/bin/env python3
"""Independent verification of the rank-8 quotient supplier. Apache-2.0.

Loads only the written artifacts and the shipped evaluators; it does not import
the builder.  Checks

  1. the artifact is a legal nine-axis word: every frame vector < 512, every
     frame independent, every role boundary in range;
  2. `synthesize` accepts both directions;
  3. the shipped literal replay returns every one of the 632 endpoints exactly
     (`verify_buffers.expected`) with the owned C field cleared;
  4. forward and backward paid profiles agree;
  5. the invoice, with the quotient's own helper and paid profiles and the
     frontier's block-8 ladder, and the two-constraint screen;
  6. the emitted word prices at the declared frontier kappa and the quotient
     strictly above it.

    python3 -B verify.py
"""
import gzip
import json
import sys
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT/'research/fresh-helper-boundary'))

import native as F  # noqa: E402

TAIL_OFFSET, CUTOFF, TARGET_GAMMA = 0.2, 20.0, 0.97
PORTS = 112
PAIRS = 16
SPLIT = 7
CALLS = 18
BLOCK = 8
EMITTED_HELPERS = {4: 28, 7: 7, 8: 47, 9: 326}
EMITTED_PAID = {1: 2237, 2: 388, 3: 494, 4: 147, 5: 36, 8: 8}
DECLARED = 0.00302015
ROLES = 632


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load(path, name):
    import importlib.util
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


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


def crossing_of(T, P, u=TAIL_OFFSET, c=CUTOFF, gamma=TARGET_GAMMA):
    k = admissible_kappa(T, P)
    t = 1.0-k
    alpha = moment(P, t)/moment(T, t)
    gam = moment(P, t+u)/((c**u)*moment(T, t))
    return {'kappa': k, 'alpha': alpha, 'gamma': gam,
            'alpha_slack': 1.0-alpha, 'gamma_slack': gamma-gam}


def rank_mass(profile):
    return sum(r*n for r, n in profile.items())


def invoice(helper_profile, paid_profile, block=BLOCK, p=PAIRS, split=SPLIT, calls=CALLS):
    targets = Counter({r: calls*n for r, n in helper_profile.items()})
    paid = Counter({r: calls*n for r, n in paid_profile.items()})
    thin = PORTS*(2*p+1-calls)
    paid[1] += thin
    targets[1+block*(p+2)] += 2*PORTS
    for length in (split, p-1-split):
        for j in range(1, length+1):
            targets[1+block*(j+1)] += 2*PORTS
            paid[block*(j+1)] += 2*PORTS
    surplus = rank_mass(targets)-rank_mass(paid)
    return targets, paid, surplus, thin


def main():
    with gzip.open(HERE/'QUOTIENT-WORD.json.gz', 'rt') as handle:
        word = json.load(handle)
    with gzip.open(HERE/'QUOTIENT-PROGRAMS.json.gz', 'rt') as handle:
        programs_raw = json.load(handle)

    frames, start, final = word['frames'], word['start'], word['final']
    need(len(start) == ROLES == len(final), 'role count')
    need(len(frames) > 0, 'no frames')
    peak = max((v for basis in frames for v in basis), default=0)
    need(peak < 512, 'quotient word left the nine-axis ambient: %d' % peak)
    for i, basis in enumerate(frames):
        need(len(F.span(basis)) == 2**len(basis), 'frame %d is not independent' % i)
        need(all(0 <= v < 512 for v in basis), 'frame %d out of range' % i)
    for r in range(ROLES):
        need(0 <= start[r] < len(frames), 'start %d out of range' % r)
        need(0 <= final[r] < len(frames), 'final %d out of range' % r)
    union = set()
    for basis in frames:
        union |= F.span(basis)
    ambient = len(union).bit_length()-1
    need(ambient == BLOCK+1,
         'ambient is dim %d, so the block-8 charge would be invalid' % ambient)
    print('artifact: %d frames, %d roles, peak vector %d, max frame dim %d' % (
        len(frames), ROLES, peak, max(len(b) for b in frames)))
    print('ambient dim %d = 1 + block %d  (the ladder charge is consistent)' % (
        ambient, BLOCK))

    ranks = [len(b) for b in frames]
    mains = [ranks[final[r]]-ranks[start[r]] for r in range(224)]
    helpers = Counter(ranks[final[r]]-ranks[start[r]] for r in range(224, ROLES))
    print('main widths %s ; main rank mass %d' % (
        dict(sorted(Counter(mains).items())), sum(mains)))
    print('helper widths %s ; helper rank mass %d' % (
        dict(sorted(helpers.items())), rank_mass(helpers)))

    V = F.load(ROOT/'research/kappa-causal-continuation/buffer-borrowing/verify_buffers.py', 'joint_rows')
    X = F.load(ROOT/'research/kappa-rebuild/complex/native_extensions.py', 'joint_literal')

    results = {}
    for direction in ('forward', 'backward'):
        program = [list(e) for e in programs_raw[direction]]
        synthesized = F.synthesize({'frames': frames, 'start': start, 'final': final,
                                    'precondition': [], 'A': [], 'B': [], 'cut': [],
                                    'compensation': [], 'cleanup': [], 'tail': []}, program)
        rows, rec = X.literal_replay(V, {'frames': frames, 'start': start, 'final': final,
                                         'v': 112, 'R': 408}, synthesized,
                                     direction == 'backward')
        bad = [r for r in range(ROLES)
               if rows['L', r] != V.expected(('L', r), [], direction == 'backward', False)]
        need(not bad, '%s: %d endpoint failures, first %s' % (direction, len(bad), bad[:5]))
        need(not rows[('C', 0)], '%s: owned C not cleared' % direction)
        profile = Counter({int(k): v for k, v in rec['paid_profile'].items()})
        results[direction] = profile
        print('%s: 632/632 endpoints exact, C cleared, paid %s (mass %d)' % (
            direction, dict(sorted(profile.items())), rank_mass(profile)))

    need(results['forward'] == results['backward'], 'directions disagree')
    paid = results['forward']
    deficit = rank_mass(paid)-rank_mass(helpers)
    print('local deficit %d (emitted 1856)' % deficit)

    t0, p0, s0, thin0 = invoice(EMITTED_HELPERS, EMITTED_PAID)
    k0 = admissible_kappa(t0, p0)
    t1, p1, s1, thin1 = invoice(dict(helpers), dict(paid))
    k1 = admissible_kappa(t1, p1)
    print()
    print('emitted : surplus %d (thin %d)  kappa %.12f' % (s0, thin0, k0))
    print('quotient: surplus %d (thin %d)  kappa %.12f' % (s1, thin1, k1))
    need(abs(k0-DECLARED) < 2e-7, 'emitted word does not reproduce the declared kappa')
    need(k1 and k1 > k0, 'quotient does not improve kappa')
    crossing = crossing_of(t1, p1)
    print('quotient constraints: alpha slack %.3e ; gamma slack %.4f' % (
        crossing['alpha_slack'], crossing['gamma_slack']))

    result = {'construction': word['map'], 'kernel_vector': word['kernel_vector'],
              'frames': len(frames), 'peak_vector': peak, 'ambient_dim': ambient,
              'main_widths': dict(sorted(Counter(mains).items())),
              'main_rank_mass': sum(mains),
              'helper_widths': dict(sorted(helpers.items())),
              'helper_rank_mass': rank_mass(helpers),
              'paid_profile': dict(sorted(paid.items())),
              'paid_rank_mass': rank_mass(paid),
              'local_deficit': deficit,
              'directions_agree': True, 'endpoint_failures': 0,
              'surplus_emitted': s0, 'surplus_quotient': s1,
              'kappa_emitted': k0, 'kappa_quotient': k1,
              'kappa_declared': DECLARED,
              'gain_absolute': k1-k0, 'gain_relative': k1/k0-1.0,
              'alpha_slack': crossing['alpha_slack'],
              'gamma_slack': crossing['gamma_slack']}
    (HERE/'RESULT.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print()
    print('gain %+.9f  %+.1f%%' % (k1-k0, 100*(k1/k0-1)))
    print('wrote RESULT.json')


if __name__ == '__main__':
    main()
