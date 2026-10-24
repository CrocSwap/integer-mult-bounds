#!/usr/bin/env python3
"""Classify the ambient-quotient kernels of the PR #4596 word.

Default run (about 30 s):
  1. reads the centre transports of the pinned base word (ground <-> dim-8
     frame, charged rank 8) and checks that the eight frames they reach are
     hyperplanes of F2^9 with the declared normals;
  2. checks that the normals have GF(2) rank 4, so the directions outside all
     eight hyperplanes form a coset of a 5-dimensional subspace with 32 points;
  3. checks that this coset meets its own difference subspace nowhere, so no
     2-dimensional kernel has all three nonzero vectors outside the hyperplanes;
  4. replays every one of the 32 predicted directions with the shipped literal
     replay (both orientations, 632/632 endpoints, owned C cleared) and checks
     the declared profiles and prices for v = 153 and v = 511;
  5. replays rejection controls, which must fail the shipped paid-rank check;
  6. checks that 511 is the only direction outside all 112 dim-8 main finals.

Options:
  --scan LO HI     replay every direction LO <= v <= HI and require that the
                   shipped replay accepts exactly the predicted directions
  --physical V     lower every realised transport of the v = V word exactly and
                   require Fourier rank = |dim difference| (the shipped convention)

Exit status is non-zero on any mismatch.
"""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import quotient as Q  # noqa: E402

F = Q.F
ROOT = Q.ROOT
NORMALS = [42, 7, 25, 52, 82, 127, 97, 76]
PREDICTED = [7, 25, 42, 52, 76, 82, 97, 127, 135, 153, 170, 180, 204, 210, 225, 255,
             263, 281, 298, 308, 332, 338, 353, 383, 391, 409, 426, 436, 460, 466, 481, 511]
DECLARED = {
    153: {'main_widths': {7: 168, 8: 56},
          'helper_widths': {3: 2, 4: 26, 6: 7, 7: 47, 8: 325, 9: 1},
          'paid_profile': {1: 1991, 2: 424, 3: 389, 4: 147, 5: 24, 8: 8},
          'paid_rank_mass': 4778, 'helper_rank_mass': 3090, 'local_deficit': 1688,
          'surplus': 3776, 'thin': 1680, 'kappa': 0.016567169219161848},
    511: {'main_widths': {7: 112, 8: 112},
          'helper_widths': {3: 2, 4: 26, 6: 7, 7: 47, 8: 325, 9: 1},
          'paid_profile': {1: 2034, 2: 382, 3: 412, 4: 139, 5: 36, 8: 8},
          'paid_rank_mass': 4834, 'helper_rank_mass': 3090, 'local_deficit': 1744,
          'surplus': 2768, 'thin': 1680, 'kappa': 0.012091850233828692},
}
WIDENED_HELPERS = [7, 52, 82, 97, 391, 436, 466, 481]
REJECTED_CONTROLS = [1, 2, 256, 510]
PAID_RANK_REASON = 'replay:Paid rank and source frame'


def need(ok, message):
    if not ok:
        raise SystemExit('FAIL: ' + message)


def parity(a, b):
    return bin(a & b).count('1') & 1


def gf2_rank(vectors):
    pivots = []
    for v in vectors:
        for p in pivots:
            v = min(v, v ^ p)
        if v:
            pivots.append(v)
    return len(pivots)


def evaluators():
    V = F.load(ROOT/'research/kappa-causal-continuation/buffer-borrowing/verify_buffers.py', 'qkf_rows')
    X = F.load(ROOT/'research/kappa-rebuild/complex/native_extensions.py', 'qkf_literal')
    return V, X


def synthesized(word, programs, direction):
    return F.synthesize({'frames': word['frames'], 'start': word['start'], 'final': word['final'],
                         'precondition': [], 'A': [], 'B': [], 'cut': [], 'compensation': [],
                         'cleanup': [], 'tail': []}, [list(e) for e in programs[direction]])


