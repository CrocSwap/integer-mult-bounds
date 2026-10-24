"""Global-precision native negacyclic record products, Apache-2.0.
Dugongue with substantial OpenAI Codex assistance.
"""
from pathlib import Path
from random import Random
import json


def need(ok,why):
    if not ok:raise ValueError(why)


def module(name):
    p=Path(__file__).with_name(name);ns={'__name__':'record_component','__file__':str(p)}
    exec(compile(p.read_bytes(),str(p),'exec'),ns);return ns


class RecordProduct:
    def __init__(self,r,p):
        need(r>=1 and r&(r-1)==0 and p>=1,'record shape')
        self.r=r;self.p=p;N=max(2,2*r)
        self.F=16*p+16*r.bit_length()+64;self.S=1<<self.F
        Convolver=module('native_convolution.py')['Convolver']
        self.cv=Convolver(N,self.F,16*(self.F+16)+20)

    def product(self,a,b):
        r=self.r;p=self.p;S=self.S;v=self.cv.val
        need(len(a)==len(b)==r,'record coefficient length')
        need(all(abs(x)<1<<p for z in a+b for x in z),'record coefficient range')
        aa=[(v(z[0]*S),v(z[1]*S)) for z in a]
        bb=[(v(z[0]*S),v(z[1]*S)) for z in b]
        kernel=self.cv.prepare(bb)
        got=self.cv.apply(aa,kernel,2*r-1)
        integers=[]
        for z in got:
            out=[]
            for x in z:
                value=v(v(x+S//2)//S)
                need(abs(x-value*S)<S//4,'integer recovery separation')
                out.append(value)
            integers.append(tuple(out))
        result=[]
        for j in range(r):
            high=integers[j+r] if j+r<len(integers) else (0,0)
            result.append((v(integers[j][0]-high[0]),v(integers[j][1]-high[1])))
        return result


def check():
    rng=Random(20261022);cases=points=0;peak=0
    for r in (1,2,4,8,16,32):
        for p in (8,48,192):
            engine=RecordProduct(r,p)
            for _ in range(2):
                a=[(rng.randrange(-(1<<p)+1,1<<p),rng.randrange(-(1<<p)+1,1<<p)) for _ in range(r)]
                b=[(rng.randrange(-(1<<p)+1,1<<p),rng.randrange(-(1<<p)+1,1<<p)) for _ in range(r)]
                actual=engine.product(a,b);expected=[[0,0] for _ in range(r)]
                # Independent exact schoolbook ring oracle; validation only.
                for i,(ar,ai) in enumerate(a):
                    for j,(br,bi) in enumerate(b):
                        sign=1 if i+j<r else -1;k=(i+j)%r
                        expected[k][0]+=sign*(ar*br-ai*bi)
                        expected[k][1]+=sign*(ar*bi+ai*br)
                need(actual==list(map(tuple,expected)),'negacyclic polynomial reference')
                points+=r;cases+=1
            peak=max(peak,engine.cv.maximum_bits)
    try:RecordProduct(2,8).product([(256,0)]*2,[(1,0)]*2)
    except ValueError:pass
    else:raise ValueError('record overflow accepted')
    return dict(status='PASS',signed_complex_record_products=cases,ring_coefficients=points,
                maximum_bits=peak,overflow_control=True,TM_calls=0,
                scope='direct global-word FFT record product; no local-log(record bitlength) word model')


if __name__=='__main__':print(json.dumps(check(),indent=2))
