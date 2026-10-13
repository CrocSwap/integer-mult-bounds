#!/usr/bin/env python3
"""Fresh physical replay on the selected split-pair/paid-clone graphs.

Uses the unchanged PR53 dense-support audit, independent matching recount,
CRT profiler and full physical timeline checker. Original contributors:
Avi Eisenberg, Chafik Boukhalfa, Rohan Arun, icekylinx, Dominik Scholz,
RaD / hipotures and all predecessor notices. Apache-2.0.
"""
import argparse, gc, importlib.util, json, os, shlex, struct, subprocess, sys
from pathlib import Path
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[1];PARENT=ROOT/'research/skip-strips'
sys.path[:0]=[str(HERE),str(PARENT),str(ROOT/'scripts')]
from graph import graph
from partial_swap.graph import export
spec=importlib.util.spec_from_file_location('split_skip_parent_producer',PARENT/'producer.py')
p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
p.HERE=HERE

def run(work,record=False):
    p.RECORD=record;p.check_sources();receipt={}
    exe=work/'profiles'
    subprocess.run([*shlex.split(os.environ.get('CXX','c++')),'-O3','-std=c++17',
                    '-I',str(ROOT/'scripts/partial_swap'),str(HERE/'profiles.cpp'),'-o',str(exe)],check=True)
    for h in (23,25):
        print('Rebuilding every scalar sum, physical use and ordered profile h='+str(h),flush=True)
        c=graph(h);scalar=c.verify();p.expect(f'scalar-{h}.json',scalar,'Scalar mismatch')
        degree,ranks,outputs,dense=p.dense_audit(c)
        dag,links=work/f'h{h}.bin',work/f'h{h}.uses';export(c,dag)
        original=json.loads(subprocess.check_output([str(exe),str(dag),str(links)],text=True,
            env=dict(os.environ,LINKS_IN=str(HERE/f'links-{h}.uses'))))
        selected=list(struct.iter_unpack('<2I',links.read_bytes()[8:]))
        p.require(sorted(selected)==sorted(struct.iter_unpack('<2I',(HERE/f'links-{h}.uses').read_bytes()[8:])), 'Matching changed')
        independent=p.recount(c,degree,ranks,outputs,links);p.require(original==independent,'Independent recount')
        p.expect(f'original-{h}.json',original,'Physical counts')
        fixed=p.read(Path(str(dag)+'.round3_rankone_certified_profiles.json'))
        p.expect(f'profiles-{h}.json',fixed,'Complete ordered profiles');p.exactness(h)
        p.timeline.basis.cache_clear();p.timeline.contained.cache_clear()
        compiled=p.timeline.check({'producer':dict(original,dag_path=str(dag)),
                                   'selected_links':{'links':[list(x) for x in selected]}},True)
        p.expect(f'timeline-{h}.json',compiled,'Timeline/dirty basis')
        receipt[str(h)]=dict(scalar=scalar,dense_audit=dense,independent_recount=independent,
                            fixed_profile=fixed,full_timeline=compiled)
        p.timeline.basis.cache_clear();p.timeline.contained.cache_clear()
        if hasattr(c,'support_in'):c.support_in.cache_clear()
        del c;gc.collect()
        print('PASS exact supports, carrier uses, CRT profiles and complete dirty basis h='+str(h),flush=True)
    data_exe=work/'data-corners'
    subprocess.run([*shlex.split(os.environ.get('CXX','c++')),'-O3','-std=c++17',str(HERE/'data_corners.cpp'),'-o',str(data_exe)],check=True)
    print('Rechecking every fixed-basis data pair',flush=True)
    data=json.loads(subprocess.check_output([str(data_exe)],text=True))
    p.require(data==p.read(HERE/'data-corners.json'),'Full data-corner replay')
    from verify import data_corners
    exact=data_corners();p.require(exact['good']==4073300 and exact['fallback']==0,'Incomplete exact recovery')
    receipt['data_corners']=dict(pairs=data['pairs'],good=data['good'],fallback=data['fallback'],nonzero_pivots=data['nonzero_pivots'])
    receipt['exact_recovery']=exact['exact_recovery']
    print('PASS all 4,073,300 pairs including ten exact rational recoveries',flush=True)
    return receipt

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--work-dir',type=Path,required=True)
    ap.add_argument('--record',action='store_true');ap.add_argument('--output',type=Path)
    args=ap.parse_args();args.work_dir.mkdir(parents=True,exist_ok=True)
    result=run(args.work_dir,args.record)
    if args.output:args.output.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
