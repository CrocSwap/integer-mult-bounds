if not __debug__:
 raise RuntimeError('Assertions are required; run without optimized Python.')
from pathlib import Path
import argparse,json,time,hashlib
from composition_algebra import load,check_frames,check_cleanup,algebra
p=argparse.ArgumentParser();p.add_argument('--base',type=Path,required=True);p.add_argument('--extra',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();assert __debug__ and not a.out.exists();start=time.process_time();reports={}
for tag,path in [('base',a.base),('extra',a.extra)]:
 w=load(path);report,starts,ends=check_frames(w);report['cleanup_events']=check_cleanup(w);report['algebra']=algebra(w);report['initial_corrections']=len(w['initial_corrections']);report['live_inputs']=704-len(w['removed']);report['helpers']=480-len(w['removed']);report['private_buffers']=len(w['helper_final']);report['word_sha256']=hashlib.sha256(path.read_bytes()).hexdigest();reports[tag]=report;print('PASS',tag,report['profile'],report['helpers'],report['initial_corrections'],flush=True)
a.out.write_text(json.dumps({'status':'PASS_INDEPENDENT_COMPOSITION_FREE_OPERATOR_AND_FULL_FRAME_INVOICE','providers':reports,'CPU_seconds':time.process_time()-start,'scope':'Every arbitrary-input row in both free-operator orientations, actual target map, cold restoration, cleanup zero ends and literal frame invoice. No physical native phases or supplier/outer admission inferred.','checker_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'algebra_module_sha256':hashlib.sha256(Path(__file__).with_name('composition_algebra.py').read_bytes()).hexdigest()},indent=2)+'\n')
