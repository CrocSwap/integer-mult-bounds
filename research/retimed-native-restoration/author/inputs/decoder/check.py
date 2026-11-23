#!/usr/bin/env python3
"""Exact source incidence, finite-alphabet codec and decoder bisimulation checks."""
import argparse
import ast
from collections import Counter,defaultdict
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
from codec import Codec,Limits,decode_packed
from source_loader import ROOT,SRC,authenticate,library,load,need,word_json


def rejected(action,label):
    try:action()
    except (ValueError,AssertionError,KeyError,ArithmeticError,StopIteration):return label
    raise AssertionError('negative control accepted: '+label)


def normalized(job):
    Axis=load()['Axis']
    if not job.axes or isinstance(job.axes[0],int):
        return [job.owner,'integer',list(job.axes)]
    need(all(isinstance(x,Axis) and x.basis==job.axes[0].basis for x in job.axes),'homogeneous basis')
    return [job.owner,word_json(job.axes[0].basis),[x.column for x in job.axes]]


def chart_incidence():
    ns=load();words,data=library();graph=ns['graph']();caller=ns['caller']();raw=ns['raw_word']
    need(len(raw.targets)==18906 and len(raw.paid)==104904,'literal port census')
    need(len(words)==595 and len(data)==215644 and max(map(len,words))==61,'fixed library constants')
    need(len(data)*8<2**21,'library bit allowance')
    fractions=[Fraction(op[-1]) for word in words for op in word if op[0] in ('add','scale')]
    max_signed=max(abs(x.numerator).bit_length()+1 for x in fractions)
    max_den=max(x.denominator.bit_length() for x in fractions)
    for word in words:
        for op,i,*args in word:
            need(op in ('add','scale','swap') and 0<=i<8 and (op=='scale' or 0<=args[0]<8),'literal base coordinates')
    need(max_signed<=16 and max_den<=16,'static coefficient fields')
    kinds=Counter();requests={}
    for paid in raw.paid:
        tag=paid.tag;kinds[tag[0]]+=1
        if tag[0]=='move':
            _,clock,site,bank=tag
            need(caller['events'][clock][0]=='LOCAL','MOVE caller incidence')
            op,dest,first,last=graph['program'][site]
            need(op=='MOVE' and dest==bank,'MOVE graph incidence')
            key=('move',first,last)
        elif tag[0]=='QUERY':
            _,clock,port=tag;need(caller['events'][clock][0]=='QUERY','QUERY incidence')
            key=('QUERY',port)
        else:
            _,clock,port=tag;need(caller['events'][clock][0]=='IDLE_ONE','IDLE incidence')
            key=('IDLE_ONE',tuple(caller['events'][clock][2]))
        old=requests.setdefault(key,paid.rank);need(old==paid.rank,'same chart rank')
    cases=0;selections=0
    for columns in (1,2,5):
        n=134*columns;c=ns['ActiveCatalogue'](n,columns)
        codec=Codec(Limits(n,24,100,100,100,20000,1))
        for key,rank in requests.items():
            if key[0]=='move':frame=c.difference(*key[1:])
            elif key[0]=='QUERY':frame=c.head(key[1])
            else:frame=c.idle(key[1])
            need(len(frame.mask)==rank*columns,'paid rank lift')
            job=ns['placed_job'](3,frame)
            need(codec.restore(codec.describe(job))==job,'literal chart roundtrip')
            for selection in (tuple(range(len(job.axes))),tuple(reversed(range(len(job.axes)))),(0,),tuple(range(0,len(job.axes),2))):
                part=job.select(selection)
                need(codec.restore(codec.describe(part))==part,'ordered selection roundtrip')
                selections+=1
            cases+=1
    # The common dictionary preserves exact signed rational coefficients.
    need(any(x<0 for x in fractions) and any(x.denominator>1 for x in fractions),'signed rational library exercised')
    return dict(paid_incidence=len(raw.paid),distinct_paid_shapes=len(requests),chart_lifts=cases,
                ordered_selections=selections,library_words=len(words),library_bytes=len(data),
                library_sha256=sha256(data).hexdigest(),maximum_word=61,
                signed_numerator_bits=max_signed,denominator_bits=max_den,paid_kinds=dict(sorted(kinds.items())))


