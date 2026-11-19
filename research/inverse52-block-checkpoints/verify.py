"""Check the block sampler, exact resource counts and complete cleanup."""
from hashlib import sha1,sha256
from math import isqrt
from pathlib import Path
import argparse
import importlib.util
import json
import time
import block

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('source_window_checks',block.SOURCE/'verify.py')
source=importlib.util.module_from_spec(spec)
spec.loader.exec_module(source)
need=source.require
PAIRS=[(0,0),(0,1),(1,0),(1,1),(1,51),(51,1),(51,51),(13,26),(26,39),(4,8),(4,13),(26,26),(52-1,26),(7,19),(2,50),(16,48)]


def weights(a,b):
    return ((52-a)*(52-b),(52-a)*b,a*(52-b),a*b)


def reference(a,b,coins,length):
    if a==b==0:
        return 1
    residues=list(weights(a,b))
    node=0
    for t in range(1,length+1):
        leaves=[]
        for label,r in enumerate(residues):
            digit,residues[label]=divmod(2*r,2704)
            if digit:
                leaves.append(label)
        child=2*node+((coins>>(t-1))&1)
        if child<len(leaves):
            return 1|(leaves[child]<<1)|(t<<3)
        node=child-len(leaves)
    return (length+1)<<3


def prefixes(a,b,length):
    if a==b==0:
        return [0,(1<<length)-1]
    live={0:0}
    stopped=set()
    for t in range(1,length+1):
        leaves=sum(((1<<t)*w//2704)&1 for w in weights(a,b))
        following={}
        for node,prefix in live.items():
            for bit in (0,1):
                child=2*node+bit
                word=prefix|(bit<<(t-1))
                if child<leaves:
                    stopped.add(word)
                    stopped.add(word|((1<<length)-(1<<t)))
                else:
                    following[child-leaves]=word
        live=following
    return sorted(stopped|set(live.values()))


def check(length,all_pairs,exhaustive,block_size=None,controls=False):
    built=block.build(length,block_size)
    gates,width=built['gates'],built['wires']
    source.gate_check(gates,width)
    output_set=set(built['output'])
    need(all(not output_set.intersection(c) for _,c in gates),'output never controls computation')
    before,after=[],[]
    summaries=[]
    pairs=[(a,b) for a in range(52) for b in range(52)] if all_pairs else PAIRS
    for a,b in pairs:
        labels=[0]*4;censored=0
        for coins in (range(1<<length) if exhaustive else prefixes(a,b,length)):
            value=reference(a,b,coins,length)
            initial=a|(b<<6)|(coins<<12)
            before.append(initial);after.append(initial|(value<<(12+length)))
            if value&1:
                labels[(value>>1)&3]+=1
            else:
                censored+=1
            need(value==sum(x<<shift for x,shift in zip(source.reference(a,b,coins,length),(0,1,3),strict=True)),'unchanged ordered source function')
        if exhaustive:
            need(labels==[(1<<length)*w//2704 for w in weights(a,b)] and censored==(1<<length)-sum(labels),'exact finite-window probability masses')
        summaries.append([a,b,*labels,censored])
    initial,expected=source.lanes(before,width),source.lanes(after,width)
    actual=source.run(gates,initial,len(before))
    need(actual==expected,'all output, input, coin, checkpoint and work wires')
    need(source.run(tuple(reversed(gates)),expected,len(before))==initial,'literal inverse and all cleanup')
    if controls:
        dirty=initial.copy();dirty_expected=expected.copy()
        # Different output words across lanes test the same XOR interface.
        pattern=sum((i%3!=0)<<i for i in range(len(before)))
        for i,w in enumerate(built['output']):
            dirty[w]^=pattern if i%2 else (1<<len(before))-1
            dirty_expected[w]^=pattern if i%2 else (1<<len(before))-1
        need(source.run(gates,dirty,len(before))==dirty_expected,'arbitrary initial output')
        need(source.run(gates[:built['cleanup_start']],initial,len(before))!=expected,'omitted checkpoint cleanup rejected')
        boundary=(built['output'][3],(built['checkpoints'][1][50],))
        need(gates.count(boundary)==1,'one boundary depth contribution')
        location=gates.index(boundary)
        changed=(*gates[:location],*gates[location+1:])
        need(source.run(changed,initial,len(before))!=expected,'missing block-boundary depth rejected')
    for index in [0,len(before)//2,len(before)-1]:
        need(source.scalar(gates,before[index])==after[index],'separate scalar circuit replay')
    return dict(length=length,block=built['bill']['block'],pairs=len(pairs),domain='all coin strings' if exhaustive else 'all stopping prefixes with zero/one suffixes and all live prefixes',cases=len(before),summary_sha256=sha256(json.dumps(summaries,separators=(',',':')).encode()).hexdigest(),bill=built['bill'],dirty_output_and_mutations=controls)


def collect():
    pins=json.loads((HERE/'SOURCE-PINS.json').read_text())['sources']
    for pin in pins:
        raw=(HERE/pin['retained']).read_bytes()
        need(sha256(raw).hexdigest()==pin['sha256'],'source SHA256')
        need(sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==pin['git_blob'],'source Git blob')
    arithmetic=source.arithmetic_checks()
    checked=0
    for length in range(1,1025):
        chosen=block.plan(length)
        alternatives=[block.plan(length,b) for b in range(1,length+1)]
        best=min((x['clean_work_bits'],x['gates']) for x in alternatives)
        need((chosen['clean_work_bits'],chosen['gates'])==best,'optimal block work and tie-break gate count')
        need(chosen['history_bits']==51*(1+isqrt(4*length-1)),'ceil two square-root state bound')
        checked+=len(alternatives)
    partitions=0
    for length in range(1,17):
        best=None
        for cuts in range(1<<(length-1)):
            ends=[0]+[i+1 for i in range(length-1) if cuts>>i&1]+[length]
            widths=[b-a for a,b in zip(ends,ends[1:])]
            count,size,last=len(widths),max(widths),widths[-1]
            cost=(559+51*(count+size),3643+977*(4*length-2*last)+102*(count-1)+2*length)
            best=cost if best is None else min(best,cost)
            partitions+=1
        chosen=block.plan(length)
        need((chosen['clean_work_bits'],chosen['gates'])==best,'all unequal-block partitions')
    bills=[]
    for length in [1,2,3,4,5,7,8,15,16,31,32,63,64,127]:
        new=block.build(length)['bill']
        old=block.build(length,length)['bill']
        need(old['gates']==3643+1956*length and old['clean_work_bits']==610+51*length,'full-history positive control')
        bills.append(dict(new=new,full_history=old))
    windows=[check(n,True,True,controls=n==4) for n in [1,3,4,8]]
    windows.append(check(16,True,False))
    windows.extend(check(n,False,False) for n in [31,64])
    windows.extend(check(8,False,True,b) for b in [1,2,3,5,8])
    for args in [(0,None),(-1,None),(True,None),(1.0,None),(8,0),(8,9),(8,False),(8,1.5)]:
        try:
            block.plan(*args)
        except ValueError:
            continue
        raise ValueError('invalid window or block accepted')
    return dict(source_files=len(pins),arithmetic=arithmetic,planner_alternatives=checked,unequal_partitions=partitions,selected_pairs=PAIRS,windows=windows,bills=bills,
                clean_work_formula='559+51*ceil(2*sqrt(L))',gate_formula='3643+977*(4*L-2*r)+102*(K-1)+2*L',
                scope='Optimal workspace, then gate count, over all partitions in the stated one-level checkpoint architecture; no global reversible-circuit optimum or physical tape claim.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--record',action='store_true')
    args=parser.parse_args();start=time.monotonic();result=json.loads(json.dumps(collect()))
    if args.record:
        (HERE/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    else:
        need(result==json.loads((HERE/'RESULT.json').read_text()),'deposited certificate')
    print('PASS_INVERSE52_BLOCK_CHECKPOINTS',sum(w['cases'] for w in result['windows']),'whole-wire cases','524800 block choices',round(time.monotonic()-start,2),'seconds')
