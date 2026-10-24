"""Exact compiler-side admission and terminal-completion tests; stdlib only."""
from fractions import Fraction as F
from functools import lru_cache
from pathlib import Path
import argparse,json


def need(ok,msg):
 if not ok:raise ValueError(msg)


def native_parameters(provider,target):
 provider,target=F(provider),F(target);c=F(3,32)
 need(0<target<min(provider,c),'target must be strictly below actual complex provider and caller cap')
 q=(target+min(provider,c))/2
 delta=min(F(1,100),(q-target)/(4*(q+1)),(c-q)/16)
 eps,beta=1-delta,1-3*delta;spare=delta/10;layout=delta/100
 xi=eps*(1+q)-c+layout;stop=(provider-q)/(2*provider)
 rows={'main_transform':eps*q,'standalone_routing':F(1),'fused_gaussian':1-eps+q*beta,'standalone_addressing':F(1),'group_scans':1-eps+beta,'boundary_algebra':c+xi-eps,'sparse_visits':F(1,2)+xi-eps,'record_products':eps,'core_face_recovery':79-eps-beta}
 guards={'provider_stop':provider*(1-stop)-q,'positive_stop':stop,'stop_below_one':1-stop,'positive_beta':beta,'beta_below_epsilon':eps-beta,'epsilon_below_one':1-eps,'layout_above_half':xi-F(1,2),'layout_below_epsilon':eps-xi,'global_gamma':1-eps-spare,'key_sublinear':1-(beta+1-eps),'membership':1-beta-2*(1-eps),'chirp':1-(beta+2*xi-2+spare)}
 for k,v in guards.items():need(v>0,'guard '+k)
 for k,v in rows.items():need(v>target,'row '+k)
 return {'provider':str(provider),'target':str(target),'q':str(q),'epsilon':str(eps),'beta':str(beta),'xi':str(xi),'delta':str(delta),'stop':str(stop),'nine_savings':{k:str(v)for k,v in rows.items()},'all_guards':{k:str(v)for k,v in guards.items()},'minimum_excess':str(min(v-target for v in rows.values()))}


@lru_cache(None)
def exact_power_bounds(n,b,bits=80):
 # Enclose n^((b-1)/b) using integer arithmetic, not floating powers/logs.
 target=pow(n,b-1) << (bits*b);lo=0;hi=(n<<bits)+1
 while hi-lo>1:
  m=(lo+hi)//2
  if pow(m,b)<=target:lo=m
  else:hi=m
 upper=lo if pow(lo,b)==target else lo+1
 return lo,upper


def elision_budget(r,s,b):
 # q=1/b, theta=1-q. Prove the quantitative moment gain from exact enclosures.
 lr,ur=exact_power_bounds(r,b);ls,us=exact_power_bounds(s,b)
 lsum,usum=exact_power_bounds(r+s,b);lm,um=exact_power_bounds(min(r,s),b)
 gap_lower=lr+ls-usum
 need(b*gap_lower>=um,'quantitative concavity budget')
 return gap_lower,um


def delete_terminal_fixture(paid,targets,r,s,*,terminal,canonical,owner_preserved,new_paid_adapters):
 need(terminal and canonical and owner_preserved,'physical terminal/endpoint/owner witness missing')
 need(not new_paid_adapters,'fixture admits only explicitly zero new paid adapters')
 need(paid.get(s,0)>0 and targets.get(r+s,0)>0,'missing billed completion/target')
 p,t=paid.copy(),targets.copy();p[s]-=1;t[r+s]-=1;t[r]=t.get(r,0)+1
 return {k:v for k,v in p.items()if v},{k:v for k,v in t.items()if v}


def run():
 count=0
 for provider in [F(i,320)for i in range(1,31)]:
  for j in range(1,20):native_parameters(provider,min(provider,F(3,32))*F(j,20));count+=1
 current=F(1057621533,350000000000);old=F(30217758,10**10)
 bound=native_parameters(current,old)
 rejects=0
 for p,t in [(current,current),(current,F(34597,10**7)),(F(1,4),F(3,32)),(0,F(1,100))]:
  try:native_parameters(p,t)
  except ValueError:rejects+=1
 need(rejects==4,'native model controls')
 concavity=0
 for b in (2,350):
  for r in range(1,10):
   for s in range(1,10):elision_budget(r,s,b);concavity+=1
 p,t=delete_terminal_fixture({1:5,2:3,4:1},{4:2,9:1},8,1,terminal=True,canonical=True,owner_preserved=True,new_paid_adapters=[])
 need(p=={1:4,2:3,4:1}and t=={4:2,8:1},'productive partial-target accounting')
 physical_rejects=0
 for flags in [(False,True,True,[]),(True,False,True,[]),(True,True,False,[]),(True,True,True,[1])]:
  try:delete_terminal_fixture({1:1},{9:1},8,1,terminal=flags[0],canonical=flags[1],owner_preserved=flags[2],new_paid_adapters=flags[3])
  except ValueError:physical_rejects+=1
 need(physical_rejects==4,'unsupported completion deletion accepted')
 return {'status':'PASS_NATIVE_COMPILER_ADMISSION','rational_native_parameter_cases':count,'current_source_native_receipt':bound,'native_rejecting_controls':rejects,'exact_concavity_cases':concavity,'power_interval_bits':80,'completion_fixture_new_paid':{str(k):v for k,v in p.items()},'completion_fixture_new_targets':{str(k):v for k,v in t.items()},'physical_contract_rejections':physical_rejects,'actual_new_complex_elision_exhibited':False,'new_kappa':None}


def main():
 p=argparse.ArgumentParser();p.add_argument('--provider');p.add_argument('--target');p.add_argument('--expected',type=Path)
 a=p.parse_args()
 if a.provider or a.target:
  need(bool(a.provider and a.target),'provider and target required together')
  out={'status':'PASS_CONDITIONAL_NATIVE_ROWS','parameters':native_parameters(a.provider,a.target),'provider_proof_scope':'Input exponent must be separately established by an actual source-bound provider; this command certifies only caller parameters.'}
 else:
  out=run()
  if a.expected:need(out==json.loads(a.expected.read_text(encoding='utf8')),'expected receipt mismatch')
 print(json.dumps(out,sort_keys=True))

if __name__=='__main__':main()
