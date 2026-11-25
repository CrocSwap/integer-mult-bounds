#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact finite screen of elementary two-term basis shears on one P104 decoder."""
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
HIT = ROOT / 'research/complex-frame-pair-decoders/inputs/pr717/P104_HIT_flip_3a.txt'
CEILING = ROOT / 'research/complex-local-word-ceiling/ceiling.py'
CLIQUES = [9, 15, 24, 46, 52, 66, 94, 104]
LAMBDAS = [Q(-2), Q(-1), Q(-1, 2), Q(1, 2), Q(1), Q(2), Q(3)]
NONCENTER = {1: 2356, 2: 418, 3: 432, 4: 134, 5: 74}
SELECTED_A = Q(1690054109089, 10**15)
TARGET_A = SELECTED_A * Q(105, 100)


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def read_hit():
    dcols, tcols = [], []
    for line in HIT.read_text().splitlines():
        s = line.strip()
        if s.startswith('d:'):
            dcols.append([Q(int(x)) for x in s[2:].split()])
        elif s.startswith('t:'):
            tcols.append([Q(int(x)) for x in s[2:].split()])
    assert len(dcols) == len(tcols) == 8
    assert all(len(c) == 104 for c in dcols + tcols)
    D = [[dcols[k][p] for k in range(8)] for p in range(104)]
    T = [[tcols[k][p] for k in range(8)] for p in range(104)]
    return D, T


def transpose(M):
    return [list(row) for row in zip(*M)]


def exact(D, T, live, IP):
    for p, i in enumerate(live):
        for q, j in enumerate(live):
            if sum(D[p][k] * T[q][k] for k in range(8)) != 2 * IP[i][j]:
                return False
    return True


def f2_rank(rows):
    basis = {}
    rank = 0
    for x in rows:
        x = int(x)
        while x:
            p = x.bit_length() - 1
            if p in basis:
                x ^= basis[p]
            else:
                basis[p] = x
                rank += 1
                break
    return rank


def term_costs(D, T, live, labels):
    costs = []
    for k in range(8):
        rows = [live[p] for p in range(len(live)) if D[p][k] != 0]
        cols = [live[p] for p in range(len(live)) if T[p][k] != 0]
        colmask = sum(1 << i for i in cols)
        costs.append(f2_rank([labels[i] & colmask for i in rows]))
    return costs


def apply_shear(D, T, i, j, lam):
    """D' = D(I+lam E_ij), T' = T(I-lam E_ji), preserving DT^T."""
    d, t = [row[:] for row in D], [row[:] for row in T]
    for p in range(len(d)):
        d[p][j] += lam * d[p][i]
        t[p][i] -= lam * t[p][j]
    return d, t


def inverse_shear(D, T, i, j, lam):
    return apply_shear(D, T, i, j, -lam)


def columns(M):
    return tuple(tuple(M[p][k] for p in range(len(M))) for k in range(8))


