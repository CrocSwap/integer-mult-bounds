#!/usr/bin/env python3
"""Exact ownership checks of pinned binary source; standard library only."""
import ast
from collections import Counter, defaultdict
from contextlib import contextmanager
from dataclasses import dataclass
from fractions import Fraction
import gzip
import hashlib
import io
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / 'sources'
def require(condition, message):
    if not condition:
        raise AssertionError(message)
def extract(filename, names, namespace):
    tree = ast.parse((SRC / filename).read_text())
    nodes = [n for n in tree.body if isinstance(n, (ast.ClassDef, ast.FunctionDef)) and n.name in names]
    require({n.name for n in nodes} == set(names), 'missing extracted definition')
    for node in nodes:
        node.decorator_list = [d for d in node.decorator_list
                               if not (isinstance(d, ast.Name) and d.id == 'cache')]
    exec(compile(ast.Module(nodes, type_ignores=[]), filename, 'exec'), namespace)
manifest = json.loads((ROOT / 'SOURCE-BINDINGS.json').read_text())
for name, row in manifest['files'].items():
    data = (SRC / name).read_bytes()
    require(len(data) == row['size'], 'source size: ' + name)
    require(hashlib.sha256(data).hexdigest() == row['sha256'], 'source hash: ' + name)
graph = json.loads((SRC / 'graph.json').read_text())
caller = json.loads((SRC / 'caller.json').read_text())
require(graph == json.loads(gzip.decompress((SRC / 'strong-bit.json.gz').read_bytes())), 'graph decoded equality')
require(caller == json.loads(gzip.decompress((SRC / 'binary-caller.gz').read_bytes())), 'caller decoded equality')
@dataclass(frozen=True)
class Port:
    tag: tuple
    rank: int
@dataclass
class Word:
    targets: tuple
    paid: tuple
    ambient: int = 134
ns = {'Port':Port, 'bit_word':lambda targets,paid:Word(tuple(targets),tuple(paid))}
extract('tagged_sources.py', ['binary_ports'], ns)
word = ns['binary_ports'](graph, caller)
P,Q = len(word.targets),len(word.paid)
require((P,Q)==(18906,104904), 'fixed port census')
ops = Counter(row[0] for row in graph['program'])
events = Counter(row[0] for row in caller['events'])
require((graph['public'],len(graph['program']),caller['ports'],len(caller['diagonal']))==(630,39600,111,38), 'literal shape')
require(P==38*111+events['LOCAL']*(630-222), 'independent target formula')
require(Q==events['LOCAL']*ops['MOVE']+(events['QUERY']+events['IDLE_ONE'])*111, 'independent paid formula')
def scan(program, omit_clear=False):
    public=set(range(graph['public'])); registers=set(public)
    peak,first_peak=0,None
    for index,row in enumerate(program):
        op,dest,*args=row
        if op=='INIT':
            require(dest not in registers,'INIT aliases live register'); registers.add(dest)
        elif op=='CLEAR':
            require(dest in registers and dest not in public,'CLEAR domain')
            if not omit_clear: registers.remove(dest)
        else:
            require(dest in registers,'opcode destination')
            if op in ('ADD','SWAP'): require(args[0] in registers,'opcode source')
            else: require(op=='MOVE','known opcode')
        now=len(registers-public)
        if now>peak: peak,first_peak=now,index
    require(registers==public,'private owners survive inner return')
    return peak,first_peak
private_peak,peak_at=scan(graph['program'])
require(private_peak==3433,'private high water')
K=P+max(private_peak,1)
require(K==22339,'context coefficient')
@dataclass(frozen=True)
class Job:
    owner:int
    axes:tuple
    def select(self,indices):
        return Job(self.owner,tuple(self.axes[i] for i in indices))
@dataclass
class Frame:
    rank:int
    def matcher_to(self,other): return ()
def placed_job(owner,frame): return Job(owner,tuple(range(frame.rank)))
@contextmanager
def work_tapes(number): yield tuple(io.BytesIO() for _ in range(number))
def copy_bytes(source,target,count):
    data=source.read(count); require(len(data)==count,'exact byte read'); target.write(data)
raw_ns={'write_zeros':lambda tape,count:tape.write(bytes(count)),
        'read_exact':lambda tape,count:tape.read(count),'copy_bytes':copy_bytes,
        'work_tapes':work_tapes,'CHUNK':4096,'Job':Job,'placed_job':placed_job}
