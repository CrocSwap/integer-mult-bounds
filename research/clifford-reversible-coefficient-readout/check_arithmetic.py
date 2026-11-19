"""Regenerate the canonical scalar weights, smallest denominator and exact record metric."""
from fractions import Fraction
from hashlib import sha256
from math import gcd,lcm
from pathlib import Path
import json
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from producer import ODD,SCALE,SHIFT


def weights():
    rows=json.loads((HERE/'retained'/'width13-spectrum.json').read_text())['rows']
    spheres=[1,30,280,960,1024]
    rhs=[Fraction(1,4**13)*Fraction(-1,64)**j for j in range(5)]
    answer=[Fraction(0)]*5
    for theta in (30,13,3,-5,-15):
        vec=[Fraction(1)]
        for j in range(4):
            lo=(1<<j)-1
            hi=2*(16-(1<<j))
            mid=30-lo-hi
            vec.append(((theta-mid)*vec[j]-(lo*vec[j-1] if j else 0))/hi)
        degree=2295/sum(k*u*u for k,u in zip(spheres,vec,strict=True))
        if degree.denominator!=1:
            raise ValueError(degree)
        eigen,=[Fraction(*r['eigenvalue']) for r in rows if r['quotient_degree']==degree]
        weight=degree/2295*sum(k*u*b for k,u,b in zip(spheres,vec,rhs,strict=True))/eigen
        for j in range(5):
            answer[j]+=weight*vec[j]
    return answer


def word_balls():
    for diagonal in (False,True):
        steps=([(1,1),(1,-1),(-1,1),(-1,-1)] if diagonal else [(1,0),(-1,0),(0,1),(0,-1)])
        ball={(0,0)}
        for length in range(9):
            expected={(x,y) for x in range(-length,length+1) for y in range(-length,length+1)
                      if (max(abs(x),abs(y))<=length and (x-y)%2==0 if diagonal else abs(x)+abs(y)<=length)}
            if ball!=expected:
                raise ValueError("Incorrect attainable lattice or metric")
            ball |= {(x+a,y+b) for x,y in ball for a,b in steps}


def main():
    for row in json.loads((HERE/'SOURCE-PINS.json').read_text()):
        if sha256((HERE/row['local']).read_bytes()).hexdigest()!=row['sha256']:
            raise ValueError(("Source bytes",row))
    h=weights()
    scale=[a/(1<<((j+1)//2)) for j,a in enumerate(h)]
    den=lcm(*(a.denominator for a in scale))
    if [int(v*den) for v in scale]!=list(SCALE) or den!=ODD<<SHIFT or scale[4].denominator!=den:
        raise ValueError((scale,den))
    word_balls()
    print("PASS five independently reconstructed weights, exact denominator",den,
          "forced by a rank-four coefficient; both complex record metrics.")


if __name__=='__main__':
    main()
