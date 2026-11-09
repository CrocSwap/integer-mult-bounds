"""Physically lift, apply the current positive leaf, and round exactly once.

Every runtime integer remains on the unchanged Count/Tape alphabet. The
complete public field is written only after a full rounded result passes
signed range checks. Valid-return named failures are atomic; interruptions
and malformed late output are outside that promise.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from contextlib import ExitStack
from rounded_sources import activate,need

S=activate(); L=S.common.leaf_provider; A=S.common.abi; C=L.S.codec
from cardinal_counts import Count,positive
from compact_counts import power_two
from encoded import compare,divide
from records import Tape
from scratch_pool import ScratchPool
from session import OuterScope
from stream import Counter

class RoundedOverflow(ValueError):
    """The fully rounded mathematical output does not fit the public width."""

def emit(port,value):
    port.write(value);port.move(1)

def at_origin(port):
    port.move(-1);ok=port.read()==A.LEFT;port.move(1)
    need(ok,'current physical origin')

def commit(source,target):
    A.origin(source);A.origin(target)
    while (bit:=source.read())!=A.BLANK:
        need(bit in (0,1) and target.read() in (0,1),'equal-size complete staged output')
        target.write(bit);source.move(1);target.move(1)
    need(target.read()==A.BLANK,'preserved complete output frontier')
    A.origin(source);A.origin(target)

class Provider:
    """521 fixed private ports: 3 fields, 130 metadata, 388 exact child.

    The parent descriptor is borrowed. The widened descriptor is LEAF-only;
    it is never used by a global row producer, ordinary or monomial service.
    """
    def __init__(self,rank):
        need(type(rank) is int and 1<=rank<=8,'fixed selected positive rank')
        self.rank=rank
        self.child=S.cutoff.PositiveChild(rank)
        with C.collect_tapes() as tapes:
            self.pool=ScratchPool(128);self.scope=OuterScope(self.pool)
            self.header_guide,self.length_guide=Tape(),Tape()
        self.cohort=L.LeafCohort(tapes)
        self.parent=self.work=None

    @property
    def port_count(self):
        return 3+len(self.cohort.tapes)+self.child.port_count

    def bind(self,work,context):
        need(len(work)==self.port_count and len(set(map(id,work)))==len(work)
             and all(p is not context.tape for p in work),'fixed disjoint rounded-leaf inventory')
        self.work,self.parent=tuple(work),context
        self.expanded,self.rounded=A.CodedPort(work[0]),A.CodedPort(work[1])
        self.wide_context=A.BinaryContextPort(work[2])
        stop=3+len(self.cohort.tapes)
        self.cohort.bind(work[3:stop]);self.child.bind(work[stop:],self.wide_context)

    read_header=L.Provider.read_header
    component_width=L.Provider.component_width

    def prepare(self,header,h,cleanup):
        def own(x): cleanup.callback(x.close);return x
        for name in ('outer','rows','f','K','record_bits','row_bits','cutoff'):
            positive(header[name])
        two=own(Count.literal(2))
        need(compare(h,two)>=0 and compare(header['rho'],header['K'])<0,
             'signed width and offset')
        need(compare(header['f'],header['cutoff'])<=0,'parent elementary leaf branch')
        g=own(Count(header['f']))
        if self.rank>1:g.multiply_small(self.rank)
        # m=ceil((g+1)/2)+1=floor((g+2)/2)+1. This is an explicit
        # safe margin even for arbitrary independently chosen h-bit inputs.
        margin=own(Count(g));margin.increment();margin.increment()
        margin.divide_small(2);margin.increment()
        wide=own(Count(h));wide.add(g);wide.add(margin)
        pair=own(Count(h));pair.increment();pair.multiply_small(6)
        coefficients,remainder=divide(header['record_bits'],pair)
        own(coefficients);own(remainder)
        need(remainder.zero(),'record_bits equals 6*c*(h+1)');positive(coefficients)
        fibre=own(power_two(header['within_bits']))
        row=own(Count.product(fibre,header['record_bits']))
        need(compare(row,header['row_bits'])==0,'complete original row extent')
        rows=own(Count.product(header['outer'],header['rows']))
        records=own(Count.product(rows,fibre))
        components=own(Count.product(records,coefficients));components.multiply_small(2)
        wide_pair=own(Count(wide));wide_pair.increment();wide_pair.multiply_small(6)
        wide_record=own(Count.product(coefficients,wide_pair))
        wide_row=own(Count.product(fibre,wide_record))
        widened=dict(header,record_bits=wide_record,row_bits=wide_row)
        return g,margin,wide,components,widened

    def write_header(self,header):
        target=self.wide_context.tape
        need(target.read()==A.BLANK,'blank widened descriptor')
        for name in L.SCHEMA:
            value=header[name];value.rewind()
            while value.read()!=3:
                need(value.read() in (0,1),'canonical Count digit')
                emit(target,1);value.step(1)
            emit(target,0);value.rewind()
            while value.read()!=3:
                emit(target,value.read());value.step(1)
            value.rewind()
        A.origin(target)

    def lift(self,field,h,g,margin,components):
        remaining=Counter(components)
        try:
            while not remaining.finished:
                zeros=Counter(g)
                try:
                    while not zeros.finished:
                        emit(self.expanded,0);zeros.decrement()
                finally:zeros.close()
                bits=Counter(h);sign=0
                try:
                    while not bits.finished:
                        sign=field.read();need(sign in (0,1),'complete uniform signed component')
                        emit(self.expanded,sign);field.move(1);bits.decrement()
                finally:bits.close()
                extension=Counter(margin)
                try:
                    while not extension.finished:
                        emit(self.expanded,sign);extension.decrement()
                finally:extension.close()
                need(field.read()==2,'exact input component delimiter')
                emit(self.expanded,2);field.move(1);remaining.decrement()
            need(field.read()==4,'exact complete input field extent')
        finally:remaining.close()
        A.origin(field.tape);A.origin(self.expanded.tape)

    def drop(self,h,g,margin,components):
        source,target=self.expanded,self.rounded
        remaining=Counter(components)
        try:
            while not remaining.finished:
                discarded=Counter(g);carry=0
                try:
                    while not discarded.finished:
                        carry=source.read();need(carry in (0,1),'complete discarded low bits')
                        source.move(1);discarded.decrement()
                finally:discarded.close()
                bits=Counter(h);out_sign=0
                try:
                    while not bits.finished:
                        bit=source.read();need(bit in (0,1),'complete retained high bits')
                        total=bit+carry;out_sign=total&1;carry=total>>1
                        emit(target,out_sign);source.move(1);bits.decrement()
                finally:bits.close()
                tail=Counter(margin);overflow=False;sign=0
                try:
                    while not tail.finished:
                        sign=source.read();need(sign in (0,1),'complete signed extension')
                        total=sign+carry;overflow=overflow or (total&1)!=out_sign
                        carry=total>>1;source.move(1);tail.decrement()
                finally:tail.close()
                # Two extra sign bits cover the sole transient 0+1 carry;
                # thereafter the infinite two's-complement tail is constant.
                for _ in (0,1):
                    total=sign+carry;overflow=overflow or (total&1)!=out_sign;carry=total>>1
                need(source.read()==2,'exact expanded component delimiter')
                emit(target,2);source.move(1);remaining.decrement()
                if overflow:raise RoundedOverflow('nearest-up final output exceeds signed public width')
            need(source.read()==4,'complete rounded return extent')
        finally:remaining.close()
        A.origin(source.tape);A.origin(target.tape)

    def run(self,field,context):
        need(self.work is not None and context.tape is self.parent.tape
             and field.tape is not context.tape and all(field.tape is not p for p in self.work),
             'bound parent and genuinely disjoint complete numerical field')
        for port in (field.tape,context.tape,*self.work):at_origin(port)
        for port in self.work:need(port.read()==A.BLANK,'blank owned rounded-leaf stage')
        self.cohort.start();cleanup=ExitStack()
        try:
            with C.execution(),self.scope.installed():
                header=self.read_header(context)
                for value in header.values():cleanup.callback(value.close)
                h=self.component_width(field);cleanup.callback(h.close)
                g,margin,wide,components,widened=self.prepare(header,h,cleanup)
                self.write_header(widened)
                self.lift(field,h,g,margin,components)
            # No nested codec or allocator scope; live Count leases remain
            # private and untouched while the separately owned child runs.
            self.child.run(self.expanded,self.wide_context)
            with C.execution(),self.scope.installed():
                self.drop(h,g,margin,components)
            commit(self.rounded.tape,field.tape)
        finally:
            with C.execution(),self.scope.installed():
                cleanup.close();self.pool.empty()
            self.cohort.finish()
            for port in self.work[:3]:A.retire(port)
            A.origin(field.tape);A.origin(context.tape)

class PaidService:
    """Exact current raw PAID identity; no enclosing remap is erased."""
    def __init__(self,event):
        triple,_op,record=S.catalog.bind_paid(event)
        self.owner,self.rank=triple[1].fields[0],record['rank']
        self.provider=Provider(self.rank);self.field=self.context=None
    @property
    def port_count(self):return self.provider.port_count
    bind=S.selected.PaidService.bind
    run=S.selected.PaidService.run
