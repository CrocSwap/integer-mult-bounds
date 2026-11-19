"""Emit the exact sampler with reversible block checkpoints.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
This applies classical Bennett checkpointing to the retained sampler.
"""
from collections import Counter
from math import isqrt
from pathlib import Path
import sys

SOURCE=Path(__file__).resolve().parent/'retained/source7773'
sys.path.insert(0,str(SOURCE))
import window as old


def plan(length,block=None):
    if type(length) is not int or length<1:
        raise ValueError('window length must be a positive integer')
    if block is None:
        slots=1+isqrt(4*length-1)
        block=(slots+isqrt(slots*slots-4*length))//2
    if type(block) is not int or not 1<=block<=length:
        raise ValueError('block length must lie between one and the window length')
    count=(length+block-1)//block
    first=length-(count-1)*block
    last=block
    draws=4*length-2*last
    pop=(length+1).bit_count()
    return dict(length=length,block=block,blocks=count,first=first,last=last,draw_oracles=draws,
                X=260+90*draws+pop,CNOT=2449+717*draws+102*(count-1)+2*length-pop,
                Toffoli=934+170*draws,gates=3643+977*draws+102*(count-1)+2*length,
                clean_work_bits=559+51*(count+block),history_bits=51*(count+block),temporary_bits=559)


def build(length,block=None):
    bill=plan(length,block)
    size,count=bill['block'],bill['blocks']
    depth_width=(length+1).bit_length()
    params=(tuple(range(6)),tuple(range(6,12)))
    coins=tuple(range(12,12+length))
    output=tuple(range(12+length,15+length+depth_width))
    history_start=output[-1]+1
    packets=[tuple(range(history_start+51*i,history_start+51*(i+1))) for i in range(count+size)]
    checkpoints,local=packets[:count],packets[count:]
    scratch_start=packets[-1][-1]+1
    c=old.Circuit(scratch_start)
    preparation=old.clean_oracle(c,checkpoints[0],old.prepare(c,*params))
    peak=c.next_wire
    gates=list(preparation)
    gates.extend((output[3+i],()) for i,v in enumerate(old.bits(length+1,depth_width)) if v)
    cleanup=[]
    depth_uses=[]
    start=0
    for part in range(count):
        width=bill['first'] if part==0 else size
        states=[checkpoints[part],*local[:width]]
        computation=[]
        for j in range(width):
            c=old.Circuit(scratch_start)
            computation.extend(old.clean_oracle(c,states[j+1],old.advance(c,states[j],coins[start+j])))
            peak=max(peak,c.next_wire)
        gates.extend(computation)
        stop=width+1 if part==count-1 else width
        for j in range(stop):
            t=start+j
            depth_uses.append(t)
            gates.extend((output[3+i],(states[j][50],)) for i,v in enumerate(old.bits(t^(t+1),depth_width)) if v)
        if part==count-1:
            done=states[-1][50]
            gates.extend([(output[0],(done,)),(output[1],(done,states[-1][48])),(output[2],(done,states[-1][49]))])
        else:
            copy=[(target,(source,)) for target,source in zip(checkpoints[part+1],states[-1],strict=True)]
            gates.extend(copy)
            cleanup.append((*computation,*copy,*reversed(computation)))
        gates.extend(reversed(computation))
        start+=width
    cleanup_start=len(gates)
    for segment in reversed(cleanup):
        gates.extend(reversed(segment))
    gates.extend(reversed(preparation))
    counts=Counter(len(controls) for _,controls in gates)
    actual=dict(X=counts[0],CNOT=counts[1],Toffoli=counts[2],gates=len(gates),clean_work_bits=peak-history_start,temporary_bits=peak-scratch_start)
    if any(actual[k]!=bill[k] for k in actual) or depth_uses!=list(range(length+1)):
        raise ValueError('generated checkpoint bill or depth coverage')
    if any(target<output[0] or len(set((target,*controls)))!=1+len(controls) for target,controls in gates):
        raise ValueError('input target or aliased gate')
    return dict(gates=tuple(gates),wires=peak,params=params,coins=coins,output=output,
                checkpoints=checkpoints,local=local,cleanup_start=cleanup_start,depth_uses=depth_uses,bill=bill)
