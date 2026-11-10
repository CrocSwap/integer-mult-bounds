"""Exact all-allocation direct-invoice exclusion; Apache-2.0.
Jerry Chen / @CubeJerry with substantial OpenAI Codex assistance.
Native invoice: zxv #6726. Prefix geometry: thu-nmrc #6717 and Ali Romman.
"""
from fractions import Fraction as Q
from itertools import combinations_with_replacement
from collections import Counter
from pathlib import Path
import json,sys,ast,hashlib
K=Q('0.00330720');SCALE=10**12;TAIL=128
K_END=Q('0.004')
HELPERS={1:14,2:8,3:4,4:108,5:16,6:3,7:9,8:40,9:361}
PAID={1:2231,2:454,3:490,4:109,5:152,6:8,7:9,8:1}
def need(ok,message):
 if not ok:raise ValueError(message)
def log_series(x):
 z=(x-1)/(x+1);z2=z*z;term=z;lo=Q(0)
 for j in range(36):lo+=2*term/(2*j+1);term*=z2
 return lo,lo+2*term/(73*(1-z2))
L2=log_series(Q(2))
def log_bounds(n):
 e=n.bit_length()-1;l,h=log_series(Q(n,2**e))
 return l+e*L2[0],h+e*L2[1]
def exp_bounds(x):
 need(0<=x<1,'Small nonnegative exponential argument')
 total=term=Q(1)
 for j in range(1,17):term*=x/j;total+=term
 first=term*x/17
 return total,total+first/(1-x/18)
def h_bounds(n,k=K):
 l,u=log_bounds(n);el=exp_bounds(k*l)[0];eu=exp_bounds(k*u)[1]
 return Q(n)/eu,Q(n)/el
def fixed_h(n):
 l,u=h_bounds(n)
 return (l*SCALE).__floor__(),(u*SCALE).__ceil__()
def inventory():
 out={}
 for m in combinations_with_replacement((3,6,7,12,14,15),8):
  r=tuple(sum(x>>i&1 for x in m)for i in range(4))
  if min(r)<4 or m.count(15)<2 or r[1]+r[2]<10:continue
  if r[0]+2*r[2]<16 or 2*r[1]+r[3]<16:continue
  out[m]=r
 return out
def minimal_inventory(inv):
 return {m:r for m,r in inv.items()if not any(tuple(sorted(m[:j]+(x^(1<<i),)+m[j+1:]))in inv for j,x in enumerate(m)for i in range(4)if x>>i&1)}
def reverse_mask(m):return sum(((m>>i)&1)<<(3-i)for i in range(4))
def authenticate():
 root=Path(__file__).resolve().parent
 pins=json.loads((root/'ORIGINS.json').read_text())
 for p in pins['files']:
  b=(root/p['local']).read_bytes()
  need(hashlib.sha256(b).hexdigest()==p['sha256'],'Pinned source SHA256 '+p['local'])
  need(hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==p['git_blob'],'Pinned Git blob '+p['local'])
 parsed={}
 for node in ast.parse((root/'inputs/pr6726-pricing.py').read_text()).body:
  if isinstance(node,ast.Assign):
   for target in node.targets:
    if isinstance(target,ast.Name)and target.id in('HELPERS','LOCAL_PAID'):parsed[target.id]=ast.literal_eval(node.value)
 need(parsed==dict(HELPERS=HELPERS,LOCAL_PAID=PAID),'Exact authenticated native signed invoice')
 return len(pins['files'])
def interval_monotonicity():
 # An outward upper bound on native ell'(k), uniformly over the stated interval.
 derivative=Q(0)
 for r in range(1,10):
  v=HELPERS.get(r,0)-PAID.get(r,0);l,u=log_bounds(r)
  derivative-=v*(h_bounds(r,K_END)[0]*l if v>=0 else h_bounds(r,K)[1]*u)/104
 need(derivative<0,'Native signed moment decreases over the kappa interval')
 # r^(-k) log(r) increases on [1,1025], so r^(1-k)log(r) is superadditive here.
 need(K_END*log_bounds(8*TAIL+1)[1]<1,'Finite-range derivative superadditivity')
 return dict(end=str(K_END),native_derivative_upper=str(Q((derivative*SCALE).__ceil__(),SCALE)))
