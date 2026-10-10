#!/usr/bin/env python3
"""Exact fixed-prime price of the reordered w3 word and positive finite-level cutoff checks."""
import sys
if not __debug__:raise SystemExit('Assertions required')
sys.dont_write_bytecode=True
sys.set_int_max_str_digits(0)
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
import argparse,hashlib,json,struct
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'supplied/pricing'))
import fixed_prime_math as R

def run(candidate,bank_path,output,complex_path):
 candidate=Path(candidate);bank=json.loads(Path(bank_path).read_text());st=json.loads((candidate/'249-states.json').read_text());fs=json.loads((candidate/'frames.json').read_text())['frames']
 H=Counter();adds=0;units=0;copies=0
 raw=(candidate/'COHORT249-RECORDS.bin').read_bytes()
 assert hashlib.sha256(raw).hexdigest()==st['record_sha256']=='a972abfe4fcd7f8b245b06a3af7a2131a1f1635ea6076ecdcce870cce19d2526'
 for op,a,b,c,f,z in struct.iter_unpack('<6i',raw):
  if op==0 and f:H[f]+=1
  elif op==2:H[z]+=1;copies+=1
  elif op==1:adds+=1;units+=abs(c)
 assert copies==24 and adds==897241 and sum(r*n for r,n in H.items())==397619
 residual=sum(fs[str(st['final'][str(i)])]['dim']-fs[str(st['initial'][str(i)])]['dim'] for i in range(3520,20107))
 assert residual==316131
 hist={r:40*n for r,n in H.items()}
 for r in (4,23,46,50):hist[r]=hist.get(r,0)+28160
 stock=bank['normalized_stock'];assert stock==161697 and bank['literal_stock']==5*stock and bank['banks_per_stage']==105377
 assert Q(4*1760*40)+Q(5*40*residual,120)==5*stock
 calls=sum(hist.values());mass=sum(r*n for r,n in hist.items());assert calls==3709480 and mass==19368440 and 120*stock-mass==35200
 cost=R.load('w3_moment',ROOT/'vendor/pr249/moment.py');other=R.load('w3_other',ROOT/'vendor/pr249/base_two_moment.py');outer=R.load('w3_outer',ROOT/'vendor/pr249/outer.py')
 q=(1<<127)-1;res=4
 for _ in range(125):res=(res*res-2)%q
 assert res==0 and q==R.PRIME and R.RHO==Q(3456000,q)
 coarse,nxt,first,first_next,second,second_next=R.certify_coarse(hist,120,stock,calls,cost,other)
 cap=R.grid_kappa(coarse);chain=[R.INITIAL_LEAF];gaps=[]
 for level in range(1,21):
  old=chain[-1];new=(1-coarse)*coarse+coarse*old
  row={'atom':coarse-new,'borrowing':1-new-coarse,'remainder':1-new-coarse*(1-old),'stock':1-coarse}
  assert old<new<coarse and min(row.values())>0
  chain.append(new);gaps.append(row)
  if R.grid_kappa(new)==cap:break
 else:raise AssertionError('No finite cap')
 supplier=json.loads(Path(complex_path).read_text());assert supplier['status']=='PASS_FRESH_PR304_COMPLEX_SUPPLIER'
 complex_saving=Q(supplier['priced_complex_saving']);assert complex_saving==Q(7635,10**7)<=Q(supplier['tensor_saving']);bit_cap=cap
 # As in the retained kappa_w.py rule, the assembled leaf is
 # capped strictly below (1-beta)*complex, and the grid kappa is the smaller of the bit cap and that leaf's grid point.
 leaf=min(chain[-1],(1-R.BETA)*complex_saving-Q(1,10**30));complex_binds=leaf<chain[-1];cap=min(bit_cap,R.grid_kappa(leaf))
 assembly=outer.assembly(leaf,complex_saving,R.bridge_template(),cap,eta=R.ETA,beta=R.BETA)
 assert len(assembly['strict_constraints'])==47 and min(assembly['strict_constraints'].values())>0 and min(assembly['margins'].values())>cap
 try:outer.assembly(leaf,complex_saving,R.bridge_template(),cap+Q(1,R.GRID),eta=R.ETA,beta=R.BETA)
 except AssertionError:pass
 else:raise AssertionError('Adjacent grid point admitted')
 assert not complex_binds and bit_cap==Q(151024082262820774685631,200000000000000000000000000)
 assert cap==Q(151024082262820774685631,200000000000000000000000000) and level==9
 result={'status':'PASS_EXACT_W3_PRICE_TWO_ENGINES_47_CONSTRAINTS','source_word_sha256':st['record_sha256'],'complex_saving':complex_saving,'complex_supplier':supplier,'cohort_candidate':{'stock':stock,'calls':calls,'rank_mass':mass,'deficit':35200,'histogram':hist,'coarse':coarse,'moment_upper':first[1],'kappa':cap},'local_histogram':dict(H),'prime':q,'prime_lucas_lehmer_steps':125,'prime_lucas_lehmer_residue':res,'rare_density':R.RHO,'full_fallback_retained':True,'coarse_bracket':[coarse,nxt],'first_interval':first,'first_next':first_next,'second_interval':second,'second_next':second_next,'ordinary_chain':chain,'ordinary_gaps':gaps,'assembly':assembly,'kappa':cap,'bit_grid_cap':bit_cap,'complex_binds':complex_binds,'assembled_leaf':leaf,'adjacent_rejected':True,'scope':'Exact arithmetic; source, geometry, bank and finite invoice admission required separately.'}
 Path(output).write_text(json.dumps(R.serial(result),sort_keys=True,indent=2)+'\n');print('PASS exact price',cap,float(cap),flush=True)
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('candidate',type=Path);ap.add_argument('--bank',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--complex',type=Path,required=True);a=ap.parse_args();run(a.candidate,a.bank,a.output,a.complex)
