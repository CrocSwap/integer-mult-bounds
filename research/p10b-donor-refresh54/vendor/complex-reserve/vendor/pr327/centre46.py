"""centre46.py: the centre-sharing variant of PR #144's Graph.finish used for PR #315's complex program (the research
copy, unchanged): the pair module supplies the star centre as an extra root (sum of all its inputs) instead of
Graph.sum over the A's. load_pmod46(path, n) checks the contract (C(n,2) roots + one full-sum root).
Prepared by DreamingOfClouds with Anthropic Claude assistance; Apache-2.0. Graph.finish is icekylinx's (PR #144)."""
import json
from pathlib import Path
from itertools import combinations


# ---- centre-sharing variant (agent-cmod): the pair module supplies the star centre as a 46th root -------------
def load_pmod46(path, n=10):
    """Pair module JSON with 45 contract roots plus a 46th root = sum of all 45 inputs (checked)."""
    from itertools import combinations as _c
    d = json.loads(Path(path).read_text())
    pairs = list(_c(range(n), 2))
    assert d['input_count'] == len(pairs) and len(d['roots']) == len(pairs) + 1
    support = []
    for x, a in enumerate(d['args']):
        if x < len(pairs):
            assert a is None; support.append(1 << x)
        else:
            assert a is not None and 0 <= a[0] < x and 0 <= a[1] < x and not support[a[0]] & support[a[1]]
            support.append(support[a[0]] | support[a[1]])
    for (i, j), r in zip(pairs, d['roots']):
        assert support[r] == sum(1 << k for k, (a, b) in enumerate(pairs) if i not in (a, b) and j not in (a, b))
    assert support[d['roots'][-1]] == (1 << len(pairs)) - 1
    return dict(kind='pair_disjoint_centre', n=n, input_count=len(pairs), input_labels=pairs, output_labels=pairs,
                args=[None if a is None else list(a) for a in d['args']], roots=list(d['roots']))


def finish_centre46(G, triple, pair46, allbut):
    """Graph.finish (star centre) with centre[2i+e] = the pair module (i, e)'s 46th root instead of G.sum(...)."""
    from itertools import product as _prod
    from fractions import Fraction
    G.local_channels()
    base_nodes = len(G.a)
    D = dict(zip(G.cubes, G.module(triple, [G.F[I] for I in G.cubes])))
    P, Q, CEN = {}, {}, {}
    for i in range(G.p):
        others = [a for a in range(G.p) if a != i]
        pairs = list(combinations(others, 2))
        for bit in range(2):
            inputs = [G.A[tuple(sorted((i, *K))), i, bit] for K in pairs]
            outs = G.module(pair46, inputs)
            for K, node in zip(pairs, outs[:len(pairs)]):
                P[tuple(sorted((i, *K))), i, bit] = node
            CEN[i, bit] = outs[len(pairs)]
    for i, j in combinations(range(G.p), 2):
        others = [a for a in range(G.p) if a not in (i, j)]
        for mode in range(2):
            inputs = [G.G[tuple(sorted((i, j, k))), i, j, mode] for k in others]
            for k, node in zip(others, G.module(allbut, inputs)):
                Q[tuple(sorted((i, j, k))), i, j, mode] = node
    query_nodes = len(G.a)
    def emit(I, bits_list, node, numerator=1, channel=''):
        G.root.append(dict(node=node, targets=[G.source[I, b] for b in bits_list],
                           coefficients=[f'{numerator}/2'] * len(bits_list), kind='side', channel=channel))
    for I in G.cubes:
        all_bits = list(_prod(range(2), repeat=3))
        emit(I, all_bits, D[I], channel='disjoint')
        for a in range(2):
            emit(I, [b for b in all_bits if b[0] == a], P[I, I[0], 1 - a], channel='face0')
        for a, b in _prod(range(2), repeat=2):
            emit(I, [(a, b, c) for c in range(2)], P[I, I[1], 1 - b], channel='face1')
        for a, b in _prod(range(2), repeat=2):
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
                status='agent-cmod centre-sharing variant')


