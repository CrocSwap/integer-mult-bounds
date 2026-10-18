#!/usr/bin/env python3
"""Exact core checks and deterministic regeneration. Apache-2.0.

Richard Hoekstra, with substantial OpenAI Codex assistance.
This finite verifier checks the written proof's canonical algebra and literal
attainment, not every complex mixing matrix in the arbitrary-dimension proof.
"""
import argparse
import copy
import hashlib
import itertools
import json
from fractions import Fraction as F
from pathlib import Path

ZERO, ONE = (F(0), F(0)), (F(1), F(0))
ROOTS = (ONE, (F(0), F(1)), (F(-1), F(0)), (F(0), F(-1)))
VECTORS = ((1, 0, 0), (0, 1, 0), (0, 0, 1), (1, -1, 1))
CHECKS = 0


def need(ok, message):
    global CHECKS
    CHECKS += 1
    if not ok:
        raise ValueError(message)


def add(a, b):
    return a[0] + b[0], a[1] + b[1]


def neg(a):
    return -a[0], -a[1]


def sub(a, b):
    return add(a, neg(b))


def mul(a, b):
    return a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0]


def divide(a, b):
    norm = b[0]**2 + b[1]**2
    return (a[0]*b[0]+a[1]*b[1])/norm, (a[1]*b[0]-a[0]*b[1])/norm


def gscalar(x):
    return F(x), F(0)


def parse(z):
    need(type(z) is list and len(z) == 2 and all(type(s) is str for s in z), 'exact Gaussian pair')
    return F(z[0]), F(z[1])


def matrix(encoded):
    return [[parse(z) for z in row] for row in encoded]


def eye(n):
    return [[ONE if i == j else ZERO for j in range(n)] for i in range(n)]


def mv(a, x):
    return [sum_g(mul(z, v) for z, v in zip(row, x)) for row in a]


def sum_g(xs):
    value = ZERO
    for x in xs:
        value = add(value, x)
    return value


def mm(a, b):
    return [[sum_g(mul(x, y) for x, y in zip(row, col)) for col in zip(*b)] for row in a]


def transfer(q, signs):
    after, columns = eye(3), [None] * 4
    for k in range(3, -1, -1):
        g = sub(q if signs[k] == 1 else divide(ONE, q), ONE)
        a = list(map(gscalar, VECTORS[k]))
        columns[k] = [mul(g, z) for z in mv(after, a)]
        reflection = [[add(ONE if i == j else ZERO, mul(g, a[i])) for j in range(3)] for i in range(3)]
        after = mm(after, reflection)
    return [list(row) for row in zip(*columns)], after


def realify(a):
    return [[z[0] for z in row] + [-z[1] for z in row] for row in a] + [
        [z[1] for z in row] + [z[0] for z in row] for row in a]


def rref(rows):
    a, pivots = [list(map(F, row)) for row in rows], []
    if not a:
        return a, pivots
    for col in range(len(a[0])):
        k = next((j for j in range(len(pivots), len(a)) if a[j][col]), None)
        if k is None:
            continue
        i = len(pivots)
        a[i], a[k] = a[k], a[i]
        divisor = a[i][col]
        a[i] = [x / divisor for x in a[i]]
        for j in range(len(a)):
            if j != i and a[j][col]:
                factor = a[j][col]
                a[j] = [x-factor*y for x, y in zip(a[j], a[i])]
        pivots.append(col)
    return a, pivots


def rank(rows):
    return len(rref(rows)[1])


def kernel(rows):
    reduced, pivots = rref(rows)
    vectors = []
    for col in range(len(rows[0])):
        if col not in pivots:
            v = [F(0)] * len(rows[0])
            v[col] = F(1)
            for i, p in enumerate(pivots):
                v[p] = -reduced[i][col]
            vectors.append(v)
    return vectors


def complex_vector(v):
    return list(zip(v[:4], v[4:]))


def word(ops, q):
    a = eye(6)
    for kind, dst, src, c in ops:
        need(type(dst) is int and 0 <= dst < 6, 'literal destination')
        if kind == 'add':
            need(type(src) is int and 0 <= src < 6 and src != dst, 'literal ADD source')
            z = parse(c)
            a[dst] = [add(x, mul(z, y)) for x, y in zip(a[dst], a[src])]
        elif kind == 'phase':
            need(type(c) is int and c in (-1, 1) and src == 0, 'same phase C or inverse')
            z = q if c == 1 else divide(ONE, q)
            a[dst] = [mul(z, x) for x in a[dst]]
        else:
            raise ValueError('unadmitted character-dependent gate')
    return a


