"""Check the first paired BIT reflection and a normalized bank-volume bound."""

import argparse
from collections import Counter
from fractions import Fraction as Q
from functools import cache
import gzip
from hashlib import sha256
from itertools import product
import json
from pathlib import Path

PINS = {
    'bit/retained/inputs/BIT-NATIVE-WORD.json.gz': '51203e7fc75ba10bd3ac3f8e675759f47e13d262bea66b6600d1e515095cad78',
}


def read(path, key):
    raw = path.read_bytes()
    if sha256(raw).hexdigest() != PINS[key]:
        raise ValueError(f'SHA-256 mismatch: {key}')
    return raw


def dot(a,b):
    return sum(x*y for x,y in zip(a,b,strict=True))


def act(matrix, vector):
    return tuple(dot(row,vector) for row in matrix)


def reflection(d):
    norm = dot(d,d)
    return tuple(tuple(Q(i==j)-Q(2)*x*y/norm for j,y in enumerate(d)) for i,x in enumerate(d))


def encode(matrix):
    return [[str(x) for x in row] for row in matrix]


def echelon(vectors):
    basis = {}
    for vector in vectors:
        row = tuple(map(Q, vector))
        for pivot, prior in sorted(basis.items()):
            row = tuple(x-row[pivot]*y for x,y in zip(row,prior,strict=True))
        first = next((i for i,x in enumerate(row) if x), None)
        if first is not None:
            pivot = row[first]
            basis[first] = tuple(x/pivot for x in row)
    for pivot in sorted(basis,reverse=True):
        for earlier in sorted(p for p in basis if p < pivot):
            row = basis[earlier]
            basis[earlier] = tuple(x-row[pivot]*y for x,y in zip(row,basis[pivot],strict=True))
    return basis


def line_kernel(vectors):
    basis = echelon(vectors)
    col, = set(range(8))-basis.keys()
    vector = [Q(0)]*8
    vector[col] = Q(1)
    for p,row in basis.items():
        vector[p] = -row[col]
    return tuple(vector)


def span(vectors):
    return tuple(row for _,row in sorted(echelon(vectors).items()))


def cover_control(d, u):
    def dot(x, y):
        return sum(a * b for a, b in zip(x, y, strict=True))

    cosine = Q(dot(d, u), dot(d, d))
    assert dot(d, d) == dot(u, u) and abs(cosine) == Q(1, 2)
    reflections = ((-1, int(-2 * cosine), 0, 1), (1, 0, int(-2 * cosine), -1))
    swap = (0, 1, 1, 0)
    q = 5

    def matmul(a, b):
        return tuple(sum(a[2 * i + k] * b[2 * k + j] for k in range(2)) % q
                     for i, j in product(range(2), repeat=2))

    def inverse(a):
        aa, ab, ba, bb = a
        factor = pow((aa * bb - ab * ba) % q, -1, q)
        return tuple(factor * x % q for x in (bb, -ab, -ba, aa))

    def apply(a, x):
        return tuple(sum(a[2 * i + j] * x[j] for j in range(2)) % q for i in range(2))

    rows = [a for a in product(range(q), repeat=4) if (a[0] * a[3] - a[1] * a[2]) % q]
    addresses = list(product(range(q), repeat=2))
    routed = {g: matmul(g, swap) for g in rows}
    assert set(routed.values()) == set(rows) and all(routed[g] != g for g in rows)
    assert matmul(swap, matmul(reflections[0], swap)) == tuple(x % q for x in reflections[1])
    targets = {}
    changed_by_matcher = 0
    for g in rows:
        matrices = [matmul(g, matmul(r, inverse(g))) for r in reflections]
        gs = routed[g]
        assert matmul(gs, matmul(reflections[0], inverse(gs))) == matrices[1]
        for address in addresses:
            changed_by_matcher += apply(matrices[0], address) != apply(matrices[1], address)
            for role, matrix in enumerate(matrices):
                targets[role, g, address] = role, g, apply(matrix, address)
    assert all(targets[target] == key for key, target in targets.items())

    lower = [key for key, target in targets.items() if key[-1] < target[-1]]
    lower.sort(key=lambda key: key[-1])
    upper_column = {targets[key]: i for i, key in enumerate(lower)}
    assert len(lower) == len(upper_column) == 2 * len(rows) * (q * q - q) // 2

    # The no-child control routes just role zero and mixes role one into it
    # at the matched row, always keeping the entire ambient address intact.
    below_diagonal = 0
    for row, key in enumerate(lower):
        role, g, z = key
        source_rows = ((0, routed[g], z), (1, g, z)) if role == 0 else (key,)
        for source in source_rows:
            column = upper_column.get(source)
            if column is not None:
                assert column < row
                below_diagonal += 1
        assert upper_column[targets[key]] == row
    assert below_diagonal and changed_by_matcher

    # Allowing a true address permutation in H changes every minor pivot.
    cancelled_by_physical_route = sum(upper_column[targets[key]] == i for i, key in enumerate(lower))
    assert cancelled_by_physical_route == len(lower)
    return {"address_prime": q, "cover_rows": len(rows), "difference_addresses_per_row": len(addresses),
            "input_slots": len(targets), "changed_conjugated_addresses": changed_by_matcher,
            "triangular_minor_dimension": len(lower), "nonzero_strictly_lower_control_entries": below_diagonal,
            "minor_pivots_cancelled_by_address_changing_control": cancelled_by_physical_route}


