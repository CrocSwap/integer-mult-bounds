"""Whole-period dyadic inverse action; host-array semantics, not tape costs.

JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0.
Reference/geometry: Jose Manuel, Vlado, Jeremy Kothe, Cinna Davis.
"""
from dataclasses import dataclass
from fractions import Fraction as Q
from hashlib import sha256
import json


def need(ok, message):
    if not ok:
        raise ValueError(message)


def up(x, bits=80):
    x=Q(x); s=1<<bits
    return Q(-((-x.numerator*s)//x.denominator),s)


def trunc(n, scale):
    return (-1 if n<0 else 1)*(abs(n)//scale)


def digest(value):
    return sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()


@dataclass(frozen=True)
class Plan:
    reference_hash: str
    rows: tuple
    bits: int
    steps: int
    radius: int
    gap: Q
    error_bound: Q
    state_bound: Q
    source_entries: int
    coefficient_degree: int

    def record(self):
        return dict(reference=self.reference_hash,table_sha256=digest(self.rows),bits=self.bits,
                    steps=self.steps,radius=self.radius,gap=str(self.gap),
                    error_upper=str(up(self.error_bound)),state_upper=str(up(self.state_bound)),
                    rows=len(self.rows),source_entries=self.source_entries,
                    stored_offdiagonal=sum(map(len,self.rows)))


def prepare(reference, target=20, radius=1):
    need(type(target)is int and target>=1 and type(radius)is int and radius>=1,'target/radius')
    reference.require_narrow_gap()
    gap=Q((reference.narrow_gap*(1<<16)).numerator//(reference.narrow_gap*(1<<16)).denominator,1<<16)
    need(0<gap<=1,'positive funded gap')
    q=1-gap; eps=Q(1,1<<target); degree=2*reference.spec.source_halfwidth
    steps=1; tail=radius*q/gap
    while tail>eps/4:
        steps+=1;tail*=q
    bits=target
    while True:
        h=Q(1,1<<bits); R=(radius+2*h)/gap
        numeric=(degree*h*R+2*h)/gap
        if numeric<=eps/4:break
        bits+=1
    scale=1<<bits; rows=[]; count=0
    for row in range(reference.target_size):
        source=reference.source_at.get(row)
        columns=([row] if source is None else
                 [reference.selected[(source+h)%reference.spec.source_size]
                  for h in range(-reference.spec.source_halfwidth,reference.spec.source_halfwidth+1)])
        need(len(columns)==len(set(columns)),'unique periodic support')
        coefficients=[];mass=Q(0)
        for column in columns:
            value=reference.entry('narrow',row,column).value;count+=1
            need(value>=0,'nonnegative source coefficient')
            if column==row:
                need(value==1,'unit diagonal')
            else:
                mass+=value
                numerator=value.numerator*scale//value.denominator
                need(0<=value-Q(numerator,scale)<h,'downward coefficient bound')
                coefficients.append((column,numerator))
        need(mass<=q,'actual source row gap')
        rows.append(tuple(coefficients))
    result=Plan(reference.description_hash,tuple(rows),bits,steps,radius,gap,tail+numeric,R,count,degree)
    need(result.error_bound<=eps/2,'complete funded error')
    return result


def execute(plan, data):
    """Requires an unchanged Plan returned by prepare. Borrow immutable grid input;
    return immutable caller-owned output and bill. Arbitrary constructed Plans
    are not certified by this arithmetic engine."""
    n=len(plan.rows);s=1<<plan.bits
    need(type(data)is tuple and len(data)==n and all(type(z)is tuple and len(z)==2
         and all(type(x)is int for x in z) and abs(z[0])+abs(z[1])<=plan.radius*s
         for z in data),'immutable signed complex input and radius')
    current=list(data);next_state=[(0,0)]*n
    products=0;roundings=0;writes=0;peak=0
    try:
        for _ in range(plan.steps-1):
            for row,coefficients in enumerate(plan.rows):
                real=imag=0
                for column,value in coefficients:
                    real+=value*current[column][0];imag+=value*current[column][1]
                    products+=2
                    peak=max(peak,abs(real).bit_length(),abs(imag).bit_length())
                next_state[row]=(data[row][0]-trunc(real,s),data[row][1]-trunc(imag,s))
                roundings+=2;writes+=2
                need(abs(next_state[row][0])+abs(next_state[row][1])<=plan.state_bound*s,
                     'computed iterate radius')
            current,next_state=next_state,current
        answer=tuple(current)
        # Both work arrays own only references to immutable integer pairs.
        # Clearing their slots never mutates borrowed input or returned pairs.
        return answer,dict(products=products,component_roundings=roundings,
                           component_update_writes=writes,component_accumulator_additions=products,
                           component_input_subtractions=roundings,scratch_initialization_components=4*n,
                           input_components=2*n,
                           scratch_components=4*n,output_components=2*n,
                           scratch_clear_components=4*n,output_copy_components=2*n,
                           peak_accumulator_magnitude_bits=peak,
                           persistent_table_records=sum(map(len,plan.rows)),
                           iterations=plan.steps-1)
    finally:
        for i in range(n):current[i]=next_state[i]=(0,0)
        current.clear();next_state.clear()
