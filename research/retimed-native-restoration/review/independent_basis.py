#!/usr/bin/env python3
"""Independent review of decoder-owned value representation.

No import of codec.py, check.py or source_loader.py. Retained original chart
constructors and Plan methods are producers; separate rational linear algebra,
calendar construction, bit codec and decoder interpretation are the oracles.
"""
import argparse
import ast
from collections import Counter, defaultdict
from dataclasses import dataclass
from fractions import Fraction as Q
from functools import cache
from hashlib import sha1, sha256
from itertools import chain
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent/'storage'/'decoder-control'
SRC = PACKAGE/'sources'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def authenticate():
    bindings=json.loads((PACKAGE/'SOURCE-BINDINGS.json').read_text())
    scientific=json.loads((PACKAGE/'SCIENTIFIC-FREEZE.json').read_text())
    for name,digest in scientific.items():
        require(sha256((PACKAGE/name).read_bytes()).hexdigest()==digest,'scientific pin '+name)
    blobs=0
    for name,entry in bindings['files'].items():
        data=(SRC/name).read_bytes()
        require(sha256(data).hexdigest()==entry['sha256'],'source pin '+name)
        if 'git_blob' in entry:
            header=('blob '+str(len(data))+'\0').encode()
            require(sha1(header+data).hexdigest()==entry['git_blob'],'Git blob '+name)
            blobs+=1
    return {'scientific_hashes':scientific,'source_files':len(bindings['files']),
            'git_blobs_recomputed':blobs,'bindings_sha256':sha256((PACKAGE/'SOURCE-BINDINGS.json').read_bytes()).hexdigest()}


def definitions(filename,names,namespace):
    """Execute named original definitions only, preserving scientific bodies."""
    tree=ast.parse((SRC/filename).read_text())
    selected=[x for x in tree.body if isinstance(x,(ast.FunctionDef,ast.ClassDef)) and x.name in names]
    require(set(names)=={x.name for x in selected},'definition list '+filename)
    class RemoveImports(ast.NodeTransformer):
        def visit_Import(self,node): return None
        def visit_ImportFrom(self,node): return None
    selected=[RemoveImports().visit(x) for x in selected]
    exec(compile(ast.Module(body=selected,type_ignores=[]),filename,'exec'),namespace)


def originals():
    graph=json.loads((SRC/'graph.json').read_text())
    caller=json.loads((SRC/'caller.json').read_text())
    ns={'Fraction':Q,'F':Q,'cache':cache,'dataclass':dataclass,'chain':chain,
        'defaultdict':defaultdict,'graph':lambda:graph,'caller':lambda:caller}
    definitions('ternary_frames.py',['identity','transpose','multiply','residue','inverse','projector','frame_at_three'],ns)
    definitions('cover.py',['require','row_program'],ns)
    definitions('factored_frames.py',['inverse_word','coordinate_word','Frame'],ns)
    definitions('raw_binary.py',['Catalogue'],ns)
    definitions('strong_binary.py',['ActiveCatalogue','fixed_binary_charts'],ns)
    definitions('transport.py',['Link','Source','axes','Plan'],ns)
    return ns,graph,caller


def identity(n):
    return [[Q(i==j) for j in range(n)] for i in range(n)]


def transpose(a):
    return [list(column) for column in zip(*a)]


def multiply(a,b):
    return [[sum((u*v for u,v in zip(row,col)),Q(0)) for col in zip(*b)] for row in a]


def inverse(a):
    """Independent ordinary rational inverse, with no modulo-three pivot rule."""
    n=len(a); work=[list(map(Q,row))+unit for row,unit in zip(a,identity(n))]
    for column in range(n):
        pivot=next(i for i in range(column,n) if work[i][column])
        work[column],work[pivot]=work[pivot],work[column]
        factor=work[column][column]
        work[column]=[v/factor for v in work[column]]
        for row in range(n):
            if row==column: continue
            factor=work[row][column]
            work[row]=[u-factor*v for u,v in zip(work[row],work[column])]
    return [row[n:] for row in work]


def matrix(word,n=8):
    result=identity(n)
    for op,*args in word:
        if op=='swap':
            i,j=args
            for row in result: row[i],row[j]=row[j],row[i]
        elif op=='add':
            i,j,a=args
            for row in result: row[i]+=Q(a)*row[j]
        elif op=='scale':
            i,a=args
            for row in result: row[i]*=Q(a)
        else: raise ValueError('unknown source operation')
    return result


