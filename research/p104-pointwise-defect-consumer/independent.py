#!/usr/bin/env python3
"""Independent exact pointwise-defect census; no construction-package imports."""
from collections import Counter, defaultdict
from itertools import product
import json


def lifted(rank, coordinates):
    values = [tuple(coordinates[2*j:2*j+2]) for j in range(1 << rank)]
    for bit in range(rank):
        for a in range(1 << rank):
            if a & (1 << bit):
                continue
            c = a ^ (1 << bit)
            ar, ai = values[a]
            cr, ci = values[c]
            dr, di = ar-cr, ai-ci
            sr, si = cr+dr//2, ci+di//2
            er, ei = -di, dr
            nr, ni = sr-er//2, si-ei//2
            values[c] = (nr, ni)
            values[a] = (nr+er, ni+ei)
    return tuple(v for pair in values for v in pair)


def ideal_numerator(rank, coordinates):
    # A_rank is the product of the unnormalized Gaussian pair matrices,
    # so no rational arithmetic or imported matrix is needed.
    values = [tuple(coordinates[2*j:2*j+2]) for j in range(1 << rank)]
    for bit in range(rank):
        for a in range(1 << rank):
            if a & (1 << bit):
                continue
            c = a ^ (1 << bit)
            ar, ai = values[a]
            cr, ci = values[c]
            pr, pi = ar+cr, ai+ci
            dr, di = ar-cr, ai-ci
            values[a] = (pr-di, pi+dr)
            values[c] = (pr+di, pi-dr)
    return tuple(v for pair in values for v in pair)


def defect(rank, coordinates):
    return tuple((1 << rank)*v-w for v, w in
                 zip(lifted(rank, coordinates), ideal_numerator(rank, coordinates)))


def inverse_lifted(rank, coordinates):
    values = [tuple(coordinates[2*j:2*j+2]) for j in range(1 << rank)]
    for bit in reversed(range(rank)):
        for a in range(1 << rank):
            if a & (1 << bit):
                continue
            c = a ^ (1 << bit)
            ar, ai = values[a]
            cr, ci = values[c]
            er, ei = ar-cr, ai-ci
            dr, di = ei, -er
            sr, si = cr+er//2, ci+ei//2
            or_, oi = sr-dr//2, si-di//2
            values[c] = (or_, oi)
            values[a] = (or_+dr, oi+di)
    return tuple(v for pair in values for v in pair)


def closed_matrix_numerator(rank, coordinates):
    result = []
    for out in range(1 << rank):
        rr = ii = 0
        for inp in range(1 << rank):
            cr, ci = 1, 0
            for bit in range(rank):
                # Gaussian coefficient is 1+i for equal address bits and
                # 1-i for distinct address bits.
                sign = 1 if ((out ^ inp) & (1 << bit)) == 0 else -1
                cr, ci = cr-sign*ci, ci+sign*cr
            xr, xi = coordinates[2*inp:2*inp+2]
            rr += cr*xr-ci*xi
            ii += cr*xi+ci*xr
        result.extend((rr, ii))
    return tuple(result)