def raw_descriptor_execution():
    """Run the literal native metadata, abstracting numerical bank payloads only."""
    ns=load();raw=ns['raw_word'];n=134
    class Banks:
        dimension=n
        def __init__(self):self.live=set();self.next=0;self.routes=0
        def zero(self):
            owner=self.next;self.next+=1;self.live.add(owner);return owner
        def retire(self,owner,**kwargs):
            need(owner in self.live,'raw retire live');self.live.remove(owner)
        def clone(self,owner):need(owner in self.live,'raw clone live');return self.zero()
        def route(self,owner,word):
            need(owner in self.live,'raw route live')
            for op,i,*args in word:
                need(0<=i<n,'route target')
                if op!='scale':need(0<=args[0]<n,'route source')
            self.routes+=1
        def xor(self,left,right):need(left in self.live and right in self.live,'raw xor live')
        def swap(self,left,right):need(left in self.live and right in self.live,'raw swap live')
    banks=Banks();inputs=[(p.tag,ns['Job'](banks.zero(),tuple(range(p.rank)))) for p in raw.targets]
    service=ns['StrongBinarySource'](banks);count=0;typed=0;unique=set()
    codec=Codec(Limits(n,24,2**24-1,1,1,len(raw.targets),1))
    for (tag,job),expected in zip(service.raw(inputs,1),raw.paid,strict=True):
        need(tag==expected.tag and len(job.axes)==expected.rank,'actual native paid label')
        need(job.owner in banks.live,'actual native owner')
        need(all(isinstance(a,ns['Axis']) for a in job.axes),'paid axes retain source basis')
        key=(job.axes[0].basis,tuple(a.column for a in job.axes))
        if key not in unique:
            unique.add(key);need(codec.restore(codec.describe(job))==job,'actual native chart codec')
        count+=1;typed+=len(job.axes)
    need(count==104904 and len(banks.live)==18906,'actual complete native descriptor return')
    return dict(paid=count,typed_axes=typed,distinct_descriptors=len(unique),routes=banks.routes,
                scope='Actual source generators, charts, masks, labels and owner existence; numerical bank actions abstracted.')


def supplied_calendar(q,ticks,replicas):
    ns=load();plan=ns['Plan'].__new__(ns['Plan']);Link,Source=ns['Link'],ns['Source']
    plan.n=128;plan.targets=(2,2);plan.paid=(1,)*q
    plan.ticks=ticks;plan.rounds=64;plan.bands=range(10,26,2)
    plan.count={e:(replicas if e in (10,24) else 0) for e in plan.bands}
    plan.delay={e:(1 if e==10 else q+1) for e in plan.bands}
    plan.send,plan.receive,plan.sources=defaultdict(list),defaultdict(list),defaultdict(list)
    plan.send[24,0].append(Link(0,replicas,10,0,0))
    plan.receive[10,0].append(Link(0,replicas,24,0,0))
    plan.source_width=2*ticks*replicas;plan.width=plan.source_width+1
    # Fully specified source periods, including a valid source which can miss the
    # round/capacity guard for later group. These are supplied-calendar fixtures.
    plan.sources[10,1].append(Source(0,replicas,0,32))
    plan.sources[24,1].append(Source(0,replicas,0,4))
    return plan


