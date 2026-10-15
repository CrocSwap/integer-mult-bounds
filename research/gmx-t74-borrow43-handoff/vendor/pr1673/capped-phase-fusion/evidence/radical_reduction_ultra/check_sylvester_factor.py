#!/usr/bin/env python3
from fractions import Fraction as F
from pathlib import Path
import json

def conv(a,b,n=None):
 c=[F(0)]*(len(a)+len(b)-1)
 for i,x in enumerate(a):
  for j,y in enumerate(b): c[i+j]+=x*y
 return c if n is None else (c+[F(0)]*n)[:n]
def poly(xs):
 p=[F(1)]
 for x in xs:p=conv(p,[F(1),x])
 return p
def inv(a,n):
 out=[1/a[0]]
 for k in range(1,n):out.append(-sum(a[j]*out[k-j] for j in range(1,min(k,len(a)-1)+1))/a[0])
 return out
def mm(a,b):return [[sum(a[i][k]*b[k][j] for k in range(len(b))) for j in range(len(b[0]))] for i in range(len(a))]
def test(b,gap):
 r=256
 left=[F(r)**i for i in range(b)]
 right=[F(r)**(b+gap+i) for i in range(b)]
 anchor=16*left[-1]
 f=poly([x/anchor for x in left]); g=poly([anchor/x for x in right])
 fi=inv(f,4*b+2)
 def h(k):return sum(g[v]*fi[k+v] for v in range(b+1) if 0<=k+v<len(fi))
 tf=[[f[i-j] if 0<=i-j<len(f) else 0 for j in range(2*b)] for i in range(2*b)]
 s=[[F(0) for _ in range(2*b)] for _ in range(2*b)]
 for j in range(b):
  for k in range(b+1):
   if j+k<2*b:s[j+k][j]+=f[k]
   if 0<=b+j-k<2*b:s[b+j-k][b+j]+=g[k]
 middle=[[F(0) for _ in range(2*b)] for _ in range(2*b)]
 for i in range(b):
  middle[i][i]=1
  for j in range(b):
   middle[i][b+j]=h(i-b-j)
   middle[b+i][b+j]=h(i-j)
 assert mm(tf,middle)==s
 norm=max(sum(abs(h(i-j)-int(i==j)) for j in range(b)) for i in range(b))
 assert norm<F(1,2)
 return 4*b*b, norm
count=entries=0; worst=F(0)
for b in range(1,10):
 for gap in range(3):
  n,w=test(b,gap);count+=1;entries+=n;worst=max(worst,w)
out={'status':'pass','arithmetic':'exact rational','merge_instances':count,'matrix_entries':entries,'max_H_minus_identity_row_norm_approx':float(worst),'exact_norm_bound':'< 1/2 in every instance','remaining':'Stable shallow in-place application of full Toeplitz H; Gaussian gauge localization'}
Path(__file__).with_name('SYLVESTER-CONTROLS.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
