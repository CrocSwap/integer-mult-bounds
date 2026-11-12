#!/usr/bin/env python3
"""Independent finite word/caller/invoice audit; no imported author checker.
Native endpoint uses the transposed circuit in reverse chronological order.
Caller identity uses exact polynomials in 18 unrestricted commuting variables
and q modulo q^4-1, with Gaussian rational coefficients.
"""
from collections import Counter
from fractions import Fraction as F
from pathlib import Path
from decimal import Decimal, localcontext
import argparse, gzip, hashlib, json, math, time

HERE=Path(__file__).resolve().parent

if not __debug__: raise RuntimeError('Run without -O; assertions are proof checks.')

def load(p):
 p=Path(p); b=p.read_bytes(); return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def pin(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def addto(a,b,q=F(1)):
 for k,v in b.items():
  z=a.get(k,0)+q*v
  if z:a[k]=z
  else:a.pop(k,None)
def scale(a,q): return {k:v*q for k,v in a.items() if v*q}
def span(b):
 s={0}
 for x in b:
  assert x not in s and 0<x<512
  s |= {v^x for v in s}
 return frozenset(s)
def native(W,mutant=None):
 n=len(W['initial']); assert W['public']==n; N=n+W['owned_fields']; frames=[span(b) for b in W['frames']]
 dim=[(len(f)).bit_length()-1 for f in frames]
 active=set(range(n)); cur=dict(enumerate(W['initial'])); paid=Counter(); rises=Counter(); peak=life=0
 for i,e in enumerate(W['program']):
  op,r=e[:2]
  if op in ('ADD','COPY','SCALE'):
   coeff=F(e[2] if op=='SCALE' else e[3]);assert coeff and abs(coeff)+1<2**16
   def smooth(z):
    for prime in (2,3,5):
     while z%prime==0:z//=prime
    return z==1
   assert smooth(coeff.denominator) and (op!='SCALE' or smooth(abs(coeff.numerator)))
  if op=='INIT':
   assert r>=n and r not in active;active.add(r);cur[r]=e[2];life+=1;peak=max(peak,len(active)-n)
  elif op=='CLEAR':
   assert r>=n and r in active and cur[r]==e[2];active.remove(r);del cur[r]
  elif op=='MOVE':
   _,r,a,b,owned=e;assert r in active and cur[r]==a and owned==(r>=n)
   assert (frames[a]<frames[b]) if not owned else (frames[a]<frames[b] or frames[b]<frames[a])
   rank=abs(dim[b]-dim[a]);assert rank>0;paid[rank]+=1;cur[r]=b
   if owned and dim[b]>dim[a]:rises[rank]+=1
  elif op=='SCALE':assert r in active and cur[r]==e[-1]
  else:assert op in ('ADD','COPY') and r in active and e[2] in active and r!=e[2] and cur[r]==cur[e[2]]==e[-1]
 assert active==set(range(n)) and [cur[r] for r in range(n)]==W['final']
 # adj[r][j] is the derivative of final output j with respect to current r.
 adj=[{r:F(1)} if r<n else {} for r in range(N)]
 for i in reversed(range(len(W['program']))):
  e=W['program'][i];op,r=e[:2]
  if op in ('INIT','CLEAR'):adj[r]={}
  elif op=='MOVE':pass # conjugated scalar coordinate: C_f^{-1}v
  elif op=='SCALE':adj[r]=scale(adj[r],F(e[2])*(2 if i==mutant else 1))
  else:
   s=e[2];q=F(e[3])*(2 if i==mutant else 1);addto(adj[s],adj[r],q)
   if op=='COPY':adj[r]={}
 # Build intended Jacobian by physical input/output labels, then transpose.
 target=[{r:F(1)} for r in range(n)]
 H=W['hosted'];D=set(H['Dports']);live=W['live']
 assert len(live)==len(W['ports'])==104 and len(D)==96
 for i,x in enumerate(live):
  q=W['ports'][i];y=x+112
  assert frames[W['initial'][x]]==frozenset((0,q)) and len(frames[W['final'][x]])==512
  assert frames[W['initial'][y]]==frozenset((0,))
  assert frames[W['final'][y]]==frozenset(v for v in range(512) if (v&q).bit_count()%2==0)
 for i,x,y in zip(H['Dports'],H['X2'],H['Y2']):
  a=live[i];assert W['initial'][x]==W['initial'][a] and W['final'][x]==W['final'][a]
  assert W['initial'][y]==W['initial'][a+112] and W['final'][y]==W['final'][a+112]
 for i,x in enumerate(live):
  y=x+112
  if i in D:target[y][x]=F(1)
  else:target[x][y]=F(-1);target[y]={x:F(1,2),y:F(1,2)}
 for x,y in zip(H['X2'],H['Y2']):target[x][y]=F(-1)
 expect=[{} for _ in range(n)]
 for j,row in enumerate(target):
  for r,q in row.items():expect[r][j]=q
 bad=[r for r in range(n) if adj[r]!=expect[r]]
 main=set(live)|{r+112 for r in live}|set(H['X2'])|set(H['Y2'])
 helper=Counter()
 for r in range(n):
  if r not in main:
   assert frames[W['initial'][r]]<frames[W['final'][r]]
   helper[dim[W['final'][r]]-dim[W['initial'][r]]]+=1
 return dict(public=n,events=len(W['program']),paid=dict(sorted(paid.items())),helpers=dict(sorted(helper.items())),rises=dict(sorted(rises.items())),owned_peak=peak,lifetimes=life,bad_inputs=bad)

# Caller polynomials are keyed by (input role, q exponent mod 4, D monomial).
# D monomial uses 8-bit exponent lanes; no idempotence relation is imposed.
# Gaussian numbers are pairs of exact rationals.
def gadd(a,b):return (a[0]+b[0],a[1]+b[1])
def gmul(a,b):return (a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0])
def padd(a,b,c=(F(1),F(0)),q=0,m=0):
 for (r,k,s),v in b.items():
  key=(r,(k+q)%4,s+m);z=gadd(a.get(key,(0,0)),gmul(c,v))
  if z!=(0,0):a[key]=z
  else:a.pop(key,None)
