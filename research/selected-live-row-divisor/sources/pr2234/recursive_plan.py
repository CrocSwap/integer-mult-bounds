"""Low-class macroplans and symbolic proper-width recursive calls.

This file builds plans, not a full selected payload simulator. PROOF.md gives
the sequential interpretation and induction. No high matrix enters a plan.
"""
from dataclasses import dataclass
from collections import Counter
from hashlib import sha256

import descriptor as d
from controlled_normalizer import Arithmetic, schedule
from fallback_program import compile_program
from expressions import FieldSpecification
from provider import RawHeader, GeneralHeader, need, canonical


def depth(n):
    result=0
    while n>=64:
        n=42*(n//64)
        result+=1
    return result


@dataclass(frozen=True)
class Child:
    kind: str
    first: int
    second: int
    expression: object


@dataclass(frozen=True)
class ResidualPlan:
    branch: str
    parent_size: int
    frozen_field: object
    children: tuple
    operations: tuple


def residual_plan(expression,request,low_matrix,catalogue):
    """Freeze only the parent field's specification; values stay on I/O."""
    n=expression.size;f=n//64;q=expression.q
    need(f>=1,"internal residual node")
    raw=RawHeader(q,1,low_matrix,tuple((0,)*64 for _ in range(64)),request.header_space)
    header=GeneralHeader(raw,request,catalogue)
    p=d.projector(header.read(Arithmetic(q)),header.axes,q)
    specification=FieldSpecification(q,expression.width,request,low_matrix)
    try:
        d.good_pivots(p,request.base.rank,q)
        good=True
    except ValueError:
        good=False
    if good:
        child=expression.append("good",request,low_matrix,expression.depth)
        # Coordinates refer to the core: first 64f head, last 64f tail.
        children=(Child("good",0,128*f-child.size,child),)
        operations=tuple(schedule(64,request.base.rank,1))
        branch="good"
    else:
        program=compile_program(d.elimination(d.residual(p,q),q))
        children=[]
        for op in program:
            if op.kind!="swap":
                continue
            i,k=op.target,op.source
            same=(i<64)==(k<64)
            def reversal():
                if f//2:
                    children.append(Child("orientation",k*f,(k+1)*f-f//2,
                                          expression.unit_child(f//2)))
            if same:
                reversal()
            if op.coefficient.kind=="pair":
                child=expression.append("pair",request,low_matrix,expression.depth,
                                        field=i,reverse=i>=64)
            else:
                need(op.coefficient.kind=="unit","fallback child grammar")
                child=expression.unit_child(f)
            children.append(Child(op.coefficient.kind,i*f,k*f,child))
            if same:
                reversal()
        operations=tuple((op.kind,op.target,op.source,op.coefficient.kind,
                          op.coefficient.reduction_index) for op in program)
        children=tuple(children);branch="fallback"
        need(len(children)<=32*64**2,"retained fallback allowance")
    for child in children:
        size=child.expression.size
        need(0<size<=42*f<n and depth(size)<depth(n),"proper weighted descent")
        need(child.first+size<=child.second and child.second+size<=128*f,
             "contiguous disjoint child blocks")
        need(child.expression.depth==expression.depth+1,"global generation depth")
    return ResidualPlan(branch,n,specification,children,operations)


def caller(catalogue):
    """Bind residual leaves to the chronological selected caller, once per replica.

The interpreter runs each whole local word for each common low class. ADD
and COPY phases select complete packets; children never split the high field.
"""
    for call in catalogue.template["calls"]:
        owners=call["owners"]
        data={family for family,_ in owners[:222]}
        helpers={family for family,_ in owners[222:]}
        need(len(data)==222 and not data.intersection(helpers),
             "completed data endpoints use distinct nonhelper families")
        need(all(owners[i][1]==owners[111+i][1] for i in range(111)),
             "paired data routes preserve low-class packet separation")
    requests={(r.kind,r.stage,r.position):r for r in catalogue.requests if r.kind!="IDLE"}
    idles={i:[r for r in catalogue.requests if r.kind=="IDLE" and r.stage==i]
           for i in range(10)}
    counts=Counter();digest=sha256();bound=[]
    for event in catalogue.template["schedule"]:
        kind=event["kind"]
        if kind=="local_cover_sweep":
            stage=event["stage"];call=catalogue.template["calls"][32*stage]
            opened=None
            for position,op in enumerate(catalogue.template["local_programs"][call["orientation"]]):
                code,role=op[:2]
                if code in (0,2):
                    label="MOVE" if code==0 else "COPY"
                    request=requests[label,stage,position]
                    need(request.role==role,"caller/provider role")
                    bound.append(request.record());counts[label]+=1
                    if code==2:
                        need(opened is None,"one private caller interval")
                        opened=request
                elif code==1:
                    counts["ADD"]+=1
                    if opened:
                        counts["ADD_with_private"]+=1
                    need(0<=op[1]<=661 and 0<=op[2]<=661,"literal ADD roles")
                    need(op[1]!=661,"private source remains read-only")
                else:
                    need(code==3 and opened is not None,"caller ERASE guard")
                    need((stage,position,opened.position,role,opened.base.key)
                         in catalogue.erase_guards,"source-bound transported ERASE")
                    opened=None;counts["ERASE"]+=1
                digest.update((canonical([stage,position,op])+"\n").encode())
            need(opened is None,"private work closes at local return")
            counts["local_sweeps"]+=1
        elif kind=="idle":
            for request in idles[event["idx"]]:
                bound.append(request.record());counts["IDLE"]+=1
        else:
            need(kind in ("bridge","exchange"),"closed global instruction alphabet")
            counts[kind]+=1
        digest.update((canonical(event)+"\n").encode())
    need(sorted(map(canonical,bound))==sorted(canonical(r.record()) for r in catalogue.requests),
         "caller consumes each paid provider request once")
    return {"canonical_counts":dict(counts),"replicas":32,
            "chronological_sha256":digest.hexdigest(),
            "high_field_recursive_splits":0,"private_work_packets":1,
            "maximum_extra_packet_buffers":4}
