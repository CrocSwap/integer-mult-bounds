"""Exact real and Gaussian quadratic-phase vector families and rank screens.

The central matrix is specifically I plus every orthogonality edge. A failed
screen does not exclude different supported binary matrices or subfamilies.
"""
from bisect import bisect_right
from functools import cache
from hashlib import sha256
from itertools import combinations
from fractions import Fraction as Q

from certify import require
from experiments.single_intersection import rank_of_rows
from audit_joint_frames import matrix,product,rank


def gaussian_binomial(t,k):
    if not 0<=k<=t:return 0
    num=den=1
    for i in range(k):num*=2**(t-i)-1;den*=2**(k-i)-1
    require(num%den==0,'Nonintegral subspace count')
    return num//den


@cache
def subspaces(t):
    require(type(t) is int and 1<=t<=5,'Explicit family budget: t=1,...,5')
    levels=[{1:()}]
    for k in range(t):
        nxt={}
        for mask,basis in sorted(levels[-1].items()):
            elements=[x for x in range(1<<t) if mask>>x&1]
            for v in range(1,1<<t):
                if mask>>v&1:continue
                new=mask|sum(1<<(x^v) for x in elements)
                if new not in nxt:nxt[new]=basis+(v,)
        require(len(nxt)==gaussian_binomial(t,k+1),'Missing or duplicate linear subspaces')
        levels.append(nxt)
    return levels


@cache
def family(t,complex_phases=False,parity=None):
    require(type(complex_phases) is bool and parity in (None,0,1),'Invalid phase family')
    require(not complex_phases or parity is None,'Complex family here uses every support dimension')
    blocks=[];ends=[];n=0;expected=0;counts=[]
    for k,level in enumerate(subspaces(t)):
        if parity is not None and k%2!=parity:continue
        phase_bits=k*(k+1)//2+int(complex_phases)*k
        count=gaussian_binomial(t,k)*2**(t-k)*2**phase_bits
        expected+=count;counts.append(dict(support_dimension=k,labels=count))
        for mask,basis in sorted(level.items()):
            points=[0]
            for b in basis:points+=[x^b for x in points]
            require(len(set(points))==2**k and sum(1<<x for x in points)==mask,'Wrong affine basis')
            covered=0
            for shift in range(1<<t):
                if covered>>shift&1:continue
                positions=[x^shift for x in points];support=sum(1<<x for x in positions)
                require(not support&covered,'Affine cosets overlap');covered|=support
                linear=tuple(sum(1<<pos for x,pos in enumerate(positions) if x>>i&1) for i in range(k))
                quadratic=tuple(sum(1<<pos for x,pos in enumerate(positions) if x>>i&1 and x>>j&1)
                                for i,j in combinations(range(k),2))
                blocks.append((support,linear,quadratic));n+=2**phase_bits;ends.append(n)
            require(covered==(1<<(1<<t))-1,'Affine cosets do not cover the ambient space')
    require(n==expected,'Wrong phase-vector count')
    return dict(t=t,D=1<<t,n=n,ell=2 if complex_phases else 1,
                d=(1<<t)*(2 if complex_phases else 1),complex_phases=complex_phases,
                parity=parity,blocks=blocks,ends=ends,counts=counts)


def vector(f,index):
    require(type(index) is int and 0<=index<f['n'],'Invalid phase-vector index')
    b=bisect_right(f['ends'],index);phase=index-(f['ends'][b-1] if b else 0)
    support,linear,quadratic=f['blocks'][b];lo=hi=0
    if f['complex_phases']:
        for mask in linear:
            c=phase&3;phase>>=2
            if c&1:hi^=lo&mask;lo^=mask
            if c&2:hi^=mask
    else:
        for mask in linear:
            if phase&1:hi^=mask
            phase>>=1
    for mask in quadratic:
        if phase&1:hi^=mask
        phase>>=1
    require(phase==0 and not ((lo|hi)&~support),'Invalid quadratic phase')
    return support,lo,hi


def inner(v,w):
    s,a,b=v;u,c,e=w;common=s&u
    lo=(a^c)&common;hi=(b^e^(a&~c))&common
    return (common^lo).bit_count()-2*(hi&~lo).bit_count(),lo.bit_count()-2*(hi&lo).bit_count()


def block_projector(v,D):
    """Rational rank-two projector onto the realification of a complex line."""
    s,lo,hi=v
    require(type(D) is int and D>=2 and 0<s<1<<D and not ((lo|hi)&~s),'Invalid Gaussian vector')
    real=[];imag=[]
    for j in range(D):
        c=((hi>>j)&1)*2+((lo>>j)&1)
        real.append((1,0,-1,0)[c] if s>>j&1 else 0)
        imag.append((0,1,0,-1)[c] if s>>j&1 else 0)
    U=matrix([[a,-b] for a,b in zip(real,imag)]+[[b,a] for a,b in zip(real,imag)])
    norm=s.bit_count();Ut=matrix(zip(*U))
    require(product(Ut,U)==matrix([[norm,0],[0,norm]]),'Wrong complex-line realification')
    P=tuple(tuple(x/norm for x in row) for row in product(U,Ut))
    require(rank(P)==2 and product(P,P)==P,'Not a rank-two idempotent')
    return P


