#!/usr/bin/env python3
"""Verification-only simulator: host dictionaries are NOT the target TM.

Checks exact raw-operation traces of independent executable descriptions.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from pathlib import Path
from dataclasses import replace
from fractions import Fraction
import argparse,json,sys
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from source_binding import authenticate,vendor,need
from lower import compile_table,check_program

class Tape:
    def __init__(self,number,body,trace,head=0):
        self.number=number;self.cells={-1:2}|dict(enumerate(body));self.head=head
        self.trace=trace;self.visited={head}
    def read(self):
        value=self.cells.get(self.head,6)
        self.trace.append(('read',self.number,self.head,value));return value
    def write(self,value):
        self.trace.append(('write',self.number,self.head,value));self.cells[self.head]=value
    def move(self,direction):
        self.trace.append(('move',self.number,self.head,direction));self.head+=direction
        self.visited.add(self.head)

class Rows:
    def __init__(self,table):self.table=table;self.count=0
    def __getitem__(self,pc):
        self.count+=1
        if self.count>200000:raise RuntimeError('bounded reference fixture')
        return self.table[pc]

def micro(program,tapes,limit=2000000):
    """Simulator of the emitted finite δ; its Python runtime is not priced."""
    pc=program.initial;clock=0
    while True:
        node=program.states[pc];op=node[0]
        if op=='stop':return (node[1],node[2]),clock
        if clock==limit:return ('prefix',''),clock
        clock+=1
        if op=='nop':pc=node[1]
        elif op=='read':pc=node[2][tapes[node[1]].read()]
        elif op=='write':tapes[node[1]].write(node[2]);pc=node[3]
        elif op=='move':tapes[node[1]].move(node[2]);pc=node[3]
        else:raise ValueError('microprogram grammar')

def snapshot(tapes):
    return [(t.head,dict(t.cells),sorted(t.visited)) for t in tapes]

def case(machine,table,bodies,heads=None,program=None):
    p=len(bodies);heads=[0]*p if heads is None else heads
    original_trace=[];compiled_trace=[]
    a=[Tape(j,body,original_trace,heads[j]) for j,body in enumerate(bodies)]
    b=[Tape(j,body,compiled_trace,heads[j]) for j,body in enumerate(bodies)]
    rows=Rows(table)
    try:machine.execute_table(rows,a);outcome=('success','')
    except ValueError as error:outcome=('reject',str(error))
    program=compile_table(table,p) if program is None else program
    got,clock=micro(program,b)
    need(got==outcome,'same terminal label')
    need(compiled_trace==original_trace,'exact raw-operation trace')
    need(snapshot(a)==snapshot(b),'identical cells, heads and visited regions')
    need(clock==len(original_trace)+rows.count,'exact serialized TM clock C=A+U')
    return dict(outcome=outcome[0],label=outcome[1],raw_actions=len(original_trace),
                rows=rows.count,clock=clock,states=len(program.states),
                state_bound=48*len(table)+3*p+4,heads=[t.head for t in b])

def symbol(value):return [(value>>j)&1 for j in (2,1,0)]
def field(width,values):
    body=[]
    for value in values:
        for j in range(width):body.extend(symbol((value>>j)&1))
        body.extend(symbol(2))
    return body

def execute_checks():
    machine=vendor('micro_original_machine','vendor/machine.py')
    tables=vendor('micro_rounded_tables','vendor/rounded_tables.py')
    observations=[]
    read=(('branch',0,tuple((s,1) for s in range(7)),2),('halt',),('reject','branch-default'))
    for value in range(7):observations.append(case(machine,read,[symbol(value)]))
    observations.append(case(machine,read,[[]]))
    observations.append(case(machine,read,[[1,1,1]]))
    for j in range(3):
        body=[0,0,0];body[j]=3
        r=case(machine,read,[body]);need(r['heads']==[j],'partial-code rejection displacement')
        observations.append(r)
    for table,bodies,heads in [
        ((('move',0,-1),('halt',)),[[0,0,0]],None),
        ((('move',0,1),('move',0,-1),('halt',)),[[]],None),
        ((('write',0,6),('goto',3),('reject','unreachable'),('halt',)),[[0,0,0]],None),
        ((('reject','fixed-label'),),[[0,0,0]],[1]),
        ((('halt',),),[[0]*12,[1]*9],[9,6]),
    ]:observations.append(case(machine,table,bodies,heads))
    scalar=[];programs=[]
    for coefficient in ('-2/3','1/2','3/2'):
        table,metadata=tables.compile_rounded('SCALE',coefficient)
        program=compile_table(table,3);programs.append(dict(coefficient=coefficient,
            rows=len(table),states=len(program.states),bound=48*len(table)+13))
        q=Fraction(coefficient)
        for width in range(1,5):
            for value in range(-(1<<(width-1)),1<<(width-1)):
                values=[0,value] if value&1 else [value,0]
                row=case(machine,table,[field(width,values),[],[]],program=program)
                expected=(q.numerator*value+q.denominator//2)//q.denominator
                need((row['outcome']=='success')==(-(1<<(width-1))<=expected<(1<<(width-1))),
                     'independent signed rounded-output range')
                scalar.append(row)
    rejected_guards=[]
    bad=[([],1),([('halt',)],True),([('write',0,0)],1),([('move',0,True),('halt',)],1),
         ([('goto',1)],1),([('branch',True,(),0)],1),
         ([('branch',0,((0,0),(0,0)),0)],1),([('branch',0,((7,0),),0)],1),
         ([('write',0,True),('halt',)],1),([('reject',3)],1),([('host_callback',)],1)]
    for i,(table,p) in enumerate(bad):
        try:compile_table(table,p)
        except ValueError:rejected_guards.append(i)
        else:raise ValueError('static guard failed')
    # Remove the first raw blank probe: even a valid nonblank case must fail
    # exact trace/clock equivalence; this is not an alternative implementation.
    program=compile_table(read,1);states=list(program.states)
    initial_read=states[0][1];first_bit=states[initial_read][2][0]
    states[0]=('nop',first_bit);mutant=replace(program,states=tuple(states))
    mutants=[]
    try:case(machine,read,[[0,0,0]],program=mutant)
    except ValueError:mutants.append('omitted_initial_raw_probe')
    else:raise ValueError('initial-probe mutation undetected')
    left=(('move',0,-1),('halt',));program=compile_table(left,1);states=list(program.states)
    first_move=states[0][1];test=states[first_move][3];restore=states[test][2][2]
    edges=list(states[test][2]);edges[2]=states[restore][3];states[test]=('read',0,tuple(edges))
    try:case(machine,left,[[0,0,0]],program=replace(program,states=tuple(states)))
    except ValueError:mutants.append('omitted_left_origin_restoration')
    else:raise ValueError('left restoration mutation undetected')
    loop=compile_table((('goto',0),),1);trace=[];tape=Tape(0,[],trace)
    state,clock=micro(loop,[tape],limit=100)
    need(state==('prefix','') and clock==100 and not trace,'nontermination prefix, no totality claim')
    return dict(primitive_cases=len(observations),primitive_observations=observations,
        scalar_cases=len(scalar),scalar_successes=sum(x['outcome']=='success' for x in scalar),
        scalar_rejections=sum(x['outcome']=='reject' for x in scalar),scalar_programs=programs,
        exact_trace_and_clock_cases=len(observations)+len(scalar),guard_rejections=len(rejected_guards),
        detected_mutants=mutants,loop_prefix_steps=100,
        scope='Finite-control/serialized-clock equivalence only; no tariff conversion or Controller lowering.')

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write-receipt',action='store_true')
    args=parser.parse_args();authenticate();result=execute_checks()
    if args.write_receipt:(ROOT/'RESULT.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print('PASS_SCALAR_TABLE_MICROCONTROL '+json.dumps({k:result[k] for k in
        ('primitive_cases','scalar_cases','scalar_successes','scalar_rejections','guard_rejections','detected_mutants')}))
if __name__=='__main__':main()
