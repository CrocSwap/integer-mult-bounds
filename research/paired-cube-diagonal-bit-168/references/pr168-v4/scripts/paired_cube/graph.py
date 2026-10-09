#!/usr/bin/env python3
# Copyright 2026 icekylinx. Apache-2.0.
# Developed with GPT-6 Astra assistance; integrated with Codex assistance.
"""Construct the actual signed H=block(B)-B producer on paired triple cubes.

The coarse positive query modules restrict the already adopted PR117 DAG
(eumemic; Apache-2.0; Claude assistance; cbb05ce504d571546d9b7794c186a613c659c3bf).
The paired-channel decomposition and this assembly are new work for icekylinx
with OpenAI GPT-6 Astra assistance. This file constructs a circuit; it performs no audit.
"""
from itertools import combinations, product



class Graph:
    def __init__(self, p, local=None):
        self.p = p
        self.local = local
        self.h = 2*p
        self.cubes = list(combinations(range(p), 3))
        self.labels = [tuple(2*i+b for i, b in zip(I, bits))
                       for I in self.cubes for bits in product(range(2), repeat=3)]
        self.a = [None] * len(self.labels)
        self.signs = [1] * len(self.labels)
        self.s = [1 << i for i in range(len(self.labels))]
        self.intern = {}
        self.source = {(I, bits): 8*j+k for j, I in enumerate(self.cubes)
                       for k, bits in enumerate(product(range(2), repeat=3))}
        self.F, self.A, self.G = {}, {}, {}
        self.root = []
        self.centers = []

    def add(self, a, b, sign=1):
        if a is None:
            assert sign == 1
            return b
        if b is None:
            return a
        if sign == 1 and a > b:
            a, b = b, a
        key = a, b, sign
        if key not in self.intern:
            # Every channel sum combines disjoint original-source supports.
            assert not self.s[a] & self.s[b], (a, b, sign)
            self.intern[key] = len(self.a)
            self.a.append([a, b])
            self.signs.append(sign)
            self.s.append(self.s[a] | self.s[b])
        return self.intern[key]

    def sum(self, xs):
        xs = list(xs)
        if not xs:
            return None
        while len(xs) > 1:
            xs = [self.add(xs[i], xs[i+1]) if i+1 < len(xs) else xs[i]
                  for i in range(0, len(xs), 2)]
        return xs[0]

    def module(self, data, inputs):
        # Modules use either zero-based or one-based node indices.
        args = data['args']
        n = data.get('input_count', len(inputs))
        one_based = args[0] == [0, 0] and len(args) > n and args[n] == [0, 0]
        image = ([None] if one_based else []) + list(inputs)
        start = n+1 if one_based else n
        for pair in args[start:]:
            a, b = pair
            image.append(self.add(image[a], image[b]))
        return [image[x] for x in data['roots']]

    def local_channels(self):
        if self.local is not None:
            return self.configured_local_channels(self.local)
        for I in self.cubes:
            edges = {}
            for ii, jj in combinations(range(3), 2):
                kk = 3-ii-jj
                for a, b in product(range(2), repeat=2):
                    bits0 = [0]*3
                    bits0[ii], bits0[jj] = a, b
                    bits1 = bits0[:]
                    bits1[kk] = 1
                    edges[ii, jj, a, b] = self.add(
                        self.source[I, tuple(bits0)], self.source[I, tuple(bits1)])
                self.G[I, I[ii], I[jj], 0] = self.add(
                    edges[ii, jj, 0, 0], edges[ii, jj, 1, 1], -1)
                self.G[I, I[ii], I[jj], 1] = self.add(
                    edges[ii, jj, 0, 1], edges[ii, jj, 1, 0], -1)
            for ii in range(3):
                jj = next(j for j in range(3) if j != ii)
                for a in range(2):
                    ids = []
                    for b in range(2):
                        key = (ii, jj, a, b) if ii < jj else (jj, ii, b, a)
                        ids.append(edges[key])
                    self.A[I, I[ii], a] = self.add(*ids)
            self.F[I] = self.add(self.A[I, I[0], 0], self.A[I, I[0], 1])

    def configured_local_channels(self, cfg):
        """The same 13 outputs per cube (positions 0,1,2 of I) by a configured circuit:
        A[i,a] = sum of the ports with bit i = a; 'e<d>': two edges along direction d, 'fd': two face diagonals.
        G[j,k,m] = [bits (j,k) = (0,m)] - [bits (j,k) = (1,1-m)], [.] summing the third bit r; 'e': edges along r,
        'l': long-diagonal differences, 's': differences at fixed r.  F = A[f,0] + A[f,1].
        Signed pairs take the smaller port as minuend so equal differences are shared."""
        A_cfg = {tuple(int(c) for c in k.split(',')): v for k, v in cfg['A'].items()}
        G_cfg = {tuple(int(c) for c in k.split(',')): v for k, v in cfg['G'].items()}

        def signed(xa, xb):
            return (self.add(xa, xb, -1), 1) if xa < xb else (self.add(xb, xa, -1), -1)

        def combine(t1, t2):
            (n1, s1), (n2, s2) = t1, t2
            if s1 == 1:
                return self.add(n1, n2, s2)
            assert s2 == 1, 'negated local output'
            return self.add(n2, n1, -1)
        for I in self.cubes:
            def at(values):
                bits = [0]*3
                for q, b in values.items():
                    bits[q] = b
                return self.source[I, tuple(bits)]

            def edge(d, fixed):
                return self.add(at({**fixed, d: 0}), at({**fixed, d: 1}))
            for j, k in combinations(range(3), 2):
                r = 3-j-k
                for mode in range(2):
                    u, v = 0, mode
                    kind = G_cfg[j, k, mode]
                    if kind == 'e':
                        node = self.add(edge(r, {j: u, k: v}), edge(r, {j: 1-u, k: 1-v}), -1)
                    else:
                        assert kind in ('l', 's')
                        far = (1, 0) if kind == 'l' else (0, 1)
                        node = combine(signed(at({j: u, k: v, r: 0}), at({j: 1-u, k: 1-v, r: far[0]})),
                                       signed(at({j: u, k: v, r: 1}), at({j: 1-u, k: 1-v, r: far[1]})))
                    self.G[I, I[j], I[k], mode] = node
            for i in range(3):
                j, k = [q for q in range(3) if q != i]
                for a in range(2):
                    kind = A_cfg[i, a]
                    if kind == 'fd':
                        n1 = self.add(at({i: a, j: 0, k: 0}), at({i: a, j: 1, k: 1}))
                        n2 = self.add(at({i: a, j: 0, k: 1}), at({i: a, j: 1, k: 0}))
                    else:
                        d = int(kind[1])
                        assert kind[0] == 'e' and d != i
                        o = j if d == k else k
                        n1, n2 = edge(d, {i: a, o: 0}), edge(d, {i: a, o: 1})
                    self.A[I, I[i], a] = self.add(n1, n2)
            f = cfg['F']
            self.F[I] = self.add(self.A[I, I[f], 0], self.A[I, I[f], 1])

    def center_channels(self):
        # Route each cube total to maximal binary-tree intervals avoiding I.
        nodes = []
        def tree(lo, hi, parent):
            x = len(nodes)
            nodes.append(dict(lo=lo, hi=hi, parent=parent, children=[], inputs=[]))
            if hi-lo > 1:
                mid = (lo+hi)//2
                nodes[x]['children'] = [tree(lo, mid, x), tree(mid, hi, x)]
            return x
        tree(0, self.p, None)
        for I in self.cubes:
            stack = [0]
            while stack:
                x = stack.pop()
                node = nodes[x]
                if all(not node['lo'] <= i < node['hi'] for i in I):
                    node['inputs'].append(self.F[I])
                else:
                    stack.extend(node['children'])
        total = [None]*len(nodes)
        Z = {}
        for x, node in enumerate(nodes):
            inherited = None if node['parent'] is None else total[node['parent']]
            total[x] = self.add(inherited, self.sum(node['inputs']))
            if node['hi']-node['lo'] == 1:
                Z[node['lo']] = total[x]
        for i in range(self.p):
            for e in range(2):
                face = self.sum(self.A[I, i, 1-e] for I in self.cubes if i in I)
                self.centers.append(self.add(Z[i], face))
        return sum(len(node['inputs']) for node in nodes)

    def finish(self, triple, pair, allbut, center_kind='star'):
        self.local_channels()
        base_nodes = len(self.a)
        D = dict(zip(self.cubes, self.module(triple, [self.F[I] for I in self.cubes])))
        P, Q = {}, {}
        for i in range(self.p):
            others = [a for a in range(self.p) if a != i]
            pairs = list(combinations(others, 2))
            for bit in range(2):
                inputs = [self.A[tuple(sorted((i, *K))), i, bit] for K in pairs]
                for K, node in zip(pairs, self.module(pair, inputs)):
                    P[tuple(sorted((i, *K))), i, bit] = node
        for i, j in combinations(range(self.p), 2):
            others = [a for a in range(self.p) if a not in (i, j)]
            for mode in range(2):
                inputs = [self.G[tuple(sorted((i, j, k))), i, j, mode] for k in others]
                for k, node in zip(others, self.module(allbut, inputs)):
                    Q[tuple(sorted((i, j, k))), i, j, mode] = node
        query_nodes = len(self.a)
        def emit(I, bits_list, node, numerator=1, channel=''):
            self.root.append(dict(node=node, targets=[self.source[I, b] for b in bits_list],
                                  coefficients=[f'{numerator}/2']*len(bits_list),
                                  kind='side', channel=channel))
        for I in self.cubes:
            all_bits = list(product(range(2), repeat=3))
            emit(I, all_bits, D[I], channel='disjoint')
            for a in range(2):
                emit(I, [b for b in all_bits if b[0] == a],
                     P[I, I[0], 1-a], channel='face0')
            for a, b in product(range(2), repeat=2):
                emit(I, [(a, b, c) for c in range(2)],
                     P[I, I[1], 1-b], channel='face1')
            for a, b in product(range(2), repeat=2):
                emit(I, [(a, b, c) for c in range(2)],
                     Q[I, I[0], I[1], a ^ b], 2*a-1, 'edge01')
            for bits in all_bits:
                emit(I, [bits], P[I, I[2], 1-bits[2]], channel='face2')
            for ii, jj in [(0, 2), (1, 2)]:
                for bits in all_bits:
                    emit(I, [bits], Q[I, I[ii], I[jj], bits[ii] ^ bits[jj]],
                         2*bits[ii]-1, f'edge{ii}{jj}')
        if center_kind == 'star':
            # Their scatter is 1/2 sum_(i in T) S_i - 1/6 sum_i S_i.
            for i in range(self.p):
                for e in range(2):
                    self.centers.append(self.sum(self.A[I, i, e] for I in self.cubes if i in I))
            incidences = 0
            center_scatter = '1/2 sum_(i in T) S_i - 1/6 sum_i S_i'
        else:
            assert center_kind == 'disjoint'
            incidences = self.center_channels()
            center_scatter = 'sum_i E_i/(h-3) - 1/2 sum_(i in T) E_i'
        from fractions import Fraction
        for coordinate, node in enumerate(self.centers):
            if center_kind == 'star':
                coefficients = ['1/3' if coordinate in t else '-1/6' for t in self.labels]
            else:
                coefficients = [str(Fraction(1, self.h-3) -
                                    (Fraction(1, 2) if coordinate in t else 0))
                                for t in self.labels]
            self.root.append(dict(node=node, targets=list(range(len(self.labels))),
                                  coefficients=coefficients, kind='center', coordinate=coordinate))
        return dict(p=self.p, h=self.h, v=len(self.labels),
                    labels=self.labels, inputs=[sum(1 << x for x in t) for t in self.labels],
                    args=self.a, signs=self.signs,
                    roots=self.root, centers=self.centers,
                    center_kind=center_kind, center_scatter=center_scatter,
                    local_K='Two 4x4 Hadamard/2 blocks on opposite cube parities, using original X destructively',
                    source_data_histogram={2: len(self.labels), self.h-4: len(self.labels),
                                           1: len(self.labels)},
                    target_data_histogram={self.h-4: len(self.labels), 1: 3*len(self.labels)},
                    counts=dict(local_channel_additions=base_nodes-len(self.labels),
                                query_additions=query_nodes-base_nodes,
                                center_additions=len(self.a)-query_nodes,
                                center_tree_incidences=incidences,
                                signed_additions=sum(x < 0 for x in self.signs),
                                side_root_uses=sum(r['kind'] == 'side' for r in self.root),
                                center_roots=len(self.centers)),
                    status='Exact signed scalar circuit and frozen-support geometry input; rank compiler and moment are separate.')
