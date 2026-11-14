#!/usr/bin/env python3
"""Exact fixed-size algebra/source/perturbation checks; read-only by default.
Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance.
Polynomial and rational inverse helpers are adapted from credited A11;
independent root review uses a separate continuous Bernstein certificate.
SPDX-License-Identifier: Apache-2.0
"""
from fractions import Fraction as Q
from hashlib import sha256
from itertools import permutations, product
from pathlib import Path
import json
Fraction=Q
class CheckFailure(RuntimeError):
    pass

def require(ok,message):
    if not ok:raise CheckFailure(message)

def add_poly(a, b, sign=1):
    out = dict(a)
    for key, value in b.items():
        out[key] = out.get(key, 0) + sign * value
        if not out[key]:
            del out[key]
    return out




def multiply_poly(a, b):
    out = {}
    for u, c in a.items():
        for v, d in b.items():
            key = tuple(x + y for x, y in zip(u, v))
            out[key] = out.get(key, 0) + c * d
    return {k: v for k, v in out.items() if v}



def tensor_monomial(x,y,g):
    key=[]
    for bit in range(g):
        xb,yb=(x>>bit)&1,(y>>bit)&1
        key.extend((int(xb==0 and yb==1),int(xb==1 and yb==0)))
    return tuple(key)



def displacement_entries(order,keep,weights=None):
    g=len(order).bit_length()-1
    def monomial(x,y):
        key=tensor_monomial(x,y,g)
        return key if weights is None else (sum(a*b for a,b in zip(key,weights)),)
    rows=[]
    for i in keep:
        row=[]
        for j in keep:
            value={monomial(order[i],order[j]):1}
            if i and j:
                value=add_poly(value,{monomial(order[i-1],order[j-1]):1},-1)
            row.append(value)
        rows.append(row)
    return rows



def poly_det(entries,variables):
    out={}
    for perm in permutations(range(len(entries))):
        sign=(-1)**sum(perm[i]>perm[j] for i in range(len(perm)) for j in range(i+1,len(perm)))
        term={(0,)*variables:sign}
        for i,j in enumerate(perm):
            term=multiply_poly(term,entries[i][j])
            if not term:
                break
        out=add_poly(out,term)
    return out



def inverse(a):
    n=len(a)
    b=[[Fraction(x) for x in row]+[Fraction(i==j) for j in range(n)] for i,row in enumerate(a)]
    for k in range(n):
        pivot=next((i for i in range(k,n) if b[i][k]),None)
        require(pivot is not None,'rational inverse exists')
        b[k],b[pivot]=b[pivot],b[k]
        scale=b[k][k]
        b[k]=[x/scale for x in b[k]]
        for i in range(n):
            if i!=k:
                factor=b[i][k]
                b[i]=[x-factor*y for x,y in zip(b[i],b[k])]
    return [row[n:] for row in b]


def poly_var(k):
    return {tuple(int(i==k) for i in range(4)):1}


def symbolic_classes():
    one={(0,0,0,0):1}; u,v,x,y=[poly_var(k) for k in range(4)]
    q1,q2=multiply_poly(u,v),multiply_poly(x,y)
    square=lambda z:multiply_poly(z,z)
    Lx=multiply_poly(square(q2),square(add_poly(one,q1,-1)))
    Lu=multiply_poly(square(q1),square(add_poly(one,q2,-1)))
    def gray(q,qother,left,right):
        f=lambda z:add_poly(multiply_poly(q,add_poly(one,qother,-1)),
                             multiply_poly(add_poly(one,q,-1),square(z)),-1)
        return multiply_poly(f(left),f(right))
    # The matrix helper uses low-bit U,V first; exchange axes in class formulas.
    forms=[((0,1,2,3),Lu),((0,2,1,3),Lx),
           ((0,1,3,2),gray(q2,q1,u,v)),((0,2,3,1),gray(q1,q2,x,y))]
    known={}
    for order,formula in forms:
        for mask in range(4):
            current=tuple(x^mask for x in order)
            require(current not in known,'distinct order class')
            actual=poly_det(displacement_entries(current,list(range(4))),4)
            require(actual==formula,'exact all-coefficient determinant identity')
            known[current]=formula
    refs={}
    h0=[[1,1,1,1],[0,1,0,1],[0,0,1,1],[0,0,0,1]]
    for order in permutations(range(4)):
        if order not in known:
            require(order[0]^order[1]==3,'all remaining orders opposite-first')
            value=det(stein(reorder(h0,order)))
            sign=1 if order[0] in (0,3) else -1
            require(value==sign,'opposite-first exact reference sign')
            refs[' '.join(map(str,order))]=sign
    require(len(known)==16 and len(refs)==8,'complete 24-order domain')
    return {'factorized_orders':16,'reference_orders':refs,
            'coefficient_terms':sum(map(len,known.values()))}


