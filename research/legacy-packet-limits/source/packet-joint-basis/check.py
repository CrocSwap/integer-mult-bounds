#!/usr/bin/env python3
"""Check a joint partial basis and early center cut with exact arithmetic.

Prepared with OpenAI Codex assistance. This is a finite search result.
It is not a new scalar supplier or a kappa certificate.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
import gzip
import hashlib
from itertools import combinations
import json
from pathlib import Path
import time


def require(ok, message):
    if not ok:
        raise ValueError(message)


def binary_basis(vectors):
    result = {}
    for vector in vectors:
        for pivot in sorted(result, reverse=True):
            if vector >> pivot & 1:
                vector ^= result[pivot]
        if vector:
            pivot = vector.bit_length()-1
            for old in result:
                if result[old] >> pivot & 1:
                    result[old] ^= vector
            result[pivot] = vector
    return tuple(result[pivot] for pivot in sorted(result, reverse=True))


def inside(small, large):
    return binary_basis(small+large) == large


def rational_basis(rows):
    result = {}
    for original in rows:
        row = list(map(Q, original))
        for pivot, old in sorted(result.items()):
            scalar = row[pivot]
            row = [a-scalar*b for a, b in zip(row, old)]
        pivot = next((i for i, value in enumerate(row) if value), None)
        if pivot is not None:
            scalar = row[pivot]
            result[pivot] = [value/scalar for value in row]
    return result


def inverse(matrix):
    n = len(matrix)
    augmented = [list(map(Q, row))+[Q(i == j) for j in range(n)]
                 for i, row in enumerate(matrix)]
    for column in range(n):
        pivot = next(i for i in range(column, n) if augmented[i][column])
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        scalar = augmented[column][column]
        augmented[column] = [value/scalar for value in augmented[column]]
        for i in range(n):
            if i != column:
                scalar = augmented[i][column]
                augmented[i] = [a-scalar*b for a, b in zip(augmented[i], augmented[column])]
    return [row[n:] for row in augmented]


def product(left, right):
    return [[sum(a*b for a, b in zip(row, column)) for column in zip(*right)] for row in left]


def components(matrix):
    parent = list(range(len(matrix)))
    def root(i):
        while parent[i] != i:
            i = parent[i]
        return i
    for column in zip(*matrix):
        support = [i for i, value in enumerate(column) if value]
        for i in support[1:]:
            parent[root(i)] = root(support[0])
    groups = {}
    for i in range(len(matrix)):
        groups.setdefault(root(i), []).append(i)
    return list(groups.values())


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--run', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    require(__debug__, 'Assertions must be enabled.')
    require(not args.out.exists(), 'Use a new result file.')
    started = time.monotonic()
    root = args.run.resolve()
    data = root/'baseline535/source531/research/direct-delivery504-global/inputs/hamming'
    geometry = json.loads((data/'PROTOTYPE.json').read_text())
    modules = json.loads(gzip.decompress((data/'PACKET-PROGRAMS.json.gz').read_bytes()))
    ports, roots = geometry['binary_ports'], geometry['root_lines']
    all_blocks = [tuple(module['receipt']['block']) for module in modules]
    result = []
    negative_control = None
    for module in modules:
        block = tuple(module['receipt']['block'])
        ids = module['receipt']['source_lines']
        rows = [[Q(i == j) for j in range(8)] if i < 8 else [Q(0)]*8 for i in range(24)]
        frames = [(ports[source],) for source in ids]+[()]*16
        for event, frame in list(zip(module['events'], module['event_frames']))[:40]:
            target, source, a, b = event
            frame = binary_basis(tuple(frame))
            require(inside(frames[target], frame) and inside(frames[source], frame),
                    'The inherited partial program has an invalid frame.')
            scalar = Q(a, b)
            rows[target] = [x+scalar*y for x, y in zip(rows[target], rows[source])]
            frames[target] = frames[source] = frame
        late = module['events'][40:]
        require(len(late) == 12 and sorted(i for event in late for i in event[:2]) == list(range(24)),
                'The twelve face assemblies are not disjoint.')
        tetrahedra = [[source for source in ids if sum(roots[source][i] < 0 for i in block)%2 == parity]
                      for parity in range(2)]
        keys = [(pair, sign) for pair in combinations(block, 2) for sign in (-1, 1)]
        packet_frames, packet_supports = [], []
        for pair, sign in keys:
            support = [source for other in all_blocks if other != block and set(pair) <= set(other)
                       for source in modules[all_blocks.index(other)]['receipt']['source_lines']
                       if roots[source][pair[0]]*roots[source][pair[1]] == sign]
            require(len(support) == 8, 'A face sum has the wrong source support.')
            packet_supports.append(set(support))
            packet_frames.append(binary_basis(tuple(ports[source] for source in support)))
        require(all(not a & b for a, b in combinations(packet_supports, 2)),
                'Different packet keys do not have disjoint source supports.')
        candidates = []
        summaries = []
        for parity, targets in enumerate(tetrahedra):
            sources = tetrahedra[1-parity]
            source_indices = [ids.index(source) for source in sources]
            partials = [(register, [rows[register][i] for i in source_indices])
                        for register in range(24)
                        if all(not rows[register][i] for i in range(8) if i not in source_indices)]
            require(len(partials) == 12 and all(sum(bool(v) for v in row) == 2 for _, row in partials),
                    'The source partial directions have changed.')
            own = [[-Q(sum(a*b for a, b in zip(roots[target], roots[source])), 4)
                    for source in sources] for target in targets]
            require(len(rational_basis(own)) == 4, 'The own-block operator is singular.')
            own_inverse = inverse(own)
            cross = [[-Q(roots[target][pair[0]], 2)
                      if roots[target][pair[0]]*roots[target][pair[1]] == sign else Q(0)
                      for pair, sign in keys] for target in targets]
            options = []
            component_counts = Counter()
            early_counts = Counter()
            all_subsets = 0
            for selected in combinations(partials, 4):
                all_subsets += 1
                query = [row for _, row in selected]
                if len(rational_basis(query)) != 4:
                    continue
                output = product(own, inverse(query))
                output_inverse = product(query, own_inverse)
                require(product(output, query) == own, 'The new output basis fails the own identity.')
                groups = components(output)
                caps = {}
                for group in groups:
                    cap = binary_basis(tuple(x for x in range(1, 512)
                        if all(not (x & ports[targets[i]]).bit_count()%2 for i in group)))
                    for j, column in enumerate(zip(*output)):
                        if any(column[i] for i in group):
                            caps[j] = cap
                require(all(inside(frames[register], caps[j]) for j, (register, _) in enumerate(selected)),
                        'The new own partial cannot enter its output component.')
                transformed = product(output_inverse, cross)
                early = tuple(k for k in range(12)
                              if all(not transformed[j][k] or inside(packet_frames[k], caps[j])
                                     for j in range(4)))
                require(all(len(group) >= 2 for group in groups),
                        'A two-source partial produced a singleton output component.')
                require(len(early) <= 4, 'The basis admits a larger early packet set.')
                component_counts[tuple(sorted(map(len, groups)))] += 1
                early_counts[len(early)] += 1
                options.append(dict(registers=tuple(register for register, _ in selected),
                                    early=early, components=tuple(sorted(map(len, groups)))))
                if negative_control is None and groups == [list(range(4))]:
                    forbidden = next((j, k) for j in range(4) for k in range(12)
                                     if transformed[j][k] and not inside(packet_frames[k], caps[j]))
                    j, k = forbidden
                    witness = next(source for source in packet_supports[k]
                                   if not inside((ports[source],), caps[j]))
                    negative_control = dict(block=block, basis_registers=[register for register, _ in selected],
                                            packet_key=k, query=j, source=witness,
                                            actual_source_port=ports[witness], required_cap=caps[j],
                                            relaxed_cap_would_admit_all_keys=12,
                                            real_cap_rejects_this_nonzero_column=True)
            candidates.append(options)
            summaries.append(dict(tetrahedron=targets, subsets=all_subsets, bases=len(options),
                                  component_counts={str(k): v for k, v in component_counts.items()},
                                  early_key_counts=dict(early_counts)))
        # Only two paired components can have early cross packets. Any other
        # basis gives at most four early keys in their union and already needs
        # at least eight ordinary clones. Check all remaining pairings.
        paired = [[option for option in options if option['components'] == (2, 2)]
                  for options in candidates]
        pair_results = []
        minimum_helpers = 40
        for left in paired[0]:
            for right in paired[1]:
                protected = set(left['registers']+right['registers'])
                early_events = [event for event in late if not protected & set(event[:2])]
                retired = [rows[event[1]] for event in early_events]
                totals = [[Q(roots[source][coordinate]) for source in ids] for coordinate in block]
                rank_before = len(rational_basis(retired))
                center_deficit = len(rational_basis(retired+totals))-rank_before
                union = set(left['early']) | set(right['early'])
                ordinary_clones = 12-len(union)
                helpers = 16+12+ordinary_clones+center_deficit
                require(helpers >= 36, 'The joint basis screen found a smaller helper inventory.')
                minimum_helpers = min(minimum_helpers, helpers)
                pair_results.append(dict(left=left['registers'], right=right['registers'],
                                         early_keys_left=left['early'], early_keys_right=right['early'],
                                         free_face_events=len(early_events), retired_rank=rank_before,
                                         center_rank_deficit=center_deficit, ordinary_clones=ordinary_clones,
                                         optimistic_helpers=helpers))
        require(len(pair_results) == 9 and minimum_helpers == 36,
                'The paired basis family or its minimum has changed.')
        result.append(dict(block=block, candidate_bases=summaries, paired_results=pair_results,
                           minimum_helpers_in_screen=minimum_helpers,
                           fixed_core_helpers=16, fixed_second_face_copies=12))
    # The aggregate ordinary row and one packet row are different objects.
    provider = root/'frontier/refresh-7/proposals/569/providers/width7/eight/FULL-WORD.json.gz'
    word = json.loads(gzip.decompress(provider.read_bytes()))
    require(word['report']['R'] == 504 and word['report']['v'] == 112,
            'The current provider is not the pinned 504-helper interface.')
    report = dict(status='PASS_EXACT_NEGATIVE_JOINT_PARTIAL_BASIS_SCREEN',
                  elapsed_seconds=round(time.monotonic()-started, 6),
                  source_pr=569, source_commit='1424da81263a5305b35e4cf74ef686c275f03f3f',
                  scalar_field='Exact rational arithmetic; the same finite matrices hold over R and C',
                  prototype_sha256=hashlib.sha256((data/'PROTOTYPE.json').read_bytes()).hexdigest(),
                  packet_programs_sha256=hashlib.sha256((data/'PACKET-PROGRAMS.json.gz').read_bytes()).hexdigest(),
                  current_provider_sha256=hashlib.sha256(provider.read_bytes()).hexdigest(),
                  all_blocks=len(result), total_partial_subsets=sum(x['subsets'] for r in result for x in r['candidate_bases']),
                  total_independent_bases=sum(x['bases'] for r in result for x in r['candidate_bases']),
                  both_tetrahedra_partial_bases_reselected=True,
                  exhaustive_paired_center_cuts=sum(len(r['paired_results']) for r in result),
                  minimum_per_block_helpers=36, minimum_full_helpers=504,
                  current_full_helpers=504, helper_paths_saved=0,
                  dirty_helpers_verified=False, physical_owner_verified=False,
                  kappa_improvement_claim=False, negative_control=negative_control, blocks=result,
                  scope='Own rows use four independent existing two-source partials per tetrahedron. '
                        'Each output component is restored once. Existing face functions may be jointly '
                        'refactored before this restoration, but their disjoint SOURCE supports cannot '
                        'cancel outside the component cap. Center totals use only early retired donors, '
                        'plus one optimistic new carrier per missing scalar direction. The fixed 16-helper '
                        'factory and 12 second face copies remain. This is a necessary feasibility and '
                        'inventory screen, not a lower bound for arbitrary interleaved words.')
    args.out.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({k: v for k, v in report.items() if k not in ('blocks', 'negative_control')}, indent=2))


if __name__ == '__main__':
    main()
