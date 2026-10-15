"""Aligned common-pair sum sharing for the F3 five-subset bit network.

Large construction is stored as integer DAG arrays; small controls additionally
reconstruct every full formal support and every partial output coefficient.
"""
from array import array
from collections import Counter
from hashlib import sha256
from itertools import combinations
from math import comb
from fractions import Fraction as Q
from types import SimpleNamespace
import sys

from certify import require
from exclusion_circuit import ExclusionCircuit
from experiments.disjoint_tensor import DisjointTensor
from experiments.shared_core import shared_counts


def canonical_hash(*arrays):
    h=sha256()
    for a in arrays:
        if a.itemsize>1 and sys.byteorder!='little':
            a=array(a.typecode,a);a.byteswap()
        h.update(a.tobytes())
    return h.hexdigest()


def build(h,retain_graph=False,progress=None):
    require(type(h) is int and 8<=h<=30,'Audited construction budget: h=8,...,30')
    require(not retain_graph or h<=10,'Full-support control budget exceeded')
    c=DisjointTensor(h);local=c.verify();v=comb(h,5)
    triples=c.inputs;pairs=list(combinations(range(h),2))
    pair_index={sum(1<<p for p in t):i for i,t in enumerate(pairs)}
    width=len(pairs);labels=[sum(1<<p for p in t) for t in combinations(range(h),5)]
    input_id={t:i+1 for i,t in enumerate(labels)}
    left=array('I',[0])*(v+1);right=array('I',[0])*(v+1)
    require(left.itemsize==4,'DAG encoding requires 32-bit unsigned arrays')
    roots=array('I');targets=array('I');table={};nodes=sorted(c.active)
    exact=[0]+[1<<i for i in range(v)] if retain_graph else None
    common=[0]+labels[:] if retain_graph else None
    def allocate(a,b):
        require(0<a<len(left) and 0<b<len(left) and a!=b,'Invalid DAG dependencies')
        y=len(left);require(y<2**32,'DAG index overflow')
        left.append(a);right.append(b)
        if exact is not None:
            require(not exact[a]&exact[b],'Formal supports overlap')
            exact.append(exact[a]|exact[b]);common.append(common[a]&common[b])
            require(common[-1].bit_count()>=2,'A new sum lost its common pair')
        return y
    for group,J in enumerate(pairs):
        fixed=sum(1<<p for p in J)
        good=sum(1<<i for i,t in enumerate(triples) if not t&fixed)
        image=[0]*len(c.args);inter=[0]*len(c.args);union=[0]*len(c.args);within={}
        for i,t in enumerate(triples):
            if not t&fixed:image[i+1]=input_id[fixed|t];inter[i+1]=union[i+1]=t
        for x in nodes:
            if not c.args[x]:continue
            u,w=c.args[x];a,b=image[u],image[w]
            if not a or not b:
                image[x]=a or b;inter[x]=inter[u] if a else inter[w]
                union[x]=union[u] if a else union[w];continue
            I=inter[u]&inter[w];U=union[u]|union[w]
            inter[x]=I;union[x]=U;support=c.support[x]&good
            require(I.bit_count()<=2,'Two distinct triples cannot share three points')
            if not I:
                y=within.get(support)
                if y is None:y=allocate(a,b);within[support]=y
            else:
                if I.bit_count()==1:
                    mask=0;bits=support
                    while bits:
                        bit=bits&-bits;bits^=bit
                        mask|=1<<pair_index[triples[bit.bit_length()-1]^I]
                else:mask=U^I
                key=((fixed|I)<<width)|mask;y=table.get(key)
                if y is None:y=allocate(a,b);table[key]=y
            if exact is not None:
                require(not exact[a]&exact[b] and exact[y]==exact[a]|exact[b],
                        'An interned signature identified unequal formal sums')
            image[x]=y
        for T,x in c.outputs.items():
            if T&fixed:continue
            y=image[x];target=T|fixed
            require(y!=0,'Empty partial output')
            roots.append(y);targets.append(input_id[target]-1)
            if exact is not None:
                expected=sum(1<<i for i,S in enumerate(labels) if S&target==fixed and S&fixed==fixed)
                require(exact[y]==expected,'Wrong complete partial coefficient row')
        if progress and group%40==0:progress(group,len(left),len(table))
    require(len(roots)==10*v,'Missing common-pair partial outputs')
    active=bytearray(len(left))
    for x in roots:active[x]=1
    count=0
    for x in range(len(left)-1,v,-1):
        if active[x]:count+=1;active[left[x]]=1;active[right[x]]=1
    require(sum(active[1:v+1])==v,'A data source disappeared')
    require(Counter(targets)=={i:10 for i in range(v)},'Wrong target multiplicities')
    S=count+len(roots);ledger=shared_counts(v,comb(h,2),h,S)
    result=dict(h=h,n=v,scalar_prime=3,central_factor_size=comb(h,2),local_template=local,
                allocated_additions=len(left)-v-1,active_additions=count,
                output_uses=len(roots),side_roles=S,sharing_entries=len(table),counts=ledger,
                edges_sha256=canonical_hash(left,right),roots_sha256=canonical_hash(roots),
                targets_sha256=canonical_hash(targets),active_sha256=sha256(active).hexdigest(),
                full_small_coefficient_maps_checked=retain_graph,
                exact_signature_controls_checked=retain_graph)
    if retain_graph:
        result['_graph']=dict(left=left,right=right,roots=roots,targets=targets,
                              active=active,labels=labels,exact_supports=exact,common=common)
    return result


