"""Exact counterexamples to two tempting but invalid integration shortcuts."""
from fractions import Fraction as Q
import importlib.util
from pathlib import Path

spec=importlib.util.spec_from_file_location('boundary_oracles',Path(__file__).with_name('oracles.py'))
O=importlib.util.module_from_spec(spec);spec.loader.exec_module(O)
ZERO=O.ZERO;ONE=O.ONE


def need(ok,message):
    if not ok:raise ValueError(message)


def inv(z):
    norm=z[0]*z[0]+z[1]*z[1];need(norm!=0,'nonzero Gaussian denominator')
    return z[0]/norm,-z[1]/norm


def matmul(a,b):
    return [[sum_pairs(O.mul(x,y) for x,y in zip(row,column)) for column in zip(*b)] for row in a]


def sum_pairs(values):
    result=ZERO
    for value in values:result=O.add(result,value)
    return result


def matrix_rank(a):
    a=[row[:] for row in a];rank=0
    for column in range(len(a[0])):
        pivot=next((i for i in range(rank,len(a)) if a[i][column]!=ZERO),None)
        if pivot is None:continue
        a[rank],a[pivot]=a[pivot],a[rank];v=inv(a[rank][column]);a[rank]=[O.mul(v,z) for z in a[rank]]
        for i in range(len(a)):
            if i==rank:continue
            coefficient=a[i][column]
            a[i]=[O.add(x,O.scale(O.mul(coefficient,y),-1)) for x,y in zip(a[i],a[rank])]
        rank+=1
    return rank


def newton_boundary():
    r=4;u=(Q(0),Q(1));powers=[ONE]
    for _ in range(r):powers.append(O.mul(powers[-1],u))
    H=[ONE]
    for j in range(1,r):H.append(O.mul(H[-1],O.add(ONE,O.scale(powers[j],-1))))
    h=[inv(z) for z in H]
    triangular=[[h[i-j] if i>=j else ZERO for j in range(r)] for i in range(r)]
    cyclic=[[h[(i-j)%r] for j in range(r)] for i in range(r)]
    diagonal=[O.scale(powers[(i*(i-1)//2)%r],(-1)**i) for i in range(r)]
    def assembled(kernel):
        N=[[O.mul(O.mul(H[i],kernel[i][j]),diagonal[j]) for j in range(r)] for i in range(r)]
        Dinv=[[inv(O.mul(H[i],diagonal[i])) if i==j else ZERO for j in range(r)] for i in range(r)]
        return matmul(matmul(N,Dinv),list(map(list,zip(*N))))
    fourier=[[powers[(i*j)%r] for j in range(r)] for i in range(r)]
    correct=assembled(triangular);wrong=assembled(cyclic)
    difference=[[O.add(c,O.scale(t,-1)) for c,t in zip(crow,trow)] for crow,trow in zip(cyclic,triangular)]
    need(correct==fourier,'Newton reconstruction')
    need(wrong!=fourier,'invalid cyclic substitution undetected')
    need(matrix_rank(difference)==r-1,'wrap boundary rank')
    witness=next(j for j in range(r) if [row[j] for row in wrong]!=[row[j] for row in fourier])
    return dict(radix=r,triangular_reconstruction_exact=True,cyclic_replacement_rejected=True,wrap_correction_rank=matrix_rank(difference),
                witness_basis_column=witness,expected=[row[witness] for row in fourier],invalid_cyclic_output=[row[witness] for row in wrong],
                general_observation='P(Z_r)-P(J_r) is strictly upper triangular, with every first-superdiagonal entry h_(r-1)=1/r. Its rank is r-1 for every r>=2 in characteristic zero.')


def gf4_mul(x,y):
    result=0
    for _ in range(2):
        if y&1:result^=x
        y>>=1;x<<=1
        if x&4:x^=7
    return result


def gf4_poly_product(a,b):
    out=[0]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b):out[i+j]^=gf4_mul(x,y)
    return out


def bit_field_boundary():
    # GF(4)=GF(2)[u]/(u^2+u+1); encodings 0,1,u,u+1 are 0,1,2,3.
    u=2
    need(gf4_mul(u,u)==u^1 and gf4_mul(gf4_mul(u,u),u)==1,'primitive cube root')
    h1=next(x for x in range(1,4) if gf4_mul(1^u,x)==1)
    denominator=gf4_mul(1^u,1^gf4_mul(u,u))
    h2=next(x for x in range(1,4) if gf4_mul(denominator,x)==1)
    P=[1,h1,h2];R=[1,u,u,1]
    need(P==[1,u,1] and gf4_poly_product(P,R)==[1,0,0,0,0,1],'exact finite-field factor identity')
    vector=R+[0];image=[0]*5
    for j,coefficient in enumerate(P):
        for i,value in enumerate(vector):image[(i+j)%5]^=gf4_mul(coefficient,value)
    need(any(vector) and not any(image),'singular length-five cyclic inverse')
    # Expanding every GF(4) value into two F2 coordinates gives a Boolean
    # singular operator as well. Check that the nonzero witness survives it.
    binary_vector=[(value>>bit)&1 for value in vector for bit in (0,1)]
    need(any(binary_vector),'nonzero Boolean encoding')
    return dict(field='GF(2)[u]/(u^2+u+1)',encoding={'1':1,'u':2,'u+1':3},radix=3,cyclic_length=5,
                kernel=P,quotient=R,polynomial_product=gf4_poly_product(P,R),nonzero_kernel_vector=vector,image=image,
                binary_kernel_vector=binary_vector,verdict='P(S_5) is singular despite primitive radix-3 phase and nonzero preparation denominators. Complex unit-circle nonvanishing does not transfer to Boolean arithmetic through this field.')
