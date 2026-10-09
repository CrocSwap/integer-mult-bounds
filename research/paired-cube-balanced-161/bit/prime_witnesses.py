"""Exact finite prime exclusions for the selected new rational bit frames.

For integer basis B and G=I-J/9, det(9 B G B^t) is a nonzero integer.
Excluding its prime divisors and 2,3 makes the reduced frame nondegenerate
over every odd local ring Z/q^w. Projector denominators divide this determinant
times fixed powers of 3. Retained frames retain their old exclusion witnesses.
The selected q is an arbitrarily large fixed prime chosen after this finite
set; this is not verification at a preselected numeric q.
"""
from pathlib import Path
import argparse,hashlib,json,sys

HERE=Path(__file__).resolve().parent

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

def certificate():
    plan=json.loads((HERE/'descent.json').read_text());p=plan['p'];h=2*p
    groups={}
    for i,B in plan['frames']:
        assert B and all(len(r)==h and all(type(x)is int for x in r) for r in B)
        key=json.dumps(B,separators=(',',':'));groups.setdefault(key,[]).append(i)
    records=[]
    for key,ops in sorted(groups.items()):
        B=json.loads(key);s=list(map(sum,B))
        gram=[[9*sum(a*b for a,b in zip(x,y))-s[i]*s[j]
               for j,y in enumerate(B)] for i,x in enumerate(B)]
        determinant=det(gram);assert 0<abs(determinant)<2**80
        records.append(dict(basis_sha256=hashlib.sha256(key.encode()).hexdigest(),
            operation_indices=ops,dimension=len(B),cleared_basis_denominator=1,
            cleared_gram_determinant=determinant,
            gram_denominator_power_of_9=len(B)))
    ambient=9**(h-1)*(9-h)
    assert 0<abs(ambient)<2**80
    record=dict(status='PASS exact nonzero finite prime-exclusion witnesses',
      h=h,source_commit='d14e29157bc905be1ced0776dd893d0714013f3a',
      plan_sha256=hashlib.sha256((HERE/'descent.json').read_bytes()).hexdigest(),
      script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
      mandatory_small_prime_exclusions=[2,3],ambient_cleared_gram_determinant=ambient,
      frame_witnesses=records,unique_new_bases=len(records),
      total_operation_frames=sum(len(z['operation_indices']) for z in records),
      maximum_determinant_bits=max(abs(z['cleared_gram_determinant']).bit_length() for z in records),
      all_new_witnesses_below_retained_prime_lower_bound=True,
      rule='Every q>2^80 avoids all new nonzero determinants; retain the source exclusions for unchanged frames.',
      scope='No new excluded prime exceeds the retained lower bound. Uniform split-rank and fallback arguments remain those of the retained local-ring interface.')
    return record

def main():
    assert not sys.flags.optimize
    ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args()
    record=certificate();target=HERE/'prime-witnesses.json'
    if args.write:target.write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
    else:assert record==json.loads(target.read_text()),'Exact prime witnesses changed'
    print(json.dumps({k:v for k,v in record.items() if k!='frame_witnesses'}))

if __name__=='__main__':main()
