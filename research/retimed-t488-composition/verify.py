#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Fresh bounded construction checks; full admission is a separate explicit replay.
Substantial OpenAI Codex assistance. A recorded summary is not a fresh full replay.
"""
from pathlib import Path
from fractions import Fraction as Q
import argparse,hashlib,json,os,subprocess,sys,tempfile,time
HERE=Path(__file__).resolve().parent

def need(ok,message):
    if not ok: raise ValueError(message)
def read(p): return json.loads(p.read_bytes())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def snapshot(): return {str(p.relative_to(HERE)):sha(p) for p in HERE.rglob('*') if p.is_file()}
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--out',type=Path);a=ap.parse_args()
    need(__debug__ and not sys.flags.optimize,'Enabled assertions required')
    before=snapshot()
    for rel,digest in read(HERE/'ARTIFACTS.json').items():need(sha(HERE/rel)==digest,'Package source binding '+rel)
    out=a.out.resolve() if a.out else Path(tempfile.mkdtemp(prefix='retimed-t488-bounded-'))
    need(HERE!=out and HERE not in out.parents,'Outputs outside package')
    if a.out:need(not out.exists(),'Fresh output required');out.mkdir(parents=True)
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',TMPDIR=str(out));env.pop('PYTHONOPTIMIZE',None)
    stages=[]
    def run(name,rel,*args):
        start=time.monotonic();cmd=[sys.executable,'-B',str(HERE/rel),*map(str,args)]
        with (out/(name+'.log')).open('w') as f:p=subprocess.run(cmd,env=env,stdout=f,stderr=subprocess.STDOUT)
        need(p.returncode==0,name+' failed; see '+str(out/(name+'.log')))
        stages.append({'name':name,'exit_code':p.returncode,'seconds':time.monotonic()-start});print('PASS',name,flush=True)
    run('local','local-audit/verify.py','--out',out/'local')
    run('owners','owners/run.py','--out',out/'owners')
    run('numerics','numerics/run.py','--profile',out/'owners/literal/PROFILE.json','--out',out/'numerics')
    run('full-replay-inputs','full-replay/reproduce.py','--check-inputs')
    owner=read(out/'owners/RUN.json');arithmetic=read(out/'numerics/RESULT.json');moment=read(out/'numerics/MOMENT.json')
    need(owner['profile']==moment['new_profile'],'independent owner/moment profile binding')
    need((owner['roles'],owner['calls'],owner['physical'])==(1791936,4392,437757),'complete roles and physical count')
    need(arithmetic['strict_outer_inequalities']==63 and arithmetic['outer_rejection_controls']==17,'outer gates')
    need(Q(arithmetic['kappa'])==Q(moment['conditional_modern_kappa']),'moment/modern outer endpoint')
    claim_path=HERE/'evidence/COMPLETE-ADMISSION.json'
    summary=None
    if claim_path.exists():
        summary=read(claim_path)
        need(summary['status']=='PASS_T488_RETIMER_COMPLETE_CONDITIONAL_RELEASE','recorded completed admission')
        need(summary['profile']==owner['profile'] and Q(summary['kappa'])==Q(arithmetic['kappa']),'recorded/fresh finite binding')
        need(len(summary['admission_stages'])==7 and all(s['exit_code']==0 for s in summary['admission_stages']),'seven recorded successful stages')
    need(snapshot()==before,'Package changed during checks')
    result={'status':'PASS_FRESH_BOUNDED_RETIMED_T488','stages':stages,'profile':owner['profile'],'candidate_kappa':arithmetic['kappa'],'recorded_full_admission_present':summary is not None,'scope':'Fresh local, literal-owner and arithmetic checks. Stored full admission, when present, is cross-bound evidence, not a new native/controller replay. All inherited theorem assumptions remain.'}
    (out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
