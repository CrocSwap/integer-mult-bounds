"""Complete rational all-height polynomial decision and source calibration.

Prepared by Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
Bell/shift conventions follow the credited net-tax LOG-MOMENTS source.
"""
from fractions import Fraction as F
from math import comb, factorial
from itertools import product


def need(ok,message):
    if not ok:raise ValueError(message)


def trim(a):
    a=list(a)
    while a and a[-1]==0:a.pop()
    return a


def evaluate(a,x):
    v=F(0)
    for c in reversed(a):v=v*x+c
    return v


def subtract(a,b,scale=F(1)):
    return [scale*(a[i] if i<len(a) else 0)-(b[i] if i<len(b) else 0) for i in range(max(len(a),len(b)))]


def tail_cutoff(poly):
    poly=trim(poly);need(poly and poly[-1]>0,'positive final coefficient')
    if len(poly)==1:return 0
    ratio=sum(-a for a in poly[:-1] if a<0)/poly[-1]
    return max(1,ratio.numerator//ratio.denominator+1)


def integer_nonnegative(poly,strict=False):
    poly=trim(poly)
    if not poly:return {'pass':not strict,'cutoff':0,'height':0 if strict else None}
    if poly[-1]<0:
        n=tail_cutoff([-x for x in poly])
        need(evaluate(poly,n)<0,'negative tail witness')
        return {'pass':False,'cutoff':n,'height':n}
    n=tail_cutoff(poly)
    for g in range(n):
        v=evaluate(poly,g)
        if v<0 or (strict and v==0):return {'pass':False,'cutoff':n,'height':g}
    return {'pass':True,'cutoff':n,'height':None}


def uniform_margin(numerator,denominator,eta):
    need(eta>0 and denominator[-1]>0,'positive capacity and denominator')
    limit=numerator[-1]/denominator[-1]
    if limit>=eta:return {'pass':False,'reason':'leading-limit','limit':limit}
    first=(eta+limit)/2
    gap=subtract(denominator,numerator,first);n=tail_cutoff(gap)
    maximum=first
    for g in range(n):
        den=evaluate(denominator,g);need(den>0,'positive height denominator')
        ratio=evaluate(numerator,g)/den
        if ratio>=eta:return {'pass':False,'reason':'finite-height','height':g,'cutoff':n}
        maximum=max(maximum,ratio)
    lam=(maximum+eta)/2
    need(lam<eta,'strict capacity margin')
    return {'pass':True,'lambda':lam,'cutoff':n,'prefix_max_or_tail':maximum,'limit':limit}


def moments(law,p):
    need(law and all(F(0)<=x<=1 and prob>0 for x,prob in law),'bounded positive law')
    need(sum(prob for _,prob in law)==1,'probability mass')
    return [sum(prob*x**i for x,prob in law) for i in range(p+1)]


def coefficients(mu,A,B,beta,p):
    need(p>=1 and len(mu)==p+1 and mu[0]==1 and A>0 and B>0 and beta>0,'exit parameters')
    bell=[[F(0)]*(p+1) for _ in range(p+1)];bell[0][0]=1
    stir=[[0]*(p+1) for _ in range(p+1)];stir[0][0]=1
    for n in range(1,p+1):
        for k in range(1,n+1):
            bell[n][k]=sum(F(comb(n-1,i-1))*mu[i]*bell[n-i][k-1] for i in range(1,n-k+2))
            stir[n][k]=stir[n-1][k-1]+k*stir[n-1][k]
    shift=[sum(F(comb(r,i))*A**(r-i)*mu[i] for i in range(r+1)) for r in range(p+1)]
    cf=[sum(F(comb(p,i))*shift[p-i]*bell[i][j] for i in range(j,p+1)) for j in range(p+1)]
    df=[sum(F(comb(p,i))*stir[i][j]*B**(p-i)*beta**i for i in range(j,p+1)) for j in range(p+1)]
    def ordinary(falling):
        out=[F(0)]*(p+1);basis=[F(1)]
        for j,c in enumerate(falling):
            for i,b in enumerate(basis):out[i]+=c*b
            basis=[F(0)]+basis
            for i in range(len(basis)-1):basis[i]-=j*basis[i+1]
        return out
    return ordinary(cf),ordinary(df),cf,df


def direct(law,A,p,g):
    dist={F(0):F(1)}
    for _ in range(g+1):
        nxt={}
        for a,pa in dist.items():
            for b,pb in law:nxt[a+b]=nxt.get(a+b,F(0))+pa*pb
        dist=nxt
    return sum(prob*(A+x)**p for x,prob in dist.items())


def source_moments(p):
    v=260;L=F(3,2);q0=F(431,500);eps=F(1,100000)
    stir=[[0]*(p+1) for _ in range(p+1)];stir[0][0]=1
    for n in range(1,p+1):
        for k in range(1,n+1):stir[n][k]=stir[n-1][k-1]+k*stir[n-1][k]
    mu=[F(1)]
    for i in range(1,p+1):
        fall=1;value=F(0)
        for j in range(i+1):
            value+=stir[i][j]*(q0/L)**j*fall
            fall*=v-j
        raw=(L/v)**i*value
        mu.append(min(F(1),(raw+eps)/(1+eps)))
    return mu


def main():
    law=[(F(0),F(1,2)),(F(1),F(1,2))]
    n,d,cf,df=coefficients(moments(law,2),F(1),F(49,16),F(1),2)
    lam=F(7,25);gap=subtract(d,n,lam)
    need(gap==[F(807,6400),F(-7,200),F(3,100)],'literal discriminator polynomial')
    need(lam*df[1]-cf[1]==F(-1,200),'coefficient domination rejects')
    result=integer_nonnegative(gap,strict=True)
    need(result['pass'] and result['cutoff']==2,'complete height certificate passes')
    margin=uniform_margin(n,d,F(29,100));need(margin['pass'],'constructive uniform lambda')
    need(integer_nonnegative(subtract(d,n,margin['lambda']))['pass'],'returned lambda valid')
    checks=0;decisions=0
    for q,A,B,beta,p in product((F(1,4),F(1,2),F(3,4)),(F(1,2),F(1)),(F(2),F(3)),(F(1),F(5,4)),(1,2,3,4)):
        law=[(F(0),1-q),(F(1,2),q)]
        n,d,_,_=coefficients(moments(law,p),A,B,beta,p)
        for g in range(7):
            need(evaluate(n,g)==direct(law,A,p,g),'independent convolution polynomial')
            need(evaluate(d,g)==(B+beta*g)**p,'denominator conversion');checks+=1
        for eta in (F(1,10),F(1,2),F(1)):
            answer=uniform_margin(n,d,eta);decisions+=1
            if answer['pass']:
                need(integer_nonnegative(subtract(d,n,answer['lambda']))['pass'],'margin certificate replay')
                need(answer['lambda']<eta,'strict margin replay')
            elif answer['reason']=='finite-height':
                need(evaluate(n,answer['height'])>=eta*evaluate(d,answer['height']),'finite rejection witness')
            else:need(n[-1]>=eta*d[-1],'asymptotic rejection witness')
    # Degree cancellation must inspect the first NONZERO coefficient.
    for poly,expected in [([F(1),F(1),F(0)],True),([F(1),F(-1),F(0)],False),([F(0),F(0)],True),([F(1),F(-2),F(1)],True)]:
        need(integer_nonnegative(poly)['pass']==expected,'equal-leading boundary')
    need(not integer_nonnegative([F(1),F(-2),F(1)],strict=True)['pass'],'integer equality is not strict')
    # Pointwise strictness does not supply a uniform margin below the limiting ratio.
    need(integer_nonnegative([F(1),F(0)],strict=True)['pass'],'positive pointwise gap')
    need(not uniform_margin([F(0),F(1)],[F(1),F(1)],F(1))['pass'],'zero uniform gap rejected')
    # Existing degree24 chord/majorant, algebraic calibration only.
    n,d,cf,df=coefficients(source_moments(24),F(139,40),F(5149,1000),F(127,125),24)
    need(all(c<F(39,2000)*e for c,e in zip(cf,df)),'source p24 coefficient calibration')
    source=uniform_margin(n,d,F(39,2000))
    need(source['pass'],'source p24 finite decision')
    # PR5070 supplied this source capacity upper bound and true capped-reference lower bound.
    cap_upper=F('0.019675906372710418424472814350')
    need((F(857,1000)/F(127,125))**23>cap_upper,'p23 capped-reference leading obstruction retained')
    bad=0
    for invalid in ([(F(0),F(1,2))],[(F(2),F(1))]):
        try:moments(invalid,2)
        except ValueError:bad+=1
    need(bad==2,'invalid exact law rejected')
    print('PASS_COMPLETE_ALL_HEIGHT_EXITS',dict(convolution_checks=checks,uniform_decisions=decisions,discriminator_cutoff=2,source_p24_cutoff=source['cutoff'],source_p24_coefficients=25,boundary_controls=9))

if __name__=='__main__':main()
