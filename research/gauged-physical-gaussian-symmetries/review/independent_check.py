"""Independent rational/complex gauge review; no author helper imports.

All arithmetic is exact Fraction arithmetic. Default is read-only.
"""
from dataclasses import dataclass
from fractions import Fraction as F
from hashlib import sha1,sha256
from itertools import product,permutations
from pathlib import Path
import argparse,json,math

def need(value,reason):
    if not value:raise ValueError(reason)

@dataclass(frozen=True)
class Q:
    re:F=F(0)
    im:F=F(0)
    def __post_init__(self):
        object.__setattr__(self,'re',F(self.re));object.__setattr__(self,'im',F(self.im))
    def __add__(self,other):
        other=cast(other);return Q(self.re+other.re,self.im+other.im)
    __radd__=__add__
    def __neg__(self):return Q(-self.re,-self.im)
    def __sub__(self,other):return self+-cast(other)
    def __rsub__(self,other):return cast(other)+-self
    def __mul__(self,other):
        other=cast(other)
        return Q(self.re*other.re-self.im*other.im,self.re*other.im+self.im*other.re)
    __rmul__=__mul__
    def __truediv__(self,other):
        other=cast(other);d=other.abs2();need(d!=0,'division by zero')
        return Q((self.re*other.re+self.im*other.im)/d,(self.im*other.re-self.re*other.im)/d)
    def __rtruediv__(self,other):return cast(other)/self
    def __bool__(self):return bool(self.re or self.im)
    def abs2(self):return self.re*self.re+self.im*self.im
    def upper(self):return abs(self.re)+abs(self.im)
    def lower(self):return max(abs(self.re),abs(self.im))

def cast(value):return value if isinstance(value,Q) else Q(value)

def inverse(matrix):
    n=len(matrix)
    work=[list(row)+[Q(int(i==j)) for j in range(n)] for i,row in enumerate(matrix)]
    for j in range(n):
        pivot=next((k for k in range(j,n) if work[k][j]),None)
        need(pivot is not None,'singular matrix')
        work[j],work[pivot]=work[pivot],work[j]
        value=work[j][j];work[j]=[x/value for x in work[j]]
        for i in range(n):
            if i!=j:
                value=work[i][j];work[i]=[a-value*b for a,b in zip(work[i],work[j])]
    return [row[n:] for row in work]

def cross(matrix,x,y):
    n=len(matrix);need(all(len(row)==n for row in matrix),'matching square index sets')
    return matrix[x][y]*matrix[y][x]/(matrix[x][x]*matrix[y][y])

def weighted(matrix,p):
    """Solve M e_x=w_x e_p(x), MG=GM, directly from all entries."""
    n=len(matrix);adj=[[] for _ in range(n)]
    for x in range(n):
        for y in range(n):
            a,b=matrix[x][y],matrix[p[x]][p[y]]
            if bool(a)!=bool(b):return None
            if a:
                ratio=b/a
                adj[y].append((x,ratio));adj[x].append((y,1/ratio))
    weights=[None]*n
    for root in range(n):
        if weights[root] is not None:continue
        weights[root]=Q(1);stack=[root]
        while stack:
            y=stack.pop()
            for x,ratio in adj[y]:
                want=ratio*weights[y]
                if weights[x] is None:weights[x]=want;stack.append(x)
                elif weights[x]!=want:return None
    need(all(weights[x]*matrix[x][y]==weights[y]*matrix[p[x]][p[y]] for x in range(n) for y in range(n)),
         'direct monomial equation residual')
    return weights

def grid(shape):return list(product(*(range(n) for n in shape)))

def gauged(shape,q,v,diagonal=None):
    points=grid(shape);n=len(points)
    gauges=(Q(1),Q(0,2),Q(1,1),Q(F(-1,2)),Q(2,F(1,3)),Q(F(2,3),-1))
    L=[gauges[i%len(gauges)] for i in range(n)]
    S=[math.prod(v[j]**x[j] for j in range(len(shape))) for x in points]
    diagonal=[Q(1)]*n if diagonal is None else list(map(cast,diagonal))
    need(all(diagonal) and all(L),'nonzero complex gauges')
    R=[diagonal[i]/L[i] for i in range(n)];A=[L[i]*S[i] for i in range(n)]
    K=[[math.prod(q[j]**((x[j]-y[j])**2) for j in range(len(shape))) for y in points] for x in points]
    G=[[L[i]*S[i]*K[i][j]*R[j]/S[j] for j in range(n)] for i in range(n)]
    return points,K,G,A,diagonal

