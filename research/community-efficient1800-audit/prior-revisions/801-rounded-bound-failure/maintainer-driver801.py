from pathlib import Path
import json,subprocess,sys,tempfile,hashlib
from fractions import Fraction as F
root=Path(__file__).resolve().parent;pkg=root/'research/label-field-census'
with tempfile.TemporaryDirectory(prefix='label-census-') as td:
 out=Path(td)/'actual.json'
 subprocess.run([sys.executable,'-I','-B',str(pkg/'census.py'),'--json',str(out)],check=True,timeout=540)
 actual=json.loads(out.read_text());expected=json.loads((pkg/'RESULT.json').read_text());assert actual==expected
 print('PASS all fields of original RESULT.json: six configurations, three calibrations and21 sweep rows',flush=True)
 for label,cost,relation in [('Eisenstein E8 (40 lines, n=4)',24,'above'),('Eisenstein E8 (40 lines, n=4)',25,'below')]:
  x=F(actual['copy_cost_sweep'][label+' cost='+str(cost)]['X_upper'])
  assert (x>F(1,99))==(relation=='above')
 sys.path.insert(0,str(root/'research/format-limits-corrected/scripts'))
 from skel import X
 extra=[]
 for cost,cap in [(22,F(807,100000)),(24,F(598,100000))]:
  bounds=[X(s,7,1,F(cost,40)) for s in (3,5,7,9,11,13)];best=max((x for x in bounds if x),key=lambda x:x['hi']);assert best['hi']<cap,(cost,best['hi'],cap)
  extra.append(dict(cost=cost,window=7,stages=[3,5,7,9,11,13],maximizing_stage=best['s'],upper=str(best['hi']),strict_cap=str(cap)))
 print('PASS conditional window-seven bounds '+json.dumps(extra),flush=True)
 report=dict(status='passed',complete_original_result_equal=True,additional_conditional_rows=extra,scope='Finite geometry and six-stage certified formula evaluation only; field realizability and the stage-count tail are not established.')
 (root/'maintainer-result801.json').write_text(json.dumps(report,indent=2)+'\n')
