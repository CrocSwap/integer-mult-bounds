#!/usr/bin/env python3
"""Independent finite sign-wrapper and retained dirty-scratch controls."""
import sys,json,random
from pathlib import Path
from fractions import Fraction as Q
REPO=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(REPO/'scripts'))
from paired_complex import PairedComplex
from complex_circuit import Checks,compile_roles,simulate_invocation

def mul(x,y):return (x[0]*y[0]-x[1]*y[1],x[0]*y[1]+x[1]*y[0])
phases=((1,0),(0,-1),(-1,0),(0,1))
entries=0
for a in range(1,5):
    for f in (1,2):
        axes=a*f
        for neg in range(1<<a):
            mask=sum(((1<<f)-1)<<(j*f) for j in range(a) if neg>>j&1)
            phase=phases[(f*neg.bit_count())%4]
            for xy in range(1<<axes):
                # Every matrix coefficient depends on x XOR y. Checking each
                # difference checks all 2^axes repeated entries simultaneously.
                lhs=rhs=(1,0)
                for j in range(axes):
                    sign=-1 if xy>>j&1 else 1
                    rhs=mul(rhs,(1,sign))
                    lhs=mul(lhs,(1,-sign if mask>>j&1 else sign))
                rhs=mul(rhs,phase)
                if (mask&xy).bit_count()%2:rhs=(-rhs[0],-rhs[1])
                assert lhs==rhs
                entries+=1<<axes
rows=[]
rng=random.Random(20261008)
for h in (8,10):
    c=PairedComplex(h);code=compile_roles(c);checks=Checks(c)
    coeff=checks.verify_map()
    calls=0
    for rep in range(4):
        r=lambda:Q(rng.randint(-9,9),2**rng.randrange(4))
        x={T:r() for T in c.triples};y={T:r() for T in c.triples}
        side=[r() for _ in range(code['roles'])];center={j:r() for j in list(range(h))+['*']}
        for reverse in (False,True):
            xx,yy,ss,cc=simulate_invocation(c,code,x,y,side,center,inverse=reverse)
            assert ss==side and cc==center
            if reverse:assert yy==y and all(xx[T]==x[T]-y[T] for T in c.triples)
            else:assert xx==x and all(yy[T]==y[T]+x[T] for T in c.triples)
            calls+=1
    rows.append(dict(h=h,map=coeff,arbitrary_dirty_controls=calls))
# Explicit full retained h28 coefficients: no numerical arithmetic.
c=PairedComplex(28);full=Checks(c).verify_map()
result=dict(status='PASS',mixed_sign_matrix_entries_checked=entries,
    axes_up_to=8,all_negative_slot_patterns=True,small_circuit_controls=rows,
    unchanged_full_h28_coefficients=full)
Path(__file__).with_name('controls.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
