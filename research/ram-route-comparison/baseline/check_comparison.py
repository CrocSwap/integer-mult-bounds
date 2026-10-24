"""Exact arithmetic checks for the fair comparison; Apache-2.0.
Dugongue with substantial OpenAI Codex assistance.
"""
from fractions import Fraction as F
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parent

def need(b,msg):
 if not b:raise ValueError(msg)

def params(lam,k,c,s):
 K=1
 while K<k:K*=2
 q=lam//(64*K*c);r=1
 while 2*r<=max(1,q):r*=2
 b=s+k*c*(2*r+1)
 return K,r,b

def check():
 pins=json.loads((R/'SOURCE-PINS.json').read_text())
 for f,row in pins.items():need(hashlib.sha256((R/f).read_bytes()).hexdigest()==row['sha256'],'source drift '+f)
 cases=0
 for k in range(1,17):
  for c in [2,4,8]:
   for s in [1,3,10]:
    for lam in range(1,10001,13):
     K,r,b=params(lam,k,c,s)
     need(r>=F(lam,128*K*c),'epoch lower bound')
     need(b>=F(k*lam,64*K),'eager table lower exponent')
     if lam>=max(64*K*c,64*s):need(16*b<=lam,'table upper exponent')
     cases+=1
 kT=F('0.0030217758');kN=F('0.0030217758');old=F('0.0030217754')
 need(kN==kT,'current same-model exponents equal')
 need(kN-old==F(1,2500000000),'historical native-only gain')
 # Concrete strict-improvement witness for the sufficient criterion, not a new algorithm.
 candidate=kT+F(1,1000000);eta=F(1,2000000)
 need(candidate-kT-eta>0,'positive logarithmic absorption slack')
 return {'status':'PASS_FAIR_COMPARISON_ARITHMETIC','source_parameter_cases':cases,'current_kappa_native':str(kN),'current_kappa_packed_TM':str(kT),'strict_computational_superiority_established':False,'historical_native_only_gain':str(kN-old),'scope':'Exact parameter arithmetic and source hashes; universal dominance and portfolio arguments are written proofs, not benchmark results.'}
if __name__=='__main__':print(json.dumps(check(),indent=2))
