"""Exact input-independent certificate, not a native Tile/page execution.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from dataclasses import dataclass
from fractions import Fraction
from math import isqrt

def need(value,message):
    if not value:raise ValueError(message)
def ceil_div(a,b):return -((-a)//b)
def ceil_log2(n):
    need(n>0,'positive logarithm');return (n-1).bit_length()
def trunc_div(a,b):return (-1 if a<0 else 1)*(abs(a)//b)

@dataclass(frozen=True)
class Certificate:
    s:int;t:int;alpha:int;q:int;b:int;P:int;sigma:int
    source_start:int;source_count:int;blocks:int

    @classmethod
    def make(cls,s,t,alpha,q):
        need(all(type(v) is int for v in (s,t,alpha,q)),'integer source descriptors')
        need(q>=101 and alpha>=2 and alpha*alpha<q,'production block precision/alpha')
        need(0<s<t<2*s,'original near-one ratio')
        need(max(s,t,alpha).bit_length()<=q,'actual fits metadata')
        root=isqrt(q)+(isqrt(q)**2!=q);b=alpha*root
        need(3*b+3<=4*q and 4*b+2<=5*q,'actual uniform short-block guards')
        P=32768*q;sigma=4096*q
        need(P>=2*sigma+q+ceil_log2(32*(3*b+4))+12,'actual complete tile precision guard')
        need(P-4256*q>=2 and 3936*q>=2,'positive lower and strict unit upper A/B')
        return cls(s,t,alpha,q,b,P,sigma,-b-1,s+2*b+3,ceil_div(t,b))

    def block(self,v,m):
        need(0<=v<v+m<=self.t and 1<=m<=self.b,'declared full-period block')
        j0=(self.s*v)//self.t;gamma=Fraction(j0)-Fraction(self.s*v,self.t)
        high=ceil_div(self.s*(v+m-1),self.t)+self.b+2
        low=j0-self.b-1;n=high-low;nc=n+m-1
        return dict(v=v,m=m,j0=j0,gamma=gamma,start=low,end=high,n=n,nc=nc,
                    width=self.P+ceil_log2(n+1)+3,extract=self.P-self.q-2*self.sigma)

    def block_sequence(self):
        for v in range(0,self.t,self.b):yield self.block(v,min(self.b,self.t-v))

    def exponents(self,block,h,z):
        k=Fraction(self.s,self.t);g=block['gamma'];u=self.alpha*self.alpha
        return (((1-k)*h*h+2*g*h+g*g)/u,
                ((k*k-k)*z*z-2*g*k*z)/u,k*(h-z)**2/u)

def final_budget(D,Kf,Kc,q,tau):
    need(D>=1 and Kf>=D and Kc>=0,'declared normalizer shares')
    J=Kf-D;Gamma=Kf+Kc
    error=(Fraction(12,1<<J)+2)/(1<<q)
    restored=Fraction(3,2)*(1<<Gamma)*error
    return dict(J=J,Gamma=Gamma,error=error,restored=restored,
                admitted=q>=Gamma+tau+5,threshold=Fraction(1,1<<tau))
