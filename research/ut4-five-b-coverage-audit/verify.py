#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Reconstruct the finite coverage audit; this is not a full #2828 proof replay."""
import argparse
from collections import Counter
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import time

import gaps as G
import profiles as P

HERE = Path(__file__).resolve().parent
TARGET = {'': 9, 'ab': 8, 'ba': 8, 'aba': 8, 'bab': 8,
          'abc': 9, 'cba': 9}
NONADJACENT = ('', 'a', 'b', 'c', 'ab', 'ba', 'bc', 'cb',
               'aba', 'abc', 'bab', 'bcb', 'cba', 'cbc')


def require(ok, message):
    if not ok:
        raise ValueError(message)


def profile_digest(pairs):
    # Sorted numeric triples [middle, a-prefix, c-prefix], compact JSON + LF.
    h = sha256()
    for row in sorted(pairs):
        h.update(G.canonical(row) + b'\n')
    return h.hexdigest()


def reduced(word):
    while 'ca' in word:
        word = word.replace('ca', 'ac')
    return None if any(x == y for x, y in zip(word, word[1:])) else word


# One A and C increment in each of the six gaps, separated by five B calls.
# Intra-gap ordering only affects AC, ACB, BAC, which are deliberately omitted.
LABELS = 'acbacbacbacbacbac'
TERMS = [(indices, reduced(''.join(LABELS[i] for i in indices)))
         for degree in (1, 2, 3)
         for indices in combinations(range(len(LABELS)), degree)]
TERMS = [(indices, name) for indices, name in TERMS if name in NONADJACENT]


def literal_profile_coefficients(middle, a, c):
    word = []
    for i, (sa, sc) in enumerate(zip(P.gaps(a), P.gaps(c))):
        word.extend((sa, sc))
        if i < 5:
            word.append(middle[i])
    result = {'': 9}
    for indices, name in TERMS:
        value = 9
        for i in indices:
            value = P.M[value][word[i]]
        result[name] = result.get(name, 0) ^ value
    return {name: result.get(name, 0) for name in NONADJACENT}


def check_profile(row):
    actual = literal_profile_coefficients(*row)
    require(actual == {name: TARGET.get(name, 0) for name in NONADJACENT},
            'nonadjacent quotient equations')


def check_caps(caps, single=3, joint=4):
    require(all(a <= single and c <= single and ac <= joint
                for a, c, ac in caps), 'gap cap is not justified by the rank bounds')


def rejects(action):
    try:
        action()
    except ValueError:
        return
    raise ValueError('negative control was not rejected')


def controls(pairs, caps):
    # Full literal subsequence expansion is independent of the side/key join.
    for row in pairs:
        check_profile(row)
    middle, a, c = pairs[0]
    altered = (middle[0] ^ 1,) + middle[1:]
    rejects(lambda: check_profile((altered, a, c)))
    rejects(lambda: check_caps(caps, single=2))
    rejects(lambda: check_caps(caps, joint=3))

    # Pure-dirty couplings have zero HH projection but a nonzero cross product.
    # This detects the incorrect active-projection simplification.
    enter, leave = G.outer(1, 4), G.outer(4, 1)
    require(G.active(enter) == G.active(leave) == 0, 'pure-dirty fixture')
    require(G.active(G.mm(enter, leave)) == 1, 'ordered dirty contraction')
    require(G.active(G.mm(leave, enter)) == 0, 'reverse dirty contraction')
    require(P.M[G.active(enter)][G.active(leave)] != 1, 'projection mutation control')
    for ao, co in (('column', 'row'), ('row', 'column')):
        aa, cc = G.alphabet(ao), G.alphabet(co)
        require(len(aa) == len(set(aa)) == len(cc) == len(set(cc)) == 21,
                'complete rank-one orientation alphabet')
        require(sum(G.active(n) == 0 for n in aa) == 3 and
                sum(G.active(n) == 0 for n in cc) == 3, 'pure-dirty alphabet coverage')
        # Explicit two-letter word must occur in the general gap table.
        a_n, c_n = (leave, enter) if ao == 'column' else (enter, leave)
        positive = [1, 1, 0, G.dirty(a_n, ao), 0, G.dirty(c_n, co), 1]
        rows = G.joint_table(aa, cc, ao, co)
        require(any(row[:-1] == positive for row in rows), 'dirty gap positive fixture')
        totals = Counter()
        for row in rows:
            totals[tuple(row[:2])] += row[-1]
        from math import comb
        require(set(totals) == {(ka, kc) for ka in range(4) for kc in range(4)
                                if ka+kc <= 4}, 'gap count-pair domain')
        require(all(count == comb(ka+kc, ka) * 21**(ka+kc)
                    for (ka, kc), count in totals.items()), 'gap multiplicity coverage')
    return {'literal_profile_checks': len(pairs), 'changed_middle_rejected': True,
            'unsupported_single_cap_2_rejected': True,
            'unsupported_joint_cap_3_rejected': True,
            'pure_dirty_and_order_controls': True,
            'gap_multiplicities_match_closed_form': True}


def run():
    stats, pairs, ranks, caps = P.enumerate_profiles(progress=True)
    require(len(pairs) == len(set(pairs)) == 5664, 'distinct profile-pair count')
    check_caps(caps)
    checked = controls(pairs, caps)
    return {
        'schema_version': 1,
        'scope': 'five-b opposite-orientation active profiles and bounded gap operators',
        'statistics': stats,
        'profile_set_sha256': profile_digest(pairs),
        'rank_sum_histogram': [[*key, count] for key, count in sorted(ranks.items())],
        'gap_cap_histogram': [[*key, count] for key, count in sorted(caps.items())],
        'gap_tables': G.run(),
        'controls': checked,
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-result', action='store_true', help='explicitly regenerate RESULT.json')
    args = parser.parse_args()
    start = time.perf_counter()
    result = run()
    if args.write_result:
        (HERE / 'RESULT.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    else:
        require(result == json.loads((HERE / 'RESULT.json').read_text(encoding='utf-8')),
                'audit receipt mismatch')
    print('PASS_UT4_FIVE_B_COVERAGE_AUDIT profiles=5664 single_gap_cap=3 joint_gap_cap=4'
          ' profile_set=' + result['profile_set_sha256'] +
          ' seconds=' + str(round(time.perf_counter()-start, 3)))
