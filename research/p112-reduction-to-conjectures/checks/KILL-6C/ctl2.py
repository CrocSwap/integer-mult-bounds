# LP controls (kmax=3, same constraints as cert.py): (a) caps from a real E8 configuration must be FEASIBLE; (b) non-vacuity boundary.
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import lil_matrix
N={1:1,2:3,3:6}
def feas(caps,NL=120):
    p=len(caps); Ks=[K for K in range(1,1<<p) if bin(K).count('1')<=3]
    A=lil_matrix((len(Ks)+p,(1<<p)-1)); b=[]
    for i,K in enumerate(Ks):
        s=K
        while s: A[i,s-1]=1; s=(s-1)&K
        b.append(N[bin(K).count('1')])
    for j in range(p):
        for M in range(1,1<<p):
            if M>>j&1: A[len(Ks)+j,M-1]=1
        b.append(caps[j])
    return linprog(np.zeros((1<<p)-1),A_ub=A.tocsr(),b_ub=b,A_eq=np.ones((1,(1<<p)-1)),b_eq=[NL],bounds=(0,None),method='highs').status==0
caps=list(map(int,open('ctl_caps.txt').read().split()))
print('(a) real-config caps',caps,'FEAS' if feas(caps) else 'INFEAS (BUG)')
for c in range(18,23):
    print('(b) 12 pieces uniform cap',c,'sum',12*c,'FEAS' if feas([c]*12) else 'infeas')
print('(b) 411 with one 6->7 extra:', 'FEAS' if feas([36,36]+[20]*8+[12,12]) else 'infeas')
