#!/usr/bin/env python3
"""Exact rational controls for Gaussian Toeplitz q-LDU and shifted exponents."""
from fractions import Fraction as F
from pathlib import Path
import json

def mm(a,b):return [[sum(x*y for x,y in zip(r,c)) for c in zip(*b)] for r in a]
def tr(a):return list(map(list,zip(*a)))
def ident(n):return [[F(i==j) for j in range(n)] for i in range(n)]
def powq(q,n):return q**n

def factors(q,n):
    Q=q*q;P=[F(1)]
    for j in range(1,n):P.append(P[-1]*(1-Q**j))
    bc=lambda i,j:P[i]/(P[j]*P[i-j])
    L=[[q**((i-j)**2)*bc(i,j) if i>=j else F(0) for j in range(n)] for i in range(n)]
    Li=[[(-q)**(i-j)*bc(i,j) if i>=j else F(0) for j in range(n)] for i in range(n)]
    D=[[P[i] if i==j else F(0) for j in range(n)] for i in range(n)]
    return L,Li,D

cases=0;entries=0
for q in (F(1,2),F(1,3),F(2,3)):
  for n in range(1,11):
    L,Li,D=factors(q,n)
    G=[[q**((i-j)**2) for j in range(n)] for i in range(n)]
    assert mm(mm(L,D),tr(L))==G
    assert mm(L,Li)==ident(n) and mm(Li,L)==ident(n)
    # Integer-power diagonal conjugation is an exact finite surrogate.
    diagonal=[q**(i*i-3*i) for i in range(n)]
    Lt=[[L[i][j]*diagonal[i]/diagonal[j] for j in range(n)] for i in range(n)]
    Lit=[[Li[i][j]*diagonal[i]/diagonal[j] for j in range(n)] for i in range(n)]
    assert mm(Lt,Lit)==ident(n)
    cases+=1;entries+=n*n

exponent_cases=0
for rho in (F(1001,1000),F(17,16),F(3,2)):
 theta=rho-1
 for c in (-2,0,3):
  for i in range(15):
   for j in range(i+1):
    h=i-j;beta=theta*i-c
    # D_i/D_j times q^h for the inverse L factor.
    raw=theta*(i*i-j*j)-2*c*(i-j)-rho*h
    condensed=(2*beta-rho)*h-theta*h*h
    assert raw==condensed
    exponent_cases+=1

# Rational validation of the perturbation bound in the worked 24x24 witness.
rbound=F(24,2**23);linv_bound=F(24)
error=linv_bound**2*rbound/(1-linv_bound*rbound)
assert linv_bound*rbound<1 and error<F(1,64)
# For beta <=1/2, the conjugated inverse exponent is at most -theta h(h+1).
for theta in (F(1,1000),F(1,100),F(1,4)):
 for h in range(20):
  for beta in (F(-1,2),F(0),F(49,100),F(1,2)):
   assert (2*beta-(1+theta))*h-theta*h*h <= -theta*h*(h+1)

result=dict(status='PASS_EXACT_Q_LDU_CONTROLS',q_ldu_cases=cases,
            matrix_entries=entries,shifted_exponent_identities=exponent_cases,
            q_values=['1/2','1/3','2/3'],
            perturbation_upper=str(error), perturbation_target='1/64',
            scope='Exact Gaussian Toeplitz LDU, inverse triangular identities, and diagonal-conjugation exponents; not a gapped-node all-size solver.')
Path(__file__).with_name('Q-LDU-CONTROLS.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
