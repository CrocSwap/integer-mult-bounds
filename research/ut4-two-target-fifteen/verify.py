#!/usr/bin/env python3
"""Replay the r = w = 2 fifteen-call search for two UT4(F2) central targets.

Checks, in order: the vendored CrocSwap/integer-mult-bounds#1690 search module is byte-identical to its
pinned head; the quotient map Q is multiplicative on UT4(F2); the GL2(F2) orbit representatives
cover every zero-sum middle sequence of length 6 and 7; the direct 16-call word passes both
endpoints; the generalized driver reproduces CrocSwap/integer-mult-bounds#1690's (4,6,4) stage counts
exactly; then the exhaustive (5,6,4), (4,6,5) and (4,7,4) searches reproduce the recorded counts
and find no formal solution. Standard library only; multiprocessing over all cores
(pass --workers N to change). --part small runs the controls and the (5,6,4)/(4,6,5) splits,
--part large the (4,7,4) split; the default runs everything.

Josie Elliston's donated session, with Claude Code. Apache-2.0.
"""
import hashlib
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fifteen as F  # noqa: E402
import pr1690_search as S  # noqa: E402

PR1690_SEARCH_SHA256 = 'eaa1380c62866acfcae77ab7e53ed30d7c4e4319978a446a6f3bb86b65920117'

PR1690_EXPECTED = {
    'canonical': 5582, 'profiles_a': 20791, 'profiles_c': 20791, 'a_pass': 3383566,
    'c_pass': 3383566, 'a_keys': 805712, 'c_keys': 805712, 'key_pairs': 184, 'pairs': 208,
    'words': 3248, 'q_pass': 0, 'formal_pass': 0,
}

EXPECTED = json.loads((HERE / 'EXPECTED.json').read_text())


def check(cond, msg):
    if not cond:
        sys.exit('FAIL: ' + msg)
    print('PASS', msg, flush=True)


def main():
    t0 = time.time()
    workers = int(sys.argv[sys.argv.index('--workers') + 1]) if '--workers' in sys.argv else None
    part = sys.argv[sys.argv.index('--part') + 1] if '--part' in sys.argv else 'all'
    check(part in ('all', 'small', 'large'), f'part {part!r} is one of all, small, large')
    splits = {'all': F.SPLITS, 'small': F.SPLITS[:2], 'large': F.SPLITS[2:]}[part]

    digest = hashlib.sha256((HERE / 'pr1690_search.py').read_bytes()).hexdigest()
    check(digest == PR1690_SEARCH_SHA256, 'vendored pr1690_search.py matches PR1690 head dfd15686 byte for byte')
    if part != 'large':
        check(S.check_quotient_homomorphism() == 4096,
              'quotient map multiplicative on all 4096 pairs; phi(z)=1+abc+acb+bac+cba')
        direct = [(g, e, e) for e in (1, 2) for g in 'abcbabcb']
        check(S.formal_ok(direct, 2, 2) and S.q_ok(direct, 2, 2),
              'direct 16-call word hits the formal and quotient endpoints')
        stats = {}
        sols = F.search((4, 6, 4), workers=workers, log=stats)
        check(stats == PR1690_EXPECTED and sols == [],
              'generalized driver reproduces PR1690 (4,6,4) stage counts exactly')

    inv = S.gl(2)
    for nb in sorted({counts[1] for counts in splits}):
        total_want, reps_want = (33489, 5582) if nb == 6 else EXPECTED['middle7']
        total = sum(1 for _ in S.middle_sequences(2, nb, False))
        reps = list(S.middle_sequences(2, nb, True))
        orbit = sum(len({tuple(S.mm(S.mm(g, N, 2), h, 2) for N in bt) for g, h in inv.items()}) for bt in reps)
        check(len(inv) == 6 and total == total_want and len(reps) == reps_want and orbit == total,
              f'GL2 orbits of {len(reps)} representatives cover all {total} zero-sum length-{nb} middle sequences')

    for counts in splits:
        stats = {}
        sols = F.search(counts, workers=workers, log=stats)
        print(json.dumps({'counts': counts, **stats}), flush=True)
        check(stats == EXPECTED[','.join(map(str, counts))], f'exhaustive {counts} counts match the record')
        check(sols == [], f'no {counts} word on two roles reaches the two-target endpoint')
    tag = {'all': 'NO_15', 'small': 'NO_15_SPLITS_564_465', 'large': 'NO_15_SPLIT_474'}[part]
    print(f'PASS_UT4_TWO_TARGET_R2_{tag} seconds={time.time() - t0:.0f}')


if __name__ == '__main__':
    main()
