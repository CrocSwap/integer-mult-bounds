"""Fresh scoped replay of grouped phase, selected routes and gauge algebra.
Cao Yifan; substantial OpenAI Codex assistance. Apache-2.0.
"""
from datetime import datetime,timezone
from hashlib import sha256
import importlib.util,json,os,subprocess,sys,time
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
OLD=ROOT/'research/kappa-lean-verification-20261022'
PIN='6c953b31c385179f852eb4b56246e62a4084cb8906843f15fbf2724508539895'


def digest(path):return sha256(Path(path).read_bytes()).hexdigest()


def main():
    assert sys.version_info[:2]==(3,14)
    helper=OLD/'verify_lean.py';assert digest(helper)==PIN
    spec=importlib.util.spec_from_file_location('phase_recursion_auditor',helper)
    audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)
    lean,env,runtime=audit.environment(str(OLD/'.toolchain/lean-4.21.0-windows/bin/lake.exe'))
    assert digest(lean)=='fb7a62288f197279fb84e55bb1972348fd2cce1d550845793975f1cebb0c24ab'
    paths=[]
    for entry in env['LEAN_PATH'].split(os.pathsep):
        if entry:
            p=Path(entry);paths.append(str(p if p.is_absolute() else (OLD/p).resolve()))
    env['LEAN_PATH']=os.pathsep.join([str(HERE),*paths])
    began=time.monotonic();reports=[]
    for name,count in [('RankGate',5),('ParallelControls',2),('GroupedPhase',4),('ActivePalette',4)]:
        source=HERE/(name+'.lean');obj=source.with_suffix('.olean');log=source.with_suffix('.log')
        source_hash=digest(source);expected=audit.audit_source(source);assert len(expected)==count
        argv=[lean,'--root='+str(HERE),'-o',str(obj),str(source)]
        with log.open('wb') as out:
            result=subprocess.run(argv,cwd=HERE,env=env,stdout=out,stderr=subprocess.STDOUT,timeout=90)
        assert result.returncode==0,log.read_text(encoding='utf-8')
        assert digest(source)==source_hash
        reports.append(dict(module=name,source_sha256=source_hash,log_sha256=digest(log),
            olean_sha256=digest(obj),exit_code=result.returncode,argv=['lean',*argv[1:]],
            axioms=audit.parse_axioms(log,expected)))
    inputs=[
        'research/kappa-round6-query-normalizer-20261022/PauliPair.lean',
        'research/kappa-round6-query-normalizer-20261022/REAL-GAUGE.json',
        'research/kappa-round6-query-normalizer-20261022/layout-audit/LAYOUT-AUDIT.json',
        'research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz',
        'research/t74-native-fast/vendor/native/new/code/borrow/vendor/clifford/clifford_exact.py',
        'research/warp-interface-20261022/verify_candidate.py',
    ]
    receipt=dict(status='PASS_SCOPED_PHASE_RECURSION_ALGEBRA',author='Cao Yifan',new_kappa=False,
        completed_utc=datetime.now(timezone.utc).isoformat(),runtime=runtime,runtime_auditor_sha256=PIN,
        allowed_axioms=sorted(audit.ALLOW),modules=reports,exported_reports=sum(len(r['axioms']) for r in reports),
        inputs_sha256={p:digest(ROOT/p) for p in inputs},script_sha256=digest(__file__),seconds=time.monotonic()-began,
        scope='All-index independent selected controls; generic rank-one word span containment and common-encoding telescoping; exact phase-sector split, fourth-root rephasing and active-mask characteristic-two kernel algebra. No all-size tape theorem, actual native Phi invoice, complete recursive supplier, or kappa theorem is formalized.')
    (HERE/'LEAN-PHASE-RECURSION.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n',encoding='utf-8',newline='\n')
    print(receipt['status'],len(reports),receipt['exported_reports'],round(receipt['seconds'],3),flush=True)


if __name__=='__main__':main()
