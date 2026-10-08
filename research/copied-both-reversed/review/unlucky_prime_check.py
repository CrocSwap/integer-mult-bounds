"""Independent exact replay of the first unlucky-prime data prefix."""
from fractions import Fraction as Q
from pathlib import Path
import json


def run():
    a,b=23,25;d=47;left=(0,9,10);right=(14,18,20)
    R=list(range(a))+[22]+list(range(a));C=list(range(a))+[0]+list(range(a))
    z=[Q(31,18) if i in left else Q(-5,24) for i in range(a)]
    w=[Q(68,39) if i in right else Q(-5,26) for i in range(b)]
    M=[[Q(R[i]==C[j])/z[R[i]]+Q(i%b==(j+3)%b)/w[i%b]-1 for j in range(d)] for i in range(d)]
    order=[46]+[i+24 for i in range(1,22)]+[46-i for i in range(22,28)]+[i-26 for i in range(28,45)]+[1,0]
    available=set(range(d));values=[];zero_count=0
    for i,c in enumerate(order):
        value=M[i][c];assert value
        for j in available:
            if j>c:assert M[i][j]==0;zero_count+=1
        values.append(value);available.remove(c)
        for r in range(i+1,d):
            if M[r][c]:
                ratio=M[r][c]/value
                for j in available:M[r][j]-=ratio*M[i][j]
                M[r][c]=0
    expected=Q(-1040817578056012397961768075264,140132077459481987775304655993)
    assert values[26]==expected
    assert values[26].numerator%1000003==0 and values[26].denominator%1000003!=0
    return dict(status='PASS exact rational profile; primary modular zero is unlucky',
        left=left,right=right,pivot_columns=order,pivot_values=list(map(str,values)),
        exact_zero_checks=zero_count,failed_modular_prime=1000003,nonzero_rational_row26=str(values[26]))

if __name__=='__main__':
    result=run();Path(__file__).with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result['status'],result['nonzero_rational_row26'])
