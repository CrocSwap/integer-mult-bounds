"""Independent rectangular operator ring for the three fresh physical planes.

No candidate modules are imported. Nonempty residues are not physical witnesses.
Relations used: q^4=1; Z_s W_s=14; D_s q=q D_s; fresh D commutes W/Z;
D_s a_s=q^-1 a_s q D_s, from exact R_s intertwining. Rational coefficients
are exterior. D powers are stored on the right of a noncommuting native word.
"""
from fractions import Fraction
from collections import defaultdict

def need(x,s):
    if not x:raise ValueError(s)

class Ring:
    def reduce(self,word):
        stack=[];factor=Fraction(1)
        for token in word:
            kind,index=token
            if kind=='q':
                index%=4
                if not index:continue
                if stack and stack[-1][0]=='q':index=(stack.pop()[1]+index)%4
                if index:stack.append(('q',index))
            elif kind=='w'and stack and stack[-1]==('z',index):stack.pop();factor*=14
            else:
                need(kind in('w','z')and index in(0,1,2),'physical typed generator')
                stack.append((kind,index))
        return tuple(stack),factor
    def monomial(self,word=(),d=(0,0,0),coefficient=1):
        w,c=self.reduce(word);c*=Fraction(coefficient)
        return {(w,tuple(d)):c}if c else{}
    def add(self,*polys):
        out=defaultdict(Fraction)
        for p in polys:
            for k,c in p.items():out[k]+=c
        return {k:c for k,c in out.items()if c}
    def scale(self,p,c):return {k:v*Fraction(c)for k,v in p.items()if v*c}
    def shift(self,d,word):
        moved=[]
        for a,s in word:
            if a=='q':moved.append((a,s))
            else:moved.extend((('q',-d[s]),(a,s),('q',d[s])))
        return tuple(moved)
    def product(self,*polys):
        out=self.monomial()
        for p in polys:
            nxt=defaultdict(Fraction)
            for(w,d),a in out.items():
                for(v,e),b in p.items():
                    key,c=self.reduce(w+self.shift(d,v));nxt[key,tuple(x+y for x,y in zip(d,e))]+=a*b*c
            out={k:c for k,c in nxt.items()if c}
        return out
    def q(self,e=1):return self.monomial((('q',e),))
    def w(self,s):return self.monomial((('w',s),))
    def z(self,s):return self.monomial((('z',s),))
    def d(self,s):
        v=[0,0,0];v[s]=1;return self.monomial(d=v)
    def identity(self,n):return [[self.monomial()if i==j else{}for j in range(n)]for i in range(n)]
    def matrix(self,a,b):
        need(all(len(row)==len(b)for row in a),'matrix dimension')
        return [[self.add(*(self.product(a[i][k],b[k][j])for k in range(len(b))))for j in range(len(b[0]))]for i in range(len(a))]
    def leftrow(self,p,row):return [self.product(p,x)for x in row]
    def rowsum(self,a,b,c=1):return [self.add(x,self.scale(y,c))for x,y in zip(a,b)]
    def typecheck(self,p,target,source):
        for(word,d),coefficient in p.items():
            typ=source
            for op,s in reversed(word):
                if op=='w':need(typ=='h','W input dimension');typ='p'
                elif op=='z':need(typ=='p','Z input dimension');typ='h'
                else:need(op=='q','native generator')
            need(typ==target,'rectangular endpoint dimension')
    def serialize(self,p):
        return [{'coefficient':str(c),'native_word':[[k,s]for k,s in w],'D_right':list(d)}for(w,d),c in sorted(p.items(),key=lambda x:str(x[0]))]

def hcode(r,s,inverse=False):
    one=r.monomial();w,z=r.w(s),r.z(s)
    if inverse:return [[one,w],[r.scale(z,-1),r.monomial(coefficient=-13)]]
    return [[r.add(one,r.scale(r.product(w,z),-1)),r.scale(w,-1)],[z,one]]

def frozen_closed_base(r):
    """Independent closed contract, not a replay of the submitted row producer."""
    G=r.product(r.d(2),r.d(1),r.d(0));S=r.product(r.q(),r.z(0),r.q(-1));T=r.product(r.q(),r.w(0),r.q(-1));one=r.monomial()
    H=r.matrix(hcode(r,2),hcode(r,1,True))
    N=[[r.product(r.q(-1),H[i][j],G)for j in range(2)]for i in range(2)]
    C=[[{},r.scale(r.product(r.w(1),G),-1)],
       [r.product(r.add(r.z(1),r.product(r.add(one,r.scale(r.product(r.z(1),T),-1)),S)),G),
        r.product(r.add(r.monomial(coefficient=14),r.scale(r.product(r.z(1),T),-1)),G)]]
    A=[N[0]+[{},{}],N[1]+[{},{}],C[0]+[r.product(r.q(),G),{}],C[1]+[{},r.product(r.q(),G)]]
    K0=[r.scale(r.product(r.z(0),r.q(-1),r.d(0)),-1),r.scale(r.product(r.q(-1),r.d(0)),-1),{},{}]
    K2=r.leftrow(r.scale(r.q(-1),-1),r.rowsum(r.leftrow(r.z(2),A[2]),A[3]))
    return A,[K0,K2]

def changed_expected(r):
    """Separately derived target formulas for ONE new joint extension."""
    one=r.monomial();G=r.product(r.d(2),r.d(1),r.d(0));S=r.product(r.q(),r.z(0),r.q(-1));T=r.product(r.q(),r.w(0),r.q(-1));delta=r.add(r.z(2),r.scale(r.z(1),-1));B=r.add(r.product(r.z(2),r.w(1)),r.monomial(coefficient=-13))
    npx=r.product(r.q(-1),r.add(one,r.scale(r.product(r.w(2),delta),-1),r.scale(r.product(r.w(1),S),-1),r.product(r.w(2),B,S)),G)
    npk=r.product(r.q(-1),r.add(r.w(1),r.scale(r.product(r.w(2),B),-1)),G)
    nkx=r.product(r.q(-1),r.add(delta,r.scale(r.product(B,S),-1)),G);nkk=r.product(r.q(-1),B,G)
    rows=[[npx,npk,{},{}],[nkx,nkk,{},{}],
          [r.product(r.w(1),S,G),r.scale(r.product(r.w(1),G),-1),r.product(r.q(),G),{}],
          [r.product(r.z(2),G),r.product(r.add(one,r.scale(r.product(r.z(1),T),-1)),G),{},r.product(r.q(),G)]]
    c0=[{},r.scale(r.product(r.q(-1),r.d(0)),-1),{},{}]
    # Actual cache2 retained BEFORE output updates; q^-1 finalPh = nk-cache2.
    c2=r.rowsum(rows[1],r.leftrow(r.q(-1),rows[3]),-1)
    return rows,[c0,c2]
