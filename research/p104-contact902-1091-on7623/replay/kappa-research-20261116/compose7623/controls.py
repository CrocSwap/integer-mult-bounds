#!/usr/bin/env python3
"""Synthetic controls for local differential primitives. Run only under root guard."""
import argparse
from fractions import Fraction as F
import json
from pathlib import Path
import runpy


def need(value, message):
    if not value: raise ValueError(message)


def rejected(name, fn, exception, reason=None):
    try:
        fn()
    except exception as exc:
        if reason is not None and getattr(exc,'reason',None)!=reason:
            raise ValueError(name+' wrong rejection: '+str(exc))
        return {'name':name,'rejected':True}
    raise ValueError(name+' unexpectedly accepted')


def controls():
    here=Path(__file__).resolve().parent
    exact=runpy.run_path(str(here/'exact.py'))
    rank=runpy.run_path(str(here/'rankone.py'))
    physical=runpy.run_path(str(here/'physical.py'))
    Refusal=exact['Refusal'];Replay=exact['Replay'];compare=rank['compare_row']
    w={'public':1501,'owned_fields':68,'initial':[0]*1501,'final':[0]*1501,
       'frames':[[],[1],[2]],'program':[]}
    origins=list(range(30));reverse=list(range(30))
    def fresh():return Replay(w,origins,reverse,'synthetic')
    def step(r,j,e):r.step(j,e)
    results=[]

    # All private input slots begin as arbitrary independent dirty symbols.
    # INIT and CLEAR are modeled resets under U, not a physical implementation.
    r=fresh();need(r.rows[1501]=={1501:F(1)},'private input not dirty')
    step(r,0,['INIT',1501,0]);need(r.rows[1501]=={},'INIT did not reset entire row')
    step(r,1,['ADD',1501,0,'2',0]);need(r.rows[1501]=={0:F(2)},'owned write wrong')
    step(r,2,['CLEAR',1501,0])
    need(r.clears[-1]['row']=={'0':'2'} and r.rows[1501]=={} and 1501 not in r.alive,
         'CLEAR did not record prestate and reset')
    results.append({'name':'dirty_INIT_CLEAR_under_U','passed':True})

    r=fresh()
    results.append(rejected('owned_read_before_INIT',lambda:step(r,0,['ADD',0,1501,'1',0]),Refusal,'owned_not_live'))
    r=fresh();step(r,0,['INIT',1501,0]);step(r,1,['CLEAR',1501,0])
    results.append(rejected('owned_read_after_CLEAR',lambda:step(r,2,['ADD',0,1501,'1',0]),Refusal,'owned_not_live'))
    r=fresh()
    results.append(rejected('owned_MOVE_before_INIT',lambda:step(r,0,['MOVE',1501,0,1,True]),Refusal,'owned_not_live'))
    r=fresh()
    results.append(rejected('scalar_wrong_coframe',lambda:step(r,0,['ADD',0,1,'1',1]),Refusal,'scalar_coframe_or_zero'))
    r=fresh();step(r,0,['INIT',1501,0])
    results.append(rejected('owned_wrong_MOVE_flag',lambda:step(r,1,['MOVE',1501,0,1,False]),Refusal,'move_owner_or_coframe'))
    r=fresh();step(r,0,['INIT',1501,0]);step(r,1,['MOVE',1501,0,1,True])
    results.append(rejected('owned_nonnested_MOVE',lambda:step(r,2,['MOVE',1501,1,2,True]),Refusal,'move_not_strict_nested'))

    # The COPY destination is initially dirty. Rejection must occur before
    # any overwrite or accumulation and the precise pre-guard must be retained.
    r=fresh();before=dict(r.rows[0])
    results.append(rejected('dirty_COPY_before_overwrite',lambda:step(r,0,['COPY',0,1,'1',0]),Refusal,'copy_nonzero'))
    need(r.rows[0]==before and len(r.guards)==1 and r.guards[0]['row']=={'0':'1'},'COPY guard or row mutated')
    r=fresh();step(r,0,['INIT',1501,0]);step(r,1,['COPY',1501,1,'-2',0])
    need(r.guards[-1]['row']=={} and r.rows[1501]=={1:F(-2)},'valid COPY result or zero pre-guard')
    results.append({'name':'zero_guard_COPY_positive','passed':True})

    # Literal coefficients must retain the source's 5-smooth denominator rule.
    r=fresh();step(r,0,['ADD',0,1,'1/15',0])
    results.append({'name':'smooth_literal_positive','passed':True})
    r=fresh()
    results.append(rejected('nonsmooth_literal_denominator',lambda:step(r,0,['ADD',0,1,'1/7',0]),Refusal,'nonsmooth_denominator'))

    # Exercise the actual fixed-case contract checker with small toy counts.
    Grid=exact['Grid'];source_grid_contract=exact['source_grid_contract']
    lit=Grid()
    for q in ('1/2','1/3','2/5'):lit.note(F(q))
    need(lit.result()['nondyadic_count']==2,'non-dyadic count includes dyadic literal')
    toy={'grid':{'literal':lit.result(),'trajectory':{'odd_den_lcm':15}}}
    source_grid_contract(toy,toy,2)
    results.append({'name':'source_grid_contract_positive','passed':True})
    unequal={'grid':{'literal':lit.result(),'trajectory':{'odd_den_lcm':5}}}
    results.append(rejected('trajectory_odd_lcm_changed',lambda:source_grid_contract(toy,unequal,2),Refusal,'trajectory_odd_lcm_changed'))
    fewer=Grid()
    for q in ('1/2','1/3'):fewer.note(F(q))
    short={'grid':{'literal':fewer.result(),'trajectory':{'odd_den_lcm':15}}}
    results.append(rejected('nondyadic_literal_event_count',lambda:source_grid_contract(toy,short,2),Refusal,'nondyadic_literal_event_count'))

    # Independent hand-worked rank-one row: candidate - original = 2*c.
    original={'2':'1','5':'2'};candidate={'2':'7','5':'-4'};c={2:F(3),5:F(-3)}
    compare(candidate,original,F(2),c,'toy positive')
    results.append({'name':'rank_one_signed_identity','passed':True})
    results.append(rejected('omitted_observer',lambda:compare(original,original,F(2),c,'missing'),ValueError))
    results.append(rejected('wrong_beta_sign',lambda:compare(candidate,original,F(-2),c,'wrong beta'),ValueError))
    results.append(rejected('wrong_source_orientation',lambda:compare(candidate,original,F(2),{2:F(-3),5:F(3)},'wrong source'),ValueError))
    # Reverse-prefix hand calculation distinguishes source/order orientation:
    # after x902*=2 then x902+=3*x1, covector is 2e902+3e1.
    prefix=[['SCALE',902,'2',0],['ADD',902,1,'3',0]]
    covector=rank['reverse_prefix'](prefix)
    need(covector=={902:F(2),1:F(3)},'reverse-prefix source orientation')
    wrong={902:F(2),1:F(6)}
    results.append(rejected('wrong_reverse_order',lambda:rank['require'](covector==wrong,'wrong order'),ValueError))

    # Test physical module's actual strict nested-chart helper without importing
    # the pinned physical oracle or pretending this proves absolute phase.
    class ToyOracle:
        span=staticmethod(exact['span'])
    physical['require_nested'](ToyOracle,w['frames'],0,1)
    results.append({'name':'strict_nested_chart_positive','passed':True})
    results.append(rejected('descending_public_chart',lambda:physical['require_nested'](ToyOracle,w['frames'],1,0),ValueError))
    results.append(rejected('nonnested_public_chart',lambda:physical['require_nested'](ToyOracle,w['frames'],1,2),ValueError))
    return {'status':'PASS_SOURCE_FREE_CONTROLS','controls':results,
            'limits':'Synthetic scalar/ownership/chart primitives only; no actual word, physical oracle, absolute-phase or common U service is established.'}


def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path);a=p.parse_args()
    report=controls()
    if a.out is not None:
        a.out.parent.mkdir(parents=True,exist_ok=True)
        with a.out.open('x',encoding='utf-8') as f:json.dump(report,f,sort_keys=True,indent=2);f.write('\n')
    print(json.dumps(report,sort_keys=True),flush=True)

if __name__=='__main__':main()
