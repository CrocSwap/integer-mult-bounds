#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Tekalign (@tekuuu), with substantial OpenAI Codex assistance.
"""Independent integer-time chronology and bit-mask whole-fill verification.

No retained window code, donor generator, solver or native checker is imported.
Credit PR2679's pre-life/refit words, PR2673/PR2621 priority scheduling,
PR2588's swapped words, PR2559's evacuation, PR2530's source-partner
fill and the PR2462/PR2322/PR2436 lineage;
Hao Yan and the retained controller authors supply the underlying schedule.
This checks a finite hosting witness, not native circuitry or an exponent.
"""
import argparse
import sys
sys.dont_write_bytecode=True
import gzip
import hashlib
import json
from collections import Counter
from pathlib import Path


def need(ok, why):
    if not ok:
        raise RuntimeError(why)


def windows(template, order):
    ranks={c['child']:c['rank'] for c in template['idle_children']}
    pairs={e['stage']:e['pair'] for e in template['recipe'] if e['kind']=='local'}
    blocks={};stage=None
    for event in template['execution_schedule']:
        if event['kind'] in ('bank_padding_cover_sweep','translate_every_live_family'):
            continue
        if event['kind']=='local_cover_sweep':
            stage=event['stage'];blocks[stage]=[]
        need(stage is not None,'event before first call')
        blocks[stage].append(event)
    progression=[0]*74;last={};result={}
    for t,(stage,replica) in enumerate(order):
        need(0<=replica<74 and stage==progression[replica],'order chronology')
        progression[replica]+=1
        for j,event in enumerate(blocks[stage]):
            kind=event['kind']
            if kind=='local_cover_sweep':
                need(j==0,'local call position')
                last[replica,pairs[stage]]=t
            elif kind=='bridge':
                last[replica,event['src']]=last[replica,event['dst']]=t
            elif kind=='idle_cover_sweep':
                need(j>0,'idle position')
                start=last.get((replica,event['pair']),-1)
                for child in event['child_indices']:
                    if child in ranks:
                        result[replica,child]=(ranks[child],start,t)
    need(progression==[9]*74,'complete replica progression')
    return result


def check(plan, template, order, fill, providers, initial_dispatch, expected_profile):
    need(len(order)==666 and len(set(map(tuple,order)))==666,'call coverage')
    win=windows(template,order)
    dispatch=dict(initial_dispatch)
    for s,r,pid in fill['dispatch_overrides']:
        need((s,r) in dispatch and pid in providers,'dispatch override')
        dispatch[s,r]=pid
    need(set(dispatch)==set(map(tuple,order)),'dispatch coverage')
    need(fill['columns']==['time','helper','owner_replica','child','port','offset'],'role columns')
    need(len(fill['rows'])==666*415,'role count')
    need(all(len(p['widths'])==415 for p in providers.values()),'helper widths')
    helper_bits=[0]*666;family_bits=[0]*666;occupied={}
    for row in fill['rows']:
        need(len(row)==6 and all(type(v) is int for v in row),'role shape')
        t,h,o,c,port,offset=row
        need(0<=t<666 and 0<=h<415 and 0<=port<112,'role bounds')
        cap,start,stop=win[o,c]
        need(start<t<=stop,'literal call window')
        hbit=1<<h
        need(not helper_bits[t]&hbit,'duplicate helper')
        helper_bits[t]|=hbit
        fam=o*896+(2*plan['pairs'][str(c)]+plan['sides'][str(c)])*112+port
        fbit=1<<fam
        need(not family_bits[t]&fbit,'same-call family collision')
        family_bits[t]|=fbit
        width=providers[dispatch[tuple(order[t])]]['widths'][h]
        need(0<=offset and offset+width<=cap,'bin capacity')
        mask=((1<<width)-1)<<offset;key=(o,c,port)
        need(not occupied.get(key,0)&mask,'overlapping bin cells')
        occupied[key]=occupied.get(key,0)|mask
    need(helper_bits==[(1<<415)-1]*666,'complete helper inventory')
    idle=Counter()
    for (owner,child),(cap,_,_) in win.items():
        for port in range(112):
            mask=occupied.get((owner,child,port),0);used=mask.bit_count()
            need(mask==(1<<used)-1,'compact bin prefix')
            if used<cap:
                idle[cap-used]+=1
    profile=Counter(idle)
    for call in order:
        profile.update({int(r):n for r,n in providers[dispatch[tuple(call)]]['actual_paid_profile'].items()})
    need(profile==expected_profile,'full profile mismatch')
    mass=sum(r*n for r,n in profile.items())
    need(mass==73*plan['live']*2-plan['deficit']*2==4816512,'rank mass')
    serial={f'{o},{c}':[cap,list(range(lo+1,hi+1))] for (o,c),(cap,lo,hi) in win.items()}
    digest=hashlib.sha256(json.dumps(serial,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return dict(status='PASS_INDEPENDENT_INTEGER_CHRONOLOGY_AND_MASK_FILL',roles=276390,
                calls=666,helpers_per_call=415,windows=len(win),window_sha256=digest,
                idle=dict(sorted(idle.items())),profile=dict(sorted(profile.items())),rank_mass=mass)
