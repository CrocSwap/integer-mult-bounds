"""Exact signed-permutation, actual-source and unchanged-controller checks.

Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from pathlib import Path
from collections import Counter
from fractions import Fraction
import argparse
import gzip
import hashlib
import json
import random
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from physical import A,IR,ROOT,Tape,load_module
from source_binding import check_inputs
from vendor import scalar_tables as scalar
from tables import compile_swap,source_literal,bind_services,need
from fixtures import check_case,encode_field,decode_field,CountedTable


def inputs():
    check_inputs();repo=ROOT.parents[1]
    word=json.loads(gzip.decompress((repo/'research/p104-helper470-twin-rung-removal/WORD.json.gz').read_bytes()))
    caller=json.loads((repo/'research/p104-productive-controller/CONTROLLER.json').read_text())
    return word,caller


def arithmetic():
    counters=Counter();receipts=[]
    for op in ('SWAP','SIGNED_SWAP'):
        table,receipt=compile_swap(op);receipts.append(receipt)
        for w in range(1,6):
            values=range(-(1<<(w-1)),1<<(w-1))
            for x in values:
                for y in values:
                    allowed,result=check_case(table,op,(x,x),(y,y),(w,w))
                    counters['cases']+=1;counters['accepted']+=allowed
                    counters['rejected']+=1-allowed
                    counters['physical_actions']+=result['actions'];counters['table_steps']+=result['steps']
        rng=random.Random(6030)
        for widths in ((1,1),(1,2),(5,5,16,16),(65,129),(129,65,1,2),(2,3,5,8,17,33)):
            for k in range(8):
                xs=tuple(rng.randrange(-(1<<(w-1)),1<<(w-1)) for w in widths)
                ys=tuple(rng.randrange(-(1<<(w-1)),1<<(w-1)) for w in widths)
                if k==0:xs=(0,)*len(widths)
                elif k==1:xs=tuple(-(1<<(w-1)) for w in widths)
                elif k==2:ys=xs
                allowed,result=check_case(table,op,xs,ys,widths)
                counters['wide_or_mixed_fields']+=1;counters['wide_or_mixed_accepted']+=allowed
                counters['physical_actions']+=result['actions'];counters['table_steps']+=result['steps']
    need(counters['cases']==2728 and counters['accepted']==2666 and counters['rejected']==62,
         'closed full signed-domain census')
    return dict(check='arithmetic',counts=dict(counters),tables=receipts)


def binding():
    word,caller=inputs();unit,summary=IR.current_caller(word,caller)
    swaps=[];counts=Counter();scopes=Counter();scalar_count=0;excluded=Counter()
    for event in unit.events:
        if event.op!='SERVICE':continue
        try:op,origin=source_literal(event,caller)
        except ValueError:
            try:scalar.source_literal(event,word,caller)
            except ValueError:excluded[event.token[0]]+=1
            else:scalar_count+=1
        else:swaps.append(event);counts[op]+=1;scopes[origin[0]]+=1
    need(dict(counts)=={'SWAP':5928,'SIGNED_SWAP':4992},'exact current two-output census')
    need(dict(scopes)=={'boundary-right':2808,'outer':4992,'boundary-left':3120},'exact source scope partition')
    need(scalar_count==366842,'retained scalar class is unchanged')
    services,receipts,origins=bind_services(swaps,caller)
    need(len(origins)==10920 and len(receipts)==2,'full current swap catalogue')
    original=next(e for e in swaps if e.token[0]=='outer')
    issuing=next(e for e in IR.current_local(word)[0] if e.op=='PAID')
    names={f:('actual-bank',j) for j,f in enumerate(original.fields)}
    right=IR.remap(original,names,('product-right',2,issuing.rank,issuing.token))
    left=IR.remap(right,{f:f for f in right.fields},('product-left',5,3))
    nested=IR.remap(left,{f:f for f in left.fields},('unit-fragment',7,11,3,0))
    need(source_literal(nested,caller)==source_literal(original,caller),'active source semantics through wrappers')
    need(nested.fields==tuple(names[f] for f in original.fields),'actual ordered remapped owners')
    return dict(check='binding',caller_events=len(unit.events),swap_services=len(origins),
                retained_scalar_services=scalar_count,combined_arithmetic_services=scalar_count+len(origins),
                counts=dict(counts),scopes=dict(scopes),tables=receipts,
                excluded_services=dict(excluded),raw_paid=summary['raw_paid'],
                source_receipt_sha256=hashlib.sha256(json.dumps(origins,separators=(',',':')).encode()).hexdigest())


def controller_run(events,services,values,width):
    public=[Tape(encode_field(v,(width,width)),origin=17+5*i) for i,v in enumerate(values)]
    def body_receipt():
        h=hashlib.sha256()
        for i,t in enumerate(public):
            body=t.body();h.update(i.to_bytes(8,'big'));h.update(len(body).to_bytes(8,'big'));h.update(bytes(body))
        return h.hexdigest()
    input_receipt=body_receipt()
    n=len(public);context=Tape((1,0,1,0,0,1),origin=500000,readonly=True)
    work=[Tape((1,0,1,0,1),origin=510000),Tape((0,1,0,1,0,1,1),origin=520000)]
    payloads=tuple(public+[context]+work)
    stack=load_module('swap_retained_stack',ROOT/'vendor/stack.py')
    program=tuple(A.Instruction('SERVICE',e.fields,e.token) for e in events)+(A.Instruction('RET'),)
    counters={id(t):CountedTable(t) for t in services.values()}
    counted={token:counters[id(t)] for token,t in services.items()}
    admin=[Tape(origin=600000+100*i,marker=A.BASE) for i in range(4)]
    controller=A.Controller(program,n,payloads,*admin,rows=None,services=counted,
                            stack_class=stack.Stack,protected_ports=(n,),
                            primitive_work=(n+1,n+2),primitive_context=(n,))
    controller.run()
    observed=[decode_field(t.body()) for t in public]
    need(all(row[1]==(width,width) for row in observed),'complete controller field shapes')
    need(context.body()==(1,0,1,0,0,1),'borrowed context preserved')
    need(all(t.blank() for t in work),'actual Controller scratch retirement')
    need(all(t.pos==t.origin and t.sentinel_ok() for t in payloads+tuple(admin)),
         'actual Controller complete heads and ancestor ownership')
    result=dict(field_count=n,component_width=width,services=len(events),
                physical_actions=sum(t.actions for t in payloads+tuple(admin)),
                table_steps=sum(t.steps for t in counters.values()),
                program_sha256=hashlib.sha256(json.dumps([(e.op,e.ports,e.token) for e in program],separators=(',',':')).encode()).hexdigest(),
                service_table_sha256s=sorted({hashlib.sha256(json.dumps(t.table,separators=(',',':')).encode()).hexdigest() for t in counters.values()}),
                input_body_sha256=input_receipt,output_body_sha256=body_receipt(),
                body_receipt_format='increasing field index: u64be index, u64be raw length, raw symbol bytes')
    return [row[0] for row in observed],result


def controller_blocks():
    word,caller=inputs();unit,summary=IR.current_caller(word,caller)
    n=len(unit.roles);width=4
    # The full original right-boundary block, after its native entry cut.
    indexed=[(i,e) for i,e in enumerate(unit.events) if e.token[0]=='boundary-right']
    right=[e for _,e in indexed]
    need(len(right)==5720 and indexed[-1][0]-indexed[0][0]+1==len(right),
         'actual uninterrupted right-boundary block')
    swaps=[e for e in right if e.token[-1][0]=='SWAP']
    scalars=[e for e in right if e.token[-1][0] in ('ADD','SCALE')]
    services,_,_=bind_services(swaps,caller)
    earlier,_,_=scalar.bind_services(scalars,word,caller)
    need(set(services).isdisjoint(earlier),'indivisible source class registries');services.update(earlier)
    values=[((r//104+2*(r%104))%7-3,(3*(r//104)+(r%104))%5-2) for r in range(n)]
    expected=[list(v) for v in values]
    # Independent source-array interpretation; it does not read lowered tokens.
    peak=3
    for raw in caller['boundaries']['right_program']:
        for j in range(104):
            x=raw[1]*104+j
            if raw[0]=='SWAP':
                y=raw[2]*104+j;expected[x],expected[y]=expected[y],expected[x]
            elif raw[0]=='SCALE':expected[x]=[Fraction(raw[2])*z for z in expected[x]]
            else:
                need(raw[0]=='ADD','original boundary opcode')
                y=raw[2]*104+j;expected[x]=[a+Fraction(raw[3])*b for a,b in zip(expected[x],expected[y])]
            need(all(Fraction(z).denominator==1 and -8<=z<8 for z in expected[x]),'right boundary fixture admission')
            peak=max(peak,*(abs(z) for z in expected[x]))
    observed,r1=controller_run(right,services,values,width)
    need(observed==[tuple(int(z) for z in row) for row in expected],'original full right-boundary endpoint')
    r1.update(first_event=indexed[0][0],last_event=indexed[-1][0],maximum_absolute_fixture_value=int(peak),
              output_sha256=hashlib.sha256(json.dumps(observed,separators=(',',':')).encode()).hexdigest())
    # A second actual contiguous block covers the first ordered signed swap.
    site=next(i for i,raw in enumerate(caller['physical_events']) if raw[0]=='SIGNED_SWAP')
    indexed=[(i,e) for i,e in enumerate(unit.events) if e.token[0]=='outer' and e.token[1]==site]
    signed=[e for _,e in indexed]
    need(len(signed)==104 and indexed[-1][0]-indexed[0][0]+1==104,'actual uninterrupted signed block')
    services,_,_=bind_services(signed,caller)
    values=[(r%5-2,r%7-3) for r in range(n)]
    raw=caller['physical_events'][site]
    for j in range(104):
        values[raw[1]*104+j]=(-7+j%8,j%7-3)
        values[raw[2]*104+j]=(-8,j%8)
    expected=list(values)
    for j in range(104):
        x,y=raw[1]*104+j,raw[2]*104+j
        expected[x],expected[y]=values[y],tuple(-v for v in values[x])
    observed,r2=controller_run(signed,services,values,width)
    need(observed==expected,'original signed source order including minimum second operands')
    r2.update(source_site=site,first_event=indexed[0][0],last_event=indexed[-1][0],
              output_sha256=hashlib.sha256(json.dumps(observed,separators=(',',':')).encode()).hexdigest())
    return dict(check='controller_blocks',right_boundary=r1,first_signed_block=r2)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--suite',choices=['arithmetic','binding','controller'],required=True)
    args=parser.parse_args();result={'arithmetic':arithmetic,'binding':binding,'controller':controller_blocks}[args.suite]()
    expected=json.loads((ROOT/'RESULT.json').read_text())[args.suite]
    need(json.loads(json.dumps(result))==expected,'committed exact suite receipt')
    print(json.dumps(result,sort_keys=True));print('PASS_CURRENT_SWAP_FLAT_TABLES_'+args.suite.upper())


if __name__=='__main__':main()
