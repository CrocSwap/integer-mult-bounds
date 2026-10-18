#!/usr/bin/env python3
"""Search exact suffix kernels with paid coupled donor-frame promotion.

Prepared with OpenAI Codex assistance. Apache-2.0. This is a bounded discovery
experiment: exact scalar relations and frame profiles, no phase/hosting claim.
"""
import argparse
from collections import Counter
import copy
from fractions import Fraction as Q
import gzip
import hashlib
import json
import math
from pathlib import Path
import sys
import time

from search_suffix_kernels import add, basis, span, inside, frames, linear_basis, solve, entropy
from promote_cold_frames import ForwardFrames


def meet(left, right):
    return basis(tuple(sorted(span(left) & span(right))))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--word', type=Path, required=True)
    parser.add_argument('--gk-dir', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--step', type=int, default=4)
    parser.add_argument('--rank', type=int, default=2)
    parser.add_argument('--pivot', type=int, action='append')
    parser.add_argument('--retain', type=int, default=12)
    args = parser.parse_args()
    assert __debug__ and not args.out.exists() and args.rank in (1, 2, 3)
    args.out.mkdir(parents=True)
    sys.path.insert(0, str(args.gk_dir.resolve()))
    import gk_word as g
    import gk_common as co
    g.V = co.V = 112
    g.DATA = co.DATA = 7168
    raw = gzip.decompress(args.word.read_bytes())
    word = json.loads(raw)
    first, before, after = frames(word)
    graph = ForwardFrames(word)
    full = basis(tuple(1 << j for j in range(9)))
    upper = graph.frames.copy()
    for node in reversed(range(graph.gates)):
        cap = full
        for register in graph.roles[node]:
            cap = meet(cap, upper[graph.next[node, register]])
        assert inside(graph.frames[node], cap)
        upper[node] = cap
    following = {r: nodes[-1] for r, nodes in enumerate(graph.regs)}
    next_nodes = [None] * graph.gates
    for index in reversed(range(graph.gates)):
        for register in graph.roles[index]:
            following[register] = index
        next_nodes[index] = following.copy()
    untouched = {r: data for r, data in first.items()
                 if r >= 224 and str(r) not in word['start_extra'] and data[0] == 'B'
                 and (not args.pivot or r in args.pivot)}
    options = {}
    for pivot, (_, first_index, frame) in untouched.items():
        # Cover the full maximal feasible first frame, not only the current one.
        permitted = upper[graph.regs[pivot][0]]
        lines = sorted(span(permitted) - {0})
        values = {(x,) for x in lines}
        if args.rank >= 2:
            values |= {basis((x, y)) for x in lines for y in lines if x != y}
        if args.rank == 3:
            planes = [value for value in values if len(value) == 2]
            values |= {basis(plane + (x,)) for plane in planes for x in lines}
        options[pivot] = sorted(frame for frame in values if len(frame) == args.rank)
    columns = [{} for _ in range(728)]
    for target in range(112):
        columns[112 + target] = {target: Q(1)}
    original = g.profile(word)
    found, counts = {}, Counter()
    last = max(data[1] for data in untouched.values())
    start = time.monotonic()
    for index in reversed(range(len(word['B']))):
        event = word['B'][index]
        if event[0] == 'add':
            add(columns[event[2]], columns[event[1]], Q(event[3], event[4]))
        else:
            columns[event[1]] = {t: q * Q(event[2], event[3])
                                 for t, q in columns[event[1]].items()}
        if index > last or index % args.step:
            continue
        current, following = before[index], next_nodes[index]
        for pivot, (_, first_index, _) in untouched.items():
            if index > first_index:
                continue
            for frame in options[pivot]:
                counts['exact_span_queries'] += 1
                donors = [r for r in range(728) if r != pivot and not 112 <= r < 224
                          and columns[r] and inside(current[r], frame)
                          and inside(frame, upper[following[r]])]
                # Prefer unchanged next frames, then the smaller propagation.
                def donor_cost(register):
                    changed = {}
                    assert graph.raise_frame(changed, following[register], frame)
                    return len(changed), -len(current[register]), register
                donors.sort(key=donor_cost)
                relation = solve(columns[pivot], linear_basis(columns, donors))
                if relation is None:
                    continue
                counts['exact_relations'] += 1
                if any(q.denominator & (q.denominator - 1) for q in relation.values()):
                    counts['nondyadic_relations'] += 1
                    continue
                # Different cuts may have different frame costs for one relation.
                key = (pivot, frame, tuple(sorted(relation.items())),
                       tuple((r, following[r]) for r in (pivot, *sorted(relation))))
                if key in found:
                    counts['duplicates'] += 1
                    continue
                changed = {}
                for register in (pivot, *relation):
                    assert graph.raise_frame(changed, following[register], frame)
                candidate = copy.deepcopy(word)
                for node, new_frame in changed.items():
                    candidate['B'][node][-1] = list(new_frame)
                gates = [['add', r, pivot, -q.numerator, q.denominator, list(frame)]
                         for r, q in sorted(relation.items())]
                candidate['B'][index:index] = gates
                candidate['start_extra'][str(pivot)] = list(frame)
                candidate['cleanup'] = [g.inverse(e, g.FULL)
                                        for e in reversed(candidate['A'] + candidate['B'])
                                        if not 112 <= e[1] < 224]
                profile = g.profile(candidate)
                delta = {r: profile[r] - original[r] for r in set(profile) | set(original)
                         if profile[r] != original[r]}
                assert sum(r * n for r, n in delta.items()) == -len(frame)
                candidate['report']['local_profile'] = dict(profile)
                estimate = entropy(delta) + len(frame) * (1 + math.log(48))
                record = dict(part='B', index=index, pivot=pivot, frame=frame,
                              coefficients={str(r): str(q) for r, q in relation.items()},
                              inserted_gates=len(gates), changed_existing_gates=len(changed),
                              profile_delta=delta, local_entropy_delta=entropy(delta),
                              optimistic_entropy_gain=estimate)
                found[key] = record, candidate
        if index % 100 == 0:
            print(json.dumps(dict(cut=index, counts=dict(counts), found=len(found),
                                  seconds=time.monotonic() - start)), flush=True)
    ordered = sorted(found.values(), key=lambda pair: (-pair[0]['optimistic_entropy_gain'],
                                                      pair[0]['inserted_gates']))
    for index, (record, candidate) in enumerate(ordered[:args.retain]):
        name = 'candidate-%03d' % index
        (args.out / (name + '.json')).write_text(json.dumps(record, indent=2) + '\n')
        (args.out / (name + '.json.gz')).write_bytes(g.dump(candidate))
    report = dict(status='PASS_EXACT_RAISED_SUFFIX_SCREEN',
                  source_content_sha256=hashlib.sha256(raw).hexdigest(),
                  rank=args.rank, B_cut_step=args.step, counts=dict(counts),
                  candidates=[record for record, _ in ordered],
                  pivot_options={str(p): len(opts) for p, opts in options.items()},
                  seconds=time.monotonic() - start,
                  scope='All donors compatible with current frame and maximal future frame are '
                        'included in exact rational span tests. Cost-ordered basis chosen. '
                        'Actual coupled frame joins are applied and complete profiles recomputed. '
                        'No phase, physical packing, or recurrence certificate is claimed.')
    (args.out / 'SEARCH.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(dict(counts=dict(counts), candidates=len(ordered), seconds=report['seconds'],
                          best=ordered[0][0] if ordered else None), indent=2))


if __name__ == '__main__':
    main()
