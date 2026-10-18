#!/usr/bin/env python3
"""Separate integer-column and subset-DP check; imports no primary checker code.

Apache-2.0. Prepared with substantial OpenAI Codex assistance in the same
session as verify.py; this is code/representation diversity, not human review.
"""
from collections import Counter
from functools import lru_cache
import gzip
import hashlib
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def rank_integer(matrix):
    a = [list(row) for row in matrix]
    row = 0
    for col in range(8):
        pivot = next((i for i in range(row, len(a)) if a[i][col]), None)
        if pivot is None:
            continue
        a[row], a[pivot] = a[pivot], a[row]
        for i in range(row+1, len(a)):
            if a[i][col]:
                u, v = a[row][col], a[i][col]
                a[i] = [u*x-v*y for x, y in zip(a[i], a[row])]
                factor = math.gcd(*a[i])
                if factor:
                    a[i] = [x//factor for x in a[i]]
        row += 1
    return row


def check():
    sources = json.loads((HERE/'SOURCES.json').read_text())
    for entry in sources['files']:
        if entry['usage'] == 'input':
            require(hashlib.sha256((ROOT/entry['path']).read_bytes()).hexdigest()
                    == entry['sha256'], 'source bytes changed')
    w = json.loads(gzip.decompress((ROOT/'research/r439-bsection-stars-seed01/candidate.json.gz').read_bytes()))
    cert = json.loads((HERE/'CERTIFICATE.json').read_text())
    total = 2*w['v'] + w['R']
    count = len(w['ret'])
    incidence = [[int(i in row) for i in range(count)] for row in w['scatter']]
    weights = [[sum(row[i]*row[j] for row in incidence)-2 for j in range(count)]
               for i in range(count)]

    @lru_cache(None)
    def distribution(mask):
        if mask == 0:
            return {0:1}
        i = (mask & -mask).bit_length()-1
        rest = mask ^ (1 << i)
        answer = Counter(distribution(rest))
        for j in range(i+1, count):
            if rest & (1 << j):
                for score, ways in distribution(rest ^ (1 << j)).items():
                    answer[score + weights[i][j]] += ways
        return dict(answer)

    hist = distribution((1 << count)-1)
    require({str(k):v for k, v in hist.items()} == cert['search']['saving_distribution'],
            'independent subset-DP distribution')
    require(max(hist) == 120 and hist[120] == 105 and sum(hist.values()) == 2620,
            'restricted optimum')
    recipe = cert['search']['chosen_partition']
    require(sorted(i for block in recipe for i in block) == list(range(count)), 'partition coverage')
    require(all(len(block) in (1, 2) for block in recipe), 'partition alphabet')
    require(sum(weights[b[0]][b[1]] for b in recipe if len(b) == 2) == 120, 'witness score')

    def sequence(paired):
        # Independently reconstruct the documented chronological instruction list.
        result = []
        for name in ('D', 'A'):
            for _, dst, srcs in w[name]:
                for src in srcs:
                    result.append((1, dst, src, 1))
        for group in recipe if paired else [[i] for i in range(count)]:
            i = group[0]
            result.append((2, total, w['ret'][i], 0))
            if len(group) == 1:
                for t in range(w['v']):
                    if incidence[t][i]:
                        result.append((1, w['v']+t, total, 1))
            else:
                j = group[1]
                result.append((2, total+1, w['ret'][j], 0))
                for t, row in enumerate(incidence):
                    if row[i] != row[j]:
                        result.append((1, w['v']+t, total + row[j], 1))
                result.append((1, total, total+1, 1))
                for t, row in enumerate(incidence):
                    if row[i] and row[j]:
                        result.append((1, w['v']+t, total, 1))
                result.append((1, total, total+1, -1))
            result.append((3, total, w['ret'][i], 0))
            if len(group) == 2:
                result.append((3, total+1, w['ret'][group[1]], 0))
        for name in ('B', 'C'):
            for _, dst, srcs in w[name]:
                for src in srcs:
                    result.append((1, dst, src, 1))
        return result

    seqs = [sequence(False), sequence(True)]

    def execute(program, col, reverse=False, absolute=False):
        values = [int(i == col) for i in range(total)] + [0, 0]
        if absolute:
            values = [1]*total + [0, 0]
        active = {}
        maximum = 1
        for kind, dst, src, sign in reversed(program) if reverse else program:
            if reverse:
                kind = {1:1, 2:3, 3:2}[kind]
                sign = -sign
            if kind == 1:
                values[dst] += (abs(sign) if absolute else sign)*values[src]
            elif kind == 2:
                require(dst not in active and values[dst] == 0, 'occupied copied slot')
                active[dst] = src
                values[dst] = values[src]
            else:
                require(active.get(dst) == src, 'wrong copied center')
                if not absolute:
                    require(values[dst] == values[src], 'integer ERASE mismatch')
                del active[dst]
                values[dst] = 0
            maximum = max(maximum, abs(values[dst]))
        require(not active and values[total:] == [0, 0], 'integer endpoint workspace')
        return values[:total], maximum

    # Equality of two complete integer matrices is stronger than their F2
    # endpoint agreement, but is NOT a claim that the full supplier is a Z shear.
    actual_max = 0
    for reverse in (False, True):
        for col in range(total):
            base, mb = execute(seqs[0], col, reverse)
            cand, mc = execute(seqs[1], col, reverse)
            require(base == cand, 'integer-column replacement mismatch')
            expected = [int(i == col) for i in range(total)]
            if col < w['v']:
                expected[w['v']+col] ^= 1
            require([v % 2 for v in cand] == expected, 'dirty F2 column mismatch')
            actual_max = max(actual_max, mb, mc)
    for k, name in enumerate(('baseline_bounds', 'candidate_bounds')):
        f = execute(seqs[k], 0, absolute=True)[1]
        b = execute(seqs[k], 0, reverse=True, absolute=True)[1]
        require((f, b) == (cert[name]['F'], cert[name]['B']), 'majorant mismatch')
        require(64*f**3*b**2 < 2**104 and 2**18*f**5*b**4 < 2**192, 'precision guard')

    # Independent fraction-free ranks and persistent frame accounting.
    dims = [rank_integer([w['lines'][i] for i in frame]) for frame in w['frames']]
    positions = list(w['start'])
    child = Counter()
    paths = [[p] for p in positions]
    for phase in ('D', 'A', 'scatter', 'B', 'C', 'final'):
        if phase == 'scatter':
            require([dims[positions[r]] for r in w['ret']] == [7]*9, 'copy ranks')
            child[7] += 9
            continue
        gs = [(f, r, []) for r, f in enumerate(w['final'])] if phase == 'final' else w[phase]
        for frame, dst, srcs in gs:
            for r in [dst, *srcs]:
                old = positions[r]
                if old != frame:
                    require(set(w['frames'][old]) <= set(w['frames'][frame]), 'nested frame')
                    require(dims[frame] > dims[old], 'rank growth')
                    child[dims[frame]-dims[old]] += 1
                    paths[r].append(frame)
                    positions[r] = frame
    require(dict(child) == {int(k):v for k, v in cert['local_recursive_invoice']['paid_profile'].items()},
            'independent recursive invoice')
    path_digest = hashlib.sha256(json.dumps(paths, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    require(path_digest == cert['local_recursive_invoice']['persistent_paths_sha256'], 'path digest')

    # Whole-program sign mutation passes F2 but must fail the stronger integer
    # copied-boundary check on at least one actual dirty input.
    mutant = list(seqs[1])
    where = next(i for i, e in enumerate(mutant) if e == (1, total, total+1, -1))
    mutant[where] = (1, total, total+1, 1)
    rejected = False
    for col in range(total):
        try:
            execute(mutant, col)
        except RuntimeError:
            rejected = True
            break
    require(rejected, 'whole-program wrong-sign control')
    print('PASS_TWO_COPY_INDEPENDENT columns=661 directions=2 integer_lifts_equal '
          'subset_DP=2620 optimum=120 controls=wrong_sign actual_max_coefficient=' + str(actual_max))


if __name__ == '__main__':
    check()
