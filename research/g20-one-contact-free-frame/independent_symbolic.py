#!/usr/bin/env python3
"""Independent complete moved-frame bills by symbolic chronological chart propagation.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
No primary executable imports; the metric is the separately checked bucket matrix.
"""
import argparse
from collections import Counter, defaultdict
from copy import deepcopy
import gzip
from hashlib import sha256
import json
from pathlib import Path

WORD_SHA='8dd441fdb9c8923df06eb5ebfda37d03e4539f2305763e688d8c7025d196c4b1'
METRIC_SHA='4e0b9aad61d7d3c9bc249c76dce0729a65216ae7bb2613c060ab2e6cd31f4a3f'
VARIABLE=-1

def need(ok,message):
    if not ok:raise ValueError(message)

def read(path):
    raw=path.read_bytes()
    return json.loads(gzip.decompress(raw) if raw[:2]==b'\x1f\x8b' else raw)

def one_contact_words(records):
    positions=defaultdict(list)
    for index,event in enumerate(records):
        if event[0]=='ADD':positions[event[1:3]].append(index)
    for (a,b),indices in sorted(positions.items()):
        for offset,left in enumerate(indices):
            for right in indices[offset+1:]:
                contacts=[];blocked=False
                for index in range(left+1,right):
                    event=records[index]
                    if event[0] in('ERASE','INIT'):
                        if event[1] in(a,b):blocked=True;break
                    else:
                        d,s,frame=event[1:]
                        if(d,s)==(b,a):blocked=True;break
                        if d==b:contacts.append((index,('ADD',a,s,frame)))
                        elif s==a:contacts.append((index,('ADD',d,b,frame)))
                if blocked or len(contacts)!=1:continue
                contact,extra=contacts[0];changed=[];correction_index=None
                for index,event in enumerate(records):
                    if index in(left,right):continue
                    changed.append(event)
                    if index==contact:
                        correction_index=len(changed);changed.append(extra)
                need(correction_index is not None,'inserted correction location')
                yield left,right,correction_index,changed

def chronological(records,start,final,owned,metric,correction_index=None,new_frame=VARIABLE):
    """Carry a formal chart variable through complete states, without trace adjacency."""
    rows=[{index} for index in range(len(start))];state=list(start)
    fixed,symbolic=Counter(),Counter()
    def demand(role,target):
        source=state[role]
        if source==target:return
        if source is None:
            need(role in owned and not rows[role],'only whole-zero owned None header')
        elif rows[role]:
            need(target is not None,'initialized paid target')
            if VARIABLE in(source,target):symbolic[source,target]+=1
            else:
                rank=metric[source][target];need(rank>0,'positive metric for distinct frames');fixed[rank]+=1
        state[role]=target
    for index,event in enumerate(records):
        op,d=event[:2]
        if op in('INIT','ERASE'):
            need(d in owned and(op!='INIT' or not rows[d]),'legal owned reset')
            rows[d]=set();state[d]=event[2];continue
        need(op=='ADD','scalar alphabet')
        s,frame=event[2:]
        if not rows[s]:continue
        if index==correction_index:frame=new_frame
        demand(d,frame);demand(s,frame)
        rows[d]=rows[d].symmetric_difference(rows[s])
    for role,frame in enumerate(final):
        if role in owned:need(not rows[role],'owned final zero')
        else:demand(role,frame)
        state[role]=frame
    need(state==list(final),'all final frames')
    return fixed,symbolic,rows

def substitute(fixed,symbolic,frame,metric):
    bill=fixed.copy()
    for (a,b),count in symbolic.items():
        a=frame if a==VARIABLE else a;b=frame if b==VARIABLE else b
        if a!=b:bill[metric[a][b]]+=count
    return bill

def delta(bill,base):
    return [[rank,bill[rank]-base[rank]] for rank in sorted(bill.keys()|base.keys()) if bill[rank]!=base[rank]]

def partition_sign(shape, proof):
    positive=Counter({rank:count for rank,count in shape if count>0})
    negative=Counter({rank:-count for rank,count in shape if count<0})
    actual=Counter(proof['left']);targets=Counter();strict=bool(proof['left'])
    for target,group in proof['groups']:
        need(type(target) is int and target>0 and group and all(type(rank) is int and rank>0 for rank in group),'positive typed partition block')
        need(sum(group)>=target,'partition block dominates target')
        targets[target]+=1;actual.update(group)
        strict |= len(group)>1 or sum(group)>target
    need(actual==positive and targets==negative,'all signed occurrences covered once')
    need(strict,'strict partition sign')


