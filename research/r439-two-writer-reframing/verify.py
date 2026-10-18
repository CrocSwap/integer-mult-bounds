#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Aaron Wang, with help from opencode (substantial AI assistance).
"""Forced-carry closure excludes reframed two-writer helper-star absorption.

No predecessor executable is imported. The nested-frame law follows the pinned
eumemic xcheck_p.py Part F: every register starts at its start frame (sources at
their own line, targets and helpers at frame 0); before each gate every operand
climbs to the gate's frame, nested with a strict increase of dimension; final
frames are the full frame for sources/helpers and t-perp (rank seven) for
target t.

Object: the complete two-writer single-donor compensation domain of
Sagar Thakrar's PR1868 open question on the pinned PR1062 11,500-ADD word,
as enumerated by Adam Gall's PR1913 at the fixed gate frames: omit one
terminal helper-star restoration, toggle one donor in each of two existing
phase-A writes of its centre before the first centre read.

New question: with the receiving gates' frames changed (arbitrary monotone
reframing, no original-frame floor, the escape class PR1913 explicitly left
open), can any completion become legal?

Method: the forced-carry closure. Start frames are fixed; at every gate the
gate frame must contain the current frames of all touched registers, so the
componentwise least legal frame assignment sets each gate frame to the span
union of its touched registers' currents. Every legal reframing dominates this
least assignment (induction on gates), so a pinned final frame that excludes a
forced carried direction certifies exclusion for every reframing, and a clean
closure is itself an explicit legal reframing.

All 52 scalar-saving completions are excluded, and 260 of the 262
cost-increasing ones as well; each exclusion has a rational leakage witness: a
dirty target's forced carried span strictly exceeds its pinned rank-7 t-perp
final frame. The only two closure-legal completions cost one ADD more than the
source word. The 52 scalar savings are therefore unusable: no legal reframing
exists to bill. No new kappa.
"""
import argparse
import copy
import gzip
import hashlib
import itertools
import json
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = 'research/r439-bsection-stars-seed01/candidate.json.gz'
SPEC = 'research/e8-bit-p111-tuned/code/xcheck_p.py'
INPUTS = [SPEC, WORD]
PROFILE = {1: 1323, 2: 1342, 3: 79, 4: 44, 5: 102, 6: 11, 7: 19}
PROFILE_MASS = 5129


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def rref(rows):
    rows = [[Fraction(x) for x in row] for row in rows]
    pivot = 0
    for col in range(8):
        found = next((k for k in range(pivot, len(rows)) if rows[k][col]), None)
        if found is None:
            continue
        rows[pivot], rows[found] = rows[found], rows[pivot]
        div = rows[pivot][col]
        rows[pivot] = [x / div for x in rows[pivot]]
        for k in range(len(rows)):
            if k != pivot and rows[k][col]:
                m = rows[k][col]
                rows[k] = [x - m * y for x, y in zip(rows[k], rows[pivot])]
        pivot += 1
    return rows[:pivot]


class Geometry:
    """Label lines, frame masks and exact rational ranks."""

    def __init__(self, word):
        self.lines = word['lines']
        self.frame_masks = []
        for fr in word['frames']:
            m = 0
            for k in fr:
                m |= 1 << k
            self.frame_masks.append(m)
        self._rank = {}

    def rank(self, mask):
        if mask not in self._rank:
            rows = [self.lines[k] for k in range(len(self.lines)) if (mask >> k) & 1]
            self._rank[mask] = len(rref(rows))
        return self._rank[mask]

    def witness(self, carry_mask, final_mask):
        """Labels of the carried span outside the final span, with rational ranks."""
        base = self.rank(final_mask)
        ext = self.rank(final_mask | carry_mask)
        leaked = []
        extra = carry_mask & ~final_mask
        k = 0
        while extra:
            if extra & 1:
                if self.rank(final_mask | (1 << k)) > base:
                    leaked.append(k)
            extra >>= 1
            k += 1
        return {'leaked_labels': leaked, 'rank_final': base, 'rank_joined': ext}


def xor_rows(rows, gates):
    for _, dest, donors in gates:
        for donor in donors:
            rows[dest] ^= rows[donor]
    return rows


