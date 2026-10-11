"""Guard PR484 dyadic int64 expansions before executing exact arithmetic.
OpenAI Codex. Upstream simulator is unchanged; inherited identity checked fresh.
Usage: guarded_lemma.py COMPLEX_PACKAGE SCRIPT [script arguments...]
"""
import sys,runpy,json
from pathlib import Path
SRC=Path(sys.argv[1]).resolve()/'code/lemmaG';script=sys.argv[2];args=sys.argv[3:]
sys.path.insert(0,str(SRC));import gd
stats=dict(add_calls=0,scale_calls=0,primitive_calls=0,maximum_proved_numerator_bits=0)
def maxabs(a):return max(abs(int(a.min())),abs(int(a.max())))if a.size else 0
def record_bound(x,op):
 stats['maximum_proved_numerator_bits']=max(stats['maximum_proved_numerator_bits'],x.bit_length());assert x<1<<63,(op,'mathematical int64 overflow',x)
oldadd=gd.GD.add_scaled
def add(self,src,num,den):
 assert den>0 and den&(den-1)==0
 e=den.bit_length()-1;D=max(self.d,src.d+e);sa=D-self.d;sb=D-src.d-e
 for a,b in((self.re,src.re),(self.im,src.im)):record_bound((maxabs(a)<<sa)+abs(num)*(maxabs(b)<<sb),'add_scaled')
 stats['add_calls']+=1;return oldadd(self,src,num,den)
gd.GD.add_scaled=add
oldscale=gd.GD.scale
def scale(self,num,den):
 for a in(self.re,self.im):record_bound(maxabs(a)*abs(num),'scale')
 stats['scale_calls']+=1;return oldscale(self,num,den)
gd.GD.scale=scale
oldprim=gd.GD.apply_prim
def prim(self,p,inverse=False):
 record_bound(2*(maxabs(self.re)+maxabs(self.im))if p[0]=='C'else max(maxabs(self.re),maxabs(self.im)),p[0]);stats['primitive_calls']+=1
 return oldprim(self,p,inverse)
gd.GD.apply_prim=prim
sys.argv=[str(SRC/script),*args]
runpy.run_path(str(SRC/script),run_name='__main__')
if script=='lg_instances.py':
 result_path=Path('INSTANCES-'+args[0]+'.json');result=json.loads(result_path.read_text())
 assert all(not result[k]['failures']for k in ['I-tr','I-comp','I-centre','I-helper']), 'guarded instance identity failure'
elif script=='lg_e2e.py':
 result_path=Path('E2E-'+args[0]+'.json');result=json.loads(result_path.read_text())
 assert result['status']=='PASS'and not result['failures'], 'guarded end-to-end identity failure'
else:raise AssertionError('unsupported guarded identity script')
import hashlib
stats['checked_result_file']=str(result_path)
stats['checked_result_sha256']=hashlib.sha256(result_path.read_bytes()).hexdigest()
stats['identity_assertions_passed']=True
Path('PREOP-GUARDS-'+Path(script).stem+'.json').write_text(json.dumps(stats,indent=2)+'\n');print('PRE_OPERATION_EXACTNESS_BOUNDS',stats,flush=True)
