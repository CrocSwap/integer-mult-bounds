"""Bounded physical, exact-oracle and source-binding verification.

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
from tables import compile_scalar, bind_services, source_literal, need
from physical import A, IR, ROOT, Tape, execute, encode_symbols, symbols_for, decode_body, load_module
from source_binding import check_inputs


def repository():
    return ROOT.parents[1]


def inputs():
    check_inputs()
    word = json.loads(gzip.decompress((repository()/'research/p104-helper470-twin-rung-removal/WORD.json.gz').read_bytes()))
    caller = json.loads((repository()/'research/p104-productive-controller/CONTROLLER.json').read_text())
    return word,caller


def check_case(table,op,q,xs,ys,width):
    expected = [Fraction(x)+(q*y) if op=='ADD' else q*x for x,y in zip(xs,ys)]
    allowed = all(z.denominator==1 and -(1<<(width-1)) <= z < 1<<(width-1) for z in expected)
    result = execute(table,op,xs,ys,width)
    need((result['error'] is None)==allowed,'exact representability/range iff')
    public,work = result['public'],result['work']
    need(all(t.sentinel_ok() for t in public+work),'protected ancestor sentinels')
    if allowed:
        need(result['output']==tuple(int(z) for z in expected),'independent Fraction endpoint')
        need(len(public[0].body())==len(result['before'][0]),'exact complete target extent')
        need(all(t.blank() for t in work),'physical scratch erased on success')
        need(all(t.pos==t.origin for t in public+work),'complete origin return')
        d=0;b=q.denominator
        while b%2==0:d+=1;b//=2
        length=len(xs)*(width+1)
        need(result['actions'] <= 1024*(d+2)*(length+1),'proven complete linear cell-action ceiling')
        need(work[0].highwater-work[0].origin <= 3*length,'output high-water bound')
        need(work[1].highwater-work[1].origin <= 3*(length+1),'guide high-water bound')
    else:
        need(public[0].body()==result['before'][0] and public[0].writes==0,
             'whole-field arithmetic rejection precedes every target write')
    if op=='ADD':
        need(public[1].body()==result['before'][1] and public[1].writes==0,'borrowed source preserved')
    return int(allowed),result['actions']


def arithmetic():
    word,_=inputs()
    variants=sorted({(e[0],Fraction(e[-2])) for e in word['program'] if e[0] in ('ADD','SCALE')})
    counters=Counter();records=[]
    for op,q in variants:
        table,receipt=compile_scalar(op,q);records.append(receipt)
        for width in range(1,5):
            values=range(-(1<<(width-1)),1<<(width-1))
            for x in values:
                for y in values if op=='ADD' else (0,):
                    passed,actions=check_case(table,op,q,(x,x),(y,y),width)
                    counters['cases']+=1;counters['accepted']+=passed
                    counters['rejected']+=1-passed;counters['physical_actions']+=actions
        # Deterministic wide complete fields: zero, extrema, equal/correlated
        # operands, multiple records, and both integer and inexact divisions.
        rng=random.Random(6030)
        for width in (5,16,65,129):
            edge=1<<(width-1)
            xs=(-edge,edge-1,0,0,rng.randrange(-edge,edge),rng.randrange(-edge,edge))
            ys=(-edge,edge-1,0,1,rng.randrange(-edge,edge),rng.randrange(-edge,edge))
            passed,actions=check_case(table,op,q,xs,ys,width)
            counters['wide_fields']+=1;counters['wide_accepted']+=passed
            counters['physical_actions']+=actions
            # Universally admitted multi-record positive control for each q.
            xs=(0,0,0,0,0,0);ys=(0,0,0,0,0,0)
            passed,actions=check_case(table,op,q,xs,ys,width)
            need(passed,'wide zero control');counters['wide_zero_fields']+=1
            counters['physical_actions']+=actions
    # General rational theorem checks beyond the concrete dyadic catalogue.
    for op,q in [('SCALE',Fraction(1,3)),('SCALE',Fraction(-7,6)),('ADD',Fraction(1,5))]:
        table,_=compile_scalar(op,q)
        for width in range(1,5):
            values=range(-(1<<(width-1)),1<<(width-1))
            for x in values:
                for y in values if op=='ADD' else (0,):
                    passed,actions=check_case(table,op,q,(x,x),(y,y),width)
                    counters['extra_rational_cases']+=1
                    counters['physical_actions']+=actions
    return dict(check='arithmetic',counts=dict(counters),variants=records)


def binding():
    word,caller=inputs()
    unit,summary=IR.current_caller(word,caller)
    supported=[];scopes=Counter();variants=Counter();excluded=Counter()
    for event in unit.events:
        if event.op!='SERVICE':continue
        try:op,q,origin=source_literal(event,word,caller)
        except ValueError:excluded[event.token[0]]+=1
        else:
            supported.append(event);scopes[origin[0]]+=1;variants[(op,str(q))]+=1
    need(len(supported)==366842,'complete selected arithmetic service coverage')
    need(dict(scopes)=={'boundary-right':2912,'local':346770,'query-add':1560,
                       'outer':9360,'boundary-left':6240},'exact caller scope partition')
    services,receipts,origins=bind_services(supported,word,caller)
    need(len(receipts)==42 and len(origins)==366842,'full source catalogue')
    # Preserve exact semantics through the actual source remap API. Neither
    # raw role numbers nor equal-rank substitutes are used as physical ports.
    original=next(e for e in supported if e.token[0]=='caller-local')
    names={f:('actual-bank',j) for j,f in enumerate(original.fields)}
    remapped=IR.remap(original,names,('unit-fragment',7,11,3,0))
    op,q,origin=source_literal(remapped,word,caller)
    need(remapped.fields==tuple(names[f] for f in original.fields),'actual mapped owners')
    need((op,q,origin)==source_literal(original,word,caller),'nested scalar semantics')
    # A chronological product carries an issuing MOVE token separately from
    # the active scalar. Follow the original wrapper's last member only.
    issuing=next(e for e in IR.current_local(word)[0] if e.op=='PAID')
    right=IR.remap(original,{f:f for f in original.fields},
                   ('product-right',3,issuing.rank,issuing.token))
    left=IR.remap(right,{f:f for f in right.fields},('product-left',2,7))
    nested=IR.remap(left,{f:f for f in left.fields},('unit-fragment',7,11,3,0))
    need(source_literal(nested,word,caller)==(op,q,origin),
         'active scalar separated from issuing paid provenance')
    rows=sum(x['rows'] for x in receipts)
    return dict(check='binding',caller_events=len(unit.events),services=len(origins),
                variants=len(receipts),table_rows=rows,scopes=dict(scopes),
                excluded_services=dict(excluded),raw_paid=summary['raw_paid'],
                source_receipt_sha256=hashlib.sha256(json.dumps(origins,separators=(',',':')).encode()).hexdigest())


def controller_prefix():
    word,caller=inputs()
    raw,summary=IR.current_local(word)
    # The actual first scalar block, after source INIT(778) and before its
    # first native MOVE. All its owners are borrowed complete fields here.
    events=[]
    for event in raw[1:]:
        if event.op!='SERVICE' or event.token[0]!='local':break
        events.append(event)
    need(len(events)==9895 and events[0].token[1]==1 and events[-1].token[1]==9895,
         'actual uninterrupted selected source block')
    services,_,_=bind_services(events,word)
    n=word['public']+word['owned_fields'];width=11
    values=[(16*(i%7-3),16*(i%5-2)) for i in range(word['public'])]
    values += [(0,0) for _ in range(word['owned_fields'])]
    expected=[list(v) for v in values]
    for event in events:
        op,q,_=source_literal(event,word)
        target=event.fields[0]
        if op=='SCALE':expected[target]=[q*x for x in expected[target]]
        else:expected[target]=[x+q*y for x,y in zip(expected[target],expected[event.fields[1]])]
        need(all(Fraction(x).denominator==1 and -1024<=x<1024 for x in expected[target]),
             'source-prefix exact oracle admission')
    public=[Tape(encode_symbols(symbols_for(v,width)),origin=17+5*i) for i,v in enumerate(values)]
    context=Tape((1,0,1,0,0,1),origin=5000,readonly=True)
    work=[Tape(origin=5100),Tape(origin=5200)]
    payloads=tuple(public+[context]+work)
    stack=load_module('scalar_retained_stack',ROOT/'vendor/stack.py')
    program=tuple(A.Instruction('SERVICE',e.fields,e.token) for e in events)+(A.Instruction('RET'),)
    admin=[Tape(origin=6000+100*i,marker=A.BASE) for i in range(4)]
    controller=A.Controller(program,n,payloads,*admin,rows=None,services=services,
                            stack_class=stack.Stack,protected_ports=(n,),
                            primitive_work=(n+1,n+2),primitive_context=(n,))
    controller.run()
    observed=[decode_body(t.body(),width) for t in public]
    need(observed==[tuple(int(x) for x in v) for v in expected],'actual Controller exact source-prefix endpoint')
    need(context.body()==(1,0,1,0,0,1),'borrowed context preserved')
    need(all(t.blank() for t in work),'actual Controller work retirement')
    need(all(t.pos==t.origin and t.sentinel_ok() for t in payloads+tuple(admin)),
         'actual Controller complete heads and ancestor ownership')
    return dict(check='controller_prefix',source_first=1,source_last=9895,
                actual_scalar_services=len(events),field_count=n,component_width=width,
                physical_actions=sum(t.actions for t in payloads+tuple(admin)),
                output_sha256=hashlib.sha256(json.dumps(observed,separators=(',',':')).encode()).hexdigest())


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--suite',choices=['arithmetic','binding','controller'],required=True)
    args=parser.parse_args()
    result={'arithmetic':arithmetic,'binding':binding,'controller':controller_prefix}[args.suite]()
    expected=json.loads((ROOT/'RESULT.json').read_text())[args.suite]
    need(json.loads(json.dumps(result))==expected,'committed exact suite receipt')
    print(json.dumps(result,sort_keys=True))
    print('PASS_CURRENT_SCALAR_FLAT_TABLES_'+args.suite.upper())


if __name__=='__main__':main()