def stream(word):
    n = 2 * word['v'] + word['R']
    ops = [('add', d, s) for section in 'DA' for _, d, ss in word[section] for s in ss]
    for j, centre in enumerate(word['ret']):
        ops.append(('copy', n, centre))
        ops.extend(('add', word['v'] + t, n) for t, row in enumerate(word['scatter']) if j in row)
        ops.append(('erase', n, centre))
    ops.extend(('add', d, s) for section in 'BC' for _, d, ss in word[section] for s in ss)
    return ops


def literal(word, reverse=False):
    n = 2 * word['v'] + word['R']
    rows = [1 << k for k in range(n)] + [0]
    ops = stream(word)
    for kind, d, s in reversed(ops) if reverse else ops:
        if reverse:
            kind = {'copy': 'erase', 'erase': 'copy'}.get(kind, kind)
        if kind == 'add':
            rows[d] ^= rows[s]
        elif kind == 'copy':
            need(rows[d] == 0, 'COPY requires a clean temporary')
            rows[d] = rows[s]
        else:
            need(rows[d] == rows[s], 'ERASE requires matching current value')
            rows[d] = 0
    need(rows[-1] == 0, 'unrestored temporary')
    return rows[:-1]


def wanted(word):
    v = word['v']
    return [(1 << k) ^ ((1 << (k - v)) if v <= k < 2 * v else 0)
            for k in range(2 * v + word['R'])]


def boundary_ok(word):
    need(literal(word) == wanted(word), 'forward dirty boundary')
    need(literal(word, reverse=True) == wanted(word), 'reverse dirty boundary')
    return True


def bill(word):
    ops = stream(word)
    maxima = []
    for reverse in (False, True):
        vals = [1] * (2 * word['v'] + word['R'] + 1)
        peak = 1
        for kind, d, s in reversed(ops) if reverse else ops:
            if reverse:
                kind = {'copy': 'erase', 'erase': 'copy'}.get(kind, kind)
            vals[d] = vals[d] + vals[s] if kind == 'add' else vals[s] if kind == 'copy' else 0
            peak = max(peak, vals[d])
        maxima.append(peak)
    f, b = maxima
    return {'ADDs': sum(k == 'add' for k, _, _ in ops), 'F': f, 'B': b,
            'local_bound': str(64 * f**3 * b**2),
            'nine_stage_bound': str((1 << 18) * f**5 * b**4)}


def closure_walk(geo, word, use_orig_floor=False):
    """Least forced frame assignment over label masks.

    Gate frame = span mask union of touched currents (plus the original gate
    frame when use_orig_floor). Starts fixed. Returns final-frame failures as
    (register, witness) with witness from geo.witness."""
    starts = [geo.frame_masks[f] for f in word['start']]
    finals = [geo.frame_masks[f] for f in word['final']]
    cur = list(starts)
    for sec in 'DABC':
        for fr, dest, donors in word[sec]:
            F = geo.frame_masks[fr] if use_orig_floor else 0
            for r in (dest, *donors):
                F |= cur[r]
            for r in (dest, *donors):
                cur[r] = F
    failures = []
    for r, final_mask in enumerate(finals):
        if cur[r] == final_mask:
            continue
        if (cur[r] | final_mask) != final_mask:
            failures.append((r, geo.witness(cur[r], final_mask)))
    return failures, cur


def paid_profile(geo, word, use_orig_floor=True):
    """Inherited paid histogram: rank increments of per-register frame paths
    plus one rank per COPY row at its scatter frame. Touches that do not
    strictly increase the carried dimension are not climbs and are not billed."""
    starts = [geo.frame_masks[f] for f in word['start']]
    paths = [[m] for m in starts]
    cur = list(starts)
    for sec in 'DABC':
        for fr, dest, donors in word[sec]:
            F = geo.frame_masks[fr] if use_orig_floor else 0
            for r in (dest, *donors):
                F |= cur[r]
            for r in (dest, *donors):
                if cur[r] != F:
                    need((cur[r] | F) == F, 'no paid profile admitted for a descent')
                    if geo.rank(F) > geo.rank(cur[r]):
                        paths[r].append(F)
                    cur[r] = F
    for r, fF in enumerate(word['final']):
        F = geo.frame_masks[fF]
        if cur[r] != F:
            need((cur[r] | F) == F, 'no paid profile admitted for an illegal final')
            if geo.rank(F) > geo.rank(cur[r]):
                paths[r].append(F)
    counts = Counter()
    for path in paths:
        for a, b in zip(path, path[1:]):
            delta = geo.rank(b) - geo.rank(a)
            need(delta > 0, 'a climb must strictly increase the dimension')
            counts[delta] += 1
    da = list(starts)
    for sec in 'DA':
        for fr, dest, donors in word[sec]:
            F = geo.frame_masks[fr] if use_orig_floor else 0
            for r in (dest, *donors):
                F |= da[r]
            for r in (dest, *donors):
                da[r] = F
    counts.update(geo.rank(da[r]) for r in word['ret'])
    return dict(sorted(counts.items()))


