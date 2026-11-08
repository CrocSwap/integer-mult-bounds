"""Physical exact-product, ownership and history controls.

Host integer arrays are external fixtures/oracles only. The measured invocation
uses the actual encoded kernel under the inherited no-decode guard.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from hashlib import sha256
from pathlib import Path
from types import ModuleType


def need(value,message):
    if not value:raise ValueError(message)


def classical(first,second,b):
    return tuple(sum(first[i*b+k]*second[k*b+j] for k in range(b))
                 for i in range(b) for j in range(b))


def emit(values,tape,width):
    from cardinal_counts import Count
    from ring_words import Signed,write_signed
    from router_metadata import owned
    for value in values:
        with owned(Signed(Count.literal(abs(value)),value<0)) as (word,):write_signed(word,tape,width)
    tape.rewind()


def decode(tape,entries,width):
    from words import BLANK
    result=[]
    for _ in range(entries):
        value=0
        for position in range(width):
            bit=tape.read();need(bit in(0,1),'returned matrix bit');value|=bit<<position;tape.step(1)
        result.append(value-(1<<width) if value&(1<<(width-1)) else value)
    need(tape.read()==BLANK,'returned matrix extent');return tuple(result)


def snapshot(tapes):
    return tuple((bytes(tape.cells),tape.head) for tape in tapes)


def totals(tapes):
    return {key:sum(getattr(tape.meter,key) for tape in tapes) for key in ('reads','writes','moves')}


def erased(owner):
    from words import BLANK
    owner.idle()
    need(all(tape.head==1 and all(value==BLANK for value in tape.cells) for tape in owner.forbidden()),
         'all physical matrix roles erased including historical backing')


class Fixture:
    def __init__(self,b,w,first,second,metadata_alias=False):
        from records import Tape
        from cardinal_counts import Count
        self.first,self.second=Tape(),Tape()
        self.block=Count.literal(b);self.width=self.block if metadata_alias else Count.literal(w)
        self.wide=Count.literal(2*w+b.bit_length()-1+2)
        self.b,self.w,self.return_width=b,w,2*w+b.bit_length()-1+2
        emit(first,self.first,self.width);emit(second,self.second,self.width)
    def ports(self):return self.first,self.second,self.block.tape,self.width.tape,self.wide.tape
    def close(self):
        from session import erase_marker
        for tape in (self.first,self.second):tape.clear();erase_marker(tape)
        for count in (self.block,self.wide):count.close();erase_marker(count.tape)
        if self.width is not self.block:self.width.close();erase_marker(self.width.tape)
    def __enter__(self):return self
    def __exit__(self,*_):self.close()


def invoke(owner,fixture):
    from check_support import no_decode
    with no_decode():
        return owner.run(fixture.first,fixture.second,fixture.block,fixture.width,fixture.wide)


def positive(owner,b,w,first,second,metadata_alias=False):
    with Fixture(b,w,first,second,metadata_alias) as fixture:
        expected=classical(first,second,b);ports=fixture.ports();before=snapshot(ports)
        roles=owner.forbidden();observed=tuple({id(t):t for t in (*roles,*ports)}.values())
        actions=totals(observed);old=(owner.nodes,owner.leaves,owner.pushes,owner.pops,owner.arithmetic.products)
        branches=dict(owner.word.calls)
        result=invoke(owner,fixture)
        try:
            actual=decode(result,b*b,fixture.return_width)
            need(actual==expected,'exact independent classical matrix product')
            need(snapshot(ports)==before,'borrowed matrix bytes and origins')
            saved=(snapshot(ports),bytes(result.cells),result.head)
            try:invoke(owner,fixture)
            except ValueError as error:need(str(error)=='consumed seven-product owner','specific pending matrix guard')
            else:raise ValueError('unconsumed matrix return accepted')
            need(saved==(snapshot(ports),bytes(result.cells),result.head),'moved pending matrix unchanged')
        finally:
            if owner.pending:owner.consume()
        erased(owner)
        end=totals(observed);now=(owner.nodes,owner.leaves,owner.pushes,owner.pops,owner.arithmetic.products)
        delta=tuple(x-y for x,y in zip(now,old));ell=b.bit_length()-1;leaves=7**ell
        need(delta==((7*leaves-1)//6,leaves,(7*leaves-7)//6,(7*leaves-7)//6,leaves),
             'exact seven-child execution counts')
        return dict(B=b,width=w,return_width=fixture.return_width,counters=delta,
            finite_alphabet_actions={key:end[key]-actions[key] for key in actions},
            action_scope='checked transaction: run, read, pending rejection, consume, idle',
            owned_roles=len(roles),owned_retained_cells=sum(len(t.cells) for t in roles),
            word_branches={key:owner.word.calls[key]-branches[key] for key in branches},
            pool_peak=owner.pool.peak,output_sha256=sha256(repr(actual).encode()).hexdigest())


def rejected(owner,fixture,operation,message):
    before=snapshot(fixture.ports())
    try:operation()
    except ValueError as error:need(str(error)==message,'specific rejection: '+str(error))
    else:raise ValueError('missing matrix rejection: '+message)
    need(snapshot(fixture.ports())==before,'rejected matrix borrowed restoration')
    erased(owner)


def controls(owner):
    from cardinal_counts import Count
    from check_support import no_decode
    from words import BLANK
    from session import erase_marker
    results=[]
    values=(1,-1,0,1)
    with Fixture(2,3,values,values[::-1]) as fixture:
        def call(a=fixture.first,b=fixture.second,n=fixture.block,w=fixture.width,v=fixture.wide):
            with no_decode():return owner.run(a,b,n,w,v)
        trials=(('duplicate operands',lambda:call(b=fixture.first),'external seven-product operands and metadata'),
                ('metadata/data alias',lambda:call(a=fixture.block.tape),'external seven-product operands and metadata'),
                ('inactive descendant alias',lambda:call(a=owner.forbidden()[-1]),'external seven-product operands and metadata'))
        for label,operation,message in trials:
            rejected(owner,fixture,operation,message);results.append(label)
        fixture.first.step(1)
        rejected(owner,fixture,call,'canonical seven-product borrowed origin')
        fixture.first.rewind();results.append('moved borrowed origin')
        wrong=Count.literal(fixture.return_width-1)
        try:rejected(owner,fixture,lambda:call(v=wrong),'exact inherited matrix return width')
        finally:wrong.close();erase_marker(wrong.tape)
        results.append('underfunded root return')
        fixture.first.write(5)
        before=snapshot(fixture.ports())
        try:call()
        except ValueError as error:
            need(str(error)=='complete fixed-width binary key','specific nonbinary input rejection')
            results.append('nonbinary input: '+str(error))
        else:raise ValueError('nonbinary input accepted')
        need(snapshot(fixture.ports())==before,'nonbinary failure restoration');erased(owner)
    with Fixture(3,3,(0,)*9,(0,)*9) as fixture:
        rejected(owner,fixture,lambda:invoke(owner,fixture),'seven-product block is a power of two')
        results.append('nondyadic block')
    for size,label in ((3,'short matrix'),(5,'trailing matrix')):
        with Fixture(2,3,(0,)*size,(0,)*4) as fixture:
            before=snapshot(fixture.ports())
            try:invoke(owner,fixture)
            except ValueError as error:
                expected='complete fixed-width binary key' if size==3 else 'complete seven-product input matrix'
                need(str(error)==expected,'specific malformed extent rejection')
                results.append(label+': '+str(error))
            else:raise ValueError(label+' accepted')
            need(snapshot(fixture.ports())==before,'bad extent restored');erased(owner)
    return results


def mutations():
    text=Path(__file__).with_name('seven_product.py').read_text();results=[]
    old='((2,False),(3,True))';new='((2,False),(3,False))'
    need(text.count(old)==1,'unique recombination mutation')
    module=ModuleType('wrong_seven_recombination')
    exec(compile(text.replace(old,new),'<wrong seven-product recombination>','exec'),module.__dict__)
    owner=module.SevenProduct()
    try:positive(owner,2,4,(1,2,3,4),(4,-2,1,3))
    except ValueError as error:need(str(error)=='exact independent classical matrix product','wrong recombination detected numerically')
    else:raise ValueError('wrong recombination accepted')
    erased(owner);results.append('executed wrong M2 recombination sign')
    need(text.count('four_ell.multiply_small(4);v.add(four_ell)')==1 and text.count('v.add(two);v.add(two)')==1,
         'unique internal-width mutation')
    wrong=text.replace('four_ell.multiply_small(4);v.add(four_ell)','v.add(four_ell)').replace('v.add(two);v.add(two)','v.add(two)')
    module=ModuleType('wrong_seven_internal_width')
    exec(compile(wrong,'<wrong internal Strassen width>','exec'),module.__dict__)
    owner=module.SevenProduct()
    with Fixture(8,4,(-8,)*64,(-8,)*64) as fixture:
        before=snapshot(fixture.ports())
        try:invoke(owner,fixture)
        except ValueError as error:
            need(str(error)=='signed data-word headroom','specific intermediate signed overflow')
            need(owner.arithmetic.products==1 and owner.pushes==3 and owner.pops==0,
                 'overflow follows the actual depth-three scalar product')
            results.append('executed root-width internal overflow: '+str(error))
        else:raise ValueError('root-only internal carrier accepted')
        need(snapshot(fixture.ports())==before,'intermediate overflow restores borrowed input')
    erased(owner)
    return results


def run():
    from seven_product import SevenProduct
    owner=SevenProduct();cases=[]
    cases.append(positive(owner,1,1,(-1,),(-1,)))
    cases.append(positive(owner,2,4,(1,2,3,4),(4,-2,1,3)))
    aa=tuple((7*i+3)%31-15 for i in range(16))
    bb=tuple((11*i+1)%29-14 for i in range(16))
    cases.append(positive(owner,4,6,aa,bb))
    cases.append(positive(owner,2,2,(-2,1,0,-1),(1,-2,-1,0),metadata_alias=True))
    cases.append(positive(owner,8,4,(-8,)*64,(-8,)*64))
    guard=controls(owner)
    narrow=(1,-1,0,1);other=(0,1,-1,1)
    reused=positive(owner,2,3,narrow,other)
    fresh=positive(SevenProduct(),2,3,narrow,other)
    need(reused['finite_alphabet_actions']==fresh['finite_alphabet_actions'],
         'history-independent current seven-product work')
    need(reused['owned_retained_cells']>fresh['owned_retained_cells'],
         'historical seven-product backing remains charged')
    return dict(cases=cases,controls=guard,mutations=mutations(),
        reuse=dict(reused=reused,fresh=fresh),kernel_sha256=sha256(Path(__file__).with_name('seven_product.py').read_bytes()).hexdigest())