def det(a):
    out=Q(0)
    for order in permutations(range(len(a))):
        term=Q((-1)**sum(order[i]>order[j] for i in range(len(a)) for j in range(i+1,len(a))))
        for i,j in enumerate(order):term*=a[i][j]
        out+=term
    return out


def stein(a):
    return [[a[i][j]-(a[i-1][j-1] if i and j else 0) for j in range(len(a))] for i in range(len(a))]


def reorder(a,o):
    return [[a[i][j] for j in o] for i in o]


def tensor(a,b):
    return [[a[i][j]*b[k][l] for j in range(len(a)) for l in range(len(b))]
            for i in range(len(a)) for k in range(len(b))]


def gram_margin(a,margin):
    n=len(a)
    b=[[sum(a[k][i]*a[k][j] for k in range(n))-(margin*margin if i==j else 0)
        for j in range(n)] for i in range(n)]
    for k in range(n):
        if b[k][k]<=0:return False
        pivot=b[k][k]
        for i in range(k+1,n):
            for j in range(k+1,n):b[i][j]-=b[i][k]*b[k][j]/pivot
    return True


def rational_checks():
    eta=Q(1,1024)
    fixtures=[(Q(1,2048),1-eta,Q(1),1,2),
              (Q(1,1<<20),Q(1),1-eta,2,1),
              (Q(1,1<<16),1-eta/2,1-eta/2,Q(3,2),Q(3,2))]
    count=0
    for w,u,x,cv,cy in fixtures:
        h=tensor([[Q(1),u],[cv*w,Q(1)]],[[Q(1),x],[cy*w,Q(1)]])
        hi=inverse(h); delta=w*w/(1<<32)
        hp=[[h[i][j]+delta*(-1 if (i+2*j)%3==0 else 1) for j in range(4)] for i in range(4)]
        hpi=inverse(hp)
        for order in permutations(range(4)):
            e,ei,ep,eip=[stein(reorder(a,order)) for a in (h,hi,hp,hpi)]
            require(abs(det(e))>=w*w/16,'rational determinant floor')
            require(gram_margin(e,w*w/(1<<10)),'exact forward singular certificate')
            require(gram_margin(ei,w*w/(1<<19)),'exact inverse singular certificate')
            require(gram_margin(ep,w*w/(1<<11)),'perturbed forward singular certificate')
            require(gram_margin(eip,w*w/(1<<20)),'perturbed inverse singular certificate')
            rev=tuple(reversed(order))
            require(det(ei)==det(stein(reorder(h,rev)))/(det(h)**2),'determinant inverse reversal identity')
            count+=1
    return {'fixtures':len(fixtures),'orders':count,'exact_gram_certificates':4*count,
            'perturbation':'unstructured signed matrix at delta=w^2/2^32; inverse recomputed exactly'}
def nearest(s,t,j):return (2*t*j+s)//(2*s)


def source_exponent(s,t,j,k):
    return Q((t*k-s*nearest(s,t,j))**2-(t*k-s*nearest(s,t,k))**2,s*s)


