#!/usr/bin/env python3
"""Exact arbitrary-dirty completions for the source-aligned complex flow.

GPT-6 Astra, for icekylinx, 2026-10-09.

This is new completion/certificate code. Its input is produced by
complex_frame_flow.py from the source-aligned rewrite of the pinned PR168
fd25adb7 producer. The inherited producer, physical-word, and query-module
credits remain in source_aligned_local.py and in the pinned source tree.

No rank or scalar identity in this checker is evaluated modulo a prime.
All local maps and their inverse gate programs use fractions.Fraction.
The certificate includes a literal invertible completion at every vertex,
including all fresh complements and all recycled fresh-zero coordinates.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from fractions import Fraction as F
from pathlib import Path
import argparse
import gzip
import hashlib
import heapq
import json
import math
import time

ROOT = Path(__file__).resolve().parent.parent


def portable(p):
    p = Path(p).resolve()
    try:
        return str(p.relative_to(ROOT))
    except ValueError:
        return str(p)


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def enc(x):
    x = F(x)
    return [x.numerator, x.denominator]


def axpy(dst, src, a):
    if not a:
        return
    for k, c in src.items():
        v = dst.get(k, 0) + a*c
        if v:
            dst[k] = v
        else:
            dst.pop(k, None)


class Span:
    """An exact sparse basis with coordinates in selected original rows."""

    def __init__(self, rows=()):
        self.pivots = {}
        self.selected = []
        for i, row in enumerate(rows):
            self.add(row, i)

    def reduce(self, row):
        row = dict(row)
        coord = {}
        for col in sorted(self.pivots):
            a = row.get(col, 0)
            if a:
                p, c = self.pivots[col]
                axpy(row, p, -a)
                axpy(coord, c, a)
        return row, coord

    def coordinates(self, row):
        rem, coord = self.reduce(row)
        assert not rem, ('Not in exact row span', rem)
        return coord

    def add(self, row, label):
        rem, coord = self.reduce(row)
        if not rem:
            return False
        col = min(rem)
        a = F(rem[col])
        k = len(self.selected)
        self.selected.append(label)
        c = {j: -v/a for j, v in coord.items()}
        c[k] = 1/a
        self.pivots[col] = ({j: F(v)/a for j, v in rem.items()}, c)
        return True


def identity(n):
    return [[F(i == j) for j in range(n)] for i in range(n)]


def apply_gate(A, gate):
    kind, i, j, num, den = gate
    c = F(num, den)
    if kind == 'swap':
        A[i], A[j] = A[j], A[i]
    elif kind == 'scale':
        A[i] = [c*x for x in A[i]]
    else:
        assert kind == 'add' and i != j
        A[i] = [x+c*y for x, y in zip(A[i], A[j])]


def inverse_gate(g):
    kind, i, j, num, den = g
    if kind == 'swap':
        return g
    a = -F(num, den) if kind == 'add' else 1/F(num, den)
    return [kind, i, j, *enc(a)]


def inverse_program(Q):
    """Literal elementary row gates taking Q to I, hence implementing Q^-1."""
    n = len(Q)
    A = [list(row) for row in Q]
    gates = []
    for col in range(n):
        candidates = [i for i in range(col, n) if A[i][col]]
        assert candidates, ('Singular completion', col, Q)
        # Prefer a dyadic unit and a small coefficient. This is a fixed
        # exact pivot convention, not a parameter search.
        def score(i):
            a = A[i][col]
            z = abs(a.numerator)
            return (bool(z & (z-1)), z.bit_length()+a.denominator.bit_length(), i)
        pivot = min(candidates, key=score)
        if pivot != col:
            g = ['swap', col, pivot, 1, 1]
            apply_gate(A, g); gates.append(g)
        if A[col][col] != 1:
            g = ['scale', col, col, *enc(1/A[col][col])]
            apply_gate(A, g); gates.append(g)
        for i in range(n):
            if i != col and A[i][col]:
                g = ['add', i, col, *enc(-A[i][col])]
                apply_gate(A, g); gates.append(g)
    assert A == identity(n)
    forward = [inverse_gate(g) for g in reversed(gates)]
    A = identity(n)
    for g in forward:
        apply_gate(A, g)
    assert A == Q
    return gates


def fresh_product(Q, C):
    out = []
    for row in Q:
        d = {}
        for a, c in zip(row, C):
            axpy(d, c, a)
        out.append(d)
    return out


def completion(node, vectors):
    n, t = node['n'], node['t']
    b, d, r = node['new_dirty'], node['d'], node['r']
    N = n+b
    C = [vectors[x] for x in node['inputs']]
    D = [vectors[x] for x in node['outputs']]
    reads = [vectors[x] for x in node['read_values']]
    if node['source_controls']:
        E = set(node['source_controls'])
        assert all(set(row) <= E for row in C+D+reads)
        assert d == r == 0 and b == max(0, t-n)
        assert not reads, 'Selected source-control vertices have no read sinks.'
        # Clear C_i(X), use an identity dirty map, then inject D_j(X).
        # In the selected word these vertices have no outgoing requests
        # or reads; all their coordinates retire with exactly zero fresh.
        Q = identity(N)
        return dict(size=N, inverse_gates=[],
                    source_erase=[node['inputs'][i] for i in range(n)],
                    source_inject=list(node['outputs']),
                    fresh_complements=[], read_coefficients=[]), Q
    span = Span(C)
    assert len(span.selected) == d
    coords = [span.coordinates(row) for row in C]
    E = [span.coordinates(row) for row in D]
    output_span = Span(E)
    assert len(output_span.selected) == r
    assert b == max(0, t+d-r-n)
    selected = span.selected
    T = []
    # Invertible change from input coordinates to d chosen fresh basis
    # coordinates, then all exact fresh-kernel coordinates.
    for j in selected:
        row = [F(0)]*N; row[j] = F(1); T.append(row)
    for j in range(n):
        if j in selected:
            continue
        row = [F(0)]*N; row[j] = F(1)
        for k, a in coords[j].items():
            row[selected[k]] -= a
        T.append(row)
    for j in range(n, N):
        row = [F(0)]*N; row[j] = F(1); T.append(row)
    assert len(T) == N
    canonical = []
    independent_outputs = set(output_span.selected)
    used_kernel = 0
    for j, ecoord in enumerate(E):
        row = [F(0)]*N
        for k, a in ecoord.items():
            row[k] = a
        if j not in independent_outputs:
            row[d+used_kernel] = F(1); used_kernel += 1
        canonical.append(row)
    assert used_kernel == t-r
    complement_positions = []
    for k in range(d):
        if output_span.add({k: F(1)}, k):
            row = [F(0)]*N; row[k] = F(1)
            canonical.append(row); complement_positions.append(k)
    assert len(complement_positions) == d-r
    for k in range(used_kernel, N-d):
        row = [F(0)]*N; row[d+k] = F(1); canonical.append(row)
    assert len(canonical) == N
    Q = [[sum(row[k]*T[k][j] for k in range(N)) for j in range(N)]
         for row in canonical]
    product = fresh_product(Q, C+[{}]*b)
    assert product[:t] == D
    assert product[t:t+d-r] == [C[selected[k]] for k in complement_positions]
    assert all(not x for x in product[t+d-r:])
    rc = []
    for row in reads:
        coord = span.coordinates(row)
        physical = {selected[k]: a for k, a in coord.items()}
        actual = {}
        for j, a in physical.items():
            axpy(actual, C[j], a)
        assert actual == row
        rc.append([[j, *enc(a)] for j, a in sorted(physical.items())])
    gates = inverse_program(Q)
    return dict(size=N, inverse_gates=gates, source_erase=[], source_inject=[],
                fresh_complements=[node['inputs'][selected[k]] for k in complement_positions],
                read_coefficients=rc), Q


def frame_key(f):
    return f[0], tuple(f[1])


def frame_basis(rows):
    piv = {}
    for x in rows:
        for k in sorted(piv, reverse=True):
            if x >> k & 1:
                x ^= piv[k]
        if x:
            k = x.bit_length()-1
            piv[k] = x
    return tuple(piv.values())


def nested(U, V):
    return len(frame_basis(tuple(U)+tuple(V))) == len(V)


def geometry_and_slots(witness, h, v):
    """Verify the whole flow DAG and the once-only physical-coordinate paths."""
    nodes = witness['nodes']
    by_frame = {frame_key(n['frame']): i for i, n in enumerate(nodes)}
    assert len(by_frame) == len(nodes)
    ins, outs, dag = defaultdict(list), defaultdict(list), defaultdict(list)
    indeg = Counter()
    H = Counter({1: v})
    for edge in witness['edges']:
        U, V = edge['source'], edge['target']
        i, j = by_frame[frame_key(U)], by_frame[frame_key(V)]
        assert U[0] <= V[0] and nested(U[1], V[1]) and i != j
        outs[i].extend(edge['basis']); ins[j].extend(edge['basis'])
        dag[i].append(j); indeg[j] += 1
        H[len(V[1])-len(U[1])] += len(edge['basis'])
    source_copies = 0
    copied_ports = set()
    R = v
    for i, node in enumerate(nodes):
        # build_flow appends original source injections after edge inputs.
        assert node['inputs'][:len(ins[i])] == ins[i]
        extras = node['inputs'][len(ins[i]):]
        for k in extras:
            row = witness['vectors'][k]
            assert len(row) == 1 and row[0][1] == 1
            j = row[0][0]
            assert j not in copied_ports; copied_ports.add(j)
            assert node['frame'] == [1,[witness['original_source_ports'][j]]]
            source_copies += 1
        assert node['outputs'] == outs[i]
        assert len(node['inputs']) == node['n']
        assert len(node['outputs']) == node['t']
        assert node['retired'] == node['n']+node['new_dirty']-node['t']
        U = node['frame'][1]
        for ident in set(node['inputs']+node['outputs']+node['read_values']):
            assert all(nested((witness['original_source_ports'][j],),U)
                       for j,c in witness['vectors'][ident])
        R += node['new_dirty']
        u = len(node['frame'][1])
        H[u] += node['new_dirty']; H[h-u] += node['retired']
    assert source_copies == v
    used_donors, used_births = set(), set()
    for i, a, j, b in witness['kernel_pairs']:
        U, V = nodes[i], nodes[j]
        assert (i, a) not in used_donors and (j, b) not in used_births
        used_donors.add((i, a)); used_births.add((j, b))
        assert 0 <= a < U['retired']-(U['d']-U['r'])
        assert 0 <= b < V['new_dirty']
        assert U['frame'][0] <= V['frame'][0]
        assert nested(U['frame'][1], V['frame'][1]) and i != j
        dag[i].append(j); indeg[j] += 1
        u, vv = len(U['frame'][1]), len(V['frame'][1])
        H[h-u] -= 1; H[vv] -= 1; H[vv-u] += 1; R -= 1
    def priority(i):
        phase, U = nodes[i]['frame']
        return phase, len(U), tuple(U), i
    ready = [priority(i) for i in range(len(nodes)) if not indeg[i]]
    heapq.heapify(ready)
    order = []
    while ready:
        i = heapq.heappop(ready)[-1]; order.append(i)
        for j in dag[i]:
            indeg[j] -= 1
            if not indeg[j]:
                heapq.heappush(ready, priority(j))
    assert len(order) == len(nodes), 'Kernel reuse created a chronological cycle.'
    assert [nodes[i]['frame'][0] for i in order] == sorted(nodes[i]['frame'][0] for i in order)
    center_count = 0
    for node in nodes:
        for read in node['reads']:
            if read['kind'] == 'center':
                assert node['frame'][0] == 1
                H[len(node['frame'][1])] += 1; center_count += 1
            else:
                assert node['frame'][0] == 2
    return dict(physical_R=R, topological_order=order,
                transport_histogram=dict(sorted((k, c) for k, c in H.items() if k and c)),
                ordinary_edges=len(witness['edges']), kernel_edges=len(witness['kernel_pairs']),
                copied_center_count=center_count)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--witness', type=Path, required=True)
    ap.add_argument('--profile', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    start = time.monotonic()
    w = json.loads(args.witness.read_text())
    p = json.loads(args.profile.read_text())
    vectors = [dict(row) for row in w['vectors']]
    transport = geometry_and_slots(w, p['h'], p['v'])
    assert transport['physical_R'] == p['new_R']
    assert transport['transport_histogram'] == {int(k):c for k,c in p['local_histogram'].items()}
    maps = []
    den_lcm = num_lcm = 1
    max_num = max_den = 1
    all_coefficients = set()
    gates = 0
    def account(a):
        nonlocal den_lcm, num_lcm, max_num, max_den
        a = F(a)
        if not a:
            return
        den_lcm = math.lcm(den_lcm, a.denominator)
        num_lcm = math.lcm(num_lcm, abs(a.numerator))
        max_num = max(max_num, abs(a.numerator)); max_den = max(max_den, a.denominator)
        all_coefficients.add(a)
    for i, node in enumerate(w['nodes']):
        record, Q = completion(node, vectors)
        maps.append(record)
        gates += len(record['inverse_gates'])
        for row in Q:
            for a in row:
                account(a)
        for g in record['inverse_gates']:
            account(F(g[3], g[4]))
            gg = inverse_gate(g); account(F(gg[3], gg[4]))
        for read in record['read_coefficients']:
            for _, num, den in read:
                account(F(num, den))
        for ident in record['source_erase']+record['source_inject']:
            for c in vectors[ident].values():
                account(c)
        if i % 4000 == 0:
            print(json.dumps(dict(stage='exact_completions', nodes=i,
                                  denominator_lcm=str(den_lcm), seconds=time.monotonic()-start)), flush=True)
    # Every non-kernel retirement survives to F; every reused kernel is
    # routed exactly once to a new dirty birth. Every local map is square
    # invertible, so their DAG composition is a square invertible global M.
    cert = dict(signature='GPT-6 Astra', schema='complex-source-aligned-exact-flow-v1',
                input_witness_sha256=digest(args.witness), input_profile_sha256=digest(args.profile),
                maps=maps, topological_order=transport['topological_order'],
                kernel_pairs=w['kernel_pairs'])
    program_binding = {k:cert[k] for k in ('maps','topological_order','kernel_pairs')}
    program_sha = hashlib.sha256(json.dumps(program_binding,separators=(',',':')).encode()).hexdigest()
    cert_path = args.out.with_suffix('.certificate.json.gz')
    encoded = (json.dumps(cert, separators=(',', ':'))+'\n').encode()
    cert_path.write_bytes(gzip.compress(encoded, compresslevel=9, mtime=0))
    dyadic = all(a.denominator & (a.denominator-1) == 0 for a in all_coefficients)
    result = dict(signature='GPT-6 Astra', status='Exact rational local lifts and inverse gate programs verified; monotone flow and zero-fresh kernel reuse DAG verified.',
                  nodes=len(maps), inverse_elementary_gates=gates,
                  source_control_vertices=sum(bool(n['source_controls']) for n in w['nodes']),
                  source_erasures=len(w['source_erasures']), kernel_reuses=len(w['kernel_pairs']),
                  physical_R=transport['physical_R'], denominator_lcm=str(den_lcm),
                  coefficient_numerator_lcm=str(num_lcm), max_abs_numerator=str(max_num),
                  max_denominator=str(max_den), all_actual_coefficients_dyadic=dyadic,
                  coefficients=[enc(a) for a in sorted(all_coefficients)],
                  certificate_path=portable(cert_path), certificate_sha256=digest(cert_path),
                  exact_scalar_program_sha256=program_sha,
                  witness_path=portable(args.witness), witness_sha256=digest(args.witness),
                  checker_path=portable(Path(__file__)), checker_sha256=digest(Path(__file__)),
                  seconds=time.monotonic()-start)
    args.out.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
