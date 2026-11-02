"""Independent integer-row test of explicitly declared zero-scratch exits."""
from collections import Counter
from fractions import Fraction as Q


def verify(word,obligations):
    n=word['public']+word['owned_fields'];rows=[[int(i==j) for j in range(n)] for i in range(n)];exponents=[0]*n
    expected={(int(x['field']),int(x['frame'])):int(x['count']) for x in obligations};counts=Counter();sites=[]
    for t,event in enumerate(word['program']):
        op,d=event[:2]
        if op=='MOVE':continue
        if op in ('INIT','CLEAR'):
            if op=='CLEAR' and (d,event[2]) in expected:
                if any(rows[d]):raise ValueError('Declared new scratch not exactly zero before erasure at event '+str(t))
                counts[d,event[2]]+=1;sites.append(t)
            rows[d]=[0]*n;exponents[d]=0;continue
        q=Q(event[-2]);power=q.denominator.bit_length()-1
        if q.denominator!=1<<power:raise ValueError('Non-dyadic scalar')
        if op=='SCALE':rows[d]=[q.numerator*x for x in rows[d]];exponents[d]+=power
        else:
            source=event[2];level=max(exponents[d],exponents[source]+power)
            a=1<<(level-exponents[d]);b=q.numerator<<(level-exponents[source]-power)
            if op=='COPY':rows[d]=[b*x for x in rows[source]]
            elif op=='ADD':rows[d]=[a*x+b*y for x,y in zip(rows[d],rows[source])]
            else:raise ValueError('Unknown scalar opcode')
            exponents[d]=level
        if not any(rows[d]):exponents[d]=0
        else:
            while exponents[d] and all(not (x&1) for x in rows[d]):
                rows[d]=[x//2 for x in rows[d]];exponents[d]-=1
    if dict(counts)!=expected:raise ValueError('Declared zero-scratch exit inventory differs')
    return dict(method='Independent dense integer rows with binary exponents',all_input_columns=n,zero_owned_clear_sites=sites,obligations=obligations)
