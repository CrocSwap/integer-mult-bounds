#!/usr/bin/env python3
"""Exact certificate for full-six-plane rectangle cancellation over F_2.

Rebuilds the 60 lines and 30 six-line planes from the current exact geometry.
Run with no arguments to print a certificate; --verify FILE checks a saved copy.
Uses only the Python standard library. No optimizer or floating-point ranks.
"""
from collections import Counter
from itertools import combinations
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from geometry.core import Geometry


def eliminate(columns):
    basis = {}
    kernel = []
    for index, column in enumerate(columns):
        value, combination = column, 1 << index
        while value:
            pivot = value.bit_length() - 1
            if pivot not in basis:
                basis[pivot] = (value, combination)
                break
            earlier, relation = basis[pivot]
            value ^= earlier
            combination ^= relation
        if not value:
            kernel.append(combination)
    return basis, kernel


def xor_selected(values, selection):
    result = 0
    while selection:
        bit = selection & -selection
        result ^= values[bit.bit_length() - 1]
        selection ^= bit
    return result


def reconstruct(target, values, allowed):
    basis = {}
    for index in allowed:
        value, combination = values[index], 1 << index
        while value:
            pivot = value.bit_length() - 1
            if pivot not in basis:
                basis[pivot] = (value, combination)
                break
            earlier, relation = basis[pivot]
            value ^= earlier
            combination ^= relation
    value, combination = target, 0
    while value:
        pivot = value.bit_length() - 1
        if pivot not in basis:
            raise AssertionError('The required row reconstruction does not exist.')
        earlier, relation = basis[pivot]
        value ^= earlier
        combination ^= relation
    return tuple(i for i in allowed if combination >> i & 1)


def minimum_short_reconstruction(target, values, allowed):
    # Every incidence row and the target has odd weight, so only odd lengths
    # can work. Exhaust weights one, three, and five before testing seven.
    for j in allowed:
        if values[j] == target:
            return (j,)
    triples = {}
    for a, b, c in combinations(allowed, 3):
        value = values[a] ^ values[b] ^ values[c]
        triples.setdefault(value, (a, b, c))
    if target in triples:
        return triples[target]
    for a, b in combinations(allowed, 2):
        triple = triples.get(target ^ values[a] ^ values[b])
        if triple is not None:
            answer = tuple(sorted((a, b) + triple))
            assert len(set(answer)) == 5
            return answer
    for a, b, c, d in combinations(allowed, 4):
        triple = triples.get(target ^ values[a] ^ values[b] ^ values[c] ^ values[d])
        if triple is not None:
            answer = tuple(sorted((a, b, c, d) + triple))
            assert len(set(answer)) == 7
            return answer
    raise AssertionError('No reconstruction through weight seven.')


def check_witness(i, witness, incidence, geometry):
    assert len(set(witness)) == len(witness)
    assert all(j != i and geometry.gram[i][j] != (0, 0) for j in witness)
    assert xor_selected(incidence, sum(1 << j for j in witness)) == incidence[i]