def indexed_outcomes(receipt):
    rows=receipt['outcomes'];keys=[tuple(row[:4]) for row in rows]
    need(len(keys)==len(set(keys)),'unique complete assignment keys')
    return {key:row[4] for key,row in zip(keys,rows)}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--word',type=Path,required=True);parser.add_argument('--metric',type=Path,required=True);parser.add_argument('--certificate',type=Path,required=True);args=parser.parse_args()
    need(sha256(args.word.read_bytes()).hexdigest()==WORD_SHA,'frozen source word')
    raw_metric=gzip.decompress(args.metric.read_bytes())
    need(sha256(raw_metric).hexdigest()==METRIC_SHA,'independently computed integer metric bytes')
    frozen=json.loads(raw_metric);codes=frozen['codes'];metric={a:dict(zip(codes,row)) for a,row in zip(codes,frozen['matrix'])}
    need(len(codes)==645 and all(len(row)==645 for row in frozen['matrix']),'complete645-square metric')
    word,receipt=read(args.word),read(args.certificate);records=[tuple(event) for event in word['records'] if event[0] not in('Q','ZERO_Q')]
    base=Counter(event[4] for event in word['records'] if event[0]=='Q');owned=set(word['owned']);width=len(word['start'])
    endpoint=[set() if i in owned else {i} ^ ({i-111} if 111<=i<222 else set()) for i in range(width)]
    baseline,symbols,rows=chronological(records,word['start'],word['final'],owned,metric)
    need(not symbols and baseline==base and rows==endpoint,'source complete invoice and endpoint')
    actual=indexed_outcomes(receipt);expected={};shapes=Counter();summaries=[];numeric_checks=0;variable_patterns=Counter()
    for left,right,at,changed in one_contact_words(records):
        fixed,symbolic,rows=chronological(changed,word['start'],word['final'],owned,metric,at)
        need(rows==endpoint,'changed all685 independent endpoints')
        need(all(VARIABLE in pair for pair in symbolic),'each variable request is marked')
        old=changed[at][-1]
        targets={old,codes[0],codes[-1],codes[(left+right)%len(codes)]}
        variable_patterns[sum(symbolic.values())]+=1
        for frame in codes:
            value=delta(substitute(fixed,symbolic,frame,metric),base)
            key=(left,right,at,frame);expected[key]=value;shapes[tuple(map(tuple,value))]+=1
            need(key in actual and actual[key]==value,'every independent assignment invoice')
            if frame in targets:
                numeric,remaining,numeric_rows=chronological(changed,word['start'],word['final'],owned,metric,at,frame)
                need(not remaining and delta(numeric,base)==value and numeric_rows==endpoint,'independent full numeric replay agrees with symbolic substitution')
                numeric_checks+=1
        summaries.append({'left':left,'right':right,'correction_index':at,'symbolic_paid_demands':sum(symbolic.values())})
    need(set(actual)==set(expected),'complete assignment domain, no extra cases')
    need(len(summaries)==184 and len(expected)==118680 and len(shapes)==245,'exact exhaustive counts')
    exceptional=((2,-1),(3,1),(4,1),(5,-1))
    need(shapes[exceptional]==3,'three strictly concave exceptional cases')
    covered=set()
    for entry in receipt['proofs']:
        shape=tuple(map(tuple,entry['delta']))
        need(shape not in covered and entry['count']==shapes[shape],'unique exact shape multiplicity')
        covered.add(shape)
        if shape==exceptional:
            need(entry['proof']['kind']=='strict_decreasing_increments','exact exceptional sign rule')
        else:
            proof=entry['partition'] if 'partition' in entry else entry['proof']['partition']
            partition_sign(shape,proof)
    need(covered | {exceptional} == set(shapes),'every sign shape is certified')
    controls=[]
    def reject(name,test):
        try:test()
        except (ValueError,KeyError):controls.append(name)
        else:raise ValueError('accepted mutant '+name)
    wrong=dict(actual);wrong.pop(next(iter(wrong)));reject('missing_assignment',lambda:need(set(wrong)==set(expected),'domain'))
    wrong=deepcopy(actual);key=next(iter(wrong));wrong[key]=[];reject('wrong_invoice',lambda:need(wrong[key]==expected[key],'invoice'))
    duplicate=deepcopy(receipt);duplicate['outcomes'].append(duplicate['outcomes'][0]);reject('duplicate_assignment',lambda:indexed_outcomes(duplicate))
    toy_metric={0:{0:0,1:1,2:2},1:{0:1,1:0,2:1},2:{0:2,1:1,2:0}}
    bill,syms,_=chronological([('ERASE',1,0),('ADD',0,1,1)],[0,0],[0,None],{1},toy_metric,1)
    need(not bill and not syms,'zero correction source creates no variable demands');controls.append('zero_source_omits_symbolic_demands')
    bill,syms,_=chronological([('ERASE',0,0),('ADD',0,1,1),('ERASE',0,None)],[0,0],[None,2],{0},toy_metric,1)
    need(sum(syms.values())==2 and substitute(bill,syms,1,toy_metric)=={1:2},'zero destination free and source final return paid');controls.append('zero_destination_and_final_return')
    reject('dirty_owned_init',lambda:chronological([('INIT',0,0)],[0],[None],{0},toy_metric))
    reject('reused_partition_occurrence',lambda:partition_sign(((1,2),(2,-1)),{'groups':[[2,[1,1]]],'left':[1]}))
    print(json.dumps({'status':'PASS_INDEPENDENT_FREE_FRAME_SYMBOLIC','intervals':len(summaries),'frames':len(codes),'assignments':len(expected),'shapes':len(shapes),'exceptional_shape_count':shapes[exceptional],'full_numeric_replays':numeric_checks,'symbolic_demand_counts':dict(sorted(variable_patterns.items())),'controls':controls,'scope':'all invoices by independent full symbolic chart propagation; independent multiset sign checks and separate integer metric premise'},sort_keys=True,indent=2))

if __name__=='__main__':main()