def main(bit):
    native = 'retained/inputs/BIT-NATIVE-WORD.json.gz'
    w = json.loads(gzip.decompress(read(bit / native, 'bit/'+native)))
    matrix = reflection((0,1,0,-1,1,0,1,0))
    frames = {int(key):value for key,value in w['frames'].items()}
    spaces = {f:span(v['B']) for f,v in frames.items()}
    heads = [spaces[f] for f in w['start'][:111]]
    assert len(heads)==len(set(heads))==111
    for i,head in enumerate(heads):
        j = heads.index(span(act(matrix,v) for v in head))
        body = spaces[w['final'][111+i]]
        assert span(act(matrix,v) for v in body)==spaces[w['final'][111+j]]

    @cache
    def complements(source,target):
        a,b = sorted((source,target),key=lambda f:frames[f]['dim'])
        direction = line_kernel(tuple(frames[b]['A'])+spaces[a])
        rotated = act(matrix,direction)
        return direction,rotated,span(act(matrix,v) for v in spaces[source])==spaces[source]

    first = {}
    counts = Counter()
    total_rank_one = 0
    for i,(op,role,*args) in enumerate(w['program']):
        if op != 'MOVE':
            continue
        source,target = args
        if abs(frames[source]['dim']-frames[target]['dim']) != 1:
            continue
        total_rank_one += 1
        a,b,same_source = complements(source,target)
        if len(span((a,b))) != 2:
            continue
        assert dot(a,a)==dot(b,b) and 2*abs(dot(a,b))==dot(a,a)
        key = 'common_source' if same_source else 'changed_source'
        counts[key] += 1
        first.setdefault(key,(i,role,source,target,a,b))
    assert counts=={'common_source':264, 'changed_source':396}
    assert total_rank_one==1386
    assert first['common_source'][:4]==(19152,0,2,125)

    i,role,source,target,d,u = first['common_source']
    a,b = reflection(d),reflection(u)
    cosine = dot(d,u)/dot(d,d)
    ab_plane = (((Q(-1),-2*cosine),(Q(0),Q(1))), ((Q(1),Q(0)),(-2*cosine,Q(-1))))
    for ambient, plane in zip((a,b),ab_plane,strict=True):
        for j, axis in enumerate((d,u)):
            assert act(ambient,axis)==tuple(plane[0][j]*x+plane[1][j]*y for x,y in zip(d,u,strict=True))
        defect = [tuple(x-Q(i==j) for j,x in enumerate(row)) for i,row in enumerate(ambient)]
        assert len(span(defect))==1
    assert act(a,act(b,d))!=act(b,act(a,d))

    def mod(v,q):
        return (v.numerator*pow(v.denominator,-1,q))%q

    def perm(map_, points, q):
        return [tuple(mod(v,q) for v in act(map_,p)) for p in points]

    controls = []
    for q in (5,7,11):
        points = list(product(range(q),repeat=2))
        index = {point:j for j,point in enumerate(points)}
        involutions = (*ab_plane, ((Q(-1),Q(0)),(Q(0),Q(-1))))
        permutations = [[index[y] for y in perm(m,points,q)] for m in involutions]
        rank = []
        for permutation in permutations:
            assert all(permutation[permutation[j]]==j for j in range(q*q))
            rank.append(sum(j<k for j,k in enumerate(permutation)))
        assert rank==[q*(q-1)//2,q*(q-1)//2,(q*q-1)//2]
        assert 2*rank[0] > rank[-1]
        assert 4*Q(q,q+1)**2 > 2
        for permutation, defect in zip(permutations,rank,strict=True):
            reflected = {x:points[permutation[j]] for j,x in enumerate(points)}
            half = pow(2,-1,q)
            projector = {x:tuple(half*(a-b)%q for a,b in zip(x,y,strict=True))
                         for x,y in reflected.items()}
            fixed = 0
            for x,y in product(points,repeat=2):
                difference = tuple((a-b)%q for a,b in zip(x,y,strict=True))
                p = projector[difference]
                out_left = tuple((a-b)%q for a,b in zip(x,p,strict=True))
                out_right = tuple((a+b)%q for a,b in zip(y,p,strict=True))
                assert tuple((a-b)%q for a,b in zip(out_left,out_right,strict=True))==reflected[difference]
                assert tuple((a+b)%q for a,b in zip(out_left,out_right,strict=True))==tuple(
                    (a+b)%q for a,b in zip(x,y,strict=True))
                fixed += out_left==x and out_right==y
            assert fixed==q*q*(q*q-2*defect)
        controls.append({'address_prime':q,'operand_plane_volume':q*q,'rank_minus_identity':rank,
                         'split_address_cases':3*q**4,
                         'minimum_bank_volume_ratio':str(Q(2*q,q+1))})

    # Replacing the second true operand by an identity field erases its
    # defect and invalidates the two-field obstruction.
    assert all(x['rank_minus_identity'][0] <= x['rank_minus_identity'][-1] for x in controls)
    for side in (3,5,7,11):
        for rank in range(2,9):
            assert rank*(1-Q(1,side))**2>(1-Q(1,side**rank))**2
    return {'status':'EXCLUDED_NORMALIZED_PAID_REFLECTION_PACKING',
            'pins':PINS, 'fixed_target':'10018846261809/2500000000000000',
            'checked_port_pairs':111,'native_rank_one_sites':total_rank_one,
            'independent_rank_one_pairs':dict(counts),
            'first_cases':{k:{'event':v[0],'role':v[1],'source':v[2],'target':v[3],
                              'directions':encode(v[4:])} for k,v in first.items()},
            'first_original_address':encode(a),'first_rotated_address':encode(b),
            'first_changed_source_addresses':[encode(reflection(direction)) for direction in first['changed_source'][4:]],
            'first_plane_addresses':[encode(m) for m in ab_plane],
            'common_plane_full_reflection':encode(((Q(-1),Q(0)),(Q(0),Q(-1)))),
            'finite_controls':controls,'finite_efficiency_controls':28,
            'cover_route_minor_control':cover_control(*first['changed_source'][4:])}


if __name__ == '__main__':
    if not __debug__:
        raise SystemExit('Use CPython 3.12 with assertions enabled')
    parser = argparse.ArgumentParser(description=__doc__)
    default = Path(__file__).resolve().parents[1] / 'paired-query-only-bit'
    parser.add_argument('--bit-package',type=Path,default=default)
    args=parser.parse_args()
    result = json.dumps(main(args.bit_package),indent=2,sort_keys=True)+'\n'
    receipt = Path(__file__).with_name('REFLECTION.json')
    if args.bit_package==default and result!=receipt.read_text():
        raise ValueError('Frozen reflection receipt differs')
    if args.bit_package==default:
        print('PASS_BIT_REFLECTION_DEFECT_BOUND')
    else:
        print(result,end='')
