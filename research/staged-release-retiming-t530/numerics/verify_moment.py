#!/usr/bin/env python3
"""Exact cost certification for the two commuting-release changes.
No global supplier/physical controller admission is inferred from arithmetic.
"""
import argparse,gzip,hashlib,importlib.util,json,sys
from fractions import Fraction as Q
from pathlib import Path

def need(x,m):
 if not x:raise ValueError(m)
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def load(name,p):
 sp=importlib.util.spec_from_file_location(name,p);x=importlib.util.module_from_spec(sp);sp.loader.exec_module(x);return x
def dec(x):
 from decimal import Decimal,localcontext
 with localcontext() as c:
  c.prec=80;return str(Decimal(x.numerator)/Decimal(x.denominator))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--t530',type=Path,required=True);ap.add_argument('--words',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
 price=load('exactprice',a.t530/'price.py')
 ind=load('independent_price',a.repo/'research/pending-claims-independent-pricing/arith.py')
 exp=read(a.t530/'EXPECTED.json');N=exp['replicas']*9;W=exp['replicas']*896
 need(N==4770 and W==474880,'actual T530 normalization')
 old={int(k):v for k,v in exp['profile'].items()}
 delta=None;pins={}
 for tag in ('base','extra'):
  s=a.t530/f'supplier3605/STAGED644-660-{tag}.json.gz';t=a.words/f'RETIMED644-660-{tag}.json.gz'
  before,after=read(s),read(t);pins[str(s)]=hashlib.sha256(s.read_bytes()).hexdigest();pins[str(t)]=hashlib.sha256(t.read_bytes()).hexdigest()
  for key in ('start_extra','helper_final','removed','warps','center_frames','cut','restore','A'):
   need(before.get(key)==after.get(key),'preserved '+key)
  x={int(k):v for k,v in before['report']['local_profile'].items()};y={int(k):v for k,v in after['report']['local_profile'].items()}
  d={r:y.get(r,0)-x.get(r,0) for r in x.keys()|y.keys()};d={r:n for r,n in d.items() if n}
  need(d=={1:-2,2:-2,3:2},'exact per-call profile delta')
  need(before['report']['width_inventory']==after['report']['width_inventory'],'width inventory')
  if delta is None:delta=d
  else:need(delta==d,'providers share delta')
 profile={r:old.get(r,0)+N*delta.get(r,0) for r in old.keys()|delta.keys()}
 need(sum(r*n for r,n in old.items())==sum(r*n for r,n in profile.items()),'rank mass')
 need(73*W-sum(r*n for r,n in profile.items())==W-64*N,'coverage law')
 lo=Q('0.001730394391813963415120');hi=lo+Q(1,10**24)
 signed={**profile,73:-W}
 l,h=price.interval(signed,lo),price.interval(signed,hi)
 need(l[1]<0<h[0],'first exact root bracket')
 il=ind.moment(profile,73,W,lo);ih=ind.moment(profile,73,W,hi)
 need(il.hi<1<ih.lo,'second independent exact root bracket')
 oldlo=Q(exp['root_interval'][0]);oldhi=Q(exp['root_interval'][1]);oldsign={**old,73:-W}
 need(price.interval(oldsign,oldlo)[1]<0<price.interval(oldsign,oldhi)[0],'source baseline')
 need(price.interval({r:N*n for r,n in delta.items()},oldhi)[1]<0,'strict improvement')
 modern=lo-Q(1,10**46)-Q(1,10**70)
 out=dict(status='PASS_TWO_ENGINE_EXACT_MOMENT',replicas=exp['replicas'],calls=N,live=W,old_profile=old,new_profile=profile,delta_per_call=delta,root_interval=[str(lo),str(hi)],root_decimal=dec(lo),first_lower=price.compact(l),first_upper=price.compact(h),second_lower_upper=str(il.hi-1),second_upper_lower=str(ih.lo-1),predecessor_root_interval=exp['root_interval'],candidate_modern_kappa=str(modern),candidate_modern_kappa_decimal=dec(modern),gain_vs_predecessor=dec(modern-Q(exp['candidate_endpoint'])),gain_percent=dec(100*(modern/Q(exp['candidate_endpoint'])-1)),pins=pins,scope='Exact local-word-linked moment only. Modern transfer and global physical/prefix admission must be separately checked; predecessor supplier remains conditional.')
 a.out.write_text(json.dumps(out,indent=2)+'\n');print(out['status'],out['root_decimal'],out['gain_vs_predecessor'])
if __name__=='__main__':main()
