from pathlib import Path
from collections import Counter
import sys,json,hashlib,subprocess
sys.dont_write_bytecode=True
CP=Path(sys.argv[1]).resolve();GEO=Path(sys.argv[2]).resolve();EXE=Path(sys.argv[3]).resolve();OUT=Path(sys.argv[4]).resolve();assert not OUT.exists();OUT.mkdir(parents=True)
sys.path.insert(0,str(GEO));from clifford_exact import *
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();c=json.loads(CP.read_text());ext=dict(c['ext']);h=c['h'];F=fourier(h);phase=[];checks=[]
def op(a):return diag(h,a['quadratic_rows'],a['linear_Z4']).then(perm(h,a['matrix_rows'])).then(xgate(h,a['offset'])).then(Op(h,identity(h),[('phase',a['phase'])]))
for f in sorted(set(ext.values())):
 E=c['frames'][f];res=canonical_frame(h,E).adjoint().then(F);rank_=h-len(E);rec,compiled=lower_child(res);assert rec['rank']==rank_;L,R=op(rec['left']),op(rec['right']);pre,P=lower_child(R.adjoint());post,Q=lower_child(L.adjoint());assert pre['rank']==post['rank']==0
 actual=P.then(res).then(Q);target=fourier(h,range(rank_));assert actual.tab==target.tab;controls=[]
 for name,bad in [('omit_pre',res.then(Q)),('omit_post',P.then(res)),('omit_both',res)]:
  if bad.tab!=target.tab or bad.zero_state()!=target.zero_state():controls.append(name)
 assert controls
 assert sum(e[0]=='C' for e in actual.circuit)<=30
 phase.append(dict(frame=f,basis=E,entrance_rank=len(E),residual_rank=rank_,decomposition=rec,pre_adapter=pre,post_adapter=post,full_address_columns=1<<h,controls_rejected=controls));checks.append(dict(frame=f,h=h,actual=actual.circuit,expected=target.circuit))
inputfile=OUT/'native-phase-input.json';inputfile.write_text(json.dumps(checks));result=subprocess.run([str(EXE),str(inputfile)],capture_output=True,text=True,check=True);(OUT/'native-phase.log').write_text(result.stdout)
(OUT/'RESIDUALS.json').write_text(json.dumps(dict(status='PASS_FRESH_ALL_CANONICAL_ENTRANCES_TWO_SIDED_RESIDUALS',candidate_sha256=sha(CP),engine_sha256=sha(GEO/'clifford_exact.py'),native_replay_source_sha256=sha(Path(sys.argv[5]).resolve() if len(sys.argv)>5 else EXE.with_suffix('.cpp')),runner_sha256=sha(Path(__file__)),native_phase_input_sha256=sha(inputfile),native_phase_log_sha256=sha(OUT/'native-phase.log'),fresh_frames=len(phase),fresh_address_columns=(1<<h)*len(phase),frames=phase,helper_ranks=dict(Counter(h-len(c['frames'][f]) for f in ext.values())),scope='Every frame and exact Gaussian address column freshly checked natively; no cached phase dependency. Requires separate zero-response and block diagonal endpoint admission.'),indent=2));assert sha(CP)==json.loads((OUT/'RESIDUALS.json').read_text())['candidate_sha256'];print(result.stdout);print('PASS FRESH ALL PHASES',len(phase))
