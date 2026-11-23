"""Independent source-service, tape-head, register and tariff review.
Prepared for Jerry Chen / CubeJerry with OpenAI assistance. Apache-2.0.
No author checker is imported or run. Implementations are subjects; oracles
use arithmetic, a separate image parser and literal original Plan methods.
"""
import argparse, ast, json, random, sys
from fractions import Fraction
from hashlib import sha1, sha256
from pathlib import Path
from types import ModuleType

def need(ok,message):
    if not ok: raise ValueError(message)

def module(name,path,raw=None):
    obj=ModuleType(name);obj.__file__=str(path);sys.modules[name]=obj
    exec(compile(path.read_bytes() if raw is None else raw,str(path),'exec'),obj.__dict__)
    return obj

def authenticate(package):
    need(sha256((package/'SCIENTIFIC-FREEZE.json').read_bytes()).hexdigest()=='2a9ad9ee52a7f2d8cc1ee066d5f6ba282c1712989121fa5c71a350df669a4de0','unreviewed original freeze')
    original=json.loads((package/'SCIENTIFIC-FREEZE.json').read_text())
    for path in ('PROOF.md','codec.py','source_loader.py','SOURCE-BINDINGS.json'):
        need(sha256((package/path).read_bytes()).hexdigest()==original[path],'changed original '+path)
    need(original['SOURCE-BINDINGS.json']=='040f858ab08ce6d7831b6ded8811dcf44ad9d1dbff2c5f9ea906329b02f41454','unreviewed original manifest')
    sources=json.loads((package/'SOURCE-BINDINGS.json').read_text())['files']
    for name,row in sources.items():
        data=(package/'sources'/name).read_bytes()
        need(sha256(data).hexdigest()==row['sha256'],'source SHA256 '+name)
        if 'git_blob' in row:
            need(sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==row['git_blob'],'source Git blob '+name)
    expected={'controller.py':'f6c9c0a988bba3f868899cf2f863a0a985a8884a7a216d3dc6377657416f0227','tapes.py':'eef9eecf511f17130534e8f8feb41f508ebc789e1b70c8392602835b3c1cf309','registers.py':'081987d56d05dea82256d0c68779f9a4e8debfb20437ba1ba0fdfac3de050adf','COST-PROOF.md':'ff44f670b01ebb6748a0f5879d2fc83c1bc1950c9f15cb0a14743d86f7634ea8'}
    for name,pin in expected.items():
        need(sha256((package/'sequential'/name).read_bytes()).hexdigest()==pin,'unreviewed sequential '+name)
    return sources,expected

def audit_tape_type(tapes):
    Base=tapes.Tape
    class Audited(Base):
        def __init__(self,meter):
            super().__init__(meter)
            self.shadow_head=0;self.shadow=[];self.shadow_peak=0;self.actions=0
        def move(self,delta):
            need(self.head==self.shadow_head,'unpriced head relocation')
            before=self.m.cells;super().move(delta)
            self.shadow_head+=delta;self.actions+=1
            need(self.head==self.shadow_head and self.m.cells==before+1,'one-cell motion invoice')
        def read(self):
            need(self.head==self.shadow_head,'unpriced head relocation')
            expected=self.shadow[self.shadow_head];self.actions+=1
            value=super().read();need(value==expected,'independent tape memory');return value
        def write(self,value):
            need(self.head==self.shadow_head,'unpriced head relocation')
            position=self.shadow_head
            if position==len(self.shadow):self.shadow.append(value)
            else:
                need(position<len(self.shadow),'physical write skipped cells');self.shadow[position]=value
            self.shadow_peak=max(self.shadow_peak,position+1);self.actions+=1
            super().write(value)
    return Audited