def centre_hyperplanes(word, programs):
    """The dim-8 frames joined to the ground frame by centre transports, as vector sets.

    Forward centre events run frame -> ground and backward events run
    ground -> frame; both orientations must name the same eight frames.
    """
    seen = {}
    for direction in ('forward', 'backward'):
        frames = []
        for e in synthesized(word, programs, direction):
            if e[0] == 'center':
                need(e[4] == 8, 'centre transport charged rank %s, expected 8' % e[4])
                ends = sorted((e[2], e[3]), key=lambda i: len(word['frames'][i]))
                need([len(word['frames'][i]) for i in ends] == [0, 8], 'centre edge is not ground <-> dim 8')
                frames.append(ends[1])
        seen[direction] = sorted(frames)
    need(seen['forward'] == seen['backward'], 'orientations disagree on the centre frames')
    out = []
    for i in seen['forward']:
        span = Q.span_of(word['frames'][i])
        if span not in out:
            out.append(span)
    return out


def check_structure(word, programs):
    hyperplanes = centre_hyperplanes(word, programs)
    need(len(hyperplanes) == 8, 'expected 8 distinct centre source frames, got %d' % len(hyperplanes))
    normals = []
    for h in hyperplanes:
        need(len(h) == 256, 'centre source frame is not a hyperplane of F2^9')
        found = [lam for lam in range(1, 512) if all(parity(lam, x) == 0 for x in h)]
        need(len(found) == 1, 'hyperplane normal is not unique')
        normals.append(found[0])
    need(sorted(normals) == sorted(NORMALS), 'normals %s != declared %s' % (normals, NORMALS))
    rank = gf2_rank(normals)
    need(rank == 4, 'normal rank %d != 4' % rank)
    union = set().union(*hyperplanes)
    outside = sorted(v for v in range(1, 512) if v not in union)
    need(len(union) == 480, 'union has %d vectors, expected 480' % len(union))
    need(outside == PREDICTED, 'outside-set differs from the declared 32 directions')
    need(outside == [v for v in range(1, 512) if all(parity(lam, v) for lam in normals)],
         'outside-set is not {v : lambda_i(v) = 1 for all i}')
    base = outside[0]
    difference = {v ^ base for v in outside}
    need(len(difference) == 32 and all(a ^ b in difference for a in difference for b in difference),
         'outside-set is not a coset of a 5-dimensional subspace')
    need(not difference & set(outside), 'outside-set meets its difference subspace')
    need(all(lam < 128 for lam in normals) and
         outside == sorted(h + 128*i + 256*j for h in normals for i in (0, 1) for j in (0, 1)),
         'outside-set is not {normal + 128 i + 256 j}')
    pairs = sum(1 for u in outside for w in outside if u < w and u ^ w in set(outside))
    need(pairs == 0, '%d two-dimensional kernels survive' % pairs)
    print('centre source frames: 8 hyperplanes, normals %s, GF(2) rank %d' % (sorted(normals), rank))
    print('outside-set: 32 directions, a coset of a 5-dimensional subspace; '
          'two-dimensional kernels inside it: 0')


def check_geometric(word):
    """Under the main-final condition, 511 is the only direction outside every dim-8 main final."""
    finals = []
    for r in range(Q.MAINS):
        basis = word['frames'][word['final'][r]]
        if len(basis) == 8:
            span = Q.span_of(basis)
            if span not in finals:
                finals.append(span)
    need(len(finals) == 112, 'expected 112 distinct dim-8 main finals, got %d' % len(finals))
    normals = []
    for h in finals:
        found = [lam for lam in range(1, 512) if all(parity(lam, x) == 0 for x in h)]
        need(len(found) == 1, 'main-final normal is not unique')
        normals.append(found[0])
    need(gf2_rank(normals) == 9, 'main-final normals do not have full rank 9')
    outside = [v for v in range(1, 512) if not any(v in h for h in finals)]
    need(outside == [511], 'directions outside every main final: %s' % outside)
    print('main finals: 112 dim-8 hyperplanes, normals of GF(2) rank 9; only 511 lies outside all')


def check_member(rec, v):
    want = DECLARED[v]
    for key, value in want.items():
        got = rec.get(key)
        need(got == value, 'v=%d %s: got %r, declared %r' % (v, key, got, value))


