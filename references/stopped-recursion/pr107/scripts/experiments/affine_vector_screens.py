"""Exact finite screens for specified affine inner-product zero patterns.

A rank rejection concerns C=I plus the entire stated relation, not all
binary matrices supported on it and not all subfamilies of these vectors.
"""
from collections import Counter
from functools import cache
from itertools import combinations
from hashlib import sha256

from certify import require
from audit_joint_frames import matrix,rank
from experiments.single_intersection import rank_of_rows
from experiments.cube_core_family import xor_permute


@cache
def golay_code():
    generator=sum(1<<i for i in (11,9,7,6,5,1,0))
    words=[]
    for message in range(4096):
        value=0
        for i in range(12):
            if message>>i&1:value^=generator<<i
        value|=(value.bit_count()%2)<<23
        words.append(value)
    require(len(set(words))==4096,'Codewords repeat')
    require(Counter(x.bit_count() for x in words)=={0:1,8:759,12:2576,16:759,24:1},
            'Wrong extended Golay weight distribution')
    return tuple(words)


@cache
def leech_lines():
    """One explicit integer representative per antipodal minimal-vector pair."""
    out=[]
    for i,j in combinations(range(24),2):
        for sign in (-1,1):
            v=[0]*24;v[i]=4;v[j]=4*sign;out.append(tuple(v))
    require(len(out)==552,'Wrong two-coordinate count')
    for octad in (x for x in golay_code() if x.bit_count()==8):
        support=[i for i in range(24) if octad>>i&1]
        for mask in range(128):
            if mask.bit_count()%2:continue
            v=[0]*24;v[support[0]]=2
            for j,i in enumerate(support[1:]):v[i]=-2 if mask>>j&1 else 2
            out.append(tuple(v))
    require(len(out)==552+48576,'Wrong octad count')
    for i in range(24):
        for word in golay_code():
            if (word&1)!=int(i==0):continue
            v=[-1 if word>>j&1 else 1 for j in range(24)];v[i]*=-3;out.append(tuple(v))
    require(len(out)==len(set(out))==98280,'Wrong number of distinct lines')
    require(all(sum(x*x for x in v)==32 and next(x for x in v if x)>0 for v in out),
            'Wrong norm or antipodal normalization')
    # The two-coordinate vectors alone span all 24 rational coordinates.
    require(rank(matrix([out[i] for i in [0]+list(range(1,46,2))]))==24,
            'Rational ambient rank is not certified')
    return tuple(out)


def leech_minor(global_indices, independent_rows, shift=0, signed=False):
    require(shift in (-16,-8,0,8,16),'Unsupported affine offset')
    require(signed or shift==0,'Shifted cases here use the full signed family')
    lines=leech_lines();size=len(lines);n=size*(2 if signed else 1);d=24+int(shift!=0)
    require(global_indices and len(set(global_indices))==len(global_indices)
            and all(type(i) is int and 0<=i<n for i in global_indices),'Invalid vector indices')
    require(independent_rows and len(set(independent_rows))==len(independent_rows)
            and all(type(i) is int and 0<=i<len(global_indices) for i in independent_rows),
            'Invalid independent rows')
    sample=[lines[i] if i<size else tuple(-x for x in lines[i-size]) for i in global_indices]
    if shift:
        # Augmented vectors (v,1) span dimension 25 using an antipodal pair.
        base=[tuple(v)+(1,) for v in [lines[i] for i in [0]+list(range(1,46,2))]]
        base.append(tuple(-x for x in lines[0])+(1,))
        require(rank(matrix(base))==25,'Affine rational rank failed')
    packed=[];digest=sha256()
    for i in independent_rows:
        sparse=[(a,x) for a,x in enumerate(sample[i]) if x]
        row=sum(1<<j for j,v in enumerate(sample)
                if i==j or sum(x*v[a] for a,x in sparse)==shift)
        packed.append(row);digest.update(row.to_bytes((len(sample)+7)//8,'little'))
    r=rank_of_rows(packed)
    require(r==len(independent_rows),'Claimed independent rows are dependent')
    return dict(n=n,d=d,shift=shift,signed=signed,minor_columns=len(sample),
                binary_rank_lower=r,positive_deficit_excluded=6*r*d>=n,
                independent_rows_sha256=digest.hexdigest(),full_matrix_expanded=False)


def polynomial_code_base(extra):
    """RM(2,5) without constants, enlarged by the listed cubic monomials."""
    require(all(len(S)==3 and tuple(sorted(set(S)))==tuple(S)
                and all(type(i) is int and 0<=i<5 for i in S) for S in extra),
            'Use distinct-coordinate cubic monomials')
    require(len(set(map(tuple,extra)))==len(extra) and len(extra)<=3,'Code discovery size exceeded')
    monomials=[S for degree in (1,2) for S in combinations(range(5),degree)]+list(map(tuple,extra))
    basis=[sum(1<<x for x in range(32) if all(x>>i&1 for i in S)) for S in monomials]
    require(rank_of_rows(basis)==len(basis),'Polynomial code generators are dependent')
    n=1<<len(basis);data=bytearray((n+7)//8);data[0]=1
    value=old=0
    for i in range(1,n):
        gray=i^(i>>1);bit=gray^old;old=gray;value^=basis[bit.bit_length()-1]
        if value.bit_count()==16:data[gray//8]|=1<<(gray%8)
    # Linear polynomials give all 32 real Walsh characters, an orthogonal basis.
    walsh=[[1-2*((a&x).bit_count()%2) for x in range(32)] for a in range(32)]
    require(all(sum(x*y for x,y in zip(u,v))==32*int(i==j)
                for i,u in enumerate(walsh) for j,v in enumerate(walsh)), 'Walsh rank witness failed')
    return dict(n=n,d=32,basis=basis,base=int.from_bytes(data,'little'),
                base_sha256=sha256(data).hexdigest())


def polynomial_code_witness(extra, independent_rows):
    data=polynomial_code_base(extra);n=data['n']
    require(independent_rows and len(set(independent_rows))==len(independent_rows)
            and all(type(i) is int and 0<=i<n for i in independent_rows),'Invalid code row indices')
    rows=[xor_permute(data['base'],i,n) for i in independent_rows]
    r=rank_of_rows(rows);require(r==len(independent_rows),'Code row witness is dependent')
    return dict(extra_monomials=extra,n=n,d=32,binary_rank_lower=r,
                positive_deficit_excluded=6*r*32>=n,base_sha256=data['base_sha256'],
                full_matrix_expanded=False)
