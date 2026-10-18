"""Integer lifting for cyclic inverse shears using borrowed dirty arrays.
Exact rational prototype. Arithmetic workspace and phase access are charged in the proof;
this is not a common-label Clifford word or a bit-reversible arithmetic compiler.
"""
from pathlib import Path
from fractions import Fraction as F
import importlib.util,json,argparse,itertools
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('weighted',P/'weighted.py');w=importlib.util.module_from_spec(s);s.loader.exec_module(w);c=w.c

def scaled(z,q):return(z[0]*q,z[1]*q)
def conj(z):return(z[0],-z[1])
def ordered(n,d):return range(n)if d==1 else range(n-1,-1,-1)

def lift(x,y,coefficient,beta,bits,d,sign=1,destination=None,multiplier=None,stats=None):
    """y += sign*F(x), restoring x exactly; no length-dependent clean data array."""
    n=len(x);c.need(x is not y and n==len(y)>0,'distinct equally sized arrays')
    c.need(d in(-1,1)and sign in(-1,1),'orientation and sign')
    c.need(0<beta<=1 and F(1,1<<bits)<=beta*beta/2,'closure precision')
    c.need(all(c.norm2(coefficient(i))<=(1-beta)**2 for i in range(n)),'stable coefficients')
    c.need(all(c.rounded(z,bits)==z for z in itertools.chain(x,y)),'fixed grid data')
    destination=destination or (lambda i:i);multiplier=multiplier or (lambda i:c.ONE)
    power=c.ONE;previous=None
    for i in ordered(n,d):
        if previous is not None:x[i]=c.add(x[i],c.rounded(c.mul(coefficient(i),x[previous]),bits))
        power=c.rounded(c.mul(coefficient(i),power),bits);previous=i
    denominator=c.sub(c.ONE,power);c.need(c.norm2(denominator)>=(beta/2)**2,'closure denominator')
    seed=c.rounded(c.div(x[previous],denominator),bits)
    power=c.ONE
    for i in ordered(n,d):
        power=c.rounded(c.mul(coefficient(i),power),bits)
        value=c.add(x[i],c.rounded(c.mul(power,seed),bits))
        value=c.rounded(c.mul(multiplier(i),value),bits)
        j=destination(i);y[j]=c.add(y[j],scaled(value,sign))
    # The scalar seed and coefficient scratch may be cleared by ordinary classical
    # arithmetic. The dirty data itself is restored by exact inverse integer lifts.
    first=0 if d==1 else n-1
    for i in ordered(n,-d):
        if i!=first:x[i]=c.sub(x[i],c.rounded(c.mul(coefficient(i),x[i-d]),bits))
    if stats is not None:stats['leaves']+=1;stats['scalar_steps']+=3*n

def leaf(x,y,factor,phases,beta,bits,d,sign,stats):
    inside,b,scale=factor;n=len(x)
    if inside:
        lift(x,y,lambda i:c.mul(b,conj(phases[(i+d)%n])),beta,bits,-d,sign,
             lambda i:(i-d)%n,lambda i:scaled(conj(phases[i]),scale),stats)
    else:
        lift(x,y,lambda i:c.mul(b,phases[i]),beta,bits,d,sign,
             multiplier=lambda i:scaled(c.neg(b),scale),stats=stats)

def compose(x,y,factors,scratch,phases,beta,bits,d,sign=1,stats=None):
    """Balanced commutator; negative call is the exact inverse instruction word."""
    c.need(sign in(-1,1)and d in(-1,1),'orientation and sign')
    c.need(factors and len(scratch)>=(len(factors)-1).bit_length(),'dirty depth')
    arrays=[x,y]+scratch;c.need(len({id(v)for v in arrays})==len(arrays),'all ancestor arrays distinct')
    c.need(len(x)>0 and all(len(v)==len(x)for v in arrays)and len(phases)==len(x),'array lengths')
    c.need(all(c.norm2(t)==1 for t in phases),'unit phases')
    if len(factors)==1:return leaf(x,y,factors[0],phases,beta,bits,d,sign,stats)
    mid=len(factors)//2;B,A=factors[:mid],factors[mid:];z=scratch[0];rest=scratch[1:]
    operations=[(x,z,B,1),(z,y,A,1),(x,z,B,-1),(z,y,A,-1)]
    if sign==-1:operations=[(src,dst,fs,-sgn)for src,dst,fs,sgn in reversed(operations)]
    for src,dst,fs,sgn in operations:compose(src,dst,fs,rest,phases,beta,bits,d,sgn,stats)

def exact_operator(x,factors,phases,d):
    # Dense rational oracle constructed independently from the lifting recurrence.
    n=len(x);out=x[:]
    for inside,b,scale in factors:
        a=[[c.ZERO for _ in range(n)]for _ in range(n)]
        if inside:
            for i in range(n):a[i][i]=c.neg(b);a[i][(i-d)%n]=c.add(a[i][(i-d)%n],phases[i])
        else:
            rho=c.div(c.ONE,b)
            for i in range(n):a[i][i]=c.neg(rho);a[i][(i-d)%n]=c.add(a[i][(i-d)%n],phases[i])
        out=[scaled(z,scale)for z in w.solve(a,out)]
    return out

