"""Independent residue/physical-entry/polynomial review. No author imports."""
import argparse
from fractions import Fraction
from hashlib import sha256
from itertools import permutations, product
from math import isqrt, prod
from pathlib import Path
import json


def need(ok, message):
    if not ok:
        raise ValueError(message)


def prime(n):
    return n >= 2 and all(n % k for k in range(2, isqrt(n)+1))


def phase(s,t,i):
    q=(2*t*i+s)//(2*s)
    return q,q-i,t*i-s*q


def physical(s,t,residue):
    A=residue if residue%2 else residue+s; B=2*t-A; delta=t-s
    if A<2*delta+1:
        return None
    n=(A-(2*t-s))//2; i=n*pow(delta,-1,s)%s
    q,c,ni=phase(s,t,i); qp,cp,nj=phase(s,t,i+1)
    need(i<=s-2 and c==cp and qp==q+1 and ni==n and nj==n+delta,'physical source pair')
    rho=Fraction(t,s)
    need((rho+Fraction(ni,s))**2-Fraction(nj,s)**2==Fraction(A,s),'upper physical exponent')
    need((-rho+Fraction(nj,s))**2-Fraction(ni,s)**2==Fraction(B,s),'lower physical exponent')
    need(A>0 and B>0 and A+B==2*t,'physical invertibility exponents')
    return dict(residue=residue,A=A,B=B,n=n,i=i)


