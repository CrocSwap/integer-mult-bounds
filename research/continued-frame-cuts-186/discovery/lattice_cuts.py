#!/usr/bin/env python3
"""Minimum cuts for coordinated frame intersections and joins.

An intersection move uses F_i -> F_i intersect L on a predecessor-closed
set; a join move uses F_i -> F_i + L on a successor-closed set. The forbidden
mixed state makes each binary edge submodular. The cut only proposes moves;
all resulting exact frame inclusions and the complete paid word are checked.
Prepared by huxint with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import deque,Counter
from pathlib import Path
import argparse,json,math,random,sys,time
import numpy as np
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
from complex_search import Experiment,numerical_root,algebraic_birth_audit
from cut_search import Expansion,minimum_cut
from paired_cube.frames import basis,perp,contained
from paired_cube_physical import physical


class Cut:
    def __init__(self,e):
        self.e=e;self.geometry=Expansion(e);self.scale=10**12;self.M=10000.
    def step(self,L,mode):
        e=self.e;N=e.N;down=mode=='meet'
        ann=np.array(perp(L,e.h),dtype=np.uint32)
        bad=np.zeros(len(self.geometry.table),dtype=bool)
        if len(ann):
            flags=(np.bitwise_count(self.geometry.rows[:,None]&ann[None,:])&1).any(axis=1)
            np.logical_or.at(bad,self.geometry.rowids,flags)
        sub=~bad
        eligible=sub[self.geometry.spans] if down else np.ones(N,dtype=bool)
        old=e.frames
        inside={F:contained(F,L) if down else contained(L,F) for F in set(old)}
        fixed={F:contained(F,L) if down else contained(L,F) for F in e.constants}
        unchanged=np.array([inside[F] for F in old],dtype=bool)
        take=eligible & ~unchanged;queue=deque()
        def forbid(i):
            if take[i]:take[i]=False;queue.append(i)
        def fixed_ok(i):return unchanged[i] if i>=0 else fixed[e.constants[-i-1]]
        for a,b in e.edges:
            if down and b>=0 and take[b] and not (a>=0 and take[a]) and not fixed_ok(a):forbid(b)
            if not down and a>=0 and take[a] and not (b>=0 and take[b]) and not fixed_ok(b):forbid(a)
        while queue:
            i=queue.popleft()
            if unchanged[i]:continue
            for k in (e.out_edges[i] if down else e.in_edges[i]):
                j=e.edges[k][1 if down else 0]
                if j>=0:forbid(j)
        nodes=np.flatnonzero(take).tolist()
        if not nodes:return 0.,0,0
        byframe={}
        if down:
            P=perp(L,e.h)
            for F in {old[i] for i in nodes}:byframe[F]=perp(basis(perp(F,e.h)+P),e.h)
        else:
            for F in {old[i] for i in nodes}:byframe[F]=basis(F+L)
        new={i:byframe[old[i]] for i in nodes};index={i:j for j,i in enumerate(nodes)};nv=len(nodes)
        touched=sorted({k for i in nodes for k in e.in_edges[i]+e.out_edges[i]})
        unary=[0.]*nv;rows=[];cols=[];caps=[];before=0.
        for k in touched:
            a,b=e.edges[k];A,B=e.F(a),e.F(b);da,db=len(A),len(B);v00=e.cost[db-da];before+=v00
            ai,bi=index.get(a),index.get(b)
            if ai is not None and bi is not None:
                na,nb=len(new[a]),len(new[b]);v11=e.cost[nb-na]
                v01=self.M if down else e.cost[nb-da]
                v10=e.cost[db-na] if down else self.M
                weight=v01+v10-v00-v11;assert weight>=0
                unary[ai]+=v10-v00;unary[bi]+=v11-v10
                rows.append(ai);cols.append(bi);caps.append(round(weight*self.scale))
            elif ai is not None:
                assert contained(new[a],B)
                unary[ai]+=e.cost[db-len(new[a])]-v00
            else:
                assert bi is not None and contained(A,new[b])
                unary[bi]+=e.cost[len(new[b])-da]-v00
        source,sink=nv,nv+1
        for i,value in enumerate(unary):
            rows.append(source if value>=0 else i);cols.append(i if value>=0 else sink);caps.append(round(abs(value)*self.scale))
        side=minimum_cut(nv+2,rows,cols,caps,source,sink)
        chosen={i for i,j in index.items() if not side[j]}
        after=0.
        for k in touched:
            a,b=e.edges[k];A=new[a] if a in chosen else e.F(a);B=new[b] if b in chosen else e.F(b)
            assert contained(A,B)
            after+=e.cost[len(B)-len(A)]
        gain=before-after
        if gain<=1e-10:return 0.,0,nv
        for i in chosen:
            assert contained(e.node_spans[i],new[i]);e.frames[i]=new[i]
        return gain,len(chosen),nv


def main():
    p=argparse.ArgumentParser();p.add_argument('--baseline',type=Path,required=True);p.add_argument('--frames',type=Path,required=True)
    p.add_argument('--pairs',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--labels',type=int,default=300);p.add_argument('--rounds',type=int,default=2);p.add_argument('--seed',type=int,default=186)
    p.add_argument('--lines',type=int,default=0);p.add_argument('--planes',type=int,default=0)
    a=p.parse_args();e=Experiment(a.baseline,a.frames,input_pairs=a.pairs,alpha=.000663)
    x=Cut(e);rng=random.Random(a.seed)
    pool=sorted({F for F in e.frames if 9<=len(F)<=21},key=lambda F:(len(F),F));rng.shuffle(pool);labels=pool[:a.labels]
    vectors=set(x for F in e.frames for x in F)
    vectors.update(x for F in e.frames for x in perp(F,e.h))
    for F in {perp(F,e.h) for F in e.frames if len(F)>=18}:
        vectors.update(x^y for x in F for y in F if x!=y)
    vec=sorted(vectors);rng.shuffle(vec)
    labels.extend((v,) for v in vec[:a.lines]);rng.shuffle(vec)
    labels.extend(perp((v,),e.h) for v in vec[:a.planes])
    labels=list(dict.fromkeys(labels))
    started=time.monotonic();print(json.dumps(dict(initial=e.profile()['numerical_complex_root'],labels=len(labels))),flush=True)
    for turn in range(a.rounds):
        total=count=0;rng.shuffle(labels)
        for k,L in enumerate(labels):
            for mode in ('meet','join'):
                gain,moved,candidates=x.step(L,mode)
                if moved:
                    total+=gain;count+=moved
                    row=e.profile();H=Counter(row['child_histogram']);H[18]-=138;H[4]-=138
                    print(json.dumps(dict(round=turn,label=k,mode=mode,rank=len(L),gain=gain,moved=moved,candidates=candidates,
                                          raw_root=row['numerical_complex_root'],paid_root_if_46_sinks=numerical_root(H,row['W_per_vertex']-46,66),seconds=time.monotonic()-started)),flush=True)
            if k%25==24:
                print(json.dumps(dict(progress=k+1,round=turn,seconds=time.monotonic()-started)),flush=True)
                e.save(a.output)
        e.check();e.save(a.output)
        print(json.dumps(dict(round_done=turn,gain=total,moved=count)),flush=True)
        if not count:break
    frames=json.loads((a.output/'frames.json').read_text())['frames']
    checked=physical(e.g,e.w,e.word,e.record,frames,e.pairs_input)
    (a.output/'verified.json').write_text(json.dumps(checked,sort_keys=True,indent=2)+'\n')
    print('PASS raw independent physical word; terminal replay remains a separate check',flush=True)


if __name__=='__main__':main()