def small_program(result):
    require('_graph' in result,'Need a retained small graph')
    g=result['_graph'];n=result['n']
    args=[None]*(n+1)+[(a,b) for a,b in zip(g['left'][n+1:],g['right'][n+1:])]
    adapter=SimpleNamespace(inputs=g['labels'],args=args,
        active={i for i,x in enumerate(g['active']) if x},
        outputs=dict(enumerate(g['roots'])),additions=result['active_additions'])
    code=ExclusionCircuit.compile(adapter)
    require(code['roles']==result['side_roles'],'Reversible role count failed')
    code.update(target_indices=list(g['targets']),labels=g['labels'],h=result['h'])
    return code


def f3add(A,B,coefficient=1):
    """Packed exact linear forms over F3; planes mark coefficients one and two."""
    a,b=A;c,d=B
    coefficient%=3
    if not coefficient:return A
    if coefficient==2:c,d=d,c
    return ((a&~(c|d))|(c&~(a|b))|(b&d),
            (b&~(c|d))|(d&~(a|b))|(a&c))


def verify_invocation(result):
    code=small_program(result);n=result['n'];h=result['h'];S=code['roles']
    labels=code['labels'];index={t:i for i,t in enumerate(labels)}
    pairs=[sum(1<<i for i in t) for t in combinations(range(h),2)];r=len(pairs)
    L=[]
    for node,ins,outs in code['gates']:
        L.extend((2*n+ins[0],2*n+s,1) for s in ins[1:])
        L.extend((2*n+t,2*n+ins[0],1) for t in outs[1:])
    Linv=[(t,s,-a) for t,s,a in reversed(L)]
    V=[(2*n+slot,index[t],1) for t,slot in code['sources'].items()]
    J=[(n+code['target_indices'][i],2*n+slot,-1) for i,slot in code['outputs'].items()]
    G=[(2*n+S+j,i,1) for j,p in enumerate(pairs) for i,t in enumerate(labels) if p&t==p]
    R=[(n+i,2*n+S+j,1) for j,p in enumerate(pairs) for i,t in enumerate(labels) if p&t==p]
    neg=lambda ops:[(t,s,-a) for t,s,a in reversed(ops)]
    sequence=L+neg(J)+Linv+neg(R)+V+G+R+L+J+Linv+neg(G)+neg(V)
    W=2*n+S+r
    for sign,ops in ((1,sequence),(-1,neg(sequence))):
        values=[(1<<i,0) for i in range(W)]
        for t,s,a in ops:values[t]=f3add(values[t],values[s],a)
        expected=[(1<<i,0) for i in range(W)]
        for i in range(n):expected[n+i]=f3add(expected[n+i],expected[i],sign)
        require(values==expected,'Ternary invocation failed on independent arbitrary inputs')
    return dict(h=h,independent_roles=W,side_roles=S,central_roles=r,
                scalar_operations=len(sequence),both_signed_directions_checked=True,
                every_auxiliary_input_restored=True)


