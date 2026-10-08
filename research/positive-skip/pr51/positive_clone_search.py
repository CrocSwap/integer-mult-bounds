#!/usr/bin/env python3
"""Selective duplicate gates on actual enlarged backward-positive frames.

New finite construction: move one complete result-carrier chain to a duplicate
gate, inherit that chain's actual first-consumer frame, and retain both inputs
from two unused earlier gate capacities. Original frames remain literal.
Native matching is rerun on the edited graph; the constructed plan supplies
an independently auditable feasible role reduction of one per selected clone.
"""
from __future__ import annotations
import argparse
import array
from collections import Counter
from concurrent.futures import ProcessPoolExecutor,as_completed
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path
import struct
import subprocess
import sys
import time
from check_compiled_witness import contained,read_dag,read_labels
from producer_search import profile


def digest(path):return sha256(Path(path).read_bytes()).hexdigest()


def opportunities(row,limit,policy,seed):
    h,v,n,q,args,core,cover,roots,kinds,active=read_dag(row['dag_path'])
    ranks,frames=read_labels(row['dag_path']+'.positive',h,n)
    links=json.loads(Path(row['witness_path']).read_text())['links']
    order=sorted((x for x in range(1,n)if active[x]),
                 key=lambda x:(ranks[x],1 if not args[2*x]else cover[x].bit_count()-core[x].bit_count(),x))
    times={node:i for i,node in enumerate(order)}
    users=[[]for _ in range(n)]
    for x in order:
        if args[2*x]:
            for p in (0,1):users[args[2*x+p]].append(2*x+p)
    for j,x in enumerate(roots):users[x].append((1<<31)|j)
    def value(e):return roots[e&0x7fffffff]if e>>31 else args[e]
    def owner(e):return roots[e&0x7fffffff]if e>>31 else e//2
    def time(e):return len(order)+(e&0x7fffffff)if e>>31 else times[e//2]
    successor={};incoming=set();used=set()
    for donor,receiver in links:
        pos=0 if args[2*donor]==value(receiver)else 1
        assert args[2*donor+pos]==value(receiver)
        successor[2*donor+pos]=receiver;incoming.add(receiver);used.add(donor)
    offers=[]
    for x in order:
        if not args[2*x]or x in used:continue
        starts=[e for e in users[x]if e not in incoming]
        if len(starts)<2:continue
        starts.sort(key=lambda e:(-ranks[owner(e)] if policy=='wide'else ranks[owner(e)],time(e)))
        for first in starts[:limit]:
            first_time=time(first);frame=frames[owner(first)]
            assert contained(frames[x],frame)
            chain=[];e=first
            while True:
                chain.append(e)
                assert contained(frame,frames[owner(e)])
                if e not in successor:break
                e=successor[e]
            for parent_pos in (0,1):
                other=args[2*x+1-parent_pos]
                providers=[]
                for use in users[other]:
                    if use>>31:continue
                    gate=use//2
                    if gate==x or gate in used or times[gate]>=first_time:continue
                    if contained(frames[gate],frame):providers.append(gate)
                providers=sorted(set(providers),key=lambda g:(ranks[g],times[g],g),reverse=policy=='late')
                for provider in providers[:limit]:
                    offers.append(dict(parent=x,parent_position=parent_pos,provider=provider,
                                       first=first,frame_owner=owner(first),chain=chain,
                                       source_children=list(args[2*x:2*x+2]),frame_rank=frame[0]))
    counts=Counter(x['parent']for x in offers)
    loads=Counter(g for x in offers for g in (x['parent'],x['provider']))
    def key(x):
        tie=sha256(repr((seed,x['parent'],x['provider'],x['first'],x['parent_position'])).encode()).digest()
        if policy=='wide':return(-x['frame_rank'],counts[x['parent']],loads[x['provider']],tie)
        if policy=='scarce':return(loads[x['parent']]+loads[x['provider']],counts[x['parent']],x['frame_rank'],tie)
        return(-times[x['parent']],-times[x['provider']],tie)
    chosen=[];capacities=set();parents=set();formal=set();reasons=Counter()
    for offer in sorted(offers,key=key):
        x=offer['parent'];caps={x,offer['provider']};children=set(offer['source_children'])
        if caps&capacities:reasons['gate capacity']+=1;continue
        if x in parents:reasons['parent already cloned']+=1;continue
        if x in formal or children&parents:reasons['formal child conflict']+=1;continue
        chosen.append(offer);capacities|=caps;parents.add(x);formal|=children
    return chosen,dict(offered=len(offers),chosen=len(chosen),rejected=dict(reasons)),order,frames


def rewrite(row,jobs,order,frames,target):
    h,v,n,q,args,core,cover,roots,kinds,active=read_dag(row['dag_path'])
    target.mkdir(parents=True,exist_ok=False)
    move={};before={};terminal=[]
    for index,job in enumerate(jobs):
        for e in job['chain']:
            assert e not in move
            move[e]=index
        if job['first']>>31:terminal.append(index)
        else:before.setdefault(job['first']//2,[]).append(index)
    newargs=[0,0];newcore=[0];newcover=[0];newframes=[None]
    mapping={};clones={}
    def clone(index):
        job=jobs[index];x=job['parent'];node=len(newcore)
        clones[index]=node
        a,b=args[2*x:2*x+2]
        assert a in mapping and b in mapping
        newargs.extend((mapping[a],mapping[b]));newcore.append(core[x]);newcover.append(cover[x])
        newframes.append(frames[job['frame_owner']])
    for old in order:
        for index in before.get(old,[]):clone(index)
        node=len(newcore);mapping[old]=node
        if args[2*old]:
            children=[]
            for pos in (0,1):
                e=2*old+pos
                child=clones[move[e]]if e in move else mapping[args[e]]
                children.append(child)
            newargs.extend(children)
        else:
            assert node==old<=v
            newargs.extend((0,0))
        newcore.append(core[old]);newcover.append(cover[old]);newframes.append(frames[old])
    for index in terminal:clone(index)
    newroots=[clones[move[(1<<31)|j]]if(1<<31)|j in move else mapping[x]for j,x in enumerate(roots)]
    nn=len(newcore);dag=target/'dag.bin'
    with dag.open('wb')as stream:
        stream.write(struct.pack('<4I',h,v,nn,q))
        for code,values in (('I',newargs),('Q',newcore),('Q',newcover),('I',newroots),('I',kinds),('B',[0]+[1]*(nn-1))):
            stream.write(array.array(code,values).tobytes())
    with Path(str(dag)+'.positive').open('wb')as stream:
        stream.write(struct.pack('<2I',h,nn))
        stream.write(array.array('I',[0]+[f[0]for f in newframes[1:]]).tobytes())
        stream.write(array.array('Q',[0]+[f[1]for f in newframes[1:]]).tobytes())
        stream.write(array.array('b',[0]*h+[x for f in newframes[1:]for x in f[2]]).tobytes())
    oldlinks=json.loads(Path(row['witness_path']).read_text())['links']
    retained=[]
    for donor,receiver in oldlinks:
        e=receiver if receiver>>31 else 2*mapping[receiver//2]+(receiver&1)
        retained.append([mapping[donor],e])
    for index,job in enumerate(jobs):
        node=clones[index];p=job['parent_position']
        retained.append([mapping[job['parent']],2*node+p])
        retained.append([mapping[job['provider']],2*node+1-p])
    constructed=dict(h=h,n=nn,links=retained)
    (target/'constructed-links.json').write_text(json.dumps(constructed,sort_keys=True)+'\n')
    (target/'rewrite.json').write_text(json.dumps(dict(source_dag=row['dag_path'],source_dag_sha256=digest(row['dag_path']),
                                                     selected_jobs=jobs,original_node_map=mapping,clone_node_map=clones),sort_keys=True)+'\n')
    return dag,constructed


def evaluate(task):
    parent,work,matcher,policy,limit,seed,round_limit,*extensions=task
    source=json.loads(Path(parent).read_text())
    if 'producer'in source:row=dict(source['producer'])
    else:row=dict(next(x for x in source['rows']if x.get('h')==8 and x['configuration']['tree']=='left'))
    initial=dict(row);stages=[];at=time.monotonic()
    name=f"h{row['h']}-{policy}-l{limit}-s{seed}"
    if extensions:name+='-'+extensions[0]
    try:
        for iteration in range(round_limit):
            jobs,diagnostic,order,frames=opportunities(row,limit,policy,seed+1000003*iteration)
            stage=dict(round=iteration+1,parent_roles=row['R'],diagnostic=diagnostic)
            if not jobs:
                stage['terminal']=True;stages.append(stage);break
            target=Path(work)/'raw'/name/f'round-{iteration+1}'
            dag,constructed=rewrite(row,jobs,order,frames,target)
            witness=target/'selected-links.json'
            native=subprocess.run([str(matcher),str(dag),str(dag)+'.positive',str(seed+iteration),str(2),str(witness)],
                                  text=True,capture_output=True,check=True)
            new=json.loads(native.stdout)
            assert new['matched']>=row['matched']+2*len(jobs)
            assert new['R']<=row['R']-len(jobs)
            (target/'native-stderr.txt').write_text(native.stderr)
            new.update(status='exact native edited-frame histogram; independent scalar/compiler check pending',
                       dag_path=str(dag),dag_sha256=digest(dag),positive_sha256=digest(str(dag)+'.positive'),
                       witness_path=str(witness),witness_sha256=digest(witness),schedule='rank-node',
                       configuration=dict(policy=policy,limit=limit,seed=seed,round=iteration+1),
                       original_producer_path=str(parent))
            stage.update(chosen=jobs,roles_upper_bound=row['R']-len(jobs),new_roles=new['R'],
                         constructed_witness_path=str(target/'constructed-links.json'),
                         rewrite_path=str(target/'rewrite.json'),new_dag_sha256=new['dag_sha256'])
            stages.append(stage);row=new
        result=dict(status='changed clone candidate',case_id=name,producer=row,initial_roles=initial['R'],
                    role_saving=initial['R']-row['R'],stages=stages,
                    selected_links=json.loads(Path(row['witness_path']).read_text()),seconds=time.monotonic()-at,
                    proof_scope='Whole actual controller chains; literal inherited frames; two disjoint unused gate capacities; original/clone formal-child exclusion; no scalar or target changes')
        (Path(work)/'raw'/f'{name}.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
        return result
    except Exception as error:
        result=dict(status='failed',case_id=name,error=repr(error),stages=stages,seconds=time.monotonic()-at)
        (Path(work)/'raw'/f'{name}-failure.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
        return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--parent',type=Path,nargs='+',required=True);p.add_argument('--work',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--workers',type=int,default=10)
    p.add_argument('--rounds',type=int,default=3);p.add_argument('--small',action='store_true')
    p.add_argument('--tag-input',action='store_true')
    p.add_argument('--policies',nargs='+',choices=['wide2','wide8','scarce','late'],
                   default=['wide2','wide8','scarce','late'])
    a=p.parse_args();assert not a.output.exists()and 1<=a.workers<=10
    (a.work/'builds').mkdir(parents=True,exist_ok=True);(a.work/'raw').mkdir(exist_ok=True)
    native=Path(__file__).with_name('moment_match_rank_node.cpp');matcher=a.work/'builds'/'matcher'
    subprocess.run(['c++','-O3','-std=c++17',str(native),'-o',str(matcher)],check=True)
    tasks=[]
    for parent in a.parent:
        families={'wide2':('wide',2),'wide8':('wide',8),'scarce':('scarce',4),'late':('late',4)}
        for policy,limit in (families[k]for k in a.policies):
            task=(parent,a.work,matcher,policy,limit,104729,a.rounds)
            if a.tag_input:task+= (parent.stem+'-'+digest(parent)[:8],)
            tasks.append(task)
    result=dict(status='running',command=sys.argv,started_utc=datetime.now(timezone.utc).isoformat(),
                source_sha256={p.name:digest(p)for p in (Path(__file__),native,Path(__file__).with_name('check_compiled_witness.py'))},
                workers=a.workers,rows=[])
    with ProcessPoolExecutor(max_workers=a.workers)as pool:
        fs=[pool.submit(evaluate,t)for t in tasks]
        for f in as_completed(fs):
            row=f.result();result['rows'].append(row)
            a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
            print(json.dumps({k:row.get(k)for k in ('case_id','status','role_saving','seconds','error')}),flush=True)
    result.update(status='complete',completed_utc=datetime.now(timezone.utc).isoformat())
    a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')


if __name__=='__main__':main()
