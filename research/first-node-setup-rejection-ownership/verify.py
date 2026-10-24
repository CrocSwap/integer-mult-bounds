#!/usr/bin/env python3
"""Independent finite controls; snapshots belong only to the checker."""
import json,sys,time,copy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import binding,transaction
from verify_core import run,check

def validate_receipt(receipt):
 check(type(receipt) is dict and receipt.get('status')=='PASS_WHOLE_SETUP_OWNERSHIP_CONTROLS','receipt status')
 check(type(receipt.get('cases')) is list and len(receipt['cases'])==14,'receipt cases')
 for row in receipt['cases']:
  report=row['report']
  check(report['state'] in ('rejected','handed_off'),'receipt state')
  for key in ('new_tapes_peak','cleanup_ops','cleanup_bound'):
   check(type(report[key]) is int and report[key]>=0,'typed receipt counter')
  check(report['cleanup_ops']<=report['cleanup_bound'],'receipt cleanup bound')

def compare_receipt(observed,expected):
 validate_receipt(expected)
 canonical=lambda value:json.dumps(value,sort_keys=True,separators=(',',':'))
 check(canonical(observed)==canonical(expected),'exact typed deterministic receipt')

def receipt_controls(expected):
 compare_receipt(expected,expected)
 mutant=copy.deepcopy(expected);mutant['cases'][0]['report']['cleanup_ops']=True
 try:validate_receipt(mutant)
 except RuntimeError:pass
 else:raise RuntimeError('boolean receipt mutant accepted')
 mutant=copy.deepcopy(expected)
 slots=mutant['cases'][0]['report']['retained_allocated_slots'];slots[0]=float(slots[0])
 try:compare_receipt(expected,mutant)
 except RuntimeError:pass
 else:raise RuntimeError('nested float receipt mutant accepted')

def main():
 started=time.monotonic();v=binding.load()
 if '--check-only' in sys.argv:print('PASS_SOURCE_BINDINGS');return
 with v.runtime() as m:rows=run(v,m,transaction.GuardedConsumer)
 original=transaction.SetupTransaction.rollback
 try:
  transaction.SetupTransaction.rollback=lambda self:None
  with v.runtime() as m:
   try:run(v,m,transaction.GuardedConsumer,['residue_inventory'])
   except RuntimeError:pass
   else:raise RuntimeError('checker accepted omitted rollback')
 finally:transaction.SetupTransaction.rollback=original
 result={'status':'PASS_WHOLE_SETUP_OWNERSHIP_CONTROLS','cases':rows,'mutants_rejected':['omitted rollback'],
         'limits':'Source reachable ownership only; actual width64 setup, no full selected payload or physical erasure.',
         'seconds':time.monotonic()-started}
 expected=json.loads((Path(__file__).resolve().parent/'RESULT.json').read_text())
 observed=dict(result);observed.pop('seconds');compare_receipt(observed,expected);receipt_controls(expected)
 print(json.dumps(result,indent=2))
if __name__=='__main__':main()
