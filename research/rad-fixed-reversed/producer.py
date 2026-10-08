#!/usr/bin/env python3
"""Reproduce RaD's pinned alternating DAGs and complete original fixed profiles.
RaD authors the graph/policy; icekylinx and prior contributors author inherited
frame/matching primitives. Each basis profile is regenerated for its own DAG.
"""
from contextlib import contextmanager
from pathlib import Path
from hashlib import sha256
import argparse,gc,importlib.util,json,os,shlex,subprocess,sys,tempfile
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
@contextmanager
def builder_context():
    oldpath=list(sys.path);missing=object();alias=sys.modules.get('producer_search',missing)
    sys.path.insert(0,str(ROOT/'scripts'))
    import partial_swap.graph as graph
    oldpoints=graph.aligned_points
    try:
        builder=load('rad_fixed_changed_builder',HERE/'sources/producer_search.py');sys.modules['producer_search']=builder
        policy=load('rad_fixed_point_policy',HERE/'sources/point_order_search.py')
        yield builder,policy
    finally:
        graph.aligned_points=oldpoints;sys.path[:]=oldpath
        if alias is missing:sys.modules.pop('producer_search',None)
        else:sys.modules['producer_search']=alias

def build_graph(config):
    with builder_context() as (builder,policy):
        policy.worker=lambda c:builder.build(c['h'],c['threshold'],c['grouping'],c['tree'],c['seed'])
        return policy.evaluate(config)

def run(work):
    assert not sys.flags.optimize
    work=Path(work).resolve();work.mkdir(parents=True,exist_ok=True)
    env=os.environ.copy();env['TMPDIR']=str(work);env['CLANG_MODULE_CACHE_PATH']=str(work/'clang-cache')
    compiler=shlex.split(os.environ.get('CXX','c++'));exe=work/'full_profiles';audit=work/'label_audit'
    for source,target in [(HERE/'full_profiles.cpp',exe),(ROOT/'research/copied-fixed-reversed/label_audit.cpp',audit)]:
        subprocess.run([*compiler,'-O3','-std=c++17','-I',str(ROOT/'scripts/partial_swap'),str(source),'-o',str(target)],check=True,env=env)
    result={}
    for h in (23,25):
        expected=json.loads((HERE/f'input-{h}.json').read_text());target=work/f'h{h}';target.mkdir(exist_ok=True)
        circuit=build_graph(expected['configuration']);scalar=circuit.verify();assert scalar==expected['scalar']
        oldpath=list(sys.path);sys.path.insert(0,str(ROOT/'scripts'))
        try:
            from partial_swap.graph import export
            from partial_swap.positive import run as positive
            dag=target/'dag.bin';export(circuit,dag);circuit.support_in.cache_clear();del circuit;gc.collect()
            digest=sha256(dag.read_bytes()).hexdigest();assert digest==expected['dag_sha256']
            with (target/'profile.log').open('w') as log:
                proc=subprocess.run([str(exe),str(dag),str(target/'profile.json'),str(target/'events.json')],check=True,text=True,stdout=subprocess.PIPE,stderr=log,env=env)
            original=json.loads(proc.stdout);assert original==expected['original']
            profile=json.loads((target/'profile.json').read_text());assert profile==json.loads((HERE/f'profile-{h}.json').read_text())
            labels=positive(str(dag));assert labels==expected['labels'];positive_hash=sha256(Path(str(dag)+'.positive').read_bytes()).hexdigest();assert positive_hash==expected['positive_sha256']
            checked=json.loads(subprocess.check_output([str(audit),str(dag),str(dag)+'.positive'],text=True,env=env))
            assert checked['h']==h and checked['exact_envelopes']==original['c'] and checked['exact_dependency_inclusions']==2*original['c'] and checked['output_frames']==original['q'] and checked['complement_orientation_by_exact_duality']
        finally:sys.path[:]=oldpath
        record=dict(scalar=scalar,original=original,profile=profile,labels=labels,label_audit=checked,dag_sha256=digest,positive_sha256=positive_hash,profile_equal=True)
        (target/'report.json').write_text(json.dumps(record,sort_keys=True,indent=2)+'\n');result[str(h)]=record
        print('PASS RaD alternating',h,'roles',original['R'],'fiveprime matrices',profile['distinct_matrices'],flush=True)
    return dict(status='FRESH SOURCE-BOUND RAD ALTERNATING ORIGINAL PROFILES',axes=result,
        source_sha256={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),HERE/'full_profiles.cpp',HERE/'sources/producer_search.py',HERE/'sources/point_order_search.py']})
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--work-dir',type=Path);p.add_argument('--output',type=Path);a=p.parse_args()
    if a.work_dir:r=run(a.work_dir)
    else:
        base=ROOT/'build/rad-fixed-reversed';base.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='producer-',dir=base) as d:r=run(d)
    if a.output:a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(r,sort_keys=True,indent=2)+'\n')