def certificate(n,beta,r,D,bits):
    N=4*n*n;a=13*(r+1)/beta**3;G=2+F(r)/beta;u=F(1,1<<bits)
    c.need(a*u<=1 and u<=beta**2/2,'uniform precision')
    return N*a*(D+1)*u*G**(N-1)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    units=[c.ONE,(F(0),F(1)),(F(3,5),F(4,5)),(F(-5,13),F(12,13))]
    cases=[];controls=[];generic=[]
    for beta in(F(1,2),F(1,16),F(1,4096)):
        for n in(1,2,3,8,17,64):
            bs=[scaled(units[(i*i+i+1)%4],(1-beta)/(1+i%2))for i in range(n)]
            original=[(F(i%5-2,4),F(i%7-3,8))for i in range(n)]
            for d in(-1,1):
                x=original[:];y=[(F(19+i,4),F(3-i,8))for i in range(n)];y0=y[:];bits=128
                lift(x,y,lambda i:bs[i],beta,bits,d);c.need(x==original,'exact source restoration')
                net=[c.sub(z,t)for z,t in zip(y,y0)];B=max(abs(a)+abs(b)for a,b in original);bound=13*(B+1)*F(1,1<<bits)/beta**3
                matrix=[[c.ZERO for _ in range(n)]for _ in range(n)]
                for i in range(n):matrix[i][i]=c.ONE;matrix[i][(i-d)%n]=c.sub(matrix[i][(i-d)%n],bs[i])
                w.residual(original,net,matrix,(2-beta)*bound)
                if n<=8:c.need(all(c.norm2(c.sub(z,t))<=bound**2 for z,t in zip(net,w.solve(matrix,original))),'leaf dense')
                lift(x,y,lambda i:bs[i],beta,bits,d,-1);c.need(y==y0 and x==original,'exact leaf cancellation')
                generic.append(dict(beta=str(beta),length=n,direction=d,dense=n<=8))
    for nf in(1,2,3,5,8):
        factors=[(i%2==0,(F(1,4),F((-1)**i,8)),F(3)if i==0 else F(1))for i in range(nf)]
        for n in(1,2,3,8):
            for d in(-1,1):
                for dirt in(0,7,-13):
                    x=[(F(i%5-2,4),F(i%3-1,8))for i in range(n)];x0=x[:]
                    y=[(F(dirt+i,4),F(dirt-i,8))for i in range(n)];y0=y[:]
                    scratch=[[(F(dirt+2*i+j,4),F(dirt-3*i-j,8))for i in range(n)]for j in range((nf-1).bit_length())];s0=[z[:]for z in scratch]
                    phases=[units[(i*i+3*i+1)%4]for i in range(n)];bits=4096;stats=dict(leaves=0,scalar_steps=0)
                    D=max(abs(a)+abs(b)for v in[x,y]+scratch for a,b in v);bound=certificate(nf,F(1,2),3,D,bits)
                    compose(x,y,factors,scratch,phases,F(1,2),bits,d,stats=stats)
                    c.need(x==x0 and scratch==s0,'exact dirty restoration')
                    expected=exact_operator(x0,factors,phases,d);net=[c.sub(z,t)for z,t in zip(y,y0)]
                    c.need(all(c.norm2(c.sub(z,t))<=bound**2 for z,t in zip(net,expected)),'commutator dense')
                    calls=stats['leaves'];c.need(calls<=4*nf*nf,'quadratic leaf count')
                    compose(x,y,factors,scratch,phases,F(1,2),bits,d,-1)
                    c.need(x==x0 and scratch==s0 and y==y0,'exact whole word inverse')
                    cases.append(dict(factors=nf,length=n,direction=d,dirt=dirt,leaf_calls=calls,dirty_arrays=len(scratch),bound=str(bound)))
        print('PASS factors',nf,flush=True)
    def reject(name,fn):
        try:fn()
        except ValueError as e:controls.append(dict(name=name,rejected=str(e)))
        else:raise ValueError('control accepted '+name)
    x=[c.ONE,c.ZERO];y=[c.ZERO,c.ONE];fs=[(True,(F(1,4),F(0)),F(1))]*2
    reject('borrowed_outer_target',lambda:compose(x,y,fs,[y],[c.ONE]*2,F(1,2),128,1))
    reject('borrowed_source',lambda:compose(x,y,fs,[x],[c.ONE]*2,F(1,2),128,1))
    reject('missing_dirty_level',lambda:compose(x,y,fs,[],[c.ONE]*2,F(1,2),128,1))
    reject('nonunit_phase',lambda:compose(x,y,fs,[[c.ZERO]*2],[c.ONE,(F(2),F(0))],F(1,2),128,1))
    reject('underprecision',lambda:lift(x,y,lambda i:c.ZERO,F(1,16),4,1))
    reject('unstable_site',lambda:lift(x,y,lambda i:c.ONE,F(1,2),128,1))
    reject('off_grid_source',lambda:lift([(F(1,3),F(0))]*2,y,lambda i:c.ZERO,F(1,2),128,1))
    args.out.write_text(json.dumps(dict(status='passed',generic=generic,cases=cases,controls=controls,scope='Classical fixed-grid dirty-array shear; excludes bit-reversible arithmetic and full multiplication reduction'),indent=2)+'\n')
    print('PASS',len(generic),'leaf cases',len(cases),'compositions',len(controls),'controls')
if __name__=='__main__':main()
