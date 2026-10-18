# SPDX-License-Identifier: Apache-2.0
"""Exact fixed-inventory fractional primal/dual certificate near its moment root.
All transcendental bounds use authenticated stdlib directed integer series.
"""
import argparse,collections,functools,hashlib,itertools,json,os,types
from pathlib import Path
from fractions import Fraction as Q

def need(p,m):
 if not p:raise AssertionError(m)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def add(*ds):
 z={}
 for d in ds:
  for r,c in d.items():z[r]=z.get(r,Q(0))+c
 return {r:c for r,c in z.items()if c}
def mul(a,d):return {r:a*c for r,c in d.items()if a*c}
def f(r):return {r:Q(1)}if r else{}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--package',type=Path,required=True);ap.add_argument('--candidate-profile',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();need(not a.out.exists(),'fresh output');here=Path(__file__).resolve().parent
 cp=here/'moment_core.py';body=cp.read_bytes();need(hashlib.sha256(body).hexdigest()=='22290074f138fa9b902e5f6f6e8a0ec366d6f812992adb6df9b617ce952fb852','executed arithmetic source bytes');m=types.ModuleType('directed');m.__file__=str(cp);exec(compile(body,str(cp),'exec'),m.__dict__);m.BITS=512;m.S=1<<512;m.LOG_TERMS=220;m.EXP_TERMS=114;m.log_int=functools.lru_cache(None)(m.log_int)
 paths={'registry':a.package/'PROVIDERS.json','baseline_profile':a.package/'PROFILE.json','baseline_claim':a.package/'CLAIM.json','candidate_profile':a.candidate_profile};pins={k:sha(p)for k,p in paths.items()};reg=json.loads(paths['registry'].read_bytes());inventory=collections.Counter(reg['extra']['widths']);need(inventory=={4:26,5:2,7:62,8:84,9:234},'current actual inventory');native={int(r):n for r,n in reg['extra']['actual_paid_profile'].items()};need(all(z['widths']==reg['extra']['widths']and z['actual_paid_profile']==reg['extra']['actual_paid_profile']for z in reg.values()),'fixed common native price/inventory')
 support=[(8,[0,0,0,1,0],Q(672)),(16,[0,0,1,0,1],Q(448)),(32,[0,0,0,0,3],Q(120)),(32,[0,0,0,4,0],Q(21)),(32,[0,0,2,0,2],Q(55)),(32,[0,1,0,0,3],Q(18)),(32,[1,0,0,0,3],Q(234)),(48,[0,0,0,0,0],Q(1808,5)),(48,[0,0,0,0,5],Q(432,5))]
 widths=[4,5,7,8,9];caps={8:672,16:448,32:448,48:448};capcheck=collections.Counter();widthcheck=collections.Counter();idle=collections.Counter();primal=[]
 for c,u,n in support:
  rem=c-sum(w*z for w,z in zip(widths,u));need(rem>=0 and n>=0,'primal nonnegative bins');capcheck[c]+=n
  for w,z in zip(widths,u):widthcheck[w]+=z*n
  if rem:idle[rem]+=n
  primal.append(dict(capacity=c,width_counts=u,bins=str(n),remainder=rem))
 need(capcheck==caps and all(widthcheck[w]==9*inventory[w]for w in widths),'all exact primal inventory constraints')
 H={r:9*Q(n)for r,n in native.items()}
 for r,n in idle.items():H[r]=H.get(r,0)+n
 C={int(r):int(n)for r,n in json.loads(paths['candidate_profile'].read_bytes()).items()};need(all(Q(C.get(r,0),185)==H.get(r,0)for r in set(C)|set(H)),'actual T185 profile attains exact fractional shape')
 # Find a directed 24-decimal bracket for the common optimum's moment root.
 grid=10**24;alpha=Q(json.loads(paths['baseline_claim'].read_bytes())['kappa']);lo=alpha.numerator*grid//alpha.denominator;hi=lo+10**17
 need(m.moment(H,896,73,Q(lo,grid))[1]<0 and m.moment(H,896,73,Q(hi,grid))[0]>0,'initial root bracket')
 while hi-lo>1:
  mid=(lo+hi)//2;l,u,_=m.moment(H,896,73,Q(mid,grid))
  if u<0:lo=mid
  elif l>0:hi=mid
  else:raise AssertionError('directed series resolution insufficient')
 al,au=Q(lo,grid),Q(hi,grid)
 # Symbolic dual prices for objective H_remainder, with H_r = r^p.
 mu9=mul(Q(1,5),add(f(3),mul(-1,f(48))));c32=add(f(5),mul(-3,mu9))
 capprice={8:mul(Q(1,4),c32),16:mul(Q(1,2),c32),32:c32,48:f(48)}
 mu={9:mu9,8:mul(Q(-1,4),c32),7:add(mul(Q(-1,2),c32),mul(-1,mu9)),5:mul(-1,f(5)),4:add(f(1),mul(-1,f(5)))}
 dualobjective=add(*(mul(n,capprice[c])for c,n in caps.items()),*(mul(9*inventory[w],mu[w])for w in widths));need(dualobjective==dict(idle),'symbolic primal/dual objective equality')
 bounds={r:(m.power(r,au)[0],m.power(r,al)[1])for r in range(1,49)}
 def evaluate(d):
  l=u=Q(0)
  for r,c in d.items():
   a,b=bounds[r]
   if c>=0:l+=c*a;u+=c*b
   else:l+=c*b;u+=c*a
  return l,u
 patterns=[];minimum=None;zeros=0
 for c in caps:
  for z in itertools.product(*(range(c//w+1)for w in widths)):
   used=sum(w*n for w,n in zip(widths,z))
   if used>c:continue
   rem=c-used;slack=add(f(rem),mul(-1,capprice[c]),*(mul(-n,mu[w])for w,n in zip(widths,z)))
   if not slack:zeros+=1;l=u=Q(0)
   else:
    l,u=evaluate(slack);need(l>0,'dual-infeasible packing pattern');minimum=l if minimum is None else min(minimum,l)
   patterns.append(dict(capacity=c,width_counts=z,remainder=rem,symbolic_slack={r:str(v)for r,v in slack.items()},scaled_interval=[str(l),str(u)]))
 need(len(patterns)==1163,'exhaustive actual packing patterns')
 # A forged dual price must be detected by its tight [8] pattern.
 bad=add(capprice[8],f(1));badslack=add(mul(-1,bad),mul(-1,mu[8]));need(evaluate(badslack)[1]<0,'forged dual control')
 for k,p in paths.items():need(sha(p)==pins[k],'input changed '+k)
 result=dict(status='PASS_EXACT_CURRENT_INVENTORY_PRIMAL_DUAL_AND_ACTUAL_ATTAINMENT',input_sha256=pins,profile_at_T185=C,per_replica_profile={r:str(n)for r,n in H.items()},primal_support=primal,dual_capacity_prices={c:{r:str(v)for r,v in d.items()}for c,d in capprice.items()},dual_helper_prices={w:{r:str(v)for r,v in d.items()}for w,d in mu.items()},moment_root_bracket=[str(al),str(au)],symbolic_objective_equals_primal=True,pattern_count=len(patterns),symbolically_tight_patterns=zeros,minimum_nontight_slack_scaled=str(minimum),scale='2^512',negative_control='forged_dual_capacity_price_rejected',scope='Actual T185 profile attains the complete fixed-capacity/fixed-native-inventory fractional packing optimum throughout the certified moment-root interval. The certificate does not cover changed native words, chronology outside the literal owner audit, alternate controllers or global optimality across all suppliers.')
 # Preserve every individual dual inequality in a separate finite certificate.
 a.out.mkdir();
 for name,obj in [('RESULT.json',result),('PATTERNS.json',patterns)]:
  p=a.out/name;lock=p.with_name(p.name+'.lock');fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY);os.close(fd)
  try:p.write_text(json.dumps(obj,sort_keys=True,indent=2)+'\n',encoding='utf8',newline='\n')
  finally:lock.unlink()
 print(json.dumps(result,sort_keys=True,indent=2))
if __name__=='__main__':main()
