"""Bound rational sizes in the retained complete inverse-circuit verifier.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
The compiler, basis search and certificate checker retain their source credit.
"""
from collections import deque
from fractions import Fraction
from pathlib import Path
import sys
import re

sys.path.insert(0,str(Path(__file__).resolve().parent/'vendor'))
from algebra import compile_program, produce, ReachableBasis, row_times
from check_certificate import reconstruct, check
from syntax import validate


def need(value,message):
    if not value:raise ValueError(message)


def height(value):
    value=Fraction(value)
    return max(abs(value.numerator).bit_length(),value.denominator.bit_length())


def parameters(program):
    # Check the representation before the source parser expands a decimal exponent.
    for side in ('left','right'):
        for ins in program[side]:
            scalars=([c for name,c in ins['terms']] if ins['op']=='linear'
                     else [ins['coefficient']] if ins['op']=='query' else [])
            for scalar in scalars:
                need(type(scalar) is int or (type(scalar) is str and
                     re.fullmatch(r'[+-]?[0-9]+(?:/[0-9]+)?',scalar) is not None),
                     'explicit integer or fraction scalar required')
    f=validate(program)
    need(not f.characteristic,'rational field required')
    r=len(program['roles']);s=len(program['operators'])
    instructions=program['left']+program['right'];m=len(instructions)
    d=r+sum(ins['op']!='linear' for ins in instructions)
    denominator=1;gain=1;terms=0;longest=0;input_bits=0;input_height=1
    for ins in instructions:
        scalars=([c for name,c in ins['terms']] if ins['op']=='linear'
                 else [ins['coefficient']] if ins['op']=='query' else [])
        values=[f.parse(c) for c in scalars]
        terms+=len(values);longest=max(longest,len(values))
        for scalar,value in zip(scalars,values):
            numerator,divisor=(scalar,1) if type(scalar) is int else (int(scalar.split('/')[0]),int(scalar.split('/')[1]) if '/' in scalar else 1)
            denominator*=value.denominator
            input_bits+=abs(numerator).bit_length()+divisor.bit_length()
            input_height=max(input_height,abs(numerator).bit_length(),divisor.bit_length())
        if ins['op']=='linear':gain*=max(1,sum(abs(c.numerator) for c in values))
        elif ins['op']=='query':gain*=1+abs(values[0].numerator)
    db=d.bit_length();qb=denominator.bit_length();gb=gain.bit_length()
    # R=Q^D, K=(1+D G)^D, M=2 D G K R, N=D^D M^(D+1).
    model_bits=1+db+gb+d*(1+db+gb)+d*qb
    path_bits=d*db+(d+1)*model_bits+1
    minor_bits=d*(db+path_bits)+1
    coefficient_bits=(d+1)*db+(d+2)*model_bits+1
    longest=max(2,d,longest)
    temporary_bits=8*(longest+d+1)*(input_height+model_bits+path_bits+minor_bits+1)
    return dict(states=d,roles=r,operators=s,instructions=m,scalar_terms=terms,
                explicit_scalar_bits=input_bits,input_height=input_height,
                denominator_bits=qb,gain_bits=gb,model_denominator_power=d,
                model_bits=model_bits,path_bits=path_bits,minor_bits=minor_bits,
                coefficient_bits=coefficient_bits,temporary_bits=temporary_bits,
                field_operations_bound=256*(m+terms+r+s+1)*(d+1)**4),denominator,gain


def bounds(program):
    return parameters(program)[0]


def check_size(limits,certificate):
    """Check the produced-certificate size contract; not its algebraic truth."""
    d=limits['states']
    if certificate['verdict']=='different':
        need(len(certificate['word'])<d,'word exceeds size contract')
        values=[certificate['coefficient']];cap=limits['coefficient_bits']
    else:
        need(certificate['verdict']=='equal','unknown certificate verdict')
        need(len(certificate['paths'])<=d and all(len(p['word'])<d for p in certificate['paths']),
             'basis paths exceed size contract')
        values=[x for row in certificate['initial'] for x in row]
        values += [x for matrix in certificate['closure'].values() for row in matrix for x in row]
        need(len(values)<=limits['roles']*d+limits['operators']*d*d,'coordinate count exceeds size contract')
        cap=limits['minor_bits']
    maximum=max((height(x) for x in values),default=1)
    need(maximum<=cap,'certificate rational height exceeds bound')
    return maximum


def audit(program):
    """Inspect a full reachable basis, then check the unchanged producer output."""
    limits,denominator,gain=parameters(program);d=limits['states']
    model=compile_program(program);f=model['field'];u,t,v=model['U'],model['T'],model['V']
    _,iu,it,iv=reconstruct(program)
    need((u,t,v)==(iu,it,iv),'independent compilers disagree')
    measured={name:1 for name in ('model','path','residual','echelon','coordinate','projection')}

    def observe(values,kind,cap,power=None):
        for x in values:
            need(height(x)<=cap,kind+' rational height exceeds bound')
            measured[kind]=max(measured[kind],height(x))
            if power is not None:
                need(pow(denominator,power,Fraction(x).denominator)==0,kind+' common denominator fails')

    for matrix in [u,v,*t.values()]:
        observe((x for row in matrix for x in row),'model',limits['model_bits'],d)
    basis=ReachableBasis(f);queue=deque();paths=[];candidates=0

    def insert(row,depth):
        nonlocal candidates
        candidates+=1
        need(depth<=d,'candidate depth exceeds state bound')
        observe(row,'path',limits['path_bits'],d*(depth+1))
        residual,removed=basis.reduce(row)
        if basis.rows:
            removed_row=row_times(removed,basis.rows,f)
            need([f.add(x,y) for x,y in zip(residual,removed_row)]==row,'elimination residual decomposition')
        observe(residual,'residual',limits['path_bits']+limits['minor_bits'])
        observe(removed,'coordinate',limits['minor_bits'])
        if basis.append(row):
            need(depth<d,'accepted path exceeds state bound')
            paths.append(depth);queue.append((row,depth))
            _,normalized,coordinates=basis.echelon[-1]
            need(row_times(coordinates,basis.rows,f)==normalized,'echelon coordinate reconstruction')
            observe(normalized,'echelon',limits['minor_bits'])
            observe(coordinates,'coordinate',limits['minor_bits'])

    for row in u:insert(row,0)
    while queue:
        row,depth=queue.popleft()
        observe(row_times(row,v,f),'projection',limits['coefficient_bits'])
        for matrix in t.values():insert(row_times(row,matrix,f),depth+1)
    for row in u:
        observe(basis.coordinates(row),'coordinate',limits['minor_bits'])
    for row in basis.rows:
        for matrix in t.values():
            observe(basis.coordinates(row_times(row,matrix,f)),'coordinate',limits['minor_bits'])
    certificate=produce(program)
    certificate_height=check_size(limits,certificate)
    checked=check(program,certificate)
    need(candidates<=limits['roles']+limits['operators']*d,'candidate count exceeds bound')
    return dict(bounds=limits,observed_bits=measured,certificate_bits=certificate_height,
                certificate=certificate,checked=checked,audited_basis_rows=len(basis.rows),
                candidates=candidates,longest_accepted_path=max(paths,default=0))
