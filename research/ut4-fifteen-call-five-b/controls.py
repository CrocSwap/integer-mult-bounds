#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent algebra, 3-role quotient, and coverage controls for the 15-call five-b boundary.

No predecessor scalar multiplication, reduction or group multiplication is
used by the dense/subsequence and literal-matrix oracles below.
"""
from collections import defaultdict
from itertools import combinations, combinations_with_replacement, product
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('ut4_fifteen_call_controls_census', HERE / 'census.py')
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)
P, source = C.load()
require = C.require


def matmul_r(a, b, r):
    aa = [[(a >> (r * i + j)) & 1 for j in range(r)] for i in range(r)]
    bb = [[(b >> (r * i + j)) & 1 for j in range(r)] for i in range(r)]
    cc = [[sum(aa[i][k] * bb[k][j] for k in range(r)) % 2 for j in range(r)] for i in range(r)]
    return sum(cc[i][j] << (r * i + j) for i in range(r) for j in range(r))


def quotient_classes():
    words = [''.join(w) for n in range(4) for w in product('abc', repeat=n)]
    result = {}
    for word in words:
        orbit, queue = {word}, [word]
        for w in queue:
            for i in range(len(w) - 1):
                if w[i:i + 2] in ('ac', 'ca'):
                    changed = w[:i] + w[i:i + 2][::-1] + w[i + 2:]
                    if changed not in orbit:
                        orbit.add(changed)
                        queue.append(changed)
        zero = any(any(w[i] == w[i + 1] for i in range(len(w) - 1)) for w in orbit)
        result[word] = None if zero else min(orbit)
    require(len(set(result.values()) - {None}) == 17, 'independent quotient dimension')
    return result


CLASSES = quotient_classes()
MM2 = [[matmul_r(a, b, 2) for b in range(16)] for a in range(16)]


def quotient_2role(word):
    result = {'': 9}
    for degree in range(1, min(3, len(word)) + 1):
        for indices in combinations(range(len(word)), degree):
            name = CLASSES[''.join(word[i][0] for i in indices)]
            if name is None:
                continue
            coefficient = 9
            for i in indices:
                coefficient = MM2[coefficient][word[i][1]]
            result[name] = result.get(name, 0) ^ coefficient
    return {k: v for k, v in result.items() if v}


def quotient_3role(word):
    ident3 = 1 | (1 << 4) | (1 << 8)
    result = {'': ident3}
    for degree in range(1, min(3, len(word)) + 1):
        for indices in combinations(range(len(word)), degree):
            name = CLASSES[''.join(word[i][0] for i in indices)]
            if name is None:
                continue
            coefficient = ident3
            for i in indices:
                coefficient = matmul_r(coefficient, word[i][1], 3)
            result[name] = result.get(name, 0) ^ coefficient
    return {k: v for k, v in result.items() if v}


def address(g):
    a, b, c, d, e, f = [(g >> i) & 1 for i in range(6)]
    return (1 | (a << 1) | (d << 2) | (f << 3), 2 | (b << 2) | (e << 3), 4 | (c << 3), 8)


def binary_product(a, b):
    rows = []
    for row in a:
        value = 0
        for j in range(4):
            if (row >> j) & 1:
                value ^= b[j]
        rows.append(value)
    return tuple(rows)


ADDRESSES = [address(g) for g in range(64)]
INDEX = {matrix: g for g, matrix in enumerate(ADDRESSES)}
GROUP = [[INDEX[binary_product(a, b)] for b in ADDRESSES] for a in ADDRESSES]
GENERATORS = dict(a=1, b=2, c=4)


def formal(word, roles):
    result = [[{0} if i == j else set() for j in range(roles)] for i in range(roles)]
    for letter, mask in word:
        old = [[set(entry) for entry in row] for row in result]
        for i, j, k in product(range(roles), repeat=3):
            if (mask >> (roles * k + j)) & 1:
                result[i][j].symmetric_difference_update(old[i][k])
                result[i][j].symmetric_difference_update(GROUP[g][GENERATORS[letter]] for g in old[i][k])
    return result


def outer(x, y, roles):
    return sum(((x >> i) & (y >> j) & 1) << (roles * i + j)
               for i in range(roles) for j in range(roles))


def project_3to2(mask):
    return sum(((mask >> (3 * i + j)) & 1) << (2 * i + j) for i in range(2) for j in range(2))


def extract_kh_vec(mask3):
    return ((mask3 >> (3 * 2 + 0)) & 1) | (((mask3 >> (3 * 2 + 1)) & 1) << 1)


def extract_hk_vec(mask3):
    return ((mask3 >> (3 * 0 + 2)) & 1) | (((mask3 >> (3 * 1 + 2)) & 1) << 1)


def catalogue_explicit(n):
    positions = tuple(combinations_with_replacement(range(6), n))
    result = defaultdict(list)
    zeros = 0
    for ns in product(P.COUPLINGS, repeat=n):
        if P.total(ns):
            continue
        zeros += 1
        prefix = [0] * (n + 1)
        for index, item in enumerate(ns, 1):
            prefix[index] = prefix[index - 1] ^ item
        for slots in positions:
            counts = [0] * 6
            for slot in slots:
                counts[slot] += 1
            acc = 0
            profile = []
            for count in counts[:5]:
                acc += count
                profile.append(prefix[acc])
            result[tuple(profile)].append((ns, slots))
    return dict(result), zeros


def main():
    for g, h in product(range(64), repeat=2):
        require(GROUP[g][h] == P.group_product(g, h), 'literal group law disagreement')

    alphabet = tuple(product('abc', P.COUPLINGS))
    short = 0
    for length in range(4):
        for word in product(alphabet, repeat=length):
            require(quotient_2role(word) == P.quotient(word), 'independent 2-role quotient disagreement')
            short += 1
    require(short == 20440, 'short-word coverage')

    result = json.loads((HERE / 'RESULT.json').read_text(encoding='utf-8'))
    positive = [tuple(step) for step in result['positive']['full_word']]
    require(quotient_2role(positive) == P.TARGET, 'positive quotient control')

    # 1. Verify rank-sum profile characterization across all 16^5 = 1,048,576 profiles
    srank = tuple(C.s_rank(P, s) for s in range(16))
    cat4, z4 = catalogue_explicit(4)
    cat5, z5 = catalogue_explicit(5)
    require((cat4, z4) == P.gap_catalogue(), 'unchanged four-call catalogue control')
    require(z4 == 441 and z5 == 3600, 'zero-sum outer sequence counts for n=4,5')
    require(sum(map(len, cat4.values())) == 55566, 'four-call realization count')
    require(sum(map(len, cat5.values())) == 907200, 'five-call realization count')

    rank_hist = [0] * 13
    by_max_rank = {4: set(), 5: set(), 6: set()}
    for prof in product(range(16), repeat=5):
        gaps = C.profile_gaps(prof)
        r = sum(srank[s] for s in gaps)
        rank_hist[r] += 1
        for n in (4, 5, 6):
            if r <= n:
                by_max_rank[n].add(prof)
    require(rank_hist == result['profile_rank_sum_histogram'], 'rank-sum histogram mismatch')
    require(set(cat4) == by_max_rank[4] and len(cat4) == 9721, 'n=4 rank-sum profile set mismatch')
    require(set(cat5) == by_max_rank[5] and len(cat5) == 47521, 'n=5 rank-sum profile set mismatch')
    require(len(by_max_rank[6]) == 174670, 'n=6 rank-sum profile count mismatch')

    # 2. Verify planted 2-role reconstruction controls across (6,5,4), (5,5,5), (4,5,6)
    for key, fixture in result['planted_controls']['two_role'].items():
        word = tuple((step[0], step[1]) for step in fixture['word'])
        middle = tuple(fixture['middle'])
        na, _, nc = map(int, key.split(','))
        pa, pc = tuple(fixture['a_profile']), tuple(fixture['c_profile'])
        ra = (tuple(fixture['a_realization'][0]), tuple(fixture['a_realization'][1]))
        rc = (tuple(fixture['c_realization'][0]), tuple(fixture['c_realization'][1]))
        require(len(ra[0]) == na and len(rc[0]) == nc, f'outer count mismatch in {key}')
        require(pa in by_max_rank[na] and pc in by_max_rank[nc], f'planted profile rank-sum invalid in {key}')
        require(word in P.expanded_words(middle, ra, rc), f'planted interleaving lost in {key}')
        q2 = quotient_2role(word)
        for cls in ('', 'a', 'b', 'c', 'ab', 'ba', 'bc', 'cb', 'aba', 'abc', 'bab', 'bcb', 'cba', 'cbc'):
            require(q2.get(cls, 0) == P.TARGET.get(cls, 0), f'2-role non-adjacent-ac {cls} mismatch in {key}')
        sa_g, sc_g = C.profile_gaps(pa), C.profile_gaps(pc)
        b_ac, b_acb, b_bac = C.eval_base_2role(P, middle, sa_g, sc_g)
        b_pref = (0, middle[0], middle[0] ^ middle[1],
                  middle[0] ^ middle[1] ^ middle[2],
                  middle[0] ^ middle[1] ^ middle[2] ^ middle[3], 0)
        for g in range(6):
            qg = P.MULT[sa_g[g]][sc_g[g]]
            b_ac ^= qg
            b_acb ^= P.MULT[qg][b_pref[g]]
            b_bac ^= P.MULT[b_pref[g]][qg]
        require(q2.get('ac', 0) == b_ac and q2.get('acb', 0) == b_acb and q2.get('bac', 0) == b_bac,
                f'long-word 2-role oracle disagreement in {key}')
        ka, kc = P.profile_key(middle, pa), P.profile_key(middle, pc)
        require((ka, kc) in P.compatible_keys({ka: [pa]}, {kc: [pc]}), f'planted cross join lost in {key}')

    # 3. Verify same-label nilpotent dirty compression vs cross-label failure in M_3(F_2[UT_4(F_2)])
    same_label_pairs = 0
    dirty_col_mask = outer(1, 4, 3)  # u=(1,0,0)^T, v=(0,0,1)
    dirty_row_mask = outer(4, 1, 3)  # u=(0,0,1)^T, v=(1,0,0)
    both_dirty_masks = [
        outer(1, 5, 3),
        outer(5, 1, 3),
        outer(5, 5, 3),
        dirty_col_mask,
        dirty_row_mask,
    ]
    for letter in ('a', 'c'):
        for m1, m2 in product(both_dirty_masks, repeat=2):
            w3 = [(letter, m1), (letter, m2)]
            actual = formal(w3, 3)
            w2 = [(letter, project_3to2(m)) for _, m in w3 if project_3to2(m)]
            compressed = formal(w2, 2)
            require([row[:2] for row in actual[:2]] == compressed,
                    'same-label nilpotent dirty compression failed')
            same_label_pairs += 1
    mixed_ac = formal([('a', dirty_col_mask), ('c', dirty_row_mask)], 3)
    require(mixed_ac[0][0] != {0}, 'cross-label dirty contraction failed to fire')

    # 4. Verify independent 3-role subsequence oracle against fast 3-role (5,5,5) formulas
    non_adjacent_ac_classes = {
        '', 'a', 'b', 'c', 'ab', 'ba', 'bc', 'cb',
        'aba', 'abc', 'bab', 'bcb', 'cba', 'cbc',
    }
    for mode, fixture in result['planted_controls']['three_role_555'].items():
        middle = tuple(fixture['middle'])
        pa, pc = tuple(fixture['a_profile']), tuple(fixture['c_profile'])
        da_prof = tuple(fixture['dirty_a_profile'])
        dc_prof = tuple(fixture['dirty_c_profile'])
        word_xy = fixture['word_xy']
        word3 = tuple((letter, outer(x3, y3, 3)) for letter, x3, y3 in word_xy)
        word2 = tuple((letter, project_3to2(m3)) for letter, m3 in word3 if project_3to2(m3))
        q2 = quotient_2role(word2)
        q3 = quotient_3role(word3)
        for cls in non_adjacent_ac_classes:
            require(project_3to2(q3.get(cls, 0)) == q2.get(cls, 0) == P.TARGET.get(cls, 0),
                    f'3-role non-adjacent-ac class {cls} disagreement in {mode}')
        is_case_I = (mode == 'case_I_col_a_row_c')
        if is_case_I:
            for cls in ('a', 'ab', 'aba', 'abc'):
                require(extract_kh_vec(q3.get(cls, 0)) == 0, f'Case I KH {cls} nonzero')
            for cls in ('c', 'bc', 'cbc', 'cba'):
                require(extract_hk_vec(q3.get(cls, 0)) == 0, f'Case I HK {cls} nonzero')
        else:
            for cls in ('a', 'ba', 'aba', 'cba'):
                require(extract_hk_vec(q3.get(cls, 0)) == 0, f'Case II HK {cls} nonzero')
            for cls in ('c', 'cb', 'cbc', 'abc'):
                require(extract_kh_vec(q3.get(cls, 0)) == 0, f'Case II KH {cls} nonzero')

        # Recompute exact (H, H) AC, ACB, BAC via eval_base_3role_hh + within-gap joint qac
        sa_g = C.profile_gaps(pa)
        sc_g = C.profile_gaps(pc)
        da_g = C.profile_gaps(da_prof)
        dc_g = C.profile_gaps(dc_prof)
        b_ac, b_acb, b_bac = C.eval_base_3role_hh(P, middle, sa_g, da_g, sc_g, dc_g, is_case_I)
        # Because first_3role_word places all a-calls before all c-calls in each gap g,
        # the within-gap q_ac contribution in gap g is sum_{c in gap g} (sa_g[g]*nc + extra) = sa_g[g]*sc_g[g] + (dc_g[g]*da_g[g] if not is_case_I else 0)
        b_pref = (0, middle[0], middle[0] ^ middle[1],
                  middle[0] ^ middle[1] ^ middle[2],
                  middle[0] ^ middle[1] ^ middle[2] ^ middle[3], 0)
        for g in range(6):
            qg = P.MULT[sa_g[g]][sc_g[g]] ^ (0 if is_case_I else P.MULT[da_g[g]][dc_g[g]])
            b_ac ^= qg
            b_acb ^= P.MULT[qg][b_pref[g]]
            b_bac ^= P.MULT[b_pref[g]][qg]
        require(project_3to2(q3.get('ac', 0)) == b_ac, f'3-role HH AC formula mismatch in {mode}')
        require(project_3to2(q3.get('acb', 0)) == b_acb, f'3-role HH ACB formula mismatch in {mode}')
        require(project_3to2(q3.get('bac', 0)) == b_bac, f'3-role HH BAC formula mismatch in {mode}')

        # Negative control: perturb the first a-call's dirty bit and verify off-diagonal violation
        bad_xy = [list(step) for step in word_xy]
        for idx, (letter, x3, y3) in enumerate(bad_xy):
            if letter == 'a':
                if is_case_I:
                    bad_xy[idx][1] = x3 ^ 4
                else:
                    bad_xy[idx][2] = y3 ^ 4
                break
        bad_q3 = quotient_3role(tuple((l, outer(x, y, 3)) for l, x, y in bad_xy))
        if is_case_I:
            require(any(extract_kh_vec(bad_q3.get(cls, 0)) != 0 for cls in ('a', 'ab', 'aba', 'abc')),
                    'Case I perturbed dirty bit not detected by 3-role oracle')
        else:
            require(any(extract_hk_vec(bad_q3.get(cls, 0)) != 0 for cls in ('a', 'ba', 'aba', 'cba')),
                    'Case II perturbed dirty bit not detected by 3-role oracle')

    # 5. Verify 15-call span-rank excess profiles and five-b classification
    span_profiles_15 = [
        ranks for ranks in product(range(2, 6), repeat=6)
        if 1 + sum(ranks) <= 15
    ]
    require(len(span_profiles_15) == 28, '15-call span profile count mismatch')
    five_b_exact_excess = [
        (eax, eay, ebx, eby, ecx, ecy)
        for eax, eay, ebx, eby, ecx, ecy in product(range(3), repeat=6)
        if ebx == 0 and eby == 0 and eax + eay + ecx + ecy == 2
    ]
    require(len(five_b_exact_excess) == 10, 'five-b excess-2 profile count mismatch')
    split_654 = [e for e in five_b_exact_excess if e[0] + e[1] == 2]
    split_456 = [e for e in five_b_exact_excess if e[4] + e[5] == 2]
    split_555 = [e for e in five_b_exact_excess if e[0] + e[1] == 1 and e[4] + e[5] == 1]
    require(len(split_654) == 3 and len(split_456) == 3 and len(split_555) == 4,
            'five-b excess-2 split partition mismatch')

    # 6. Verify weighted price envelope and (1,3,1) sharpness
    price_cases = 0
    for alpha, beta, gamma in product(range(6), repeat=3):
        direct = 4 * alpha + 6 * beta + 4 * gamma
        bound = min(direct, 4 * alpha + 5 * beta + 4 * gamma + 3 * min(alpha, gamma))
        relaxed = min(
            a * alpha + b * beta + c * gamma
            for a, b, c in product(range(4, 13), range(5, 13), range(4, 13))
            if b >= 6 or a + c >= 11
        )
        require(bound == relaxed, 'weighted lower-envelope arithmetic mismatch')
        if beta <= 3 * min(alpha, gamma):
            require(bound == direct, 'sharp price cone mismatch')
        price_cases += 1
    require(4 * 1 + 6 * 3 + 4 * 1 == 26 and 4 * 1 + 5 * 3 + 4 * 1 + 3 * 1 == 26,
            '(1,3,1) boundary equality failed')
    require(min(4 + 24 + 4, 4 + 20 + 4 + 3) == 31 < 32,
            'outside-cone (1,4,1) false sharpness control failed')

    print('PASS_UT4_FIFTEEN_CALL_CONTROLS', json.dumps(dict(
        literal_group_products=4096,
        short_quotient_words=short,
        profile_rank_sum_total=sum(rank_hist),
        four_call_realizations=55566,
        five_call_realizations=907200,
        six_call_profiles=len(by_max_rank[6]),
        planted_2role_domains=len(result['planted_controls']['two_role']),
        same_label_nilpotent_pairs=same_label_pairs,
        cross_label_dirty_detected=True,
        planted_3role_modes=len(result['planted_controls']['three_role_555']),
        span_profiles_15=len(span_profiles_15),
        price_grids=price_cases,
        price_1_3_1_minimum=26,
        outside_cone_sharpness_rejected=True,
    ), sort_keys=True))


if __name__ == '__main__':
    main()
