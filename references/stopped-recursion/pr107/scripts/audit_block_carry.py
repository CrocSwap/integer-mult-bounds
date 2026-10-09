#!/usr/bin/env python3
"""Exact deferred-scatter block schedule and a scoped rank-cost rejection.

The scalar schedule uses no new roles. Its coordinate-subspace carry fails
with retained column central frames, even allowing general cleanup matrices.
This is not a lower bound on arbitrary block fusion.
"""
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations
from math import comb
from pathlib import Path
import json

from certify import require,verify_sources
from paired_network import circuit
from prepare_layers import serializable
from rational_span_frames import basis,dot,nondegenerate,orthogonal

ROOT=Path(__file__).resolve().parents[1]
SCHEDULE=('L','J','Li','R','V','G','R','L','J','Li','G','V')


def block_program(h,columns,rows,delayed=True,omit=None):
    """Primitive XOR program; column a and row b address cell (a,b)."""
    code=circuit(h).program();triples=code['triples'];v=len(triples);R=code['roles']
    columns=tuple(sorted(columns));rows=tuple(sorted(rows))
    require(len(set(columns))==len(columns) and len(set(rows))==len(rows),'Duplicate invocation')
    require(set(columns)<=set(range(v)) and set(rows)<=set(range(v)),'Invalid invocation index')
    size=2*v*v;row_aux={};col_aux={};ops=[]
    for table,indices in ((row_aux,rows),(col_aux,columns)):
        for index in indices:
            table[index]=(list(range(size,size+R)),list(range(size+R,size+R+h)))
            size+=R+h
    def data(b=None,a=None,bank=0):
        return [bank*v*v+i*v+b for i in range(v)] if b is not None else [bank*v*v+a*v+j for j in range(v)]
    def emit(op,x,y,scratch,center,selected=None):
        selected=range(v) if selected is None else selected
        if op in ('L','Li'):
            gates=code['gates'] if op=='L' else reversed(code['gates'])
            for ins,outs in gates:
                local=[(scratch[ins[0]],scratch[s]) for s in ins[1:]]
                local += [(scratch[s],scratch[ins[0]]) for s in outs[1:]]
                ops.extend(local if op=='L' else reversed(local))
        elif op=='V':ops.extend((scratch[s],x[t]) for t,s in code['sources'])
        elif op=='J':ops.extend((y[t],scratch[s]) for t,s in code['outputs'])
        elif op=='R':ops.extend((y[t],center[i]) for t in selected for i in triples[t])
        elif op=='G':ops.extend((center[i],x[t]) for t in selected for i in triples[t])
        else:raise ValueError(op)
    selected_columns=set(columns)
    outside=tuple(t for t in range(v) if t not in selected_columns)
    for b in rows:
        x,y=data(b=b),data(b=b,bank=1);scratch,center=row_aux[b]
        if not delayed:
            for op in SCHEDULE:emit(op,x,y,scratch,center)
        else:
            for op in ('L','J','Li','R','V','G'):emit(op,x,y,scratch,center)
            emit('R',x,y,scratch,center,outside)
            # Side cleanup commutes with the deferred central scatter and
            # the final central gather while the source X is unchanged.
            for op in ('L','J','Li','V'):emit(op,x,y,scratch,center)
    for a in columns:
        x,y=data(a=a,bank=1),data(a=a);scratch,center=col_aux[a]
        inverse=[{'L':'Li','Li':'L'}.get(op,op) for op in reversed(SCHEDULE)]
        for op in inverse:emit(op,x,y,scratch,center)
    if delayed:
        for b in rows:
            x,y=data(b=b),data(b=b,bank=1);scratch,center=row_aux[b]
            if omit!='compensating_scatter':emit('R',y,x,scratch,center,columns)
            emit('R',x,y,scratch,center,columns)
            emit('G',x,y,scratch,center)
            if omit!='restoration_correction':emit('G',y,x,scratch,center,columns)
    return dict(h=h,v=v,R=R,roles=size,columns=columns,rows=rows,
                operations=ops,row_aux=row_aux,col_aux=col_aux)


def execute(program,values,inverse=False):
    values=list(values)
    ops=reversed(program['operations']) if inverse else program['operations']
    for target,source in ops:values[target]^=values[source]
    return values


