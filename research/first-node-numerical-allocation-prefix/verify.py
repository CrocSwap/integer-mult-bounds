#!/usr/bin/env python3
"""Source prefix controls and strict complete receipts; no full GL64 payload."""
import sys,json,copy,time
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import source_binding,controls,ledger

def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'))
def equal(a,b):controls.check(canonical(a)==canonical(b),'complete typed receipt equality')

def cheap_controls(expected):
 equal(expected,expected)
 mutant=copy.deepcopy(expected);mutant['cases'][0]['entry_allocated'][0]=float(mutant['cases'][0]['entry_allocated'][0])
 try:equal(expected,mutant)
 except RuntimeError:pass
 else:raise RuntimeError('nested numeric type mutant accepted')
 controls.check(ledger.BOUND==(37672,41),'whole phase maximum')
 warm=ledger.capacities((40000,80),(6,3),(5,8))
 controls.check(warm['capacities']==[40000,80] and warm['backing_cells']==(40001*7+81*10),'warm separate arena maxima')
 mutant=copy.deepcopy(warm);mutant['capacities']=[6+37672,3+41]
 try:equal(warm,mutant)
 except RuntimeError:pass
 else:raise RuntimeError('warm live-only substitution accepted')
 rejected=0
 for args in [((1,),(0,0),(3,8)),((False,1),(0,0),(3,8)),((1,1),(2,0),(3,8)),((1,1),(0,0),(1,8))]:
  try:ledger.capacities(*args)
  except ValueError:rejected+=1
 controls.check(rejected==4,'invalid ledger inventories rejected')

def main():
 data=source_binding.authenticate()
 if '--emit' not in sys.argv:
  expected=json.loads((HERE/'RESULT.json').read_text());cheap_controls(expected)
 if '--check-only' in sys.argv:print('PASS_SOURCE_PINS_AND_TYPED_RECEIPT_CONTROLS');return
 started=time.monotonic();rows=controls.run(data)
 old=ledger.PHASES['route'];ledger.PHASES['route']=(old[0]-64**2,0)
 try:
  with source_binding.runtime(data):
   try:controls.route_case(data)
   except RuntimeError as error:controls.check(str(error)=='proved phase prefix exceeded','intended omitted-chart rejection')
   else:raise RuntimeError('omitted retained-chart mutation accepted')
 finally:ledger.PHASES['route']=old
 result={'status':'PASS_WHOLE_NODE_NUMERICAL_PREFIX_CONTROLS','bound':list(ledger.BOUND),'phases':{k:list(v) for k,v in ledger.PHASES.items()},'cases':rows,'mutants_rejected':['omitted retained route chart','nested int to float','invalid inventories','warm live-only substitution'], 'limits':'Conditional original source prefix proof; selected64 route single record and n65 numerical peel; complete GL2 local call separate; no full selected payload or physical bank admission.'}
 if '--emit' not in sys.argv:equal(result,expected)
 print(json.dumps(result,indent=2));print('elapsed_seconds='+str(time.monotonic()-started),file=sys.stderr)
if __name__=='__main__':main()
