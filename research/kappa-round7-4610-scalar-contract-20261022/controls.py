"""Independent small Gaussian oracle for proof-dependency exclusion safety."""
from pathlib import Path
import contextlib,io,json,random,shutil,sys,tempfile,time
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
import owned_phase_probe as P
from exact_defect_probe import ProofEqualities,gaussian,reduce

def main():
    if not __debug__:raise ValueError('Run the research assertions enabled')
    began=time.monotonic();rng=random.Random(46104665);tests=0;counterfactuals=0
    for n in range(1,8):
        for trial in range(32):
            rows=[(rng.randrange(8),(i+1,)) for i in range(n)]
            for _ in range(12):
                row=tuple(i+1 for i in range(n) if rng.randrange(2))
                if row:rows.append((rng.randrange(8),row))
            rng.shuffle(rows)
            eq=ProofEqualities(n)
            for group,row in rows:eq.equation(group,row)
            eq.finish();assert not eq.pending
            for x in range(1,n+1):
                deps=eq.dependencies([x]);assert deps
                for excluded in range(8):
                    if excluded in deps:continue
                    basis=gaussian(sum(1<<(i-1) for i in row) for group,row in rows if group!=excluded)
                    assert reduce(1<<(x-1),basis)==0
                    counterfactuals+=1
                tests+=1
    # A truly decisive higher-arity equation must appear in the dependency DAG.
    eq=ProofEqualities(3)
    for group,row in [(0,[1]),(1,[2]),(2,[1,2,3])]:eq.equation(group,row)
    eq.finish();assert eq.dependencies([3])=={0,1,2}
    # Mutation reaches the actual owned probe's input-authentication predicate.
    scratch=HERE/'.scratch';scratch.mkdir(exist_ok=True)
    saved=P.HERE
    with tempfile.TemporaryDirectory(prefix='source-control-',dir=scratch) as folder:
        target=Path(folder).resolve();assert target.is_relative_to(scratch.resolve())
        shutil.copytree(HERE/'sources',target/'sources');shutil.copyfile(HERE/'SOURCES.json',target/'SOURCES.json')
        source=target/'sources/PR4665-verify.py';source.write_bytes(source.read_bytes()+b'\n# corruption\n')
        P.HERE=target
        try:
            with contextlib.redirect_stdout(io.StringIO()):P.main()
        except AssertionError as error:assert str(error)=='PR4665-verify.py'
        else:raise AssertionError('actual source-authentication predicate accepted mutation')
        finally:P.HERE=saved
    output=dict(status='PASS_PHASE_PROOF_DEPENDENCY_CONTROLS',query_proofs=tests,
        exact_gaussian_edge_deletion_counterfactuals=counterfactuals,
        higher_arity_decisive_dependency_checked=True,actual_probe_source_corruption_rejected=True,
        script_sha256=P.digest(__file__),proof_engine_sha256=P.digest(HERE/'exact_defect_probe.py'),
        graph_probe_sha256=P.digest(HERE/'owned_phase_probe.py'),seconds=time.monotonic()-began,
        scope='Small exact independent linear-algebra controls and actual source mutation; not a native endpoint or Clifford proof.')
    (HERE/'CONTROLS.json').write_text(json.dumps(output,indent=2,sort_keys=True)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(output,sort_keys=True))
if __name__=='__main__':main()
