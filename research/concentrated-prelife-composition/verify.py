"""Bounded constructor and actual combined-word controls; no admission shortcut."""
if not __debug__:
 raise RuntimeError('Optimized Python disables required upstream assertions; run without -O.')
from pathlib import Path
import argparse,copy,contextlib,io,importlib.util,json,sys
from fractions import Fraction as Q
from generate import HERE,read,write,generate
ap=argparse.ArgumentParser();ap.add_argument('--source2679',type=Path,default=HERE.parent/'gmx-t74-borrow43-handoff');ap.add_argument('--source2696',type=Path,default=HERE.parent/'t74-concentrated-source-partners');ap.add_argument('--work',type=Path,required=True);a=ap.parse_args();result=generate(a.source2679,a.source2696,a.work);work=a.work.resolve();import word_patch as WP,audit_local as AU
controls=[]
for tag in ['base','extra']:
 w=read(work/f'words/{tag}.json.gz')
 for name in ['anticipatory-sign','source-restoration-sign','prelife-warp-image']:
  m=copy.deepcopy(w)
  if name=='anticipatory-sign':m['initial_corrections'][0]['coefficient']=str(-Q(m['initial_corrections'][0]['coefficient']))
  elif name=='source-restoration-sign':
   hits=[i for i,g in enumerate(m['B'])if g[:5]==['add',49,33,-1,1]];assert hits;m['B'][hits[0]][3]=1
  else:next(r for r in m['warps']if r[1]==273)[4][0]^=1
  t=copy.deepcopy(m);t['A']=t['A'][t.get('prelude_events',0):];m['cleanup']=WP.derive_cleanup(t,WP.restored_of(w));dest=work/'controls'/f'{tag}-{name}.json.gz';write(dest,m);log=io.StringIO()
  try:
   with contextlib.redirect_stdout(log):AU.run(dest,work/'controls'/f'{tag}-{name}-unexpected.json')
  except (AssertionError,RuntimeError,ValueError)as exc:controls.append({'provider':tag,'name':name,'rejected':True,'reason':str(exc),'cleanup_rederived':True})
  else:raise AssertionError('Accepted invalid composition '+name)
  (dest.with_suffix('.log')).write_text(log.getvalue())
sp=importlib.util.spec_from_file_location('exact_composition_price',HERE/'vendor/price.py');M=importlib.util.module_from_spec(sp);sp.loader.exec_module(M);endpoint=M.price(read(work/'PROFILE.json'));assert Q(endpoint['lower'])>Q(read(a.source2696/'CLAIM.json')['kappa']);result.update(status='PASS_PORTABLE_COMPOSITION_AND_REJECTION_CONTROLS',rejected_controls=controls,endpoint=endpoint,previous_entire_kappa=read(a.source2696/'CLAIM.json')['kappa']);(work/'VERIFY-RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(result['status'],endpoint['lower'])
