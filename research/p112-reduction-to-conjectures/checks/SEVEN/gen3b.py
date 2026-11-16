import sys; sys.path.insert(0,'../CARRIER'); from lib import lines,lab,n,simple
import sympy
def parab(J):
    M=sympy.Matrix.hstack(*[sympy.Matrix(simple[j]) for j in J]); r=M.rank()
    return [t for t in range(n) if sympy.Matrix.hstack(M,sympy.Matrix(lines[t])).rank()==r]
with open('tri7b.in','w') as f:
    f.write(' '.join(map(str,lab))+'\n')
    for J in [list(range(6)), [0,1,2,3,4,6]]:
        PJ=set(parab(J)); T=[t for t in range(n) if t not in PJ]
        f.write('%d %d %s\n'%(len(J),len(T),' '.join(map(str,T)))); print(J,len(PJ),len(T))
