"""Native limb arithmetic for paid offline setup; Apache-2.0.
Dugongue with substantial OpenAI Codex assistance.
Runtime routines use bounded 15-bit limbs and <=32-bit arithmetic only.
Python whole integers appear only in conversions and independent check().
"""
from random import Random
import json

BITS=15;BASE=1<<BITS;MASK=BASE-1


def need(ok,why):
    if not ok:raise ValueError(why)


def norm(a):
    a=list(a)
    need(all(type(x) is int and 0<=x<BASE for x in a),'limb range')
    while a and a[-1]==0:a.pop()
    return a


def compare(a,b):
    a=norm(a);b=norm(b)
    if len(a)!=len(b):return 1 if len(a)>len(b) else -1
    for x,y in zip(reversed(a),reversed(b)):
        if x!=y:return 1 if x>y else -1
    return 0


def add(a,b):
    a=norm(a);b=norm(b);out=[];carry=0
    for i in range(max(len(a),len(b))):
        t=(a[i] if i<len(a) else 0)+(b[i] if i<len(b) else 0)+carry
        need(t<1<<32,'word bound');out.append(t&MASK);carry=t>>BITS
    if carry:out.append(carry)
    return norm(out)


def subtract(a,b):
    need(compare(a,b)>=0,'negative limb subtraction');out=[];borrow=0
    for i,x in enumerate(a):
        t=x-(b[i] if i<len(b) else 0)-borrow
        borrow=1 if t<0 else 0;out.append(t+BASE if borrow else t)
    need(borrow==0,'undrained borrow');return norm(out)


def multiply(a,b):
    a=norm(a);b=norm(b);out=[0]*(len(a)+len(b)+1)
    for i,x in enumerate(a):
        carry=0
        for j,y in enumerate(b):
            t=out[i+j]+x*y+carry
            need(t<1<<32,'raw limb product bound')
            out[i+j]=t&MASK;carry=t>>BITS
        k=i+len(b)
        while carry:
            t=out[k]+carry;need(t<1<<32,'limb carry bound')
            out[k]=t&MASK;carry=t>>BITS;k+=1
    return norm(out)


def shift_bit(a,bit):
    need(bit in (0,1),'bit input');out=[];carry=bit
    for x in a:
        t=(x<<1)+carry;need(t<1<<32,'shift bound')
        out.append(t&MASK);carry=t>>BITS
    if carry:out.append(carry)
    return norm(out)


def divide(a,b):
    a=norm(a);b=norm(b);need(b,'zero divisor')
    q=[];r=[]
    for limb in reversed(a):
        for bit in range(BITS-1,-1,-1):
            r=shift_bit(r,(limb>>bit)&1);q=shift_bit(q,0)
            if compare(r,b)>=0:
                r=subtract(r,b)
                if q:q[0]|=1
                else:q=[1]
    return norm(q),norm(r)


def encode(x):
    need(x>=0,'nonnegative test integer');out=[]
    while x:out.append(x&MASK);x>>=BITS
    return out


def decode(a):
    return sum(x<<(BITS*i) for i,x in enumerate(a))


def check():
    rng=Random(20261022);cases=0
    for size in (1,15,31,64,129,257,513):
        for _ in range(6):
            x=rng.getrandbits(size);y=rng.getrandbits(max(1,size-3)) or 1
            a=encode(x);b=encode(y)
            need(decode(add(a,b))==x+y,'limb addition reference')
            need(decode(multiply(a,b))==x*y,'limb multiplication reference')
            q,r=divide(a,b);need((decode(q),decode(r))==divmod(x,y),'long-division reference')
            if x>=y:need(decode(subtract(a,b))==x-y,'limb subtraction reference')
            cases+=1
    try:divide([1],[])
    except ValueError:pass
    else:raise ValueError('zero denominator accepted')
    return dict(status='PASS',arithmetic_cases=cases,limb_bits=BITS,maximum_allowed_raw_bits=32,
                zero_denominator_control=True,scope='explicit polynomial-cost multiword setup arithmetic, not unit-cost unbounded integers')


if __name__=='__main__':print(json.dumps(check(),indent=2))
