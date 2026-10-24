"""Direct finite-word CRT, rounding and carry recovery for integer convolution.
Apache-2.0. Dugongue with substantial OpenAI Codex assistance. No TM primitive.
"""
import json
import random


def need(p,msg):
    if not p:raise ValueError(msg)

class Words:
    def __init__(self,w):self.limit=1<<w;self.ops=0;self.max_bits=0
    def put(self,x,cost=1):
        self.ops+=cost;self.max_bits=max(self.max_bits,abs(x).bit_length())
        need(abs(x)<self.limit,'word overflow');return x
    def mulmod(self,a,b,p):return self.put(self.put(a*b)%p,2)
    def powmod(self,a,e,p):
        x=1;a=self.put(a%p,2)
        while e:
            if e&1:x=self.mulmod(x,a,p)
            a=self.mulmod(a,a,p);e>>=1;self.ops+=6
        return x


def prime_check(p,v):
    need(p>=2,'prime lower bound')
    d=2
    while v.put(d*d)<=p:
        v.ops+=5
        if p%d==0:return p==d
        d+=1
    return True


def crt_setup(primes,w=64):
    v=Words(w);M=1;data=[]
    for p in primes:
        need(prime_check(p,v),'nonprime CRT modulus')
        need(all(q!=p for q,_,_ in data),'duplicate CRT modulus')
        inv=v.powmod(M,p-2,p)
        need(v.mulmod(M%p,inv,p)==1,'CRT inverse failure')
        data.append((p,M,inv));M=v.put(M*p)
    return data,M,v


def crt_recover(residues,data,Q,v,signed=False):
    need(len(residues)==len(data),'CRT residue length')
    x=0
    for residue,(p,M,inv) in zip(residues,data):
        need(0<=residue<p,'CRT residue range')
        s=v.put(x%p,2);difference=v.put(residue+p-s,3)
        t=v.mulmod(difference%p,inv,p)
        x=v.put(x+v.put(M*t),3);v.ops+=4
    need(0<=x<Q,'CRT canonical range')
    if signed and v.put(x+x)>Q:x=v.put(x-Q,3)
    return x


def round_coefficients(values,precision,bound,v):
    need(precision>=1,'positive recovery precision')
    scale=1<<precision;out=[]
    for y in values:
        v.put(y)
        value=(abs(y)+(scale>>1))>>precision;value=value if y>=0 else -value
        v.put(value,8);need(0<=value<=bound,'nonnegative convolution range')
        out.append(value)
    return out


def carry(coefficients,b,la,lb,v):
    need(b>=1 and la>=1 and lb>=1,'carry shape')
    beta=1<<b;bound=min(la,lb)*(beta-1)*(beta-1)
    need(len(coefficients)==la+lb-1,'convolution length')
    c=0;out=[]
    for j in range(la+lb):
        a=coefficients[j] if j<len(coefficients) else 0
        need(0<=a<=bound,'coefficient bound')
        t=v.put(a+c,3)
        out.append(v.put(t&(beta-1),3));c=v.put(t>>b,4)
        need(c<=min(la,lb)*(beta-1),'carry envelope')
    need(c==0,'convolution does not fit product width')
    return out


def check():
    rng=random.Random(4542);cases=crt_cases=round_cases=ops=0;controls=0
    for b in (1,2,4,8):
        for la in (1,2,3,8,17):
            for lb in (1,2,5,16):
                beta=1<<b;bound=min(la,lb)*(beta-1)**2
                primes=[];Q=1
                for p in (3,5,7,11,13,17,19,23,29):
                    primes.append(p);Q*=p
                    if Q>2*bound:break
                data,Q,v=crt_setup(primes)
                for sample in range(12):
                    a=[rng.randrange(beta) for _ in range(la)]
                    d=[rng.randrange(beta) for _ in range(lb)]
                    if sample==0:a=[beta-1]*la;d=[beta-1]*lb
                    gold=[sum(a[i]*d[j] for i in range(la) for j in range(lb) if i+j==t) for t in range(la+lb-1)]
                    recovered=[crt_recover([x%p for p in primes],data,Q,v) for x in gold]
                    need(recovered==gold,'CRT convolution recovery')
                    crt_cases+=len(gold)
                    scaled=[(x<<12)+rng.randrange(-2047,2048) for x in gold]
                    rounded=round_coefficients(scaled,12,bound,v)
                    need(rounded==gold,'strict half-unit rounding recovery')
                    round_cases+=len(gold)
                    actual=carry(recovered,b,la,lb,v)
                    left=sum(x<<(b*i) for i,x in enumerate(a));right=sum(x<<(b*i) for i,x in enumerate(d))
                    need(sum(x<<(b*i) for i,x in enumerate(actual))==left*right,'native carry exact product')
                    cases+=1
                # Signed CRT: symmetric interval recovery, not modulo ambiguity.
                for x in (-bound,0,bound):
                    need(crt_recover([x%p for p in primes],data,Q,v,True)==x,'signed CRT recovery')
                ops+=v.ops
    for primes in ((9,),(5,5)):
        try:crt_setup(primes)
        except ValueError:controls+=1
        else:raise ValueError('bad CRT setup accepted')
    try:carry([100],2,1,1,Words(8))
    except ValueError:controls+=1
    else:raise ValueError('bad coefficient accepted')
    # Actual half-unit fault changes a rounded integer and must fail the gold oracle.
    v=Words(32);need(round_coefficients([(3<<12)+2049],12,10,v)!=[3],'rounding fault escaped');controls+=1
    return dict(status='PASS',product_cases=cases,CRT_coefficients=crt_cases,
                rounded_coefficients=round_cases,negative_controls=controls,
                charged_word_operations=ops,TM_calls=False,unbounded_runtime_product=False,
                setup_primality_and_inversion_charged=True,emitted_RamStd_program=False,Lean_proof=False)

if __name__=='__main__':print(json.dumps(check(),indent=2))
