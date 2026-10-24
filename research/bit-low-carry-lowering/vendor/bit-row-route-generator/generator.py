"""Actual frame506 matcher -> executable, owned, completed-primitive schedule.

This emits addressed operations; the named primitive implementations remain
P1/P2 contracts. It is not a lowering of those contracts to physical bit tapes.
"""
from dataclasses import dataclass, asdict
from fractions import Fraction as F
from collections import Counter
from hashlib import sha256
from math import gcd, prod, isqrt
import json


def need(ok, message):
    if not ok: raise ValueError(message)


def inverse(a):
    n=len(a);x=[[F(v) for v in row]+[F(i==j) for j in range(n)] for i,row in enumerate(a)]
    for j in range(n):
        k=next((i for i in range(j,n) if x[i][j]),None)
        need(k is not None,'singular matcher')
        x[j],x[k]=x[k],x[j];v=x[j][j];x[j]=[z/v for z in x[j]]
        for i in range(n):
            if i!=j:
                v=x[i][j];x[i]=[u-v*z for u,z in zip(x[i],x[j])]
    return [row[n:] for row in x]


def factors(s):
    """Elimination inverses in chronological RIGHT-product order."""
    x=[[F(z) for z in row] for row in s];result=[];n=len(s)
    for j in range(n):
        k=next((i for i in range(j,n) if x[i][j]),None)
        need(k is not None,'singular matcher')
        if k!=j:x[j],x[k]=x[k],x[j];result.append(('swap',j,k,F(1)))
        z=x[j][j]
        if z!=1:x[j]=[v/z for v in x[j]];result.append(('scale',j,j,z))
        for i in range(n):
            if i!=j and x[i][j]:
                z=x[i][j];x[i]=[a-z*b for a,b in zip(x[i],x[j])]
                result.append(('add',i,j,z))
    return tuple(result)


@dataclass(frozen=True)
class Step:
    op: str
    addresses: tuple=()
    coefficient: tuple=(0,1)
    direction: int=0


@dataclass(frozen=True)
class Program:
    f: int
    q: int
    w: int
    borrowed_digits: int
    reserve: int
    owners: tuple
    matcher: tuple
    steps: tuple
    ledger: dict

    def export(self):
        result=asdict(self);result['matcher']=[[str(v) for v in row] for row in self.matcher]
        return result


