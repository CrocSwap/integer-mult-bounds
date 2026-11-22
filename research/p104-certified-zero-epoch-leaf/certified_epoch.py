"""Prototype: skip an unborrowed first zero loan at FINISH, without skipping ISSUE.

The certificate is deliberately restricted to the first paid block in each
native frame.  It assumes the pinned source's first-cut contract has been
independently established: the first cut copies helper (4,222), and applying
it in every powered factor reads the omitted (helper,4,222)^power input.
The caller must bind `word`, graph, caller and the physical source interpreter
to the authenticated implementations.  Merely providing plausible metadata
for a different interpreter is NOT a certificate of that interpreter.
"""
from dataclasses import dataclass
from itertools import count
from hashlib import sha256
from pathlib import Path
import gzip
import json
from periodic import row_axes
from epoch_tape import OPEN,ISSUE,CLOSE,FINISH,LOAN

@dataclass(frozen=True)
class FirstZeroCertificate:
    power:int
    floor:int
    source_tag:tuple
    paid_tag:tuple
    source_rank:int
    paid_rank:int
    source_graph_sha256:str
    caller_sha256:str


def first_zero_certificate(word,graph,caller,graph_sha,caller_sha):
    assert graph_sha=='74e93daf2b7acf794ffb51f92f03f51556f68126d41ee13a8969bddb4cbe6326'
    assert caller_sha=='757b3523798f840bdb02028b23708c3416627a99ea09e7a3c4bcdc5cd0c7ce4b'
    source=Path(__file__).resolve().parent/'pinned'
    for name,digest,claimed in [('strong-bit.json.gz',graph_sha,graph),
                                ('EFREE-CALLER.json.gz',caller_sha,caller)]:
        data=(source/name).read_bytes()
        assert sha256(data).hexdigest()==digest
        assert json.loads(gzip.decompress(data))==claimed
    from tagged_sources import binary_ports
    expected=binary_ports(graph,caller)
    assert (word.ambient,word.targets,word.paid)==(expected.ambient,expected.targets,expected.paid)
    assert caller['events'][:5]==[['ADD',0,1],['SWAP',0,1],['ADD',19,20],['SWAP',19,20],['LOCAL',1,1,0]]
    assert graph['program'][:3]==[['INIT',630,0],['ADD',630,222,0],['MOVE',630,0,2]]
    first_target=('helper',4,222);first_paid=('move',4,2,630)
    targets=[p for p in word.targets if p.tag==first_target]
    assert len(targets)==1 and targets[0].rank==8
    assert word.paid[0].tag==first_paid and word.paid[0].rank==1
    assert 8**word.power < word.floor**word.power
    assert not word.target((word.targets.index(targets[0]),)*word.power).rank>=word.floor**word.power
    blocks=list(word.blocks((0,)*word.power))
    assert len(blocks)==1 and blocks[0].first==0 and blocks[0].rank==1
    assert blocks[0].tags==(first_paid,)*word.power
    return FirstZeroCertificate(word.power,word.floor,first_target,first_paid,8,1,graph_sha,caller_sha)


def run(rule,n,fields,machine,*,planner,certificate,unsafe_first=False):
    """Follow epoch_tape.run exactly, except at a certified unborrowed FINISH.

    unsafe_first exists solely to demonstrate a failing negative control; use
    requires explicitly passing True and no certificate.
    """
    if unsafe_first: assert certificate is None
    else: assert isinstance(certificate,FirstZeroCertificate)
    plan=planner(n); public=tuple(fields)
    if len(public)!=plan.width or len({j.owner for j in public})!=plan.width or any(len(j.axes)!=n for j in public):
        raise ValueError('The carrier needs independent full input fields')
    stats={'issued':0,'issued_first':0,'certified_first':0,'borrowed_certificates':0,
           'aliased_certificates':0,'skipped_elementary_leaf_calls':0,'performed_elementary_leaf_calls':0}
    def finish(job,first,skip=False):
        for i in range(first,len(job.axes)):
            if skip: stats['skipped_elementary_leaf_calls']+=1
            else: machine.leaf(job.select((i,)));stats['performed_elementary_leaf_calls']+=1
    if plan.forest is None:
        for job in public:finish(job,0)
        return stats
    code=planner.image(n);fields=list(public)
    for _ in range(plan.copies*plan.owners_per_copy-plan.width):fields.append(machine.zero(public[0]))
    frames={};ordinals={};loans={};first_loans=set();borrowed=set();aliased=set();owners={};end=object()
    for iteration in range(plan.rounds):
        for row in code.rows():
            op,key,*args=row
            if op==OPEN:
                columns,*descriptors=args;entries=iter(descriptors);ports=[]
                for kind in entries:
                    index,size=next(entries),next(entries)
                    if kind==LOAN:
                        if index in first_loans:borrowed.add(index)
                        job=loans[index].select(range(size))
                    else:
                        q=next(entries)
                        job=fields[index+iteration//q].select(row_axes(plan.active,size,q,iteration%q))
                    ports.append(job)
                frames[key]=iter(machine.native(tuple(ports),columns));ordinals[key]=0
            elif op==ISSUE:
                loan,size=args;job=next(frames[key]);ordinal=ordinals[key];ordinals[key]+=1
                if len(job.axes)!=size:raise ValueError('A native cut issued the wrong rank')
                loans[loan]=job;stats['issued']+=1
                if ordinal==0:
                    stats['issued_first']+=1
                    if certificate or unsafe_first:first_loans.add(loan);stats['certified_first']+=bool(certificate)
                previous=owners.setdefault(job.owner,set())
                if previous:
                    aliased.update(previous);aliased.add(loan)
                previous.add(loan)
            elif op==CLOSE:
                if next(frames.pop(key),end) is not end:raise ValueError('A native cut remained after the final return')
                del ordinals[key]
            elif op==FINISH:
                job=loans.pop(key);first=args[0]
                skip=key in first_loans and key not in borrowed and key not in aliased
                if key in borrowed:stats['borrowed_certificates']+=1
                if key in aliased:stats['aliased_certificates']+=1
                finish(job,first,skip)
                owners[job.owner].remove(key)
                if not owners[job.owner]:del owners[job.owner]
                first_loans.discard(key);borrowed.discard(key);aliased.discard(key)
            else:raise ValueError('The installed instruction is unknown')
        if frames or loans or owners:raise ArithmeticError('The epoch left an open frame or loan')
    for job in public:finish(job,plan.active)
    for job in reversed(fields[len(public):]):machine.retire_zero(job)
    return stats