def shear(q, count=3):
    a = eye(6)
    for i in range(count):
        a[3+i][i] = sub(q, ONE)
    return a


def closed_transfer(q, signs):
    """Independently derived coefficient formulas in the written proof."""
    t = divide(ONE, q)
    u = sub(ONE, t)
    if signs[0] == 1:
        return [[t,u,neg(u),neg(t)], [ZERO,neg(ONE),u,t], [ZERO,ZERO,t,neg(t)]]
    return [[neg(ONE),u,neg(u),ONE], [ZERO,t,u,neg(ONE)], [ZERO,ZERO,neg(ONE),ONE]]


def joint_check(record):
    signs = record['signs']
    need(signs in ([1,-1,1,-1], [-1,1,-1,1]), 'canonical alternating family')
    h = [closed_transfer(q, signs) for q in ROOTS[1:]]
    for q, closed in zip(ROOTS[1:], h):
        need(closed == [[divide(z, sub(q, ONE)) for z in row] for row in transfer(q, signs)[0]], 'closed formula versus literal product')
    need(len(record['normalized_transfers']) == 3, 'all active values required')
    need([matrix(a) for a in record['normalized_transfers']] == h, 'separate transfer reconstruction')
    constraints = [[sub(x, y) for x, y in zip(row, original)]
                   for later in h[1:] for row, original in zip(later, h[0])]
    need(matrix(record['constraints']) == constraints, 'simultaneous interpolation equations')
    real = realify(constraints)
    independent_kernel = kernel(real)
    native_kernel = [list(map(F, v)) for v in record['real_kernel']]
    need(all(len(v) == 8 for v in native_kernel), 'kernel vector width')
    need(all(not any(sum(x*y for x,y in zip(row,v)) for row in real) for v in native_kernel), 'every native kernel vector satisfies equations')
    need(len(native_kernel) == rank(native_kernel) == len(independent_kernel), 'native kernel complete and independent')
    images = [mv(h[0], complex_vector(v)) for v in native_kernel]
    need([[parse(z) for z in row] for row in record['image_basis']] == images, 'native output image')
    for v in independent_kernel:
        beta = complex_vector(v)
        need(mv(h[0], beta) == mv(h[1], beta) == mv(h[2], beta), 'independent kernel covers every active value')
    real_images = [list(row) for row in zip(*[[z[0] for z in col]+[z[1] for z in col] for col in images])]
    expected_rank, expected_nullity = (1,2) if signs[0] == 1 else (2,3)
    need(rank(real_images) == 2*expected_rank == 2*record['complex_image_rank'], 'complex image rank ceiling')
    need(len(independent_kernel) == 2*expected_nullity == 2*record['complex_nullity'], 'complex kernel dimension')
    need(rank(realify(h[0])) == 6, 'binary specialization permits rank three')
    rows = real + realify(h[0])
    feasible = []
    for target in range(3):
        rhs = [F(0)]*12 + [F(i == target) for i in range(6)]
        feasible.append(int(rank(rows) == rank([row+[b] for row,b in zip(rows,rhs)])))
    need(feasible == record['unit_targets_feasible'], 'unit transfer consistency')
    need(not all(feasible), 'three independent columns cannot all be supplied')
    return dict(signs=signs, complex_image_rank=expected_rank, complex_nullity=expected_nullity,
                unit_targets_feasible=feasible, single_active_value_image_rank=3)


