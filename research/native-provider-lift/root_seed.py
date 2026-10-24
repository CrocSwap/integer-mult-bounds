"""Native bounded-word Gaussian root seeds; no TM, FFT or root oracle.
Apache-2.0. Dugongue with substantial OpenAI Codex assistance.
Signed values below are represented by a sign bit and a bounded magnitude.
"""
import json
from decimal import Decimal,localcontext


def need(p,msg):
    if not p:raise ValueError(msg)

class Bound:
    def __init__(self,w):self.limit=1<<w;self.ops=0;self.high_bits=0
    def value(self,x,cost=1):
        self.ops+=cost;self.high_bits=max(self.high_bits,abs(x).bit_length())
        need(abs(x)<self.limit,'finite-word overflow');return x


def trunc_div(x,d):
    return x//d if x>=0 else -((-x)//d)


def root_seed(order,p,word_width=None):
    need(order>=1 and p>=1,'root seed shape')
    P=8*(p+16);S=1<<P;K=128*(p+1)
    w=max(2*P+20,order.bit_length()+1) if word_width is None else word_width
    need(w>=2*P+20 and order<(1<<w),'word-width contract')
    v=Bound(w);v.value(order);v.value(S)
    def atan_inverse(q):
        power=q;j=0;acc=0
        while power<=S:
            den=v.value(power*(2*j+1),4)
            term=v.value(S//den,1)
            acc=v.value(acc+term if j%2==0 else acc-term,5)
            power=v.value(power*q*q,2);j=v.value(j+1,2)
        return acc
    a5=atan_inverse(5);a239=atan_inverse(239)
    pi=v.value((a5<<4)-(a239<<2),5)
    theta=v.value((pi<<1)//order,3)
    need(0<=theta<=8*S,'angle enclosure')
    ar=S;ai=0;sr=S;si=0
    for k in range(1,K+1):
        den=v.value(S*k,2)
        nr=v.value(trunc_div(v.value(-ai*theta,2),den),4)
        ni=v.value(trunc_div(v.value(ar*theta,2),den),4)
        ar,ai=nr,ni
        sr=v.value(sr+ar,6);si=v.value(si+ai,6)
    shift=P-p;half=1<<(shift-1)
    def nearest(x):
        z=v.value((abs(x)+half)>>shift,5)
        return z if x>=0 else -z
    real,imag=nearest(sr),nearest(si)
    error_numerator=40*(P+2)+1+4096*K+32
    # Seed internal error <= error_numerator/2^P; nearest rounding adds 2^(-p-1).
    need((error_numerator<<(p+1))<(1<<P),'root error proof inequality')
    need(v.ops<=100*(P+1)+40*(K+1),'root operation envelope')
    return dict(real=real,imag=imag,fraction_bits=p,working_bits=P,order=order,
                internal_error_numerator=error_numerator,internal_error_scale_bits=P,
                max_coordinate_error_power=-p,word_width=w,largest_intermediate_bits=v.high_bits,
                charged_word_operations=v.ops)


def decimal_reference(order,p):
    # Independent high-precision validation only; never part of the native runtime.
    digits=int(p*.302)+60
    with localcontext() as ctx:
        ctx.prec=digits
        tol=Decimal(10)**(-(digits-10))
        def atan(q):
            q=Decimal(q);power=q;j=0;s=Decimal(0)
            while True:
                t=1/(power*(2*j+1));s+=t if j%2==0 else -t
                if t<tol:break
                power*=q*q;j+=1
            return s
        pi=16*atan(5)-4*atan(239);t=2*pi/Decimal(order)
        tr=sr=Decimal(1);ti=si=Decimal(0)
        for k in range(1,10000):
            tr,ti=-ti*t/k,tr*t/k;sr+=tr;si+=ti
            if abs(tr)+abs(ti)<tol:break
        return +sr,+si


def check():
    cases=0;ops=0;peak=0
    for p in (1,2,4,8,16,32,64,128):
        for order in (1,2,3,4,5,8,16,97,1009,(1<<40)+87):
            out=root_seed(order,p)
            x,y=decimal_reference(order,p)
            with localcontext() as ctx:
                ctx.prec=max(90,int(p*.302)+50)
                scale=Decimal(2)**p;err=Decimal(2)**(-p)
                need(abs(Decimal(out['real'])/scale-x)<err,'real root error')
                need(abs(Decimal(out['imag'])/scale-y)<err,'imaginary root error')
            need(out['largest_intermediate_bits']<out['word_width'],'bounded native intermediate')
            cases+=1;ops+=out['charged_word_operations'];peak=max(peak,out['largest_intermediate_bits'])
    try:root_seed(17,8,32)
    except ValueError:pass
    else:raise ValueError('undersized word accepted')
    r=root_seed(4,16)
    need((r['real'],r['imag'])==(0,1<<16),'exact quarter root')
    return dict(status='PASS',root_seed_cases=cases,charged_native_word_operations=ops,
                maximum_intermediate_bits=peak,undersized_word_rejected=True,
                no_root_or_TM_oracle=True,uses_only_bounded_word_products=True,
                emitted_RamStd_program=False,Lean_proof=False)

if __name__=='__main__':print(json.dumps(check(),indent=2))
