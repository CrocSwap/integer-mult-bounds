"""Independent weighted completed-bank endpoint checks on arbitrary formal data."""
from math import gcd


def run():
    m=72;cases=0;rejected=[]
    patterns=([4]*6+[24]*2,[24]*3)
    def apply(parts,modulus,reverse=False,repeat_first=False):
        rows=[{i:1} for i in range(2*m)]
        intervals=[];offset=0
        for width in parts:intervals.append(range(offset,offset+width));offset+=width
        if repeat_first:intervals.append(intervals[0])
        if reverse:intervals.reverse()
        for interval in intervals:
            for i in interval:
                weight=(1,2,4)[i%3];assert gcd(weight,modulus)==1
                a,b=rows[i],rows[2*m-1-i]
                rows[i]={j:weight*x%modulus for j,x in b.items()}
                rows[2*m-1-i]={j:pow(weight,-1,modulus)*x%modulus for j,x in a.items()}
        return rows
    def expected(modulus):
        return [{2*m-1-i:(1,2,4)[i%3]} for i in range(m)]+[
            {m-1-i:pow((1,2,4)[(m-1-i)%3],-1,modulus)} for i in range(m)]
    for modulus in (9,25,125):
        for pattern in patterns:
            for reverse in (False,True):
                assert apply(pattern,modulus,reverse)==expected(modulus)
                cases+=1
        try:assert apply(patterns[0],modulus,repeat_first=True)==expected(modulus)
        except AssertionError:rejected.append('repeated block mod '+str(modulus))
        else:raise AssertionError('Repeated block accepted')
        try:assert apply(patterns[0][:-1],modulus)==expected(modulus)
        except AssertionError:rejected.append('omitted block mod '+str(modulus))
        else:raise AssertionError('Omitted block accepted')
    return dict(formal_columns_per_case=2*m,weighted_partition_cases=cases,rejected=rejected)
