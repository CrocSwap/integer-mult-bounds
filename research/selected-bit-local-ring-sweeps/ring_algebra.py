"""Exact local-ring checks for the selected dyadic frame identities."""
from math import gcd


def need(condition,message):
    if not condition:raise ValueError(message)


def eye(n):return [[int(i==j) for j in range(n)] for i in range(n)]
def transpose(a):return [list(row) for row in zip(*a)]


def multiply(a,b,modulus):
    out=[[0]*len(b[0]) for _ in a]
    for i,row in enumerate(a):
        for k,x in enumerate(row):
            if x:
                for j,y in enumerate(b[k]):
                    if y:out[i][j]=(out[i][j]+x*y)%modulus
    return out


def difference(a,b,modulus):
    return [[(x-y)%modulus for x,y in zip(row,other)] for row,other in zip(a,b)]


def reduce_matrix(a,modulus):
    return [[x.numerator*pow(x.denominator,-1,modulus)%modulus for x in row] for row in a]


def inverse(a,q,modulus):
    n=len(a);rows=[list(row)+unit for row,unit in zip(a,eye(n))]
    for j in range(n):
        pivot=next((i for i in range(j,n) if gcd(rows[i][j],q)==1),None)
        need(pivot is not None,"unit matrix pivot")
        rows[j],rows[pivot]=rows[pivot],rows[j]
        unit=pow(rows[j][j],-1,modulus)
        rows[j]=[x*unit%modulus for x in rows[j]]
        for i in range(n):
            if i!=j and rows[i][j]:
                c=rows[i][j];rows[i]=[(x-c*y)%modulus for x,y in zip(rows[i],rows[j])]
    need([row[:n] for row in rows]==eye(n),"inverse endpoint")
    return [row[n:] for row in rows]


def independent_columns(a,q):
    rows=[[x%q for x in row] for row in a];rank=0;columns=[]
    for j in range(len(rows[0])):
        pivot=next((i for i in range(rank,len(rows)) if rows[i][j]),None)
        if pivot is None:continue
        rows[rank],rows[pivot]=rows[pivot],rows[rank]
        u=pow(rows[rank][j],-1,q)
        rows[rank]=[x*u%q for x in rows[rank]]
        for i in range(len(rows)):
            if i!=rank and rows[i][j]:
                c=rows[i][j];rows[i]=[(x-c*y)%q for x,y in zip(rows[i],rows[rank])]
        columns.append(j);rank+=1
        if rank==len(rows):break
    return columns


def split_basis(p,rank,q,modulus):
    """Lift an image/kernel basis from F_q using the actual ring columns."""
    n=len(p);complement=difference(eye(n),p,modulus)
    image=independent_columns(p,q);kernel=independent_columns(complement,q)
    need(len(image)==rank and len(kernel)==n-rank,"specialized rank")
    basis=[[p[i][j] for j in image]+[complement[i][j] for j in kernel] for i in range(n)]
    inv=inverse(basis,q,modulus)
    diagonal=[[int(i==j and i<rank) for j in range(n)] for i in range(n)]
    need(multiply(p,p,modulus)==p,"ring idempotent")
    need(multiply(multiply(basis,diagonal,modulus),inv,modulus)==p,"exact split-rank basis")
    return image,kernel,basis


def weighted_swap(p,weights,modulus,reverse_tail=True):
    """Address matrix Q_A D_C(P) Q_A^-1, with a fixed tail convention."""
    n=len(p);out=[[0]*(2*n) for _ in range(2*n)]
    need(len(weights)==n and all(gcd(a,modulus)==1 for a in weights),"unit weights")
    ai=[pow(a,-1,modulus) for a in weights]
    tail=lambda i:n+(n-1-i if reverse_tail else i)
    for i in range(n):
        for j in range(n):
            out[i][j]=weights[i]*(int(i==j)-p[i][j])*ai[j]%modulus
            out[i][tail(j)]=weights[i]*p[i][j]%modulus
            out[tail(i)][j]=p[i][j]*ai[j]%modulus
            out[tail(i)][tail(j)]=(int(i==j)-p[i][j])%modulus
    return out


def chart(n,q,width,high=True):
    modulus=q**width;g=eye(n)
    g[1][2]=q if high else 1
    if n>8:g[0][n-1]=1+q
    return g,inverse(g,q,modulus)


def conjugate(p,g,gi,modulus):
    return multiply(multiply(g,p,modulus),gi,modulus)


def lifted_stage(p,stage,n=64,reverse=False):
    out=[[0]*n for _ in range(n)]
    for i in range(8):
        for j in range(8):out[i][j]=(int(i==j)-p[i][j]) if reverse else p[i][j]
    for i in range(8,8+7*stage):out[i][i]=1
    return out


