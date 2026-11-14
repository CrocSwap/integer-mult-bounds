#!/usr/bin/env python3
from fractions import Fraction as F
from pathlib import Path
import json
from check_lower import matmul,inv,eye

def scan(lam,u):
 P=F(1);Q=F(0)
 for a,b in zip(lam,u):P=a*P;Q=a*Q+b
 prev=Q/(1-P);out=[]
 for a,b in zip(lam,u):prev=a*prev+b;out.append(prev)
 return out

count=0
for n in range(2,31):
 for offset in range(7):
  lam=[F((-1)**(i+offset)*(i%3+1),5+i%4) for i in range(n)]
  u=[F((-1)**i*(2*i+offset+1),i+1) for i in range(n)]
  A=eye(n)
  for i,a in enumerate(lam):A[i][(i-1)%n]-=a
  expected=[r[0] for r in matmul(inv(A),[[x] for x in u])]
  assert scan(lam,u)==expected
  count+=1
out={'status':'all exact assertions passed','cyclic_signed_scan_systems':count,'scope':'Two-pass cyclic affine recurrence against dense exact inversion; bilateral coefficient estimates are analytic.'}
Path(__file__).with_name('CYCLIC-SCAN-CONTROLS.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
