"""Exact certificates for varying unit phases on a cyclic neighbor shift."""
from pathlib import Path
from fractions import Fraction as F
import argparse, importlib.util, json
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('kernel',P/'check.py');k=importlib.util.module_from_spec(s);s.loader.exec_module(k)
c=k.c

def scan(x,bs,beta,bits,direction):
    c.need(len(x)>0 and len(bs)==len(x),'coefficient length')
    c.need(direction in (-1,1),'direction')
    c.need(0<beta<=1 and all(c.norm2(b)<=(1-beta)**2 for b in bs),'stable coefficients')
    c.need(F(1,1<<bits)<=beta*beta/2,'closure precision')
    order=range(len(x)) if direction==1 else range(len(x)-1,-1,-1)
    z,power=c.ZERO,c.ONE
    for i in order:
        z=c.rounded(c.add(x[i],c.mul(bs[i],z)),bits)
        power=c.rounded(c.mul(bs[i],power),bits)
    den=c.sub(c.ONE,power)
    c.need(c.norm2(den)>=(beta/2)**2,'closure denominator')
    previous=c.rounded(c.div(z,den),bits);y=[c.ZERO]*len(x)
    for i in order:
        previous=c.rounded(c.add(x[i],c.mul(bs[i],previous)),bits);y[i]=previous
    return y

def apply(x,state,phases,direction,wrong_phase=False):
    n=len(x);c.need(n>0 and len(phases)==n,'phase length')
    c.need(all(c.norm2(t)==1 for t in phases),'unit phases')
    y=[(v[0]*state['radix'],v[1]*state['radix'])for v in x]
    for inside,b in state['factors']:
        if inside:
            inv=[(phases[(i+direction)%n][0],-phases[(i+direction)%n][1])for i in range(n)]
            if wrong_phase:inv=[(v[0],-v[1])for v in phases]
            bs=[c.mul(b,t)for t in inv]
            y=scan(y,bs,state['beta'],state['bits'],-direction)
            y=[c.rounded(c.mul(inv[i],y[(i+direction)%n]),state['bits'])for i in range(n)]
        else:
            y=scan(y,[c.mul(b,t)for t in phases],state['beta'],state['bits'],direction)
            y=[c.rounded(c.neg(c.mul(b,v)),state['bits'])for v in y]
    return y

def matrix(q,phases,direction):
    # Independently expand W^j entry-by-entry, including wrap-around phases.
    n=len(phases);a=[[c.ZERO for _ in range(n)]for _ in range(n)]
    for i in range(n):
        weight=c.ONE
        for j,v in enumerate(q):
            col=(i-direction*j)%n;a[i][col]=c.add(a[i][col],c.mul(v,weight))
            weight=c.mul(weight,phases[col])
    return a

def residual(x,y,a,bound):
    for i,row in enumerate(a):
        v=c.ZERO
        for z,t in zip(row,y):v=c.add(v,c.mul(z,t))
        c.need(c.norm2(c.sub(v,x[i]))<=bound**2,'expanded weighted residual')