def main():
    # Pairwise-era PR968 model; production verify.py ships the neighborhood enumerator.
    sources = json.loads((HERE / 'SOURCES.json').read_text())
    e8_model = sources['e8_model']
    pinned = ROOT / e8_model['path']
    assert hashlib.sha256(pinned.read_bytes()).hexdigest() == e8_model['sha256'], 'E8 model pin mismatch'
    model = load_module(pinned, 'p104_predecessor_model')
    ceiling = load_module(CEILING, 'p104_exact_ceiling')
    P112 = [i for i in range(model.NL) if i not in model.FRAME0]
    F1 = [P112[q] for q in CLIQUES]
    live = [i for i in range(model.NL) if i not in model.FRAME0 and i not in F1]
    assert len(live) == 104
    labels = [sum(((model.IP[i][j] + 1) & 1) << j for j in range(model.NL)) for i in range(model.NL)]
    D, T = read_hit()
    assert exact(D, T, live, model.IP)
    base_costs = term_costs(D, T, live, labels)
    assert base_costs == [7] * 8
    assert sum(base_costs) == 56
    original_values = sorted({int(x) for M in (D, T) for row in M for x in row})
    assert original_values == [-2, -1, 0, 1, 2]

    # Direct controls: a broken factor fails exactness; the inverse basis move restores the input.
    bad = [row[:] for row in D]
    bad[0][0] += 1
    assert not exact(bad, T, live, model.IP)

    live_bits = tuple(1 << i for i in live)

    def support_mask(v):
        return sum(bit for bit, x in zip(live_bits, v) if x)

    @lru_cache(None)
    def pair_rank_masks(row_mask, col_mask):
        return f2_rank(labels[i] & col_mask for i in range(model.NL) if row_mask >> i & 1)

    def costs_from_masks(row_masks, col_masks):
        return [pair_rank_masks(row_masks[k], col_masks[k]) for k in range(8)]

    @lru_cache(None)
    def priced(hist_tuple, centre):
        profile = dict(NONCENTER)
        for r, n in hist_tuple:
            if r:
                profile[r] = profile.get(r, 0) + n
        lo, hi = ceiling.ceiling(profile, 73, 8 * 104, 9, centre)
        return str(lo), str(hi), lo >= TARGET_A, hi < TARGET_A

    rows = []
    first_states = []
    for i in range(8):
        for j in range(8):
            if i == j:
                continue
            for lam in LAMBDAS:
                d, t = apply_shear(D, T, i, j, lam)
                assert exact(d, t, live, model.IP)
                back_d, back_t = inverse_shear(d, t, i, j, lam)
                assert back_d == D and back_t == T
                costs = term_costs(d, t, live, labels)
                cst = sum(costs)
                assert costs.count(8) == 2 and costs.count(7) == 6 and cst == 58
                hist = tuple(sorted(Counter(costs).items()))
                lo, hi, qualifies, fails = priced(hist, cst)
                assert not (qualifies and fails)
                rows.append(dict(i=i, j=j, lambda_=str(lam), costs=costs, cst=cst,
                                 cost_histogram={str(r): n for r, n in hist},
                                 ceiling_lo=lo, ceiling_hi=hi,
                                 clears_five_percent_gate=qualifies,
                                 below_five_percent_gate=fails))
                dcols, tcols = columns(d), columns(t)
                first_states.append((i, j, lam, dcols, tcols,
                                     tuple(support_mask(v) for v in dcols),
                                     tuple(support_mask(v) for v in tcols)))

    assert len(rows) == 392
    totals = Counter(r['cst'] for r in rows)
    assert totals == Counter({58: 392})
    assert not any(r['clears_five_percent_gate'] for r in rows)

    # One bounded pivot: length-two elementary paths whose term-pair edges touch.
    two_hist = Counter()
    two_hash = hashlib.sha256()
    two_count = same_edge_inverse = restored = nontrivial_cst56 = 0
    original_dcols, original_tcols = columns(D), columns(T)
    for i, j, lam1, dcols, tcols, dmask, tmask in first_states:
        second_edges = [(k, l) for k in range(8) for l in range(8)
                        if k != l and ({k, l} & {i, j})]
        assert len(second_edges) == 26
        for k, l in second_edges:
            for lam2 in LAMBDAS:
                d2 = list(dcols); t2 = list(tcols)
                d2[l] = tuple(x + lam2 * y for x, y in zip(dcols[l], dcols[k]))
                t2[k] = tuple(x - lam2 * y for x, y in zip(tcols[k], tcols[l]))
                dm2 = list(dmask); tm2 = list(tmask)
                dm2[l] = support_mask(d2[l]); tm2[k] = support_mask(t2[k])
                costs = costs_from_masks(dm2, tm2)
                cst = sum(costs)
                two_hist[cst] += 1
                two_count += 1
                two_hash.update(('%d,%d,%s;%d,%d,%s:%s\n' %
                                 (i, j, lam1, k, l, lam2, ','.join(map(str, costs)))).encode())
                if cst == 56:
                    same_edge_inverse += int((k, l) == (i, j) and lam2 == -lam1)
                    returned = tuple(d2) == original_dcols and tuple(t2) == original_tcols
                    restored += int(returned)
                    nontrivial_cst56 += int(not returned)
                    assert returned
                    assert exact([list(row) for row in zip(*d2)],
                                 [list(row) for row in zip(*t2)], live, model.IP)
    assert two_count == 71344
    assert two_hist == Counter({58: 2744, 59: 32928, 60: 35336, 56: 336})
    assert same_edge_inverse == restored == 336 and nontrivial_cst56 == 0
    assert two_hist[57] == 0

    # At the target a, minimize over every eight-term rank profile 0..9. Allowing
    # a zero term makes this an optimistic lower bound for any sheared decoder.
    w = Q(8 * 104, 9)
    idle_mass = 72 * w - sum(r * n for r, n in NONCENTER.items())
    fixed_lo = sum(n * ceiling.child_cost(r, 73, TARGET_A)[0]
                   for r, n in NONCENTER.items())
    fixed_hi = sum(n * ceiling.child_cost(r, 73, TARGET_A)[1]
                   for r, n in NONCENTER.items())
    rank_cost = {0: (Q(0), Q(0))}
    rank_cost.update({r: ceiling.child_cost(r, 73, TARGET_A) for r in range(1, 10)})
    idle_cost = ceiling.child_cost(51, 73, TARGET_A)
    fixed_lo += idle_mass / 51 * idle_cost[0]
    fixed_hi += idle_mass / 51 * idle_cost[1]
    dp = {(0, 0): (Q(0), Q(0), ())}
    for _ in range(8):
        nxt = {}
        for (_, subtotal), (lo, hi, seq) in dp.items():
            for r in range(10):
                total = subtotal + r
                if total > 58:
                    continue
                key = (len(seq) + 1, total)
                value = (lo + rank_cost[r][0], hi + rank_cost[r][1], seq + (r,))
                if key not in nxt or value[0] < nxt[key][0]:
                    nxt[key] = value
        dp = nxt
    rank_profile_screen = {}
    for total in (56, 57, 58):
        lo, hi, seq = dp[(8, total)]
        rank_profile_screen[str(total)] = dict(
            minimum_moment_lower=str((fixed_lo + lo) / w),
            matching_sequence_upper=str((fixed_hi + hi) / w),
            most_favorable_rank_sequence=list(seq),
            fails_target=(fixed_lo + lo) / w > 1)
    assert Q(rank_profile_screen['57']['minimum_moment_lower']) > 1
    assert Q(rank_profile_screen['58']['minimum_moment_lower']) > 1
    # Every added unit raises r^(1-a); cst 57 is the most favorable failed total.
    assert rank_profile_screen['57']['fails_target'] and rank_profile_screen['58']['fails_target']
    baseline_profile = dict(NONCENTER)
    baseline_profile[7] = 8
    baseline_lo, baseline_hi = ceiling.ceiling(baseline_profile, 73, 8 * 104, 9, 56)
    plus21 = dict(baseline_profile); plus21[1] += 21
    plus22 = dict(baseline_profile); plus22[1] += 22
    assert ceiling.relax(plus21, 73, 8 * 104, 9, 56, TARGET_A)[1] < 1
    assert ceiling.relax(plus22, 73, 8 * 104, 9, 56, TARGET_A)[0] > 1

    out = dict(
        status='PASS_P104_TERM_SHEAR_FINITE_SCREEN',
        seed='8be7a2eedea3e46ac14a43b092df843e',
        track='complex-mechanisms', task_id='complex-new-helper-inventory', priority_revision=3,
        base_commit='0b1cccf86e2f5132ed286a26ef0a681a495740ea',
        selected_record_sha256='10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32',
        input_sha256=hashlib.sha256(HIT.read_bytes()).hexdigest(),
        domain=dict(ordered_term_pairs=56, lambdas=[str(x) for x in LAMBDAS], shears=len(rows),
                    coefficient_values=original_values,
                    coverage='all nonzero real entry-cancellation ratios for values in {-2,-1,1,2}, plus generic 3',
                    two_shear=dict(first_paths=392, second_edges_per_first=26,
                                   coefficient_alphabet_each_step=[str(x) for x in LAMBDAS],
                                   total_paths=two_count,
                                   overlap='successive ordered term-pair edges share at least one term index')),
        baseline=dict(costs=base_costs, cst=sum(base_costs),
                      local_profile={str(k): v for k, v in sorted(baseline_profile.items())},
                      ceiling_lo=str(baseline_lo), ceiling_hi=str(baseline_hi),
                      selected_fixed_word_ceiling=str(SELECTED_A), ratio_over_selected=str(baseline_hi / SELECTED_A)),
        screen=dict(target_a=str(TARGET_A), max_extra_rank1_children=21,
                    **{'21_child_moment_upper': str(ceiling.relax(plus21, 73, 8 * 104, 9, 56, TARGET_A)[1]),
                       '22_child_moment_lower': str(ceiling.relax(plus22, 73, 8 * 104, 9, 56, TARGET_A)[0])}),
        results=dict(one_shear_cost_histogram={str(k): totals[k] for k in sorted(totals)},
                     aggregate_term_ranks={str(k): v for k, v in sorted(Counter(c for row in rows for c in row['costs']).items())},
                     count_retaining_cst56=totals[56],
                     count_clearing_five_percent_gate=sum(r['clears_five_percent_gate'] for r in rows),
                     best_cost=min(totals), best_shear_ceiling_lo=str(max(Q(r['ceiling_lo']) for r in rows))),
        two_shear=dict(cost_histogram={str(k): two_hist[k] for k in sorted(two_hist)},
                       sequence_sha256=two_hash.hexdigest(), cst56_count=two_hist[56],
                       cst57_count=two_hist[57], cst58_or_more=sum(v for k, v in two_hist.items() if k >= 58),
                       cst56_same_edge_inverse_count=same_edge_inverse,
                       cst56_restores_original_factorization_count=restored,
                       nontrivial_cst56_count=nontrivial_cst56,
                       rank_profile_screen_at_target=rank_profile_screen),
        controls=dict(base_exact=True, all_shears_exact=True, all_inverse_shears_restore=True,
                      all_two_shear_products_exact_by_inverse_basis_identity=True,
                      cst56_two_shear_cases_are_inverse_moves=True,
                      corrupted_factor_rejected=True, cst56_floor_retained=True),
        shears=rows,
        scope='One elementary rational basis shear, plus one bounded length-two touching-edge extension, on the pinned PR717 P104 decoder. This screen checks exactness, copied-information support ranks and the favorable local moment. It does not schedule term delivery, realize dirty-state restoration, change the selected supplier, or claim a new kappa.'
    )
    assert min(totals) >= 56
    assert out['results']['best_cost'] >= 56
    print('PASS_P104_TERM_SHEAR_FINITE_SCREEN',
          f"one_shears={len(rows)} one_hist={dict(totals)}",
          f"two_shears={two_count} two_hist={dict(two_hist)} cst56_nontrivial={nontrivial_cst56}",
          f"gate_pass={out['results']['count_clearing_five_percent_gate']}",
          f"ceiling={baseline_hi} controls=base,exact,inverse,mutation")
    if '--write' in sys.argv:
        (HERE / 'RESULT.json').write_text(json.dumps(out, indent=2, sort_keys=True) + '\n')
    else:
        saved = json.loads((HERE / 'RESULT.json').read_text())
        assert saved == out, 'saved finite certificate differs from recomputation'


if __name__ == '__main__':
    main()
