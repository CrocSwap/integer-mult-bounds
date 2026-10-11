"""spec_graph.py: the per-invocation module spec of the p = 10 complex word, and the centre-sharing graph it builds.

A spec names the triple module (tmod), a default pair module with the star centre as its last root (pmod, 37 roots
at p = 10; centre46.load_pmod46) and a default all-but-one module (qmod), and may override them per invocation:
  pmods {"i,bit": path}        the pair module of invocation (i, bit), i < p, bit in {0, 1}   (2p invocations)
  qmods {"i,j,mode": path}     the all-but-one module of invocation (i, j, mode), i < j < p   (p(p-1) invocations)
expand() resolves the spec into one module file per invocation. finish_spec() is centre46.finish_centre46 with
the module of each invocation looked up in those tables (same node order, same roots, same centres); with one
module per kind it builds finish_centre46's graph, which verify.py checks field by field (anchor (e)) and through
the written word files (anchor (f)); the status string is finish_centre46's.
Cube orientation is the sorted one throughout (position k of cube {a < b < c} is its k-th element).
Prepared by Chafik Boukhalfa with substantial Anthropic Claude assistance; Apache-2.0. finish_centre46 is
DreamingOfClouds' (PR #327, from PR #315), Graph.finish is icekylinx's (PR #144)."""
from itertools import combinations, product
from pathlib import Path


def expand(spec, base):
    """{('p', i, bit): Path, ('q', i, j, mode): Path} for every invocation of the p-cube word"""
    P = spec['p']
    base = Path(base)
    out = {}
    extra = set(spec.get('pmods', {})) - {'%d,%d' % (i, b) for i in range(P) for b in range(2)}
    extra |= set(spec.get('qmods', {})) - {'%d,%d,%d' % (i, j, m) for i, j in combinations(range(P), 2) for m in range(2)}
    assert not extra, 'spec names invocations that do not exist: %s' % sorted(extra)
    for i in range(P):
        for b in range(2):
            out['p', i, b] = base / spec.get('pmods', {}).get('%d,%d' % (i, b), spec['pmod'])
    for i, j in combinations(range(P), 2):
        for m in range(2):
            out['q', i, j, m] = base / spec.get('qmods', {}).get('%d,%d,%d' % (i, j, m), spec['qmod'])
    return out


def shared(table):
    """the single module file per kind if every invocation of that kind uses the same file, else None"""
    res = {}
    for kind in ('p', 'q'):
        files = {f for k, f in table.items() if k[0] == kind}
        res[kind] = files.pop() if len(files) == 1 else None
    return res


def finish_spec(G, triple, pmod_of, qmod_of):
    """finish_centre46 with per-invocation modules: pmod_of(i, bit) a load_pmod46 module, qmod_of(i, j, mode) an
    all_but_one_from module"""
    G.local_channels()
    base_nodes = len(G.a)
    D = dict(zip(G.cubes, G.module(triple, [G.F[I] for I in G.cubes])))
    P, Q, CEN = {}, {}, {}
    for i in range(G.p):
        others = [a for a in range(G.p) if a != i]
        pairs = list(combinations(others, 2))
        for bit in range(2):
            inputs = [G.A[tuple(sorted((i, *K))), i, bit] for K in pairs]
            outs = G.module(pmod_of(i, bit), inputs)
            for K, node in zip(pairs, outs[:len(pairs)]):
                P[tuple(sorted((i, *K))), i, bit] = node
            CEN[i, bit] = outs[len(pairs)]
    for i, j in combinations(range(G.p), 2):
        others = [a for a in range(G.p) if a not in (i, j)]
        for mode in range(2):
            inputs = [G.G[tuple(sorted((i, j, k))), i, j, mode] for k in others]
            for k, node in zip(others, G.module(qmod_of(i, j, mode), inputs)):
                Q[tuple(sorted((i, j, k))), i, j, mode] = node
    query_nodes = len(G.a)

    def emit(I, bits_list, node, numerator=1, channel=''):
        G.root.append(dict(node=node, targets=[G.source[I, b] for b in bits_list],
                           coefficients=[f'{numerator}/2'] * len(bits_list), kind='side', channel=channel))
    for I in G.cubes:
        all_bits = list(product(range(2), repeat=3))
        emit(I, all_bits, D[I], channel='disjoint')
        for a in range(2):
            emit(I, [b for b in all_bits if b[0] == a], P[I, I[0], 1 - a], channel='face0')
        for a, b in product(range(2), repeat=2):
            emit(I, [(a, b, c) for c in range(2)], P[I, I[1], 1 - b], channel='face1')
        for a, b in product(range(2), repeat=2):
            emit(I, [(a, b, c) for c in range(2)], Q[I, I[0], I[1], a ^ b], 2 * a - 1, 'edge01')
        for bits in all_bits:
            emit(I, [bits], P[I, I[2], 1 - bits[2]], channel='face2')
        for ii, jj in [(0, 2), (1, 2)]:
            for bits in all_bits:
                emit(I, [bits], Q[I, I[ii], I[jj], bits[ii] ^ bits[jj]], 2 * bits[ii] - 1, f'edge{ii}{jj}')
    for i in range(G.p):
        for e in range(2):
            G.centers.append(CEN[i, e])
    for coordinate, node in enumerate(G.centers):
        coefficients = ['1/3' if coordinate in t else '-1/6' for t in G.labels]
        G.root.append(dict(node=node, targets=list(range(len(G.labels))), coefficients=coefficients, kind='center',
                           coordinate=coordinate))
    return dict(p=G.p, h=G.h, v=len(G.labels), labels=G.labels, inputs=[sum(1 << x for x in t) for t in G.labels],
                args=G.a, signs=G.signs, roots=G.root, centers=G.centers, center_kind='star',
                center_scatter='1/2 sum_(i in T) S_i - 1/6 sum_i S_i',
                local_K='Two 4x4 Hadamard/2 blocks on opposite cube parities, using original X destructively',
                source_data_histogram={2: len(G.labels), G.h - 4: len(G.labels), 1: len(G.labels)},
                target_data_histogram={G.h - 4: len(G.labels), 1: 3 * len(G.labels)},
                counts=dict(local_channel_additions=base_nodes - len(G.labels), query_additions=query_nodes - base_nodes,
                            center_additions=0, center_tree_incidences=0,
                            signed_additions=sum(x < 0 for x in G.signs),
                            side_root_uses=sum(r['kind'] == 'side' for r in G.root), center_roots=len(G.centers)),
                status='agent-cmod centre-sharing variant')   # finish_centre46's status, so that both write the same graph.json

