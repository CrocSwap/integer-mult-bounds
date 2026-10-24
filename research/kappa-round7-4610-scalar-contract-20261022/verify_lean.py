"""Fresh scoped analytic preprocessing lemma, using the retained pinned runtime."""
from pathlib import Path
from hashlib import sha256
import importlib.util,json,os,subprocess,sys,time
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
RUNTIME=ROOT/'research/kappa-lean-verification-20261022'
AUDITOR='6c953b31c385179f852eb4b56246e62a4084cb8906843f15fbf2724508539895'
def digest(p):return sha256(Path(p).read_bytes()).hexdigest()
def main():
    began=time.monotonic();receipt=HERE/'LEAN-VERIFICATION.json'
    result=dict(status='CHECKING_INPUTS',script_sha256=digest(__file__))
    try:
        if sys.version_info[:2]!=(3,14):raise ValueError('Use global Python3.14')
        if digest(RUNTIME/'verify_lean.py')!=AUDITOR:raise ValueError('Auditor source pin')
        spec=importlib.util.spec_from_file_location('phase_preprocessing_auditor',RUNTIME/'verify_lean.py')
        W=importlib.util.module_from_spec(spec);spec.loader.exec_module(W)
        lean,env,runtime=W.environment(str(RUNTIME/'.toolchain/lean-4.21.0-windows/bin/lake.exe'))
        paths=[]
        for entry in env['LEAN_PATH'].split(os.pathsep):
            if entry:
                p=Path(entry);paths.append(str(p if p.is_absolute() else (RUNTIME/p).resolve()))
        env['LEAN_PATH']=os.pathsep.join([str(HERE),*paths])
        source=HERE/'Preprocessing.lean';pin=digest(source);expected=W.audit_source(source)
        if len(expected)!=4:raise ValueError('Four scoped analytic reports')
        argv=[lean,'-s','65536','-o','Preprocessing.olean','Preprocessing.lean']
        with (HERE/'Preprocessing.log').open('wb') as stream:
            proc=subprocess.run(argv,cwd=HERE,env=env,stdout=stream,stderr=subprocess.STDOUT,timeout=300)
        if proc.returncode or digest(source)!=pin:raise ValueError('Lean failed or source changed')
        reports=W.parse_axioms(HERE/'Preprocessing.log',expected)
        result.update(status='PASS_SCOPED_PHASE_PREPROCESSING_INEQUALITY_LEAN',module='Preprocessing',
            source_sha256=pin,log_sha256=digest(HERE/'Preprocessing.log'),olean_sha256=digest(HERE/'Preprocessing.olean'),
            auditor_sha256=AUDITOR,runtime=runtime,argv=['lean',*argv[1:]],exit_code=proc.returncode,
            axioms=reports,fresh_modules=1,fresh_axiom_reports=len(reports),allowed_axioms=sorted(W.ALLOW),
            seconds=time.monotonic()-began,
            scope='Strict real-power subadditivity and its conditional one-helper boundary cost consequence only. Python finite phase classification, native amplitudes/absolute phases, controller, compiler and multiplication are not formalized.')
    except Exception as e:
        result.update(status='FAIL',error=str(e));raise
    finally:receipt.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8',newline='\n')
    print(result['status'],result['fresh_axiom_reports'])
if __name__=='__main__':main()