def check_family(word, programs, V, X):
    records = {}
    for v in PREDICTED:
        rec = Q.evaluate(word, programs, v, V, X)
        need(rec['admissible'], 'predicted direction %d rejected: %s' % (v, rec['reason']))
        records[v] = rec
    for v in DECLARED:
        check_member(records[v], v)
    widened = sorted(v for v, r in records.items()
                     if r['helper_widths'] != DECLARED[153]['helper_widths'])
    need(widened == WIDENED_HELPERS, 'directions with a widened helper profile: %s' % widened)
    need(all(records[v]['helper_widths'] == {4: 28, 6: 7, 7: 47, 8: 325, 9: 1} for v in widened),
         'unexpected widened helper profile')
    ranking = sorted(PREDICTED, key=lambda v: -records[v]['kappa'])
    need(ranking[0] == 153, 'best direction is %d, not 153' % ranking[0])
    for v in REJECTED_CONTROLS:
        rec = Q.evaluate(word, programs, v, V, X)
        need(not rec['admissible'] and rec['reason'] == PAID_RANK_REASON,
             'control %d: admissible=%s reason=%r' % (v, rec['admissible'], rec['reason']))
    print('replayed all 32 predicted directions: 632/632 endpoints, both orientations, C cleared')
    for v in ranking[:3] + [511]:
        r = records[v]
        print('  v=%3d deficit %d surplus %d complex saving %.12f'
              % (v, r['local_deficit'], r['surplus'], r['kappa']))
    print('rejection controls %s: shipped paid-rank check rejects each' % REJECTED_CONTROLS)


def scan(word, programs, V, X, lo, hi):
    need(1 <= lo <= hi <= 511, 'scan range must lie in 1..511')
    accepted = []
    for v in range(lo, hi+1):
        rec = Q.evaluate(word, programs, v, V, X)
        need(rec['admissible'] == (v in PREDICTED),
             'v=%d admissible=%s, predicted %s (%s)' % (v, rec['admissible'], v in PREDICTED, rec['reason']))
        if not rec['admissible']:
            need(rec['reason'] == PAID_RANK_REASON, 'v=%d rejected for %r' % (v, rec['reason']))
        else:
            accepted.append(v)
    print('scan %d..%d: %d directions, %d accepted, all as predicted'
          % (lo, hi, hi-lo+1, len(accepted)))


def physical(word, programs, v):
    need(v in PREDICTED, 'physical check needs an admissible direction')
    ce = F.load(ROOT/'research/t74-native-fast/vendor/native/new/code/borrow/vendor/clifford/clifford_exact.py',
                'qkf_clifford')
    P = F.load(ROOT/'research/kappa-function-composition/complex/prune_native.py', 'qkf_lowering')
    X = F.load(ROOT/'research/kappa-rebuild/complex/native_extensions.py', 'qkf_literal_physical')
    qword, qprograms, _ = Q.quotient(word, programs, v)
    need(Q.pad_ambient(qword, v.bit_length()-1) is not None, 'no helper absorbs the unused axis')
    frames = qword['frames']
    edges = set()
    for direction in ('forward', 'backward'):
        for e in synthesized(qword, qprograms, direction):
            if e[0] == 'climb':
                edges.add((e[3], e[4]))
            elif e[0] == 'center':
                edges.add((e[2], e[3]))
    for r in range(Q.MAINS, Q.ROLES):
        edges.add((qword['start'][r], qword['final'][r]))
    bad = 0
    for a, b in sorted(edges):
        want = abs(len(frames[b])-len(frames[a]))
        op = ce.canonical_frame(9, frames[a]).adjoint().then(ce.canonical_frame(9, frames[b]))
        for actual in (op, P.conjugate(ce, op)):
            if X.N.lower_exact(P, ce, actual)['rank'] != want:
                bad += 1
    need(bad == 0, 'v=%d: %d lowering mismatches' % (v, bad))
    print('physical lowering v=%d: %d distinct edges, both orientations, 0 mismatches' % (v, len(edges)))


def main():
    args = sys.argv[1:]
    word, programs = Q.build_base()
    if '--physical' in args:
        physical(word, programs, int(args[args.index('--physical')+1]))
        print('PASS_QUOTIENT_KERNEL_PHYSICAL')
        return
    V, X = evaluators()
    if '--scan' in args:
        i = args.index('--scan')
        scan(word, programs, V, X, int(args[i+1]), int(args[i+2]))
        print('PASS_QUOTIENT_KERNEL_SCAN')
        return
    check_structure(word, programs)
    check_geometric(word)
    check_family(word, programs, V, X)
    print('PASS_QUOTIENT_KERNEL_FAMILY')


if __name__ == '__main__':
    main()
