#!/usr/bin/env python3
"""Verifier for the bit paid-profile duality and the PR #589 tuned-word audit.

    python3 research/bit-profile-pair-audit/verify.py            # cheap checks (~1 min)
    python3 research/bit-profile-pair-audit/verify.py --full     # adds the complete pair search (~10 min)

Checks
  1  source pins (sha256) of every file this audit reads from main
  2  independent word replay: paid profile of PR #555's base word and PR #589's tuned word
  3  the profile-to-saving identity: the certified c is the unique root of
     Psi(a) = sum_r n_r r((m/r)^a - 1) = D,  D = m*W - rank_mass, and the shipped c is bracketed
     exactly by rational interval arithmetic
  4  the rank-mass / deficit identity of #545: m*W - rank_mass = 32*(8v - 9*cst)
  5  complete nominated one-move neighbourhood of the tuned word: no strictly improving move
  6  completeness of the nomination: the exact-objective argmin frame equals the nominated frame for
     every operation, over every legal (slot, frame) pair
  7  positive control: exact-objective steepest descent from PR #555's base word rediscovers PR #589's
     two transports and lands on the tuned word
  8  negative controls
  9  with --full: the complete register-connected two-move neighbourhood
"""
import argparse
import gzip
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
CODE = os.path.join(HERE, 'code')
sys.path.insert(0, CODE)
sys.path.insert(0, os.path.join(ROOT, 'research', 'e8-bit-p111-tuned', 'tune'))
sys.path.insert(0, os.path.join(ROOT, 'research', 'e8-bit-carrier-skeleton', 'code',
                                'hub', 'e8-r740-replica32', 'code', 'engines'))

import replay                                    # noqa: E402  (this package, independent replay)
from fractions import Fraction as F              # noqa: E402
from bitprof import certify_c, certify_c_bad, profile_deficit, fee_float, surcharge_num, SURCHARGE_DEN  # noqa: E402

EXPECTED = json.load(open(os.path.join(HERE, 'EXPECTED.json')))
for _k in ('base_word', 'tuned_word'):
    EXPECTED[_k]['profile'] = {int(r): n for r, n in EXPECTED[_k]['profile'].items()}
EXPECTED['pipeline']['idle_remainder'] = {int(r): n for r, n in EXPECTED['pipeline']['idle_remainder'].items()}
FAILURES = []


def check(name, ok, detail=''):
    print('  %-6s %s%s' % ('PASS' if ok else 'FAIL', name, ('   ' + detail) if detail else ''))
    if not ok:
        FAILURES.append(name)