def generate(frame, f, q, w, borrowed_digits=1, reserve=3, owners=(462,461)):
    need(type(f) is int and f>0 and type(w) is int and w>=2,'positive tensor width and w>=2')
    need(type(q) is int and q>=3 and q%2==1,'odd prime radix')
    need(all(q%d for d in range(3,isqrt(q)+1,2)),'prime radix required')
    need(type(borrowed_digits) is int and borrowed_digits>0,'positive borrowed width')
    need(type(reserve) is int and 1<=reserve<=q**borrowed_digits,'available borrowed reserve')
    need(len(owners)==2 and len(set(owners))==2 and owners[0]==462,'distinct physical source owners')
    need(sha256(json.dumps(frame,sort_keys=True,separators=(',',':')).encode()).hexdigest()=='7462680ac7a7cbe7d098900c9b9d45e097db37c529c442ba2f88350e51ea8f67','exact source frame506')
    need(frame['dim']==4 and len(frame['A'])==len(frame['B'])==4,'actual rank-four frame')
    s=tuple(tuple(F(v) for v in row) for row in zip(*(frame['B']+frame['A'])))
    si=inverse(s);fs=factors(s)
    need(Counter(op[0] for op in fs)==Counter(swap=5,scale=5,add=14),'actual frame506 factor census')
    for row in (*s,*si):
        for value in row:need(gcd(value.denominator,q)==1,'nonunit matcher denominator')
    n=8*f;e=w-1;steps=[]
    def emit(op,*addresses,coefficient=F(0),direction=0):
        steps.append(Step(op,tuple(addresses),(coefficient.numerator,coefficient.denominator),direction))
    # Addresses are flattened high-matrix cell indices, with physical owner
    # resolved once at invocation. Low cache has exactly N*N distinct cells.
    emit('outer_enter')
    for direction in (1,-1):
        emit('route_enter',direction=direction)
        emit('cache_allocate')
        for k in range(n*n):emit('cache_copy',k)
        seq=fs if direction==1 else tuple((kind,i,j,(1/z if kind=='scale' else -z if kind=='add' else z)) for kind,i,j,z in reversed(fs))
        for kind,i,j,z in seq:
            for row in range(n):
                for lane in range(f):
                    a=row*n+i*f+lane;b=row*n+j*f+lane
                    if kind=='swap':
                        if 2*borrowed_digits<e:
                            emit('inner_borrow',a,b);emit('row_pad',a,b)
                            for op in ('body_sub','raw_reverse_swap','body_add','raw_reverse_swap','body_rsub'):
                                emit(op,a,b)
                            emit('inner_return',a,b);emit('row_unpad',a,b);emit('older_high_swap',a,b)
                        else:emit('older_full_swap',a,b)
                    elif kind=='scale':emit('unit_scale',a,coefficient=z)
                    else:
                        # A RIGHT elementary E[i,j] adds source column i to j.
                        emit('ordered_shift',b,a,coefficient=z)
        for k in range(n*n):emit('carry_shift',k,direction=direction)
        emit('low_type_commit',direction=direction)
        for k in range(n*n):emit('cache_clear',k)
        emit('cache_release');emit('route_return',direction=direction)
        if direction==1:emit('native_canonical',4*f)
    emit('outer_return')
    counts=dict(sorted(Counter(s.op for s in steps).items()))
    bits=(q**w-1).bit_length();lowbits=(q-1).bit_length()
    ledger=dict(primitive_calls=counts,dimension=n,active_original_owner=owners[0],spectator_original_owner=owners[1],
                inherited_contracts={'raw_reverse_swap':'P1 completed F_body; all exposed ROW and other fields restored',
                'older_full_swap':'P2 older completed ordinary interchange at e=w-1 radix-q digits',
                'older_high_swap':'P2 older completed ordinary interchange at borrowed_digits radix-q digits',
                'unit_scale':'P2 fixed unit scaling over Z/q^(w-1)',
                'ordered_shift':'P2 fixed rational ordered affine shift over Z/q^(w-1)',
                'carry_shift':'P2 low-type-controlled ordered shift over Z/q^(w-1)',
                'native_canonical':'P1 completed canonical rank-4f whole-job; entire ROW restored',
                'low_type_commit':'P2 finite GL_N(F_q) permutation; NOT free address lookup'},
                address_row_words=2*n*n,owned_cache_bits=n*n*lowbits,
                source_frame_sha256='7462680ac7a7cbe7d098900c9b9d45e097db37c529c442ba2f88350e51ea8f67',
                low_type_table_entries_bound=prod(q**n-q**i for i in range(n)),
                borrowed_row_range=q**borrowed_digits,
                padded_row_range=((q**borrowed_digits+reserve-1)//reserve)*reserve,
                body_scalar_adds=(30*n*f*(e-borrowed_digits) if 2*borrowed_digits<e else 0),
                max_live_padding_rows=((((q**borrowed_digits+reserve-1)//reserve)*reserve-q**borrowed_digits) if 2*borrowed_digits<e else 0),
                padding_volume_charge='added ROW ranges times the complete body/spectator fibre; initialization and removal remain charged',
                logical_cell_bits=bits,integer_route_accumulator_bits=(n*(q**w-1)**2).bit_length()+1,
                coefficient_preparation='exact modular inverses; physical preparation time and tape realization remain charged P2 obligations',
                width_contracts={'ordinary_full_digits':e,'ordinary_high_digits':borrowed_digits,'raw_body_digits':max(0,e-borrowed_digits)},
                tape_inventory='active owner + distinct spectator owner + one owned low cache + scoped ROW padding extent; plus inherited primitive tape inventories',
                physical_tape_cost_closed=False,P3_closed=False,primitive_API_admitted=False)
    return Program(f,q,w,borrowed_digits,reserve,tuple(owners),s,tuple(steps),ledger)
