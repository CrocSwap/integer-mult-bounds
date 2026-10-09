from pathlib import Path
from hashlib import sha256
import json

def det(A):
    A=[list(r) for r in A];n=len(A)
    if not n:return 1
    sign=1;previous=1
    for k in range(n-1):
        pivot=next((i for i in range(k,n) if A[i][k]),None)
        if pivot is None:return 0
        if pivot!=k:A[k],A[pivot]=A[pivot],A[k];sign=-sign
        p=A[k][k]
        for i in range(k+1,n):
            for j in range(k+1,n):
                v=A[i][j]*p-A[i][k]*A[k][j]
                assert v%previous==0
                A[i][j]=v//previous
            A[i][k]=0
        previous=p
    return sign*A[-1][-1]

def certificate(path):
    plan=json.loads(path.read_text());assert type(plan['p']) is int and plan['p']==12
    h=2*plan['p'];groups={};previous=-1
    for i,B in plan['frames']:
        assert type(i) is int and i>previous
        previous=i
        assert B and all(len(r)==h and all(type(x)is int for x in r) for r in B)
        key=json.dumps(B,separators=(',',':'));groups.setdefault(key,[]).append(i)
    records=[]
    for key,ops in sorted(groups.items()):
        B=json.loads(key);s=list(map(sum,B))
        gram=[[9*sum(a*b for a,b in zip(x,y))-s[i]*s[j] for j,y in enumerate(B)] for i,x in enumerate(B)]
        determinant=det(gram);assert determinant
        residual=abs(determinant);powers={}
        for p in (2,3,5,7,11,13,17,19,23,29,31):
            while residual%p==0:powers[p]=powers.get(p,0)+1;residual//=p
        assert residual<2**80
        records.append(dict(basis_sha256=sha256(key.encode()).hexdigest(),operation_indices=ops,
            dimension=len(B),cleared_gram_determinant=determinant,gram_denominator_power_of_9=len(B),
            small_prime_powers=powers,residual=residual))
    return dict(status='PASS exact determinant factors below retained prime lower bound',h=h,
        plan_sha256=sha256(path.read_bytes()).hexdigest(),mandatory_small_prime_exclusions=[2,3],
        frame_witnesses=records,unique_new_bases=len(records),total_operation_frames=len(plan['frames']),
        maximum_determinant_bits=max(abs(z['cleared_gram_determinant']).bit_length() for z in records),
        maximum_residual_bits=max(z['residual'].bit_length() for z in records),
        rule='All displayed small primes and every prime divisor of the positive residual are below 2^80. Thus every retained q>2^80 avoids the new determinants. The source exclusions for unchanged frames remain in force.')
