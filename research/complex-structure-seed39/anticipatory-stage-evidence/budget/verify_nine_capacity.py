#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact favorable capacity obstruction for PR2339 nine-stage assembly.
Prepared for Tekalign (@tekuuu) with substantial OpenAI Codex assistance.
No current-frontier, supplier admission or new kappa claim.
"""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
import importlib.util,json,gzip,hashlib
HERE=Path(__file__).resolve().parent
PACKAGE=HERE.parent/'vendor/pr2339'
INHERITED=HERE.parents[1]/'face-hoist-evidence/budget/inherited/vendor'
B=Q('0.0016870');M=73;CALLS=666;D=23680
WIDTHS=(4,5,7,8,9)
PARENT=HERE.parent/'parent'
PARENT_PINS={'new/PLAN.json':'bf1abd33c8ba946371cae37e021747343ef6603a31297bcc962197cc23f535e2','new/PROFILE.json':'50fcc0960a47f6d35064d3b55ea6dcb4cebbd305aec215c8034f626718595538'}
DEMAND=(2664,2664,23976,55944,181152)
DUAL=tuple(map(Q,['0.01564724162', '0.03129448326', '0.03332425781', '0.03396187965', '-0.01540137223', '-0.02266563498', '-0.02774160900', '-0.01564724165', '-0.00355287430']))
PINS={'check_ext.py':'769061ef58133b3c018613cd5d51d4c3331c4456311eda6b8ca1b48914290010','words/BORROW-WORD-80base.json.gz':'61290abffd8c8225e0abb3958c1506674e256de688fc4cdf358bbe7c981df493','words/BORROW-WORD-80extra.json.gz':'1dd2d6f2ae5b5a27b5f89fb830203f0cca7a78d0323a7845e85e1e80f8f6d1a5'}
ENGINES={'moment.py':'81cbc864e106418fc7854322746f72180cb8110ff39f74450a3b8d55a82c1482','base_two_moment.py':'aee70c242a2f1d225528fabe2002e1564d1dc884797c07d28a831c7878ee9098'}
def require(x,msg):
 if not x:raise ValueError(msg)
def pin(path,expected):require(hashlib.sha256(path.read_bytes()).hexdigest()==expected,'source pin '+str(path))
def load(path,name):
 s=importlib.util.spec_from_file_location(name,path);mod=importlib.util.module_from_spec(s);s.loader.exec_module(mod);return mod
def iv(lo,hi):
 grid=10**35
 lo=Q((lo*grid).__floor__(),grid);hi=Q((hi*grid).__ceil__(),grid)
 return {'lower':str(lo),'upper':str(hi),'decimal_lower_approx':float(lo),'decimal_upper_approx':float(hi)}
def E(rank,b,engine):
 if hasattr(engine,'logarithm'):
  lo,hi=engine.logarithm(Q(M,rank)); a,z=engine.exponential(b*lo,b*hi)
 else:
  lo,hi=engine.log_bounds(Q(M,rank));a=engine.exp_bounds(b*lo)[0];z=engine.exp_bounds(b*hi)[1]
 return rank*(a-1),rank*(z-1)
def patterns(cap,j=0,p=()):
 if j==len(WIDTHS):yield p;return
 for k in range(cap//WIDTHS[j]+1):yield from patterns(cap-k*WIDTHS[j],j+1,p+(k,))
def check_dual(y,lower):
 count=0;least=None
 for cap in (8,16,32,48,73):
  for p in patterns(cap):
   if cap==73 and not sum(p):continue
   lhs=sum(y[4+i]*p[i] for i in range(5))+(y[(8,16,32,48).index(cap)] if cap!=73 else 0)
   rest=cap-sum(w*n for w,n in zip(WIDTHS,p));gap=lower[rest]-lhs
   require(gap>=0,'infeasible dual')
   least=gap if least is None else min(least,gap);count+=1
 return count,least

def main():
 require(__debug__,'Optimized Python unsupported by inherited exact engines')
 for f,h in PINS.items():pin(PACKAGE/f,h)
 checker=load(PACKAGE/'check_ext.py','p2339_frames');words={}
 for file,h in PARENT_PINS.items():pin(PARENT/file,h)
 plan=json.loads((PARENT/'new/PLAN.json').read_text());oldH={int(k):n for k,n in json.loads((PARENT/'new/PROFILE.json').read_text()).items()}
 require(tuple(plan[k]for k in ['K','L','M','T','live','deficit'])==(4,9,73,74,66304,23680),'parent geometry binding')
 capacities=Counter(v[0]for v in plan['windows'].values())
 require({r:112*n for r,n in capacities.items()}=={8:49728,16:33152,32:33152,48:33152},'actual parent bin stock')
 require(len(plan['provider_calls'])==666,'parent call count')
 require(sum(r*n for r,n in oldH.items())==73*66304-23680,'parent positive-control rank identity')
 for tag in ('base','extra'):
  w=json.loads(gzip.decompress((PACKAGE/f'words/BORROW-WORD-80{tag}.json.gz').read_bytes()));P=checker.parse_borrow(w);f=checker.frame_check(P)
  require(f['mass']==5264 and f['helper_width_sum']==3408 and f['mass']-f['helper_width_sum']==1856,'local rank identity')
  require(dict(f['inventory'])==dict(zip(WIDTHS,(4,4,36,84,272))),'helper inventory')
  require(f['copies']=={8:8},'COPY charge')
  require(len(P['buffers'])==44 and len(P['corr'])==64,'extra operation counts')
  words[tag]={'profile':dict(f['paid']),'inventory':dict(f['inventory']),'mass':f['mass'],'width_sum':f['helper_width_sum'],'buffers':44,'compensation_terms':64}
 require(73*66304-(666*1856+49728*8+33152*(16+32+48))==23680,'geometry rank identity')
 dual_bound=sum(Q(n)*y for n,y in zip((49728,33152,33152,33152)+DEMAND,DUAL))
 engines={};controls=[]
 for file,h in ENGINES.items():
  pin(INHERITED/file,h);engine=load(INHERITED/file,'capacity_'+file[:-3]);cost={0:(Q(0),Q(0))}
  for r in range(1,52):cost[r]=E(r,B,engine)
  # Exact dynamic programming over every positive-rank composition of residual,
  # granting arbitrary many recursive padding children of ranks1..51.
  lower=[Q(0)];upper=[Q(0)]
  for total in range(1,74):
   lower.append(min(lower[total-r]+cost[r][0] for r in range(1,min(51,total)+1)))
   upper.append(min(upper[total-r]+cost[r][1] for r in range(1,min(51,total)+1)))
  count,least=check_dual(DUAL,lower)
  require(count==5927,'complete pattern coverage')
  oldlo=sum(n*cost[r][0]for r,n in oldH.items());oldhi=sum(n*cost[r][1]for r,n in oldH.items())
  require(oldhi<D,'inherited43word profile positive control')
  checks={}
  for tag,w in words.items():
   lo=sum(CALLS*n*cost[r][0] for r,n in w['profile'].items());hi=sum(CALLS*n*cost[r][1] for r,n in w['profile'].items())
   require(lo+dual_bound>D,'strict favorable budget rejection')
   checks[tag]={'local_excess':iv(lo,hi),'local_plus_certified_padding_lower_bound':iv(lo+dual_bound,hi+dual_bound),'rejection_margin':iv(lo+dual_bound-D,hi+dual_bound-D)}
  engines[file]={'parent43_profile_excess_positive_control':iv(oldlo,oldhi),'dual_patterns_checked':count,'minimum_dual_slack':iv(least,least),'providers':checks,'residual_min_cost':{r:iv(lower[r],upper[r]) for r in range(74)}}
  bad=list(DUAL);bad[0]+=1
  try:check_dual(bad,lower)
  except ValueError as e:require(str(e)=='infeasible dual','intended dual control reason')
  else:raise ValueError('forged dual accepted')
  controls.append(file+': increase rank8-bin dual by1 rejected')
  require(E(1,Q(0),engine)==(0,0),'zero exponent control')
  controls.append(file+': zero rate yields zero excess')
 for tag in words:
  a=engines['moment.py']['providers'][tag]['rejection_margin'];z=engines['base_two_moment.py']['providers'][tag]['rejection_margin']
  require(max(Q(a['lower']),Q(z['lower']))<=min(Q(a['upper']),Q(z['upper'])),'independent interval overlap')
 try:pin(PACKAGE/'words/BORROW-WORD-80extra.json.gz','0'*64)
 except ValueError as e:require(str(e).startswith('source pin '),'pin control reason')
 else:raise ValueError('forged source pin accepted')
 controls.append('incorrect word hash rejected')
 result={'status':'PASS_EXACT_NINE_STAGE_CAPACITY_OBSTRUCTION_WITH_FULL_BANKS_NO_NEW_KAPPA','base':'7ee02b7c96d85f22b38d28bd7ed49bb8c1aeb261','seed':39,'source_head':'bf1742aee4d855efb8bbd44a8419eddb33a679e5','comparison_rate':str(B),'comparison_scope':'Primitive-rate threshold b=.0016870 from concurrent PR2360. Rejection extends to reported kappa .001697065994108880 used directly as b or its balanced conversion. No frontier or outer reduction is certified.', 'concurrent_predecessor':{'pr':2360,'head':'16d4ea6c26cd45ebb9301ab90f33a73615627f8d','scope':'PR2360 proves same-stock cap below .0016870 with1163patterns. This adds arbitrary full73banks and all padding partitions, using two independent interval engines; not a novel same-stock result.'},'geometry':{'m':73,'calls':666,'base_live':66304,'deficit':23680,'pending_capacities':{8:49728,16:33152,32:33152,48:33152},'arbitrary_full_banks_capacity':73,'maximum_idle_rank':51},'words':words,'dual':list(map(str,DUAL)),'certified_padding_excess_lower_bound':str(dual_bound),'engines':engines,'controls':controls,'pins':PINS,'parent_pins':PARENT_PINS,'positive_control_scope':'The pinned PR2269 global profile is arithmetically below budget at this rate; this control is not a replay of that full construction.','engine_pins':ENGINES,'scope':'Necessary bound only for these exact local profiles and width inventory with whole-helper capacity hosting in the inherited nine-stage geometry. Fractional bin counts, arbitrary count of full73 banks, arbitrary roles per bin and all padding partitions rank<=51 are allowed. No temporal/family or buffer charge required for rejection. Changes to local word, slot fragmentation, bank geometry or sharing accounting are outside scope.','attribution':'PR2339 Sagar Thakrar local construction and frame checker; PR2226 Cinna Davis borrowing; PR2269 Jeremy Kothe emission/audit; prior seed39 nine-stage geometry and independent retained exact engines. Downstream analysis prepared with substantial OpenAI Codex assistance.'}
 (HERE/'EXACT-NINE-CAPACITY-RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(result['status']);print('padding lower bound',float(dual_bound));print({t:engines['moment.py']['providers'][t]['rejection_margin']['decimal_lower_approx'] for t in words})
if __name__=='__main__':main()
