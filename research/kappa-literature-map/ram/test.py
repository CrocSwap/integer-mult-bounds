#!/usr/bin/env python3
"""Exact, bounded technique tests. Standard library only; no timing claims."""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import hashlib,json,sys


def need(p, label):
    if not p:
        raise RuntimeError(label)


def lazy_inverse_butterfly():
    # Harvey, arXiv:1205.2926v2, Algorithm 4 / Theorem 3.
    beta = 128
    cases = 0
    for p in (3, 5, 13, 17, 29):
        need(4*p < beta, 'word slack')
        for w in range(1, p):
            wp = (w*beta)//p
            for x, y in product(range(4*p), repeat=2):
                xx = x - 2*p if x >= 2*p else x
                q = (wp*y)//beta
                t = (w*y-q*p) % beta
                a, b = xx+t, xx-t+2*p
                need(0 <= t < 2*p, 'redundant multiplication range')
                need(0 <= a < 4*p and 0 <= b < 4*p, 'butterfly word range')
                need(a % p == (x+w*y) % p and b % p == (x-w*y) % p,
                     'lazy butterfly value')
                cases += 1
    # Fixed explicit mutant: omitting the approximate quotient is not safe.
    p,w,x,y = 29,28,0,115
    bad_t = (w*y) % beta
    bad_a = bad_t
    need(bad_a % p != (x+w*y) % p, 'quotient-removal mutant')
    return {'cases':cases,'word_bits':7,'primes':[3,5,13,17,29],
            'quotient_removal_mutant_rejected':True}


def invmat(a,p):
    n=len(a)
    m=[[(x % p) for x in row]+[int(i==j) for j in range(n)] for i,row in enumerate(a)]
    for j in range(n):
        pivot=next((i for i in range(j,n) if m[i][j]),None)
        need(pivot is not None, 'TFT principal minor invertible')
        m[j],m[pivot]=m[pivot],m[j]
        z=pow(m[j][j],-1,p)
        m[j]=[(v*z)%p for v in m[j]]
        for i in range(n):
            if i != j:
                z=m[i][j]
                m[i]=[(u-z*v)%p for u,v in zip(m[i],m[j])]
    return [row[n:] for row in m]


def mv(a,x,p):
    return [sum(u*v for u,v in zip(row,x))%p for row in a]


