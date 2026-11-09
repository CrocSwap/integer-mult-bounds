"""Dynamic-grid codec, metadata, ownership and mutation controls.

Finite sweeps delimit their domains; the all-width arguments are in PROOF.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from contextlib import ExitStack
from fractions import Fraction
import json
from types import MethodType
from check_rounded import (Provider,PaidService,RoundedOverflow,S,A,C,Count,HERE,need,
    bank,put,body,encode_header,decode_header,encode_components,decode_components,
    descriptor,upward,run_case)

def codec(h,g,values,lift=False):
    provider,work,field,context=bank(1)
    margin=(g+2)//2+1;wide=h+g+margin
    put(field,encode_components(values,h) if lift else [])
    if not lift:put(work[0],encode_components(values,wide))
    tapes=(*work,field,context);before=sum(t.actions() for t in tapes)
    provider.cohort.start();cleanup=ExitStack();error=None
    try:
        with C.execution(),provider.scope.installed():
            def own(x):cleanup.callback(x.close);return x
            ch,cg,cm,cn=(own(Count.literal(x)) for x in (h,g,margin,len(values)))
            if lift:
                provider.lift(A.CodedPort(field),ch,cg,cm,cn)
                need(decode_components(body(work[0]),wide)==[x<<g for x in values],
                     'literal lift equals independent signed bitstring oracle')
            try:provider.drop(ch,cg,cm,cn)
            except RoundedOverflow as caught:error=str(caught)
        expected=values if lift else [upward(Fraction(x,1<<g)) for x in values]
        overflow=any(not -(1<<(h-1))<=x<(1<<(h-1)) for x in expected)
        need((error is not None)==overflow,'codec rejects iff mathematical rounded result outside signed range')
        if not overflow:need(decode_components(body(work[1]),h)==expected,'exact once-rounded codec result')
    finally:
        with C.execution(),provider.scope.installed():cleanup.close();provider.pool.empty()
        provider.cohort.finish()
        for p in work[:3]:A.retire(p)
        A.origin(field);A.origin(context)
    need(all(not body(t) and t.head==t.origin for t in work),'codec full physical retirement')
    return dict(h=h,g=g,H=wide,components=len(values),lift=lift,overflow=error,
                actions=sum(t.actions() for t in tapes)-before)

def codecs():
    rows=[];accepted=0;rejected=0;lifted=0
    for h in range(2,5):
        for g in range(1,4):
            lower=-(1<<(h-1))*(1<<g)-(1<<(g-1))
            upper=(1<<(h-1))*(1<<g)-(1<<(g-1))-1
            values=list(range(lower,upper+1));rows.append(codec(h,g,values));accepted+=len(values)
            wide=h+g+(g+2)//2+1
            for value in sorted({lower-1,upper+1,-(1<<(wide-1)),(1<<(wide-1))-1}):
                rows.append(codec(h,g,[0,value]));rejected+=1
    for h in range(2,6):
        for g in (1,2,5):
            values=list(range(-(1<<(h-1)),1<<(h-1)))
            rows.append(codec(h,g,values,True));lifted+=len(values)
    need(upward(Fraction(-1,2))==0 and upward(Fraction(-3,2))==-1,'negative ties use mathematical floor')
    return dict(cases=rows,complete_accepted_drop_values=accepted,overflow_controls=rejected,
                complete_lift_values=lifted,drop_domain='h=2..4,g=1..3; every representable rounded output preimage',
                lift_domain='h=2..5,g in {1,2,5}; every signed h-bit input')

def metadata_case(rank,f,h):
    provider,work,field,context=bank(rank)
    coefficients=3 if f==7 else 1
    values=descriptor(h,f,rank,coefficients=coefficients);original=encode_header(values)
    put(context,original);put(field,encode_components([0,0],h))
    before=sum(t.actions() for t in (*work,field,context))
    provider.cohort.start();cleanup=ExitStack()
    try:
        with C.execution(),provider.scope.installed():
            header=provider.read_header(A.BinaryContextPort(context))
            for value in header.values():cleanup.callback(value.close)
            width=provider.component_width(A.CodedPort(field));cleanup.callback(width.close)
            g,margin,wide,components,widened=provider.prepare(header,width,cleanup)
            provider.write_header(widened)
        H=h+rank*f+(rank*f+2)//2+1
        expected=dict(values,record_bits=6*coefficients*(H+1),row_bits=(1<<values['within_bits'])*6*coefficients*(H+1))
        observed=body(work[2]);need(decode_header(observed)==expected,'all23 widened fields and exact complete row size')
        ratio=Fraction(H+1,h+1);L=0
        while (1<<L)<ratio:L+=1
        need(len(observed)<=len(original)+4*L,'exact self-delimiting header growth')
        provider.child.view.prepare()
        try:
            child=body(provider.child.view.context.tape)
            need(decode_header(child)==dict(expected,f=rank*f,cutoff=rank*f),
                 'current cutoff transport sees widened fields and preserves all others')
            need(len(child)<=len(observed)+12,'subsequent rank view adds at most12 physical bits')
        finally:provider.child.view.release()
        need(body(context)==bytes(original),'original public header remains byte equal')
        peak=provider.pool.peak
    finally:
        with C.execution(),provider.scope.installed():cleanup.close();provider.pool.empty()
        provider.cohort.finish()
        for p in work[:3]:A.retire(p)
    need(all(not body(t) and t.head==t.origin for t in work) and context.head==context.origin,
         'widened and cutoff descriptors fully retired')
    return dict(rank=rank,f=f,h=h,H=H,original_E=len(original),widened_E=len(observed),
                coefficients=coefficients,
                private_child_E=len(child),wrapper_live_peak=peak,
                actions=sum(t.actions() for t in (*work,field,context))-before,
                metadata_only=True)

def metadata():
    rows=[metadata_case(r,f,(2,3,17,31)[j]) for r in range(1,9) for j,f in enumerate((1,2,7,31))]
    entries=S.catalog.catalog()[1]
    representatives=[next(t for t in entries.values() if t[1].rank==r) for r in range(1,9)]
    need(all(PaidService(t[1]).port_count==521 for t in representatives),'fixed inventory for every actual source rank')
    invalid=0
    for rank in (0,9,-1,True,1.5):
        try:Provider(rank)
        except ValueError:invalid+=1
        else:raise ValueError('invalid static rank accepted')
    provider,work,field,context=bank(1);bad_grants=0
    for bad in (work[:-1],work[:-1]+[work[0]],work[:-1]+[context]):
        try:provider.bind(bad,A.BinaryContextPort(context))
        except ValueError:bad_grants+=1
        else:raise ValueError('aliased/incomplete private grant accepted')
    return dict(cases=rows,all_source_occurrences=len(entries),source_ranks=8,private_ports=521,
                invalid_ranks=invalid,bad_grants=bad_grants,universal_domain_proved_not_enumerated=True)

def mutations():
    # Same complete physical provider, with one deliberate finite-control fault.
    source=(HERE/'rounded_leaf.py').read_text();results=[]
    edits=(('rounding-bit','carry=source.read();need(carry in (0,1)',
                         'carry=0;need(carry in (0,1)'),
           ('signed-overflow',"if overflow:raise RoundedOverflow('nearest-up final output exceeds signed public width')",
                              'if False:raise RoundedOverflow("disabled")'))
    for label,old,new in edits:
        need(source.count(old)==1,'unique deliberate mutation site')
        namespace={'__name__':'rounded_mutation_'+label};exec(compile(source.replace(old,new),'<deliberate mutation>','exec'),namespace)
        provider,work,field,context=bank(1)
        provider.drop=MethodType(namespace['Provider'].drop,provider)
        values=[(1,0),(0,0)] if label=='rounding-bit' else [(0,0),(3,-3),(0,0),(3,3)]
        try:run_case(label,values,3,a=1 if label=='rounding-bit' else 2,reusable=(provider,work,field,context))
        except ValueError as error:
            need(str(error) in ('complete rational answer or protected original','true mathematical final overflow iff'),
                 'independent endpoint/overflow oracle caught intended mutation')
            results.append(dict(mutation=label,detected_by=str(error)))
        else:raise ValueError('semantic mutation escaped independent oracle')
    return results

def history():
    values=[((j*3)%5-2,(j*7)%5-2) for j in range(16)]
    large,reusable=run_case('retained-large',values,4,a=4,K=2,rho=1,active=1)
    small,_=run_case('retained-small',[(1,0),(0,0)],3,reusable=reusable)
    fresh,_=run_case('fresh-small',[(1,0),(0,0)],3)
    need(small['actions']==fresh['actions'],'short call does not rescan old blank historical extent')
    need(sum(small['private_visited_extents'])>sum(fresh['private_visited_extents']),
         'completed larger history remains charged by physical role')
    return dict(large_actions=large['actions'],small_actions=small['actions'],fresh_actions=fresh['actions'],
                retained_visited=sum(small['private_visited_extents']),fresh_visited=sum(fresh['private_visited_extents']))

def check():
    return dict(codecs=codecs(),metadata=metadata(),mutations=mutations(),history=history())

if __name__=='__main__':
    from argparse import ArgumentParser
    parser=ArgumentParser();parser.add_argument('--output',type=Path);args=parser.parse_args()
    result=check()
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('PASS_ROUNDED_LEAF_INTERFACES',json.dumps(dict(drop_values=result['codecs']['complete_accepted_drop_values'],
        overflow_controls=result['codecs']['overflow_controls'],lift_values=result['codecs']['complete_lift_values'],
        metadata_cases=len(result['metadata']['cases']),mutants=len(result['mutations']),ports=521),sort_keys=True))
