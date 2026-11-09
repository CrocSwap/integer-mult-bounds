"""Current descriptor to retained Compact: a structured finite-control service.

This is an executable source-level refinement, not an emitted A transition
table. It accepts precisely A's numeric/context port views and fixed blank
work ports. Runtime numerical values remain in Count tapes throughout.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from contextlib import ExitStack
from binding_sources import need
from codec import S,A,Cohort,collect_tapes,execution
from cardinal_counts import Count,positive
from compact_counts import power_two,copy_bits,append_bits
from compact_layout import Layout
from compact_streams import digit_permutation
from encoded import compare,subtract
from records import Tape
from stream import Counter
from session import OuterScope,borrowed_count,borrowed_tape,erase_marker,sealed_constructors
from scratch_pool import ScratchPool

SCHEMA=('outer','rows','stock','row_bits','within_bits','record_bits','p','d','K','G','H',
        'q0','qF','qB','D','f','rho','active_start','back_start','selected_axes',
        'entry_start','remainder','cutoff')
NAMES=('u','u_rest','t','t_rest','before','x','middle','y','after','b')

def scale(value,constant):
    need(type(constant) is int and constant>=0,'compiled nonnegative multiplier')
    if constant==0:return Count.literal(0)
    out=Count(value)
    if constant>1:out.multiply_small(constant)
    return out

class Provider:
    def __init__(self,rank,source_block,target_block,native_factory):
        need(type(rank) is int and rank>=2,'fixed compiled rank')
        need(0<=source_block<rank and 0<=target_block<rank and source_block!=target_block,
             'fixed distinct selected-block pair')
        self.rank=rank;self.source_block=source_block;self.target_block=target_block
        self.late=source_block>target_block
        # native_factory constructs a fixed precompiled Ordinary supplier.
        # It receives no runtime parameter or payload and is never called again.
        with collect_tapes() as tapes:
            native=native_factory()
            need(type(native) is S.ordinary.Ordinary and native.observe is None
                 and native.runtime.observe is None,'unchanged ordinary engine without payload callbacks')
            self.engine=S.engine.CompactEngine(NAMES,'y' if self.late else 'x',
                                              'x' if self.late else 'y',self.late,native)
            self.pool=ScratchPool(160);self.scope=OuterScope(self.pool)
            self.bridge,self.field_guide,self.header_guide,self.length_guide=(Tape() for _ in range(4))
        self.cohort=Cohort(tapes,native)
        self.observed_calls=0

    @property
    def port_count(self):return self.cohort.port_count

    def bind(self,work):self.cohort.bind(work)

    def read_header(self,context):
        result={}
        def advance():
            self.header_guide.append(1);context.move(1)
        for name in SCHEMA:
            self.length_guide.rewind()
            while context.read()==1:
                self.length_guide.append(1);advance()
            need(context.read()==0,'self-delimiting current header length');advance()
            self.length_guide.rewind()
            value=object.__new__(Count);value.tape=self.pool.acquire()
            any_digit=multiple=False;last=0
            while self.length_guide.read()!=4:
                need(self.length_guide.read()==1,'unary current header length')
                bit=context.read();need(bit in (0,1),'binary current header digit')
                multiple=multiple or any_digit;any_digit=True;last=bit
                value.tape.append(bit);advance();self.length_guide.step(1)
            need(any_digit and (last==1 or not multiple),'canonical LSF current header value')
            value.tape.append(3);value.rewind();result[name]=value
            self.length_guide.clear()
        need(context.read()==6,'exact current header frontier')
        self.header_guide.rewind()
        while self.header_guide.read()!=4:
            context.move(-1);self.header_guide.step(1)
        self.header_guide.clear()
        return result

    def prepare(self,header,cleanup):
        def own(x):cleanup.callback(x.close);return x
        for key in ('outer','rows','row_bits','record_bits','f','K','G','H'):
            positive(header[key])
        one=own(Count.literal(1));twoH=own(scale(header['H'],2))
        need(compare(header['rho'],header['K'])<0,'selected offset inside one chunk')
        n=own(subtract(header['f'],one))
        compact=own(Count.product(n,header['G']))
        rest=own(subtract(header['H'],compact))
        chunk=own(Count.product(header['f'],header['K']))
        left=own(scale(chunk,min(self.source_block,self.target_block)))
        right=own(scale(chunk,max(self.source_block,self.target_block)))
        left.add(header['active_start']);right.add(header['active_start'])
        before=own(subtract(left,twoH))
        difference=own(subtract(right,left));middle=own(subtract(difference,chunk))
        right_end=own(Count(right));right_end.add(chunk)
        after=own(subtract(header['back_start'],right_end))
        tail=own(subtract(header['within_bits'],header['back_start']))
        suffix=own(subtract(tail,compact))
        # The full reserved back field exists, including its unused suffix.
        need(compare(tail,header['H'])>=0,'complete root back reservation')
        reduced=own(subtract(header['K'],one));rho=own(subtract(reduced,header['rho']))
        fibre=own(power_two(suffix));record=own(Count.product(fibre,header['record_bits']))
        rows=own(Count.product(header['outer'],header['rows']))
        full=own(power_two(header['within_bits']));expected=own(Count.product(full,header['record_bits']))
        need(compare(expected,header['row_bits'])==0,'exact complete physical row length')
        active=own(scale(header['f'],self.rank));active.add(header['remainder'])
        need(compare(active,header['selected_axes'])==0,'current f/remainder geometry')
        rank=own(Count.literal(self.rank))
        need(compare(header['remainder'],rank)<0,'ordinary remainder below fixed rank')
        need(compare(header['selected_axes'],header['d'])<=0,'ordinary width within root budget')
        active_end=own(scale(chunk,self.rank));active_end.add(header['active_start'])
        need(compare(active_end,header['back_start'])<=0,'complete active block list precedes back field')
        widths=(compact,rest,compact,rest,before,chunk,middle,chunk,after,compact)
        return widths,n,rho,record,rows

    def import_field(self,field):
        while (symbol:=field.read())!=4:
            need(symbol in (0,1,2),'complete canonical numerical field')
            for shift in (2,1,0):self.bridge.append((symbol>>shift)&1)
            self.field_guide.append(1);field.move(1)
        self.bridge.rewind();self.field_guide.rewind()
        while self.field_guide.read()!=4:
            field.move(-1);self.field_guide.step(1)
        self.field_guide.rewind()

    def export_field(self,field,output):
        output.rewind();self.field_guide.rewind()
        while self.field_guide.read()!=4:
            value=0
            for _ in range(3):
                bit=output.read();need(bit in (0,1),'complete returned physical codeword')
                value=2*value+bit;output.step(1)
            need(value in (0,1,2),'returned complete numerical record format')
            need(field.read() in (0,1,2),'returned field has original exact extent')
            field.write(value);field.move(1);self.field_guide.step(1)
        need(output.read()==4 and field.read()==4,'exact full-field return frontier')
        self.field_guide.rewind()
        while self.field_guide.read()!=4:
            field.move(-1);self.field_guide.step(1)
        self.field_guide.clear();output.rewind()

    def single(self,widths,rho,record,rows):
        """f=1: the actual retained four-bucket bit gate, with no n>0 guard."""
        e=self.engine;e.rearm();source=borrowed_tape(self.bridge)
        with sealed_constructors(),e.scope.installed(),ExitStack() as cleanup:
            plan=Layout(NAMES,widths,record);cleanup.callback(plan.close)
            remaining=Counter(rows);cleanup.callback(remaining.close)
            source_bit=plan.bit_position(e.source,rho);cleanup.callback(source_bit.close)
            target_bit=plan.bit_position(e.target,rho);cleanup.callback(target_bit.close)
            early=compare(source_bit,target_bit)<0
            first,second=(source_bit,target_bit) if early else (target_bit,source_bit)
            mapping=(0,1,3,2) if early else (0,3,2,1)
            while not remaining.finished:
                current=e.pool.acquire()
                copy_bits(source,current,plan.row_bits);current.rewind()
                following=digit_permutation(current,plan,first,second,mapping,e.pool.acquire)
                append_bits(following,e.output);following.clear();remaining.decrement()
                e.calls['rows']+=1
            need(source.read()==4,'complete f=1 outer-row packet');source.rewind()
        e.pool.empty()
        for tape in e.pool.tapes:erase_marker(tape)
        e.output.rewind();e.closed=True
        return e.output

    def run(self,field,context):
        """field=A.CodedPort, context=A.BinaryContextPort; both start at origin.

        The successful-input theorem leaves only field's exact output, context
        unchanged, and every work port physically blank at its current origin.
        No interrupted-service rollback contract is claimed.
        """
        self.cohort.start()
        with execution(),self.scope.installed(),ExitStack() as cleanup:
            header=self.read_header(context)
            for value in header.values():cleanup.callback(value.close)
            widths,n,rho,record,rows=self.prepare(header,cleanup)
            self.import_field(field)
            with self.scope.suspended():
                returned=(self.single(widths,rho,record,rows) if n.zero() else
                          self.engine.run(self.bridge,widths,n,header['K'],header['G'],rho,record,rows))
            self.export_field(field,returned)
            returned.clear();erase_marker(returned);self.bridge.clear()
        self.pool.empty()
        self.cohort.finish();self.observed_calls+=1
