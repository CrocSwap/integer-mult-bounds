"""Independent rational support costs and finite enumeration review."""
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path
from collections import Counter
import json,hashlib,tempfile,subprocess
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent;D=ROOT/'experiments/architecture/d4-insource'
def rational_rank(rows):
    A=[[Q(x) for x in row] for row in rows];rank=0
    if not A:return 0
    for j in range(4):
        pivot=next((i for i in range(rank,len(A)) if A[i][j]),None)
        if pivot is None:continue
        A[rank],A[pivot]=A[pivot],A[rank];scale=A[rank][j];A[rank]=[x/scale for x in A[rank]]
        for i in range(len(A)):
            if i!=rank:
                z=A[i][j];A[i]=[x-z*y for x,y in zip(A[i],A[rank])]
        rank+=1
        if rank==4:return rank
    return rank
def main():
    r=json.loads((D/'support-costs.json').read_text());roots=[]
    for i,j in combinations(range(4),2):
        for sign in [1,-1]:
            v=[0]*4;v[i]=1;v[j]=sign;roots.append(v)
    costs=[0]+[rational_rank([v for i,v in enumerate(roots) if mask>>i&1]) for mask in range(1,4096)]
    assert costs==r['cost']
    span={0}
    for x in r['central_basis']:span|={a^x for a in list(span)}
    assert len(span)==8
    central=[sum(((1+sum(a*b for a,b in zip(u,v)))%2)<<j for j,v in enumerate(roots)) for u in roots]
    assert all(x in span for x in central)
    # Gaussian binomial recurrence independently checks the exact complete
    # quotient-subspace counts in dimension9; symmetry alone is not enough.
    counts=[Q(1)]
    for k in range(1,10):counts.append(counts[-1]*Q(2**(10-k)-1,2**k-1))
    expected=[int(x) for x in counts];assert all(x.denominator==1 for x in counts)
    source=(D/'all-supercodes.cpp').read_text()
    # Reviewed RREF loops use largest pivots, zero allotherpivotpositions,
    # arbitrary lower nonpivotentries: one canonical matrix per subspace.
    # Its greedy pass sorts trueweights, maintains binaryindependence, and
    # stops atcost12. Positiveweights make that early stop sound even if
    # a fullbasis is not yet reached. A counterexample exits nonzero.
    with tempfile.TemporaryDirectory(prefix='d4-independent-') as tmp:
        exe=Path(tmp)/'audit';subprocess.run(['clang++','-O3','-std=c++17',str(D/'all-supercodes.cpp'),'-o',str(exe)],check=True,capture_output=True)
        run=subprocess.run([str(exe),str(D/'INPUT.txt')],check=True,capture_output=True,text=True)
    lines=run.stdout.splitlines();assert len(lines)==11 and not run.stderr
    assert [int(x.split()[1]) for x in lines[:10]]==expected
    assert sum(expected)==8283458
    out=dict(status='PASS_INDEPENDENT_D4_RATIONAL_COSTS_CENTRAL_SPACE_COUNTS_AND_FRESH_ENUMERATION',
        support_vectors_checked=4095,support_rank_counts=dict(Counter(costs[1:])),central_rank=3,
        independent_quotient_counts=expected,total_supercodes=sum(expected),copy_support_rank_lower_bound=12,
        all_supercodes_source_sha256=hashlib.sha256(source.encode()).hexdigest(),
        reviewed_greedy_argument='Minimum weight basis of vector matroid, sorted by exactsupportweight; positiveweights permit threshold12 early rejection.',
        scope='All binary retainedresponse supercodes containing fixedD4 centralspace with existing root-supportcopy contract. Grants free source transform, but excludes changeddecoder/ports/nonbinaryscatter/sharedbanks/targetmixing.')
    (OUT/'D4-CROSSCHECK.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'])
if __name__=='__main__':main()