def pscale(a,c=(F(1),F(0)),q=0,m=0):
 b={};padd(b,a,c,q,m);return b
def caller(C,mutant=None):
 degree=Counter()
 for event in C['events']:
  if event[0]=='J':degree[event[1]]+=1
  elif event[1]=='IDLE_ONE':degree.update(event[3])
 assert degree and max(degree.values())<256 # no packed-exponent carry
 rows=[{(r,0,0):(F(1),F(0))} for r in range(C['roles'])];maxterms=0
 mass=[F(1)]*C['roles'];height=[0]*C['roles'];maxmass=F(1);maxheight=0
 def scale_major(r,q):
  mass[r]*=abs(q);height[r]+=q.denominator.bit_length()-1
 def add_major(r,s,q):
  mass[r]+=abs(q)*mass[s];height[r]=max(height[r],height[s]+q.denominator.bit_length()-1)
 for idx,e in enumerate(C['events']):
  if e[0]=='J':
   mon=1<<(8*(e[1]-1));x,y,u,v=e[2];s,t=e[3][:2];al,be=map(F,e[3][2:4])
   padd(rows[y],rows[x],q=-1);padd(rows[u],rows[v],(F(C['types']['A']['alpha2']),F(0)),q=1)
   add_major(y,x,F(1));add_major(u,v,abs(F(C['types']['A']['alpha2'])))
   for r in (x,y,u,v):rows[r]=pscale(rows[r],m=mon)
   rs=pscale(rows[s]);padd(rs,rows[t],(al,F(0)),q=1)
   rt=pscale(rows[t],(1+al*be,F(0)));padd(rt,rows[s],(be,F(0)),q=-1)
   ms,mt=mass[s],mass[t];hs,ht=height[s],height[t]
   mass[s]=ms+abs(al)*mt;mass[t]=abs(be)*ms+abs(1+al*be)*mt
   height[s]=max(hs,ht+al.denominator.bit_length()-1)
   height[t]=max(hs+be.denominator.bit_length()-1,ht+(1+al*be).denominator.bit_length()-1)
   rows[s]=pscale(rs,m=mon);rows[t]=pscale(rt,m=mon)
  else:
   op=e[1];r=e[2]
   if op=='ADD':
    q=F(e[4])*(2 if idx==mutant else 1);padd(rows[r],rows[e[3]],(q,F(0)));add_major(r,e[3],q)
   elif op=='SCALE':q=F(e[3]);rows[r]=pscale(rows[r],(q,F(0)));scale_major(r,q)
   elif op=='SWAP':
    s=e[3];rows[r],rows[s]=rows[s],rows[r];mass[r],mass[s]=mass[s],mass[r];height[r],height[s]=height[s],height[r]
   elif op=='QUERY':padd(rows[r],rows[e[3]],q=e[4]);add_major(r,e[3],F(1))
   elif op=='LAMBDA':
    s=e[3];out=pscale(rows[r],(F(1,2),F(s,2)));padd(out,rows[r],(F(1,2),F(-s,2)),q=2);rows[r]=out
    mass[r]*=2; height[r]+=1 # coefficient l1 on real/imag, no cancellation
   elif op=='IDLE_ONE':rows[r]=pscale(rows[r],m=sum(1<<(8*(s-1)) for s in e[3]))
   else:raise AssertionError(op)
  maxterms=max(maxterms,sum(map(len,rows)));maxmass=max(maxmass,*mass);maxheight=max(maxheight,*height)
  if idx%500==0:print('caller',idx,'terms',sum(map(len,rows)),flush=True)
 bad=[]
 for ty,d in C['types'].items():
  for i,dg in enumerate(d['diagonal']):
   r=d['offset']+i;mon=sum(int(v)<<(8*k) for k,v in enumerate(dg[2:]));ex={(r,dg[0]%4,mon):(F(1),F(0))}
   if rows[r]!=ex:bad.append(r)
 return dict(bad_outputs=bad,max_terms=maxterms,caller_mass_bound=str(maxmass),caller_mass_ceiling_bits=math.ceil(math.log2(maxmass)),caller_denominator_height_bound=maxheight)