def truncated_fourier():
    # Exact linear-algebra oracle, NOT an implementation of the fast TFT.
    p,length,omega=17,8,2
    need(pow(omega,length,p)==1 and pow(omega,length//2,p)!=1, 'root order')
    br=lambda j:int(format(j,'03b')[::-1],2)
    a=[[pow(omega,br(i)*j,p) for j in range(length)] for i in range(length)]
    cases=0
    for n in range(1,length+1):
        t=[row[:n] for row in a[:n]]
        ti=invmat(t,p)
        for seed in range(32):
            x=[(seed*(j+1)+3*j*j+5)%p for j in range(n)]
            y=mv(t,x,p)
            need(mv(ti,y,p)==x, 'truncated roundtrip')
            full=mv(a,x+[0]*(length-n),p)
            need(full[:n]==y, 'zero-tail TFT equals selected full outputs')
            cases+=1
    # A nonzero discarded tail must remain visible in an arbitrary-input ABI.
    n=5
    dirty=[0]*length;dirty[n]=1
    need(any(mv(a,dirty,p)[:n]), 'dirty-tail mutant rejected')
    return {'roundtrips':cases,'length':length,'prime':p,
            'dirty_tail_mutant_rejected':True,'implementation':'exact matrix oracle'}


def zadd(x,y):return (x[0]+y[0],x[1]+y[1])
def zneg(x):return (-x[0],-x[1])
def zmul(x,y):return (x[0]*y[0]-x[1]*y[1],x[0]*y[1]+x[1]*y[0])
def red(x,p,i):
    def rat(q):return q.numerator*pow(q.denominator,-1,p)%p
    return (rat(x[0])+i*rat(x[1]))%p


def split_gaussian_base_change():
    # Ring homomorphism Z[i,1/2] -> F_p. Absolute phases remain present.
    values=[(F(a,2**d),F(b,2**d)) for a,b,d in product(range(-2,3),range(-2,3),range(3))]
    count=0
    for p,ii in ((17,4),(97,22)):
        need(ii*ii%p==p-1,'split Gaussian prime')
        for x,y in product(values,repeat=2):
            need(red(zadd(x,y),p,ii)==(red(x,p,ii)+red(y,p,ii))%p,'base change addition')
            need(red(zmul(x,y),p,ii)==red(x,p,ii)*red(y,p,ii)%p,'base change multiplication')
            count+=1
        one=(F(1),F(0)); zero=(F(0),F(0))
        c=[[(F(1,2),F(1,2)),(F(1,2),F(-1,2))],
           [(F(1,2),F(-1,2)),(F(1,2),F(1,2))]]
        cm=[[red(z,p,ii) for z in row] for row in c]
        cc=[[sum(cm[a][k]*cm[k][b] for k in range(2))%p for b in range(2)] for a in range(2)]
        need(cc==[[0,1],[1,0]],'absolute-phase C squared equals X')
        # Wrong i=1 loses i^2=-1 and must not be accepted.
        need(red(zmul((F(0),F(1)),(F(0),F(1))),p,1)!=1,'phase-drop mutant')
    return {'add_mul_pairs':count,'split_primes':[17,97],
            'full_phase_C_squared_X':True,'phase_drop_mutant_rejected':True}


def packing_and_precision():
    # Positive no-carry lemma: s lanes of q-bit data plus one guard bit.
    cases=0
    for q in range(1,5):
        width=q+1; mask=(1<<width)-1
        for a,b,c,d in product(range(1<<q),repeat=4):
            x=a+(b<<width);y=c+(d<<width);z=x+y
            need(z&mask==a+c and (z>>width)&mask==b+d, 'carry-isolated packed addition')
            cases+=1
    need(((3+(0<<2))+(1+(0<<2)))>>2 != 0,'unguarded carry mutant')
    rows=[]
    for logn in (16,32,64,128,256,1024,4096):
        f=(logn-1).bit_length();h=precision=logn
        bits=precision+h+4*f+12
        word=8*logn
        lanes=word//bits
        # cp22f: error <= 10*2^(3f/2)*2^(-P-2f-6).
        # Squared ratio to 2^-P is 100 / (4096*2^f), strictly below 1.
        squared_ratio=F(100,4096*(1<<f))
        need(squared_ratio<1,'cp22f precision budget')
        need(lanes<4,'full-precision coordinates only constant pack')
        rows.append({'log2_n':logn,'f':f,'coordinate_bits':bits,'word_bits':word,
                     'lanes':lanes,'error_ratio_squared':str(squared_ratio)})
    # A full two-bank triangular block never produces three independent banks.
    # Identity diagonal plus any shear has rank exactly two banks, not three.
    p=17;n=4;shear=[[int((i+1)%n==j)+2*int((i+2)%n==j) for j in range(n)] for i in range(n)]
    u=[[int(i==j) for j in range(n)]+[0]*n for i in range(n)]
    u += [row+[int(i==j) for j in range(n)] for i,row in enumerate(shear)]
    invmat(u,p)
    invoice={'two_call_paid_jobs':2,'independent_input_banks':2,'independent_output_banks':2,
             'off_diagonal_is_not_extra_productive_bank':True,
             'owned_initialization_and_cleanup':'linear stores, separately charged',
             'numeric_word_constant_C':8,'coordinate_contract':'P + H + 4 f + 12'}
    return {'packed_add_cases':cases,'unguarded_carry_mutant_rejected':True,
            'precision_rows':rows,'paid_invoice':invoice}



def mm(a,b,p):
    n=len(a);out=[[0]*n for _ in range(n)]
    for i,row in enumerate(a):
        for k,x in enumerate(row):
            if x:
                for j,y in enumerate(b[k]):
                    if y:out[i][j]=(out[i][j]+x*y)%p
    return out


def plus(a,b,p):return [[(x+y)%p for x,y in zip(ar,br)] for ar,br in zip(a,b)]
def scale(k,a,p):return [[k*x%p for x in row] for row in a]
def identity(n):return [[int(i==j) for j in range(n)] for i in range(n)]
def kron(a,b,p):
    return [[x*y%p for x in ar for y in br] for ar in a for br in b]
def tensor(a,f,p):
    out=[[1]]
    for _ in range(f):out=kron(out,a,p)
    return out


def actual_cp22f_modular_port():
    # Independently rebuild the literal 8x8 letters from PR 4710's public definitions.
    def letters(p,ii):
        def mono(perm,phases=None):
            phases=phases or [0]*8
            return [[pow(ii,phases[j]%4,p) if i==perm[j] else 0 for j in range(8)] for i in range(8)]
        def pauli(x,z):return mono([j^x for j in range(8)],[(x&z).bit_count()+2*(j&z).bit_count() for j in range(8)])
        def c(bit):return plus(scale((1+ii)*pow(2,-1,p),identity(8),p),scale((1-ii)*pow(2,-1,p),pauli(1<<bit,0),p),p)
        sall=mono(list(range(8)),[j.bit_count() for j in range(8)])
        u=mono([0,5,2,7,4,1,6,3]);v=mono([0,2,1,3,4,6,5,7])
        c0,c1,c2=(c(j) for j in range(3))
        pp=mm(mm(sall,u,p),sall,p);qq=mm(mm(sall,v,p),sall,p)
        j=mm(mm(pauli(0,2),v,p),c2,p)
        k=mm(mm(c0,c1,p),c2,p)
        m=mono([2,0,3,1,4,6,5,7],[0,0,2,2,1,3,3,1])
        return {'A':c0,'C2':c2,'P':pp,'Q':qq,'J':j,'W':pauli(0,5),'K':k,'a':pauli(1,3),'M':m}
    cases=[]
    for p,ii in ((5,2),(17,4),(97,22)):
        need(ii*ii%p==p-1,'actual port split prime')
        base=letters(p,ii)
        for f in (1,2):
            d={k:tensor(v,f,p) for k,v in base.items()};n=8**f;e=identity(n)
            a,pp,qq,j,w,k,aa,m,c2=[d[z] for z in ('A','P','Q','J','W','K','a','M','C2')]
            l=plus(pp,scale(2,qq,p),p);ai=invmat(a,p)
            branchp=mm(mm(a,pp,p),a,p);branchq=mm(mm(a,qq,p),a,p)
            need(mm(mm(j,w,p),branchp,p)==mm(m,c2,p),'actual P branch')
            need(mm(mm(j,w,p),branchq,p)==mm(k,aa,p),'actual Q branch')
            coupled=mm(mm(a,l,p),a,p)
            dd=mm(mm(j,w,p),a,p);ddi=invmat(dd,p)
            expected=plus(mm(m,c2,p),scale(2,mm(k,aa,p),p),p)
            need(mm(mm(dd,l,p),a,p)==expected,'actual third-call target plus residual')
            # Both inverse block products reduce to these exact diagonal/lower-block identities.
            need(mm(a,ai,p)==e and mm(ai,a,p)==e,'two-call diagonal inverses')
            need(mm(dd,ddi,p)==e and mm(ddi,dd,p)==e,'three-call diagonal inverses')
            need(mm(coupled,ai,p)==mm(a,l,p),'two-call reverse lower block')
            need(mm(ai,coupled,p)==mm(l,a,p),'two-call forward lower block')
            need(mm(mm(dd,l,p),mm(a,ai,p),p)==mm(dd,l,p),'three-call reverse lower block')
            need(mm(ddi,mm(mm(dd,l,p),a,p),p)==mm(l,a,p),'three-call forward lower block')
            wrongm=[row[:] for row in m]
            for row in wrongm:row[0]=row[0]*ii%p
            need(mm(mm(j,w,p),branchp,p)!=mm(wrongm,c2,p),'actual phase mutation')
            if p not in (3,5):
                pinv=invmat(pp,p);rr=mm(pinv,qq,p)
                rr2=mm(rr,rr,p);rr3=mm(rr2,rr,p);rr4=mm(rr3,rr,p)
                need(rr4==e,'actual relative letter order four')
                poly=plus(plus(e,scale(-2,rr,p),p),plus(scale(4,rr2,p),scale(-8,rr3,p),p),p)
                li=scale(-pow(15,-1,p),mm(poly,pinv,p),p)
                need(mm(l,li,p)==e and mm(li,l,p)==e,'optional coupling inverse')
            else:
                try:invmat(l,p)
                except RuntimeError:pass
                else:raise RuntimeError('characteristic five singular-coupling control')
            # Tensoring the sum replaces coefficient 2 by extra mixed terms and is wrong.
            if f==2:
                wrong=tensor(plus(base['P'],scale(2,base['Q'],p),p),2,p)
                need(wrong!=l,'whole-sum tensor mutant rejected')
            cases.append({'prime':p,'width':f,'array_length':n,'two_paid_call_port':True,
                          'three_paid_call_port':True,'optional_coupling_inverse':p not in (3,5)})
    return {'actual_literal_cases':cases,'absolute_phase_preserved':True,
            'whole_sum_tensor_mutant_rejected':True,
            'characteristic_five_port_survives_singular_coupling':True}



def crt_signed_convolution():
    # Exact signed negacyclic recovery; this pays for all prime channels.
    primes=[17,97];modulus=17*97
    def crt(u,v):
        z=(u+17*(((v-u)*pow(17,-1,97))%97))%modulus
        return z-modulus if 2*z>=modulus else z
    cases=0
    for r in (2,4,8):
        bound=r*3*3
        need(modulus>2*bound,'strict signed CRT range')
        for seed in range(64):
            a=[((seed+3*j*j)%7)-3 for j in range(r)]
            b=[((2*seed+5*j+1)%7)-3 for j in range(r)]
            exact=[0]*r
            for i,x in enumerate(a):
                for j,y in enumerate(b):
                    q,k=divmod(i+j,r);exact[k]+=(-1 if q else 1)*x*y
            channels=[[x%p for x in exact] for p in primes]
            need([crt(u,v) for u,v in zip(*channels)]==exact,'signed negacyclic CRT')
            cases+=1
    # Modulus alone never recovers signed data outside its strict range.
    need(crt((-825)%17,(-825)%97)!=-825,'insufficient modulus mutant rejected')
    return {'cases':cases,'primes':primes,'modulus':modulus,
            'max_coefficient_bound':72,'strict_recovery_modulus_lower_bound':144,
            'paid_prime_channels':2,'insufficient_modulus_mutant_rejected':True}


def run():
    return {'lazy_butterfly':lazy_inverse_butterfly(),'truncated_fourier':truncated_fourier(),
            'split_base_change':split_gaussian_base_change(),'packing_precision_invoice':packing_and_precision(),
            'actual_cp22f_modular_port':actual_cp22f_modular_port(),
            'crt_signed_convolution':crt_signed_convolution()}


if __name__=='__main__':
    got=run(); path=Path(__file__).with_name('EXPECTED.json')
    if '--write-expected' in sys.argv:
        path.write_text(json.dumps(got,indent=2)+'\n',encoding='utf-8')
    else:
        need(got==json.loads(path.read_text(encoding='utf-8')),'deterministic expected receipt')
        print(json.dumps(got,sort_keys=True))
        print('PASS_RAM_LITERATURE_TECHNIQUES')