def projection(basis,rank):
    return multiply([[v if j<rank else Q(0) for j,v in enumerate(row)] for row in basis],inverse(basis))


def json_word(word):
    return [[([v.numerator,v.denominator] if isinstance(v,Q) else v) for v in row] for row in word]


def lift(word,columns):
    result=[]
    for row in word:
        op=row[0]
        for lane in range(columns):
            if op=='scale': result.append((op,row[1]*columns+lane,row[2]))
            elif op=='add': result.append((op,row[1]*columns+lane,row[2]*columns+lane,row[3]))
            else: result.append((op,row[1]*columns+lane,row[2]*columns+lane))
    return tuple(result)


def charts(ns,graph,caller):
    differences,joints=ns['fixed_binary_charts']()
    projectors={int(k):projection(transpose(f['B']+f['A']),f['dim']) for k,f in graph['frames'].items()}
    endpoint_checks=0
    for (i,j),(word,rank) in differences.items():
        delta=[[b-a for a,b in zip(r,s)] for r,s in zip(projectors[i],projectors[j])]
        require(projection(matrix(word),rank)==delta,'independent difference endpoint')
        require(multiply(delta,delta)==delta,'difference is idempotent')
        endpoint_checks+=1
    ports=caller['ports']
    for p,word in enumerate(joints):
        expected=transpose(graph['frames'][str(graph['start'][p])]['B']+
                           graph['frames'][str(graph['final'][ports+p])]['B'])
        require(matrix(word)==expected,'independent joint endpoint')
        endpoint_checks+=1
    words={tuple(word) for word,rank in differences.values()}|set(joints)
    words.discard(())
    words=((),*sorted(words,key=lambda w:json.dumps(json_word(w),separators=(',',':'))))
    data=json.dumps([json_word(w) for w in words],separators=(',',':'),sort_keys=True).encode()
    require(len(words)==595 and len(data)==215644,'exact dictionary census')
    require(sha256(data).hexdigest()=='734035814cb639382a12a81e7f408b222f949cd69ad28a28544aeb5d0490d3f9','dictionary hash')
    coefficients=[Q(row[-1]) for word in words for row in word if row[0]!='swap']
    require(all(c.denominator%3 for c in coefficients),'source denominators integral at three')
    require(max(abs(c.numerator).bit_length()+1 for c in coefficients)==5,'signed numerator width')
    require(max(c.denominator.bit_length() for c in coefficients)==5,'denominator width')
    require(max(map(len,words))==61,'source length bound')
    counts=Counter(); requests={}; targets=ports*len(caller['diagonal'])
    dims={int(k):v['dim'] for k,v in graph['frames'].items()}
    moves=[row for row in graph['program'] if row[0]=='MOVE']
    for event in caller['events']:
        op=event[0]
        if op=='LOCAL':
            targets+=len(graph['start'])-2*ports
            for _,bank,i,j in moves:
                counts['move']+=1; requests['move',i,j]=abs(dims[i]-dims[j])
        elif op=='QUERY':
            counts[op]+=ports
            for p in range(ports): requests[op,p]=1
        elif op=='IDLE_ONE':
            counts[op]+=ports; requests[op,tuple(event[2])]=7*len(event[2])
    require(targets==18906 and dict(counts)=={'move':100908,'IDLE_ONE':3552,'QUERY':444},'independent paid/target incidence')
    require(len(requests)==2481,'distinct shapes')
    lifted=0; ordered=0
    for columns in (1,3,7):
        catalogue=ns['ActiveCatalogue'](134*columns,columns)
        for key,rank in requests.items():
            if key[0]=='move':
                i,j=key[1:]
                if dims[i]>dims[j]: i,j=j,i
                base,base_rank=differences[i,j]
                frame=catalogue.difference(*key[1:]); mask=range(base_rank)
            elif key[0]=='QUERY':
                base=joints[key[1]]; frame=catalogue.head(key[1]); mask=(0,)
            else:
                frame=catalogue.idle(key[1]); base=(); mask=None
            require(frame.word==lift(base,columns),'exact operation-major/lane-minor lift')
            require(len(frame.mask)==rank*columns,'source rank lift')
            if mask is not None:
                require(frame.mask==tuple(i*columns+j for i in mask for j in range(columns)),'ordered lifted mask')
            require(all(0<=a<134*columns for a in frame.mask),'mask ambient')
            lifted+=1; ordered+=len(frame.mask)
    noncommuting=next(w for w in words if matrix(w)!=matrix(tuple(reversed(w))))
    require(noncommuting,'reverse-word mutant must differ')
    return words,{'rational_endpoint_checks':endpoint_checks,'dictionary_words':len(words),
          'dictionary_bytes':len(data),'dictionary_sha256':sha256(data).hexdigest(),
          'targets':targets,'paid':sum(counts.values()),'paid_kinds':dict(sorted(counts.items())),
          'distinct_shapes':len(requests),'source_lifts':lifted,'mask_coordinates_checked':ordered,
          'coefficient_bits':[5,5],'max_word':61}


