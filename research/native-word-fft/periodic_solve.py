"""Native real periodic band inverse with reusable factors, Apache-2.0.
Dugongue with substantial OpenAI Codex assistance.
Exact Fraction arithmetic is confined to independent check residuals.
"""
from pathlib import Path
from fractions import Fraction
from random import Random
import json


def need(ok,why):
    if not ok:raise ValueError(why)


def band_class():
    p=Path(__file__).with_name('band_solve.py');scope={'__name__':'periodic_band','__file__':str(p)}
    exec(compile(p.read_bytes(),str(p),'exec'),scope)
    return scope['BandSystem']


class PeriodicSystem:
    def __init__(self,a,h,p,width):
        self.n=len(a);self.h=h;self.p=p;self.S=1<<p;self.width=width
        self.limit=1<<width;self.operations=0;self.peak=0
        n=self.n;S=self.S
        need(h>=1 and n>2*h and all(len(row)==2*h+1 for row in a),'periodic band shape')
        for i,row in enumerate(a):
            need(abs(row[h]-S)+sum(abs(x) for j,x in enumerate(row) if j!=h)<=S//8,'periodic near-identity contract')
            for x in row:self.val(x)
        boundary=list(range(h))+list(range(n-h,n));self.boundary=boundary
        r=len(boundary);positions={j:k for k,j in enumerate(boundary)}
        ordinary=[list(row) for row in a];U=[[0]*r for _ in range(n)]
        for i in range(n):
            for d in range(-h,h+1):
                if not 0<=i+d<n:
                    j=(i+d)%n;U[i][positions[j]]=ordinary[i][d+h];ordinary[i][d+h]=0
        BandSystem=band_class();self.band=BandSystem(ordinary,h,p,width)
        self.operations+=self.band.preparation['operations'];self.peak=max(self.peak,self.band.preparation['maximum_bits'])
        self.X=[[0]*r for _ in range(n)]
        for j in range(r):
            out=self.band.solve([row[j] for row in U]);self.account(out)
            for i,x in enumerate(out['solution']):self.X[i][j]=x
        small=[[0]*(2*r-1) for _ in range(r)]
        for i,row_index in enumerate(boundary):
            for j in range(r):small[i][j-i+r-1]=self.val(self.X[row_index][j]+(S if i==j else 0))
        self.small=BandSystem(small,r-1,p,width)
        self.operations+=self.small.preparation['operations'];self.peak=max(self.peak,self.small.preparation['maximum_bits'])
        self.setup_operations=self.operations

    def val(self,x):
        need(abs(x)<self.limit,'word overflow')
        self.operations+=1;self.peak=max(self.peak,abs(x).bit_length());return x

    def account(self,out):
        self.operations+=out['operations'];self.peak=max(self.peak,out['maximum_bits'])

    def solve(self,rhs):
        before=self.operations
        out=self.band.solve(rhs);self.account(out);y=out['solution']
        out=self.small.solve([y[i] for i in self.boundary]);self.account(out);z=out['solution']
        answer=[]
        for i in range(self.n):
            correction=0
            for a,b in zip(self.X[i],z):correction=self.val(correction+self.val(a*b))
            answer.append(self.val(y[i]-correction//self.S))
        return dict(solution=answer,operations=self.operations-before,maximum_bits=self.peak)


def check():
    rng=Random(20261022);systems=solves=rows=0;worst=Fraction(0);peak=0
    for n,h in ((5,1),(11,2),(25,3)):
        p=96;S=1<<p
        a=[[0]*(2*h+1) for _ in range(n)]
        for i in range(n):
            a[i][h]=S
            for d in range(-h,h+1):
                if d:a[i][d+h]=rng.randrange(-4,5)*(S//(256*h))
        system=PeriodicSystem(a,h,p,256)
        for _ in range(3):
            truth=[rng.randrange(-S,S) for _ in range(n)]
            rhs=[sum(a[i][d+h]*truth[(i+d)%n]//S for d in range(-h,h+1)) for i in range(n)]
            out=system.solve(rhs)
            residual=max(abs(sum(Fraction(a[i][d+h],S)*out['solution'][(i+d)%n] for d in range(-h,h+1))-rhs[i]) for i in range(n))
            need(residual<100000*(h+1)**4,'periodic solve residual envelope')
            worst=max(worst,residual/S);peak=max(peak,out['maximum_bits']);solves+=1;rows+=n
        systems+=1
    return dict(status='PASS',periodic_systems=systems,reused_rhs_solves=solves,
                rows_checked=rows,maximum_bits=peak,maximum_normalized_residual=str(worst),
                scope='real periodic band/Woodbury model with paid reusable factors; complex extension proof-level')


if __name__=='__main__':print(json.dumps(check(),indent=2))