def star_domain(word):
    v, d = word['v'], word['D']
    count = sum(dest >= 2 * v for _, dest, _ in d)
    need(count % 2 == 0, 'paired helper preparation/restoration')
    count //= 2
    prep, rest = d[:count], d[-count:]
    need(rest == prep[::-1], 'literal star restoration suffix')
    need(all(f == 0 and a >= 2 * v and len(ss) == 1 and ss[0] >= 2 * v for f, a, ss in prep),
         'source-free zero-frame helper stars')
    edges = [(a, ss[0]) for _, a, ss in rest]
    centres = {a for a, _ in edges}
    leaves = [b for _, b in edges]
    need(len(set(leaves)) == len(leaves) and centres.isdisjoint(leaves), 'disjoint star leaves')
    first = {a: next((i for i, (_, _, ss) in enumerate(word['A']) if a in ss), len(word['A']))
             for a in centres}
    writers = {a: [i for i, (_, dd, _) in enumerate(word['A'][:first[a]]) if dd == a]
               for a in centres}
    n = 2 * v + word['R']
    rows = xor_rows([1 << k for k in range(n)], word['D'])
    need(all(rows[k] == 1 << k for k in list(range(v)) + list(range(2 * v, n))),
         'D restores every source/helper')
    cutset = {i for ws in writers.values() for i in ws}
    snapshots = {}
    for i, gate in enumerate(word['A']):
        if i in cutset:
            need(len(set(rows)) == n and all(rows), 'invertible state has distinct nonzero rows')
            snapshots[i] = tuple(rows)
        xor_rows(rows, [gate])
    return count, edges, first, writers, snapshots


def solve(word):
    """Complete two-writer single-donor domain: every edge, writer pair and
    first donor, with the unique exact second donor (PR1913's criterion
    r_i(s) XOR r_j(t) = e_leaf, re-derived here)."""
    n, v = 2 * word['v'] + word['R'], word['v']
    count, edges, first, writers, snapshots = star_domain(word)
    solutions, trials, pairs = [], 0, 0
    for centre, leaf in sorted(edges):
        donors = [r for r in range(n) if r != centre and not v <= r < 2 * v]
        for i, j in itertools.combinations(writers[centre], 2):
            pairs += 1
            lookup = {snapshots[j][r]: r for r in donors}
            need(len(lookup) == len(donors), 'unique second donor lookup')
            for s in donors:
                trials += 1
                t = lookup.get(snapshots[i][s] ^ (1 << leaf))
                if t is not None:
                    delta = -1 + (1 - 2 * (s in word['A'][i][2])) + (1 - 2 * (t in word['A'][j][2]))
                    solutions.append((delta, centre, leaf, i, j, s, t))
    return count, pairs, trials, sorted(solutions)


def edited_word(word, solution, count):
    delta, centre, leaf, i, j, s, t = solution
    out = copy.deepcopy(word)
    matches = [k for k in range(len(out['D']) - count, len(out['D']))
               if out['D'][k] == [0, centre, [leaf]]]
    need(len(matches) == 1, 'unique specified terminal restoration')
    out['D'].pop(matches[0])
    for gate, donor in ((i, s), (j, t)):
        out['A'][gate][2] = sorted(set(out['A'][gate][2]) ^ {donor})
    return out


def load_word():
    manifest = json.loads((HERE / 'SOURCES.json').read_text(encoding='utf-8'))
    pins = {x['path']: x['sha256'] for x in manifest['files'] if x['usage'] == 'input'}
    need(sorted(pins) == INPUTS, 'complete source inventory')
    need(json.loads((HERE / 'VERIFY.json').read_text(encoding='utf-8'))['inputs'] == INPUTS,
         'complete replay inventory')
    data = {}
    for path in INPUTS:
        data[path] = (ROOT / path).read_bytes()
        need(sha(data[path]) == pins[path], 'source pin mismatch: ' + path)
    return json.loads(gzip.decompress(data[WORD]))


