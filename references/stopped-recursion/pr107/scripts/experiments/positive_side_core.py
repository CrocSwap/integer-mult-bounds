"""Cancellation-free side DAGs for positive-definite two-field bit cores.

Discovery strategies are bounded heuristics, not circuit lower bounds.
The explicit three-stage compiler checks all roles and every frame edge.
"""
from collections import Counter
from itertools import combinations,product as cartesian

from audit_joint_frames import eye,zero,matrix,row_basis,product,inverse,add,sub,scale,rank
from certify import require
from exclusion_circuit import ExclusionCircuit
from experiments.rank_product_core import check_core,counts,tensor
from experiments.shared_core import shared_counts,check_matching


class PositiveSide(ExclusionCircuit):
    def __init__(self, rows, vectors, strategy='balanced', maximum_labels=300):
        n=len(rows)
        require(2<=n<=maximum_labels,'Side DAG expansion budget exceeded')
        require(strategy in ('balanced','frequent-pairs'),'Unknown side strategy')
        self.core=check_core(rows,vectors,eye(len(vectors[0])))
        self.vectors=matrix(vectors);self.strategy=strategy
        self.inputs=list(range(n));self.support=[0]+[1<<i for i in range(n)]
        self.args=[None]*(n+1);self.lookup={s:i for i,s in enumerate(self.support)}
        self.variables={i:i+1 for i in range(n)}
        pending=[set(j+1 for j in range(n) if i!=j and row>>j&1)
                 for i,row in enumerate(rows)]
        require(all(pending),'This adapter requires nonempty side outputs')
        if strategy=='frequent-pairs':
            while True:
                freq=Counter(pair for row in pending for pair in combinations(sorted(row),2))
                if not freq:break
                pair,count=max(freq.items(),key=lambda kv:(kv[1],-kv[0][0],-kv[0][1]))
                if count<2:break
                a,b=pair;node=self.add(a,b)
                for row in pending:
                    if a in row and b in row:row.difference_update(pair);row.add(node)
        self.outputs={i:self.total(sorted(row)) for i,row in enumerate(pending)}
        self.active=set();todo=list(self.outputs.values())
        while todo:
            node=todo.pop()
            if node in self.active:continue
            self.active.add(node)
            if self.args[node]:todo.extend(self.args[node])
        self.additions=sum(self.args[node] is not None for node in self.active)
        self.rows=list(rows)

    def verify(self):
        for node in sorted(self.active):
            if self.args[node]:
                a,b=self.args[node]
                require(a<node and b<node and not self.support[a]&self.support[b],
                        'Not a disjoint acyclic addition')
                require(self.support[node]==self.support[a]|self.support[b],'Wrong node support')
        for i,node in self.outputs.items():
            require(self.support[node]==self.rows[i]^(1<<i),'Wrong side coefficient row')
        code=self.compile();values=[0]*code['roles']
        for i,slot in code['sources'].items():values[slot]=1<<i
        for node,ins,outs in code['gates']:
            for slot in ins[1:]:values[ins[0]]^=values[slot]
            for slot in outs[1:]:values[slot]^=values[ins[0]]
        require(all(values[slot]==self.support[self.outputs[i]] for i,slot in code['outputs'].items()),
                'Compiled side product is wrong')
        return dict(n=len(self.inputs),d=self.core['d'],strategy=self.strategy,
                    additions=self.additions,side_roles=code['roles'],
                    all_integer_coefficients_and_zero_entries_verified=True)

    def frame_labels(self):
        """Ordinary rational projections onto all ancestor-source spans."""
        h=self.core['d'];spans={};labels={}
        for node in sorted(self.active):
            if self.args[node]:
                a,b=self.args[node];spans[node]=row_basis(spans[a]+spans[b])
            else:spans[node]=(self.vectors[node-1],)
            U=spans[node];Ut=matrix(zip(*U))
            P=product(product(Ut,inverse(product(U,Ut))),U)
            require(product(P,P)==P,'Non-idempotent source-span projection')
            labels[node]=P
        return labels

    def verify_frames(self):
        code=self.compile();E=self.frame_labels();d=self.core['d'];I=eye(d);Z=zero(d)
        P=self.core['projections'];checked=set();incidences=0
        def transition(A,B):
            nonlocal incidences
            incidences+=1
            if (A,B) in checked:return
            require(product(A,B)==A and product(B,A)==A,'Decreasing side frame')
            require(rank(sub(B,A))==rank(B)-rank(A),'Nonmonotone rank charge')
            checked.add((A,B))
        for reverse in (False,True):
            labels=[Z]*code['roles']
            starts=code['outputs'] if reverse else code['sources']
            ends=code['sources'] if reverse else code['outputs']
            for t,slot in starts.items():transition(labels[slot],P[t]);labels[slot]=P[t]
            sequence=reversed(code['gates']) if reverse else code['gates']
            for node,ins,outs in sequence:
                F=sub(I,E[node]) if reverse else E[node]
                for slot in set(ins+outs):transition(labels[slot],F);labels[slot]=F
            for t,slot in ends.items():
                F=sub(I,P[t]);transition(labels[slot],F);labels[slot]=F
            for F in labels:transition(F,I)
        return dict(orientations=2,physical_transitions_checked=incidences,
                    distinct_transitions=len(checked),all_side_rank_changes_monotone=True)

    def verify_invocation(self):
        """Every independent data/side/center input, in both scalar directions."""
        code=self.compile();n=self.core['n'];S=code['roles'];r=self.core['r']
        W=2*n+S+r
        def L(inverse_order=False):
            out=[]
            for _,ins,outs in code['gates']:
                out += [(2*n+ins[0],2*n+s) for s in ins[1:]]
                out += [(2*n+t,2*n+ins[0]) for t in outs[1:]]
            return list(reversed(out)) if inverse_order else out
        V=[(2*n+s,t) for t,s in code['sources'].items()]
        J=[(n+t,2*n+s) for t,s in code['outputs'].items()]
        G=[(2*n+S+k,t) for k,mask in enumerate(self.core['V']) for t in range(n) if mask>>t&1]
        R=[(n+t,2*n+S+k) for t,mask in enumerate(self.core['U']) for k in range(r) if mask>>k&1]
        operations=[L(),J,L(True),R,V,G,R,L(),J,L(True),G,V]
        updates=[update for op in operations for update in op]
        expected=[(1<<t)^((1<<(t-n)) if n<=t<2*n else 0) for t in range(W)]
        for sequence in (updates,list(reversed(updates))):
            values=[1<<t for t in range(W)]
            for t,s in sequence:values[t]^=values[s]
            require(values==expected,'Dirty-input invocation failed')
        return dict(independent_roles=W,scalar_xors=len(updates),
                    forward_and_inverse_shear_verified=True,all_auxiliary_inputs_restored=True)


