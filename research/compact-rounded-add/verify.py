#!/usr/bin/env python3
"""Independent integer oracle and bounded literal lifecycle checks."""
import argparse,hashlib,json,sys
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT))
from source_binding import authenticate,bind_witnesses,census,need,vendor
from tables import compile_compact,cost_bound
P=vendor('compact_rounded_fixture','vendor/physical_fixture.py')

def check(table,r,x,y,w,work=None,contexts=()):
    out=P.execute(table,'ADD',tuple(x),tuple(y),w,work,contexts=contexts,count_rows=True)
    a,b=r['numerator'],r['denominator']
    expected=tuple(xx+(a*yy+b//2)//b for xx,yy in zip(x,y))
    fits=all(-(1<<(w-1))<=z<(1<<(w-1)) for z in expected)
    need((out['error'] is None)==fits,'independent final-range iff')
    if fits:need(out['output']==expected,'independent mathematical-floor oracle')
    Qc=sum(len(t.body())+1 for t in contexts)
    bound=cost_bound(r,len(x)*(w+1),len(x),out['old_backing'],Qc)
    need(out['actions']+out['table_rows']<=bound,'positive tape plus finite-control bill')
    return fits,out,bound

def source_suite():
    rows=census();qs={q for _,_,q in rows}
    def odd(q):
        v=q.denominator
        while v%2==0:v//=2
        return v
    need(max(max(abs(q.numerator).bit_length(),q.denominator.bit_length()) for q in qs)==24,'current bit bound')
    need(max(odd(q) for q in qs)==125,'current odd bound')
    registry,receipts=bind_witnesses();samples=[]
    for r,(x,y,w) in zip(receipts,[(100,2,8),(7,2,4),(-7,3,4)]):
        token=('local',r['pc'],tuple(r['raw']));table=registry[token]
        need(all(z[0] in ('branch','write','move','goto','halt','reject') for z in table),'literal runtime alphabet')
        need(all(z[2] in (-1,1) for z in table if z[0]=='move'),'only unit tape moves')
        need(all(z[1]<4 for z in table if z[0] in ('branch','write','move')),'four data ports: exactly two private banks')
        ok,out,bound=check(table,r,(x,0),(y,0),w);need(ok,'source cancellation witness')
        need(not (-(1<<(w-1))<=P.rounded(F(r['coefficient']),y)<(1<<(w-1))),'standalone product would overflow')
        samples.append(dict(pc=r['pc'],width=w,target=[x,0],source=[y,0],output=list(out['output']),actions=out['actions'],table_rows=out['table_rows'],bound=bound))
    need(('local',252,('ADD',281,261,'-14729531/163840',4)) not in registry,'source origin-token mutation rejected')
    return dict(ADD_occurrences=61052,COPY_coefficient_occurrences=1,ADD_COPY_occurrences=len(rows),coefficients=len(qs),max_coefficient_bits=24,max_odd_divisor=125,
                constructed_occurrences=3,constructed_coefficients=3,inventory=receipts,cancellation=samples,
                full_class_installed=False,source_scope='three exact current local SERVICE tokens; not a whole caller installation')

def arithmetic_suite():
    counts=[]
    for q,limit in [(F(0),4),(F(1,2),4),(F(-2,3),4),(F(3),4),(F(-5,6),4),
                    (F(-14729531,163840),3),(F(-1379,250),3),(F(1085645,393216),3)]:
        table,r=compile_compact(q);total=okcount=0
        for w in range(1,limit+1):
            vals=range(-(1<<(w-1)),1<<(w-1))
            for x in vals:
                for y in vals:
                    ok,out,bound=check(table,r,(x,0),(y,0),w);total+=1;okcount+=ok
        counts.append(dict(coefficient=str(q),widths=[1,limit],cases=total,accepted=okcount,rejected=total-okcount))
    # Width far smaller than d and K, even ties on both sides, signed endpoints.
    extremes=[]
    for q,w in [(F(1,32),2),(F(-31,16),2),(F(-14729531,163840),8),(F(1085645,393216),4)]:
        t,r=compile_compact(q)
        for x,y in [(-(1<<(w-1)),-(1<<(w-1))),((1<<(w-1))-1,(1<<(w-1))-1),(0,-1)]:
            ok,out,bound=check(t,r,(x,0),(y,0),w);extremes.append(dict(coefficient=str(q),width=w,x=x,y=y,accepted=ok))
    return dict(exhaustive=counts,total_cases=sum(r['cases'] for r in counts),extra_endpoint_cases=extremes,
                oracle='direct signed integers and mathematical floor; no transition arithmetic imported')

def history_suite():
    t,r=compile_compact(F(-14729531,163840))
    work=[P.Tape(tuple(i%2 for i in range(4500)),101),P.Tape(tuple((i+1)%2 for i in range(6000)),209)]
    work[0].pos+=4499;work[1].pos+=6000
    history=[]
    for w,R in [(19,8),(2,2),(9,4),(1,2)]:
        x=tuple(0 for _ in range(R));y=tuple(0 for _ in range(R))
        ok,out,bound=check(t,r,x,y,w,work);need(ok,'long-short success')
        history.append(dict(width=w,components=R,actions=out['actions'],table_rows=out['table_rows'],bound=bound,old_backing=out['old_backing'],historical_backing=[z.highwater-z.origin for z in work]))
    # First component stages zero, last overflows. No target write precedes guard.
    late=P.execute(t,'ADD',(0,0),(0,1),4,work,count_rows=True)
    need(late['error'] is not None,'late overflow rejected')
    ok,out,bound=check(t,r,(0,0),(0,0),2,work);need(ok,'failed dirty scratch retired on reuse')
    bad=[]
    for label,syms in [('empty',()),('odd_record',P.symbols((0,),3)),('empty_component',(2,)),
                       ('foreign_symbol',(3,2,0,0,0,2)),('unterminated',(0,1,0))]:
        v=P.execute(t,'ADD',(0,0),(0,0),3,target_symbols=syms)
        need(v['error'] is not None,'canonical grammar detection '+label);bad.append(label)
    v=P.execute(t,'ADD',(0,0),(0,0),3,source_symbols=P.symbols((0,0),4));need(v['error'] is not None,'unequal shapes rejected')
    contexts=[P.Tape((1,0,1),301,True),P.Tape((0,1)*7,401,True),P.Tape((),501,True)]
    contexts[0].pos+=3;contexts[1].pos+=7
    ok,out,bound=check(t,r,(0,0),(0,0),3,contexts=contexts);need(ok,'borrowed contexts preserved')
    # Equal values remain separate physical fields; no source alias is assumed.
    tt,rr=compile_compact(F(-1));ok,out,bound=check(tt,rr,(-4,3),(-4,3),3);need(ok and out['output']==(0,0),'equal signed values on distinct tapes')
    return dict(history=history,late_failure_public_unchanged=True,failed_work_reused=True,malformed_controls=bad+['unequal_shapes'],
                preserved_contexts=3,signed_equal_distinct_sources=True,
                failure_scope='public field unchanged; heads and private scratch may remain dirty/repositioned')

def controls_suite():
    caught=[]
    cases=[('lost-leading',F(3),0,1,3),('lost-negative',F(-2,3),0,1,3),('tie-down',F(1,2),0,1,2),
           ('unsigned-residue',F(-2,3),0,1,2),('omit-high',F(3),0,3,3)]
    for mutation,q,x,y,w in cases:
        table,r=compile_compact(q,mutant=mutation)
        try:check(table,r,(x,0),(y,0),w)
        except ValueError:caught.append(mutation)
        else:raise ValueError('undetected mutant '+mutation)
    need(P.rounded(F(1,2),-1)==0 and P.rounded(F(1,2),1)==1,'even-denominator ties upward')
    need(P.rounded(F(-2,3),1)==-1 and int(F(-2,3))==0,'floor is not truncation')
    try:compile_compact(F(1,127))
    except ValueError:pass
    else:raise ValueError('odd divisor domain escaped')
    return dict(detected_mutants=caught,extra_controls=['positive_negative_even_ties','floor_not_truncation','odd_divisor_domain'])

def main():
    p=argparse.ArgumentParser();p.add_argument('--suite',choices=('source','arithmetic','history','controls','all'),default='all');p.add_argument('--write',action='store_true');a=p.parse_args();authenticate()
    for name,fn in [('source',source_suite),('arithmetic',arithmetic_suite),('history',history_suite),('controls',controls_suite)]:
        if a.suite not in (name,'all'):continue
        v=fn();dest=ROOT/(name.upper()+'.json')
        if a.write:dest.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
        else:need(v==json.loads(dest.read_bytes()),'frozen '+name+' receipt')
        print('PASS_COMPACT_ROUNDED_ADD_'+name.upper(),flush=True)
if __name__=='__main__':main()
