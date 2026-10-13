"""Exact integer checks of the explicit uniform precision budgets."""
from pathlib import Path
import argparse,json,math

def need(ok,msg):
    if not ok:raise ValueError(msg)
def ceil_log2(n):
    need(type(n)==int and n>0,'positive integer log argument')
    return (n-1).bit_length()
def prime_power_data(r):
    need(type(r)==int and r>=3,'radix')
    prime=next((d for d in range(2,math.isqrt(r)+1) if r%d==0),r)
    q=r
    while q%prime==0:q//=prime
    need(q==1,'prime power')
    return r-r//prime
def budgets(r,p):
    D=prime_power_data(r);need(type(p)==int and p>=1,'target bits')
    n=r-1;ell=ceil_log2(r);d=1+2*ell+r*n*D;g=d+ell+2*r+2;a=ell+n*g
    e=max(d+1,a+1,p+2*a+3);b=max(n*ell,e+r+3)
    w=max(2*g+ceil_log2(14*n),p+(n+2)*g+ceil_log2(28*n*(r+1)))
    return dict(radix=r,target_bits=p,n=n,D=D,ell=ell,d=d,g=g,a=a,e=e,b=b,w=w)
def check(x):
    r,p,n,D,ell,d,g,a,e,b,w=(x[k] for k in ('radix','target_bits','n','D','ell','d','g','a','e','b','w'))
    need(D==prime_power_data(r) and n==r-1 and ell==ceil_log2(r),'kernel parameters')
    need(d>=1+2*ell+r*(n*D-1),'delta bound exponent')
    need(g>=d+ell+2*r and g>=2,'root gap exponent')
    need(a>=ell+n*g,'inverse prefix bound')
    need(e>=d+1 and e>=a+1 and e>=p+2*a+3,'factor perturbation budget')
    need(b>=n*ell and b>=e+r+3,'approximate factorization precision')
    need(w-2*g>=ceil_log2(14*n),'rounded recurrence growth budget')
    gap=w-p-(n+2)*g-1
    need(gap>=0 and 14*n*(r+1)<=1<<gap,'final rounding error budget')
    # For smaller instances also check the exact PR621 denominator.
    if r<=32:
        den=2*r*n*((1<<r)-1)**(n*D-1)
        need(den<=1<<d,'direct exact delta inequality')
    return True
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',required=True,type=Path);args=ap.parse_args()
    records=[]
    for r in range(3,257):
        try:prime_power_data(r)
        except ValueError:continue
        for p in (1,32,128,1024,1048576):
            x=budgets(r,p);check(x);records.append(x)
    controls=[]
    for name,key,value in [('gap','g',1),('factor_precision','e',1),('execution_precision','w',128),('degree','n',5)]:
        x=budgets(9,128);x[key]=value
        try:check(x)
        except ValueError as err:controls.append(dict(name=name,rejected=str(err)))
        else:raise ValueError('corrupt budget accepted')
    for r in (2,6,10,15):
        try:budgets(r,128)
        except ValueError as err:controls.append(dict(name='unsupported_radix_'+str(r),rejected=str(err)))
        else:raise ValueError('nonprimepower accepted')
    args.out.write_text(json.dumps(dict(status='passed',records=records,controls=controls,scope='Finite integer budget checks supporting PROOF.md; not a proof of Pan factorization or full multiplication.'),indent=2)+'\n')
    print(json.dumps(dict(status='passed',radices=len(records)//5,cases=len(records),controls=len(controls))))
if __name__=='__main__':main()