def coordinate_group(shape,q,diagonal):
    points=grid(shape);indices={x:i for i,x in enumerate(points)};answer=set()
    for sigma in permutations(range(len(shape))):
        if any((shape[i],q[i])!=(shape[sigma[i]],q[sigma[i]]) for i in range(len(shape))):continue
        for signs in product((1,-1),repeat=len(shape)):
            mapped=[]
            for x in points:
                y=[0]*len(shape)
                for i in range(len(shape)):y[sigma[i]]=x[i] if signs[i]==1 else shape[i]-1-x[i]
                mapped.append(indices[tuple(y)])
            if all(diagonal[mapped[i]]==diagonal[i] for i in range(len(points))):answer.add(tuple(mapped))
    return answer

def cycles(p):
    seen=set();lengths=[]
    for x in range(len(p)):
        if x in seen:continue
        here=x;length=0
        while here not in seen:seen.add(here);length+=1;here=p[here]
        lengths.append(length)
    return lengths

def exact_groups():
    fixtures=[((2,2),(F(1,2),F(1,3)),(F(3,2),F(5,4)),None),
              ((2,2),(F(1,2),F(1,3)),(F(3,2),F(5,4)),(1,Q(0,1),1,Q(0,1))),
              ((2,2),(F(1,2),F(1,3)),(F(3,2),F(5,4)),(1,Q(0,1),-1,Q(0,-1))),
              ((2,2),(F(1,2),F(1,2)),(F(2),F(3)),None),
              ((2,3),(F(1,16),F(1,2)),(F(1),F(2)),None),
              ((3,),(F(1,2),),(F(3,2),),None)]
    reports=[]
    for shape,q,v,diagonal in fixtures:
        points,K,G,A,Qdiag=gauged(shape,q,v,diagonal);n=len(points);Gi=inverse(G)
        for x in range(n):
            for y in range(n):need(cross(G,x,y)==Q(K[x][y]**2),'complex-gauge/shift cancellation')
        expected=coordinate_group(shape,q,Qdiag);actual=set();inverse_group=set();ordinary=0
        for p in permutations(range(n)):
            solved=weighted(G,p)
            if solved is not None:
                actual.add(p);prediction=[A[p[x]]/A[x] for x in range(n)]
                prediction=[w/prediction[0] for w in prediction]
                need(solved==prediction,'scalar-normalized monomial weights')
            if weighted(Gi,p) is not None:inverse_group.add(p)
            ordinary+=all(G[p[x]][p[y]]==G[x][y] for x in range(n) for y in range(n))
        need(actual==expected==inverse_group,'all vertex permutations/forward-inverse centralizers')
        if len(set(q))==len(q):
            need(all(max(cycles(p))<=2 and len(cycles(p))>=math.ceil(n/2) for p in actual),'distinct-width floor')
        reports.append({'shape':shape,'q':list(map(str,q)),'permutations_checked_each':math.factorial(n),
                        'weighted_symmetries':len(actual),'ordinary_symmetries':ordinary,
                        'maximum_vertex_cycle':max(max(cycles(p)) for p in actual),
                        'equal_physical_side_lengths_unequal_counts':shape==(2,3)})
    need(reports[3]['maximum_vertex_cycle']==4,'equal-width long-cycle control')
    need(reports[2]['weighted_symmetries']==1,'diagonal phases versus magnitudes')
    _,_,G,A,_=gauged((2,2),(F(1,2),F(1,3)),(F(2),F(3)))
    p=tuple(3-i for i in range(4));weights=[2*A[p[i]]/A[i] for i in range(4)]
    need(all(weights[i]*weights[p[i]]==Q(4) for i in range(4)),'weighted square4I')
    return reports

def bounds(G):
    return max(x.upper() for row in G for x in row),min(G[i][i].lower() for i in range(len(G)))

def perturb(G,epsilon):
    return [[value+Q(epsilon*F(((2*i+3*j)%5)-2,4),epsilon*F(((i+4*j)%3)-1,4))
             for j,value in enumerate(row)] for i,row in enumerate(G)]

