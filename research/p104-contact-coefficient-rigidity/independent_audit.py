#!/usr/bin/env python3
# Jerry Chen / @CubeJerry with substantial OpenAI assistance; Apache-2.0.
"""Independent audit of the coordinator's finite rigidity claim.
No primary verifier or discovery code is imported. Public maps use rational
COPY overwrite and owned reset semantics. Gaussian elimination is applied to
the full changed public matrix, independently of its rank-two factorization.
"""
from pathlib import Path
from fractions import Fraction as Q
from collections import defaultdict, Counter
import gzip, json, hashlib, time, argparse
parser = argparse.ArgumentParser(description='Independent full-matrix audit; no primary verifier imports.')
parser.add_argument('--word', type=Path, required=True)
parser.add_argument('--output', type=Path)
args = parser.parse_args()
w = json.loads(gzip.decompress(args.word.read_bytes()))
p = w['program']
n = w['public']
nn = n + w['owned_fields']
dims = list(map(len, w['frames']))
start = time.time()
canon = json.dumps(w, sort_keys=True, separators=(',', ':')).encode()
if not hashlib.sha256(canon).hexdigest() == 'd3ccfce7bdbca3b79771844e6c9fee48f1a8066444a19218995648df96982821':
    raise ValueError("Independent audit failed: hashlib.sha256(canon).hexdigest() == 'd3ccfce7bdbca3b79771844e6c9fee48f1a8066444a19218995648df96982821'")
traces = [[] for _ in range(nn)]
for k, e in enumerate(p):
    touched = {e[1]}
    if e[0] in ('ADD', 'COPY'):
        touched.add(e[2])
    for r in touched:
        traces[r].append(k)
visits = []
for r, trace in enumerate(traces):
    moves = [z for z, k in enumerate(trace) if p[k][0] == 'MOVE']
    for a, b in zip(moves, moves[1:]):
        inside = trace[a + 1:b]
        adds = [k for k in inside if p[k][0] == 'ADD']
        if len(adds) != 1 or any((p[k][0] not in ('ADD', 'SCALE') for k in inside)):
            continue
        ei, ej = (p[trace[a]], p[trace[b]])
        if abs(dims[ei[3]] - dims[ei[2]]) == 0 or abs(dims[ej[3]] - dims[ej[2]]) == 0:
            continue
        visits.append((r, trace[a], adds[0], trace[b]))
deletions = sorted({z[2] for z in visits})
scalar = [k for k, e in enumerate(p) if e[0] in ('ADD', 'COPY', 'SCALE')]
K = {r for r in range(n) if dims[w['initial'][r]] == 0}
R = {r for r in range(n) if dims[w['final'][r]] == 9}
Kb = set(range(n)) - K
Rb = set(range(n)) - R

def axpy(row, other, q):
    if not q:
        return
    for j, v in other.items():
        row[j] = row.get(j, Q(0)) + q * v
        if not row[j]:
            del row[j]

def coefficient(e):
    return Q(e[2] if e[0] == 'SCALE' else e[3])

def source(e):
    return e[1] if e[0] == 'SCALE' else e[2]

def mutate(rows, e, delta=Q(0)):
    op, r = e[:2]
    if op == 'ADD':
        axpy(rows[r], rows[e[2]], coefficient(e) + delta)
    elif op == 'COPY':
        rows[r] = {j: (coefficient(e) + delta) * v for j, v in rows[e[2]].items() if (coefficient(e) + delta) * v}
    elif op == 'SCALE':
        rows[r] = {j: (coefficient(e) + delta) * v for j, v in rows[r].items() if (coefficient(e) + delta) * v}
    elif op in ('INIT', 'CLEAR'):
        rows[r] = {}

def replay(changes=None):
    changes = changes or {}
    rows = [{r: Q(1)} if r < n else {} for r in range(nn)]
    for k, e in enumerate(p):
        mutate(rows, e, changes.get(k, Q(0)))
    return rows[:n]
rows = [{r: Q(1)} if r < n else {} for r in range(nn)]
v = {}
for k, e in enumerate(p):
    if e[0] in ('ADD', 'COPY', 'SCALE'):
        v[k] = dict(rows[source(e)])
    mutate(rows, e)
A = [{r: Q(1)} for r in range(n)]
for r in w['live']:
    A[r + 112][r] = Q(1)
if not rows[:n] == A:
    raise ValueError('Independent audit failed: rows[:n] == A')
adj = [{r: Q(1)} if r < n else {} for r in range(nn)]
u = {}
for k in reversed(range(len(p))):
    e = p[k]
    op, r = e[:2]
    if op in ('ADD', 'COPY', 'SCALE'):
        u[k] = dict(adj[r])
    if op == 'ADD':
        axpy(adj[e[2]], adj[r], coefficient(e))
    elif op == 'COPY':
        tail = dict(adj[r])
        adj[r] = {}
        axpy(adj[e[2]], tail, coefficient(e))
    elif op == 'SCALE':
        adj[r] = {j: coefficient(e) * z for j, z in adj[r].items() if coefficient(e) * z}
    elif op in ('INIT', 'CLEAR'):
        adj[r] = {}
pp = {k: {r: z for r, z in u[k].items() if r in Rb} for k in scalar}
qq = {k: {r: z for r, z in v[k].items() if r in Kb} for k in scalar}

def direction(x):
    if not x:
        return None
    fst = min(x)
    s = x[fst]
    return tuple(((r, z / s) for r, z in sorted(x.items())))
