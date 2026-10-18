#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Set-valued scalar replay and fraction-free rational geometry; no verify.py import.
Ross Richardson, with substantial OpenAI Codex assistance.
"""
import argparse
import gzip
import hashlib
import json
import math
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent


def require(ok, message):
    if not ok:
        raise ValueError(message)


def integer_basis(vectors):
    basis = {}
    for v in vectors:
        a = list(v)
        for p, b in sorted(basis.items()):
            if a[p]:
                x, y = b[p], a[p]
                a = [x*u-y*v for u, v in zip(a, b)]
                gcd = 0
                for z in a:
                    gcd = math.gcd(gcd, z)
                if gcd:
                    a = [z//gcd for z in a]
        if any(a):
            p = next(i for i, x in enumerate(a) if x)
            basis[p] = a
    return list(basis.values())


def inverse_sets(rows):
    left, right = [r.copy() for r in rows], [{i} for i in range(len(rows))]
    for c in range(len(rows)):
        p = next(i for i in range(c, len(rows)) if c in left[i])
        left[c], left[p] = left[p], left[c]
        right[c], right[p] = right[p], right[c]
        for r in range(len(rows)):
            if r != c and c in left[r]:
                left[r].symmetric_difference_update(left[c])
                right[r].symmetric_difference_update(right[c])
    require(left == [{i} for i in range(len(rows))], 'independent inverse')
    return right


def set_rank(rows):
    basis = {}
    for row in rows:
        row = set(row)
        while row:
            p = min(row)
            if p in basis:
                row ^= basis[p]
            else:
                basis[p] = row
                break
    return len(basis)


def check(root):
    pins = json.loads((HERE/'SOURCES.json').read_text())
    pin, = [x for x in pins['files'] if x['usage'] == 'input']
    raw = (root/pin['path']).read_bytes()
    require(hashlib.sha256(raw).hexdigest() == pin['sha256'], 'independent source hash')
    w = json.loads(gzip.decompress(raw))
    cert = json.loads((HERE/'CERTIFICATE.json').read_text())
    v, n = w['v'], 2*w['v']+w['R']
    bases = [integer_basis(w['lines'][i] for i in f) for f in w['frames']]
    dims = [len(b) for b in bases]
    contain_cache = {}

    def contains(a, b):
        key = (a, b)
        if key not in contain_cache:
            contain_cache[key] = len(integer_basis(bases[a]+bases[b])) == dims[b]
        return contain_cache[key]

    state = [{i} for i in range(n)]
    frames = w['start'][:]
    for name in ['D', 'A']:
        for f, t, ss in w[name]:
            for r in [t, *ss]:
                require(contains(frames[r], f), 'prefix frame')
                frames[r] = f
            for s in ss:
                state[t] ^= state[s]
    for t, ss in enumerate(w['scatter']):
        for s in ss:
            state[v+t] ^= state[w['ret'][s]]
    inverse = inverse_sets(state)
    require([x['helper'] for x in cert['retirements']] == [465, 466, 468, 469, 470, 476], 'helper coverage')
    lost_total, least_survivors = 0, []
    for case in cert['retirements']:
        h, U = case['helper'], case['terminal_frame']
        restore = inverse[h]
        dirt = {i for i, r in enumerate(state) if h in r}
        participants = restore | dirt | {h}
        require(case['restore_row'] == sorted(restore) and case['dirty_column'] == sorted(dirt), 'cut row/column')
        require(case['forced_participants'] == sorted(participants), 'forced participant coverage')
        require(dims[U] == 7 and all(contains(frames[r], U) for r in participants), 'retirement geometry')
        join = integer_basis(z for r in participants for z in bases[frames[r]])
        require(len(join) == 7, 'terminal uniqueness')
        missed = [{'target': t, 'boundary_coordinates': sorted((inverse[t] ^ inverse[t-v]) & participants)}
                  for t in range(v, 2*v) if not contains(U, w['final'][t]) and
                  (inverse[t] ^ inverse[t-v]) & participants]
        require(missed == case['lost_targets'], 'all target obligations')
        require(set_rank(x['boundary_coordinates'] for x in missed) == case['lost_dependency_rank'], 'lost rank')
        lost_total += len(missed)
        least = case['least_frame_restoration']
        minimum = integer_basis(z for r in restore for z in bases[frames[r]])
        matches = [f for f in range(len(bases)) if dims[f] == len(minimum) and
                   all(contains(frames[r], f) for r in restore)]
        require(matches == [least['frame']] and dims[matches[0]] == least['rank'], 'least frame')
        missed_least = [{'target': t, 'boundary_coordinates': sorted((inverse[t] ^ inverse[t-v]) & restore)}
                        for t in range(v, 2*v) if not contains(matches[0], w['final'][t]) and
                        (inverse[t] ^ inverse[t-v]) & restore]
        require(missed_least == least['lost_targets'], 'least-frame target cut')
        if not missed_least:
            least_survivors.append(h)
        example = case['witness']
        donor, target = example['boundary_coordinate'], example['target']
        require(donor in restore and donor < v, 'source witness')
        delta = set(example['original_input_delta'])
        require([len(r & delta) % 2 for r in state] == [int(r == donor) for r in range(n)], 'two-input witness')
        require(len({target, target-v} & delta) % 2 == 1, 'distinguishable output')
        sep = example['separation']
        dot = lambda line: sum(a*b for a, b in zip(sep['normal'], w['lines'][line]))
        require(all(dot(line) == 0 for line in w['frames'][w['final'][target]]), 'target annihilator')
        require(sep['line'] in w['frames'][U] and dot(sep['line']) == sep['dot'] != 0, 'separating vector')
        copied = [x.copy() for x in state]
        for t, s in case['star_gates']:
            copied[t] ^= copied[s]
        require(copied[h] == {h} and all(h not in row for r, row in enumerate(copied) if r != h), 'common-frame star')
    require(lost_total == 59 and least_survivors == [470], 'classification')

    construction = cert['construction']
    for candidate in [False, True]:
        state = [{i} for i in range(n)]
        frames = w['start'][:]
        paths, histogram, tape = [[f] for f in frames], Counter(), []
        positive, peak, copy_ranks = [1]*n, 1, []
        adds = moves = 0
        sections = ['D', 'A', 'scatter', 'E', 'B', 'C'] if candidate else ['D', 'A', 'scatter', 'B', 'C']
        final = w['final'][:]
        if candidate:
            final[470] = construction['final_helper_frame']

        def move(r, f):
            nonlocal moves
            require(contains(frames[r], f), 'whole-word frame legality')
            if frames[r] != f:
                d = dims[f]-dims[frames[r]]
                require(d > 0, 'strict frame climb')
                histogram[d] += 1
                paths[r].append(f)
                moves += 1
                frames[r] = f

        def add(t, s):
            nonlocal adds, peak
            state[t] ^= state[s]
            positive[t] += positive[s]
            peak = max(peak, positive[t])
            adds += 1
            tape.append((t, s))

        for section in sections:
            if section == 'scatter':
                copy_ranks = [dims[frames[r]] for r in w['ret']]
                histogram.update(copy_ranks)
                for t, ss in enumerate(w['scatter']):
                    for s in ss:
                        add(v+t, w['ret'][s])
                continue
            gates = construction['retirement_gates'] if section == 'E' else w[section]
            for i, (f, t, ss) in enumerate(gates):
                if candidate and section == 'C':
                    if i == construction['cleanup_omit_gate']:
                        continue
                    if i == construction['cleanup_replace_source']['gate']:
                        ss = [construction['cleanup_replace_source']['new_source']]
                for r in [t, *ss]:
                    move(r, f)
                for s in ss:
                    add(t, s)
            if section == 'E':
                require(state[470] == {470} and all(470 not in row for r, row in enumerate(state) if r != 470), 'E separation')
        expected = [{r, r-v} if v <= r < 2*v else {r} for r in range(n)]
        require(state == expected, 'complete 661-column endpoint')
        reverse = [{i} for i in range(n)]
        for t, s in tape[::-1]:
            reverse[t] ^= reverse[s]
        require(reverse == expected, 'literal inverse')
        for r, f in enumerate(final):
            move(r, f)
        actual = {'ADDs': adds, 'MOVEs': moves, 'COPYs': 9, 'ERASEs': 9, 'COPY_ranks': copy_ranks,
                  'records': adds+moves+18, 'profile': {str(k): x for k, x in sorted(histogram.items())},
                  'rank_mass': sum(k*x for k, x in histogram.items()), 'children': sum(histogram.values()),
                  'positive_majorant_peak': str(peak), 'positive_majorant_bits': peak.bit_length()}
        require(actual == construction['candidate' if candidate else 'baseline'], 'complete local invoice')
        if candidate:
            require([i for i in range(n) if paths[i] != base_paths[i]] == [470], 'other paths changed')
        else:
            base_paths = paths
    print('PASS_INDEPENDENT_EARLY_RETIREMENT sets=661 geometry=integer '
          'target_contracts=666 lost=59 least_frame_survivor=470 complete_word=both_directions')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root', type=Path, default=HERE.parents[1])
    args = ap.parse_args()
    try:
        check(args.root)
    except (ValueError, OSError, KeyError, IndexError, StopIteration) as exc:
        raise SystemExit('REJECT: ' + str(exc))
