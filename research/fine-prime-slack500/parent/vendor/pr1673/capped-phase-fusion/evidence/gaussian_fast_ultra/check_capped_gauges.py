#!/usr/bin/env python3
from fractions import Fraction as F
from pathlib import Path
import json

def p2(n):return F(2)**n

def carve(L,W,cap):
 if L<=6*W:return [('B',0,L)]
 ps=[('B',0,W)];pos=W;R=L-2*W
 while R>4*W:
  B=min(cap,1<<((R-W).bit_length()-1))
  ps.append(('I',pos,pos+B));pos+=B
  ps.append(('B',pos,pos+W));pos+=W;R-=B+W
 if R:ps.append(('B',pos,pos+R));pos+=R
 ps.append(('B',pos,L))
 return ps

def main():
 c={'partitions':0,'narrow_slope_pairs':0,'rounded_ratio_and_exact_reanchoring_pairs':0,'broad_slope_pairs':0}
 for W in [1,2,3,5,9,17]:
  for power in range(2,11):
   cap=1<<power
   for L in list(range(1,501))+[1001,4097,20003,100003]:
    ps=carve(L,W,cap);ins=[x for x in ps if x[0]=='I']
    assert ps[0][1]==0 and ps[-1][2]==L
    assert all(x[2]==y[1] for x,y in zip(ps,ps[1:]))
    assert all(0<b-a<=cap and (b-a)&(b-a-1)==0 for _,a,b in ins)
    assert all(y[1]-x[2]>=W for x,y in zip(ins,ins[1:]))
    budget=(L+cap-1)//cap+cap.bit_length()+10
    assert len(ins)<=budget
    assert sum(b-a for typ,a,b in ps if typ=='B')<=W*budget
    c['partitions']+=1
 for s in range(3,31):
  for K in range(1,min(s,6)):
   rho=F(s+K,s);theta=rho-1;lam=1/rho
   q=[(2*(s+K)*i+s)//(2*s) for i in range(s)]
   cells={}
   for i in range(s):cells.setdefault(q[i]-i,[]).append(i)
   # a/log(2)=4*s*K makes every original narrow weight dyadic.
   exps=[4*(K*i-s*(q[i]-i))**2-s*s for i in range(s)]
   aa=[p2(e) for e in exps];eta=p2(-2*s*s-100)
   ah=[x-(1+i%4)*eta for i,x in enumerate(aa)]
   for phase,inds in cells.items():
    for start in range(0,len(inds),3):
     block=inds[start:start+3];m=block[0]
     for i in block:
      for j in block:
       assert abs(exps[i]-exps[j])<=4*s*K*abs(i-j)
       c['narrow_slope_pairs']+=1
       assert F(1,2)*p2(-4*s*K*abs(i-j))<=ah[i]/ah[j]<=2*p2(4*s*K*abs(i-j))
       kernel=F(2,3) if i!=j else F(1)
       before=ah[i]*kernel/ah[j]
       after=(ah[i]/ah[m])*kernel/(ah[j]/ah[m])
       assert before==after
       c['rounded_ratio_and_exact_reanchoring_pairs']+=1
    # Broad gauges on target coordinates in the original physical phase cell.
    target=[q[i] for i in inds];anchor=target[len(target)//2]
    delta=(1-lam)*anchor-phase
    def col(k):
     x=k-anchor
     return -((1-lam)*x*x+2*delta*x)
    def row(k):
     y=k-anchor
     return lam*(1-lam)*y*y+2*delta*lam*y-delta*delta
    for i in target:
     for j in target:
      assert abs(col(i)-col(j))<=abs(i-j)
      assert abs(row(i)-row(j))<=abs(i-j)
      c['broad_slope_pairs']+=1
 out={'status':'all exact assertions passed','arithmetic':'integers and fractions.Fraction','checks':c,'scope':'Capped dyadic carving, narrow exact log-slope, positive perturbed global weights, exact local reanchoring, and broad gauge log-slope. Final tensor schedule/ledger excluded.'}
 Path(__file__).with_name('CAPPED-GAUGE-CONTROLS.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