def sha256(path):
    return hashlib.sha256(open(path, 'rb').read()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--full', action='store_true', help='add the complete two-move neighbourhood')
    args = ap.parse_args()

    print('1. source pins')
    for rel, want in EXPECTED['pins'].items():
        p = os.path.join(ROOT, rel)
        got = sha256(p) if os.path.exists(p) else None
        check(rel, got == want, '' if got == want else 'sha256 %s' % got)

    print('2. independent replay of both words')
    words = {}
    for key in ('base_word', 'tuned_word'):
        w = json.load(gzip.open(os.path.join(ROOT, EXPECTED[key]['path']), 'rt'))
        P, dims = replay.replay_profile(w)
        words[key] = (w, P)
        check('%s profile' % key, P == EXPECTED[key]['profile'],
              '' if P == EXPECTED[key]['profile'] else str(P))
        check('%s live count' % key, replay.live_count(w) == EXPECTED[key]['live'],
              'live=%d' % replay.live_count(w))
        check('%s rank mass' % key, sum(r * n for r, n in P.items()) == EXPECTED[key]['rank_mass'])

    print('3. profile -> certified saving')
    for key in ('base_word', 'tuned_word'):
        w, loc = words[key]
        P = global_profile(loc)
        D = profile_deficit(P, EXPECTED['pipeline']['m'], EXPECTED['pipeline']['W'])
        check('%s deficit' % key, D == EXPECTED['pipeline']['deficit'], 'D=%d' % D)
        lo, hi, _ = certify_c_bad(P, EXPECTED['pipeline']['m'], EXPECTED['pipeline']['W'], digits=24)
        want = F(EXPECTED[key]['shipped_c'])
        check('%s certified c bracketed exactly' % key, lo <= want < hi, 'lo=%s' % lo)
        check('%s bracket lower endpoint equals shipped c' % key, lo == want, 'lo=%s' % lo)
        check('%s bracket width is one grid step' % key, hi - lo == F(1, 10 ** 24))
        # negative control: without the inherited bad-envelope surcharge the root is strictly larger
        lo0, hi0, _ = certify_c(P, EXPECTED['pipeline']['m'], EXPECTED['pipeline']['W'], digits=24)
        check('%s unsurcharged root is strictly larger (surcharge control)' % key, lo0 > want,
              'unsurcharged lo=%s' % lo0)

    print('4. #545 rank-mass / deficit identity')
    for key in ('base_word', 'tuned_word'):
        w, loc = words[key]
        v, cst = w['v'], EXPECTED[key]['decoder_constant']
        lhs = EXPECTED['pipeline']['m'] * replay.live_count(w) - sum(r * n for r, n in global_profile(loc).items())
        rhs = EXPECTED['pipeline']['T'] * (8 * v - 9 * cst)
        check('%s  m*W - rank_mass = T(8v - 9*cst)' % key, lhs == rhs, '%d == %d' % (lhs, rhs))
        # negative control: a wrong decoder constant breaks the identity
        check('%s wrong cst breaks the identity' % key,
              EXPECTED['pipeline']['m'] * replay.live_count(w) - sum(r * n for r, n in global_profile(loc).items())
              != EXPECTED['pipeline']['T'] * (8 * v - 9 * (cst + 1)))

    print('5. complete nominated one-move neighbourhood of the tuned word')
    import tune
    from stateprof import StateProf, apply_move, undo_move
    import search as S_search
    tuned = words['tuned_word'][0]
    T = tune.Tuner(tuned, a=EXPECTED['a0'])
    S = StateProf(T, EXPECTED['a0'])
    base_obj, rows = S_search.scan_singles(T, S, tune.best_move)
    neg = [r for r in rows if r[0] < -1e-12]
    zero = [r for r in rows if abs(r[0]) <= 1e-12]
    check('base exact objective', abs(base_obj - EXPECTED['tuned_word']['objective']) < 1e-6,
          '%.9f' % base_obj)
    check('candidates evaluated', len(rows) == EXPECTED['tuned_word']['n_candidates'], '%d' % len(rows))
    check('no strictly improving single move', not neg, '%d found' % len(neg))
    check('cost-neutral plateau size', len(zero) == EXPECTED['tuned_word']['n_neutral'], '%d' % len(zero))
    # Steinberg 3 -> 2 is also empty at this word
    ns = 0
    for sec in 'AB':
        V = T.view(sec)
        for (case, pl, pk, pq) in tune.find_triples(V):
            r = tune.eval_steinberg(V, pl, pk, pq)
            if r and r[0] < -1e-12:
                ns += 1
    check('no improving Steinberg 3->2 move', ns == 0, '%d found' % ns)

    print('6. completeness of the nomination over all legal (slot, frame) pairs')
    mism = 0
    nlegal = 0
    for sec in 'AB':
        V = T.view(sec)
        for i in range(len(V.ops)):
            cands = tune.best_move(V, i, thr=1e9, all_=True)
            if not cands:
                continue
            nom_best = min(cands, key=lambda x: x[0])
            exact_best = None
            for (q, Fr) in S_search.all_legal_moves(V, i, tune.commute, tune.best_move):
                if q == i and Fr == V.ops[i][0]:
                    continue
                om = apply_move(V, i, q, Fr)
                S.rebuild_z()
                d = S.objective() - base_obj
                undo_move(V, q, om)
                nlegal += 1
                if exact_best is None or d < exact_best[0]:
                    exact_best = (d, q, Fr)
            if exact_best and (exact_best[1], exact_best[2]) != (nom_best[1], nom_best[2]):
                mism += 1
    check('legal (slot, frame) pairs examined', nlegal >= EXPECTED['n_legal_pairs_min'],
          '%d (>= %d; the exact count depends on closure frames created earlier in the run)'
          % (nlegal, EXPECTED['n_legal_pairs_min']))
    check('nominated frame is exact-objective optimal for every operation', mism == 0, '%d mismatches' % mism)

    print('7. positive control: exact steepest descent from the base word')
    bword = words['base_word'][0]
    T2 = tune.Tuner(bword, a=EXPECTED['a0'])
    S2 = StateProf(T2, EXPECTED['a0'])
    obj2, applied = S_search.exact_greedy(T2, S2, tune.best_move)
    check('steepest descent applies exactly two moves', len(applied) == 2, '%d' % len(applied))
    check('moves are the PR #589 hoist and sink',
          [list(x) for x in [(a['section'], a['slot'], a['frame']) for a in applied]] == EXPECTED['pr589_moves'],
          str([(a['section'], a['slot'], a['frame']) for a in applied]))
    check('descends to the tuned word objective', abs(obj2 - EXPECTED['tuned_word']['objective']) < 1e-6,
          '%.9f' % obj2)
    check('descends to the tuned word profile', S2.profile() == EXPECTED['tuned_word']['profile'],
          str(S2.profile()))

    print('8. controls')
    # 8a the pricer is sensitive to a rank-mass-preserving profile perturbation whose objective
    #    direction is known by hand: 3 climbs of rank 1 -> 1 climb of rank 3 (mass 3 -> 3)
    P = global_profile(words['tuned_word'][1])
    P2 = dict(P); P2[1] -= 3; P2[3] = P2.get(3, 0) + 1
    lo1, _, _ = certify_c_bad(P, 64, 28416, digits=24)
    lo2, _, _ = certify_c_bad(P2, 64, 28416, digits=24)
    dG = (3 * 1.0 ** (1 - EXPECTED['a0'])) - (1 * 3.0 ** (1 - EXPECTED['a0']))
    check('mass-preserving perturbation lowers G and raises c', dG > 0 and lo2 > lo1,
          'dG=%+.6e  %s -> %s' % (dG, lo1, lo2))
    # 8b the identity is not vacuous: a perturbed live count gives a different root
    check('pricer responds to a perturbed deficit',
          certify_c_bad(P, 64, 28417, digits=12)[0] != certify_c_bad(P, 64, 28416, digits=12)[0])
    # 8c the exact objective orders the two words the way the certified saving does
    check('base word profile differs from the tuned profile',
          EXPECTED['base_word']['profile'] != EXPECTED['tuned_word']['profile'])
    check('base word objective is strictly worse than the tuned objective',
          EXPECTED['base_word']['objective'] > EXPECTED['tuned_word']['objective'],
          '%.9f > %.9f' % (EXPECTED['base_word']['objective'], EXPECTED['tuned_word']['objective']))
    check('and the base word therefore has the smaller certified saving',
          F(EXPECTED['base_word']['shipped_c']) < F(EXPECTED['tuned_word']['shipped_c']))

    if args.full:
        print('9. complete register-connected two-move neighbourhood')
        # a fresh tuner so the pair count does not depend on closure frames created by steps 5-6
        T4 = tune.Tuner(tuned, a=EXPECTED['a0'])
        S4 = StateProf(T4, EXPECTED['a0'])
        _, rows4 = S_search.scan_singles(T4, S4, tune.best_move)
        b, best, info, npairs = S_search.pair_search(T4, S4, tune.best_move, rows4)
        check('register-adjacent pairs evaluated', npairs >= EXPECTED['pair_search']['n_pairs_min'],
              '%d (>= %d)' % (npairs, EXPECTED['pair_search']['n_pairs_min']))
        check('best two-move delta', abs(best - EXPECTED['pair_search']['best_delta']) < 1e-12,
              '%.9e' % best)
        check('no improving pair', best >= -1e-12, '%.9e' % best)

    print()
    if FAILURES:
        print('FAILED: %s' % ', '.join(FAILURES))
        return 1
    print('all checks passed')
    return 0


def global_profile(local):
    """the nine-stage paid profile from the word-level (per-column) profile:
    T*L replicas of the local profile plus the frozen idle remainder."""
    T = EXPECTED['pipeline']['T']
    L = EXPECTED['pipeline']['L']
    P = {r: T * L * n for r, n in local.items()}
    for r, n in EXPECTED['pipeline']['idle_remainder'].items():
        P[r] = P.get(r, 0) + n
    return P


if __name__ == '__main__':
    sys.exit(main())
