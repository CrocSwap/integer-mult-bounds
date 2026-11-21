# DECOMP: search a k=3, n=2 Q=0 word (un-lifted, u = q) with M(1)=I, M(-1)=-I.
import sympy as sp
x,y,z,w=sp.symbols('x y z w')
def H(a,b,u): return sp.Matrix([[1,a*u],[b/u,1+a*b]])
C1=sp.Matrix([[1,x],[0,1]]); C2=sp.Matrix([[1,0],[y,1]])
def M0(u,a3,b3): return H(a3,b3,u)*C2*H(1,1,u)*C1*H(1,2,u)
for b3 in [1,2,3,-2,sp.Rational(1,2)]:
    C0=M0(1,1,b3).inv()
    E=sp.simplify(M0(-1,1,b3)*C0+sp.eye(2))
    sol=sp.solve([E[0,0],E[0,1],E[1,0],E[1,1]],[x,y],dict=True)
    print(b3,sol)
