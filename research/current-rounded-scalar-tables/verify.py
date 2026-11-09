#!/usr/bin/env python3
"""Bounded literal rounded scalar verification; standard library only.

Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
import argparse
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import sys
import types

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from source_binding import authenticate,bind_scales,need,current_scales,word
from tables import compile_rounded
from physical import check_case,execute,Tape,encode_symbols,symbols,rounded


def source_suite():
    registry,cache,rows=bind_scales()
    for table,receipt in cache.values():
        need(all(r[0] in ('branch','write','move','goto','halt','reject') for r in table),"literal finite instruction alphabet")
        need(all(r[2] in (-1,1) for r in table if r[0]=='move'),"only unit table movements")
        need(all(r[1]<3 for r in table if r[0] in ('branch','write','move')),"three SCALE ports only")
    inventory=[dict(receipt,occurrences=sum(z['coefficient']==str(q) for z in rows))
               for q,(table,receipt) in sorted(cache.items())]
    w=word();odd_adds=sum(e[0] in ('ADD','COPY') and F(e[3]).denominator & (F(e[3]).denominator-1)!=0
                          for e in w['program'])
    need(odd_adds==4079,"odd ADD class remains uninstantiated")
    # Literal current site and exact old ABI token; no new op is introduced.
    token=('local',37480,('SCALE',697,'-2/3',591))
    table=registry[token];receipt=cache[F(-2,3)][1]
    admitted,out,bound=check_case(table,receipt,'SCALE',F(-2,3),(1,0),(),4)
    need(admitted and out['output']==(-1,0),"current source seam rounded successfully")
    need(('local',37480,('SCALE',697,'-1/3',591)) not in registry,"wrong current source coefficient rejected")
    return dict(occurrences=len(rows),coefficients=len(cache),inventory=inventory,
                total_table_rows=sum(len(t) for t,r in cache.values()),
                max_table_rows=max(len(t) for t,r in cache.values()),
                actual_source_seam=dict(pc=37480,field=697,input=[1,0],output=list(out['output']),actions=out['actions']),
                remaining_odd_ADD_occurrences=odd_adds,
                binding_scope='exact local tokens for current SCALE class only; complete caller/recursive exporter not installed')


def arithmetic_suite():
    qs=sorted(set(q for _,_,q in current_scales()))
    cases=accepts=0;max_actions=0
    for q in qs:
        table,receipt=compile_rounded('SCALE',q)
        for width in range(1,6):
            for x in range(-(1<<(width-1)),1<<(width-1)):
                admitted,out,bound=check_case(table,receipt,'SCALE',q,(x,0),(),width)
                cases+=1;accepts+=admitted;max_actions=max(max_actions,out['actions'])
    extras=[F(-2,3),F(1,2),F(-5,6),F(3,5),F(0),F(3),F(-3)]
    add_cases=add_accepts=0
    for q in extras:
        table,receipt=compile_rounded('ADD',q)
        for width in range(1,5):
            domain=range(-(1<<(width-1)),1<<(width-1))
            for x in domain:
                for y in domain:
                    admitted,out,bound=check_case(table,receipt,'ADD',q,(x,0),(y,0),width)
                    add_cases+=1;add_accepts+=admitted
    table,receipt=compile_rounded('SCALE',F(-2,3))
    seam_cases=0
    for width in range(2,10):
        for x in range(-(1<<(width-1)),1<<(width-1)):
            admitted,_,_=check_case(table,receipt,'SCALE',F(-2,3),(x,0),(),width)
            need(admitted,"all -2/3 inputs admitted for W>=2");seam_cases+=1
    return dict(current_SCALE_cases=cases,current_SCALE_accepts=accepts,current_SCALE_rejects=cases-accepts,
                small_ADD_cases=add_cases,small_ADD_accepts=add_accepts,small_ADD_rejects=add_cases-add_accepts,
                seam_all_inputs_cases=seam_cases,max_current_SCALE_actions=max_actions,
                oracle='direct mathematical floor and final signed range; no table transitions imported')


def history_suite():
    table,receipt=compile_rounded('SCALE',F(-2,3))
    work=[Tape(tuple(i%2 for i in range(1800)),101),Tape(tuple((i+1)%2 for i in range(2400)),209)]
    work[0].pos+=1700;work[1].pos+=2400
    history=[]
    for width,components in [(19,12),(2,2),(7,4),(3,2)]:
        values=tuple((1 if i%2 else -1)*min(i+1,(1<<(width-1))-1) for i in range(components))
        ok,out,bound=check_case(table,receipt,'SCALE',F(-2,3),values,(),width,work)
        need(ok,"history values in range")
        history.append(dict(width=width,components=components,actions=out['actions'],bound=bound,
                            old_backing=out['old_backing'],historical_backing=[t.highwater-t.origin for t in work]))
    # A late overflow leaves the whole target unchanged, despite earlier staged output.
    t,r=compile_rounded('SCALE',F(2))
    late=execute(t,'SCALE',(0,3),(),3,work)
    need(late['error']=='rounded signed output overflow',"late-component overflow guard")
    # A rejected dirty bank can be retired and reused; the new public input is
    # freshly at its origin. No automatic restoration after failure is claimed.
    ok,reused,bound=check_case(table,receipt,'SCALE',F(-2,3),(1,0),(),3,work)
    need(ok and reused['output']==(-1,0),"dirty failed work retired before reuse")
    residue_failure=execute(table,'SCALE',(0,0),(),3,work,target_symbols=(0,1,0))
    need(residue_failure['error'] is not None,"residue prepass fails with marker6 live")
    ok,_,_=check_case(table,receipt,'SCALE',F(-2,3),(1,0),(),3,work)
    need(ok,"encoded marker6 does not hide dirty tail from retirement")
    bad=[]
    for label,syms in [('empty',()),('odd_component',symbols((1,),3)),
                       ('empty_component',(2,)),('foreign_numeric_symbol',(3,2,0,0,0,2)),
                       ('unterminated',(0,1,0))]:
        out=execute(table,'SCALE',(0,0),(),3,target_symbols=syms)
        need(out['error'] is not None,"numeric grammar rejection "+label);bad.append(label)
    ta,ra=compile_rounded('ADD',F(-2,3))
    mismatch=execute(ta,'ADD',(1,0),(1,0),3,source_symbols=symbols((1,0),4))
    need(mismatch['error'] is not None,"different input component shapes rejected")
    contexts=[Tape((1,0,1),301,True),Tape((0,1)*7,401,True),Tape((),501,True)]
    ctx=execute(table,'SCALE',(1,0),(),4,contexts=contexts)
    need(ctx['output']==(-1,0),"preserved extra borrowed contexts")
    metered=[]
    for op,q,x,y,width in [('SCALE',F(-2,3),(-2,1),(),3),
                           ('SCALE',F(-5,48),(-2,1),(),2),
                           ('ADD',F(-5,6),(-1,0),(1,-1),3)]:
        tt,rr=compile_rounded(op,q)
        out=execute(tt,op,x,y,width,count_rows=True)
        need(out['error'] is None,"metered representable fixture")
        S=len(x)*(width+1);R=len(x);d=rr['denominator_twos']
        need(out['table_rows']<=37*S+3*d*R+32,"finite-control row count")
        need(out['actions']+out['table_rows']<=512*(S+1)+64*d*R+7*out['old_backing'],
             "combined physical and finite-control count")
        metered.append(dict(op=op,coefficient=str(q),width=width,physical_actions=out['actions'],table_rows=out['table_rows']))
    return dict(history=history,late_overflow_public_unchanged=True,dirty_failure_then_success=True,
                malformed_rejected=bad+['ADD_component_shape'],
                borrowed_binary_contexts=3,
                residue_marker_failure_reused=True,combined_cost_samples=metered,
                failure_scope='public unchanged; failed heads and scratch may remain unrestored')


def controls_suite():
    source=(ROOT/'tables.py').read_text();caught=[]
    mutations=[('missing_signed_residue_correction','residue = (rho - a * sign * power) % odd','residue = rho % odd','SCALE',F(-2,3),(-2,0),(),2),
               ('missing_upward_rounding_offset','offset = denominator // 2','offset = 0','SCALE',F(1,2),(1,0),(),2),
               ('wrong_final_signed_guard','carry != p*sx+r*sy-odd*sq','carry != p*sx+r*sy+odd*sq','SCALE',F(1,2),(-2,0),(),2)]
    for label,old,new,op,q,x,y,w in mutations:
        need(source.count(old)==1,"unique mutation site")
        ns={'__name__':'rounded_mutant_'+label}
        exec(compile(source.replace(old,new),'<negative-control>','exec'),ns)
        table,receipt=ns['compile_rounded'](op,q)
        try:check_case(table,receipt,op,q,x,y,w)
        except ValueError:caught.append(label)
        else:raise ValueError('mutant escaped '+label)
    # Floor, truncation and symmetry are distinct on these actual signed cases.
    need(rounded(F(1,2),1)==1 and rounded(F(1,2),-1)==0,"even ties upward")
    need(rounded(F(-2,3),1)==-1 and int(F(-2,3))==0,"floor differs from truncation")
    return dict(table_mutants_detected=caught,additional_controls=['even_positive_and_negative_ties','floor_not_truncation'])


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--suite',choices=('source','arithmetic','history','controls','all'),default='all');parser.add_argument('--write',action='store_true');args=parser.parse_args()
    authenticate()
    for name,fn in [('source',source_suite),('arithmetic',arithmetic_suite),('history',history_suite),('controls',controls_suite)]:
        if args.suite not in (name,'all'):continue
        result=fn();path=ROOT/(name.upper()+'.json')
        if args.write:path.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
        else:need(result==json.loads(path.read_bytes()),'frozen '+name+' receipt')
        print('PASS_CURRENT_ROUNDED_SCALAR_'+name.upper(),flush=True)


if __name__=='__main__':main()