pdir = {k: direction(pp[k]) for k in scalar}
qdir = {k: direction(qq[k]) for k in scalar}
if not all((pp[d] and qq[d] for d in deletions)):
    raise ValueError('Independent audit failed: all((pp[d] and qq[d] for d in deletions))')
pairs = []
for d in deletions:
    for c in scalar:
        if c < d and qdir[c] == qdir[d] and (pdir[c] is None or pdir[c] == pdir[d]):
            pairs.append((d, c))
        elif c > d and pdir[c] == pdir[d] and (qdir[c] is None or qdir[c] == qdir[d]):
            pairs.append((d, c))
if (len(visits),len(deletions),len(scalar),len(pairs)) != (1466,1278,15072,172):
    raise ValueError('Independent domain census changed')
print('DOMAIN', len(visits), len(deletions), len(scalar), 'PAIRS', len(pairs), 'seconds', time.time() - start, flush=True)

def transfer(a, b):
    z = [Q(0)] * nn
    z[p[a][1]] = Q(1)
    for e in p[a + 1:b]:
        op, r = e[:2]
        if op == 'ADD':
            z[r] += Q(e[3]) * z[e[2]]
        elif op == 'COPY':
            z[r] = coefficient(e) * z[e[2]]
        elif op == 'SCALE':
            z[r] *= Q(e[2])
        elif op in ('INIT', 'CLEAR'):
            z[r] = Q(0)
    return z[source(p[b])]

def outer(x, y):
    return {(r, c): a * b for r, a in x.items() for c, b in y.items() if a * b}

def scaled(x, a):
    return {r: a * z for r, z in x.items() if a * z}

def null_full(T):
    piv = {}
    for original in T:
        row = dict(original)
        while row:
            lead = min(row)
            if lead not in piv:
                s = row[lead]
                piv[lead] = {j: v / s for j, v in row.items()}
                break
            axpy(row, piv[lead], -row[lead])
    free = sorted(set(range(n)) - set(piv))
    if not free:
        return (None, len(piv))
    x = {free[0]: Q(1)}
    for lead, row in sorted(piv.items(), reverse=True):
        z = -sum((a * x.get(j, Q(0)) for j, a in row.items() if j != lead))
        if z:
            x[lead] = z
    if not (x and all((sum((a * x.get(j, Q(0)) for j, a in row.items())) == 0 for row in T))):
        raise ValueError('Independent audit failed: x and all((sum((a * x.get(j, Q(0)) for j, a in row.items())) == 0 for row in T))')
    return (x, len(piv))
report = {'payload_sha256': hashlib.sha256(canon).hexdigest(), 'visits': len(visits), 'deleted_ADDs': len(deletions), 'scalar_events': len(scalar), 'K': len(K), 'R': len(R), 'direction_pairs': len(pairs), 'pair_kinds': dict(Counter(('both_nonzero' if pp[c] and qq[c] else 'zero_original_boundary_derivative' for d, c in pairs))), 'inconsistent': [], 'singular': []}
for d, c in pairs:
    a, b = sorted((d, c))
    tau = transfer(a, b)
    dd = -coefficient(p[d])
    D = scaled(outer(pp[d], qq[d]), dd)
    if d < c:
        row = dict(qq[c])
        axpy(row, qq[d], dd * tau)
        B = outer(pp[c], row)
    else:
        column = dict(pp[c])
        axpy(column, pp[d], dd * tau)
        B = outer(column, qq[c])
    if not B:
        if not D:
            raise ValueError('Independent audit failed: D')
        report['inconsistent'].append([d, c])
        continue
    key = next(iter(D))
    if not key in B:
        raise ValueError('Independent audit failed: key in B')
    dc = -D[key] / B[key]
    if not all((D.get(k, Q(0)) + dc * B.get(k, Q(0)) == 0 for k in D.keys() | B.keys())):
        raise ValueError('Independent audit failed: all((D.get(k, Q(0)) + dc * B.get(k, Q(0)) == 0 for k in D.keys() | B.keys()))')
    T = replay({d: dd, c: dc})
    if not all((T[r].get(j, Q(0)) == A[r].get(j, Q(0)) for r in Rb for j in Kb)):
        raise ValueError('Independent audit failed: all((T[r].get(j, Q(0)) == A[r].get(j, Q(0)) for r in Rb for j in Kb))')
    vec, rank = null_full(T)
    if not vec is not None:
        raise ValueError('Independent audit failed: vec is not None')
    report['singular'].append({'deleted': d, 'compensator': c, 'new_coefficient': str(coefficient(p[c]) + dc), 'rank': rank, 'null_vector': {r: str(z) for r, z in vec.items()}})
    print('SINGULAR', d, c, 'new', coefficient(p[c]) + dc, 'rank', rank, 'support', len(vec), flush=True)
if not (len(report['inconsistent']) == 157 and len(report['singular']) == 15):
    raise ValueError("Independent audit failed: len(report['inconsistent']) == 157 and len(report['singular']) == 15")
if {x['rank'] for x in report['singular']} != {771}:
    raise ValueError('Independent singular ranks changed')
if report['pair_kinds'] != {'both_nonzero':103,'zero_original_boundary_derivative':69}:
    raise ValueError('Independent pair-kind census changed')
report['runtime_seconds'] = time.time() - start
if args.output:
    args.output.write_text(json.dumps(report, indent=2) + '\n')
print('PASS_INDEPENDENT_FULL_MATRIX_AUDIT', report['pair_kinds'], 'singular_ranks', sorted({x['rank'] for x in report['singular']}), 'seconds', report['runtime_seconds'], flush=True)
