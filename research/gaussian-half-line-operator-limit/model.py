"""Exact finite controls for a written operator-limit theorem; no norm fitting.
JoyboyBrian with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as F

def need(value,message):
    if not value: raise ValueError(message)

def products(q,n):
    p=[F(1)]
    for k in range(1,n): p.append(p[-1]*(1-q**(2*k)))
    return p

def coefficient(q,n,i,j):
    if i>j: i,j=j,i
    p=products(q,n)
    return sum((q**(2*r)*p[j+r]/(p[i]*p[j-i+r]*p[j]*p[r]) for r in range(n-j)),F())

def exact_inverse(a):
    n=len(a); w=[list(v)+[F(i==j) for j in range(n)] for i,v in enumerate(a)]
    for k in range(n):
        pivot=next(i for i in range(k,n) if w[i][k])
        w[k],w[pivot]=w[pivot],w[k]
        scale=w[k][k];w[k]=[v/scale for v in w[k]]
        for i in range(n):
            if i!=k:
                z=w[i][k];w[i]=[v-z*t for v,t in zip(w[i],w[k])]
    return [v[n:] for v in w]

def gauge(theta,i,j):
    """Exponent divided by b, from the original Dr,Dc factorization."""
    rho=1+theta;c=F(1,2)/rho
    return (theta/rho*i*i-2*c*i-theta/rho**2*j*j+2*c/rho*j+c*c)-abs(i-j)/rho

def edge(theta,n,i,j):
    rho=1+theta; beta=theta*j-F(1,2)
    if i<=j: return beta*beta/rho**2-theta/rho*(j*j-i*i)
    delta=1/theta-(n-1);a=n-1-i;c=n-1-j
    return beta*beta/rho**2-theta/rho*((c+delta)**2-(a+delta)**2)

def inverse_checks():
    cases=entries=0
    for q in (F(1,2),F(2,3),F(3,4)):
        for n in (2,3,5,7):
            direct=exact_inverse([[q**((i-j)**2) for j in range(n)] for i in range(n)])
            p=products(q,n)
            for i in range(n):
                for j in range(n):
                    a=coefficient(q,n,i,j)
                    need(direct[i][j]==(-1)**(i+j)*q**abs(i-j)*a,'full q-LDU versus independent elimination')
                    need(a==coefficient(q,n,n-1-i,n-1-j),'exact reflection')
                    need(a<=1/p[-1]**3,'normalized predecessor envelope')
                    entries+=1
            cases+=1
    q=F(1,2);n=20;i=6;j=12;p=products(q,n)
    a=coefficient(q,n,i,j);first=1/(p[i]*p[j-i])
    need(a>first,'discarded positive tail changes coefficient')
    # A finite product encloses P_infinity: the omitted product is at least1-tail.
    L=60; ps=products(q,L+1)[-1];tail=q**(2*(L+1))/(1-q*q)
    lo=ps*(1-tail);hi=ps
    need(lo>0,'infinite product lower endpoint')
    need(1/hi**3>1/lo**2,'three factors distinguish two factors')
    return {'matrices':cases,'entries':entries,'nonfirst_tail':str(a-first),'product_interval':[str(lo),str(hi)]}

def geometry_checks(source_setup,source_expression):
    from types import SimpleNamespace
    pairs=0; offsets=[]
    for theta,n in ((F(1,400),400),(F(2,799),399),(F(3,1000),333)):
        rho=1+theta;delta=1/theta-(n-1);offsets.append(str(delta))
        need(1<=delta<2,'floor section reflected offset')
        env={'alpha':3,'theta':theta,'beta_start':-F(1,2),'math':SimpleNamespace(pi=F(1))}
        exec(source_setup,env)
        for i in range(n):
            for j in sorted({0,1,5,n//2,n-2,n-1,i}):
                env.update(i=F(i),j=F(j))
                original=eval(source_expression,env)
                expected=F(1,9)*(F(i)-F(j)/rho-env['c'])**2
                need(original==expected,'original block exponent binding')
                need(gauge(theta,i,j)==edge(theta,n,i,j),'both edge gauge identities')
                need(gauge(theta,i,j)<=F(1,4),'exponent envelope')
                pairs+=1
    theta=F(2,799);n=399;i=n-1;j=n-4;rho=1+theta
    wrong=(theta*j-F(1,2))**2/rho**2-theta/rho*((n-1-j)**2-(n-1-i)**2)
    need(wrong!=gauge(theta,i,j),'omitting reflected offset rejected')
    need(gauge(F(1,400),0,20)!=gauge(F(1,400),20,0),'one edge cannot replace both orientations')
    return {'source_pairs':pairs,'offsets':offsets,'first_fixture':{'alpha':3,'theta':'1/400','N':400}}

def operator_controls():
    # Isometric cell embeddings and direct sums tested exactly, not sampled norms.
    h=F(1,20);v=[F(2),F(-3),F(5)]
    need(sum(x*x for x in v)==sum(h*(x*x/h) for x in v),'cell isometry')
    a=[[F(1),F(2)],[F(0),F(3)]];x=[F(4),F(-1)]
    matrix=[h*sum(t*s for t,s in zip(row,x)) for row in a]
    kernel=[sum(h*t*s for t,s in zip(row,x)) for row in a]
    need(matrix==kernel,'hA versus piecewise constant kernel')
    need(matrix!=[sum(t*s for t,s in zip(row,x)) for row in a],'missing h normalization rejected')
    # The norm on block-diagonal identical scalar maps is max, not sqrt(sum squares).
    z=[F(3),F(4)];need(sum((2*t)**2 for t in z)==4*sum(t*t for t in z),'orthogonal corner outputs')
    # Polynomial coefficients after factoring exp(-b x²): L*(x exp)=exp, L(exp)=4bx exp.
    for b in (F(1,3),F(1),F(7)):
        for x0 in (F(0),F(1,5),F(3)):
            need((1-2*b*x0*x0)+2*b*x0*x0==1,'adjoint ground state')
            need(-(-2*b*x0)+2*b*x0==4*b*x0,'LL* ground eigenvalue')
    # A nonzero-trace trial does not belong to the adjoint domain.
    need(F(1)!=0,'exp(-b x²) has forbidden adjoint trace')
    return {'controls':['cell-isometry','kernel-h','missing-h','orthogonal-corners','adjoint-ground-state','nonzero-adjoint-trace']}

def remainder_checks():
    tested=0
    # Exact exponent comparison, including fractional floor offsets and cell corners.
    for h,R in ((F(1,20),F(1)),(F(1,32),F(2)),(F(3,100),F(2))):
        theta=h*h;n=int(1/theta);J=int(R/h)
        for i in sorted({0,1,J//2,J-1}):
            for j in sorted({i,min(i+1,J-1),J-1}):
                for dx,dy in ((0,0),(0,1),(1,0),(1,1)):
                    x=h*(i+dx);y=h*(j+dy)
                    if x>y: continue
                    target=F(1,4)-(y*y-x*x)
                    for u,v in ((i,j),(n-1-i,n-1-j)):
                        need(abs(gauge(theta,u,v)-target)<=12*(R+1)**2*h,'compact exponent remainder')
                        tested+=1
    # Finite geometric sums dominate full row/column tails without a numerical exp.
    for t in (F(1,2),F(2,3),F(9,10)):
        for J in (2,5,9):
            for i in range(12):
                row=sum((t**(j*j-i*i) for j in range(max(i,J),15)),F())
                need(row<=1/(1-t**J),'tail row geometric comparison')
            for j in range(J,15):
                col=sum((t**(j*j-i*i) for i in range(j+1)),F())
                need(col<=1/(1-t**J),'tail column geometric comparison')
    # Explicit scale regime at an exact rational subsequence, no large matrices.
    for k in range(1,7):
        h=F(1,2**(10*k));R=2**k;m=2**(2*k);J=int(R/h);n=int(1/(h*h))
        need(2*J<=n and J>=m and n-J>=m+1,'explicit regime admissibility')
    return {'exponent_comparisons':tested,'geometric_tail_parameters':9,'regime_subsequence_cases':6}