def perturbation_checks():
    shape=(2,2);q=(F(1,2),F(2,5));v=(F(3,2),F(5,4))
    _,K,G,A,Qdiag=gauged(shape,q,v);M,delta=bounds(G);T=len(G)
    gap=min(min(x*x for x in q)-max(x**4 for x in q),abs(q[0]**2-q[1]**2))
    epsilon=gap*delta**2/(384*M);X=perturb(G,epsilon);eta=24*M*epsilon/delta**2
    need(epsilon<=delta/2 and 2*eta<gap,'rigorous forward margin')
    for i in range(T):
        for j in range(T):
            need((X[i][j]-G[i][j]).abs2()<=epsilon**2,'entrywise perturbation contract')
            need((cross(X,i,j)-cross(G,i,j)).abs2()<=eta**2,'normalized pair error bound')
    allowed=coordinate_group(shape,q,[Q(1)]*T)
    surviving={p for p in permutations(range(T)) if weighted(X,p) is not None}
    need(surviving<=allowed,'perturbed weighted permutations preserve axes')
    inverse_epsilon=min(1/(4*T*T*M),delta/(8*T**3*M*M),gap*delta**2/(384*T**3*M**3))
    Y=perturb(inverse(G),inverse_epsilon);Yi=inverse(Y);e=2*T**3*M*M*inverse_epsilon
    need(T*T*M*inverse_epsilon<=F(1,2) and e<=delta/2 and 48*M*e/delta**2<gap,'all inverse conditions')
    for i in range(T):
        for j in range(T):need((Yi[i][j]-G[i][j]).abs2()<=e*e,'exact inverse perturbation bound')
    inverse_surviving={p for p in permutations(range(T)) if weighted(Y,p) is not None}
    need(inverse_surviving<=allowed,'approximate inverse containment')
    return {'forward_epsilon':str(epsilon),'M_upper':str(M),'diagonal_lower':str(delta),
            'gap':str(gap),'surviving_forward_permutations':len(surviving),
            'inverse_epsilon':str(inverse_epsilon),'inverse_back_error_bound':str(e),
            'surviving_inverse_permutations':len(inverse_surviving)}