class Service:
    def __init__(self,plan,mutant=None):
        self.plan=plan;self.live=set(range(plan.width));self.vacant=[];self.capacity=plan.width
        self.events=[];self.opens=0;self.mutant=mutant;self.words=library()[0]
    def record(self,kind,*args):self.events.append([kind,*args])
    def zero(self,exemplar):
        owner=self.vacant.pop() if self.vacant else self.capacity
        if owner==self.capacity:self.capacity+=1
        self.live.add(owner);job=load()['Job'](owner,exemplar.axes)
        self.record('zero',normalized(job));return job
    def native(self,ports,columns):
        ident=self.opens;self.opens+=1
        self.record('native',columns,[normalized(job) for job in ports])
        words=self.words;ns=load();index=1+(ident%min(7,len(words)-1))
        basis=tuple(x for op in words[index] for j in range(columns)
                    for x in ns['coordinate_word']((op,),lambda k,j=j:k*columns+j))
        def body():
            for k,rank in enumerate(self.plan.paid):
                job=ns['Job'](ports[0].owner,tuple(ns['Axis'](basis,i) for i in range(rank*columns)))
                self.record('resume',ident,k,normalized(job));yield job
            self.record('native-return',ident)
        return body()
    def leaf(self,job):
        need(job.owner in self.live,'leaf owner live');self.record('leaf',normalized(job))
    def retire_zero(self,job):
        need(job.owner in self.live,'retired owner live');self.live.remove(job.owner);self.vacant.append(job.owner)
        self.record('retire',normalized(job))


def bisimulation():
    results=[];roundtrips=0
    for q,ticks,replicas in ((2,1,1),(2,3,1),(3,2,2),(4,3,2)):
        plan=supplied_calendar(q,ticks,replicas);rows=[load()['Job'](i,tuple(range(plan.n))) for i in range(plan.width)]
        C=sum(plan.count[e]*(q*plan.delay[e]+1) for e in plan.bands)
        codec=Codec(Limits(plan.n,24,plan.width+10*C,C,q*C,len(plan.targets),plan.width))
        records=list(plan.events())
        event_image=codec.pack_records(records)
        need(codec.unpack_records(event_image)==records,'literal immutable event tape')
        for group,round_no in ((0,0),(0,plan.rounds-1),(1,0)):
            original=Service(plan);packed=Service(plan)
            plan.decode(rows,round_no,group,original,iter(records))
            receipt=decode_packed(plan,rows,round_no,group,packed,iter(records),codec)
            need(original.events==packed.events,'source and packed traces differ')
            need(original.live==packed.live==set(range(plan.width)),'complete fixture return')
            need(original.capacity==packed.capacity,'allocator chronology')
            need(receipt['max_live']<=C and receipt['max_pending']<=q*C,'inclusive capacities')
            digest=sha256(json.dumps(original.events,separators=(',',':')).encode()).hexdigest()
            results.append(dict(q=q,ticks=ticks,replicas=replicas,group=group,round_no=round_no,
                                trace_sha256=digest,service_actions=len(original.events),**receipt))
            roundtrips+=receipt['roundtrips']
    return dict(fixtures=results,event_roundtrips=roundtrips)


