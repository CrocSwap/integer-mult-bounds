#!/usr/bin/env python3
"""Independent exact full-involution/atom/opposite-bank controls for PR104.
Finite algebra controls, not verification of the inherited tape primitive.
"""
from fractions import Fraction as F
from pathlib import Path
import hashlib,json,argparse
HERE=Path(__file__).resolve().parent

def I(n):return[[F(i==j)for j in range(n)]for i in range(n)]
def Z(n,m=None):return[[F(0)]*(n if m is None else m)for _ in range(n)]
def tr(A):return list(map(list,zip(*A)))
def add(A,B,k=1):return[[x+k*y for x,y in zip(a,b)]for a,b in zip(A,B)]
def mul(A,B):return[[sum((x*y for x,y in zip(a,b)),F())for b in zip(*B)]for a in A]
def inv(A):
 n=len(A);B=[list(a)+b for a,b in zip(A,I(n))]
 for j in range(n):
  k=next(i for i in range(j,n)if B[i][j]);B[j],B[k]=B[k],B[j];q=B[j][j];B[j]=[x/q for x in B[j]]
  for i in range(n):
   if i!=j:
    q=B[i][j];B[i]=[x-q*y for x,y in zip(B[i],B[j])]
 return[b[n:]for b in B]
def kron(A,B):return[[x*y for x in a for y in b]for a in A for b in B]
def block(A,B,C,D):return[a+b for a,b in zip(A,B)]+[c+d for c,d in zip(C,D)]
def rev(n):return[[F(i+j==n-1)for j in range(n)]for i in range(n)]
def diag(A,B):return block(A,Z(len(A),len(B)),Z(len(B),len(A)),B)
def lower(A):return all(not A[i][j]for i in range(len(A))for j in range(i+1,len(A)))
def mod(A,q):return[[int(x.numerator)*pow(int(x.denominator),-1,q)%q for x in row]for row in A]
def act(A,x,q):return[sum(a*b for a,b in zip(row,x))%q for row in A]
def northeast(A,r):
 n=len(A);M=[row[:]for row in A];L=I(n);R=I(n)
 for i in range(r):
  c=n-1-i;p=M[i][c];assert p
  M[i]=[x/p for x in M[i]];L[i]=[x/p for x in L[i]]
  for k in range(i+1,n):
   q=M[k][c];M[k]=[x-q*y for x,y in zip(M[k],M[i])];L[k]=[x-q*y for x,y in zip(L[k],L[i])]
  for j in range(c):
   q=M[i][j]
   for k in range(n):M[k][j]-=q*M[k][c];R[k][j]-=q*R[k][c]
 assert lower(L)and lower(R)
 return L,R,M

