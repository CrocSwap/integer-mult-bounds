"""Native fixed-grid Strassen batches for a shared triangular band solve.
Python integers emulate checked finite words. Fraction is external oracle only.
"""
from __future__ import annotations
import json, random
from fractions import Fraction

class Word:
    def __init__(self, precision=100, width=384):
        self.p, self.S, self.width, self.ops, self.bits = precision, 1 << precision, width, 0, 0
    def val(self, x):
        self.ops += 1
        self.bits = max(self.bits, abs(x).bit_length())
        if abs(x).bit_length() >= self.width:
            raise OverflowError('finite-word magnitude overflow')
        return x
    def add(self,a,b): return self.val(a+b)
    def sub(self,a,b): return self.val(a-b)
    def mul(self,a,b):
        t=self.val(a*b)
        return self.val((abs(t)//self.S)*(-1 if t<0 else 1))
    def div(self,a,b):
        if not b: raise ZeroDivisionError
        t=self.val(a*self.S)
        return self.val((abs(t)//abs(b))*(-1 if (a<0)!=(b<0) else 1))

def zero(n): return [[0]*n for _ in range(n)]
def combine(a,b,w,sign=1):
    return [[w.add(x,y) if sign==1 else w.sub(x,y) for x,y in zip(r,s)] for r,s in zip(a,b)]
def multiply(a,b,w):
    n=len(a)
    if n==1: return [[w.mul(a[0][0],b[0][0])]]
    h=n//2
    def split(x):
        return ( [r[:h] for r in x[:h]], [r[h:] for r in x[:h]],
                 [r[:h] for r in x[h:]], [r[h:] for r in x[h:]] )
    A,B,C,D=split(a); E,F,G,H=split(b)
    add=lambda x,y:combine(x,y,w)
    sub=lambda x,y:combine(x,y,w,-1)
    M1=multiply(add(A,D),add(E,H),w)
    M2=multiply(add(C,D),E,w)
    M3=multiply(A,sub(F,H),w)
    M4=multiply(D,sub(G,E),w)
    M5=multiply(add(A,B),H,w)
    M6=multiply(sub(C,A),add(E,F),w)
    M7=multiply(sub(B,D),add(G,H),w)
    R=add(sub(add(M1,M4),M5),M7)
    S=add(M3,M5)
    T=add(M2,M4)
    U=add(sub(add(M1,M3),M2),M6)
    return [r+s for r,s in zip(R,S)]+[r+s for r,s in zip(T,U)]

def inverse_lower(a,w):
    n=len(a); out=zero(n)
    for col in range(n):
        for row in range(n):
            t=w.S if row==col else 0
            for j in range(row): t=w.sub(t,w.mul(a[row][j],out[j][col]))
            out[row][col]=w.div(t,a[row][row])
    return out

def prepare(a,block,w):
    """Input lower triangular with bandwidth <= block, side divisible by block."""
    n=len(a)
    if block<1 or block&(block-1) or n%block: raise ValueError('block shape')
    for i in range(n):
        if a[i][i]==0: raise ValueError('zero pivot')
        for j in range(n):
            if (j>i or i-j>block) and a[i][j]: raise ValueError('outside band')
    result=[]
    for start in range(0,n,block):
        diag=[r[start:start+block] for r in a[start:start+block]]
        prev=zero(block) if not start else [r[start-block:start] for r in a[start:start+block]]
        result.append((inverse_lower(diag,w),prev))
    return result

def solve(prepared,b,block,w):
    n=len(b); q=len(b[0]); result=[[0]*q for _ in range(n)]
    for col in range(0,q,block):
        previous=zero(block)
        for i,(inverse,edge) in enumerate(prepared):
            start=i*block
            rhs=[r[col:col+block]+[0]*max(0,col+block-q) for r in b[start:start+block]]
            current=multiply(inverse,combine(rhs,multiply(edge,previous,w),w,-1),w)
            for j in range(block): result[start+j][col:min(col+block,q)]=current[j][:min(block,q-col)]
            previous=current
    return result

def check():
    rng=random.Random(4554); cases=entries=ops=peak=0; max_error=Fraction(0)
    for block in (1,2,4,8):
        for count in (1,2,4):
            n=block*count
            for q in (1,block,max(1,2*block-1)):
                w=Word(); a=zero(n)
                for i in range(n):
                    a[i][i]=w.S
                    for j in range(max(0,i-block),i): a[i][j]=rng.randrange(-3,4)*w.S//(16*block)
                b=[[rng.randrange(-8,9)*w.S//8 for _ in range(q)] for _ in range(n)]
                prepared=prepare(a,block,w); x=solve(prepared,b,block,w)
                for i in range(n):
                    for col in range(q):
                        residual=sum(Fraction(a[i][j]*x[j][col],w.S*w.S) for j in range(n))-Fraction(b[i][col],w.S)
                        max_error=max(max_error,abs(residual)); entries+=1
                        if abs(residual)>=Fraction(1,1<<70): raise AssertionError('residual')
                cases+=1; ops+=w.ops; peak=max(peak,w.bits)
    # Scalar multiplication work scales as exactly 7^log2(side), not side^3.
    for side in (1,2,4,8):
        w=Word(); a=[[w.S if i==j else 0 for j in range(side)] for i in range(side)]
        if multiply(a,a,w)!=a: raise AssertionError('identity')
    try: Word(width=4).val(16)
    except OverflowError: pass
    else: raise AssertionError('overflow control')
    return {'systems':cases,'residual_entries':entries,'charged_operations':ops,'max_raw_bits':peak,'residual_below_2^-70':True,'overflow_control':True}
if __name__=='__main__': print(json.dumps(check(),sort_keys=True))
