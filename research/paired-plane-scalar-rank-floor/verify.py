#!/usr/bin/env python3
"""Read-only exact witness replay with fail-closed controls."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from model import HERE, ROOT, authenticated_model, construct, fitting, require


def check(certificate, pairs, nonorthogonal):
    clique = certificate['plane_clique']
    require(len(clique) == 24 and len(set(clique)) == 24 and
            all(type(v) is int and 0 <= v < 56 for v in clique), '24 distinct clique planes')
    require(all(nonorthogonal[i][j] for i in clique for j in clique), 'clique nonorthogonality')
    ports = sorted(port for plane in clique for port in pairs[plane])
    require(ports == certificate['port_clique'] and len(ports) == 48, '48 principal ports')
    classes = certificate['orthogonal_classes']
    require(len(classes) == 25 and all(classes), '25 nonempty classes')
    require(sorted(v for group in classes for v in group) == list(range(56)), 'plane class partition')
    require(all(not nonorthogonal[i][j] for group in classes for i in group for j in group if i != j),
            'orthogonal class pairs')
    supports, matrix = construct(classes, pairs)
    require(fitting(matrix, pairs, nonorthogonal), 'scalar fit')
    require(sorted(i for support in supports for i in support) == list(range(112)), 'disjoint channel supports')
    pivots = [support[0] for support in supports]
    require(all(matrix[i][j] == int(i == j) for i in pivots for j in pivots), 'I50 rank witness')
    require(all(matrix[i][j] == int(i == j) for i in ports for j in ports), 'I48 principal witness')
    return supports, matrix, ports


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--certificate', type=Path, default=HERE / 'CERTIFICATE.json')
    parser.add_argument('--receipt', type=Path, default=HERE / 'RESULTS.json')
    parser.add_argument('--write-receipt', action='store_true')
    args = parser.parse_args()
    labels, pairs, nonorthogonal = authenticated_model(args.root)
    certificate = json.loads(args.certificate.read_text(encoding='utf-8'))
    supports, matrix, ports = check(certificate, pairs, nonorthogonal)
    owner = {port: plane for plane, pair in enumerate(pairs) for port in pair}
    # Linear symbolic dirty-target update z <- z + K*x. Each of the 112 source
    # basis vectors is checked with a nonzero target, plus dense signed sources.
    vectors = [[int(i == j) for i in range(112)] for j in range(112)]
    vectors += [[((i + 3) * (seed + 7)) % 19 - 9 for i in range(112)] for seed in range(8)]
    for source in vectors:
        dirty = [i - 53 for i in range(112)]
        actual = dirty[:]
        for support in supports:
            value = sum(source[j] for j in support)
            for i in support:
                actual[i] += value
        expected = [dirty[i] + sum(matrix[i][j] * source[j] for j in range(112)) for i in range(112)]
        require(actual == expected, 'dirty scalar update')
    # A free plane pair is found by the full four-pairing test. Mistaking its
    # nonorthogonal complement for free must be rejected, regardless of parity.
    bad = [row[:] for row in matrix]
    bad[ports[0]][ports[1]] = 1
    require(not fitting(bad, pairs, nonorthogonal), 'nonorthogonal offdiagonal control')
    bad = [row[:] for row in matrix]
    bad[ports[0]][ports[0]] = 0
    require(not fitting(bad, pairs, nonorthogonal), 'diagonal control')
    bad = [row[:] for row in matrix]
    bad[ports[0]][ports[1]] = 2
    require(not fitting(bad, pairs, nonorthogonal), 'parity-invisible scalar control')
    bad = [row[:] for row in matrix]
    for i in supports[0]:
        for j in supports[0]:
            bad[i][j] -= 1
    require(not fitting(bad, pairs, nonorthogonal), 'missing channel control')
    receipt = {
        'schema_version': 1, 'ports': 112, 'matched_planes': 56,
        'scalar_rank_lower_bound': 48, 'constructed_scalar_rank': 50,
        'field_scope': 'every field; fixed strict scalar plane mask',
        'nonorthogonal_ordered_offdiagonal_entries': sum(nonorthogonal[owner[i]][owner[j]] for i in range(112) for j in range(112) if i != j),
        'plane_clique': certificate['plane_clique'], 'principal_ports': ports,
        'orthogonal_class_sizes': [len(group) for group in certificate['orthogonal_classes']],
        'matrix_sha256': hashlib.sha256(bytes(x for row in matrix for x in row)).hexdigest(),
        'dirty_scalar_vectors': len(vectors), 'rejected_controls': 4,
        'native_copy_cost_claim': None,
    }
    if args.write_receipt:
        args.receipt.write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8', newline='\n')
    else:
        require(json.loads(args.receipt.read_text(encoding='utf-8')) == receipt, 'receipt mismatch')
    print('PASS_PAIRED_PLANE_SCALAR_RANK_FLOOR lower=48 upper=50 dirty=120 controls=4')


if __name__ == '__main__':
    main()
