# dump labels + Off sets (rank-7 parabolics: remove node k) + root control, for tri7.c
import sys,itertools; sys.path.insert(0,'../CARRIER'); sys.path.insert(0,'../G777')
from lib import lines,lab,n
import sympy
full=(1<<n)-1
def parab(J):
    S=[sympy.Matrix(__import__('lib').simple[j]) for j in J]
    M=sympy.Matrix.hstack(*S); r=M.rank()
    return [t for t in range(n) if sympy.Matrix.hstack(M,sympy.Matrix(lines[t])).rank()==r]
with open('tri7.in','w') as f:
    f.write(' '.join(map(str,lab))+'\n')
    for k in range(8):
        J=[j for j in range(8) if j!=k]; PJ=set(parab(J))
        T=[t for t in range(n) if t not in PJ]
        f.write('%d %d %s\n'%(k,len(T),' '.join(map(str,T))))
        print('remove simple',k,'|Phi_J|',len(PJ),'|Off|',len(T))