def certificate():
    geometry = Geometry()
    # Enumerate pair closures instead of trusting the stored flat catalog.
    planes = sorted({geometry.closure((i, j)) for i in range(60)
                     for j in range(i) if len(geometry.closure((i, j))) == 6})
    assert len(planes) == 30
    assert all(geometry.rank(plane) == 2 for plane in planes)
    incidence = [sum(1 << p for p, plane in enumerate(planes) if i in plane)
                 for i in range(60)]
    assert all(bin(row).count('1') == 3 for row in incidence)
    witnesses = []
    for i in range(60):
        allowed = [j for j in range(60) if j != i and geometry.gram[i][j] != (0, 0)]
        witness = minimum_short_reconstruction(incidence[i], incidence, allowed)
        check_witness(i, witness, incidence, geometry)
        try:
            check_witness(i, witness[1:], incidence, geometry)
        except AssertionError:
            pass
        else:
            raise AssertionError('Altered witness was incorrectly accepted.')
        orthogonal_index = next(j for j in range(60)
                                if j != i and geometry.gram[i][j] == (0, 0))
        try:
            check_witness(i, (orthogonal_index,) + witness[1:], incidence, geometry)
        except AssertionError:
            pass
        else:
            raise AssertionError('An orthogonal witness index was incorrectly accepted.')
        clique = (i,) + witness
        assert all(geometry.gram[a][b] != (0, 0) for a, b in combinations(clique, 2))
        assert all(len(set(clique) & set(plane)) in (0, 2) for plane in planes)
        witnesses.append(witness)
    forced = [(i, j) for i in range(60) for j in range(60)
              if i != j and geometry.gram[i][j] != (0, 0)]
    assert len(forced) == 2640
    lookup = {pair: index for index, pair in enumerate(forced)}
    census = Counter()
    columns, diagonals, pairs = [], [], []
    for a, readers in enumerate(planes):
        for b, sources in enumerate(planes):
            charge = geometry.pairing_rank(readers, sources)
            census[charge] += 1
            column = sum(1 << lookup[i, j] for i in readers for j in sources
                         if (i, j) in lookup)
            diagonal = sum(1 << i for i in set(readers) & set(sources))
            if not charge:
                assert column == diagonal == 0
                continue
            columns.append(column)
            diagonals.append(diagonal)
            pairs.append((a, b, charge))
    basis, kernel = eliminate(columns)
    assert census == {0: 30, 1: 360, 2: 510}
    assert len(basis) == 595 and len(kernel) == 275
    assert len(eliminate(kernel)[0]) == 275
    for relation in kernel:
        assert xor_selected(columns, relation) == 0
        assert xor_selected(diagonals, relation) == 0
    return {
        'status': 'PASS: exact restricted obstruction, not an unrestricted lower bound',
        'base_commit': '66849e1475c930fd7732b1a0067ffee7e1e95f60',
        'seed': 3476255234,
        'originating_task_id': '01a13378-812e-75b3-9b4b-0dd927f1901a',
        'subagent_task': '/root/asymmetric_search',
        'started_at_UTC': '2026-10-13 05:02:22 UTC',
        'ordering': 'Lexicographic exact line and plane ordering; deterministic elimination',
        'all_oriented_plane_pairs': 900,
        'pairing_rank_census': {str(k): v for k, v in sorted(census.items())},
        'forced_offdiagonal_count': 2640,
        'positive_cost_column_count': 870,
        'forced_column_rank_F2': 595,
        'forced_kernel_dimension': 275,
        'all_kernel_diagonal_images_zero': True,
        'six_line_planes': planes,
        'positive_cost_plane_pairs': pairs,
        'kernel_basis_hex': [hex(x) for x in kernel],
        'incidence_row_reconstruction_witnesses': witnesses,
        'minimum_witness_weight_census': dict(Counter(map(len, witnesses))),
        'incidence_rank_F2': len(eliminate(incidence)[0]),
        'all_witness_eight_sets_pairwise_nonorthogonal': True,
        'all_witness_eight_sets_meet_planes_in_zero_or_two': True,
        'altered_witnesses_rejected': 60,
        'altered_orthogonality_witnesses_rejected': 60,
        'stronger_scope': 'Every column of B lies in the binary span of the thirty full-six-plane indicators. If all distinct nonorthogonal entries of B vanish, every diagonal entry vanishes. Transposition gives the corresponding row-space statement.',
        'control_extension': 'A decoder mixing this uniform-side family with any individually forbidden-free rectangles costs at least sixty. The full-six-plane component has zero diagonal; controls cost at least their diagonal support size.',
        'not_covered': 'Rectangles with arbitrary partial plane supports on both sides, mixtures of the two uniform-side classes, or mixtures with other forbidden-entry-producing supports.',
        'line_coordinates_sha256': hashlib.sha256(json.dumps(geometry.lines, separators=(',', ':')).encode()).hexdigest(),
        'verifier_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'stopping_condition': 'Exhaustive domain completed by exact binary elimination and all sixty incidence witnesses; no MILP required.',
    }


if __name__ == '__main__':
    if sys.flags.optimize:
        raise SystemExit('Run without -O because this certificate uses assertions.')
    output = certificate()
    if len(sys.argv) == 3 and sys.argv[1] == '--verify':
        saved = json.loads(Path(sys.argv[2]).read_text())
        assert json.loads(json.dumps(output)) == saved
        print('PASS: saved six-plane certificate agrees with exact reconstruction.')
    elif len(sys.argv) == 1:
        print(json.dumps(output, sort_keys=True, indent=2))
    else:
        raise SystemExit('Usage: six_plane_certificate.py [--verify FILE]')