def source_checks():
    # Each odd prime divisor of s=k*2^m+1 has order divisible by2^m
    # under this power residue. If k<2^m, that divisor exceeds sqrt(s).
    fixtures=[{'p':4096,'t':18446744073709551616,'s':18446743738702102529,
               'm':33,'k':2147483609,'witness':3},
              {'p':4096,'t':18446744073709551616,'s':18446743532543672321,
               'm':33,'k':2147483585,'witness':3}]
    out=[]; alias_checks=0
    for f in fixtures:
        p,t,s,m,k,base=(f[z] for z in ('p','t','s','m','k','witness'))
        require(s==k*(1<<m)+1 and k%2==1 and 0<k<1<<m,'power-residue prime structure')
        require(pow(base,(s-1)//2,s)==s-1,'exact prime certificate')
        require(s>=p**4 and (1-Q(1,2*p*p))*t<s<=(1-Q(1,4*p*p))*t,'actual fine-prime interval')
        delta=t-s; n=-(s-1)//2; i=n*pow(delta,-1,s)%s
        A,B=2*delta+1,2*s-1
        require(0<=i<s-1 and t*i-s*nearest(s,t,i)==n,'actual extremal source point')
        require(nearest(s,t,i+1)==nearest(s,t,i)+1,'same-cell target gap')
        require(source_exponent(s,t,i,i+1)==Q(A,s) and source_exponent(s,t,i+1,i)==Q(B,s),'literal coefficients')
        require(A>4 and 4*A+4<s,'degree-four span guard')
        require(len({(u*A+v*B)%s for u,v in product(range(5),repeat=2)})==25,'A11-good box')
        low=4*16*Q(69,100)/Q(22,7); high=4*16*Q(7,10)/3
        require(9<low<high<16,'elementary pi/log bounds certify alpha four')
        a_low,a_high=Q(48),Q(352,7)
        require(a_high*Q(A,s)<Q(1,1024) and a_high/s<Q(1,1024),'uniform source box')
        require(2*a_low>11*Q(7,10),'source w below2^-11')
        for row,col in product((i,i+1),repeat=2):
            for wrap in (-2,-1,1,2):
                require(source_exponent(s,t,row,col+wrap*s)>=Q(wrap*wrap*t*t,8),'literal alias exponent')
                alias_checks+=1
        require(4*p*delta<s,'named old production guard impossible')
        out.append({**f,'alpha':4,'index':i,'A':A,'B':B,'local_box':25})
    require(fixtures[0]['s']!=fixtures[1]['s'],'distinct source axes')
    for exponent in (12,13,16,32,64):
        p=1<<exponent
        require(p>=36+36*(4+exponent),'p-bit periodic-factor budget')
        require(Q(27,8*p)<Q(1,1024),'uniform source guard')
    return {'fixtures':out,'literal_alias_checks':alias_checks,
            'precision_boundaries':[1<<e for e in (12,13,16,32,64)],
            'prime_certificate':'Exact power residue with elementary prime-divisor order proof; no probable-prime premise.'}
def controls():
    out=[]
    h=tensor([[Q(1),Q(1)],[Q(1,2048),Q(1)]],[[Q(1),Q(1)],[Q(1,2048),Q(1)]])
    coarse=tensor([[Q(1),Q(1)],[Q(0),Q(1)]],[[Q(1),Q(1)],[Q(0),Q(1)]])
    require(det(stein(h))!=0 and det(stein(coarse))==0,'coarse rounding destroys lex rank')
    out.append('coarse rounding loses rank')
    balanced=tensor([[Q(1),Q(1,2)],[Q(1,2),Q(1)]],[[Q(1),Q(1,2)],[Q(1,2),Q(1)]])
    require(det(stein(reorder(balanced,(0,1,3,2))))==0,'balanced equal factors have zero Gray determinant')
    out.append('balanced phase outside selector box loses rank')
    order=(0,3,1,2)
    require(det(stein(reorder(inverse(h),order)))!=det(stein(reorder(h,order)))/(det(h)**2),'inverse determinant needs reversal')
    out.append('omitted inverse reversal detected')
    require(not gram_margin(stein(h),Q(16)),'forged singular margin rejected')
    out.append('forged Gram margin rejected')
    z=Q(1,100)
    require((1+z)**2-1>z and (1+z)**2-1<=3*z,'tensor error is not one factor error')
    out.append('omitted tensor error charge detected')
    F=[[z]*4 for _ in range(4)]; vec=[Q(1,2)]*4
    squared=sum(sum(a*b for a,b in zip(row,vec))**2 for row in F)
    require(squared==(4*z)**2>z*z,'unit-vector witness for entry-to-norm factor four')
    out.append('entry norm conversion needs dimension factor')
    s,t=499,512; terminal=s-1
    require(nearest(s,t,terminal+1)==nearest(s,t,terminal)+1 and terminal+1==s,'terminal pair exceeds finite grid')
    out.append('terminal same-cell step is outside finite grid')
    require(4*4096*Q(1,4096**2)<=1,'fine gap contradicts named old production admission')
    out.append('old production guard cannot be inherited')
    require(pow(3,(15-1)//2,15)!=14,'composite prime-certificate control')
    out.append('composite modulus fails exact certificate')
    exact=(Q(3)-Q(3,2))**2-Q(1,2)**2
    require(Q(9,8)<=exact<Q(9,4),'alias beta-square subtraction cannot be omitted')
    out.append('alias denominator exponent must be retained')
    order=(0,1,2,4,3,6,7,5)
    def power_entry(i,j):
        value={(order[i]&~order[j]).bit_count():1}
        if i and j:
            key=(order[i-1]&~order[j-1]).bit_count()
            value[key]=value.get(key,0)-1
        return {key:coef for key,coef in value.items() if coef}
    left=[power_entry(i,2) for i in range(8)]
    right=[power_entry(i,5) for i in range(8)]
    require(left==right==[{0:1},{1:1,0:-1},{},{},{},{},{},{}],
            'symbolic three-axis duplicate-column nonextension')
    out.append('three-axis continuous-box full-rank extension fails identically')
    return out


def authenticate():
    root=Path(__file__).resolve().parent
    pins=json.loads((root/'DEPENDENCIES.json').read_text())
    for item in pins['files']:
        data=(root/item['local']).read_bytes()
        require(len(data)==item['bytes'] and sha256(data).hexdigest()==item['sha256'],'source authentication '+item['local'])
    return len(pins['files'])


def main():
    result={'status':'PASS_EXTREMAL_PHASE_TWO_AXIS_MARGIN','authenticated_inputs':authenticate(),
            'symbolic_classes':symbolic_classes(),'rational_checks':rational_checks(),
            'source_checks':source_checks(),'negative_controls':controls(),
            'scope':'Fixed two-axis extremal source pairs and matched selected periodic sections; explicit entry-error premise; no producer/full-source/kappa admission.'}
    print(json.dumps(result,sort_keys=True,indent=2))

if __name__=='__main__':main()
