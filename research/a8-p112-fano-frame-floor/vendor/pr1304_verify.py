#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact finite lemmas for one A8 simplex P112 decoder floor.

The deficiency method follows mightyOil's PR1248. This implementation extends
it to the declared puncture, enumerating every subspace of every partner space.
No predecessor code, numerical solver, or unproved symmetry reduction is used.
"""

import argparse
from collections import Counter
from fractions import Fraction
from itertools import combinations
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
FRAME = (0, 15, 26, 33, 42, 89, 112, 119)
FULL = (1 << 9) - 1


def require(condition, message):
    if not condition:
        raise ValueError(message)


def binary_basis(vectors):
    pivots = {}
    for value in vectors:
        while value:
            p = value.bit_length() - 1
            if p in pivots:
                value ^= pivots[p]
            else:
                pivots[p] = value
                break
    return tuple(pivots[p] for p in sorted(pivots, reverse=True))


def rank(vectors):
    return len(binary_basis(vectors))


def rational_rank(rows):
    pivots = {}
    for row in rows:
        v = list(map(Fraction, row))
        for p in range(len(v)):
            if not v[p]:
                continue
            if p in pivots:
                multiple = v[p]
                v = [x - multiple * y for x, y in zip(v, pivots[p])]
            else:
                multiple = v[p]
                pivots[p] = [x / multiple for x in v]
                break
    return len(pivots)


def members(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def model():
    """Rows are (binary label, v=3r), in the declared canonical order."""
    rows = []
    for a, b in combinations(range(9), 2):
        rows.append((FULL ^ (1 << a) ^ (1 << b),
                     tuple(3 * (int(k == a) - int(k == b)) for k in range(9))))
    for triple in combinations(range(9), 3):
        label = sum(1 << k for k in triple)
        rows.append((label, tuple(2 if k in triple else -1 for k in range(9))))
    return rows


def first_frame(rows):
    adjacency = [{j for j in range(i + 1, len(rows))
                  if dot(rows[i][1], rows[j][1]) == 0} for i in range(len(rows))]

    def visit(prefix, candidates):
        if len(prefix) == 8:
            return prefix
        for i in sorted(candidates):
            rest = candidates & adjacency[i]
            if len(prefix) + 1 + len(rest) >= 8:
                found = visit(prefix + (i,), rest)
                if found is not None:
                    return found
        return None

    return visit((), set(range(len(rows))))


def matching_frame_orbit(rows):
    """Coordinate-permutation images: choose one singleton and four pairs."""
    lookup = {v: i for i, (_, v) in enumerate(rows)}

    def matchings(items):
        if not items:
            yield ()
            return
        a = items[0]
        for b in items[1:]:
            for rest in matchings(tuple(x for x in items[1:] if x != b)):
                yield ((a, b),) + rest

    frames = set()
    for singleton in range(9):
        for pairs in matchings(tuple(k for k in range(9) if k != singleton)):
            indices = []
            for a, b in pairs:
                pair = tuple(3 * (int(k == a) - int(k == b)) for k in range(9))
                triple = tuple(2 if k in (a, b, singleton) else -1 for k in range(9))
                indices.extend((lookup[pair], lookup[triple]))
            frame = tuple(sorted(indices))
            require(all(dot(rows[i][1], rows[j][1]) == 0 for i, j in combinations(frame, 2)),
                    'matching-frame orbit orthogonality')
            frames.add(frame)
    require(len(frames) == 945 and FRAME in frames, 'matching-frame orbit count')
    return len(frames)


def check_model(rows, frame=FRAME):
    require(len(rows) == 120 and len({u for u, _ in rows}) == 120,
            '120 distinct root labels required')
    require(len(frame) == 8 and len(set(frame)) == 8 and
            all(type(i) is int and 0 <= i < 120 for i in frame), 'frame shape')
    for i, j in combinations(frame, 2):
        require(dot(rows[i][1], rows[j][1]) == 0, 'puncture must be an orthogonal frame')
    for u, v in rows:
        require(sum(v) == 0 and dot(v, v) == 18, 'sum-zero norm-two root')
        for w, z in rows:
            gram, remainder = divmod(dot(v, z), 9)
            require(remainder == 0, 'integral Gram entries')
            require((u & w).bit_count() % 2 == (gram + 1) % 2,
                    'binary label/Gram pairing')
    live = [row for i, row in enumerate(rows) if i not in frame]
    require(len(live) == 112 and rational_rank(v for _, v in live) == 8,
            'live roots span the eight-dimensional sum-zero space')
    require(rank(u for u, _ in live) == 9, 'live labels span F2^9')
    for k in range(9):
        require(rank(u for u, v in live if v[k]) == 9, 'column support label rank nine')
    return live


def tables(live):
    words = [sum(((u & w).bit_count() % 2) << i
                 for i, (u, _) in enumerate(live)) for w in range(512)]
    unequal = {(j, k): sum((v[j] != v[k]) << i for i, (_, v) in enumerate(live))
               for j, k in combinations(range(9), 2)}
    return words, unequal


def compatibility_spaces(live, words, unequal, anchor):
    others = [k for k in range(9) if k != anchor]
    allowed, forced = {}, {}
    for k in others:
        different = unequal[min(k, anchor), max(k, anchor)]
        allowed[k] = [sum(1 << z for z in range(1, 512)
                          if not (words[w] & words[z] & different))
                      for w in range(512)]
        for z in range(1, 512):
            support = words[z] & different
            forced[k, z] = binary_basis(u for i, (u, _) in enumerate(live)
                                        if support >> i & 1)
    return others, allowed, forced


def plane_configurations(others, allowed):
    """Every plane has exactly one encoding 0<a<b<a xor b."""
    configs = {}
    histogram = Counter()
    planes = 0
    for a in range(1, 512):
        for b in range(a + 1, 512):
            if b >= (a ^ b):
                continue
            planes += 1
            hs = tuple(allowed[k][a] & allowed[k][b] for k in others)
            dimensions = []
            for h in hs:
                vectors = list(members(h))
                require(len(vectors) in (0, 1, 3), 'partner space dimension at most two')
                if len(vectors) == 3:
                    require(vectors[0] ^ vectors[1] == vectors[2], 'partner plane closure')
                dimensions.append((len(vectors) + 1).bit_length() - 1)
            histogram[tuple(sorted(dimensions))] += 1
            if hs not in configs:
                configs[hs] = {'first_plane': (a, b), 'multiplicity': 0}
            configs[hs]['multiplicity'] += 1
    require(planes == 43435 and sum(c['multiplicity'] for c in configs.values()) == planes,
            'complete plane coverage')
    return configs, [{'dimensions': list(ds), 'planes': count}
                     for ds, count in sorted(histogram.items())]


def subspace_options(k, h, forced, words):
    """All subspaces of H: zero, every line, and H itself if dim H=2."""
    vectors = list(members(h))
    require(len(vectors) in (0, 1, 3), 'unsupported partner dimension')
    options = [((), (), 0)]
    for z in vectors:
        options.append(((z,), forced[k, z], words[z]))
    if len(vectors) == 3:
        require(vectors[0] ^ vectors[1] == vectors[2], 'partner plane closure')
        options.append((binary_basis(vectors),
                        binary_basis(x for z in vectors for x in forced[k, z]),
                        words[vectors[0]] | words[vectors[1]]))
    return options


def enumerate_configuration(others, hs, forced, words, unequal, mutual=True):
    choices = [(k, subspace_options(k, h, forced, words)) for k, h in zip(others, hs)]
    choices.sort(key=lambda item: -len(item[1]))
    best, leaves, conflicts = 0, 0, 0

    def visit(position, constraints, dimension_sum, selected):
        nonlocal best, leaves, conflicts
        if position == len(choices):
            leaves += 1
            # K_anchor is contained in the annihilator of these constraints.
            best = max(best, 9 - len(constraints) + dimension_sum)
            return
        k, options = choices[position]
        for zs, fs, support in options:
            if mutual and any(support & old_support & unequal[min(k, j), max(k, j)]
                              for j, old_support in selected):
                conflicts += 1
                continue
            visit(position + 1, binary_basis(constraints + fs),
                  dimension_sum + len(zs), selected + [(k, support)])

    visit(0, (), 0, [])
    return best, leaves, conflicts


def census(live, words, unequal):
    result = []
    for anchor in range(9):
        others, allowed, forced = compatibility_spaces(live, words, unequal, anchor)
        configs, histogram = plane_configurations(others, allowed)
        maxima = Counter()
        leaves = conflicts = 0
        for hs in configs:
            maximum, count, rejected = enumerate_configuration(others, hs, forced, words, unequal)
            require(maximum <= 10, 'total deficiency exceeds ten')
            maxima[maximum] += 1
            leaves += count
            conflicts += rejected
        result.append({'anchor': anchor, 'planes': 43435, 'configurations': len(configs),
                       'partner_dimension_histogram': histogram,
                       'maximum_histogram': dict(sorted(maxima.items())),
                       'compatible_leaves': leaves, 'rejected_branches': conflicts})
    return result


def check_identity(live, coefficients):
    require(len(coefficients) == len(live) and all(len(c) == 9 for c in coefficients),
            'decoder shape')
    for (_, v), c in zip(live, coefficients):
        for _, z in live:
            require(dot(c, z) == 2 * dot(v, z), 'exact all-pairs identity')


def witness(live, all_active):
    # The first live line is e_0-e_2. Switch its anchor to 2 to activate term 0.
    c = [tuple(2 * (x - v[2 if all_active and i == 0 else 0]) for x in v)
         for i, (_, v) in enumerate(live)]
    check_identity(live, c)
    costs = [rank(u for (u, _), row in zip(live, c) if row[k]) for k in range(9)]
    require(sum(costs) == 71, 'witness cost must be seventy-one')
    require(not all_active or min(costs) > 0, 'all nine terms must be active')
    return c, costs


def semantic_controls(rows, live, words, unequal, c):
    passed = []

    def rejected(name, function):
        try:
            function()
        except ValueError:
            passed.append(name)
            return
        raise ValueError('control unexpectedly accepted: ' + name)

    bad = list(c)
    bad[0] = tuple(x + (k == 0) for k, x in enumerate(bad[0]))
    rejected('coefficient_perturbation', lambda: check_identity(live, bad))
    bad = list(c)
    bad[0] = (0,) + bad[0][1:]
    rejected('active_term_deleted', lambda: check_identity(live, bad))
    corrupt = list(rows)
    corrupt[1] = (corrupt[1][0] ^ 1, corrupt[1][1])
    rejected('label_pairing_corrupted', lambda: check_model(corrupt))
    rejected('nonorthogonal_puncture', lambda: check_model(rows, (1,) + FRAME[1:]))
    others, allowed, forced = compatibility_spaces(live, words, unequal, 0)
    hs = tuple(allowed[k][1] & allowed[k][508] for k in others)
    require(hs[0].bit_count() == 3, 'puncturing permits a partner plane')
    rejected('unpunctured_dimension_lemma', lambda: require(hs[0].bit_count() <= 1,
                                                          'false dimension-one inference'))
    relaxed, _, _ = enumerate_configuration(others, hs, forced, words, unequal, mutual=False)
    checked, _, _ = enumerate_configuration(others, hs, forced, words, unequal)
    require(relaxed == 11 and checked == 10, 'mutual compatibility is necessary')
    passed.append('omitted_mutual_compatibility_changes_bound')
    rejected('false_cost_seventy', lambda: require(sum(rank(u for (u, _), row in zip(live, c)
                                                            if row[k]) for k in range(9)) == 70,
                                                 'support ranks disagree with claimed cost'))
    # A non-real shift C_i = 2v_i + 3i*1, checked using integer real/imaginary parts.
    check_identity(live, [tuple(2 * x for x in v) for _, v in live])
    require(all(dot((3,) * 9, v) == 0 for _, v in live), 'imaginary shift is in the kernel')
    require(9 * rank(u for u, _ in live) == 81, 'generic complex shift cost')
    passed.append('nonreal_kernel_shift_positive')
    return passed


def compute():
    rows = model()
    require(first_frame(rows) == FRAME, 'declared frame is not lexicographically first')
    live = check_model(rows)
    words, unequal = tables(live)
    anchors = census(live, words, unequal)
    _, dropped = witness(live, False)
    c, active = witness(live, True)
    result = {'schema_version': 1, 'kind': 'scoped proof with exhaustive finite lemmas',
              'model': 'fixed A8 simplex; one P112 frame puncture; all-pairs; separate term costs',
              'frame_indices': list(FRAME), 'frame_labels': [rows[i][0] for i in FRAME],
              'coordinate_permutation_punctures': matching_frame_orbit(rows),
              'live_roots': 112, 'live_root_rank': 8, 'column_label_ranks': [9] * 9,
              'anchors': anchors, 'total_planes': sum(a['planes'] for a in anchors),
              'total_configurations': sum(a['configurations'] for a in anchors),
              'total_compatible_leaves': sum(a['compatible_leaves'] for a in anchors),
              'deficiency_upper_bound': 10, 'sharp_copy_cost': 71,
              'dropped_witness_costs': dropped, 'active_witness_costs': active,
              'all_pairs_checked_per_witness': 112 * 112,
              'semantic_controls': semantic_controls(rows, live, words, unequal, c)}
    return json.loads(json.dumps(result))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='regenerate the deterministic certificate')
    args = parser.parse_args()
    path = HERE / 'CERTIFICATE.json'
    expected = None if args.write else json.loads(path.read_text())
    result = compute()
    if args.write:
        path.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    else:
        require(expected == result, 'certificate differs from exact replay')
    print('PASS_A8_P112_DECODER_FLOOR planes=390915 configurations=19299 '
          'compatible_leaves=462141 cost=71 controls=8')


if __name__ == '__main__':
    main()
