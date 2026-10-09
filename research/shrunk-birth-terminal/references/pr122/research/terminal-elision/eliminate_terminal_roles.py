#!/usr/bin/env python3
"""Explicit terminal-role deletion, retaining old garbage/front schedules.

Input is an exported deferred word and its complete one-child profile.
The literal stage-one event word keeps every retained auxiliary update at
its old time; it redirects only destination-only terminal roles into Y.
"""
import argparse
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import random
import sys
from frame_extension import basis, contains
from inventory_terminal_schedule import inspect


def need(ok, msg):
    if not ok: raise ValueError(msg)


def main():
    if sys.flags.optimize: raise ValueError('Assertions required')
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--word',type=Path,required=True);p.add_argument('--profile',type=Path,required=True)
    p.add_argument('--inventory',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
    w=json.loads(gzip.decompress(a.word.read_bytes()));oldprof=json.loads(a.profile.read_text())
    inv=json.loads(a.inventory.read_text())
    need(hashlib.sha256(a.word.read_bytes()).hexdigest()==inv['word_sha256'],'inventory word hash')
    schedule=inspect(w,set(inv['terminal_roles']))
    removed=set(schedule['accepted'])
    need(removed and not schedule['rejected'],'prescribed simultaneous candidates')
    frames={int(k):v for k,v in w['frames'].items()};sigma={int(k):v for k,v in w['sigma'].items()}
    roots={int(k):v for k,v in w['role_root'].items()};leaves={int(k):v for k,v in w['leaf_of'].items()}
    rootframes={int(k):v for k,v in w['root_frames'].items()}
    phase1=set(w['phase_one']);dset=set(w['deferred']);v,h=w['v'],w['h'];m=h*h
    active=[s for s in range(w['R']) if s not in removed]
    # Each event stores its original source index, making temporal claims
    # independently inspectable. A target_front executes even if its old
    # associated garbage readout was removed.
    events=[];current=[[] for _ in range(v)];target_paths=[[[]] for _ in range(v)]
    def front(t,F,why):
        need(contains(current[t],F),'target frame reversal')
        if basis(current[t])!=basis(F):
            events.append(['target_front',t,F,why]);target_paths[t].append(F)
        current[t]=F
    def redirect(s,src,frame,index,data=False):
        j=roots[s];t=w['target'][j];coeff=21 if j<v else -21
        front(t,frame,['redirect',index,s])
        events.append(['direct_input' if data else 'direct_aux',t,src,coeff,frame,index,s])
    def gate(i,inverse=False):
        o=w['ops'][i]
        if o[0]=='src':return
        dst,src=(o[1],o[2]) if o[0]=='add' else (o[2],o[1])
        need(src not in removed,'removed control used')
        if dst in removed:
            need(i not in phase1,'redirect would cross center phase')
            if not inverse:redirect(dst,src,frames[o[3]],i)
        else:events.append(['gate',i,-1 if inverse else 1])
    for s in active:
        if s not in dset:events.append(['readout',s,-1,False,'initial'])
    for s,leaf in leaves.items():
        if s not in dset:
            need(s not in removed,'nondeferred leaf deletion')
            events.append(['input',s,leaf,1])
    for i in w['phase_one']:gate(i)
    for s,j in roots.items():
        if w['kind'][j]:
            need(s not in removed,'center removed')
            events.append(['readout',s,1,True,'center'])
    for s in w['deferred']:
        for t in w['reach'][s]:front(t,sigma[s],['old_garbage',s])
        if s not in removed:events.append(['readout',s,-1,False,'deferred'])
    for s in w['deferred']:
        if s in leaves:
            if s in removed:redirect(s,leaves[s],frames[w['first_node'][s]],-1,True)
            else:events.append(['input',s,leaves[s],1])
    for i in range(len(w['ops'])):
        if i not in phase1:gate(i)
    for s,j in roots.items():
        if not w['kind'][j]:
            front(w['target'][j],rootframes[s],['ordinary_root',s])
            if s not in removed:events.append(['readout',s,1,True,'ordinary'])
    for i in reversed(range(len(w['ops']))):gate(i,True)
    for s,leaf in leaves.items():
        if s not in removed:events.append(['input',s,leaf,-1])
    need(all(len(basis(F))==h-1 for F in current),'terminal target frames')
    # Preserve every retained role's old chain: each replaced gate still
    # reads its retained control in exactly the same node frame. There are
    # no missing source incidences and no new auxiliary frame transitions.
    old_target=Counter();new_target=Counter();deleted_hist=Counter()
    levels=[{0,h-1} for _ in range(v)]
    for s in w['deferred']:
        for t in w['reach'][s]:levels[t].add(len(basis(sigma[s])))
    for levels_t in levels:
        ds=sorted(levels_t)
        for x,y in zip(ds,ds[1:]):old_target[y-x]+=2*v
    for seq in target_paths:
        ds=[len(basis(F)) for F in seq]
        for x,y in zip(ds,ds[1:]):
            if y>x:new_target[y-x]+=2*v
    for s in removed:
        ds=w['chain_dims'][s]
        for x,y in zip(ds[:-1],ds[1:-1]):
            if y>x:deleted_hist[y-x]+=2*v
        deleted_hist[h-ds[-2]]+=2*v
        deleted_hist[m-h+ds[0]]+=2*v
    deleted_hist.pop(0,None)
    need(sum(t*c for t,c in deleted_hist.items())==2*v*len(removed)*m,'deleted role mass')
    z=Counter({int(t):c for t,c in oldprof['child_multiplicities'].items()})
    z.subtract(deleted_hist);z.subtract(old_target);z.update(new_target)
    need(all(c>=0 for c in z.values()),'negative child multiplicity')
    z=Counter({t:c for t,c in z.items() if c})
    newR=w['R']-len(removed);newW=2*v*v+2*v*newR;rank=sum(t*c for t,c in z.items())
    need(newW*m-rank==oldprof['deficit'],'complete deficit changed')
    incoming=sum(e[0] in ('direct_aux','direct_input') for e in events)
    oldscalar=oldprof['literal_scalar_terms']
    # Each removed role had one ordinary adjoint read and one final read.
    # An incoming gate/injection and its inverse cost two old operations;
    # replacing those by one ±1/2 output update costs at most one of the
    # same generously expanded fixed-coefficient scalar groups.
    newscalar=oldscalar-2*len(removed)-incoming
    need(newscalar<=oldscalar,'local scalar bound increase')
    prof=dict(oldprof);prof.update(pre_elimination_R=w['R'],R=newR,W=newW,total_rank=rank,
        terminal_elimination_count=len(removed),terminal_direct_updates=incoming,
        child_multiplicities=dict(sorted(z.items())),maxchild=max(z),
        literal_scalar_terms=newscalar,
        safe_one_axis_scalar_groups=(4*oldprof['max_coefficient_bits']+16)*newscalar,
        deferred_roles=oldprof['deferred_roles']-len(removed),
        role_count_scope='Explicit terminal-elided word; old DAG c+q-links is pre-elimination only.')
    dd=Counter({int(k):c for k,c in oldprof['deferred_dims'].items()})
    for s in removed:dd[len(basis(sigma[s]))]-=1
    prof['deferred_dims']={k:c for k,c in sorted(dd.items()) if c}
    receipt=dict(removed=sorted(removed),active_roles=active,events=events,
        target_paths=target_paths,deleted_child_multiplicities=dict(sorted(deleted_hist.items())),
        old_target_histogram=dict(sorted(old_target.items())),
        new_target_histogram=dict(sorted(new_target.items())),
        target_delta={t:new_target[t]-old_target[t] for t in sorted(old_target.keys()|new_target.keys())
                      if new_target[t]!=old_target[t]},
        input_word_sha256=hashlib.sha256(a.word.read_bytes()).hexdigest())
    # Scalar replay is separate from the exact structural/adjoint proof.
    P=(1<<61)-1;inv42=pow(42,P-2,P)
    trip=[tuple(i for i in range(h) if mask>>i&1) for mask in []]
    from itertools import combinations
    trip=list(combinations(range(h),3))
    scatter=[[2-21*(i in T) for T in trip] for i in range(h)]
    def replay(seed):
        rng=random.Random(seed);x=[rng.randrange(P) for _ in range(v)]
        z0={s:rng.randrange(P) for s in active};aux=dict(z0)
        y0=[rng.randrange(P) for _ in range(v)];y=list(y0)
        # Batched centers change only evaluator work, not exported word.
        center_pending=[0]*h
        def read(s,sign,seeded):
            if seeded:
                j=roots[s]
                if w['kind'][j]:cv=[0]*h;cv[int(w['centre_of'][str(j)])]=1;dp={}
                else:cv=None;dp={w['target'][j]:21 if j<v else -21}
            else:cv=w['adjoint_centre'][s];dp=w['adjoint_ordinary'][s]
            value=sign*aux[s]*inv42%P
            if cv:
                for i,c in enumerate(cv):center_pending[i]=(center_pending[i]+c*value)%P
            for t,c in dp.items():y[int(t)]=(y[int(t)]+c*value)%P
        for e in events:
            if e[0]=='target_front':continue
            if e[0]=='input':aux[e[1]]=(aux[e[1]]+e[3]*x[e[2]-1])%P
            elif e[0]=='gate':
                o=w['ops'][e[1]];dst,src=(o[1],o[2]) if o[0]=='add' else (o[2],o[1])
                aux[dst]=(aux[dst]+e[2]*aux[src])%P
            elif e[0]=='readout':read(e[1],e[2],e[3])
            elif e[0] in ('direct_aux','direct_input'):
                value=aux[e[2]] if e[0]=='direct_aux' else x[e[2]-1]
                y[e[1]]=(y[e[1]]+e[3]*inv42*value)%P
            else:raise ValueError('unknown event')
        for i,f in enumerate(center_pending):
            for t,c in enumerate(scatter[i]):y[t]=(y[t]+f*c)%P
        need(aux==z0,'remaining dirty scratch not restored')
        need(all((yy-yb-xx)%P==0 for yy,yb,xx in zip(y,y0,x)),'normalized scalar map')
    for seed in (202610081,202610082):replay(seed)
    receipt['modular_replay']=dict(seeds=[202610081,202610082],prime=P,passed=True)
    (a.out/'word.json.gz').write_bytes(gzip.compress(json.dumps(receipt,separators=(',',':')).encode(),mtime=0))
    (a.out/'complex-profile.json').write_text(json.dumps(prof,indent=2)+'\n')
    (a.out/'selection.json').write_text(json.dumps(schedule,indent=2)+'\n')
    paths=[a.word,a.profile,a.inventory,Path(__file__),Path(__file__).with_name('frame_extension.py'),
           Path(__file__).with_name('inventory_terminal_schedule.py')]
    (a.out/'SOURCE.json').write_text(json.dumps({str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},indent=2)+'\n')
    (a.out/'generator-source.py').write_bytes(Path(__file__).read_bytes())
    print(json.dumps(dict(removed=len(removed),R=newR,W=newW,total_rank=rank,
        direct_updates=incoming,target_delta=receipt['target_delta'],replay='PASS'),indent=2))


if __name__=='__main__':main()
