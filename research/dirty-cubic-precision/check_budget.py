"""Separate integer inequalities and recurrence checks for uniform budgets."""
import hashlib,json
from functools import lru_cache
from pathlib import Path
import importlib.util
P=Path(__file__).resolve().parent

def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

@lru_cache(None)
def calls(n):
 return 1 if n==1 else 2*(calls(n//2)+calls(n-n//2))

def check(rows):
 old=load('quartic877',P/'vendor/877/core.py')
 inherited=load('old_budget628',P/'vendor/628/check_budgets.py')
 comparison=[]
 for row in rows:
  r,p,m,w0=[row[k] for k in ('radix','target_bits','magnitude_bits','input_bits')]
  phi=inherited.prime_power_data(r);n=r-1;depth=(n-1).bit_length()
  if calls(n)!=row['leaf_calls'] or phi!=row['phi']:raise ValueError('independent resource check')
  ell=(r-1).bit_length();delta=1+2*ell+r*n*phi;Ai=2*delta+r+2;gap=delta+ell+2*r+2
  J=Ai+2*r+ell+1+2*depth
  if row['prefix_exponent']!=J:raise ValueError('independent prefix exponent')
  w=row['working_bits'];loc=row['local_error_exponent'];e=row['coefficient_error_exponent'];b=row['factor_bits']
  if loc<3*gap or 13*(r+1)>2**(loc-3*gap):raise ValueError('independent leaf error constant')
  if 2*3**depth>2**(J-Ai-2*r-ell):raise ValueError('independent coefficient mass')
  if w<max(w0,2*gap+1):raise ValueError('independent closure/grid')
  exponent=w-p-m-3*J-loc-3
  if exponent<0 or calls(n)>2**exponent:raise ValueError('independent execution')
  if e<max(delta+1,Ai+1,p+2*Ai+m+4):raise ValueError('independent coefficient perturbation')
  if b<max(n*ell,e+r+3):raise ValueError('independent factor budget')
  if w>max(p,w0)+m+16*r**3:raise ValueError('independent cubic majorant')
  previous=old.kernel_budget(r,p,m,inherited)
  comparison.append(dict(radix=r,p=p,m=m,input_bits=w0,cubic_bits=w,quartic_bits=max(w0,previous['working_bits'])))
 def digest(rows):return hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(',',':')).encode()).hexdigest()
 return dict(cases=len(rows),budgets_sha256=digest(rows),comparisons_sha256=digest(comparison),
             radix64=[r for r in comparison if r['radix']==64 and r['p']==128 and r['m']==20])
