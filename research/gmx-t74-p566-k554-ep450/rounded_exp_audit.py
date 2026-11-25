"""Regression and rejection controls for directed integer Taylor enclosures.
The general enclosure proof is in ROUNDED-EXP-PROOF.md.
"""
import importlib.util,json,argparse
from pathlib import Path
from fractions import Fraction as Q
P=Path(__file__).resolve().parent
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def run():
 m=load('current_dyad',P/'code/fine_mercator.py');b=load('current_decimal',P/'code/fine_moment.py');rm=load('reference_dyad',P/'evidence/reference450/fine_mercator.py');rb=load('reference_decimal',P/'evidence/reference450/fine_moment.py')
 values=[Q(0),Q(1,10**600),Q(1,1000),Q(7,1000),Q(9,1000),Q(99,1000)]
 for x in values:
  lo,hi=m.exponential(x,x);rl,rh=rm.exponential(x,x);assert lo<=rl<=rh<=hi,(x,'dyadic')
  lo,hi=b.exp_bounds(x);rl,rh=rb.exp_bounds(x);assert lo<=rl<=rh<=hi,(x,'decimal')
 for x in [Q(1,10),Q(1,2),Q(999,1000)]:
  lo,hi=b.exp_bounds(x);rl,rh=rb.exp_bounds(x);assert lo<=rl<=rh<=hi,(x,'decimal boundary')
 lo,hi=m.exponential(Q(7,1000),Q(71,10000));rl,rh=rm.exponential(Q(7,1000),Q(71,10000));assert lo<=rl<=rh<=hi
 rejects=0
 for fn,args in [(m.exponential,(Q(-1),Q(0))),(m.exponential,(Q(1,10),Q(1,10))),(m.exponential,(Q(1,100),Q(0))),(b.exp_bounds,(Q(-1),)),(b.exp_bounds,(Q(1),))]:
  try:fn(*args)
  except (AssertionError,ValueError):rejects+=1
  else:raise AssertionError('invalid input accepted')
 # A removed upper tail must fail against the exact reference upper at x=0.999.
 x=Q(999,1000);term=total=Q(1)
 for j in range(1,b.EXP_TERMS):term=term*x/j;total+=term
 assert total<rb.exp_bounds(x)[1]
 return dict(status='PASS_DIRECTED_INTEGER_TAYLOR_REFERENCE_CONTROLS',reference_enclosures=16,invalid_inputs_rejected=rejects,omitted_tail_rejected=True,scope='Exact reference controls and general directed-rounding proof; endpoint and full admission checks remain separate.')
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path);a=ap.parse_args();v=run()
 if a.out:a.out.write_text(json.dumps(v,indent=2)+'\n')
 print(v['status'],flush=True)