def solve(a,x):
    a=[row[:]+[v]for row,v in zip(a,x)];n=len(a)
    for j in range(n):
        i=next(i for i in range(j,n)if a[i][j]!=c.ZERO);a[i],a[j]=a[j],a[i]
        z=a[j][j];a[j]=[c.div(v,z)for v in a[j]]
        for i in range(n):
            if i!=j:
                z=a[i][j];a[i]=[c.sub(v,c.mul(z,t))for v,t in zip(a[i],a[j])]
    return [row[-1]for row in a]

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    units=[c.ONE,(F(0),F(1)),(F(3,5),F(4,5)),(F(-5,13),F(12,13))]
    cases=[];certs=[];generic=[];controls=[]
    for beta in (F(1,2),F(1,16),F(1,4096)):
        for n in (1,2,3,8,17,64):
            bs=[c.mul((1-beta,F(0)),units[(i*i+3*i+1)%4])for i in range(n)]
            # Alternate magnitudes as well as phases.
            bs=[(z[0]/(1+i%2),z[1]/(1+i%2))for i,z in enumerate(bs)]
            x=[(F(i%5-2,4),F(i%7-3,8))for i in range(n)]
            B=max(abs(z[0])+abs(z[1])for z in x);bound=6*(B+1)*F(1,1<<64)/beta**3
            for d in (-1,1):
                y=scan(x,bs,beta,64,d)
                m=[[c.ZERO for _ in range(n)]for _ in range(n)]
                for i in range(n):m[i][i]=c.ONE;m[i][(i-d)%n]=c.sub(m[i][(i-d)%n],bs[i])
                residual(x,y,m,beta*bound)
                if n<=8:c.need(all(c.norm2(c.sub(v,t))<=bound**2 for v,t in zip(y,solve(m,x))),'generic dense')
                generic.append(dict(beta=str(beta),length=n,direction=d,dense=n<=8))
    sigma,nu,phase_cert=k.irrational_gauge()
    for row in json.loads((P/'FACTORS.json').read_text()):
        if row['radix'] not in (4,9,16):continue
        st=k.certify(row);A=F(st['certificate']['inverse_norm_bound'])
        eps=F(st['certificate']['coefficient_error_bound'])+sum(j*(abs(v[0])+abs(v[1]))for j,v in enumerate(st['q']))*nu
        c.need(A*eps<1 and A*A*eps/(1-A*eps)+st['budgets'][-1]<=F(1,1<<row['target_bits']),'varying phase perturbation')
        certs.append(st['certificate'])
        for n in (1,2,3,8,17):
            x=[(F(i%5-2,4),F(i%7-3,8))for i in range(n)]
            for d in (-1,1):
                for oracle in (False,True):
                    pool=units+[sigma]if oracle else units
                    phases=[pool[(i*i+3*i+1)%len(pool)]for i in range(n)]
                    y=apply(x,st,phases,d);m=matrix(st['q'],phases,d)
                    residual(x,y,m,sum(abs(v[0])+abs(v[1])for v in st['q'])*st['budgets'][-1])
                    if n<=3:c.need(all(c.norm2(c.sub(v,t))<=st['budgets'][-1]**2 for v,t in zip(y,solve(m,x))),'kernel dense')
                    cases.append(dict(radix=row['radix'],embedding=row['embedding'],length=n,direction=d,oracle=oracle,dense=n<=3))
        print('PASS',row['radix'],row['embedding'],flush=True)
    st=k.certify(next(z for z in json.loads((P/'FACTORS.json').read_text())if z['radix']==9))
    x=[c.ONE,c.ZERO,(F(1,2),F(1,4))];phases=units[:3]
    def reject(name,fn):
        try:fn()
        except ValueError as e:controls.append(dict(name=name,rejected=str(e)))
        else:raise ValueError('control accepted: '+name)
    reject('wrong_inner_phase_index',lambda:residual(x,apply(x,st,phases,1,True),matrix(st['q'],phases,1),F(1,1<<128)))
    reject('nonunit_phase',lambda:apply(x,st,[c.ONE,c.ONE,(F(1),F(1))],1))
    reject('short_phase_array',lambda:apply(x,st,[c.ONE],1))
    reject('unstable_single_site',lambda:scan(x,[(F(1,2),F(0)),c.ONE,c.ZERO],F(1,2),64,1))
    reject('underprecision',lambda:scan(x,[c.ZERO]*3,F(1,16),4,1))
    reject('constant_phase_substitution',lambda:residual(x,apply(x,st,[c.ONE]*3,1),matrix(st['q'],phases,1),F(1,1<<128)))
    a.out.write_text(json.dumps(dict(status='passed',generic=generic,certificates=certs,cases=cases,phase_certificate=phase_cert,controls=controls),indent=2)+'\n')
    print(json.dumps(dict(status='passed',generic=len(generic),cases=len(cases),dense=sum(z['dense']for z in generic+cases),controls=len(controls))))
if __name__=='__main__':main()