extract('raw_binary.py',['Banks','BinarySource'],raw_ns)
BaseBanks=raw_ns['Banks']
class OwnerMeter(BaseBanks):
    # Real allocation/retirement/clone, abstract field transformations.
    def __init__(self,dimension):
        self.dimension,self.volume=dimension,1
        self.tape=io.BytesIO()
        self.capacity,self.vacant,self.live=0,[],set()
        self.allocations,self.retirements,self.peak=0,0,0
    def zero(self):
        owner=super().zero(); self.allocations+=1
        self.peak=max(self.peak,len(self.live))
        require(self.capacity==self.peak,'free-first high water')
        return owner
    def retire(self,owner,**kwargs):
        super().retire(owner,**kwargs); self.retirements+=1
    def route(self,owner,word): require(owner in self.live,'route live owner')
    def xor(self,left,right): require(left in self.live and right in self.live,'xor live owners')
    def swap(self,left,right): require(left in self.live and right in self.live,'swap live owners')
target_ranks={p.tag:p.rank for p in word.targets}
class Catalogue:
    def target(self,tag): return Frame(target_ranks[tag]*self.columns)
    def difference(self,first,last):
        return Frame(abs(graph['frames'][str(first)]['dim']-graph['frames'][str(last)]['dim'])*self.columns)
    def port_stage(self,port,stage): return ()
    def idle(self,stages): return Frame(7*len(stages)*self.columns)
    def head(self,port): return Frame(self.columns)
strong_ns={'Catalogue':Catalogue,'BinarySource':raw_ns['BinarySource'],
           'graph':lambda:graph,'caller':lambda:caller,'placed_job':placed_job,
           'job_frame':lambda job,dimension:Frame(len(job.axes)),
           'inverse_word':lambda word:tuple(reversed(word))}
extract('strong_binary.py',['ActiveCatalogue','active_catalogue','StrongBinarySource'],strong_ns)
strong_ns['ActiveCatalogue'].difference=Catalogue.difference
stage_ns={}
extract('raw_binary_stage.py',['BinaryWord'],stage_ns)
native=stage_ns['BinaryWord'].__new__(stage_ns['BinaryWord']); native.tagged=word
raw_runs=[]
for columns in (1,3):
    banks=OwnerMeter(134*columns)
    inputs=[Job(banks.zero(),tuple(range(p.rank*columns))) for p in word.targets]
    raw=strong_ns['StrongBinarySource'](banks); issued=0; paid_peak=0
    for job in native.native(inputs,columns,raw):
        require(job.owner in banks.live,'issued live owner')
        require(len(banks.live)<=K,'raw context bound'); issued+=1
        paid_peak=max(paid_peak,len(banks.live))
    require(issued==Q,'complete paid iteration')
    require(len(banks.live)==P,'raw returns only input owners')
    require(banks.peak==K,'attained all-zero input bound')
    for job in inputs: banks.retire(job.owner,require_zero=True)
    require(not banks.live and len(banks.vacant)==banks.capacity,'empty allocator')
    raw_runs.append({'columns':columns,'paid':issued,'peak':banks.peak,'peak_at_paid_cut':paid_peak,
                     'allocations':banks.allocations,'retirements':banks.retirements})

# Actual source events/decode on bounded descending-loan fixtures. Replica
# counts are supplied; these fixtures do not run the numerical Measure class.
plan_ns={'F':Fraction,'defaultdict':defaultdict,'dataclass':dataclass}
extract('transport.py',['Link','Source','axes','Plan'],plan_ns)
Plan,Link=plan_ns['Plan'],plan_ns['Link']
calendar_runs=[]
def calendar(q,ticks,replicas,equal_delay=False):
    plan=Plan.__new__(Plan)
    plan.n,plan.targets,plan.paid=256,(2,),(1,)*q
    plan.ticks,plan.rounds,plan.bands=ticks,1,range(10,26,2)
    plan.count={e:(replicas if e in (10,24) else 0) for e in plan.bands}
    plan.delay={e:(1 if e==10 else q+1) for e in plan.bands}
    if equal_delay: plan.delay[24]=1
    plan.send,plan.receive,plan.sources=defaultdict(list),defaultdict(list),defaultdict(list)
    plan.send[24,0].append(Link(0,replicas,10,0,0))
    plan.receive[10,0].append(Link(0,replicas,24,0,0))
    plan.source_width,plan.width=1,1
    bank=OwnerMeter(256); external=Job(bank.zero(),tuple(range(256)))
    active,contexts,origins={},{},{}
    maximum=max(plan.count.values()); span=len(plan.bands)
    def info(ident):
        birth,remainder=divmod(ident,span*maximum)
        bandindex,replica=divmod(remainder,maximum)
        return birth,10+2*bandindex,replica
    class Machine:
        current=None
        def native(self,ports,columns):
            ident=self.current; active[ident]={j.owner for j in ports}
            def body():
                for _ in range(q):
                    for job in ports:
                        if origins.get(job.owner)==ident:
                            require(not any(job.owner in owners for other,owners in active.items() if other!=ident),
                                    'parent resumed before child returned')
                    yield Job(ports[0].owner,tuple(range(columns)))
                active.pop(ident)
            return body()
        def zero(self,exemplar):
            owner=bank.zero(); origins[owner]=self.current
            return Job(owner,exemplar.axes)
        def retire_zero(self,job):
            require(not any(job.owner in owners for owners in active.values()),'retired borrowed owner')
            bank.retire(job.owner); origins.pop(job.owner)
        def leaf(self,job): require(job.owner in bank.live,'leaf live owner')
    machine=Machine()
    cstar=sum(plan.count[e]*(q*plan.delay[e]+1) for e in plan.bands)
    records,peak_contexts=0,0
    def checked_records():
        nonlocal records,peak_contexts
        for row in plan.events():
            op,ident,*_=row
            if op==0: contexts[ident]=info(ident)
            require(ident in contexts,'context exists for resume/close')
            peak_contexts=max(peak_contexts,len(contexts))
            require(len(contexts)<=cstar,'inclusive context coefficient')
            machine.current=ident; records+=1
            yield row
            require(len(bank.live)<=1+len(contexts),'one input-zero owner per fixture context')
            if op==2: contexts.pop(ident)
        require(not contexts and not active and not origins,'complete fixture cleanup')
    plan.decode([external],0,0,machine,checked_records())
    require(bank.capacity<=1+cstar,'fixture historical capacity')
    return {'q':q,'ticks':ticks,'replicas':replicas,'records':records,
            'inclusive_context_bound':cstar,'observed_contexts':peak_contexts,
            'owner_capacity':bank.capacity}
