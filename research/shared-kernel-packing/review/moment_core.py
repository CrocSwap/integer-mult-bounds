# SPDX-License-Identifier: Apache-2.0
"""Independent directed dyadic moment review using elementary positive series.
No solver, floating transcendental, mpmath, numpy or upstream checker is imported.
"""
import argparse,hashlib,json,os
from fractions import Fraction as Q
from pathlib import Path
BITS=11000;S=1<<BITS;LOG_TERMS=BITS//3+50;EXP_TERMS=BITS//8+50

def need(p,m):
 if not p:raise AssertionError(m)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def down(q):return q.numerator*S//q.denominator
def up(q):return -((-q.numerator*S)//q.denominator)
def ceildiv(a,b):return -((-a)//b)
def log_ratio(a,b):
 need(1<=Q(a,b)<=2,'log range reduction');z=Q(a-b,a+b);zl=down(z);zu=up(z);z2l=zl*zl//S;z2u=ceildiv(zu*zu,S);vl,vu=zl,zu;lo=hi=0
 for j in range(LOG_TERMS):
  lo+=vl//(2*j+1);hi+=ceildiv(vu,2*j+1)
  vl=vl*z2l//S;vu=ceildiv(vu*z2u,S)
 # Here z <= 1/3 and the unadded power is z^(2J+1).
 tail=ceildiv(9*vu,4*(2*LOG_TERMS+1))
 return 2*lo,2*hi+tail
def log_int(n):
 need(type(n)is int and n>=1,'positive integer base')
 if n==1:return 0,0
 k=n.bit_length()-1;l,u=log_ratio(2,1);a,b=log_ratio(n,1<<k);return k*l+a,k*u+b

def exp_positive(t):
 need(0<=t<=S//2,'small nonnegative exponent');vl=vu=S;lo=hi=S
 for j in range(1,EXP_TERMS+1):
  vl=vl*t//(S*j);vu=ceildiv(vu*t,S*j);lo+=vl;hi+=vu
 # For x <= 1/2, remaining positive Taylor terms are at most twice the first.
 tail=2*ceildiv(vu*t,S*(EXP_TERMS+1))
 return lo,hi+tail
def power(n,alpha):
 # n^(1-alpha) = n / exp(alpha log n).
 l,u=log_int(n);tl=down(alpha*Q(l,S));tu=up(alpha*Q(u,S));el,_=exp_positive(tl);_,eu=exp_positive(tu)
 return n*(S*S//eu),n*(-((-S*S)//el))
def rational(value):
 if isinstance(value,dict):return Q(int(value['numerator']),int(value['denominator']))
 return Q(str(value))
def moment(H,live,m,alpha):
 need(0<alpha<Q(1,100),'exponent saving scope');lo=hi=0;bounds={}
 for n,c in H.items():
  a,b=power(n,alpha);lo+=c*a;hi+=c*b;bounds[n]=[str(a),str(b)]
 a,b=power(m,alpha);return lo-live*b,hi-live*a,bounds

def controls(H,live,m,alpha):
 rejected=[]
 try:moment(H,live,m,Q(1,2))
 except AssertionError:rejected.append('out_of_scope_exponent')
 else:raise AssertionError('exponent control accepted')
 # One additional rank-one child destroys the tiny strict paid slack in the fixture.
 bad=dict(H);bad[1]=bad.get(1,0)+1;l,u,_=moment(bad,live,m,alpha)
 need(l>0,'extra paid child control not strictly rejected');rejected.append('extra_unpaid_rank_one_child')
 return rejected

