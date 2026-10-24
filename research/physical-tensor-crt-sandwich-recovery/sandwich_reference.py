"""Natural-coordinate staged oracle; no physical numerical child calls.

Retains Jose Manuel's exact expansion/core reference formulas, replacing the
fixed (7,7) chirp exponents and axes by the original source lengths.
"""
from tensor_model import catalogue,axis_apply,expand,compress,roots16,tz
from check_fourier import dense
from chirp_check_middle import conjugate,multiply
from ring_check_product import oracle as ring_product

def full(values,raw,opposite=False):
    header,profiles=catalogue(raw)
    p=header['p'];sources=header['sources']
    if header['ell']!=3 or header['flags']!=(1,) or sources!=[5,7]:raise ValueError('declared 5x7 finite oracle')
    data=[(a,-b if opposite else b) for a,b in values];shape=tuple(sources)
    for axis in (0,1):data,shape=axis_apply(data,shape,axis,profiles[axis],expand)
    fine_p=p+6;fine=roots16(fine_p)
    basis=fine[1],fine[2],fine[4],(-(1<<fine_p),0)
    kernel=[]
    for i in range(8):
        for j in range(8):
            exponent=(-sources[0]*i*i-sources[1]*j*j)%16;phase=1<<fine_p,0
            for bit in range(4):
                if exponent&(1<<bit):phase=multiply(phase,basis[bit],fine_p)
            kernel.append(tuple(tz(v,64) for v in phase))
    twists=roots16(p)
    incoming=[multiply(conjugate(a),b,p) for a,b in zip(kernel,data)]
    left=[multiply(twists[i%8],a,p) for i,a in enumerate(kernel)]
    right=[multiply(twists[i%8],a,p) for i,a in enumerate(incoming)]
    first,second=dense(left,(1,),3,1,False),dense(right,(1,),3,1,False)
    product=ring_product(first,second,3,p,3,1)
    inverse=dense(product,(1,),3,1,True)
    cyclic=[multiply(conjugate(twists[i%8]),(8*a,8*b),p) for i,(a,b) in enumerate(inverse)]
    data=[multiply(conjugate(a),b,p) for a,b in zip(kernel,cyclic)]
    for axis in (0,1):data,shape=axis_apply(data,shape,axis,profiles[axis],compress)
    gamma=len(sources)*(2*header['alpha']**2+(32*p-1).bit_length()+1)
    return [(a<<gamma,(-b if opposite else b)<<gamma) for a,b in data]


def crt(values):
    out=[None]*35
    for k,value in enumerate(values):out[(k%5)*7+(3*k%7)]=value
    return out


def inverse_crt(values):
    return [values[(k%5)*7+(3*k%7)] for k in range(35)]


def sandwich(digits1,digits2,raw,b=8):
    header,_=catalogue(raw);p=header['p']
    inputs=[crt([(d<<(p-b-2),0) for d in digits]+[(0,0)]*(35-len(digits))) for digits in (digits1,digits2)]
    first,second=(full(v,raw) for v in inputs)
    product=[(tz(a*c-bb*d,1<<p),tz(a*d+bb*c,1<<p)) for (a,bb),(c,d) in zip(first,second)]
    opposite=full(product,raw,True)
    def nearest(v):return (abs(v)+(1<<(p-1)))//(1<<p)*(-1 if v<0 else 1)
    coefficients=inverse_crt([nearest(a*35*35*(1<<(2*b+4))) for a,_ in opposite])
    return dict(inputs=inputs,transforms=[first,second,opposite],pointwise=product,coefficients=coefficients)
