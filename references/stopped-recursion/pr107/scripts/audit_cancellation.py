#!/usr/bin/env python3
"""Small cancellation circuits and their nonorthogonal-path rank cost.

Scalar correctness does not imply a valid rank-saving network. The present
candidates are rejected under the retained data-copy/injection frames.
"""
from fractions import Fraction as Q
from itertools import combinations
from math import comb
from pathlib import Path
import json

from certify import require,verify_sources
from prepare_layers import serializable

ROOT=Path(__file__).resolve().parents[1]


class PointCancellation:
    """A1=B1+I over F2, with unshared point-aggregate reduction trees.

    Track XOR coefficients and graph reachability separately. Identical or
    zero algebraic values are not silently removed from this fixed topology.
    """
    def __init__(self,h):
        require(h>=6,'Use h>=6')
        self.h=h
        self.triples=list(combinations(range(h),3))
        v=len(self.triples)
        self.args=[None]*v
        self.coefficients=[1<<i for i in range(v)]
        self.reachable=list(self.coefficients)
        def total(nodes):
            if len(nodes)==1:return nodes[0]
            cut=len(nodes)//2
            return self.add(total(nodes[:cut]),total(nodes[cut:]))
        self.points=[total([j for j,T in enumerate(self.triples) if i in T])
                     for i in range(h)]
        self.outputs=[]
        for t,(a,b,c) in enumerate(self.triples):
            aggregate=self.add(self.add(self.points[a],self.points[b]),self.points[c])
            self.outputs.append(self.add(aggregate,t))
        require(len(self.args)-v==6*v-h,'Unexpected formula count')

    def add(self,a,b):
        require(a!=b,'Keep distinct graph inputs')
        node=len(self.args)
        self.args.append((a,b))
        self.coefficients.append(self.coefficients[a]^self.coefficients[b])
        self.reachable.append(self.reachable[a]|self.reachable[b])
        return node

    def verify(self):
        for t,T in enumerate(self.triples):
            expected=sum(1<<s for s,S in enumerate(self.triples) if len(set(S)&set(T))==1)
            node=self.outputs[t]
            require(self.coefficients[node]==expected,'Wrong side map')
            require(not self.coefficients[node]>>t&1 and self.reachable[node]>>t&1,
                    'Cancelled diagonal path was not distinguished')
        v=len(self.triples)
        return dict(h=self.h,inputs=v,outputs=v,additions=len(self.args)-v,
                    side_roles=len(self.args),exact_neighbor_map=True,
                    cancelled_private_diagonal_paths=v)

    def compile(self):
        """Audited scalar embedding, but NOT the cancellation-free frame rule."""
        v=len(self.triples)
        users=[[] for _ in self.args]
        for node,args in enumerate(self.args):
            if args:
                for pos,source in enumerate(args):users[source].append(('gate',node,pos))
        for target,node in enumerate(self.outputs):users[node].append(('output',target))
        edge={};gates=[];sources=[];outputs=[];size=0;diagonal_edges=[]
        for node,args in enumerate(self.args):
            if args:ins=(edge[node,0],edge[node,1]);pivot=ins[0]
            else:
                pivot=size;size+=1;ins=(pivot,)
                sources.append((node,pivot))
            require(users[node],'Unused node in fixed circuit')
            outs=(pivot,)+tuple(range(size,size+len(users[node])-1))
            size+=len(users[node])-1
            require(len(set(ins))==len(ins) and set(ins)&set(outs)=={pivot},
                    'Overlapping live slots')
            gates.append((ins,outs))
            for user,slot in zip(users[node],outs):
                if user[0]=='gate':
                    edge[user[1],user[2]]=slot
                    if node<v and user[1]==self.outputs[node]:
                        diagonal_edges.append((node,user[1],slot))
                else:outputs.append((user[1],slot))
        require(size==7*v-self.h,'Wrong reversible role count')
        require(len(diagonal_edges)==v and len({x[2] for x in diagonal_edges})==v,
                'Private diagonal wire paths overlap')
        return dict(triples=self.triples,gates=gates,sources=sources,outputs=outputs,
                    roles=size,private_diagonal_edges=diagonal_edges)