def table_oracle(tapes):
    rng=random.Random(881092);operations=cell_actions=0
    def decode(bits,w):
        index=0
        def scalar():
            nonlocal index
            answer=0
            for bit in bits[index:index+w]:answer=2*answer+bit
            need(index+w<=len(bits),'independent header truncation');index+=w;return answer
        count=scalar();out=[]
        for _ in range(count):
            key,length=scalar(),scalar();payload=bits[index:index+length];index+=length
            need(len(payload)==length,'independent payload truncation');out.append((key,payload))
        need(index==len(bits),'independent trailing data');return out
    for width in (5,8,13):
        meter=tapes.Meter(width);table=tapes.Table(meter);expected={}
        for step in range(120):
            key=rng.randrange(16)
            if key in expected and step%4==0:need(table.pop(key)==expected.pop(key),'dictionary pop oracle')
            else:
                payload=[rng.randrange(2) for _ in range(rng.randrange(17))]
                table.rewrite(key,payload);expected[key]=payload
            want=sorted(expected.items())
            need(decode(table.a.cells,width)==want,'independent sorted image')
            need(list(table.walk())==want,'sequential walk oracle')
            need(table.historical_bits()==table.a.shadow_peak+table.b.shadow_peak,'separate physical histories')
            need(meter.cells==table.a.actions+table.b.actions,'complete cell-action census');operations+=1
        prior=table.historical_bits();table.close()
        need(table.historical_bits()==prior,'clear must preserve historical peak')
        need(not any(table.a.shadow) and not any(table.b.shadow),'complete initialized erasure')
        seen=[]
        def records():
            for i in range(3):seen.append(i);yield i,[i%2]*(i+1)
        table.reset(records(),count=3)
        need(seen==[0,1,2] and list(table.walk())==[(i,[i%2]*(i+1)) for i in range(3)],'counted streaming initialization')
        table.close();cell_actions+=meter.cells
    return operations,cell_actions