def tail():
 ell=Q(0)
 for r in range(1,10):
  l,u=h_bounds(r);v=HELPERS.get(r,0)-PAID.get(r,0);ell+=v*(u if v>=0 else l)/104
 h16=h_bounds(16);h17=h_bounds(17);ahi=2*(h17[1]-h16[0])-1;h=h_bounds(2*TAIL)[1]
 b=TAIL*ell+(TAIL-4)*ahi+8*h+3;der=ell+ahi+16*(1-K)*h/(2*TAIL)
 need(b<0 and der<0,'Concave all-size tail is strictly negative')
 return dict(start=TAIL,upper=str(Q((b*SCALE).__ceil__(),SCALE)),derivative_upper=str(Q((der*SCALE).__ceil__(),SCALE)),upper_decimal=float(b),derivative_upper_decimal=float(der))
def main():
 source_files=authenticate();monotonicity=interval_monotonicity()
 inv=inventory();mini=minimal_inventory(inv)
 can={min(m,tuple(sorted(reverse_mask(x)for x in m)))for m in mini}
 need((len(inv),len(mini),len(can))==(267,9,6),'Complete finite support inventory')
 hs=[(0,0)]+[fixed_h(n)for n in range(1,8*TAIL+2)]
 ell=sum((HELPERS.get(r,0)-PAID.get(r,0))*(hs[r][1]if HELPERS.get(r,0)>=PAID.get(r,0)else hs[r][0])for r in range(1,10))
 lo=[hs[8*n][0]for n in range(TAIL+1)];up=[hs[8*n+1][1]for n in range(TAIL+1)];d=[0]*(TAIL+1)
 for n in range(2,TAIL+1):d[n]=max(d[j]+d[n-j]for j in range(1,n))+2*(up[n]-lo[n])-SCALE
 pats=[]
 for m in sorted(can):
  r=tuple(sum(x>>i&1 for x in m)for i in range(4));c=Counter(m)
  pats.append((m,r,tuple(c[x]for x in(3,6,7,12,14,15)),tuple(x-4 for x in r)))
 def bound(a,m,r):
  f=sum(a)
  return 2*f*ell+208*sum(d[x]for x in a)+104*(sum(up[sum(a[i]for i in range(4)if x>>i&1)]for x in m)-sum((r[i]-4)*lo[a[i]]for i in range(4)))-208*SCALE
 best=None;winner=None;count=0
 for f in range(4,TAIL):
  base=2*f*ell-208*SCALE;t15=up[f]
  for a in range(1,f-2):
   ha=lo[a];da=d[a]
   for b in range(1,f-a-1):
    hb=lo[b];dab=da+d[b];t3=up[a+b]
    for c in range(1,f-a-b):
     z=f-a-b-c;hc=lo[c];hz=lo[z];common=base+208*(dab+d[c]+d[z])
     t6=up[b+c];t7=up[a+b+c];t12=up[c+z];t14=up[b+c+z];count+=1
     for idx,(_,_,co,ex)in enumerate(pats):
      v=common+104*(co[0]*t3+co[1]*t6+co[2]*t7+co[3]*t12+co[4]*t14+co[5]*t15-ex[0]*ha-ex[1]*hb-ex[2]*hc-ex[3]*hz)
      if best is None or v>best:best=v;winner=(a,b,c,z,idx)
  if f%16==0:print('checked total leaves through',f,flush=True)
 need(best<0,'Every full recursive invoice is strictly losing')
 a=winner[:4];m,r,_,_=pats[winner[4]]
 need(best==bound(a,m,r),'Loop equals direct full-invoice formula')
 need(best+208*SCALE>0,'Omitting root thin query changes upper sign')
 result=dict(status='PASS_Q2_N4_FOUR_STAGE_DIRECT_INVOICE_EXCLUSION',kappa=str(K),authenticated_source_files=source_files,monotonicity=monotonicity,inventory_count=len(inv),minimal_count=len(mini),reflection_classes=len(pats),allocation_count=count,checked_pattern_allocations=count*len(pats),scale=SCALE,gap_upper_numerator=best,gap_upper_denominator=208*SCALE,gap_upper_decimal=best/(208*SCALE),winner=dict(child_sizes=a,masks=m,ranks=r),tail=tail(),scope='q2 n4 full sites0,1,3,4; shortest query root; arbitrary compatible commuting actual-prefix stages; binary children; direct separately paid stage idles; no new retirement or cross-stage idle fusion; ordinary work optimistically free',source_pr6726_head='435bbe91fb28cb1d7a569ca70c6c4e9eb302d486',source_pr6717_head='3c9072b8738323dda9f9c7dfb421d578ed3fc17a')
 print(json.dumps(result,indent=2),flush=True)
 receipt=Path(__file__).with_name('DIRECT-INVOICE-RESULT.json')
 if '--write'in sys.argv:receipt.write_text(json.dumps(result,indent=2)+'\n')
 else:need(json.loads(json.dumps(result))==json.loads(receipt.read_text()),'Complete mathematical receipt reproduced')
if __name__=='__main__':main()
