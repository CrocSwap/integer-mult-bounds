#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent full Gaussian-rational operators, native kernel and basis witnesses.

No eigenvalue formula from verify.py is used to construct the matrices.
Arham Tahir with substantial OpenAI Codex assistance.
"""
import argparse
from fractions import Fraction as Q
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify as V  # source/receipt utilities and comparison values only

ZERO = (Q(0), Q(0))
ONE = (Q(1), Q(0))
ROOTS = (ONE, (Q(0), Q(1)), (-Q(1), Q(0)), (Q(0), -Q(1)))


def add(a, b):
    return a[0] + b[0], a[1] + b[1]


def neg(a):
    return -a[0], -a[1]


def mul(a, b):
    return a[0]*b[0] - a[1]*b[1], a[0]*b[1] + a[1]*b[0]


def div(a, b):
    d = b[0]*b[0] + b[1]*b[1]
    V.require(d != 0, 'zero Gaussian divisor')
    return (a[0]*b[0]+a[1]*b[1])/d, (a[1]*b[0]-a[0]*b[1])/d


def eye(n):
    return [[ONE if i == j else ZERO for j in range(n)] for i in range(n)]


def mm(a, b):
    V.require(len(a[0]) == len(b), 'matrix dimensions')
    out = [[ZERO for _ in b[0]] for _ in a]
    for i, row in enumerate(a):
        for k, x in enumerate(row):
            if x != ZERO:
                for j, y in enumerate(b[k]):
                    if y != ZERO:
                        out[i][j] = add(out[i][j], mul(x, y))
    return out


def scale(a, c):
    return [[mul(x, c) for x in row] for row in a]


def transpose(a):
    return [list(row) for row in zip(*a)]


def difference(a, b):
    return [[add(x, neg(y)) for x, y in zip(ar, br)] for ar, br in zip(a, b)]


def rank(a):
    a = [row[:] for row in a]
    pivot = 0
    for j in range(len(a[0])):
        k = next((i for i in range(pivot, len(a)) if a[i][j] != ZERO), None)
        if k is None:
            continue
        a[pivot], a[k] = a[k], a[pivot]
        p = a[pivot][j]
        a[pivot] = [div(x, p) for x in a[pivot]]
        for i in range(pivot+1, len(a)):
            factor = a[i][j]
            if factor != ZERO:
                a[i] = [add(x, neg(mul(factor, y))) for x,y in zip(a[i],a[pivot])]
        pivot += 1
        if pivot == len(a):
            break
    return pivot


def tr(a):
    out = ZERO
    for i in range(len(a)):
        out = add(out, a[i][i])
    return out


def tensor(f, direction=1):
    """Execute literal two-coordinate butterflies on every basis column."""
    n = 2 ** f
    a = [[ZERO for _ in range(n)] for _ in range(n)]
    c0, c1 = (Q(1,2), Q(direction,2)), (Q(1,2), -Q(direction,2))
    for column in range(n):
        vector = [ONE if i == column else ZERO for i in range(n)]
        for axis in range(f):
            vector = [add(mul(c0, vector[i]), mul(c1, vector[i ^ (1 << axis)])) for i in range(n)]
        for row, value in enumerate(vector):
            a[row][column] = value
    return a


def blocks(arrays):
    n = sum(len(a) for a in arrays)
    out = [[ZERO for _ in range(n)] for _ in range(n)]
    offset = 0
    for a in arrays:
        for i, row in enumerate(a):
            for j, x in enumerate(row):
                out[offset+i][offset+j] = x
        offset += len(a)
    return out


def walsh(f):
    return [[(Q(-1 if (i & j).bit_count() % 2 else 1), Q(0))
             for j in range(2 ** f)] for i in range(2 ** f)]


def serialize(a):
    return [[[str(x), str(y)] for x,y in row] for row in a]


def readable_json(value, depth=0):
    """Keep each Gaussian matrix row on one line in the reviewable receipt."""
    if isinstance(value, list) and (not value or all(isinstance(x, (str,int,bool)) for x in value)
            or all(isinstance(x,list) and len(x)==2 and all(isinstance(y,str) for y in x) for x in value)):
        return json.dumps(value)
    indent, inner = '  '*depth, '  '*(depth+1)
    if isinstance(value, dict):
        rows = [inner+json.dumps(k)+': '+readable_json(v,depth+1) for k,v in value.items()]
        return '{\n'+',\n'.join(rows)+'\n'+indent+'}'
    if isinstance(value, list):
        rows = [inner+readable_json(v,depth+1) for v in value]
        return '[\n'+',\n'.join(rows)+'\n'+indent+']'
    return json.dumps(value)


def native_module():
    V.check_sources()
    spec = importlib.util.spec_from_file_location('pinned_clifford_kernel', V.ROOT / V.KERNEL)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def eigenspace_counts(a):
    return [len(a) - rank(difference(a, scale(eye(len(a)), mu))) for mu in ROOTS]


def mixed_witness(f, h, spectators, phase):
    u = blocks([walsh(f), walsh(f)])
    w = blocks([walsh(h) for _ in range(spectators)])
    wanted = [j.bit_count() % 4 for j in range(2 ** f)] + [(-j.bit_count()) % 4 for j in range(2 ** f)]
    offered = [(phase+j.bit_count()) % 4 for _ in range(spectators) for j in range(2 ** h)]
    available = {j: [k for k,v in enumerate(offered) if v == j] for j in range(4)}
    perm = [available[j].pop(0) for j in wanted]
    V.require(all(not xs for xs in available.values()), 'eigenbasis matching incomplete')
    v = [[row[j] for j in perm] for row in w]
    e = scale(mm(v, transpose(u)), (Q(1, 2 ** f), Q(0)))
    einv = scale(mm(u, transpose(v)), (Q(1, 2 ** h), Q(0)))
    target = blocks([tensor(f), tensor(f, -1)])
    child = scale(blocks([tensor(h) for _ in range(spectators)]), ROOTS[phase])
    V.require(mm(einv,e) == eye(len(e)) and mm(e,einv) == eye(len(e)), 'basis not invertible')
    V.require(mm(child,e) == mm(e,target) and mm(mm(einv,child),e) == target, 'full mixed identity failed')
    V.require(mm(mm(einv,scale(child,ROOTS[1])),e) != target, 'wrong-phase control did not fail')
    return {'f': f, 'h': h, 'spectators': spectators, 'phase': phase,
            'dimension': len(e), 'encoding': serialize(e), 'inverse_encoding': serialize(einv),
            'all_columns_checked': len(e), 'wrong_phase_rejected': True}


def make_certificate():
    native = native_module()
    digest = hashlib.sha256()
    native_entries = 0
    for f in range(1,6):
        w = walsh(f)
        V.require(mm(w,w) == scale(eye(2 ** f), (Q(2 ** f), Q(0))), 'Walsh basis identity')
        for direction in (-1,1):
            a = tensor(f, direction)
            op = native.fourier(f)
            if direction == -1:
                op = op.adjoint()
            for col in range(2 ** f):
                vec, den = op.zero_state(col)
                V.require([a[row][col] for row in range(2 ** f)] ==
                          [(Q(x,2 ** den),Q(y,2 ** den)) for x,y in vec], 'native basis-column mismatch')
                native_entries += len(vec)
            expected = [[mul(w[i][j], ROOTS[(direction*j.bit_count())%4]) for j in range(2 ** f)] for i in range(2 ** f)]
            V.require(mm(a,w) == expected, 'complete eigenbasis identity')
            V.require(tr(mm(a,a)) == ZERO, 'dense tensor square trace')
            if f <= 3:
                V.require(eigenspace_counts(a) == V.spectrum(f,direction), 'independent elimination/multiplicity disagreement')
            digest.update(V.canonical(serialize(a)).encode())
    witnesses = [mixed_witness(1,2,1,3), mixed_witness(3,4,1,0), mixed_witness(4,4,2,0)]
    # Dense arbitrary nonmonomial reciprocal change: E=I+u*v^T, v^T*u=0.
    target = blocks([tensor(1) for _ in range(16)])
    n = len(target)
    e, einv = eye(n), eye(n)
    for i in range(n):
        e[i][0] = add(e[i][0], ONE)
        e[i][1] = add(e[i][1], neg(ONE))
        einv[i][0] = add(einv[i][0], neg(ONE))
        einv[i][1] = add(einv[i][1], ONE)
    V.require(mm(e,einv) == eye(n), 'nonmonomial basis inverse failed')
    correction_ranks = []
    for phase in range(4):
        a = scale(tensor(5),ROOTS[phase])
        b = mm(mm(einv,a),e)
        defect = rank(difference(target,b))
        bound = V.correction_floor(V.target(1,16),V.child(5,1,phase))
        V.require(defect >= bound and defect > 0, 'rank perturbation control')
        correction_ranks.append(defect)
    # Arbitrary independent left/right maps are outside the theorem.
    t = blocks([tensor(1),tensor(1)])
    a, ainv = tensor(2),tensor(2,-1)
    left = mm(t,ainv)
    V.require(mm(left,a) == t and left != eye(4), 'nonreciprocal escape fixture')
    dirty_target = blocks([tensor(1),eye(2)])
    V.require(tr(mm(dirty_target,dirty_target)) == (Q(2),Q(0)) and tr(mm(a,a)) == ZERO, 'dirty square-trace control')
    V.require(eigenspace_counts(blocks([tensor(2),tensor(2,-1)])) != V.child(3,1), 'mixed even control')
    return {'schema_version': 1, 'native_matrix_entries': native_entries, 'native_tensor_range': [1,5],
            'native_directions': [-1,1], 'native_digest': digest.hexdigest(),
            'mixed_full_space_witnesses': witnesses,
            'nonmonomial_basis_correction_ranks_by_phase': correction_ranks,
            'nonreciprocal_left_adapter': serialize(left),
            'controls': {'wrong_phase': 3, 'nonreciprocal_escape': True, 'restored_dirty_square_trace': True,
                         'mixed_even_rejected': True, 'nonmonomial_rank_defects_checked': 4}}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write', action='store_true')
    args = ap.parse_args()
    cert = make_certificate()
    path = V.PKG / 'DENSE.json'
    if args.write:
        path.write_text(readable_json(cert)+'\n',encoding='utf-8',newline='\n')
    else:
        V.require(V.canonical(V.read_json(path)) == V.canonical(cert), 'dense certificate mismatch')
    print('PASS_DENSE_RECIPROCAL_BASIS native_entries=' + str(cert['native_matrix_entries'])
          + ' mixed_witnesses=3 arbitrary_basis_defects=4 no_new_kappa')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, OSError, TypeError) as error:
        raise SystemExit('FAIL: '+str(error))