for q in (2,3,4):
    for ticks in (1,4,7):
        for replicas in (1,2): calendar_runs.append(calendar(q,ticks,replicas))
controls=[]
def rejects(name,fn):
    try: fn()
    except (AssertionError,ValueError,ArithmeticError,KeyError): controls.append(name)
    else: raise AssertionError('control accepted: '+name)
rejects('omitted inner CLEAR retirement',lambda:scan(graph['program'],omit_clear=True))
rejects('omitted input-zero term',lambda:require(P+private_peak<=private_peak,'P term necessary'))
rejects('paid-cut peak substituted for all microsteps',lambda:require(raw_runs[0]['peak']<=raw_runs[0]['peak_at_paid_cut'],'closing cleanup peak'))
rejects('equal parent-child delay violates custody',lambda:calendar(3,4,1,equal_delay=True))
def omitted_query_retirement():
    tree=ast.parse((SRC/'strong_binary.py').read_text())
    node=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='StrongBinarySource')
    class DropQueryRetire(ast.NodeTransformer):
        changed=0
        def visit_Expr(self,item):
            if (isinstance(item.value,ast.Call) and isinstance(item.value.func,ast.Attribute)
                and item.value.func.attr=='retire' and len(item.value.args)==1
                and isinstance(item.value.args[0],ast.Name) and item.value.args[0].id=='borrowed'):
                self.changed+=1
                return ast.copy_location(ast.Pass(),item)
            return self.generic_visit(item)
    mutation=DropQueryRetire(); node=mutation.visit(node)
    require(mutation.changed==1,'exact outer retirement mutation')
    altered=dict(strong_ns)
    exec(compile(ast.fix_missing_locations(ast.Module([node],type_ignores=[])), '<query-retire-mutant>', 'exec'),altered)
    bank=OwnerMeter(134)
    inputs=[Job(bank.zero(),tuple(range(p.rank))) for p in word.targets]
    for job in native.native(inputs,1,altered['StrongBinarySource'](bank)):
        require(len(bank.live)<=K,'unretired query broke bound')
    require(len(bank.live)==P,'query clones survive return')
rejects('omitted outer QUERY retirement',omitted_query_retirement)
warm=OwnerMeter(134); old=[warm.zero() for _ in range(32)]
for owner in old: warm.retire(owner)
small=[warm.zero() for _ in range(2)]
require(warm.capacity==32 and len(warm.live)==2,'retained warm reserve')
rejects('current live substituted for capacity',lambda:require(warm.capacity<=len(warm.live),'warm history'))
result={'status':'PASS','source_commit':manifest['commit'],'source_files':len(manifest['files']),
        'fixed_template':{'public':630,'instructions':39600,'targets':P,'paid':Q,
                          'private_peak':private_peak,'first_peak_instruction':peak_at,'coefficient':K,
                          'opcodes':dict(sorted(ops.items())),'root_events':dict(sorted(events.items()))},
        'raw_runs':raw_runs,'calendar_fixtures':calendar_runs,'negative_controls':controls,
        'scope':'Fixed literal ownership and bounded source event/decoder traces. No analytic mass, production calendar, geometry or all-size delay certification.'}
print(json.dumps(result,indent=2,sort_keys=True))
