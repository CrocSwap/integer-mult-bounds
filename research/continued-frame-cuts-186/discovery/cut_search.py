#!/usr/bin/env python3
"""Joint physical-frame moves by submodular binary minimum cuts.

For a fixed candidate frame F, each operation keeps its old frame or moves
to F. An edge's four costs are f(b-a), f(dim(F)-a), f(b-dim(F)), 0;
incompatible containments receive a prohibitive cost. Concavity of f makes
this binary energy submodular. A cut can therefore move many distinct
current frames together, including moves that individually cost more.
Only the final exact nested-frame witness is used in certification.

Prepared by huxint with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import deque
from pathlib import Path
import argparse
import json
import math
import random
import sys
import time

import numpy as np

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from complex_search import Experiment,algebraic_birth_audit
from paired_cube.frames import perp
from paired_cube_physical import physical


def minimum_cut(size,rows,cols,capacities,source,sink):
    """Dinic with Python integer capacities; no 32-bit flow truncation."""
    adj=[[] for _ in range(size)]
    for a,b,c in zip(rows,cols,capacities):
        if c<=0:continue
        adj[a].append([b,int(c),len(adj[b])])
        adj[b].append([a,0,len(adj[a])-1])
    sys.setrecursionlimit(max(sys.getrecursionlimit(),2*size+100))
    limit=sum(e[1] for e in adj[source])
    while True:
        level=[-1]*size;level[source]=0;queue=deque([source])
        while queue:
            a=queue.popleft()
            for b,c,_ in adj[a]:
                if c and level[b]<0:level[b]=level[a]+1;queue.append(b)
        if level[sink]<0:return np.array([d>=0 for d in level],dtype=bool)
        cursor=[0]*size
        def push(a,amount):
            if a==sink:return amount
            while cursor[a]<len(adj[a]):
                edge=adj[a][cursor[a]];b,c,rev=edge
                if c and level[b]==level[a]+1:
                    sent=push(b,min(amount,c))
                    if sent:
                        edge[1]-=sent;adj[b][rev][1]+=sent;return sent
                cursor[a]+=1
            return 0
        while push(source,limit):pass


class Expansion:
    def __init__(self,e):
        self.e=e
        self.table=[];self.ids={}
        def intern(F):
            F=tuple(F)
            if F not in self.ids:self.ids[F]=len(self.table);self.table.append(F)
            return self.ids[F]
        self.old=np.array([intern(F) for F in e.frames],dtype=np.int32)
        self.spans=np.array([intern(F) for F in e.node_spans],dtype=np.int32)
        self.fixed=np.array([intern(F) for F in e.constants],dtype=np.int32)
        self.gauges=[intern(F) for F in e.gauges.values()]
        self.dims=np.array([len(F) for F in self.table],dtype=np.int32)
        ann=[perp(F,e.h) for F in self.table]
        self.rows=np.array([x for F in self.table for x in F],dtype=np.uint32)
        self.rowids=np.repeat(np.arange(len(self.table)),[len(F) for F in self.table])
        self.ann=np.array([x for A in ann for x in A],dtype=np.uint32)
        self.annids=np.repeat(np.arange(len(self.table)),[len(A) for A in ann])
        self.anns=ann
        self.M=10000.
        self.scale=10**12

    def inclusion(self,fid):
        F=np.array(self.table[fid],dtype=np.uint32)
        A=np.array(self.anns[fid],dtype=np.uint32)
        bad_sub=np.zeros(len(self.table),dtype=bool)
        bad_super=np.zeros(len(self.table),dtype=bool)
        if len(A):
            bad=(np.bitwise_count(self.rows[:,None]&A[None,:])&1).any(axis=1)
            np.logical_or.at(bad_sub,self.rowids,bad)
        if len(F):
            bad=(np.bitwise_count(self.ann[:,None]&F[None,:])&1).any(axis=1)
            np.logical_or.at(bad_super,self.annids,bad)
        return ~bad_sub,~bad_super

    def step(self,fid):
        e=self.e;N=e.N;d=int(self.dims[fid]);cost=e.cost
        sub,sup=self.inclusion(fid)
        take=sub[self.spans] & (self.old!=fid)
        lower=sub[self.old];upper=sup[self.old]
        clower=sub[self.fixed];cupper=sup[self.fixed]
        queue=deque()
        def forbid(i):
            if take[i]:take[i]=False;queue.append(i)
        def left_ok(i):return lower[i] if i>=0 else clower[-i-1]
        def right_ok(i):return upper[i] if i>=0 else cupper[-i-1]
        for a,b in e.edges:
            av=a>=0 and take[a];bv=b>=0 and take[b]
            if av and not bv and not right_ok(b):forbid(a)
            if bv and not av and not left_ok(a):forbid(b)
        while queue:
            i=queue.popleft()
            if not lower[i]:
                for k in e.out_edges[i]:
                    b=e.edges[k][1]
                    if b>=0:forbid(b)
            if not upper[i]:
                for k in e.in_edges[i]:
                    a=e.edges[k][0]
                    if a>=0:forbid(a)
        nodes=np.flatnonzero(take).tolist()
        if not nodes:return 0.,0,0
        index={i:j for j,i in enumerate(nodes)};nv=len(nodes)
        unary=np.zeros(nv,dtype=np.float64)
        row=[];col=[];data=[]
        touched=sorted({k for i in nodes for k in e.in_edges[i]+e.out_edges[i]})
        before=0.
        dims=self.dims[self.old];cdims=self.dims[self.fixed]
        def dim(i):return int(dims[i]) if i>=0 else int(cdims[-i-1])
        for k in touched:
            a,b=e.edges[k];da,db=dim(a),dim(b)
            old=cost[db-da];before+=old
            ai,bi=index.get(a),index.get(b)
            if ai is not None and bi is not None:
                e01=cost[d-da] if lower[a] else self.M
                e10=cost[db-d] if upper[b] else self.M
                w=e01+e10-old
                assert w>=-1e-9,'binary frame energy must be submodular'
                unary[ai]+=e10-old;unary[bi]-=e10
                if w>0:row.append(ai);col.append(bi);data.append(round(w*self.scale))
            elif ai is not None:
                assert right_ok(b)
                unary[ai]+=cost[db-d]-old
            else:
                assert bi is not None and left_ok(a)
                unary[bi]+=cost[d-da]-old
        source,sink=nv,nv+1
        for i,u in enumerate(unary):
            if u>=0:row.append(source);col.append(i);data.append(round(u*self.scale))
            else:row.append(i);col.append(sink);data.append(round(-u*self.scale))
        seen=minimum_cut(nv+2,row,col,data,source,sink)
        assert not seen[sink],'maximum-flow residual must separate source and sink'
        moved={i for i,j in index.items() if not seen[j]}
        if not moved:return 0.,0,nv
        after=0.
        for k in touched:
            a,b=e.edges[k]
            aa=fid if a in moved else int(self.old[a]) if a>=0 else int(self.fixed[-a-1])
            bb=fid if b in moved else int(self.old[b]) if b>=0 else int(self.fixed[-b-1])
            if a in moved and b not in moved:assert right_ok(b)
            if b in moved and a not in moved:assert left_ok(a)
            assert self.dims[bb]>=self.dims[aa]
            after+=cost[int(self.dims[bb]-self.dims[aa])]
        gain=before-after
        if gain<=1e-10:return 0.,0,nv
        for i in moved:e.frames[i]=self.table[fid];self.old[i]=fid
        return gain,len(moved),nv