def compile_positive_side(circuit,matching=None,maximum_roles=1000):
    """Complete transparent twelve-operation circuit, including stage sharing."""
    circuit.verify();core=circuit.core;n,r,d=core['n'],core['r'],core['d']
    code=circuit.compile();S=code['roles'];P=core['projections'];E=circuit.frame_labels()
    shared=matching is not None
    if shared:check_matching(core,matching)
    expected=shared_counts(n,r,d,S) if shared else counts(n,r,d,S)
    require(expected['W']<=maximum_roles,'Full positive-side expansion exceeds budget')
    W=expected['W'];m=d**3;N=n**3;bank=S+r
    coords=list(cartesian(range(n),repeat=3));index={a:i for i,a in enumerate(coords)}
    I,Z=eye(m),zero(m)
    lines=[tensor(P[t] for t in a) for a in coords]
    sources=[scale(M,-1) for M in lines]+[Z]*(W-N)
    sinks=[I]*N+[sub(I,M) for M in lines]+[I]*(W-2*N)
    gates=[]
    for stage in range(3):
        for fixed in cartesian(range(n),repeat=2):
            coords0=list(fixed);coords0.insert(stage,0)
            X=[];Y=[]
            for t in range(n):
                coords0[stage]=t;X.append(index[tuple(coords0)]);Y.append(N+index[tuple(coords0)])
            source,target=(Y,X) if stage==1 else (X,Y)
            invocation=stage*n*n+fixed[0]*n+fixed[1]
            if shared and stage==2:
                # stage-one (a,b) joins stage-three (b,pi(a)).
                a=matching.index(fixed[1]);invocation=a*n+fixed[0]
            offset=2*N+invocation*bank
            side=list(range(offset,offset+S));centers=list(range(offset+S,offset+bank))
            prior=tensor(P[coords0[j]] for j in range(stage))
            B=sub(eye(d**stage),prior)
            future=tensor(P[coords0[j]] for j in range(stage+1,3))
            low=tensor([B,eye(d)]);high=eye(d**(stage+1))
            def lift(F):return tensor([add(low,tensor([prior,F])),future])
            D0=tensor([low,future]);D1=tensor([high,future])
            forward=('L','J','l','R','V','G','R','L','J','l','G','V')
            operations=tuple(reversed(forward)) if stage==1 else forward
            # Inverting L swaps its forward/reverse scalar order.
            if stage==1:operations=tuple('l' if op=='L' else 'L' if op=='l' else op for op in operations)
            labels=('0','0','0','X','u','1','0','Y','1','1','1','1') if stage==1 else (
                   '0','0','0','0','X','1','0','u','Y','1','1','1')
            for op,label in zip(operations,labels):
                if op in ('L','l'):
                    sequence=code['gates'] if op=='L' else reversed(code['gates'])
                    for node,ins,outs in sequence:
                        updates=[(ins[0],slot) for slot in ins[1:]]+[(slot,ins[0]) for slot in outs[1:]]
                        if op=='l':updates=list(reversed(updates))
                        F=D0 if label=='0' else D1 if label=='1' else lift(sub(eye(d),E[node]) if stage==1 else E[node])
                        gates.append(dict(roles=sorted({side[i] for i in ins+outs}),
                            xors=[[side[t],side[s]] for t,s in updates],frame=F))
                elif op in ('V','J'):
                    ports=code['sources'] if op=='V' else code['outputs']
                    data=source if op=='V' else target
                    for t in range(n):
                        if t not in ports:continue
                        slot=side[ports[t]]
                        F=D0 if label=='0' else D1 if label=='1' else lift(P[t] if label=='X' else sub(eye(d),P[t]))
                        gates.append(dict(roles=[data[t],slot],
                            xors=[[slot,data[t]]] if op=='V' else [[data[t],slot]],frame=F))
                else:
                    if op=='G':
                        ports=source+centers
                        updates=[[centers[k],source[t]] for k,mask in enumerate(core['V'])
                                 for t in range(n) if mask>>t&1]
                    else:
                        ports=target+centers
                        updates=[[target[t],centers[k]] for t,mask in enumerate(core['U'])
                                 for k in range(r) if mask>>k&1]
                    require(label in ('0','1'),'Central gate has an unexpected label')
                    if stage==1:updates=list(reversed(updates))
                    gates.append(dict(roles=ports,xors=updates,frame=D0 if label=='0' else D1))
    rho=list(range(N,2*N))+list(range(N))+list(range(2*N,W))
    return dict(W=W,m=m,rho=rho,gates=gates,source_frames=sources,sink_frames=sinks),expected
