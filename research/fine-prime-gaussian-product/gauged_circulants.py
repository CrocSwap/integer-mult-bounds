"""Produce a gauged circulant on one pure dyadic block in original coordinates."""
from dataclasses import dataclass
from fractions import Fraction

from gaussian_pages import admit, ceildiv, exp_minus_pi, inverse_rational, pi_bounds, require


@dataclass(frozen=True)
class GaugedBlock:
    kind: str
    first_padded: int
    first_source: int
    length: int
    width: int
    bits: int
    row: tuple
    weights: tuple
    column: tuple
    inverse_weights: tuple
    row_defect: Fraction

    def entry(self, i, j):
        scale = 1 << self.bits
        return Fraction(self.row[i]*self.weights[(j-i)%self.length]*self.column[j],scale**3)


def build_circulant(s, t, alpha, first, length, width, bits, kind, setup_bits=None):
    """Return dyadic gauges and a kernel indexed by column minus row modulo length."""
    require(kind in ("broad","narrow"),"unknown Gaussian factor")
    require(isinstance(s,int) and 2<=s<t<2*s and t&(t-1)==0 and s%2==1,
            "invalid period or target")
    require(isinstance(length,int) and length>0 and length&(length-1)==0
            and 0<=first and first+length<=t and first%length==0,
            "invalid padded block")
    require(isinstance(width,int) and width>=0 and isinstance(alpha,int)
            and alpha>=2 and isinstance(bits,int) and bits>=8,"invalid band or precision")
    work=bits+64 if setup_bits is None else setup_bits
    require(isinstance(work,int) and work>=bits+8,"insufficient gauge setup width")
    unit,grid=1<<bits,1<<work
    pi=pi_bounds(work)
    ratio=Fraction(t,s)
    lam=1/ratio
    theta=ratio-1
    source=max(0,ceildiv(s*(2*first-1),2*t))

    def position(j):
        return (2*t*j+s)//(2*s)

    require(source+length<=s and position(source)==first
            and position(source+length-1)==first+length-1,
            "block contains a hole or crosses the original period")
    c0=first-source
    m=first+length//2
    delta=(1-lam)*m-c0
    beta0=ratio*delta
    require(abs(beta0)<=Fraction(1,2),"block anchor has the wrong phase")
    shift=-delta*(1-theta)

    def exponential(e):
        # Return an enclosure of exp(pi*e), at the setup grid.
        a,b=exp_minus_pi(abs(e),work,pi)
        if e<=0:
            return a,b
        admit(a>0,"positive gauge exponent exceeds reciprocal precision")
        return grid*grid//b,ceildiv(grid*grid,a)

    def quantize(bounds):
        vals=[]
        error=limit=Fraction(0)
        for lo,hi in bounds:
            weight=((lo+hi)*unit)//(2*grid)
            vals.append(weight)
            limit=max(limit,Fraction(hi,grid))
            error=max(error,abs(Fraction(weight,unit)-Fraction(lo,grid)),
                      abs(Fraction(weight,unit)-Fraction(hi,grid)))
        return tuple(vals),limit,error

    row=[]
    column=[]
    for padded in range(first,first+length):
        z=padded-m
        if kind=="broad":
            e=(lam*(1-lam)*z*z+2*lam*(delta+shift)*z-delta*delta+lam*shift*shift)/alpha**2
            low,high=exponential(e)
            row.append((low//alpha,ceildiv(high,alpha)))
            column.append(exponential(-((1-lam)*z*z+2*(delta+lam*shift)*z)/alpha**2))
        else:
            row.append(exponential(alpha**2*theta*z*z))
            column.append(exponential(-alpha**2*theta*z*z))
    weights=[(0,0)]*length
    for h in range(-width,width+1):
        e=-(lam*(h-shift)**2/alpha**2 if kind=="broad"
            else alpha**2*(ratio*h*h+2*beta0*h))
        low,high=weights[h%length]
        a,b=exponential(e)
        weights[h%length]=low+a,high+b

    u,U,du=quantize(row)
    c,C,dc=quantize(weights)
    v,V,dv=quantize(column)
    admit(min(u)>0 and min(v)>0,"diagonal gauge rounds to zero")
    defect=min(2*width+1,length)*(du*C*V+(U+du)*dc*V+(U+du)*(C+dc)*dv)
    kernel_inverse=()
    if kind=="narrow":
        kernel_inverse=inverse_rational([[Fraction(c[(j-i)%length],unit) for j in range(length)]
                                         for i in range(length)])[0]
        for j in range(length):
            require(sum(c[h]*kernel_inverse[(j-h)%length] for h in range(length))
                    ==unit*int(j==0),"inverse circulant orientation")
    return GaugedBlock(kind,first,source,length,width,bits,u,c,v,tuple(kernel_inverse),defect)
