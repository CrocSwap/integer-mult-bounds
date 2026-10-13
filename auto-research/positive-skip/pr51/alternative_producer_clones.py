#!/usr/bin/env python3
"""Clone complete output chains through a new source-coefficient partition.

Unlike literal parent duplication, the new producer uses y+z with disjoint
coefficient supports partitioning the parent's form, and uses two arbitrary
unused earlier controller capacities consuming y and z. Actual frames are
inherited from the first consumer. Old scalar gates and frames remain literal.
"""
from __future__ import annotations
import argparse
import array
from collections import Counter
from concurrent.futures import ProcessPoolExecutor,as_completed
from datetime import datetime,timezone
import json
import math
from pathlib import Path
import struct
import subprocess
import sys
import time
from check_compiled_witness import contained,read_dag,read_labels
from producer_search import digest,ordinary_profile


def opportunities(row,limit,policy='conservative'):
    h,v,n,q,args,core,cover,roots,kinds,active=read_dag(row['dag_path'])
    ranks,frames=read_labels(row['dag_path']+'.positive',h,n)
    order=sorted((x for x in range(1,n)if active[x]),key=lambda x:(ranks[x],x))
    times={x:i for i,x in enumerate(order)}
    scalar=[0]*n;users=[[]for _ in range(n)]
    for x in range(1,n):
        if not active[x]:continue
        if args[2*x]:
            a,b=args[2*x:2*x+2];assert not scalar[a]&scalar[b]
            scalar[x]=scalar[a]|scalar[b]
            for p in (0,1):users[args[2*x+p]].append(2*x+p)
        else:scalar[x]=1<<(x-1)
    for j,x in enumerate(roots):users[x].append((1<<31)|j)
    def value(e):return roots[e&0x7fffffff]if e>>31 else args[e]
    def owner(e):return roots[e&0x7fffffff]if e>>31 else e//2
    def when(e):return len(order)+(e&0x7fffffff)if e>>31 else times[e//2]
    next_use={};incoming=set();used=set()
    for donor,e in json.loads(Path(row['witness_path']).read_text())['links']:
        p=0 if args[2*donor]==value(e)else 1
        assert args[2*donor+p]==value(e)
        next_use[2*donor+p]=e;incoming.add(e);used.add(donor)
    providers={};by_min={}
    for gate in order:
        if not args[2*gate]or gate in used:continue
        for value_node in args[2*gate:2*gate+2]:
            support=scalar[value_node]
            if support not in providers:
                providers[support]=[]
                by_min.setdefault(support&-support,[]).append(support)
            providers[support].append((gate,value_node))
    for bucket in by_min.values():bucket.sort(key=lambda support:(-support.bit_count(),support))
    offers=[];tested=0
    for x in order:
        if not args[2*x]:continue
        starts=[e for e in users[x]if e not in incoming]
        if len(starts)<2:continue
        starts.sort(key=lambda e:(-ranks[owner(e)],when(e)))
        target_support=scalar[x];old_partition={scalar[args[2*x]],scalar[args[2*x+1]]}
        candidates=[]
        for y in by_min.get(target_support&-target_support,[]):
            if y==target_support or y&~target_support:continue
            z=target_support^y
            if z not in providers or {y,z}==old_partition:continue
            candidates.append((y,z))
            if len(candidates)>=limit:break
        for first in starts[:2]:
            frame=frames[owner(first)];chain=[];e=first
            while True:
                chain.append(e)
                if e not in next_use:break
                e=next_use[e]
            for y,z in candidates:
                tested+=1
                left=[(g,a)for g,a in providers[y]if times[g]<when(first)and contained(frames[g],frame)]
                right=[(g,b)for g,b in providers[z]if times[g]<when(first)and contained(frames[g],frame)]
                if not left or not right:continue
                found=0
                for g,a in left[:4]:
                    for k,b in right[:4]:
                        if g==k:continue
                        offers.append(dict(parent=x,providers=[g,k],source_children=[a,b],
                                           first=first,frame_owner=owner(first),chain=chain,
                                           frame_rank=frame[0]))
                        found+=1
                        if found==2:break
                    if found==2:break
    loads=Counter(g for o in offers for g in o['providers'])
    counts=Counter(o['parent']for o in offers)
    if policy=='conservative':
        offers.sort(key=lambda o:(-o['frame_rank'],sum(loads[g]for g in o['providers']),counts[o['parent']],o['parent'],o['first']))
    else:
        phi=[sum(k*t*math.expm1(.0000413*math.log(575/t))for t,k in ordinary_profile(h,r).items()if t)for r in range(h+1)]
        external=h*math.expm1(.0000413*math.log(575/h))+(575-2*h)*math.expm1(.0000413*math.log(575/(575-2*h)))
        def benefit(o):
            rx=ranks[o['parent']];rf=o['frame_rank'];r1,r2=(ranks[g]for g in o['providers'])
            return external+phi[rx]+phi[h-r1]+phi[h-r2]+phi[rf-rx]-phi[rf-r1]-phi[rf-r2]-phi[h-rf]
        def priority(o):
            score=benefit(o)
            if policy=='mapped-scarce':score/=math.sqrt(1+sum(loads[g]for g in o['providers']))
            return(-score,sum(loads[g]for g in o['providers']),counts[o['parent']],o['parent'],o['first'])
        offers.sort(key=priority)
    chosen=[];caps=set();parents=set();formal=set()
    for o in offers:
        x=o['parent'];gs=set(o['providers']);ys=set(o['source_children'])
        if gs&caps or x in parents:continue
        if policy=='conservative'and(x in formal or ys&parents):continue
        chosen.append(o);caps|=gs;parents.add(x);formal|=ys
    return chosen,dict(partitions_tested=tested,offered=len(offers),chosen=len(chosen)),order,frames


def rewrite(row,jobs,order,frames,target):
    h,v,n,q,args,core,cover,roots,kinds,active=read_dag(row['dag_path'])
    target.mkdir(parents=True,exist_ok=False)
    move={};before={};terminal=[]
    for i,job in enumerate(jobs):
        for e in job['chain']:assert e not in move;move[e]=i
        if job['first']>>31:terminal.append(i)
        else:before.setdefault(job['first']//2,[]).append(i)
    aa=[0,0];cc=[0];vv=[0];ff=[None];mapping={};clones={}
    def clone(i):
        job=jobs[i];x=job['parent'];node=len(cc);children=[]
        for g,old_child in zip(job['providers'],job['source_children']):
            pos=0 if args[2*g]==old_child else 1
            assert args[2*g+pos]==old_child
            edge=2*g+pos
            child=clones[move[edge]]if edge in move else mapping[old_child]
            children.append(child)
        clones[i]=node;aa.extend(children);cc.append(core[x]);vv.append(cover[x]);ff.append(frames[job['frame_owner']])
    for x in order:
        for i in before.get(x,[]):clone(i)
        mapping[x]=len(cc)
        if args[2*x]:aa.extend(clones[move[e]]if e in move else mapping[args[e]]for e in (2*x,2*x+1))
        else:assert mapping[x]==x<=v;aa.extend((0,0))
        cc.append(core[x]);vv.append(cover[x]);ff.append(frames[x])
    for i in terminal:clone(i)
    rr=[clones[move[(1<<31)|j]]if(1<<31)|j in move else mapping[x]for j,x in enumerate(roots)]
    nn=len(cc);dag=target/'dag.bin'
    with dag.open('wb')as stream:
        stream.write(struct.pack('<4I',h,v,nn,q))
        for code,values in (('I',aa),('Q',cc),('Q',vv),('I',rr),('I',kinds),('B',[0]+[1]*(nn-1))):stream.write(array.array(code,values).tobytes())
    with Path(str(dag)+'.positive').open('wb')as stream:
        stream.write(struct.pack('<2I',h,nn));stream.write(array.array('I',[0]+[f[0]for f in ff[1:]]).tobytes());stream.write(array.array('Q',[0]+[f[1]for f in ff[1:]]).tobytes());stream.write(array.array('b',[0]*h+[z for f in ff[1:]for z in f[2]]).tobytes())
    old=json.loads(Path(row['witness_path']).read_text())['links']
    links=[[mapping[d],e if e>>31 else 2*mapping[e//2]+(e&1)]for d,e in old]
    for i,job in enumerate(jobs):
        for p,g in enumerate(job['providers']):links.append([mapping[g],2*clones[i]+p])
    (target/'constructed-links.json').write_text(json.dumps(dict(h=h,n=nn,links=links),sort_keys=True)+'\n')
    (target/'rewrite.json').write_text(json.dumps(dict(source_dag=row['dag_path'],source_dag_sha256=digest(row['dag_path']),selected_jobs=jobs,original_node_map=mapping,clone_node_map=clones),sort_keys=True)+'\n')
    return dag


def evaluate(task):
    parent,work,matcher,limit,rounds,*options=task;at=time.monotonic();policy=options[0]if options else'conservative'
    document=json.loads(Path(parent).read_text())
    if 'rows'in document:
        assert len(document['rows'])==1
        document=document['rows'][0]
    row=dict(document['producer']);initial=dict(row)
    name=f"h{row['h']}-alternative-l{limit}-"+digest(parent)[:12];stages=[]
    if policy!='conservative':name+='-'+policy
    try:
        for iteration in range(rounds):
            jobs,diagnostic,order,frames=opportunities(row,limit,policy)
            stage=dict(round=iteration+1,parent_roles=row['R'],diagnostic=diagnostic)
            if not jobs:stage['terminal']=True;stages.append(stage);break
            target=Path(work)/'raw'/name/f'round-{iteration+1}';dag=rewrite(row,jobs,order,frames,target);witness=target/'selected-links.json'
            native=subprocess.run([str(matcher),str(dag),str(dag)+'.positive','104729','2',str(witness)],capture_output=True,text=True,check=True)
            new=json.loads(native.stdout);assert new['matched']>=row['matched']+2*len(jobs);assert new['R']<=row['R']-len(jobs)
            new.update(dag_path=str(dag),dag_sha256=digest(dag),positive_sha256=digest(str(dag)+'.positive'),witness_path=str(witness),witness_sha256=digest(witness),schedule='rank-node',configuration=dict(alternative_partitions=True,limit=limit,round=iteration+1),original_producer_path=str(parent))
            if policy!='conservative':new['configuration']['selection_policy']=policy
            stage.update(chosen=jobs,new_roles=new['R'],rewrite_path=str(target/'rewrite.json'),new_dag_sha256=new['dag_sha256']);stages.append(stage);row=new
        result=dict(status='alternative-producer clone candidate',case_id=name,producer=row,
                    initial_roles=initial['R'],role_saving=initial['R']-row['R'],stages=stages,
                    selected_links=json.loads(Path(row['witness_path']).read_text()),seconds=time.monotonic()-at)
    except Exception as error:result=dict(status='failed',case_id=name,error=repr(error),stages=stages,seconds=time.monotonic()-at)
    (Path(work)/'raw'/f'{name}.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--parent',type=Path,nargs='+',required=True);p.add_argument('--work',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--workers',type=int,default=7)
    p.add_argument('--limit',type=int,default=32);p.add_argument('--rounds',type=int,default=2)
    p.add_argument('--policy',choices=['conservative','mapped-moment','mapped-scarce'],default='conservative')
    a=p.parse_args();assert not a.work.exists()and not a.output.exists()
    (a.work/'builds').mkdir(parents=True);(a.work/'raw').mkdir()
    native=Path(__file__).with_name('moment_match_rank_node.cpp');matcher=a.work/'builds'/'matcher'
    subprocess.run(['c++','-O3','-std=c++17',str(native),'-o',str(matcher)],check=True)
    result=dict(status='running',command=sys.argv,started_utc=datetime.now(timezone.utc).isoformat(),workers=a.workers,rows=[])
    with ProcessPoolExecutor(max_workers=a.workers)as pool:
        futures=[pool.submit(evaluate,(parent,a.work,matcher,a.limit,a.rounds,a.policy))for parent in a.parent]
        for future in as_completed(futures):
            row=future.result();result['rows'].append(row);a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps({k:row.get(k)for k in('case_id','status','role_saving','seconds','error')}),flush=True)
    result.update(status='complete',completed_utc=datetime.now(timezone.utc).isoformat());a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')


if __name__=='__main__':main()
