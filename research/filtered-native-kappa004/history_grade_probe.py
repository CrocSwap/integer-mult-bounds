#!/usr/bin/env python3
"""Price the support of every source-X term in actual native history.

Unlike a phase-erased G-matrix test, this uses the actual phase-sensitive
native K_G tableau and conjugate raw-dual frame conventions.
Apache-2.0. Substantial OpenAI Codex assistance.
"""
from collections import Counter, defaultdict
from fractions import Fraction as Q
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import json
import sys
import time

from snapshot_probe import load, need

HERE = Path(__file__).resolve().parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--packet', type=Path, required=True)
    ap.add_argument('--output', type=Path, default=HERE/'evidence/history-grades.json')
    args = ap.parse_args()
    root, start = args.packet, time.monotonic()
    source = root/'research/native_contact/SCALED-GLOBAL-CANCEL-WORD.json.gz'
    raw = source.read_bytes()
    w = json.loads(gzip.decompress(raw))
    c = w['canonical']
    sys.path.insert(0, str(root/'research/retained_state_next'))
    kg = load('history_grade_kg', root/'research/retained_state_next/consumer_kg_module.py')
    ce = load('history_grade_ce', kg.CLIFFORD)
    review = load('history_grade_review', root/'research/retained_state_next/review_kg_full_frame_kernel.py')
    group = kg.PhaseGroup(ce, c, True)

    @lru_cache(None)
    def frame(f):
        return review.conjugate(ce, ce.canonical_frame(9, c['frames'][f]))

    @lru_cache(None)
    def grade(f, op, origin):
        actual = frame(c['start'][origin]).adjoint().then(group.ops[op]).then(frame(f))
        return ce.rank([x for x, z, p in actual.tab[9:]])

    rows = [{(i, 0): Q(1)} for i in range(632)]+[{}]
    cur = c['start'][:]+[None]
    all_terms = [set() for _ in range(112)]
    census = [Counter() for _ in range(112)]
    high = []
    peak_row = 0
    observed = 0

    def observe(d, pos):
        nonlocal peak_row, observed
        if cur[d] is None:
            return
        observed += 1
        src = [((i, op), a) for (i, op), a in rows[d].items() if i < 112]
        peak_row = max(peak_row, len(src))
        for (i, op), a in src:
            key = cur[d], op
            if key in all_terms[i]:
                continue
            all_terms[i].add(key)
            g = grade(cur[d], op, i)
            census[i][g] += 1
            if g == 9 and len(high) < 12:
                high.append({'origin': i, 'owner': d, 'after_event': pos,
                             'frame': cur[d], 'native_word': group.word[op],
                             'coefficient': str(a)})

    for i in range(632):
        observe(i, -1)
    for pos, e in enumerate(w['programs']['backward']):
        typ, d = e[0], None
        if typ == 'scalar':
            a, f = e[1:]
            d = a[1][1]+632*(a[1][0] == 'C')
            if a[0] == 'clear':
                need(d == 632, 'Owned clear')
                rows[d], cur[d] = {}, f
            elif a[0] in ('add', 'copy'):
                s = a[2][1]+632*(a[2][0] == 'C')
                need(cur[s] == cur[d] == f, 'Literal scalar frame')
                if a[0] == 'copy':
                    rows[d] = dict(rows[s])
                else:
                    kg.add(rows[d], rows[s], Q(a[3], a[4]))
            else:
                need(a[0] == 'scale', 'Known scalar')
                rows[d] = {k: a0*Q(a[2], a[3]) for k, a0 in rows[d].items() if a[2]*a0}
        elif typ == 'warp':
            d = e[1][1]+632*(e[1][0] == 'C')
            need(cur[d] == e[3], 'Warp frame')
            rows[d] = group.left(group.letters[e[2]], rows[d])
            cur[d] = e[4]
        elif typ in ('climb', 'center'):
            d, old, new, rank = e[2:] if typ == 'climb' else (632+e[1], *e[2:])
            need(cur[d] == old, 'Paid entrance')
            cur[d] = new
        else:
            need(typ in ('phase', 'adapter', 'residual_adapter'), 'Known event')
        if d is not None:
            observe(d, pos)
        if pos and pos % 5000 == 0:
            print('HISTORY', pos, 'grade evaluations', grade.cache_info(),
                  'full-rank witnesses', len(high), flush=True)
    for i in range(632):
        expected = {(i, 0): Q(1)}
        if i < 112:
            expected[i+112, 0] = Q(-1)
        need(rows[i] == expected, 'All 632 independent inputs and helpers')
    need(not rows[632], 'Owned return')
    targets = []
    for i in range(112):
        op = frame(c['start'][i]).adjoint().then(frame(c['final'][112+i]))
        r = ce.rank([x for x, z, p in op.tab[9:]])
        need(r == 9, 'Missing thin-query X coefficient is full rank nine')
        targets.append(r)
    bound = max(max(row) for row in census)
    out = {'status': 'ACTUAL_PHASE_AWARE_NATIVE_HISTORY_SUPPORT_SCREEN',
           'source_sha256': sha256(raw).hexdigest(), 'arbitrary_originals': 632,
           'snapshots_observed': observed, 'unique_physical_source_terms': grade.cache_info().currsize,
           'per_origin_grade_counts': [dict(sorted(row.items())) for row in census],
           'maximum_snapshot_source_grade': bound, 'target_source_grades': targets,
           'rank_nine_term_witnesses': high, 'maximum_row_source_terms': peak_row,
           'all_original_endpoints': True, 'owned_final_zero': True,
           'support_bound_applicable': bound < 9,
           'scope': 'Actual backward native history and the fresh X column of a following thin query. Grade counts alone are not a reconstruction or a general paid-cache lower bound.',
           'new_kappa': False, 'elapsed_seconds': time.monotonic()-start}
    args.output.write_text(json.dumps(out, indent=2)+'\n')
    print(json.dumps({k: out[k] for k in ('status', 'maximum_snapshot_source_grade',
          'unique_physical_source_terms', 'support_bound_applicable', 'elapsed_seconds')}), flush=True)


if __name__ == '__main__':
    main()