def invoices(W,C,N):
 assert C['types']['A']['ports']==W['hosted']['Dports']
 assert sorted(C['types']['B']['ports'])==[i for i in range(104) if i not in set(W['hosted']['Dports'])]
 T=Counter();P=Counter();calls=0
 for e in C['events']:
  if e[0]=='J':calls+=1;T.update(N['helpers']);P.update(N['paid'])
  else:
   ports=len(C['types'][e[0]]['ports'])
   if e[1]=='QUERY':P[1]+=ports
   elif e[1]=='IDLE_ONE':P[8*len(e[3])]+=ports
 for d in C['types'].values():
  for dg in d['diagonal']:T[dg[0]%2+8*sum(dg[2:])]+=len(d['ports'])
 assert calls==18
 S=sum(r*(T[r]-P[r]) for r in T.keys()|P.keys())
 with localcontext() as cx:
  cx.prec=65;logs={r:Decimal(r).ln() for r in T.keys()|P.keys()}
  def margin(k,t=T,p=P):return sum(Decimal(t[r]-p[r])*Decimal(r)*(-k*logs[r]).exp() for r in logs)
  lo,hi=Decimal(0),Decimal('.01')
  for _ in range(200):
   mid=(lo+hi)/2
   if margin(mid)>0:lo=mid
   else:hi=mid
  crossing=str((lo+hi)/2)
  Ecount=sum(len(d['ports']) for d in C['types'].values() for dg in d['diagonal'] if not any(dg[2:]));Te=T.copy();Te[1]-=Ecount;lo,hi=Decimal(0),Decimal('.01')
  for _ in range(200):
   mid=(lo+hi)/2
   if margin(mid,Te)>0:lo=mid
   else:hi=mid
  nocredit=str((lo+hi)/2)
 return dict(T=dict(sorted(T.items())),P=dict(sorted(P.items())),S=S,raw_crossing=crossing,empty_root_credits=Ecount,no_E_credit_crossing=nocredit)

