"""Independent integer oracle for the eight-coordinate composite, no imports
from cached/chirp/Fourier/word verifiers. Prepared for @CubeJerry with
substantial OpenAI assistance. Apache-2.0.
"""
from fractions import Fraction
from math import isqrt

def trunc(x,d):return (abs(x)//d)*(-1 if x<0 else 1)
def conj(z):return z[0],-z[1]
def mul(x,y,f):
    a,b=x;c,d=y;Q=1<<f
    return trunc(a*c-b*d,Q),trunc(a*d+b*c,Q)
def add(x,y,sign=1):return x[0]+sign*y[0],x[1]+sign*y[1]

def transform(x):
    out=[]
    for sign in (1,-1):
        for k in range(4):
            a,b=add(x[k],x[k+4],sign)
            out.append((trunc(a,2),trunc(b,2)))
    return out

def product(x,y,f):
    out=[]
    for start in (0,4):
        sums=[[0,0] for _ in range(4)]
        for i in range(4):
            for j in range(4):
                a,b=x[start+i];c,d=y[start+j]
                sign=-1 if i+j>=4 else 1;k=(i+j)%4
                sums[k][0]+=sign*(a*c-b*d);sums[k][1]+=sign*(a*d+b*c)
        out.extend((trunc(a,4<<f),trunc(b,4<<f)) for a,b in sums)
    return out

def staged(values,q,f,*,first_conjugate=True,last_conjugate=True,scale=True,final_drop=True):
    Q=1<<f;v=isqrt(1<<(2*f-1))
    roots=[(Q,0),(v,v),(0,Q),(-v,v),(-Q,0),(-v,-v),(0,-Q),(v,-v)]
    phases=[roots[(-3*k*k-2*j*j)%8] for j in range(2) for k in range(4)]
    lifted=[(a<<(f-q),b<<(f-q)) for a,b in values]
    first=[mul(conj(a) if first_conjugate else a,x,f) for a,x in zip(phases,lifted)]
    twists=[roots[k] for j in range(2) for k in range(4)]
    left=[mul(t,a,f) for t,a in zip(twists,phases)]
    right=[mul(t,x,f) for t,x in zip(twists,first)]
    ring=transform(product(transform(left),transform(right),f))
    if scale:ring=[(2*a,2*b) for a,b in ring]
    cyclic=[mul(conj(t),x,f) for t,x in zip(twists,ring)]
    final=[mul(conj(a) if last_conjugate else a,x,f) for a,x in zip(phases,cyclic)]
    result=([(trunc(a,1<<(f-q)),trunc(b,1<<(f-q))) for a,b in final]
            if final_drop else final)
    return result,phases

def ideal(values,q):
    rows=[]
    for j in range(2):
        for k in range(4):
            real=imag=0
            for u in range(2):
                for v in range(4):
                    a,b=values[4*u+v]
                    c,d=((a,b),(-b,a),(-a,-b),(b,-a))[(2*j*u+3*k*v)%4]
                    real+=c;imag+=d
            rows.append((Fraction(real,8<<q),Fraction(imag,8<<q)))
    return rows

def external(values,q):
    return ''.join(''.join(str(int(v<0))+format(abs(v),'0'+str(q+1)+'b') for v in pair)+'#'
                   for pair in values)

def decode(text,q):
    result=[];step=q+2
    for row in text.split('#')[:-1]:
        if len(row)!=2*step:raise ValueError('external record width')
        pair=[]
        for offset in (0,step):
            word=row[offset:offset+step]
            pair.append((-1 if word[0]=='1' else 1)*int(word[1:],2))
        result.append(tuple(pair))
    return result
