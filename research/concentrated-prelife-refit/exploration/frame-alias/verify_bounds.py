"""Exact recorded-profile signs and five-profile fractional packing exclusions.
No optimizer is used in this certificate check; all supplied dual inequalities are checked.
"""
if not __debug__:raise RuntimeError('Assertions are required; run without -O')
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
import json,gzip,hashlib,importlib.util,argparse
HERE=Path(__file__).resolve().parent
read=lambda p:json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
sp=importlib.util.spec_from_file_location('own_rational_bounds',HERE/'independent.py');M=importlib.util.module_from_spec(sp);sp.loader.exec_module(M)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--work',type=Path,required=True);a=ap.parse_args();assert not a.work.exists()and not a.work.resolve().is_relative_to(HERE);a.work.mkdir(parents=True)
 pins=read(HERE/'SOURCE-PINS.json')['sha256'];assert all(hashlib.sha256((HERE/n).read_bytes()).hexdigest()==h for n,h in pins.items());cp=HERE/'independent-inputs';manifest=read(cp/'MANIFEST.json');assert all(hashlib.sha256((cp/n).read_bytes()).hexdigest()==h for n,h in manifest.items());claim=read(HERE/'PR2733-CLAIM.json');point=Q(claim['kappa']);old={int(k):v for k,v in claim['local_profile'].items()};records=[json.loads(s)for s in(HERE/'receipts/FRAME-PROFILES.jsonl').read_text().splitlines()];assert len(records)==914;signs=Counter();wins=[]
 for rec in records:
  profile={int(k):v for k,v in rec['profile'].items()};delta={k:profile.get(k,0)-old.get(k,0)for k in set(profile)|set(old)};assert{k:v for k,v in delta.items()if v}=={int(k):v for k,v in rec['delta'].items()};assert sum(k*v for k,v in delta.items())==0
  if not any(delta.values()):signs['same_profile']+=1;continue
  lo=hi=Q(0)
  for k,v in delta.items():
   if not v:continue
   l,u=M.cost(k,point);lo+=v*(l if v>0 else u);hi+=v*(u if v>0 else l)
  if hi<0:signs['strictly_cheaper']+=1;wins.append([rec['time'],rec['op']])
  else:assert lo>0;signs['strictly_worse']+=1
 assert wins==[[12235,'lower']]
 d=read(HERE/'receipts/ALIAS-RELAXED-LP.json');assert Q(d['comparison_point'])==point;B=Counter()
 for c in read(cp/'GLOBAL-TEMPLATE.json.gz')['idle_children']:B[c['rank']]+=2*c['replicas']
 assert dict(B)=={int(k):v for k,v in d['bin_multiset'].items()};W=[4,5,7,8,9];N=[666*d['new_percall_width_counts'][str(w)]for w in W];pi=list(map(Q,d['pi']));y={int(k):Q(v)for k,v in d['y'].items()};den=1<<256;down=lambda q:Q(q.numerator*den//q.denominator,den);phi={0:Q(0)}
 for r in range(1,49):phi[r]=down(M.cost(r,point)[0]/66304)
 def pats(c,i=0):
  if i==5:yield ();return
  for n in range(c//W[i]+1):
   for rest in pats(c-n*W[i],i+1):yield(n,)+rest
 count=0
 for c in B:
  for p in pats(c):
   idle=c-sum(w*n for w,n in zip(W,p));assert y[c]+sum(n*q for n,q in zip(p,pi))<=phi[idle];count+=1
 assert count==1163;idle_lb=sum(B[c]*y[c]for c in B)+sum(n*q for n,q in zip(N,pi));margins={}
 for p in d['profiles']:
  paid=sum(666*n*M.cost(int(k),point)[0]/66304 for k,n in p['profile'].items());total=down(idle_lb+paid);assert total==Q(p['native_moment_lower'])and total>1;margins[p['follower']]=str(total-1)
 result={'status':'PASS_EXACT_RECORDED_INVOICE_SIGNS_AND_ALIAS_DUAL_EXCLUSIONS','frame_records':914,'frame_profile_signs':dict(signs),'unique_improving_closure':wins,'fractional_patterns_checked':count,'five_alias_positive_moment_margins':margins,'scope':'Signs for the recorded finite invoices and packing exclusions for exactly five emitted414-helper local profiles. Source-bound census replay checks those invoice calculations separately. No universal frame/alias optimum or supplier theorem.'};(a.work/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
