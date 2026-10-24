#!/usr/bin/env python3
"""Independent exact fixed-dyadic AD census plus exact one-fault trajectories.
No candidate checker import. Conditional on the separately audited moving-chart ABI.
"""
import argparse,collections,gzip,hashlib,json,pathlib
from fractions import Fraction
import numpy as np
GRID=1<<30
PIN='7679daa4ec6a40f56fc7f0202379a6f454310e94945aba4f48beaaaafb838d05'
def check(b,s):
 if not b:raise ValueError(s)
def own(x):return 632 if x[0]=='C' else x[1]
def paid(e):return (e[2],e[-1]) if e[0]=='climb' else ((632,e[-1]) if e[0]=='center' else None)
def dyadic_scale(row,num,den):
 check(abs(num)<(1<<20) and np.all(np.abs(row)<(1<<40)), 'safe integer product')
 v=row*num
 check(np.all(v%den==0), 'fixed dyadic grid exact')
 return v//den
def fp_step(a,e,adj=False):
 if e[0]!='scalar':return
 g=e[1];op=g[0];i=own(g[1])
 if op=='clear':a[i]=0
 elif op=='copy':
  j=own(g[2]);check(i!=j,'self copy');check(np.all(np.abs(a[i])<(1<<40)) and np.all(np.abs(a[j])<(1<<40)), 'safe copy sum')
  if adj:a[j]=a[j]+a[i];a[i]=0
  else:a[i]=a[j].copy()
 elif op=='add':
  j=own(g[2]);check(np.all(np.abs(a[i])<(1<<40)) and np.all(np.abs(a[j])<(1<<40)), 'safe add sum')
  if adj:a[j]=a[j]+dyadic_scale(a[i],g[3],g[4])
  else:a[i]=a[i]+dyadic_scale(a[j],g[3],g[4])
 elif op=='scale':a[i]=dyadic_scale(a[i],g[2],g[3])
 else:raise ValueError(op)
 check(np.all(np.abs(a[i])<(1<<40)), 'safe updated row')
