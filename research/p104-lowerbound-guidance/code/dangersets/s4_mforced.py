# Gram class: solve for all real M (8x8) with l^T M l = l.l on ports and l^T M l' = 0 on orthogonal port pairs. Exact (sympy rational).
import numpy as np, sympy as sp
from ds_lib import *
L=e8_lines()
def solve(P,nm):
    rows=[];rhs=[]
    n=len(P)
    for i in range(n):
        for j in range(n):
            if i==j or (P[i]@P[j])==0:
                rows.append(np.outer(P[i],P[j]).reshape(-1)); rhs.append(8 if i==j else 0)
    A=sp.Matrix(np.array(rows,dtype=object)); b=sp.Matrix(rhs)
    r=A.rank(); 
    print(nm,'constraints',len(rows),'rank',r,'of 64 unknowns -> solution space dim',64-r)
    if r==64:
        sol=A.solve_least_squares(b) if False else None
for nm,P in (('halfspin',halfspin(L)),('E7(in R8)',e7a1(L)[:-1]),('E7A1',e7a1(L)),('P120',L)):
    solve(P,nm)