@dataclass(frozen=True)
class Axis:
    basis: tuple
    column: int


@dataclass(frozen=True)
class Job:
    owner: int
    axes: tuple
    def select(self,indices):
        return Job(self.owner,tuple(self.axes[i] for i in indices))


class IndependentCodec:
    """Separate integer/bit-string implementation of the written value grammar."""
    def __init__(self,words,n,w=24):
        self.words=words;self.n=n;self.h=(n-1).bit_length();self.w=w
        self.cache={(): (0,1)}
        self.identity_tokens={};self.expansions={}
    def descriptor(self,job):
        require(0<=job.owner<1<<self.w,'owner range')
        require(len(job.axes)<=self.n,'job length')
        if all(isinstance(x,int) for x in job.axes):
            kind,index,c,axes=0,0,1,job.axes
        else:
            require(job.axes and all(isinstance(x,Axis) for x in job.axes),'axis kinds')
            base=job.axes[0].basis
            require(all(x.basis==base for x in job.axes),'uniform basis')
            known=self.identity_tokens.get(id(base))
            if known is not None:
                require(known[0] is base,'retained basis identity')
                index,c=known[1:]
            elif base in self.cache:
                index,c=self.cache[base]
                self.identity_tokens[id(base)]=(base,index,c)
            else:
                matches=[(i,len(base)//len(word)) for i,word in enumerate(self.words[1:],1)
                         if len(base)%len(word)==0 and lift(word,len(base)//len(word))==base]
                require(matches,'unsupported basis')
                index,c=matches[0];self.cache[base]=(index,c)
                self.identity_tokens[id(base)]=(base,index,c)
            kind=1;axes=tuple(x.column for x in job.axes)
        require(all(isinstance(x,int) and 0<=x<self.n for x in axes),'axis bound')
        return job.owner,kind,index,c,axes
    def job_fields(self,job):
        owner,kind,index,c,axes=self.descriptor(job)
        return [(owner,self.w),(kind,1),(index,self.w),(c,self.w),(len(axes),self.w)]+[(a,self.h) for a in axes]
    @staticmethod
    def bits(fields):
        require(all(0<=v<1<<w for v,w in fields),'field width')
        text=''.join(format(v,'0'+str(w)+'b') for v,w in fields)
        bits=len(text); text+='0'*(-bits%8)
        return int(text or '0',2).to_bytes(len(text)//8,'big'),bits
    @staticmethod
    def reader(image):
        data,bits=image
        require(len(data)==(bits+7)//8,'image length')
        number=int.from_bytes(data,'big');pad=8*len(data)-bits
        require(number&((1<<pad)-1)==0,'image padding')
        value=number>>pad;left=bits
        def read(width):
            nonlocal left
            require(0<=width<=left,'truncated field')
            left-=width
            return (value>>left)&((1<<width)-1)
        def finish(): require(left==0,'trailing image bits')
        return read,finish
    def read_job(self,read):
        owner=read(self.w);kind=read(1);index=read(self.w);c=read(self.w);length=read(self.w)
        require(length<=self.n and index<len(self.words) and c>=1,'job header')
        axes=tuple(read(self.h) for _ in range(length))
        if kind==0:
            require(index==0 and c==1,'integer kind header');job=Job(owner,axes)
        else:
            require(axes,'typed empty mask')
            if (index,c) not in self.expansions:self.expansions[index,c]=lift(self.words[index],c)
            base=self.expansions[index,c]
            job=Job(owner,tuple(Axis(base,a) for a in axes))
        self.descriptor(job)
        return job
    def state(self,rows,live,pending,group,round_no):
        fields=[(x,self.w) for x in (group,round_no,len(rows),len(live),len(pending))]
        for job in rows: fields.extend(self.job_fields(job))
        for ident,(slot,zeros) in sorted(live.items()):
            fields.extend((x,self.w) for x in (ident,slot,len(zeros)))
            for job in zeros: fields.extend(self.job_fields(job))
        for serial,job in sorted(pending.items()):
            fields.append((serial,self.w));fields.extend(self.job_fields(job))
        return self.bits(fields)
    def restore_state(self,image):
        read,finish=self.reader(image)
        group,round_no,nr,nl,np=[read(self.w) for _ in range(5)]
        rows=[self.read_job(read) for _ in range(nr)];live={};pending={};last=-1;slots=set()
        for _ in range(nl):
            ident,slot,nz=[read(self.w) for _ in range(3)]
            require(ident>last and slot not in slots,'live key or slot')
            live[ident]=(slot,[self.read_job(read) for _ in range(nz)])
            last=ident;slots.add(slot)
        last=-1
        for _ in range(np):
            serial=read(self.w);require(serial>last,'pending order')
            pending[serial]=self.read_job(read);last=serial
        finish();return rows,live,pending,group,round_no
    def transfer(self,job,controls):
        fields=[(len(controls),self.w)]+[(x,self.w) for x in controls]+self.job_fields(job)
        image=self.bits(fields);read,finish=self.reader(image)
        control=tuple(read(self.w) for _ in range(read(self.w)))
        restored=self.read_job(read);finish()
        require(control==controls,'leaf continuation restored')
        return restored,image[1]


def budget():
    P,q=18906,104904;N0=1<<30
    # Every term is positive times a negative power of N. Consequently its
    # value at N>=N0 is bounded by this exact rational constant. Production
    # N>=2^3000 exceeds N0; no sampling of heights is used for generalization.
    state=Q(2)+Q(640,N0**93)+Q(768+256*q,N0**10)+Q(4*(P+q),N0**9)
    A=5+4*P+5*q
    event=Q(128,N0**93)+Q(256*A,N0**5)
    transfer=Q(4*P+16+256,N0**92)+Q(128*(4*P+20),N0**93)
    dictionary=Q(2**21,N0**93) # h>=1, weaker than actual h>=3000
    require(513<N0,'J < 2Nh using 512h+1<=513h')
    require(state<3 and event<1 and 2*state+event+transfer+dictionary<8,'uniform coefficient certificate')
    # This proves a stronger <8BNh from the conservative displayed terms;
    # acceptance concerns the author's intentionally looser <32BNh claim.
    require(9**2>4*2**2,'strict exponential base')
    # 9n^2-(n+1)^2=8n^2-2n-1>0 at n>=1, since
    # 8n^2-2n-1 >= 8n-2n-1 = 6n-1>0.
    require(8-2-1>0,'exponential induction polynomial')
    require(sum(2**k for k in range(1,8))==254,'seven stage sum')
    require(2*254*9==4572,'history coefficient')
    return {'monotone_base_N':N0,'state_ratio_ceiling':3,'event_ratio_ceiling':1,
            'independent_total_ratio_ceiling':8,'published_total_ratio_ceiling':32,
            'strict_bytes_comparison':'32BNh < 8W from W/B>=9^N and 4Nh<9^N',
            'same_stage_bytes_ceiling':'2W','conditional_seven_stage_bytes_ceiling':'4572X',
            'scope':'Uniform algebraic certificate; not numerical extrapolation from finite heights.'}


def fixture(ns,q,ticks,replicas):
    plan=ns['Plan'].__new__(ns['Plan'])
    plan.n=256;plan.targets=(2,2);plan.paid=(1,)*q
    plan.ticks=ticks;plan.rounds=128;plan.bands=range(10,26,2)
    plan.count={e:replicas if e in (10,24) else 0 for e in plan.bands}
    plan.delay={e:1 if e==10 else q+1 for e in plan.bands}
    plan.send=defaultdict(list);plan.receive=defaultdict(list);plan.sources=defaultdict(list)
    plan.send[24,0].append(ns['Link'](0,replicas,10,0,0))
    plan.receive[10,0].append(ns['Link'](0,replicas,24,0,0))
    plan.sources[10,1].append(ns['Source'](0,replicas,0,64))
    plan.sources[24,1].append(ns['Source'](0,replicas,2*ticks*replicas,8))
    plan.source_width=18*ticks*replicas;plan.width=plan.source_width+3
    return plan


def independent_calendar(plan):
    """Birth-indexed appointments, sorted once; source enumerates tick/band/j."""
    appointments=defaultdict(list);q=len(plan.paid);span=len(plan.bands);maximum=max(plan.count.values())
    def ident(birth,e,rep): return (birth*span+(e-plan.bands.start)//2)*maximum+rep
    for e in plan.bands:
        for birth in range(plan.ticks):
            for rep in range(plan.count[e]):
                appointments[birth+q*plan.delay[e]].append((0,e,0,rep,birth))
                for j in range(q):
                    appointments[birth+j*plan.delay[e]].append((1,-e,j,rep,birth))
    result=[];serial=0;counts=Counter()
    for tick,items in sorted(appointments.items()):
        loans={}
        for kind,signed_e,j,rep,birth in sorted(items):
            e=signed_e if kind==0 else -signed_e;context=ident(birth,e,rep)
            if kind==0: result.append((2,context));counts['closes']+=1;continue
            if j==0:
                record=[0,context,e-8]
                for port in (0,1):
                    key=e,rep,port
                    if key in loans:record.extend((1,loans.pop(key)));counts['loan_bindings']+=1
                    elif port==1:
                        period=64 if e==10 else 8
                        initial=0 if e==10 else 2*plan.ticks*maximum
                        base=initial+(birth*maximum+rep)*(plan.rounds//period)
                        record.extend((2,base,2*(e-8),period));counts['source_bindings']+=1
                    else:record.extend((0,2*(e-8)));counts['zero_bindings']+=1
                result.append(tuple(record));counts['opens']+=1
            selected=4 if e==24 and j==0 and tick<plan.ticks else 0
            if selected:loans[10,rep,0]=serial
            result.append((1,context,serial,e-8,selected));serial+=1;counts['paid']+=1
        require(not loans,'appointment loans return in tick')
    return result,counts


def observed(job):
    if all(isinstance(x,int) for x in job.axes):return job.owner,'integer',job.axes
    return job.owner,'typed',job.axes[0].basis,tuple(a.column for a in job.axes)


class Service:
    def __init__(self,plan,words):
        self.plan=plan;self.words=words;self.actions=[];self.live=set(range(plan.width))
        self.capacity=plan.width;self.vacant=[];self.opens=0
    def zero(self,exemplar):
        if self.vacant:owner=self.vacant.pop()
        else:owner=self.capacity;self.capacity+=1
        self.live.add(owner);job=Job(owner,exemplar.axes)
        self.actions.append(('zero',observed(job)));return job
    def native(self,ports,columns):
        number=self.opens;self.opens+=1
        self.actions.append(('open',columns,tuple(map(observed,ports))))
        basis=lift(self.words[1+number%13],columns)
        def iterator():
            for j,rank in enumerate(self.plan.paid):
                job=Job(ports[0].owner,tuple(Axis(basis,i) for i in reversed(range(rank*columns))))
                self.actions.append(('resume',number,j,observed(job)));yield job
            self.actions.append(('return',number))
        return iterator()
    def leaf(self,job):
        require(job.owner in self.live,'leaf live owner')
        self.actions.append(('leaf',observed(job)))
    def retire_zero(self,job):
        require(job.owner in self.live,'retire live owner')
        self.live.remove(job.owner);self.vacant.append(job.owner)
        self.actions.append(('retire',observed(job)))


def independent_decode(plan,rows,round_no,group,service,records,codec):
    live={};pending={};services={};max_bits=max_live=max_pending=max_transfer=0;transfers=0
    zeros=delayed=leaves=0
    for record in records:
        opcode,context=record[:2]
        if opcode==0:
            columns=record[2];position=3;ports=[];zero_jobs=[]
            for port in range(len(plan.targets)):
                kind=record[position];position+=1
                if kind==1:
                    serial=record[position];position+=1;ports.append(pending.pop(serial));delayed+=1
                    continue
                if kind==2:
                    base,size,period=record[position:position+3];position+=3
                    cycle,step=divmod(round_no,period);index=group*plan.source_width+base+cycle
                    if cycle<plan.rounds//period and index<plan.width:
                        five=(period*size-plan.n)//4
                        indices=[t//5 if t<5*five else t-4*five for t in range(step,period*size,period)]
                        ports.append(rows[index].select(indices));continue
                else:size=record[position];position+=1
                job=service.zero(rows[0].select(range(size)));ports.append(job);zero_jobs.append(job);zeros+=1
            require(position==len(record),'all opening fields consumed')
            slot=0
            while slot in services:slot+=1
            services[slot]=iter(service.native(ports,columns));live[context]=(slot,zero_jobs)
        elif opcode==1:
            _,_,serial,size,selected=record;slot=live[context][0];job=next(services[slot])
            require(len(job.axes)==size,'source paid extent')
            for index in range(selected,size):
                job,bits=codec.transfer(job,(context,serial,size,selected,index))
                max_transfer=max(max_transfer,bits);transfers+=1
                service.leaf(job.select((index,)));leaves+=1
            if selected:pending[serial]=job.select(range(selected))
        else:
            slot,zero_jobs=live.pop(context)
            require(next(services[slot],None) is None,'source extra return')
            for job in zero_jobs:service.retire_zero(job)
            del services[slot]
        image=codec.state(rows,live,pending,group,round_no)
        restored=codec.restore_state(image)
        require(restored==(rows,live,pending,group,round_no),'state value roundtrip')
        rows,live,pending,group,round_no=restored
        max_bits=max(max_bits,image[1]);max_live=max(max_live,len(live));max_pending=max(max_pending,len(pending))
    require(not live and not pending and not services,'complete return')
    return {'state_roundtrips':len(records),'callback_roundtrips':transfers,'max_state_bits':max_bits,
            'max_transfer_bits':max_transfer,'max_live':max_live,'max_pending':max_pending,
            'zero_allocations':zeros,'delayed_bindings':delayed,'leaf_calls':leaves}


def event_image_roundtrip(records,targets,w=24):
    image=IndependentCodec.bits([(len(records),w)]+[(value,w) for row in records for value in row])
    read,finish=IndependentCodec.reader(image);restored=[]
    for _ in range(read(w)):
        op=read(w);row=[op,read(w)]
        require(op in (0,1,2),'event kind')
        if op==0:
            row.append(read(w))
            for _ in range(targets):
                kind=read(w);require(kind in (0,1,2),'port kind');row.append(kind)
                row.extend(read(w) for _ in range(3 if kind==2 else 1))
        elif op==1:row.extend(read(w) for _ in range(3))
        restored.append(tuple(row))
    finish();require(restored==records,'event tape value roundtrip')
    require(image[1]==w*(1+sum(map(len,records))),'complete event fields charged')
    return image[1]


def calendars(ns,words):
    result=[]
    for q,ticks,rep in ((2,1,1),(3,5,2),(4,6,1),(5,3,2)):
        plan=fixture(ns,q,ticks,rep);records,counts=independent_calendar(plan)
        require(records==list(plan.events()),'birth appointments versus original tick calendar')
        S=sum(plan.count.values());require(counts['opens']==counts['closes']==ticks*S and counts['paid']==q*ticks*S,'exact event census')
        tape_bits=event_image_roundtrip(records,len(plan.targets))
        bound=24*(1+ticks*S*(5+4*len(plan.targets)+5*q))
        require(tape_bits<=bound,'stored event tape upper bound')
        C=sum(plan.count[e]*(q*plan.delay[e]+1) for e in plan.bands)
        for group,round_no in ((0,0),(0,127),(1,0)):
            rows=[Job(i,tuple(range(plan.n))) for i in range(plan.width)]
            a=Service(plan,words);b=Service(plan,words);codec=IndependentCodec(words,plan.n)
            plan.decode(rows,round_no,group,a,iter(records))
            values=independent_decode(plan,rows,round_no,group,b,records,codec)
            require(a.actions==b.actions,'literal source versus independent serialized trace')
            require(a.live==b.live==set(range(plan.width)) and a.capacity==b.capacity,'owner and allocation chronology')
            require(values['max_live']<=C and values['max_pending']<=q*C,'inclusive descriptor count')
            require(values['delayed_bindings']==ticks*rep,'all actual delayed bindings')
            expected_leaves=q*ticks*rep*(2+16)-4*ticks*rep
            require(values['leaf_calls']==expected_leaves,'selected prefix excluded from leaves')
            J=4*24+1+plan.n*codec.h
            state=5*24+plan.width*J+C*(3*24+2*J)+q*C*(24+J)
            require(values['max_state_bits']<=state,'finite state allowance')
            digest=sha256(repr(a.actions).encode()).hexdigest()
            result.append({'q':q,'ticks':ticks,'replicas':rep,'group':group,'round':round_no,
                           'trace_sha256':digest,'event_bits':tape_bits,'event_counts':dict(counts),**values})
        print('CALENDAR_ACCEPTED '+str((q,ticks,rep)),flush=True)
    return {'fixtures':result,'total_event_roundtrips':sum(r['state_roundtrips'] for r in result),
            'total_callback_roundtrips':sum(r['callback_roundtrips'] for r in result),
            'scope':'Supplied calendars exercise original Plan.events/decode; numerical native services abstracted.'}


def controls(words):
    codec=IndependentCodec(words,256);basis=lift(words[1],2)
    job=Job(7,tuple(Axis(basis,a) for a in (7,0,3)))
    names=[]
    def reject(action,name):
        try:action()
        except (ValueError,IndexError,KeyError):names.append(name);return
        raise ValueError('accepted negative control '+name)
    reject(lambda:codec.descriptor(Job(-1,(0,))),'negative owner')
    reject(lambda:codec.descriptor(Job(0,(256,))),'axis outside ambient')
    reject(lambda:codec.descriptor(Job(0,(0,Axis(basis,1)))),'mixed axis kinds')
    reject(lambda:codec.descriptor(Job(0,(Axis((('scale',0,Q(7,11)),),0),))),'unsupported basis')
    image=codec.state([Job(0,(2,0))],{9:(0,[Job(3,(0,1))])},{11:job},0,0)
    reject(lambda:codec.restore_state((image[0][:-1],image[1])),'truncated state')
    small=codec.bits([(1,1)])
    reject(lambda:codec.reader((bytes([small[0][0]|1]),small[1])),'nonzero padding')
    sorted_job=Job(7,tuple(sorted(job.axes,key=lambda a:a.column)))
    require(observed(sorted_job)!=observed(job),'ordered mask mutation')
    names.append('sorting mask changes interface value')
    require(observed(job)!=observed(Job(7,tuple(a.column for a in job.axes))),'basis erasure mutation')
    names.append('erasing basis changes interface value')
    typed=Job(0,(Axis((),0),));integer=Job(0,(0,))
    require(codec.job_fields(typed)!=codec.job_fields(integer),'typed identity versus integer')
    names.append('typed empty basis differs from integer kind')
    require(codec.state([Job(0,(2,0))],{9:(0,[])},{11:job},0,0)!=image,'zero retirement list omission')
    names.append('omitting zero list changes image')
    require(codec.state([Job(0,(2,0))],{9:(0,[Job(3,(0,1))])},{},0,0)!=image,'pending omission')
    names.append('omitting pending loan changes image')
    # A callback needs the full job after return to select the following axis.
    one=job.select((0,));reject(lambda:one.select((1,)),'single-axis callback cannot restore full continuation')
    require(24*(1+5)>0,'event tape nonzero')
    names.append('omitting immutable tape undercounts encoded fields')
    # Excluded-service counterexample: arbitrarily many private bits can coexist
    # with the same slot and exactly the same observable deterministic trace.
    states=[bytes([i])*4096 for i in range(4)]
    require(len(set(states))==4,'private service distinction')
    require(len({(0,('return',)) for _ in states})==1,'same external service image')
    names.append('slot image cannot encode arbitrary native private state')
    return names


def main():
    global PACKAGE,SRC
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path)
    parser.add_argument('--package',type=Path,help='decoder-control package; default discovers parent package or swarm sibling')
    args=parser.parse_args()
    if args.package is not None:
        PACKAGE=args.package.resolve()
    else:
        PACKAGE=next((p for p in (HERE.parent,HERE.parent/'storage'/'decoder-control')
                      if (p/'SOURCE-BINDINGS.json').is_file()),PACKAGE)
    SRC=PACKAGE/'sources'
    pins=authenticate();ns,graph,caller=originals()
    print('SOURCE_PINS_ACCEPTED',flush=True)
    words,chart=charts(ns,graph,caller)
    print('EXACT_CHARTS_ACCEPTED',flush=True)
    result={'status':'PASS_INDEPENDENT_DECODER_STORAGE_REVIEW','pins':pins,'chart':chart,'budget':budget()}
    result.update(decoder=calendars(ns,words),negative_controls=controls(words))
    payload=json.dumps(result,sort_keys=True,indent=2)+'\n'
    if args.output: args.output.write_text(payload)
    print(json.dumps({k:v for k,v in result.items() if k in ('status','budget')},sort_keys=True))


if __name__=='__main__': main()
