"""The actual periodic Gaussian maps, selector, and certified Neumann inverse.

The formulae are Harvey--van der Hoeven's, in the retained source07 notation.
This is a dense reference execution, not their fast tape implementation.
"""
from fractions import Fraction as F
from math import gcd, isqrt

from intervals import (Interval, need, ceildiv, pi_interval, exp_negative,
                       cadd, cscale, cmul, point, root_of_unity, grid_point,
                       inward_quantize, in_disk)


def zeros(rows, columns, bits):
    return [[Interval.rational(0, bits) for _ in range(columns)] for _ in range(rows)]


def matmul(a, b):
    return [[sum((a[i][k]*b[k][j] for k in range(len(b))), 0)
             for j in range(len(b[0]))] for i in range(len(a))]


def beta(j, s, t):
    nearest = (2*t*j+s) // (2*s)
    return F(t*j, s) - nearest


def correction_matrix(s, t, alpha, bits, omit_winding=False):
    """N-I, with every nonzero integer shift, including nonzero multiples of s."""
    sigma, theta = F(t, s), F(t-s, s)
    decay = 3 * alpha**2 * sigma * theta
    need(decay > 0, "Gaussian correction decay")
    ratio = F(bits+16, 1) / decay
    cutoff = isqrt(ceildiv(ratio.numerator, ratio.denominator)) + 2
    # Beyond cutoff, each side is bounded by a geometric tail whose first
    # term is < 2^-(bits+16), since pi>3, e>2 and X>=sigma*theta*h^2.
    need(decay*cutoff**2 > bits+16 and decay*(2*cutoff+1) >= 1,
         "certified correction tail cutoff")
    out = zeros(s, s, bits)
    pi = pi_interval(bits)
    for j in range(s):
        for h in range(-cutoff, cutoff+1):
            if h == 0 or (omit_winding and h % s == 0):
                continue
            exponent = (sigma*h+beta(j,s,t))**2 - beta(j+h,s,t)**2
            need(exponent >= sigma*theta*h*h, "correction exponent lower bound")
            out[j][(j+h) % s] += exp_negative(pi * (alpha**2 * exponent))
        # The sum of both omitted tails is below one working-grid unit;
        # adding one to each entry is a conservative entrywise enclosure.
        out[j] = [Interval(x.lo, x.hi+1, bits) for x in out[j]]
    return out, cutoff


