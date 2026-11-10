"""Compile a literal fixed-tape recursive shape dispatcher.

All Python arithmetic/loops here run before execution. Runtime is only the
retained finite microinstruction machine. No callback, decoded descriptor,
host continuation, computed tape index or dynamic tape allocation is emitted.
Generic stack, codec, arithmetic and whole-high identity retain prior credit.
thu-nmrc with substantial OpenAI Codex assistance, Apache-2.0.
"""
from pathlib import Path
import importlib.util
import sys

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('recursive_retained_shape',HERE/'inputs/shape/producer.py')
P=importlib.util.module_from_spec(spec);sys.modules[spec.name]=P;spec.loader.exec_module(P)
m=P.m

# A bijective renaming of the retained physical stack alphabet. Router logical
# symbols are separately encoded as three actual binary symbols Z/O.
BL,Z,O,LEFT,BASE,SEP,END=m.BLANK,m.ZERO,m.ONE,m.LEFT,m.RIGHT,m.UNIT,m.MARK


def multiply_constant(a,tape,base,fail,prefix):
    """LSB binary multiplication; carry is a finite compiled state < base."""
    labels=[a.fresh(prefix+'_carry') for _ in range(base)]
    done=a.fresh(prefix+'_done');a.goto(labels[0])
    for carry,label in enumerate(labels):
        a.label(label)
        cases={}
        for bit in (0,1):
            action=a.fresh(prefix+'_digit');cases[m.ONE if bit else m.ZERO]=action
        drain=a.fresh(prefix+'_drain');cases[m.RIGHT]=drain
        a.branch(tape,cases,fail)
        for bit in (0,1):
            a.label(cases[m.ONE if bit else m.ZERO]);v=base*bit+carry
            a.write(tape,m.ONE if v&1 else m.ZERO);a.move(tape,1);a.goto(labels[v>>1])
        a.label(drain)
        value=carry
        while value:
            a.write(tape,m.ONE if value&1 else m.ZERO);a.move(tape,1);value>>=1
        a.write(tape,m.RIGHT);a.goto(done)
    a.label(done);P.c.emit_rewind(a,tape,prefix+'_rewind')


def high_program(base):
    """Four logical tapes: preserved w, delivered H, unary w, binary work."""
    m.need(type(base)is int and base>=3,'fixed odd-prime-power base')
    a=m.Assembler(4);fail=a.fresh('bad_root_width');out,guide,work=1,2,3
    P.marked_blank(a,out,fail,'high_output')
    a.write(out,m.ONE);a.move(out,1);a.write(out,m.RIGHT)
    P.c.emit_rewind(a,out,'high_one')
    for t in (guide,work):P.marked_blank(a,t,fail,'high_work')
    P.c.emit_binary_to_unary(a,0,work,guide,'width')
    first=a.fresh('positive_width');a.branch(guide,{m.UNIT:first},fail);a.label(first);a.move(guide,1)
    loop,take,done=(a.fresh(x)for x in ('width_loop','width_multiply','width_done'))
    a.label(loop);a.branch(guide,{m.UNIT:take,m.RIGHT:done},fail)
    a.label(take);multiply_constant(a,out,base,fail,'fixed_base');a.move(guide,1);a.goto(loop)
    a.label(done);P.retire_unary_at_end(a,guide,fail,'erase_width')
    a.move(work,-1);ok=a.fresh('work_left');a.branch(work,{m.LEFT:ok},fail);a.label(ok);a.write(work,m.BLANK)
    a.halt();a.label(fail);a.reject('positive canonical width and blank owned high work')
    return a.finish()