def source_identities():
    checks=0;max_narrow_exponent=F(0)
    for theta,n,delta in product((F(1,16),F(1,7),F(1,3)),(2,3,5),(F(-1,2),F(0),F(1,5),F(1,2))):
        rho=1+theta;lam=1/rho;b=F(3,7);s=-delta*(1-theta);B=n-1
        coords=[F(2*i-n+1,2) for i in range(n)]
        for x,y in product(coords,repeat=2):
            actual=-b*(x-lam*y+delta)**2
            row=b*lam*(1-lam)*y*y+2*b*lam*(delta+s)*y
            col=-b*(1-lam)*x*x-2*b*(delta+lam*s)*x
            normalized=-b*lam*(x-y)**2+2*b*lam*s*(x-y)
            need(actual==-b*delta*delta+row+col+normalized,'broad quadratic/normalizer identity')
            if x==y:need((x-lam*y+delta)**2<=F(1,4)*(1+theta*B)**2,'broad diagonal exponent floor')
            checks+=1
        for beta0 in (F(0),F(1,4),F(-1,4)):
            betas=[beta0+theta*x for x in coords]
            if not all(abs(beta)<=F(1,2) for beta in betas):continue
            for i,j in product(range(n),repeat=2):
                h=j-i;ti,tj=coords[i],coords[j]
                actual=-((rho*h+betas[i])**2-betas[j]**2)
                predicted=-rho*h*h-2*beta0*h+theta*(ti*ti-tj*tj)
                need(actual==predicted,'same-phase narrow identity')
                need(actual==0 if i==j else actual<0,'narrow diagonal1/strict off-diagonal bound')
                max_narrow_exponent=max(max_narrow_exponent,actual);checks+=1
    theta=F(1,4);rho=1+theta;bi=F(2,5);bj=bi+theta-1
    need(abs(bi)<=F(1,2) and abs(bj)<=F(1,2),'both cell representatives bounded')
    actual=-((rho+bi)**2-bj*bj);false_same_cell=-rho-2*bi-theta
    need(actual!=false_same_cell,'cross-phase-cell control')
    need(-F(3,7)*F(1,5)**2!=0,'missing broad exponential normalizer')
    p,r=2,128;targets=(128,64);primes=(113,59)
    for t,s0 in zip(targets,primes):
        need(all(s0%d for d in range(2,math.isqrt(s0)+1)),'actual small odd primes')
        need((1-F(1,2*p*p))*t<s0<=(1-F(1,4*p*p))*t,'fine-prime interval fixture')
    m=[r*s0//t for t,s0 in zip(targets,primes)]
    broad=[F(x,r) for x in m];narrow=[F(r,x) for x in m]
    need(len(set(m))==2 and abs(broad[0]-broad[1])>=F(1,r)
         and abs(narrow[0]-narrow[1])>F(1,r),'scaled width separation across both target lengths')
    need(all(F(7,8)<x<1 for x in broad) and all(1<x<F(8,7) for x in narrow),
         'both separate family edge bands')
    return {'exact_rational_exponent_checks':checks,'same_phase_required':True,
            'broad_normalizer_required':True,'max_narrow_log_entry':str(max_narrow_exponent),
            'small_fine_prime_fixture':{'p':p,'r':r,'targets':targets,'primes':primes,'m':m},
            'prime_fixture_scope':'Checks an admissible finite interval and scaled width identities; not a prime-existence or production-page theorem.'}

def negative_controls():
    out=['equal-width-four-cycle','nonconstant-diagonal-phase-restriction','weighted-square4I-not-permutation-order']
    q=(F(1,3),F(1,4));_,K,_,_,_=gauged((2,2),q,(F(1),F(1)))
    h=F(1,2**40);G=[[Q(h*x) for x in row] for row in K]
    X=[[Q(h if i==j else 0) for j in range(4)] for i in range(4)]
    epsilon=h/3;three_cycle=(1,2,0,3)
    need(weighted(X,three_cycle) is not None and weighted(G,three_cycle) is None,'tiny scaled-identity long cycle')
    gap=min(min(x*x for x in q)-max(x**4 for x in q),abs(q[0]**2-q[1]**2))
    need(epsilon<=h/2 and 48*h*epsilon<gap and not 48*h*epsilon/(h*h)<gap,'missing diagonal floor falsely certifies')
    out.append('tiny-gauge-nonzero-diagonal-long-cycle')
    R=F(2**40);K2=[[Q(1),Q(F(1,3))],[Q(F(1,3)),Q(1)]]
    unbalanced=[[K2[i][j]*(R if i==0 else 1)/(R if j==0 else 1) for j in range(2)] for i in range(2)]
    changed=[row.copy() for row in unbalanced];changed[1][0]=Q(0)
    need((changed[1][0]-unbalanced[1][0]).abs2()==F(1,9)/R**2
         and cross(unbalanced,0,1)-cross(changed,0,1)==Q(F(1,9)),'unbalanced-gauge amplification')
    out.append('unbalanced-similarity-needs-M')
    K3=[[Q(F(1,2)**((i-j)**2)) for j in range(3)] for i in range(3)];Ki=inverse(K3)
    need(cross(Ki,0,2)!=cross(K3,0,2),'inverse entries not Gaussian metric')
    need([row[:2] for row in Ki[:2]]!=inverse([row[:2] for row in K3[:2]]),'inverse/section interchange')
    out+=['inverse-pair-metric-misuse','inverse-section-interchange']
    K3=[[Q(F(9,10)**((i-j)**2)) for j in range(3)] for i in range(3)]
    epsilon=F(1,100000);Y=[[x+epsilon for x in row] for row in inverse(K3)];Yi=inverse(Y)
    need((Yi[1][1]-K3[1][1]).abs2()>(2*epsilon)**2,'dimension-free inverse bound false')
    need((Yi[1][1]-K3[1][1]).abs2()<=(2*27*epsilon)**2,'dimension-paid inverse bound')
    out.append('inverse-dimension-factor-required')
    rows=(0,1,2);cols=(0,2,1)
    bad=[[Q(F(1,2)**((x-y)**2)) for y in cols] for x in rows]
    need(cross(bad,1,2).re>1,'nonmatching column-grid metric failure')
    out.append('nonmatching-row-column-grid')
    try:cross([[Q(1),Q(1),Q(1)],[Q(1),Q(1),Q(1)]],0,1)
    except ValueError:out.append('rectangular-domain-rejected')
    else:raise ValueError('rectangular control escaped')
    return out

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--package',type=Path,default=Path(__file__).resolve().parent)
    parser.add_argument('--write',type=Path);args=parser.parse_args();p=args.package
    proof='9aae57aa8ade47a89b7b22b39df968056853f04d240094a38e065153a7a53224'
    need(sha256((p/'PROOF.md').read_bytes()).hexdigest()==proof,'reviewed proof changed')
    pins=json.loads((p/'DEPENDENCIES.json').read_text())['files']
    for pin in pins:
        raw=(p/pin['local']).read_bytes()
        need(len(raw)==pin['bytes'] and sha256(raw).hexdigest()==pin['sha256'],'exact retained source bytes')
        need(sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==pin['git_blob'],'exact retained Git blob')
    result={'status':'PASS','reviewed_proof_sha256':proof,'authenticated_sources':len(pins),
            'complete_groups':exact_groups(),'error_transfer':perturbation_checks(),
            'physical_source':source_identities(),'controls':negative_controls(),
            'scope':'Exact rational complex matrices, direct weighted commutator equations and inverse elimination. No author code imported, full source pipeline or matrix-construction algorithm claimed.'}
    text=json.dumps(result,indent=2,sort_keys=True)+'\n'
    if args.write:args.write.write_text(text)
    print(text,end='')

if __name__=='__main__':main()
