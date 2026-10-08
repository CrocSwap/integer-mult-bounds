"""Exact small-network controls and full five-set matching for the F3 motif.

Finite checks complement the general source-span and finite-alphabet proofs.
They are not a formal proof of the full multiplication theorem.
"""
from itertools import combinations
from math import comb
from fractions import Fraction as Q
from functools import lru_cache
import argparse,json,time
from paired_triple_circuit import PairedTriple
from prime_field_circuit import point_orders
from exclusion_circuit import ExclusionCircuit


def edge_cycle(vertices):
    graph={x:set(vertices)-{x} for x in vertices};stack=[vertices[0]];tour=[]
    while stack:
        x=stack[-1]
        if graph[x]:
            y=min(graph[x]);graph[x].remove(y);graph[y].remove(x);stack.append(y)
        else:tour.append(stack.pop())
    edges=[tuple(sorted(p)) for p in zip(tour,tour[1:])]
    assert len(edges)==comb(len(vertices),2) and len(set(edges))==len(edges)
    return {e:edges[(j+1)%len(edges)] for j,e in enumerate(edges)}


def matching(h=28):
    assert h%4==0
    q=h//2;cycles={i:edge_cycle([j for j in range(q) if j!=i]) for i in range(q)}
    images=set()
    for S in combinations(range(h),5):
        members=set(S);full={x//2 for x in S if (x^1) in members}
        singles=[x for x in S if (x^1) not in members]
        if not full:
            keep=set(sorted(singles,key=lambda x:x//2)[:2]);T=tuple(sorted(x if x in keep else x^1 for x in S))
        elif len(full)==1:
            T=tuple(sorted([x for x in S if x//2 in full]+[x^1 for x in singles]))
        else:
            assert len(full)==2 and len(singles)==1
            u=singles[0];new=cycles[u//2][tuple(sorted(full))]
            T=tuple(sorted([2*j+b for j in new for b in (0,1)]+[u^1]))
        assert len(members&set(T))==2
        images.add(T)
    assert len(images)==comb(h,5)
    return dict(h=h,domain=comb(h,5),distinct_images=len(images),every_intersection_two=True)


class SmallProducer:
    def __init__(self,h=8):
        self.h=h;self.inputs=list(combinations(range(h),5));self.variables={s:i+1 for i,s in enumerate(self.inputs)}
        self.support=[0]+[1<<i for i in range(len(self.inputs))];self.args=[None]*len(self.support)
        self.lookup={s:i for i,s in enumerate(self.support)};self.outputs={};self.side=[];self.totals=[]
        c=PairedTriple(h-2);total=c.triple(list(range(h-2)),c.variables)[()]
        active=set(c.active);stack=[total]
        while stack:
            x=stack.pop()
            if not x or x in active:continue
            active.add(x)
            if c.args[x]:stack.extend(c.args[x])
        for C,order in point_orders(h,'aligned').items():
            ids={0:0}
            for node in sorted(active):
                if not c.args[node]:
                    T=tuple(sorted(C+tuple(order[x] for x in c.inputs[node-1])));ids[node]=self.variables[T]
                else:
                    a,b=c.args[node];ids[node]=self.add(ids[a],ids[b])
            for E,node in c.outputs.items():
                S=tuple(sorted(C+tuple(order[x] for x in E)));k=len(self.outputs)
                self.outputs[k]=ids[node];self.side.append((k,self.inputs.index(S)))
            k=len(self.outputs);self.outputs[k]=ids[total];self.totals.append((k,C))
        self.active=set();stack=list(self.outputs.values())
        while stack:
            x=stack.pop()
            if not x or x in self.active:continue
            self.active.add(x)
            if self.args[x]:stack.extend(self.args[x])
        self.additions=sum(self.args[x] is not None for x in self.active);self.roles=self.additions+len(self.outputs)
    add=ExclusionCircuit.add
    compile=ExclusionCircuit.compile

    def verify_map(self):
        v=len(self.inputs);side=[0]*v
        for i,j in self.side:
            s=self.support[self.outputs[i]];assert not side[j]&s;side[j]|=s
        for j,S in enumerate(self.inputs):
            assert side[j]==sum(1<<i for i,T in enumerate(self.inputs) if len(set(S)&set(T))==2)
        for i,C in self.totals:
            assert self.support[self.outputs[i]]==sum(1<<j for j,T in enumerate(self.inputs) if set(C)<=set(T))
        for k in range(6):assert (comb(k,2)-int(k==2))%3==int(k==5)
        cores={}
        for node in sorted(self.active):
            if self.args[node]:
                a,b=self.args[node];assert not self.support[a]&self.support[b]
                assert self.support[node]==self.support[a]|self.support[b];cores[node]=cores[a]&cores[b]
            else:cores[node]=set(self.inputs[node-1])
            assert len(cores[node])>=2
        return dict(h=self.h,inputs=v,roles=self.roles,side_coefficients_exact=True,retained_coefficients_exact=True,every_node_has_common_pair=True)


def scalar_control(c):
    code=c.compile();v=len(c.inputs);R=c.roles;n=2*v+R
    rows=[{i:1} for i in range(n)];x=rows[:v];y=rows[v:2*v];z=rows[2*v:]
    def update(a,b,sign):
        for k,x in b.items():
            value=(a.get(k,0)+sign*x)%3
            if value:a[k]=value
            else:a.pop(k,None)
    def L(sign):
        for _,ins,outs in code['gates'] if sign==1 else reversed(code['gates']):
            if sign==1:
                for slot in ins[1:]:update(z[ins[0]],z[slot],1)
                for slot in outs[1:]:update(z[slot],z[ins[0]],1)
            else:
                for slot in outs[1:]:update(z[slot],z[ins[0]],-1)
                for slot in ins[1:]:update(z[ins[0]],z[slot],-1)
    def V(sign,bank):
        for T,slot in code['sources'].items():update(z[slot],bank[c.variables[T]-1],sign)
    def J(sign,bank):
        for i,j in c.side:update(bank[j],z[code['outputs'][i]],-sign)
    def Rscatter(sign,bank):
        for i,C in c.totals:
            for j,S in enumerate(c.inputs):
                if set(C)<=set(S):update(bank[j],z[code['outputs'][i]],sign)
    def invoke(source,target,inverse=False):
        ops=[(L,1),(Rscatter,-1),(J,-1),(L,-1),(V,1),(L,1),(Rscatter,1),(J,1),(L,-1),(V,-1)]
        if inverse:ops=[(op,-sign) for op,sign in reversed(ops)]
        for op,sign in ops:
            if op is L:op(sign)
            else:op(sign,source if op is V else target)
    original=[dict(r) for r in rows];invoke(x,y);expected=[dict(r) for r in original]
    for j in range(v):update(expected[v+j],expected[j],1)
    assert rows==expected
    invoke(x,y,True);assert rows==original
    invoke(x,y);invoke(y,x,True);invoke(x,y)
    for row in x:
        for k in row:row[k]=(-row[k])%3
    expected=[dict(r) for r in original];expected[:v]=original[v:2*v];expected[v:2*v]=original[:v]
    assert rows==expected
    return dict(h=c.h,all_basis_inputs=n,dirty_scratch_restored=True,forward_inverse_exact=True,corrected_three_stage_exchange=True)


@lru_cache(None)
def basis(rows):
    if not rows:return ()
    a=[[Q(x) for x in row] for row in rows];r=0
    for j in range(len(a[0])):
        k=next((k for k in range(r,len(a)) if a[k][j]),None)
        if k is None:continue
        a[r],a[k]=a[k],a[r];v=a[r][j];a[r]=[x/v for x in a[r]]
        for k in range(len(a)):
            if k!=r and a[k][j]:
                v=a[k][j];a[k]=[x-v*y for x,y in zip(a[k],a[r])]
        r+=1
        if r==len(a):break
    return tuple(tuple(row) for row in a[:r])


def frame_control(c):
    h=c.h;code=c.compile();v=len(c.inputs);R=c.roles
    full=tuple(tuple(int(i==j) for j in range(h)) for i in range(h));zero=()
    lines=[(tuple(int(i in T) for i in range(h)),) for T in c.inputs]
    labels={}
    for node in sorted(c.active):
        if c.args[node]:
            a,b=c.args[node];labels[node]=basis(labels[a]+labels[b])
        else:labels[node]=basis(lines[node-1])
    @lru_cache(None)
    def perp(U):
        if not U:return full
        equations=basis(tuple(tuple(x-Q(2,25)*sum(u) for x in u) for u in U))
        pivots=[next(i for i,x in enumerate(row) if x) for row in equations]
        vectors=[]
        for f in range(h):
            if f in pivots:continue
            vector=[Q(0)]*h;vector[f]=Q(1)
            for row,pivot in zip(equations,pivots):vector[pivot]=-row[f]
            vectors.append(tuple(vector))
        return basis(tuple(vectors))
    @lru_cache(None)
    def nonsingular(U):
        gram=tuple(tuple(sum(x*y for x,y in zip(u,v))-Q(2,25)*sum(u)*sum(v) for v in U) for u in U)
        return len(basis(gram))==len(U)
    for U in labels.values():assert nonsingular(U)
    for i,C in c.totals:assert len(labels[c.outputs[i]])==h-2
    @lru_cache(None)
    def transition(U,V):
        assert nonsingular(U) and nonsingular(V)
        if len(U)<=len(V):assert len(basis(U+V))==len(V)
        else:assert len(basis(U+V))==len(U)
        return abs(len(V)-len(U)),max(len(U)-len(V),0)
    results=[]
    for reverse in (False,True):
        frames=[basis(x) for x in lines]+[zero]*(v+R);total=loss=0
        def gate(wires,U):
            nonlocal total,loss
            for w in set(wires):
                a,b=transition(frames[w],U);total+=a;loss+=b;frames[w]=U
        def mix(mode,inverse=False):
            for node,ins,outs in reversed(code['gates']) if inverse else code['gates']:
                U=zero if mode=='low' else full if mode=='high' else labels[node] if mode=='node' else perp(labels[node])
                gate([2*v+s for s in ins+outs],U)
        def copy(bank,mode):
            for T,slot in code['sources'].items():
                j=c.variables[T]-1;U=zero if mode=='low' else full if mode=='high' else basis(lines[j]) if mode=='line' else perp(basis(lines[j]))
                gate([bank+j,2*v+slot],U)
        def inject(bank,mode):
            groups=[[] for _ in c.inputs]
            for i,j in c.side:groups[j].append(2*v+code['outputs'][i])
            for j,slots in enumerate(groups):
                U=zero if mode=='low' else full if mode=='high' else basis(lines[j]) if mode=='line' else perp(basis(lines[j]))
                gate([bank+j]+slots,U)
        def scatter(bank,U):gate(list(range(bank,bank+v))+[2*v+code['outputs'][i] for i,_ in c.totals],U)
        if not reverse:
            mix('low');scatter(v,zero);inject(v,'low');mix('low',True);copy(0,'line');mix('node');scatter(v,zero);inject(v,'perp');mix('high',True);copy(0,'high')
        else:
            copy(v,'low');mix('low');inject(0,'line');scatter(0,full);mix('perp',True);copy(v,'perp');mix('high');inject(0,'high');scatter(0,full);mix('high',True)
        for j in range(v):gate([j],full);gate([v+j],perp(basis(lines[j])))
        gate(list(range(2*v,2*v+R)),full)
        assert loss==comb(h,2)*(h-2)
        assert total==(2*v+R)*h-2*v+2*loss
        results.append(dict(reverse=reverse,total_rank=total,loss=loss,every_edge_nested_and_nondegenerate=True))
    return dict(h=h,frames=results)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--h',type=int,default=8);p.add_argument('--frames',action='store_true');a=p.parse_args();start=time.monotonic()
    print(json.dumps(dict(matching=matching())),flush=True)
    c=SmallProducer(a.h);print(json.dumps(dict(producer=c.verify_map())),flush=True)
    print(json.dumps(dict(scalar=scalar_control(c))),flush=True)
    if a.frames:print(json.dumps(dict(physical_frames=frame_control(c))),flush=True)
    print(json.dumps(dict(elapsed=time.monotonic()-start)),flush=True)
