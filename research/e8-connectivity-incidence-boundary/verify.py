#!/usr/bin/env python3
"""Exact finite E8 connectivity/rank boundary; stdlib only, no source imports.

Aaron Wang / navinor, with help from chatgpt. Apache-2.0.
Definitions and fixture credit: https://github.com/CrocSwap/integer-mult-bounds/pull/1560
Question credit: https://github.com/CrocSwap/integer-mult-bounds/pull/1616
"""
import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
PRIME = 1000003


def require(ok, message):
    if not ok:
        raise ValueError(message)


def digest(value):
    raw = json.dumps(value, separators=(',', ':')).encode('ascii')
    return hashlib.sha256(raw).hexdigest()


def root_model():
    # Enumerate norm-eight doubled roots, then quotient by the sign of the line.
    integer = [v for v in itertools.product((-2, 0, 2), repeat=8)
               if sum(t*t for t in v) == 8]
    half = [v for v in itertools.product((-1, 1), repeat=8)
            if math.prod(v) == 1]
    roots = sorted(v for v in integer + half if next(t for t in v if t) > 0)
    require(len(roots) == len(set(roots)) == 120, 'root count')
    dots = [[sum(x*y for x, y in zip(a, b)) for b in roots] for a in roots]
    require(all(t % 4 == 0 for row in dots for t in row), 'Gram integrality')
    return roots, [[t//4 for t in row] for row in dots]


def frames_in(gram, live):
    frames = []

    def extend(prefix, candidates):
        if len(prefix) == 8:
            frames.append(prefix)
            return
        if len(prefix) + len(candidates) < 8:
            return
        for pos, i in enumerate(candidates):
            extend(prefix + [i], [j for j in candidates[pos+1:] if gram[i][j] == 0])

    extend([], sorted(live))
    return frames


def rank_mod(rows):
    """Modular nonzero minors certify lower bounds on rational rank only."""
    basis = {}
    for row in rows:
        v = [x % PRIME for x in row]
        for col, b in sorted(basis.items()):
            if v[col]:
                a = v[col]
                v = [(x-a*y) % PRIME for x, y in zip(v, b)]
        col = next((c for c, x in enumerate(v) if x), None)
        if col is not None:
            scale = pow(v[col], -1, PRIME)
            basis[col] = [x*scale % PRIME for x in v]
    return len(basis)


def graph_checks(gram, pivot, supports, frames):
    results = []
    for k, ell in itertools.combinations(pivot, 2):
        vertices = sorted(set(supports[k]) & set(supports[ell]))
        require(vertices, 'empty pair graph')
        vertex_set = set(vertices)
        edges = set()
        for frame in frames:
            hit = sorted(vertex_set.intersection(frame))
            if len(hit) == 2:
                i, j = hit
                require(gram[i][k]*gram[i][ell] + gram[j][k]*gram[j][ell] == 0,
                        'edge sign identity')
                edges.add((i, j))
        adjacency = {i: set() for i in vertices}
        for i, j in edges:
            adjacency[i].add(j)
            adjacency[j].add(i)
        reached = {vertices[0]}
        todo = [vertices[0]]
        while todo:
            for i in adjacency[todo.pop()] - reached:
                reached.add(i)
                todo.append(i)
        require(len(reached) == len(vertices), f'disconnected graph {k},{ell}')
        results.append({'pair': [k, ell], 'vertices': len(vertices), 'edges': len(edges),
                        'edges_sha256': digest(sorted(edges))})
    return results


def evaluate(data):
    require(all(PRIME % d for d in range(2, math.isqrt(PRIME)+1)), 'modulus not prime')
    roots, gram = root_model()
    all_frames = frames_in(gram, range(120))
    require(len(all_frames) == 2025, 'full frame count')
    frame0, pivot = data['frame0'], data['pivot']
    require(frame0 in all_frames and pivot in all_frames, 'not a genuine frame')
    deleted = data['deleted_lines']
    require(len(deleted) == len(set(deleted)) == 5 and set(deleted) <= set(range(120)),
            'invalid deletion')
    require(not set(deleted) & set(frame0), 'deletion already punctured')
    live = set(range(120)) - set(frame0) - set(deleted)
    require(set(pivot) <= live and len(live) == 107, 'deleted pivot')
    live_frames = [f for f in all_frames if set(f) <= live]
    supports = {k: [i for i in sorted(live-set(pivot)) if gram[i][k]] for k in pivot}
    k = data['coordinate']
    require(k in pivot, 'coordinate outside pivot')
    negatives = data['negative_lines']
    require(len(negatives) == len(set(negatives)) and set(negatives) <= set(supports[k]),
            'unknown/duplicate negative line')
    q = {i: -1 if i in negatives else 1 for i in supports[k]}
    selected = [f for f in live_frames if sum(q.get(i, 0) for i in f) == 0]
    require(pivot in selected, 'pivot not selected')
    graphs = graph_checks(gram, pivot, supports, selected)
    graph_checks(gram, pivot, supports, live_frames)  # full-family positive control
    ranks = []
    for kk in pivot:
        columns = supports[kk]
        kernels = [[gram[i][kk]*gram[i][ell] for i in columns]
                   for ell in pivot if ell != kk]
        require(rank_mod(kernels) == 7, 'canonical kernel independence')
        # Direct integer products give an upper bound valid over Q and any
        # characteristic-zero field. The modular rank supplies the lower bound.
        matrices = [[[int(i in f) for i in columns] for f in fs]
                    for fs in (selected, live_frames)]
        for matrix in matrices:
            require(all(sum(a*b for a, b in zip(row, h)) == 0
                        for row in matrix for h in kernels), 'canonical vector not in kernel')
        extra = [q[i] for i in columns] if kk == k else None
        if extra is not None:
            require(rank_mod(kernels + [extra]) == 8, 'extra vector in canonical span')
            require(all(sum(a*b for a, b in zip(row, extra)) == 0 for row in matrices[0]),
                    'extra vector not in selected kernel')
            require(any(sum(a*b for a, b in zip(row, extra)) != 0 for row in matrices[1]),
                    'full-family control failed to remove extra vector')
        selected_rank, full_rank = map(rank_mod, matrices)
        require(selected_rank == len(columns) - (8 if kk == k else 7),
                'selected lower/upper rank bounds do not meet')
        require(full_rank == len(columns)-7, 'complete-family (D) positive control')
        ranks.append({'coordinate': kk, 'columns': len(columns), 'selected_rank': selected_rank,
                      'full_rank': full_rank, 'required_D_rank': len(columns)-7})
    # Local failure control: a real pivot alone must not pass connectivity.
    try:
        graph_checks(gram, pivot, supports, [pivot])
    except ValueError:
        pass
    else:
        raise ValueError('pivot-only disconnected control accepted')
    violating = next(f for f in live_frames if sum(q.get(i, 0) for i in f))
    repaired = selected + [violating]
    repair_ranks = [rank_mod([[int(i in f) for i in supports[kk]] for f in repaired])
                    for kk in pivot]
    require(repair_ranks == [len(supports[kk])-7 for kk in pivot],
            'one-frame repair does not saturate all diagonal ranks')
    return {'root_order_sha256': digest(roots), 'all_frames': len(all_frames),
            'live_frames': len(live_frames), 'selected_frames': len(selected),
            'selected_frames_sha256': digest(selected), 'graphs': graphs, 'ranks': ranks,
            'full_family_q_obstruction': {'frame': violating,
                'sum': sum(q.get(i, 0) for i in violating)},
            'one_frame_repair_ranks': repair_ranks,
            'scope': 'selected subfamily only; all-live-frame implication remains open'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--certificate', type=Path, default=HERE / 'CERTIFICATE.json')
    parser.add_argument('--write', action='store_true', help='regenerate deterministic result after checks')
    args = parser.parse_args()
    data = json.loads(args.certificate.read_text(encoding='utf-8'))
    result = evaluate(data)
    if args.write:
        data['result'] = result
        args.certificate.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
    else:
        require(result == data['result'], 'certificate result mismatch')
    row = next(r for r in result['ranks'] if r['coordinate'] == data['coordinate'])
    print('PASS_E8_CONNECTIVITY_INCIDENCE_BOUNDARY '
          f"live={result['live_frames']} selected={result['selected_frames']} "
          f"graphs={len(result['graphs'])} rank={row['selected_rank']} "
          f"required={row['required_D_rank']} canonical_kernel=7 extra_kernel=1 "
          'full_family_control=PASS one_frame_repair=PASS')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, TypeError) as error:
        raise SystemExit('FAIL_E8_CONNECTIVITY_INCIDENCE_BOUNDARY: ' + str(error))
