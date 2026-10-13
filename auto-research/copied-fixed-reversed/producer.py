#!/usr/bin/env python3
"""Fresh base-two h25 DAG, five-prime original profile and positive-label audit.

PR36/PR21 base-two graph by icekylinx and preceding contributors; PR32
structured profiler adapted to h25 and five-prime reconstruction. Full label
audit retained from Zhihao Chen PR29. This does not use PR24's base-four graph.
"""
from pathlib import Path
from hashlib import sha256
import argparse,gc,json,os,shlex,subprocess,sys,tempfile,time
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from partial_swap.graph import graph,export
from partial_swap.positive import run as positive

def run(work):
    assert not sys.flags.optimize
    work=Path(work).resolve();work.mkdir(parents=True,exist_ok=True)
    start=time.monotonic();expected=json.loads((HERE/'producer-input-25.json').read_text())
    circuit=graph(25);scalar=circuit.verify();assert scalar==expected['scalar']
    dag=work/'h25.bin';export(circuit,dag);circuit.support_in.cache_clear();del circuit;gc.collect()
    env=os.environ.copy();env['TMPDIR']=str(work);env['CLANG_MODULE_CACHE_PATH']=str(work/'clang-cache')
    sources=dict(full_profiles25=HERE/'full_profiles25.cpp',match_positive_dag=ROOT/'scripts/partial_swap/match_positive_dag.cpp',label_audit=HERE/'label_audit.cpp')
    programs={}
    for name,source in sources.items():
        programs[name]=work/name
        subprocess.run([*shlex.split(os.environ.get('CXX','c++')),'-O3','-std=c++17','-I',str(ROOT/'scripts/partial_swap'),str(source),'-o',str(programs[name])],check=True,env=env)
    with (work/'profile.log').open('w') as log:
        proc=subprocess.run([str(programs['full_profiles25']),str(dag),str(dag)+'.links'],stdout=subprocess.PIPE,stderr=log,text=True,check=True,env=env)
    original=json.loads(proc.stdout);assert original==expected['original']
    profile=json.loads(Path(str(dag)+'.h25_five_prime_profiles.json').read_text())
    assert profile==json.loads((HERE/'profile-25.json').read_text())
    labels=positive(str(dag));assert labels==expected['labels'];gc.collect()
    def call(name):return json.loads(subprocess.check_output([str(programs[name]),str(dag),str(dag)+'.positive'],text=True,env=env))
    matched=call('match_positive_dag');assert matched==expected['matched']
    audit=call('label_audit');assert audit==json.loads((HERE/'label-input-25.json').read_text())
    assert profile['crt_matrices']==profile['distinct_matrices'] and profile['rank_sum']==original['rank_sum']
    assert matched['R']==original['R']==profile['R']
    files=[HERE/'producer.py',*sources.values(),HERE/'profile-25.json',HERE/'producer-input-25.json',HERE/'label-input-25.json']
    files += [ROOT/'scripts'/p for p in ['paired_exclusion_circuit.py','partial_swap/graph.py','partial_swap/shared.py','partial_swap/positive.py','partial_swap/binary_io.hpp']]
    return dict(status='FRESH BASE-TWO h25 COMPLETE ORIGINAL PROFILE AND POSITIVE LABEL AUDIT',scalar=scalar,original=original,matched=matched,labels=labels,label_audit=audit,profile=profile,profile_equal=True,dag_sha256=sha256(dag.read_bytes()).hexdigest(),source_sha256={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in files},elapsed_seconds=time.monotonic()-start,
        scope='Complete original fixed-basis transition histogram, before copied-center replacement. Every profiled high-rank transition uses allfive primes; maxNE corner ranks resolves modular disagreements.')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--work-dir',type=Path);p.add_argument('--output',type=Path);a=p.parse_args()
    if a.work_dir:result=run(a.work_dir)
    else:
        base=ROOT/'build/copied-fixed-reversed';base.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='profile-',dir=base) as name:result=run(name)
    if a.output:a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('PASS fresh base-two h25 original/positive producer and five-prime profile; matrices='+str(result['profile']['distinct_matrices']))