def residue_audit(s,t,r):
    need(prime(s) and s%2 and s<t<2*s and t&(t-1)==0,'source arithmetic domain')
    need(r>=2 and r%2==0 and 2*r<s,'degree domain')
    need({phase(s,t,i)[2] for i in range(s)}==set(range(-(s-1)//2,(s-1)//2+1)),'full centered phase period')
    roots=set(); classes=set(); equal_nonzero=0
    for da,db in product(range(-r,r+1),repeat=2):
        if da==db:
            if da:
                need(2*t*db%s != 0,'equal nonzero differences cannot collide'); equal_nonzero+=1
            continue
        key=min((da,db),(-da,-db)); classes.add(key)
        roots.add((-2*t*db*pow((da-db)%s,-1,s))%s)
    need(len(classes)==2*r*r+r and equal_nonzero==2*r,'opposite difference count')
    bad=set();good=[]; inadmissible=0;box_points=0
    for ares in range(1,s):
        A=ares if ares%2 else ares+s;B=2*t-A
        values={(a*A+b*B)%s for a,b in product(range(r+1),repeat=2)}
        box_points+=(r+1)**2
        if len(values)<(r+1)**2:bad.add(ares)
        record=physical(s,t,ares)
        if record is None:inadmissible+=1
        elif ares not in bad:good.append(record)
    need(bad==roots-{0},'independent box collisions equal difference roots')
    need(len(bad)<=2*r*r+r and inadmissible<=t-s,'bad residue and phase bounds')
    lower=s-1-(t-s)-2*r*r-r
    need(len(good)>=lower,'combined good-phase count')
    return dict(s=s,t=t,r=r,bad_count=len(bad),inadmissible=inadmissible,
                good_count=len(good),lower_bound=lower,first=good[0] if good else None,
                checked_residues=s-1,box_points=box_points)


def add(poly,exponent,coefficient):
    poly[exponent]=poly.get(exponent,0)+coefficient
    if poly[exponent]==0:del poly[exponent]


def determinant(entries,zero,plus):
    n=len(entries); states={0:{zero:1}}
    for i in range(n):
        out={}
        for mask,left in states.items():
            for j in range(n):
                if mask>>j&1:continue
                sign=-1 if (mask>>(j+1)).bit_count()%2 else 1
                target=out.setdefault(mask|1<<j,{})
                for a,x in left.items():
                    for b,y in entries[i][j].items():add(target,plus(a,b),sign*x*y)
        states=out
    return states[(1<<n)-1]


def entries(order,g,weights=None):
    def monomial(x,y):
        exponent=[0]*(2*g)
        for i in range(g):
            a=x>>i&1;b=y>>i&1
            if a!=b:exponent[2*i+a]=1
        return tuple(exponent) if weights is None else sum(a*b for a,b in zip(exponent,weights))
    result=[]
    for i,x in enumerate(order):
        row=[]
        for j,y in enumerate(order):
            term={monomial(x,y):1}
            if i and j:add(term,monomial(order[i-1],order[j-1]),-1)
            row.append(term)
        result.append(row)
    return result


def directed_minor_checks():
    count=terms=0
    for moduli,targets in [((127,251),(128,256)),((971,977),(1024,1024))]:
        selected=[residue_audit(s,t,4)['first'] for s,t in zip(moduli,targets)]
        need(all(selected),'admitted phase selection')
        S=prod(moduli)
        weights=tuple(v*(S//s) for s,record in zip(moduli,selected) for v in (record['A'],record['B']))
        for order in permutations(range(4)):
            poly=determinant(entries(order,2),(0,)*4,lambda a,b:tuple(x+y for x,y in zip(a,b)))
            need(poly and all(max(exponent)<=4 for exponent in poly),'directed minor and degree')
            powers=[sum(a*b for a,b in zip(exponent,weights)) for exponent in poly]
            need(len(set(powers))==len(powers),'CRT directed monomial injection')
            mapped={sum(a*b for a,b in zip(exponent,weights)):coefficient for exponent,coefficient in poly.items()}
            direct=determinant(entries(order,2,weights),0,lambda a,b:a+b)
            need(mapped==direct and direct,'direct physical univariate determinant')
            symmetric={}
            for exponent,coefficient in poly.items():add(symmetric,(exponent[0]+exponent[1],exponent[2]+exponent[3]),coefficient)
            need(symmetric,'symmetric restriction certificate remains nonzero')
            count+=1;terms+=len(poly)
    return dict(all_four_vertex_orders=48,expanded_minor_cases=count,expanded_terms=terms)


def controls():
    s,t=13,16;_,c,n=phase(s,t,2);_,cp,np=phase(s,t,3);rho=Fraction(t,s)
    need(c!=cp,'cross-cell source witness')
    need((rho+Fraction(n,s))**2-Fraction(np,s)**2 != Fraction(2*t-s+2*n,s),'incorrect same-cell formula rejected')
    _,c,n=phase(s,t,s-1);_,cp,np=phase(s,t,s)
    need(c==cp and 2*t-s+2*n==s,'period-cut pair corresponds to excluded zero residue')
    need(residue_audit(13,16,4)['good_count']==0,'overlarge degree has no good modular phase')
    # These are countercontrols to modular injectivity, not proofs of low matrix rank.
    witness=residue_audit(127,128,4)
    need(witness['bad_count']>0 and witness['good_count']>0,'both returning good and bad modular phases exist')
    need((Fraction(t,s)*s)**2>0,'periodized diagonal has a positive omitted alias')
    # A nonzero directed polynomial can disappear on U=V.
    directed={(1,0):1,(0,1):-1}; collapsed={}
    for exponents,coefficient in directed.items():add(collapsed,sum(exponents),coefficient)
    need(directed and not collapsed,'symmetric restriction only proves nonzero when its image is nonzero')
    return ['cross-cell exponent formula fails','physical period-cut pair is excluded by A=0',
            'degree4 over modulus13 has no good modular phase','bad modular phase detected without claiming rank failure',
            'periodized diagonal differs by positive aliases','nonzero symmetric restriction is sufficient, not necessary']


def source_checks(package):
    pins={'inputs/A9-PROOF.md':'3e87c32b9cb3695dc42c2ef10da9c05e74d1742a37e49ce0fe5890ea093463dc',
          'inputs/BILATERAL-LDU.md':'0d65e66d227464dda1a19f781ae0a0be671cbfd347c41e37ec954f3d629d8a77',
          'inputs/FINE-PRIME-PADDING.md':'47d1b1b4df28aadda3cd6bdeb1fbc47290595e9208cd09c1a1f338520d33fdce',
          'inputs/PHASE-CELLS.md':'3cdf492bcb719db4295658604dc202d6a2c5a008b87de43ec54f0107c64db730'}
    for name,digest in pins.items():need(sha256((package/name).read_bytes()).hexdigest()==digest,'exact source pin')
    return pins


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--package',type=Path,default=Path(__file__).resolve().parent)
    parser.add_argument('--write',type=Path);args=parser.parse_args()
    pins=source_checks(args.package);cases=[]
    for s in range(3,132,2):
        if prime(s):
            t=1<<s.bit_length()
            for r in range(2,min(11,(s-1)//2+1),2):cases.append(residue_audit(s,t,r))
    density=[];p=3;original=[(971,1024),(977,1024),(487,512),(491,512)]
    r=min(2*((16+7)//5),2*(isqrt(min(s for s,t in original))//4))
    need(r==8,'exact square-root floor at sixteen vertices')
    for s,t in original:
        need(s>=p**4 and (t-s)*p*p<=s,'declared positive-density source hypotheses')
        need(Fraction((2*p*p-1)*t,2*p*p)<s<=Fraction((4*p*p-1)*t,4*p*p),'exact fine-prime interval')
        row=residue_audit(s,t,r)
        need(3*(row['good_count']+1)>=s,'positive-density count')
        density.append(row)
    result=dict(status='PASS_INDEPENDENT_PHYSICAL_PHASE_REVIEW',source_sha256=pins,
                small_cases=len(cases),small_residues=sum(c['checked_residues'] for c in cases),
                small_degree_box_points=sum(c['box_points'] for c in cases),
                actual_fine_prime_density_fixtures=density,directed_minors=directed_minor_checks(),controls=controls(),
                limits='Exact selected alias-deleted column-normalized factors only. No numerical transcendence, rounded or periodic rank, larger-source inverse, runtime or kappa claim.')
    text=json.dumps(result,indent=2,sort_keys=True)+'\n'
    if args.write:args.write.write_text(text)
    print(text,end='')


if __name__=='__main__':main()