def verify(data):
    need(data['status'] == 'PASS', 'native admission status')
    wanted_signs = {s for s in itertools.product((-1,1), repeat=4) if sum(s) % 4 == 0}
    need(len(data['binary_words']) == 8 and {tuple(r['signs']) for r in data['binary_words']} == wanted_signs, 'complete eight-orientation census')
    for rec in data['binary_words']:
        passes = [int(word(rec['ops'], q) == shear(q)) for q in ROOTS]
        need(passes == rec['root_passes'] == [1,1,0,0], 'binary words reject promotion')
        need(sum(op[0] == 'phase' for op in rec['ops']) == 4, 'four-read binary witness')
    need(len(data['canonical_target_loops']) == 8 and
         {tuple(r['signs']) for r in data['canonical_target_loops']} == wanted_signs, 'complete target-loop census')
    for rec in data['canonical_target_loops']:
        passes = [int(transfer(q, rec['signs'])[1] == eye(3)) for q in ROOTS]
        expected = [1,1,1,1] if rec['signs'] in ([1,-1,1,-1], [-1,1,-1,1]) else [1,0,1,0]
        need(passes == rec['target_root_passes'] == expected, 'canonical target orientation closure')
    need(len(data['joint']) == 2, 'both alternating patterns')
    joint = [joint_check(r) for r in data['joint']]
    need(len({tuple(r['signs']) for r in data['joint']}) == 2, 'distinct alternating patterns')
    need(sum(op[0] == 'phase' for op in data['six_call_ops']) == data['six_call_phase_calls'] == 6, 'complete read invoice')
    need(sum(op[0] == 'add' for op in data['six_call_ops']) == data['six_call_adds'] == 6, 'complete ADD invoice')
    need([int(word(data['six_call_ops'], q) == shear(q)) for q in ROOTS] == data['six_call_root_passes'] == [1]*4, 'six-call full dirty map')
    need(sum(op[0] == 'phase' for op in data['rank_two_ops']) == 4, 'rank-two scope control read count')
    need(all(word(data['rank_two_ops'], q) == shear(q,2) for q in ROOTS), 'rank-two scope control full map')
    return joint



def encode(z):
    return [str(z[0]), str(z[1])]


def encode_matrix(a):
    return [[encode(z) for z in row] for row in a]


def gaussian_solve(a, rhs):
    rows = realify(a)
    b = [z[0] for z in rhs]+[z[1] for z in rhs]
    reduced, pivots = rref([row+[v] for row,v in zip(rows,b)])
    n = len(rows[0])
    need(pivots == list(range(n)), 'unique exact Gaussian solve')
    v = [reduced[i][-1] for i in range(n)]
    half = n//2
    return list(zip(v[:half],v[half:]))


def binary_word(signs):
    q, prefix = ROOTS[1], ONE
    d = []
    for sign in signs:
        z = q if sign == 1 else divide(ONE,q)
        d.append(mul(prefix, sub(z,ONE)))
        prefix = mul(prefix,z)
    vectors = [list(map(gscalar,v)) for v in VECTORS[:3]]
    vectors.append([neg(divide(x,d[3])) for x in d[:3]])
    after, columns = eye(3), [None]*4
    for k in range(3,-1,-1):
        g = sub(q if signs[k]==1 else divide(ONE,q),ONE)
        columns[k] = [mul(g,x) for x in mv(after,vectors[k])]
        after = mm(after,[[add(ONE if i==j else ZERO,mul(g,vectors[k][i])) for j in range(3)] for i in range(3)])
    need(after==eye(3), 'binary old-target restoration')
    a = [list(row) for row in zip(*columns[:3])]
    beta = [[ZERO]*3 for _ in range(4)]
    for j in range(3):
        solved = gaussian_solve(a,[sub(q,ONE) if i==j else ZERO for i in range(3)])
        for k in range(3):
            beta[k][j] = solved[k]
    ops = []
    def emit(dst,src,c):
        if c!=ZERO:
            ops.append(['add',dst,src,encode(c)])
    for k in range(4):
        p = vectors[k].index(ONE)
        encoding = [(3+j,3+p,neg(z)) for j,z in enumerate(vectors[k]) if j!=p and z!=ZERO]
        reads = [(3+p,3+j,ONE) for j in range(3) if j!=p]
        reads += [(3+p,j,z) for j,z in enumerate(beta[k]) if z!=ZERO]
        for op in encoding+reads:
            emit(*op)
        ops.append(['phase',3+p,0,signs[k]])
        for dst,src,c in reversed(reads+[]):
            emit(dst,src,neg(c))
        for dst,src,c in reversed(encoding):
            emit(dst,src,neg(c))
    return ops


