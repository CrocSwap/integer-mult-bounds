#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact premises for small-block selected-centre information repair.

Ross Richardson, with substantial OpenAI Codex assistance. The predecessor
forward interpreter is explicitly reused; independent.py uses reverse adjoints.
"""
import argparse
from collections import Counter, defaultdict
from fractions import Fraction as Q
import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile
import types

HERE = Path(__file__).resolve().parent
ARCHIVE = 'research/community-frontier1094-audit/selected-replay.tar.gz'
PREDECESSOR = 'research/centre-owner-observation-floor/verify.py'


def need(ok, why):
    if not ok:
        raise ValueError(why)


def canonical(value):
    return (json.dumps(value, sort_keys=True, indent=2) + '\n').encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def load(root):
    manifest = json.loads((HERE / 'SOURCES.json').read_text())
    inputs = {}
    for row in manifest['files']:
        if row['usage'] == 'input':
            raw = (root / row['path']).read_bytes()
            actual = hashlib.sha256(raw).hexdigest()
            need(actual == row['sha256'], 'source pin: ' + row['path'])
            inputs[row['path']] = raw
    # Execute the authenticated source bytes, never a timestamp-selected .pyc.
    source = types.ModuleType('retained_owner_source')
    source.__file__ = str(root / PREDECESSOR)
    exec(compile(inputs[PREDECESSOR], source.__file__, 'exec'), source.__dict__)
    data = {}
    with tarfile.open(fileobj=io.BytesIO(inputs[ARCHIVE])) as archive:
        for key, (name, expected) in source.MEMBERS.items():
            members = [m for m in archive.getmembers() if m.name == name]
            need(len(members) == 1 and members[0].isfile(), 'unique regular source member')
            raw = archive.extractfile(members[0]).read()
            need(hashlib.sha256(raw).hexdigest() == expected, 'archive member pin')
            data[key] = json.loads(gzip.decompress(raw) if name.endswith('.gz') else raw)
    data['prior_receipt'] = json.loads(inputs['research/centre-owner-observation-floor/RESULT.json'])
    return source, data


def column_pair_minors(columns):
    """One nonzero 2x2 minor per unordered pair, over Q (therefore also C)."""
    minors = []
    for p, a in enumerate(columns):
        need(any(a), 'zero column')
        for q in range(p):
            b = columns[q]
            witness = next(((i, j, a[i]*b[j]-a[j]*b[i])
                            for i in range(len(a)) for j in range(i)
                            if a[i]*b[j] != a[j]*b[i]), None)
            need(witness is not None, 'parallel columns')
            i, j, det = witness
            minors.append([q, p, i, j, str(det)])
    return minors


def route_products(source, routes):
    n = len(routes[0])
    identity = tuple(1 << k for k in range(n))
    need(len(set(routes)) == len(routes), 'duplicate route')
    table = defaultdict(list)
    for p, left in enumerate(routes):
        need(tuple(source.act(left, c) for c in left) == identity, 'route not involutory')
        for q, right in enumerate(routes):
            if p != q:
                product = tuple(source.act(left, c) for c in right)
                need(product != identity, 'nontrivial relative route is identity')
                table[product].append([p, q])
    return table


def dependent_triple(columns):
    """A T-kernel with three source owners need not be in the old kernel."""
    for p, a in enumerate(columns):
        for q in range(p):
            b = columns[q]
            i, j = next((i, j) for i in range(8) for j in range(i)
                        if a[i]*b[j] != a[j]*b[i])
            det = a[i]*b[j]-a[j]*b[i]
            for r in range(q):
                c = columns[r]
                u = (c[i]*b[j]-c[j]*b[i])/det
                v = (a[i]*c[j]-a[j]*c[i])/det
                if u and v and all(u*x+v*y == z for x, y, z in zip(a, b, c)):
                    return {'ports': [p, q, r], 'coefficients': [str(u), str(v), '-1']}
    raise ValueError('expected dependent triple not found')


def build(root):
    source, data = load(root)
    forward, end = source.replay(data['programs']['forward'])
    backward, bend = source.replay(data['programs']['backward'])
    # Bind to the complete formal scalar endpoint, including arbitrary ordinary dirt.
    for i in range(704):
        f = {i: Q(1)}
        if 112 <= i < 224:
            f[i-112] = Q(1)
        b = {i: Q(1)}
        if i < 112:
            b[i+112] = Q(-1)
        need(end['L', i] == f and bend['L', i] == b, 'complete scalar endpoint')
    R = [{p: q for p, q in row.items() if p < 112} for row in forward]
    H = []
    for row in backward:
        out = {}
        for i, q in row.items():
            source.add(out, {p: v for p, v in end['L', i].items() if p < 112}, q)
        H.append(out)
    need(H == [{p: q/4 for p, q in row.items()} for row in R], 'H=R/4')
    need(len(source.echelon(R)) == 8, 'old rank is eight')
    calls = sorted(data['template']['calls'], key=lambda c: c['time'])
    need([(calls[t]['time'], calls[t]['stage'], calls[t]['replica'], calls[t]['orientation'])
          for t in (0, 4)] == [(0, 0, 0, 'forward'), (4, 1, 0, 'backward')],
         'selected chronological pair')
    for c in calls[:5]:
        raw = json.dumps(data['programs'][c['orientation']], sort_keys=True, separators=(',', ':')).encode()
        need(c['local_program_sha256'] == hashlib.sha256(raw).hexdigest(), 'call program binding')
        need(len(c['owners']) == len({o[0] for o in c['owners']}) == 704, 'injective ordinary owners')
    for t, stage in ((0, 0), (4, 1)):
        need(calls[t]['owners'][:224] == [[p, [1, stage, p % 112]] for p in range(224)],
             'source owner boundary')
    need(all(not set(range(224)) & {o[0] for o in c['owners']} for c in calls[1:4]),
         'intervening source-data contact')
    need([e['kind'] for e in data['template']['execution_schedule'][:5]] == ['local_cover_sweep']*5,
         'intervening schedule event')
    dense = [[str(row.get(p, 0)) for p in range(112)] for row in R]
    prior = data['prior_receipt']
    need(dense == prior['R'], 'retained R coefficient comparison')
    need([[str(row.get(p, 0)) for p in range(112)] for row in H] == prior['H'], 'retained H coefficient comparison')
    columns = [tuple(row.get(p, Q(0)) for row in R) for p in range(112)]
    minors = column_pair_minors(columns)
    routes = [source.route(record) for record in data['phases']['recipes']]
    need(len(routes) == 112, 'route count')
    need([r['q'] for r in data['phases']['recipes']] == data['word']['ports'], 'route port order')
    table = route_products(source, routes)
    histogram = Counter(map(len, table.values()))
    need(histogram == {1: 12432}, 'ordered relative route multiplicities')
    pivots = sorted(source.echelon(R))
    complement = [p for p in range(112) if p not in pivots]
    need(len(complement) == 104, 'sharp repair dimension')
    need(len(source.echelon(R + [{p: Q(1)} for p in complement])) == 112, 'repair attainment')
    need(len(source.echelon(R + [{p: Q(1)} for p in complement[:-1]])) == 111, '103-read defect control')

    # Mathematical controls exercise load-bearing hypotheses.
    mutant = list(columns)
    mutant[1] = mutant[0]
    try:
        column_pair_minors(mutant)
    except ValueError as e:
        need(str(e) == 'parallel columns', 'wrong parallel-column rejection')
    else:
        raise ValueError('parallel columns accepted')
    try:
        route_products(source, [routes[0], routes[0]])
    except ValueError as e:
        need(str(e) == 'duplicate route', 'wrong duplicate-route rejection')
    else:
        raise ValueError('duplicate route accepted')
    # If every route collapses to I, T is ownerwise R/4: no repair is needed.
    need(len(source.echelon(R + H)) == 8, 'collapsed-route zero-repair control')
    # On C2 with two parallel columns R=(1,1), x=(1,-1) at both owners
    # lies in both S and T kernels for routes identity and swap.
    xs = ((Q(1), Q(-1)), (Q(1), Q(-1)))
    need(all(sum(x) == 0 for x in xs), 'parallel-column local-kernel control')
    need(all(xs[g][0] + xs[1-g][1] == 0 for g in range(2)), 'parallel-column routed-kernel control')
    triple = dependent_triple(columns)
    ps, coeffs = triple['ports'], list(map(Q, triple['coefficients']))
    need(all(sum(c*columns[p][i] for p, c in zip(ps, coeffs)) == 0 for i in range(8)), 'triple T-kernel')
    need(all(c and any(columns[p]) for p, c in zip(ps, coeffs)), 'triple is not in S-kernel')
    controls = ['parallel_column_rejected', 'duplicate_route_rejected',
                'collapsed_routes_need_no_repair', 'parallel_column_C2_two_owner_counterexample',
                'three_owner_T_kernel_fails_old_kernel', '103_coordinate_repair_loses_dimension']
    return {
        'status': 'PASS_CENTRE_BLOCK_REPAIR_INFORMATION',
        'source_base': 'd8e0f83f00191df62174b641e9fff055c357f641',
        'model': 'PR1094 calls0/4; independent scalar source values by regular cover owner; equal ordinary dirt',
        'old_rank': 8, 'ports': 112, 'nonparallel_column_pairs': len(minors),
        'column_pair_minor_sha256': digest(minors), 'R_sha256': digest(dense),
        'route_count': 112, 'route_dimension': 73, 'ordered_nonidentity_route_products': 12432,
        'distinct_nonidentity_route_products': len(table),
        'relative_route_multiplicity_histogram': {str(k): v for k, v in sorted(histogram.items())},
        'ordered_route_product_sha256': digest([[p, q, list(product)] for product, pairs in table.items() for p, q in pairs]),
        'source_minimum_active_ports_lower_bound': 3, 'output_minimum_active_owners_lower_bound': 3,
        'kernel_nonzero_owner_support_lower_bound': 7,
        'all_blocks_proved': {'minimum_size': 1, 'maximum_size': 6,
                              'extra_scalar_linear_observations_exact': '104*block_size'},
        'repair_pivot_columns': pivots, 'repair_coordinate_reads': complement,
        'T_kernel_without_old_kernel_control': triple, 'controls': controls,
        'scope': 'finite exhaustive premises plus written all-block theorem; no kernel proof, native tariff, supplier admission or new kappa',
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source-root', type=Path, default=HERE.parents[1])
    p.add_argument('--write', type=Path)
    p.add_argument('--receipt', type=Path, default=HERE / 'RESULT.json')
    args = p.parse_args()
    result = build(args.source_root.resolve())
    if args.write:
        with args.write.open('xb') as stream:
            stream.write(canonical(result))
    else:
        need(canonical(result) == canonical(json.loads(args.receipt.read_text())), 'receipt mismatch')
    print('PASS_CENTRE_BLOCK_REPAIR_INFORMATION blocks=1..6 repair=104*b products=12432 controls=6 no_new_kappa')


if __name__ == '__main__':
    main()