def register_oracle(regs_module):
    count=max_actions=0
    for width in (1,2,3,4,8,17):
        regs=regs_module.Registers(width)
        values=range(1<<width) if width<=4 else sorted({0,1,2,3,(1<<(width//2))-1,1<<(width-1),(1<<width)-1})
        for a in values:
            for b in values:
                regs.load(0,a);regs.load(1,b)
                def trial(action,expect,out=2):
                    nonlocal count,max_actions
                    before=regs.meter.cells;action();spent=regs.meter.cells-before
                    need(regs.value(out)==expect,'independent register integer oracle')
                    need(spent<2**20*(2*width+1)**4,'universal macro envelope')
                    max_actions=max(max_actions,spent);count+=1
                trial(lambda:regs.copy(0,2),a)
                before=regs.meter.cells
                need(regs.compare(0,1)==(a>b)-(a<b),'register comparison');count+=1
                spent=regs.meter.cells-before;max_actions=max(max_actions,spent)
                need(spent<2**20*(2*width+1)**4,'comparison envelope')
                if a+b<1<<width:trial(lambda:regs.add(0,1,2),a+b)
                if a>=b:trial(lambda:regs.sub(0,1,2),a-b)
                if a*b<1<<width:trial(lambda:regs.mul(0,1,2),a*b)
                if b:
                    before=regs.meter.cells;regs.divide(0,1,2,3)
                    spent=regs.meter.cells-before;max_actions=max(max_actions,spent)
                    need((regs.value(2),regs.value(3))==divmod(a,b),'restoring division oracle')
                    need(spent<2**20*(2*width+1)**4,'division envelope');count+=1
        need(regs.meter.cells==sum(t.actions for t in regs.tapes),'register physical accounting')
    return count,max_actions

def original_plan(package):
    tree=ast.parse((package/'sources/transport.py').read_text())
    selected=[n for n in tree.body if isinstance(n,(ast.ClassDef,ast.FunctionDef)) and n.name in ('ceil','axes','Plan')]
    namespace={'F':Fraction}
    exec(compile(ast.Module(body=selected,type_ignores=[]),'<literal-original-Plan>','exec'),namespace)
    return namespace['Plan']

def plain(job):
    result=[]
    for axis in job.axes:
        if isinstance(axis,int):result.append(('integer',axis))
        else:result.append(('typed',tuple(tuple(str(x) for x in op) for op in axis.basis),axis.column))
    return job.owner,tuple(result)

class Service:
    def __init__(self,codec,width):
        self.codec=codec;self.live=set(range(width));self.next_owner=width;self.trace=[];self.opened=0
    def zero(self,job):
        result=self.codec.ns['Job'](self.next_owner,job.axes);self.live.add(self.next_owner);self.next_owner+=1
        self.trace.append(('zero',plain(job),plain(result)));return result
    def native(self,ports,columns):
        ident=self.opened;self.opened+=1
        self.trace.append(('native',ident,columns,tuple(plain(x) for x in ports)))
        base=self.codec.words[(1,173,594)[ident%3]];expanded=[]
        for op in base:
            for j in range(columns):
                row=list(op);row[1]=row[1]*columns+j
                if row[0]!='scale':row[2]=row[2]*columns+j
                expanded.append(tuple(row))
        basis=tuple(expanded);Job,Axis=self.codec.ns['Job'],self.codec.ns['Axis']
        result=Job(ports[0].owner,tuple(Axis(basis,i) for i in (2,0,1)))
        def body():
            self.trace.append(('resume',ident,plain(result)));yield result
            self.trace.append(('return',ident))
        return body()
    def leaf(self,job):
        need(job.owner in self.live,'leaf live owner');self.trace.append(('leaf',plain(job)))
    def retire_zero(self,job):
        need(job.owner in self.live,'retire live owner');self.live.remove(job.owner)
        self.trace.append(('retire',plain(job)))

def controller_oracle(package,codec_module,controller_type,short=False):
    Plan=original_plan(package);counts=callbacks=decodes=0;digests=[]
    for width,source_width,rounds in ((3,2,4),(5,3,3),(2,1,5))[:1 if short else 3]:
        plan=Plan.__new__(Plan);plan.n=128;plan.width=width;plan.source_width=source_width;plan.rounds=rounds
        records=[(0,10,1,0,3,2,0,4,2),(1,10,30,3,2),(0,20,1,1,30,0,2),
                 (1,20,31,3,0),(2,20),(2,10)]
        plan.events=lambda:iter(records)
        codec=codec_module.Codec(codec_module.Limits(128,20,10000,10,20,2,width))
        rows=[codec.ns['Job'](i,tuple(reversed(range(128)))) for i in range(width)]
        wanted=Service(codec,width);plan.run(rows,wanted)
        actual=Service(codec,width);subject=controller_type(codec)
        receipt=subject.run(plan,rows,actual,records)
        need(wanted.trace==actual.trace,'literal Plan service trace')
        need(actual.live==wanted.live==set(range(width)),'restored source owner set')
        expected_decodes=((width+source_width-1)//source_width)*rounds
        need(receipt['decode_calls']==expected_decodes,'every group and round')
        need(receipt['row_records_written']==width*expected_decodes,'all repeated row initializations')
        need(receipt['calendar_copies']==1,'one supplied calendar copy')
        row_before=tuple(subject.input_rows.cells)
        need(bool(row_before),'input rows survive caller return')
        historical=tuple(t.historical_bits() for t in subject.tables)
        warm=Service(codec,width);subject.run(plan,rows,warm,records)
        need(warm.trace==wanted.trace and tuple(subject.input_rows.cells)==row_before,'warm caller trace and input image')
        need(tuple(t.historical_bits() for t in subject.tables)==historical,'same reusable physical table roles')
        # The charged adapter bound must remain D, even for integer-only input.
        before=subject.m.registers;subject.job_bits(rows[0])
        need(subject.m.registers-before>=2**32*(plan.n+1)**4,'quartic Job adapter charge')
        counts+=1;callbacks+=len(actual.trace);decodes+=expected_decodes
        digests.append(sha256(repr(wanted.trace).encode()).hexdigest())
    return counts,callbacks,decodes,digests

def tariff_oracle():
    rows=[]
    for h in (3000,3001,4096,10000):
        N=1<<h;B=N**92;w=128*h;P=18906;q=104904;C=2*N**83;J=4*w+1+N*h
        table=3*w+B*(2*w+J)+C*(4*w+P*J)+q*C*(2*w+J)
        input_rows=w+B*(w+J);events=w+2*N**88*(5+4*P+5*q)*w
        buffers=(10*P+32)*J+(16*P+256)*w+1024*N*h
        S=2*(2*table+input_rows+events+buffers+2**21+512*w+2048)
        D=2**32*(N+1)**4;R=2**20*(2*w+1)**4
        Q=64*S*(D+128)*(R+32);M=64*(C+P*N+N*N+N+1);E=2*(q+2)*N**88
        need(J<2*N*h and table<3*B*N*h and input_rows<2*B*N*h,'storage leading terms')
        need(events<B*N*h and buffers<B*N*h and S<32*B*N*h and S<N**96,'per-role histories')
        need(D<N**5 and R<N**16 and Q<N**128 and M<N**128 and E<N**90,'composed positive envelopes')
        need(E*Q*M<N**346,'one decode event cost')
        need(2*N**348+N**200<N**350<N**512,'complete Plan.run absorption')
        need(max(S,E,C,q*C,B)<1<<w,'all dynamic counters below w')
        rows.append({'h':h,'space_bits':S.bit_length(),'sweep_bits':Q.bit_length(),'one_decode_event_bits':(E*Q*M).bit_length()})
    # Exact base plus the written integer-ratio induction, never 9**(2**h).
    N0=1<<16
    need(N0**512<2**(3*N0)<9**N0,'exponential absorption base')
    need(2*512<=N0,'geometric induction ratio bound')
    return rows

def expect_fault(call):
    try:call()
    except (ValueError,KeyError,ArithmeticError,StopIteration,IndexError):return
    raise ValueError('negative control survived')

def run(package):
    sources,pins=authenticate(package);seq=package/'sequential'
    module('source_loader',package/'source_loader.py')
    codec=module('codec',package/'codec.py')
    tapes=module('tapes',seq/'tapes.py');tapes.Tape=audit_tape_type(tapes)
    registers=module('registers',seq/'registers.py')
    controller=module('controller',seq/'controller.py')
    table_count,table_cells=table_oracle(tapes)
    reg_count,reg_peak=register_oracle(registers)
    calls,callbacks,decodes,digests=controller_oracle(package,codec,controller.Controller)
    tariff=tariff_oracle();controls=[]
    raw=(seq/'controller.py').read_bytes()
    mutations=[('omitted_source_rounds',b'for round_no in range(plan.rounds):',b'for round_no in range(1):'),
               ('reversed_pending_prefix',b'job.select(range(selected))',b'job.select(reversed(range(selected)))'),
               ('undercharged_quartic_adapter',b'(self.codec.limits.n+1)**4',b'(self.codec.limits.n+1)**2')]
    for i,(name,old,new) in enumerate(mutations):
        need(old in raw,'mutation source binding '+name)
        mutant=module('_controller_mutant_'+str(i),seq/'controller.py',raw.replace(old,new))
        expect_fault(lambda:controller_oracle(package,codec,mutant.Controller,short=True));controls.append(name)
    old_at=tapes.Tape.at
    tapes.Tape.at=lambda self,position:setattr(self,'head',position)
    try:expect_fault(lambda:table_oracle(tapes))
    finally:tapes.Tape.at=old_at
    controls.append('unpriced_head_jump')
    old_clear=tapes.Tape.clear
    def lose_history(self):old_clear(self);self.peak=0
    tapes.Tape.clear=lose_history
    try:expect_fault(lambda:table_oracle(tapes))
    finally:tapes.Tape.clear=old_clear
    controls.append('erasure_resets_history')
    reg_raw=(seq/'registers.py').read_bytes()
    need(b'self.compare(remainder,b)>=0' in reg_raw,'division mutation binding')
    mutant=module('_register_mutant',seq/'registers.py',reg_raw.replace(b'self.compare(remainder,b)>=0',b'self.compare(remainder,b)>0'))
    expect_fault(lambda:register_oracle(mutant));controls.append('exact_divisor_not_subtracted')
    # Source bytes, rather than source object caches, anchor the original oracle.
    sample=(package/'sources/transport.py').read_bytes()
    need(sha256(sample+b'\n# changed\n').hexdigest()!=sources['transport.py']['sha256'],'source corruption discriminator')
    controls.append('source_corruption')
    return dict(schema='independent-sequential-storage-review/1',status='PASS_SCOPED_SEQUENTIAL_BOOKKEEPING',
                source_files=len(sources),scientific_pins=pins,table_operations=table_count,
                independent_table_cell_actions=table_cells,register_value_checks=reg_count,
                largest_register_macro_actions=reg_peak,source_plan_cases=calls,
                source_service_actions=callbacks,complete_run_decodes=decodes,
                warm_run_cases=calls,source_trace_sha256=digests,tariff_cases=tariff,
                rejected_controls=controls,author_checker_used=False,
                scope='Supplied calendar/library decoder bookkeeping; native dispatcher, native bodies and setup generation excluded')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--package',type=Path,required=True)
    parser.add_argument('--output',type=Path);args=parser.parse_args()
    result=json.dumps(run(args.package.resolve()),sort_keys=True,indent=2)+'\n'
    if args.output:args.output.write_text(result)
    print(result,end='')
