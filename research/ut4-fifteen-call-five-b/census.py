#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Complete 15-call five-b quotient census for diag([z],[uz],I_rest) over F2[UT4(F2)].

Extends Gareth Davidson's PR #2314 (ut4-mixed-weighted-boundary) and PR #2343
(register-pairing-compression), and Nick Petalas's PR #2175 (ut4-mixed-central-middle),
to the three open 15-call five-b splits (6,5,4), (5,5,5) and (4,5,6) across
arbitrary finite restored dirty workspaces.

The profile-screen method is credited to Aaron Wang (PR #1690), common-orientation
and span-excess compression to ToikY (PR #1662, PR #1680) and CinnaDavis / 1337isnot1337
(PR #1541), the mixed-middle rank inequality to Nick Petalas (PR #2175), and the
mixed root tariffs, weighted boundary and pairing compression to Gareth Davidson
(PR #2027, PR #2314, PR #2343). No native bit supplier or new kappa is claimed.
"""
from collections import defaultdict
from hashlib import sha256
from itertools import product
import importlib.util
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def load():
    source = json.loads((HERE / 'SOURCES.json').read_text(encoding='utf-8'))
    vendor = source['vendor']
    require(sha256((HERE / vendor['path']).read_bytes()).hexdigest() == vendor['sha256'],
            'predecessor source hash')
    for entry in source['files']:
        if entry['usage'] == 'input':
            require(sha256((ROOT / entry['path']).read_bytes()).hexdigest() == entry['sha256'],
                    'proof input hash: ' + entry['path'])
    spec = importlib.util.spec_from_file_location('ut4_retained_2175', HERE / vendor['path'])
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result, source


def s_rank(P, s):
    if s == 0:
        return 0
    return 1 if s in P.COUPLINGS else 2


def profile_gaps(p):
    return (p[0], p[0] ^ p[1], p[1] ^ p[2], p[2] ^ p[3], p[3] ^ p[4], p[4])


def build_two_role_gap_dp(P):
    gap_dp = {(0, 0): {(0, 0, 0): 1}}
    for total_k in range(1, 11):
        for ka in range(total_k + 1):
            kc = total_k - ka
            if ka > 6 or kc > 6:
                continue
            cur = {}
            if ka > 0 and (ka - 1, kc) in gap_dp:
                for (sa, sc, qac), cnt in gap_dp[(ka - 1, kc)].items():
                    for r in P.COUPLINGS:
                        key = (sa ^ r, sc, qac ^ P.MULT[sc][r])
                        cur[key] = cur.get(key, 0) + cnt
            if kc > 0 and (ka, kc - 1) in gap_dp:
                for (sa, sc, qac), cnt in gap_dp[(ka, kc - 1)].items():
                    for r in P.COUPLINGS:
                        key = (sa, sc ^ r, qac ^ P.MULT[sa][r])
                        cur[key] = cur.get(key, 0) + cnt
            gap_dp[(ka, kc)] = cur

    gap_qac = {}
    for (ka, kc), d in gap_dp.items():
        by_s = {}
        for (sa, sc, qac), cnt in d.items():
            by_s.setdefault((sa, sc), []).append((qac, cnt))
        for (sa, sc), lst in by_s.items():
            gap_qac[(ka, kc, sa, sc)] = tuple(sorted(lst))
    return gap_qac


def build_three_role_tables(P, srank):
    a_choices_I = []
    c_choices_I = []
    a_choices_II = []
    c_choices_II = []
    for n in P.COUPLINGS:
        x, y = P.SPLIT[n]
        x_col = (x & 1) | ((x >> 1) << 2)
        a_choices_I.append((n, 0, 0))
        a_choices_I.append((n, y, 1))
        c_choices_I.append((n, 0, 0))
        c_choices_I.append((n, x_col, 1))
        a_choices_II.append((n, 0, 0))
        a_choices_II.append((n, x_col, 1))
        c_choices_II.append((n, 0, 0))
        c_choices_II.append((n, y, 1))
    for v in (1, 2, 3):
        v_col = (v & 1) | ((v >> 1) << 2)
        a_choices_I.append((0, v, 1))
        c_choices_I.append((0, v_col, 1))
        a_choices_II.append((0, v_col, 1))
        c_choices_II.append((0, v, 1))

    def build_gap_dirty(choices):
        gap_d = {0: {0: ((0, 0, 1),)}}
        dp_cur = {(0, 0, 0): 1}
        for k in range(1, 4):
            nxt = {}
            for (s, w, hu), cnt in dp_cur.items():
                for n, dw, du in choices:
                    key = (s ^ n, w ^ dw, hu | du)
                    nxt[key] = nxt.get(key, 0) + cnt
            dp_cur = nxt
            by_s = {}
            for (s, w, hu), cnt in dp_cur.items():
                by_s.setdefault(s, []).append((w, hu, cnt))
            gap_d[k] = {s: tuple(sorted(v)) for s, v in by_s.items()}
        return gap_d

    def build_joint_dp(a_ch, c_ch, is_case_I):
        joint_dp = {(0, 0): {(0, 0, 0, 0, 0): 1}}
        for tot in range(1, 5):
            for ka in range(tot + 1):
                kc = tot - ka
                if ka > 3 or kc > 3:
                    continue
                cur = {}
                if ka > 0 and (ka - 1, kc) in joint_dp:
                    for (sa, da, sc, dc, qac), cnt in joint_dp[(ka - 1, kc)].items():
                        for na, dna, _ in a_ch:
                            extra = P.MULT[dc][dna] if is_case_I else 0
                            key = (sa ^ na, da ^ dna, sc, dc, qac ^ P.MULT[sc][na] ^ extra)
                            cur[key] = cur.get(key, 0) + cnt
                if kc > 0 and (ka, kc - 1) in joint_dp:
                    for (sa, da, sc, dc, qac), cnt in joint_dp[(ka, kc - 1)].items():
                        for nc, dnc, _ in c_ch:
                            extra = 0 if is_case_I else P.MULT[da][dnc]
                            key = (sa, da, sc ^ nc, dc ^ dnc, qac ^ P.MULT[sa][nc] ^ extra)
                            cur[key] = cur.get(key, 0) + cnt
                joint_dp[(ka, kc)] = cur
        gap_qac3 = {}
        for (ka, kc), d in joint_dp.items():
            by_s = {}
            for (sa, da, sc, dc, qac), cnt in d.items():
                by_s.setdefault((sa, da, sc, dc), []).append((qac, cnt))
            for k, lst in by_s.items():
                gap_qac3[(ka, kc) + k] = tuple(sorted(lst))
        return gap_qac3

    return {
        'I': (a_choices_I, c_choices_I, build_gap_dirty(a_choices_I),
              build_gap_dirty(c_choices_I), build_joint_dp(a_choices_I, c_choices_I, True)),
        'II': (a_choices_II, c_choices_II, build_gap_dirty(a_choices_II),
               build_gap_dirty(c_choices_II), build_joint_dp(a_choices_II, c_choices_II, False)),
    }


def outer_inventories(P, srank):
    dp = {0: 1}
    zero_seqs = {}
    for step in range(1, 7):
        nxt = {}
        for s, cnt in dp.items():
            for c in P.COUPLINGS:
                nxt[s ^ c] = nxt.get(s ^ c, 0) + cnt
        dp = nxt
        if step in (4, 5, 6):
            zero_seqs[step] = dp[0]
    hist = [0] * 13
    for p0, p1, p2, p3, p4 in product(range(16), repeat=5):
        r = (srank[p0] + srank[p0 ^ p1] + srank[p1 ^ p2] +
             srank[p2 ^ p3] + srank[p3 ^ p4] + srank[p4])
        hist[r] += 1
    catalogues = {}
    for n in (4, 5, 6):
        catalogues[str(n)] = {
            'zero_sequences': zero_seqs[n],
            'profiles': sum(hist[:n + 1]),
            'realizations': zero_seqs[n] * math.comb(n + 5, n),
        }
    return catalogues, hist


def eval_base_2role(P, middle, sa_g, sc_g):
    a = c = b = ac = ba = bc = acb = bac = 0
    for g in range(6):
        sa, sc = sa_g[g], sc_g[g]
        ac ^= P.MULT[a][sc] ^ P.MULT[c][sa]
        bac ^= P.MULT[ba][sc] ^ P.MULT[bc][sa]
        ba ^= P.MULT[b][sa]
        bc ^= P.MULT[b][sc]
        a ^= sa
        c ^= sc
        if g < 5:
            nb = middle[g]
            acb ^= P.MULT[ac][nb]
            b ^= nb
    return ac, acb, bac


def eval_base_3role_hh(P, middle, sa_g, da_g, sc_g, dc_g, is_case_I):
    a = c = b = ac = ba = bc = acb = bac = 0
    d_pref = 0
    bd_pref = 0
    for g in range(6):
        sa, da, sc, dc = sa_g[g], da_g[g], sc_g[g], dc_g[g]
        cross_d = P.MULT[d_pref][da] if is_case_I else P.MULT[d_pref][dc]
        b_cross_d = P.MULT[bd_pref][da] if is_case_I else P.MULT[bd_pref][dc]
        ac ^= P.MULT[a][sc] ^ P.MULT[c][sa] ^ cross_d
        bac ^= P.MULT[ba][sc] ^ P.MULT[bc][sa] ^ b_cross_d
        ba ^= P.MULT[b][sa]
        bc ^= P.MULT[b][sc]
        bd_step = dc if is_case_I else da
        bd_pref ^= P.MULT[b][bd_step]
        a ^= sa
        c ^= sc
        d_pref ^= bd_step
        if g < 5:
            nb = middle[g]
            acb ^= P.MULT[ac][nb]
            b ^= nb
    return ac, acb, bac


def first_2role_word_for_profile(P, middle, pa, pc, na, nc):
    sa_g = profile_gaps(pa)
    sc_g = profile_gaps(pc)
    srank = tuple(s_rank(P, s) for s in range(16))
    valid_k = {0: (0, 2, 3, 4, 5, 6), 1: (1, 2, 3, 4, 5, 6), 2: (2, 3, 4, 5, 6)}

    def first_split(sg, n):
        res = []
        def rec(g, rem):
            if g == 6:
                return rem == 0
            for k in valid_k[srank[sg[g]]]:
                if k <= rem:
                    res.append(k)
                    if rec(g + 1, rem - k):
                        return True
                    res.pop()
            return False
        require(rec(0, n), 'split must exist')
        return tuple(res)

    def first_seq_for_sum(k, target_s):
        seq = []
        def rec(rem_k, cur_s):
            if rem_k == 0:
                return cur_s == target_s
            for r in P.COUPLINGS:
                seq.append(r)
                if rec(rem_k - 1, cur_s ^ r):
                    return True
                seq.pop()
            return False
        require(rec(k, 0), 'gap sequence must exist')
        return tuple(seq)

    ka_tup = first_split(sa_g, na)
    kc_tup = first_split(sc_g, nc)
    a_ns, a_slots = [], []
    c_ns, c_slots = [], []
    word = []
    for g in range(6):
        aseq = first_seq_for_sum(ka_tup[g], sa_g[g])
        cseq = first_seq_for_sum(kc_tup[g], sc_g[g])
        for r in aseq:
            a_ns.append(r)
            a_slots.append(g)
            word.append(['a', r])
        for r in cseq:
            c_ns.append(r)
            c_slots.append(g)
            word.append(['c', r])
        if g < 5:
            word.append(['b', middle[g]])
    return {
        'middle': list(middle),
        'a_profile': list(pa),
        'c_profile': list(pc),
        'a_realization': [a_ns, a_slots],
        'c_realization': [c_ns, c_slots],
        'word': word,
    }


def first_3role_word(P, middle, pa, pc, r_prof, ka_tup, q_prof, kc_tup, a_ch, c_ch, is_case_I):
    sa_g = profile_gaps(pa)
    sc_g = profile_gaps(pc)
    da_g = profile_gaps(r_prof)
    dc_g = profile_gaps(q_prof)

    def first_dirty_seq(k, target_s, target_d, choices):
        seq = []
        def rec(rem, cs, cd):
            if rem == 0:
                return cs == target_s and cd == target_d
            for n, d, ubit in choices:
                seq.append((n, d, ubit))
                if rec(rem - 1, cs ^ n, cd ^ d):
                    return True
                seq.pop()
            return False
        require(rec(k, 0, 0), 'dirty gap sequence must exist')
        return tuple(seq)

    word = []
    for g in range(6):
        aseq = first_dirty_seq(ka_tup[g], sa_g[g], da_g[g], a_ch)
        cseq = first_dirty_seq(kc_tup[g], sc_g[g], dc_g[g], c_ch)
        for n, d, ubit in aseq:
            if n == 0:
                x2, y2 = (0, d) if is_case_I else ((d & 1) | ((d >> 2) << 1), 0)
            else:
                x2, y2 = P.SPLIT[n]
            x3 = (x2 | (ubit << 2)) if is_case_I else x2
            y3 = y2 if is_case_I else (y2 | (ubit << 2))
            word.append(['a', x3, y3])
        for n, d, vbit in cseq:
            if n == 0:
                x2, y2 = ((d & 1) | ((d >> 2) << 1), 0) if is_case_I else (0, d)
            else:
                x2, y2 = P.SPLIT[n]
            x3 = x2 if is_case_I else (x2 | (vbit << 2))
            y3 = (y2 | (vbit << 2)) if is_case_I else y2
            word.append(['c', x3, y3])
        if g < 5:
            xb, yb = P.SPLIT[middle[g]]
            word.append(['b', xb, yb])
    return {
        'middle': list(middle),
        'a_profile': list(pa),
        'c_profile': list(pc),
        'dirty_a_profile': list(r_prof),
        'dirty_c_profile': list(q_prof),
        'a_gap_counts': list(ka_tup),
        'c_gap_counts': list(kc_tup),
        'word_xy': word,
    }


def run(P, progress=False):
    srank = tuple(s_rank(P, s) for s in range(16))
    catalogues, rank_hist = outer_inventories(P, srank)
    gap_qac = build_two_role_gap_dp(P)
    three_role_tabs = build_three_role_tables(P, srank)

    valid_k_for_type = {0: (0, 2, 3, 4, 5, 6), 1: (1, 2, 3, 4, 5, 6), 2: (2, 3, 4, 5, 6)}
    splits_cache = {}

    def get_splits(stypes, n):
        key = (stypes, n)
        if key not in splits_cache:
            res = []
            def rec(g, rem, cur):
                if g == 6:
                    if rem == 0:
                        res.append(tuple(cur))
                    return
                for k in valid_k_for_type[stypes[g]]:
                    if k <= rem:
                        cur.append(k)
                        rec(g + 1, rem - k, cur)
                        cur.pop()
            rec(0, n, [])
            splits_cache[key] = tuple(res)
        return splits_cache[key]

    def side_row(left, n):
        right = left ^ n
        row = []
        for p in range(16):
            pn, np = P.MULT[p][n], P.MULT[n][p]
            bab = P.MULT[P.MULT[left][p]][n] ^ P.MULT[np][right]
            row.append(pn | (np << 4) | (P.MULT[pn][p] << 8) | (bab << 12))
        return tuple(row)

    key_int_tab = {}
    for j in range(5):
        for n in P.COUPLINGS:
            x, y = P.SPLIT[n]
            row = []
            for p in range(16):
                px = ((p & 1) * (x & 1)) ^ (((p >> 1) & 1) * ((x >> 1) & 1))
                px |= ((((p >> 2) & 1) * (x & 1)) ^ (((p >> 3) & 1) * ((x >> 1) & 1))) << 1
                yp = ((y & 1) * (p & 1)) ^ (((y >> 1) & 1) * ((p >> 2) & 1))
                yp |= (((y & 1) * ((p >> 1) & 1)) ^ (((y >> 1) & 1) * ((p >> 3) & 1))) << 1
                val = (((px & 1) << j) | (((px >> 1) & 1) << (j + 5)) |
                       ((yp & 1) << (j + 10)) | (((yp >> 1) & 1) << (j + 15)))
                row.append(val)
            key_int_tab[(j, n)] = tuple(row)

    left_tab = {}
    right_tab = {}
    for n0 in P.COUPLINGS:
        t0_r = side_row(0, n0)
        k0_r = key_int_tab[(0, n0)]
        for n1 in P.COUPLINGS:
            t1_r = side_row(n0, n1)
            k1_r = key_int_tab[(1, n1)]
            for p2 in range(16):
                lmap, lcnt = {}, {}
                for p0 in range(16):
                    r0 = srank[p0]
                    v0, k0 = t0_r[p0], k0_r[p0]
                    for p1 in range(16):
                        rl = r0 + srank[p0 ^ p1] + srank[p1 ^ p2]
                        if rl <= 6:
                            vl = v0 ^ t1_r[p1]
                            lmap.setdefault(vl, []).append((p0, p1, rl, k0 | k1_r[p1]))
                            lcnt[vl] = lcnt.get(vl, 0) + (1 << (8 * rl))
                left_tab[(n0, n1, p2)] = (tuple(lmap.items()), lcnt)

    for n4 in P.COUPLINGS:
        t4_r = side_row(n4, n4)
        k4_r = key_int_tab[(4, n4)]
        for n3 in P.COUPLINGS:
            t3_r = side_row(n3 ^ n4, n3)
            k3_r = key_int_tab[(3, n3)]
            for p2 in range(16):
                rmap, rcnt = {}, {}
                for p3 in range(16):
                    r23 = srank[p2 ^ p3]
                    v3, k3 = t3_r[p3], k3_r[p3]
                    for p4 in range(16):
                        rr = r23 + srank[p3 ^ p4] + srank[p4]
                        if rr <= 6:
                            vr = v3 ^ t4_r[p4]
                            rmap.setdefault(vr, []).append((p3, p4, rr, k3 | k4_r[p4]))
                            rcnt[vr] = rcnt.get(vr, 0) + (1 << (8 * rr))
                right_tab[(n3, n4, p2)] = (rmap, rcnt)

    def unpack_valid_key(k):
        u0, u1, w0, w1 = k & 31, (k >> 5) & 31, (k >> 10) & 31, (k >> 15) & 31
        if not (u0 and u1 and u0 != u1 and w0 and w1 and w0 != w1):
            return None
        return (u0, u1, w0, w1)

    def get_dirty_profs(p, gap_d, cache):
        if p not in cache:
            sg = profile_gaps(p)
            res = set()
            def rec(g, rem_k, cur_r, cur_hu, r_pref, k_tup):
                if g == 6:
                    if rem_k == 0 and cur_r == 0 and cur_hu == 1:
                        res.add((tuple(r_pref), tuple(k_tup)))
                    return
                s = sg[g]
                for k in range(min(3, rem_k) + 1):
                    for w, hu, _ in gap_d[k].get(s, ()):
                        nr = cur_r ^ w
                        k_tup.append(k)
                        if g < 5:
                            r_pref.append(nr)
                            rec(g + 1, rem_k - k, nr, cur_hu | hu, r_pref, k_tup)
                            r_pref.pop()
                        else:
                            rec(g + 1, rem_k - k, nr, cur_hu | hu, r_pref, k_tup)
                        k_tup.pop()
            rec(0, 5, 0, 0, [], [])
            by_r = {}
            for r_pref, k_tup in sorted(res):
                by_r.setdefault(r_pref, []).append(k_tup)
            cache[p] = tuple((r_pref, tuple(ktups)) for r_pref, ktups in sorted(by_r.items()))
        return cache[p]

    dirty_caches = {'I': ({}, {}), 'II': ({}, {})}

    domains = {
        '4,5,4': (4, 4), '5,5,4': (5, 4), '4,5,5': (4, 5),
        '6,5,4': (6, 4), '5,5,5': (5, 5), '4,5,6': (4, 6),
    }
    counts = {
        key: dict(middles=0, a_pass=0, c_pass=0, key_pairs=0,
                  profile_pairs=0, words=0, q_pass=0)
        for key in domains
    }
    failures = {key: defaultdict(int) for key in domains}
    digests = {key: sha256() for key in domains}
    planted_2role = {}

    three_role_stats = {
        mode: dict(active_profile_pairs=0, dirty_profile_pairs=0,
                   words=0, hh_q_pass=0, ac_fail=0, acb_fail=0, bac_fail=0)
        for mode in ('case_I_col_a_row_c', 'case_II_row_a_col_c')
    }
    three_role_digests = {
        mode: sha256() for mode in ('case_I_col_a_row_c', 'case_II_row_a_col_c')
    }
    planted_3role = {}

    for middle in product(P.COUPLINGS, repeat=5):
        if P.total(middle):
            continue
        for key in domains:
            counts[key]['middles'] += 1
        n0, n1, n2, n3, n4 = middle
        t2_r = side_row(n0 ^ n1, n2)
        k2_r = key_int_tab[(2, n2)]
        a_by_n = {4: {}, 5: {}, 6: {}}
        a_counts = [0] * 7
        c_counts = [0] * 7
        for p2 in range(16):
            v2_base = t2_r[p2]
            k2_base = k2_r[p2]
            l_items, lcnt = left_tab[(n0, n1, p2)]
            rmap, rcnt = right_tab[(n3, n4, p2)]
            for vl, l_list in l_items:
                lc = lcnt[vl]
                rc = rcnt.get(vl ^ v2_base, 0)
                if rc:
                    for rl in range(7):
                        c_l = (lc >> (8 * rl)) & 0xff
                        if c_l:
                            for rr in range(7 - rl):
                                c_counts[rl + rr] += c_l * ((rc >> (8 * rr)) & 0xff)
                ra = rmap.get(vl ^ v2_base ^ 0x8888)
                if ra:
                    for p0, p1, rl, kl in l_list:
                        kl2 = kl | k2_base
                        for p3, p4, rr, kr in ra:
                            rtot = rl + rr
                            if rtot <= 6:
                                a_counts[rtot] += 1
                                pk = unpack_valid_key(kl2 | kr)
                                if pk is not None:
                                    prof = (p0, p1, p2, p3, p4)
                                    if rtot <= 4:
                                        a_by_n[4].setdefault(pk, []).append(prof)
                                    if rtot <= 5:
                                        a_by_n[5].setdefault(pk, []).append(prof)
                                    a_by_n[6].setdefault(pk, []).append(prof)
        a_tots = {4: sum(a_counts[:5]), 5: sum(a_counts[:6]), 6: sum(a_counts[:7])}
        c_tots = {4: sum(c_counts[:5]), 5: sum(c_counts[:6]), 6: sum(c_counts[:7])}
        for key, (na, nc) in domains.items():
            counts[key]['a_pass'] += a_tots[na]
            counts[key]['c_pass'] += c_tots[nc]
        if not a_by_n[6]:
            continue
        max_nc = 6 if a_by_n[4] else (5 if a_by_n[5] else 4)
        c_by_n = {4: {}, 5: {}, 6: {}}
        for p2 in range(16):
            v2_base = t2_r[p2]
            k2_base = k2_r[p2]
            l_items, _ = left_tab[(n0, n1, p2)]
            rmap, _ = right_tab[(n3, n4, p2)]
            for vl, l_list in l_items:
                rc_list = rmap.get(vl ^ v2_base)
                if rc_list:
                    for p0, p1, rl, kl in l_list:
                        if rl > max_nc:
                            continue
                        kl2 = kl | k2_base
                        for p3, p4, rr, kr in rc_list:
                            rtot = rl + rr
                            if rtot <= max_nc:
                                pk = unpack_valid_key(kl2 | kr)
                                if pk is not None:
                                    prof = (p0, p1, p2, p3, p4)
                                    if rtot <= 4:
                                        c_by_n[4].setdefault(pk, []).append(prof)
                                    if rtot <= 5 and max_nc >= 5:
                                        c_by_n[5].setdefault(pk, []).append(prof)
                                    if max_nc >= 6:
                                        c_by_n[6].setdefault(pk, []).append(prof)

        for n in (4, 5, 6):
            for k in a_by_n[n]:
                a_by_n[n][k].sort()
            for k in c_by_n[n]:
                c_by_n[n][k].sort()

        b_pref = (0, middle[0], middle[0] ^ middle[1],
                  middle[0] ^ middle[1] ^ middle[2],
                  middle[0] ^ middle[1] ^ middle[2] ^ middle[3], 0)

        for key, (na, nc) in domains.items():
            if not a_by_n[na] or not c_by_n[nc]:
                continue
            counter = counts[key]
            a_dict, c_dict = a_by_n[na], c_by_n[nc]
            for ka, kc in sorted(P.compatible_keys(a_dict, c_dict)):
                counter['key_pairs'] += 1
                for pa, pc in product(a_dict[ka], c_dict[kc]):
                    counter['profile_pairs'] += 1
                    sa_g = profile_gaps(pa)
                    sc_g = profile_gaps(pc)
                    sa_t = tuple(srank[s] for s in sa_g)
                    sc_t = tuple(srank[s] for s in sc_g)
                    base_ac, base_acb, base_bac = eval_base_2role(P, middle, sa_g, sc_g)
                    pair_words = pair_ac = pair_acb = 0
                    for ka_tup in get_splits(sa_t, na):
                        for kc_tup in get_splits(sc_t, nc):
                            g_lists = [gap_qac[(ka_tup[g], kc_tup[g], sa_g[g], sc_g[g])] for g in range(6)]
                            for q0, w0 in g_lists[0]:
                                for q1, w1 in g_lists[1]:
                                    w01 = w0 * w1
                                    ac1 = base_ac ^ q0 ^ q1
                                    acb1 = base_acb ^ P.MULT[q1][b_pref[1]]
                                    bac1 = base_bac ^ P.MULT[b_pref[1]][q1]
                                    for q2, w2 in g_lists[2]:
                                        w02 = w01 * w2
                                        ac2 = ac1 ^ q2
                                        acb2 = acb1 ^ P.MULT[q2][b_pref[2]]
                                        bac2 = bac1 ^ P.MULT[b_pref[2]][q2]
                                        for q3, w3 in g_lists[3]:
                                            w03 = w02 * w3
                                            ac3 = ac2 ^ q3
                                            acb3 = acb2 ^ P.MULT[q3][b_pref[3]]
                                            bac3 = bac2 ^ P.MULT[b_pref[3]][q3]
                                            for q4, w4 in g_lists[4]:
                                                w04 = w03 * w4
                                                ac4 = ac3 ^ q4
                                                acb4 = acb3 ^ P.MULT[q4][b_pref[4]]
                                                bac4 = bac3 ^ P.MULT[b_pref[4]][q4]
                                                for q5, w5 in g_lists[5]:
                                                    w = w04 * w5
                                                    ac = ac4 ^ q5
                                                    pair_words += w
                                                    if ac != 0:
                                                        pair_ac += w
                                                    elif acb4 != 9:
                                                        pair_acb += w
                                                    else:
                                                        require(bac4 != 9, 'unexpected 2-role quotient survivor: ' + key)
                                                        failures[key]['bac'] += w
                    counter['words'] += pair_words
                    failures[key]['ac'] += pair_ac
                    failures[key]['acb'] += pair_acb
                    digests[key].update(
                        P.canonical([list(middle), list(pa), list(pc), pair_words, pair_ac, pair_acb]) + b'\n'
                    )
                    if key in ('6,5,4', '5,5,5', '4,5,6') and key not in planted_2role:
                        planted_2role[key] = first_2role_word_for_profile(P, middle, pa, pc, na, nc)

                    if key == '5,5,5':
                        for tag, mode_name, is_case_I in (
                            ('I', 'case_I_col_a_row_c', True),
                            ('II', 'case_II_row_a_col_c', False),
                        ):
                            a_ch, c_ch, gap_da, gap_dc, gap_qac3 = three_role_tabs[tag]
                            da_cache, dc_cache = dirty_caches[tag]
                            st3 = three_role_stats[mode_name]
                            st3['active_profile_pairs'] += 1
                            valid_da = []
                            for da_prof, ka_tups in get_dirty_profs(pa, gap_da, da_cache):
                                v1 = v2 = v3 = 0
                                for j in range(5):
                                    if is_case_I:
                                        rn = P.MULT[da_prof[j]][middle[j]]
                                        v1 ^= rn
                                        v2 ^= P.MULT[rn][pa[j]]
                                        v3 ^= P.MULT[rn][pc[j]]
                                    else:
                                        nq = P.MULT[middle[j]][da_prof[j]]
                                        v1 ^= nq
                                        v2 ^= P.MULT[pa[j]][nq]
                                        v3 ^= P.MULT[pc[j]][nq]
                                if v1 == 0 and v2 == 0 and v3 == 0:
                                    valid_da.append((da_prof, ka_tups))
                            if not valid_da:
                                continue
                            valid_dc = []
                            for dc_prof, kc_tups in get_dirty_profs(pc, gap_dc, dc_cache):
                                v1 = v2 = v3 = 0
                                for j in range(5):
                                    if is_case_I:
                                        nq = P.MULT[middle[j]][dc_prof[j]]
                                        v1 ^= nq
                                        v2 ^= P.MULT[pc[j]][nq]
                                        v3 ^= P.MULT[pa[j]][nq]
                                    else:
                                        rn = P.MULT[dc_prof[j]][middle[j]]
                                        v1 ^= rn
                                        v2 ^= P.MULT[rn][pc[j]]
                                        v3 ^= P.MULT[rn][pa[j]]
                                if v1 == 0 and v2 == 0 and v3 == 0:
                                    valid_dc.append((dc_prof, kc_tups))
                            if not valid_dc:
                                continue
                            for da_prof, ka_tups in valid_da:
                                da_g = profile_gaps(da_prof)
                                for dc_prof, kc_tups in valid_dc:
                                    dc_g = profile_gaps(dc_prof)
                                    st3['dirty_profile_pairs'] += 1
                                    b_ac, b_acb, b_bac = eval_base_3role_hh(
                                        P, middle, sa_g, da_g, sc_g, dc_g, is_case_I
                                    )
                                    dp_words = dp_ac = dp_acb = 0
                                    for ka_tup in ka_tups:
                                        for kc_tup in kc_tups:
                                            g_lists = [
                                                gap_qac3[(ka_tup[g], kc_tup[g], sa_g[g], da_g[g], sc_g[g], dc_g[g])]
                                                for g in range(6)
                                            ]
                                            for q0, w0 in g_lists[0]:
                                                for q1, w1 in g_lists[1]:
                                                    w01 = w0 * w1
                                                    ac1 = b_ac ^ q0 ^ q1
                                                    acb1 = b_acb ^ P.MULT[q1][b_pref[1]]
                                                    bac1 = b_bac ^ P.MULT[b_pref[1]][q1]
                                                    for q2, w2 in g_lists[2]:
                                                        w02 = w01 * w2
                                                        ac2 = ac1 ^ q2
                                                        acb2 = acb1 ^ P.MULT[q2][b_pref[2]]
                                                        bac2 = bac1 ^ P.MULT[b_pref[2]][q2]
                                                        for q3, w3 in g_lists[3]:
                                                            w03 = w02 * w3
                                                            ac3 = ac2 ^ q3
                                                            acb3 = acb2 ^ P.MULT[q3][b_pref[3]]
                                                            bac3 = bac2 ^ P.MULT[b_pref[3]][q3]
                                                            for q4, w4 in g_lists[4]:
                                                                w04 = w03 * w4
                                                                ac4 = ac3 ^ q4
                                                                acb4 = acb3 ^ P.MULT[q4][b_pref[4]]
                                                                bac4 = bac3 ^ P.MULT[b_pref[4]][q4]
                                                                for q5, w5 in g_lists[5]:
                                                                    w = w04 * w5
                                                                    ac = ac4 ^ q5
                                                                    dp_words += w
                                                                    if ac != 0:
                                                                        dp_ac += w
                                                                    elif acb4 != 9:
                                                                        dp_acb += w
                                                                    else:
                                                                        require(bac4 != 9, 'unexpected 3-role survivor')
                                                                        st3['bac_fail'] += w
                                    st3['words'] += dp_words
                                    st3['ac_fail'] += dp_ac
                                    st3['acb_fail'] += dp_acb
                                    three_role_digests[mode_name].update(
                                        P.canonical([
                                            list(middle), list(pa), list(pc),
                                            list(da_prof), list(dc_prof),
                                            dp_words, dp_ac, dp_acb,
                                        ]) + b'\n'
                                    )
                                    if mode_name not in planted_3role:
                                        planted_3role[mode_name] = first_3role_word(
                                            P, middle, pa, pc, da_prof, ka_tups[0],
                                            dc_prof, kc_tups[0], a_ch, c_ch, is_case_I
                                        )

        if progress and counts['4,5,4']['middles'] % 900 == 0:
            print('Checked middle sequences:', counts['4,5,4']['middles'], flush=True)

    for key in domains:
        counts[key]['profile_pair_digest_sha256'] = digests[key].hexdigest()
        counts[key]['first_differing_coefficient'] = dict(sorted(failures[key].items()))

    for mode_name, st3 in three_role_stats.items():
        st3['first_differing_hh_coefficient'] = {'ac': st3.pop('ac_fail'), 'acb': st3.pop('acb_fail')}
        bac_f = st3.pop('bac_fail')
        if bac_f:
            st3['first_differing_hh_coefficient']['bac'] = bac_f
        st3['dirty_pair_digest_sha256'] = three_role_digests[mode_name].hexdigest()

    return {
        'outer_catalogues': catalogues,
        'profile_rank_sum_histogram': rank_hist,
        'domains': counts,
        'three_role_555': three_role_stats,
        'planted_controls': {
            'two_role': planted_2role,
            'three_role_555': planted_3role,
        },
    }
