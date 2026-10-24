"""Native radix phase tables over signed Gaussian dyadics.
All arithmetic is bounded by the caller's logarithmic-word contract; no TM,
transition table, transcendental oracle, or recursive integer multiplier appears.
The caller supplies a certified seed with coordinate error < 2^-p.
"""
from fractions import Fraction
from random import Random
import json


def need(ok,msg):
    if not ok: raise ValueError(msg)


def round_scaled(v,p):
    """Nearest integer to v/2^p, ties away from zero; shifts and sign only."""
    a=abs(v)
    q=(a+(1<<(p-1)))>>p
    return -q if v<0 else q


class PhaseTable:
    def __init__(self,D,p,radix_bits,seed,word_width=None):
        need(D>=2 and p>=2 and radix_bits>=1,'shape')
        self.D,self.p,self.t=D,p,radix_bits
        self.Q=1<<p;self.R=1<<radix_bits
        self.d=((D-1).bit_length()+radix_bits-1)//radix_bits
        self.E=1<<(radix_bits*self.d)
        need(self.Q>=64*(self.E+self.d),'precision guard')
        self.w=2*p+8 if word_width is None else word_width
        need(self.w>=2*p+8 and D<(1<<self.w),'bounded word guard')
        need(len(seed)==2 and all(abs(x)<=2*self.Q for x in seed),'seed representation')
        self.operations=0;self.tables=[]
        base=tuple(seed)
        for j in range(self.d):
            row=[(self.Q,0)]
            for a in range(1,self.R): row.append(self.multiply(row[-1],base))
            self.tables.append(row)
            self.operations+=4*self.R # writes and bounded counters
            if j+1<self.d:
                for _ in range(self.t): base=self.multiply(base,base)
        self.setup_operations=self.operations

    def multiply(self,a,b):
        ar,ai=a;br,bi=b
        need(all(abs(x)<=2*self.Q for x in (*a,*b)),'intermediate component guard')
        products=(ar*br,ai*bi,ar*bi,ai*br)
        need(all(abs(x)<(1<<(self.w-2)) for x in products),'word product guard')
        real=products[0]-products[1];imag=products[2]+products[3]
        need(max(abs(real),abs(imag))<(1<<(self.w-1)),'signed word sum guard')
        self.operations+=48 # four word MULs, signs, adds, shifts, bounded control
        out=(round_scaled(real,self.p),round_scaled(imag,self.p))
        need(all(abs(x)<=2*self.Q for x in out),'rounded magnitude guard')
        return out

    def power(self,e):
        need(0<=e<self.D,'exponent outside certified domain')
        out=(self.Q,0)
        for row in self.tables:
            digit=e&(self.R-1);e>>=self.t
            self.operations+=6 # digit extraction, table addresses, loads, loop
            out=self.multiply(out,row[digit])
        need(e==0,'exponent digit exhaustion')
        return out

    def coordinate_error_bound(self):
        return Fraction(16*(self.E+self.d),self.Q)


def cmul(a,b):
    return a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0]


def cpow(z,e):
    result=(Fraction(1),Fraction(0))
    while e:
        if e&1: result=cmul(result,z)
        z=cmul(z,z);e>>=1
    return result


def nearest_fraction(x,Q):
    v=x*Q
    sign=-1 if v<0 else 1;v=abs(v)
    return sign*((2*v.numerator+v.denominator)//(2*v.denominator))


def check():
    rng=Random(20261022);cases=queries=0;maximum_setup=0;maximum_query=0
    # Rational exact unit-circle points make the error oracle algebraic and exact.
    # The phase-table proof applies to every unit complex z, including roots.
    units=[(Fraction(0),Fraction(1)),(Fraction(3,5),Fraction(4,5)),
           (Fraction(-5,13),Fraction(12,13))]
    for D in (3,7,17,41,129):
      for t in (1,2,3):
       for z in units:
        p=24
        seed=tuple(nearest_fraction(x,1<<p) for x in z)
        tab=PhaseTable(D,p,t,seed)
        exponents=range(D) if D<=41 else [0,1,D-1,*[rng.randrange(D) for _ in range(15)]]
        for e in exponents:
            before=tab.operations;got=tab.power(e);used=tab.operations-before
            want=cpow(z,e);bound=tab.coordinate_error_bound()
            need(all(abs(Fraction(g,tab.Q)-v)<=bound for g,v in zip(got,want)),'exact phase error bound')
            need(used<=54*tab.d,'constant digit operation envelope')
            maximum_query=max(maximum_query,used);queries+=1
        need(tab.setup_operations<=60*tab.d*(tab.R+tab.t),'setup envelope')
        maximum_setup=max(maximum_setup,tab.setup_operations);cases+=1
    # An actual altered table entry must change an exponent that uses it.
    tab=PhaseTable(17,24,2,(0,1<<24));tab.tables[0][1]=(0,0)
    need(tab.power(1)!=(0,1<<24),'mutated phase table escaped')
    try:PhaseTable(129,8,3,(0,256))
    except ValueError:pass
    else:raise ValueError('undersized precision accepted')
    return dict(status='PASS',table_cases=cases,power_queries=queries,
                maximum_setup_operations=maximum_setup,maximum_query_operations=maximum_query,
                mutated_table_control=True,undersized_precision_control=True,
                scope='native bounded-word phase-table component; not a complete multiplication theorem')


if __name__=='__main__':print(json.dumps(check(),indent=2))