def make_joint(signs):
    h = [closed_transfer(q,signs) for q in ROOTS[1:]]
    constraints = [[sub(x,y) for x,y in zip(row,original)] for later in h[1:] for row,original in zip(later,h[0])]
    real = realify(constraints)
    basis = kernel(real)
    images = [mv(h[0],complex_vector(v)) for v in basis]
    real_images = [list(row) for row in zip(*[[z[0] for z in col]+[z[1] for z in col] for col in images])]
    rows = real+realify(h[0])
    feasible = []
    for target in range(3):
        rhs = [F(0)]*12+[F(i==target) for i in range(6)]
        feasible.append(int(rank(rows)==rank([row+[b] for row,b in zip(rows,rhs)])))
    return dict(signs=signs,normalized_transfers=[encode_matrix(a) for a in h],
                constraints=encode_matrix(constraints),real_kernel=[[str(x) for x in v] for v in basis],
                image_basis=[[encode(z) for z in v] for v in images],complex_nullity=len(basis)//2,
                complex_image_rank=rank(real_images)//2,unit_targets_feasible=feasible)


def direct_word(count):
    ops = []
    for i in range(count):
        ops += [['add',3+i,i,encode(neg(ONE))],['phase',i,0,1],
                ['add',3+i,i,encode(ONE)],['phase',i,0,-1]]
    return ops


def generate():
    binary, targets = [], []
    for bits in range(16):
        signs = [1 if bits>>i&1 else -1 for i in range(4)]
        if sum(signs)%4:
            continue
        ops = binary_word(signs)
        binary.append(dict(signs=signs,ops=ops,root_passes=[int(word(ops,q)==shear(q)) for q in ROOTS]))
        targets.append(dict(signs=signs,target_root_passes=[int(transfer(q,signs)[1]==eye(3)) for q in ROOTS]))
    return dict(status='PASS',binary_words=binary,canonical_target_loops=targets,
                joint=[make_joint([1,-1,1,-1]),make_joint([-1,1,-1,1])],six_call_ops=direct_word(3),
                six_call_root_passes=[1]*4,six_call_phase_calls=6,six_call_adds=6,rank_two_ops=direct_word(2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--certificate',type=Path,default=Path(__file__).with_name('CERTIFICATE.json'))
    parser.add_argument('--regenerate',type=Path,help='write a new certificate; refuse an existing output')
    parser.add_argument('--receipt',type=Path,help='write a verification receipt')
    args = parser.parse_args()
    if args.regenerate:
        value = generate()
        verify(value)
        with args.regenerate.open('x') as out:
            out.write(json.dumps(value,indent=2,sort_keys=True)+'\n')
        print('PASS regenerated certificate')
        return
    raw = args.certificate.read_bytes()
    data = json.loads(raw)
    joint = verify(data)
    controls = []
    def refuse(name, alter):
        damaged = copy.deepcopy(data)
        alter(damaged)
        try:
            verify(damaged)
        except (ValueError, KeyError, IndexError, ZeroDivisionError):
            controls.append(name)
        else:
            raise ValueError('accepted corruption: '+name)
    refuse('wrong source restoration inverse', lambda d: d['six_call_ops'][-1].__setitem__(3,1))
    def flip(d):
        next(op for op in d['binary_words'][0]['ops'] if op[0]=='phase')[3] *= -1
    refuse('corrupt binary phase', flip)
    refuse('omit active value', lambda d: d['joint'][0]['normalized_transfers'].pop())
    refuse('forged rank-three image', lambda d: d['joint'][0].update(complex_image_rank=3))
    def kernel_corrupt(d):
        v = d['joint'][0]['real_kernel'][0]
        v[0] = str(F(v[0])+1)
    refuse('corrupt interpolation kernel', kernel_corrupt)
    refuse('unpaid phase call', lambda d: d.update(six_call_phase_calls=5))
    refuse('forged target restoration', lambda d: d['canonical_target_loops'][0]['target_root_passes'].__setitem__(1,1))

    need(data == generate(), 'deterministic certificate regeneration')
    for rec in data['binary_words']:
        additions = [parse(op[3]) for op in rec['ops'] if op[0]=='add']
        need(len(additions)==32, 'binary literal invoice')
        need(sum(2 for z in additions for part in z if part)==76, 'binary real ADD invoice')
        need(all(abs(part)==1 for z in additions for part in z if part), 'unit real coefficients')
    names = ('README.md','PROOF.md','verify.py','CERTIFICATE.json','NOTICE.md')
    source_hashes = {name:hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest() for name in names}
    result = dict(status='PASS',canonical_joint=joint,negative_controls=controls,
                  source_sha256=source_hashes,checks=CHECKS,written_lower_bound=6,attained_calls=6,
                  formal_proof=False,new_kappa=0)
    if args.receipt:
        args.receipt.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('PASS_FOUR_SPECTRUM_SHEAR minimum=6 binary_minimum=4 controls=7 no_new_kappa')


if __name__ == '__main__':
    main()
