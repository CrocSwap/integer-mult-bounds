"""Fixed-prime scalar circuits with rational rank frames.

The scalar alphabet and the prime used for rational address shears are
independent. Expanded controls verify arbitrary inputs over the scalar field.
"""
from itertools import product as cartesian
from math import isqrt

from audit_joint_frames import eye,sub,rank
from certify import require
from experiments.rank_product_core import check_core,_compile
from experiments.shared_core import compile_shared
from finite_bit_contract import physical_graph,rational_matrix


def prime_factor(C,p):
    require(type(p) is int and p>=2 and all(p%j for j in range(2,isqrt(p)+1)),
            'Need a prime scalar field')
    n=len(C)
    require(n>=2 and all(len(row)==n and all(type(x) is int and 0<=x<p for x in row)
                        for row in C),'Need an exact square field matrix')
    basis={}
    for row in C:
        row=list(row)
        for j,v in sorted(basis.items()):
            a=row[j];row=[(x-a*y)%p for x,y in zip(row,v)]
        j=next((i for i,x in enumerate(row) if x),None)
        if j is not None:
            a=pow(row[j],-1,p);basis[j]=[(a*x)%p for x in row]
    V=[v for j,v in sorted(basis.items())];U=[]
    for row in C:
        row=list(row);out=[]
        for j,v in sorted(basis.items()):
            a=row[j];out.append(a);row=[(x-a*y)%p for x,y in zip(row,v)]
        require(not any(row),'Prime factorization failed');U.append(out)
    return U,V


def compile_prime(C,p,vectors,form,matching=None,maximum_roles=1000):
    U,V=prime_factor(C,p);n=len(C);r=len(V)
    require(all(C[i][i]==1 for i in range(n)),'Central diagonal must be one')
    support=[sum(1<<j for j,x in enumerate(row) if x) for row in C]
    core=check_core(support,vectors,form)
    core.update(r=r,U=[sum(1<<j for j,x in enumerate(row) if x) for row in U],
                V=[sum(1<<j for j,x in enumerate(row) if x) for row in V])
    if matching is None:net,expected=_compile(core,maximum_roles)
    else:net,expected=compile_shared(core,matching,maximum_roles)
    S=len(core['side_edges']);bank=S+r;N=n**3
    index={a:i for i,a in enumerate(cartesian(range(n),repeat=3))}
    coefficients=[];cursor=0
    for stage in range(3):
        for fixed in cartesian(range(n),repeat=2):
            a=list(fixed);a.insert(stage,0);X=[];Y=[]
            for t in range(n):
                a[stage]=t;X.append(index[tuple(a)]);Y.append(N+index[tuple(a)])
            source,target=(Y,X) if stage==1 else (X,Y)
            source_index={x:i for i,x in enumerate(source)}
            target_index={x:i for i,x in enumerate(target)}
            invocation=stage*n*n+fixed[0]*n+fixed[1]
            if matching is not None and stage==2:
                invocation=matching.index(fixed[1])*n+fixed[0]
            offset=2*N+invocation*bank
            side={offset+i:pair for i,pair in enumerate(core['side_edges'])}
            center={offset+S+i:i for i in range(r)}
            program=[('J',-1,n),('R',-1,1),('V',1,n),('G',1,1),
                     ('R',1,1),('J',1,n),('G',-1,1),('V',-1,n)]
            if stage==1:program=[(op,-sign,count) for op,sign,count in reversed(program)]
            for op,sign,count in program:
                for _ in range(count):
                    gate=net['gates'][cursor];cursor+=1;weights=[]
                    for t,s in gate['xors']:
                        if op=='V':weight=1
                        elif op=='J':i,j=side[s];weight=-C[i][j]
                        elif op=='G':weight=V[center[t]][source_index[s]]
                        else:weight=U[target_index[t]][center[s]]
                        weights.append(sign*weight%p)
                    coefficients.append(weights)
    require(cursor==len(net['gates']),'Prime operation schedule mismatch')
    # The three signed shears give (-Y,X). Correct the bank sign at its
    # existing identity frame, adding no edge rank.
    net['gates'].append(dict(roles=list(range(N)),xors=[],frame=eye(net['m'])))
    coefficients.append([])
    net.update(scalar_prime=p,field_coefficients=coefficients,
               final_negated_roles=list(range(N)))
    return net,expected


def inspect_prime(net,require_deficit=True):
    p=net['scalar_prime'];W=net['W'];m=net['m'];gates=net['gates']
    require(len(net['field_coefficients'])==len(gates),'Missing scalar coefficients')
    values=[[int(i==j) for j in range(W)] for i in range(W)]
    for gate,weights in zip(gates,net['field_coefficients']):
        require(len(weights)==len(gate['xors']) and
                all(type(a) is int and 0<=a<p for a in weights),'Invalid field coefficients')
        for (t,s),a in zip(gate['xors'],weights):
            values[t]=[(x+a*y)%p for x,y in zip(values[t],values[s])]
    require(not gates[-1]['xors'] and set(net['final_negated_roles'])==set(gates[-1]['roles']),
            'Final sign correction must use exactly its listed ports')
    for t in net['final_negated_roles']:values[t]=[(-x)%p for x in values[t]]
    rho=net['rho']
    require(sorted(rho)==list(range(W)) and
            all(values[rho[i]]==[int(i==j) for j in range(W)] for i in range(W)),
            'Scalar action is not the declared all-role permutation')
    source=tuple(rational_matrix(M,m) for M in net['source_frames'])
    sink=tuple(rational_matrix(M,m) for M in net['sink_frames'])
    require(len(source)==len(sink)==W,'Missing terminal frames')
    require(all(sub(sink[rho[i]],source[i])==eye(m) for i in range(W)),
            'Prime scalar endpoint contract failed')
    internal=tuple(rational_matrix(g['frame'],m) for g in gates)
    frames=source+internal+sink;edges=physical_graph(W,gates)
    costs=[rank(sub(frames[v],frames[u])) for u,v,_ in edges];s=sum(costs)
    require(not require_deficit or s<W*m,'No strict prime-scalar deficit')
    return dict(scalar_prime=p,W=W,m=m,s=s,deficit=W*m-s,
                scalar_and_endpoints_verified=True,all_independent_field_inputs_checked=True,
                physical_edges=len(edges),edge_ranks=costs,strict_transfer_contract=s<W*m)
