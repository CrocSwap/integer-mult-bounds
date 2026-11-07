# SPDX-License-Identifier: Apache-2.0
"""Exact R/W/unit-move tariffs for the authenticated complex controller.

This is an invoice/checker, not a machine implementation. Sizes used here are
checker observations or proof variables; the runtime continues to use Counts.
All source execution and imports must follow the orchestrator's authentication.
"""
from dataclasses import dataclass


def need(condition, message):
    if not condition:
        raise ValueError(message)


@dataclass(frozen=True)
class Actions:
    reads: int = 0
    writes: int = 0
    moves: int = 0

    def __add__(self, other):
        return Actions(self.reads+other.reads, self.writes+other.writes,
                       self.moves+other.moves)

    def __sub__(self, other):
        return Actions(self.reads-other.reads, self.writes-other.writes,
                       self.moves-other.moves)

    def __mul__(self, count):
        return Actions(self.reads*count, self.writes*count, self.moves*count)

    @property
    def total(self):
        return self.reads+self.writes+self.moves

    def record(self):
        return dict(reads=self.reads, writes=self.writes, moves=self.moves,
                    total=self.total)


def size(n):
    need(type(n) is int and n >= 0, 'nonnegative proof/checker size')
    return n


def rewind(head_offset=0):
    """Offset from body origin, with LEFT immediately before that origin."""
    n=size(head_offset)
    return Actions(n+1, 0, n+2)


def clear(n):
    n=size(n)
    return Actions(2*n+3, n, 2*n+4)


def copy(n, old=0):
    n,old=size(n),size(old)
    return Actions(5*n+2*old+7, n+old, 4*n+2*old+10)


def transfer(n, old=0):
    n,old=size(n),size(old)
    return Actions(5*n+2*old+7, 2*n+old, 4*n+2*old+10)


def origin(marker_absent=False):
    need(type(marker_absent) is bool, 'typed marker state')
    return Actions(2, int(marker_absent), 2)


def erase_marker():
    return Actions(2, 1, 2)


def parking_empty():
    return Actions(3, 0, 2)


def header_read(h):
    h=size(h)
    return Actions(2*h+3, 0, 2*h+4)


def header_write(h):
    h=size(h)
    return Actions(2*h+2, h, 2*h+2)


def park(S,r):
    S,r=size(S),size(r)
    need(r>0,'nonempty finite parked role set')
    return Actions(3*S+3*r+2,5*S+r+1,6*S+5*r+1)


def restore(S,r):
    S,r=size(S),size(r)
    need(r>0,'nonempty finite parked role set')
    return Actions(15*S+5*r+5,13*S+r+1,14*S+7*r+1)


def external_minus_embedded(S,C,r,k=15,marker_debt=0):
    """Matched shared-bundle original-binding call, after prepare_child through reconnection.

    The two controllers share the exact scalar/leaf/monomial engine history.
    Independent closed native engines do not suffice: allocator slot order
    and encoded IDs need a separate equivariance proof before using this bill.

    marker_debt is the number of additional absent child parked/output markers
    at external entry. Under source prepared entry embedded parked markers are
    present. A fresh backend adds slots plus its possible output-marker debt;
    closed reuse leaves parked markers present. The root's constructor and
    terminal disposal are separate, not absorbed by this per-call difference.
    """
    S,C,r,k=size(S),size(C),size(r),size(k)
    need(r>0 and k==15,'source fixed original Machine capsule inventory')
    need(type(marker_debt) is int and marker_debt>=-1,'signed marker potential')
    return Actions(2*C+3*k+3-18*S-10*r,
                   -18*S-2*r-1+marker_debt,
                   2*C+4*k+6-20*S-14*r)


def adoption_credit(n, checked_heads=True):
    """Transfer versus ownership return; finite binding control is separate.

    The implemented candidate checks both LEFT origins, costing R2/M4.
    """
    n=size(n)
    need(type(checked_heads) is bool, "typed head-check choice")
    return Actions(5*n+2,2*n,4*n+2) if checked_heads else Actions(5*n+4,2*n,4*n+6)


def measure(tapes):
    unique={id(t):t for t in tapes}.values()
    totals=[0,0,0]
    for tape in unique:
        for i,key in enumerate(('reads','writes','moves')):
            totals[i]+=getattr(tape.meter,key)
    return Actions(*totals)


def verify_primitives(Tape, Parking, FiniteFields, source_transfer, source_copy,
                      source_origin, source_erase_marker, LEFT, BLANK):
    """Meter actual authenticated operations including empty and nested cases."""
    def loaded(n, offset=0):
        tape=Tape()
        alphabet=(0,1,3,5,6,7,8,9,10,11,12,13)
        for i in range(n):tape.append(alphabet[(i+offset)%len(alphabet)])
        tape.rewind()
        return tape
    cases=0
    for n in (0,1,2,5,17):
        for old in (0,1,3,11):
            for fn,bill in ((source_transfer,transfer),(source_copy,copy)):
                a,b=loaded(n),loaded(old,3)
                before=measure((a,b));fn(a,b);actual=measure((a,b))-before
                need(actual==bill(n,old),'literal preserved/owned transfer tariff')
                cases+=1
        t=loaded(n);before=measure((t,));t.clear()
        need(measure((t,))-before==clear(n),'literal clear tariff');cases+=1
    nested=[]
    for lens in ((0,),(3,),(0,2,5),(1,0,0,2),(13,11,0,7)):
        for prefix in (False,True):
            roles=tuple(loaded(n) for n in lens);p=Parking(roles)
            if prefix:
                p.park()
                for tape,n in zip(roles,lens):
                    for i in range(n):tape.append((i+1)%2)
                    tape.rewind()
            tapes=(*roles,p.stack,p.reverse);before=measure(tapes)
            p.park();middle=measure(tapes);p.restore();after=measure(tapes)
            need(middle-before==park(sum(lens),len(lens)),'literal complex parking tariff')
            need(after-middle==restore(sum(lens),len(lens)),'literal complex restoration tariff')
            if prefix:
                for t in roles:t.clear()
                p.restore()
            nested.append({'lengths':list(lens),'ancestor_prefix':prefix,
                           'park':(middle-before).record(),
                           'restore':(after-middle).record()});cases+=1
    for bounds,values in (((2,),(0,)),((2,17,65536),(1,16,352)),((2,17,65536),(0,0,0))):
        fields=FiniteFields(bounds);h=sum(fields.widths);t=Tape();before=measure((t,))
        fields.write(t,values);middle=measure((t,));got=fields.read(t);after=measure((t,))
        need(got==values and middle-before==header_write(h)
             and after-middle==header_read(h),'literal finite-header tariffs');cases+=1
    for absent in (False,True):
        t=Tape()
        if absent:source_erase_marker(t)
        before=measure((t,));source_origin(t)
        need(measure((t,))-before==origin(absent),'literal origin tariff');cases+=1
    t=loaded(2);t.step(1)
    try:source_origin(t)
    except ValueError:pass
    else:raise ValueError('wrong canonical head was accepted')
    # Restoring a nonempty target and omitting append reads are separated by
    # actual measured cases, including empty calibrations above.
    need(transfer(5,3)!=transfer(5,0),'dirty-target cost control')
    need(park(3,1).reads!=0 and restore(3,1).reads!=0,'loop/append-check cost control')
    return {'status':'PASS_ACTUAL_COMPLEX_PRIMITIVE_TARIFFS','meter_cases':cases,
            'nested_cases':nested,'controls':['wrong canonical head rejected',
             'dirty target costs retained','loop and append reads retained'],
            'scope':'Primitive calibrations; actual reachable child contexts are checked separately.'}
