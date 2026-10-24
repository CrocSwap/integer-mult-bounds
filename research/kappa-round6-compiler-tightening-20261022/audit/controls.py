"""Corrupt isolated copies and invoke the actual pinned verifier.

Only artifact locations are relocated; no verification predicate is replaced.
Compilation is guarded so an unexpectedly accepted corruption cannot start Lean.
Cao Yifan; substantial OpenAI Codex assistance. Apache-2.0.
"""
from contextlib import redirect_stdout,redirect_stderr
from hashlib import sha256
from pathlib import Path
import copy,importlib.util,io,json,shutil,subprocess,sys,tempfile,time
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;PACKAGE=HERE.parent;ROOT=PACKAGE.parents[1]


def digest(p):return sha256(Path(p).read_bytes()).hexdigest()
def save(p,d):Path(p).write_text(json.dumps(d,indent=2,sort_keys=True)+'\n',encoding='utf-8',newline='\n')


def main():
    began=time.monotonic();verifier=PACKAGE/'verify_lean.py';pinned=digest(verifier)
    frozen={p.name:digest(p) for p in PACKAGE.iterdir() if p.suffix in ['.py','.lean'] or p.name=='ARITHMETIC.json'}
    scratch=HERE/'.scratch';scratch.mkdir(exist_ok=True)
    results=[];original_run=subprocess.run
    def guarded_run(command,*args,**kwargs):
        argv=list(command) if not isinstance(command,str) else [command]
        if any(str(x)=='-o' for x in argv) and 'lean' in Path(str(argv[0])).name.lower():
            raise AssertionError('UNEXPECTED_LEAN_COMPILATION_REACHED')
        return original_run(command,*args,**kwargs)
    subprocess.run=guarded_run
    try:
        for kind,want in [('claimed_kappa','Saving contract'),('paid_profile','Complete arithmetic recomputation'),('proof_and_prepared_hash','Nonreproducible generated TightenedNumerical.lean')]:
            with tempfile.TemporaryDirectory(prefix='corrupt-'+kind+'-',dir=scratch) as name:
                tmp=Path(name).resolve();assert tmp.is_relative_to(scratch.resolve())
                for source in PACKAGE.iterdir():
                    if source.is_file() and (source.suffix in ['.py','.lean','.json']) and source.name!='LEAN-VERIFICATION.json':shutil.copy2(source,tmp/source.name)
                if kind in ['claimed_kappa','paid_profile']:
                    data=json.loads((tmp/'ARITHMETIC.json').read_text(encoding='utf-8'))
                    if kind=='claimed_kappa':data['kappa']='15108880/5000000000'
                    else:data['paid']['1']+=1
                    save(tmp/'ARITHMETIC.json',data)
                else:
                    target=tmp/'TightenedNumerical.lean';text=target.read_text(encoding='utf-8')
                    old='504 * (4 : ℝ) ^ t';assert text.count(old)==1
                    target.write_text(text.replace(old,'505 * (4 : ℝ) ^ t'),encoding='utf-8',newline='\n')
                    prepared=json.loads((tmp/'PROOF-SOURCES.json').read_text(encoding='utf-8'))
                    prepared['prepared_sha256'][target.name]=digest(target);save(tmp/'PROOF-SOURCES.json',prepared)
                spec=importlib.util.spec_from_file_location('corrupt_actual_verifier_'+kind,verifier)
                module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
                module.HERE=tmp
                # Copied loaders derive ROOT from their new physical location.
                # Restore only those path globals to the original pinned tree.
                actual_load=module.load
                def relocated_load(path,name):
                    loaded=actual_load(path,name)
                    if Path(path).resolve().parent==tmp:
                        if hasattr(loaded,'ROOT'):loaded.ROOT=ROOT
                        if hasattr(loaded,'SOURCE') and Path(path).name=='generate_arithmetic.py':
                            loaded.SOURCE=ROOT/'research/pr4359-p7-padding/dependencies/compiler-refill/endpoint.py'
                    return loaded
                module.load=relocated_load
                assert module.ROOT==ROOT and module.NATIVE.parent==ROOT/'research'
                output=io.StringIO();old_argv=sys.argv[:];sys.argv=[str(verifier)]
                try:
                    with redirect_stdout(output),redirect_stderr(output):module.main()
                except Exception as error:
                    message=str(error);assert message==want,(kind,message,want)
                    receipt=json.loads((tmp/'LEAN-VERIFICATION.json').read_text(encoding='utf-8'))
                    assert receipt['status']=='FAIL_TIGHTENED_VERIFICATION' and receipt['error']==want
                    assert not list(tmp.glob('*.olean')) and 'COMPILE ' not in output.getvalue()
                    results.append(dict(control=kind,rejected=True,reason=message,failed_before_Lean_compilation=True,stdout_sha256=sha256(output.getvalue().encode()).hexdigest()))
                else:raise AssertionError('Corrupted artifacts accepted: '+kind)
                finally:sys.argv=old_argv
                assert tmp.is_relative_to(scratch.resolve())
    finally:subprocess.run=original_run
    assert digest(verifier)==pinned
    assert all(digest(PACKAGE/name)==value for name,value in frozen.items())
    result=dict(status='PASS_ACTUAL_VERIFIER_ISOLATED_CORRUPTION_CONTROLS',verifier_sha256=pinned,control_runner_sha256=digest(__file__),root_arithmetic_sha256=digest(PACKAGE/'ARITHMETIC.json'),root_proof_sources_unchanged=True,results=results,seconds=time.monotonic()-began,
                harness='The actual verifier is imported unchanged. HERE points to a temporary copy under audit/.scratch; ROOT/native/runtime remain original. Copied loader ROOT and generator SOURCE path globals are restored to the original pinned tree. subprocess.run rejects any attempt to compile Lean, but permits runtime/version probes. All three corruptions must fail at their exact expected verification predicates. Original source/data files are hash-checked unchanged. Scratch target paths are verified inside the dedicated directory before automatic cleanup.',
                scope='Meaningful rejection controls for artifact binding only; no successful Lean replay or unconditional theorem is claimed by these expected failures.')
    save(HERE/'CONTROLS.json',result);print(json.dumps(result,indent=2))


if __name__=='__main__':main()
