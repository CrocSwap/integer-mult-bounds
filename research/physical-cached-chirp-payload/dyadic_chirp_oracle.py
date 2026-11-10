"""Independent dyadic chirp enclosures from positive half-angle square roots.

Prepared for @CubeJerry by a separate source-aware OpenAI verifier.
Apache-2.0. This is an external finite source oracle, not an online supplier.
No pi enclosure, Taylor exponential, trigonometric float or producer code is
used. All enclosure operations use outward-rounded exact integer arithmetic.
"""
from math import isqrt


def need(condition,message):
    if not condition:raise ValueError(message)


def ceil_div(numerator,denominator):
    return -((-numerator)//denominator)


def sqrt_half_grid(numerator,bits):
    """Enclose sqrt(numerator/(2*2**bits)) on the same 2**-bits grid."""
    unit=1<<bits
    need(bits>=1 and 0<=numerator<=2*unit,'bounded positive half-angle argument')
    scaled=numerator*unit
    lower=isqrt(scaled//2)
    upper=lower if 2*lower*lower==scaled else lower+1
    need(2*lower*lower<=scaled<=2*upper*upper,'directed integer square root')
    return lower,upper


def product_interval(left,right):
    a,b=left;c,d=right;values=(a*c,a*d,b*c,b*d)
    return min(values),max(values)


def multiply(left,right,bits):
    """Rectangle product with outward rounding on each component."""
    u=1<<bits
    ac=product_interval(left[:2],right[:2]);bd=product_interval(left[2:],right[2:])
    ad=product_interval(left[:2],right[2:]);bc=product_interval(left[2:],right[:2])
    return ((ac[0]-bd[1])//u,ceil_div(ac[1]-bd[0],u),
            (ad[0]+bc[0])//u,ceil_div(ad[1]+bc[1],u))


def primitive(t,bits):
    """Enclose exp(-pi*i/t) by repeated fourth-quadrant square roots of -1."""
    need(type(t) is int and t>0 and t&(t-1)==0,'positive dyadic denominator')
    need(type(bits) is int and bits>=1,'positive enclosure precision')
    unit=1<<bits;lo=hi=-unit;sine_lo=sine_hi=0
    for _ in range(t.bit_length()-1):
        cosine_lo,_=sqrt_half_grid(unit+lo,bits)
        _,cosine_hi=sqrt_half_grid(unit+hi,bits)
        sine_lo,_=sqrt_half_grid(unit-hi,bits)
        _,sine_hi=sqrt_half_grid(unit-lo,bits)
        lo,hi=cosine_lo,cosine_hi
    return lo,hi,-sine_hi,-sine_lo


def enclose(t,s,x,bits):
    """Enclose exp(-pi*i*s*x*x/t), with exact symbolic quarter roots."""
    need(type(s) is int and s%2!=0 and type(x) is int,'odd slope and integer coordinate')
    need(type(t) is int and t>0 and t&(t-1)==0,'positive dyadic denominator')
    need(type(bits) is int and bits>=1,'positive enclosure precision')
    order=2*t;k=(s*x*x)%order;unit=1<<bits
    if (4*k)%order==0:
        exact=((unit,0),(0,-unit),(-unit,0),(0,unit))[(4*k//order)%4]
        return exact[0],exact[0],exact[1],exact[1]
    power=primitive(t,bits);result=(unit,unit,0,0)
    while k:
        if k&1:result=multiply(result,power,bits)
        k>>=1
        if k:power=multiply(power,power,bits)
    return result


def component_error(value,interval):
    lo,hi=interval
    return (lo-value if value<lo else value-hi if value>hi else 0,
            max(abs(value-lo),abs(value-hi)))


def check_row(t,s,x,real,imaginary,precision,max_refinements=8):
    """Certify unit disk, inner endpoints, exact axes and <=2 ulp per component.

    Inconclusive enclosures are distinguished from proved coefficient errors.
    Refinement changes only the oracle, never the producer's coefficients.
    """
    need(all(type(v) is int for v in (real,imaginary,precision)) and precision>=0,
         'integer dyadic complex coefficient')
    need(real*real+imaginary*imaginary<=1<<(2*precision),'exact dyadic unit disk')
    need(type(t) is int and t>0 and t&(t-1)==0,'positive dyadic denominator')
    bits=precision+4*(t.bit_length()-1)+32
    for _ in range(max_refinements):
        rectangle=enclose(t,s,x,bits);shift=bits-precision
        values=(real<<shift,imaginary<<shift)
        intervals=(rectangle[:2],rectangle[2:])
        errors=tuple(component_error(v,I) for v,I in zip(values,intervals))
        budget=2<<shift
        if (4*((s*x*x)%(2*t)))%(2*t)==0:
            need(values==(rectangle[0],rectangle[2]),'exact quarter-root encoding')
        if max(e[0] for e in errors)>budget:
            raise ValueError('proved chirp component error exceeds two ulp')
        inward=True
        for value,(lo,hi) in zip(values,intervals):
            if lo>=0:
                need(value>=0 and value<=hi,'proved outward positive component')
                inward=inward and value<=lo
            elif hi<=0:
                need(value<=0 and value>=lo,'proved outward negative component')
                inward=inward and value>=hi
            else:
                inward=False
        if inward and max(e[1] for e in errors)<=budget:
            return dict(t=t,s=s,x=x,precision=precision,root_bits=bits,
                exponent=(s*x*x)%(2*t),rectangle=rectangle,
                maximum_component_error_numerator=max(e[1] for e in errors),
                error_denominator=1<<bits)
        bits+=32
    raise ValueError('chirp component check inconclusive after refinement')


def check_tables(radices,slopes,tables,precision):
    """Check original source coordinates and literal consumer conjugation."""
    need(len(radices)>0 and len(radices)==len(slopes)==len(tables),'complete axis table family')
    need(all(type(t) is int and t>=2 and t&(t-1)==0 for t in radices),'dyadic radices at least two')
    need(radices[0]==max(radices),'largest radix is axis zero')
    records=0;maximum=(0,1);max_bits=0;axes=0
    for t,s,table in zip(radices,slopes,tables):
        need(len(table)==t,'complete original chirp coordinate table')
        for x,pair in enumerate(table):
            need(len(pair)==2,'complex coefficient pair')
            receipt=check_row(t,s,x,pair[0],pair[1],precision)
            check_row(t,-s,x,pair[0],-pair[1],precision)
            n,d=receipt['maximum_component_error_numerator'],receipt['error_denominator']
            if n*maximum[1]>maximum[0]*d:maximum=(n,d)
            max_bits=max(max_bits,receipt['root_bits']);records+=1
            axes+=((4*receipt['exponent'])%(2*t)==0)
    return dict(method='positive half-angle integer-isqrt intervals plus complex powering',
                coefficients=records,conjugates_checked=records,exact_quarter_roots=axes,
                maximum_component_error_numerator=maximum[0],error_denominator=maximum[1],
                maximum_oracle_bits=max_bits,precision=precision)


def selfcheck():
    bits=96;unit=1<<bits
    for t in (1,2,4,8,16,64):
        for s in (-7,-1,1,3,5):
            for x in range(min(2*t,32)):
                k=(s*x*x)%(2*t)
                if (4*k)%(2*t)==0:
                    a=enclose(t,s,x,bits)
                    need(a[0]==a[1] and a[2]==a[3],'exact dyadic root axes')
                    need(a[0]**2+a[2]**2==unit*unit,'exact axis norm')
    c0,c1,s0,s1=primitive(4,bits)
    need(2*c0*c0<=unit*unit<=2*c1*c1 and (s0,s1)==(-c1,-c0),'known eighth root')
    c0,c1,s0,s1=primitive(8,bits);a=enclose(8,3,1,bits)
    need(max(a[0],-s1)<=min(a[1],-s0) and max(a[2],-c1)<=min(a[3],-c0),
         'third-power quadrant identity')
    value=11863283
    need(2*value*value<=1<<48<2*(value+1)*(value+1),'exact fixed eighth-root floor')
    check_row(4,1,1,value,-value,24);check_row(8,1,0,1<<24,0,24)
    controls=((lambda:check_row(8,1,0,1<<24,1,24),'exact dyadic unit disk'),
              (lambda:check_row(8,1,0,-(1<<24),0,24),'exact quarter-root encoding'),
              (lambda:check_row(4,1,1,value,value,24),'proved chirp component error exceeds two ulp'),
              (lambda:check_row(8,1,1,value,-value,24),'proved chirp component error exceeds two ulp'))
    for operation,message in controls:
        try:operation()
        except ValueError as error:need(str(error)==message,'specific independent negative control')
        else:raise ValueError('independent negative control escaped')
    return dict(method='positive half-angle integer-isqrt intervals plus complex powering',
                tested_denominators=(1,2,4,8,16,64),negative_controls=len(controls))


if __name__=='__main__':
    print('PASS_DYADIC_ROOT_ORACLE',selfcheck())
