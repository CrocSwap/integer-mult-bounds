#!/usr/bin/env python3
"""Exact bounded search for additional cold entrances in the PR564 word.

This changes actual scalar donor gates and prices actual frame-chain splits.
It is a discovery screen, not a phase/hosting/recurrence certificate.
Prepared with OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from collections import Counter
import copy
from fractions import Fraction as Q
from functools import lru_cache
import gzip
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys
import time


@lru_cache(None)
def basis(vectors):
    pivots = {}
    for x in vectors:
        for k in sorted(pivots, reverse=True):
            if x >> k & 1:
                x ^= pivots[k]
        if x:
            k = x.bit_length() - 1
            for j in pivots:
                if pivots[j] >> k & 1:
                    pivots[j] ^= x
            pivots[k] = x
    return tuple(pivots[k] for k in sorted(pivots, reverse=True))


@lru_cache(None)
def span(frame):
    values = {0}
    for x in frame:
        values |= {y ^ x for y in values}
    return frozenset(values)


def inside(a, b):
    return basis(a + b) == b


def add(row, other, coefficient):
    for key, value in other.items():
        new = row.get(key, Q(0)) + coefficient * value
        if new:
            row[key] = new
        else:
            row.pop(key, None)


def linear_basis(columns, donors):
    result = {}
    for donor in donors:
        row = columns[donor].copy()
        combination = {donor: Q(1)}
        while row:
            key = min(row)
            if key not in result:
                q = row[key]
                row = {j: v / q for j, v in row.items()}
                combination = {j: v / q for j, v in combination.items()}
                result[key] = row, combination
                break
            q = row[key]
            other, relation = result[key]
            add(row, other, -q)
            add(combination, relation, -q)
    return result


def solve(column, eliminated):
    row, answer = column.copy(), {}
    while row:
        key = min(row)
        if key not in eliminated:
            return None
        other, relation = eliminated[key]
        q = row[key]
        add(row, other, -q)
        add(answer, relation, q)
    return answer


def frames(word, selected_part='B'):
    size = 2 * len(word['ports']) + word['report']['R']
    full = basis(tuple(1 << j for j in range(word['report']['h'])))
    current = [(p,) for p in word['ports']] + [()] * (size - len(word['ports']))
    for r, frame in word['start_extra'].items():
        current[int(r)] = basis(tuple(frame))
    first = {}
    before = []
    for part in ('A', 'B'):
        for index, event in enumerate(word[part]):
            if part == selected_part:
                before.append(current.copy())
            for r in event[1:3] if event[0] == 'add' else event[1:2]:
                first.setdefault(r, (part, index, basis(tuple(event[-1]))))
                current[r] = basis(tuple(event[-1]))
    after, nxt = [None] * len(word[selected_part]), [full] * size
    for index in reversed(range(len(word['B']))):
        event = word['B'][index]
        for r in event[1:3] if event[0] == 'add' else event[1:2]:
            nxt[r] = basis(tuple(event[-1]))
        if selected_part == 'B':
            after[index] = nxt.copy()
    if selected_part == 'A':
        for register, frame in zip(word['centers'], word['center_frames']):
            nxt[register] = basis(tuple(frame))
        for index in reversed(range(len(word['A']))):
            event = word['A'][index]
            for register in event[1:3] if event[0] == 'add' else event[1:2]:
                nxt[register] = basis(tuple(event[-1]))
            after[index] = nxt.copy()
    return first, before, after


def entropy(delta):
    return sum(n * r * math.log(r) for r, n in delta.items())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--word', type=Path, required=True)
    parser.add_argument('--gk-dir', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--step', type=int, default=1)
    parser.add_argument('--max-rank', type=int, default=2)
    parser.add_argument('--part', choices=('A', 'B'), default='B')
    parser.add_argument('--retain', type=int, default=12)
    args = parser.parse_args()
    assert __debug__ and args.step > 0 and 1 <= args.max_rank <= 3
    assert not args.out.exists()
    args.out.mkdir(parents=True)
    sys.path.insert(0, str(args.gk_dir.resolve()))
    import gk_word as g
    import gk_common as co
    g.V = co.V = 112
    g.DATA = co.DATA = 7168
    raw = gzip.decompress(args.word.read_bytes())
    word = json.loads(raw)
    original_profile = g.profile(word)
    first, before, after = frames(word, args.part)
    untouched = {r: data for r, data in first.items()
                 if r >= 224 and str(r) not in word['start_extra']
                 and (args.part == 'A' or data[0] == 'B')}
    options = {}
    for r, (_, _, frame) in untouched.items():
        lines = sorted(span(frame) - {0})
        values = {(x,) for x in lines}
        if args.max_rank >= 2:
            values |= {basis((x, y)) for x in lines for y in lines if x != y}
        if args.max_rank >= 3 and len(frame) <= 3:
            values.add(frame)
        options[r] = sorted(v for v in values if len(v) <= args.max_rank)
    columns = [{} for _ in range(728)]
    for target in range(112):
        columns[112 + target] = {target: Q(1)}
    if args.part == 'A':
        for event in reversed(word['cut'] + word['B']):
            if event[0] == 'add':
                add(columns[event[2]], columns[event[1]], Q(event[3], event[4]))
            else:
                columns[event[1]] = {t: q * Q(event[2], event[3])
                                     for t, q in columns[event[1]].items()}
    counts = Counter()
    found = {}
    start = time.monotonic()
    last = max(data[1] if data[0] == args.part else len(word[args.part]) - 1
               for data in untouched.values())
    for index in reversed(range(len(word[args.part]))):
        event = word[args.part][index]
        if event[0] == 'add':
            add(columns[event[2]], columns[event[1]], Q(event[3], event[4]))
        else:
            columns[event[1]] = {t: q * Q(event[2], event[3])
                                 for t, q in columns[event[1]].items()}
        if index > last or index % args.step:
            continue
        cur, nxt = before[index], after[index]
        for pivot, (first_part, first_index, first_frame) in untouched.items():
            if first_part == args.part and index > first_index:
                continue
            for frame in options[pivot]:
                counts['exact_span_queries'] += 1
                donors = [r for r in range(728) if r != pivot and not 112 <= r < 224
                          and columns[r] and inside(cur[r], frame) and inside(frame, nxt[r])]
                # Prefer donors that avoid splitting a paid climb. This is only
                # a basis choice; the existence test still uses every donor.
                def score(r):
                    a, e, b = len(cur[r]), len(frame), len(nxt[r])
                    delta = Counter({b - a: -1}) if b > a else Counter()
                    if e > a:
                        delta[e - a] += 1
                    if b > e:
                        delta[b - e] += 1
                    return -entropy(delta), r
                donors.sort(key=score)
                relation = solve(columns[pivot], linear_basis(columns, donors))
                if relation is None:
                    continue
                counts['exact_relations'] += 1
                if any(q.denominator & (q.denominator - 1) for q in relation.values()):
                    counts['nondyadic_relations'] += 1
                    continue
                key = (pivot, frame, tuple(sorted(relation.items())))
                if key in found:
                    counts['duplicate_relations'] += 1
                    continue
                changed = copy.deepcopy(word)
                gates = [['add', r, pivot, -q.numerator, q.denominator, list(frame)]
                         for r, q in sorted(relation.items())]
                changed[args.part][index:index] = gates
                changed['start_extra'][str(pivot)] = list(frame)
                changed['cleanup'] = [g.inverse(e, g.FULL)
                                      for e in reversed(changed['A'] + changed['B'])
                                      if not 112 <= e[1] < 224]
                profile = g.profile(changed)
                delta = {r: profile[r] - original_profile[r]
                         for r in set(profile) | set(original_profile)
                         if profile[r] != original_profile[r]}
                assert sum(r * n for r, n in delta.items()) == -len(frame)
                changed['report']['local_profile'] = dict(profile)
                # Optimistic global entropy credits released rank at a size-48
                # remainder. It screens candidates, never certifies hosting.
                estimate = entropy(delta) + len(frame) * (1 + math.log(48))
                candidate = dict(part=args.part, index=index, pivot=pivot, frame=frame,
                                 coefficients={str(r): str(q) for r, q in relation.items()},
                                 inserted_gates=len(gates), profile_delta=delta,
                                 local_entropy_delta=entropy(delta),
                                 optimistic_entropy_gain=estimate)
                found[key] = (candidate, changed)
        if index % 100 == 0:
            print(json.dumps(dict(cut=index, queries=counts['exact_span_queries'],
                                  found=len(found), seconds=time.monotonic() - start)), flush=True)
    ordered = sorted(found.values(), key=lambda pair: (-pair[0]['optimistic_entropy_gain'],
                                                      pair[0]['inserted_gates'], pair[0]['pivot']))
    for index, (candidate, changed) in enumerate(ordered[:args.retain]):
        name = 'candidate-%03d' % index
        (args.out / (name + '.json')).write_text(json.dumps(candidate, indent=2) + '\n')
        (args.out / (name + '.json.gz')).write_bytes(g.dump(changed))
    report = dict(status='PASS_EXACT_BOUNDED_SUFFIX_SCREEN',
                  source_sha256=hashlib.sha256(args.word.read_bytes()).hexdigest(),
                  source_content_sha256=hashlib.sha256(raw).hexdigest(),
                  part=args.part, cuts_step=args.step, max_frame_rank=args.max_rank,
                  untouched_pivots={str(r): data for r, data in untouched.items()},
                  counts=dict(counts), distinct_relations=len(found),
                  candidates=[candidate for candidate, _ in ordered],
                  seconds=time.monotonic() - start,
                  scope='Exact rational span test over all currently frame-compatible non-target donors; '
                        'one deterministic cost-ordered donor basis per pivot/frame/cut. '
                        'Rank limit and selected part are explicit. Nondyadic bases are skipped, '
                        'not proofs of absence of another dyadic solution. New words require '
                        'native, phase, owner, invoice and moment admission.')
    (args.out / 'SEARCH.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(dict(status=report['status'], distinct_relations=len(found),
                          counts=dict(counts), seconds=report['seconds'])), flush=True)


if __name__ == '__main__':
    main()