def exact_fault(program,upper,site,port,eta):
 a=[Fraction(0) for _ in range(633)];a[port]=1
 if upper:a[112+port]=1
 for k,e in enumerate(program):
  if k==site:a[paid(e)[0]]*=1+eta
  if e[0]!='scalar':continue
  g=e[1];op=g[0];i=own(g[1])
  if op=='clear':a[i]=Fraction(0)
  elif op=='copy':a[i]=a[own(g[2])]
  elif op=='add':a[i]+=Fraction(g[3],g[4])*a[own(g[2])]
  elif op=='scale':a[i]*=Fraction(g[2],g[3])
  else:raise ValueError(op)
 return [a[i] if upper else a[i]-a[112+i] for i in range(112)]+a[224:632]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--source',type=pathlib.Path,required=True);ap.add_argument('--receipt',type=pathlib.Path,required=True);ap.add_argument('--out',type=pathlib.Path,required=True);args=ap.parse_args()
 raw=args.source.read_bytes();check(hashlib.sha256(raw).hexdigest()==PIN,'source pin');d=json.loads(gzip.decompress(raw));rr=args.receipt.read_bytes();payload=gzip.decompress(rr) if rr.startswith(b'\x1f\x8b') else rr;r=json.loads(payload);out=[];total=collections.Counter()
 for call in r['calls']:
  upper=call['call']=='upper';program=d['programs'][call['source_orientation']];F=np.zeros((633,112),dtype=np.int64);F[:112]=np.eye(112,dtype=np.int64)*GRID
  if upper:F[112:224]=F[:112]
  pre={}
  for k,e in enumerate(program):
   z=paid(e)
   if z:pre[k]=F[z[0]].copy()
   fp_step(F,e)
  check(np.all(F[224:]==0),'no helper leak at exact delta input')
  check(np.array_equal(F[:112],np.zeros((112,112),dtype=np.int64) if upper else np.eye(112,dtype=np.int64)*GRID),'exact X endpoint')
  check(np.array_equal(F[112:224],np.eye(112,dtype=np.int64)*GRID),'exact Y endpoint')
  A=np.zeros((633,520),dtype=np.int64);A[:112,:112]=np.eye(112,dtype=np.int64)*GRID
  if not upper:A[112:224,:112]=-np.eye(112,dtype=np.int64)*GRID
  A[224:632,112:]=np.eye(408,dtype=np.int64)*GRID;suf={};clears=[]
  for k in reversed(range(len(program))):
   e=program[k];z=paid(e)
   if z:suf[k]=A[z[0]].copy()
   fp_step(A,e,True)
   if e[0]=='scalar' and e[1][0]=='clear':check(np.all(A[own(e[1][1])]==0),'clear adjoint');clears.append(k)
  check(np.all((A[:112]+A[112:224])==0) if upper else np.all(A[:112]==0),'zero unscaled baseline')
  flagged=collections.Counter();split=collections.Counter();main_split=collections.Counter();minimum=None;chosen={};count=0
  for w in call['sites']:
   k=w['event'];z=paid(program[k]);check(z==(w['owner'],w['rank']),'paid identity')
   active=np.any(pre[k]) and np.any(suf[k]);check(bool(active)==w['epsilon_minus_one_witness'],'classification')
   check(np.count_nonzero(pre[k])==w['nonzero_inputs'],'prefix support');check(np.count_nonzero(suf[k])==w['nonzero_observations'],'suffix support')
   if not active:continue
   count+=1;flagged[w['rank']]+=1
   for j in {1:[1],2:[2],3:[3],4:[3,1],5:[3,2],8:[3,3,2]}[w['rank']]:
    split[j]+=1
    if np.any(suf[k][:112]):main_split[j]+=1
   value=abs(Fraction(w['pole_coefficient_ignoring_common_sign']));minimum=value if minimum is None else min(minimum,value)
   i,c=w['prefix_witness'];j,b=w['suffix_witness'];check(Fraction(int(pre[k][i]),GRID)==Fraction(c),'prefix coefficient');check(Fraction(int(suf[k][j]),GRID)==Fraction(b),'suffix coefficient');check(Fraction(int(pre[k][i])*int(suf[k][j]),GRID*GRID)==Fraction(w['pole_coefficient_ignoring_common_sign']),'pole coefficient');check(bool(np.any(suf[k][:112]))==w['main_visible'],'main visibility');check(bool(np.any(suf[k][112:]))==w['helper_visible'],'helper visibility')
   chosen.setdefault(('rank',w['rank']),w)
   if w['kind']=='center':chosen[('center',k)]=w
   if j>=112:chosen.setdefault(('helper',w['rank']),w)
  check(dict(flagged)=={int(k):v for k,v in call['flagged_profile'].items()},'flagged counts');check(dict(split)=={int(k):v for k,v in call['flagged_split_profile'].items()},'split counts');total.update(split)
  exact=[]
  for key,w in chosen.items():
   port=w['prefix_witness'][0];j=w['suffix_witness'][0];eta=Fraction(1,8);values=exact_fault(program,upper,w['event'],port,eta);check(values[j]==eta*Fraction(w['pole_coefficient_ignoring_common_sign']),'exact injected trajectory')
   exact.append({'event':w['event'],'rank':w['rank'],'kind':w['kind'],'input_port':port,'observation':j,'exact_difference':str(values[j])})
  out.append({'call':call['call'],'paid_sites':len(pre),'exact_flagged_sites':count,'flagged_profile':dict(flagged),'split_profile':dict(split),'main_visible_split_profile':dict(main_split),'minimum_absolute_pole_coefficient':str(minimum),'owned_clears':len(clears),'exact_fault_trajectories':exact})
 main_rank1=sum(c['main_visible_split_profile'][1] for c in out);check(main_rank1==3608,'main-only sufficient surcharge')
 targets={4:56,7:14,8:94,9:652,17:224};basepaid={1:4656,2:920,3:1386};tmass=sum(k*v for k,v in targets.items());pmass=sum(k*v for k,v in basepaid.items())+main_rank1;check((tmass,pmass)==(10750,14262),'strict-separation mass theorem')
 result={'status':'PASS_INDEPENDENT_EXACT_SENSITIVITY_RECOUNT','dyadic_grid':GRID,'source_sha256':PIN,'candidate_receipt_sha256':hashlib.sha256(rr).hexdigest(),'candidate_receipt_payload_sha256':hashlib.sha256(payload).hexdigest(),'checker_sha256':hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),'numpy_version':np.__version__,'calls':out,'flagged_split_profile':dict(total),'conditional_tariff_mass_certificate':{'target_mass':tmass,'base_paid_mass':pmass-main_rank1,'main_rank1_surcharge':main_rank1,'penalized_paid_mass':pmass,'min_target_rank':min(targets),'max_paid_rank':max(basepaid),'for_0_le_t_le_1':'T(t)/P_penalized(t) <= (4/3)^(t-1) * 10750/14262 < 1'},'scope':'All scalar-chart site classifications and advertised coefficients crosschecked exactly on a fixed dyadic integer grid with divisibility and overflow guards, without importing candidate code. Separate exact Fraction direct fault trajectories verify selected rank/center/helper witnesses. All-width physical moving-chart and outer boundary justification reviewed separately.'}
 args.out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='calls'}));print('Exact trajectories',sum(len(x['exact_fault_trajectories']) for x in out))
if __name__=='__main__':main()