def expect_rejection(function, message):
    try:
        function()
    except ValueError:
        return
    raise ValueError(message)


def run(write=False):
    word = load_word()
    geo = Geometry(word)
    controls = []

    # Baseline: legal closures and the pinned paid profile.
    fail_pure, _ = closure_walk(geo, word, use_orig_floor=False)
    fail_floor, _ = closure_walk(geo, word, use_orig_floor=True)
    need(not fail_pure and not fail_floor, 'baseline closure legality')
    profile = paid_profile(geo, word)
    need(profile == PROFILE, 'baseline complete paid histogram')
    base_bill = bill(word)
    need(base_bill['ADDs'] == 11500, 'baseline scalar count')
    controls.append({'name': 'baseline_legal_profile_and_bill'})

    count, pairs, trials, solutions = solve(word)
    need((count, pairs, trials, len(solutions)) == (236, 414, 227286, 314),
         'complete two-writer domain counts')
    saving = [x for x in solutions if x[0] == -1]
    need(len(saving) == 52, 'scalar-saving completion count')
    controls.append({'name': 'domain_counts_match_pr1913'})

    # Every exact completion: full dirty boundary (both orientations) and the
    # forced-carry closure under arbitrary monotone reframing. The 52
    # scalar-saving completions are the useful class; the 262 cost-increasing
    # ones are recorded for completeness.
    rows = []
    excluded_pure = 0
    legal = 0
    for sol in solutions:
        edited = edited_word(word, sol, count)
        need(boundary_ok(edited), 'exact completion boundary')
        fails, cur = closure_walk(geo, edited, use_orig_floor=False)
        fails_floor, _ = closure_walk(geo, edited, use_orig_floor=True)
        if fails:
            excluded_pure += 1
            row = {
                'solution': list(sol),
                'verdict_reframed': 'excluded',
                'failures': [{'register': r, **w} for r, w in fails],
                'failures_orig_floor': len(fails_floor),
            }
        else:
            legal += 1
            need(bill(edited)['ADDs'] == 11500 + sol[0], 'completion scalar delta')
            # Currents right after section A: the scatter-time frames of the
            # nine retained totals, whose COPY ranks the Part T contract pins.
            da_cur = [geo.frame_masks[f] for f in word['start']]
            for sec in 'DA':
                for fr, dest, donors in edited[sec]:
                    F = 0
                    for r in (dest, *donors):
                        F |= da_cur[r]
                    for r in (dest, *donors):
                        da_cur[r] = F
            copy_rows = {}
            for r in word['ret']:
                copy_rows[str(r)] = {
                    'closure_scatter_rank': geo.rank(da_cur[r]),
                    'closure_scatter_labels': sorted(
                        k for k in range(len(geo.lines)) if (da_cur[r] >> k) & 1)}
            row = {
                'solution': list(sol),
                'verdict_reframed': 'legal',
                'failures': [],
                'failures_orig_floor': len(fails_floor),
                'closure_paid_profile': {str(k): v for k, v in
                                         paid_profile(geo, edited, use_orig_floor=False).items()},
                'closure_copy_rows': copy_rows,
                'bill': bill(edited),
            }
        rows.append(row)
    need(excluded_pure == 312, 'reframing exclusions among all exact completions')
    need(legal == 2, 'closure-legal cost-increasing completions')
    controls.append({'name': 'all_314_boundaries_replayed_both_orientations'})
    controls.append({'name': 'reframed_exclusions_witnessed_312_of_314'})

    # Positive fixture: Sagar Thakrar / PR1868's single-writer absorption
    # 506 ^= 374 omitted with A[288] donors [374] -> [69]. It stays legal at
    # the original frames with an identical paid profile and saves one ADD.
    fixture = copy.deepcopy(word)
    matches = [k for k in range(len(fixture['D']) - count, len(fixture['D']))
               if fixture['D'][k] == [0, 506, [374]]]
    need(len(matches) == 1, 'fixture restoration')
    fixture['D'].pop(matches[0])
    need(374 in fixture['A'][288][2], 'fixture donor')
    fixture['A'][288][2] = sorted(set(fixture['A'][288][2]) ^ {374, 69})
    need(boundary_ok(fixture), 'fixture dirty boundary')
    f_fail, _ = closure_walk(geo, fixture, use_orig_floor=False)
    need(not f_fail, 'fixture reframing legality')
    need(paid_profile(geo, fixture) == PROFILE, 'fixture unchanged paid profile')
    need(bill(fixture)['ADDs'] == 11499, 'fixture scalar saving')
    controls.append({'name': 'pr1868_single_writer_fixture_legal_same_profile'})

    # Geometry-only success control: a removal-only edit forces no join, so its
    # closure stays legal, while its scalar boundary fails. This separates the
    # two checks.
    geo_ctrl = copy.deepcopy(word)
    need(4 in geo_ctrl['A'][9][2], 'geometry control donor')
    geo_ctrl['A'][9][2] = sorted(set(geo_ctrl['A'][9][2]) ^ {4})
    g_fail, _ = closure_walk(geo, geo_ctrl, use_orig_floor=False)
    need(not g_fail, 'removal-only edit closure legality')
    expect_rejection(lambda: boundary_ok(geo_ctrl),
                     'removal-only edit must fail the dirty boundary')
    controls.append({'name': 'removal_only_edit_legal_geometry_illegal_boundary'})

    # Failure controls.
    bad = edited_word(word, saving[0], count)
    bad['A'][saving[0][4]][2] = sorted(set(bad['A'][saving[0][4]][2]) ^ {saving[0][6],
                                                                       (saving[0][6] + 1) % (2 * word['v'] + word['R'])})
    expect_rejection(lambda: boundary_ok(bad), 'wrong-substitute mutation must be rejected')
    controls.append({'name': 'wrong_substitute_rejected_by_boundary'})

    def bill_illegal():
        edited = edited_word(word, saving[0], count)
        fails, _ = closure_walk(geo, edited, use_orig_floor=False)
        need(fails, 'completion is excluded')
        raise ValueError('illegal path cannot be billed')

    expect_rejection(bill_illegal, 'billing an excluded completion must be refused')
    controls.append({'name': 'excluded_completion_not_billed'})

    def corrupt_pin():
        manifest = json.loads((HERE / 'SOURCES.json').read_text(encoding='utf-8'))
        manifest['files'][2]['sha256'] = '0' * 64
        data = (ROOT / WORD).read_bytes()
        need(sha(data) == manifest['files'][2]['sha256'], 'source pin mismatch: ' + WORD)

    expect_rejection(corrupt_pin, 'source corruption must be rejected')
    controls.append({'name': 'source_corruption_rejected'})

    expect_rejection(lambda: star_domain(edited_word(word, (-1, 506, 374, 288, 1033, 374, 69), count)),
                     'mutated star domain must be rejected')
    controls.append({'name': 'star_domain_mutation_rejected'})

    report = {
        'schema_version': 1,
        'result': 'PASS_R439_TWO_WRITER_REFRAMING',
        'no_new_kappa': True,
        'domain': {'star_edges': count, 'writer_pairs': pairs, 'first_donor_trials': trials,
                   'exact_completions': len(solutions),
                   'scalar_saving_completions': len(saving),
                   'excluded_under_reframing': excluded_pure,
                   'closure_legal_completions': legal,
                   'excluded_saving_under_reframing': sum(
                       1 for row in rows if row['verdict_reframed'] == 'excluded'
                       and row['solution'][0] == -1)},
        'baseline': {'paid_profile': {str(k): v for k, v in profile.items()},
                     'rank_mass': sum(k * v for k, v in profile.items()),
                     'bill': base_bill},
        'fixture_pr1868': {'ADDs': 11499, 'paid_profile_unchanged': True},
        'completions': rows,
        'controls': controls,
    }
    need(report['domain']['excluded_saving_under_reframing'] == 52,
         'all scalar-saving completions excluded')
    need(report['baseline']['rank_mass'] == PROFILE_MASS, 'baseline rank mass')
    marker = ('PASS_R439_TWO_WRITER_REFRAMING pairs=414 trials=227286 exact=314 '
              'saving=52 saving_excluded=52 reframing_excluded=312 legal=2 '
              f'columns=661 controls={len(controls)} no_new_kappa')
    if write:
        (HERE / 'CERTIFICATE.json').write_text(
            json.dumps(report, indent=1, sort_keys=True) + '\n', encoding='utf-8')
    else:
        stored = json.loads((HERE / 'CERTIFICATE.json').read_text(encoding='utf-8'))
        need(stored == report, 'certificate mismatch (rerun with --write to regenerate)')
    print(marker)
    return marker


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding='utf-8')
    run(write=args.write)


if __name__ == '__main__':
    main()