class GaussianLine:
    def __init__(self, s, t, alpha, precision=256, bits=448):
        need(precision > 100 and 2 <= s < t < 2**precision and gcd(s,t)==1,
             "original resampling integer domain")
        need(2 <= alpha and alpha**2 < precision and F(t-s,s) > F(precision,alpha**4),
             "original resampling alpha/theta domain")
        need(t & (t-1) == 0, "power-of-two target")
        need(bits > precision+2*alpha**2+32, "working enclosure guard")
        self.s,self.t,self.alpha,self.p,self.bits=s,t,alpha,precision,bits
        self.gamma=2*alpha**2
        self.selector=[(2*t*j+s)//(2*s) for j in range(s)]
        need(self.selector[0]==0 and self.selector[-1]<t and
             all(a<b for a,b in zip(self.selector,self.selector[1:])), "ordered selector")
        pi=pi_interval(bits)
        radius=alpha*(isqrt(bits+16)+2)
        need(F(3*radius**2,alpha**2)>bits+16 and F(3*(2*radius+1),alpha**2)>=1,
             "certified expansion tail cutoff")
        expansion=zeros(t,s,bits)
        for k in range(t):
            center=F(s*k,t)
            left=center.numerator//center.denominator-radius
            right=ceildiv(center.numerator,center.denominator)+radius
            for j in range(left,right+1):
                x=pi*((F(j)-center)**2/alpha**2)
                expansion[k][j%s] += exp_negative(x) / (2*alpha)
            expansion[k]=[Interval(x.lo,x.hi+1,bits) for x in expansion[k]]
        self.expansion=expansion
        self.expansion_radius=radius
        self.correction,self.correction_cutoff=correction_matrix(s,t,alpha,bits)
        scale=1<<bits
        eta=F(max(sum(x.hi for x in row) for row in self.correction),scale)
        need(0 <= eta < F(1,2), "actual correction contraction")
        self.eta=eta
        power=eta
        terms=1
        while power/(1-eta) >= F(1,1<<(bits-24)):
            power*=eta
            terms+=1
        self.neumann_terms=terms
        self.inverse_tail=power/(1-eta)
        ident=zeros(s,s,bits)
        for i in range(s):ident[i][i]=Interval.rational(1,bits)
        # Horner evaluates I-E+E^2-...+(-E)^(terms-1).
        partial=ident
        for _ in range(terms-1):
            product=matmul(self.correction,partial)
            partial=[[ident[i][j]-product[i][j] for j in range(s)] for i in range(s)]
        tail_units=ceildiv(self.inverse_tail.numerator*scale,self.inverse_tail.denominator)
        self.inverse=[[x.widen(tail_units) for x in row] for row in partial]
        self.diagonal=[]
        for j in range(s):
            inv=exp_negative(pi*(alpha**2*beta(j,s,t)**2)).reciprocal()
            self.diagonal.append(inv / (1<<(2*alpha**2-2)))
        self.compression=[[self.diagonal[i]*self.inverse[i][j]/2 for j in range(s)] for i in range(s)]
        self.expansion_norm=F(max(sum(x.absolute_upper() for x in row) for row in self.expansion),scale)
        self.compression_norm=F(max(sum(x.absolute_upper() for x in row) for row in self.compression),scale)
        need(self.expansion_norm<1 and self.compression_norm<1, "certified map contractions")
        self.operator_error=None
        self.uniform_error=None

    def certify_operator(self, mutation=None):
        """Bound the entire Gaussian/Fourier operator difference on the unit ball.

        This independently enclosed Fourier matrix is used only to certify
        the operator, never to supply a transform result to the multiplier.
        """
        rows=[0]*self.s
        separated=0
        for column in range(self.s):
            actual=self.exact_column(column,mutation)
            expected=self.direct_column(column)
            for i,(a,b) in enumerate(zip(actual,expected)):
                delta=(a[0]-b[0],a[1]-b[1])
                rows[i]+=sum(c.absolute_upper() for c in delta)
                separated+=int(not all(x.overlaps(y) for x,y in zip(a,b)))
        bound=F(max(rows),1<<self.bits)
        if mutation is not None:
            return bound,separated
        need(bound<F(1,1<<(self.p+8)),"Gaussian/Fourier operator certificate")
        self.operator_error=bound
        scale=1<<self.bits
        h=F(1,1<<self.p)
        def matrix_error(matrix):
            width=max(sum(x.hi-x.lo for x in row) for row in matrix)
            return 2*h+F(2*width+4*len(matrix[0]),scale)
        fft_error=F(0)
        length=2
        while length<=self.t:
            widths=max(sum(x.hi-x.lo for x in root_of_unity(-j,length,self.bits))
                       for j in range(length//2))
            fft_error+=2*h+F(widths+8,scale)
            length*=2
        self.uniform_error=(matrix_error(self.expansion)+fft_error+
                            matrix_error(self.compression))*(1<<self.gamma)+bound
        return bound,separated

    def apply_real(self,matrix,values):
        out=[];error=F(0)
        for row in matrix:
            z=point(0,0,self.bits)
            for entry,value in zip(row,values):
                z=cadd(z,cscale(grid_point(value,self.p,self.bits),entry))
            rounded,local=inward_quantize(z,self.p)
            need(in_disk(rounded,self.p),"completed Gaussian map returns disk grid")
            out.append(rounded);error=max(error,local)
        return out,error

    def fft(self,values):
        """Executed normalized radix-two FFT; round after every butterfly."""
        n=len(values)
        if n==1:return list(values),F(0)
        even,ee=self.fft(values[::2]);odd,eo=self.fft(values[1::2])
        out=[None]*n;local=F(0)
        for j in range(n//2):
            a=grid_point(even[j],self.p,self.bits)
            b=cmul(grid_point(odd[j],self.p,self.bits),root_of_unity(-j,n,self.bits))
            for index,sign in ((j,1),(j+n//2,-1)):
                z=cscale(cadd(a,cscale(b,sign)),F(1,2))
                rounded,err=inward_quantize(z,self.p)
                need(in_disk(rounded,self.p),"normalized butterfly disk")
                out[index]=rounded;local=max(local,err)
        return out,max(ee,eo)+local

    def transform(self,values,opposite=False,mutation=None):
        if self.operator_error is None:self.certify_operator()
        need(len(values)==self.s and all(in_disk(z,self.p) for z in values),"line input contract")
        if opposite:values=[(a,-b) for a,b in values]
        expanded,ea=self.apply_real(self.expansion,values)
        transformed,ef=self.fft(expanded)
        routed=[transformed[(-self.s*k)%self.t] for k in range(self.t)]
        if mutation=="omit_target_permutation":routed=transformed
        selected=[routed[k] for k in self.selector]
        if mutation=="wrong_selector":selected=routed[:self.s]
        compressed,eb=self.apply_real(self.compression,selected)
        power=self.gamma-(1 if mutation=="missing_rescale_bit" else 0)
        result=[(a<<power,b<<power) for a,b in compressed]
        error=(ea+ef+eb)*(1<<self.gamma)+self.operator_error
        need(error<=self.uniform_error,"executed error is within uniform operator budget")
        if opposite:result=[(a,-b) for a,b in result]
        need(all(in_disk(z,self.p) for z in result),"source transform disk after exact scale")
        return result,error

    def exact_column(self,column,mutation=None):
        """Unrounded Gaussian composite enclosing one RF_s basis column."""
        a=[row[column] for row in self.expansion]
        transformed=[]
        for k in range(self.t):
            z=point(0,0,self.bits)
            for j,value in enumerate(a):
                z=cadd(z,cscale(root_of_unity(-j*k,self.t,self.bits),value/F(self.t)))
            transformed.append(z)
        routed=[transformed[(-self.s*k)%self.t] for k in range(self.t)]
        if mutation=="omit_target_permutation":routed=transformed
        selected=[routed[k] for k in self.selector]
        if mutation=="wrong_selector":selected=routed[:self.s]
        out=[]
        for i in range(self.s):
            z=point(0,0,self.bits)
            for j,value in enumerate(selected):
                coeff=self.compression[i][j]
                if mutation=="omit_correction":
                    coeff=self.diagonal[i]/2 if i==j else Interval.rational(0,self.bits)
                z=cadd(z,cscale(value,coeff))
            out.append(cscale(z,1<<(self.gamma-(mutation=="missing_rescale_bit"))))
        return out

    def direct_column(self,column):
        return [cscale(root_of_unity(-self.t*k*column,self.s,self.bits),F(1,self.s))
                for k in range(self.s)]