def generate():
 m=4;eye=I(m);C=rev(m);rows=[];negative_missing_atom_reverse=0;negative_missing_diagonals=0;negative_cross_bank_order=0;field_controls=0
 for r in range(1,m):
  V=[[F(x**j)for j in range(r)]for x in(1,2,4,7)];P=mul(mul(V,inv(mul(tr(V),V))),tr(V));assert mul(P,P)==P
  L,R,Pi=northeast(mul(P,C),r);E=[row[:r]for row in eye];G=[row[:r]for row in C];assert Pi==mul(E,tr(G))
  D=block(add(eye,P,-1),mul(P,C),mul(C,P),mul(mul(C,add(eye,P,-1)),C));Q=diag(L,inv(R));g=mul(mul(Q,D),inv(Q));A=[row[:m]for row in add(g,I(2*m),-1)[:r]];B=mul([row[m:]for row in add(g,I(2*m),-1)[m:]],G)
  assert mul(block(E,Z(m,0),B,Z(m,0)),[a+b for a,b in zip(A,tr(G))])==add(g,I(2*m),-1)
  assert add(mul(A,E),mul(tr(G),B))==[[F(-2*(i==j))for j in range(r)]for i in range(r)]
  K=add(mul(add(B,G),tr(E)),mul(mul(G,A),add(eye,mul(E,tr(E)),-1)),-1);K=[[-x for x in row]for row in K]
  assert mul(K,E)==[[-x-y for x,y in zip(a,b)]for a,b in zip(B,G)]
  assert mul(tr(G),K)==add(A,tr(E))
  for f in(1,2,3):
   J=I(f);Cf=rev(f);Qf=diag(kron(L,J),kron(inv(R),J));Sf=block(I(m*f),Z(m*f),kron(K,Cf),I(m*f));assert lower(Qf)and lower(Sf)
   Df=block(kron(add(eye,P,-1),J),kron(mul(P,C),Cf),kron(mul(C,P),Cf),kron(mul(mul(C,add(eye,P,-1)),C),J))
   middle=mul(mul(Sf,mul(mul(Qf,Df),inv(Qf))),inv(Sf));expected=I(2*m*f)
   for a in range(r*f):
    b=2*m*f-1-a;expected[a]=[F(j==b)for j in range(2*m*f)];expected[b]=[F(j==a)for j in range(2*m*f)]
   assert middle==expected
   omitted=block(I(m*f),kron(mul(P,C),Cf),kron(mul(C,P),Cf),I(m*f))
   assert mul(mul(Sf,mul(mul(Qf,omitted),inv(Qf))),inv(Sf))!=expected
   negative_missing_diagonals+=1
   upper_cross=block(I(m*f),kron(K,Cf),Z(m*f),I(m*f))
   assert not lower(upper_cross),'Upper cross-bank controls violate physical predecessor order'
   negative_cross_bank_order+=1
   wrong=block(I(m*f),Z(m*f),kron(K,J),I(m*f))
   if f>1:
    assert mul(mul(wrong,mul(mul(Qf,Df),inv(Qf))),inv(wrong))!=expected;negative_missing_atom_reverse+=1
   for w in(1,2):
    q=101**w;matrices=[Qf,Sf,expected,inv(Sf),inv(Qf)];MM=[mod(X,q)for X in matrices];DD=mod(Df,q)
    # Chronological Q,S,F,S^-1,Q^-1; tests every module basis vector plus
    # vectors at carry boundaries of the radix101 atom ring.
    vectors=[[int(i==j)for i in range(2*m*f)]for j in range(2*m*f)]
    vectors+=[[q-1]*len(DD),[(j*100+101)%q for j in range(len(DD))]]
    for x in vectors:
     y=x
     for M in MM:y=act(M,y,q)
     assert y==act(DD,x,q);field_controls+=1
   rows.append(dict(rank=r,atoms_per_formal_coordinate=f,lower_adapters=True,exact_full_matrix_identity=True))
 # Constant outer wrapper: L_- ; F ; L_+ ; F ; (H,D)->(H,H-D).
 for n in(1,2,4):
  J=I(n);O=Z(n);Fswap=block(O,rev(n),rev(n),O);Lm=block(J,O,[[-x for x in row]for row in J],J);Lp=block(J,O,J,J);last=block(J,O,J,[[-x for x in row]for row in J])
  assert mul(last,mul(Fswap,mul(Lp,mul(Fswap,Lm))))==block(O,J,J,O)
 result=dict(status='PASS',fixtures=rows,modular_complete_basis_and_carry_vectors=field_controls,atom_primes_and_widths=[['101',1],['101',2]],omitted_internal_atom_reversal_rejections=negative_missing_atom_reverse,ordinary_outer_wrapper_dimensions=[1,2,4],omitted_complementary_diagonal_rejections=negative_missing_diagonals,wrong_cross_bank_order_rejections=negative_cross_bank_order,scope='Independent finite exact matrix identities and atom-ring evaluations of PR104 full factorization, lower adapter orientation, and ordinary wrapper. Does not prove ordered-affine streaming cost or the inherited fixed-tape/analytic contract.',source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
 return result

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--record',action='store_true');a=p.parse_args();result=generate();encoded=json.dumps(result,indent=2,sort_keys=True)+'\n';receipt=HERE/'interface-audit.json'
 if a.record:receipt.write_text(encoded)
 else:assert receipt.read_text()==encoded,'Frozen interface audit differs'
 print('Independent full-factorization/atom/wrapper interface controls PASS')