def ordinary(W,C,N):
 # Atomic contributions are separately itemized to prevent zero-charge shortcuts.
 calls=18;portsA=len(C['types']['A']['ports']);ports=sum(len(v['ports']) for v in C['types'].values())
 scalar=0;init_clear=0;odd=Counter()
 for e in W['program']:
  if e[0] in ('ADD','COPY','SCALE'):
   q=F(e[2] if e[0]=='SCALE' else e[3]);a=abs(q.numerator);d=q.denominator
   scalar+=4*(a.bit_length()+d.bit_length()+1+(a.bit_count() if e[0]!='SCALE' else 0))
   if d&(d-1):odd[e[0]]+=1
  elif e[0] in ('INIT','CLEAR'):init_clear+=2
 route_items=dict(moves=sum(N['paid'].values()),helper_boundary=2*sum(N['helpers'].values()),first_main_boundary=2*ports,second_main_boundary=2*portsA,first_main_adapter=4*ports,second_main_adapter=4*portsA,owned_lifetime=4*N['lifetimes'])
 routing=1000*sum(route_items.values());rest_items={};lam=0
 def swapcost(axes):return len(set(axes)-set(range(len(axes))))
 for ty,t in C['types'].items():
  ne=sum(e[0] in (ty,'J') for e in C['events']);p=len(t['ports']);nr=t['roles'];env=32*nr*p*ne
  qr=[e for e in C['events'] if e[0]==ty and e[1]=='QUERY'];idle=[e for e in C['events'] if e[0]==ty and e[1]=='IDLE_ONE'];la=sum(e[0]==ty and e[1]=='LAMBDA' for e in C['events']);lam+=la*p
  output=0
  for qp,zero,*mask in t['diagonal']:
   axes=([0] if qp else [])+[a for k,v in enumerate(mask) if v for a in range(9+8*k,17+8*k)]
   output+=p*1000*(2*swapcost(axes)+2*bool(qp)+(qp==-1))
  idleroute=sum(2*p*1000*swapcost([a for k in e[3] for a in range(1+8*k,9+8*k)]) for e in idle)
  queryroute=sum(p*1000*(2+(e[4]==-1)) for e in qr)
  rest_items[ty]=dict(envelope=env,thin=16*p*len(qr),field_boundary=26*nr*p,output_routes=output,idle_routes=idleroute,query_routes=queryroute)
 rest=sum(sum(d.values()) for d in rest_items.values());upper=calls*(scalar+routing)+rest;conversion=calls*len(W['initial'])*104;secondlam=lam*1000
 return dict(scalar_upper=scalar,init_clear_allowance=init_clear,route_items=route_items,routing=routing,caller_items=rest_items,caller_total=rest,raw_upper=upper,per_input_conversion=conversion,lambda_second_charge=secondlam,conservative_total=upper+conversion+secondlam,margin_to_billion=10**9-upper-conversion-secondlam,odd_divisions=dict(odd),lambda_paid_rank1_would_reduce_S_by=lam)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('word');ap.add_argument('--out',required=True);ap.add_argument('--caller',action='store_true');ap.add_argument('--mutant',type=int);ap.add_argument('--caller-path',required=True);a=ap.parse_args()
 W=load(a.word);C=load(a.caller_path);start=time.time();N=native(W,a.mutant)
 result=dict(schema='independent-reverse-circuit-audit/1',word=str(Path(a.word).resolve()),word_sha256=pin(a.word),caller_sha256=pin(a.caller_path),native=N)
 if a.mutant is None:
  result['invoice']=invoices(W,C,N);result['ordinary']=ordinary(W,C,N)
 if a.caller:result['caller']=caller(C)
 result['seconds']=time.time()-start;Path(a.out).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
