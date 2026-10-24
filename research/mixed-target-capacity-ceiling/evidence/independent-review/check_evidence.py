#!/usr/bin/env python3
"""Independent scalar-data and exact invoice audit, not an operator replay."""
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def require(value, message):
    if not value:
        raise RuntimeError(message)


def edge_property(matrix, directions):
    return all(not x or (directions[s] & directions[j]).bit_count() % 2 == 0
               for s, row in enumerate(matrix) for j, x in enumerate(row))


def main():
    pins = {
        'CODE.json': '8be7f3f073b7981ec91c6af43edff0ac8a89f4824ef6026ae758c287dd6c03d0',
        'NORMALIZERS.json': 'ae8aad06aa5d1811d725895b3ab5a4f4daa9dcdd88294aa0d5f723e78bb1e0da',
    }
    for name, digest in pins.items():
        require(sha256((HERE / 'frozen' / name).read_bytes()).hexdigest() == digest,
                'Source pin mismatch: ' + name)
    code = json.loads((HERE / 'frozen/CODE.json').read_text())
    ports = json.loads((HERE / 'frozen/NORMALIZERS.json').read_text())['ports']
    matrix = [[Fraction(x) for x in row] for row in code['A']]
    require(len(matrix) == 112 and all(len(row) == 112 for row in matrix)
            and len(ports) == 112, 'Wrong source dimensions')
    # G is stored by rows. Its image of the first basis vector uses the
    # first BIT of each row, not the first literal row as a column.
    directions = [sum((row & 1) << bit for bit, row in enumerate(p['G_rows']))
                  for p in ports]
    require(all(q == p['q'] for q, p in zip(directions, ports)),
            'Rows/columns or declared source q mismatch')
    require(len(set(directions)) == 112, 'Non-distinct source directions')
    require(all(q.bit_count() % 2 == 1 for q in directions), 'Non-odd direction')
    require(all(((p['G_rows'][i] & p['G_rows'][j]).bit_count() % 2) == (i == j)
                for p in ports for i in range(9) for j in range(9)),
            'Source G lost orthogonality')
    require(edge_property(matrix, directions), 'Supported source edge is not orthogonal')
    edge_count = sum(bool(x) for row in matrix for x in row)
    require(edge_count == 5824, 'Source edge census mismatch')

    native = {1: 2201, 2: 412, 3: 510, 4: 127, 5: 40}
    paid = {r: 2 * count for r, count in native.items()}
    for rank, count in {1: 112 + 94, 2: 14, 5: 56}.items():
        paid[rank] += count
    target = {17: 112, 16: 112, 9: 816}
    mass = lambda p: sum(rank * count for rank, count in p.items())
    require(paid == {1: 4608, 2: 838, 3: 1020, 4: 254, 5: 136},
            'Paid decomposition mismatch')
    require(mass(paid) == mass(target) == 11040, 'Mass mismatch')
    require(sum(target.values()) == 1040 and min(target) > max(paid),
            'Owner census/support gap mismatch')
    require(2 * 408 == 816 and 2 * (47 + 7 + 28) == 94 + 14 + 56,
            'Helper complement multiplicity mismatch')

    bad_matrix = [row.copy() for row in matrix]
    bad_matrix[0][0] = Fraction(1)
    duplicated = directions.copy()
    duplicated[1] = duplicated[0]
    bad_paid = paid.copy()
    bad_paid[1] -= 112
    bad_target = {17: 113, 16: 111, 9: 816}
    controls = {
        'reject_added_nonzero_diagonal': not edge_property(bad_matrix, directions),
        'reject_duplicate_direction': len(set(duplicated)) != 112,
        'reject_omitted_query_bank_mass': mass(bad_paid) != 11040,
        'reject_unfunded_113th_fullrank_target_mass': mass(bad_target) != mass(paid),
    }
    require(all(controls.values()), 'Mutation control failed')
    print(json.dumps({
        'status': 'PASS_INDEPENDENT_SCALAR_SOURCE_AND_INVOICE_ONLY',
        'source_edges': edge_count,
        'nonorthogonal_supported_edges': 0,
        'direction_convention': 'G rows; image of e_q formed from first bit of each row',
        'paid': paid, 'optimistic_target': target,
        'paid_mass': mass(paid), 'optimistic_target_mass': mass(target),
        'target_min_rank': min(target), 'paid_max_rank': max(paid),
        'controls': controls,
        'scope': 'Exact existing scalar source data and invoice arithmetic only; no native, '
                 'operator, group enumeration, solver, compiler, Lean or moment scan.',
    }, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
