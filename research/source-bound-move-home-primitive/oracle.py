"""Direct selected-frame Gaussian columns, not the MOVE factor word. Apache-2.0."""
import json
from adapter import C,NATIVE


def gamma(n):
    if type(n) is not int or n<=0:raise ValueError('positive Gamma integer')
    b=bin(n)[2:]
    return '0'*(len(b)-1)+b


def header(shape):return ''.join(gamma(n) for n in shape)


def encode(values,w):
    result=[]
    for pair in values:
        for value in pair:
            if not -(1<<(w-1))<=value<(1<<(w-1)):raise ValueError('signed fixture overflow')
            result.append(format(value%(1<<w),'0'+str(w)+'b'))
    return ''.join(result)


def reverse9(x):
    return int(format(x,'09b')[::-1],2)


def expected_f1(values,shape):
    f,r,p,s,w,_=shape
    if f!=1 or len(values)!=p*512*s*r:raise ValueError('complete f=1 oracle domain')
    witness=json.loads((NATIVE/'reference/SOURCE-FRAMES.json').read_text())
    if witness['event']!=['MOVE',415,3,99,False]:raise ValueError('wrong selected source event')
    engine=C.load('home_move_frame_engine','source/native_verify.py')
    a,b=witness['event'][2:4]
    circuit=engine.adjoint(engine.frame(witness['frames'][str(a)],9))+engine.frame(witness['frames'][str(b)],9)
    result=[(0,0) for _ in values]
    tail=s*r
    for source in range(512):
        column,denominator=engine.state(circuit,reverse9(source))
        if denominator!=1:raise ValueError('selected rank-one Gaussian denominator')
        for target,(c,d) in column.items():
            out=reverse9(target)
            for outer in range(p):
                for suffix in range(tail):
                    u,v=values[(outer*512+source)*tail+suffix]
                    x,y=c*u-d*v,d*u+c*v
                    index=(outer*512+out)*tail+suffix
                    old=result[index];result[index]=(old[0]+x,old[1]+y)
    if any(x%2 or y%2 for x,y in result):raise ValueError('nonintegral complete expected image')
    return encode([(x//2,y//2) for x,y in result],w)