def ring_certificate(projectors,dims,programs,word):
    residuals={};pairs=set()
    for orientation,events in programs.items():
        rev=orientation=="reverse"
        for event in events:
            if event[0] not in (0,2):continue
            a,b=(event[2],event[3]) if event[0]==0 else (event[3],event[4])
            rank=event[4] if event[0]==0 else event[5]
            lo,hi=(a,b) if dims[a]<=dims[b] else (b,a)
            p=tuple(tuple(x-y for x,y in zip(r,s)) for r,s in zip(projectors[hi],projectors[lo]))
            need(all(x.denominator&(x.denominator-1)==0 for row in p for x in row),"dyadic residual")
            need(sum(p[i][i] for i in range(8))==rank,"exact rational residual rank")
            residuals[p]=rank;pairs.add((rev,a,b,p))
    tests=list(zip(projectors,dims))+list(residuals.items())
    ring_cases=0;rank_divisible_by_prime=0;basis_digest=[]
    for q,width in ((3,2),(5,2),(7,2),(3,3)):
        modulus=q**width
        for rational,rank in tests:
            p=reduce_matrix(rational,modulus)
            image,kernel,_=split_basis(p,rank,q,modulus)
            basis_digest.append([q,width,rank,image,kernel])
            ring_cases+=1;rank_divisible_by_prime+=int(rank>0 and rank%q==0)
    transports=0
    for q,width,high in ((3,2,True),(5,2,False),(3,3,True)):
        modulus=q**width;g,gi=chart(8,q,width,high)
        weights=[(1+i%(q-1)+q*(i+1))%modulus for i in range(8)]
        labels={}
        for rev,a,b,residual in pairs:
            for f in (a,b):
                if (rev,f) not in labels:
                    p=reduce_matrix(projectors[f],modulus)
                    if rev:p=difference(eye(8),p,modulus)
                    labels[rev,f]=weighted_swap(conjugate(p,g,gi,modulus),weights,modulus)
            r=conjugate(reduce_matrix(residual,modulus),g,gi,modulus)
            need(multiply(labels[rev,a],labels[rev,b],modulus)==weighted_swap(r,weights,modulus),"weighted ring MOVE/COPY transport")
            transports+=1
    # A high-only departure from O: a transpose shortcut passes modulo3.
    q,modulus=3,9;g,gi=chart(8,q,2,True)
    p=reduce_matrix(projectors[word["start"][8]],modulus)
    good=conjugate(p,g,gi,modulus);bad=conjugate(p,g,transpose(g),modulus)
    defect=difference(multiply(bad,bad,modulus),bad,modulus)
    need(multiply(good,good,modulus)==good,"GL inverse conjugation")
    need(all((x-y)%q==0 for r,s in zip(good,bad) for x,y in zip(r,s)),"same low projector")
    need((good[1][1],bad[1][1],defect[1][1])==(1,4,6),"zero-based transpose witness")
    bad_swap=weighted_swap(bad,[1]*8,modulus)
    need(difference(multiply(bad_swap,bad_swap,modulus),eye(16),modulus)[1][1]==3,"bad involution control")
    # Reorthogonalizing also fails, even when each replacement is an idempotent.
    root=word["lines"][word["frames"][word["start"][8]][0]]
    need(root==[0,1,1,0,1,0,0,1],"selected port-eight line")
    u=[row[0] for row in multiply(g,[[x] for x in root],modulus)]
    v=[row[0] for row in multiply(transpose(gi),[[x] for x in root],modulus)]
    def orthogonal_line(vector):
        norm=sum(x*x for x in vector)%modulus
        return [[x*y*pow(norm,-1,modulus)%modulus for y in vector] for x in vector]
    wrong_p=orthogonal_line(u)
    wrong_q=difference(eye(8),orthogonal_line(v),modulus)
    split_basis(wrong_p,1,q,modulus);split_basis(wrong_q,7,q,modulus)
    for candidate,reference in ((wrong_p,good),(wrong_q,difference(eye(8),good,modulus))):
        need(all((x-y)%q==0 for a,b in zip(candidate,reference) for x,y in zip(a,b)),"reorthogonalized low agreement")
        action=weighted_swap(candidate,[1]*8,modulus)
        need(multiply(action,action,modulus)==eye(16),"reorthogonalized individual involution")
    wrong_endpoint=multiply(weighted_swap(wrong_p,[1]*8,modulus),weighted_swap(wrong_q,[1]*8,modulus),modulus)
    endpoint_defect=difference(wrong_endpoint,weighted_swap(eye(8),[1]*8,modulus),modulus)
    need((endpoint_defect[1][4],endpoint_defect[4][1])==(6,3),"reorthogonalization loses complementary kernels")
    # Actual ambient dimension, stage padding and a chart mixing local/exterior axes.
    ambient=0
    for q,width in ((3,2),(5,2)):
        modulus=q**width;g,gi=chart(64,q,width)
        weights=[(1+i%(q-1)+q*(i+1))%modulus for i in range(64)]
        for stage in (0,3,8):
            for rev in (False,True):
                a=reduce_matrix(lifted_stage(projectors[510],stage,reverse=rev),modulus)
                b=reduce_matrix(lifted_stage(projectors[0],stage,reverse=rev),modulus)
                r=reduce_matrix(lifted_stage(projectors[510],0),modulus)
                aa=weighted_swap(conjugate(a,g,gi,modulus),weights,modulus)
                bb=weighted_swap(conjugate(b,g,gi,modulus),weights,modulus)
                rr=weighted_swap(conjugate(r,g,gi,modulus),weights,modulus)
                need(multiply(aa,bb,modulus)==rr,"ambient weighted rank-seven COPY")
                ambient+=1
    return {"frames":len(projectors),"distinct_nested_residuals":len(residuals),
            "split_basis_cases":ring_cases,"rank_divisible_by_prime_cases":rank_divisible_by_prime,
            "weighted_transport_cases":transports,"ambient_COPY_cases":ambient,
            "transpose_shortcut_control":{"status":"REJECT","q":3,"width":2,"entry":[1,1],
                "good":1,"bad":4,"idempotence_defect":6,"involution_defect":3},
            "reorthogonalization_control":{"status":"REJECT","q":3,"width":2,
                "individual_ranks":[1,7],"individual_involutions":True,"same_low_projectors":True,
                "endpoint_defect_entries":[[1,4,6],[4,1,3]]},
            "basis_choices":basis_digest}
