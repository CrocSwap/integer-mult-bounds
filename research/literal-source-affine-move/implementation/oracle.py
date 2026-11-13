"""Original-frame exact Gaussian columns, independent of emitted factors."""
from functools import cache
import move as C


def gamma(n):
    if type(n) is not int or n<=0:raise ValueError('positive Gamma')
    bits=bin(n)[2:];return '0'*(len(bits)-1)+bits


def header(shape):return ''.join(gamma(n) for n in shape)


def encode(values,width):
    if any(not -(1<<(width-1))<=x<(1<<(width-1)) for z in values for x in z):raise ValueError('signed oracle overflow')
    return ''.join(format(x%(1<<width),'0'+str(width)+'b') for z in values for x in z)


def reverse9(x):return int(format(x,'09b')[::-1],2)


@cache
def columns():
    exact=C.load('actual_affine_forward_oracle',C.HERE/'engines/reference/rank2/reference/source/native_verify.py')
    circuit=exact.adjoint(exact.frame((),9))+exact.frame((75,137,265),9)
    result=[]
    for source in range(512):
        vec,exponent=exact.state(circuit,reverse9(source))
        result.append((tuple((reverse9(target),a,b) for target,(a,b) in vec.items()),1<<exponent))
    return tuple(result)


def image(values,shape):
    f,c,p,s,width,_=shape
    if f!=1 or len(values)!=p*512*s*c:raise ValueError('complete f1 oracle domain')
    out=[(0,0) for _ in values];den=max(d for _,d in columns());tail=s*c
    for source,(entries,d) in enumerate(columns()):
        scale=den//d
        for target,a,b in entries:
            a*=scale;b*=scale
            for outer in range(p):
                for suffix in range(tail):
                    x,y=values[(outer*512+source)*tail+suffix];i=(outer*512+target)*tail+suffix
                    u,v=out[i];out[i]=(u+a*x-b*y,v+b*x+a*y)
    if any(a%den or b%den for a,b in out):raise ValueError('nonintegral original-frame output')
    return [(a//den,b//den) for a,b in out]
