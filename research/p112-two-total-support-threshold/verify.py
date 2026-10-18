#!/usr/bin/env python3
"""Exact support thresholds for fixed P112 coordinate readers (stdlib)."""

import argparse
from collections import Counter
from fractions import Fraction
from hashlib import sha1, sha256
import importlib.util
from itertools import combinations, product
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WEIGHTS = (24, 36, 44, 48, 52, 54, 55, 56)
SUBSPACE_COUNTS = (255, 10795, 97155, 200787, 97155, 10795, 255, 1)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def parity(value):
    return value.bit_count() & 1


def rank_f2(rows):
    pivots = {}
    for original in rows:
        value = original
        while value:
            pivot = value.bit_length() - 1
            if pivot in pivots:
                value ^= pivots[pivot]
            else:
                pivots[pivot] = value
                break
    return len(pivots)


def rank_q(rows):
    basis = {}
    for original in rows:
        row = list(map(Fraction, original))
        for pivot, previous in sorted(basis.items()):
            coefficient = row[pivot]
            if coefficient:
                row = [a - coefficient * b for a, b in zip(row, previous)]
        pivot = next((i for i, a in enumerate(row) if a), None)
        if pivot is not None:
            coefficient = row[pivot]
            basis[pivot] = [a / coefficient for a in row]
    return len(basis)


def basis_f2(rows):
    result = []
    for row in rows:
        if rank_f2(result + [row]) > len(result):
            result.append(row)
    return result


