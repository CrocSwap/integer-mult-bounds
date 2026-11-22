#!/usr/bin/env python3
"""Bounded one-unit epoch control for the certified first-loan optimization.

Uses the actual #8035 predecessor's PoweredWord, tag lists, pinned graph and
caller, and actual epoch_tape.Image/run stream. The 36-call source is executed
with symbolic pairs over F2 and real owner lifetimes. Address routing and each
leaf are a tiny two-point involution: this is a bounded linear-control model,
not a replay of the full ternary projector geometry. physical_zero_v1.py is a
separate nonconstant physical projector control. The finite band is explicitly
constructed by hand; it is not claimed to be an installed production plan.
"""
import json,sys
from pathlib import Path
from dataclasses import replace
from types import SimpleNamespace
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from upstream import install
install()
from strong_binary import graph,caller
from tagged_sources import binary_ports
from periodic import Job,Unit,period
import epoch_tape
from certified_epoch import first_zero_certificate,run

G=graph();C=caller();q=C['ports'];dims={int(k):x['dim'] for k,x in G['frames'].items()}
graph_sha='74e93daf2b7acf794ffb51f92f03f51556f68126d41ee13a8969bddb4cbe6326'
caller_sha='757b3523798f840bdb02028b23708c3416627a99ea09e7a3c4bcdc5cd0c7ce4b'

class Banks:
    def __init__(self):self.data={};self.next=0
    def make(self,a=0,b=0):
        owner=self.next;self.next+=1;self.data[owner]=(a,b);return owner
    def zero(self):return self.make()
    def clone(self,owner):return self.make(*self.data[owner])
    def xor(self,a,b):
        x,y=self.data[a];s,t=self.data[b];self.data[a]=(x^s,y^t)
    def swap(self,a,b):self.data[a],self.data[b]=self.data[b],self.data[a]
    def retire(self,owner,require_zero=False):
        value=self.data.pop(owner)
        if require_zero:assert value==(0,0)

class ScalarSource:
    """Exact source owner/ADD schedule; two-point physical action in leaf()."""
    def __init__(self,banks):self.banks=banks
    def fresh(self,exemplar,rank,tag):return Job(self.banks.zero(),tuple(range(rank)))
    def retire(self,job):self.banks.retire(job.owner,require_zero=True)
    def raw(self,inputs,columns):
        B=self.banks;active={tag:job.owner for tag,job in inputs}
        for clock,(op,*args) in enumerate(C['events']):
            if op=='LOCAL':
                stage,x,y=args
                owners=([active['root',x,p] for p in range(q)]+
                        [active['root',y,p] for p in range(q)]+
                        [active['helper',clock,i] for i in range(2*q,G['public'])])
                regs=dict(enumerate(owners));chart=dict(enumerate(G['start']))
                for site,(cmd,d,*a) in enumerate(G['program']):
                    if cmd=='INIT':assert d not in regs;regs[d]=B.zero();chart[d]=a[0]
                    elif cmd=='ADD':
                        s,c=a;assert chart[d]==c==chart[s];B.xor(regs[d],regs[s])
                    elif cmd=='SWAP':
                        s,=a;B.swap(regs[d],regs[s]);chart[d],chart[s]=chart[s],chart[d]
                    elif cmd=='CLEAR':
                        assert d>=G['public'] and chart.pop(d)==a[0];B.retire(regs.pop(d))
                    elif cmd=='MOVE':
                        f,t=a;assert chart[d]==f
                        r=abs(dims[t]-dims[f]);yield ('move',clock,site,d),Job(regs[d],tuple(range(r*columns)))
                        chart[d]=t
                    else:raise AssertionError(cmd)
                assert chart==dict(enumerate(G['final'])) and len(regs)==G['public']
            elif op=='IDLE_ONE':
                x,stages=args
                for p in range(q):yield (op,clock,p),Job(active['root',x,p],tuple(range(7*len(stages)*columns)))
            elif op=='ADD':
                x,y=args
                for p in range(q):B.xor(active['root',x,p],active['root',y,p])
            elif op=='SWAP':
                x,y=args
                for p in range(q):B.swap(active['root',x,p],active['root',y,p])
            elif op=='QUERY':
                x,y=args
                for p in range(q):
                    source=B.clone(active['root',y,p]);yield (op,clock,p),Job(source,tuple(range(columns)))
                    B.xor(active['root',x,p],source);B.retire(source)
            else:raise AssertionError(op)

class Machine:
    def __init__(self,word,seed):
        self.word=word;self.banks=Banks();self.source=ScalarSource(self.banks);self.leaves=0;self.seed=seed
    def leaf(self,job):
        assert len(job.axes)==1
        a,b=self.banks.data[job.owner];self.banks.data[job.owner]=(b,a);self.leaves+=1
    def native(self,ports,columns):
        # Only the first full powered block is surfaced to this deliberately
        # bounded epoch. Serve all later real blocks inside the same frame and
        # in their original order. With one frame and no child, this preserves
        # the exact source chronology, but is not a production band schedule.
        for i,(block,job) in enumerate(zip(self.word.paid_paths(),self.word.native(ports,columns,self.source),strict=True)):
            if i==0:
                assert block.rank==1 and block.first==0
                yield job
            else:
                for axis in job.axes:self.leaf(Job(job.owner,(axis,)))
    def zero(self,exemplar):return Job(self.banks.zero(),exemplar.axes)
    def retire_zero(self,job):self.banks.retire(job.owner,require_zero=True)

