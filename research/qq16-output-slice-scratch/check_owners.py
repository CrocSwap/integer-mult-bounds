#!/usr/bin/env python3
"""Independent finite physical-bank replay, with scalar bodies owner-major.

Reads JSON only; does not import the transform, formal interpreter or source
verifier. Native symbols receive explicit invertible noncommuting toy actions;
this checks allocation equivalence, not QQ16 native-kernel admission.
"""
from fractions import Fraction as Q
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent


def need(ok,message):
    if not ok:raise ValueError(message)


def execute(word,n,wrong_owner=False):
    banks={}
    def dirt(name):
        k=sum((i+1)*ord(c) for i,c in enumerate(name))
        return [[Q(k+3*j+1),Q(2*k-5*j-2)] for j in range(n)]
    for side in ('Z','W'):
        for p in range(112):banks[f'{side}{p}']=dirt('dirty'+f'{side}{p}')
    for p in range(112):banks[f'X{p}']=dirt('early'+str(p))
    current={};checks=0
    def scalar(e,owner,local,active):
        nonlocal checks
        op=e['op']
        if op=='clear':
            name=e['field']
            if name in local:local[name]=[Q(0),Q(0)]
            else:banks[name][owner]=[Q(0),Q(0)]
        else:
            need(op=='add','scalar-only owner body')
            src,dst=e['src'],e['dst']
            read_owner=(owner+1)%n if wrong_owner and src in active else owner
            a=local[src] if src in local else banks[src][read_owner]
            b=local[dst] if dst in local else banks[dst][owner]
            result=[v+Q(e['coefficient'])*u for u,v in zip(a,b)]
            if dst in local:local[dst]=result
            else:banks[dst][owner]=result
        checks+=2
    i=0
    while i<len(word):
        e=word[i];op=e['op']
        if op in ('private_begin','output_slices_begin'):
            end_op='private_end' if op=='private_begin' else 'output_slices_end'
            end=next(j for j in range(i+1,len(word)) if word[j]['op']==end_op)
            fields=e['fields']
            for owner in range(n):
                # Baseline has actual extra local storage; candidate has none.
                local={name:dirt(name)[owner] for name in fields} if op=='private_begin' else {}
                for event in word[i+1:end]:scalar(event,owner,local,set(fields))
                need(all((local[name] if name in local else banks[name][owner])==[0,0] for name in fields),'zero owner-local return')
            i=end+1;continue
        if op=='history_boundary':
            for side in ('X','Y'):
                for p in range(112):
                    name=f'{side}{p}';banks[name]=dirt('current'+name)
                    current[name]=[v[:] for v in banks[name]]
        elif op in ('add','clear'):
            for owner in range(n):scalar(e,owner,{},set())
        elif op in ('line','stage','current_map'):
            name=e['field'];old=banks[name]
            if op=='current_map':
                k=e['port']%5+1;step=(e['port']+1)%n;s=-1 if e['inverse'] else 1
                banks[name]=[[old[(j+s*step)%n][0]+s*k*old[(j+s*step)%n][1],old[(j+s*step)%n][1]] for j in range(n)]
            elif op=='line':
                k=e['port']%7+1;s=e['sign']
                banks[name]=[[x,y+s*k*x] for x,y in old]
            else:banks[name]=[[y,-x] for x,y in old]
        elif op!='checkpoint':raise ValueError('unknown finite event '+op)
        i+=1
    need(all(banks[name]==value for name,value in current.items()),'borrowed current banks restored')
    return {k:v for k,v in banks.items() if k[0] in 'ZW'},checks


if __name__=='__main__':
    old=json.loads((HERE/'vendor/WORD.json').read_text())
    new=json.loads((HERE/'WORD.json').read_text())
    total=0
    for n in (2,3,5):
        a,c=execute(old,n);b,d=execute(new,n)
        need(a==b,'all complete physical output banks');total+=c+d
    try:
        bad,_=execute(new,3,True)
        good,_=execute(old,3)
        need(bad==good,'wrong-owner read changes endpoint')
    except ValueError:pass
    else:raise ValueError('wrong-owner control ineffective')
    print('PASS_QQ16_OWNER_STORAGE owners=2,3,5 output_cells=4480 scalar_component_updates='+str(total)+' wrong_owner=1')
