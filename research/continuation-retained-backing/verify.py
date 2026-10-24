#!/usr/bin/env python3
"""Literal source tests for complete continuation-bank retained backing."""
import argparse
from contextlib import contextmanager
from dataclasses import dataclass
import hashlib
import itertools
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from capacity import Cut,Node,capacities,coarse_grant,compact_peak,extents,need
from load import activate
stack,output,adapter,streams,compact=activate()
Tape,Stack=stack.Tape,stack.Stack
BASE,LEFT,BLANK=stack.BASE,stack.LEFT,stack.BLANK


def bits(n,salt=0):return tuple((i+i//3+salt)%2 for i in range(n))


def load(tape,data,head=0,marker=LEFT):
    for bit in data:stack.emit(tape,bit)
    stack.rewind(tape,marker)
    for _ in range(head):tape.move(1)


def snapshot(tape):
    cells=list(tape.cells)
    while cells and cells[-1]==BLANK:cells.pop()
    return cells,tape.head


class Guard:
    def __init__(self,tapes,limits):
        self.tapes=tuple(tapes);self.limits=tuple(limits);self.writes=0

    @contextmanager
    def installed(self):
        original=Tape.write;guard=self
        by_id={id(t):i for i,t in enumerate(self.tapes)}
        def write(tape,value):
            i=by_id[id(tape)];before=len(tape.cells);head=tape.head
            need(max(before,head+1)<=guard.limits[i],'Prospective per-tape backing grant')
            original(tape,value)
            need(len(tape.cells)==max(before,head+1),'Monotone write-only backing semantics')
            guard.writes+=1
        Tape.write=write
        try:yield
        finally:Tape.write=original


@dataclass(frozen=True)
class Case:
    sizes: tuple
    heads: tuple
    descriptor: int=0
    children: tuple=()
    output: int=0
    slot: int=1
    scratch: tuple=()
    descriptor_scratch: int=0

    def model(self):
        k=len(self.sizes);peak=list(self.sizes)
        if self.scratch:peak=[max(a,b) for a,b in zip(peak,self.scratch)]
        peak[self.slot]=max(peak[self.slot],self.output)
        if self.children:peak[0]=max(peak[0],max(c.output for c in self.children))
        return Node(tuple(peak),max(self.descriptor,self.descriptor_scratch),
                    tuple(Cut(self.sizes,self.heads,self.descriptor,c.model()) for c in self.children),self.output)


def bank(k,prefix=0,warm=()):
    meter=stack.Counts()
    tapes=[Tape(bits(prefix,i),counts=meter) for i in range(k)]
    tapes += [Tape(bits(prefix+3),BASE,meter),Tape((),BASE,meter),Tape(bits(prefix+5),BASE,meter)]
    origins=tuple(t.head for t in tapes)
    for t,n in zip(tapes,warm):t.cells.extend([BLANK]*n)
    return tapes,origins,meter


def execute(case,tapes):
    p=tapes[:-3];c,d,r=tapes[-3:];k=len(p)
    if case.scratch:
        for j,n in enumerate(case.scratch):load(p[j],bits(n,j));output.retire(p[j])
    if case.descriptor_scratch:
        load(d,bits(case.descriptor_scratch),marker=BASE);stack.clear_descriptor(d)
    for j,(n,h) in enumerate(zip(case.sizes,case.heads)):load(p[j],bits(n,j),h)
    load(d,bits(case.descriptor),marker=BASE)
    for child in case.children:
        need(case.sizes[0]==case.heads[0]==0,'Reserved empty parent output')
        before=[snapshot(t) for t in tapes]
        Stack(p,c,d).push([True]*k)
        execute(child,tapes)
        state=output.return_output(p,c,d,r,child.slot,0)
        need(state==[(True,s,h) for s,h in zip(case.sizes,case.heads)],'Decoded parked role metadata')
        expected=list(before);old,head=expected[0];expected[0]=(old+list(bits(child.output,child.slot)),head)
        need([snapshot(t) for t in tapes]==expected,'Complete returned payload/head/descriptor/prefix state')
        output.retire(p[0])
    for t in p:output.retire(t)
    load(p[case.slot],bits(case.output,case.slot))


def envelopes(node):
    """Independent scalar path envelopes for the coarse sufficient grant."""
    volume=depth=descpath=descmax=outmax=0
    def visit(n,parked,level,ds):
        nonlocal volume,depth,descpath,descmax,outmax
        volume=max(volume,parked+sum(n.peaks));depth=max(depth,level)
        descpath=max(descpath,ds);descmax=max(descmax,n.descriptor_peak)
        for cut in n.cuts:
            outmax=max(outmax,cut.child.output)
            visit(cut.child,parked+sum(cut.sizes),level+1,ds+cut.descriptor)
    visit(node,0,0,0)
    return volume,depth,descpath,descmax,outmax


def history(cases,prefix=0,warm=()):
    k=len(cases[0].sizes);tapes,origins,meter=bank(k,prefix,warm)
    entry=tuple(len(t.cells) for t in tapes);start=[snapshot(t) for t in tapes]
    growth=(0,)*(k+3);totals=[];writes=0
    for case in cases:
        model=case.model();growth=tuple(map(max,growth,extents(model,k)))
        expected=capacities(origins,entry,growth);guard=Guard(tapes,expected)
        with guard.installed():
            execute(case,tapes)
            for tape in tapes[:-3]:output.retire(tape)
            stack.clear_descriptor(tapes[-2])
        actual=tuple(len(t.cells) for t in tapes)
        need(actual==expected,'Exact tree/history per-tape retained capacities')
        need([snapshot(t) for t in tapes]==start,'All root contents and heads restored')
        env=envelopes(model)
        # Coarse grant applies to a whole history: retain coordinatewise maxima
        # of scalar envelopes, rather than only this invocation's envelope.
        if len(totals)==0:historical_env=env
        else:historical_env=tuple(map(max,historical_env,env))
        need(sum(actual)<=coarse_grant(k,sum(entry),*historical_env),'Complete coarse history grant')
        totals.append(sum(actual));writes+=guard.writes
    return {'totals':totals,'capacities':list(actual),'writes':writes,'growth':list(growth)}


def child(k,role,n,desc=0,output_len=0):
    scratch=[0]*k;scratch[role]=n
    return Case((0,)*k,(0,)*k,desc,output=output_len,slot=role,scratch=tuple(scratch))


def root_for(k,leaf,descriptor=0):
    return Case((0,)*k,(0,)*k,descriptor,(leaf,))


def census():
    rows=[]
    for sizes in itertools.product(range(3),repeat=2):
      parent=(0,)+sizes
      for heads in itertools.product(*(range(n+1) for n in sizes)):
       for d,q,length in itertools.product(range(3),range(2),range(3)):
        leaf=child(3,2,4,q,length)
        case=Case(parent,(0,)+heads,d,(leaf,))
        rows.append(history([case],prefix=3))
    return {'cases':len(rows),'writes':sum(r['writes'] for r in rows)}


def discriminators():
    k=16;n=64
    cases=[root_for(k,child(k,j,n)) for j in range(k)]
    rotated=history(cases)
    fresh=[history([case])['totals'][0] for case in cases]
    need(rotated['totals'][-1]>max(fresh),'Reject maximum standalone total')
    need(rotated['totals']==sorted(set(rotated['totals'])),'Each rotated role retains additional backing')
    tiny=root_for(k,child(k,1,1,output_len=1))
    erased=root_for(k,child(k,1,4096,output_len=1))
    tiny_row=history([tiny]);erased_row=history([erased])
    need(erased_row['totals'][0]>tiny_row['totals'][0]+4000,'Erased child interior is not a boundary extent')
    warm=history([tiny],warm=(500,)*(k+3))
    need(warm['totals'][0]>=19*500,'Entry backing cannot be discarded')
    chain=[]
    for depth in (1,2,8,31):
        node=child(k,1,0)
        for _ in range(depth):node=Case((0,64)+(0,)*14,(0,)*k,32,(node,))
        row=history([node]);chain.append({'depth':depth,'total':row['totals'][0],'capacities':row['capacities']})
    need(chain[-1]['total']>10*chain[0]['total'],'Local linear bills do not bound recursive backing')
    zero=root_for(k,child(k,1,0))
    zero_row=history([zero])
    need(sum(zero_row['growth'])==k+2*k+3,'Empty frame still needs payload delimiters and complete control header')
    descriptor_only=root_for(k,child(k,1,0),descriptor=2048)
    descriptor_row=history([descriptor_only])
    need(descriptor_row['growth'][-3]==2*k+3+2048 and descriptor_row['growth'][-2]==2048,
         'Control copy and descriptor backing are separate coordinates')
    unequal=Case((0,7,2),(0,5,1),11,(
        Case((0,3,9),(0,2,7),5,(child(3,1,17,13,6),),output=4,slot=2),
        child(3,1,21,7,8)),output=3,slot=1,descriptor_scratch=29)
    nested_unequal=history([unequal],prefix=23)
    leaf=child(k,1,128,output_len=128)
    relay=[]
    for depth in (1,2,8):
        node=leaf
        for _ in range(depth):node=Case((0,)*k,(0,)*k,children=(node,),output=128)
        row=history([node]);need(row['growth'][-1]==128,'Shared relay uses history maximum, not depth sum');relay.append(row['capacities'][-1])
    return {'rotation':rotated,'fresh_totals':fresh,'erased_interior':erased_row,
            'same_boundary_tiny_interior':tiny_row,'warm_entry':warm,
            'chains':chain,'empty_frame':zero_row,'descriptor_copy':descriptor_row,
            'unequal_siblings':nested_unequal,'shared_relay_capacities':relay}


def source_case(prefix,late,peak_override=None):
    k=16;a=adapter.Arena([bits(prefix,j) for j in range(k)],bits(prefix+3))
    relay=Tape(bits(prefix+5),BASE,a.counts);tapes=(*a.payloads,a.control,a.descriptor,relay)
    origins=tuple(t.head for t in tapes);entry=tuple(len(t.cells) for t in tapes)
    fields=(('u',1),('t',1))+((('y',2),('x',2)) if late else (('x',2),('y',2)))+(('b',1),)
    layout=compact.Layout(fields,8);word=compact.Compact(1,1,1,0,'x','y',late)
    maximum=compact_peak(layout.bits,layout.record_bits)
    if peak_override is not None:maximum=peak_override
    sizes=(0,)+tuple(j+2 for j in range(1,k));heads=(0,)+tuple(j//2 for j in range(1,k))
    leaf=Node((maximum,)*k,17,output=1024)
    model=Node((1024,)+sizes[1:],43,(Cut(sizes,heads,43,leaf),))
    limits=capacities(origins,entry,extents(model,k));guard=Guard(tapes,limits)
    saved=(streams.Tape,compact.Tape)
    streams.Tape=compact.Tape=a.tape
    try:
        with guard.installed():
            parents=[a.tape(streams.Meter(),bits(n,j)) for j,n in enumerate(sizes)]
            for j,role in enumerate(parents):role.read(heads[j])
            a.set_descriptor(bits(43));before=[snapshot(t) for t in tapes]
            a.stack.push(a.present);a.present=[False]*k;a.sizes=[0]*k;a.heads=[0]*k;a.depth+=1
            raw=bytes(b for i in range(layout.records) for b in streams.bit_key(i,8))
            source=a.tape(streams.Meter(),raw);result=compact.execute(source,layout,word)
            expected=bytearray(len(raw))
            for i in range(layout.records):
                j=layout.encode(word.ideal(layout.decode(i),True))
                expected[j*8:(j+1)*8]=raw[i*8:(i+1)*8]
            need(bytes(result.data)==expected,'Independent complete compact endpoint')
            a.set_descriptor(bits(17));start=a.counts.total
            output.return_output(a.payloads,a.control,a.descriptor,relay,result.slot,0)
            need(a.counts.total-start==24388,'Unchanged complete source return invoice')
            wanted=list(before);old,h=wanted[0];wanted[0]=(old+list(expected),h)
            need([snapshot(t) for t in tapes]==wanted,'Complete source return state')
    finally:streams.Tape,compact.Tape=saved
    return {'prefix':prefix,'late':late,'records':layout.records,'record_bits':8,
            'per_role_local_bound':maximum,'capacities':[len(t.cells) for t in tapes],
            'grants':list(limits),'writes':guard.writes,'return_steps':24388,
            'output_sha256':hashlib.sha256(expected).hexdigest()}


def controls():
    rejected=[]
    # An actual too-small grant rejects before its offending source write.
    case=root_for(2,child(2,1,17));tapes,origins,_=bank(2)
    caps=list(capacities(origins,origins,extents(case.model(),2)));caps[1]-=1
    try:
        with Guard(tapes,caps).installed():execute(case,tapes)
    except ValueError as e:need(str(e)=='Prospective per-tape backing grant','Specific quota rejection');rejected.append('one_cell_short')
    else:raise ValueError('short grant accepted')
    # read and move do not allocate, including well beyond the written end.
    t=Tape();old=len(t.cells)
    for _ in range(100):t.move(1);t.read()
    need(len(t.cells)==old,'Reads/moves do not allocate')
    t.write(BLANK);need(len(t.cells)==t.head+1,'Blank writes allocate')
    rejected.append('blank_write_is_not_free_storage')
    try:source_case(0,False,1024)
    except ValueError as e:
        need(str(e)=='Prospective per-tape backing grant','Keyed source exceeds payload-only grant')
        rejected.append('omitted_actual_source_keys')
    else:raise ValueError('payload-only compact grant accepted')
    case=root_for(2,child(2,1,7,output_len=7));tapes,origins,_=bank(2)
    caps=list(capacities(origins,origins,extents(case.model(),2)));caps[-1]=origins[-1]
    try:
        with Guard(tapes,caps).installed():execute(case,tapes)
    except ValueError as e:
        need(str(e)=='Prospective per-tape backing grant','Relay is separately allocated')
        rejected.append('omitted_relay')
    else:raise ValueError('relay-free grant accepted')
    for bad in (Node((-1,0),0),Node((0,0),-1),Node((0,0),0,(Cut((0,0),(1,0),0,Node((0,0),0)),))):
        try:extents(bad,2)
        except ValueError:rejected.append('malformed_model')
        else:raise ValueError('bad model accepted')
    return rejected


def run():
    source=[source_case(prefix,late) for late in (False,True) for prefix in (0,257,4096)]
    return {'status':'PASS_CONTINUATION_RETAINED_BACKING','census':census(),
            'discriminators':discriminators(),'source':source,'controls':controls()}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--emit',action='store_true');args=p.parse_args()
    result=run()
    if not args.emit:
        expected=json.loads((HERE/'RESULT.json').read_text())
        need(json.dumps(result,sort_keys=True,separators=(',',':'))==json.dumps(expected,sort_keys=True,separators=(',',':')),
             'Complete typed deterministic receipt')
    print(json.dumps(result,indent=2,sort_keys=True))
