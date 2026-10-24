"""Fresh sequential admission of the changed-map kappa result.

Uses the frozen emitted word, not the discovery solver. Apache-2.0.
Substantial OpenAI Codex assistance. Inherited assumptions remain explicit.
"""
from datetime import datetime,timezone
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import gzip
import json
import subprocess
import sys
import time
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
NATIVE=ROOT/'research/warp-interface-20261022'


def need(ok,why):
    if not ok:raise ValueError(why)


def read(p):
    b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)


def main():
    # Baseline dependency gates were freshly replayed in the preceding round.
    # Authenticate the saved evidence and rerun native/BIT dependencies here.
    baseline=read(ROOT/'research/kappa-search-20261022/BASELINE-REPLAY.json')
    for row in baseline['gates']:
        path=ROOT/'research/kappa-search-20261022'/row['log']
        need(row['exit_code']==0 and sha256(path.read_bytes()).hexdigest()==row['sha256'],'Retained baseline evidence')
    deps="import sys;sys.dont_write_bytecode=True;sys.path.insert(0,'research/joint-helper-lattice');import verify as V;print('SOURCE_COUNT',V.authenticate());print(V.replay_dependencies()['status'])"
    commands=[
        ('regeneration',[str(NATIVE/'regenerate.py')]),
        ('native',[str(NATIVE/'verify_candidate.py'),'--part','native']),
        ('absolute-phases',[str(NATIVE/'verify_candidate.py'),'--part','phases']),
        ('uniform-gain',[str(NATIVE/'uniform_gain.py')]),
        ('retained-dependencies',['-c',deps]),
        ('whole-arithmetic',[str(HERE/'price_profile.py'),'--native',str(NATIVE/'NATIVE-VALIDATION.json')]),
        ('independent-audit',[str(ROOT/'research/query-projector-interface-20261022/positive-candidate-audit/audit.py')])]
    records=[]
    for name,args in commands:
        argv=[sys.executable,'-B',*args];started=time.monotonic()
        proc=subprocess.run(argv,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=300)
        log=HERE/(name+'.log');log.write_bytes(proc.stdout)
        row={'part':name,'argv':argv,'exit_code':proc.returncode,'seconds':time.monotonic()-started,
             'log':log.name,'sha256':sha256(proc.stdout).hexdigest()}
        records.append(row);print(json.dumps(row),flush=True)
        need(proc.returncode==0,'Fresh gate failed: '+name)
    native=read(NATIVE/'NATIVE-VALIDATION.json');phase=read(NATIVE/'PHASE-VALIDATION.json.gz')
    arithmetic=read(HERE/'ARITHMETIC.json')
    need(native['status']=='PASS_CHANGED_G_NATIVE_BOTH_632_COLUMN_INTERPRETERS','Exact native admission')
    need(phase['status']=='PASS_ALL_ACTUAL_WARP_AND_NEW_PAID_ABSOLUTE_PHASES','All new phase admission')
    need(Q(arithmetic['kappa'])==Q('.00302152') and Q(arithmetic['gain_over_PR4535'])>0,'Strict claimed saving')
    need(arithmetic['native_receipt_sha256']==sha256((NATIVE/'NATIVE-VALIDATION.json').read_bytes()).hexdigest(),'Actual native invoice feeds complete arithmetic')
    need(native['paid']==arithmetic['local_paid'] and native['helpers']==arithmetic['local_helpers'],'Whole ledger binds exact emitted native lists')
    for path,h in arithmetic['source_sha256'].items():need(sha256((ROOT/path).read_bytes()).hexdigest()==h,'Loaded arithmetic source pin '+path)
    need(len(phase['changed_G_operators'])==34 and len(phase['actual_warp_classes'])==180 and len(phase['new_paid_pairs'])==128,'Complete physical coverage inventory')
    need(arithmetic['paid_calls']==64404 and arithmetic['rank_mass_surplus']==752,'Complete paid list and helper credit')
    need(len(arithmetic['outer']['strict_checks'])==54 and len(arithmetic['outer']['functional_checks'])==4,'Whole outer predicate inventory')
    need(all(Q(x)>0 for name in ('strict_checks','functional_checks') for x in arithmetic['outer'][name].values()),'Every outer predicate strictly positive')
    receipt={'status':'PASS_CONDITIONAL_CHANGED_MAP_KAPPA_00302152','checked_utc':datetime.now(timezone.utc).isoformat(),
             'python':sys.version,'python_executable':sys.executable,'kappa':arithmetic['kappa'],
             'baseline_evidence_authenticated':True,'gates':records,
             'outputs_sha256':{p.relative_to(ROOT).as_posix():sha256(p.read_bytes()).hexdigest() for p in [
                 NATIVE/'ACTUAL-WORD.json.gz',NATIVE/'NATIVE-VALIDATION.json',NATIVE/'PHASE-VALIDATION.json.gz',NATIVE/'UNIFORM-GAIN.json',HERE/'ARITHMETIC.json',
                 ROOT/'research/query-projector-interface-20261022/positive-candidate-audit/audit-result.json']},
             'scope':'Exact local native/phase and complete recursive/outer arithmetic, plus independent AI audit. Repository analytic/native/precision/tape/recovery assumptions retained; no independent human review or unconditional theorem.'}
    (HERE/'SESSION-VERIFICATION.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(receipt['status'],flush=True)


if __name__=='__main__':main()