def candidate_counts(h):
    require(h>=6,'Use h>=6')
    v=comb(h,3);N=v**3;m=h**3
    side=7*v-h
    # This is an optimistic role allocation before the failed frame audit.
    W=2*N+2*v*v*(side+h)
    return dict(h=h,v=v,N=N,m=m,additions=6*v-h,side_roles=side,
                optimistic_shared_W=W,old_deficit=N-6*v*v*h*h,
                stage_one_disjoint_diagonal_paths=N,
                rank_sum_lower_bound_without_negative_source_charge=W*m,
                deficit_upper_bound=0,
                status='REJECTED with retained data-copy/injection frames; W count alone is not a witness')


def line_projection(h,T):
    require(len(T)==3 and len(set(T))==3 and all(0<=i<h for i in T),'Invalid triple')
    return [[Q((3*int(j in T)-1)*int(i in T),6) for j in range(h)] for i in range(h)]


def private_path_bound(h):
    require(h>=3,'Need a triple line')
    return dict(start_rank=1,end_rank=h-1,endpoint_difference_rank=h,
                minimum_excess_over_signed_rank_change=2,
                scope='Any internal rational matrices on an edge path between the retained line and orthogonal-complement frames')


def local_exclusion_identity(n):
    """Total + two stars + private input, over F2, for every omitted pair."""
    require(n>=4,'Need at least four points')
    pairs=list(combinations(range(n),2))
    total=(1<<len(pairs))-1
    stars=[sum(1<<j for j,p in enumerate(pairs) if i in p) for i in range(n)]
    for j,(a,b) in enumerate(pairs):
        out=total^stars[a]^stars[b]^(1<<j)
        expected=sum(1<<k for k,p in enumerate(pairs) if a not in p and b not in p)
        require(out==expected,'Local cancellation formula failed')
    return dict(n=n,outputs=len(pairs),private_diagonal_terms=len(pairs),exact=True)


def eulerian_pairs(n):
    """Cyclic order of all pairs with consecutive pairs sharing one point."""
    require(n>=3 and n%2==1,'Complete graph needs even vertex degrees')
    neighbors=[set(range(n))-{i} for i in range(n)]
    stack=[0];tour=[]
    while stack:
        u=stack[-1]
        if neighbors[u]:
            v=min(neighbors[u]);neighbors[u].remove(v);neighbors[v].remove(u);stack.append(v)
        else:tour.append(stack.pop())
    tour.reverse()
    pairs=[tuple(sorted((a,b))) for a,b in zip(tour,tour[1:])]
    require(len(pairs)==comb(n,2) and len(set(pairs))==len(pairs),'Not an Euler circuit')
    require(all(len(set(pairs[j])&set(pairs[(j+1)%len(pairs)]))==1
                for j in range(len(pairs))),'Nonincident consecutive pairs')
    return pairs


