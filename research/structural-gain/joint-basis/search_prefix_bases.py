#!/usr/bin/env python3
"""Unlock the static kernel jointly and enumerate compatible response bases.

Prepared with OpenAI Codex assistance. Apache-2.0. Every retained word has
exact rational suffix identities and a recomputed full frame profile; native
scalar/phase/global admission remain separate.
"""
import argparse
from collections import Counter
import copy
from fractions import Fraction as Q
import gzip
import hashlib
import itertools
import json
import math
from pathlib import Path
import sys
import time


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--word', type=Path, required=True)
    ap.add_argument('--selection', type=Path, required=True)
    ap.add_argument('--prefix-count', type=int, default=69)
    ap.add_argument('--gk-dir', type=Path, required=True)
    ap.add_argument('--search-code', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--raise-frames', action='store_true')
    args = ap.parse_args()
    assert __debug__ and not args.out.exists()
    args.out.mkdir(parents=True)
    sys.path.insert(0, str(args.gk_dir.resolve()))
    sys.path.insert(0, str(args.search_code.resolve()))
    import gk_word as g
    import gk_common as co
    from search_suffix_kernels import basis, span, inside, add, linear_basis, solve
    from coupled_frames_base import Chains
    g.V = co.V = 112
    g.DATA = co.DATA = 7168
    original = json.loads(gzip.decompress(args.word.read_bytes()))
    selection = json.loads(args.selection.read_text())
    unlocked = {224 + p for c in selection['kernel'] for p in c['pivots']}
    assert len(unlocked) == 44
    base = copy.deepcopy(original)
    removed = base['A'][:args.prefix_count]
    assert all(e[0] == 'add' and e[1] >= 224 and e[2] >= 224 for e in removed)
    base['A'] = base['A'][args.prefix_count:]
    base['start_extra'] = {r: frame for r, frame in base['start_extra'].items() if int(r) not in unlocked}
    base['cleanup'] = [g.inverse(e, g.FULL) for e in reversed(base['A'] + base['B'])
                       if not 112 <= e[1] < 224]
    columns = g.responses(base)
    assert all(not columns[int(r) - 224] for r in base['start_extra'])
    original_profile, base_profile = g.profile(original), g.profile(base)
    first = {h: basis(tuple(frame)) for h, frame in g.first_frames(base).items()}
    graph = Chains(base)
    caps = {h: graph.upper[graph.regs[h+224][1]] for h in first} if args.raise_frames else first
    cold = [h for h in range(504) if columns[h] and str(h + 224) not in base['start_extra']]
    options = set()
    for h in cold:
        subspaces = {()}
        for vector in span(caps[h]) - {0}:
            subspaces |= {basis(frame + (vector,)) for frame in tuple(subspaces)}
        options |= subspaces - {()}
    components = []
    counts = Counter()
    started = time.monotonic()
    for frame in sorted(options, key=lambda e: (len(e), e)):
        helpers = [h for h in cold if inside(frame, caps[h])]
        if len(helpers) < 2:
            continue
        counts['frame_classes'] += 1
        parent = {h: h for h in helpers}

        def root(h):
            while parent[h] != h:
                parent[h] = parent[parent[h]]
                h = parent[h]
            return h

        donors, eliminated, circuits = [], {}, []
        for h in helpers:
            relation = solve(columns[h], eliminated)
            if relation is None:
                donors.append(h)
                eliminated = linear_basis(columns, donors)
            else:
                support = [h, *relation]
                for d in support[1:]:
                    parent[root(d)] = root(h)
                circuits.append(dict(pivot=h, coefficients={str(d): str(q) for d, q in relation.items()}))
        groups = {}
        for h in helpers:
            groups.setdefault(root(h), []).append(h)
        for group in groups.values():
            if len(group) == 1:
                continue
            donor_group = [h for h in donors if h in group]
            pivot_group = [h for h in group if h not in donors]
            relations = {p: solve(columns[p], linear_basis(columns, donor_group)) for p in pivot_group}
            assert all(rel is not None for rel in relations.values())
            if any(q.denominator & (q.denominator - 1) for rel in relations.values() for q in rel.values()):
                counts['non_dyadic_components'] += 1
                continue
            used_donors = sorted({d for rel in relations.values() for d in rel})
            assert used_donors == donor_group
            delta = Counter()
            rank = len(frame)
            for h in group:
                width = len(first[h])
                delta[width] -= 1
                if width > rank:
                    delta[width - rank] += 1
            delta[rank] += len(donor_group)
            record = dict(frame=list(frame), helpers=group, donors=donor_group, pivots=pivot_group,
                          rank=len(donor_group), nullity=len(pivot_group),
                          coefficients={str(p): {str(d): str(q) for d, q in rel.items()}
                                        for p, rel in relations.items()},
                          profile_delta={r: n for r, n in sorted(delta.items()) if n},
                          released_rank=rank * len(pivot_group))
            changes = {}
            if args.raise_frames:
                for helper in group:
                    closure = graph.closure(graph.regs[helper+224][1], frame, 'raise', len(graph.nodes))
                    assert closure is not None
                    for node, value in closure.items():
                        changes[node] = basis(changes.get(node, graph.nodes[node]['F']) + value)
                candidate = copy.deepcopy(base)
                for node, value in changes.items():
                    point = graph.nodes[node]
                    candidate[point['section']][point['index']][-1] = list(value)
                gates = []
                for pivot in pivot_group:
                    candidate['start_extra'][str(pivot+224)] = list(frame)
                    for donor, coefficient in relations[pivot].items():
                        q = -coefficient
                        gates.append(['add', donor+224, pivot+224, q.numerator, q.denominator, list(frame)])
                candidate['A'] = gates + candidate['A']
                profile = g.profile(candidate)
                record['profile_delta'] = {r: profile[r]-base_profile[r] for r in set(profile)|set(base_profile)
                                           if profile[r] != base_profile[r]}
            record['frame_changes'] = [dict(section=graph.nodes[node]['section'],
                                            index=graph.nodes[node]['index'], frame=list(value))
                                       for node,value in sorted(changes.items())]
            components.append(record)
            counts['components_rank' + str(rank)] += 1
    dump(args.out / 'BASE-PROFILE.json', dict(profile=dict(base_profile), widths=co.widths_of(base)))
    (args.out / 'UNLOCKED-WORD.json.gz').write_bytes(g.dump(base))
    for rank in range(1, 5):
        chosen, used = [], set()
        eligible = [r for r in components if len(r['frame']) == rank]
        eligible.sort(key=lambda r: (-r['released_rank'], len(r['helpers']), r['frame']))
        for record in eligible:
            if not used.intersection(record['helpers']):
                chosen.append(record)
                used.update(record['helpers'])
        word = copy.deepcopy(base)
        gates, predicted = [], base_profile.copy()
        for record in chosen:
            predicted.update(record['profile_delta'])
            for change in record['frame_changes']:
                event = word[change['section']][change['index']]
                event[-1] = list(basis(tuple(event[-1]) + tuple(change['frame'])))
            for pivot in record['pivots']:
                word['start_extra'][str(pivot + 224)] = record['frame']
                for donor, coefficient in record['coefficients'][str(pivot)].items():
                    q = -Q(coefficient)
                    gates.append(['add', int(donor) + 224, pivot + 224,
                                  q.numerator, q.denominator, record['frame']])
        word['A'] = gates + word['A']
        word['cleanup'] = [g.inverse(e, g.FULL) for e in reversed(word['A'] + word['B'])
                           if not 112 <= e[1] < 224]
        profile = g.profile(word)
        if not args.raise_frames:
            assert profile == +predicted
        final_columns = g.responses(word)
        assert all(not final_columns[int(r) - 224] for r in word['start_extra'])
        delta = {r: profile[r] - original_profile[r] for r in set(profile) | set(original_profile)
                 if profile[r] != original_profile[r]}
        widths = co.widths_of(word)
        word['report'].update(local_profile=dict(profile), local_rank_mass=sum(r*n for r,n in profile.items()),
                              entrance_rank=sum(9-w for w in widths), entering_helpers=sum(w<9 for w in widths),
                              width_inventory=dict(Counter(widths)))
        folder = args.out / ('rank%d-disjoint' % rank)
        folder.mkdir()
        (folder / 'FULL-WORD.json.gz').write_bytes(g.dump(word))
        dump(folder / 'CONSTRUCTION.json', dict(status='PASS_EXACT_JOINT_PREFIX_CONSTRUCTION',
             source_sha256=sha(args.word), selected_components=chosen, profile_after=dict(profile),
             profile_delta=delta, widths_after=dict(Counter(widths)), ordered_widths=widths,
             removed_prefix_gates=len(removed), inserted_prefix_gates=len(gates),
             all_entering_response_columns_zero=True,
             scope='Simultaneous prefix donor-basis selection with complete exact frame profile; '
                   'native scalar, phase and global admission remain separate.'))
    report = dict(status='PASS_EXACT_JOINT_PREFIX_BASIS_SCREEN', source_sha256=sha(args.word),
                  selection_sha256=sha(args.selection), source_code_sha256={str(p): sha(p) for p in
                  (Path(__file__), args.gk_dir/'gk_word.py', args.gk_dir/'gk_common.py',
                   args.search_code/'search_suffix_kernels.py')},
                  original_profile=dict(original_profile), unlocked_profile=dict(base_profile),
                  removed_prefix_gates=args.prefix_count, unlocked_pivots=sorted(unlocked),
                  raised_first_frames=args.raise_frames,
                  cold_nonzero_columns=len(cold), frame_class_count=len(options), counts=dict(counts),
                  components=components, seconds=time.monotonic()-started,
                  scope='All subspaces of the selected fixed-first or maximal-future frame caps '
                        'and their exact rational dependency components after unlocking44 static '
                        'pivots. With raised_first_frames=true, literal forward closures are '
                        'applied and fully repriced. One deterministic donor basis per component; '
                        'no non-prefix operation or global hosting claim.')
    dump(args.out/'SEARCH.json', report)
    print(json.dumps(dict(counts=dict(counts), components=len(components), seconds=report['seconds']),indent=2))


if __name__ == '__main__':
    main()