def census(rank):
    q = 1 << (rank//2+1)
    dimension = 1 << (rank+1)
    fibers = defaultdict(list)
    for x in product(range(q), repeat=dimension):
        assert inverse_lifted(rank, lifted(rank, x)) == x
        fibers[defect(rank, x)].append(x)
    counts = Counter(map(len, fibers.values()))
    # A congruence must keep every equal-defect pair equal after translation.
    # Search only unit translations first; candidates are exact integer vectors,
    # never reduced modulo q when computing translated defects.
    witness = None
    for axis in range(dimension):
        translation = tuple(int(j == axis) for j in range(dimension))
        for d, points in fibers.items():
            images = {}
            for x in points:
                shifted = tuple(u+v for u, v in zip(x, translation))
                nd = defect(rank, shifted)
                if images and nd not in images:
                    old_d, old_x = next(iter(images.items()))
                    witness = dict(x=old_x, y=x, translation=translation,
                                   defect=d, defect_x_plus_t=old_d,
                                   defect_y_plus_t=nd)
                    break
                images.setdefault(nd, x)
            if witness:
                break
        if witness:
            break
    return dict(rank=rank, q=q, dimension=dimension, domain_size=q**dimension,
                image_size=len(fibers),
                fiber_size_histogram={str(k):v for k,v in sorted(counts.items())},
                coordinate_ranges=[[min(d[j] for d in fibers), max(d[j] for d in fibers)]
                                   for j in range(dimension)],
                zero_defect_fiber_size=len(fibers[(0,)*dimension]),
                translation_witness=witness)


def local_floor_identity():
    # The pair defect is (h,-h,h,-h), h=q-p,
    # p=dr mod 2, q=di mod 2.
    # This independent formula catches sign/floor conventions on negatives.
    for x in product(range(-3,4), repeat=4):
        h = (x[1]-x[3]) % 2 - (x[0]-x[2]) % 2
        assert defect(1,x) == (h,-h,h,-h)


def controls():
    # Independent closed coefficient oracle on a spanning basis.
    for rank in (1,2):
        dimension = 1 << (rank+1)
        for axis in range(dimension):
            x = tuple(int(j == axis) for j in range(dimension))
            assert ideal_numerator(rank,x) == closed_matrix_numerator(rank,x)
    # Defect equality fails translation stability in every positive rank;
    # this finite check covers ranks 1..6, the written proof covers all ranks.
    for rank in range(1,7):
        repeats = 1 << (rank-1)
        zero = (0,)* (1 << (rank+1))
        y = (0,0,1,1)*repeats
        t = (1,0,0,0)*repeats
        yt = tuple(u+v for u,v in zip(y,t))
        expected = tuple((1 << (rank-1))*v for v in (-1,1,-1,1)*repeats)
        assert defect(rank,zero) == defect(rank,y) == zero
        assert defect(rank,t) == expected
        assert defect(rank,yt) == tuple(-v for v in expected)
    # Negative control: replacing the signed floor by truncation flips this
    # local fixture's nonzero defect.
    signed_fixture = (0,0,1,0)
    assert defect(1,signed_fixture) == (-1,1,-1,1)
    dr, di = -1, 0
    sr, si = 1+int(dr/2), int(di/2)
    er, ei = -di, dr
    nr, ni = sr-int(er/2), si-int(ei/2)
    truncated_output = (nr+er,ni+ei,nr,ni)
    truncated_defect = tuple(2*u-v for u,v in
                             zip(truncated_output, ideal_numerator(1,signed_fixture)))
    assert truncated_defect != defect(1,signed_fixture)
    # Parent-proposed rank-one XOR oracle: signed two-bit D coordinates,
    # arbitrary eight-bit output target, two clean parity ancillas.
    for x in product(range(2), repeat=4):
        encoded = sum((v % 4) << (2*j) for j,v in enumerate(defect(1,x)))
        for target in range(256):
            out = target
            p = q = 0
            p ^= x[0]
            p ^= x[2]
            q ^= x[1]
            q ^= x[3]
            for low in (0,2,4,6):
                out ^= p << low
                out ^= q << low
            q ^= 1
            for high in (1,5):
                out ^= (p & q) << high
            q ^= 1
            p ^= 1
            for high in (3,7):
                out ^= (p & q) << high
            p ^= 1
            p ^= x[2]
            p ^= x[0]
            q ^= x[3]
            q ^= x[1]
            assert (out,p,q) == (target ^ encoded,0,0)
    return {'closed_matrix_basis_checks':12,
            'repeated_translation_witness_ranks':[1,2,3,4,5,6],
            'truncation_negative_control_rejected':True,
            'truncation_fixture_defect':truncated_defect,
            'rank1_xor_oracle_checks':16*256,
            'rank1_xor_oracle_gates':{'CNOT':16,'Toffoli':4,'X':4},
            'raw_lut_n32_toffoli':2*(32-1)*(1 << 32)}


if __name__ == '__main__':
    local_floor_identity()
    check_receipt = controls()
    print(json.dumps({'censuses':[census(1),census(2)],
                      'local_identity_domain':'[-3,3]^4',
                      'local_identity_count':7**4,
                      'inverse_checks':'Every census input, 65552 total',
                      'controls':check_receipt}, indent=2))
