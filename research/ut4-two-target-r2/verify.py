#!/usr/bin/env python3
"""Replay the r = w = 2 fourteen-call search for two UT4(F2) central targets.

Checks, in order: the quotient map Q is multiplicative on UT4(F2); the GL2(F2) orbit
representatives cover every zero-sum middle sequence; CrocSwap/integer-mult-bounds#1662's direct 16-call word passes
the formal endpoint and each one-call omission fails; then the exhaustive (4,6,4) search
reproduces the recorded counts with no formal solution. Standard library only, ~3 min.

Aaron Wang / navinor, with help from Claude Code. Apache-2.0.
"""
import json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import search as S

EXPECTED = {
    'canonical': 5582, 'profiles': 20791, 'side_pass': 3383566, 'keys': 805712,
    'key_pairs': 184, 'pairs': 208, 'words': 3248, 'q_pass': 0, 'formal_pass': 0,
}


def check(cond, msg):
    if not cond:
        sys.exit('FAIL: ' + msg)
    print('PASS', msg)


def main():
    t0 = time.time()
    check(S.check_quotient_homomorphism() == 4096, 'quotient map multiplicative on all 4096 pairs; phi(z)=1+abc+acb+bac+cba')

    inv = S.gl(2)
    total = sum(1 for _ in S.middle_sequences(2, 6, False))
    reps = list(S.middle_sequences(2, 6, True))
    orbit = sum(len({tuple(S.mm(S.mm(g, N, 2), h, 2) for N in bt) for g, h in inv.items()}) for bt in reps)
    check(len(inv) == 6 and total == 33489 and orbit == total and len(reps) == EXPECTED['canonical'],
          f'GL2 orbits of {len(reps)} representatives cover all {total} zero-sum middle sequences')

    direct = [(g, e, e) for e in (1, 2) for g in 'abcbabcb']
    check(S.formal_ok(direct, 2, 2) and S.q_ok(direct, 2, 2), 'direct 16-call word hits the formal and quotient endpoints')
    check(not any(S.formal_ok(direct[:i] + direct[i + 1:], 2, 2) for i in range(16)), 'all 16 one-call omissions fail')

    stats = {}
    sols = S.fast_search(stats)
    print(json.dumps(stats))
    check(stats == EXPECTED, 'exhaustive (4,6,4) counts match the record')
    check(sols == [], 'no 14-call word on two roles reaches the two-target endpoint')
    print(f'PASS_UT4_TWO_TARGET_R2_NO_14 seconds={time.time() - t0:.0f}')


if __name__ == '__main__':
    main()
