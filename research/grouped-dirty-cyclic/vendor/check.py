"""Rational proof of mixed inside/outside cyclic factor inversion."""
from pathlib import Path
from fractions import Fraction as F
import argparse,importlib.util,json,math,sys
sys.set_int_max_str_digits(100000)
P=Path(__file__).resolve().parent
def module(name):
    s=importlib.util.spec_from_file_location(name,P/(name+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
c=module('scan');ik=module('interval_kernel')

def prime_power(r):
    if type(r)!=int or r<3:return False
    p=next((d for d in range(2,math.isqrt(r)+1) if r%d==0),r)
    while r%p==0:r//=p
    return r==1

def certify(data):
    r,k=data['radix'],data['embedding']
    c.need(prime_power(r) and type(k)==int and 0<k<r and math.gcd(r,k)==1,'radix/embedding')
    ci=ik.kernel(r,k)
    beta=F(data['beta']);bits=data['working_bits'];target=data['target_bits'];fb=data['factor_bits']
    c.need(0<beta<=1 and type(bits)==int and bits>0 and type(target)==int and target>0,'precision budget')
    c.need(type(fb)==int and 0<fb<=1024,'factor bit declaration')
    roots=[tuple(F(v) for v in z) for z in data['roots']]
    c.need(len(roots)==r-1 and all(len(z)==2 for z in roots),'factor count')
    q=[c.ONE];factors=[]
    for z in roots:
        c.need(all(v.denominator&(v.denominator-1)==0 and v.denominator<=1<<fb for v in z),'dyadic root')
        inside=c.norm2(z)<1
        b=z if inside else c.div(c.ONE,z)
        c.need(c.norm2(b)<=(1-beta)**2,'stable margin')
        factors.append((inside,b))
        new=[c.ZERO]*(len(q)+1)
        for j,v in enumerate(q):
            new[j]=c.sub(new[j],c.mul(z,v));new[j+1]=c.add(new[j+1],v)
        q=new
    q=[(v[0]/r,v[1]/r) for v in q]
    epsilon=F(0)
    for box,z in zip(ci,q):
        epsilon+=sum(max(abs(t-v) for t in iv) for iv,v in zip(box,z))
    A=F(r)*beta**-(r-1);t=A*epsilon
    c.need(t<1,'coefficient residual')
    perturbation=A*t/(1-t)
    u=F(1,1<<bits);c.need(u<=beta**2/2,'closure precision')
    error=F(0);amplification=F(r);budgets=[]
    for inside,b in factors:
        # Includes final rounded multiplication by -b for outer roots.
        error=error/beta+7*(amplification+error+1)*u/beta**3
        amplification/=beta;budgets.append(error)
    c.need(error+perturbation<=F(1,1<<target),'target error')
    return dict(radix=r,embedding=k,factors=factors,beta=beta,bits=bits,q=q,budgets=budgets,
                certificate=dict(radix=r,embedding=k,inner_factors=sum(t[0] for t in factors),outer_factors=sum(not t[0] for t in factors),
                coefficient_error_bound=str(epsilon),inverse_norm_bound=str(A),factorization_inverse_error_bound=str(perturbation),
                rounded_execution_error_bound=str(error),total_error_bound=str(error+perturbation),target_bits=target,
                working_bits=bits,factor_bits=fb,beta=str(beta),all_cycle_lengths=True))

def apply(x,state,direction,tau=c.ONE,omit_inner_shift=False):
    c.need(c.norm2(tau)==1,'unit gauge')
    r=state['radix'];y=[(v[0]*r,v[1]*r) for v in x]
    for inside,b in state['factors']:
        conjugate=(tau[0],-tau[1])
        coefficient=c.mul(b,conjugate if inside else tau)
        y=c.scan(y,coefficient,state['beta'],state['bits'],-direction if inside else direction)
        if inside:
            if not omit_inner_shift:y=[y[(i+direction)%len(y)] for i in range(len(y))]
            y=[c.rounded(c.mul(conjugate,v),state['bits']) for v in y]
        else:y=[c.rounded(c.neg(c.mul(b,v)),state['bits']) for v in y]
    return y

def phased_polynomial(q,tau):
    power=c.ONE;out=[]
    for v in q:out.append(c.mul(v,power));power=c.mul(power,tau)
    return out

def matrix_solve(x,q,direction):
    n=len(x);a=[[c.ZERO for _ in range(n)]+[x[i]] for i in range(n)]
    for i in range(n):
        for j,v in enumerate(q):
            column=(i-direction*j)%n;a[i][column]=c.add(a[i][column],v)
    for k in range(n):
        pivot=next(i for i in range(k,n) if a[i][k]!=c.ZERO);a[k],a[pivot]=a[pivot],a[k]
        p=a[k][k];a[k]=[c.div(v,p) for v in a[k]]
        for i in range(n):
            if i==k:continue
            p=a[i][k];a[i]=[c.sub(v,c.mul(p,w)) for v,w in zip(a[i],a[k])]
    return [row[-1] for row in a]

def residual_check(x,y,state,direction,tau=c.ONE):
    q=phased_polynomial(state['q'],tau);bound=sum(abs(v[0])+abs(v[1]) for v in q)*state['budgets'][-1]
    for i in range(len(x)):
        total=c.ZERO
        for j,v in enumerate(q):total=c.add(total,c.mul(v,y[(i-direction*j)%len(x)]))
        c.need(c.norm2(c.sub(total,x[i]))<=bound**2,'expanded residual')

def kernel_crosschecks():
    # Independent closed coefficients in Q(i) and Q(sqrt(2),i).
    exact4=[(F(1),F(0)),(F(1,2),F(1,2)),(F(1,4),F(1,4)),(F(1,4),F(0))]
    for box,z in zip(ik.kernel(4,1),exact4):
        c.need(all(iv[0]<=v<=iv[1] for iv,v in zip(box,z)),'Gaussian kernel crosscheck')
    raw=[[1,0,0,0],[F(1,2)]*4,[0,0,F(1,2),F(1,2)],[0,0,0,F(1,2)],
         [0,0,0,F(1,4)],[F(1,8),F(-1,8),F(1,8),F(1,8)],[F(1,8),0,0,F(1,8)],[F(1,8),0,0,0]]
    scale=1<<4096;v=math.isqrt((1<<8192)//2);s=(F(v,scale),F(v+1,scale))
    c.need(2*s[0]**2<1<2*s[1]**2,'independent sqrt enclosure')
    for box,a in zip(ik.kernel(8,1),raw):
        for iv,constant,multiplier in ((box[0],a[0],a[1]-a[3]),(box[1],a[2],a[1]+a[3])):
            values=[constant+multiplier*t for t in s]
            c.need(iv[0]<=min(values)<=max(values)<=iv[1],'radix8 independent coefficient enclosure')
    return ['radix4_exact_Gaussian_coefficients','radix8_independent_algebraic_coefficients']

def irrational_gauge():
    # Enclose tau=exp(2*pi*i/7), then project a dyadic stereographic
    # parameter to an exactly rational point on the unit circle.
    box=ik.root_interval(7,1)
    choices=[]
    for center in (c.ONE,(F(-1),F(0)),(F(0),F(1)),(F(0),F(-1))):
        conjugate=(center[0],-center[1])
        rotated=ik.cmul(box,(ik.point(conjugate[0]),ik.point(conjugate[1])))
        choices.append((rotated[0][0],center,rotated))
    _,center,v=max(choices,key=lambda x:x[0])
    c.need(v[0][0]>=F(1,2),'gauge chart')
    parameters=[im/(1+re) for im in v[1] for re in v[0]]
    mid=(min(parameters)+max(parameters))/2
    t=c.rounded((mid,F(0)),1024)[0]
    sigma=c.mul(center,((1-t*t)/(1+t*t),2*t/(1+t*t)))
    c.need(c.norm2(sigma)==1,'exact rational unit phase')
    error=sum(max(abs(endpoint-coordinate) for endpoint in iv) for iv,coordinate in zip(box,sigma))
    c.need(error<F(1,1<<1020),'phase approximation error')
    return sigma,error,dict(target='exp(2*pi*i/7)',rational_unit=[str(v) for v in sigma],error_bound=str(error),parameter_bits=1024)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True,type=Path);args=parser.parse_args()
    crosschecks=kernel_crosschecks();sigma,gauge_error,gauge_record=irrational_gauge()
    data=json.loads((P/'FACTORS.json').read_text());certificates=[];cases=[]
    for row in data:
        state=certify(row)
        # The approximation of the target phase is charged as an operator
        # coefficient perturbation, using both phases' unit modulus.
        derivative=sum(j*(abs(v[0])+abs(v[1])) for j,v in enumerate(state['q']))
        combined=F(state['certificate']['coefficient_error_bound'])+derivative*gauge_error
        A=F(state['certificate']['inverse_norm_bound']);c.need(A*combined<1,'gauged residual contraction')
        gauged_error=A*A*combined/(1-A*combined)+state['budgets'][-1]
        c.need(gauged_error<=F(1,1<<row['target_bits']),'irrational gauge target')
        state['certificate']['irrational_gauge_total_error_bound']=str(gauged_error)
        certificates.append(state['certificate'])
        for n in (1,2,3,8,17,64):
            for direction in (-1,1):
                for gauge_name,tau in (('1',c.ONE),('i',(F(0),F(1))),('3/5+4i/5',(F(3,5),F(4,5))),('certified_exp(2pi_i/7)',sigma)):
                    x=[(F((5*i)%7-3,8),F((7*i)%11-5,16)) for i in range(n)]
                    y=apply(x,state,direction,tau);residual_check(x,y,state,direction,tau)
                    if n<=3:
                        exact=matrix_solve(x,phased_polynomial(state['q'],tau),direction)
                        c.need(all(c.norm2(c.sub(v,w))<=state['budgets'][-1]**2 for v,w in zip(y,exact)),'independent dense comparison')
                    cases.append(dict(radix=row['radix'],embedding=row['embedding'],length=n,direction=direction,gauge=gauge_name,dense_comparison=n<=3,residual=True))
        print(json.dumps(dict(radix=row['radix'],embedding=row['embedding'],inner=state['certificate']['inner_factors'],status='passed')),flush=True)
    controls=[]
    mixed=next(row for row,cert in zip(data,certificates) if cert['inner_factors']>0)
    for name in ('unit_root','missing_root','wrong_embedding','low_precision','bad_margin'):
        row=json.loads(json.dumps(mixed))
        if name=='unit_root':row['roots'][0]=['1','0']
        if name=='missing_root':row['roots'].pop()
        if name=='wrong_embedding':row['embedding']=row['radix']
        if name=='low_precision':row['working_bits']=8
        if name=='bad_margin':row['beta']='1'
        try:certify(row)
        except ValueError as error:controls.append(dict(name=name,rejected=str(error)))
        else:raise ValueError('bad control accepted '+name)
    state=certify(mixed);x=[c.ONE,c.ZERO,(F(1,2),F(1,4))]
    bad=apply(x,state,1,omit_inner_shift=True)
    try:residual_check(x,bad,state,1)
    except ValueError as error:controls.append(dict(name='omitted_inner_shift',rejected=str(error)))
    else:raise ValueError('inner-shift mutation accepted')
    try:apply(x,state,1,(F(1),F(1)))
    except ValueError as error:controls.append(dict(name='nonunit_gauge',rejected=str(error)))
    else:raise ValueError('nonunit gauge accepted')
    args.out.write_text(json.dumps(dict(status='passed',kernel_crosschecks=crosschecks,irrational_gauge=gauge_record,certificates=certificates,cases=cases,controls=controls),indent=2)+'\n')
    print(json.dumps(dict(status='passed',certificates=len(certificates),cases=len(cases),dense_cases=sum(row['dense_comparison'] for row in cases),controls=len(controls))))

if __name__=='__main__':main()