def scalar_check(h,columns,rows):
    new=block_program(h,columns,rows);old=block_program(h,columns,rows,False)
    require(new['roles']==old['roles'],'Unexpected scratch allocation')
    initial=[1<<i for i in range(new['roles'])];v=new['v']
    expected=list(initial)
    for b in new['rows']:
        for a in range(v):expected[v*v+a*v+b]^=expected[a*v+b]
    for a in new['columns']:
        for b in range(v):expected[a*v+b]^=expected[v*v+a*v+b]
    actual=execute(new,initial)
    require(actual==expected==execute(old,initial),'Incorrect block map or dirty scratch restoration')
    require(execute(new,actual,True)==initial,'Inverse block failed')
    extra=len(new['operations'])-len(old['operations'])
    require(extra==6*len(columns)*len(rows),'Wrong compensation count')
    encoded=json.dumps(new['operations'],separators=(',',':')).encode()
    return dict(h=h,row_invocations=len(rows),column_invocations=len(columns),
                independent_variables=new['roles'],baseline_xors=len(old['operations']),
                deferred_xors=len(new['operations']),extra_xors=extra,
                additional_roles=0,full_map_and_dirty_restoration_exact=True,
                inverse_exact=True,program_sha256=sha256(encoded).hexdigest())


def coordinate_geometry(h,k):
    require(h>=6 and h!=9 and 1<=k<=h,'Invalid geometry')
    outside=tuple(tuple(int(i==j) for i in range(h)) for j in range(k,h))
    U=orthogonal(outside,h)
    require(len(U)==k,'Wrong retained dimension')
    vectors=[tuple(int(i in t) for i in range(h)) for t in combinations(range(h),3)]
    touched=sum(any(dot(u,t) for u in U) for t in vectors)
    require(touched==comb(h,3)-comb(h-k,3),'Wrong deferred family')
    return dict(h=h,k=k,retained_dimension=len(U),deferred_targets=touched,
                nondegenerate=nondegenerate(U))


def rank_screen(h,k,rows=1):
    require(h>=6 and h!=9 and 1<=k<=h and rows>=1,'Invalid screen')
    v=comb(h,3);q=v-comb(h-k,3)
    # With at most three points left, the outside triples need not span
    # their coordinate space. Credit the entire return for free instead.
    saving=h*h if h-k<4 else k*h+(h-k)*k
    return dict(h=h,k=k,row_invocations=rows,deferred_columns=q,
                optimistic_saved_decreasing_dimensions=rows*saving,
                maximum_return_rank_saving=2*rows*saving,
                late_Y_rank_charge_lower_bound=2*rows*q,
                net_rank_increase_lower_bound=2*rows*(q-saving),
                coordinate_candidate_excluded=q>saving,
                flexible_cleanup_charge_lower_bound=rows*q,
                flexible_cleanup_net_increase_lower_bound=rows*(q-2*saving),
                flexible_cleanup_excluded=q>2*saving,
                scope='Coordinate-complement carry retained at late readout, unchanged column central frames and outer Y cuts. Canonical readout cuts give two rank units per target; arbitrary cleanup/readout matrices containing the carry give at least one. Other new costs are credited as zero.')


def certificate():
    controls=[]
    for h,k,r in ((6,1,1),(6,1,3),(6,2,2),(6,6,2),(8,1,1)):
        triples=list(combinations(range(h),3))
        columns=[a for a,t in enumerate(triples) if any(i<k for i in t)]
        controls.append(scalar_check(h,columns,list(range(r))))
    # Include non-geometric and empty selections to isolate scalar correctness
    # from any proposed rational frame construction.
    controls += [scalar_check(6,[0,3,7],[1,4]),scalar_check(6,[],[0,1]),
                 scalar_check(6,[0,1],[])]
    geometries=[coordinate_geometry(h,k) for h,k in ((6,1),(8,2),(10,1),(10,2),(50,1),(50,5))]
    screens=[rank_screen(50,k) for k in (1,5,10,25,40,48,49,50)]
    require(all(r['flexible_cleanup_excluded'] for r in screens),'Unexpected viable coordinate screen')
    proofs=['scripts/audit_block_carry.py','docs/research/block-carry-audit.md']
    return dict(status='EXACT BLOCK CARRY SCHEDULE; RETAINED COLUMN RETURNS DEFEAT CARRY READOUT; NO NEW KAPPA',
                upstream_commit=verify_sources(),scalar_controls=controls,
                rational_geometry_controls=geometries,full_size_screens=screens,
                full_frame_certificate_supplied=False,
                source_sha256={p:sha256((ROOT/p).read_bytes()).hexdigest() for p in proofs},
                decision='Retain the scalar schedule, but reject the coordinate-carry realization even with arbitrary cleanup matrices when column central frames are retained. A viable continuation must also redesign column returns or change the carried representation/topology.')


if __name__=='__main__':
    result=certificate()
    (ROOT/'certificates/block-carry-audit.json').write_text(
        json.dumps(serializable(result),indent=2,sort_keys=True)+'\n')
    print('PASS exact delayed block scatter and dirty restoration; retained column returns defeat the rank saving.')
