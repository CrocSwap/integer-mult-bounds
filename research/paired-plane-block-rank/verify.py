"""Check fixed-mask premises, sharp block attainers and effective controls."""
from pathlib import Path
import argparse
import copy
import hashlib
import json
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import model as m
import independent as oracle


def encoded(value):
    return json.dumps(value, indent=2, sort_keys=True) + '\n'


def reject(action, reason):
    try:
        action()
    except ValueError as error:
        m.need(str(error) == reason, 'unexpected rejection: ' + str(error))
        return reason
    raise ValueError('ineffective negative control ' + reason)


def result():
    data, matching, certificate = m.sources()
    labels, pairs, owner, orthogonal, allowed = m.geometry(data, matching)
    m.need(oracle.mask(labels, pairs) == allowed, 'independent all-span mask')
    m.premises(certificate, orthogonal)
    groups = m.supports(certificate, allowed)
    ranks = {}
    # The all-size/all-field lower bound is the written subspace proof.
    # Finite elimination corroborates attainers, not a search lower bound.
    for d in (1, 2, 3):
        matrix = m.tensor_fit(groups, d)
        m.fit(matrix, d, allowed)
        oracle.block_mask(matrix, d, allowed)
        ranks[str(d)] = {str(p): oracle.rank(matrix, p) for p in (2, 3, 101)}
        m.need(set(ranks[str(d)].values()) == {49*d}, 'tensor attainer ranks')
        representatives = [d*s[0]+a for s in groups for a in range(d)]
        m.need([[matrix[i][j] for j in representatives] for i in representatives] == m.identity(49*d), 'identity minor all-field certificate')
    nc, triple, charts = m.noncommuting_fit(groups)
    m.fit(nc, 2, allowed)
    oracle.block_mask(nc, 2, allowed)
    a, b, c = triple
    x = [row[2*b:2*b+2] for row in nc[2*a:2*a+2]]
    y = [row[2*c:2*c+2] for row in nc[2*a:2*a+2]]
    m.need(m.multiply(x, y) != m.multiply(y, x), 'genuinely noncommuting allowed blocks')
    nc_ranks = {str(p): oracle.rank(nc, p) for p in (2, 3, 101)}
    m.need(set(nc_ranks.values()) == {98}, 'noncommuting rank98')
    for source in range(224):
        values = [[int(source == 2*i), int(source == 2*i+1)] for i in range(112)]
        m.need(oracle.direct_query_action(groups, charts, values) == [r[source] for r in nc], '224 independent query-action columns')
    cycle_allowed = [[(i-j) % 5 in (1, 4) for j in range(5)] for i in range(5)]
    cycle_ranks = {}
    for size in range(1, 9):
        cycle, supports = m.cycle_fit(size)
        m.fit(cycle, size, cycle_allowed)
        oracle.block_mask(cycle, size, cycle_allowed)
        rr = {str(p): oracle.rank(cycle, p) for p in (2, 3, 101)}
        m.need(set(rr.values()) == {(5*size+1)//2}, 'sharp cycle block rank')
        cycle_ranks[str(size)] = rr
    # Scalar C5 rank3, while two-dimensional rank5<6: tensorizing a scalar
    # lower bound alone is invalid, motivating the all-size proof.
    m.need(cycle_ranks['1']['2'] == 3 and cycle_ranks['2']['2'] == 5, 'strict scalar/vector countercontrol')
    controls = {}
    bad = copy.deepcopy(certificate); bad['clique22'].remove(20); bad['clique22'].append(22)
    controls['cross_zero_premise'] = reject(lambda: m.premises(bad, orthogonal), 'clique-core forced zero')
    bad = copy.deepcopy(certificate); bad['c5_core'][1], bad['c5_core'][2] = bad['c5_core'][2], bad['c5_core'][1]
    controls['cycle_order'] = reject(lambda: m.premises(bad, orthogonal), 'induced orthogonality cycle')
    # Ordered nonsymmetric illegal block invisible to trace and the constant vector.
    i, j = pairs[0]
    bad = copy.deepcopy(nc)
    fault = [[1, -1], [1, -1]]
    m.need(sum(fault[k][k] for k in range(2)) == 0 and all(sum(row) == 0 for row in fault), 'weak scalar projections miss fault')
    for a in range(2):
        for b in range(2): bad[2*i+a][2*j+b] = fault[a][b]
    controls['trace_and_constant_invisible'] = reject(lambda: m.fit(bad, 2, allowed), 'ordered block mask')
    controls['independent_hidden_fault'] = reject(lambda: oracle.block_mask(bad, 2, allowed), 'independent basis endpoint')
    m.need(all(bad[2*j+a][2*i+b] == 0 for a in range(2) for b in range(2)), 'fault changed only one direction')
    controls['transposed_hidden_fault'] = reject(lambda: m.fit(list(map(list, zip(*bad))), 2, allowed), 'ordered block mask')
    bad = copy.deepcopy(nc); bad[0][0] = 0
    controls['diagonal_normalization'] = reject(lambda: m.fit(bad, 2, allowed), 'ordered block mask')
    return {'status': 'PASS_PAIRED_PLANE_BLOCK_RANK', 'ports': 112, 'planes': 56,
            'ordered_forbidden_pairs': sum(not allowed[i][j] for i in range(112) for j in range(112) if i != j),
            'core': certificate['c5_core'], 'clique22': certificate['clique22'],
            'theorem': 'minimum rank is 49*d for every field and every positive integer d; arbitrary nonsymmetric noncommuting d-by-d free blocks',
            'proof': 'I_(44d) direct sum C5 block core; C5 rank >= ceil(5L/2), L=2d',
            'tensor_attainer_ranks': ranks, 'noncommuting_ranks': nc_ranks, 'noncommuting_triple': triple,
            'noncommuting_matrix_sha256': hashlib.sha256(encoded(nc).encode()).hexdigest(),
            'direct_query_basis_columns': 224, 'cycle_attainer_ranks': cycle_ranks,
            'scalar_tensorization_countercontrol': 'C5 scalar minimum3 but block2 minimum5<6',
            'rejected_controls': controls,
            'limits': 'Fixed matching and zero mask only; no native COPY price, physically legal chart circuit, altered endpoint contract, supplier or kappa.'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', type=Path)
    args = parser.parse_args()
    if args.write and args.write.exists(): raise FileExistsError(args.write)
    receipt = result()
    if args.write:
        with args.write.open('x', encoding='utf-8', newline='\n') as handle: handle.write(encoded(receipt))
    else:
        m.need(encoded(json.loads((m.HERE/'RESULT.json').read_text())) == encoded(receipt), 'complete typed receipt mismatch')
    print('PASS_PAIRED_PLANE_BLOCK_RANK normalized=49 noncommuting_rank=98 query_columns=224 controls=6')


if __name__ == '__main__': main()
