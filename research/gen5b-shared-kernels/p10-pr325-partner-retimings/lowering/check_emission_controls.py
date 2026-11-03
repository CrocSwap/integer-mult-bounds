from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
import packet325 as contract
contract.require_assertions()
contract.verify_inputs()
contract.verify_frame_binding()
"""Independent malformed-input controls for the fresh PR325 global IR."""
from pathlib import Path
from collections import Counter
import json,gzip,struct,hashlib,copy,os
if not __debug__:raise RuntimeError('Assertions required')
HERE=contract.GLOBAL;P=contract.GLOBAL;PREP=contract.PREPARED
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text())
def assignments(rows):
 assert len(rows)==486000
 seen=set();cover=bytearray(8568000)
 for r,t,b,o,w,c in rows:
  assert 0<=r<9060 and 0<=t<60 and 0<=b<85680 and w in(4,20)and 0<=o<o+w<=100 and c==o//w+1
  assert(r,t)not in seen;seen.add((r,t));s=slice(b*100+o,b*100+o+w);assert not any(cover[s]);cover[s]=b'\1'*w
 assert all(cover)
def phases(ps):
 expected=[]
 for stage in range(5):
  expected.extend(('helper',stage,t,None)for t in range(60))
  if stage in(1,2,4):expected.extend((k,stage,t,{1:0,2:1,4:2}[stage])for t in range(60)for k in('idle','bridge'))
 expected.extend(('terminal_exchange',None,t,None)for t in range(60))
 assert len(ps)==720
 for i,(p,w)in enumerate(zip(ps,expected)):
  assert(p['kind'],p.get('stage'),p['replica'],p.get('which'))==w and p['phase_index']==i and p['cover']=='all_GL100_Rw'
  if p['kind']=='helper':assert p['reverse_complement']==(p['stage']in(1,3))
def fees(x):
 S=658800;E=14514000;J=6242400;K=170009279400
 expected={'unit_expanded_additions':106113600,'high_affine_factors':J*16*10001**2,'low_transpositions':J*(S+20),'generic_wrappers':E*80008,
 'matrix_preparation':E*128*200**3,'global_matrix_preparation':16000000,'copy_erase_episodes':6000,'paid_child_overhead':E,'bank_selectors':K,'constant':1}
 assert x['terms']==expected and sum(expected.values())==x['coefficient']==24857617667871401
 assert x['all_edges_pay_fallback320000']and x['row_reserve']==10001 and x['completion_children']==0 and x['max_rank']==42
 assert(x['route_movements'],x['selector_calls'],x['literal_stock'],x['children'],x['rank_mass'])==(J,K,S,E,65757600)
def main():
 rows=list(struct.iter_unpack('>6I',gzip.decompress((PREP/'literal-bank-assignments.bin.gz').read_bytes())));ps=read(P/'extended-phases.json');bill=read(P/'invoice.json');assignments(rows);phases(ps);fees(bill)
 rejected=[]
 def reject(name,check,obj,mutate):
  bad=copy.deepcopy(obj);mutate(bad)
  try:check(bad)
  except(AssertionError,KeyError):rejected.append(name)
  else:raise AssertionError('accepted '+name)
 reject('omitted_bank_assignment',assignments,rows,lambda x:x.pop())
 reject('duplicate_bank_assignment',assignments,rows,lambda x:x.__setitem__(1,x[0]))
 reject('wrong_bank_address',assignments,rows,lambda x:x.__setitem__(0,(*x[0][:2],85680,*x[0][3:])))
 reject('overlapping_bank_support',assignments,rows,lambda x:x.__setitem__(1,(*x[1][:3],x[0][3],x[1][4],x[0][5])))
 reject('omitted_helper_sweep',phases,ps,lambda x:x.pop(59))
 reject('boundary_before_last_helper',phases,ps,lambda x:x.__setitem__(slice(119,121),list(reversed(x[119:121]))))
 reject('unrequested_completion',phases,ps,lambda x:x.append({'kind':'paid_bank_completion'}))
 reject('missing_wrappers',fees,bill,lambda x:x['terms'].__setitem__('generic_wrappers',0))
 reject('missing_selectors',fees,bill,lambda x:x['terms'].__setitem__('bank_selectors',0))
 reject('missing_matrix_preparation',fees,bill,lambda x:x['terms'].__setitem__('matrix_preparation',0))
 reject('missing_copy_fee',fees,bill,lambda x:x['terms'].__setitem__('copy_erase_episodes',0))
 reject('missing_fallback',fees,bill,lambda x:x.__setitem__('all_edges_pay_fallback320000',False))
 result={'status':'PASS_INDEPENDENT_PR325_EMITTED_BANK_PHASE_FEE_CONTROLS','global_result_sha256':sha(P/'RESULT.json'),'checker_sha256':sha(__file__),'rejected':rejected,'negative_controls':len(rejected)}
 (HERE/'EMISSION-CONTROLS.json').write_text(json.dumps(contract.portable(result),indent=2)+'\n');print(json.dumps(contract.portable(result),indent=2))
if __name__=='__main__':main()