class Builder:
    def __init__(self,low,q,dimension):
        m.need(type(low)is int and low>=2 and type(q)is int and q>=3 and q%2 and
               type(dimension)is int and dimension>=1,'fixed template integers')
        self.low=low;self.p=P.r.ports(low);self.K=max(16,low+11)
        self.grant_a,self.grant_r,self.r_guide=low+7,low+8,low+9
        self.return_role=self.K-1
        self.control,self.phase= self.K,self.K+1
        self.input_relay,self.a_relay,self.r_relay,self.output_relay=range(self.K+2,self.K+6)
        self.depth,self.width,self.high=range(self.K+6,self.K+9)
        self.a=m.Assembler(self.K+9);self.fail=self.a.fresh('invalid_physical_contract')
        self.events={};self.q=q;self.dimension=dimension

    def mark(self,name):
        self.events[name]=len(self.a.instructions)

    def expect(self,tape,value):
        ok=self.a.fresh('expected');self.a.branch(tape,{value:ok},self.fail);self.a.label(ok)

    def emit(self,tape,symbol):
        self.a.write(tape,symbol);self.a.move(tape,1)

    def origin(self,tape,marker=LEFT):
        loop,done=self.a.fresh('origin'),self.a.fresh('at_origin')
        self.a.move(tape,-1);self.a.label(loop);self.a.branch(tape,{marker:done},loop+'_more')
        self.a.label(loop+'_more');self.a.move(tape,-1);self.a.goto(loop)
        self.a.label(done);self.a.move(tape,1)

    def body(self,tape,marker=LEFT):
        self.origin(tape,marker)
        for _ in range(3):self.a.move(tape,1)

    def retire(self,tape,marker=LEFT):
        self.origin(tape,marker)
        loop,end=self.a.fresh('retire'),self.a.fresh('retired')
        more=self.a.fresh('retire_binary');self.a.label(loop)
        self.a.branch(tape,{Z:more,O:more,BL:end},self.fail)
        self.a.label(more);self.emit(tape,BL);self.a.goto(loop)
        self.a.label(end);self.origin(tape,marker)

    def copy(self,source,target,source_marker=LEFT,target_marker=LEFT):
        self.origin(source,source_marker);self.origin(target,target_marker);self.expect(target,BL)
        loop,end=self.a.fresh('copy'),self.a.fresh('copied');self.a.label(loop)
        labels={v:self.a.fresh('copy_bit')for v in (Z,O)}
        self.a.branch(source,{**labels,BL:end},self.fail)
        for bit,label in labels.items():
            self.a.label(label);self.expect(target,BL);self.emit(target,bit);self.a.move(source,1);self.a.goto(loop)
        self.a.label(end);self.origin(source,source_marker);self.origin(target,target_marker)

    def code_write(self,tape,symbol):
        for shift in (2,1,0):self.emit(tape,O if symbol>>shift&1 else Z)
        for _ in range(3):self.a.move(tape,-1)

    def code_move(self,tape,direction):
        if direction==1:
            blank,ready=self.a.fresh('materialize_blank'),self.a.fresh('cross_code')
            self.a.branch(tape,{BL:blank,Z:ready,O:ready},self.fail)
            self.a.label(blank);self.code_write(tape,m.BLANK)
            self.a.label(ready)
        for _ in range(3):self.a.move(tape,direction)

    def code_branch(self,tape,cases,default):
        """Three bit choices are finite control, never a decoded runtime int."""
        a=self.a;root=a.fresh('code_root');a.goto(root)
        labels={(n,v):a.fresh('code_bits')for n in range(4)for v in range(1<<n)}
        a.label(root)
        a.branch(tape,{BL:cases.get(m.BLANK,default),Z:labels[1,0],O:labels[1,1]},self.fail)
        for n in (1,2):
            for value in range(1<<n):
                a.label(labels[n,value]);a.move(tape,1)
                a.branch(tape,{Z:labels[n+1,2*value],O:labels[n+1,2*value+1]},self.fail)
        for value in range(8):
            a.label(labels[3,value]);a.move(tape,-1);a.move(tape,-1)
            a.goto(cases.get(value,default)if value<7 else self.fail)

    def logical(self,program,ports,continuation,name):
        """Statically lower an entire fixed table, including its continuations."""
        labels=[self.a.fresh(name+'_pc')for _ in program.instructions]
        self.a.goto(labels[program.entry])
        for i,row in enumerate(program.instructions):
            self.a.label(labels[i]);op=row[0]
            if op=='branch':self.code_branch(ports[row[1]],{s:labels[k]for s,k in row[2]},labels[row[3]])
            elif op=='write':self.code_write(ports[row[1]],row[2])
            elif op=='move':self.code_move(ports[row[1]],row[2])
            elif op=='goto':self.a.goto(labels[row[1]])
            elif op=='halt':self.a.goto(continuation)
            else:self.a.goto(self.fail)

    def push(self):
        a=self.a;c=self.control;self.mark('push_begin')
        self.expect(c,BL);self.emit(c,LEFT)
        for t in range(self.K):
            self.emit(c,Z if t==self.return_role else O)
            a.move(t,-1);loop,done=a.fresh('save_head'),a.fresh('head_saved');more=a.fresh('head_digit')
            a.label(loop);a.branch(t,{LEFT:done,Z:more,O:more},self.fail)
            a.label(more);self.emit(c,O);a.move(t,-1);a.goto(loop)
            a.label(done);self.emit(c,Z);a.move(t,1)
            scan,park=a.fresh('park_parent'),a.fresh('parent_parked');step=a.fresh('parent_digit')
            a.label(scan);a.branch(t,{Z:step,O:step,BL:park},self.fail)
            a.label(step);a.move(t,1);a.goto(scan)
            a.label(park);self.emit(t,LEFT)
        self.emit(c,SEP)
        loop,end=a.fresh('save_phase'),a.fresh('phase_saved');a.label(loop)
        labels={v:a.fresh('phase_bit')for v in (Z,O)};a.branch(self.phase,{**labels,BL:end},self.fail)
        for bit,label in labels.items():
            a.label(label);self.emit(c,bit);self.emit(self.phase,BL);a.goto(loop)
        a.label(end);self.origin(self.phase,BASE);self.emit(c,END);self.mark('push_end')

    def pop(self):
        a=self.a;c=self.control;self.mark('pop_begin');self.retire(self.phase,BASE)
        a.move(c,-1);self.expect(c,END);a.move(c,-1)
        scan,first=a.fresh('frame_start'),a.fresh('frame_found');back=a.fresh('frame_back')
        a.label(scan);a.branch(c,{LEFT:first,Z:back,O:back,SEP:back},self.fail)
        a.label(back);a.move(c,-1);a.goto(scan);a.label(first);self.emit(c,BL)
        for t in range(self.K):
            self.expect(c,Z if t==self.return_role else O);self.emit(c,BL)
            self.expect(t,BL);a.move(t,-1);self.expect(t,LEFT);a.write(t,BL);a.move(t,-1)
            self.origin_from_inside(t)
            loop,more,end=a.fresh('restore_head'),a.fresh('head_move'),a.fresh('head_restored')
            a.label(loop);a.branch(c,{O:more,Z:end},self.fail)
            a.label(more);ok=a.fresh('parent_head_digit');a.branch(t,{Z:ok,O:ok},self.fail)
            a.label(ok);a.move(t,1);self.emit(c,BL);a.goto(loop)
            a.label(end);self.emit(c,BL)
        self.expect(c,SEP);self.emit(c,BL)
        loop,end=a.fresh('restore_phase'),a.fresh('phase_done');a.label(loop)
        labels={v:a.fresh('restore_bit')for v in (Z,O)};a.branch(c,{**labels,END:end},self.fail)
        for bit,label in labels.items():
            a.label(label);self.emit(self.phase,bit);self.emit(c,BL);a.goto(loop)
        a.label(end);a.write(c,BL);a.move(c,-1)
        scan,done=a.fresh('previous_top'),a.fresh('at_top');a.label(scan)
        a.branch(c,{BASE:done,END:done,BL:scan+'_left'},self.fail)
        a.label(scan+'_left');a.move(c,-1);a.goto(scan);a.label(done);a.move(c,1)
        self.origin(self.phase,BASE);self.mark('pop_end')

    def origin_from_inside(self,tape):
        a=self.a;loop,done=a.fresh('parent_origin'),a.fresh('parent_origin_found')
        a.label(loop);a.branch(tape,{LEFT:done,Z:loop+'_left',O:loop+'_left'},self.fail)
        a.label(loop+'_left');a.move(tape,-1);a.goto(loop);a.label(done);a.move(tape,1)

    def compile(self):
        a=self.a;p=self.p;entry=a.fresh('node_entry');root_done=a.fresh('root_done')
        high_done=a.fresh('high_generated')
        self.logical(high_program(self.q**(self.dimension*self.dimension)),
                     {0:self.width,1:self.high,2:p['repeats'],3:p['binary_work']},high_done,'high')
        a.label(high_done)
        for t in (p['repeats'],p['binary_work']):self.retire(t)
        a.goto(entry)
        a.label(entry);self.mark('node_entry')
        split_done=a.fresh('split_done');self.logical(P.r.build(self.low),{t:t for t in range(p['count'])},split_done,'split')
        a.label(split_done);leaf=a.fresh('leaf');call0=a.fresh('call0');call1=a.fresh('call1');merge=a.fresh('merge')
        a.branch(self.depth,{BL:leaf,O:call0},self.fail)
        call_push=a.fresh('call_push')
        # Two statically selected callsites; both produce their own live grants.
        for bank,label in ((0,call0),(1,call1)):
            a.label(label);self.mark('grant_site_'+str(bank))
            done=a.fresh('grants_delivered')
            mapping={0:p['repeats_input'],1:self.high,2:p['block_input'],3:self.grant_a,4:self.grant_r,
                     5:p['repeats'],6:p['block'],7:self.r_guide,8:p['binary_work']}
            self.logical(P.build(self.low),mapping,done,'grant_'+str(bank));a.label(done)
            self.mark('grant_ready_'+str(bank))
            self.copy(bank,self.input_relay,target_marker=BASE);self.body(bank)
            for grant,relay in ((self.grant_a,self.a_relay),(self.grant_r,self.r_relay)):
                self.copy(grant,relay,target_marker=BASE);self.retire(grant)
            for t in (p['repeats'],p['block'],self.r_guide,p['binary_work']):self.retire(t)
            self.expect(self.phase,BL);self.emit(self.phase,O if bank else Z);self.origin(self.phase,BASE)
            a.goto(call_push)
        a.label(call_push);self.push()
        self.copy(self.input_relay,p['source'],source_marker=BASE);self.body(p['source'])
        for target,relay in ((p['repeats_input'],self.a_relay),(p['block_input'],self.r_relay)):
            self.copy(relay,target,source_marker=BASE);self.body(target)
        for t in (self.input_relay,self.a_relay,self.r_relay):self.retire(t,BASE)
        self.expect(self.depth,O);a.move(self.depth,1);a.goto(entry)
        # A literal complete leaf, rather than a host callback.
        a.label(leaf);self.mark('leaf');self.body(0)
        loop,done=a.fresh('complement'),a.fresh('complement_done')
        zero,one=a.fresh('leaf_zero'),a.fresh('leaf_one');a.label(loop)
        self.code_branch(0,{m.ZERO:zero,m.ONE:one,m.RIGHT:done},self.fail)
        for label,value in ((zero,m.ONE),(one,m.ZERO)):
            a.label(label);self.code_write(0,value);self.code_move(0,1);a.goto(loop)
        a.label(done);self.body(0);a.goto(merge)
        a.label(merge);merged=a.fresh('merged');self.logical(P.r.build(self.low,merge=True),{t:t for t in range(p['count'])},merged,'merge')
        a.label(merged);self.mark('node_merged')
        for t in p['banks']+(p['repeats'],p['block'],p['binary_work']):self.retire(t)
        a.move(self.control,-1);has_parent=a.fresh('has_parent');a.branch(self.control,{BASE:root_done,END:has_parent},self.fail)
        a.label(has_parent);a.move(self.control,1)
        self.mark('save_child_output')
        self.copy(p['output'],self.output_relay,target_marker=BASE)
        self.mark('retire_child')
        for t in range(self.K):self.retire(t)
        self.pop();a.move(self.depth,-1);self.expect(self.depth,O)
        self.copy(self.output_relay,self.return_role,source_marker=BASE);self.retire(self.output_relay,BASE)
        zero,one=a.fresh('resume0'),a.fresh('resume1');a.branch(self.phase,{Z:zero,O:one},self.fail)
        for bank,label in ((0,zero),(1,one)):
            a.label(label);self.retire(self.phase,BASE)
            self.retire(bank);self.copy(self.return_role,bank);self.retire(self.return_role);self.body(bank)
            a.goto(call1 if bank==0 else merge)
        a.label(root_done);a.move(self.control,1);self.mark('root_done')
        self.retire(self.high,BASE);a.halt()
        a.label(self.fail);a.reject('recursive fixed-width physical contract')
        program=a.finish()
        return program,{'L':self.low,'q':self.q,'N':self.dimension,'payloads':self.K,'tapes':self.K+9,
                        'ports':p,'grant_A':self.grant_a,'grant_R':self.grant_r,'R_guide':self.r_guide,
                        'return':self.return_role,'control':self.control,'phase':self.phase,
                        'input_relay':self.input_relay,'A_relay':self.a_relay,'R_relay':self.r_relay,
                        'output_relay':self.output_relay,'depth':self.depth,'width':self.width,'high':self.high,
                        'events':self.events}


def build(low=4,q=3,dimension=1):return Builder(low,q,dimension).compile()