def controls():
    ns=load();codec=Codec(Limits(256,24,1000,1000,1000,20000,1));Job,Axis=ns['Job'],ns['Axis']
    word=library()[0][1];basis=codec.lift(1,2);job=Job(5,tuple(Axis(basis,a) for a in (7,2,0)))
    names=[]
    names.append(rejected(lambda:codec.describe(Job(-1,(0,))),'negative-owner'))
    names.append(rejected(lambda:codec.describe(Job(0,(256,))),'ambient-overflow'))
    names.append(rejected(lambda:codec.lift(1,256),'basis-coordinate-overflow'))
    names.append(rejected(lambda:codec.describe(Job(0,(0,Axis(basis,1)))),'mixed-axis-kinds'))
    names.append(rejected(lambda:codec.describe(Job(0,(Axis((('scale',0,Fraction(7,11)),),0),))),'unlisted-rational-basis'))
    image=codec.pack([Job(0,tuple(range(256)))],{8:(0,[Job(1,(0,1))])},{9:job},0,0)
    names.append(rejected(lambda:codec.unpack((image[0][:-1],image[1])),'truncated-state'))
    names.append(rejected(lambda:Codec(Limits(256,2,1000,1000,1000,20000,1)),'underwidth-header'))
    # These changes are accepted valid states but alter the source observation.
    d=codec.describe(job);sorted_job=codec.restore((*d[:-1],tuple(sorted(d[-1]))))
    need(normalized(sorted_job)!=normalized(job),'sorted-axis negative control')
    names.append('sorting-ordered-mask-changes-observation')
    rows,live,pending,g,r=codec.unpack(image)
    missing=codec.pack(rows,{8:(0,[])},pending,g,r)
    need(missing!=image,'omitted-zero-list negative control');names.append('omitted-zero-list-changes-state')
    # Genuine source mutation: serving the borrowed prefix too changes the call trace.
    plan=supplied_calendar(2,2,1);rows=[Job(i,tuple(range(plan.n))) for i in range(plan.width)]
    original=Service(plan);plan.decode(rows,0,0,original,plan.events())
    tree=ast.parse((SRC/'transport.py').read_text());klass=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='Plan')
    method=next(n for n in klass.body if isinstance(n,ast.FunctionDef) and n.name=='decode')
    changes=0
    for node in ast.walk(method):
        if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id=='range' and len(node.args)==2 and isinstance(node.args[0],ast.Name) and node.args[0].id=='selected':
            node.args[0]=ast.Constant(0);changes+=1
    need(changes==1,'precise source mutation')
    ast.fix_missing_locations(method);scope={'axes':ns['axes']}
    exec(compile(ast.Module([method],type_ignores=[]),'mutated-source-decode','exec'),scope)
    changed=Service(plan);scope['decode'](plan,rows,0,0,changed,plan.events())
    need(changed.events!=original.events,'selected-prefix source mutant');names.append('actual-source-serves-borrowed-prefix')
    return names


def symbolic_budget():
    # These are exact lemma base cases and coefficient checks. They are not
    # finite substitutes for the induction and all-h argument in PROOF.md.
    P,q=18906,104904
    need(P<2**15 and q<2**17,'fixed word sizes')
    need(9**2>=4*2**2,'exponential domination base')
    for n in range(2,200):need(9*n*n>=(n+1)**2,'domination induction coefficient')
    # Production height permits all small constants below N/1024.
    for h in (3000,5610,9100):
        N=1<<h;B=N**92;C=2*N**83;w=128*h;J=4*w+1+N*h
        state=5*w+B*J+C*(3*w+P*J)+(q*C)*(w+J)
        event_tape=w+2*N**88*(5+4*P+5*q)*w
        transfer=(2*P+8)*J+(4*P+20)*w+256*N*h
        total=2*state+event_tape+transfer+2**21
        need(J<2*N*h and state<3*B*N*h and event_tape<B*N*h,'written intermediate bounds')
        need(total<32*B*N*h,'complete local descriptor allowance')
        need(4*N*h<=4*N*N,'h<=N')
    # Full population/history inequality after the geometric source shrink.
    from fractions import Fraction as Q
    need(sum(2**k for k in range(1,8))==254,'seven-stage weights')
    need(Q(32768,32767)<2 and 2*254*9==4572,'ancestor history coefficient')
    return dict(checked_heights=[3000,5610,9100],local_bits='32 B N h',same_stage_bytes='<2 W',seven_stage_bytes='<4572 Xmax',induction_bases=198)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path);args=parser.parse_args()
    authenticate()
    result=dict(status='PASS_RETIMED_DECODER_CONTROL',chart=chart_incidence(),raw=raw_descriptor_execution(),decoder=bisimulation(),negative_controls=controls(),budget=symbolic_budget(),
                scope='Decoder-owned values and immutable calendar/library only; native service bodies, full headers, runtime tariff and complete tape realization excluded.')
    payload=json.dumps(result,indent=2,sort_keys=True)+'\n'
    if args.output:args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(payload)
    print(json.dumps({'status':result['status'],'paid_incidence':result['chart']['paid_incidence'],'chart_lifts':result['chart']['chart_lifts'],'event_roundtrips':result['decoder']['event_roundtrips'],'negative_controls':len(result['negative_controls'])},sort_keys=True))

if __name__=='__main__':main()