def _character_masks(vectors,D):
    """Lane-packed column masks: lane j of masks[k][p] holds 2 iff column j
    holds i^k at position p. Lanes sit at bit 8j to match _lane_flags, and
    pre-doubling keeps every lane even so the SWAR zero test stays exact."""
    n=len(vectors)
    lists=[[[] for _ in range(D)] for _ in range(4)]
    for j,(s,lo,hi) in enumerate(vectors):
        x=s
        while x:
            p=x.bit_length()-1;x^=1<<p
            lists[((lo>>p)&1)+2*((hi>>p)&1)][p].append(j)
    masks=[[0]*D for _ in range(4)]
    for k in range(4):
        for p in range(D):
            js=lists[k][p]
            if js:
                buf=bytearray(n)
                for j in js:buf[j]=2
                masks[k][p]=int.from_bytes(buf,'little')
    return masks


def _lane_flags(x,lanes):
    """Exact zero-lane mask for 8-bit lanes holding even values in [0,126].

    Even lanes never underflow on borrow-in, so borrows propagate only
    through zero lanes and the classic SWAR zero test is exact per lane.
    Lanes live at bit 8k, so the byte width is the lane count. Returns
    bit 8k+7 set iff lane k is zero."""
    ones=int.from_bytes(b'\x01'*lanes,'little')
    return (x-ones)&~x&int.from_bytes(b'\x80'*lanes,'little')


_GATHER_CACHE={}


def _gather_lanes(flags,lanes):
    """Compress stride-8 lane flags at bit 8k+7 into bit k of a dense mask.

    Each bit k travels down 7, then down 7*2**i at stage i whenever bit i
    of k is set, for total displacement 7*(k+1). Stage i selects bits by
    bit i+3 of their current position (equal to bit i of their index), and
    distinct indices never collide: within one 2**i block positions differ
    by the index difference, across blocks the 8*(k-k') term dominates."""
    x=flags>>7
    masks=_GATHER_CACHE.get(lanes)
    if masks is None:
        masks=[]
        i=0
        while (1<<i)<=lanes:
            period=1<<(i+1)
            buf=bytearray(period)
            for b in range(1<<i,period):buf[b]=0xff
            masks.append(int.from_bytes((bytes(buf)*((lanes+period-1)//period))[:lanes],'little'))
            i+=1
        _GATHER_CACHE[lanes]=masks
    for i,mask in enumerate(masks):
        x=(x&~mask)|((x&mask)>>(7<<i))
    return x&((1<<lanes)-1)


def _orthogonality_rows(vectors,D,row_indices):
    """Row masks of the orthogonality-plus-diagonal matrix, batched over columns.

    inner(v,w)==(0,0) is the pair sum of per-position products i^(e_v-e_w),
    so each row is accumulated as lane-packed character-mask counts instead
    of one inner call per pair. Lanes hold doubled counts to keep the SWAR
    zero test exact. Differential evidence: research/quadratic-affine-performance.
    """
    n=len(vectors)
    masks=_character_masks(vectors,D)
    rows={}
    for i in row_indices:
        s,lo,hi=vectors[i];pos_r=neg_r=pos_i=neg_i=0
        x=s
        while x:
            p=x.bit_length()-1;x^=1<<p
            ev=((lo>>p)&1)+2*((hi>>p)&1)
            a,b,c,d=(masks[ev][p],masks[(ev+2)&3][p],masks[(ev+3)&3][p],masks[(ev+1)&3][p])
            if a:pos_r+=a
            if b:neg_r+=b
            if c:pos_i+=c
            if d:neg_i+=d
        rows[i]=_gather_lanes(_lane_flags(pos_r^neg_r,n)&_lane_flags(pos_i^neg_i,n),n)|(1<<i)
    return rows


def rank_witness(t,complex_phases,parity,sample,independent_rows):
    f=family(t,complex_phases,parity)
    require(sample and len(set(sample))==len(sample) and all(type(i) is int and 0<=i<f['n'] for i in sample),
            'Sample must contain distinct valid labels')
    require(independent_rows and len(set(independent_rows))==len(independent_rows) and
            all(type(i) is int and 0<=i<len(sample) for i in independent_rows),'Invalid independent row indices')
    vectors=[vector(f,i) for i in sample]
    rows=_orthogonality_rows(vectors,f['D'],independent_rows)
    basis={};digest=sha256();bytewidth=(len(sample)+7)//8
    for i in independent_rows:
        row=rows[i]
        digest.update(row.to_bytes(bytewidth,'little'));x=row
        while x:
            p=x.bit_length()-1
            if p not in basis:basis[p]=x;break
            x^=basis[p]
        require(x!=0,'Claimed rows are linearly dependent')
    r=len(basis);ell=f['ell'];d=f['d'];n=f['n']
    return dict(t=t,complex_phases=complex_phases,parity=parity,n=n,d=d,ell=ell,
                normalized_dimension=Q(d,ell),counts_by_support_dimension=f['counts'],
                minor_columns=len(sample),binary_rank_lower=r,independent_row_sha256=digest.hexdigest(),
                positive_deficit_excluded=n*ell<=6*r*d,
                scope='Only I plus the full orthogonality relation on this exact vector family; no rank upper bound asserted')