def verify_invocation_frames(result):
    """Every physical rational edge of both signed invocation directions."""
    from audit_joint_frames import eye,zero,matrix,row_basis,product,inverse,sub,rank
    code=small_program(result);g=result['_graph'];n=result['n'];h=result['h']
    S=code['roles'];r=comb(h,2);W=2*n+S+r
    H=matrix([[Q(int(i==j))-Q(2,25) for j in range(h)] for i in range(h)])
    I,Z=eye(h),zero(h)
    require(rank(H)==h,'Degenerate ambient form')
    lines=[(tuple(Q(int(t>>i&1)) for i in range(h)),) for t in g['labels']]
    def projection(U):
        Ut=matrix(zip(*U));UH=product(U,H)
        P=product(product(Ut,inverse(product(UH,Ut))),UH)
        require(product(P,P)==P,'Non-idempotent frame')
        return P
    P=[projection(U) for U in lines];spans={};E={}
    for x,is_active in enumerate(g['active']):
        if not is_active:continue
        if x<=n:spans[x]=lines[x-1]
        else:spans[x]=row_basis(spans[g['left'][x]]+spans[g['right'][x]])
        require(g['common'][x].bit_count()>=2,'Missing common-pair positivity witness')
        E[x]=projection(spans[x])
    index={t:i for i,t in enumerate(g['labels'])}
    sources={index[t]:slot for t,slot in code['sources'].items()}
    outputs={i:[] for i in range(n)}
    for j,slot in code['outputs'].items():outputs[code['target_indices'][j]].append(slot)
    evidence=[]
    for reverse in (False,True):
        physical=P+[Z]*n+[Z]*(S+r);cost=lost=edges=0
        X=list(range(n));Y=list(range(n,2*n));source,target=(Y,X) if reverse else (X,Y)
        centers=list(range(2*n+S,W))
        def touch(ports,F):
            nonlocal cost,lost,edges
            for slot in set(ports):
                old=physical[slot];a=rank(sub(F,old));change=rank(F)-rank(old)
                require(a==abs(change),'A physical edge has a non-nested rank charge')
                cost+=a;lost+=max(0,-change);edges+=1;physical[slot]=F
        program=('L','J','l','R','V','G','R','L','J','l','G','V')
        frames=('0','0','0','0','X','1','0','u','Y','1','1','1')
        if reverse:
            program=tuple('l' if op=='L' else 'L' if op=='l' else op for op in reversed(program))
            frames=('0','0','0','X','u','1','0','Y','1','1','1','1')
        for op,label in zip(program,frames):
            if op in ('L','l'):
                sequence=code['gates'] if op=='L' else reversed(code['gates'])
                for node,ins,outs in sequence:
                    F=Z if label=='0' else I if label=='1' else sub(I,E[node]) if reverse else E[node]
                    touch([2*n+i for i in ins+outs],F)
            elif op in ('V','J'):
                for t in range(n):
                    slots=[sources[t]] if op=='V' else outputs[t]
                    data=source if op=='V' else target
                    F=Z if label=='0' else I if label=='1' else P[t] if label=='X' else sub(I,P[t])
                    touch([data[t]]+[2*n+s for s in slots],F)
            else:touch((source if op=='G' else target)+centers,Z if label=='0' else I)
        ends=[I]*n+[sub(I,p) for p in P]+[I]*(S+r)
        for slot,F in enumerate(ends):touch([slot],F)
        require(lost==r*h and cost==W*h-2*n+2*r*h,'Invocation rank ledger failed')
        evidence.append(dict(reverse=reverse,physical_edges=edges,rank_sum=cost,
                             decreasing_dimensions=lost,expected=W*h-2*n+2*r*h))
    return dict(h=h,ordinary_rational_frame_edges_checked=True,
                common_pair_source_spans_checked=True,orientations=evidence)