def leave_one_out_control(h):
    """An alternative with no explicit self term still has a bad path packing.

    Prefix/suffix circuits compute each point sum with its own target removed.
    Euler orders give nonorthogonal cyclic source-target paths. A matching
    selects one per global source and target, permitting shared input roots.
    """
    require(h>=6 and h%2==0,'Use the even-h family')
    triples=list(combinations(range(h),3));index={T:i for i,T in enumerate(triples)}
    v=len(triples);n=h-1;order=eulerian_pairs(n);m=len(order)
    outputs=[0]*v;choices=[[] for _ in triples]
    for common in range(h):
        points=[i for i in range(h) if i!=common]
        ids=[index[tuple(sorted((common,points[a],points[b])))] for a,b in order]
        prefix=[1<<ids[0]]
        for k in range(1,m-1):prefix.append(prefix[-1]^(1<<ids[k]))
        suffix={m-1:1<<ids[-1]}
        for k in range(m-2,0,-1):suffix[k]=(1<<ids[k])^suffix[k+1]
        for j,t in enumerate(ids):
            value=suffix[1] if j==0 else prefix[m-2] if j==m-1 else prefix[j-1]^suffix[j+1]
            require(not value>>t&1,'Own input was not excluded')
            outputs[t]^=value
        for k,s in enumerate(ids):
            j=(k+1)%m;t=ids[j]
            path=[('copy',s),('input',s)]
            if k==m-1:
                path += [(common,'suffix',l) for l in range(m-2,0,-1)]
            else:
                if k:path.append((common,'prefix',k))
                if j<m-1:path.append((common,'output',j))
            path.append(('inject',t))
            require(len(set(triples[s])&set(triples[t]))==2,'Path endpoints are orthogonal')
            choices[s].append((t,path))
    incoming=[0]*v
    for edges in choices:
        require(len(edges)==3,'Wrong outgoing degree')
        for target,_ in edges:incoming[target]+=1
    require(all(x==3 for x in incoming),'Wrong incoming degree')
    matched={}
    def augment(source,seen):
        for target,path in choices[source]:
            if target in seen:continue
            seen.add(target)
            if target not in matched or augment(matched[target][0],seen):
                matched[target]=(source,path);return True
        return False
    require(all(augment(s,set()) for s in range(v)),'Regular bipartite matching failed')
    used=set()
    for source,path in matched.values():
        edges=set(zip(path,path[1:]))
        require(not used&edges,'Selected paths share an edge')
        used|=edges
    for t,T in enumerate(triples):
        expected=sum(1<<s for s,S in enumerate(triples) if len(set(S)&set(T))==1)
        require(outputs[t]==expected,'Wrong leave-one-out side map')
    return dict(h=h,inputs=v,outputs=3*v,additions=h*(3*m-6),
                side_roles=h*(4*m-6),matched_nonorthogonal_paths=v,
                edge_disjoint=True,exact_neighbor_map=True,no_explicit_self_term=True)


def certificate():
    small=[]
    for h in (6,7,8,10):
        c=PointCancellation(h)
        row=c.verify();code=c.compile()
        require(code['roles']==row['side_roles'],'Compile/identity mismatch')
        small.append(row)
    n=candidate_counts(50)
    # If the original centers and both forward stages are retained, replacing
    # r targets by private-diagonal cancellation incurs at least 4*v^2*r.
    budget=Q(n['old_deficit'],4*n['v']**2)
    return dict(status='CANCELLATION SCREEN: SMALLER SCALAR CIRCUIT, FAILED RANK BUDGET; NO NEW KAPPA',
                upstream_commit=verify_sources(),scalar_controls=small,
                full_size_candidate=n,published_side_roles=509194,
                apparent_role_reduction=Q(509194,n['side_roles']),
                path_bound=private_path_bound(50),
                local_exclusion_controls=[local_exclusion_identity(i) for i in (5,7,9)],
                leave_one_out_controls=[leave_one_out_control(h) for h in (6,8,10)],
                leave_one_out_h50=dict(side_roles=12*n['v']-6*50,
                    additions=9*n['v']-6*50,nonorthogonal_paths_per_invocation=n['v'],
                    deficit_upper_bound=0,
                    status='Also rejected for this Euler-ordered prefix/suffix topology with retained copy/injection frames'),
                partial_replacement=dict(strict_upper_limit_on_targets_per_invocation=budget,
                    maximum_integer_targets=(budget.numerator-1)//budget.denominator,
                    assumptions='Original central returns and two forward stages retained; only their disjoint private-path penalties charged'),
                scope='Rejects the explicit private-diagonal and Euler-ordered leave-one-out topologies under canonical copy/injection frames, even with arbitrary rational internal frames. Not a lower bound on all cancellation circuits or new stage frames.',
                next_step='Screen edge-disjoint paths between nonorthogonal source-target labels, not just self paths. A new cancellation circuit must reduce that path packing or change data-stage frames before scalar savings can help.')


if __name__=='__main__':
    (ROOT/'certificates/cancellation-audit.json').write_text(
        json.dumps(serializable(certificate()),indent=2,sort_keys=True)+'\n')
    print('PASS scalar cancellation and nonorthogonal-path audit; candidates rejected, no new kappa.')