def check_sources():
    manifest = json.loads((HERE / 'SOURCES.json').read_text())
    require(manifest['base_commit'] ==
            'a18b4b0136d647529971e9fcb99fa83f5b9a0b81', 'base commit')
    for entry in manifest['files']:
        if entry['usage'] == 'provenance':
            continue  # Bound to base Git by research_package.py, not live input.
        raw = (ROOT / entry['path']).read_bytes()
        require(sha256(raw).hexdigest() == entry['sha256'],
                'source SHA-256: ' + entry['path'])
        blob = sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        require(blob == entry['git_blob'], 'source Git blob: ' + entry['path'])


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def check_geometry(data):
    roots, frame = data['roots'], data['frame']
    labels, duals, x = data['labels'], data['duals'], data['X']
    require(len(roots) == len(labels) == len(duals) == len(x) == 112,
            'P112 port count')
    require(len(frame) == 8 and len({tuple(v) for v in roots}) == 112,
            'frame and distinct root lines')
    require(all(len(v) == 8 and dot(v, v) == 8 for v in roots),
            'scaled E8 root norms')
    require(all(len(v) == 8 and dot(v, v) == 8 for v in frame),
            'scaled frame norms')
    require(all(dot(frame[j], frame[k]) == 0
                for j, k in combinations(range(8), 2)), 'frame orthogonality')
    require(all(0 <= v < 512 for v in labels + duals), 'nine-bit labels')
    require(0 not in labels and len(set(labels)) == 112,
            'distinct nonzero live source labels')
    require(rank_f2(labels) == 9 and rank_f2(duals) == 9,
            'full label and dual spans')
    for i in range(112):
        require(x[i] == [dot(roots[i], f) // 4 for f in frame]
                and all(dot(roots[i], f) % 4 == 0 for f in frame),
                'coordinate columns bound to E8 roots')
        require(all(v in (-1, 0, 1) for v in x[i]), 'coordinate alphabet')
        for k in range(112):
            gram4 = dot(roots[i], roots[k])
            require(gram4 % 4 == 0, 'integral Gram')
            gram = gram4 // 4
            require(dot(x[i], x[k]) == 2 * gram, 'XX^T = 2G')
            require(parity(duals[i] & labels[k]) == ((1 + gram) & 1),
                    'binary pairing identity')


def geometry_mutation_controls(data):
    for field, index, bit in [('labels', 0, 1), ('duals', 0, 1)]:
        bad = dict(data)
        bad[field] = list(data[field])
        bad[field][index] ^= bit
        try:
            check_geometry(bad)
        except ValueError:
            pass
        else:
            raise ValueError('undetected geometry mutation: ' + field)
    bad = dict(data)
    bad['X'] = [list(row) for row in data['X']]
    bad['X'][0][0] = 0
    try:
        check_geometry(bad)
    except ValueError:
        pass
    else:
        raise ValueError('undetected coordinate mutation')


def reader_rows(data, j):
    return [i for i, row in enumerate(data['X']) if row[j] != 0]


def term_rank(data, j, sources):
    """Direct rank of the actual restricted reader/source pairing matrix."""
    rows = reader_rows(data, j)
    labels, duals = data['labels'], data['duals']
    return rank_f2(sum(parity(duals[i] & labels[t]) << p
                       for p, t in enumerate(sources)) for i in rows)


def code_for_reader(data, j):
    """The eight-dimensional binary evaluation code on this reader's support."""
    ports = reader_rows(data, j)
    require(len(ports) == 56, 'coordinate support size')
    dual_basis = basis_f2(data['duals'][i] for i in ports)
    require(len(dual_basis) == 8, 'reader dual span dimension')
    basis = [sum(parity(v & data['labels'][i]) << t
                 for t, i in enumerate(ports)) for v in dual_basis]
    require(rank_f2(basis) == 8, 'baseline COPY rank eight')
    code = [0] * 256
    for a in range(1, 256):
        low = a & -a
        code[a] = code[a ^ low] ^ basis[low.bit_length() - 1]
    require(len(set(code)) == 256, 'distinct evaluation words')
    # A second description enumerates every ambient nine-bit functional.
    ambient = {sum(parity(q & data['labels'][i]) << t
                   for t, i in enumerate(ports)) for q in range(512)}
    require(ambient == set(code), 'ambient quotient code agreement')
    require(Counter(v.bit_count() for v in code) ==
            {0: 1, 24: 63, 28: 128, 32: 63, 56: 1},
            'single-word weight distribution')
    return ports, code


def added_reader_span_census(data):
    """Exact all-functional premise for arbitrary complex on-column readers."""
    exceptions = []
    ranks = Counter()
    for q in range(1, 512):
        rows = [row for row, dual in zip(data['X'], data['duals'])
                if parity(q & dual)]
        rank = rank_q(rows)
        ranks[rank] += 1
        if rank == 7:
            zero_columns = [j for j in range(8)
                            if all(row[j] == 0 for row in rows)]
            require(len(zero_columns) == 1,
                    'rank-seven coordinate-axis kernel')
            exceptions.append({'functional': q,
                               'zero_coordinate': zero_columns[0]})
        else:
            require(rank == 8, 'unexpected functional rational rank')
    require(ranks == {7: 8, 8: 503}, 'complete 511-functional census')
    require(sorted(e['zero_coordinate'] for e in exceptions) ==
            list(range(8)), 'one exceptional kernel per coordinate')
    require(not ({e['functional'] for e in exceptions} & set(data['labels'])),
            'no live source label is exceptional')
    return {'rank_counts': {str(k): v for k, v in sorted(ranks.items())},
            'exceptions': exceptions,
            'distinct_live_labels': len(set(data['labels']))}


def source_price_lower(sites):
    """If the on-column reader span is >=8, its source rank obeys this."""
    require(sites >= 1, 'nonempty source support')
    return next(r for r in range(1, 10) if sites <= 1 << (r + 1))


def two_total_small_support_screen():
    """A lower bill for full-rank on-column factors at union size <=43."""
    records = []
    for union_size in range(1, 44):
        # Distinct source labels imply m<=2^(r+1): the preimage of an
        # r-dimensional image under a map with kernel dimension <=1.
        minimum_added = min(source_price_lower(m1) + source_price_lower(m2)
                            for m1 in range(1, union_size + 1)
                            for m2 in range(1, union_size + 1)
                            if m1 + m2 >= union_size)
        if union_size < 24:
            maximum_retained_loss = 0
        elif union_size < 36:
            maximum_retained_loss = 2
        elif union_size < 40:
            maximum_retained_loss = 4
        else:
            maximum_retained_loss = 5
        require(minimum_added > maximum_retained_loss,
                'strict full-rank COPY floor through 43')
        records.append({'union_size': union_size,
                        'minimum_added_rank': minimum_added,
                        'maximum_retained_loss': maximum_retained_loss})
    return {'records': records,
            'minimum_full_rank_margin': min(r['minimum_added_rank'] -
                                            r['maximum_retained_loss']
                                            for r in records)}


def rref_subspaces(k):
    """Enumerate every k-space of F2^8 once by its unique RREF matrix."""
    for pivots in combinations(range(8), k):
        free = [tuple(c for c in range(p + 1, 8) if c not in pivots)
                for p in pivots]
        choices = [tuple((1 << p) |
                         sum(1 << col for b, col in enumerate(cols)
                             if mask >> b & 1)
                         for mask in range(1 << len(cols)))
                   for p, cols in zip(pivots, free)]
        yield from product(*choices)


def global_mask(local_mask, ports):
    return sum(1 << ports[t] for t in range(56) if local_mask >> t & 1)


def rank_of_surviving_columns(data, j, deleted):
    sources = [i for i in reader_rows(data, j) if i not in deleted]
    return term_rank(data, j, sources)


def generalized_weights(data):
    codes = [code_for_reader(data, j) for j in range(8)]
    minima = [[57] * 8 for _ in range(8)]
    minimizer_counts = [[0] * 8 for _ in range(8)]
    witnesses = [[None] * 8 for _ in range(8)]
    subspace_counts = []
    for d in range(1, 9):
        count = 0
        for rows in rref_subspaces(d):
            count += 1
            for j, (ports, code) in enumerate(codes):
                support = 0
                for row in rows:
                    support |= code[row]
                weight = support.bit_count()
                if weight < minima[j][d - 1]:
                    minima[j][d - 1] = weight
                    minimizer_counts[j][d - 1] = 1
                    witnesses[j][d - 1] = {
                        'rref_rows': list(rows),
                        'deleted_ports': [ports[t] for t in range(56)
                                          if support >> t & 1],
                    }
                elif weight == minima[j][d - 1]:
                    minimizer_counts[j][d - 1] += 1
        subspace_counts.append(count)
    require(tuple(subspace_counts) == SUBSPACE_COUNTS,
            'complete RREF subspace counts')
    require(all(tuple(row) == WEIGHTS for row in minima),
            'generalized support weights')
    for j in range(8):
        for d in range(1, 9):
            deleted = set(witnesses[j][d - 1]['deleted_ports'])
            require(len(deleted) == WEIGHTS[d - 1], 'witness support size')
            require(rank_of_surviving_columns(data, j, deleted) <= 8 - d,
                    'independent direct-rank witness')
            # Removing any one site from a minimum d-erosion witness
            # must restore at least one rank unit.
            require(all(rank_of_surviving_columns(data, j, deleted - {i})
                        >= 9 - d for i in deleted),
                    'one-port-short control')
    return codes, {
        'weights': minima,
        'subspace_counts': subspace_counts,
        'minimizer_counts': minimizer_counts,
        'witnesses': witnesses,
    }


def cross_reader_cuts(data, codes):
    supports = [sum(1 << i for i in reader_rows(data, j)) for j in range(8)]
    require(all((supports[a] & supports[b]).bit_count() == 24
                for a, b in combinations(range(8), 2)),
            'reader support pair intersections')
    cuts = []
    for ports, code in codes:
        cuts.append({global_mask(v, ports) for v in code if v.bit_count() == 24})
    require(all(len(c) == 63 for c in cuts), '63 minimum cuts per reader')
    overlaps = Counter(c for family in cuts for c in family)
    require(Counter(overlaps.values()) == {1: 448, 2: 28},
            'size-24 cross-reader multiplicities')
    common = {}
    for a, b in combinations(range(8), 2):
        intersection = cuts[a] & cuts[b]
        require(len(intersection) == 1, 'one common cut per reader pair')
        common[f'{a},{b}'] = sorted(i for i in range(112)
                                if next(iter(intersection)) >> i & 1)
    # Any rank drop requires the source deletion set to contain a nonzero
    # evaluation word. Search all pair unions below 40 and rule out a third.
    under_40 = [{global_mask(v, ports) for v in code
                 if 0 < v.bit_count() < 40} for ports, code in codes]
    require(all(len(c) == 254 for c in under_40), 'all cuts below 40')
    triple_witness = None
    for a, b, c in combinations(range(8), 3):
        pair_unions = {x | y for x in under_40[a] for y in under_40[b]
                       if (x | y).bit_count() < 40}
        require(all((u | z).bit_count() >= 40
                    for u in pair_unions for z in under_40[c]),
                'no triple rank drop below 40 source sites')
        if triple_witness is None:
            options = ((x | y | z, x, y, z)
                       for x in cuts[a] for y in cuts[b] for z in cuts[c])
            triple_witness = next((t for t in options if t[0].bit_count() == 40),
                                  None)
    require(triple_witness is not None, 'triple combinatorial threshold 40')
    triple_ports = [i for i in range(112)
                    if triple_witness[0] >> i & 1]
    require(all(rank_of_surviving_columns(data, j, set(triple_ports)) <= 7
                for j in (0, 1, 2)), 'three-reader direct-rank witness')
    # The word weights jump from 32 to 56, so under_40 is also the full
    # nonzero cut inventory below 44. Every four-reader drop below 44
    # contains one of these exact unions.
    # Their 42 minimal supports have size 40; a fifth reader needs >=4
    # additional sites. Along with w_2=36 and pairwise |S_a cap S_b|=24,
    # at most one of four dropping readers can lose a second rank unit.
    pair_unions_44 = {}
    for a, b in combinations(range(8), 2):
        pair_unions_44[a, b] = {x | y for x in under_40[a]
                               for y in under_40[b]
                               if (x | y).bit_count() < 44}
    four_masks = set()
    for a, b, c, d in combinations(range(8), 4):
        four_masks.update(x | y for x in pair_unions_44[a, b]
                          for y in pair_unions_44[c, d]
                          if (x | y).bit_count() < 44)
    require(len(four_masks) == 42 and
            all(x.bit_count() == 40 for x in four_masks),
            'all four-reader cuts below 44')
    for mask in four_masks:
        hit = [j for j in range(8)
               if any((word & ~mask) == 0 for word in under_40[j])]
        require(len(hit) == 4, 'four-reader cut hits exactly four')
        require(all((word & ~mask).bit_count() >= 4
                    for j in range(8) if j not in hit
                    for word in under_40[j]),
                'fifth reader needs four more ports')
    return {'minimum_cut_multiplicity':
            {str(k): v for k, v in sorted(Counter(overlaps.values()).items())},
            'common_minimum_cuts': common,
            'triple_minimum_union': 40,
            'triple_witness_ports': triple_ports,
            'four_reader_cuts_below_44': len(four_masks),
            'four_reader_cut_sizes': sorted({x.bit_count() for x in four_masks}),
            'reader_support_pair_intersection': 24}


def two_total_fixture(data, common_ports):
    """Full-rank coupled two-total identity at the sharp 24-site boundary."""
    c = set(common_ports)
    require(len(c) == 24, 'fixture cut length')
    x = [[row[j] for row in data['X']] for j in range(8)]

    def evaluate(deleted):
        # A has rows (1,1), (1,-1), then six zero rows. Its columns
        # overlap at both retained coordinates and have rank two.
        z1 = [(x[0][i] + x[1][i]) // 2 if i in deleted else 0
              for i in range(112)]
        z2 = [(x[0][i] - x[1][i]) // 2 if i in deleted else 0
              for i in range(112)]
        require(all((x[0][i] + x[1][i]) % 2 == 0 and
                    (x[0][i] - x[1][i]) % 2 == 0 for i in deleted),
                'integral fixture sources')
        require(any(z1[i] * z2[k] != z2[i] * z1[k]
                    for i in range(112) for k in range(i + 1, 112)),
                'independent source columns')
        d1 = [a + b for a, b in zip(x[0], x[1])]
        d2 = [a - b for a, b in zip(x[0], x[1])]
        t0 = [a - b - c0 for a, b, c0 in zip(x[0], z1, z2)]
        t1 = [a - b + c0 for a, b, c0 in zip(x[1], z1, z2)]
        t = [t0, t1] + x[2:]
        # The identity is checked entrywise, independently of supports.
        for i in range(112):
            for k in range(112):
                lhs = sum(col[i] * col[k] for col in x)
                rhs = sum(col[i] * src[k] for col, src in zip(x, t))
                rhs += d1[i] * z1[k] + d2[i] * z2[k]
                require(lhs == rhs, 'full ten-term matrix identity')
        require(any(d1[i] * z1[k] for i in range(112) for k in range(112))
                and any(d2[i] * z2[k] for i in range(112) for k in range(112)),
                'either omitted added term changes the matrix')
        def beta(reader, source):
            rs = [i for i, value in enumerate(reader) if value]
            ss = [i for i, value in enumerate(source) if value]
            return rank_f2(sum(parity(data['duals'][i] &
                                      data['labels'][k]) << p
                               for p, k in enumerate(ss)) for i in rs)
        costs = [beta(r, s) for r, s in zip(x + [d1, d2], t + [z1, z2])]
        return {'source_union_size': len(deleted), 'retained_ranks': costs[:8],
                'added_ranks': costs[8:], 'total_copy_rank': sum(costs)}

    full = evaluate(c)
    short = evaluate(c - {min(c)})
    require(full['retained_ranks'] == [7, 7] + [8] * 6 and
            short['retained_ranks'] == [8] * 8, 'sharp 24-site boundary')
    require(full['total_copy_rank'] >= 64 and
            short['total_copy_rank'] >= 64, 'no fixture cost claim')
    return {'at_24': full, 'at_23': short}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', type=Path, help='write a new receipt path')
    args = parser.parse_args()
    check_sources()
    data = json.loads((ROOT / 'research/p112-single-lift/reference-geometry.json').read_text())
    check_geometry(data)
    geometry_mutation_controls(data)
    # Rebuild from the predecessor's exact root-coordinate generator and
    # compare every geometry field. No previous cost or proof checker is imported.
    geometry_file = ROOT / 'research/p112-single-lift/geometry.py'
    spec = importlib.util.spec_from_file_location('p112_reference_geometry', geometry_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    require(module.build() == data, 'independent geometry reconstruction')
    codes, weights = generalized_weights(data)
    cuts = cross_reader_cuts(data, codes)
    span_census = added_reader_span_census(data)
    screen = two_total_small_support_screen()
    fixture = two_total_fixture(data, cuts['common_minimum_cuts']['0,1'])
    result = {'schema_version': 1, 'base_commit':
              'a18b4b0136d647529971e9fcb99fa83f5b9a0b81',
              'source_geometry_sha256': sha256((ROOT /
                  'research/p112-single-lift/reference-geometry.json').read_bytes()).hexdigest(),
              'generalized_weights': weights, 'cross_reader_cuts': cuts,
              'added_reader_span_census': span_census,
              'two_total_small_support_screen': screen,
              'two_total_fixture': fixture}
    if args.write:
        with args.write.open('x', encoding='utf-8') as out:
            json.dump(result, out, sort_keys=True, indent=2)
            out.write('\n')
    else:
        expected = json.loads((HERE / 'RESULT.json').read_text())
        require(result == expected, 'full RESULT.json comparison')
    print('PASS_P112_TWO_TOTAL_SUPPORT_THRESHOLD weights=24,36,44,48,52,54,55,56 '
          'union_floor=43 triple=40 fixture=24 '
          'controls=source,geometry,omission,one-port-short')


if __name__ == '__main__':
    main()
