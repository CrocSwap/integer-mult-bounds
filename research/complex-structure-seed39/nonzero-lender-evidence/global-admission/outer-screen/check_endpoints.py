#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Tekalign (@tekuuu), with substantial OpenAI Codex assistance.
"""Two-engine finite profile screen; no global or outer admission."""
import hashlib
import importlib.util
import json
from fractions import Fraction as Q
from pathlib import Path

HERE=Path(__file__).resolve().parent
CASE=HERE.parents[1]
RESEARCH=CASE.parent
ENGINES=RESEARCH/'face-hoist-evidence/budget/inherited/vendor'
PINS={
 'moment.py':'81cbc864e106418fc7854322746f72180cb8110ff39f74450a3b8d55a82c1482',
 'base_two_moment.py':'aee70c242a2f1d225528fabe2002e1564d1dc884797c07d28a831c7878ee9098',
}
PROFILE_PIN='479c54182b51f200402387ff9bb4b8d911f89615d701a64e76bd543a9dbfcff6'
NATIVE=Q('0.001697210569589237219727')
CONSERVATIVE=Q('0.001697210566704226823872')
ROUND_RATE=Q('0.0016972105')


def load(name):
 path=ENGINES/name
 assert hashlib.sha256(path.read_bytes()).hexdigest()==PINS[name],name
 spec=importlib.util.spec_from_file_location('screen_'+name[:-3],path)
 mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 return mod


def enc(iv):
 return {'lower':str(iv[0]),'upper':str(iv[1]),
         'lower_approx':float(iv[0]),'upper_approx':float(iv[1])}


def main():
 assert __debug__,'Assertions required'
 raw=(CASE/'budget/RESTRICTED-PROFILE.json').read_bytes()
 assert hashlib.sha256(raw).hexdigest()==PROFILE_PIN
 H={int(k):v for k,v in json.loads(raw).items()}
 assert 73*66304-sum(r*n for r,n in H.items())==23680
 M=load('moment.py');B=load('base_two_moment.py')
 def moment(engine,H,z,bad):
  if engine=='mercator':return M.moment(H,73,66304,z,bad)
  lo,hi=B.moment(73,66304,list(H.items()),z)
  if bad:
   fl,fu=B.moment(73,66304,[(1,32*73*73*sum(H.values()))],z)
   lo+=fl/10**16;hi+=fu/10**16
  return lo,hi
 rows={}
 for name,bad,endpoint in [('native',False,NATIVE),('conservative',True,CONSERVATIVE)]:
  rows[name]={}
  for engine in ('mercator','base_two'):
   lower=moment(engine,H,endpoint,bad)
   upper=moment(engine,H,endpoint+Q(1,10**24),bad)
   target=moment(engine,H,ROUND_RATE,bad)
   assert lower[1]<1<upper[0]
   assert target[1]<1
   rows[name][engine]={'accepted_endpoint':str(endpoint),
    'rejected_next_endpoint':str(endpoint+Q(1,10**24)),
    'lower_endpoint_residual':enc((lower[0]-1,lower[1]-1)),
    'upper_endpoint_residual':enc((upper[0]-1,upper[1]-1)),
    'round_rate_residual':enc((target[0]-1,target[1]-1))}
  for key in ('lower_endpoint_residual','upper_endpoint_residual','round_rate_residual'):
   x,y=[rows[name][e][key] for e in ('mercator','base_two')]
   assert max(Q(x['lower']),Q(y['lower']))<=min(Q(x['upper']),Q(y['upper']))
 comparison=json.loads((CASE/'PR2374-OUTER-CLAIM.json').read_text())
 K=Q(comparison['kappa'])
 assert hashlib.sha256(comparison['kappa'].encode()).hexdigest()=='b14d377d6aa465aafd8d8f23953a210763744fbc7a538fd378f89c48704885be'
 assert K<ROUND_RATE<CONSERVATIVE<NATIVE<Q('0.001733427039589844234749')
 controls={}
 extra=dict(H);extra[1]+=1
 for engine in ('mercator','base_two'):
  v=moment(engine,extra,ROUND_RATE,False)
  assert v[0]>1
  controls[engine+':one_additional_global_rank1_child']=enc((v[0]-1,v[1]-1))
  v=moment(engine,H,NATIVE,True)
  assert v[0]>1
  controls[engine+':native_endpoint_with_old_surcharge']=enc((v[0]-1,v[1]-1))
 out={'status':'PASS_TWO_ENGINE_PROFILE_ENDPOINT_SCREEN_NOT_GLOBAL_ADMISSION',
  'profile':H,'profile_sha256':PROFILE_PIN,'engine_pins':PINS,
  'native_endpoint':str(NATIVE),'conservative_endpoint':str(CONSERVATIVE),
  'round_supplier_rate':str(ROUND_RATE),'endpoint_digits':24,
  'comparison_pr':2374,'comparison_head':'5449da65da12bdfd94675dccc38731eaa91e93b6',
  'round_rate_gain_over_pinned_comparison':str(ROUND_RATE-K),
  'brackets':rows,'rejecting_controls':controls,
  'surcharge_formula':'sum_r H[r]*r/(73*66304)*(73/r)^b + 32*73*sum(H)/(10^16*66304)*73^b',
  'scope':'Exact rational arithmetic for the literal restricted profile. Physical/controller/parent/supplier admission and outer all-size assumptions remain separate; no new kappa is claimed.'}
 (HERE/'ENDPOINT-SCREEN.json').write_text(json.dumps(out,indent=2)+'\n')
 print(out['status']);print('native',str(NATIVE),'conservative',str(CONSERVATIVE),'round',str(ROUND_RATE))


if __name__=='__main__':main()