class Planner:
    def __init__(self,word):
        self.n=512
        kept=[p for p,yes in word.target_paths() if yes]
        paid=[next(word.paid_paths())]
        self.rule=SimpleNamespace(ambient=word.ambient**word.power,
                                  targets=tuple(p.rank for p in kept),paid=tuple(b.rank for b in paid))
        size=len(kept);unit=Unit((),1,tuple(('source',i) for i in range(size)))
        forest=SimpleNamespace(layers={(): (unit,)},prefixes=frozenset({()}))
        self.plan=SimpleNamespace(width=size,forest=forest,copies=1,owners_per_copy=size,
            offsets=tuple(range(size)),periods=tuple(period(self.n,p.rank) for p in kept),
            rounds=1,active=self.n)
        self.code=epoch_tape.Image(self.rule,self.plan)
        self.kept=kept
    def __call__(self,n):assert n==self.n;return self.plan
    def image(self,n):assert n==self.n;return self.code

def evaluate(word,planner,mode):
    machine=Machine(word,mode);axis=tuple(range(planner.n));jobs=[]
    for i,port in enumerate(planner.kept):
        tag=port.tag[0]
        if mode=='all':a,b=1<<(2*i),1<<(2*i+1)
        elif tag==('helper',4,222):a,b=1,0
        else:a,b=0,0
        jobs.append(Job(machine.banks.make(a,b),axis))
    if mode in ('all','helper-baseline'):
        epoch_tape.run(planner.rule,planner.n,jobs,machine,planner=planner);stats=None
    else:
        if mode=='helper-unsafe':cert=None
        else:cert=first_zero_certificate(word,G,C,graph_sha,caller_sha)
        stats=run(planner.rule,planner.n,jobs,machine,planner=planner,certificate=cert,
                  unsafe_first=(mode=='helper-unsafe'))
    assert len(machine.banks.data)==len(jobs)
    result=[machine.banks.data[j.owner] for j in jobs]
    return result,machine.leaves,stats

raw=binary_ports(G,C)
# Floor 29 gives a valid one-factor diagnostic rule with every helper omitted.
w=replace(raw,power=1,floor=29,low_cut=12,high_cut=12);planner=Planner(w)
print('prepared certified bounded stream',len(planner.kept),planner.code.records,file=sys.stderr,flush=True)
base,base_leaves,_=evaluate(w,planner,'all')
# Same symbolic input as baseline; use a separate flag so optimized evaluation
# retains the complete independent basis rather than the negative-control seed.
def optimized_all():
    machine=Machine(w,'all');axis=tuple(range(planner.n));jobs=[]
    for i,p in enumerate(planner.kept):jobs.append(Job(machine.banks.make(1<<(2*i),1<<(2*i+1)),axis))
    cert=first_zero_certificate(w,G,C,graph_sha,caller_sha)
    stats=run(planner.rule,planner.n,jobs,machine,planner=planner,certificate=cert)
    assert len(machine.banks.data)==len(jobs)
    return [machine.banks.data[j.owner] for j in jobs],machine.leaves,stats
changed,changed_leaves,stats=optimized_all()
assert base==changed and base_leaves-changed_leaves==1
assert stats['skipped_elementary_leaf_calls']==1 and stats['certified_first']==1
print('certified symbolic map passed',file=sys.stderr,flush=True)
# Unsafe negative control: floor=8 retains helper 222, so certificate must fail.
wbad=replace(raw,power=1,floor=8,low_cut=12,high_cut=12)
try:first_zero_certificate(wbad,G,C,graph_sha,caller_sha)
except AssertionError:pass
else:raise AssertionError('The certificate accepted a nonzero-capable helper input')
plbad=Planner(wbad)
badbase,badbase_leaves,_=evaluate(wbad,plbad,'helper-baseline')
badchanged,bad_leaves,badstats=evaluate(wbad,plbad,'helper-unsafe')
different=[i for i,(x,y) in enumerate(zip(badbase,badchanged,strict=True)) if x!=y]
assert different and badbase_leaves-bad_leaves==1
print(json.dumps({'certified_case':{'power':1,'floor':29,'retained_owners':len(planner.kept),
       'independent_input_bits':2*len(planner.kept),'image_records':planner.code.records,
       'baseline_leaf_actions':base_leaves,'changed_leaf_actions':changed_leaves,
       'actual_elementary_leaf_actions_saved':base_leaves-changed_leaves,'stats':stats,
       'all_public_output_forms_match':True,'all_owned_fields_returned':True},
       'negative_control':{'power':1,'floor':8,'certificate_rejected':True,
        'baseline_leaf_actions':badbase_leaves,'unsafe_leaf_actions':bad_leaves,
        'different_output_owner_count':len(different),'different_output_indices_first_10':different[:10]},
       'scope':'hand-constructed one-unit bounded epoch; symbolic two-point involution; physical_zero_v1.py checks genuine projector action separately'},indent=2))
print('PASS_BOUNDED_CERTIFIED_EPOCH_AND_UNSAFE_CONTROL')
