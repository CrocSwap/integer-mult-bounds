#!/usr/bin/env python3
"""Actual-cohort, whole-query lifecycle and independent table checks. Apache-2.0."""
from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE))
from query_machine import *

def check(condition,message):
    if not condition:raise RuntimeError(message)

def rejects(operation,reason):
    try:operation()
    except ValueError as error:
        check(str(error)==reason,'precise rejection: '+str(error));return
    raise RuntimeError('invalid case accepted: '+reason)

def authenticate():
    manifest=HERE/'SOURCES.json'
    for row in json.loads(manifest.read_text())['files']:
        if row['usage']=='input':check(sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256'],'source '+row['path'])
    controller=json.loads((ROOT/'research/joint-helper-lattice/CONTROLLER.json').read_text())
    events=controller['physical_events'] if 'physical_events' in controller else controller['events']
    check(events[5]==['QUERY_SHEAR',2,0,False],'actual event5')
    result=json.loads((ROOT/'research/pr4470-owned-query-charges/RESULT.json').read_text())
    site=next(s for s in result['sites'] if s['event_index']==5)
    check(site['source_role']==0 and site['destination_role']==1,'actual owners')
    phases=json.loads((ROOT/'research/kappa-0023-productive-jobs/dependencies/kappa-next-regime/direct-decoder/sources/DATA-PHASES.json').read_text())
    q=phases['recipes'][0]['q'];check(q>0 and q.bit_count()%2==1,'actual port0 norm-one direction')
    return {'event':5,'stage':2,'pair':0,'port':0,'q':q,'f':2,'spectator_axes':1}

def plus(x,y):return x[0]+y[0],x[1]+y[1]
def times(x,y):return x[0]*y[0]-x[1]*y[1],x[0]*y[1]+x[1]*y[0]
A=(F(1,2),F(1,2));B=(F(1,2),F(-1,2))

def child_interval(values):
    # Finite semantic stand-in for completed charts/positive child/T_f only.
    rows=list(values)
    for axis in (0,1):
        rows=[plus(times(A,row),times(B,rows[i^(1<<axis)])) for i,row in enumerate(rows)]
    return [rows[i^3] for i in range(len(rows))]

def inverse_oracle(values):
    # Separate subset convolution, not sequential child-axis execution.
    result=[]
    for i in range(len(values)):
        value=(F(0),F(0))
        for mask in range(4):
            coefficient=(F(1),F(0))
            for axis in (0,1):coefficient=times(coefficient,A if mask>>axis&1 else B)
            value=plus(value,times(coefficient,values[i^mask]))
        result.append(value)
    return result

class Dense:
    def __init__(self,body,head=1):self.cells=list(body);self.head=head
    def read(self):return self.cells[self.head] if self.head<len(self.cells) else BLANK
    def write(self,value):
        while len(self.cells)<=self.head:self.cells.append(BLANK)
        self.cells[self.head]=value
    def step(self,direction):self.head+=direction;check(self.head>=0,'dense boundary')

def independent(table,ports):
    cursor=0;steps=0
    while table[cursor][0]!='halt':
        instruction=table[cursor];kind=instruction[0];steps+=1
        if kind=='reject':raise ValueError(instruction[1])
        if kind=='goto':cursor=instruction[1];continue
        tape=ports[instruction[1]]
        if kind=='branch':
            cursor=instruction[3]
            for symbol,target in instruction[2]:
                if tape.read()==symbol:cursor=target;break
            continue
        if kind=='move':tape.step(instruction[2])
        elif kind=='write':tape.write(instruction[2])
        else:raise RuntimeError('dense instruction')
        cursor+=1
    return steps+1

def run():
    binding=authenticate();tables=build(ROOT)
    check(tuple(map(len,tables))==(243,248),'fixed finite table sizes')
    sys.path.insert(0,str(ROOT/'research/physical-gaussian-tensor'))
    import tensor_sources
    receipts=[];controls=[]
    with tensor_sources.opened():
        from records import Tape
        from cardinal_counts import Count
        from ring_words import Signed,write_signed,read_signed
        def encode(values,p):
            tape=Tape();width=Count.literal(p)
            try:
                for number in values:
                    check(F(number).denominator==1,'exact child grid representability')
                    number=int(number);value=Signed(Count.literal(abs(number)),number<0)
                    try:write_signed(value,tape,width)
                    finally:value.close()
            finally:width.close()
            tape.rewind();return tape
        def decode(tape,p,count):
            width=Count.literal(p);out=[]
            try:
                for _ in range(count):
                    value=read_signed(tape,width);n=0;k=0
                    try:
                        while value.magnitude.read()!=RIGHT:
                            n|=value.magnitude.read()<<k;k+=1;value.magnitude.step(1)
                        out.append(-n if value.negative else n)
                    finally:value.close()
                check(tape.read()==BLANK,'complete actual field')
            finally:width.close();tape.rewind()
            return out
        def flat(values):return [component for row in values for component in row]
        def field(tape,p,m):
            values=decode(tape,p,2*m);return list(zip(values[::2],values[1::2]))
        def ports(x,y,p):
            check(len(x)==len(y),'whole-field dimensions')
            m=len(x)
            return [encode(flat(x),p),encode(flat(y),p),encode([-1]*(2*m),p),
                    Count.literal(p).tape,Count.literal(m).tape,Tape(),Tape(),Tape()]
        def snapshot(ts):return [(bytes(t.cells),t.head) for t in ts]
        def erase_baseline(ts):
            return all(t.head==1 and all(v==BLANK for v in t.cells[1:]) for t in (ts[Z],ts[W],ts[M],ts[T]))
        def replace_child(tape,values,p):
            # Caller retains SAME physical owner. All work here belongs to named child.
            result=encode(flat(values),p)
            tape.clear()
            while result.read()!=BLANK:
                tape.append(result.read());result.step(1)
            tape.rewind()
        def observe(ts):
            ranges=[[t.head,t.head] for t in ts]
            for i,t in enumerate(ts):
                for name in ('read','write','step'):
                    original=getattr(t,name)
                    def watched(*args,original=original,t=t,i=i):
                        ranges[i][0]=min(ranges[i][0],t.head)
                        ranges[i][1]=max(ranges[i][1],t.head)
                        value=original(*args)
                        ranges[i][0]=min(ranges[i][0],t.head)
                        ranges[i][1]=max(ranges[i][1],t.head)
                        return value
                    setattr(t,name,watched)
            return ranges
        def lifecycle(p,offset=0):
            x=[(4*((i+offset)%3-1),4*((i+offset)%2)) for i in range(8)]
            y=[(i-3,2-i) for i in range(8)]
            ts=ports(x,y,p);before=snapshot([ts[X],ts[WD],ts[MD]])
            helper=encode([3,-2]*8,p);helper_before=snapshot([helper])
            initial_backing=sum(len(t.cells) for t in ts)
            visited=observe(ts)
            dense=[Dense(t.cells,t.head) for t in ts]
            invocation=Invocation(ts,tables);invocation.prepare()
            dense_steps=independent(tables[0],dense)
            check(snapshot(ts)==[(bytes(t.cells),t.head) for t in dense],'independent prepare')
            check(field(ts[Z],p,8)==x,'whole source COPY')
            response=child_interval(x);expected=inverse_oracle(x)
            check(response==expected,'independent whole f2 query')
            replace_child(ts[Z],response,p)
            dense[Z]=Dense(ts[Z].cells,ts[Z].head)
            invocation.finish();dense_steps+=independent(tables[1],dense)
            check(snapshot(ts)==[(bytes(t.cells),t.head) for t in dense],'independent finish')
            check(invocation.steps==dense_steps,'independent transition count')
            check(field(ts[Y],p,8)==[plus(a,b) for a,b in zip(y,expected)],'whole query endpoint')
            check(snapshot([ts[X],ts[WD],ts[MD]])==before and erase_baseline(ts),'borrowed preservation and all owned erase')
            check(snapshot([helper])==helper_before,'independent dirty helper preserved')
            n=16*p;space=sum(len(t.cells)+1 for t in ts)
            check(invocation.steps<=256*n+256 and space<=initial_backing+8*n+32,'proved physical envelopes')
            visit_count=sum(hi-lo+1 for lo,hi in visited)
            check(visit_count<=8*n+32,'visited spans independent of entry capacity')
            receipts.append({'p':p,'records':8,'steps':invocation.steps,'visited_cells':visit_count,'entry_backing':initial_backing,'retained_backing_plus_end':space})
            return ts
        for p in (5,9,17):lifecycle(p)
        # Width beyond the optional tensor codec's4096 cap uses actual original codecs.
        ts=ports([(-1,1)],[(1,-1)],4097);inv=Invocation(ts,tables)
        inv.prepare();inv.finish()
        check(field(ts[Y],4097,1)==[(0,0)] and erase_baseline(ts),'unbounded-width ABI beyond optimization cap')
        check(inv.steps<=256*(2*4097)+256,'wide physical bill')
        receipts.append({'p':4097,'records':1,'steps':inv.steps})
        # Arbitrary entry blank capacity is retained, not called visited/new space.
        ts=ports([(-1,1)],[(1,0)],5)
        for t in ts:t.cells.extend([BLANK]*1000)
        initial=sum(len(t.cells) for t in ts);ranges=observe(ts)
        inv=Invocation(ts,tables);inv.prepare();inv.finish()
        check(sum(hi-lo+1 for lo,hi in ranges)<=8*10+32,'long blank tail is not visited')
        check(sum(len(t.cells) for t in ts)<=initial+8*10+32 and erase_baseline(ts),'entry-relative backing')
        controls.append('retained long blank entry tails')
        # Actual source codec boundaries and no wraparound in the physical ADD.
        for p in (1,2,5,12):
            high=(1<<(p-1))-1;low=-(1<<(p-1))
            ts=ports([(high,low)],[(0,0)],p);inv=Invocation(ts,tables);inv.prepare();inv.finish()
            check(field(ts[Y],p,1)==[(high,low)] and erase_baseline(ts),'signed extrema accepted')
        for p in (2,5,12):
            ts=ports([((1<<(p-1))-1,0)],[(1,0)],p);inv=Invocation(ts,tables);inv.prepare()
            rejects(inv.finish,'signed addition overflow');controls.append('positive overflow p'+str(p))
            ts=ports([(-(1<<(p-1)),0)],[(-1,0)],p);inv=Invocation(ts,tables);inv.prepare()
            rejects(inv.finish,'signed addition overflow');controls.append('negative overflow p'+str(p))
        xa=[(4*(i-3),4*(2-i)) for i in range(8)];ya=[(i,1-i) for i in range(8)]
        xb=[(-a,b+4) for a,b in xa];yb=[(-i,2+i) for i in range(8)]
        pa,pb=ports(xa,ya,9),ports(xb,yb,9)
        pair=SuspendedPair(pa,pb,tables);pair.first.prepare();held=snapshot(pa)
        pair.second.prepare();replace_child(pb[Z],child_interval(xb),9);pair.second.finish()
        check(snapshot(pa)==held,'suspended parent retains complete field and counters')
        replace_child(pa[Z],child_interval(xa),9);pair.first.finish()
        check(field(pa[Y],9,8)==[plus(a,b) for a,b in zip(ya,inverse_oracle(xa))],'parent A endpoint')
        check(field(pb[Y],9,8)==[plus(a,b) for a,b in zip(yb,inverse_oracle(xb))],'parent B endpoint')
        check(erase_baseline(pa) and erase_baseline(pb),'two private complete erasures')
        bad=list(pb);bad[Z]=pa[Z]
        rejects(lambda:SuspendedPair(pa,bad,tables),'distinct suspended parent slots');controls.append('suspended alias')
        ts=ports([(1,0)],[(0,0)],5);inv=Invocation(ts,tables);inv.prepare();ts[Z].step(1)
        rejects(inv.finish,'return field shape');controls.append('wrong child head')
        ts=ports([(1,0)],[(0,0)],5);inv=Invocation(ts,tables);inv.prepare();ts[Z]=ts[X]
        rejects(inv.finish,'fixed physical ports across child');controls.append('changed child port')
        mutant=list(tables[0])
        at=next(i for i,row in enumerate(mutant) if row==('write',Z,ZERO))
        mutant[at]=('write',X,ZERO)
        ts=ports([(-1,1)],[(0,0)],5);before=snapshot([ts[X]])
        inv=Invocation(ts,(tuple(mutant),tables[1]));inv.prepare();inv.finish()
        check(snapshot([ts[X]])!=before,'borrowed-clear physical mutant detected')
        controls.append('borrowed clear table mutation')
        ts=ports([(1,0)],[(0,0)],5);ts[X].cells[3]=BLANK
        inv=Invocation(ts,tables)
        rejects(inv.prepare,'prepare field/descriptor shape');controls.append('short source component')
        # Real table mutation: omit every private-Z erasure write.
        mutant=tuple(('goto',i+1) if row==('write',Z,BLANK) else row for i,row in enumerate(tables[1]))
        ts=ports([(1,-1)],[(0,0)],5);inv=Invocation(ts,(tables[0],mutant));inv.prepare();inv.finish()
        check(not erase_baseline(ts),'missing erasure mutant actually fails');controls.append('missing physical erase')
        # Real wrong-child control: all record checks can pass, but omitted spectator action cannot.
        expected=inverse_oracle(xa);wrong=expected[:4]+[(0,0)]*4
        check(wrong!=expected,'spectator control nontrivial')
        ts=ports(xa,ya,9);inv=Invocation(ts,tables);inv.prepare();replace_child(ts[Z],wrong,9);inv.finish()
        check(field(ts[Y],9,8)!=[plus(a,b) for a,b in zip(ya,expected)],'missed spectator rejected by semantic oracle')
        controls.append('missed spectator child semantics (not runtime-certified)')
    return {'status':'PASS_COMPLETE_PRIVATE_QUERY_STREAM','binding':binding,'fixed_instructions':[len(t) for t in tables],
            'physical_ports_per_parent':8,'receipts':receipts,'two_suspended_slots':'PASS','controls':controls,
            'scope':'local physical ABI; child/chart/translation and global precision/allocation remain contracts'}

if __name__=='__main__':
    print(json.dumps(run(),indent=2))
